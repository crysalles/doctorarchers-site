/**
 * Contact form: submit in place instead of navigating away.
 *
 * This is an enhancement only. With JavaScript off, the form does a plain POST
 * to /api/contact and the Function answers with its own confirmation page, so
 * nobody is left without a working form.
 */
(function () {
  "use strict";

  var form = document.getElementById("contact-form-el");
  if (!form) { return; }

  var status = document.getElementById("cf-status");
  var button = form.querySelector('button[type="submit"]');
  var ts = form.querySelector('input[name="ts"]');

  // Stamp the render time. The Function rejects anything posted within a few
  // seconds of this, which no human can type a message in.
  if (ts) { ts.value = String(Date.now()); }

  function say(message, ok) {
    if (!status) { return; }
    status.textContent = message;
    status.className = "contact-status " + (ok ? "is-ok" : "is-error");
    status.hidden = false;
  }

  form.addEventListener("submit", function (event) {
    if (!window.fetch) { return; }  // let the browser post it the old way
    event.preventDefault();

    var label = button ? button.textContent : "";
    if (button) { button.disabled = true; button.textContent = "Sending…"; }
    if (status) { status.hidden = true; }

    fetch(form.getAttribute("action"), {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" },
    })
      .then(function (res) {
        return res.json().catch(function () {
          return { ok: false, message: "Something went wrong. Please try again." };
        });
      })
      .then(function (data) {
        if (data && data.ok) {
          form.hidden = true;
          say(data.message || "Your message has been sent. Thank you.", true);
        } else {
          say((data && data.message) || "Something went wrong. Please try again.", false);
        }
      })
      .catch(function () {
        say("Your message could not be sent just now. Please try again in a few minutes.", false);
      })
      .then(function () {
        if (button) { button.disabled = false; button.textContent = label; }
      });
  });
})();
