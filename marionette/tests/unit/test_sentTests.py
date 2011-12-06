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

#TODO add to class below
returnSyncFailed = "return Marionette.finish();"
returnSyncPassed = "return Marionette.finish();"
returnAsyncFailed = "Marionette.finish();"
returnAsyncPassed = "Marionette.finish()"

class TestSentTests(MarionetteTestCase):
    def test_is(self):
        sentFail1 = "Marionette.is(true, false, 'isTest1');"
        sentFail2 = "Marionette.is(true, false, 'isTest2');" 
        sentPass1 = "Marionette.is(true, true, 'isTest3');"
        sentPass2 = "Marionette.is(true, true, 'isTest4');"

        self.assertEqual(1, self.marionette.execute_script(sentFail1 + returnSyncFailed)['failed'])
        self.assertEqual(0, self.marionette.execute_script(sentFail2 + returnSyncPassed)['passed'])
        self.assertEqual(1, self.marionette.execute_script(sentPass1 + returnSyncPassed)['passed'])
        self.assertEqual(0, self.marionette.execute_script(sentPass2 + returnSyncFailed)['failed'])

        self.marionette.set_script_timeout(1000)
        self.assertEqual(1, self.marionette.execute_async_script(sentFail1 + returnAsyncFailed)['failed'])
        self.assertEqual(0, self.marionette.execute_async_script(sentFail2 + returnAsyncPassed)['passed'])
        self.assertEqual(1, self.marionette.execute_async_script(sentPass1 + returnAsyncPassed)['passed'])
        self.assertEqual(0, self.marionette.execute_async_script(sentPass2 + returnAsyncFailed)['failed'])

        self.marionette.set_context("chrome")

        self.assertEqual(1, self.marionette.execute_script(sentFail1 + returnSyncFailed)['failed'])
        self.assertEqual(0, self.marionette.execute_script(sentFail2 + returnSyncPassed)['passed'])
        self.assertEqual(1, self.marionette.execute_script(sentPass1 + returnSyncPassed)['passed'])
        self.assertEqual(0, self.marionette.execute_script(sentPass2 + returnSyncFailed)['failed'])

        self.marionette.set_context("content")

    def test_isNot(self):
        sentFail1 = "Marionette.isnot(true, true, 'isTest3');"
        sentFail2 = "Marionette.isnot(true, true, 'isTest4');"
        sentPass1 = "Marionette.isnot(true, false, 'isTest1');"
        sentPass2 = "Marionette.isnot(true, false, 'isTest2');"

        self.assertEqual(1, self.marionette.execute_script(sentFail1 + returnSyncFailed)['failed']);
        self.assertEqual(0, self.marionette.execute_script(sentFail2 + returnSyncPassed)['passed']);
        self.assertEqual(0, self.marionette.execute_script(sentPass1 + returnSyncFailed)['failed']);
        self.assertEqual(1, self.marionette.execute_script(sentPass2 + returnSyncPassed)['passed']);

        self.marionette.set_script_timeout(1000)
        self.assertEqual(1, self.marionette.execute_async_script(sentFail1 + returnAsyncFailed)['failed']);
        self.assertEqual(0, self.marionette.execute_async_script(sentFail2 + returnAsyncPassed)['passed']);
        self.assertEqual(0, self.marionette.execute_async_script(sentPass1 + returnAsyncFailed)['failed']);
        self.assertEqual(1, self.marionette.execute_async_script(sentPass2 + returnAsyncPassed)['passed']);

    def test_ok(self):
        sentFail1 = "Marionette.ok(1==2, 'testOk', 'testOk');"
        sentFail2 = "Marionette.ok(1==2, 'testOk', 'testOk');"
        sentPass1 = "Marionette.ok(1==1, 'testOk', 'testOk');"
        sentPass2 = "Marionette.ok(1==1, 'testOk', 'testOk');" 

        self.assertEqual(1, self.marionette.execute_script(sentFail1 + returnSyncFailed)['failed']);
        self.assertEqual(0, self.marionette.execute_script(sentFail2 + returnSyncPassed)['passed']);
        self.assertEqual(0, self.marionette.execute_script(sentPass1 + returnSyncFailed)['failed']);
        self.assertEqual(1, self.marionette.execute_script(sentPass2 + returnSyncPassed)['passed']);

        self.marionette.set_script_timeout(1000)
        self.assertEqual(1, self.marionette.execute_async_script(sentFail1 + returnAsyncFailed)['failed']);
        self.assertEqual(0, self.marionette.execute_async_script(sentFail2 + returnAsyncPassed)['passed']);
        self.assertEqual(0, self.marionette.execute_async_script(sentPass1 + returnAsyncFailed)['failed']);
        self.assertEqual(1, self.marionette.execute_async_script(sentPass2 + returnAsyncPassed)['passed']);

