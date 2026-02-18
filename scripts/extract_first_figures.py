#!/usr/bin/env python3

from __future__ import annotations

import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from PIL import Image, ImageChops


CAPTION_RE = re.compile(r"\b(fig\.?|figure)\s*1\b", re.IGNORECASE)


@dataclass(frozen=True)
class ExtractResult:
    slug: str
    pdf: str
    image: Optional[str]
    status: str
    detail: Optional[str] = None


def trim_whitespace(img: Image.Image) -> Image.Image:
    if img.mode != "RGB":
        img = img.convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    return img.crop(bbox) if bbox else img


def pixmap_to_pil(pix: fitz.Pixmap) -> Image.Image:
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)  # drop alpha
    if pix.colorspace and pix.colorspace.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def find_figure1_caption_rect(page: fitz.Page) -> Optional[fitz.Rect]:
    blocks = page.get_text("blocks")
    for block in blocks:
        # (x0, y0, x1, y1, "text", block_no, block_type)
        x0, y0, x1, y1, text, _, block_type = block
        if block_type != 0:
            continue
        normalized = " ".join((text or "").split())
        if CAPTION_RE.search(normalized):
            return fitz.Rect(x0, y0, x1, y1)
    return None


def render_clip(page: fitz.Page, rect: fitz.Rect, *, dpi: int = 180) -> Image.Image:
    pix = page.get_pixmap(clip=rect, dpi=dpi, alpha=False)
    return trim_whitespace(pixmap_to_pil(pix))


def extract_by_caption(doc: fitz.Document, max_pages: int = 3) -> Optional[Image.Image]:
    for page_index in range(min(max_pages, doc.page_count)):
        page = doc.load_page(page_index)
        caption_rect = find_figure1_caption_rect(page)
        if not caption_rect:
            continue

        # Heuristic: crop the region above the caption as the figure.
        page_rect = page.rect
        top_margin = 0
        left_margin = 0
        right_margin = 0
        bottom = max(top_margin + 50, caption_rect.y0)  # avoid tiny crop
        crop_rect = fitz.Rect(
            left_margin,
            top_margin,
            page_rect.width - right_margin,
            min(bottom, page_rect.height),
        )
        img = render_clip(page, crop_rect)
        # Avoid returning near-empty crops
        if img.size[0] >= 200 and img.size[1] >= 120:
            return img
    return None


def extract_first_large_embedded_image(doc: fitz.Document, max_pages: int = 3) -> Optional[Image.Image]:
    for page_index in range(min(max_pages, doc.page_count)):
        page = doc.load_page(page_index)
        images = page.get_images(full=True)
        for img_info in images:
            xref = img_info[0]
            try:
                extracted = doc.extract_image(xref)
            except Exception:
                continue

            img_bytes = extracted.get("image")
            if not img_bytes:
                continue

            try:
                img = Image.open(io.BytesIO(img_bytes))
                img.load()
            except Exception:
                continue

            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                img = bg
            img = trim_whitespace(img)

            # Skip tiny icons/logos
            if img.size[0] * img.size[1] < 120_000:
                continue
            return img
    return None


def fallback_first_page_thumbnail(doc: fitz.Document) -> Image.Image:
    page = doc.load_page(0)
    return render_clip(page, page.rect)


def update_publication_teaser(publication_path: Path, teaser_rel: str) -> None:
    text = publication_path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("---"):
        return

    parts = text.split("---", 2)
    if len(parts) < 3:
        return
    prefix, frontmatter, rest = parts[0], parts[1], parts[2]
    fm_lines = frontmatter.splitlines()

    # Ensure we never introduce tabs in YAML.
    teaser_line = f"  teaser: {teaser_rel}"
    if any(line.strip() == "header:" for line in fm_lines):
        out_lines: list[str] = []
        in_header = False
        teaser_written = False
        header_indent = ""
        for line in fm_lines:
            stripped = line.strip()
            if stripped == "header:":
                in_header = True
                header_indent = line[: len(line) - len(line.lstrip(" "))]
                out_lines.append(line)
                continue

            if in_header:
                # Leaving header block when indentation decreases or new top-level key.
                if stripped and not line.startswith(header_indent + " "):
                    if not teaser_written:
                        out_lines.append(header_indent + teaser_line)
                        teaser_written = True
                    in_header = False
                elif stripped.startswith("teaser:"):
                    out_lines.append(header_indent + teaser_line)
                    teaser_written = True
                    continue

            out_lines.append(line)

        if in_header and not teaser_written:
            out_lines.append(header_indent + teaser_line)
        fm_lines = out_lines
    else:
        # Add header at end of frontmatter.
        fm_lines.append("header:")
        fm_lines.append(teaser_line)

    new_text = "---".join([prefix, "\n".join(fm_lines) + "\n", rest])
    publication_path.write_text(new_text, encoding="utf-8")


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    pdf_dir = repo_root / "files" / "papers"
    out_dir = repo_root / "images" / "publications"
    pubs_dir = repo_root / "_publications"
    out_dir.mkdir(parents=True, exist_ok=True)

    dpi = 180
    if "--dpi" in argv:
        try:
            dpi = int(argv[argv.index("--dpi") + 1])
        except Exception:
            pass

    results: list[ExtractResult] = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        slug = pdf_path.stem
        pub_md = pubs_dir / f"{slug}.md"
        if not pub_md.exists():
            results.append(ExtractResult(slug=slug, pdf=str(pdf_path), image=None, status="skipped", detail="No matching _publications markdown"))
            continue

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            results.append(ExtractResult(slug=slug, pdf=str(pdf_path), image=None, status="error", detail=str(e)))
            continue

        img: Optional[Image.Image] = None
        method = None
        try:
            img = extract_by_caption(doc)
            method = "caption" if img else None
            if img is None:
                img = extract_first_large_embedded_image(doc)
                method = "embedded-image" if img else None
            if img is None:
                img = fallback_first_page_thumbnail(doc)
                method = "fallback-page"

            if img is None:
                results.append(ExtractResult(slug=slug, pdf=str(pdf_path), image=None, status="error", detail="No image extracted"))
                continue

            # Resize for web thumbnail.
            img = trim_whitespace(img)
            img.thumbnail((900, 900))

            out_path = out_dir / f"{slug}.png"
            img.save(out_path, format="PNG", optimize=True)

            teaser_rel = f"publications/{slug}.png"
            update_publication_teaser(pub_md, teaser_rel)

            results.append(ExtractResult(slug=slug, pdf=str(pdf_path), image=str(out_path), status="ok", detail=method))
        except Exception as e:
            results.append(ExtractResult(slug=slug, pdf=str(pdf_path), image=None, status="error", detail=str(e)))
        finally:
            doc.close()

    ok = sum(1 for r in results if r.status == "ok")
    skipped = sum(1 for r in results if r.status == "skipped")
    errors = sum(1 for r in results if r.status == "error")
    print(f"Done. ok={ok} skipped={skipped} errors={errors}")
    for r in results:
        if r.status != "ok":
            print(f"- {r.slug}: {r.status} ({r.detail})")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
