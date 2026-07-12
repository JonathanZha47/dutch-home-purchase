#!/usr/bin/env python3
"""Generate hub dashboard/index.html from liked-house/ and viewing/ data."""

from __future__ import annotations
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
LIKED_DIR = ROOT / "liked-house"
VIEWING_DIR = ROOT / "viewing"
OUTPUT = ROOT / "dashboard" / "index.html"

# ── Viewing folder → liked-house slug ────────────────────────────────────
FOLDER_TO_SLUG = {
    "bos-en-vaartlaan45": "amstelveen-bos-en-vaartlaan-45",
    "bijlmer": "bijlmer-boeninlaan-389",
    "hardstee29": "bijlmer-haardstee-29",
    "Leksmondhof 313": "bijlmer-leksmondhof-313",
    "weesp": "weesp-heemraadweg-101",
    "zaandam": "zaandam-teakhout-29",
}

# ── Viewed-only properties (not in liked-house) ───────────────────────────
EXTRA_VIEWED = [
    {
        "id": "concourslaan-86-hoofddorp",
        "address": "Concourslaan 86", "city": "Hoofddorp", "region": "hoofddorp",
        "funda_url": None, "price": None, "area": 80, "energy": "B", "vve": 269,
        "score": None,
        "verdict": "中高风险：三层 VvE 财务混乱、漏水风险，需价格折价",
        "tags": ["viewed", "vve_reviewed", "bidding_done"],
        "vve_risk": "medium_high",
        "vve_flags": ["split_vve_entities", "planned_major_work", "measurement_mismatch", "governance_watch"],
        "viewing_date": "2026-07-08",
        "viewing_folder": "concorselaan-hoofddorp centurm",
        "docs_summary_rel": "viewing/documents-summary/concorselaan-86-hoofddorp.md",
        "bidding_rel": "viewing/concorselaan-hoofddorp centurm/bidding-price/bidding-strategy.md",
    },
    {
        "id": "hoofdweg-854v-hoofddorp",
        "address": "Hoofdweg 854V", "city": "Hoofddorp", "region": "hoofddorp",
        "funda_url": None, "price": None, "area": 51, "energy": "A", "vve": 147,
        "score": None,
        "verdict": "中风险：面积偏小，潮湿待核实，2030 年 MJOP 支出集中",
        "tags": ["viewed", "vve_reviewed"],
        "vve_risk": "medium",
        "vve_flags": ["moisture_history", "planned_major_work"],
        "viewing_date": "2026-07-04",
        "viewing_folder": "Hoofdweg 854V Hoofddorp",
        "docs_summary_rel": "viewing/documents-summary/hoofdweg-854v-hoofddorp.md",
        "bidding_rel": None,
    },
    {
        "id": "anna-blamansingel-19-amsterdam",
        "address": "Anna Blamansingel 19", "city": "Amsterdam", "region": "bijlmer",
        "funda_url": None, "price": 325000, "area": 49, "energy": "A", "vve": 171,
        "score": None,
        "verdict": "中风险：含车位但面积小，缺 VvE 核心文件，出租状态需确认",
        "tags": ["viewed", "vve_reviewed", "bidding_done"],
        "vve_risk": "medium",
        "vve_flags": ["missing_vve_core_docs", "rental_status_verify", "moisture_history"],
        "viewing_date": "2026-07-08",
        "viewing_folder": "venspolder",
        "docs_summary_rel": "viewing/documents-summary/venspolder-anna-blamansingel-19.md",
        "bidding_rel": "viewing/venspolder/bidding-price/bidding-strategy.md",
    },
    {
        "id": "havikskruid-145-diemen",
        "address": "Havikskruid 145", "city": "Diemen", "region": "diemen",
        "funda_url": None, "price": None, "area": None, "energy": None, "vve": None,
        "score": None,
        "verdict": "待分析",
        "tags": ["viewed"],
        "vve_risk": "unknown",
        "vve_flags": [],
        "viewing_date": None,
        "viewing_folder": "harvisk145-diemen",
        "docs_summary_rel": None,
        "bidding_rel": None,
    },
]

# ── Community pages ───────────────────────────────────────────────────────
COMMUNITY_PAGES = [
    {"name": "Almere",      "file": "community/almere.html",     "tier": "B", "desc": "面积最大，B 级通勤，预算效率高；出租有限制"},
    {"name": "Amstelveen",  "file": "community/amstelveen.html", "tier": "S", "desc": "近 Zuid/VU，生活配套强；预算紧，面积小"},
    {"name": "Bijlmer",     "file": "community/bijlmer.html",    "tier": "S", "desc": "S 级通勤直达 Zuid；需按楼栋 VvE 精筛"},
    {"name": "Gaasperplas", "file": "community/gaasperplas.html","tier": "S", "desc": "湖区绿地，重点看面积和车位"},
    {"name": "Hoofddorp",   "file": "community/hoofddorp.html",  "tier": "A", "desc": "省心通勤型，Schiphol 方向基准"},
    {"name": "Nieuw-West",  "file": "community/nieuw-west.html", "tier": "S", "desc": "阿姆位置属性；需按 buurt 精筛"},
    {"name": "Weesp",       "file": "community/weesp.html",      "tier": "A", "desc": "小城稳定，火车强，供应少"},
    {"name": "Zaandam",     "file": "community/zaandam.html",    "tier": "A", "desc": "到 AMS CS 强；注意 erfpacht 和多 VvE"},
]

# ── VvE risk info for liked-house properties ──────────────────────────────
# keyed by liked-house slug
VVE_RISK_MAP = {
    "amstelveen-bos-en-vaartlaan-45": "medium_high",
    "bijlmer-boeninlaan-389": "high",
    "bijlmer-haardstee-29": "high",
    "weesp-heemraadweg-101": "high",
    "zaandam-teakhout-29": "high",
}
VVE_FLAGS_MAP = {
    "amstelveen-bos-en-vaartlaan-45": ["energy_label_below_B", "reserve_subfund_negative", "planned_major_work", "blokverwarming_cost_risk", "moisture_history"],
    "bijlmer-boeninlaan-389": ["planned_major_work", "future_reserve_gap", "moisture_history"],
    "bijlmer-haardstee-29": ["future_reserve_gap", "planned_major_work"],
    "weesp-heemraadweg-101": ["energy_label_below_B", "future_reserve_gap", "planned_major_work"],
    "zaandam-teakhout-29": ["erfpacht_trap", "split_vve_entities", "planned_major_work", "future_reserve_gap"],
}
DOCS_SUMMARY_MAP = {
    "amstelveen-bos-en-vaartlaan-45": "viewing/documents-summary/bos-en-vaartlaan-45-amstelveen.md",
    "bijlmer-boeninlaan-389": "viewing/documents-summary/bijlmer-boeninlaan-389.md",
    "bijlmer-haardstee-29": "viewing/documents-summary/hardstee29.md",
    "weesp-heemraadweg-101": "viewing/documents-summary/weesp-heemraadweg-101.md",
    "zaandam-teakhout-29": "viewing/documents-summary/zaandam-teakhout-29.md",
}
BIDDING_MAP = {
    "amstelveen-bos-en-vaartlaan-45": "viewing/bos-en-vaartlaan45/bidding-price/bidding-strategy.md",
}
VIEWING_DATE_MAP = {
    "amstelveen-bos-en-vaartlaan-45": "2026-07-09",
    "bijlmer-boeninlaan-389": "2026-07-04",
    "bijlmer-haardstee-29": "2026-07-04",
    "bijlmer-leksmondhof-313": None,
    "weesp-heemraadweg-101": "2026-07-04",
    "zaandam-teakhout-29": "2026-07-04",
}
VIEWING_FOLDER_MAP = {
    "amstelveen-bos-en-vaartlaan-45": "bos-en-vaartlaan45",
    "bijlmer-boeninlaan-389": "bijlmer",
    "bijlmer-haardstee-29": "hardstee29",
    "bijlmer-leksmondhof-313": "Leksmondhof 313",
    "weesp-heemraadweg-101": "weesp",
    "zaandam-teakhout-29": "zaandam",
}


# ── Data loading ──────────────────────────────────────────────────────────

def load_liked_houses() -> list[dict]:
    houses = []
    for md_file in sorted(LIKED_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        try:
            end = text.index("---", 3)
        except ValueError:
            continue
        fm = yaml.safe_load(text[3:end]) or {}
        fm["_slug"] = md_file.stem
        houses.append(fm)
    return houses


def normalize_liked(fm: dict) -> dict:
    slug = fm["_slug"]
    scores = fm.get("scores") or {}
    vve_analysis = fm.get("vve_analysis") or {}
    viewing_docs = fm.get("viewing_documents") or {}

    is_viewed = slug in FOLDER_TO_SLUG.values() or bool(fm.get("viewing_completed"))
    is_vve_reviewed = slug in DOCS_SUMMARY_MAP
    is_bidding = slug in BIDDING_MAP

    tags = ["liked"]
    if is_viewed:
        tags.append("viewed")
    if is_vve_reviewed:
        tags.append("vve_reviewed")
    if is_bidding:
        tags.append("bidding_done")

    vve_risk = (
        viewing_docs.get("overall_risk_level")
        or vve_analysis.get("risk_level")
        or VVE_RISK_MAP.get(slug)
        or "unknown"
    )

    return {
        "id": slug,
        "address": fm.get("address", ""),
        "city": fm.get("city", ""),
        "region": fm.get("region", ""),
        "funda_url": fm.get("funda_url"),
        "price": fm.get("price_asking"),
        "area": fm.get("living_area_m2"),
        "energy": fm.get("energy_label"),
        "vve": fm.get("vve_monthly"),
        "score": scores.get("total"),
        "verdict": fm.get("verdict", ""),
        "tags": tags,
        "vve_risk": vve_risk,
        "vve_flags": VVE_FLAGS_MAP.get(slug) or vve_analysis.get("red_flags") or [],
        "viewing_date": fm.get("viewing_date") or VIEWING_DATE_MAP.get(slug),
        "viewing_folder": fm.get("viewing_folder") or VIEWING_FOLDER_MAP.get(slug),
        "docs_summary_rel": DOCS_SUMMARY_MAP.get(slug),
        "bidding_rel": BIDDING_MAP.get(slug),
    }


def build_all_properties() -> list[dict]:
    liked_raw = load_liked_houses()
    liked = [normalize_liked(fm) for fm in liked_raw]
    # Sort liked: viewed first, then by score desc
    liked.sort(key=lambda x: (
        0 if "viewed" in x["tags"] else 1,
        -(x["score"] or 0),
    ))
    return liked + EXTRA_VIEWED


# ── HTML helpers ──────────────────────────────────────────────────────────

def fmt_price(v) -> str:
    if v is None:
        return "—"
    return f"€{v:,}".replace(",", ".")

def fmt_area(v) -> str:
    if v is None:
        return "—"
    return f"{v} m²"

def fmt_score(v) -> str:
    if v is None:
        return "—"
    return f"{v:.1f}"

def energy_badge(e) -> str:
    if not e:
        return "<span class='badge badge-gray'>—</span>"
    colors = {"A++": "badge-green", "A+": "badge-green", "A": "badge-green",
              "B": "badge-blue", "C": "badge-amber", "D": "badge-red",
              "E": "badge-red", "F": "badge-red", "G": "badge-red"}
    cls = colors.get(e, "badge-gray")
    return f"<span class='badge {cls}'>{e}</span>"

def risk_badge(r) -> str:
    labels = {
        "high": ("高风险", "badge-red"),
        "medium_high": ("中高", "badge-amber"),
        "medium": ("中", "badge-blue"),
        "low": ("低", "badge-green"),
        "unknown": ("待审", "badge-gray"),
    }
    label, cls = labels.get(r, ("?", "badge-gray"))
    return f"<span class='badge {cls}'>{label}</span>"

def tag_pill(tag: str) -> str:
    labels = {
        "liked": ("偏好", "pill-gray"),
        "viewed": ("已看", "pill-blue"),
        "vve_reviewed": ("VvE✓", "pill-amber"),
        "bidding_done": ("竞价✓", "pill-green"),
    }
    label, cls = labels.get(tag, (tag, "pill-gray"))
    return f"<span class='pill {cls}'>{label}</span>"

def flag_chip(f: str) -> str:
    return f"<span class='flag'>{f}</span>"

def link_btn(href: str, label: str) -> str:
    return f"<a href='{href}' target='_blank' class='btn-link'>{label}</a>"

def score_class(v) -> str:
    if v is None:
        return ""
    if v >= 22:
        return "score-high"
    if v >= 18:
        return "score-mid"
    return "score-low"


# ── Tab content generators ────────────────────────────────────────────────

def render_overview(props: list[dict]) -> str:
    n_liked = len([p for p in props if "liked" in p["tags"]])
    n_viewed = len([p for p in props if "viewed" in p["tags"]])
    n_vve = len([p for p in props if "vve_reviewed" in p["tags"]])
    n_bid = len([p for p in props if "bidding_done" in p["tags"]])

    recent_viewed = sorted(
        [p for p in props if "viewed" in p["tags"] and p.get("viewing_date")],
        key=lambda x: x["viewing_date"],
        reverse=True,
    )[:5]

    recent_rows = ""
    for p in recent_viewed:
        tags_html = "".join(tag_pill(t) for t in p["tags"] if t != "liked")
        recent_rows += f"""
        <tr>
          <td><strong>{p['address']}</strong></td>
          <td>{p['city']}</td>
          <td>{p.get('viewing_date') or '—'}</td>
          <td>{risk_badge(p['vve_risk'])}</td>
          <td>{tags_html}</td>
        </tr>"""

    return f"""
    <div class="stat-grid">
      <div class="stat-card"><span class="stat-num">{n_liked}</span><span class="stat-label">偏好房源</span></div>
      <div class="stat-card"><span class="stat-num">{n_viewed}</span><span class="stat-label">已看</span></div>
      <div class="stat-card"><span class="stat-num">{n_vve}</span><span class="stat-label">VvE 已审查</span></div>
      <div class="stat-card"><span class="stat-num">{n_bid}</span><span class="stat-label">已出价分析</span></div>
    </div>
    <h3 class="section-title">最近看房记录</h3>
    <div class="table-wrap">
    <table class="data-table">
      <thead><tr><th>地址</th><th>城市</th><th>看房日期</th><th>VvE 风险</th><th>标签</th></tr></thead>
      <tbody>{recent_rows}</tbody>
    </table>
    </div>
    <div class="area-link-row">
      <a href="amsterdam-region-buying-2026.html" class="area-main-link">📋 阿姆周边买房综合看板</a>
    </div>"""


def render_liked(props: list[dict]) -> str:
    liked = [p for p in props if "liked" in p["tags"]]
    rows = ""
    for p in liked:
        funda = link_btn(p["funda_url"], "Funda") if p.get("funda_url") else ""
        tags_html = "".join(tag_pill(t) for t in p["tags"] if t != "liked")
        region_badge = f"<span class='region-tag region-{p['region']}'>{p['region']}</span>"
        sc = fmt_score(p["score"])
        sc_cls = score_class(p["score"])
        rows += f"""
        <tr>
          <td><strong>{p['address']}</strong>{funda}</td>
          <td>{region_badge}</td>
          <td>{fmt_area(p['area'])}</td>
          <td>{fmt_price(p['price'])}</td>
          <td>{energy_badge(p['energy'])}</td>
          <td>{f"€{int(p['vve'])}" if p['vve'] else '—'}</td>
          <td class="{sc_cls}">{sc}</td>
          <td>{tags_html}</td>
        </tr>"""

    return f"""
    <p class="tab-intro">{len(liked)} 套偏好房源，按看房状态和评分排序。</p>
    <div class="table-wrap">
    <table class="data-table liked-table">
      <thead>
        <tr>
          <th>地址</th><th>区域</th><th>面积</th><th>挂牌价</th>
          <th>能效</th><th>VvE/月</th><th>总分/30</th><th>标签</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    </div>"""


def render_viewed(props: list[dict]) -> str:
    viewed = [p for p in props if "viewed" in p["tags"]]
    viewed.sort(key=lambda x: x.get("viewing_date") or "", reverse=True)
    rows = ""
    for p in viewed:
        funda = link_btn(p["funda_url"], "Funda") if p.get("funda_url") else ""
        docs = link_btn(p["docs_summary_rel"], "VvE文件") if p.get("docs_summary_rel") else ""
        bid = link_btn(p["bidding_rel"], "竞价策略") if p.get("bidding_rel") else ""
        rows += f"""
        <tr>
          <td><strong>{p['address']}</strong>{funda}</td>
          <td>{p['city']}</td>
          <td>{fmt_area(p['area'])}</td>
          <td>{energy_badge(p['energy'])}</td>
          <td>{f"€{int(p['vve'])}/月" if p['vve'] else '—'}</td>
          <td>{risk_badge(p['vve_risk'])}</td>
          <td>{p.get('viewing_date') or '—'}</td>
          <td>{docs} {bid}</td>
        </tr>"""

    return f"""
    <p class="tab-intro">{len(viewed)} 套已实地看房记录。</p>
    <div class="table-wrap">
    <table class="data-table">
      <thead>
        <tr>
          <th>地址</th><th>城市</th><th>面积</th><th>能效</th>
          <th>VvE/月</th><th>VvE 风险</th><th>看房日期</th><th>文件</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    </div>"""


def render_vve(props: list[dict]) -> str:
    reviewed = [p for p in props if "vve_reviewed" in p["tags"]]
    risk_order = {"high": 0, "medium_high": 1, "medium": 2, "low": 3, "unknown": 4}
    reviewed.sort(key=lambda x: risk_order.get(x["vve_risk"], 4))

    cards = ""
    for p in reviewed:
        flags_html = "".join(flag_chip(f) for f in (p.get("vve_flags") or []))
        doc_link = link_btn(p["docs_summary_rel"], "完整审查报告") if p.get("docs_summary_rel") else ""
        cards += f"""
        <div class="vve-card">
          <div class="vve-card-header">
            <div>
              <strong class="vve-addr">{p['address']}</strong>
              <span class="vve-city">{p['city']}</span>
            </div>
            {risk_badge(p['vve_risk'])}
          </div>
          <div class="vve-verdict">{p['verdict']}</div>
          <div class="flags-row">{flags_html}</div>
          <div class="vve-links">{doc_link}</div>
        </div>"""

    return f"""
    <p class="tab-intro">{len(reviewed)} 套已完成 VvE 文件审查，按风险高低排序。</p>
    <div class="vve-grid">{cards}</div>"""


def render_bidding(props: list[dict]) -> str:
    bid = [p for p in props if "bidding_done" in p["tags"]]
    bid.sort(key=lambda x: x.get("viewing_date") or "", reverse=True)

    cards = ""
    for p in bid:
        bid_link = link_btn(p["bidding_rel"], "竞价策略文件") if p.get("bidding_rel") else ""
        price_str = fmt_price(p["price"])
        cards += f"""
        <div class="bid-card">
          <div class="bid-card-header">
            <h3>{p['address']}<span class="bid-city">· {p['city']}</span></h3>
            {risk_badge(p['vve_risk'])}
          </div>
          <div class="bid-stats">
            <span>挂牌价：{price_str}</span>
            <span>能效：{energy_badge(p['energy'])}</span>
            <span>面积：{fmt_area(p['area'])}</span>
          </div>
          <div class="bid-verdict">{p['verdict']}</div>
          <div class="bid-links">{bid_link}</div>
        </div>"""

    return f"""
    <p class="tab-intro">{len(bid)} 套已完成竞价分析。</p>
    <div class="bid-grid">{cards}</div>"""


def render_area() -> str:
    cards = ""
    for c in COMMUNITY_PAGES:
        tier_cls = {"S": "tier-s", "A": "tier-a", "B": "tier-b"}.get(c["tier"], "tier-b")
        cards += f"""
        <a href="{c['file']}" class="area-card">
          <div class="area-card-header">
            <span class="area-name">{c['name']}</span>
            <span class="tier-badge {tier_cls}">{c['tier']} 级</span>
          </div>
          <div class="area-desc">{c['desc']}</div>
        </a>"""

    return f"""
    <div class="area-top-link">
      <a href="amsterdam-region-buying-2026.html" class="area-main-btn">阿姆周边买房综合看板 →</a>
    </div>
    <div class="area-grid">{cards}</div>"""


# ── Full HTML ─────────────────────────────────────────────────────────────

def generate_html(props: list[dict]) -> str:
    n_liked  = len([p for p in props if "liked"        in p["tags"]])
    n_viewed = len([p for p in props if "viewed"       in p["tags"]])
    n_vve    = len([p for p in props if "vve_reviewed" in p["tags"]])
    n_bid    = len([p for p in props if "bidding_done" in p["tags"]])

    tab_overview = render_overview(props)
    tab_liked    = render_liked(props)
    tab_viewed   = render_viewed(props)
    tab_vve      = render_vve(props)
    tab_bidding  = render_bidding(props)
    tab_area     = render_area()

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>荷兰买房助手</title>
<style>
:root{{
  --bg:#f4f1eb;--card:#fffdf8;--ink:#1c1917;--muted:#78716c;
  --accent:#c45c26;--accent-soft:#fdebd3;
  --green:#166534;--green-bg:#dcfce7;
  --red:#991b1b;--red-bg:#fee2e2;
  --amber:#92400e;--amber-bg:#fef3c7;
  --blue:#1e40af;--blue-bg:#dbeafe;
  --border:#e7e5e4;
}}
*{{box-sizing:border-box;}}
body{{
  margin:0;
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  background:linear-gradient(180deg,#ebe4d8 0%,var(--bg) 120px);
  color:var(--ink);line-height:1.5;
}}
.wrap{{max-width:1150px;margin:0 auto;padding:1.5rem 1.25rem 4rem;}}

/* ── Header ── */
.page-header{{
  margin-bottom:1.5rem;padding-bottom:1.25rem;
  border-bottom:2px solid var(--accent);
  display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:.5rem;
}}
.page-header h1{{margin:0;font-size:1.85rem;letter-spacing:-.02em;}}
.page-header p{{margin:0;color:var(--muted);font-size:.9rem;}}

/* ── Tabs ── */
.tab-nav{{
  display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:1.75rem;
  padding:.5rem;background:var(--card);border:1px solid var(--border);
  border-radius:12px;box-shadow:0 2px 8px rgba(28,25,23,.05);
}}
.tab-btn{{
  padding:.45rem 1.1rem;border:none;background:transparent;
  border-radius:8px;cursor:pointer;font-size:.9rem;font-weight:500;
  color:var(--muted);font-family:inherit;transition:all .15s;
}}
.tab-btn:hover{{background:var(--accent-soft);color:var(--accent);}}
.tab-btn.active{{background:var(--accent);color:#fff;}}
.tab-panel{{display:none;}}
.tab-panel.active{{display:block;}}

/* ── Overview stats ── */
.stat-grid{{
  display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:1rem;margin-bottom:2rem;
}}
.stat-card{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.25rem;text-align:center;
  box-shadow:0 4px 12px rgba(28,25,23,.06);
}}
.stat-num{{display:block;font-size:2.5rem;font-weight:700;color:var(--accent);line-height:1;}}
.stat-label{{display:block;font-size:.82rem;color:var(--muted);margin-top:.35rem;text-transform:uppercase;letter-spacing:.04em;}}

/* ── Tables ── */
.table-wrap{{overflow-x:auto;border-radius:10px;box-shadow:0 4px 16px rgba(28,25,23,.07);margin-bottom:1.5rem;}}
.data-table{{width:100%;border-collapse:collapse;font-size:.88rem;background:var(--card);}}
.data-table th{{
  background:#292524;color:#fafaf9;font-weight:600;
  padding:.55rem .7rem;text-align:left;white-space:nowrap;
}}
.data-table td{{
  border-bottom:1px solid var(--border);padding:.5rem .7rem;vertical-align:middle;
}}
.data-table tr:last-child td{{border-bottom:none;}}
.data-table tr:hover td{{background:#faf9f7;}}
.score-high{{background:var(--green-bg);color:var(--green);font-weight:700;text-align:center;}}
.score-mid{{background:var(--amber-bg);color:var(--amber);font-weight:700;text-align:center;}}
.score-low{{background:var(--red-bg);color:var(--red);font-weight:700;text-align:center;}}

/* ── Badges & pills ── */
.badge{{
  display:inline-block;padding:.15rem .5rem;border-radius:6px;
  font-size:.78rem;font-weight:700;
}}
.badge-green{{background:var(--green-bg);color:var(--green);}}
.badge-blue{{background:var(--blue-bg);color:var(--blue);}}
.badge-amber{{background:var(--amber-bg);color:var(--amber);}}
.badge-red{{background:var(--red-bg);color:var(--red);}}
.badge-gray{{background:#f3f4f6;color:#374151;}}
.pill{{
  display:inline-block;padding:.1rem .45rem;border-radius:999px;
  font-size:.75rem;font-weight:600;margin-right:.2rem;
}}
.pill-gray{{background:#f3f4f6;color:#374151;}}
.pill-blue{{background:var(--blue-bg);color:var(--blue);}}
.pill-amber{{background:var(--amber-bg);color:var(--amber);}}
.pill-green{{background:var(--green-bg);color:var(--green);}}
.flag{{
  display:inline-block;background:var(--red-bg);color:var(--red);
  font-size:.72rem;padding:.1rem .4rem;border-radius:4px;margin:.15rem .1rem;
}}
.region-tag{{
  display:inline-block;font-size:.75rem;padding:.1rem .4rem;
  border-radius:4px;background:#f1f5f9;color:#475569;margin-left:.3rem;
}}

/* ── Buttons / links ── */
.btn-link{{
  display:inline-block;padding:.15rem .5rem;border-radius:5px;
  font-size:.78rem;background:var(--accent-soft);color:var(--accent);
  text-decoration:none;margin-right:.3rem;
}}
.btn-link:hover{{background:var(--accent);color:#fff;}}

/* ── VvE cards ── */
.vve-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem;}}
.vve-card{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.1rem;box-shadow:0 4px 14px rgba(28,25,23,.06);
}}
.vve-card-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.5rem;}}
.vve-addr{{font-size:1.05rem;font-weight:700;}}
.vve-city{{color:var(--muted);font-size:.88rem;margin-left:.3rem;}}
.vve-verdict{{color:var(--muted);font-size:.86rem;margin-bottom:.6rem;}}
.flags-row{{margin-bottom:.7rem;}}
.vve-links{{margin-top:.25rem;}}

/* ── Bidding cards ── */
.bid-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1.25rem;}}
.bid-card{{
  background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:1.25rem;box-shadow:0 6px 18px rgba(28,25,23,.07);
}}
.bid-card-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.75rem;}}
.bid-card-header h3{{margin:0;font-size:1.15rem;}}
.bid-city{{color:var(--muted);font-weight:400;font-size:.9rem;}}
.bid-stats{{
  display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.75rem;font-size:.86rem;
  color:var(--muted);
}}
.bid-stats span{{
  background:#f8f8f7;border:1px solid var(--border);
  border-radius:999px;padding:.1rem .55rem;
}}
.bid-verdict{{font-size:.88rem;margin-bottom:.75rem;}}
.bid-links{{margin-top:.25rem;}}

/* ── Area analysis ── */
.area-top-link{{margin-bottom:1.5rem;}}
.area-main-btn{{
  display:inline-block;padding:.65rem 1.4rem;background:var(--accent);color:#fff;
  text-decoration:none;border-radius:10px;font-weight:600;font-size:.95rem;
}}
.area-main-btn:hover{{background:#a04d1f;}}
.area-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;}}
.area-card{{
  display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.1rem;text-decoration:none;color:var(--ink);
  box-shadow:0 4px 12px rgba(28,25,23,.05);transition:box-shadow .15s;
}}
.area-card:hover{{box-shadow:0 8px 24px rgba(28,25,23,.12);}}
.area-card-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem;}}
.area-name{{font-weight:700;font-size:1.05rem;}}
.tier-badge{{
  font-size:.78rem;font-weight:700;padding:.15rem .5rem;border-radius:6px;
}}
.tier-s{{background:var(--green-bg);color:var(--green);}}
.tier-a{{background:var(--blue-bg);color:var(--blue);}}
.tier-b{{background:var(--amber-bg);color:var(--amber);}}
.area-desc{{font-size:.85rem;color:var(--muted);}}
.area-link-row{{margin-top:1.5rem;}}
.area-main-link{{
  display:inline-block;padding:.5rem 1.1rem;border-radius:8px;
  background:var(--accent-soft);color:var(--accent);font-weight:600;text-decoration:none;
}}
.area-main-link:hover{{background:var(--accent);color:#fff;}}

/* ── Misc ── */
.section-title{{
  font-size:.95rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);
  margin:1.5rem 0 .75rem;
}}
.tab-intro{{color:var(--muted);font-size:.9rem;margin:0 0 1rem;}}
@media(max-width:600px){{
  .page-header{{flex-direction:column;align-items:flex-start;}}
  .tab-nav{{gap:.25rem;}}
  .tab-btn{{font-size:.82rem;padding:.4rem .75rem;}}
}}
</style>
</head>
<body>
<div class="wrap">

<header class="page-header">
  <div>
    <h1>荷兰买房助手</h1>
    <p>购房追踪 · 2026</p>
  </div>
  <p>今日：2026-07-11</p>
</header>

<nav class="tab-nav">
  <button class="tab-btn active" onclick="switchTab('overview',this)">全部概览</button>
  <button class="tab-btn" onclick="switchTab('liked',this)">偏好 ({n_liked})</button>
  <button class="tab-btn" onclick="switchTab('viewed',this)">已看 ({n_viewed})</button>
  <button class="tab-btn" onclick="switchTab('vve',this)">VvE 审查 ({n_vve})</button>
  <button class="tab-btn" onclick="switchTab('bidding',this)">竞价分析 ({n_bid})</button>
  <button class="tab-btn" onclick="switchTab('area',this)">地段研究</button>
</nav>

<div id="tab-overview" class="tab-panel active">{tab_overview}</div>
<div id="tab-liked"    class="tab-panel">{tab_liked}</div>
<div id="tab-viewed"   class="tab-panel">{tab_viewed}</div>
<div id="tab-vve"      class="tab-panel">{tab_vve}</div>
<div id="tab-bidding"  class="tab-panel">{tab_bidding}</div>
<div id="tab-area"     class="tab-panel">{tab_area}</div>

</div>
<script>
function switchTab(name, btn) {{
  document.querySelectorAll('.tab-panel').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
}}
</script>
</body>
</html>"""


def main() -> None:
    props = build_all_properties()
    html = generate_html(props)
    OUTPUT.write_text(html, encoding="utf-8")
    n_liked  = len([p for p in props if "liked"        in p["tags"]])
    n_viewed = len([p for p in props if "viewed"       in p["tags"]])
    n_vve    = len([p for p in props if "vve_reviewed" in p["tags"]])
    n_bid    = len([p for p in props if "bidding_done" in p["tags"]])
    print(f"Generated {OUTPUT}")
    print(f"  偏好 {n_liked}  已看 {n_viewed}  VvE审查 {n_vve}  竞价 {n_bid}")


if __name__ == "__main__":
    main()
