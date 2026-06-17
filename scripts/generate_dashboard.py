#!/usr/bin/env python3
"""Generate the property comparison HTML dashboard from data/listings.json."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "listings.json"
OUTPUT_FILE = ROOT / "dashboard" / "index.html"

DIMENSIONS = [
    ("quality", "质量"),
    ("size", "面积"),
    ("groceries", "买菜"),
    ("tennis", "网球"),
    ("transport", "交通"),
    ("financial", "财务"),
]


def load_listings() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return data.get("listings", [])


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


def format_eur(amount) -> str:
    if amount is None:
        return "—"
    return f"€{int(amount):,}"


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

      <footer class="card-footer">
        <span>分析日期: {esc(listing.get('analyzed_at', '—'))}</span>
        <span>状态: {esc(listing.get('status', 'active'))}</span>
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


def generate_html(listings: list[dict]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = "".join(render_listing_card(l) for l in listings)
    comparison = render_comparison_table(listings)

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
    .two-col h3, .vve-box h3 {{
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
    .pricing-box {{
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 10px;
      padding: .85rem 1rem;
      margin-bottom: 1rem;
    }}
    .pricing-box h3 {{ margin: 0 0 .65rem; color: #1e40af; }}
    .flags {{ display: flex; flex-wrap: wrap; gap: .4rem; margin: .5rem 0; }}
    .flag {{
      background: var(--red-bg);
      color: var(--red);
      font-size: .78rem;
      padding: .15rem .5rem;
      border-radius: 6px;
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
  </style>
</head>
<body>
  <div class="wrap">
    <nav class="top-nav">
      <a href="index.html" class="active">深度分析看板</a>
      <a href="search-board.html">搜房 Inbox</a>
    </nav>
    <header class="page">
      <h1>荷兰买房助手 · 房源库</h1>
      <p>预算 ≤ €500k · 2000年后 · 能效 B+ · 共 {len(listings)} 套 · 更新于 {generated_at}</p>
    </header>

    <section class="comparison-wrap">
      <h2 style="margin-top:0">总览对比</h2>
      {comparison}
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
