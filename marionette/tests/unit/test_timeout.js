MARIONETTE_TIMEOUT = 100;

/* this test will timeout */

function do_test() {
  Marionette.is(1, 1);
  Marionette.isnot(1, 2);
  Marionette.ok(1 == 1);
  Marionette.finish();
}

setTimeout(do_test, 1000);
