#!/usr/bin/env python3
"""Re-run Level 1 price estimates for all listings in data/listings.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "listings.json"


def main() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from estimate_price import apply_estimate_to_listing

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    for listing in data.get("listings", []):
        apply_estimate_to_listing(listing, force=True)
        est = listing["price_estimate"]
        print(
            f"{listing.get('id')}: ask €{listing.get('price_asking'):,} → "
            f"bid €{est['price_estimated_bid']:,} "
            f"(market €{est['market_value_eur']:,}, overbid {est['overbid_pct']:.1%})"
        )

    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    from generate_dashboard import main as gen_main

    sys.argv = ["generate_dashboard.py"]
    gen_main()


if __name__ == "__main__":
    main()
