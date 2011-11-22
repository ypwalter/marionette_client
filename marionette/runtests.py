import imp
from optparse import OptionParser
import os

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
    if 'do_test' in dir(test_mod):
        print 'running test', mod_name
        test_mod.do_test(marionette)
        print 'TEST-PASS: %s' % mod_name


if __name__ == "__main__":
    parser = OptionParser(usage='%prog [options] test_file_or_dir <test_file_or_dir> ...')
    parser.add_option("--emulator",
                      action = "store_true", dest = "emulator",
                      default = False,
                      help = "launch a B2G emulator on which to run tests")
    parser.add_option('--address', dest='address', action='store',
                      help='host:port of running Gecko instance to connect to')
    options, tests = parser.parse_args()

    if not tests:
        parser.print_usage()
        parser.exit()

    if options.address:
        host, port = options.address.split(':')
        if options.emulator:
            m = Marionette(host=host, port=int(port), connectToRunningEmulator=True)
        else:
            m = Marionette(host=host, port=int(port))
    elif options.emulator:
        m = Marionette(emulator=True)
    else:
        raise Exception("must specify --address or --emulator")

    assert(m.start_session())

    for test in tests:
        run_test(test, m)

    m.delete_session()

