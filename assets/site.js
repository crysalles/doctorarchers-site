/* DoctorArchers.com — shared, minimal, optional JS.
   Every page works fully without it (the nav simply wraps instead of
   collapsing). Jobs:
   1. Mobile nav toggle (progressive enhancement).
   2. Close the Shop menu on outside click / Escape.
   3. Pre-launch guard: block clicks and form submits that point at an
      unfilled [BRACKET] placeholder and show a gentle note instead,
      so the site previews safely before every link is wired up. */
(function () {
  "use strict";

  document.body.classList.add("js");

  /* ---- 1. Mobile nav toggle ---- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---- 2. Shop menu: close on outside click / Escape ---- */
  var shop = document.querySelector(".shop-menu");
  if (shop) {
    document.addEventListener("click", function (e) {
      if (shop.open && !shop.contains(e.target)) { shop.open = false; }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && shop.open) {
        shop.open = false;
        shop.querySelector("summary").focus();
      }
    });
  }

  /* ---- 3. Placeholder guard ---- */
  function isPlaceholder(v) { return !v || v.indexOf("[") !== -1; }

  var note = null;
  var noteTimer = null;
  function showNote(msg) {
    if (!note) {
      note = document.createElement("div");
      note.className = "guard-note";
      note.setAttribute("role", "status");
      document.body.appendChild(note);
    }
    note.textContent = msg;
    clearTimeout(noteTimer);
    noteTimer = setTimeout(function () {
      if (note) { note.remove(); note = null; }
    }, 7000);
  }

  // Links whose destination is still a [PLACEHOLDER]
  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest("a[href]") : null;
    if (a && isPlaceholder(a.getAttribute("href"))) {
      e.preventDefault();
      showNote("This link is not connected yet. It will go live once the address is added (see README.md).");
    }
  });

  // Forms whose action is still a [PLACEHOLDER]
  Array.prototype.forEach.call(document.querySelectorAll("form"), function (form) {
    form.addEventListener("submit", function (e) {
      if (isPlaceholder(form.getAttribute("action"))) {
        e.preventDefault();
        var inline = form.querySelector("[data-form-note]");
        if (inline) { inline.classList.add("show"); }
        else { showNote("This form is not connected yet. Add your provider's form action first (see README.md)."); }
      }
    });
  });
}());
