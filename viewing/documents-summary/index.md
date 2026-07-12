# 看房文件审查总览

审查日期：2026-07-09（Bos en Vaartlaan 增补）；2026-07-08（Concourslaan、Venspolder 增补）；其余 2026-07-04  
来源目录：`dutch-home-purchase/viewing/`  
方法：PDF 使用 `pdftotext` 抽取文本，图片使用 `tesseract` OCR，然后人工做 VvE / MJOP 风险审查。  

本次覆盖：122 个内容文件（含 Concourslaan 15 份 PDF、Venspolder 9 份 PDF、Bos en Vaartlaan 35 份 PDF）；另包含 `weesp/move-documents.zip` 作为容器文件。该 zip 内的 Weesp 文件已解压并审查。

## 子看板：阿姆斯特丹周边社区研究

这个子看板把 40 万欧预算下的区域选择、通勤、社区背景和投资属性单独拆出来，作为 VvE / MJOP 文件审查之外的区域判断入口。

- [打开阿姆周边买房综合看板](../../dashboard/amsterdam-region-buying-2026.html)
- [社区深度页目录](../../dashboard/community/)

| 区域 | 看点 | 社区深度页 |
|---|---|---|
| Almere | 面积换通勤，预算效率高，但社区差异和出租限制要逐套看 | [almere.html](../../dashboard/community/almere.html) |
| Weesp | 小城稳定型，火车通勤强，供应少，投资更偏保守 | [weesp.html](../../dashboard/community/weesp.html) |
| Zaandam | 到 Amsterdam CS 很强，但 erfpacht 和 VvE 结构需要扣分 | [zaandam.html](../../dashboard/community/zaandam.html) |
| Amsterdam Nieuw-West | 位置属性强，但不同 buurt 的居住和投资逻辑差异很大 | [nieuw-west.html](../../dashboard/community/nieuw-west.html) |
| Amstelveen | 近 Zuid / VU 和租客池是优势，预算内通常牺牲面积或楼龄 | [amstelveen.html](../../dashboard/community/amstelveen.html) |
| Bijlmer / Zuidoost | 预算内面积和通勤组合强，但必须按 buurt、楼栋、VvE 精筛 | [bijlmer.html](../../dashboard/community/bijlmer.html) |
| Gaasperplas / Nellestein | 绿地湖区体验好，重点看大面积、车位和 VvE 质量 | [gaasperplas.html](../../dashboard/community/gaasperplas.html) |
| Hoofddorp | 省心通勤型，可作为本轮 Amsterdam 周边区域基准 | [hoofddorp.html](../../dashboard/community/hoofddorp.html) |

## 总体风险排序

| 房源目录 | 总体风险 | 主要原因 | 摘要文件 |
|---|---:|---|---|
| `bos-en-vaartlaan45` | 中高 | 能源 C、1965 年老楼、VvE 建筑分项储备为负、MJOP 集中维护、2025 月费上涨和取暖分摊风险 | [bos-en-vaartlaan-45-amstelveen.md](bos-en-vaartlaan-45-amstelveen.md) |
| `concorselaan-hoofddorp centurm` | 中高 | 三层 VvE 财务混乱、2024 年报未通过、MJOP 远期支出、88 号商铺漏水、文件地址不一致 | [concorselaan-86-hoofddorp.md](concorselaan-86-hoofddorp.md) |
| `venspolder` | 中 | A 标签、2006 年、带车位、erfpacht 似已永久买断；但缺少 jaarrekening/MJOP/notulen，卖家披露浴室霉斑、出租状态和 warmtenet 月租需核实 | [venspolder-anna-blamansingel-19.md](venspolder-anna-blamansingel-19.md) |
| `Hoofdweg 854V Hoofddorp` | 中 | NEN 实测室内面积偏小，卖家披露潮湿但未写细节，2030 年 MJOP 维护支出集中 | [hoofdweg-854v-hoofddorp.md](hoofdweg-854v-hoofddorp.md) |
| `bijlmer` | 高 | 大型老 VvE，已有漏水/外墙疑虑，2026-2027 年油漆和屋顶大修，长期 MJOP 储备金转负 | [bijlmer-boeninlaan-389.md](bijlmer-boeninlaan-389.md) |
| `hardstee29` | 高 | 1980s 小区，VvE 月费上升，节能改造方案未定，MJOP 多个年份储备金为负 | [hardstee29.md](hardstee29.md) |
| `weesp` | 高 | 能源标签 C 不符合硬性偏好，阳台/外墙/节能路径较重，MJOP 未来储备金转负 | [weesp-heemraadweg-101.md](weesp-heemraadweg-101.md) |
| `zaandam` | 高 | Erfpacht、住宅/车库多 VvE、漏水和车库工程、2026 年月费上涨未完全明确、旧 MJOP 储备缺口 | [zaandam-teakhout-29.md](zaandam-teakhout-29.md) |

## 跨房源红旗

- `planned_major_work`：几个大型/老 VvE 都有较大的 MJOP 工程；Concourslaan、Bijlmer、Haardstee、Weesp、Zaandam 需要特别谨慎。
- `future_reserve_gap`：Concourslaan（MJOP Version A）、Bijlmer、Haardstee、Weesp、Zaandam 的 MJOP 模型都出现储备金转负，或依赖未来提高月供。
- `split_vve_entities`：Concourslaan 和 Zaandam 都有主/子 VvE 或多实体结构，真实月成本与账目责任需额外核实。
- `special_assessment_or_fee_increase`：Concourslaan 2026 预算涨约 6% 且计划 TOP 脱碳；Zaandam 有 25% 月费上涨讨论以及车库/主分割 VvE 分摊；Weesp 和 Haardstee 的节能/维护资金路径也可能推高月成本。
- `measurement_mismatch`：Concourslaan 文件夹名/测量报告/官方文件地址不一致（88 vs 8 vs 86），出价前必须书面确认标的。
- `energy_label_below_B`：Weesp 是能源标签 C，除非明确放弃硬性要求，否则不符合 buyer profile。
- `machine_unreadable_scan`：Concourslaan splitsingsakte、Hardstee 和 Weesp 的 splitsingsakte，以及 Zaandam 的 kadastrale legger 无法完整抽取文本。应视为“未实质审查”，需要公证员或 aankoopmakelaar 核实关键条款。
- `missing_vve_core_docs`：Venspolder 只有 checklist，没有 jaarrekening、begroting、MJOP、notulen；暂不能判断 reserve 是否足够。
- `rental_status_verify`：Venspolder 卖家问卷当前使用写 Verhuur，出价前必须确认空置交付和无租客权利。
- `reserve_subfund_negative`：Bos en Vaartlaan 的 VvE 建筑/油漆/吊篮储备为负，未来大修资金路径必须问清。
- `blokverwarming_cost_risk`：Bos en Vaartlaan 是集中供暖 + Techem 分摊，月预付不是最终真实账单。

## 已覆盖文件

| 目录 | 已审查文件 |
|---|---:|
| `bos-en-vaartlaan45` | 35 份 PDF |
| `concorselaan-hoofddorp centurm` | 15 份 PDF |
| `Hoofdweg 854V Hoofddorp` | 12 份当前文件，加旧版本地 `documents-summary.md` |
| `venspolder` | 9 份 PDF |
| `bijlmer` | 6 份文件 |
| `hardstee29` | 17 份文件 |
| `weesp/move-documents` | 12 份文件，加 zip 容器 |
| `zaandam` | 16 份文件 |

## 出价纪律

这些总结是出价前风险清单，不是法律意见。出价前至少要问清：

1. 该套房的最新 VvE 月供，以及是否有独立车位/车库权利和单独费用。
2. 已批准工程之后的最新储备金余额。
3. 是否已有或预期会有一次性追加缴费、VvE 贷款、延迟生效的月供上涨。
4. 漏水、潮湿、外墙、屋顶问题的书面状态。
5. 让 aankoopmakelaar / 公证员确认 erfpacht、splitsing、私人/公共边界和使用限制。
