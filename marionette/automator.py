# This function will run the pulse build watcher,
# then on detecting a build, it will run the tests
# using that build.

import os
import sys
import traceback
import urllib
import mozlog
from optparse import OptionParser
from threading import Thread
from manifestparser import TestManifest
from runtests import run_test
from marionette import Marionette

from mozillapulse.config import PulseConfiguration
from mozillapulse.consumers import GenericConsumer


class B2GPulseConsumer(GenericConsumer):
    def __init__(self, **kwargs):
        super(B2GPulseConsumer, self).__init__(PulseConfiguration(**kwargs),
                                               'org.mozilla.exchange.b2g',
                                               **kwargs)


class B2GAutomation:
    def __init__(self, test_manifest, offline=False):
        self.logger = mozlog.getLogger('B2G_AUTOMATION')
        self.testlist = self.get_test_list(test_manifest)
        print "Testlist: %s" % self.testlist
        self.offline = offline

        pulse = B2GPulseConsumer(applabel='b2g_build_listener')
        pulse.configure(topic='#', callback=self.on_build)

        if not offline:
            pulse.listen()
        else:
            t = Thread(target=pulse.listen)
            t.daemon = True
            t.start()

    def get_test_list(self, manifest):
        self.logger.info("Reading test manifest: %s" % manifest)
        mft = TestManifest()
        mft.read(manifest)

        # In the future if we want to add in more processing to the manifest
        # here is where you'd do that. Right now, we just return a list of
        # tests
        testlist = []
        for i in mft.get():
            testlist.append(i["path"])

        return testlist

    def on_build(self, msg):
        # Found marionette build! Install it
        print "Found build %s" % msg
        if buildurl in msg:
            dir = self.install_build(msg["buildurl"])
            if dir == None:
                self.logger.info("Failed to return build directory")
            self.run_marionette(dir)
        else:
            self.logger.error("Fail to find buildurl in msg not running test")

    # Download the build and untar it, return the directory it untared to
    def install_build(self, url):
        try:
            self.logger.info("Installing build from url: %s" % url)
            buildfile = os.path.abspath("b2gtarball.tar.gz")
            urllib.urlretrieve(url, buildfile)
        except:
            self.logger.error("Failed to download build: %s %s" % sys.exc_info()[:2])

        try:
            self.logger.info("Untarring build")
            p = subprocess.Popen(["tar", "-zvxf", "b2gtarball.tar.gz"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            logmsg = p.communicate()[0]
            self.logger.info(logmsg)
            # This should open a qemu directory
            if os.path.exists("qemu"):
                return os.path.abspath("qemu")
            else:
                return None
        except:
            self.logger.error("Failed to untar file")
        return None


    def run_marionette(self, dir):
        self.logger.info("Starting test run")
        # Start up marionette
        m = Marionette(emulator=True, homedir=dir)
        assert(m.start_session())
        for test in self.testlist:
            run_test(test, m)
        m.delete_session()

def main():
    parser = OptionParser(usage="%prog <options>")
    parser.add_option("--offline", action="store_true", dest="offline",
                      default = False, help = "Start without using pulse")
    parser.add_option("--test-manifest", action="store", dest="testmanifest",
                      default = os.path.join("tests","all-tests.ini"),
                      help="Specify the test manifest, defaults to tests/all-tests.ini")
    parser.add_option("--log-file", action="store", dest="logfile",
                      default="b2gautomation.log",
                      help="Log file to store results, defaults to b2gautomation.log")

    LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
    LEVEL_STRING = ", ".join(LOG_LEVELS)
    parser.add_option("--log-level", action="store", type="choice",
                      dest="loglevel", default="DEBUG", choices=LOG_LEVELS,
                      help = "One of %s for logging level, defaults  to debug" % LEVEL_STRING)
    options, args = parser.parse_args()

    if not options.testmanifest:
        parser.print_usage()
        parser.exit()

    if not os.path.exists(options.testmanifest):
        print "Could not find manifest file: %s" % options.testmanifest
        parser.print_usage()
        parser.exit()

    # Set up the logger
    if os.path.exists(options.logfile):
        os.remove(options.logfile)

    logger = mozlog.getLogger("B2G_AUTOMATION", options.logfile)
    if options.loglevel:
        logger.setLevel(getattr(mozlog, options.loglevel, "DEBUG"))

    try:
        b2gauto = B2GAutomation(options.testmanifest, offline=options.offline)
        # this is test code
        d = b2gauto.install_build("http://10.242.30.20/out/qemu_package.tar.gz")
        b2gauto.run_marionette(d)
    except:
        s = traceback.format_exc()
        logger.error(s)
        return 1
    return 0

if __name__ == "__main__":
    main()

