from marionette_test import MarionetteTestCase
from errors import *

class ExecuteTest(MarionetteTestCase):

    def test_execute(self):
        self.assertTrue(self.marionette.execute_script("return true;"))

    def test_execute_async(self):
        self.assertTrue(self.marionette.execute_async_script("""
            var callback = arguments[arguments.length -1];
            callback(true);
            """))

    def test_same_context(self):
        var1 = self.marionette.execute_script("""
            window.wrappedJSObject._testvar = 'testing';
            return window.wrappedJSObject._testvar;
            """)

        var3 = self.marionette.execute_script("return window.wrappedJSObject._testvar;")
        self.assertTrue(var1 == var3 == 'testing')

        var2 = self.marionette.execute_async_script("""
            var callback = arguments[arguments.length - 1];
            callback(window.wrappedJSObject._testvar);
            """)
        self.assertTrue(var1 == var2 == 'testing')

    def test_timeout(self):
        self.marionette.set_script_timeout(1000)
        self.assertRaises(ScriptTimeoutException,
            self.marionette.execute_async_script, """
            var callback = arguments[arguments.length - 1];
            setTimeout(function() { callback(true); }, 2000);
            """)

    def test_no_timeout(self):
        self.marionette.set_script_timeout(2000)
        self.assertTrue(self.marionette.execute_async_script("""
            var callback = arguments[arguments.length - 1];
            setTimeout(function() { callback(true); }, 1000);
            """))

    def test_execute_js_exception(self):
        self.assertRaises(JavascriptException,
            self.marionette.execute_script, "return foo(bar);")

    def test_execute_async_js_exception(self):
        self.assertRaises(JavascriptException,
            self.marionette.execute_async_script, "return foo(bar);")

    def test_script_finished(self):
        self.assertTrue(self.marionette.execute_async_script("""
            marionetteScriptFinished(true);
            """))

