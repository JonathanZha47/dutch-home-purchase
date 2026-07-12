# Teakhout 29 Zaandam - 文档审查

审查日期：2026-07-04  
来源目录：`viewing/zaandam/`  
总体风险：**高（High）**  
决策影响：房子较新且能源标签 A，但 erfpacht、住宅/车库/主分割多 VvE 维护关系让复杂度显著上升。应保守出价。

## 关键发现

- **Erfpacht：** 2018 交付契约显示 erfpacht 权利，并有约 **EUR 43,900.63** 的资本化 canon 价值用于税务计算。出价前必须换算成当前 canon、已买断到何时、买断成本。
- **两份 VvE 储备信：** 住宅 VvE Galilei 与停车库 Murano 是分开的。住宅 VvE 2025-01-01 储备为 **EUR 321,895.51**；车库储备为 **EUR 93,503.14**。
- **储备看起来不小，但压力在上升：** 后续报表显示 VvE Galilei onderhoudsreserve 约 **EUR 429,485.30**，但 2026 中期结果约 **-EUR 29,099.65**。
- **月供上涨未完全落地：** 2026 会议纪要讨论预算约上涨 **25%**、月供增加和后续决议时间。
- **漏水/车库/主分割问题：** 会议纪要提到 Murano 主分割工程，用于处理平台/停车库接缝、伸缩缝，防止漏水；费用从流动性支付，会减少储备。
- **旧 MJOP 储备模型为负：** 旧 MJOP 在历史 EUR 29,463 年度储备水平下出现多个负余额年份；2026 会议纪要说新 MJOP/预算上涨意在修正。
- **面积：** 测量报告显示 **54.30 m2 居住面积**。
- **能源：** OCR 确认 Teakhout 29 为标签 A，但图片质量不完美；应在 EP-online/Funda 核实官方记录。

## 出价前必须确认

- 当前 canon、erfpacht 买断到期日和买断成本。
- 2026 上涨后的住宅 VvE 月供，以及任何车库相关月供。
- 25% 月供上涨是否最终批准，以及从何时生效。
- Murano 主分割车库/平台工程的本户业主分摊。
- 漏水工程是否已完成、已签约，还是仍在调查。
- 获取批准 2026 dotatie 上调后的新版 MJOP/资本化测算。

## 单文件摘要

| 文件 | 类型 | 有用信息 | 风险标签 |
|---|---|---|---|
| `43727577301-16.pdf` | 资产负债 / 中期结果 | VvE Galilei 中期余额显示维护储备 EUR 429,485.30，计算结果 -EUR 29,099.65。 | `reserve_ok_but_deficit`, `fee_pressure` |
| `AVG akte van levering Teakhout 29 Zaandam d.d. 20-12-2018-10.pdf` | 交付契约 | 确认 erfpacht 背景，以及用于转让税计算的资本化 canon 价值 EUR 43,900.63。 | `erfpacht_trap`, `notary_verify` |
| `AVG kadastrale legger Teakhout 29 Zaandam-9.pdf` | 地籍登记 | 无可抽取文本；需要人工/公证员核查。 | `machine_unreadable_scan`, `notary_verify` |
| `Brief_galilei_20260202_56905192 VVE reserve-2.pdf` | VvE 储备信 | 住宅 VvE 2025-01-01 储备：EUR 321,895.51。列出 Teakhout 29 在 general/groot onderhoud/lift reserve 中的份额。 | `reserve_context` |
| `Brief_murano pp_20260202_56906999 VVE garage-3.pdf` | 车库 VvE 储备信 | 停车库 Murano 2025-01-01 储备：EUR 93,503.14；列出 PP-52 份额。 | `split_vve_entities` |
| `D1308_-_MJOP_Teakhout_1_tm_54_Zaandam gecomprimeerd-5.pdf` | MJOP | VvE Galilei 旧 MJOP。注明已知缺陷未纳入，并建议定期更新。历史资金模型存在负储备年份。 | `future_reserve_gap`, `mjop_update_needed` |
| `Energielabel-1.jpg` | 能源标签图片 | OCR 识别 Teakhout 29、标签 A、建造期 2006-2013、HR 玻璃和独立 CV。OCR 不完美，应核实官方记录。 | `energy_ok`, `ocr_verify` |
| `Finenzo Hypotheken - Er is financieel meer mogelijk dan je denkt-8.pdf` | 营销传单 | 按揭/融资广告；无房源特定风险。 | `not_relevant` |
| `Lijst van zaken Teakhout 29 te Zaandam-12.pdf` | 物品清单 | Teakhout 29 的包含/不包含清单；未发现重大风险。 | `low_risk` |
| `Veel gestelde vragen-6.pdf` | 销售 FAQ | 说明出价/销售条款；买方从交割日起承担成本/canon；强调自查义务。 | `buyer_due_diligence` |
| `Verkoopprocedure-7.pdf` | 销售流程 | 写明卖方在签署购房协议前不受约束；所有条件必须写入出价。 | `bid_process` |
| `f-13.pdf` | 住户规则 / VvE 规则 | 关于外墙改动、电梯、屋顶露台、摄像头、VvE 缴费和限制的规则。 | `use_restrictions` |
| `jaarverslag (1)-14.pdf` | 年报 | 维护储备 EUR 354,539.08，早期期间正结果 EUR 8,990.21；dotatie 约 EUR 78,750。 | `reserve_ok` |
| `jaarverslag-15.pdf` | 年报 / 中期报表 | 维护储备 EUR 429,485.30，但 exploitatie 计算结果 -EUR 29,099.65；中期视图中 2026 ledenbijdrage 低于早期预算。 | `reserve_ok_but_deficit` |
| `meetrapport_A_1658593_20260603062831-11.pdf` | NEN 测量 | 居住面积 **54.30 m2**；无其他室内面积。应按此计算每平米价格。 | `measurement_verify` |
| `notulen-4.pdf` | VvE 会议纪要 | 批准新 MJOP 和 2026 预算，dotatie EUR 120,000/年；讨论 25% 月供上涨、漏水/车库/平台工程，以及从流动性支付一次性主分割贡献。 | `fee_increase`, `planned_major_work`, `split_vve_entities`, `leakage_history` |

## 定价结论

Zaandam / Teakhout 比表面看起来复杂得多。它有不错的能源标签和看似合理的储备缓冲，但 erfpacht、独立车库 VvE、2026 月供上涨和车库工程让真实月成本不确定。不要在把所有 VvE + erfpacht 项目折算成月成本、并确认 25% 上涨是否最终落地之前出价。
