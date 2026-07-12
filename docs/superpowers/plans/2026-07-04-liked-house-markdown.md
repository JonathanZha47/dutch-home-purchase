# Liked House Markdown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Use per-listing markdown files as the dashboard source and create the initial liked-house library from the user's Funda URLs.

**Architecture:** Add a markdown loader to the existing dashboard generator rather than replacing the HTML renderer. Keep JSON fallback for old data. Generate missing listing markdown files from `inbox.md` with conservative fields and `verify` notes.

**Tech Stack:** Python 3, PyYAML, unittest, static HTML.

---

### Task 1: Markdown Loader

**Files:**
- Modify: `scripts/generate_dashboard.py`
- Modify: `tests/test_generate_dashboard.py`

- [x] Write a failing test showing one markdown file becomes a dashboard listing.
- [x] Implement YAML frontmatter parsing and `load_liked_house_listings`.
- [x] Make `load_listings` prefer `liked-house/*.md` and fall back to `data/listings.json`.
- [x] Render a source markdown link on each card.

### Task 2: Initial Content

**Files:**
- Create: `inbox.md`
- Create: `liked-house/*.md`

- [x] Add the supplied Funda URLs to `inbox.md`, grouped by region.
- [x] Generate one markdown file per URL with frontmatter fields and detailed sections.
- [x] Seed known facts from existing JSON and verified Funda pages where available.
- [x] Mark unknown ownership, VvE, prices, energy, or build year with `verify` rather than guessing.

### Task 3: Regeneration And Verification

**Files:**
- Modify: `dashboard/index.html`

- [x] Run the focused markdown loader test.
- [x] Run the full dashboard test file.
- [x] Regenerate `dashboard/index.html`.
- [x] Confirm the dashboard reports the markdown listing count and each card links to its source markdown file.
