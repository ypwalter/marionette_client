MARIONETTE_CONTEXT="chrome";
MARIONETTE_TIMEOUT=60000;

function waitForExplicitFinish() {}

const kDefaultWait = 20000;
// Wait for a condition and call a supplied callback if condition is met within
// alloted time. If condition is not met, cause a hard failure,
// stopping the test.
function waitFor(callback, test, timeout) {
  if (test()) {
    callback();
    return;
  }

  timeout = timeout || Date.now();
  if (Date.now() - timeout > kDefaultWait) {
    ok(false, 'waitFor timeout', test.toString());
    finish();
  }
  setTimeout(waitFor, 50, callback, test, timeout);
}

// The browser-chrome tests define a test() method but do not explicitly
// call it, so we do that here.
test();

