/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

MARIONETTE_TIMEOUT = 1000;

/* this test will fail */

setTimeout(function() { 
    Marionette.is(1, 2); 
    Marionette.finish();
}, 100);
Marionette.isnot(1, 1);
Marionette.ok(1 == 2);


