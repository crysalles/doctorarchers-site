# Deploy DoctorArchers.com — step by step

Your site is packaged and ready: **`doctorarchers-site-DEPLOY.zip`** (in Downloads).
Netlify is the recommended host because your contact form uses Netlify Forms.

---

## 🟢 CHOSEN PATH: launch on a subdomain (`book.doctorarchers.com`)

This is the plan. It is the **safe, email-proof** way to launch now while your
Squarespace site stays exactly as it is until it lapses (Feb 14, 2027). You are
only **adding** one subdomain record. You are **not** changing the apex domain,
and you are **not** touching your MX (email) records, so `hi@doctorarchers.com`
cannot be affected.

1. **Deploy the zip to Netlify.** Sign up at netlify.com (free), then drag
   `doctorarchers-site-DEPLOY.zip` onto the "drag and drop" deploy area. Netlify
   gives you a temporary address like `random-name.netlify.app`. Open it and
   click around; the whole site should work.
2. **Turn on the contact form.** Netlify → your site → **Forms** → it should show
   a "contact" form. **Form notifications → Add notification → Email** →
   `hi@doctorarchers.com`.
3. **Add the subdomain in Netlify.** Domain management → **Add a domain** → type
   **`book.doctorarchers.com`** → Netlify shows you the target to point it at
   (your `random-name.netlify.app`).
4. **Add ONE DNS record where doctorarchers.com's DNS lives** (Squarespace domains
   dashboard, or Namecheap Advanced DNS, wherever you manage it):

   | Type  | Host / Name | Value                        | TTL       |
   |-------|-------------|------------------------------|-----------|
   | CNAME | `book`      | `your-site-name.netlify.app` | Automatic |

   That is the whole DNS change. **Do not touch** the `@`/apex records, and **do
   not touch** any `MX` or `TXT` records. Your website and email keep working.
5. **HTTPS.** Once the record resolves (minutes to a couple of hours), Netlify
   auto-issues SSL for `book.doctorarchers.com`. Turn on **Force HTTPS**. Done:
   the book is live at **https://book.doctorarchers.com**.
6. **Later (optional), Feb 2027 or whenever:** to move the whole site onto the
   main `doctorarchers.com`, follow the full apex + MX instructions below. Not
   needed now.

> The rest of this document (apex A-record + the MX/email warnings) only applies
> if you later point the **root** `doctorarchers.com` at Netlify. For the
> subdomain launch above, you can ignore it.

---

## (Later) Full apex-domain deploy

Plan for about 30–45 minutes. Your current Squarespace site stays live until the
very last step (DNS), so nothing breaks while you set up.

> ⚠️ **The one thing not to skip:** when you change DNS, you must KEEP your Google
> Workspace **MX records** or email to **hi@doctorarchers.com stops working.**
> Step 5 tells you exactly how. Read it before you touch DNS.

---

## Step 0 — What to have ready (optional but ideal before launch)
The site deploys fine with a few placeholders still in, and the built-in guard
keeps unfinished buttons/forms safe (they just show a gentle note). For a clean
public launch, ideally fill these first (all locations are in `README.md`):
- **Kit**: opt-in form UID, newsletter form UID, and the Commerce product URL →
  `[KIT_OPTIN_FORM_UID]`, `[KIT_NEWSLETTER_FORM_UID]`, `[KIT_BOOK_PRODUCT_URL]`.
- **Images**: `[PORTRAIT_IMAGE_URL]`, `[BOOK_COVER_IMAGE_URL]`.
- **PMA signup**: `[PMA_SIGNUP_URL_OR_EMBED]`. **Privacy**: `[PRIVACY_DETAILS]`.
You can also launch now and fill them later — just re-deploy (Step 6) after edits.

---

## Step 1 — Create a Netlify account
Go to **netlify.com** → sign up (free). No credit card needed.

## Step 2 — Deploy the site (drag-and-drop)
1. In Netlify, open **Sites** → find the **"drag and drop"** deploy area
   (or **Add new site → Deploy manually**).
2. Drag **`doctorarchers-site-DEPLOY.zip`** onto it (or unzip and drag the folder).
3. Netlify gives you a temporary URL like `random-name.netlify.app`. Open it —
   your whole site should be live there. Click around and check it.

*(Optional, for auto-updates later: instead of drag-and-drop, put the folder in a
GitHub repo and "Import from Git." Then edits push live automatically. Not
required — drag-and-drop is fine; to update you just re-drag the new zip.)*

## Step 3 — Turn on the contact form
1. Netlify → your site → **Forms**. It should already show a form named
   **"contact"** (detected automatically).
2. **Forms → Form notifications → Add notification → Email notification** →
   send to **hi@doctorarchers.com**. Now messages from the site's contact form
   land in your inbox, and your address never appears on the site. A spam
   honeypot is already built in.

## Step 4 — Add your domain
1. Netlify → **Domain management → Add a domain** → type **doctorarchers.com**.
2. Netlify will confirm you own it and then show you the DNS to set (Step 5).
   Add **both** `doctorarchers.com` and `www.doctorarchers.com` (Netlify redirects
   one to the other automatically).

## Step 5 — Point DNS (the careful step) 🔑
Your domain's DNS is managed wherever **doctorarchers.com** is registered (likely
Squarespace/Google Domains/Squarespace Domains, or your registrar). Pick ONE option:

**Option A — Netlify DNS (simplest, Netlify recommends).**
- In Netlify's domain setup, choose **"Use Netlify DNS"**. It gives you **4
  nameservers** (like `dns1.p0X.nsone.net`).
- At your registrar, replace the current nameservers with Netlify's 4.
- **Then, in Netlify DNS, re-add your Google Workspace MX records** (see box below)
  so email keeps working. With Netlify DNS you manage all records there.

**Option B — Keep current DNS, just point the site (safest for email).**
- Leave your nameservers alone. At your current DNS host, set:
  - **A record** for `doctorarchers.com` (the apex/root) → **`75.2.60.5`**
    (Netlify's load balancer), OR an ALIAS/ANAME to your Netlify site if your host
    supports it.
  - **CNAME** for `www` → your Netlify site (`your-site-name.netlify.app`).
- This leaves your MX (email) records untouched — the safest path.

> ⚠️ **EMAIL — do not break this.** `hi@doctorarchers.com` runs on Google
> Workspace, which uses **MX records** on your domain. Changing the A/CNAME above
> does NOT affect email. But if you switch nameservers (Option A), the old MX
> records don't come along — you must re-create them in Netlify DNS. Google
> Workspace MX is a single record: `1  smtp.google.com` (older accounts may have
> five ASPMX records — copy whatever your registrar currently shows before you
> change anything). **When in doubt, use Option B**, which never touches email.

## Step 6 — HTTPS (automatic)
Once DNS resolves (minutes to a few hours), Netlify auto-issues a free SSL
certificate. Turn on **"Force HTTPS"** in Domain settings. Done — the site is live
at https://doctorarchers.com.

## Step 7 — Finish the connections
- **Kit**: create the opt-in form (with the free-chapter incentive email),
  newsletter form, and the Commerce product, then paste the IDs into the brackets
  and re-deploy (Step 2). Full steps are in `README.md → Kit setup`.
- **Google Search Console**: add doctorarchers.com and submit
  `https://doctorarchers.com/sitemap.xml` so Google indexes the new site.

---

## Post-launch checklist
- [ ] Every page loads and looks right on **phone** and desktop.
- [ ] Send yourself a test through the **contact form** → it arrives at
      hi@doctorarchers.com.
- [ ] Test the **free-chapter opt-in** and **Buy** button (after Kit is wired).
- [ ] **Email still works** — send a test to hi@doctorarchers.com from another
      account and confirm it arrives.
- [ ] Booking (**OnceHub**), **Shop Labs** (Rupa), **Shop Supplements**
      (Fullscript) links all open.
- [ ] Prices ($27 / $14) and the 30-day guarantee read correctly on `/book`.

## Updating later
- **Any page**: edit the file, re-zip the folder, re-drag to Netlify (or `git
  push` if you connected Git).
- **Blog post**: add a markdown file in `posts/`, run `python3 build.py`, then
  re-deploy. (Details in `README.md`.)

## Safety / rollback
Your Squarespace site stays fully intact until you change DNS in Step 5, and you
can point DNS back to it at any time. Nothing here deletes your old site — you're
just choosing where the domain points.

---

## Namecheap DNS — exact records (this domain is registered at Namecheap)

**First check:** Namecheap → Domain List → Manage doctorarchers.com → **Domain**
tab → **Nameservers**.
- "Namecheap BasicDNS" → DNS is here; your Google MX records are already here, so
  do Section A and leave email alone.
- "Custom DNS" (Squarespace) → switch to Namecheap BasicDNS, then re-add Google MX
  + SPF/DKIM/DMARC (Section B) as well as the records below.

**⚠️ Before editing:** screenshot your current Advanced DNS records, especially any
**MX** and **TXT** (`v=spf1...`, `google._domainkey`, `_dmarc`). That's your email
restore point.

### Section A — point the website to Netlify
Advanced DNS → Host Records. Delete existing `@`/`www` A/CNAME/URL-Redirect records
that point to Squarespace or parking. Do NOT touch MX/TXT. Then add:

| Type         | Host | Value                        | TTL       |
|--------------|------|------------------------------|-----------|
| A Record     | @    | 75.2.60.5                    | Automatic |
| CNAME Record | www  | your-site-name.netlify.app   | Automatic |

(`your-site-name` = the temporary Netlify URL from your drag-and-drop deploy.
Apex `@` must be an A record on Namecheap, not a CNAME.)

Keep "Mail Settings" on **Custom MX** (leave your existing Google MX as-is).

### Section B — only if you switched nameservers to Namecheap BasicDNS
Re-add email so it keeps working:
- MX Record | Host @ | Value `smtp.google.com` | Priority 1  (or your five existing
  `ASPMX...google.com` records — match what you had).
- TXT Record | Host @ | `v=spf1 include:_spf.google.com ~all`
- Plus your existing DKIM (`google._domainkey`) and DMARC (`_dmarc`) TXT records,
  copied from your screenshot.

### Netlify side
Add doctorarchers.com + www in Netlify → Domain management. After it verifies
(minutes to a few hours), enable Force HTTPS.
