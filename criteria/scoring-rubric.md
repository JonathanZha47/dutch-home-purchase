# Scoring Rubric (1–5 per dimension)

Use this rubric consistently. Scores are integers or half-points (e.g. 4.5). Sum all six for **total /30**.

## 1. 房屋质量 (Quality) — build year, energy label, hardware

| Score | Criteria |
|-------|----------|
| 5 | Built ≥2010, label A+/A, elevator, modern insulation, private garage/parking, move-in ready |
| 4 | Built 2000–2009, label A/B, good condition, minor compromises |
| 3 | Built 2000+, label B, acceptable but dated interior or missing parking |
| 2 | Pre-2000 OR label C with mitigating factors (user waived age rule) |
| 1 | Pre-1990, label C/D, galley flat, major maintenance backlog |

**Hard rule:** If build year < 2000 or energy label < B, cap at 2 unless user explicitly overrides.

## 2. 面积 (Size)

| Score | Living area (m²) | Notes |
|-------|------------------|-------|
| 5 | ≥90 m² multi-bed / maisonnette | Best value for WFH + future rental |
| 4 | 80–89 m² 2-bed | Strong |
| 3 | 70–79 m² 2-bed or large 1-bed | Acceptable |
| 2 | 60–69 m² 1-bed | Tight for long-term |
| 1 | <60 m² | Too small |

Adjust ±0.5 for layout (open plan WFH) or extra storage/garage.

## 3. 买菜便利度 (Groceries)

| Score | Distance / access |
|-------|-------------------|
| 5 | AH/Jumbo/Lidl within 500 m walk |
| 4 | Supermarket within 1 km or strong Picnic/AH delivery zone |
| 3 | Small shop nearby; large supermarket ~1 km (bike ok) |
| 2 | Need car or delivery for regular shops |
| 1 | Remote; poor delivery coverage |

## 4. 网球场 (Tennis)

| Score | Cycling distance to club |
|-------|--------------------------|
| 5 | ≤2 km |
| 4 | 2–4 km |
| 3 | 4–5 km |
| 2 | 5–7 km |
| 1 | >7 km or no club in reasonable range |

Bonus +0.5 for indoor/outdoor club with good facilities (NTC, Toolenburg, etc.).

## 5. 交通 (Transport) — Amsterdam Zuid/VU (see `buyer-profile.yaml` transport_tiers)

Use **tier** from listing/zone config first, then fine-tune by minutes:

| Tier | Typical | Score guide (Zuid/VU) |
|------|---------|------------------------|
| **S** | Metro direct, no transfer (Bijlmer, Ganzenhoef corridor) | 5 |
| **A** | Train ~1 stop (Hoofddorp Centraal → Zuid) | 4.5–5 |
| **B** | ~1h train OK (Almere, Zaandam, Den Haag suburbs, Floriande) | 3–4 if ≤65 min |
| **watchlist** | Too far / won't visit (e.g. Nesselande ~2h) | ≤2 |

| Score | To Amsterdam Zuid/VU | Notes |
|-------|----------------------|-------|
| 5 | Tier S, or metro direct ≤20 min | Bijlmer, Ganzenhoef |
| 4.5 | Tier A, train ≤15 min minimal hops | Hoofddorp Centraal |
| 4 | Tier B but ≤45 min train total | Almere, Zaandam |
| 3 | Tier B ~45–65 min | Acceptable if size/price wins |
| 2 | >65 min or watchlist | Factor +€15k car if considering |
| 1 | ≥90 min, poor PT | |

Weight **Zuid/VU** for 2×/week office commute. **Do not** penalize tier B towns automatically — compare total package vs tier S/A.

## 6. 真实财务 (Financial) — bid + Erfpacht + VvE + KK

Estimate **true cost**:

```
true_cost = estimated_bid + erfpacht_buyout (if applicable) + buyer_costs (~6000)
monthly_carry = vve_monthly + erfpacht_monthly (after current term)
```

| Score | True cost vs €500k budget | Monthly carry |
|-------|----------------------------|---------------|
| 5 | ≤€380k true cost, eigen grond, VvE ≤€180 | Low |
| 4 | €380–420k, no surprise erfpacht | Moderate |
| 3 | €420–450k or erfpacht paid until ≥2030 | Acceptable |
| 2 | €450–500k OR high erfpacht kicking in ≤2 years | High VvE (>€250) |
| 1 | >€500k OR erfpacht trap (€3k+/yr soon) + overbid | Very high carry |

**Zaandam-style trap:** low ask + €3,400/yr erfpacht from 2027 → financial score ≤2 unless buyout priced in.

---

## VvE Red-Flag Checklist

Always inspect Funda **VvE** section and annual report (if available at viewing):

| Flag | Severity | Action |
|------|----------|--------|
| VvE reserve fund (reservefonds) low vs building age | 🔴 | Ask for MJOP (maintenance plan) |
| Planned major work (dak/schilder/gevel) not budgeted | 🔴 | Estimate special assessment (herstellingsbijdrage) |
| Monthly fee >> age-adjusted norm (>€300 for 1980s) | 🟡 | Compare similar buildings |
| Active legal disputes / achterstallig onderhoud | 🔴 | Walk away unless discounted |
| VvE owns only apartment, not garage (split fees) | 🟡 | Sum all components |
| Self-managed VvE (beheer door VvE) in large block | 🟡 | Check meeting minutes |
| No recent energy label upgrade plan for C/D building | 🟡 | Future cost risk |

**Norms (rule of thumb):**
- 2000+ building: VvE ~€80–180/mo typical
- 1980s building: VvE €200–350/mo can be normal if reserves healthy

---

## Verdict Labels

| Total /30 | Label |
|-----------|-------|
| ≥24 | 强烈推荐 |
| 21–23.5 | 值得看房 |
| 18–20.5 | 备选 |
| 15–17.5 | 谨慎 |
| <15 | 淘汰 |

Override verdict if any **dealbreaker** triggers.
