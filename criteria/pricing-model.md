# Level 1 成交价预估模型

基于 **免费 CBS 数据** + 区域 overbid 系数 + 街区质量调整。不需要购买 Kadaster CSV。

## 公式

```
CBS 公允价 = 市政年均成交价 × (面积 / 85m²) × 街区系数 × 能效系数 × 房龄系数

若 公允价 ≥ 挂牌价:
  预估成交 = 挂牌价 + (公允价 - 挂牌价) × 竞争系数
否则:
  预估成交 = 挂牌价 × (1 + 调整后 overbid%)
```

**真实总成本** = 预估成交 + Erfpacht 买断（如适用）+ ~€6k KK

## 数据来源（免费）

| 数据 | CBS 表 | 内容 |
|------|--------|------|
| 市政年均成交价 | [83625ENG](https://opendata.cbs.nl/ODataApi/OData/83625ENG) | Amsterdam、Haarlemmermeer、Zaanstad、Gouda 等 |
| 全国月度均价/指数 | [85773ENG](https://opendata.cbs.nl/ODataApi/OData/85773ENG) | 宏观趋势参考 |

刷新本地缓存：

```bash
python3 scripts/fetch_cbs_market.py
```

## 关键限制（务必了解）

1. **CBS 市政均价是全市平均**，含运河豪宅也含 Bijlmer。必须用 `neighborhood_factor` 打折（如 Bijlmer Hoptille ≈ 0.58）。
2. **CBS 没有单笔成交明细**，不能做法拍式 comparable sales（那是 Level 2 Kadaster 付费）。
3. **CBS 均价 ≠ 单价指数** — 大户型成交月会拉高均价，不代表涨价。
4. 模型输出带 **confidence**；街区 profile 越具体，置信度越高。

## 街区 Profile

编辑 `config/regional-pricing.json`：

- `postcode_profiles` — 邮编前缀 → profile 名
- `neighborhood_profiles` — profile 的街区系数、overbid 调整、竞争系数
- `tag_overbid_adjustments` — 如 `social_housing_nearby: -1.5%`

## 命令

```bash
# 单套估算
python3 scripts/estimate_price.py --file listing.json --pretty

# 全部重算
python3 scripts/reestimate_all.py
```

## 人工 override

在 listing JSON 中设置 `"skip_price_estimate": true` 并手动填 `price_estimated_bid`，
或看房后告诉 agent 你的判断（如「这套 35 万能拿下」）以微调 profile。
