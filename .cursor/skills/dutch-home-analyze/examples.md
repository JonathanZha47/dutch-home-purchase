# Listing JSON Examples

## Minimal template

```json
{
  "id": "FundaListingId",
  "funda_url": "https://www.funda.nl/detail/12345678",
  "address": "Street 1, City",
  "city": "Hoofddorp",
  "postcode": "2132",
  "price_asking": 365000,
  "living_area_m2": 70,
  "bedrooms": 1,
  "build_year": 2018,
  "energy_label": "A",
  "vve_monthly": 130,
  "erfpacht": {
    "type": "eigen_grond",
    "summary": "永久产权，无地租",
    "buyout_cost_estimate": 0
  },
  "buyer_costs_eur": 6000,
  "pricing_tags": ["private_garage"],
  "scores": {
    "quality": 4.5,
    "size": 2,
    "groceries": 5,
    "tennis": 4,
    "transport": 4.5,
    "financial": 4
  },
  "pros": ["..."],
  "cons": ["..."],
  "vve_analysis": { "monthly_fee": 130, "red_flags": [], "notes": "..." },
  "verdict": "值得看房",
  "analyzed_at": "2026-06-17",
  "status": "active"
}
```

`price_estimated_bid`, `true_cost_eur`, `monthly_carry_eur` auto-computed by `add_listing.py`.

## Commands

```bash
python3 scripts/add_listing.py --file listing.json
python3 scripts/reestimate_all.py
python3 scripts/generate_dashboard.py
```
