#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


RE_PAPERURL = re.compile(r"^paperurl:\s*['\"]?(?P<url>[^'\"\n]+)['\"]?\s*$", re.MULTILINE)
RE_FRONTMATTER = re.compile(r"\A---\s*\n(?P<fm>.*?\n)---\s*\n", re.DOTALL)


@dataclass(frozen=True)
class DownloadResult:
    publication_file: str
    paperurl: Optional[str]
    download_url: Optional[str]
    output_path: Optional[str]
    status: str
    detail: Optional[str] = None


def _extract_paperurl(markdown_text: str) -> Optional[str]:
    match = RE_PAPERURL.search(markdown_text)
    if not match:
        return None
    return match.group("url").strip()


def _arxiv_abs_to_pdf(url: str) -> Optional[str]:
    m = re.search(r"https?://arxiv\.org/abs/(?P<id>[^?#/]+)", url)
    if not m:
        return None
    arxiv_id = m.group("id")
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


def _biorxiv_abstract_to_pdf(url: str) -> Optional[str]:
    if "biorxiv.org" not in url:
        return None
    if url.endswith(".abstract"):
        return url[: -len(".abstract")] + ".full.pdf"
    if url.endswith(".full"):
        return url + ".pdf"
    if url.endswith(".full.pdf"):
        return url
    return None


def derive_download_url(paperurl: str) -> Optional[str]:
    paperurl = paperurl.strip()

    # Prefer arXiv if present.
    arxiv_pdf = _arxiv_abs_to_pdf(paperurl)
    if arxiv_pdf:
        return arxiv_pdf
    if re.search(r"https?://arxiv\.org/pdf/[^?#]+\.pdf", paperurl):
        return paperurl

    # Next: known preprint hosts.
    biorxiv_pdf = _biorxiv_abstract_to_pdf(paperurl)
    if biorxiv_pdf:
        return biorxiv_pdf

    # If it's already a direct PDF (e.g., workshop sites).
    if paperurl.lower().endswith(".pdf"):
        return paperurl

    return None


def safe_slug_from_filename(publication_path: Path) -> str:
    # Example: 2023-04-20-Backpropagation-free.md -> 2023-04-20-Backpropagation-free
    return publication_path.stem


def _referer_for(url: str) -> str:
    # Some hosts (e.g., bioRxiv) block non-browser traffic unless a Referer is set.
    m = re.match(r"^(https?://[^/]+)", url)
    return m.group(1) if m else "https://example.com"


def download_pdf(url: str, out_path: Path, *, referer: Optional[str] = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={
            # Some hosts (notably bioRxiv) are picky; a minimal UA works reliably here.
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/pdf,*/*;q=0.8",
            "Referer": referer or _referer_for(url),
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    # Small sanity check: many hosts return HTML error pages.
    if data[:4] != b"%PDF":
        raise ValueError("Downloaded content does not look like a PDF")
    out_path.write_bytes(data)


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    publications_dir = repo_root / "_publications"
    output_dir = repo_root / "files" / "papers"
    manifest_path = output_dir / "manifest.json"

    dry_run = "--dry-run" in argv
    force = "--force" in argv

    results: list[DownloadResult] = []
    for pub_file in sorted(publications_dir.glob("*.md")):
        text = pub_file.read_text(encoding="utf-8")
        paperurl = _extract_paperurl(text)
        if not paperurl:
            results.append(
                DownloadResult(
                    publication_file=str(pub_file.relative_to(repo_root)),
                    paperurl=None,
                    download_url=None,
                    output_path=None,
                    status="skipped",
                    detail="No paperurl found",
                )
            )
            continue

        download_url = derive_download_url(paperurl)
        if not download_url:
            results.append(
                DownloadResult(
                    publication_file=str(pub_file.relative_to(repo_root)),
                    paperurl=paperurl,
                    download_url=None,
                    output_path=None,
                    status="skipped",
                    detail="No supported download URL (not arXiv/bioRxiv/direct PDF)",
                )
            )
            continue

        slug = safe_slug_from_filename(pub_file)
        out_path = output_dir / f"{slug}.pdf"
        if out_path.exists() and not force:
            results.append(
                DownloadResult(
                    publication_file=str(pub_file.relative_to(repo_root)),
                    paperurl=paperurl,
                    download_url=download_url,
                    output_path=str(out_path.relative_to(repo_root)),
                    status="exists",
                )
            )
            continue

        if dry_run:
            results.append(
                DownloadResult(
                    publication_file=str(pub_file.relative_to(repo_root)),
                    paperurl=paperurl,
                    download_url=download_url,
                    output_path=str(out_path.relative_to(repo_root)),
                    status="dry-run",
                )
            )
            continue

        try:
            referer = _referer_for(download_url) if "biorxiv.org" in download_url else paperurl
            download_pdf(download_url, out_path, referer=referer)
            results.append(
                DownloadResult(
                    publication_file=str(pub_file.relative_to(repo_root)),
                    paperurl=paperurl,
                    download_url=download_url,
                    output_path=str(out_path.relative_to(repo_root)),
                    status="downloaded",
                )
            )
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            if out_path.exists():
                try:
                    out_path.unlink()
                except OSError:
                    pass
            results.append(
                DownloadResult(
                    publication_file=str(pub_file.relative_to(repo_root)),
                    paperurl=paperurl,
                    download_url=download_url,
                    output_path=str(out_path.relative_to(repo_root)),
                    status="error",
                    detail=str(e),
                )
            )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir.relative_to(repo_root)),
        "results": [r.__dict__ for r in results],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    downloaded = sum(1 for r in results if r.status == "downloaded")
    skipped = sum(1 for r in results if r.status == "skipped")
    errors = sum(1 for r in results if r.status == "error")
    print(f"Done. downloaded={downloaded} skipped={skipped} errors={errors}")
    print(f"Manifest: {manifest_path}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
