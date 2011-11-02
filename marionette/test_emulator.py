import time
from marionette import Marionette, HTMLElement

#
# Test that Marionette can manage multiple emulators.
# Before running this code, you should have built B2G with the config-qemu
# configuration, see 
# https://wiki.mozilla.org/Auto-tools/Projects/Marionette/DevNotes#Running_B2G_on_an_emulator
#
# You should also set your B2G_HOME environment variable to point to the
# directory where the B2G code lives.
#

if __name__ == '__main__':
    # launch two instance of Marionette, each with their own emulator
    driver1 = Marionette(emulator=True, port=2626)
    assert(driver1.emulator.is_running)
    assert(driver1.emulator.port)
    print 'emulator1 is running on port', driver1.emulator.port

    driver2 = Marionette(emulator=True, port=2626)
    assert(driver2.emulator.is_running)
    assert(driver2.emulator.port)
    print 'emulator2 is running on port', driver2.emulator.port

    time.sleep(90)

    # shutdown both emulators
    assert(driver2.emulator.close() == 0)
    assert(not driver2.emulator.is_running)
    assert(driver1.emulator.close() == 0)
    assert(not driver1.emulator.is_running)


