/**
 * POST /api/contact — Cloudflare Pages Function backing the contact form.
 *
 * Replaces Netlify Forms, which stopped working when the site moved to
 * Cloudflare Pages and was silently discarding every submission.
 *
 * WHY THE REST API AND NOT A BINDING: Cloudflare's `send_email` binding is a
 * Workers feature and is not among the bindings supported by Pages Functions,
 * so this calls the Email Sending REST API instead.
 *
 * WHY THIS COSTS NOTHING: paid Email Sending is only needed to mail arbitrary
 * recipients. Sending to a *verified destination address* on the account is
 * free on every plan, including Workers Free, and does not count against any
 * quota. This form only ever mails one fixed address, so CONTACT_TO must be a
 * verified destination address and CONTACT_FROM must sit on a domain that has
 * Email Routing enabled. Point CONTACT_TO anywhere else and the send fails.
 *
 * REQUIRED environment variables, set in the Cloudflare dashboard under
 * Workers & Pages -> doctorarchers-site -> Settings -> Variables and Secrets.
 * None of these may ever appear in the repo or in any HTML:
 *
 *   CF_ACCOUNT_ID    plain variable  Cloudflare account id
 *   EMAIL_API_TOKEN  SECRET          API token with email sending permission
 *   CONTACT_TO       SECRET          verified destination address to deliver to
 *   CONTACT_FROM     plain variable  e.g. contact@laveenaarchers.com, on a
 *                                    domain with Email Routing enabled
 *
 * Spam defense without any storage: a honeypot field that humans never see,
 * plus a render timestamp. Bots post instantly; people take longer than three
 * seconds to write a message.
 */

const MIN_SECONDS_ON_PAGE = 3;
const MAX_MESSAGE = 5000;
const MAX_FIELD = 200;

/** Minimal HTML escaping for values interpolated into the email body. */
function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

/** A small styled page, so the no-JavaScript path still looks like the site. */
function page(title, heading, body, status) {
  return new Response(
    `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${esc(title)} — Rev. Dr. LaVeena Archers</title>
<link rel="stylesheet" href="/assets/styles.css"></head>
<body><main id="main"><section class="page-hero"><div class="wrap narrow" style="margin-inline:auto">
<h1>${esc(heading)}</h1><p class="lede">${body}</p>
<p style="margin-top:1.5rem"><a class="btn btn-primary" href="/">Back to the site</a>
&nbsp;<a class="btn btn-outline" href="/blog/index.html">Read the library</a></p>
</div></section></main></body></html>`,
    { status, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } }
  );
}

/** Respond as JSON when the browser asked for it, otherwise as a page. */
function reply(wantsJson, ok, httpStatus, heading, message) {
  if (wantsJson) {
    return new Response(JSON.stringify({ ok, message }), {
      status: httpStatus,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  }
  return page(heading, heading, message, httpStatus);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const wantsJson = (request.headers.get("accept") || "").includes("application/json");

  let form;
  try {
    form = await request.formData();
  } catch {
    return reply(wantsJson, false, 400, "Something went wrong", "That submission could not be read. Please try again.");
  }

  const honeypot = (form.get("bot-field") || "").toString().trim();
  const name = (form.get("name") || "").toString().trim().slice(0, MAX_FIELD);
  const email = (form.get("email") || "").toString().trim().slice(0, MAX_FIELD);
  const subject = (form.get("subject") || "").toString().trim().slice(0, MAX_FIELD);
  const message = (form.get("message") || "").toString().trim().slice(0, MAX_MESSAGE);
  const renderedAt = parseInt((form.get("ts") || "0").toString(), 10);

  // Honeypot filled, or submitted implausibly fast. Answer as if it worked so
  // a bot learns nothing, but send nothing.
  const tooFast = Number.isFinite(renderedAt) && renderedAt > 0 &&
    (Date.now() - renderedAt) / 1000 < MIN_SECONDS_ON_PAGE;
  if (honeypot || tooFast) {
    return reply(wantsJson, true, 200, "Thank you", "Your message has been sent.");
  }

  if (!name || !email || !message) {
    return reply(wantsJson, false, 400, "Something is missing",
      "Please fill in your name, your email, and a message, then send again.");
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return reply(wantsJson, false, 400, "That email looks wrong",
      "Please check the email address and send again.");
  }

  const { CF_ACCOUNT_ID, EMAIL_API_TOKEN, CONTACT_TO, CONTACT_FROM } = env;
  if (!CF_ACCOUNT_ID || !EMAIL_API_TOKEN || !CONTACT_TO || !CONTACT_FROM) {
    // Better a visible failure than a message quietly vanishing, which is
    // exactly what the Netlify form was doing.
    console.error("contact form: missing env vars", {
      CF_ACCOUNT_ID: !!CF_ACCOUNT_ID, EMAIL_API_TOKEN: !!EMAIL_API_TOKEN,
      CONTACT_TO: !!CONTACT_TO, CONTACT_FROM: !!CONTACT_FROM,
    });
    return reply(wantsJson, false, 503, "The form is not available",
      "Something is misconfigured on my end and your message was not sent. " +
      "Nothing was lost on your side, but please try again later.");
  }

  const text =
    `New message from the contact form\n\n` +
    `Name:    ${name}\n` +
    `Email:   ${email}\n` +
    `Subject: ${subject || "(none given)"}\n\n` +
    `${message}\n`;

  const html =
    `<h2>New message from the contact form</h2>` +
    `<p><strong>Name:</strong> ${esc(name)}<br>` +
    `<strong>Email:</strong> ${esc(email)}<br>` +
    `<strong>Subject:</strong> ${esc(subject) || "(none given)"}</p>` +
    `<hr><p style="white-space:pre-wrap">${esc(message)}</p>`;

  try {
    const res = await fetch(
      `https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/email/sending/send`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${EMAIL_API_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          to: [{ address: CONTACT_TO }],
          from: { address: CONTACT_FROM, name: "DoctorArchers.com contact form" },
          reply_to: { address: email, name: name },
          subject: subject ? `Contact form: ${subject}` : `Contact form message from ${name}`,
          text,
          html,
        }),
      }
    );

    if (!res.ok) {
      console.error("contact form: email API returned", res.status, await res.text());
      return reply(wantsJson, false, 502, "That did not send",
        "Your message could not be delivered just now. Please try again in a few minutes.");
    }
  } catch (err) {
    console.error("contact form: email API threw", err && err.message);
    return reply(wantsJson, false, 502, "That did not send",
      "Your message could not be delivered just now. Please try again in a few minutes.");
  }

  return reply(wantsJson, true, 200, "Thank you",
    "Your message has been sent, and it goes straight to me. " +
    "I read every note, and I usually reply within a few days.");
}

/** Anything other than POST. */
export async function onRequest(context) {
  if (context.request.method === "POST") { return onRequestPost(context); }
  return new Response("Method not allowed", {
    status: 405,
    headers: { Allow: "POST", "Cache-Control": "no-store" },
  });
}
