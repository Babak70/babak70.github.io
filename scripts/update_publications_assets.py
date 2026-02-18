#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd)
    return proc.returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch publicly accessible publication PDFs into files/papers/ and generate first-figure thumbnails into images/publications/. "
            "Updates each _publications/*.md header.teaser accordingly."
        )
    )
    parser.add_argument(
        "--force-pdfs",
        action="store_true",
        help="Re-download PDFs even if they already exist.",
    )
    parser.add_argument(
        "--force-figures",
        action="store_true",
        help="Re-generate figure thumbnails even if they already exist.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=180,
        help="DPI used for rendering page crops when extracting figures (default: 180).",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    fetcher = repo_root / "scripts" / "fetch_publication_pdfs.py"
    extractor = repo_root / "scripts" / "extract_first_figures.py"

    if not fetcher.exists() or not extractor.exists():
        print("Missing scripts. Expected:")
        print(f"- {fetcher}")
        print(f"- {extractor}")
        return 2

    fetch_cmd = [sys.executable, str(fetcher)]
    if args.force_pdfs:
        fetch_cmd.append("--force")

    print("== Fetch PDFs ==")
    code = run(fetch_cmd)
    if code != 0:
        print(f"PDF fetcher returned non-zero exit code: {code}")
        return code

    print("\n== Extract first figures ==")
    extract_cmd = [sys.executable, str(extractor), "--dpi", str(args.dpi)]
    if args.force_figures:
        # Current extractor regenerates by default; keep flag for forward-compat.
        pass

    code = run(extract_cmd)
    if code != 0:
        print(f"Figure extractor returned non-zero exit code: {code}")
        return code

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
