# Listing JSON Examples

See dutch-home-analyze skill. Minimal template:

```json
{
  "id": "FundaListingId",
  "funda_url": "https://www.funda.nl/detail/12345678",
  "address": "Street 1, City",
  "city": "Hoofddorp",
  "postcode": "2132",
  "price_asking": 365000,
  "living_area_m2": 70,
  "build_year": 2018,
  "energy_label": "A",
  "vve_monthly": 130,
  "scores": { "quality": 4.5, "size": 2, "groceries": 5, "tennis": 4, "transport": 4.5, "financial": 4 },
  "pros": ["..."],
  "cons": ["..."],
  "verdict": "值得看房",
  "analyzed_at": "2026-06-17"
}
```

Full examples: `.cursor/skills/dutch-home-analyze/examples.md`
