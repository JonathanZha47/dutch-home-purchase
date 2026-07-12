# Heemraadweg 101 Weesp - 文档审查

审查日期：2026-07-04  
来源目录：`viewing/weesp/move-documents/`  
容器文件：`viewing/weesp/move-documents.zip` 包含同样的 12 份已解压文件。  
总体风险：**高（High）**  
决策影响：面积很强，但能源标签 C 与买方硬性要求冲突；VvE 的节能改造和 MJOP 资金路径也不够舒服。

## 关键发现

- **能源标签 C：** 官方能源标签为 **C / 201.59 kWh/m2**，有效期 2026-2036。除非明确放弃最低 B 的硬性要求，否则不符合 buyer profile。
- **面积大：** 测量报告显示 **94.60 m2 woonoppervlak**。面积是明显优点，但报告文字里有 stahoogte 相关排除说明，需要留意。
- **储备金显著下降：** 2025 jaarrekening 显示 onderhoudsreserve 为 **EUR 198,526.01**，低于前期 **EUR 314,479.36**，主要因为 **EUR 190,000** 阳台栏杆/扶手工程入账。
- **MJOP 未来转负：** 调整版 MJOP 储备预测在 2034 年左右及之后周期出现负数，如无额外资金会有缺口。
- **节能改造路径：** VvE 文件讨论节能场景和可能的 Nationaal Warmtefonds 贷款。这是未来月成本风险。
- **Splitsingsakte 不可读：** 22 页文件无可抽取文本。需要公证员确认 VvE/私人边界，尤其节能文件称外墙、地板、屋顶、窗框、供暖和通风属于 VvE/共享事项。

## 出价前必须确认

- 你是否愿意为这套房放弃能源标签 B 的硬性规则。
- 当前准确 VvE 月供，以及是否有与 MJOP/节能改造相关的预期上涨。
- 阳台栏杆工程是否已完成，是否还有未筹资工程。
- VvE 是否已批准或即将批准 Warmtefonds 贷款。
- 公证员审查不可读的 splitsingsakte。

## 单文件摘要

| 文件 | 类型 | 有用信息 | 风险标签 |
|---|---|---|---|
| `Heemraadweg 101 Weesp - Energielabel-12.pdf` | 能源标签 | 官方标签 C，201.59 kWh/m2，无太阳能板。与买方标准冲突。 | `energy_label_below_B` |
| `Heemraadweg 101 Weesp - Lijst van Zaken-1.pdf` | 物品清单 | 包含/不包含物品清单；抽取文本中未发现重大风险。 | `low_risk` |
| `Heemraadweg 101 Weesp - Meetrapport-2.pdf` | NEN 测量 | Woonoppervlak **94.60 m2**；面积很好。报告说明 1.50m 以下 stahoogte 等排除规则。 | `measurement_ok` |
| `Heemraadweg 101 Weesp - Vragenlijst deel B-3.pdf` | 卖家问卷 | 抽取文本中，卖家对纠纷、潮湿、屋顶漏水、地基问题、石棉等回答否；注明机械通风是共享/VvE 事项。 | `seller_disclosure_check` |
| `Verduurzaming_VVE_2025-4.pdf` | 节能改造提案 | 讨论节能场景、可能通过 Nationaal Warmtefonds 贷款直接执行，以及外墙/地板/屋顶/窗框/供暖/通风归 VvE。 | `verduurzaming_loan_watch`, `fee_increase_watch` |
| `VvE Heemraadweg 101-809 - Begroting-5.pdf` | VvE 预算 | 2026 VvE 预算列出 CV、电梯、hydrofoor、消防管道和日常维护费用；用于核实准确月供。 | `vve_fee_verify` |
| `VvE Heemraadweg 101-809 - Jaarrekening 2025-6.pdf` | 年度账目 | Onderhoudsreserve 降至 EUR 198,526.01；2025 正结果 EUR 12,905.25；EUR 190,000 阳台栏杆工程计入储备。 | `reserve_spend`, `planned_major_work` |
| `VvE Heemraadweg 101-809 - MJOP (aangepast)-7.pdf` | 调整版 MJOP | 储备预测显示未来数年低于零，包括 2034 年左右及之后周期。 | `future_reserve_gap` |
| `VvE Heemraadweg 101-809 - MJOP-8.pdf` | 完整 MJOP | 48 年维护计划。关键循环成本包括外墙/窗户/油漆和屋顶/屋面项目。 | `planned_major_work`, `future_reserve_gap` |
| `VvE Heemraadweg 101-809 - Notulen 13 mei 2025-10.pdf` | VvE 会议纪要 | 讨论 2024 负结果处理、新 MJOP、MJOP 内外工程、2025 预算上涨和储备使用。 | `reserve_spend`, `fee_increase_watch` |
| `VvE Heemraadweg 101-809 - Notulen 3 juni 2025-9.pdf` | VvE 会议纪要 | 2024 负结果 EUR 11,327.99 从储备扣除；部分成本本应归入储备项；MVGM 被任命为 reserve fund manager。 | `reserve_spend`, `accounting_reclassification` |
| `VvE Heemraadweg 101-809 - Splitsingsakte-11.pdf` | Splitsingsakte | 22 页，无可抽取文本。需要公证员/人工审查。 | `machine_unreadable_scan`, `notary_verify` |
| `move-documents.zip` | 压缩包 | 包含上述 12 份 Weesp 文件；已审查解压后的文件。 | `container_reviewed` |

## 定价结论

面积是最大优点，但能源标签 C 和节能融资风险很重。只有在价格足够有吸引力、能覆盖未来能源/VvE 成本，并且你愿意放弃能源标签硬规则时，才值得继续。
