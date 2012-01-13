/*
 * Launch a Gaia app; see CommonTestCase.launch_gaia_app in 
 * marionette.py for implementation.  The iframe that the app is loaded
 * in will get passed to this script as _marionetteParams[0].
 */
MARIONETTE_LAUNCH_APP = '../sms/sms.html';
MARIONETTE_TIMEOUT = 1000;

/*
 * Verify that the <header> element of the content loaded in the 
 * iframe contains an <h1> element with the text 'SMS'.
 */
var frame = __marionetteParams[0];
Marionette.is('SMS', frame.contentWindow.document.getElementsByTagName('header')[0].getElementsByTagName('h1')[0].innerHTML);

/* more tests here.... */

Marionette.finish();

