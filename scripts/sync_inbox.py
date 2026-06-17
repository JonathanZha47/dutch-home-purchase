#!/usr/bin/env python3
"""Merge search shortlist into persistent inbox (data/inbox.json)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHORTLIST = ROOT / "data" / "search" / "shortlist.json"
INBOX = ROOT / "data" / "inbox.json"
ZONES_CFG = ROOT / "config" / "search-zones.json"


def zone_tier_map() -> dict[str, str]:
    if not ZONES_CFG.exists():
        return {}
    cfg = json.loads(ZONES_CFG.read_text(encoding="utf-8"))
    return {z["id"]: z.get("transport_tier", "B") for z in cfg.get("zones", [])}


def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]


def listing_id(item: dict) -> str:
    if item.get("id"):
        return str(item["id"])
    url = item.get("funda_url", "")
    m = re.search(r"/(\d{6,})", url)
    if m:
        return f"funda-{m.group(1)}"
    return slugify(item.get("address", "unknown"))


def load_json(path: Path, default: dict) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def main() -> None:
    shortlist = load_json(SHORTLIST, {"listings": []})
    inbox = load_json(INBOX, {"listings": []})

    by_id = {listing_id(x): x for x in inbox.get("listings", [])}

    tiers = zone_tier_map()
    next_by_id: dict[str, dict] = {}

    for raw in shortlist.get("listings", []):
        lid = listing_id(raw)
        merged = {**raw, "id": lid}
        merged.setdefault("pipeline_status", "discovered")
        merged.setdefault("source", "search")
        merged["last_seen_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        zid = raw.get("zone_id")
        if zid and zid in tiers:
            merged["transport_tier"] = tiers[zid]

        if merged.get("transport_tier") == "watchlist" or raw.get("zone_id") == "rotterdam_nesselande":
            merged["viewing_intent"] = "watchlist_only"
            if merged.get("pipeline_status") == "discovered":
                merged["pipeline_status"] = "watchlist"

        if lid in by_id:
            prev = by_id[lid]
            merged["pipeline_status"] = prev.get("pipeline_status", merged["pipeline_status"])
            merged["viewing_intent"] = prev.get("viewing_intent", merged.get("viewing_intent"))
            merged["first_seen_at"] = prev.get("first_seen_at", merged.get("first_seen_at"))
        else:
            merged["first_seen_at"] = merged["last_seen_at"]

        by_id[lid] = merged
        next_by_id[lid] = merged

    out = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "criteria": shortlist.get("criteria", {}),
        "listings": sorted(next_by_id.values(), key=lambda x: (x.get("rank") or 999, x.get("address", ""))),
    }
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    INBOX.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inbox synced: {len(out['listings'])} listings → {INBOX}")


if __name__ == "__main__":
    main()
