# Setting up /api/contact

Runbook for the contact and corrections forms. Both post to `/api/contact`
(`functions/api/contact.js`). If either returns **503**, the env vars are not set
and this is the page to follow.

The function is written to fail loudly rather than swallow a message, because the
Netlify form it replaced was silently discarding every submission. A 503 means
nothing was lost — it means nothing was sent.

---

## Prerequisite: Email Routing on the sending domain

`CONTACT_FROM` must sit on a domain with Cloudflare Email Routing enabled. Sending
to a **verified destination address** is free on every plan; that is the only thing
this form ever does.

As of 2 August 2026, `laveenaarchers.com` had Email Routing **off** — its MX records
pointed at Namecheap forwarding (`eforward1.registrar-servers.com`). DNS for the
domain is on Cloudflare, so enabling it is straightforward, but **enabling Email
Routing replaces the MX records**. Confirmed with LaVeena that nothing currently
receives mail at `@laveenaarchers.com`, so this is safe.

Check before touching it again:

```bash
dig +short MX laveenaarchers.com
```

- `route1.mx.cloudflare.net` etc. → Email Routing is on.
- anything else → it is off, and turning it on will replace whatever is there.

---

## Steps

**1. Enable Email Routing** on `laveenaarchers.com` (Cloudflare dashboard → the
domain → Email → Email Routing). Let it create the MX and SPF records.

**2. Verify the destination address.** Add the address you actually read mail at as
a destination and click the confirmation link Cloudflare emails you. This is the
value for `CONTACT_TO`. It does not change anything about that mailbox's own DNS.

**3. Create an API token** with permission to send email on this account
(My Profile → API Tokens, or the account-level token page). Scope it to this account
and nothing else. This is the value for `EMAIL_API_TOKEN`.

**4. Set all four variables** on the Pages project: Workers & Pages →
`doctorarchers-site` → Settings → Variables and Secrets, on the **Production**
environment.

| Name | Type | Value |
|---|---|---|
| `CF_ACCOUNT_ID` | plain variable | `1d18bf879817a7681e338e3682580a87` |
| `CONTACT_FROM` | plain variable | e.g. `contact@laveenaarchers.com` |
| `CONTACT_TO` | secret | the destination address verified in step 2 |
| `EMAIL_API_TOKEN` | secret | the token from step 3 |

**5. Redeploy.** This is the step that gets missed. **Pages does not apply
environment variable changes to the running site until the next deployment.** Setting
the variables and then testing the form will still return 503.

**6. Test both forms**, not just one. `contact.html` and `corrections.html` both
post here.

---

## Checking it

```bash
npx wrangler pages secret list --project-name doctorarchers-site
```

Lists the secrets only. Plain variables are not shown by this command; check those in
the dashboard.

A failing send logs the reason. Look at the Pages function logs for
`contact form: missing env vars` (a variable is absent) or
`contact form: email API returned` (the send itself was rejected — usually
`CONTACT_TO` is not a verified destination, or `CONTACT_FROM` is on a domain without
Email Routing).

---

## What must never happen

None of these values may appear in the repo, in any HTML, or in a build log. They are
set in the dashboard only. `CF_ACCOUNT_ID` is written above because it is an account
identifier rather than a credential; the token and the destination address are not,
and are not recorded here.
