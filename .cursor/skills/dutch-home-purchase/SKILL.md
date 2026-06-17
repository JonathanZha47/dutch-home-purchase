---
name: dutch-home-purchase
description: >-
  Orchestrator for Dutch home buying in the Randstad. Routes to sub-skills:
  criteria setup, Funda search, listing analysis/scoring, and post-viewing VvE
  audit. Use when buying a house in Netherlands, Funda listings, Dutch mortgage
  budget, or managing the property dashboard.
---

# Dutch Home Purchase (Orchestrator)

Parent skill for the `dutch-home-purchase/` project. **Do not do everything in one pass** — load the sub-skill that matches the user's intent.

## Sub-skills

| Skill | When to use | Path |
|-------|-------------|------|
| **dutch-home-criteria** | New user, update budget/priorities, brainstorm must-haves | `.cursor/skills/dutch-home-criteria/SKILL.md` |
| **dutch-home-search** | Find listings matching budget + hard filters | `.cursor/skills/dutch-home-search/SKILL.md` |
| **dutch-home-analyze** | Score a Funda URL, pros/cons, update dashboard | `.cursor/skills/dutch-home-analyze/SKILL.md` |
| **dutch-home-vve** | After bezichtiging: deep VvE / MJOP / reserve audit | `.cursor/skills/dutch-home-vve/SKILL.md` |

## Routing

```
User intent                          → Read this skill first
─────────────────────────────────────────────────────────────
"帮我搜房" / search / 找房           → dutch-home-search
"分析这套" / Funda URL / 打分        → dutch-home-analyze
"看过房了" / VvE / jaarverslag       → dutch-home-vve
"我的预算/要求" / 优先级 / criteria  → dutch-home-criteria
Unclear / full workflow              → dutch-home-criteria then search then analyze
```

## Project layout

```
dutch-home-purchase/
├── config/buyer-profile.yaml      # Budget + hard requirements (THIS user)
├── config/search-zones.json         # Target postcodes / Funda paths
├── config/regional-pricing.json     # Level 1 bid model
├── criteria/scoring-rubric.md
├── criteria/pricing-model.md
├── data/listings.json               # Analyzed properties
├── data/search/funda_search_urls.json
├── dashboard/index.html             # Open in browser
└── scripts/                         # add_listing, estimate_price, build_search_urls, …
```

Working directory: `dutch-home-purchase/`.

## Typical journey

1. **dutch-home-criteria** — confirm or update `buyer-profile.yaml`
2. **dutch-home-search** — generate Funda links, shortlist URLs
3. **dutch-home-analyze** — each URL → scores + dashboard
4. **dutch-home-vve** — after viewing, validate VvE before bidding

## Codex install

Link all sub-skills (run from repo root):

```bash
for s in dutch-home-purchase dutch-home-criteria dutch-home-search dutch-home-analyze dutch-home-vve; do
  ln -sf "$(pwd)/dutch-home-purchase/.cursor/skills/$s" ~/.codex/skills/$s
done
```

Cursor picks up project skills from `.cursor/skills/` automatically when this folder is open.
