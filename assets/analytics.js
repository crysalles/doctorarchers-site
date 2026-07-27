/* DoctorArchers.com — privacy-friendly analytics loader.
 *
 * Cloudflare Web Analytics: free, cookieless, no personal data collected,
 * and therefore no cookie-consent banner required.
 *
 * ---------------------------------------------------------------------
 * TO TURN ANALYTICS ON (one-time, ~2 minutes):
 *
 *   1. Create a free account at https://dash.cloudflare.com/sign-up
 *   2. Go to: Analytics & Logs  ->  Web Analytics  ->  Add a site
 *   3. Enter the hostname:  book.laveenaarchers.com
 *   4. Cloudflare shows you a snippet containing  token: "abc123..."
 *      Copy ONLY that token string.
 *   5. Paste it between the quotes on the TOKEN line below, save, and push.
 *
 * Until a token is filled in, this file does nothing at all — no requests,
 * no errors. Every page already loads it, so filling in the token switches
 * analytics on across the whole site at once.
 * ---------------------------------------------------------------------
 */
(function () {
  "use strict";

  var TOKEN = "3fe52d86007a40b9a024cb7608b8aeb5";   // book.laveenaarchers.com

  // Not configured yet (or still a [PLACEHOLDER]) — do nothing.
  if (!TOKEN || TOKEN.indexOf("[") !== -1) { return; }

  // Never count local previews as real traffic.
  var host = location.hostname;
  if (host === "localhost" || host === "127.0.0.1" || host === "" ||
      host.indexOf("--") !== -1) {          // Netlify deploy previews
    return;
  }

  var s = document.createElement("script");
  s.defer = true;
  s.src = "https://static.cloudflareinsights.com/beacon.min.js";
  s.setAttribute("data-cf-beacon", JSON.stringify({ token: TOKEN }));
  document.head.appendChild(s);
}());
