# This function will run the pulse build watcher,
# then on detecting a build, it will run the tests
# using that build.

import logging
import os
import sys
import traceback
import urllib
import mozlog
import shutil
from optparse import OptionParser
from threading import Thread
from manifestparser import TestManifest
from runtests import run_test
from marionette import Marionette
from mozinstall import install

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

    def on_build(self, data, msg):
        # Found marionette build! Install it
        print "Found build %s" % data 
        if "buildurl" in data["payload"]:
            dir = self.install_build(data["payload"]["buildurl"])
            rev = data["payload"]["commit"]
            if dir == None:
                self.logger.info("Failed to return build directory")
            self.run_marionette(dir, rev)
            self.cleanup(dir)
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
            # Extract to the same local directory where we downloaded the build
            # to.  This defaults to the local directory where our script runs
            dest = os.path.dirname(buildfile)
            install(buildfile, dest)
            # This should extract into a qemu directory
            if os.path.exists("qemu"):
                return os.path.abspath("qemu")
            else:
                return None
        except:
            self.logger.error("Failed to untar file: %s %s" % sys.exc_info()[:2])
        return None


    def run_marionette(self, dir, rev):
        self.logger.info("Starting test run for revision: %s" % rev)
        runner = MarionetteTestRunner(emulator=True,
                                      homedir=dir,
                                      autolog=True,
                                      revision=rev)
        runner.run_tests(self.testlist)

    def cleanup(self, dir):
        self.logger.info("Cleaning up")
        if os.path.exists("b2gtarball.tar.gz"):
            os.remove("b2gtarball.tar.gz")
        if os.path.exists(dir):
            shutil.rmtree(dir)

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
    logger.addHandler(logging.StreamHandler())

    try:
        b2gauto = B2GAutomation(options.testmanifest, offline=options.offline)
        # this is test code, only executed if you run with --offline
        #d = b2gauto.install_build("http://10.242.30.20/out/qemu_package.tar.gz")
        #b2gauto.run_marionette(d)
    except:
        s = traceback.format_exc()
        logger.error(s)
        return 1
    return 0

if __name__ == "__main__":
    main()

