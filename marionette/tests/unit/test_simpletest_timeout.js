/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

MARIONETTE_TIMEOUT = 100;

/* this test will timeout */

function do_test() {
  Marionette.is(1, 1);
  Marionette.isnot(1, 2);
  Marionette.ok(1 == 1);
  Marionette.finish();
}

setTimeout(do_test, 1000);
