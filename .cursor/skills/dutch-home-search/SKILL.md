---
name: dutch-home-search
description: >-
  Search Funda for Dutch homes matching buyer-profile hard filters and budget.
  Generates regional search URLs, scans for apartments ≥2000, energy B+, within
  price cap. Use when user asks to find/search/listings/houses to buy in
  Randstad Netherlands.
---

# Dutch Home Search

Find candidate listings using **`config/buyer-profile.yaml`** + **`config/search-zones.json`**.

## Workflow

```
- [ ] 1. Read buyer-profile.yaml (budget + hard requirements)
- [ ] 2. Run build_search_urls.py
- [ ] 3. Open each Funda URL (or WebFetch); collect 3–8 promising listings
- [ ] 4. Pre-filter against dealbreakers
- [ ] 5. Present shortlist with links → offer dutch-home-analyze on each
```

## Step 2 — Generate search URLs

```bash
cd dutch-home-purchase
python3 scripts/build_search_urls.py              # tier S+A (default — Bijlmer, Ganzenhoef, Hoofddorp Centraal, …)
python3 scripts/build_search_urls.py --tier all   # include Almere, Den Haag, watchlist zones
python3 scripts/build_search_urls.py --tier B     # ~1h train towns only
```

Transport tiers (see `buyer-profile.yaml`):
- **S** — Metro direct to Zuid: Bijlmer, Ganzenhoef, Amstelveen metro
- **A** — Train ~1 stop: Hoofddorp Centraal
- **B** — ~1h train OK: Almere, Zaandam, Den Haag suburbs, Floriande
- **watchlist** — Compare only (e.g. Nesselande)

Output: `data/search/funda_search_urls.json` + printed markdown.

Then sync inbox + regenerate boards:

```bash
python3 scripts/sync_inbox.py
python3 scripts/regenerate_all.py
```

Open **`dashboard/search-board.html`** to mark 想看 / 仅追踪 / 跳过 (browser localStorage).

## Step 3 — Scan Funda

Funda blocks bots. For each zone URL:

1. Give user the links to browse in app/browser, **or**
2. WebFetch if available; if captcha, ask user to paste 2–3 listing URLs per zone

**Pre-filter each candidate:**

| Check | Source |
|-------|--------|
| Price ≤ max_total_kk | Funda |
| Build year ≥ min_build_year | Funda (waive only with user OK) |
| Energy ≥ min_energy_label | Funda |
| Area / bed count vs preferences | Funda |
| Obvious dealbreakers | Description + maps (social housing, erfpacht) |

## Step 4 — Shortlist format

```markdown
## 搜房结果 — [date]

预算: €X–€Y | 硬条件: ≥2000, label ≥B

| # | 区域 | 地址 | 挂牌 | m² | 年份 | Label | 链接 | 备注 |
|---|------|------|------|-----|------|-------|------|------|
| 1 | Zaandam | ... | €395k | 88 | 2017 | A+ | funda | 有 erfpacht 风险 |

**建议下一步**: 对 #1 #2 运行 dutch-home-analyze
```

Save shortlist to `data/search/shortlist.json` if user wants persistence:

```json
{
  "searched_at": "2026-06-17",
  "listings": [
    { "funda_url": "...", "address": "...", "price_asking": 395000, "zone_id": "zaandam", "pre_filter_pass": true }
  ]
}
```

## Zone / transport tiers (this user)

**S — 最想要:** Bijlmer, Ganzenhoef / Zuidoost metro, Amstelveen metro → Zuid 不换乘  
**A:** Hoofddorp Centraal 火车 ~1 站到 Zuid  
**B — 也可考虑:** Almere, Zaandam, 海牙郊区, Floriande, Utrecht (~1h 火车)  
**watchlist:** 鹿特丹 Nesselande 等 — 仅追踪不看房  

No hard exclude for Randstad satellite towns — use tier + total cost vs size.

## Handoff

- **dutch-home-analyze** — full score + dashboard for a chosen URL
- **dutch-home-criteria** — if user wants to widen/narrow search
