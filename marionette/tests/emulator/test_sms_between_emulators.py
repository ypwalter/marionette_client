from marionette_test import *


class SMSTest(MarionetteTestCase):

    def test_sms_between_emulators(self):
        # Tests always have one emulator available as self.marionette; we'll
        # use this for the receiving emulator.  We'll also launch a second
        # emulator to use as the sender.
        sender = self.get_new_emulator()
        receiver = self.marionette

        # Setup the event listsener on the receiver, which should store
        # a global variable when an SMS is received.
        message = 'hello world!'
        receiver.set_context("content")
        self.assertTrue(receiver.execute_script("return navigator.mozSms != undefined;"))
        receiver.execute_script("""
window.wrappedJSObject.smsreceived = "none";
navigator.mozSms.addEventListener("received", function(e) {
    window.wrappedJSObject.smsreceived = e.message;
});
""")

        # Send the SMS from the sender.
        sender.set_context("content")
        sender.execute_script("""
navigator.mozSms.send("%d", "%s");
""" % (receiver.emulator.port, message))

        # On the receiver, wait up to 30s for an SMS to be received, by 
        # checking the value of the global var that the listener will 
        # change.
        receiver.set_script_timeout(30000)
        received = receiver.execute_async_script("""
        function check_sms() {
            if (window.wrappedJSObject.smsreceived != "none") {
                marionetteScriptFinished(window.wrappedJSObject.smsreceived);
            }
            else {
                setTimeout(check_sms, 500);
            }
        }
        setTimeout(check_sms, 0);
    """)
        self.assertEqual(received, message)


