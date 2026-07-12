import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_dashboard import (  # noqa: E402
    generate_html,
    load_document_summaries,
    load_liked_house_listings,
    render_document_summary_dashboard,
)


class GenerateDashboardViewedWorkflowTest(unittest.TestCase):
    def test_liked_house_markdown_is_loaded_as_dashboard_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            house_dir = Path(tmp)
            house_file = house_dir / "almere-zeistpad-42.md"
            house_file.write_text(
                """---
id: "44453969"
funda_url: "https://www.funda.nl/detail/koop/almere/huis-zeistpad-42/44453969/"
address: "Zeistpad 42"
city: "Almere"
region: "almere"
postcode: ""
price_asking: null
price_estimated_bid: null
living_area_m2: null
bedrooms: null
build_year: null
energy_label: null
vve_monthly: null
erfpacht:
  type: verify
  summary: "产权/地租待从 Funda 与 koopakte 核实"
buyer_costs_eur: 6000
true_cost_eur: null
monthly_carry_eur: null
scores:
  quality: null
  size: null
  groceries: null
  tennis: null
  transport: null
  financial: null
  total: null
pros:
  - "Almere B-tier，可作为空间/总价对照组"
cons:
  - "产权、地租、VvE、面积和能效均未核实"
vve_analysis:
  monthly_fee: null
  red_flags:
    - verify_vve
  notes: "待核实是否有 VvE、reservefonds/MJOP 或自有地。"
verdict: "待补充分析"
status: "liked"
analyzed_at: "2026-07-04"
source_markdown: "liked-house/almere-zeistpad-42.md"
---

# Zeistpad 42, Almere

## 产权与财务

- 产权/地租：待核实。

## 待核实

- Funda 页面当前详情、产权、VvE、面积、能效。
""",
                encoding="utf-8",
            )

            listings = load_liked_house_listings(house_dir)
            html = generate_html(listings)

            self.assertEqual(len(listings), 1)
            self.assertEqual(listings[0]["id"], "44453969")
            self.assertEqual(listings[0]["source_markdown"], "liked-house/almere-zeistpad-42.md")
            self.assertIn("Zeistpad 42", html)
            self.assertIn("产权/地租待从 Funda 与 koopakte 核实", html)
            self.assertIn("verify_vve", html)
            self.assertIn("liked-house/almere-zeistpad-42.md", html)

    def test_dashboard_includes_region_and_community_entry_points(self):
        html = generate_html([])

        self.assertIn("区域与社区总览", html)
        self.assertIn("amsterdam-region-buying-2026.html", html)
        self.assertIn("community/bijlmer.html", html)
        self.assertIn("Bijlmer / Amsterdam Zuidoost", html)
        self.assertIn("Hoofddorp", html)

    def test_viewed_listing_renders_document_review_section(self):
        html = generate_html(
            [
                {
                    "id": "89726920",
                    "funda_url": "https://www.funda.nl/detail/koop/amsterdam/appartement-gooise-kant-374/89726920/",
                    "address": "Gooise Kant 374, Amsterdam Zuidoost",
                    "city": "Amsterdam",
                    "postcode": "1104",
                    "price_asking": 370000,
                    "living_area_m2": 60,
                    "build_year": 2023,
                    "energy_label": "A++",
                    "status": "viewed",
                    "viewing_completed": True,
                    "viewing_date": "2026-07-04",
                    "viewing_folder": "viewing/gooise-kant-374",
                    "scores": {
                        "quality": 5,
                        "size": 2,
                        "groceries": 4,
                        "tennis": 3,
                        "transport": 5,
                        "financial": 4,
                        "total": 23,
                    },
                    "verdict": "值得看房",
                    "vve_analysis": {
                        "risk_level": "medium",
                        "red_flags": ["verify_mjop_and_reservefonds"],
                        "notes": "MJOP reserve needs confirmation before bidding.",
                    },
                    "viewing_documents": {
                        "summary_path": "viewing/gooise-kant-374/documents-summary.md",
                        "overall_risk_level": "medium",
                        "documents": [
                            {
                                "filename": "MJOP.pdf",
                                "type": "MJOP",
                                "summary": "Major facade work appears in the maintenance plan.",
                                "risks": ["planned_major_work"],
                            }
                        ],
                    },
                }
            ]
        )

        self.assertIn("已看房", html)
        self.assertIn("文件审查", html)
        self.assertIn("viewing/gooise-kant-374/documents-summary.md", html)
        self.assertIn("MJOP.pdf", html)
        self.assertIn("planned_major_work", html)

    def test_document_summaries_render_visual_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary_dir = Path(tmp)
            summary_file = summary_dir / "sample-home.md"
            summary_file.write_text(
                """# Sample Home - 文档审查

总体风险：**高（High）**
决策影响：只有明显折价才值得出价。

## 关键发现

- **储备问题：** 未来年份储备金转负。
- **能源问题：** 能源标签 C 与要求冲突。

## 出价前必须确认

- 询问是否预计有一次性追加缴费。

## 单文件摘要

| 文件 | 类型 | 有用信息 | 风险标签 |
|---|---|---|---|
| `MJOP.pdf` | MJOP | 储备金转负。 | `future_reserve_gap`, `planned_major_work` |
""",
                encoding="utf-8",
            )

            summaries = load_document_summaries(summary_dir)
            html = render_document_summary_dashboard(summaries)
            full_html = generate_html([])

            self.assertEqual(len(summaries), 1)
            self.assertIn("已看房文件风险", full_html)
            self.assertIn("Sample Home", html)
            self.assertIn("高", html)
            self.assertIn("关键发现", html)
            self.assertIn("future_reserve_gap", html)
            self.assertIn("询问是否预计有一次性追加缴费。", html)


if __name__ == "__main__":
    unittest.main()
