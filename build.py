#!/usr/bin/env python3
"""
build.py — markdown blog generator for DoctorArchers.com.

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
           ---

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
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
OUT_DIR = ROOT / "blog"

SITE_URL = "https://book.doctorarchers.com"

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
<meta property="og:site_name" content="DoctorArchers.com">

<!-- Twitter card -->
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{description}">

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
    <a class="brand" href="../index.html">Dr. LaVeena Archers</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" hidden>Menu</button>
    <nav id="site-nav" class="site-nav" aria-label="Main">
      <a href="../index.html">Home</a>
      <a href="../about.html">About</a>
      <a href="../books.html">Books</a>
      <a href="../testing.html">Testing &amp; Reports</a>
      <a href="index.html" aria-current="page">Blog</a>
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
        <h3>Dr. LaVeena Archers</h3>
        <p>Awaken To Your ICONIC Potential.<br>Sedona, Arizona · serving clients worldwide.<br>© 2026 Rev. Dr. LaVeena B. Archers, PhD.</p>
      </div>
      <div>
        <h3>Contact</h3>
        <ul class="footer-links">
          <li><a href="mailto:hi@doctorarchers.com">hi@doctorarchers.com</a></li>
          <li><a href="[INSTAGRAM_URL]">Instagram</a></li>
        </ul>
      </div>
      <div>
        <h3>Explore</h3>
        <ul class="footer-links">
          <li><a href="../book.html">Bad Medicine Blues — the book</a></li>
          <li><a href="../testing.html">Testing &amp; Reports</a></li>
          <li><a href="https://labs.rupahealth.com/store/storefront_nYeZEmn" rel="noopener">Shop Labs</a></li>
          <li><a href="https://us.fullscript.com/welcome/iconic/store-start" rel="noopener">Shop Supplements</a></li>
          <li><a href="../privacy.html">Privacy</a></li>
        </ul>
      </div>
    </div>
    <p class="disclaimer"><strong>Scope of practice.</strong> Rev. Dr. LaVeena B. Archers is a Doctor of Natural Medicine and board-certified holistic practitioner. She is not a conventional medical doctor. Her role is to educate and support, not to diagnose, treat, prescribe, or manage diseases. Services are offered within a Private Membership Association (PMA). Nothing on this website is medical advice, and nothing here promises to cure, reverse, or treat any disease. Always seek the advice of a qualified medical professional with any questions about a medical condition.</p>
  </div>
</footer>

<script src="../assets/site.js"></script>
</body>
</html>
"""

SITE_JSON_LD = """{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://book.doctorarchers.com/#laveena",
      "name": "Rev. Dr. LaVeena B. Archers, PhD",
      "url": "https://book.doctorarchers.com/",
      "email": "mailto:hi@doctorarchers.com",
      "description": "Holistic Functional Medicine practitioner and author of Bad Medicine Blues. Educates and supports; does not diagnose, treat, prescribe, or manage disease.",
      "knowsAbout": ["Holistic Functional Medicine", "Functional nutrition", "Human Design", "Entrepreneur wellness", "Longevity"]
    },
    {
      "@type": "WebSite",
      "@id": "https://book.doctorarchers.com/#website",
      "url": "https://book.doctorarchers.com/",
      "name": "DoctorArchers.com",
      "publisher": { "@id": "https://book.doctorarchers.com/#laveena" },
      "inLanguage": "en"
    }
  ]
}"""


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
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()
        i += 1
    if i >= len(lines):
        raise SystemExit(f"ERROR: {path} front matter never closes with '---'.")
    body = "\n".join(lines[i + 1:])

    for required in ("title", "date", "slug", "summary"):
        if not meta.get(required):
            raise SystemExit(f"ERROR: {path} front matter is missing '{required}'.")
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
    # bold, then italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


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


def build_post_page(meta, body_html):
    canonical = f"{SITE_URL}/blog/{meta['slug']}.html"
    json_ld = SITE_JSON_LD
    head = HEADER.format(
        title_tag=esc_attr(meta["title"]) + " — Dr. LaVeena Archers",
        description=esc_attr(meta["summary"]),
        canonical=canonical,
        og_type="article",
        og_title=esc_attr(meta["title"]),
        json_ld=json_ld,
    )
    article = f"""
  <article class="post-body" style="padding:3.5rem 1.25rem">
    <span class="eyebrow">From the blog</span>
    <h1>{render_inline(meta["title"])}</h1>
    <p class="post-meta"><time datetime="{esc_attr(meta["date"])}">{esc_attr(meta["date_pretty"])}</time> · Rev. Dr. LaVeena B. Archers, PhD</p>
{body_html}
    <p style="margin-top:2.5rem"><a href="index.html">← All posts</a></p>
  </article>
"""
    return head + article + FOOTER


def build_index_page(posts):
    canonical = f"{SITE_URL}/blog/index.html"
    head = HEADER.format(
        title_tag="Blog — Dr. LaVeena Archers",
        description="Notes on holistic functional health, clear-eyed and grounded, from Rev. Dr. LaVeena B. Archers, PhD.",
        canonical=canonical,
        og_type="website",
        og_title="Blog — Dr. LaVeena Archers",
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

  <section class="alt" aria-labelledby="newsletter-title">
    <div class="wrap">
      <div class="optin-card">
        <span class="eyebrow">Newsletter</span>
        <h2 id="newsletter-title">Get new posts by email.</h2>
        <p>An occasional email when something new is published. No spam, and every email has a one-click unsubscribe.</p>
        <!--
          NEWSLETTER: point the action below at your email provider's form
          endpoint, or replace this whole <form> with your provider's embed
          code: https://app.kit.com/forms/9680706/subscriptions — see README.md.
        -->
        <form action="https://app.kit.com/forms/9680706/subscriptions" method="post" data-newsletter>
          <div>
            <label for="nl-email">Email address</label>
            <input type="email" id="nl-email" name="email_address" autocomplete="email" required>
          </div>
          <button class="btn btn-primary" type="submit">Subscribe</button>
          <p class="form-note" role="status" data-form-note>This form is not connected yet. Add your email provider's form action first (see the README).</p>
          <p class="microcopy">Used only to send you new posts. Never sold or shared.</p>
        </form>
      </div>
    </div>
  </section>
"""
    return head + body + FOOTER


def main():
    if not POSTS_DIR.is_dir():
        raise SystemExit("ERROR: posts/ directory not found next to build.py.")
    OUT_DIR.mkdir(exist_ok=True)

    posts = []
    for md_file in sorted(POSTS_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text, md_file.name)
        body_html = markdown_to_html(body)
        page = build_post_page(meta, body_html)
        out_file = OUT_DIR / f"{meta['slug']}.html"
        out_file.write_text(page, encoding="utf-8")
        print(f"  wrote blog/{out_file.name}  ({md_file.name})")
        posts.append(meta)

    posts.sort(key=lambda m: m["date_obj"], reverse=True)  # newest first
    (OUT_DIR / "index.html").write_text(build_index_page(posts), encoding="utf-8")
    print(f"  wrote blog/index.html  ({len(posts)} post(s), newest first)")


if __name__ == "__main__":
    main()
