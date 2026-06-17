---
name: dutch-home-analyze
description: >-
  Analyze a Dutch Funda listing: six-dimension score, Level 1 CBS bid estimate,
  VvE summary, pros/cons, append to HTML dashboard. Use when user shares a
  funda.nl/detail URL or asks to compare/score a specific property.
---

# Dutch Home Analyze

Score one listing and update the dashboard.

## Prerequisites

Read first:
- `config/buyer-profile.yaml`
- `criteria/scoring-rubric.md`
- `criteria/pricing-model.md`

## Workflow

```
- [ ] 1. Fetch Funda listing (or ask user to paste fields if captcha)
- [ ] 2. Score 6 dimensions (1–5) per scoring-rubric.md
- [ ] 3. Run Level 1 price estimate (estimate_price.py / add_listing auto)
- [ ] 4. Brief VvE + Erfpacht flags (full audit → dutch-home-vve after viewing)
- [ ] 5. Pros / cons / verdict
- [ ] 6. Save via add_listing.py → regenerate dashboard
```

## Data collection

Funda URL → extract ID from `/detail/(\d+)`.

If blocked, ask for: price, m², build year, energy label, VvE, erfpacht, address, postcode.

Set `pricing_tags` when relevant: `social_housing_nearby`, `erfpacht_trap`, `private_garage`.

Postcode auto-maps to neighborhood profile in `config/regional-pricing.json`.

## Scoring dimensions (total /30)

| ID | Label |
|----|-------|
| quality | 房屋质量 |
| size | 面积 |
| groceries | 买菜 |
| tennis | 网球 |
| transport | 交通 |
| financial | 真实财务 |

## Price estimate

```bash
python3 scripts/add_listing.py --file /tmp/listing.json
```

Uses CBS Level 1 model — see `criteria/pricing-model.md`. **Never use flat 10% overbid.**

## Persist

JSON schema: [examples.md](examples.md)

## Respond with

1. Score table + total /30
2. CBS 公允价 + 预估成交 + 真实成本
3. Top pros/cons
4. Verdict
5. Path: `dashboard/index.html`

## Related skills

- **dutch-home-vve** — after in-person viewing
- **dutch-home-search** — find more candidates
