# Liked House Markdown Design

## Goal

Make `liked-house/*.md` the canonical source for the deep analysis dashboard, and use `inbox.md` as the append-only list of newly liked Funda links.

## Approach

- Each liked listing has one markdown file in `liked-house/`.
- YAML frontmatter contains fields the dashboard can compute: address, price, area, ownership, VvE, scores, pros, cons, verdict, status, and the original Funda URL.
- Markdown body contains human-readable analysis sections: facts, ownership, VvE, pros, cons, dealbreakers, due diligence, and notes.
- `scripts/generate_dashboard.py` reads `liked-house/*.md` first. If the folder is empty, it falls back to `data/listings.json` for compatibility.
- Existing `data/listings.json` remains a legacy/cache file and can be trimmed later once the markdown library is mature.

## Scope

This change does not attempt to fully scrape every Funda page automatically. The first batch of markdown files records reliable information from URLs, existing local data, and explicitly marked verification gaps. Deeper per-listing facts can be filled in directly in each markdown file.
