# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1 
# 
# The contents of this file are subject to the Mozilla Public License Version 
# 1.1 (the "License"); you may not use this file except in compliance with 
# the License. You may obtain a copy of the License at 
# http://www.mozilla.org/MPL/ # 
# Software distributed under the License is distributed on an "AS IS" basis, 
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
# for the specific language governing rights and limitations under the 
# License. 
# 
# The Original Code is Marionette Client. 
# 
# The Initial Developer of the Original Code is 
#   Mozilla Foundation. 
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved. 
# 
# Contributor(s): 
# 
# Alternatively, the contents of this file may be used under the terms of 
# either the GNU General Public License Version 2 or later (the "GPL"), or 
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"), 
# in which case the provisions of the GPL or the LGPL are applicable instead 
# of those above. If you wish to allow use of your version of this file only 
# under the terms of either the GPL or the LGPL, and not to allow others to 
# use your version of this file under the terms of the MPL, indicate your 
# decision by deleting the provisions above and replace them with the notice 
# and other provisions required by the GPL or the LGPL. If you do not delete 
# the provisions above, a recipient may use your version of this file under 
# the terms of any one of the MPL, the GPL or the LGPL. 
# 
# ***** END LICENSE BLOCK ***** 

from marionette_test import MarionetteTestCase
from errors import JavascriptException, MarionetteException, ScriptTimeoutException

class TestExecute(MarionetteTestCase):
    def test_execute_async_simple(self):
        marionette = self.marionette
        self.assertEqual(1, marionette.execute_async_script("arguments[arguments.length-1](1);"))

    def test_execute_async_ours(self):
        marionette = self.marionette
        self.assertEqual(1, marionette.execute_async_script("marionetteScriptFinished(1);"))

    def test_execute_async_timeout(self):
        marionette = self.marionette
        self.assertRaises(ScriptTimeoutException, marionette.execute_async_script, "1;")

    def test_execute_async_unload(self):
        marionette = self.marionette
        marionette.set_script_timeout(15000)
        unload = """
                window.location.href = "about:blank";
                 """
        self.assertRaises(JavascriptException, marionette.execute_async_script, unload)

    def test_check_window(self):
        marionette = self.marionette
        self.assertTrue(marionette.execute_script("return (window !=null && window != undefined);"))

    def test_execute_no_return(self):
        marionette = self.marionette
        self.assertRaises(MarionetteException, marionette.execute_script, "1;")
        
    def test_execute_permission_failure(self):
        marionette = self.marionette
        self.assertRaises(JavascriptException, marionette.execute_script, "return Components.classes;")

    def test_chrome_async(self):
        self.marionette.set_context("chrome")
        self.assertEquals(2, self.marionette.execute_async_script("marionetteScriptFinished(2);"))
        self.marionette.set_context("content")



