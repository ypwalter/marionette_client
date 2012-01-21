import imp
import inspect
from optparse import OptionParser
import os
import types
import unittest
import socket
from datetime import datetime

try:
    from manifestparser import TestManifest
    from mozhttpd import iface, MozHttpd
except ImportError:
    print "manifestparser or mozhttpd not found!  Please install mozbase:\n"
    print "\tgit clone git clone git://github.com/mozilla/mozbase.git"
    print "\tpython setup_development.py\n"
    import sys
    sys.exit(1)


from marionette import Marionette
from marionette_test import MarionetteJSTestCase


class MarionetteTestResult(unittest._TextTestResult):

    def __init__(self, *args):
        super(MarionetteTestResult, self).__init__(*args)
        self.passed = 0

    def addSuccess(self, test):
        super(MarionetteTestResult, self).addSuccess(test)
        self.passed += 1

    def getInfo(self, test):
        if hasattr(test, 'jsFile'):
            return os.path.basename(test.jsFile)
        else:
            return '%s.py:%s.%s' % (test.__class__.__module__,
                                    test.__class__.__name__,
                                    test._testMethodName)

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            desc = str(test)
            if hasattr(test, 'jsFile'):
                desc = "%s, %s" % (test.jsFile, desc)
            return desc


class MarionetteTextTestRunner(unittest.TextTestRunner):

    resultclass = MarionetteTestResult


class MarionetteTestRunner(object):

    def __init__(self, address=None, emulator=False, homedir=None,
                 autolog=False, revision=None):
        self.address = address
        self.emulator = emulator
        self.homedir = homedir
        self.autolog = autolog
        self.revision = revision
        self.httpd = None
        self.baseurl = None
        self.marionette = None
        self.passed = 0
        self.failed = 0
        self.todo = 0
        self.failures = []

    def start_httpd(self):
        host = iface.get_lan_ip()
        port = 8765
        self.baseurl = 'http://%s:%d/' % (host, port)
        print 'running webserver on', self.baseurl
        self.httpd = MozHttpd(host=host,
                              port=port,
                              docroot=os.path.join(os.path.dirname(__file__), 'www'))
        self.httpd.start()

    def start_marionette(self):
        assert(self.baseurl is not None)
        if self.address:
            host, port = self.address.split(':')
            if self.emulator:
                self.marionette = Marionette(host=host, port=int(port),
                                            connectToRunningEmulator=True,
                                            homedir=self.homedir,
                                            baseurl=self.baseurl)
            else:
                self.marionette = Marionette(host=host, port=int(port), baseurl=self.baseurl)
        elif self.emulator:
            self.marionette = Marionette(emulator=True,
                                         homedir=self.homedir,
                                         baseurl=self.baseurl)
        else:
            raise Exception("must specify address or emulator")

    def post_to_autolog(self, elapsedtime):
        # This is all autolog stuff.
        # See: https://wiki.mozilla.org/Auto-tools/Projects/Autolog
        from mozautolog import RESTfulAutologTestGroup
        testgroup = RESTfulAutologTestGroup(
            testgroup = 'marionette',
            os = 'android',
            platform = 'emulator',
            harness = 'marionette',
            machine = socket.gethostname())

        testgroup.set_primary_product(
            tree = 'b2g',
            buildtype = 'opt',
            revision = self.revision)

        testgroup.add_test_suite(
            testsuite = 'b2g emulator testsuite',
            elapsedtime = elapsedtime.total_seconds(),
            cmdline = '',
            passed = self.passed,
            failed = self.failed,
            todo = self.todo)

        # Add in the test failures.
        for f in self.failures:
            testgroup.add_test_failure(test=f[0], text=f[1])

        testgroup.submit()

    def run_tests(self, tests):
        starttime = datetime.utcnow()
        for test in tests:
            self.run_test(test)
        print '\nSUMMARY'
        print 'passed:', self.passed
        print 'failed:', self.failed
        print 'todo:', self.todo
        elapsedtime = datetime.utcnow() - starttime
        if self.autolog:
            self.post_to_autolog(elapsedtime)

    def run_test(self, test):
        if not self.httpd:
            self.start_httpd()
        if not self.marionette:
            self.start_marionette()
        print 'running', test

        filepath = os.path.join(os.path.dirname(__file__), test)

        if os.path.isdir(filepath):
            for root, dirs, files in os.walk(filepath):
                for filename in files:
                    if filename.startswith('test_') and (filename.endswith('.py') or
                                                         filename.endswith('.js')):
                        filepath = os.path.join(root, filename)
                        self.run_test(filepath)
            return

        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

        testloader = unittest.TestLoader()
        suite = unittest.TestSuite()

        if file_ext == '.ini':
            manifest = TestManifest()
            manifest.read(filepath)
            for i in manifest.get():
                self.run_test(i["path"])
            return

        if file_ext == '.py':
            test_mod = imp.load_source(mod_name, filepath)

            for name in dir(test_mod):
                obj = getattr(test_mod, name)
                if (isinstance(obj, (type, types.ClassType)) and
                    issubclass(obj, unittest.TestCase)):
                    testnames = testloader.getTestCaseNames(obj)
                    for testname in testnames:
                        suite.addTest(obj(self.marionette, methodName=testname))

        elif file_ext == '.js':
            suite.addTest(MarionetteJSTestCase(self.marionette, jsFile=filepath))

        if suite.countTestCases():
            results = MarionetteTextTestRunner(verbosity=3).run(suite)
            self.failed += len(results.failures) + len(results.errors) + len(results.unexpectedSuccesses)
            self.todo += len(results.skipped) + len(results.expectedFailures)
            self.passed += results.passed
            for failure in results.failures + results.errors + results.unexpectedSuccesses:
                self.failures.append((results.getInfo(failure[0]), failure[1]))

    def cleanup(self):
        if self.httpd:
            self.httpd.stop()

    __del__ = cleanup


if __name__ == "__main__":
    parser = OptionParser(usage='%prog [options] test_file_or_dir <test_file_or_dir> ...')
    parser.add_option("--autolog",
                      action = "store_true", dest = "autolog",
                      default = False,
                      help = "send test results to autolog")
    parser.add_option("--emulator",
                      action = "store_true", dest = "emulator",
                      default = False,
                      help = "launch a B2G emulator on which to run tests")
    parser.add_option('--address', dest='address', action='store',
                      help='host:port of running Gecko instance to connect to')
    parser.add_option('--homedir', dest='homedir', action='store',
                      help='home directory of emulator files')
    options, tests = parser.parse_args()

    if not tests:
        parser.print_usage()
        parser.exit()

    if not options.emulator and not options.address:
        parser.print_usage()
        print "must specify --emulator or --address"
        parser.exit()

    runner = MarionetteTestRunner(address=options.address,
                                  emulator=options.emulator,
                                  homedir=options.homedir,
                                  autolog=options.autolog)
    runner.run_tests(tests)



