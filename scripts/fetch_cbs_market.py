#!/usr/bin/env python3
"""Fetch free CBS housing market data and cache locally."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = ROOT / "data" / "cbs" / "market_cache.json"

# CBS table 83625ENG — average purchase price by municipality/province (annual)
CBS_REGIONAL_TABLE = "83625ENG"
# CBS table 85773ENG — national monthly average + price index
CBS_NATIONAL_TABLE = "85773ENG"

REGION_KEYS = {
    "NL01  ": "Netherlands",
    "PV27  ": "Noord-Holland",
    "PV28  ": "Zuid-Holland",
    "GM0363": "Amsterdam",
    "GM0394": "Haarlemmermeer",
    "GM0479": "Zaanstad",
    "GM0513": "Gouda",
}


def odata_get(table: str, params: dict) -> dict:
    base = f"https://opendata.cbs.nl/ODataApi/OData/{table}/TypedDataSet"
    url = base + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def fetch_regional_annual() -> dict:
    out: dict[str, dict[str, int]] = {}
    for period in ["2023JJ00", "2024JJ00", "2025JJ00"]:
        for key, label in REGION_KEYS.items():
            filt = f"Regions eq '{key}' and Periods eq '{period}'"
            data = odata_get(CBS_REGIONAL_TABLE, {"$filter": filt})
            rows = data.get("value", [])
            if not rows:
                continue
            year = period[:4]
            out.setdefault(label, {})[year] = int(rows[0]["AveragePurchasePrice_1"])
    return out


def fetch_national_monthly(limit: int = 18) -> list[dict]:
    data = odata_get(CBS_NATIONAL_TABLE, {"$top": 5000})
    rows = data.get("value", [])
    recent = [r for r in rows if r["Periods"].startswith("2024") or r["Periods"].startswith("2025")]
    recent.sort(key=lambda r: r["Periods"], reverse=True)
    result = []
    for r in recent[:limit]:
        result.append(
            {
                "period": r["Periods"],
                "avg_price_eur": int(r["AveragePurchasePrice_7"]),
                "price_index_2020": float(r["PriceIndexSellingPrices_1"]),
            }
        )
    return result


def main() -> None:
    cache = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "regional": f"CBS OData {CBS_REGIONAL_TABLE} (municipal/provincial annual avg purchase price)",
            "national_monthly": f"CBS OData {CBS_NATIONAL_TABLE} (national monthly avg + price index)",
        },
        "regional_annual_avg_eur": fetch_regional_annual(),
        "national_monthly": fetch_national_monthly(),
    }
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CBS cache written to {CACHE_FILE}")


if __name__ == "__main__":
    main()
