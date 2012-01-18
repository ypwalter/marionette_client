/*
 * Launch a Gaia app; see CommonTestCase.launch_gaia_app in 
 * marionette.py for implementation.  The iframe that the app is loaded
 * in will get passed to this script as Marionette.namedArgs.appframe.
 */
MARIONETTE_LAUNCH_APP = '../sms/sms.html';
MARIONETTE_TIMEOUT = 1000;

/*
 * Verify that the <header> element of the content loaded in the 
 * iframe contains an <h1> element with the text 'SMS'.
 */
var frame = Marionette.namedArgs.appframe;
Marionette.is('SMS', frame.contentWindow.document.getElementsByTagName('header')[0].getElementsByTagName('h1')[0].innerHTML);

/* more tests here.... */

Marionette.finish();

