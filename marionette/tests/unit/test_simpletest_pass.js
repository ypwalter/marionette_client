/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

MARIONETTE_TIMEOUT = 1000;

Marionette.is(1, 1, "test for Marionette.is()");
is(2, 2, "test for is()");
Marionette.isnot(1, 2, "test for Marionette.isnot()");
isnot(2, 3, "test for isnot()");
Marionette.ok(1 == 1, "test for Marionette.ok()");
ok(2 == 2, "test for ok()");
setTimeout(finish, 100);

