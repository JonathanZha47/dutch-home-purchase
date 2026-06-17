#!/usr/bin/env python3
"""Build Funda search URLs from buyer profile + search zones."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUYER_PROFILE = ROOT / "config" / "buyer-profile.yaml"
SEARCH_ZONES_JSON = ROOT / "config" / "search-zones.json"
OUTPUT_DIR = ROOT / "data" / "search"


def _load_buyer_profile() -> dict:
    text = BUYER_PROFILE.read_text(encoding="utf-8")

    def find_int(key: str, default: int) -> int:
        m = re.search(rf"{key}:\s*(\d+)", text)
        return int(m.group(1)) if m else default

    def find_range(key: str, default: list[int]) -> list[int]:
        m = re.search(rf"{key}:\s*\[(\d+),\s*(\d+)\]", text)
        return [int(m.group(1)), int(m.group(2))] if m else default

    return {
        "budget": {
            "max_total_kk": find_int("max_total_kk", 500000),
            "target_range": find_range("target_range", [400000, 450000]),
        },
        "hard_requirements": {
            "min_build_year": find_int("min_build_year", 2000),
            "min_energy_label": "B",
        },
    }


def _budget_from_profile(profile: dict) -> tuple[int, int]:
    budget = profile.get("budget", {})
    lo, hi = budget.get("target_range", [300000, 500000])
    max_kk = budget.get("max_total_kk", hi)
    return int(lo), int(min(hi, max_kk))


def _hard_filters(profile: dict, zones_cfg: dict) -> dict:
    hard = profile.get("hard_requirements", {})
    funda = zones_cfg.get("funda_filters", {})
    return {
        "build_year_min": hard.get("min_build_year", funda.get("build_year_min", 2000)),
        "energy_label_min": hard.get("min_energy_label", funda.get("energy_label_min", "B")),
        "price_min": funda.get("price_min", 300000),
        "price_max": _budget_from_profile(profile)[1],
    }


def build_funda_url(base_path: str, filters: dict) -> str:
    base = "https://www.funda.nl"
    path = base_path if base_path.startswith("/") else f"/{base_path}"
    if not path.endswith("/"):
        path += "/"
    params = [
        "selected_area=%5B%5D",
        f"price={filters['price_min']}-{filters['price_max']}",
        f"construction_year={filters['build_year_min']}-",
        "object_type=apartment",
    ]
    energy = filters.get("energy_label_min", "B")
    if energy:
        params.append(f"energy_label={energy}-")
    return base + path + "?" + "&".join(params)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Funda search URLs")
    parser.add_argument(
        "--tier",
        choices=["S", "A", "B", "top", "all"],
        default="top",
        help="top = S+A tiers (default); all includes watchlist",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown")
    args = parser.parse_args()

    profile = _load_buyer_profile()
    zones_cfg = json.loads(SEARCH_ZONES_JSON.read_text(encoding="utf-8"))
    filters = _hard_filters(profile, zones_cfg)
    price_lo, price_hi = _budget_from_profile(profile)

    allowed_tiers = {"S", "A", "B", "watchlist"}
    if args.tier == "top":
        allowed_tiers = {"S", "A"}
    elif args.tier != "all":
        allowed_tiers = {args.tier}

    results = []
    for zone in zones_cfg.get("zones", []):
        tier = zone.get("transport_tier", zone.get("priority", "B"))
        if args.tier != "all" and tier not in allowed_tiers:
            continue
        url = build_funda_url(zone["funda_path"], filters)
        results.append(
            {
                "id": zone["id"],
                "label": zone["label"],
                "transport_tier": tier,
                "postcodes": zone.get("postcodes", []),
                "funda_url": url,
                "zuid_commute_note": zone.get("zuid_commute_note"),
                "caution": zone.get("caution"),
                "notes": zone.get("notes"),
            }
        )

    payload = {
        "budget_eur": [price_lo, price_hi],
        "hard_filters": filters,
        "zones": results,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / "funda_search_urls.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"# Funda search plan (budget €{price_lo:,}–€{price_hi:,})\n")
        print(f"Hard filters: build ≥{filters['build_year_min']}, energy ≥{filters['energy_label_min']}\n")
        for z in results:
            print(f"## {z['label']} [tier {z['transport_tier']}]")
            if z.get("zuid_commute_note"):
                print(f"- {z['zuid_commute_note']}")
            if z.get("caution"):
                print(f"⚠️ {z['caution']}")
            print(f"- Postcodes: {', '.join(z['postcodes'])}")
            print(f"- {z['funda_url']}\n")
        print(f"Saved to {out_file}")


if __name__ == "__main__":
    main()
