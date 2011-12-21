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

import os
from marionette_test import MarionetteTestCase
from marionette import HTMLElement
from errors import NoSuchElementException

class TestElements(MarionetteTestCase):
    def test_id(self):
        #TODO: use the webserver when we have one, and in test.html, change the link to a local one
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
        self.marionette.navigate(test_html)
        self.assertEqual(HTMLElement, type(self.marionette.find_element("id", "mozLink")))

    def test_tag_name(self):
        #TODO: use the webserver when we have one, and in test.html, change the link to a local one
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
        self.marionette.navigate(test_html)
        self.assertEqual(HTMLElement, type(self.marionette.find_element("tag name", "body")))

    def test_class_name(self):
        #TODO: use the webserver when we have one, and in test.html, change the link to a local one
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
        self.marionette.navigate(test_html)
        self.assertEqual(HTMLElement, type(self.marionette.find_element("class name", "linkClass")))

    def test_name(self):
        #TODO: use the webserver when we have one, and in test.html, change the link to a local one
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
        self.marionette.navigate(test_html)
        self.assertEqual(HTMLElement, type(self.marionette.find_element("name", "myInput")))
    
    def test_selector(self):
        #not supported yet
        pass

    def test_link_text(self):
        #not supported yet
        pass

    def test_partial_link_text(self):
        #not supported yet
        pass

    def test_xpath(self):
        #not supported yet
        pass

    def test_not_found(self):
        #TODO: use the webserver when we have one, and in test.html, change the link to a local one
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
        self.marionette.navigate(test_html)
        self.assertRaises(NoSuchElementException, self.marionette.find_element, "id", "I'm not on the page")

    def test_timeout(self):
        #TODO: use the webserver when we have one, and in test.html, change the link to a local one
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
        self.marionette.navigate(test_html)
        self.assertRaises(NoSuchElementException, self.marionette.find_element, "id", "newDiv")
        self.assertTrue(True, self.marionette.set_search_timeout(4000))
        test_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
        self.marionette.navigate(test_html)
        self.assertEqual(HTMLElement, type(self.marionette.find_element("id", "newDiv")))
