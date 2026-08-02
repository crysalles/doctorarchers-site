# LaVeenaArchers.com — static site

A clean, fast, accessible, code-based rebuild of laveenaarchers.com, off
Squarespace, unified with the look of *A Symptom Is a Signal*. Plain HTML + one
shared stylesheet + a tiny Python blog generator. No frameworks, no build
tools, no third-party requests of any kind.

## What's in this folder

| Path | What it is |
|---|---|
| `index.html` | Home |
| `about.html` | About & Scope (bio, credentials, scope by credential, PMA) |
| `services.html` | Services (four categories, tier placeholders) |
| `training.html` | Training & Certifications |
| `book.html` | The Book — *A Symptom Is a Signal* sales page (the `/book` page) |
| `testimonials.html` | Testimonials (the four real quotes) |
| `faq.html` | FAQ (native `<details>` accordion) |
| `contact.html` | Contact / Booking |
| `join-pma.html` | Join PMA |
| `privacy.html` | Privacy |
| `blog/` | GENERATED — do not edit by hand; run `build.py` instead |
| `posts/` | Blog sources (markdown). `welcome.md` is a sample to replace |
| `build.py` | Blog generator (Python 3 standard library only) |
| `assets/styles.css` | The one shared stylesheet (extracted from the book landing page) |
| `assets/site.js` | Optional JS: mobile menu + pre-launch placeholder guard |

Every internal link is relative, so the site works opened straight from this
folder on your Mac, and on any host.

## Before launch: every [PLACEHOLDER] to fill

Search the files for `[` to find them all. Complete list:

| Placeholder | Where | What to put there |
|---|---|---|
| `[KIT_BOOK_PRODUCT_URL]` | `book.html` (3 buy buttons) | Your checkout link (Gumroad, Payhip, Stripe Payment Link, etc.) |
| `[PRICE_BUNDLE]` | `book.html` (hero, buy box, final call) | Bundle price, digits only (the `$` is already there) |
| `[PRICE_BOOK]` | `book.html` (buy box) | Book-alone price |
| `[REFUND_POLICY]` | `book.html` (buy box reassurance line) | Your refund/guarantee wording, or delete the phrase |
| `[FREE_CHAPTER_URL]` | `book.html` (chapters section button) | Link to the free-chapter page or PDF |
| ~~`[KIT_OPTIN_FORM_UID]`~~ | ✅ **DONE** — Free Chapter form (UID `9680686`) wired into `book.html`; its Kit incentive email delivers the free-chapter PDF on confirm. | — |
| ~~`[KIT_NEWSLETTER_FORM_UID]`~~ | ✅ **DONE** — Newsletter form (UID `9680706`) wired into the blog template in `build.py` (rebuilt). | — |
| ~~`[KIT_BOOK_PRODUCT_URL]`~~ | ✅ **DONE** — book product wired into all 3 buy buttons on `book.html`: `https://laveena-b-archers-phd.kit.com/products/bad-medicine-blues-book-workbook`. Goes live once you connect payments and hit Publish in Kit. | — |
| ~~`[BOOK_COVER_IMAGE_URL]`~~ | ✅ **DONE** — real cover added at `assets/bad-medicine-blues-cover.png` and wired into `book.html` + `index.html` (hero images, og:image, twitter:image, JSON-LD). Kindle 1600×2560 version is in your Downloads folder for Amazon | — |
| ~~`[PORTRAIT_IMAGE_URL]`~~ | ✅ **DONE** — real portrait added at `assets/laveena-archers-portrait.jpg` (pulled from the live site, cropped 4:5) and wired into `index.html`, `about.html`, `book.html`. Certification logos added to About at `assets/certifications.png`. | — |
| `[PACKAGE_DETAILS]` / `[PRICE]` | `services.html` (every tier), `training.html` (program tiers) | What each package includes, and its price |
| `[TRAINING_DETAILS]` | `training.html` | Institutions/years behind her credentials; curriculum details for the two programs |
| `[FAQ_ANSWER]` | `faq.html` (insurance question; Human Design question) | LaVeena's own answers. When filled, also add them to the FAQPage JSON-LD at the top of `faq.html` (answers in the schema must mirror the visible text) |
| `[PMA_SIGNUP_URL_OR_EMBED]` | `join-pma.html` | The real membership signup link or form embed |
| ~~`[PRIVACY_DETAILS]`~~ | ✅ **DONE** — filled from the live ICONIC Human Design LLC policy (operating entity, no-sale, ~5yr retention, GDPR/CCPA rights, under-16). Have your advisor confirm before launch. | — |
| `[REPORT_ORDER_URL]` | `testing.html` (Step 2 "Request a report") | Where a reader requests/pays for a written lab report. A Kit/Payhip product link, a form, or a mailto. |
| `[REPORT_CALL_URL]` | `testing.html` (Step 3 "Add a 15-minute call") | Optional short-call booking link for report clients. Point it at a dedicated OnceHub 15-min event with limited availability, or delete the link to go fully async. |
| `[ONCEHUB_EMBED]` | `contact.html` (HTML comment only — optional) | Only if you want the scheduler embedded on-page; the direct link already works |
| `[INSTAGRAM_URL]` | Footer of every page + `build.py` footer template | Instagram profile URL (or delete the line). Add other socials the same way |
| `[TESTIMONIAL_1/2]` | `book.html` "From early readers" | Real reader quotes with permission — or delete the section |
| `[TESTIMONIAL_5/6]` | `testimonials.html` | Real client quotes with permission — **delete if unused, never invent** |
| `[LOGO_IMAGE_URL]` | optional — not placed | The header uses a text wordmark; if she wants a logo image, add it to the `.brand` link |

**Pre-launch safety:** `assets/site.js` blocks any click or form submit whose
destination still contains `[` and shows a gentle note instead, so the site
can be previewed (and even soft-launched) safely before everything is wired.
These are already REAL and hardcoded — do not placeholder them:
booking `https://go.oncehub.com/HealthConsultation`, labs
`https://labs.rupahealth.com/store/storefront_nYeZEmn`, supplements
`https://us.fullscript.com/welcome/iconic/store-start`, email
`the contact form`.

## Wiring things up

- **Booking (OnceHub)** — already live everywhere ("Book a Consultation"
  header button, CTAs, footer). To embed the scheduler on `contact.html`
  instead of linking, paste your OnceHub embed snippet where the
  `[ONCEHUB_EMBED]` comment sits. Note: an embed adds a third-party request
  to that page; the link keeps the site 100% self-contained.
- **Stores** — Rupa Health (labs) and Fullscript (supplements) are linked in
  the header Shop menu, home CTA band, FAQ, and footer. Nothing to configure.
- **Book checkout** — create the product (Gumroad/Payhip/Stripe Payment
  Link), then replace all three `[KIT_BOOK_PRODUCT_URL]` in `book.html` and the two
  price placeholders.
- **Free-chapter opt-in** — in your email provider (Kit/ConvertKit,
  MailerLite, Buttondown, etc.) create a form; either point the existing
  `<form action="...">` at the provider's POST endpoint (keep the `email`
  input name it expects) or replace the whole form with the provider embed.
- **Sitewide reader opt-in** — the same Companion Workbook offer appears near
  the foot of every content page, mid-way through longer blog posts, and on
  the blog index. For the hand-written pages the form lives in the page HTML;
  for anything generated, change `OPTIN_FORM_ACTION` at the top of `build.py`
  and re-run. Legal and utility pages (`privacy`, `scope-of-practice`, `404`)
  are deliberately left clean, and `book.html` keeps its own dedicated card.
- **PMA signup** — put the membership agreement link or embed into
  `join-pma.html` at `[PMA_SIGNUP_URL_OR_EMBED]`.
- **Analytics** — `assets/analytics.js` loads Cloudflare Web Analytics
  (free, cookieless, no consent banner needed). Paste your site token into the
  `TOKEN` line in that file and analytics switches on everywhere at once.
  Until then it makes no requests at all. Full instructions are in the file.

## The blog

1. Write markdown in `posts/`, one file per post, with front matter.
   `title`, `date` (YYYY-MM-DD), `slug` and `summary` are required:

   ```
   ---
   title: Creatine for Women in Midlife
   date: 2026-07-12
   slug: creatine-for-women-midlife
   summary: One or two sentences shown on the blog index.
   reviewed: 2026-07-27
   questions:
     - Is creatine only for athletes? :: No. It is one of the most studied...
   references:
     - Smith-Ryan AE, et al. Creatine Supplementation in Women's Health.
       Nutrients. 2021;13(3):877. https://doi.org/10.3390/nu13030877
   ---
   ```

   The optional fields:

   - **`reviewed`** — when you last checked the piece for accuracy. Shows as
     "Last reviewed …" when it differs from the publication date, and becomes
     `dateModified` in the article's structured data. Bump it whenever you
     revisit a post.
   - **`references`** — one source per `- ` line. These render as a numbered
     "Sources" section at the foot of the post, with any trailing URL linked,
     and are published as citations in the structured data. Cite them in the
     body with bracketed numbers — `…after 40 [1], and creatine helps [2,3]` —
     which become superscript links down to the source list.
   - **`questions`** — `Question :: Answer` pairs. These render as a "Quick
     answers" box at the head of the post and are published as FAQ structured
     data, so AI assistants can lift a question and its answer together.
   - **`image`** — social-share image for the post (absolute URL, or a path
     like `assets/foo.jpg`). Defaults to the portrait.

2. Run `python3 build.py` (any Python 3; no packages to install).
3. It writes `blog/<slug>.html` for each post and regenerates
   `blog/index.html`, newest first. It also regenerates `sitemap.xml` and
   `llms.txt` from what is actually on disk, so neither can drift out of
   date — do not edit those two by hand. Commit/deploy the output.

## Scheduling posts ahead

**A post dated in the future is scheduled, not published.** `build.py` skips
it, deletes any previously generated copy, and keeps it out of `blog/index.html`,
`sitemap.xml` and `llms.txt`. It prints a line like:

```
  scheduled  why-you-wake-at-3am  (publishes 2026-08-07)
```

To publish a run of posts on a drip rather than all at once, just set the
`date:` fields apart — every other day, weekly, whatever you want.

- `python3 build.py` builds what is due today. This is what you normally run.
- `python3 build.py --all` renders scheduled posts too, so you can preview
  them locally. **Do not commit the output of `--all`** — it puts unpublished
  posts on the live site. Re-run plain `python3 build.py` before committing.

The GitHub Action in `.github/workflows/publish-scheduled-posts.yml` runs the
build once a day at 19:00 UTC (noon in Arizona). When a post comes due it commits
and pushes, which triggers the Netlify deploy. If nothing is due, it exits
without committing. You can also run it on demand from the repo's **Actions**
tab, and the schedule needs no maintenance as you add posts.

Markdown supported: `#`–`######` headings (auto-shifted down one level so
the post title stays the page's only `h1`), paragraphs, `-`/`*` and `1.`
lists, `>` quotes, ``` fences, bold/italic/inline code/links.

## Deploying to laveenaarchers.com

**Netlify:** drag this folder onto app.netlify.com (or connect a Git repo;
no build command, publish directory = the folder itself). Then Domain
settings → add `laveenaarchers.com`. At your DNS registrar, point an `A`/
`ALIAS` record for the apex to Netlify (or switch nameservers to Netlify
DNS) and a `CNAME` for `www` to your site's `*.netlify.app` name. To serve
`book.html` as `/book`, either enable "Pretty URLs" (Site settings → Build &
deploy → Post processing) or add a `_redirects` file with lines like
`/book /book.html 200`.

**Cloudflare Pages:** create a project → direct upload (or Git), no build
command. Pages serves clean URLs automatically, so `/book`, `/about`, etc.
work out of the box. Add the custom domain in the Pages project; if the
domain's DNS is on Cloudflare it wires itself, otherwise follow the CNAME
instructions shown.

In Squarespace: after DNS cutover, keep the account only long enough to
confirm nothing else (email forwarding, etc.) depends on it.

## Claims to review (LaVeena decides; nothing was deleted silently)

1. **"world-wide leading provider of Holistic Functional Medicine"** (live
   Squarespace home page) → softened on the new home page to **"a provider
   of Holistic Functional Medicine"**. "World-wide leading" is not
   verifiable; restore it only if she can stand behind it.
2. That is the only wording change made. All other copy (tagline,
   credentials, service names, scope statement, testimonials, book copy) is
   used verbatim from the approved sources. The four testimonials are the
   only social proof on the site; no ratings, counts, badges, or urgency
   were added anywhere — please keep it that way.

## LaVeena / LaVeena spelling note

The site pages use **LaVeena** (her practice spelling). The book page
(`book.html`) uses **LaVeena**, matching the book cover and approved sales
copy. Decide on one spelling (or intentionally keep both) and standardize:
search for `LaVeena` and `LaVeena` across the folder. JSON-LD `Person`
entries currently use "Rev. Dr. LaVeena B. Archers, PhD".

## Best practices applied (researched July 2026)

- **Performance:** zero third-party requests on every page (no CDNs, web
  fonts, trackers, or analytics); system font stacks (no font download, no
  layout shift from font swap); one small shared CSS file; inline SVG icons
  and favicon (data URI); tiny optional JS. Static HTML comfortably meets
  Core Web Vitals targets (LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1).
- **WCAG 2.2 AA:** exactly one `h1` per page and logical heading order; skip
  link; visible thick offset focus indicators; `scroll-padding-top` so
  anchored/focused content is not obscured by the sticky header (2.4.11
  Focus Not Obscured); interactive targets at least 24px (buttons 40–48px)
  (2.5.8 Target Size); AA-checked palette, including a darkened gold
  `#7a5f1e` for gold text on cream and a lightened gold `#dcb765` for gold
  text on green panels; alt text / `role="img"` labels on placeholders;
  `prefers-reduced-motion` honored; FAQ uses native keyboard-accessible
  `<details>/<summary>`; mobile menu is progressive enhancement (full nav
  still reachable with JS off).
- **SEO:** unique title + meta description + canonical + Open Graph +
  Twitter card per page; JSON-LD as a single `@graph` with stable `@id`s:
  `Person` (with `hasCredential`/`knowsAbout`) + `WebSite` sitewide, `Book`
  on the book page, `FAQPage` on the FAQ (answers mirror visible text;
  placeholder answers are excluded until filled). Deliberately NOT
  `MedicalBusiness`/`Physician` schema — she does not diagnose or treat.
  Note: Google retired FAQ rich results for most sites in 2025, but valid
  `FAQPage` markup remains correct and useful for other consumers/AI search.
- **Architecture:** multi-page static HTML with one shared same-origin
  stylesheet; all internal links relative (works locally and on any host);
  blog generated by a dependency-free Python script; generated pages use the
  identical template so the whole site stays one system.

Validate structured data any time at validator.schema.org and Google's Rich
Results Test after deploying.

---

## Contact form (email kept private)

The site no longer shows an email address anywhere (better for spam). All
"contact" links point to the **form on `/contact`**, and `the contact form`
is only ever the *private destination* the form delivers to — it is never printed
on a page or in the page source / structured data.

**The form is pre-wired for Netlify Forms (recommended, free):**
1. Deploy the site on Netlify. Netlify auto-detects the form (it has
   `data-netlify="true"` and a hidden `form-name="contact"`).
2. In Netlify → **Forms → Form notifications**, add an email notification to
   `the contact form`. Submissions now arrive in your inbox; the address stays
   private. A honeypot field is already included for spam.
3. (Optional) create a `/thank-you` page and set the form `action` to it for a
   nicer post-submit screen.

**If you host on Cloudflare Pages or elsewhere instead**, use a form backend and
change the form `action` in `contact.html`:
- **Formspree** or **Web3Forms** (both free): create a form, set the destination to
  `the contact form` (private), and paste their endpoint URL into
  `action="[CONTACT_FORM_ENDPOINT]"`.

Until a handler is connected, the form is inert (submitting just reloads with
`?sent=1`), so the page previews safely. Your Google Workspace address
`the contact form` is the reply-to / destination in whichever tool you choose.

---

## Email + book sales: Kit (ConvertKit) setup

The opt-in, newsletter, and book checkout are all wired for **Kit**. The forms are
plain, on-brand HTML that POST straight to Kit (no third-party script added to the
site), so all you do is paste a few IDs. Until you do, the pre-launch guard keeps
them inert so the site previews safely.

**One-time setup in your Kit account:**

1. **Free-chapter opt-in (list-builder + auto-delivery).**
   - In Kit, create a **Form** (e.g. "Free Chapter + Checklist").
   - Set its **Incentive email** to deliver the free-chapter PDF and a link to the
     Quick-Start Checklist. This IS "Email 0" from `BMB_Launch_Emails.md` — Kit
     sends it automatically the moment someone subscribes.
   - Copy the form's **UID** (the number in its URL: `app.kit.com/forms/XXXXXXX`).
   - Paste it wherever you see **`[KIT_OPTIN_FORM_UID]`** in `book.html`
     (2 spots: the form `action` and `data-sv-form`).

2. **Newsletter (blog).**
   - Create a second **Form** ("New posts by email"), copy its UID, and paste it
     into **`[KIT_NEWSLETTER_FORM_UID]`** in `blog/index.html` (2 spots).

3. **Sell the book (Kit Commerce).**
   - In Kit → **Products**, create a product ("A Symptom Is a Signal — the bundle"),
     upload the book PDF/ePub + workbook + checklist, and set the price.
   - Copy the product's **share URL** and paste it into **`[KIT_BOOK_PRODUCT_URL]`**
     in `book.html` (3 spots: hero, buy box, final call).
   - Set **`[PRICE_BUNDLE]`** and **`[PRICE_BOOK]`** to match your product price.

4. **The launch sequence (Emails 1–3).**
   - Build a **Sequence** in Kit with the copy from `BMB_Launch_Emails.md`, then a
     **Visual Automation**: *when someone subscribes to the opt-in form → send the
     sequence.* Segment buyers out of the buy-CTAs, per the doc's sending notes.

**Notes.**
- Field names are already Kit-correct (`email_address`, `fields[first_name]`), so
  submissions map straight to Kit contacts. After submit, Kit shows its own
  confirmation/thank-you (or set a redirect in the form's settings).
- Automated **sequences** require Kit's paid **Creator** plan; the **free** plan
  still covers Commerce (selling the book) and broadcasts.
- Your Google Workspace address `the contact form` is the from/reply-to inside
  Kit, so replies land in your inbox. (It is never shown on the site — the contact
  form is separate; see "Contact form" above.)
- Prefer Kit's fancy inline embed instead of the plain form? You can paste Kit's
  JS embed in place of the `<form>`, but the current plain form keeps the site
  free of third-party scripts.
