# Site speed / SEO / AIO — execution prompts and roadmap corrections

Working document for book.laveenaarchers.com. Not published (excluded by
`stage-deploy.py`).

This holds two things: the corrections a real audit forced on the original
roadmap, and the reusable prompts that executed it. If you re-run this work in
six months, start from the prompts at the bottom — but read the corrections
first, because four of the roadmap's premises were wrong.

---

## Part 1 — Where the roadmap was wrong

The original roadmap was well-shaped, and its priority order (speed first, then
schema, then linking) was right. But it was written from the outside, and five of
its factual premises did not survive contact with the actual site.

### 1. "Blocking GPTBot/ClaudeBot significantly reduces AI citation" — wrong

This was the roadmap's central strategic claim, and it is backwards. Those are
**training-only** crawlers. Every major answer engine uses a *separate* agent for
its search index, and none of those are blocked:

| System | Index/answer crawler | Blocked? |
|---|---|---|
| ChatGPT | `OAI-SearchBot` | No — citable |
| Claude | `Claude-SearchBot`, `Claude-User` | No — citable |
| Google AI Overviews / AI Mode | `Googlebot` | No — citable |
| Perplexity | `PerplexityBot` | No — citable |
| Copilot | `bingbot` | No — citable |
| Meta AI | `Meta-WebIndexer` | No — citable |

OpenAI states this explicitly: a site can allow `OAI-SearchBot` to appear in
search results while disallowing `GPTBot`. That is exactly the configuration
already in place.

**The one genuine casualty is `Google-Extended`**, which controls Gemini training
*and* Gemini grounding with a single token — there is no way to split them. That
is a real either/or, and the decision was to keep training refused and accept the
loss of Gemini-app citations. Note that this does **not** affect Google AI
Overviews or AI Mode, which run off Googlebot.

**The gap the roadmap missed entirely:** Microsoft has no separate AI user-agent.
`bingbot` does indexing, Copilot answers, *and* model training, and it was not
blocked — so the site's stated "no training" position was not being enforced
against Microsoft at all. Fixed with a site-wide `<meta name="robots"
content="nocache">`, which limits Microsoft to title+snippet for training while
keeping the page fully citable in Copilot. `noarchive` would have been stronger
but removes the site from Copilot answers entirely.

### 2. "Cloudflare's managed robots.txt blocks your rules" — wrong

Cloudflare **prepends** its managed block; it does not override. The repo's own
`Disallow:` rules and `Sitemap:` directive are served intact below the
`# END Cloudflare Managed Content` marker. (Easy to get wrong — reading only the
first 60 lines of the served file makes it look replaced.)

One real side effect: the served file now has two `User-agent: *` groups. RFC 9309
parsers merge them and most-specific-match wins, so the rules still apply to
Google. A naive first-group-wins parser would miss them.

### 3. "Add llms.txt — low effort, harmless" — already done, and oversized

`llms.txt` already existed at 13.8 KB. The framing prose in it is accurate and
worth keeping; the page list had grown to 35 entries, 34 of which redundantly
repeated the author's name in the link text.

### 4. "Add Article / FAQPage / Book schema" — mostly already there, and partly broken

The site already had ~15 `Article`, ~10 `FAQPage`, 5 `Book`, and a carefully
scoped `Person`/`WebSite` graph. All 33 blocks parsed cleanly. The problem was
never absence — it was **correctness**:

- One `Person` `@id` asserted with **14 different payloads**, including three
  mutually incompatible credential lists.
- `FAQPage` markup stating Q&A text that does not appear on the page — a manual
  action risk, not a missed opportunity.
- A `Book` `image` pointing at a cover file that does not exist.
- HTML entities (`&amp;`) leaked into JSON string values.

"Add schema" would have made this worse. The work was deduplication and repair.

### 5. "Confirm clean 301s from www" — they were not clean

`laveenaarchers.com`, `www.laveenaarchers.com` and `book.laveenaarchers.com` all
returned **200** with byte-identical content. Canonical tags were the only thing
holding the signals together.

---

## Part 2 — What the roadmap could not have known

Three problems outranked everything on the original list.

### The deploy published the entire repository

`wrangler pages deploy .` from the repo root uploaded every file in the working
tree. In production, at 200:

- `BOOK_still-normal-manuscript.md` — a complete unpublished book, 136 KB
- all 8 future-dated draft posts at `/posts/*.md`, defeating the whole scheduling
  mechanism
- `build.py`, `CLAUDE.md`, `README.md`, `DEPLOY.md`, `_reshape.py`

Fixed with `stage-deploy.py`, an **allowlist** that assembles `dist/`. A denylist
fails silently and permanently; an allowlist fails loudly. Note that
`.assetsignore` does **not** work here — it is a Workers-assets feature and the
`wrangler pages deploy` path ignores it (verified empirically against wrangler
4.120.0).

**Cache caveat:** removing a file from the deploy does not evict it from
Cloudflare's edge cache, which holds static assets for 7 days (`s-maxage=604800`).
A purge from the dashboard is required. Verify any removal with a cache-buster
query string, which bypasses the cached copy.

### Cloudflare Pages 308-redirects `.html` to extensionless

`/about.html` → 308 → `/about`. Consequences, all measured:

- 39 of 40 sitemap URLs pointed at redirects rather than the URLs that serve 200
- nearly every `<link rel="canonical">` and `og:url` named a redirecting URL
- 834 internal links each paid a redirect hop

### The gated post's noindex never applied

`_headers` set `X-Robots-Tag: noindex` on `/blog/nature-glp1.html`. That path
308-redirects, so the header lands on the redirect — and the URL that actually
serves the content (`/blog/nature-glp1`, HTTP 200) sends **no** noindex header at
all. Meanwhile `sitemap.xml` and `llms.txt` were both advertising it.

The gated PDFs were fine, because `.pdf` is not extension-stripped. Worth checking
rather than assuming.

---

## Part 3 — The prompts

These ran as two multi-agent passes: a read-only audit, then implementation
partitioned by file ownership. The full runnable scripts are in
`.claude/projects/.../workflows/scripts/`.

### Constraint preamble — prepend to every prompt

This block did more to keep the work safe than any individual instruction. The
credential rule in particular exists because credential wording has drifted wrong
in this project before.

```
=== FILE OWNERSHIP ===
Other agents are editing this repo in parallel. Edit ONLY your assigned files.
If another file needs a change, report it as a handoff — do not edit it.

=== NON-NEGOTIABLE ===
1. She is NOT a medical doctor. Never introduce language, schema, or markup
   implying diagnosis, treatment, cure, or clinical practice. No Physician /
   MedicalBusiness / MedicalWebPage schema types, ever.
2. Do NOT reword any credential, degree, board certification, or
   scope-of-practice sentence. That text is legally sensitive and has drifted
   wrong before. Move it or wrap it in markup; never rewrite what it claims.
3. US English ("practice", not "practise").
4. Never run `build.py --all`. A future date: means SCHEDULED — it stays
   unpublished.
5. Do not commit, push, or deploy.
6. Preserve every alt attribute VERBATIM when restructuring image markup.
7. Preserve width/height on images — they prevent layout shift.
```

### Audit prompts (read-only, six dimensions)

Each auditor got the preamble plus one dimension: **images and payload**,
**structured data**, **technical SEO**, **internal linking**, **AI
extractability**, **content and build pipeline**. Two instructions did most of
the work:

> Every finding must be CONCRETE and VERIFIED: cite file path + line number, or a
> command whose output you actually ran and observed. No speculation, no "consider
> reviewing X". If you cannot verify it, do not report it.

> IMPORTANT: `blog/*.html` are GENERATED from `posts/*.md` by `build.py`.
> Determine whether a fix belongs in the source, the template, or the generated
> file. State this per recommendation — a fix applied to the wrong layer gets
> silently reverted.

Every critical and high finding then went to an adversarial verifier prompted to
**refute** it, defaulting to `holds=false` when it could not independently
confirm. Of 89 findings, that pass killed one and corrected several severities.
The most valuable verifier instruction:

> Would the proposed fix actually work on CLOUDFLARE PAGES specifically, or is it
> advice that only applies to another host? This is a common error — check it.

That question caught a proposed CSS change (`width:fit-content` on `.hero-cover`)
that would have ballooned three images on mobile.

### Implementation prompts (five disjoint file sets)

| Agent | Owns | Brief |
|---|---|---|
| `build.py` | `build.py` alone | Extensionless canonicals through every emitter; root-relative links in templates; title ≤60 / description ≤155; `nocache` meta; `dateModified` clamping; typed `ScholarlyArticle` citations; sitemap `lastmod` for every URL; drop the gated post from sitemap and llms.txt |
| posts | `posts/*.md` | Direct-answer ledes; headings as questions; self-contained section openings; contextual post→post links; correct book targets; evidence-standards links; carry citations into Quick answers |
| book pages | 7 book/imprint pages | `<picture>` markup; fix the 404 cover; fix the mislabeled author photo; Book schema repair; shared Person `@id` |
| site pages | 24 remaining pages | 21 certificates to `<picture>`; below-fold lazy-loading; FAQPage/visible-text mismatch; de-orphan `faq.html`; Person dedup |
| headers | `_headers`, `_redirects` | Cache policy; noindex on the URL that actually serves; collapse the redirect chain |

The two instructions that mattered most:

> **CRITICAL LAYOUT TRAP, already verified in a real browser:** on `book.html` the
> `<img class="hero-cover">` is a DIRECT GRID ITEM of `.wrap.hero-grid`. The class
> carries `order:-1` and `margin:0 auto` at ≤820px. If you wrap it and leave the
> class on the `<img>`, the cover drops below the headline on phones. MOVE
> `class="hero-cover"` onto the `<picture>`. On pages where the img sits inside a
> plain `<div>` grid item the class is inert and should STAY on the `<img>` —
> check each page's actual DOM before deciding.

> **CLAIMS vs STRUCTURE.** Structure and links: change freely. Claims and voice:
> do not invent, do not embellish, do not add a factual claim not already in the
> piece, and do not add a citation that is not already there. Moving a sentence is
> fine; changing what it asserts is not.

### Review prompt

Each implementer's diff went to an independent read-only reviewer:

> Check the ACTUAL diff with `git diff`, not the agent's description of it. Hunt
> for: broken references (test them); invalid JSON-LD (parse it); **alt text lost
> or altered** during `<picture>` restructuring (compare against
> `git show HEAD:<file>` — any change to an alt string is a defect); width/height
> lost; an LCP image marked `loading="lazy"`; **credential or scope-of-practice
> text reworded — the most serious possible defect on this site, diff the words**;
> `og:image` pointed at `.avif`/`.webp`; British spelling; and anything the agent
> claimed to do that it did not actually do.

---

## Part 4 — Standing checks

`check-site.py` runs against `dist/` before any deploy and gates on exit code.
Every check corresponds to something that was actually broken, which is the only
good reason to have a check.

```bash
python3 build.py && python3 stage-deploy.py && python3 check-site.py
```

`optimize-images.py` is idempotent — re-run it after adding any image. It emits
AVIF + WebP at 2× the CSS display size. Originals stay put as the `<img>`
fallback and as the `og:image` target, because social scrapers are not reliably
AVIF-aware.

## Part 5 — Still open

Ordered by urgency. The first two need the Cloudflare dashboard and cannot be
done from this repo.

**1. Purge the Cloudflare cache — do this first.** The origin no longer has the
manuscript or the draft posts (verified: a cache-buster query returns 404), but
static assets are served `s-maxage=604800`, so edge copies keep serving for up to
7 days to anyone who has the URL. Dashboard → Caching → Configuration → Purge
Everything. The wrangler OAuth token holds only `zone:read` and cannot purge, so
this is not automatable with the current credentials.

**2. 301 the apex and www to `book.`** All three hostnames are custom domains on
the same Pages project, which is why `laveenaarchers.com`,
`www.laveenaarchers.com` and `book.laveenaarchers.com` all return 200 with
byte-identical content. Canonical tags are currently the only thing consolidating
them.

*Order matters:* create the Redirect Rule **first**, then remove the two custom
domains from the Pages project. Removing them first leaves the apex resolving to
Pages with no route, which breaks it.

Worth deciding deliberately while you are in there: `book.` is the canonical host
today and every signal on the site points at it, so redirecting to it is the
low-risk consolidation. Moving canonical to the apex would be the stronger
long-term brand, but it is a full host migration and should be its own project,
not a side effect of this one.

**3. ~~The Nature GLP-1 shield~~ — DONE, 2026-08-07.** Lifted on your say-so.
`_headers` rules removed, `GATED_POST_SLUGS` emptied, so the post is back in
sitemap.xml, llms.txt and the blog index. Verified live: `/blog/nature-glp1`
returns 200 with no `X-Robots-Tag`.

The sample-PDF gate from the same commit is untouched and still holds — that one
shields a lead magnet you get by joining the list, unrelated to KDP.

Worth remembering: the original rule was written for `/blog/nature-glp1.html`,
which Pages 308-redirects, so the noindex landed on the redirect and the article
was fully indexable the entire time the shield was supposedly up. Write any
future gate for the URL that serves 200, and pair `GATED_POST_SLUGS` with a
matching `_headers` rule in the same edit — the constant only stops the build
advertising a URL, it does not stop anything indexing a page reached another way.

**4. The credential lists still disagree between pages.** This was the original
audit finding and it is deliberately *not* fixed. `index.html` asserts 4
credentials, `credentials.html` 14, `about.html` 6, with different wording and
different `credentialCategory` values for what look like the same qualifications.
Every node is byte-identical to what it was before this session — nothing was
reworded — but one `@id` is still describing one person three different ways.

Reconciling them means deciding which list is correct, which is yours to make and
not safely inferable from the markup.

**5. ~~`blog/ozempic-muscle-loss.html`~~ — DONE, 2026-08-07.** Handled
automatically. `SUPERSEDED` in `build.py` maps it to `glp1-muscle-loss`; on the
first build after that post publishes on the 12th, the stale page is deleted and
a 301 for both URL forms appears in the generated block of `_redirects`. Nothing
happens before then, so there is no window where the old URL 404s.

Why that page and not the other: it is hand-written with no `posts/*.md` source,
has zero inbound links, is in neither `sitemap.xml` nor `llms.txt`, and carries
no inline citations across 1,158 words against 12 in its replacement.

**6. `DEPLOY.md` describes Netlify.** The site is on Cloudflare Pages. The file no
longer deploys, but it will mislead the next person who reads it — including a
future session of me.

**7. Your review pass on the post edits.** Per the protocol in `CLAUDE.md`, your
read is the final human gate. What changed in `posts/*.md`: opening paragraphs
reordered so the answer comes first, some H2s rephrased as questions, contextual
internal links added, and existing `[n]` markers carried into the Quick-answers
blocks. Reference lists are byte-identical across every post and no new factual
claim was introduced — but "the citation now attached to this Quick answer really
does support this sentence" is exactly the judgment the protocol exists for, and
it has not had your eyes yet.
