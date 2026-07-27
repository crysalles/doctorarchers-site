# GLP-1 reader welcome + review sequence

Three emails to paste into a Kit **Sequence**. They enroll people who join the
**GLP-1 Free Chapter** list (form `9733667`) and, further along, the **GLP-1
Support Kit** list (form `9732823`). Nothing here sends on its own. You build
the sequence in Kit, paste the copy, and switch it on.

The review ask points at **laveenaarchers.com/review**, not a raw Amazon link.
That page forwards to Amazon's review composer once you paste the ASIN into it
on launch day, and shows a friendly "reviews open on launch day" note until
then. So this sequence is safe to switch on before the book is live.

| # | Email | Send (Wait) | Goal |
|---|---|---|---|
| 1 | Welcome | Day 0 (immediately) | Warm hello, set expectations, deepen the relationship |
| 2 | The one thing about the drugs | Day 4 | Give real value, earn the next open, soft nudge to the book |
| 3 | A small favour | Day 8 | Ask a reader who has the book for a short review |

---

## Email 1 — Welcome

**Send:** immediately on joining (Wait: 0 days).

### Subject line options
1. Your first chapter is in your inbox
2. Thank you for reading
3. The noise about these drugs, turned down

**Preview text:** A little of what is coming, and one promise.

### Body

Hi {{ subscriber.first_name | default: "there" }},

Thank you for reading. You have the first chapter of *Your Body's Own GLP-1* in
hand, and I hope it already turned the noise around this subject down a little.

Over the next couple of weeks I will send you a few of the most useful things
from the book. The kind you can put to work whether you ever take a medication
or never do. No hype, no fear, and nothing dressed up as "nature's Ozempic" and
sold back to you.

Here is my one promise: I take no money from any drug company or supplement
seller, so I have no reason to talk you into anything. I am here to give you the
whole picture and let you decide.

If a friend is wrestling with the same questions, send her to
[laveenaarchers.com/glp1-book](https://book.laveenaarchers.com/glp1-book.html).
The first chapter is free for her too.

Warmly,

Rev. Dr. LaVeena B. Archers

*Education and support, not medical advice. Every decision about a medicine
belongs with you and your own prescriber.*

---

## Email 2 — The one thing about the drugs

**Send:** about 4 days after joining (Wait: 4 days).

### Subject line options
1. The thing too few women are told about these drugs
2. What you lose besides fat
3. Protect this, whichever way you go

**Preview text:** Roughly a quarter of the weight lost is not fat.

### Body

Hi {{ subscriber.first_name | default: "there" }},

One thing from the book worth having early, because it matters whether you take
a medication or not.

On these drugs, roughly a quarter of the weight people lose is not fat. It is
lean mass, muscle and bone. For a woman in midlife, who is already losing muscle
to the years, that is the part worth guarding most closely. It is the difference
between coming out the other side lighter and strong, or simply smaller and more
fragile.

Two things protect it, and they are free:

- **Protein at every meal.** Aim to build each plate around it.
- **Resistance training.** Lifting, bands, even bodyweight. Two or three times
  a week is plenty to start.

This is true if you take a GLP-1, and it is true if you never do. It is one of
the clearest examples of supporting the work your own body is doing.

The whole picture, drug or not, is in the book:
[laveenaarchers.com/glp1-book](https://book.laveenaarchers.com/glp1-book.html).

Warmly,

Rev. Dr. LaVeena B. Archers

*Education and support, not medical advice. Talk with your own prescriber before
starting new exercise if you have a health condition.*

---

## Email 3 — A small favour

**Send:** about 8 days after joining (Wait: 4 days after email 2).

### Subject line options
1. A small favour, if the book helped
2. The kindest thing you can do for the next woman
3. Can I ask you something?

**Preview text:** It takes two minutes and does more than any advertising I could buy.

### Body

Hi {{ subscriber.first_name | default: "there" }},

If you picked up *Your Body's Own GLP-1* and it helped you think more clearly,
may I ask you for something small.

Would you leave a short review?

Here is why I am asking. I am one woman with a book and no publisher's marketing
budget behind me. Reviews are how a book like this gets found. When a woman
searches at eleven at night, unsure whether to start one of these drugs or how
to come off one, what decides whether she finds this book is other women saying
it was worth reading.

**[Leave a review](https://book.laveenaarchers.com/review)**

Two things worth saying. It does not have to be long. A sentence or two about
who you are and what you took from it helps more than an essay. And it does not
have to be glowing. If something did not land for you, say so. A fair review
helps the right reader find the book and the wrong reader skip it, and both of
those are good.

If you read it in Kindle Unlimited, you can still review it. Amazon counts that
the same way.

And if you have not got to the book yet, please ignore this entirely. It will
keep.

Thank you for being here,

Rev. Dr. LaVeena B. Archers

---

## Setting this up in Kit

1. **Kit → Automate → Sequences → New sequence**, name it *GLP-1 reader welcome*.
2. Add three emails, in order. Paste the subject you picked and the body for each.
3. Set each email's **Wait**: Email 1 = 0 days, Email 2 = 4 days, Email 3 = 4 days.
4. **Kit → Grow → Landing Pages & Forms → GLP-1 Free Chapter (`9733667`) →
   Settings → add this sequence** so everyone who grabs the free chapter flows in.
   Repeat for **GLP-1 Support Kit (`9732823`)** if you want kit-grabbers in it too.
5. Send yourself a test of each, then switch the sequence on.
6. **On launch day**, paste the Kindle ASIN into `review.html` (one line, marked
   in the file). That activates the redirect behind laveenaarchers.com/review, so
   Email 3's button lands people straight on the Amazon review form.

## House rules

- Education and support only. Never claim the book or anything in it treats,
  cures, or reverses a condition.
- **Never offer anything in exchange for a review.** Amazon prohibits
  incentivised reviews and enforces against the listing. Asking is fine; paying,
  discounting, or bonusing for it is not.
- Keep Kit's one-click unsubscribe. Do not remove it.
- If someone replies that they have not read it yet, that is a warm lead, not a
  failure. Reply personally.
