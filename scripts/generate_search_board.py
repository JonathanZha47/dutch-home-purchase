#!/usr/bin/env python3
"""Generate interactive search inbox board (dashboard/search-board.html)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX_FILE = ROOT / "data" / "inbox.json"
SHORTLIST_FILE = ROOT / "data" / "search" / "shortlist.json"
OUTPUT = ROOT / "dashboard" / "search-board.html"


def load_inbox() -> dict:
    if INBOX_FILE.exists():
        return json.loads(INBOX_FILE.read_text(encoding="utf-8"))
    if SHORTLIST_FILE.exists():
        return json.loads(SHORTLIST_FILE.read_text(encoding="utf-8"))
    return {"listings": []}


def generate_html(inbox: dict) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    data_json = json.dumps(inbox, ensure_ascii=False)
    count = len(inbox.get("listings", []))

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>荷兰买房助手 · 搜房 Inbox</title>
  <style>
    :root {{
      --bg: #f4f1eb; --card: #fffdf8; --ink: #1c1917; --muted: #78716c;
      --accent: #c45c26; --accent-soft: #fdebd3; --green: #166534; --green-bg: #dcfce7;
      --red: #991b1b; --red-bg: #fee2e2; --amber: #92400e; --amber-bg: #fef3c7;
      --blue: #1e40af; --blue-bg: #dbeafe; --border: #e7e5e4;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Iowan Old Style", Palatino, Georgia, serif;
      background: linear-gradient(180deg, #ebe4d8 0%, var(--bg) 120px); color: var(--ink); }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 1.5rem 1.25rem 4rem; }}
    .top-nav {{ display: flex; gap: .5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }}
    .top-nav a {{ text-decoration: none; padding: .45rem .85rem; border-radius: 999px;
      border: 1px solid var(--border); background: var(--card); color: var(--ink); font-size: .9rem; }}
    .top-nav a.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    header.page {{ margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid var(--accent); }}
    header.page h1 {{ margin: 0 0 .35rem; font-size: 1.85rem; }}
    header.page p {{ margin: 0; color: var(--muted); }}
    .toolbar {{ display: flex; gap: .5rem; flex-wrap: wrap; margin: 1rem 0 1.25rem; }}
    button {{ cursor: pointer; border: 1px solid var(--border); background: var(--card);
      padding: .45rem .75rem; border-radius: 8px; font: inherit; }}
    button.primary {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    button.small {{ font-size: .82rem; padding: .25rem .55rem; }}
    .stats {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }}
    .stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px;
      padding: .65rem 1rem; min-width: 120px; }}
    .stat .n {{ font-size: 1.4rem; font-weight: 700; color: var(--accent); }}
    .stat .l {{ font-size: .78rem; color: var(--muted); text-transform: uppercase; }}
    section.panel {{ margin-bottom: 2rem; }}
    section.panel h2 {{ font-size: 1.15rem; margin: 0 0 .75rem; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--card); font-size: .9rem; }}
    th, td {{ border: 1px solid var(--border); padding: .55rem .6rem; vertical-align: middle; }}
    th {{ background: #292524; color: #fafaf9; text-align: left; }}
    tr.watchlist {{ background: #fafaf9; }}
    tr.want {{ background: var(--green-bg); }}
    tr.skip {{ opacity: .55; }}
    .tag {{ display: inline-block; font-size: .72rem; padding: .12rem .45rem; border-radius: 999px; }}
    .tag-watch {{ background: var(--amber-bg); color: var(--amber); }}
    .tag-zuid {{ background: var(--blue-bg); color: var(--blue); }}
    .tag-far {{ background: var(--red-bg); color: var(--red); }}
    .actions {{ display: flex; gap: .25rem; flex-wrap: wrap; }}
    .empty {{ color: var(--muted); font-style: italic; padding: 1rem 0; }}
    .help {{ font-size: .85rem; color: var(--muted); margin-top: .5rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <nav class="top-nav">
      <a href="index.html">深度分析看板</a>
      <a href="search-board.html" class="active">搜房 Inbox</a>
    </nav>
    <header class="page">
      <h1>搜房 Inbox · 互动看板</h1>
      <p>从搜索结果里勾选「想去看」· 选择保存在浏览器 · 共 {count} 条 · {generated_at}</p>
    </header>

    <div class="stats" id="stats"></div>

    <div class="toolbar">
      <button class="primary" id="btn-export">导出选择 (JSON)</button>
      <button id="btn-clear">清除本地选择</button>
    </div>
    <p class="help">提示：选择存在浏览器 localStorage。换电脑需点「导出」保存文件。</p>

    <section class="panel">
      <h2>想去看 · Bezichtiging 列表</h2>
      <div id="want-table"></div>
    </section>

    <section class="panel">
      <h2>新发现 · 待筛选</h2>
      <div id="discovered-table"></div>
    </section>

    <section class="panel">
      <h2>仅追踪 · 不看房</h2>
      <div id="watchlist-table"></div>
    </section>

    <section class="panel">
      <h2>已跳过</h2>
      <div id="skip-table"></div>
    </section>
  </div>

  <script id="inbox-data" type="application/json">{data_json}</script>
  <script>
    const STORAGE_KEY = 'dutch-home-purchase-inbox-state-v1';
    const inbox = JSON.parse(document.getElementById('inbox-data').textContent);

    function loadState() {{
      try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}'); }}
      catch {{ return {{}}; }}
    }}
    function saveState(state) {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }}

    function effectiveStatus(item) {{
      const state = loadState();
      if (state[item.id]) return state[item.id];
      if (item.viewing_intent === 'watchlist_only') return 'watchlist';
      return item.pipeline_status || 'discovered';
    }}

    function setStatus(id, status) {{
      const state = loadState();
      state[id] = status;
      saveState(state);
      render();
    }}

    function fmtEur(n) {{
      if (n == null) return '—';
      return '€' + Number(n).toLocaleString('en-US');
    }}

    function zoneTag(item) {{
      const tier = item.transport_tier;
      if (tier === 'S') return '<span class="tag tag-zuid">Tier S · 地铁直达 Zuid</span>';
      if (tier === 'A') return '<span class="tag tag-zuid">Tier A · 火车一站 Zuid</span>';
      if (tier === 'B') return '<span class="tag tag-watch">Tier B · ~1h OK</span>';
      if (tier === 'watchlist' || item.viewing_intent === 'watchlist_only')
        return '<span class="tag tag-far">仅追踪</span>';
      return '';
    }}

    function rowHtml(item, showActions=true) {{
      const st = effectiveStatus(item);
      const cls = st === 'want_view' ? 'want' : st === 'skip' ? 'skip' : st === 'watchlist' ? 'watchlist' : '';
      const link = item.funda_url || '#';
      const actions = showActions ? `<div class="actions">
        <button class="small primary" onclick="setStatus('${{item.id}}','want_view')">想看</button>
        <button class="small" onclick="setStatus('${{item.id}}','watchlist')">仅追踪</button>
        <button class="small" onclick="setStatus('${{item.id}}','skip')">跳过</button>
      </div>` : '';
      return `<tr class="${{cls}}" data-id="${{item.id}}">
        <td>${{zoneTag(item)}} ${{item.address || '—'}}</td>
        <td>${{fmtEur(item.price_asking)}}</td>
        <td>${{item.living_area_m2 ?? '—'}}</td>
        <td>${{item.energy_label ?? '—'}}</td>
        <td>${{item.notes || ''}}</td>
        <td><a href="${{link}}" target="_blank" rel="noopener">Funda</a></td>
        <td>${{actions}}</td>
      </tr>`;
    }}

    function tableHtml(items, showActions=true) {{
      if (!items.length) return '<p class="empty">暂无</p>';
      const head = '<table><thead><tr><th>地址</th><th>挂牌</th><th>m²</th><th>Label</th><th>备注</th><th>链接</th><th>操作</th></tr></thead><tbody>';
      const rows = items.map(i => rowHtml(i, showActions)).join('');
      return head + rows + '</tbody></table>';
    }}

    function render() {{
      const items = inbox.listings || [];
      const buckets = {{ want_view: [], discovered: [], watchlist: [], skip: [] }};
      items.forEach(item => {{
        const st = effectiveStatus(item);
        if (st === 'want_view') buckets.want_view.push(item);
        else if (st === 'skip') buckets.skip.push(item);
        else if (st === 'watchlist') buckets.watchlist.push(item);
        else buckets.discovered.push(item);
      }});

      document.getElementById('want-table').innerHTML = tableHtml(buckets.want_view, false);
      document.getElementById('discovered-table').innerHTML = tableHtml(buckets.discovered);
      document.getElementById('watchlist-table').innerHTML = tableHtml(buckets.watchlist, false);
      document.getElementById('skip-table').innerHTML = tableHtml(buckets.skip, false);

      document.getElementById('stats').innerHTML = [
        ['想看', buckets.want_view.length],
        ['待筛选', buckets.discovered.length],
        ['仅追踪', buckets.watchlist.length],
        ['跳过', buckets.skip.length],
      ].map(([l,n]) => `<div class="stat"><div class="n">${{n}}</div><div class="l">${{l}}</div></div>`).join('');
    }}

    document.getElementById('btn-export').onclick = () => {{
      const state = loadState();
      const payload = {{
        exported_at: new Date().toISOString(),
        selections: state,
        want_to_view: (inbox.listings||[]).filter(i => effectiveStatus(i) === 'want_view').map(i => ({{
          id: i.id, address: i.address, funda_url: i.funda_url, price_asking: i.price_asking
        }}))
      }};
      const blob = new Blob([JSON.stringify(payload, null, 2)], {{type: 'application/json'}});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'want-to-view.json';
      a.click();
    }};

    document.getElementById('btn-clear').onclick = () => {{
      if (confirm('清除所有本地选择？')) {{ localStorage.removeItem(STORAGE_KEY); render(); }}
    }};

    window.setStatus = setStatus;
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    inbox = load_inbox()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(generate_html(inbox), encoding="utf-8")
    print(f"Search board written to {args.output} ({len(inbox.get('listings', []))} items)")


if __name__ == "__main__":
    main()
