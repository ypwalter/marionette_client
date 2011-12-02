import imp
from optparse import OptionParser
import os
import types
import unittest

from marionette import Marionette


def run_test(test, marionette):
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
    for name in dir(test_mod):
        obj = getattr(test_mod, name)
        if (isinstance(obj, (type, types.ClassType)) and
            issubclass(obj, unittest.TestCase)):
            testnames = testloader.getTestCaseNames(obj)
            for testname in testnames:
                suite.addTest(obj(marionette, methodName=testname))
    if suite.countTestCases():
        results = unittest.TextTestRunner(verbosity=3).run(suite)
        print "CLINTDBG: results are: %s" % results


if __name__ == "__main__":
    parser = OptionParser(usage='%prog [options] test_file_or_dir <test_file_or_dir> ...')
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
        run_test(test, m)

    m.delete_session()

