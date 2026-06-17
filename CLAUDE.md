# Dutch Home Purchase — Claude Code

Read the orchestrator skill first: `.cursor/skills/dutch-home-purchase/SKILL.md`

## Routing

| User intent | Skill |
|-------------|-------|
| Budget / priorities / transport tiers | `dutch-home-criteria` |
| Search Funda, shortlist, inbox board | `dutch-home-search` |
| Score a listing + dashboard | `dutch-home-analyze` |
| Post-viewing VvE audit | `dutch-home-vve` |

## Config

- Criteria: `config/buyer-profile.yaml`
- Search zones: `config/search-zones.json`
- Working directory: this folder (`dutch-home-purchase/`)

## After search or analysis

```bash
python3 scripts/regenerate_all.py
```

Open `dashboard/search-board.html` (inbox) or `dashboard/index.html` (analyzed).

## Transport tiers

S = metro direct Zuid · A = train ~1 stop (Hoofddorp Centraal) · B = ~1h train OK · watchlist = no viewing
