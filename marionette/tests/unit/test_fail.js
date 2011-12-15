MARIONETTE_TIMEOUT = 1000;

/* this test will fail */

Marionette.is(1, 2);
Marionette.isnot(1, 1);
Marionette.ok(1 == 2);
Marionette.finish();

