---
name: dutch-home-criteria
description: >-
  Discover and document Dutch home buyer criteria: budget, mortgage, hard
  requirements (build year, energy label), soft preferences, dealbreakers. Writes
  config/buyer-profile.yaml. Use for new users, "what are my priorities", or
  updating search filters before house hunting.
---

# Dutch Home Criteria

Interview the buyer and maintain **`config/buyer-profile.yaml`**.

For a **different user** in the future, run this skill first to produce their own profile (same schema, different values).

## When to run

- First-time setup
- User changes budget, job location, or must-haves
- Before **dutch-home-search** if profile is missing or stale

## Interview checklist

Ask or infer:

1. **Budget**: max k.k. price, mortgage capacity, own funds, include erfpacht buyout?
2. **Hard requirements**: min build year, min energy label, regions/postcodes
3. **Commute**: days/week in office, destinations (e.g. Amsterdam Zuid/VU)
4. **Lifestyle**: tennis, groceries, parking, quiet vs central
5. **Dealbreakers**: social housing adjacent, erfpacht traps, max VvE, etc.
6. **Hold period**: short (rentability) vs long (comfort)

Use `assistant-design.md` and prior chat as defaults for **this** user if already documented.

## Output

Update `config/buyer-profile.yaml` with:

```yaml
budget:
  max_total_kk: 500000
  target_range: [400000, 450000]
  mortgage_estimate: [170000, 200000]
  own_funds: 132000

hard_requirements:
  min_build_year: 2000
  min_energy_label: B
  regions: [...]

soft_preferences: { ... }
dealbreakers: [ ... ]
```

Also sync hard filters into `config/search-zones.json` → `funda_filters` if budget bounds changed.

## Handoff

When profile is stable, tell user:

> Criteria saved. Next: run **dutch-home-search** to generate Funda links, or paste a Funda URL for **dutch-home-analyze**.

Do **not** score listings in this skill — only define criteria.
