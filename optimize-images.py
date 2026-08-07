#!/usr/bin/env python3
"""Generate AVIF + WebP derivatives at the sizes the pages actually display.

The originals stay exactly where they are. They remain the `<img src>` fallback
and — importantly — the `og:image` / `twitter:image` / JSON-LD `image` target,
because social-card scrapers are not reliably AVIF- or WebP-aware. Only the
`<source>` elements inside `<picture>` point at what this script produces.

Naming is `<stem>-<width>.avif` / `<stem>-<width>.webp`, so markup can be written
against a predictable name without consulting a manifest.

Sizing rationale: every target below is 2x the largest CSS width the image is
ever displayed at, which covers retina without paying for the 3-4x oversampling
the originals currently ship. The 21 certificates are the clearest case — each is
1000-1280px intrinsic for a slot that computes to 296 CSS px at every breakpoint.

Idempotent: re-running skips derivatives already newer than their source.

    python3 optimize-images.py            # generate
    python3 optimize-images.py --report   # show the savings, generate nothing
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

# stem -> widths to emit. Each width is 2x the largest CSS display width.
TARGETS: dict[str, list[int]] = {
    # Book covers. Largest display is 300 CSS px (book.html hero); index.html and
    # books.html show the same file smaller and reuse the 600px file.
    "bad-medicine-blues-cover": [600],
    "good-years-cover": [600],
    "glp1-book-cover": [600],
    # Author portrait, displayed at 280 CSS px.
    "laveena-archers-portrait": [560],
    # Certifying-boards banner, full container width on desktop.
    "certifications": [1078],
}

# Every certificate renders in a 296 CSS px slot -> 600px covers 2x DPR.
CREDENTIAL_WIDTH = 600

# Visually-lossless settings, chosen by measuring PSNR against the originals
# rather than by taste. -sharp_yuv matters on the certificates, which are full of
# thin dark text on white where naive chroma subsampling smears the strokes.
CWEBP = ["-q", "82", "-sharp_yuv", "-m", "6", "-quiet"]
AVIFENC = ["-q", "63", "-s", "4"]


def sources() -> list[tuple[Path, int]]:
    out: list[tuple[Path, int]] = []
    for stem, widths in TARGETS.items():
        for ext in (".png", ".jpg", ".jpeg"):
            p = ASSETS / f"{stem}{ext}"
            if p.exists():
                out.extend((p, w) for w in widths)
                break
        else:
            print(f"  ! no source found for {stem}", file=sys.stderr)
    for p in sorted((ASSETS / "credentials").iterdir()):
        if p.suffix.lower() in {".png", ".jpg", ".jpeg"} and "-600." not in p.name:
            out.append((p, CREDENTIAL_WIDTH))
    return out


def resized_png(src: Path, width: int, tmp: Path) -> Path:
    """Downscale to `width` and write a lossless PNG for the encoders to read.

    Going through PNG rather than piping the original keeps the encoders from
    re-encoding JPEG artifacts, and normalizes the palette-mode ("P") certificate
    scans to RGB, which cwebp handles far better.
    """
    with Image.open(src) as im:
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") and _has_alpha(im) else "RGB")
        if im.width > width:
            h = round(im.height * width / im.width)
            im = im.resize((width, h), Image.LANCZOS)
        out = tmp / f"{src.stem}-{width}.png"
        im.save(out)
    return out


def _has_alpha(im: Image.Image) -> bool:
    if im.mode == "P":
        return "transparency" in im.info
    return im.mode in ("RGBA", "LA")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    tmp = ROOT / ".img-tmp"
    tmp.mkdir(exist_ok=True)

    before = after = 0
    made = skipped = 0

    for src, width in sources():
        avif = src.with_name(f"{src.stem}-{width}.avif")
        webp = src.with_name(f"{src.stem}-{width}.webp")
        orig = src.stat().st_size
        before += orig

        fresh = (avif.exists() and webp.exists()
                 and avif.stat().st_mtime > src.stat().st_mtime
                 and webp.stat().st_mtime > src.stat().st_mtime)

        if args.report or fresh:
            if fresh:
                after += avif.stat().st_size
                skipped += 1
            continue

        staged = resized_png(src, width, tmp)
        subprocess.run(["cwebp", *CWEBP, str(staged), "-o", str(webp)],
                       check=True, capture_output=True)
        subprocess.run(["avifenc", *AVIFENC, str(staged), str(avif)],
                       check=True, capture_output=True)
        staged.unlink()

        after += avif.stat().st_size
        made += 1
        print(f"  {src.name:<62} {orig/1024:>7.0f}K -> "
              f"avif {avif.stat().st_size/1024:>6.1f}K  webp {webp.stat().st_size/1024:>6.1f}K")

    for leftover in tmp.glob("*"):
        leftover.unlink()
    tmp.rmdir()

    if not args.report:
        print(f"\ngenerated {made} pairs, {skipped} already current")
        print(f"originals {before/1024:.0f} KB -> AVIF {after/1024:.0f} KB "
              f"({100 * (1 - after / before):.1f}% smaller)")


if __name__ == "__main__":
    main()
