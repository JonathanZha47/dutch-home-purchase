# VvE Checklist — Funda Field Mapping

When analyzing a listing, extract these from Funda **"VvE"** / **"Servicekosten"** sections.

## Funda fields → what they mean

| Funda label | Meaning | Watch for |
|-------------|---------|-----------|
| Servicekosten (VvE) | Monthly HOA fee | Compare to building age |
| VvE maandlasten | Same | Split garage/storage lines |
| Reservefonds | Reserve fund balance | Low balance + old building = risk |
| MJOP | Maintenance plan | Upcoming dak/gevel/schilderwerk |
| Inschrijving KvK | VvE registered | Should exist for formal VvE |
| VvE activa/passiva | Balance sheet | Ask at viewing if not public |

## Questions for viewing / agent

1. Recent or planned **groot onderhoud** (roof, facade, windows)?
2. Any **herstellingsbijdrage** (one-time special levy) voted or expected?
3. **Achterstallig onderhoud** or active disputes?
4. Is parking/garage in **same VvE** or separate entity?
5. For pre-2000 buildings: **sustainability fund** / energy upgrade plans?

## Red-flag keys (use in JSON)

| Key | When |
|-----|------|
| `low_reservefonds` | Reserve low vs building size/age |
| `planned_major_work` | MJOP shows expensive near-term work |
| `1980s_building_high_vve` | VvE >€250/mo on 1980s block |
| `split_vve_entities` | Apartment vs garage billed separately |
| `verify_mjop_and_reservefonds` | Must verify at viewing |

## Erfpacht checklist

| Situation | Impact |
|-----------|--------|
| **Eigen grond** | Best — no lease cost |
| **Paid until 20XX** | Note date; estimate buyout |
| **Canon about to jump** | Financial score ≤2 unless buyout in budget |

Annual canon >€2,000 with renewal within 3 years → flag as `erfpacht_trap`.
