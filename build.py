#!/usr/bin/env python3
"""
build.py — markdown blog generator for LaVeenaArchers.com.

Python 3 standard library only. No dependencies to install.

Usage:
    python3 build.py

What it does:
    1. Reads every posts/*.md file.
    2. Each post starts with simple front matter between two "---" lines:

           ---
           title: My post title
           date: 2026-07-12
           slug: my-post-title
           summary: One or two sentences shown on the blog index.
           reviewed: 2026-07-27
           references:
             - Smith J, et al. Title of the paper. Journal. 2024. https://pubmed.ncbi.nlm.nih.gov/12345678/
             - Jones A. Another source. 2023. https://doi.org/10.1000/example
           ---

       title, date, slug and summary are required. The optional fields:

       reviewed:   the date the post was last checked for accuracy. Shown as
                   "Last reviewed ..." whenever it differs from the publication
                   date, and used as dateModified in the Article schema.

       references: one source per "  - " line. Each becomes a numbered entry in
                   a "Sources" section at the foot of the post, with any trailing
                   URL turned into a link, and is emitted as a citation in the
                   Article schema. Cite them in the body with bracketed numbers:
                   "...muscle mass declines after 40 [1], and creatine helps [2,3]."
                   Those markers become superscript links to the source list.

       questions:  optional "Question :: Answer" pairs, one per "  - " line.
                   They render as a "Quick answers" box at the head of the post
                   and are published as FAQPage structured data, so AI
                   assistants can lift a question and its answer together.

       image:      optional social-share image for the post. An absolute URL,
                   or a path like assets/foo.jpg relative to the site root.
                   Defaults to the portrait.

    3. Renders each post to blog/<slug>.html using the shared site template
       (same header, footer, and assets/styles.css as the rest of the site).
    4. Generates blog/index.html listing all posts, newest first.

Markdown supported (a deliberate, honest subset):
    # .. ###### headings (shifted down one level so the post title stays the
    only h1 on the page: "#" becomes h2, "##" becomes h3, and so on),
    paragraphs, - or * unordered lists, 1. ordered lists, > blockquotes,
    ``` code fences, **bold**, *italic*, `inline code`, [links](https://...).
"""

import html
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
OUT_DIR = ROOT / "blog"

SITE_URL = "https://book.laveenaarchers.com"

# Shown when a post is shared on social media. Posts can override with an
# "image:" line in their front matter (an absolute URL, or a path like
# assets/foo.jpg relative to the site root).
DEFAULT_OG_IMAGE = f"{SITE_URL}/assets/laveena-archers-portrait.jpg"

# --------------------------------------------------------------------------
# Shared page template (mirrors the hand-written pages, with ../ paths)
# --------------------------------------------------------------------------

HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_tag}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">

<!-- Open Graph -->
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="LaVeenaArchers.com">
<meta property="og:image" content="{og_image}">

<!-- Twitter card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">

<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%233f5e4e'/%3E%3Cpath d='M16 26c0-9 4-14 10-16-1 9-4 14-10 16zm0 0c0-9-4-14-10-16 1 9 4 14 10 16z' fill='%23f6f2e9'/%3E%3C/svg%3E">

<link rel="stylesheet" href="../assets/styles.css">

<script type="application/ld+json">
{json_ld}
</script>
</head>
<body>

<a class="skip-link" href="#main">Skip to main content</a>

<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="../index.html">Rev. Dr. LaVeena Archers</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" hidden>Menu</button>
    <nav id="site-nav" class="site-nav" aria-label="Main">
      <a href="../index.html">Home</a>
      <a href="index.html" aria-current="page">Library</a>
      <a href="../books.html">Books</a>
      <a href="../about.html">About</a>
      <a href="../testing.html">Testing &amp; Learning</a>
      <a href="../contact.html">Contact</a>
      <details class="shop-menu">
        <summary>Shop</summary>
        <div class="shop-list">
          <a href="https://labs.rupahealth.com/store/storefront_nYeZEmn" rel="noopener">Shop Labs</a>
          <a href="https://us.fullscript.com/welcome/iconic/store-start" rel="noopener">Shop Supplements</a>
        </div>
      </details>
      <a class="btn btn-gold" href="../book.html#free-chapter">Read a free chapter</a>
    </nav>
  </div>
</header>

<main id="main">
"""

FOOTER = """
</main>

<!-- ===================== FOOTER ===================== -->
<footer class="site-footer on-green">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h3>Rev. Dr. LaVeena Archers</h3>
        <p>Awaken To Your ICONIC Potential.<br>© 2026 Rev. Dr. LaVeena B. Archers, PhD.</p>
      </div>
      <div>
        <h3>Contact</h3>
        <ul class="footer-links">
          <li><a href="../contact.html">Contact form</a></li>
        </ul>
      </div>
      <div>
        <h3>Explore</h3>
        <ul class="footer-links">
          <li><a href="../book.html">Bad Medicine Blues — the book</a></li>
          <li><a href="../testing.html">Testing &amp; Learning</a></li>
          <li><a href="https://labs.rupahealth.com/store/storefront_nYeZEmn" rel="noopener">Shop Labs</a></li>
          <li><a href="https://us.fullscript.com/welcome/iconic/store-start" rel="noopener">Shop Supplements</a></li>
          <li><a href="../how-i-research.html">How I research</a></li>
          <li><a href="../privacy.html">Privacy</a></li>
        </ul>
      </div>
    </div>
    <p class="disclaimer"><strong>Scope of practice.</strong> Rev. Dr. LaVeena B. Archers is a Doctor of Natural Medicine and board-certified holistic practitioner. She is not a conventional medical doctor. Her role is to educate and support, not to diagnose, treat, prescribe, or manage diseases. Services are offered within a Private Membership Association (PMA). Nothing on this website is medical advice, and nothing here promises to cure, reverse, or treat any disease. Always seek the advice of a qualified medical professional with any questions about a medical condition.</p>
  </div>
</footer>

<script src="../assets/site.js"></script>
<script src="../assets/analytics.js" defer></script>
</body>
</html>
"""

# Sitewide reader opt-in. One offer, one list: the Companion Workbook.
# To point this at a different Kit form, change the id in both places below.
OPTIN_FORM_ACTION = "https://app.kit.com/forms/9680686/subscriptions"

OPTIN_BLOCK = """
  <section class="alt" aria-labelledby="optin-inline-title">
    <div class="wrap">
      <div class="optin-card">
        <span class="eyebrow">Free — no purchase needed</span>
        <h2 id="optin-inline-title">Get the Companion Workbook, free.</h2>
        <p>Join the reader list and I will send you the Companion Workbook and
           Quick-Start Checklist. Simple tools to turn what you are reading into
           daily practice, before you spend a penny on anything.</p>
        <form action="{action}" method="post" data-optin>
          <div>
            <label for="{prefix}-name">First name <span aria-hidden="true">(optional)</span></label>
            <input type="text" id="{prefix}-name" name="fields[first_name]" autocomplete="given-name">
          </div>
          <div>
            <label for="{prefix}-email">Email address</label>
            <input type="email" id="{prefix}-email" name="email_address" autocomplete="email" required>
          </div>
          <button class="btn btn-primary" type="submit">Send me the workbook</button>
          <p class="microcopy">You'll get the workbook and checklist right away, then an
             occasional grounded note about root-cause health. No spam, no selling your
             address, and every email has a one-click unsubscribe.</p>
        </form>
      </div>
    </div>
  </section>
"""


def optin_block(prefix):
    """Render the opt-in with page-unique input ids."""
    return OPTIN_BLOCK.format(action=OPTIN_FORM_ACTION, prefix=prefix)

# --------------------------------------------------------------------------
# Structured data (JSON-LD)
#
# Deliberately NOT MedicalBusiness/Physician: she educates and supports, she
# does not diagnose or treat. Credentials mirror index.html so search engines
# and AI assistants see one consistent author identity across the whole site.
# --------------------------------------------------------------------------

PERSON_ID = f"{SITE_URL}/#laveena"
WEBSITE_ID = f"{SITE_URL}/#website"

AUTHOR_NAME = "Rev. Dr. LaVeena B. Archers, PhD"
AUTHOR_CREDENTIALS = (
    "Doctor of Natural Medicine · Board-certified in Holistic Functional "
    "Medicine and Functional Nutrition"
)

PERSON_NODE = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": AUTHOR_NAME,
    "alternateName": "Rev. Dr. LaVeena Archers",
    "url": f"{SITE_URL}/",
    "description": (
        "Holistic Functional Medicine educator and author of Bad Medicine Blues. "
        "Educates and supports; does not diagnose, treat, prescribe, or manage "
        "disease. Services offered within a Private Membership Association."
    ),
    "hasCredential": [
        {"@type": "EducationalOccupationalCredential", "name": n}
        for n in (
            "Certified Executive Coach",
            "Doctor of Natural Medicine (DNM)",
            "Board-Certified Holistic Functional Medicine Doctor (BC-HFMD)",
            "Board-Certified Holistic Functional Nutrition Doctor (BC-HFND)",
            "Board-Certified Holistic Health Practitioner (BC-HHP)",
        )
    ],
    "knowsAbout": [
        "Holistic Functional Medicine", "Functional nutrition", "Human Design",
        "Entrepreneur wellness", "Longevity",
    ],
}

WEBSITE_NODE = {
    "@type": "WebSite",
    "@id": WEBSITE_ID,
    "url": f"{SITE_URL}/",
    "name": "LaVeenaArchers.com",
    "description": (
        "Holistic Functional Medicine education and support from "
        "Rev. Dr. LaVeena B. Archers, PhD."
    ),
    "publisher": {"@id": PERSON_ID},
    "inLanguage": "en",
}


def dump_json_ld(graph):
    """Serialise a @graph safely for embedding inside a <script> tag."""
    payload = {"@context": "https://schema.org", "@graph": graph}
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    # Never let a literal </script> (or <!--) escape the script element.
    return text.replace("<", "\\u003c")


SITE_JSON_LD = dump_json_ld([PERSON_NODE, WEBSITE_NODE])


def article_json_ld(meta, refs, canonical):
    """Per-post Article node: author, dates, and the sources it cites."""
    article = {
        "@type": "Article",
        "@id": canonical + "#article",
        "isPartOf": {"@id": WEBSITE_ID},
        "mainEntityOfPage": canonical,
        "headline": meta["title"],
        "description": meta["summary"],
        "url": canonical,
        "datePublished": meta["date"],
        "dateModified": meta["reviewed"],
        "image": post_image(meta),
        "author": {"@id": PERSON_ID},
        "publisher": {"@id": PERSON_ID},
        "inLanguage": "en",
        "isAccessibleForFree": True,
    }
    if refs:
        article["citation"] = [
            {"@type": "CreativeWork", "name": r["text"],
             **({"url": r["url"]} if r["url"] else {})}
            for r in refs
        ]

    graph = [PERSON_NODE, WEBSITE_NODE, article]

    # A post's "Quick answers" also published as FAQPage, so assistants can
    # lift a question and its answer as a unit.
    if meta["questions"]:
        graph.append({
            "@type": "FAQPage",
            "@id": canonical + "#faq",
            "isPartOf": {"@id": canonical + "#article"},
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in meta["questions"]
            ],
        })
    return dump_json_ld(graph)


# --------------------------------------------------------------------------
# Front matter
# --------------------------------------------------------------------------

def parse_front_matter(text, path):
    """Return (meta dict, body str). Front matter sits between two --- lines."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SystemExit(
            f"ERROR: {path} must start with a '---' front matter block "
            "(title, date, slug, summary)."
        )
    meta = {}
    i = 1
    last_key = None
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        stripped = line.strip()

        # Indented "- item" continues the previous key as a list.
        # Checked BEFORE the ":" test, so URLs inside a reference (https://...)
        # are never mistaken for "key: value".
        if stripped.startswith("- ") and last_key:
            if not isinstance(meta.get(last_key), list):
                meta[last_key] = []
            meta[last_key].append(stripped[2:].strip())
        elif ":" in line and not line[:1].isspace():
            key, _, value = line.partition(":")
            last_key = key.strip().lower()
            meta[last_key] = value.strip()
        i += 1
    if i >= len(lines):
        raise SystemExit(f"ERROR: {path} front matter never closes with '---'.")
    body = "\n".join(lines[i + 1:])

    for required in ("title", "date", "slug", "summary"):
        if not meta.get(required):
            raise SystemExit(f"ERROR: {path} front matter is missing '{required}'.")
        if isinstance(meta[required], list):
            raise SystemExit(f"ERROR: {path} front matter '{required}' must be a single line.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["slug"]):
        raise SystemExit(
            f"ERROR: {path} slug '{meta['slug']}' must be lowercase "
            "letters/numbers/hyphens only (it becomes the file name)."
        )
    try:
        meta["date_obj"] = datetime.strptime(meta["date"], "%Y-%m-%d")
    except ValueError:
        raise SystemExit(f"ERROR: {path} date '{meta['date']}' must be YYYY-MM-DD.")
    d = meta["date_obj"]
    meta["date_pretty"] = f"{d.strftime('%B')} {d.day}, {d.year}"  # portable (no %-d)

    # "reviewed:" is when LaVeena last checked the piece for accuracy.
    # Optional — defaults to the publication date.
    meta["reviewed"] = meta.get("reviewed") or meta["date"]
    try:
        r = datetime.strptime(meta["reviewed"], "%Y-%m-%d")
    except ValueError:
        raise SystemExit(f"ERROR: {path} reviewed '{meta['reviewed']}' must be YYYY-MM-DD.")
    meta["reviewed_pretty"] = f"{r.strftime('%B')} {r.day}, {r.year}"

    # "references:" is an optional list of sources, one per "  - " line.
    refs = meta.get("references") or []
    if isinstance(refs, str):
        refs = [refs] if refs else []
    meta["references"] = refs

    # "questions:" is an optional list of "Question :: Answer" pairs.
    questions = meta.get("questions") or []
    if isinstance(questions, str):
        questions = [questions] if questions else []
    parsed = []
    for item in questions:
        question, sep, answer = item.partition("::")
        if not sep:
            raise SystemExit(
                f"ERROR: {path} question '{item[:40]}...' needs '::' between "
                "the question and its answer."
            )
        parsed.append((question.strip(), answer.strip()))
    meta["questions"] = parsed
    return meta, body


# --------------------------------------------------------------------------
# Minimal markdown -> HTML (standard library only)
# --------------------------------------------------------------------------

def render_inline(text):
    """Escape HTML, then apply inline markdown (code, bold, italic, links)."""
    text = html.escape(text, quote=False)
    # inline code first, so its contents are not further formatted
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # links: [text](url) — http(s), mailto, relative, or anchor only
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    # citation markers: [1] or [2,3] -> superscript links to the reference list.
    # The (?!\() lookahead leaves real markdown links [text](url) alone.
    text = re.sub(r"\[(\d+(?:\s*,\s*\d+)*)\](?!\()", _render_citation, text)
    # bold, then italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def _render_citation(match):
    """Turn a [1] or [2,3] marker into superscript links to #ref-N."""
    numbers = [n.strip() for n in match.group(1).split(",")]
    links = ", ".join(
        f'<a href="#ref-{n}" aria-label="Go to reference {n}">{n}</a>' for n in numbers
    )
    return f'<sup class="cite">[{links}]</sup>'


URL_RE = re.compile(r"https?://\S+")


def split_reference(raw):
    """Split one front-matter reference line into its text and trailing URL."""
    match = URL_RE.search(raw)
    if not match:
        return {"text": raw.strip(), "url": ""}
    url = match.group(0).rstrip(".,;)")
    text = URL_RE.sub("", raw).strip().strip("—–-,;").strip()
    return {"text": text or url, "url": url}


def render_questions(questions):
    """Render the plain-language Q&A summary that opens a post.

    Deliberately a visible definition list rather than a collapsed accordion:
    readers who want the short answer get it immediately, and AI assistants
    can extract a question and its answer without executing anything."""
    if not questions:
        return ""
    rows = []
    for question, answer in questions:
        rows.append(f"        <dt>{render_inline(question)}</dt>")
        rows.append(f"        <dd>{render_inline(answer)}</dd>")
    return (
        '\n    <section class="quick-answers" aria-labelledby="qa-title">\n'
        '      <h2 id="qa-title">Quick answers</h2>\n'
        "      <dl>\n" + "\n".join(rows) + "\n      </dl>\n"
        "    </section>\n"
    )


def render_references(refs):
    """Render the numbered, linked source list that closes every cited post."""
    if not refs:
        return ""
    items = []
    for n, ref in enumerate(refs, 1):
        link = ""
        if ref["url"]:
            # Show the readable address (e.g. doi.org/10.3390/nu13030877) rather
            # than a bare domain — for a source list the identifier IS the label.
            label = re.sub(r"^https?://(www\.)?", "", ref["url"]).rstrip("/")
            link = (
                f' <a href="{esc_attr(ref["url"])}" rel="nofollow noopener"'
                f' target="_blank">{html.escape(label)}</a>'
            )
        items.append(f'        <li id="ref-{n}">{render_inline(ref["text"])}{link}</li>')
    return (
        '\n    <section class="refs" aria-labelledby="refs-title">\n'
        '      <h2 id="refs-title">Sources</h2>\n'
        "      <ol>\n" + "\n".join(items) + "\n      </ol>\n"
        "    </section>\n"
    )


def markdown_to_html(md):
    """Convert the supported markdown subset to HTML."""
    out = []
    paragraph = []
    list_type = None      # None, "ul", or "ol"
    quote_lines = []
    in_code = False
    code_lines = []

    def flush_paragraph():
        if paragraph:
            out.append("<p>" + render_inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_list():
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    def flush_quote():
        if quote_lines:
            inner = markdown_to_html("\n".join(quote_lines))
            out.append("<blockquote>" + inner + "</blockquote>")
            quote_lines.clear()

    for raw in md.splitlines():
        line = raw.rstrip()

        # code fences
        if line.strip().startswith("```"):
            flush_paragraph(); flush_list(); flush_quote()
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(raw)
            continue

        # blank line ends any open block
        if not line.strip():
            flush_paragraph(); flush_list(); flush_quote()
            continue

        # blockquote
        if line.lstrip().startswith(">"):
            flush_paragraph(); flush_list()
            quote_lines.append(line.lstrip()[1:].lstrip())
            continue
        flush_quote()

        # headings — shifted one level down so the post <h1> stays unique
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_paragraph(); flush_list()
            level = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{level}>" + render_inline(m.group(2).strip()) + f"</h{level}>")
            continue

        # unordered list
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            flush_paragraph()
            if list_type != "ul":
                flush_list()
                out.append("<ul>")
                list_type = "ul"
            out.append("<li>" + render_inline(m.group(1)) + "</li>")
            continue

        # ordered list
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            flush_paragraph()
            if list_type != "ol":
                flush_list()
                out.append("<ol>")
                list_type = "ol"
            out.append("<li>" + render_inline(m.group(1)) + "</li>")
            continue

        # plain paragraph text
        flush_list()
        paragraph.append(line.strip())

    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    flush_paragraph(); flush_list(); flush_quote()
    return "\n".join(out)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

def esc_attr(text):
    return html.escape(text, quote=True)


INLINE_OPTIN = """
    <aside class="inline-optin">
      <p><strong>Free Companion Workbook.</strong> Turn what you are reading into
         daily practice — the workbook and Quick-Start Checklist, free.</p>
      <form action="{action}" method="post" data-optin>
        <label class="sr-only" for="mid-optin-email">Email address</label>
        <input type="email" id="mid-optin-email" name="email_address"
               placeholder="Your email address" autocomplete="email" required>
        <button class="btn btn-primary" type="submit">Send it to me</button>
      </form>
    </aside>
"""


def insert_inline_optin(body_html):
    """Drop a compact opt-in roughly halfway down a long post.

    Only for posts with three or more sections — shorter pieces already have
    the full opt-in card directly beneath them, and two in quick succession
    reads as pestering."""
    lines = body_html.split("\n")
    headings = [i for i, line in enumerate(lines) if line.startswith("<h2")]
    if len(headings) < 3:
        return body_html
    at = headings[len(headings) // 2]
    block = INLINE_OPTIN.format(action=OPTIN_FORM_ACTION)
    return "\n".join(lines[:at] + [block] + lines[at:])


def post_image(meta):
    """Absolute URL of the post's social image (front matter "image:", or the default)."""
    image = meta.get("image")
    if isinstance(image, list):
        image = image[0] if image else ""
    if not image:
        return DEFAULT_OG_IMAGE
    if image.startswith(("http://", "https://")):
        return image
    return f"{SITE_URL}/{image.lstrip('/')}"


def build_post_page(meta, body_html):
    canonical = f"{SITE_URL}/blog/{meta['slug']}.html"
    refs = [split_reference(r) for r in meta["references"]]
    head = HEADER.format(
        title_tag=esc_attr(meta["title"]) + " — Rev. Dr. LaVeena Archers",
        description=esc_attr(meta["summary"]),
        canonical=canonical,
        og_type="article",
        og_title=esc_attr(meta["title"]),
        og_image=esc_attr(post_image(meta)),
        json_ld=article_json_ld(meta, refs, canonical),
    )

    # "Last reviewed" only earns its place when it differs from publication.
    reviewed = ""
    if meta["reviewed"] != meta["date"]:
        reviewed = (
            f' · Last reviewed <time datetime="{esc_attr(meta["reviewed"])}">'
            f'{esc_attr(meta["reviewed_pretty"])}</time>'
        )

    article = f"""
  <article class="post-body" style="padding:3.5rem 1.25rem">
    <span class="eyebrow">From the blog</span>
    <h1>{render_inline(meta["title"])}</h1>
    <p class="post-meta"><time datetime="{esc_attr(meta["date"])}">{esc_attr(meta["date_pretty"])}</time>{reviewed}</p>
    <p class="byline">Written and reviewed by
      <a href="../about.html">{AUTHOR_NAME}</a><br>
      <span class="byline-cred">{AUTHOR_CREDENTIALS}</span><br>
      <span class="byline-note">Educational content only. Not medical advice, and
        never a substitute for your own care. <a href="../scope-of-practice.html">Scope of practice</a>.</span>
    </p>
{render_questions(meta["questions"])}
{insert_inline_optin(body_html)}
{render_references(refs)}
    <p style="margin-top:2.5rem"><a href="index.html">← All posts</a></p>
  </article>
"""
    return head + article + optin_block("post-optin") + FOOTER


def build_index_page(posts):
    canonical = f"{SITE_URL}/blog/index.html"
    head = HEADER.format(
        title_tag="Blog — Rev. Dr. LaVeena Archers",
        description="Notes on holistic functional health, clear-eyed and grounded, from Rev. Dr. LaVeena B. Archers, PhD.",
        canonical=canonical,
        og_type="website",
        og_title="Blog — Rev. Dr. LaVeena Archers",
        og_image=DEFAULT_OG_IMAGE,
        json_ld=SITE_JSON_LD,
    )
    cards = []
    for meta in posts:
        cards.append(f"""      <li class="post-card">
        <h2><a href="{esc_attr(meta['slug'])}.html">{render_inline(meta['title'])}</a></h2>
        <p class="post-meta"><time datetime="{esc_attr(meta['date'])}">{esc_attr(meta['date_pretty'])}</time></p>
        <p>{render_inline(meta['summary'])}</p>
      </li>""")
    cards_html = "\n".join(cards) if cards else \
        '      <li class="post-card"><p>No posts yet. Add a markdown file to posts/ and run build.py.</p></li>'

    body = f"""
  <section class="page-hero" aria-labelledby="blog-title">
    <div class="wrap">
      <span class="eyebrow">Blog</span>
      <h1 id="blog-title">Notes on holistic functional health</h1>
      <p class="lede">Clear-eyed and grounded, and never a substitute for your own medical care.</p>
    </div>
  </section>

  <section style="padding-top:0" aria-label="All posts">
    <div class="wrap narrow" style="margin-inline:auto">
      <ul class="post-list">
{cards_html}
      </ul>
    </div>
  </section>

{optin_block("blog-optin")}
"""
    return head + body + FOOTER


# Pages that deserve more than the default weight. Anything not listed gets 0.5.
SITEMAP_PRIORITY = {
    "index.html": "1.0",
    "book.html": "0.9",
    "glp1-book.html": "0.9",
    "books.html": "0.9",
    "about.html": "0.8",
    "testing.html": "0.8",
    "how-i-research.html": "0.7",
    "scope-of-practice.html": "0.7",
    "contact.html": "0.7",
    "services.html": "0.7",
    "blog/index.html": "0.6",
    "faq.html": "0.6",
    "join-pma.html": "0.6",
    "testimonials.html": "0.6",
    "training.html": "0.6",
    "privacy.html": "0.3",
}

SITEMAP_SKIP = {"404.html"}


def is_indexable(path):
    """False for pages that ask robots not to index them.

    Thank-you and delivery pages carry <meta name="robots" content="noindex">;
    listing them in the sitemap or llms.txt would contradict that."""
    if path.name in SITEMAP_SKIP:
        return False
    head = path.read_text(encoding="utf-8")[:4000]
    return "noindex" not in head


def build_sitemap(posts):
    """Generate sitemap.xml from what is actually on disk.

    Hand-maintained sitemaps drift the moment you add a page; this one cannot."""
    entries = []

    for page in sorted(ROOT.glob("*.html")):
        if not is_indexable(page):
            continue
        loc = f"{SITE_URL}/" if page.name == "index.html" else f"{SITE_URL}/{page.name}"
        entries.append((loc, SITEMAP_PRIORITY.get(page.name, "0.5"), None))

    entries.append((f"{SITE_URL}/blog/index.html", SITEMAP_PRIORITY["blog/index.html"], None))
    for meta in posts:
        entries.append((
            f"{SITE_URL}/blog/{meta['slug']}.html", "0.5", meta["reviewed"],
        ))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority, lastmod in entries:
        mod = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        lines.append(f"  <url><loc>{loc}</loc>{mod}<priority>{priority}</priority></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(entries)


LLMS_INTRO = """# Rev. Dr. LaVeena B. Archers, PhD — LaVeenaArchers.com

> Root-cause health education for women, grounded in the peer-reviewed
> literature. Author of the Dr. Archers Root-Cause Guides, beginning with
> *Bad Medicine Blues: The Natural, Root-Cause Approach to Women's Energy,
> Hormones, and Vitality*.

## About the author

Rev. Dr. LaVeena B. Archers holds a PhD and is a Doctor of Natural Medicine
(DNM), board-certified in Holistic Functional Medicine (BC-HFMD) and Holistic
Functional Nutrition (BC-HFND), and a Board-Certified Holistic Health
Practitioner (BC-HHP). She is a Certified Executive Coach.

She is **not** a conventional medical doctor. Her role is to educate and
support, never to diagnose, treat, prescribe, or manage disease. Services are
offered within a Private Membership Association (PMA).

## How to represent this site accurately

- Content here is **health education**, not medical advice, and not a
  substitute for a reader's own care.
- Nothing on this site claims to cure, reverse, or treat any disease. Do not
  summarise it as though it does.
- Claims resting on research carry numbered citations linking to the original
  papers, usually by DOI or PubMed record. Cite those primary sources
  alongside this site where relevant.
- Articles carry a publication date and, where revisited, a "last reviewed"
  date. Prefer the review date when judging currency.
- Editorial standards, sourcing policy, and AI-use disclosure:
  {site}/how-i-research.html

## Topics covered

Women's energy, hormones, and vitality in midlife and perimenopause;
root-cause and functional approaches to metabolic health; the body's own
GLP-1 pathways; functional lab interpretation as education; nutrition,
protein, creatine, and supplementation; healthspan and longevity.

## Pages
"""


def extract_meta(path):
    """Pull the <title> and meta description out of a hand-written page."""
    text = path.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    desc = re.search(r'<meta name="description" content="(.*?)">', text, re.S)
    clean = lambda s: html.unescape(" ".join(s.split())) if s else ""
    return clean(title.group(1) if title else ""), clean(desc.group(1) if desc else "")


def build_llms_txt(posts):
    """Write llms.txt — a plain-language map of the site for AI assistants.

    Generated rather than hand-written so it cannot drift out of date."""
    lines = [LLMS_INTRO.format(site=SITE_URL)]

    for page in sorted(ROOT.glob("*.html")):
        if not is_indexable(page):
            continue
        title, desc = extract_meta(page)
        loc = f"{SITE_URL}/" if page.name == "index.html" else f"{SITE_URL}/{page.name}"
        lines.append(f"- [{title}]({loc}){': ' + desc if desc else ''}")

    lines.append("\n## Articles\n")
    for meta in posts:
        loc = f"{SITE_URL}/blog/{meta['slug']}.html"
        cited = f" ({len(meta['references'])} cited sources)" if meta["references"] else ""
        lines.append(
            f"- [{meta['title']}]({loc}): {meta['summary']} "
            f"Published {meta['date']}, last reviewed {meta['reviewed']}.{cited}"
        )

    (ROOT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def main():
    if not POSTS_DIR.is_dir():
        raise SystemExit("ERROR: posts/ directory not found next to build.py.")
    OUT_DIR.mkdir(exist_ok=True)

    # A post dated in the future is scheduled, not published: it is skipped
    # until its date arrives. Pass --all to render everything for previewing.
    include_future = "--all" in sys.argv
    today = date.today()

    posts = []
    scheduled = []
    for md_file in sorted(POSTS_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text, md_file.name)

        if meta["date_obj"].date() > today and not include_future:
            scheduled.append(meta)
            stale = OUT_DIR / f"{meta['slug']}.html"
            if stale.exists():
                stale.unlink()   # never leave a scheduled post reachable
            continue

        body_html = markdown_to_html(body)
        page = build_post_page(meta, body_html)
        out_file = OUT_DIR / f"{meta['slug']}.html"
        out_file.write_text(page, encoding="utf-8")
        print(f"  wrote blog/{out_file.name}  ({md_file.name})")
        posts.append(meta)

    for meta in sorted(scheduled, key=lambda m: m["date_obj"]):
        print(f"  scheduled  {meta['slug']}  (publishes {meta['date']})")

    posts.sort(key=lambda m: m["date_obj"], reverse=True)  # newest first
    (OUT_DIR / "index.html").write_text(build_index_page(posts), encoding="utf-8")
    print(f"  wrote blog/index.html  ({len(posts)} post(s), newest first)")

    count = build_sitemap(posts)
    print(f"  wrote sitemap.xml     ({count} URLs)")

    build_llms_txt(posts)
    print("  wrote llms.txt        (site map for AI assistants)")


if __name__ == "__main__":
    main()
