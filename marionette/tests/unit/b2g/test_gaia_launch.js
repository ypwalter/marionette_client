/*
 * Launch a Gaia app; see CommonTestCase.launch_gaia_app in 
 * marionette.py for implementation.  The iframe that the app is loaded
 * in will get passed to this script as Marionette.namedArgs.appframe.
 */
MARIONETTE_LAUNCH_APP = '../sms/sms.html';
MARIONETTE_TIMEOUT = 1000;

/*
 * Verify that the <title> element of the content loaded in the 
 * iframe contains the text 'SMS'.
 */
var frame = Marionette.namedArgs.appframe;
Marionette.is('Messages', frame.contentWindow.document.getElementsByTagName('title')[0].innerHTML);

/* more tests here.... */

finish();

