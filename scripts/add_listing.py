#!/usr/bin/env python3
"""Add or update a listing in data/listings.json and regenerate the dashboard."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "listings.json"


def extract_funda_id(url: str) -> str:
    match = re.search(r"/detail/(?:koop|huur)?/?(\d+)", url)
    if match:
        return match.group(1)
    match = re.search(r"(\d{6,})", url)
    if match:
        return match.group(1)
    raise ValueError(f"Cannot extract Funda listing ID from URL: {url}")


def load_data() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"listings": []}


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compute_total(scores: dict) -> float | None:
    keys = ["quality", "size", "groceries", "tennis", "transport", "financial"]
    values = [scores.get(k) for k in keys]
    if any(v is None for v in values):
        return scores.get("total")
    return round(sum(float(v) for v in values), 1)


def normalize_listing(raw: dict) -> dict:
    listing = dict(raw)

    if listing.get("funda_url") and not listing.get("id"):
        listing["id"] = extract_funda_id(listing["funda_url"])

    # Level 1 price estimate (CBS + regional model) unless explicitly skipped
    if not listing.get("skip_price_estimate"):
        sys.path.insert(0, str(ROOT / "scripts"))
        from estimate_price import apply_estimate_to_listing

        apply_estimate_to_listing(listing, force=listing.get("force_price_estimate", False))

    scores = listing.setdefault("scores", {})
    total = compute_total(scores)
    if total is not None:
        scores["total"] = total

    # Auto-compute true cost if not provided (may already be set by price estimate)
    if listing.get("true_cost_eur") is None:
        bid = listing.get("price_estimated_bid") or listing.get("price_asking") or 0
        buyout = (listing.get("erfpacht") or {}).get("buyout_cost_estimate") or 0
        kk = listing.get("buyer_costs_eur", 6000)
        listing["true_cost_eur"] = int(bid + buyout + kk)

    if listing.get("monthly_carry_eur") is None:
        vve = listing.get("vve_monthly") or 0
        erf = (listing.get("erfpacht") or {}).get("monthly_after_term") or 0
        listing["monthly_carry_eur"] = int(vve + erf)

    listing.setdefault("status", "active")
    return listing


def upsert_listing(data: dict, listing: dict) -> None:
    listing = normalize_listing(listing)
    listings = data.setdefault("listings", [])
    for i, existing in enumerate(listings):
        if existing.get("id") == listing.get("id"):
            listings[i] = listing
            print(f"Updated listing {listing['id']}")
            return
    listings.append(listing)
    print(f"Added listing {listing['id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add or update a Funda listing")
    parser.add_argument("--file", type=Path, help="JSON file with listing object")
    parser.add_argument("--json", type=str, help="Inline JSON string")
    parser.add_argument("--no-dashboard", action="store_true", help="Skip dashboard regeneration")
    args = parser.parse_args()

    if not args.file and not args.json:
        parser.error("Provide --file or --json")

    if args.file:
        raw = json.loads(args.file.read_text(encoding="utf-8"))
    else:
        raw = json.loads(args.json)

    data = load_data()
    upsert_listing(data, raw)
    save_data(data)

    if not args.no_dashboard:
        from generate_dashboard import main as gen_main

        sys.argv = ["generate_dashboard.py"]
        gen_main()


if __name__ == "__main__":
    main()
