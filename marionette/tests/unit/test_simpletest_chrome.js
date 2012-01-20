MARIONETTE_TIMEOUT = 1000;
MARIONETTE_CONTEXT = 'chrome';

Marionette.is(1, 1, "test for Marionette.is()");
is(2, 2, "test for is()");
Marionette.isnot(1, 2, "test for Marionette.isnot()");
isnot(2, 3, "test for isnot()");
Marionette.ok(1 == 1, "test for Marionette.ok()");
ok(2 == 2, "test for ok()");
finish();

