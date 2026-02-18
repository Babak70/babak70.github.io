Personal page of Babak Rahmani. Forked from [Stuart Geiger](https://github.com/staeiou) and from the [Minimal Mistakes Jekyll Theme](https://mmistakes.github.io/minimal-mistakes/), which is © 2016 Michael Rose and released under the MIT License. See LICENSE.md.

## Update publication assets (PDFs + figure thumbnails)

This repo can fetch publicly accessible paper PDFs (preferring arXiv when available) into `files/papers/`, then generate a thumbnail for each paper (best-effort “Figure 1” extraction with fallbacks) into `images/publications/` and update each publication’s `header.teaser`.

Run:

`python3 scripts/update_publications_assets.py`

Optional:

`python3 scripts/update_publications_assets.py --force-pdfs`

