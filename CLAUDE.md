# doctorarchers-site — working notes for Claude

This is Rev. Dr. LaVeena Archers' evidence-library site (book.laveenaarchers.com). The public promise this repo has to keep, stated on [how-i-research.html](how-i-research.html): "Where a source is cited, I have checked that the source exists and says what the article claims it says." Everything below exists to actually make that true, not just claim it.

## Publishing pipeline

- Posts live in `posts/*.md`, built to `blog/*.html` by `build.py`. A future `date:` means scheduled, not published — plain `python3 build.py` (no `--all`) skips it and won't generate its HTML.
- Never commit `build.py --all` output; it puts unpublished, unreviewed posts live.
- `.github/workflows/publish-scheduled-posts.yml` runs daily and auto-publishes + deploys whatever has come due, with no human in the loop at that point. **Committing and pushing a scheduled post is the point of no manual return** — treat it as equivalent to approving that post for publication on its date, not as a safe intermediate step.

## Mandatory fact-check protocol before scheduling any post

Do not set a future `date:` and commit a post until all four steps below are done. This applies to every post, not just ones that feel high-risk — the error that prompted this file was in a piece that had already been through one review pass and felt fine.

1. **Draft with real citations.** Every claim that rests on research gets a `[n]` marker tied to a verified reference — PubMed, DOI, or an equally checkable primary source. Not a blog post, not a podcast transcript, not something asserted from general training knowledge.

2. **Citation-claim audit, as its own pass.** For every numbered reference, re-fetch the actual source (abstract at minimum) and confirm the *specific sentence* attributed to it is what the source actually says — not just that a real paper exists at that citation number. Check direction of effect, sample size, population studied, and any number quoted. A citation that's real but stretched is a defect, same as one that's simply wrong.

3. **Uncited-claim sweep, as its own pass.** Read the full draft and flag every sentence stated as fact that carries no `[n]` marker: historical claims, named studies/journals/events mentioned in passing, guideline or policy specifics, physiological mechanisms, dates, thresholds, "most labs define X," anything a skeptical reader could look up. For each one: verify it and add a citation, confirm it's genuinely safe general knowledge, soften it to match what's actually known, or cut it.

   This is the exact failure mode that got past review once already: a confident, plausible-sounding, uncited claim about when a specific journal added peer review, which turned out to be wrong for the papers being discussed. It didn't look like the kind of thing that needed checking. Assume more claims like that exist in anything drafted before this file did, until swept.

4. **Adversarial pass, ideally by someone other than the drafter.** One read whose only goal is finding what's wrong — not improving prose, not adding material. If the same session drafted the piece, treat this as a distinct, later pass with a genuinely skeptical stance, not a re-read for flow. Ask: what here would embarrass us if a skeptical reader or a journalist checked it?

No process here guarantees zero errors, ever — say that plainly rather than promising perfection this can't deliver. What this buys is that a wrong claim has to survive four independent checks instead of one drafting pass. LaVeena's own review, per how-i-research.html, remains the final human gate regardless of how clean an automated pass comes back.

## Standing back-catalogue audits

Research moves, and the site says so explicitly: "a site that never revisits its own back catalogue is steadily accumulating errors." The fact-check protocol above is for new posts. Periodically re-run the same citation-claim audit and uncited-claim sweep against everything already in `posts/`, not just new drafts.

Pattern used for the first full-catalogue audit (2026-08): parallel research agents, each covering a small group of posts, verifying citations against PubMed and uncited claims against PubMed/WebSearch, each returning a structured findings report before any fix touched a file. Re-use that shape for future sweeps rather than reviewing serially post-by-post.
