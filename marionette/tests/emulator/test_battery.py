from marionette import Marionette, HTMLElement

if __name__ == '__main__':
    # before running this test, launch Fennec in an emulator
    qemu = Marionette(connectToRunningEmulator=True, port=2929)
    assert(qemu.emulator.is_running)
    assert(qemu.start_session())
    qemu.set_script_timeout(10000)

    # verify the emulator's battery status as reported by Gecko is the same as
    # reported by the device
    moz_level = qemu.execute_script("return navigator.mozBattery.level;")
    assert(moz_level == qemu.emulator.battery.level)

    moz_charging = qemu.execute_script("return navigator.mozBattery.charging;")
    emulator_charging = qemu.emulator.battery.charging
    assert(moz_charging == emulator_charging)

    # setup event listeners to be notified when the level or charging status 
    # changes
    assert(qemu.execute_script("""
    window._levelchanged = false;
    window._chargingchanged = false;
    navigator.mozBattery.addEventListener("levelchange", function() {
        window._levelchanged = true;
    });
    navigator.mozBattery.addEventListener("chargingchange", function() {
        window._chargingchanged = true;
    });
    return true;
"""))

    # set the battery to a new level, and verify
    if moz_level > 0.2:
        new_level = moz_level - 0.1
    else:
        new_level = moz_level + 0.1
    qemu.emulator.battery.level = new_level

    # XXX: do we need to wait here a bit?  this WFM...
    moz_level = qemu.emulator.battery.level
    assert(int(new_level * 100) == int(moz_level * 100))

    # verify that the 'levelchange' listener was hit
    level_changed = qemu.execute_async_script("""
    var callback = arguments[arguments.length - 1];
    function check_level_change() {
        if (window._levelchanged) {
            callback(window._levelchanged);
        }
        else {
            setTimeout(check_level_change, 500);
        }
    }
    setTimeout(check_level_change, 0);
""")
    assert(level_changed)

    # set the battery charging state, and verify
    qemu.emulator.battery.charging = not emulator_charging
    new_emulator_charging_state = qemu.emulator.battery.charging
    assert(new_emulator_charging_state == (not emulator_charging))

    # verify that the 'chargingchange' listener was hit
    charging_changed = qemu.execute_async_script("""
    var callback = arguments[arguments.length - 1];
    function check_charging_change() {
        if (window._chargingchanged) {
            callback(window._chargingchanged);
        }
        else {
            setTimeout(check_charging_change, 500);
        }
    }
    setTimeout(check_charging_change, 0);
""")
    assert(charging_changed)

    # if we have set the charging state to 'off', set it back to 'on' to prevent
    # the emulator from sleeping
    if not new_emulator_charging_state:
        qemu.emulator.battery.charging = True

    print 'Test passed!'


