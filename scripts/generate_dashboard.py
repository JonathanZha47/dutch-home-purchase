#!/usr/bin/env python3
"""Generate the property comparison HTML dashboard from data/listings.json."""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "listings.json"
LIKED_HOUSE_DIR = ROOT / "liked-house"
OUTPUT_FILE = ROOT / "dashboard" / "index.html"
DOCUMENT_SUMMARY_DIR = ROOT / "viewing" / "documents-summary"

DIMENSIONS = [
    ("quality", "质量"),
    ("size", "面积"),
    ("groceries", "买菜"),
    ("tennis", "网球"),
    ("transport", "交通"),
    ("financial", "财务"),
]

COMMUNITY_AREAS = [
    {
        "name": "Almere",
        "score": 82,
        "summary": "面积换通勤：预算效率最高，但社区差异、旧房维修和出租限制要逐套看。",
        "communities": "Stedenwijk Midden-west、Muziekwijk Noord",
        "href": "community/almere.html",
    },
    {
        "name": "Weesp",
        "score": 75,
        "summary": "小城稳定型：通勤和居住质感好，供应少，投资更偏保守。",
        "communities": "Hogewey-Noord、Weespersluis",
        "href": "community/weesp.html",
    },
    {
        "name": "Zaandam",
        "score": 78,
        "summary": "到 Amsterdam CS 很强：站区新房好用，但 erfpacht 是核心陷阱。",
        "communities": "Zaans Hout / Murano / Teakhout",
        "href": "community/zaandam.html",
    },
    {
        "name": "Amsterdam Nieuw-West",
        "score": 80,
        "summary": "同是 Nieuw-West，Dijkgraafplein 和 De Aker 完全不是同一种投资逻辑。",
        "communities": "Dijkgraafpleinbuurt、De Aker-West",
        "href": "community/nieuw-west.html",
    },
    {
        "name": "Amstelveen",
        "score": 77,
        "summary": "近 Zuid/VU 和租客质量是卖点，但 €400k 预算通常要牺牲面积或楼龄。",
        "communities": "Vredeveldbuurt、Randwijck Oost、Rembrandtweg",
        "href": "community/amstelveen.html",
    },
    {
        "name": "Bijlmer / Amsterdam Zuidoost",
        "score": 84,
        "summary": "预算内最强面积+通勤组合，但要按 buurt、楼栋和 VvE 文件精细筛。",
        "communities": "Venserpolder-West、F-buurt、G-buurt-West、Haardstee",
        "href": "community/bijlmer.html",
    },
    {
        "name": "Gaasperplas / Nellestein",
        "score": 79,
        "summary": "绿地和湖区体验强，投资看大面积和车位，风险看 VvE。",
        "communities": "L-buurt / Leksmondhof",
        "href": "community/gaasperplas.html",
    },
    {
        "name": "Hoofddorp",
        "score": 83,
        "summary": "省心通勤型：本轮没有新 Funda 链接，但仍应保留为基准区。",
        "communities": "Centrum / Station corridor",
        "href": "community/hoofddorp.html",
    },
]


@dataclass
class DocumentSummary:
    title: str
    path: Path
    risk_level: str = "unknown"
    decision_impact: str = ""
    key_findings: list[str] = field(default_factory=list)
    must_verify: list[str] = field(default_factory=list)
    document_count: int = 0
    risk_keys: list[str] = field(default_factory=list)


def _relative_markdown_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_liked_house_markdown(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"{path} is missing YAML frontmatter")

    raw = yaml.safe_load(match.group(1)) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path} frontmatter must be a mapping")

    listing = dict(raw)
    listing.setdefault("source_markdown", _relative_markdown_path(path))
    listing.setdefault("status", "liked")

    scores = listing.setdefault("scores", {})
    if isinstance(scores, dict) and scores.get("total") is None:
        dimensions = [scores.get(dim) for dim, _ in DIMENSIONS]
        if all(isinstance(value, (int, float)) for value in dimensions):
            scores["total"] = round(sum(float(value) for value in dimensions), 1)

    return listing


def load_liked_house_listings(liked_house_dir: Path = LIKED_HOUSE_DIR) -> list[dict]:
    if not liked_house_dir.exists():
        return []

    listings = []
    for path in sorted(liked_house_dir.glob("*.md")):
        if path.name.lower() in {"readme.md", "index.md"}:
            continue
        listings.append(parse_liked_house_markdown(path))
    return listings


def load_json_listings() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return data.get("listings", [])


def load_listings() -> list[dict]:
    liked = load_liked_house_listings()
    if liked:
        return liked
    return load_json_listings()


def _strip_markdown(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", value)
    return value.strip()


def _heading_key(value: str) -> str:
    return re.sub(r"\s+", " ", _strip_markdown(value).strip("#：: ").lower())


def _matches_heading(value: str, headings: set[str]) -> bool:
    return _heading_key(value) in {_heading_key(heading) for heading in headings}


def _extract_bullets(lines: list[str], headings: set[str]) -> list[str]:
    bullets: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = _matches_heading(stripped, headings)
            continue
        if in_section and stripped.startswith("- "):
            bullets.append(_strip_markdown(stripped[2:]))
        elif in_section and stripped.startswith("## "):
            break
    return bullets


def _extract_labeled_value(line: str, labels: set[str]) -> str | None:
    stripped = line.strip()
    plain = _strip_markdown(stripped)
    for label in labels:
        match = re.match(rf"^{re.escape(label)}\s*[：:]\s*(.*)$", plain, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def normalize_risk_level(value: str | None) -> str:
    risk = (value or "").strip().lower()
    if "high" in risk or "高" in risk:
        return "high"
    if "medium" in risk or "中" in risk:
        return "medium"
    if "low" in risk or "低" in risk:
        return "low"
    return "unknown"


def risk_label(risk_level: str | None) -> str:
    return {
        "high": "高",
        "medium": "中",
        "low": "低",
        "unknown": "未知",
    }.get(normalize_risk_level(risk_level), "未知")


def parse_document_summary(path: Path) -> DocumentSummary | None:
    if path.name == "index.md":
        return None

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = path.stem.replace("-", " ").title()
    risk = "unknown"
    decision = ""
    document_count = 0
    risk_keys: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = _strip_markdown(
                stripped[2:]
                .replace(" - Document Review", "")
                .replace(" - 文档审查", "")
                .replace(" - 文件审查", "")
            )
        elif value := _extract_labeled_value(stripped, {"Overall risk", "总体风险", "整体风险"}):
            risk = normalize_risk_level(value)
        elif value := _extract_labeled_value(stripped, {"Decision impact", "决策影响", "出价影响"}):
            decision = value
        elif stripped.startswith("| `"):
            document_count += 1
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) >= 4:
                risk_keys.extend(re.findall(r"`([^`]+)`", cells[3]))

    unique_risk_keys = sorted(set(risk_keys))
    return DocumentSummary(
        title=title,
        path=path,
        risk_level=normalize_risk_level(risk),
        decision_impact=decision,
        key_findings=_extract_bullets(lines, {"## Key findings", "## 关键发现", "## 核心发现"}),
        must_verify=_extract_bullets(lines, {"## Must verify before bid", "## 出价前必须确认", "## 出价前必须核实"}),
        document_count=document_count,
        risk_keys=unique_risk_keys,
    )


def load_document_summaries(summary_dir: Path = DOCUMENT_SUMMARY_DIR) -> list[DocumentSummary]:
    if not summary_dir.exists():
        return []
    summaries = []
    for path in sorted(summary_dir.glob("*.md")):
        parsed = parse_document_summary(path)
        if parsed:
            summaries.append(parsed)

    risk_order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
    summaries.sort(key=lambda item: (risk_order.get(item.risk_level.lower(), 3), item.title))
    return summaries


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def score_class(score: float | None) -> str:
    if score is None:
        return "score-na"
    if score >= 4.5:
        return "score-high"
    if score >= 3:
        return "score-mid"
    return "score-low"


def verdict_class(verdict: str) -> str:
    if "强烈推荐" in verdict or "strong" in verdict.lower():
        return "verdict-strong"
    if "淘汰" in verdict or "reject" in verdict.lower():
        return "verdict-reject"
    if "备选" in verdict or "谨慎" in verdict:
        return "verdict-caution"
    return "verdict-good"


def risk_class(risk_level: str | None) -> str:
    risk = normalize_risk_level(risk_level)
    if risk == "high":
        return "risk-high"
    if risk == "medium":
        return "risk-medium"
    if risk == "low":
        return "risk-low"
    return "risk-unknown"


def is_viewed_listing(listing: dict) -> bool:
    return bool(
        listing.get("viewing_completed")
        or listing.get("viewing_folder")
        or listing.get("status") in {"viewed", "visited", "post_viewing"}
    )


def format_eur(amount) -> str:
    if amount is None:
        return "—"
    return f"€{int(amount):,}"


def _summary_link(summary: DocumentSummary) -> str:
    try:
        rel = summary.path.relative_to(ROOT)
    except ValueError:
        rel = summary.path
    return f"../{esc(rel)}"


def render_document_summary_dashboard(summaries: list[DocumentSummary]) -> str:
    if not summaries:
        return "<p class='empty'>暂无 viewing document summaries。先运行 VvE/document review。</p>"

    counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    total_documents = 0
    for summary in summaries:
        risk = normalize_risk_level(summary.risk_level)
        counts[risk] += 1
        total_documents += summary.document_count

    risk_tags = sorted({tag for summary in summaries for tag in summary.risk_keys})
    tag_html = "".join(f'<span class="flag neutral">{esc(tag)}</span>' for tag in risk_tags[:18])
    if len(risk_tags) > 18:
        tag_html += f'<span class="muted">+{len(risk_tags) - 18} 个更多</span>'

    cards = []
    for summary in summaries:
        findings = "".join(f"<li>{esc(item)}</li>" for item in summary.key_findings[:4])
        must_verify = "".join(f"<li>{esc(item)}</li>" for item in summary.must_verify[:3])
        tags = "".join(f'<span class="flag neutral">{esc(tag)}</span>' for tag in summary.risk_keys[:8])
        cards.append(
            f"""
        <article class="doc-risk-card">
          <header>
            <div>
              <h3><a href="{_summary_link(summary)}">{esc(summary.title)}</a></h3>
              <p class="meta">{esc(summary.decision_impact)}</p>
            </div>
            <span class="risk-pill {risk_class(summary.risk_level)}">{esc(risk_label(summary.risk_level))}</span>
          </header>
          <div class="doc-risk-stats">
            <span>{summary.document_count} 份文档</span>
            <span>{len(summary.risk_keys)} 个风险标签</span>
          </div>
          <div class="doc-risk-body">
            <section>
              <h4>关键发现</h4>
              <ul>{findings or '<li class="muted">暂无提取到的发现。</li>'}</ul>
            </section>
            <section>
              <h4>出价前必须确认</h4>
              <ul>{must_verify or '<li class="muted">暂无必须确认项。</li>'}</ul>
            </section>
          </div>
          <div class="flags compact">{tags or '<span class="muted">暂无风险标签</span>'}</div>
        </article>
            """
        )

    return f"""
      <div class="doc-risk-overview">
        <div><span class="label">已总结房源</span><span class="value">{len(summaries)}</span></div>
        <div><span class="label">已审查文档</span><span class="value">{total_documents}</span></div>
        <div><span class="label">高风险</span><span class="value risk-number high">{counts['high']}</span></div>
        <div><span class="label">中风险</span><span class="value risk-number medium">{counts['medium']}</span></div>
      </div>
      <div class="flags doc-risk-tags">{tag_html}</div>
      <div class="doc-risk-grid">{''.join(cards)}</div>
    """


def render_document_review(listing: dict) -> str:
    docs = listing.get("viewing_documents") or {}
    documents = docs.get("documents") or []
    if not docs and not listing.get("viewing_folder"):
        return ""

    risk = docs.get("overall_risk_level") or (listing.get("vve_analysis") or {}).get("risk_level") or "unknown"
    summary_path = docs.get("summary_path") or ""
    folder = listing.get("viewing_folder") or docs.get("folder") or ""
    summary_link = (
        f'<a href="../{esc(summary_path)}">{esc(summary_path)}</a>'
        if summary_path
        else '<span class="muted">summary pending</span>'
    )
    folder_text = esc(folder) if folder else "—"

    if documents:
        rows = []
        for doc in documents:
            risks = doc.get("risks") or []
            risk_tags = (
                "".join(f'<span class="flag">{esc(r)}</span>' for r in risks)
                if risks
                else '<span class="muted">无明显风险</span>'
            )
            rows.append(
                "<tr>"
                f"<td>{esc(doc.get('filename', ''))}</td>"
                f"<td>{esc(doc.get('type', '—'))}</td>"
                f"<td>{esc(doc.get('summary', '—'))}</td>"
                f"<td><div class=\"flags compact\">{risk_tags}</div></td>"
                "</tr>"
            )
        documents_html = (
            '<table class="documents-table">'
            "<thead><tr><th>文件</th><th>类型</th><th>摘要</th><th>风险</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )
    else:
        documents_html = '<p class="empty">还没有结构化到每份文件；先查看 summary，再补充 viewing_documents.documents。</p>'

    return f"""
      <section class="viewing-box">
        <h3>看房文件审查</h3>
        <div class="stats-grid">
          <div><span class="label">看房日期</span><span class="value">{esc(listing.get('viewing_date', '—'))}</span></div>
          <div><span class="label">总体风险</span><span class="risk-pill {risk_class(risk)}">{esc(risk)}</span></div>
          <div><span class="label">文件夹</span><span class="value small-value">{folder_text}</span></div>
          <div><span class="label">Summary</span><span class="value small-value">{summary_link}</span></div>
        </div>
        {documents_html}
      </section>
    """


def render_listing_card(listing: dict) -> str:
    scores = listing.get("scores", {})
    total = scores.get("total")
    pros = listing.get("pros", [])
    cons = listing.get("cons", [])
    vve = listing.get("vve_analysis", {})
    erf = listing.get("erfpacht", {})

    score_cells = "".join(
        f'<td class="{score_class(scores.get(dim))}">{esc(scores.get(dim, "—"))}</td>'
        for dim, _ in DIMENSIONS
    )

    pros_html = "".join(f"<li>{esc(p)}</li>" for p in pros) or "<li class='muted'>—</li>"
    cons_html = "".join(f"<li>{esc(c)}</li>" for c in cons) or "<li class='muted'>—</li>"

    flags = vve.get("red_flags", [])
    flags_html = (
        "".join(f'<span class="flag">{esc(f)}</span>' for f in flags)
        if flags
        else '<span class="muted">无明显红旗</span>'
    )

    erf_text = erf.get("summary") or erf.get("type", "—")
    monthly_carry = listing.get("monthly_carry_eur")
    true_cost = listing.get("true_cost_eur")
    pest = listing.get("price_estimate") or {}
    market_value = pest.get("market_value_eur")
    overbid_pct = pest.get("overbid_pct")
    confidence = pest.get("confidence", "—")
    estimate_notes = pest.get("notes", "")
    source_markdown = listing.get("source_markdown")
    source_html = ""
    if source_markdown:
        source_html = (
            f'<span>源 markdown: <a href="../{esc(source_markdown)}">{esc(source_markdown)}</a></span>'
        )

    pricing_box = ""
    if pest:
        overbid_label = f"{overbid_pct * 100:.1f}%" if isinstance(overbid_pct, (int, float)) else "—"
        pricing_box = f"""
      <section class="pricing-box">
        <h3>成交价预估 (Level 1 · CBS)</h3>
        <div class="stats-grid">
          <div><span class="label">CBS 公允价</span><span class="value">{format_eur(market_value)}</span></div>
          <div><span class="label">预估溢价</span><span class="value">{overbid_label}</span></div>
          <div><span class="label">置信度</span><span class="value">{esc(confidence)}</span></div>
          <div><span class="label">模型</span><span class="value">{esc(pest.get('method', '—'))}</span></div>
        </div>
        <p class="meta">{esc(estimate_notes)}</p>
      </section>
        """

    return f"""
    <article class="listing-card" id="listing-{esc(listing.get('id'))}">
      <header class="card-header">
        <div>
          <h2><a href="{esc(listing.get('funda_url', '#'))}" target="_blank" rel="noopener">{esc(listing.get('address', 'Unknown'))}</a></h2>
          <p class="meta">{esc(listing.get('city', ''))} · {esc(listing.get('postcode', ''))} · {esc(listing.get('build_year', ''))} · Label {esc(listing.get('energy_label', '—'))}</p>
        </div>
        <div class="badges">
          <span class="verdict {verdict_class(listing.get('verdict', ''))}">{esc(listing.get('verdict', '—'))}</span>
          <span class="total-score">{esc(total)}/30</span>
        </div>
      </header>

      <div class="stats-grid">
        <div><span class="label">挂牌价</span><span class="value">{format_eur(listing.get('price_asking'))}</span></div>
        <div><span class="label">预估成交价</span><span class="value">{format_eur(listing.get('price_estimated_bid'))}</span></div>
        <div><span class="label">真实总成本</span><span class="value">{format_eur(true_cost)}</span></div>
        <div><span class="label">面积</span><span class="value">{esc(listing.get('living_area_m2', '—'))} m²</span></div>
        <div><span class="label">VvE/月</span><span class="value">{format_eur(listing.get('vve_monthly'))}</span></div>
        <div><span class="label">月持有成本</span><span class="value">{format_eur(monthly_carry)}</span></div>
      </div>

      <table class="score-table">
        <thead><tr>{''.join(f'<th>{label}</th>' for _, label in DIMENSIONS)}<th>总分</th></tr></thead>
        <tbody><tr>{score_cells}<td class="total-cell">{esc(total)}</td></tr></tbody>
      </table>

      {pricing_box}

      <div class="two-col">
        <section>
          <h3>优点</h3>
          <ul class="pros">{pros_html}</ul>
        </section>
        <section>
          <h3>缺点</h3>
          <ul class="cons">{cons_html}</ul>
        </section>
      </div>

      <section class="vve-box">
        <h3>VvE 分析</h3>
        <p>{esc(vve.get('notes', '—'))}</p>
        <div class="flags">{flags_html}</div>
        <p class="meta">Erfpacht: {esc(erf_text)}</p>
      </section>

      {render_document_review(listing)}

      <footer class="card-footer">
        <span>分析日期: {esc(listing.get('analyzed_at', '—'))}</span>
        <span>状态: {esc(listing.get('status', 'active'))}</span>
        {source_html}
      </footer>
    </article>
    """


def render_comparison_table(listings: list[dict]) -> str:
    if not listings:
        return "<p class='empty'>暂无房源。添加 Funda 链接后重新生成 dashboard。</p>"

    sorted_listings = sorted(
        listings,
        key=lambda x: (x.get("scores", {}).get("total") or 0),
        reverse=True,
    )

    header = "<tr><th>排名</th><th>地址</th><th>挂牌</th><th>公允价</th><th>预估成交</th><th>真实成本</th><th>溢价</th><th>总分</th><th>结论</th></tr>"

    rows = []
    for i, listing in enumerate(sorted_listings, 1):
        scores = listing.get("scores", {})
        pest = listing.get("price_estimate") or {}
        ob = pest.get("overbid_pct")
        ob_label = f"{ob * 100:.1f}%" if isinstance(ob, (int, float)) else "—"
        rows.append(
            "<tr>"
            f"<td>{i}</td>"
            f"<td><a href=\"{esc(listing.get('funda_url', '#'))}\" target=\"_blank\" rel=\"noopener\">{esc(listing.get('address', ''))}</a></td>"
            f"<td>{format_eur(listing.get('price_asking'))}</td>"
            f"<td>{format_eur(pest.get('market_value_eur'))}</td>"
            f"<td>{format_eur(listing.get('price_estimated_bid'))}</td>"
            f"<td>{format_eur(listing.get('true_cost_eur'))}</td>"
            f"<td>{ob_label}</td>"
            f"<td class=\"total-cell\">{esc(scores.get('total', '—'))}</td>"
            f"<td><span class=\"verdict {verdict_class(listing.get('verdict', ''))}\">{esc(listing.get('verdict', ''))}</span></td>"
            + "</tr>"
        )

    return f"<table class=\"comparison-table\"><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def render_viewed_table(listings: list[dict]) -> str:
    viewed = [listing for listing in listings if is_viewed_listing(listing)]
    if not viewed:
        return "<p class='empty'>暂无已看房房源。完成 bezichtiging 后把文件放入 viewing/&lt;房源名&gt;/ 并更新 listing。</p>"

    def sort_key(listing: dict) -> tuple[str, str]:
        return (listing.get("viewing_date") or "", listing.get("address") or "")

    rows = []
    for listing in sorted(viewed, key=sort_key, reverse=True):
        docs = listing.get("viewing_documents") or {}
        documents = docs.get("documents") or []
        risk = docs.get("overall_risk_level") or (listing.get("vve_analysis") or {}).get("risk_level") or "unknown"
        summary_path = docs.get("summary_path") or ""
        summary = (
            f'<a href="../{esc(summary_path)}">summary</a>'
            if summary_path
            else '<span class="muted">pending</span>'
        )
        rows.append(
            "<tr>"
            f"<td><a href=\"#{'listing-' + esc(listing.get('id', ''))}\">{esc(listing.get('address', ''))}</a></td>"
            f"<td>{esc(listing.get('viewing_date', '—'))}</td>"
            f"<td><span class=\"risk-pill {risk_class(risk)}\">{esc(risk)}</span></td>"
            f"<td>{len(documents)}</td>"
            f"<td>{summary}</td>"
            f"<td>{esc((listing.get('vve_analysis') or {}).get('notes', '—'))}</td>"
            "</tr>"
        )
    header = "<tr><th>地址</th><th>看房日期</th><th>风险</th><th>文件数</th><th>审查摘要</th><th>VvE/文件重点</th></tr>"
    return f"<table class=\"comparison-table viewed-table\"><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def render_community_overview() -> str:
    cards = []
    for area in COMMUNITY_AREAS:
        cards.append(
            f"""
        <article class="region-card">
          <header>
            <h3><a href="{esc(area['href'])}">{esc(area['name'])}</a></h3>
            <span class="region-score">{esc(area['score'])}</span>
          </header>
          <p>{esc(area['summary'])}</p>
          <p class="meta"><strong>涉及社区：</strong>{esc(area['communities'])}</p>
          <a class="region-link" href="{esc(area['href'])}">打开社区深度页</a>
        </article>
            """
        )

    return f"""
      <div class="region-intro">
        <div>
          <h2>区域与社区总览</h2>
          <p class="meta">把独立 community pages 合并为主看板入口：先看大区判断，再进入每个社区深度页核对安全、宜居和投资属性。</p>
        </div>
        <a class="region-overview-link" href="amsterdam-region-buying-2026.html">打开完整区域总览</a>
      </div>
      <div class="region-grid">{''.join(cards)}</div>
    """


def generate_html(listings: list[dict]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = "".join(render_listing_card(l) for l in listings)
    comparison = render_comparison_table(listings)
    viewed = render_viewed_table(listings)
    document_summaries = render_document_summary_dashboard(load_document_summaries())
    community_overview = render_community_overview()

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>荷兰买房助手 · 房源对比</title>
  <style>
    :root {{
      --bg: #f4f1eb;
      --card: #fffdf8;
      --ink: #1c1917;
      --muted: #78716c;
      --accent: #c45c26;
      --accent-soft: #fdebd3;
      --green: #166534;
      --green-bg: #dcfce7;
      --red: #991b1b;
      --red-bg: #fee2e2;
      --amber: #92400e;
      --amber-bg: #fef3c7;
      --border: #e7e5e4;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
      background: linear-gradient(180deg, #ebe4d8 0%, var(--bg) 120px);
      color: var(--ink);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
    header.page {{
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 2px solid var(--accent);
    }}
    header.page h1 {{
      margin: 0 0 .25rem;
      font-size: 2rem;
      letter-spacing: -0.02em;
    }}
    header.page p {{ margin: 0; color: var(--muted); }}
    .comparison-table, .score-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .92rem;
      background: var(--card);
    }}
    .comparison-table th, .comparison-table td,
    .score-table th, .score-table td {{
      border: 1px solid var(--border);
      padding: .55rem .65rem;
      text-align: center;
    }}
    .comparison-table th, .score-table th {{
      background: #292524;
      color: #fafaf9;
      font-weight: 600;
    }}
    .comparison-table td:nth-child(2) {{ text-align: left; }}
    .viewed-table td:nth-child(1), .viewed-table td:nth-child(6) {{ text-align: left; }}
    .comparison-wrap {{
      overflow-x: auto;
      margin-bottom: 2.5rem;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(28,25,23,.08);
    }}
    .listing-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.25rem 1.35rem 1rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 6px 18px rgba(28,25,23,.06);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: flex-start;
      margin-bottom: 1rem;
    }}
    .card-header h2 {{ margin: 0; font-size: 1.35rem; }}
    .card-header a {{ color: var(--accent); text-decoration: none; }}
    .card-header a:hover {{ text-decoration: underline; }}
    .meta {{ color: var(--muted); font-size: .9rem; margin: .25rem 0 0; }}
    .badges {{ display: flex; flex-direction: column; align-items: flex-end; gap: .35rem; }}
    .verdict {{
      display: inline-block;
      padding: .2rem .65rem;
      border-radius: 999px;
      font-size: .82rem;
      font-weight: 600;
    }}
    .verdict-strong {{ background: var(--green-bg); color: var(--green); }}
    .verdict-good {{ background: #dbeafe; color: #1e40af; }}
    .verdict-caution {{ background: var(--amber-bg); color: var(--amber); }}
    .verdict-reject {{ background: var(--red-bg); color: var(--red); }}
    .total-score {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent);
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: .75rem;
      margin-bottom: 1rem;
    }}
    .stats-grid .label {{
      display: block;
      font-size: .78rem;
      text-transform: uppercase;
      letter-spacing: .04em;
      color: var(--muted);
    }}
    .stats-grid .value {{ font-weight: 700; font-size: 1.05rem; }}
    .score-table {{ margin-bottom: 1rem; border-radius: 8px; overflow: hidden; }}
    .score-high {{ background: var(--green-bg); color: var(--green); font-weight: 600; }}
    .score-mid {{ background: var(--amber-bg); color: var(--amber); }}
    .score-low {{ background: var(--red-bg); color: var(--red); }}
    .score-na {{ background: #f5f5f4; color: var(--muted); }}
    .total-cell {{ font-weight: 700; background: var(--accent-soft) !important; }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-bottom: 1rem;
    }}
    @media (max-width: 700px) {{
      .two-col {{ grid-template-columns: 1fr; }}
      .card-header {{ flex-direction: column; }}
      .badges {{ align-items: flex-start; }}
    }}
    .two-col h3, .vve-box h3, .viewing-box h3 {{
      margin: 0 0 .5rem;
      font-size: .95rem;
      text-transform: uppercase;
      letter-spacing: .05em;
      color: var(--muted);
    }}
    .pros li {{ color: var(--green); }}
    .cons li {{ color: var(--red); }}
    ul {{ margin: 0; padding-left: 1.2rem; }}
    .vve-box {{
      background: #fafaf9;
      border: 1px dashed var(--border);
      border-radius: 10px;
      padding: .85rem 1rem;
      margin-bottom: .75rem;
    }}
    .viewing-box {{
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: .85rem 1rem;
      margin-bottom: .75rem;
    }}
    .documents-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .86rem;
      background: #fff;
    }}
    .documents-table th, .documents-table td {{
      border: 1px solid var(--border);
      padding: .45rem .55rem;
      vertical-align: top;
    }}
    .documents-table th {{
      background: #475569;
      color: #fff;
      text-align: left;
    }}
    .pricing-box {{
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 10px;
      padding: .85rem 1rem;
      margin-bottom: 1rem;
    }}
    .pricing-box h3 {{ margin: 0 0 .65rem; color: #1e40af; }}
    .flags {{ display: flex; flex-wrap: wrap; gap: .4rem; margin: .5rem 0; }}
    .flags.compact {{ margin: 0; }}
    .flag {{
      background: var(--red-bg);
      color: var(--red);
      font-size: .78rem;
      padding: .15rem .5rem;
      border-radius: 6px;
    }}
    .risk-pill {{
      display: inline-block;
      padding: .18rem .55rem;
      border-radius: 999px;
      font-size: .8rem;
      font-weight: 700;
    }}
    .risk-low {{ background: var(--green-bg); color: var(--green); }}
    .risk-medium {{ background: var(--amber-bg); color: var(--amber); }}
    .risk-high {{ background: var(--red-bg); color: var(--red); }}
    .risk-unknown {{ background: #e5e7eb; color: #374151; }}
    .small-value {{ font-size: .9rem; overflow-wrap: anywhere; }}
    .doc-risk-overview {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: .75rem;
      margin-bottom: 1rem;
    }}
    .doc-risk-overview > div {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: .75rem .85rem;
    }}
    .doc-risk-overview .label {{
      display: block;
      color: var(--muted);
      font-size: .78rem;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .doc-risk-overview .value {{ font-weight: 800; font-size: 1.35rem; }}
    .risk-number.high {{ color: var(--red); }}
    .risk-number.medium {{ color: var(--amber); }}
    .doc-risk-tags {{ margin-bottom: 1rem; }}
    .flag.neutral {{ background: #e7e5e4; color: #44403c; }}
    .doc-risk-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
    }}
    .doc-risk-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1rem;
      box-shadow: 0 5px 14px rgba(28,25,23,.05);
    }}
    .doc-risk-card header {{
      display: flex;
      justify-content: space-between;
      gap: .8rem;
      align-items: flex-start;
      margin-bottom: .6rem;
    }}
    .doc-risk-card h3 {{ margin: 0; font-size: 1.05rem; }}
    .doc-risk-card h3 a {{ color: var(--accent); text-decoration: none; }}
    .doc-risk-card h3 a:hover {{ text-decoration: underline; }}
    .doc-risk-stats {{
      display: flex;
      gap: .45rem;
      flex-wrap: wrap;
      margin-bottom: .75rem;
      color: var(--muted);
      font-size: .86rem;
    }}
    .doc-risk-stats span {{
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: .1rem .5rem;
      background: #fafaf9;
    }}
    .doc-risk-body {{
      display: grid;
      grid-template-columns: 1fr;
      gap: .75rem;
      margin-bottom: .75rem;
    }}
    .doc-risk-body h4 {{
      margin: 0 0 .35rem;
      color: var(--muted);
      font-size: .8rem;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .doc-risk-body li {{ margin-bottom: .25rem; }}
    .region-intro {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: flex-start;
      margin-bottom: 1rem;
    }}
    .region-intro h2 {{ margin: 0 0 .25rem; }}
    .region-overview-link, .region-link {{
      display: inline-block;
      text-decoration: none;
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      border-radius: 8px;
      padding: .45rem .75rem;
      font-size: .9rem;
      white-space: nowrap;
    }}
    .region-link {{
      background: var(--card);
      color: var(--accent);
      margin-top: .4rem;
    }}
    .region-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: .85rem;
    }}
    .region-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: .95rem 1rem;
      box-shadow: 0 5px 14px rgba(28,25,23,.05);
    }}
    .region-card header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: .75rem;
      margin-bottom: .45rem;
    }}
    .region-card h3 {{ margin: 0; font-size: 1.05rem; }}
    .region-card h3 a {{ color: var(--accent); text-decoration: none; }}
    .region-card p {{ margin: .45rem 0; }}
    .region-score {{
      background: #292524;
      color: #fafaf9;
      border-radius: 8px;
      padding: .2rem .5rem;
      font-weight: 700;
    }}
    .card-footer {{
      display: flex;
      justify-content: space-between;
      font-size: .82rem;
      color: var(--muted);
      border-top: 1px solid var(--border);
      padding-top: .65rem;
    }}
    .empty {{ color: var(--muted); font-style: italic; }}
    .muted {{ color: var(--muted); }}
    .top-nav {{ display: flex; gap: .5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }}
    .top-nav a {{ text-decoration: none; padding: .45rem .85rem; border-radius: 999px;
      border: 1px solid var(--border); background: var(--card); color: var(--ink); font-size: .9rem; }}
    .top-nav a.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    @media (max-width: 700px) {{
      .region-intro {{ flex-direction: column; }}
      .region-overview-link {{ white-space: normal; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <nav class="top-nav">
      <a href="index.html" class="active">深度分析看板</a>
      <a href="search-board.html">搜房 Inbox</a>
      <a href="amsterdam-region-buying-2026.html">区域/社区</a>
    </nav>
    <header class="page">
      <h1>荷兰买房助手 · 房源库</h1>
      <p>预算 ≤ €500k · 2000年后 · 能效 B+ · 共 {len(listings)} 套 · 更新于 {generated_at}</p>
    </header>

    <section class="comparison-wrap">
      <h2 style="margin-top:0">总览对比</h2>
      {comparison}
    </section>

    <section class="comparison-wrap" id="community-overview">
      {community_overview}
    </section>

    <section class="comparison-wrap">
      <h2 style="margin-top:0">已看房 · 文件审查</h2>
      {viewed}
    </section>

    <section class="comparison-wrap">
      <h2 style="margin-top:0">已看房文件风险</h2>
      {document_summaries}
    </section>

    <section>
      <h2>详细卡片</h2>
      {cards if cards else '<p class="empty">暂无详细卡片。</p>'}
    </section>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML dashboard from listings.json")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    args = parser.parse_args()

    listings = load_listings()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(generate_html(listings), encoding="utf-8")
    print(f"Dashboard written to {args.output} ({len(listings)} listings)")

    # Also refresh search inbox board if script exists
    try:
        from generate_search_board import main as gen_search

        gen_search()
    except Exception as e:
        print(f"Note: search board not regenerated: {e}")


if __name__ == "__main__":
    main()
