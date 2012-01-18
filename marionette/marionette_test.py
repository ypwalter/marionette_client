import os
import re
import sys
import types
import unittest

from errors import *
from marionette import HTMLElement

def skip_if_b2g(target):
    def wrapper(self, *args, **kwargs):
        if not hasattr(self.marionette, 'b2g') or not self.marionette.b2g:
            return target(self, *args, **kwargs)
        else:
            sys.stderr.write('skipping ... ')
    return wrapper


class CommonTestCase(unittest.TestCase):

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def kill_gaia_apps(self):
        # shut down any running Gaia apps
        app_count = self.marionette.execute_script("""
var runningApps = window.wrappedJSObject.Gaia.AppManager._runningApps;
runningApps.forEach(function(app) { 
    window.wrappedJSObject.Gaia.AppManager.kill(app.url);
});
return runningApps.length;
""")
        self.assertEqual(app_count, 0)

    def launch_gaia_app(self, url):
        # launch the app using Gaia's AppManager
        self.marionette.execute_script("""
window.wrappedJSObject.Gaia.AppManager.launch("%s");
return(true);
    """ % url)

        # This is the last directory of the path plus the basename,
        # e.g., 'sms/sms.html'.
        short_url = os.path.join(os.path.basename(os.path.dirname(url)), os.path.basename(url))

        # Wait for the iframe to appear that will load the app, attach
        # an onload hanlder to it, and wait for it to load.  This seems
        # like it could potentially be racy...could the app finish loading
        # before we attach our listener?
        self.marionette.set_script_timeout(30000)
        frame = self.marionette.execute_async_script("""
function checkframes() {
    var frames = document.getElementsByTagName('iframe');
    for (var index in frames) {
        if (frames[index].src.indexOf("%s") > -1) {
            var frame = frames[index];
            frame.addEventListener('load', function frameload() {
                frame.removeEventListener('load', frameload);
                setTimeout(function() {marionetteScriptFinished(frame);}, 1000);
                return;
            });
        }
    }
    setTimeout(checkframes, 0);
}
setTimeout(checkframes, 0);
""" % short_url)
        self.assertTrue(isinstance(frame, HTMLElement))
        return frame

    def setUp(self):
        if self.marionette.session is None:
            self.marionette.start_session()
        if self.marionette.b2g:
            self.kill_gaia_apps()

    def tearDown(self):
        if self.marionette.session is not None:
            self.marionette.delete_session()


class MarionetteTestCase(CommonTestCase):

    def __init__(self, marionette, methodName='runTest'):
        self.marionette = marionette
        CommonTestCase.__init__(self, methodName)


class MarionetteJSTestCase(CommonTestCase):

    context_re = re.compile(r"MARIONETTE_CONTEXT(\s*)=(\s*)['|\"](.*?)['|\"];")
    timeout_re = re.compile(r"MARIONETTE_TIMEOUT(\s*)=(\s*)(\d+);")
    launch_re = re.compile(r"MARIONETTE_LAUNCH_APP(\s*)=(\s*)['|\"](.*?)['|\"];")

    def __init__(self, marionette, methodName='runTest', jsFile=None):
        assert(jsFile)
        self.jsFile = jsFile
        self.marionette = marionette
        CommonTestCase.__init__(self, methodName)

    def runTest(self):
        if self.marionette.session is None:
            self.marionette.start_session()
        f = open(self.jsFile, 'r')
        js = f.read()
        args = []

        context = self.context_re.search(js)
        if context:
            context = context.group(3)
            self.marionette.set_context(context)

        timeout = self.timeout_re.search(js)
        if timeout:
            timeout = timeout.group(3)
            self.marionette.set_script_timeout(timeout)

        launch_app = self.launch_re.search(js)
        if launch_app:
            launch_app = launch_app.group(3)
            frame = self.launch_gaia_app(launch_app)
            args.append({'__marionetteArgs': {'appframe': frame}})

        try:
            results = self.marionette.execute_js_script(js, args)

            self.assertTrue(not 'timeout' in self.jsFile,
                            'expected timeout not triggered')

            if 'fail' in self.jsFile:
                self.assertTrue(results['failed'] > 0,
                                "expected test failures didn't occur")
            else:
                self.assertEqual(0, results['failed'],
                                 '%d tests failed' % results['failed'])
            self.assertTrue(results['passed'] + results['failed'] > 0,
                            'no tests fun')
            if self.marionette.session is not None:
                self.marionette.delete_session()

        except ScriptTimeoutException:
            if 'timeout' in self.jsFile:
                # expected exception
                pass
            else:
                raise




