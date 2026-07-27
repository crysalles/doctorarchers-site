/* GLP-1 reflection tool — scoring.
 *
 * PRIVACY: this file never transmits anything. There is no fetch, no XHR, no
 * beacon, no form submission of answers. Everything below runs in the reader's
 * browser and the answers are discarded when the page closes. The email
 * sign-up further down the page is a separate form that collects an email
 * address and nothing else. That promise is made in the page copy, so please
 * keep it true if you edit this file.
 */
(function () {
  "use strict";

  var form = document.getElementById("glp1-quiz");
  if (!form) { return; }

  var FIT_Q = ["q1", "q2", "q3", "q4", "q5", "q6"];        // max 26
  var READY_Q = ["q7", "q8", "q9", "q10"];                  // max 8

  var FIT_BANDS = [
    { max: 6, name: "The foundations are still your best leverage",
      body: "On your own answers, the case for a medication is not yet the live question. That is not a brush-off. It means the things that would help you most are the ones already in your hands, and they have not yet been given a full run. Come back to this page in six months if that changes." },
    { max: 13, name: "A fair question, but not an urgent one",
      body: "There is something real here, and it is worth raising when you next see someone. It is also worth one more honest, tracked run at the foundations first, because the evidence is clear that they change what any medication has to do." },
    { max: 19, name: "Worth a conversation before long",
      body: "Your answers describe genuine health stakes alongside real effort already made. That combination is exactly what a prescriber needs to hear, and it is worth booking the conversation rather than waiting for things to declare themselves further." },
    { max: 99, name: "Worth taking to a prescriber now",
      body: "You are describing serious stakes and a sustained effort that has not got you where your health needs you to be. That is the situation these medications were developed for. What follows is a decision for you and a qualified prescriber, and it deserves a proper appointment rather than a rushed one." }
  ];

  var READY_BANDS = [
    { max: 3, name: "Practical gaps to close first",
      body: "Cost, muscle protection, and having a prescriber who knows your history are what decide whether any of this works in a real life. Closing those gaps is useful whichever way you go." },
    { max: 6, name: "Mostly there, with a gap or two",
      body: "You have most of the practical pieces. Look at whichever answers scored lowest, because those are the ones most likely to trip up a plan that is otherwise sound." },
    { max: 99, name: "Practically ready",
      body: "Cost, muscle protection, prescriber access and your own openness are all in reasonable shape. Whatever you decide, you are positioned to carry it out properly." }
  ];

  function sum(ids) {
    var total = 0, answered = 0;
    ids.forEach(function (id) {
      var picked = form.querySelector('input[name="' + id + '"]:checked');
      if (picked) { total += parseInt(picked.value, 10); answered++; }
    });
    return { total: total, answered: answered };
  }

  function band(score, bands) {
    for (var i = 0; i < bands.length; i++) {
      if (score <= bands[i].max) { return bands[i]; }
    }
    return bands[bands.length - 1];
  }

  function combined(fit, ready) {
    if (fit >= 14 && ready <= 3) {
      return "Notice the shape of your two scores. The health case is there, and the practical footing is not yet. That is a solvable problem and a common one, and it is worth solving before you start rather than after.";
    }
    if (fit <= 6 && ready >= 7) {
      return "Notice the shape of your two scores. You are well prepared for a tool your own answers suggest you may not need yet. That preparation is not wasted. Pointed at the foundations, it is exactly what makes them work.";
    }
    if (fit >= 14 && ready >= 7) {
      return "Both of your scores point the same way. You have the health case and the practical footing, which means the useful next step is a proper conversation rather than more reading.";
    }
    return "Read the two scores together rather than adding them. One describes whether the question is live for you. The other describes whether the answer would hold up in your actual life.";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();   // nothing is ever sent

    var fit = sum(FIT_Q);
    var ready = sum(READY_Q);
    var missing = (FIT_Q.length + READY_Q.length) - (fit.answered + ready.answered);

    var notice = document.getElementById("quiz-missing");
    if (missing > 0) {
      notice.textContent = "You have " + missing + (missing === 1 ? " question" : " questions") +
        " still to answer. The score only means anything with all ten.";
      notice.classList.add("show");
      notice.focus();
      return;
    }
    notice.classList.remove("show");

    var fitBand = band(fit.total, FIT_BANDS);
    var readyBand = band(ready.total, READY_BANDS);

    document.getElementById("fit-score").textContent = fit.total + " out of 26";
    document.getElementById("fit-band").textContent = fitBand.name;
    document.getElementById("fit-body").textContent = fitBand.body;
    document.getElementById("ready-score").textContent = ready.total + " out of 8";
    document.getElementById("ready-band").textContent = readyBand.name;
    document.getElementById("ready-body").textContent = readyBand.body;
    document.getElementById("combined-note").textContent = combined(fit.total, ready.total);

    var results = document.getElementById("quiz-results");
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
    results.focus();
  });

  form.addEventListener("reset", function () {
    document.getElementById("quiz-results").hidden = true;
    document.getElementById("quiz-missing").classList.remove("show");
  });
}());
