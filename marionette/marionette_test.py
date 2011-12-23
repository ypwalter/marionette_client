import re
import unittest
from errors import *

class MarionetteTestCase(unittest.TestCase):

    def __init__(self, marionette, methodName='runTest'):
        self.marionette = marionette
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        self.marionette.start_session()

    def tearDown(self):
        self.marionette.delete_session()

class MarionetteJSTestCase(unittest.TestCase):

    context_re = re.compile(r"MARIONETTE_CONTEXT(\s*)=(\s*)['|\"](.*?)['|\"];")
    timeout_re = re.compile(r"MARIONETTE_TIMEOUT(\s*)=(\s*)(\d+);")

    def __init__(self, marionette, methodName='runTest', jsFile=None):
        assert(jsFile)
        self.jsFile = jsFile
        self.marionette = marionette
        unittest.TestCase.__init__(self, methodName)

    def runTest(self):
        if self.marionette.session is None:
            self.marionette.start_session()
        f = open(self.jsFile, 'r')
        js = f.read()

        context = self.context_re.search(js)
        if context:
            context = context.group(3)
            self.marionette.set_context(context)
        timeout = self.timeout_re.search(js)
        if timeout:
            timeout = timeout.group(3)
            self.marionette.set_script_timeout(timeout)

        try:
            results = self.marionette.execute_js_script(js)

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




