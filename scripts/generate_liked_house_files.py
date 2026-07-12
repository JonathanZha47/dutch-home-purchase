#!/usr/bin/env python3
"""Create inbox.md and liked-house markdown files from curated Funda URLs."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
INBOX_FILE = ROOT / "inbox.md"
LIKED_DIR = ROOT / "liked-house"
LISTINGS_JSON = ROOT / "data" / "listings.json"

REGIONS = {
    "almere": [
        "https://www.funda.nl/detail/koop/almere/huis-zeistpad-42/44453969/",
        "https://www.funda.nl/detail/koop/almere/huis-prokofjevstraat-88/80866678/",
        "https://www.funda.nl/detail/koop/almere/appartement-louis-davidsstraat-250/44458501/",
        "https://www.funda.nl/detail/koop/almere/huis-rachmaninovstraat-21/80875756/",
        "https://www.funda.nl/detail/koop/almere/appartement-keizerstraat-28/44407386/",
    ],
    "weesp": [
        "https://www.funda.nl/detail/koop/weesp/appartement-heemraadweg-101/44404623/",
        "https://www.funda.nl/detail/koop/weesp/appartement-fort-heemstedestraat-83/44496014/",
    ],
    "zaandam": [
        "https://www.funda.nl/detail/koop/zaandam/appartement-teakhout-40/89776878/",
        "https://www.funda.nl/detail/koop/zaandam/appartement-teakhout-29/44492615/",
        "https://www.funda.nl/detail/koop/zaandam/appartement-teakhout-32/44415290/",
        "https://www.funda.nl/detail/koop/zaandam/huis-vurehout-44/80857078/",
    ],
    "nieuw-west": [
        "https://www.funda.nl/detail/koop/amsterdam/appartement-dijkgraafplein-14/80818281/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-dijkgraafplein-311/80860141/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-dijkgraafplein-163/43317021/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-ladogameerhof-253/44472010/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-ladogameerhof-277/80870826/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-pieter-calandlaan-720/80869364/",
    ],
    "amstelveen": [
        "https://www.funda.nl/detail/koop/amstelveen/appartement-duivelandselaan-35/44412372/",
        "https://www.funda.nl/detail/koop/amstelveen/appartement-schouwenselaan-75/44493093/",
        "https://www.funda.nl/detail/koop/amstelveen/appartement-tholenseweg-22/44483838/",
        "https://www.funda.nl/detail/koop/amstelveen/appartement-bos-en-vaartlaan-45/44426958/",
        "https://www.funda.nl/detail/koop/amstelveen/appartement-rembrandtweg-559/44419300/",
        "https://www.funda.nl/detail/koop/amstelveen/appartement-zonnesteinhof-24/44464587/",
    ],
    "bijlmer": [
        "https://www.funda.nl/detail/koop/amsterdam/appartement-boeninlaan-389/80864744/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-barbusselaan-175/80821531/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-fleerde-705/89704975/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-haardstee-29/80838370/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-bijlmerdreef-1053/89602391/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-leksmondhof-32/80856190/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-leksmondhof-313/80862661/",
        "https://www.funda.nl/detail/koop/amsterdam/appartement-leksmondhof-217/44419986/",
    ],
}

VERIFIED_OVERRIDES: dict[str, dict[str, Any]] = {
    "44453969": {
        "address": "Zeistpad 42",
        "city": "Almere",
        "postcode": "1324 ND",
        "price_asking": 375000,
        "living_area_m2": 114,
        "bedrooms": 5,
        "build_year": 1981,
        "energy_label": "A",
        "erfpacht": {"type": "eigen_grond", "summary": "Volle eigendom / full ownership, per Funda kadastrale gegevens."},
        "pros": [
            "114 m2 and 5 bedrooms: unusually large space for the budget.",
            "Energy label A with solar panels, good running-cost profile for an older house.",
            "Full ownership, so no erfpacht carry risk if Funda data is confirmed in the deed.",
        ],
        "cons": [
            "1981 build year violates the default 2000+ preference and needs explicit exception.",
            "Listed as a kluswoning, so renovation budget and execution risk are central.",
            "Ymere conditions include self-occupancy / anti-speculation style restrictions; rental flexibility is weak.",
        ],
        "vve_analysis": {"monthly_fee": None, "red_flags": [], "notes": "House, no apartment VvE expected; verify any homeowners' association or municipal obligations."},
        "verdict": "谨慎看房：空间很好，但房龄和装修风险大",
    },
    "44458501": {
        "address": "Louis Davidsstraat 250",
        "city": "Almere",
        "postcode": "1311 LZ",
        "price_asking": 350000,
        "living_area_m2": 96,
        "bedrooms": 2,
        "build_year": 1998,
        "energy_label": "A",
        "vve_monthly": 251,
        "erfpacht": {"type": "eigen_grond", "summary": "Volle eigendom / full ownership, per Funda kadastrale gegevens."},
        "pros": [
            "96 m2 maisonette with own entrance and garden, very strong usable space.",
            "Near Almere Muziekwijk facilities and station, good daily convenience.",
            "Funda VvE checklist reports reserve fund and maintenance plan present.",
        ],
        "cons": [
            "1998 build year is just below the 2000+ preference.",
            "Complex has 35+ and no resident children rule, which narrows resale/rental audience.",
            "VvE at EUR 251/month is meaningful and deserves MJOP/reserve review.",
        ],
        "vve_analysis": {"monthly_fee": 251, "red_flags": ["age_restriction", "verify_mjop"], "notes": "Active VvE per Funda; review annual report, MJOP and the 35+ household rule before bidding."},
        "verdict": "值得研究：面积强，但居住规则和 VvE 要核实",
    },
    "80875756": {
        "address": "Rachmaninovstraat 21",
        "city": "Almere",
        "postcode": "1323 NA",
        "price_asking": 395000,
        "living_area_m2": 88,
        "bedrooms": 3,
        "build_year": 1989,
        "energy_label": "A",
        "erfpacht": {"type": "eigen_grond", "summary": "Volle eigendom / full ownership, per Funda kadastrale gegevens."},
        "pros": [
            "88 m2 family house with 3 bedrooms and private garden.",
            "Muziekwijk station and shops are close, making Almere commute more practical.",
            "Energy label A and renovated kitchen/bathroom reduce immediate work.",
        ],
        "cons": [
            "1989 build year is below the 2000+ preference.",
            "Asking price is close to the target upper range for an older Almere house.",
            "No VvE, but building envelope and roof maintenance must be checked privately.",
        ],
        "vve_analysis": {"monthly_fee": None, "red_flags": [], "notes": "House; no VvE expected. Replace VvE review with bouwkundige keuring focus."},
        "verdict": "备选：实用但房龄折扣要足够",
    },
    "44407386": {
        "address": "Keizerstraat 28",
        "city": "Almere",
        "postcode": "1312 AV",
        "price_asking": 325000,
        "living_area_m2": 83,
        "bedrooms": 2,
        "build_year": 1987,
        "energy_label": "A",
        "vve_monthly": 177,
        "erfpacht": {"type": "verify", "summary": "Funda page excerpt did not expose kadastrale ownership; verify deed and apartment rights."},
        "pros": [
            "83 m2 ground-floor apartment with south-facing garden near Almere centrum/station.",
            "Low asking price leaves room for renovation and due diligence.",
            "Energy label A is good for an older building.",
        ],
        "cons": [
            "1987 build year violates the 2000+ preference.",
            "Former housing association sale with self-occupancy, anti-speculation, old-age/asbestos clauses.",
            "Funda VvE checklist fields show 'Nee' even though text mentions about EUR 177/month; this contradiction must be resolved.",
        ],
        "vve_analysis": {"monthly_fee": 177, "red_flags": ["vve_checklist_contradiction", "former_social_housing", "old_age_clause"], "notes": "Ask for splitsingsakte, current VvE status, reserve fund, MJOP and exact monthly contribution."},
        "verdict": "谨慎：便宜但法律/VvE 条款复杂",
    },
}

REGION_PROFILES = {
    "almere": {"transport": 3.5, "pros": "Almere gives the best m2 per euro and is acceptable as a B-tier train town.", "cons": "Commute and older stock must be weighed against the space discount."},
    "weesp": {"transport": 4.0, "pros": "Weesp has a strong train connection and village-style daily life near Amsterdam.", "cons": "Older VvE buildings can hide maintenance and energy-label risk."},
    "zaandam": {"transport": 4.0, "pros": "Zaandam can be fast to Amsterdam and often offers newer apartments below Amsterdam prices.", "cons": "Erfpacht, separate garage rights, and VvE reserve quality need careful checking."},
    "nieuw-west": {"transport": 4.0, "pros": "Nieuw-West keeps Amsterdam access and local amenities within the search area.", "cons": "Many buildings have erfpacht and older VvE/energy issues."},
    "amstelveen": {"transport": 4.5, "pros": "Amstelveen is strong for Zuid/VU access, liquidity, and daily amenities.", "cons": "Prices are tighter and apartment rights/erfpacht must be checked closely."},
    "bijlmer": {"transport": 5.0, "pros": "Bijlmer/Zuidoost is the strongest commute tier with metro access to Zuid.", "cons": "Older blocks require VvE, safety, energy and maintenance diligence."},
}


def extract_id(url: str) -> str:
    match = re.search(r"/(\d{6,})/?$", url)
    if not match:
        raise ValueError(f"Cannot extract listing id from {url}")
    return match.group(1)


def slug_from_url(url: str) -> str:
    match = re.search(r"/(?:huis|appartement)-([^/]+)/\d+/?$", url)
    if not match:
        raise ValueError(f"Cannot extract slug from {url}")
    return match.group(1)


def title_from_slug(slug: str) -> str:
    words = slug.replace("-", " ").split()
    if words and words[-1].isdigit():
        return " ".join(words[:-1]).title() + f" {words[-1]}"
    return slug.replace("-", " ").title()


def object_type_from_url(url: str) -> str:
    if "/huis-" in url:
        return "house"
    if "/appartement-" in url:
        return "apartment"
    return "verify"


def city_from_url(url: str) -> str:
    match = re.search(r"/koop/([^/]+)/", url)
    if not match:
        return ""
    city = match.group(1).replace("-", " ")
    return city.title()


def load_existing_listings() -> dict[str, dict[str, Any]]:
    if not LISTINGS_JSON.exists():
        return {}
    data = json.loads(LISTINGS_JSON.read_text(encoding="utf-8"))
    return {str(item.get("id")): item for item in data.get("listings", []) if item.get("id")}


def base_listing(region: str, url: str, existing: dict[str, dict[str, Any]]) -> dict[str, Any]:
    listing_id = extract_id(url)
    slug = slug_from_url(url)
    profile = REGION_PROFILES[region]
    listing: dict[str, Any] = {
        "id": listing_id,
        "funda_url": url,
        "address": title_from_slug(slug),
        "city": city_from_url(url),
        "region": region,
        "object_type": object_type_from_url(url),
        "postcode": "",
        "price_asking": None,
        "price_estimated_bid": None,
        "living_area_m2": None,
        "bedrooms": None,
        "build_year": None,
        "energy_label": None,
        "vve_monthly": None,
        "erfpacht": {"type": "verify", "summary": "产权/地租待从 Funda、kadastraal bericht 和 koopakte 核实。"},
        "buyer_costs_eur": 6000,
        "true_cost_eur": None,
        "monthly_carry_eur": None,
        "features": [],
        "pricing_tags": [],
        "scores": {
            "quality": None,
            "size": None,
            "groceries": None,
            "tennis": None,
            "transport": profile["transport"],
            "financial": None,
            "total": None,
        },
        "pros": [profile["pros"]],
        "cons": [profile["cons"], "Key financial fields are not fully verified yet."],
        "vve_analysis": {
            "monthly_fee": None,
            "red_flags": ["verify_vve", "verify_ownership"],
            "notes": "待核实 VvE 月供、reservefonds、MJOP、opstalverzekering、splitsingsakte 和 erfpacht/volle eigendom。",
        },
        "verdict": "待补充分析",
        "status": "liked",
        "analyzed_at": date.today().isoformat(),
        "source_markdown": f"liked-house/{region}-{slug}.md",
    }

    if listing_id in existing:
        merged = dict(existing[listing_id])
        merged.update({"region": region, "source_markdown": listing["source_markdown"]})
        listing.update(merged)

    if listing_id in VERIFIED_OVERRIDES:
        listing.update(VERIFIED_OVERRIDES[listing_id])
        listing["id"] = listing_id
        listing["funda_url"] = url
        listing["region"] = region
        listing["object_type"] = object_type_from_url(url)
        listing["source_markdown"] = f"liked-house/{region}-{slug}.md"
        listing.setdefault("scores", {})["transport"] = profile["transport"]

    return listing


def markdown_body(listing: dict[str, Any]) -> str:
    pros = "\n".join(f"- {item}" for item in listing.get("pros", []))
    cons = "\n".join(f"- {item}" for item in listing.get("cons", []))
    red_flags = "\n".join(f"- `{item}`" for item in (listing.get("vve_analysis") or {}).get("red_flags", []))
    ownership = (listing.get("erfpacht") or {}).get("summary", "")
    vve_notes = (listing.get("vve_analysis") or {}).get("notes", "")
    return f"""# {listing.get('address')}, {listing.get('city')}

## Snapshot

- Funda: {listing.get('funda_url')}
- Region: {listing.get('region')}
- Object type: {listing.get('object_type')}
- Asking price: {listing.get('price_asking') or 'verify'}
- Living area: {listing.get('living_area_m2') or 'verify'} m2
- Build year: {listing.get('build_year') or 'verify'}
- Energy label: {listing.get('energy_label') or 'verify'}
- VvE/month: {listing.get('vve_monthly') or 'verify'}

## 产权与财务

- Ownership / erfpacht: {ownership}
- True cost and estimated bid should be recomputed after price, erfpacht and VvE are verified.

## VvE / Maintenance

{vve_notes}

Red flags:
{red_flags or '- None recorded yet.'}

## 优点

{pros or '- 待补充。'}

## 缺点

{cons or '- 待补充。'}

## 出价前必须核实

- Funda current status and whether the listing is still available.
- Exact ownership: volle eigendom vs erfpacht, canon, paid-until date, buyout option.
- For apartments: VvE fee, reserve fund, MJOP, meeting minutes and insurance.
- For houses: bouwkundige keuring focus, roof/facade/installations and any municipal restrictions.
- Any self-occupancy, anti-speculation, old-age, asbestos or non-occupancy clauses.

## 结论

{listing.get('verdict')}
"""


def write_inbox() -> None:
    lines = ["# Inbox", "", "New liked Funda links are recorded here. Keep grouped by region.", ""]
    for region, urls in REGIONS.items():
        lines.append(f"## {region}")
        lines.append("")
        for url in urls:
            lines.append(f"- [ ] {url}")
        lines.append("")
    INBOX_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_liked_files() -> None:
    LIKED_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_existing_listings()
    for region, urls in REGIONS.items():
        for url in urls:
            slug = slug_from_url(url)
            path = LIKED_DIR / f"{region}-{slug}.md"
            listing = base_listing(region, url, existing)
            frontmatter = yaml.safe_dump(listing, allow_unicode=True, sort_keys=False).strip()
            path.write_text(f"---\n{frontmatter}\n---\n\n{markdown_body(listing)}", encoding="utf-8")


def main() -> None:
    write_inbox()
    write_liked_files()
    print(f"Wrote {INBOX_FILE}")
    print(f"Wrote liked-house markdown files to {LIKED_DIR}")


if __name__ == "__main__":
    main()
