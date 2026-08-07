# Deploying book.laveenaarchers.com

The site is on **Cloudflare Pages**, project `doctorarchers-site`. It is live at
<https://book.laveenaarchers.com>.

> **This file used to describe a Netlify launch.** That was the original plan and
> it is no longer how anything works: the host is Cloudflare Pages, the contact
> form is a Pages Function rather than Netlify Forms, and the DNS warnings in the
> old version named Google Workspace MX records this domain does not have.
> Rewritten 2026-08-07. If you find another document still saying Netlify, it is
> out of date — `README.md` had the same problem.

---

## Deploy

```bash
python3 build.py && python3 stage-deploy.py --deploy
```

That is the whole thing. It renders `posts/*.md` into `blog/`, assembles `dist/`,
and uploads `dist/` to Pages.

To look before you publish, run the two steps separately:

```bash
python3 build.py
python3 stage-deploy.py     # assembles dist/, deploys nothing
python3 check-site.py       # exits non-zero if anything is wrong
npx wrangler@4 pages deploy dist --project-name doctorarchers-site --branch main
```

### Never `wrangler pages deploy .`

Deploying the repo root uploads **every file in the working tree**. That is how a
complete unpublished book manuscript, all eight future-dated draft posts,
`build.py` and the internal working notes were once publicly fetchable in
production, at 200, with no guessing required.

`stage-deploy.py` exists to prevent that. It is an **allowlist**: a file reaches
`dist/` only if a rule in its `ALLOW` list names it, and it hard-fails if a page
it expects is missing. A denylist would fail silently and permanently — add a new
manuscript, forget to exclude it, and it is public until someone notices.

`.assetsignore` does **not** work here. It is a Workers-assets feature and the
`wrangler pages deploy` code path ignores it entirely — verified against wrangler
4.120.0 by deploying with one in place and watching the excluded files come back
200. Do not reach for it.

### `check-site.py`

Gates the deploy on broken links, JSON-LD that does not parse, canonicals
pointing at redirects, images missing `alt`, an above-the-fold image marked
`loading="lazy"`, `og:image` pointing at AVIF/WebP, and `dist/` containing
anything it should not. Every check is there because that exact thing was broken
once. It runs automatically in CI before every deploy.

---

## Scheduled posts

A post with a **future `date:`** is scheduled, not published. `build.py` holds it
back and does not render it.

**Never run `python3 build.py --all`.** That renders everything including
unpublished drafts, and deploying that output puts unreviewed work live.

`.github/workflows/publish-scheduled-posts.yml` runs daily at **19:00 UTC** (noon
in Arizona, which does not observe DST). If a post has come due it builds,
commits, pushes, stages, runs `check-site.py`, and deploys — with no human in the
loop at that point.

**Committing and pushing a post with a future date is the point of no manual
return.** Treat it as approving that post for publication on its date.

The job needs one repository secret, `CLOUDFLARE_API_TOKEN`, with the
**Cloudflare Pages: Edit** permission. It is set and working — the last few
`Publish scheduled post(s):` commits came from it. Without the secret the job
still builds and commits, then fails loudly rather than deploying silently.

---

## Domains and DNS

DNS is on Cloudflare nameservers (`johnathan.ns.cloudflare.com`,
`blakely.ns.cloudflare.com`).

**Three hostnames are custom domains on the same Pages project**, so all three
serve identical content:

| Hostname | Status |
|---|---|
| `book.laveenaarchers.com` | canonical — every canonical tag, sitemap URL and schema `@id` points here |
| `laveenaarchers.com` | serves 200, **should 301 to `book.`** |
| `www.laveenaarchers.com` | serves 200, **should 301 to `book.`** |

Right now canonical tags are the only thing consolidating the three. To fix it,
create a **Redirect Rule first**, then remove the apex and www custom domains
from the Pages project. Doing it in the other order leaves the apex resolving to
Pages with no route, which breaks it.

### Email — do not touch MX

`laveenaarchers.com` uses **Namecheap email forwarding**:

```
10 eforward1.registrar-servers.com.    10 eforward2.registrar-servers.com.
10 eforward3.registrar-servers.com.    15 eforward4.registrar-servers.com.
20 eforward5.registrar-servers.com.
```

Website records (A/CNAME) and mail records (MX) are independent — changing where
the site points does not affect email. The previous version of this file warned
at length about preserving **Google Workspace** MX records. This domain does not
have them, and following that advice would replace working forwarding with mail
routing for an account that isn't there.

---

## The contact form

`contact.html` posts to `/api/contact`, a **Pages Function** at
`functions/api/contact.js`. It sends through Cloudflare's Email Sending REST API.

Netlify Forms is gone. When the site moved to Cloudflare Pages it kept silently
discarding every submission, which is why the Function exists.

It needs four values set in the dashboard under **Workers & Pages →
doctorarchers-site → Settings → Variables and Secrets**. None of them may ever
appear in the repo or in any HTML:

| Name | Kind | What it is |
|---|---|---|
| `CF_ACCOUNT_ID` | variable | Cloudflare account id |
| `EMAIL_API_TOKEN` | **secret** | API token with email sending permission |
| `CONTACT_TO` | **secret** | a **verified destination address** on the account |
| `CONTACT_FROM` | variable | an address on a domain with Email Routing enabled |

Sending to a verified destination address is free on every plan. Point
`CONTACT_TO` anywhere else and the send fails — that is the constraint that keeps
this costing nothing.

Spam defense is a honeypot field plus a render timestamp, with no storage.

---

## Cache

Cloudflare caches static assets for **7 days** (`s-maxage=604800`). Removing a
file from a deploy does not evict it from the edge — a deleted file keeps serving
to anyone with the URL until the cache is purged.

Purge from the dashboard: **Caching → Configuration → Purge Everything**. The
wrangler OAuth token holds only `zone:read` and **cannot** purge, so this is not
scriptable with the current credentials.

To check whether something is really gone, request it with a junk query string.
That bypasses the cached copy and shows you what the origin actually has:

```bash
curl -sI "https://book.laveenaarchers.com/whatever?cachebust=$RANDOM"
```

---

## Rollback

Every deploy is an immutable snapshot and Pages keeps them all.

```bash
npx wrangler@4 pages deployment list --project-name doctorarchers-site
```

Roll back from the dashboard (**Workers & Pages → doctorarchers-site →
Deployments → ⋯ → Rollback**), or redeploy a known-good tree. Rolling back does
not purge the cache.

---

## Checklist after a deploy

- [ ] `check-site.py` passed (CI runs it; run it yourself for a manual deploy).
- [ ] Pages load on phone and desktop.
- [ ] A test message through the contact form arrives.
- [ ] Nothing private is public — spot-check a manuscript and a scheduled post:
      `curl -sI https://book.laveenaarchers.com/BOOK_still-normal-manuscript.md`
      and `.../posts/why-you-wake-at-3am.md` should both be **404**.
- [ ] Booking (OnceHub), Shop Labs (Rupa) and Shop Supplements (Fullscript)
      links open.

## Related

- `README.md` — site structure, Kit setup, writing posts
- `stage-deploy.py` — the allowlist; read `ALLOW` and `DENY` before adding files
- `check-site.py` — pre-deploy checks
- `CLAUDE.md` — the fact-check protocol that must run before any post is scheduled
