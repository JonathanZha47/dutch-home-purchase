#!/usr/bin/env python3
"""Level 1 price estimate: CBS municipal average + neighborhood/overbid adjustments."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRICING_CONFIG = ROOT / "config" / "regional-pricing.json"
CBS_CACHE = ROOT / "data" / "cbs" / "market_cache.json"


def _load_pricing_config() -> dict:
    return json.loads(PRICING_CONFIG.read_text(encoding="utf-8"))


def load_cbs_cache() -> dict:
    if not CBS_CACHE.exists():
        from fetch_cbs_market import main as refresh

        refresh()
    return json.loads(CBS_CACHE.read_text(encoding="utf-8"))


def resolve_cbs_region(listing: dict, pricing: dict) -> tuple[str, str, dict | None, str | None]:
    postcode = str(listing.get("postcode", "")).strip()
    prefix = postcode[:4] if len(postcode) >= 4 else ""
    profile_name = listing.get("neighborhood_profile")
    profile = None

    pc_profiles = pricing.get("postcode_profiles", {})
    if not profile_name and prefix in pc_profiles:
        profile_name = pc_profiles[prefix].get("profile")

    if profile_name:
        profile = pricing.get("neighborhood_profiles", {}).get(profile_name)

    if profile:
        return profile["cbs_region"], profile.get("municipality_label", ""), profile, profile_name

    city = listing.get("city", "")
    muni_map = pricing.get("municipality_map", {})
    key = muni_map.get(city, "NL01")
    return key, city, None, None


def get_cbs_municipal_avg(cbs_cache: dict, municipality_label: str, year: str = "2024") -> int | None:
    regional = cbs_cache.get("regional_annual_avg_eur", {})
    muni = regional.get(municipality_label, {})
    if year in muni:
        return muni[year]
    years = sorted(muni.keys(), reverse=True)
    return muni[years[0]] if years else None


def label_for_cbs_key(cbs_key: str, pricing: dict) -> str:
    for city, key in pricing.get("municipality_map", {}).items():
        if key == cbs_key:
            return city
    fallback = {
        "GM0363": "Amsterdam",
        "GM0394": "Haarlemmermeer",
        "GM0479": "Zaanstad",
        "GM0513": "Gouda",
        "PV27": "Noord-Holland",
        "PV28": "Zuid-Holland",
        "NL01": "Netherlands",
    }
    return fallback.get(cbs_key, "Netherlands")


def energy_factor(label: str | None, pricing: dict) -> float:
    if not label:
        return 1.0
    return float(pricing.get("energy_factors", {}).get(label.upper().replace(" ", ""), 1.0))


def age_factor(build_year: int | None, pricing: dict) -> float:
    if not build_year:
        return 1.0
    min_year = pricing.get("age_factors", {}).get("min_year", 2000)
    if build_year < min_year:
        return float(pricing.get("age_factors", {}).get("factor_if_below", 0.92))
    return 1.0


def collect_tag_adjustments(listing: dict, profile: dict | None, pricing: dict) -> float:
    tags = set(listing.get("pricing_tags", []))
    if profile:
        tags.update(profile.get("tags", []))
    if listing.get("near_social_housing"):
        tags.add("social_housing_nearby")
    adj_map = pricing.get("tag_overbid_adjustments", {})
    return sum(adj_map.get(t, 0.0) for t in tags)


def estimate_listing(listing: dict, pricing: dict | None = None, cbs_cache: dict | None = None) -> dict:
    pricing = pricing or _load_pricing_config()
    cbs_cache = cbs_cache or load_cbs_cache()

    asking = int(listing.get("price_asking") or 0)
    area_m2 = float(listing.get("living_area_m2") or pricing.get("reference_m2", 85))
    reference_m2 = float(pricing.get("reference_m2", 85))

    cbs_key, muni_label, profile, profile_name = resolve_cbs_region(listing, pricing)
    if not muni_label:
        muni_label = label_for_cbs_key(cbs_key, pricing)

    cbs_avg = get_cbs_municipal_avg(cbs_cache, muni_label)
    if cbs_avg is None:
        cbs_avg = get_cbs_municipal_avg(cbs_cache, "Netherlands")

    neighborhood_factor = profile.get("neighborhood_factor", 1.0) if profile else 1.0
    e_factor = energy_factor(listing.get("energy_label"), pricing)
    a_factor = age_factor(listing.get("build_year"), pricing)

    market_value = int(
        cbs_avg * (area_m2 / reference_m2) * neighborhood_factor * e_factor * a_factor
    )

    base_overbid = float(pricing.get("base_overbid_pct", {}).get(cbs_key, 0.04))
    overbid_adj = profile.get("overbid_adjustment", 0.0) if profile else 0.0
    overbid_adj += collect_tag_adjustments(listing, profile, pricing)

    if listing.get("build_year") and listing["build_year"] < pricing.get("age_factors", {}).get("min_year", 2000):
        overbid_adj -= 0.005

    overbid_pct = max(0.005, min(0.12, base_overbid + overbid_adj))

    # Reduce overbid when asking already above market
    if asking > market_value * 1.08:
        overbid_pct = max(0.0, overbid_pct - 0.02)
    elif asking > market_value * 1.03:
        overbid_pct = max(0.005, overbid_pct * 0.6)

    competition = profile.get("competition_factor", 0.65) if profile else 0.65
    gap = market_value - asking

    pct_bid = int(asking * (1 + overbid_pct))

    if gap >= 0:
        competition_bid = int(asking + gap * competition)
        estimated_bid = max(competition_bid, pct_bid)
    else:
        # Asking above model value — at most a small premium
        estimated_bid = int(asking * (1 + max(0.0, overbid_pct)))

    estimated_bid = round(estimated_bid, -3)

    overbid_eur = estimated_bid - asking
    effective_overbid_pct = round(overbid_eur / asking, 4) if asking else 0.0

    confidence = "medium"
    if profile and cbs_avg:
        confidence = "medium-high"
    if not cbs_avg:
        confidence = "low"

    return {
        "method": "level1_cbs",
        "confidence": confidence,
        "market_value_eur": market_value,
        "price_estimated_bid": estimated_bid,
        "overbid_pct": effective_overbid_pct,
        "overbid_eur": overbid_eur,
        "factors": {
            "cbs_municipality": muni_label,
            "cbs_avg_eur": cbs_avg,
            "cbs_year": "2024",
            "neighborhood_profile": profile_name or listing.get("neighborhood_profile"),
            "neighborhood_factor": neighborhood_factor,
            "energy_factor": e_factor,
            "age_factor": a_factor,
            "base_overbid_pct": base_overbid,
            "overbid_adjustments": round(overbid_adj, 4),
            "competition_factor": competition,
            "implied_eur_per_m2": round(market_value / area_m2) if area_m2 else None,
            "asking_eur_per_m2": round(asking / area_m2) if area_m2 else None,
        },
        "data_sources": [
            cbs_cache.get("sources", {}).get("regional", "CBS 83625ENG"),
            "config/regional-pricing.json",
        ],
        "notes": _build_notes(listing, profile, market_value, asking, estimated_bid),
    }


def _build_notes(listing: dict, profile: dict | None, market_value: int, asking: int, bid: int) -> str:
    parts = []
    if profile and "social_housing_nearby" in profile.get("tags", []):
        parts.append("邻里有 social housing，竞价压力低于 Amsterdam 均价所暗示的水平。")
    if asking < market_value * 0.95:
        parts.append(f"CBS 模型公允价 €{market_value:,} 高于挂牌，但弱区环境压制溢价。")
    elif asking > market_value * 1.05:
        parts.append(f"挂牌已高于 CBS 公允价 €{market_value:,}，预估仅小幅溢价或平价成交。")
    parts.append(f"模型预估成交 €{bid:,}（较挂牌 {'+' if bid >= asking else ''}€{bid - asking:,}）。")
    return " ".join(parts)


def apply_estimate_to_listing(listing: dict, force: bool = False) -> dict:
    if listing.get("price_estimate") and not force and listing.get("price_estimated_bid"):
        return listing
    est = estimate_listing(listing)
    listing["price_estimate"] = est
    listing["price_estimated_bid"] = est["price_estimated_bid"]
    bid = est["price_estimated_bid"]
    buyout = (listing.get("erfpacht") or {}).get("buyout_cost_estimate") or 0
    kk = listing.get("buyer_costs_eur", 6000)
    listing["true_cost_eur"] = int(bid + buyout + kk)
    return listing


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Estimate bid price for a listing JSON file")
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    raw = json.loads(args.file.read_text(encoding="utf-8"))
    result = estimate_listing(raw)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
