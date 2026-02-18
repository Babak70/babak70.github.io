# Manual publication thumbnails

Put your cropped PNG thumbnails in this folder.

Suggested convention:
- Name the image to match the publication markdown filename (without `.md`), e.g.
  - `_publications/2023-04-20-Backpropagation-free.md` → `images/publications/manual/2023-04-20-Backpropagation-free.png`

Then set in the publication frontmatter:

```yaml
header:
  teaser: publications/manual/2023-04-20-Backpropagation-free.png
```
