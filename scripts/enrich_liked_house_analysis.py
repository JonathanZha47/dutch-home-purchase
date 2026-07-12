#!/usr/bin/env python3
"""Enrich liked-house markdown files with Chinese analysis and scores."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
LIKED_DIR = ROOT / "liked-house"

DIMENSIONS = ["quality", "size", "groceries", "tennis", "transport", "financial"]

REGION_DUE_DILIGENCE = {
    "almere": [
        "确认到 Amsterdam Zuid/VU 的实际门到门时间，尤其是晚间和周末班次。",
        "确认是否需要长期持车；如果需要，把车位/停车/月度交通成本算入真实成本。",
    ],
    "weesp": [
        "确认火车站步行/骑车时间，以及高峰期到 Amsterdam Zuid 的换乘稳定性。",
        "重点检查老楼 VvE 的 MJOP、reservefonds 和能源改造计划。",
    ],
    "zaandam": [
        "逐字核实 erfpacht：canon、已买断到期日、买断成本、车库/储藏室是否单独权利。",
        "确认住宅 VvE 与车库/主分割 VvE 是否分开收费。",
    ],
    "nieuw-west": [
        "确认 Amsterdam erfpacht 是否已转 perpetual leasehold，以及未来 canon/买断选择。",
        "查 VvE 是否有电梯、外墙、屋顶、管道和能源升级的大额维护计划。",
    ],
    "amstelveen": [
        "确认是否 eigen grond；Amstelveen 老公寓也可能有复杂地权或分割权利。",
        "核实 tram/metro 到 Zuid 的门到门时间，以及电梯、储藏室、停车规则。",
    ],
    "bijlmer": [
        "核实 VvE reservefonds、MJOP、漏水/外墙/电梯维护和能源升级计划。",
        "白天和晚上各走一次周边，确认安全感、噪音、停车和到地铁路线。",
    ],
}

DEFAULT_BY_REGION = {
    "almere": {
        "scores": {"quality": 2.5, "size": 4.0, "groceries": 4.0, "tennis": 3.0, "transport": 3.5, "financial": 3.5},
        "pros": [
            "同预算下通常能换到更大面积或独栋/联排，适合作为空间优先的对照组。",
            "Almere Muziekwijk / centrum 一带生活配套相对完整，日常买菜不弱。",
            "如果是 eigen grond，财务结构会比 Amsterdam/Zaandam 的 erfpacht 简单很多。",
        ],
        "cons": [
            "对 Amsterdam Zuid/VU 属于 B-tier 通勤，门到门时间和班次稳定性要实测。",
            "很多性价比房源是 1980s/1990s，默认违反 2000 年后偏好，需要房况或价格补偿。",
            "转售/出租流动性通常弱于 Amsterdam/Amstelveen/Bijlmer 近地铁资产。",
        ],
        "verdict": "备选：空间换通勤，适合价格明显好时继续",
    },
    "weesp": {
        "scores": {"quality": 2.5, "size": 4.5, "groceries": 4.0, "tennis": 3.5, "transport": 4.0, "financial": 3.0},
        "pros": [
            "Weesp 火车连接好，生活氛围比纯郊区更稳定，长期自住体验不错。",
            "如果面积能到 85-95 m2，同预算的居住舒适度会明显强于 Amsterdam 小户型。",
            "Amsterdam 外围但仍有较强流动性，适合兼顾自住与未来出租。",
        ],
        "cons": [
            "老公寓常见能源标签、外墙、屋顶和电梯维护风险，不能只看挂牌价。",
            "VvE 月供和 reservefonds 需要逐项核实，否则真实月成本可能被低估。",
            "到 Zuid 通勤通常需要火车/换乘，体验优于 Almere 但不如 Bijlmer/Amstelveen 直达。",
        ],
        "verdict": "值得研究：交通和生活不错，但要先过 VvE/能效关",
    },
    "zaandam": {
        "scores": {"quality": 4.0, "size": 4.0, "groceries": 3.5, "tennis": 2.5, "transport": 4.0, "financial": 2.5},
        "pros": [
            "Zaandam 新一点的房源硬件和面积通常比 Amsterdam 同价位更好。",
            "去 Amsterdam Centraal 很快，若工作/生活重心不只在 Zuid，交通价值不错。",
            "Teakhout/Vurehout 这一类房源常带现代楼宇、储藏室/车位等实用配置。",
        ],
        "cons": [
            "Zaandam 房源最容易出现 erfpacht、车库权利、住宅 VvE/车库 VvE 分开等复杂财务。",
            "去 Zuid 往往要火车加换乘，通勤稳定性不如 Bijlmer/Amstelveen。",
            "如果 canon 很快恢复或买断成本高，低挂牌价会被真实成本吃掉。",
        ],
        "verdict": "备选：硬件可能好，但必须先拆清 erfpacht 和 VvE",
    },
    "nieuw-west": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 4.5, "tennis": 3.5, "transport": 4.0, "financial": 2.5},
        "pros": [
            "仍在 Amsterdam，生活配套、公共交通和未来出租需求明显强于远郊。",
            "Osdorpplein / Meer en Vaart / Pieter Calandlaan 一带买菜和日常服务便利。",
            "如果面积价格合适，可作为 Amsterdam 内部低总价方案。",
        ],
        "cons": [
            "很多楼龄偏老，质量分会被 2000 年后偏好硬性压低。",
            "Amsterdam erfpacht、VvE 大修、电梯/外墙/管道维护是核心风险。",
            "部分街区居住环境参差，需要实地确认晚间安全感和楼内管理。",
        ],
        "verdict": "谨慎：Amsterdam 流动性好，但老楼和地租要折价",
    },
    "amstelveen": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 4.5, "tennis": 4.5, "transport": 4.5, "financial": 2.5},
        "pros": [
            "到 Zuid/VU 和 Stadshart 的生活动线很好，自住舒适度强。",
            "Amstelveen 流动性和租售需求通常较稳，区域基本面优于多数远郊。",
            "买菜、网球、学校/公园等软性配套是这组房源最大优点。",
        ],
        "cons": [
            "同预算下楼龄往往偏老、面积不一定大，质量分容易低。",
            "老公寓 VvE、隔音、电梯、外墙和能源升级风险需要查文件。",
            "好区域会压缩财务安全边际，若价格接近上限则性价比下降。",
        ],
        "verdict": "值得研究：位置强，但要用价格弥补楼龄",
    },
    "bijlmer": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 3.5, "tennis": 3.5, "transport": 5.0, "financial": 3.5},
        "pros": [
            "地铁直达 Zuid/Centraal，是这批里通勤最强的板块。",
            "同预算面积通常明显大于 Amsterdam Zuid/West/Amstelveen，适合 WFH 和未来出租。",
            "如果能源至少 B、VvE 文件健康，综合性价比会很能打。",
        ],
        "cons": [
            "多数楼龄偏老，质量分默认受限，需要靠 VvE 健康度和折价补偿。",
            "部分楼栋有 social housing、公共空间管理、漏水/外墙/电梯维护风险。",
            "安全感和楼内管理必须实地验证，不能只看地铁距离。",
        ],
        "verdict": "值得重点筛：交通王者，但 VvE 文件决定能不能买",
    },
}

OVERRIDES: dict[str, dict[str, Any]] = {
    "almere-zeistpad-42.md": {
        "scores": {"quality": 2.0, "size": 5.0, "groceries": 3.5, "tennis": 3.0, "transport": 3.5, "financial": 3.5},
        "pros": [
            "114 m2 + 5 bedrooms 是这批里空间优势最明显的房源之一，未来家庭/出租分房都灵活。",
            "Energy label A 和太阳能板让 1981 年房子的运行成本风险降低不少。",
            "Funda 显示 volle eigendom，若契约确认无地租，财务结构比 Amsterdam/Zaandam 简单。",
        ],
        "cons": [
            "1981 年建，硬性违反 2000 年后偏好；质量分必须封顶，除非验房非常干净。",
            "Kluswoning 意味着装修预算、工期和隐藏问题风险都要预留。",
            "Ymere 条款可能限制出租/转售灵活性，流动性不如普通自由市场房源。",
        ],
        "verdict": "备选偏谨慎：空间很香，但只适合低价+验房通过",
        "red_flags": ["pre_2000_exception", "kluswoning", "ymere_conditions"],
    },
    "almere-louis-davidsstraat-250.md": {
        "scores": {"quality": 2.0, "size": 5.0, "groceries": 4.5, "tennis": 3.0, "transport": 3.5, "financial": 3.0},
        "pros": [
            "96 m2 maisonette、自有入口和花园，居住体验接近小联排。",
            "靠近 Almere Muziekwijk 配套和车站，Almere 里通勤/买菜相对顺。",
            "Funda 显示 VvE 有 reservefonds 和 MJOP，比完全未知的老楼更可审查。",
        ],
        "cons": [
            "1998 年建略低于 2000 年门槛，仍需作为例外处理。",
            "35+ 且无常住儿童规则会显著缩小未来买家/租客池。",
            "VvE 约 EUR 251/月不低，真实财务分会被月持有成本压低。",
        ],
        "verdict": "备选：面积很好，但居住规则让流动性打折",
        "red_flags": ["age_restriction", "pre_2000_exception", "verify_mjop"],
    },
    "almere-rachmaninovstraat-21.md": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 4.0, "tennis": 3.0, "transport": 3.5, "financial": 3.5},
        "pros": [
            "88 m2 三居 + 花园，适合自住，空间比 Amsterdam 同价位舒服。",
            "Muziekwijk 车站和商店相对近，是 Almere 中较实用的位置。",
            "Energy label A 和已更新厨卫降低短期装修压力。",
        ],
        "cons": [
            "1989 年建，仍然不符合 2000 年后偏好。",
            "395k 挂牌对 Almere 老房不算便宜，需要用成交价折扣保护安全边际。",
            "没有 VvE 分摊，屋顶、外墙、管线等维护风险都由自己承担。",
        ],
        "verdict": "备选：可看但必须用房龄压价",
        "red_flags": ["pre_2000_exception", "bouwkundige_keuring_needed"],
    },
    "almere-keizerstraat-28.md": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 4.5, "tennis": 3.5, "transport": 3.5, "financial": 3.0},
        "pros": [
            "83 m2 底层 + 朝南花园，使用感比普通公寓更好。",
            "靠 Almere Centrum/车站，买菜和公共交通便利度在 Almere 组里较强。",
            "325k 挂牌给了较多预算空间，可承受一定维修/文件风险。",
        ],
        "cons": [
            "1987 年建，且前房协房源条款复杂，必须要求折价。",
            "Funda VvE 描述与 checklist 存在矛盾，月供、reservefonds、MJOP 都要书面确认。",
            "可能有自住、反投机、ouderdom/asbest 条款，未来出租/转售灵活性受限。",
        ],
        "verdict": "谨慎：便宜但文件风险多，先查 VvE 再决定",
        "red_flags": ["vve_checklist_contradiction", "former_social_housing", "old_age_clause"],
    },
    "almere-prokofjevstraat-88.md": {
        "scores": {"quality": 2.5, "size": 4.0, "groceries": 4.0, "tennis": 3.0, "transport": 3.5, "financial": 3.5},
        "pros": [
            "Muziekwijk 音乐街区生活/车站便利度通常不错，适合作为 Almere 组核心对比。",
            "如果是 house 且 eigen grond，产权结构会比公寓 VvE 简单。",
            "Almere house 通常能给到更好的面积和储物空间。",
        ],
        "cons": [
            "关键字段缺失：价格、面积、建造年份、能效、产权都要补齐后重算。",
            "如为 1980s/1990s house，验房和维护预算会决定是否值得。",
            "B-tier 通勤，不能只看总价，需要算门到门时间。",
        ],
        "verdict": "待核实后再定：先补价格/面积/能效",
        "red_flags": ["missing_core_fields", "verify_ownership"],
    },
    "weesp-heemraadweg-101.md": {
        "scores": {"quality": 1.5, "size": 5.0, "groceries": 4.0, "tennis": 3.5, "transport": 4.0, "financial": 2.5},
        "pros": [
            "已看房文件显示约 94.6 m2，面积是很强的加分项。",
            "Weesp 交通和生活品质整体不错，比纯远郊更稳。",
            "如果价格足够低，可以作为大面积自住备选。",
        ],
        "cons": [
            "能源标签 C 直接冲突最低 B 的硬性要求，默认应视为 dealbreaker。",
            "文档显示储备金下降、MJOP 后续可能转负，VvE 风险高。",
            "节能改造和未来月供上涨都可能侵蚀财务优势。",
        ],
        "verdict": "谨慎/接近淘汰：除非能源规则可豁免且折价明显",
        "red_flags": ["energy_label_below_B", "future_reserve_gap", "vve_fee_pressure"],
    },
    "weesp-fort-heemstedestraat-83.md": {
        "scores": {"quality": 4.0, "size": 3.5, "groceries": 3.5, "tennis": 3.5, "transport": 4.0, "financial": 3.0},
        "pros": [
            "Fort/Weespersluis 一带通常更新、更规整，质量潜力优于 Weesp 老楼。",
            "Weesp 站连接 Amsterdam 好，区域比 Almere 更接近核心圈。",
            "若能效和 VvE 正常，会是自住舒适度较好的安静型选择。",
        ],
        "cons": [
            "价格、面积、VvE 和产权仍未核实，财务分只能先保守。",
            "如果离 Weesp station 较远，实际通勤会被骑车/公交前置时间拉长。",
            "新社区流动性不错但总价可能偏高，需要控制 overbid。",
        ],
        "verdict": "值得补资料：可能是 Weesp 组更干净的选择",
        "red_flags": ["missing_core_fields", "verify_vve"],
    },
    "zaandam-teakhout-29.md": {
        "scores": {"quality": 4.0, "size": 4.0, "groceries": 3.5, "tennis": 2.5, "transport": 4.0, "financial": 2.0},
        "pros": [
            "已看房文件显示房子较新、能源表现好，硬件层面有吸引力。",
            "Zaandam 到 Amsterdam Centraal 快，非 Zuid 单点通勤时交通不错。",
            "如果带车位/储藏室，实用性会强于普通 Amsterdam 老公寓。",
        ],
        "cons": [
            "文档显示 erfpacht 和住宅/车库多 VvE 结构复杂，是这套最大风险。",
            "VvE 月供上涨、储备和多分割关系会让真实成本难算。",
            "如果 canon 或买断成本高，低挂牌价会变成假便宜。",
        ],
        "verdict": "备选偏谨慎：硬件好，但 erfpacht/VvE 必须拆清",
        "red_flags": ["erfpacht_trap", "multiple_vve", "fee_increase"],
    },
    "bijlmer-boeninlaan-389.md": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 3.5, "tennis": 3.0, "transport": 5.0, "financial": 2.5},
        "pros": [
            "Bijlmer metro 通勤强，去 Zuid/Centraal 的效率是核心优势。",
            "能源标签 B 满足最低门槛，至少没有像 C 标签那样直接出局。",
            "如果面积/价格合适，出租需求和自住实用性都不错。",
        ],
        "cons": [
            "已看房文件显示 VvE 规模大、2026 预算上涨、维护储备压力明显。",
            "会议纪要提到漏水/外墙问题线索，未来特别维修风险不能忽略。",
            "区域和楼栋管理需要实地确认，不能只看地铁近。",
        ],
        "verdict": "谨慎备选：交通强，但 VvE 风险要求明显折价",
        "red_flags": ["large_vve", "fee_increase", "leakage_history", "future_reserve_gap"],
    },
    "bijlmer-haardstee-29.md": {
        "scores": {"quality": 2.5, "size": 5.0, "groceries": 3.5, "tennis": 3.5, "transport": 5.0, "financial": 5.0},
        "pros": [
            "91 m2 三居复式，同预算空间最大，WFH 和未来出租都很实用。",
            "地铁直达 Amsterdam Zuid/Centraal，可省车，通勤分是满分级别。",
            "地租已付至 2031，短期没有 canon 现金流压力；若买断金额可控，财务结构仍然能打。",
            "挂牌和模型成交价都较低，真实总成本在当前预算内有明显余地。",
        ],
        "cons": [
            "1981 年建，违反 2000 年后偏好；需要明确接受这个妥协。",
            "VvE 约 EUR 264/月偏高，且看房文档显示未来节能改造/维护压力。",
            "周边 social housing 和楼栋公共空间管理需要实地确认。",
            "老楼隔音、漏水、外墙和能源升级风险不能按新房逻辑看。",
        ],
        "verdict": "值得看房（务实派：空间+交通，妥协房龄）",
        "red_flags": ["pre_2000_exception", "high_vve_fee", "verify_mjop_and_reservefonds", "energy_upgrade_watch"],
    },
}

STREET_OVERRIDES = {
    "dijkgraafplein": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 5.0, "tennis": 3.5, "transport": 4.0, "financial": 2.5},
        "pros": [
            "Dijkgraafplein/Osdorpplein 生活配套强，买菜、商店、tram/bus 都方便。",
            "Amsterdam 内部资产，未来出租/转售流动性强于远郊。",
            "如果总价低于 Amstelveen 同面积房源，性价比有机会。",
        ],
        "cons": [
            "大概率是老楼/大型 VvE，质量、隔音、电梯和外墙维护要严查。",
            "Amsterdam erfpacht 是核心财务不确定性，必须查 perpetual leasehold 状态。",
            "区域居住环境参差，晚间安全感和楼内管理要实地验证。",
        ],
        "verdict": "谨慎：配套强，但老楼+erfpacht 要折价",
        "red_flags": ["verify_erfpacht", "large_vve", "older_building"],
    },
    "ladogameerhof": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 4.5, "tennis": 3.5, "transport": 4.0, "financial": 2.5},
        "pros": [
            "靠 Nieuw-West 配套和公共交通，生活便利性不错。",
            "Amsterdam 内部位置带来较好流动性。",
            "如果楼层/户型好，居住体验可能优于 Dijkgraafplein 更嘈杂位置。",
        ],
        "cons": [
            "老楼概率高，VvE、管道、电梯和能源改造风险要查。",
            "产权/erfpacht 未核实前，财务分不能给高。",
            "周边环境需要现场确认，尤其是楼内公共区域。",
        ],
        "verdict": "谨慎备选：先查 erfpacht 和 VvE 文件",
        "red_flags": ["verify_erfpacht", "verify_vve", "older_building"],
    },
    "pieter-calandlaan": {
        "scores": {"quality": 2.5, "size": 3.5, "groceries": 4.5, "tennis": 3.5, "transport": 4.0, "financial": 2.5},
        "pros": [
            "Pieter Calandlaan 交通和生活配套不错，Amsterdam 内部流动性较好。",
            "如果靠近 tram/metro/bus，日常去 Zuid 和市区都还算顺。",
            "有机会在 Amsterdam 内拿到比核心区更大的面积。",
        ],
        "cons": [
            "临主干道可能有噪音，楼层和朝向很关键。",
            "仍需核实 Amsterdam erfpacht、VvE 和能源标签。",
            "如果价格接近 450k，上述风险会显著压低性价比。",
        ],
        "verdict": "可研究但谨慎：交通配套好，噪音/地租要查",
        "red_flags": ["road_noise_watch", "verify_erfpacht", "verify_vve"],
    },
    "leksmondhof": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 3.5, "tennis": 3.5, "transport": 5.0, "financial": 3.0},
        "pros": [
            "Zuidoost 地铁优势强，去 Zuid/Centraal 都方便。",
            "Leksmondhof 这类房源通常面积比 Amsterdam 西/南同价位大。",
            "如果 VvE 健康且能源 B+，会是务实型高性价比选择。",
        ],
        "cons": [
            "老楼/大 VvE 风险是主线，必须看 MJOP 和 reservefonds。",
            "楼内公共空间、邻里安全感和噪音需要实地走访。",
            "产权/erfpacht 未核实前，财务安全边际不能假设太好。",
        ],
        "verdict": "备选：交通面积都好，等 VvE 文件定生死",
        "red_flags": ["large_vve", "verify_erfpacht", "older_building"],
    },
    "barbusselaan": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 3.5, "tennis": 3.0, "transport": 5.0, "financial": 3.0},
        "pros": [
            "地铁通勤强，是 Bijlmer 组共同优势。",
            "若面积足够大，适合 WFH 和未来出租。",
            "价格若低于 Amsterdam 其他片区，可以用折价抵消楼龄。",
        ],
        "cons": [
            "与 Boeninlaan 同片区，要高度关注 VvE 维护和外墙/漏水问题。",
            "楼栋管理和周边安全感需要实地确认。",
            "如果能源低于 B 或 VvE 月供偏高，应直接降级。",
        ],
        "verdict": "谨慎备选：先拿 VvE 文件再约看",
        "red_flags": ["verify_vve", "older_building", "area_safety_check"],
    },
    "fleerde": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 3.0, "tennis": 3.0, "transport": 4.5, "financial": 3.0},
        "pros": [
            "Zuidoost 通勤仍然强，整体交通分高。",
            "Fleerde 一带如果价格低，面积/总价可能有优势。",
            "适合作为 Bijlmer 组低价对照样本。",
        ],
        "cons": [
            "相对更需要核实街区安全感、楼内管理和公共空间状态。",
            "老楼 VvE、能源和维护风险不能省略。",
            "如果离 metro 步行距离较长，交通优势会被削弱。",
        ],
        "verdict": "谨慎：价格要足够低才值得看",
        "red_flags": ["area_safety_check", "verify_vve", "older_building"],
    },
    "bijlmerdreef": {
        "scores": {"quality": 2.0, "size": 4.0, "groceries": 3.5, "tennis": 3.5, "transport": 5.0, "financial": 3.0},
        "pros": [
            "Bijlmerdreef 通常交通非常强，近 metro 是核心买点。",
            "面积/价格组合有机会优于 Amsterdam 其他片区。",
            "出租需求相对稳，适合务实型资产。",
        ],
        "cons": [
            "临主路/高架/公共交通可能有噪音，朝向和楼层重要。",
            "老楼大 VvE 风险仍在，必须看 MJOP、reservefonds、会议纪要。",
            "区域安全感和楼内管理不能跳过。",
        ],
        "verdict": "备选：交通很强，文件和现场决定是否升级",
        "red_flags": ["road_noise_watch", "large_vve", "area_safety_check"],
    },
    "teakhout": {
        "scores": {"quality": 4.0, "size": 4.0, "groceries": 3.5, "tennis": 2.5, "transport": 4.0, "financial": 2.0},
        "pros": [
            "Teakhout/Murano 类型房源硬件通常较新，居住品质优于老楼。",
            "Zaandam 到 Amsterdam Centraal 很快，通勤到市中心不错。",
            "如果带车位/储藏室，会有实用加分。",
        ],
        "cons": [
            "同小区/同类型要重点警惕 erfpacht 与车库/住宅 VvE 分离。",
            "VvE 月供上涨和未来维护储备会直接影响真实财务。",
            "去 Zuid 需要换乘，交通优势不如 Bijlmer/Amstelveen。",
        ],
        "verdict": "备选偏谨慎：硬件好，但先算清地租",
        "red_flags": ["erfpacht_trap", "multiple_vve", "verify_mjop"],
    },
    "vurehout": {
        "scores": {"quality": 3.5, "size": 4.0, "groceries": 3.0, "tennis": 2.5, "transport": 4.0, "financial": 2.5},
        "pros": [
            "Vurehout/Vurehout 周边通常能用较低总价换较大面积。",
            "Zaandam 到 Amsterdam Centraal 快，工作地点灵活时价值不错。",
            "如果是 house 且产权清晰，可减少公寓 VvE 复杂度。",
        ],
        "cons": [
            "Zaandam 同类房源已有 erfpacht trap 先例，必须查 canon/买断成本。",
            "买菜和网球便利度一般，日常体验不如 Amstelveen/Nieuw-West。",
            "到 Zuid 换乘成本高，需要把通勤真实时间算进去。",
        ],
        "verdict": "备选：空间可以，但财务和通勤要折价",
        "red_flags": ["verify_erfpacht", "commute_tradeoff"],
    },
    "duivelandselaan": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 4.5, "tennis": 4.5, "transport": 4.5, "financial": 2.5},
        "verdict": "值得研究但谨慎：位置好，楼龄/VvE 要压价",
        "red_flags": ["older_building", "verify_vve"],
    },
    "schouwenselaan": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 4.5, "tennis": 4.5, "transport": 4.5, "financial": 2.5},
        "verdict": "值得研究但谨慎：Amstelveen 配套强，先核 VvE",
        "red_flags": ["older_building", "verify_vve"],
    },
    "tholenseweg": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 4.5, "tennis": 4.5, "transport": 4.5, "financial": 2.5},
        "verdict": "谨慎备选：位置加分，财务安全边际待确认",
        "red_flags": ["older_building", "verify_vve"],
    },
    "bos-en-vaartlaan": {
        "scores": {"quality": 2.5, "size": 3.5, "groceries": 4.0, "tennis": 4.5, "transport": 4.0, "financial": 2.5},
        "verdict": "谨慎：安静自住潜力有，但价格/面积要补齐",
        "red_flags": ["verify_vve", "verify_energy_label"],
    },
    "rembrandtweg": {
        "scores": {"quality": 2.0, "size": 3.0, "groceries": 5.0, "tennis": 4.5, "transport": 4.5, "financial": 2.5},
        "verdict": "备选：Stadshart 配套强，但通常面积/楼龄吃亏",
        "red_flags": ["older_building", "price_premium"],
    },
    "zonnesteinhof": {
        "scores": {"quality": 2.0, "size": 3.5, "groceries": 4.5, "tennis": 4.5, "transport": 4.5, "financial": 2.5},
        "verdict": "谨慎备选：区域好，先看 VvE 与能效",
        "red_flags": ["older_building", "verify_vve"],
    },
}


def parse_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"{path} missing frontmatter")
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def score_total(scores: dict[str, Any]) -> float:
    return round(sum(float(scores[key]) for key in DIMENSIONS), 1)


def verdict_from_total(total: float, current: str) -> str:
    if current and current != "待补充分析":
        return current
    if total >= 24:
        return "强烈推荐"
    if total >= 21:
        return "值得看房"
    if total >= 18:
        return "备选"
    if total >= 15:
        return "谨慎"
    return "淘汰"


def match_street_override(filename: str) -> dict[str, Any] | None:
    for key, value in STREET_OVERRIDES.items():
        if key in filename:
            return value
    return None


def merge_unique(first: list[str], second: list[str]) -> list[str]:
    out = []
    for item in first + second:
        if item and item not in out:
            out.append(item)
    return out


def enriched_analysis(path: Path, listing: dict[str, Any]) -> dict[str, Any]:
    region = listing.get("region", "")
    base = DEFAULT_BY_REGION[region]
    update = {**base}
    update.update(match_street_override(path.name) or {})
    update.update(OVERRIDES.get(path.name, {}))

    scores = dict(update["scores"])
    scores["total"] = score_total(scores)
    listing["scores"] = scores
    listing["analysis_confidence"] = "medium" if path.name in OVERRIDES else "preliminary"
    listing["analysis_basis"] = (
        "基于本地已有 listing/VvE 文档和 Funda 已核实字段。"
        if path.name in OVERRIDES
        else "基于地址、区域、房型和买方评分规则的临时分析；价格/面积/产权/VvE 补齐后需重算。"
    )
    listing["pros"] = update.get("pros", base["pros"])
    listing["cons"] = update.get("cons", base["cons"])
    listing["verdict"] = verdict_from_total(scores["total"], update.get("verdict", listing.get("verdict", "")))
    listing["status"] = "analyzed_preliminary"

    vve = listing.setdefault("vve_analysis", {})
    red_flags = update.get("red_flags", [])
    existing_flags = vve.get("red_flags") or []
    vve["red_flags"] = merge_unique(red_flags, existing_flags)
    if not vve.get("notes") or "待核实" in str(vve.get("notes")):
        vve["notes"] = "先按区域和房型做初筛；出价前必须读取 VvE 年报、MJOP、reservefonds、会议纪要和保险。"

    if listing.get("object_type") == "house":
        vve["notes"] = "House 不依赖公寓 VvE；重点改为 bouwkundige keuring、屋顶/外墙/管线、地权和市政限制。"
        vve["red_flags"] = [flag for flag in vve["red_flags"] if flag != "verify_vve"]

    return listing


def fmt_value(value: Any, suffix: str = "") -> str:
    if value in (None, ""):
        return "待核实"
    if isinstance(value, int) and suffix == " EUR":
        return f"EUR {value:,}"
    return f"{value}{suffix}"


def markdown_body(listing: dict[str, Any]) -> str:
    scores = listing["scores"]
    score_rows = "\n".join(
        f"| {label} | {scores[key]} | {note} |"
        for key, label, note in [
            ("quality", "房屋质量", "看建造年份、能效、硬件和是否违反 2000+ 偏好"),
            ("size", "面积", "按当前已知或区域典型面积做临时判断"),
            ("groceries", "买菜", "按街区配套和区域经验评分"),
            ("tennis", "网球", "按到可用球场的便利度估计"),
            ("transport", "交通", "按 buyer profile 的 S/A/B 通勤 tier"),
            ("financial", "真实财务", "含挂牌、VvE、erfpacht、买断和月持有成本风险"),
        ]
    )
    pros = "\n".join(f"- {item}" for item in listing.get("pros", []))
    cons = "\n".join(f"- {item}" for item in listing.get("cons", []))
    vve = listing.get("vve_analysis") or {}
    flags = "\n".join(f"- `{flag}`" for flag in vve.get("red_flags", [])) or "- 暂无明确红旗，但仍需文件核实。"
    erf = listing.get("erfpacht") or {}
    due = REGION_DUE_DILIGENCE.get(listing.get("region", ""), [])
    due_items = merge_unique(
        due,
        [
            "核实 Funda 当前状态、挂牌价、面积、建造年份、energy label 和交付条件。",
            "核实产权：volle eigendom / erfpacht、canon、paid-until date、perpetual leasehold、买断金额。",
            "如果是公寓，索要 splitsingsakte、VvE jaarverslag、MJOP、reservefonds、notulen 和 opstalverzekering。",
            "用补齐后的价格/面积/产权重新运行 Level 1 CBS 估价和财务分。",
        ],
    )
    due_md = "\n".join(f"- {item}" for item in due_items)

    return f"""# {listing.get('address')}, {listing.get('city')}

## 一句话结论

{listing.get('verdict')}。{listing.get('analysis_basis')}

## 关键事实

- Funda: {listing.get('funda_url')}
- 区域: {listing.get('region')}
- 房型: {listing.get('object_type')}
- 挂牌价: {fmt_value(listing.get('price_asking'), ' EUR') if listing.get('price_asking') else '待核实'}
- 面积: {fmt_value(listing.get('living_area_m2'), ' m2')}
- 卧室: {fmt_value(listing.get('bedrooms'))}
- 建造年份: {fmt_value(listing.get('build_year'))}
- Energy label: {fmt_value(listing.get('energy_label'))}
- VvE/月: {fmt_value(listing.get('vve_monthly'), ' EUR') if listing.get('vve_monthly') else '待核实'}

## 六维打分

| 维度 | 分数 | 说明 |
|---|---:|---|
{score_rows}
| **总分** | **{scores['total']} / 30** | 临时可比较分数，补齐事实后更新 |

## 产权与真实财务

- 产权/地租: {erf.get('summary') or erf.get('type') or '待核实'}
- 预估成交价: {fmt_value(listing.get('price_estimated_bid'), ' EUR') if listing.get('price_estimated_bid') else '待核实'}
- 真实总成本: {fmt_value(listing.get('true_cost_eur'), ' EUR') if listing.get('true_cost_eur') else '待核实'}
- 月持有成本: {fmt_value(listing.get('monthly_carry_eur'), ' EUR') if listing.get('monthly_carry_eur') else '待核实'}

## VvE / Maintenance

{vve.get('notes') or '待核实。'}

风险标签:
{flags}

## 优点

{pros}

## 缺点

{cons}

## 出价前必须核实

{due_md}

## 决策建议

- 如果补齐事实后总分仍 >= 21，进入看房/索取文件队列。
- 如果 energy label < B、建造年份 < 2000 且没有明显折价，默认降级。
- 如果 erfpacht 或 VvE 文件无法解释清楚，宁愿跳过。
"""


def write_markdown(path: Path, listing: dict[str, Any]) -> None:
    frontmatter = yaml.safe_dump(listing, allow_unicode=True, sort_keys=False).strip()
    path.write_text(f"---\n{frontmatter}\n---\n\n{markdown_body(listing)}", encoding="utf-8")


def main() -> None:
    count = 0
    for path in sorted(LIKED_DIR.glob("*.md")):
        listing, _ = parse_markdown(path)
        enriched = enriched_analysis(path, listing)
        write_markdown(path, enriched)
        count += 1
    print(f"Enriched {count} liked-house markdown files")


if __name__ == "__main__":
    main()
