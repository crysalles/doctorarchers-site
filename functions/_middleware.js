/**
 * Send laveenaarchers.com and www.laveenaarchers.com to book.laveenaarchers.com.
 *
 * All three hostnames are custom domains on the same Pages project, so all three
 * served byte-identical content at 200. Canonical tags were the only thing
 * consolidating them, and a canonical is a hint — a 301 is not.
 *
 * WHY THIS IS HERE RATHER THAN A CLOUDFLARE REDIRECT RULE: a zone-level Redirect
 * Rule is the better tool. It runs at the edge before any Worker, costs no
 * invocations, and is visible in the dashboard next to everything else. This
 * exists only because the credentials available could not reach the Rulesets API
 * (the wrangler OAuth token carries zone:read, which is not enough to read or
 * write rulesets, and account-level Bulk Redirects were closed too).
 *
 * IF YOU CREATE THE REDIRECT RULE, DELETE THIS FILE AND _routes.json. Running
 * both is harmless but pointless: the rule fires first and this never sees the
 * request. Dashboard path is laveenaarchers.com -> Rules -> Redirect Rules, then
 * remove the apex and www custom domains from the Pages project — in that order,
 * because removing the domains first leaves them resolving to Pages with no
 * route.
 *
 * FAIL-SAFE BY CONSTRUCTION. Every path that is not exactly one of the two
 * redirected hostnames falls through to context.next() untouched, and the whole
 * body is wrapped so that a throw serves the page rather than an error. This
 * file sits in front of every HTML request on the site; it must never be able to
 * take the site down.
 *
 * Static assets never reach here — _routes.json excludes /assets/*, so images
 * and CSS are served directly without a Worker invocation. The cost is one
 * invocation per HTML page view.
 */

const CANONICAL_HOST = "book.laveenaarchers.com";

// Exact matches only. A prefix or suffix test would catch hostnames nobody
// intended, and the preview deployments on *.pages.dev must pass through
// untouched or there is no way to test a build before it goes live.
const REDIRECT_FROM = new Set([
  "laveenaarchers.com",
  "www.laveenaarchers.com",
]);

export async function onRequest(context) {
  try {
    const url = new URL(context.request.url);

    if (REDIRECT_FROM.has(url.hostname)) {
      url.hostname = CANONICAL_HOST;
      url.protocol = "https:";
      url.port = "";
      // 301, not 302: this is permanent, and it is the whole point — a
      // temporary redirect would not consolidate the ranking signals that are
      // currently split three ways.
      return Response.redirect(url.toString(), 301);
    }

    return context.next();
  } catch {
    // Whatever went wrong, serving the page is better than serving an error.
    return context.next();
  }
}
