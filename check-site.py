#!/usr/bin/env python3
"""Pre-deploy checks. Run against dist/ before publishing anything.

    python3 build.py && python3 stage-deploy.py && python3 check-site.py

Every check here exists because the corresponding thing was actually broken at
some point, not because it seemed like a good idea:

  links        A book page shipped an <img> pointing at a cover file that was
               never committed. It 404'd in the hero, og:image, twitter:image and
               the JSON-LD Book image simultaneously, for weeks.
  jsonld       33 JSON-LD blocks and no parser in the loop. One stray comma
               silently removes a page from every rich result.
  canonical    Cloudflare Pages 308-redirects /foo.html to /foo, so every
               canonical ending in .html pointed at a redirect instead of the URL
               that serves 200.
  alt          Restructuring <img> into <picture> is exactly the kind of edit
               that drops an alt attribute without anyone noticing.
  dimensions   width/height are what stop the page shifting as images load.
  lazy-lcp     loading="lazy" on an above-the-fold hero makes the page slower.
               It looks like an optimization, which is why it survives review.
  social       og:image pointing at .avif or .webp: most social scrapers will not
               render it, so the card silently breaks.
  leaks        The deploy used to publish the whole repo, including an unpublished
               book manuscript. This asserts dist/ never regains that shape.

Exit code is non-zero if any check fails, so it can gate a deploy.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SITE = "https://book.laveenaarchers.com"

failures: list[str] = []
warnings: list[str] = []


def fail(check: str, msg: str) -> None:
    failures.append(f"[{check}] {msg}")


def warn(check: str, msg: str) -> None:
    warnings.append(f"[{check}] {msg}")


def pages(base: Path) -> list[Path]:
    return sorted(base.rglob("*.html"))


def gated_slugs() -> set[str]:
    """The posts build.py holds out of the sitemap, llms.txt and the blog index.

    Parsed out of build.py's source rather than imported, because importing it
    runs a build as a side effect. Returns an empty set if the constant moves or
    is renamed — a missing gate is visible in the sitemap, whereas a check that
    crashes on every run gets deleted.
    """
    src = (ROOT / "build.py").read_text(encoding="utf-8")
    m = re.search(r"^GATED_POST_SLUGS\s*=\s*(set\(\)|\{[^}]*\})", src, re.M)
    if not m or m.group(1) == "set()":
        return set()
    return set(re.findall(r'"([^"]+)"', m.group(1)))


COMMENT = re.compile(r"<!--.*?-->", re.S)


def source(page: Path) -> str:
    """Page markup with HTML comments stripped.

    The comments on this site quote the markup they are explaining — several
    literally contain the string "<img>" while describing where a class belongs.
    Scanning raw text flags those as images with no alt attribute, which sends
    you looking for a bug in a file that is correct.
    """
    return COMMENT.sub("", page.read_text(encoding="utf-8", errors="replace"))


# --------------------------------------------------------------------------
def check_links(base: Path) -> None:
    """Every local src/href must resolve to a file that exists."""
    for page in pages(base):
        html = source(page)
        for attr, val in re.findall(r'\b(src|href)="([^"]+)"', html):
            if val.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#", "//")):
                continue
            path, _, _ = val.partition("#")
            path, _, _ = path.partition("?")
            if not path:
                continue
            target = (base / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
            if target.exists():
                continue
            # Extensionless internal links are the canonical form; Pages serves
            # /about from about.html. Resolve that before calling it broken.
            if (target.with_suffix(".html")).exists():
                continue
            if path.endswith("/") and (target / "index.html").exists():
                continue
            fail("links", f"{page.relative_to(base)} -> {val} (no such file)")


def check_jsonld(base: Path) -> None:
    for page in pages(base):
        html = source(page)
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        for i, block in enumerate(blocks):
            try:
                data = json.loads(block)
            except json.JSONDecodeError as e:
                fail("jsonld", f"{page.relative_to(base)} block {i+1} does not parse: {e}")
                continue
            flat = json.dumps(data)
            for banned in ("Physician", "MedicalBusiness", "MedicalWebPage",
                           "MedicalClinic", "MedicalOrganization", "Dentist"):
                if f'"{banned}"' in flat:
                    fail("jsonld", f"{page.relative_to(base)} uses {banned} — "
                                   "implies clinical practice, which she does not do")
            if "&amp;" in flat:
                warn("jsonld", f"{page.relative_to(base)} has an HTML entity in a "
                               "JSON string value (should be the literal character)")


def check_canonical(base: Path) -> None:
    for page in pages(base):
        rel = page.relative_to(base).as_posix()
        if rel in {"404.html", "review.html"} or rel.endswith("-thanks.html"):
            continue
        html = source(page)
        m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        if not m:
            warn("canonical", f"{rel} has no canonical")
            continue
        href = m.group(1)
        if href.endswith(".html"):
            fail("canonical", f"{rel} canonical ends in .html ({href}) — that URL "
                              "308-redirects; use the extensionless form")
        og = re.search(r'<meta property="og:url" content="([^"]+)"', html)
        if og and og.group(1) != href:
            fail("canonical", f"{rel} og:url ({og.group(1)}) != canonical ({href})")


def check_images(base: Path) -> None:
    for page in pages(base):
        rel = page.relative_to(base).as_posix()
        html = source(page)
        for tag in re.findall(r"<img\b[^>]*>", html):
            if 'alt="' not in tag and "alt='" not in tag:
                fail("alt", f"{rel}: <img> with no alt — {tag[:90]}")
            if "width=" not in tag or "height=" not in tag:
                warn("dimensions", f"{rel}: <img> without width/height — {tag[:90]}")
        # An image inside the first ~2500 chars of <body> is above the fold on
        # essentially every viewport; lazy-loading it delays the LCP.
        body = html.partition("<body")[2]
        for tag in re.findall(r"<img\b[^>]*>", body[:2500]):
            if 'loading="lazy"' in tag:
                fail("lazy-lcp", f"{rel}: above-the-fold image is loading=\"lazy\" — "
                                 f"this makes the page slower — {tag[:90]}")
        for prop in ("og:image", "twitter:image"):
            for val in re.findall(rf'(?:property|name)="{prop}" content="([^"]+)"', html):
                if val.endswith((".avif", ".webp")):
                    fail("social", f"{rel}: {prop} is {val} — social scrapers need "
                                   "a raster .jpg/.png")


def check_picture_sources(base: Path) -> None:
    """<source srcset> inside <picture> must point at files that exist."""
    for page in pages(base):
        html = source(page)
        for srcset in re.findall(r"<source\b[^>]*srcset=\"([^\"]+)\"", html):
            for cand in srcset.split(","):
                url = cand.strip().split()[0]
                if url.startswith(("http", "data:")):
                    continue
                t = (base / url.lstrip("/")) if url.startswith("/") else (page.parent / url)
                if not t.exists():
                    fail("links", f"{page.relative_to(base)} <source> -> {url} (missing)")


def check_placeholders(base: Path) -> None:
    """No unfilled placeholder may reach a reader.

    On 2026-08-07 a deploy published three of these to the live /training page,
    including a note addressed to the author asking whether the certifications
    were accredited. They were sitting in the working tree as in-progress copy;
    the deploy sweeps every root *.html, so it took them along.

    The guillemet markers are the house convention for "decide this before it
    ships". The bracketed forms are the older README-style placeholders.
    """
    patterns = [
        # Unbounded between the markers on purpose. A first attempt capped this
        # at 200 characters and missed the one that mattered most — a 340-char
        # note asking whether the certifications were accredited. The longest
        # placeholder is always the one carrying the real unresolved question.
        (re.compile(r"«[^»]*»"), "«…»"),
        (re.compile(r"\[(?:[A-Z][A-Z0-9_]{4,})\]"), "[UPPER_CASE]"),
        (re.compile(r"\bTK\b|\bTODO\b|\bFIXME\b"), "TK/TODO/FIXME"),
    ]
    for page in pages(base):
        html = source(page)
        body = html.partition("<body")[2] or html
        for rx, label in patterns:
            for m in rx.finditer(body):
                fail("placeholder", f"{page.relative_to(base)} still contains an "
                                    f"unfilled {label}: {m.group(0)[:70]}")


def check_leaks(base: Path) -> None:
    """dist/ must never contain source, notes, or manuscripts."""
    for f in base.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(base).as_posix()
        if f.suffix in {".py", ".pyc"}:
            fail("leaks", f"dist/ contains {rel} — build tooling must not be public")
        if f.suffix == ".md":
            fail("leaks", f"dist/ contains {rel} — manuscripts and notes must not "
                          "be public")
        if ".bak" in f.name:
            fail("leaks", f"dist/ contains {rel} — editor backup")
    if (base / "posts").exists():
        fail("leaks", "dist/posts/ exists — post SOURCES must not be published; "
                      "future-dated drafts live there")


def check_sitemap(base: Path) -> None:
    sm = base / "sitemap.xml"
    if not sm.exists():
        fail("sitemap", "no sitemap.xml in dist/")
        return
    xml = sm.read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", xml)
    if not locs:
        fail("sitemap", "sitemap.xml has no <loc> entries")
    for loc in locs:
        if loc.endswith(".html"):
            fail("sitemap", f"{loc} ends in .html — that URL 308-redirects")
        rel = loc.replace(SITE, "").lstrip("/") or "index.html"
        cand = base / rel
        if not (cand.exists() or cand.with_suffix(".html").exists()
                or (cand / "index.html").exists()):
            fail("sitemap", f"{loc} is in the sitemap but not in dist/")
    missing_lastmod = len(locs) - xml.count("<lastmod>")
    if missing_lastmod > 0:
        warn("sitemap", f"{missing_lastmod} of {len(locs)} entries have no <lastmod>")

    # Read the gate list out of build.py rather than naming a slug here. This
    # check used to hardcode "nature-glp1" and went stale the moment that post
    # was un-gated, failing a build that was correct — which is the same class
    # of bug it exists to catch.
    for slug in gated_slugs():
        if slug in xml:
            fail("sitemap", f"gated post '{slug}' is advertised in the sitemap")


def main() -> None:
    base = DIST if DIST.exists() else ROOT
    if base is ROOT:
        print("dist/ not found — checking the repo root instead. "
              "Run stage-deploy.py first for a real pre-deploy check.\n")

    for fn in (check_links, check_jsonld, check_canonical, check_images,
               check_picture_sources, check_sitemap, check_placeholders):
        fn(base)
    if base is DIST:
        check_leaks(base)

    n_pages = len(pages(base))
    if warnings:
        print(f"warnings ({len(warnings)}):")
        for w in warnings[:40]:
            print("  " + w)
        if len(warnings) > 40:
            print(f"  ... and {len(warnings)-40} more")
        print()
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print("  " + f)
        print(f"\n{len(failures)} problems across {n_pages} pages. Not safe to deploy.")
        sys.exit(1)
    print(f"all checks passed across {n_pages} pages"
          + (f" ({len(warnings)} warnings)" if warnings else ""))


if __name__ == "__main__":
    main()
