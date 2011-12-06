import imp
from optparse import OptionParser
import os
import types
import unittest
import socket
from datetime import datetime

from mozautolog import RESTfulAutologTestGroup
from marionette import Marionette


def run_test(test, marionette, revision=None, autolog=False):
    filepath = os.path.join(os.path.dirname(__file__), test)

    if os.path.isdir(filepath):
        for root, dirs, files in os.walk(filepath):
            for filename in files:
                if filename.startswith('test_') and filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    run_test(filepath, marionette)
        return

    mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
    test_mod = imp.load_source(mod_name, filepath)

    testloader = unittest.TestLoader()
    suite = unittest.TestSuite()
    timestart = datetime.utcnow()
    for name in dir(test_mod):
        obj = getattr(test_mod, name)
        if (isinstance(obj, (type, types.ClassType)) and
            issubclass(obj, unittest.TestCase)):
            testnames = testloader.getTestCaseNames(obj)
            for testname in testnames:
                suite.addTest(obj(marionette, methodName=testname))
    elapsedtime = datetime.utcnow() - timestart
    if suite.countTestCases():
        results = unittest.TextTestRunner(verbosity=3).run(suite)
        if autolog:
            report_results(results, revision, elapsedtime)

# The results are the TextTestResults object. Let's go push these to autolog
def report_results(results, revision, elapsedtime):
    # This is all autolog stuff.
    # See: https://wiki.mozilla.org/Auto-tools/Projects/Autolog
    testgroup = RESTfulAutologTestGroup(
        testgroup = 'b2gautomatedtest',
        os = 'android',
        platform = 'emulator',
        machine = socket.gethostname())

    testgroup.set_primary_product(
        tree = 'b2g',
        buildtype = 'opt',
        revision = revision)

    # Results don't have a passed count, calc it
    # We map expected failures and skips as todos
    # We add failures and errors together as failures
    failures = len(results.failures) + len(results.errors) + len(results.unexpectedSuccesses)
    todo = len(results.skipped) + len(results.expectedFailures)
    passes = results.testsRun - (failures + todo)

    testgroup.add_test_suite(
        testsuite='b2g emulator testsuite',
        elapsedtime = elapsedtime.total_seconds(),
        cmdline = '',
        passed = passes,
        failed = failures,
        todo = todo,
        id = 'b2g-%s-%s' % (socket.gethostname(), revision))

    # Add in the test failures.  We can't track passes
    # since python doesn't really keep details on that
    for f in results.failures:
        testgroup.add_test_failure(
            test=f[0].id(),
            traceback = f[1])
    for e in results.errors:
        testgroup.add_test_failure(
            test = e[0].id(),
            traceback = e[1])
    for u in results.unexpectedSuccesses:
        testgroup.add_test_failure(
            test = u[0].id(),
            traceback = u[1])

    testgroup.submit()

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

    if options.address:
        host, port = options.address.split(':')
        if options.emulator:
            m = Marionette(host=host, port=int(port),
                           connectToRunningEmulator=True,
                           homedir=options.homedir)
        else:
            m = Marionette(host=host, port=int(port))
    elif options.emulator:
        m = Marionette(emulator=True,
                       homedir=options.homedir)
    else:
        raise Exception("must specify --address or --emulator")

    assert(m.start_session())

    for test in tests:
        run_test(test, m, autolog=options.autolog)

    m.delete_session()

