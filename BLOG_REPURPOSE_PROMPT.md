# Blog Repurpose Prompt - The Good Years -> LaVeenaArchers.com posts

## Goal
Turn the deep-dive material in the book *The Good Years* into standalone SEO blog posts that
**complement** the book (they do not replace it; the book stays the comprehensive reference), and
that funnel readers back to it. Each post takes one topic the book covers in depth and gives it the
room a chapter cannot.

## The credit-efficient rule (read first)
**The source content is already written and already fact-checked.** Do not re-research from scratch.
- Book manuscript: `~/Downloads/the-good-years/blocks.json` (array of `{type,text}`; chapters are
  `chapter` blocks, sections are `sub`). Read only the chapter(s) named in the manifest.
- Citations already exist in that book's `Further Reading and Real Sources` chapter, grouped by
  `## Chapter N`. **Reuse those citations.** Only run a web search if you are adding a fact the book
  does not contain, and if you do, verify it to a named primary source and never fabricate one.
- **Every reference must end in a URL, and you must confirm that URL resolves before publishing.**
  The book's reference list does not carry URLs, so reusing it verbatim produces a Sources section
  of dead text. `build.py` only linkifies a trailing URL, and the site's published editorial
  standards promise the opposite: "every source in that list links out to the original paper,
  usually by DOI or PubMed record... A citation that cannot be checked is decoration."
  Look each one up (the PubMed MCP tool returns the DOI directly), append `https://doi.org/<doi>`
  or the PubMed record URL, and check it: `curl -s -o /dev/null -w '%{http_code}' -L https://doi.org/<doi>`
  returns 302 for a valid DOI and 404 for a bad one. Correct the volume and page numbers against
  the record while you are there, since the book's list has at least one transcription error.
  Never invent a DOI. If a source genuinely has no stable URL, say so in the reference rather than
  guessing at one.
- Draft each post by reshaping the verified book prose into the post format below. This is repurposing,
  not new reporting, which is where the savings are.

## Output format (match the house style exactly)
Write each post to `posts/<slug>.md`, then run `python3 build.py` (it renders `blog/<slug>.html` and
rebuilds the index/sitemap/llms.txt). Front matter:

```
---
title: <compelling, specific, search-friendly>
date: <YYYY-MM-DD, stagger future dates so they schedule>
slug: <kebab-case>
summary: <1-2 sentences for the index and meta description>
reviewed: 2026-07-27
questions:
  - <A natural search question> :: <A tight, quotable answer>   (2-4 of these; becomes FAQ schema)
references:
  - <Author. Title. Journal. Year. URL>                         (one per line; reuse the book's)
---
```
Body: plain markdown, `#` for section headings, cite sources inline with bracketed numbers that match
the reference order, e.g. "no level of alcohol is safe [1]." End every post with one italic line that
points back to the book, for example:
`*Adapted from the [topic] chapter of The Good Years. The book takes the same honest look at the whole longevity industry, written for a woman's body.*`

## House rules (non-negotiable, same as the book)
- Voice: warm, plain, honest, first person, direct address to "you." **No em dashes** (commas, periods,
  parentheses only). **No "not X but Y" antithesis.** No AI-tells (delve, tapestry, testament, realm,
  navigate-as-filler, unlock, game-changer, more than just, at the end of the day, in today's world).
- **Explain every abbreviation** on first use (readers land cold on a post). No bare Lp(a), VO2 max,
  LDL, PFAS, DEXA, etc.
- **PMA-safe:** educate and support, never diagnose, treat, or prescribe. Route decisions to the
  reader's own clinician. **No dosing numbers directed at the reader** (mg/mcg/g/IU); doses reported
  from a cited study are fine.
- Keep safety content intact (crisis lines, red flags) if the topic touches it.
- 900-1500 words is the sweet spot. One clear idea per post.

## Do not duplicate existing posts
Already live or scheduled (skip these topics): creatine for women, the protein number, GLP-1 (several:
your-body-already-makes-glp-1, nature-glp1, glp1-muscle-loss, fibre-and-your-own-glp1), normal
bloodwork / ferritin / TSH, why you wake at 3am, what changes first in perimenopause, the FDA hormone
warning change, A Symptom Is a Signal on Kindle, and **blue-zones-what-they-actually-ate (already done as
the model post - copy its structure).**

## Manifest (12 posts, each with its source chapter and angle)
1. **slug: no-safe-level-of-alcohol** - "The Wine-With-Dinner Story Fell Apart. Here Is What Replaced It." Source: Ch10. Angle: the health-halo collapse, acetaldehyde, why women absorb more harm, the Surgeon General advisory. (Ch10 Further Reading has the citations.)
2. **slug: is-sunscreen-toxic** - "Is Sunscreen Toxic? The Honest Answer." Source: Ch21 (the sun sections). Angle: the FDA GRASE ruling, systemic absorption, mineral vs the chemical filters under review, and why zero-sun is also a mistake. Timely, high search volume.
3. **slug: biological-age-tests-worth-it** - "That Biological Age Test Is Mostly Theater. Here Is Why." Source: Ch26. Angle: the clocks disagree, drift by time of day, no proof lowering the number helps you.
4. **slug: ldl-rises-on-keto** - "When LDL Shoots Up on Keto: The Lean-Mass Hyper-Responder Story." Source: Ch8. Angle: the pattern, the retracted trial, what to actually do. Unique, high interest.
5. **slug: zone-2-what-research-shows** - "Zone 2 Training: What the Research Actually Shows." Source: Ch6. Angle: the cult vs the evidence; it is your base, not a magic key. Trendy.
6. **slug: vo2-max-longevity** - "VO2 Max: The Number That Predicts Your Longevity Better Than Your Cholesterol." Source: Ch6. Angle: no ceiling of benefit; women's data; how to raise it.
7. **slug: grip-strength-longevity-test** - "The Free Longevity Test You Can Do at Home." Source: Ch4 and Ch5. Angle: grip strength and the sit-to-stand, what they predict.
8. **slug: microplastics-in-your-arteries** - "Plastic in Your Arteries: What the 2024 Study Found." Source: Ch7. Angle: the NEJM plaque study, honest limits, the cheap swaps.
9. **slug: pelvic-floor-incontinence-fix** - "The Leaking No One Warned You About, and the Fix That Gets Skipped." Source: Ch22. Angle: incontinence is common and treatable; pelvic floor PT is first-line. Underserved, high value.
10. **slug: vaginal-estrogen-best-kept-secret** - "The Safest Menopause Treatment Almost No One Is Offered." Source: Ch17 (genitourinary syndrome section). Angle: low-dose local estrogen for dryness/UTIs; safe for most; the oncology exception.
11. **slug: do-longevity-supplements-work** - "NAD, Resveratrol, Taurine: Do Any Longevity Supplements Actually Work?" Source: Ch25 and Ch29. Angle: the mouse-to-woman gap; what earned a look (creatine); the taurine reversal.
12. **slug: womens-heart-attack-symptoms** - "A Woman's Heart Attack Does Not Look Like the Movies." Source: Ch19. Angle: pressure not pain, the atypical symptoms, SCAD, do not drive yourself. (Keep the emergency guidance intact.)

## Scheduling: do not collide with the existing queue
Posts are published every other day and the queue is already full to 16 August:

  Jul 29 FDA hormone warning, Jul 31 normal lab results, Aug 02 ferritin, Aug 04 TSH,
  Aug 06 perimenopause, Aug 08 3am waking, Aug 10 protein, Aug 12 GLP-1 muscle,
  Aug 14 fibre, Aug 16 blue zones, Aug 18 chrononutrition

**Start new posts at 20 August and continue every other day** (20, 22, 24...). A post dated today
publishes on the next push, which double-posts and breaks the cadence. `build.py` holds back any
future-dated post and prints what is queued, so run it and read that list before choosing a date.

## After each post
Run `python3 build.py`, confirm `blog/<slug>.html` rendered and the post appears in `blog/index.html`.
Two to four FAQ `questions` per post lift well into AI-assistant answers, so include them.

**Never run `python3 build.py --all` and commit the result.** That flag renders scheduled posts for
local preview only; committing its output publishes everything early. Re-run plain `python3 build.py`
before staging.

## Another agent is working in this same directory
Stage your own files by name. **Do not `git add -A`**, because it will sweep up another agent's
half-finished work and publish it. Check `git status` before committing and leave anything you did
not create alone.

## Which opt-in form to embed
These longevity posts feed a **dedicated Kit list**, separate from the site default. `build.py`
defaults the blog opt-in to form `9680686` (the BMB reader list). For these posts, embed the new
**"The Good Years — Longevity"** form instead, ID **`9734257`** (created in Kit, live). Post to
`https://app.kit.com/forms/9734257/subscriptions` with `data-sv-form="9734257"`, matching the pattern
already used on `support-kit.html` and `glp1-quiz.html`. Its dedicated welcome sequence lives in
`email-templates/goodyears-longevity-nurture.md`; that sequence still needs to be built inside Kit and
its automation switched on before the posts start driving signups, so confirm that before relying on it.
