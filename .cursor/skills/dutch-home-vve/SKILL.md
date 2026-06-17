---
name: dutch-home-vve
description: >-
  Post-viewing VvE audit for Dutch apartments: jaarverslag, reservefonds, MJOP,
  planned levies, red flags before bidding. Use after bezichtiging when user has
  VvE documents, Funda VvE section, or asks "is this VvE safe".
---

# Dutch Home VvE Audit

Run **after viewing** (bezichtiging), when user can supply VvE documents or detailed Funda VvE section.

For initial listing triage only, **dutch-home-analyze** gives a brief VvE summary — this skill goes deep.

## Inputs to request

| Document | Dutch name | Why |
|----------|------------|-----|
| Annual report | VvE jaarverslag | Income, reserves, debts |
| Balance sheet | activa/passiva | Reservefonds health |
| Maintenance plan | MJOP / meerjarenonderhoudsplan | Future special levies |
| Meeting minutes | notulen ALV | Voted repairs, disputes |
| Split fees | garage/berging separate VvE? | True monthly cost |

User may paste text, photos, or Funda VvE fields.

## Checklist

Full field mapping: [vve-checklist.md](vve-checklist.md)

### Red flags (🔴 walk away or discount heavily)

- Reservefonds far below MJOP needs
- Approved herstellingsbijdrage (special assessment) not reflected in price
- Achterstallig onderhoud / lawsuit mentioned in notulen
- VvE fee spike with no explanation

### Yellow flags (🟡 verify)

- 1980s building + VvE >€250/mo
- Energy C/D with no upgrade plan
- Self-managed VvE (beheer door VvE) in large block

## Output format

Update the listing in `data/listings.json`:

```json
{
  "vve_analysis": {
    "monthly_fee": 264,
    "reservefonds_eur": 120000,
    "mjop_summary": "Gevel 2028 geschat €800k → ~€4k/unit",
    "red_flags": ["planned_major_work", "1980s_building_high_vve"],
    "risk_level": "medium",
    "notes": "中文总结：..."
  },
  "viewing_completed": true,
  "viewing_date": "2026-06-17"
}
```

Then regenerate dashboard:

```bash
python3 scripts/add_listing.py --file updated-listing.json
```

## Verdict impact

| risk_level | Action |
|------------|--------|
| low | Proceed; adjust financial score up |
| medium | Bid lower or confirm MJOP at notary |
| high | 淘汰 unless major price discount |

## Handoff

- Re-run **dutch-home-analyze** financial dimension if VvE costs changed materially
- **dutch-home-criteria** if VvE dealbreakers need updating for future search
