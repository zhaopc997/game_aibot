#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原神全维度数值体系入库与初始化脚本
数据源：米哈游原神官方观测枢 (HoYoWiki) & 官方底层战斗数据架构
包含：
1. 角色全量成长属性 (1-90级14阶段生命/攻击白值/防御)、突破专有属性、技能1-10(13)倍率与机制、固有天赋、命之座1-6、突破材料、推荐配装、底层机制(ICD/附着/削韧/生命之契/夜魂/卡肉)
2. 武器全量数值 (1-90级白值曲线、副词条、1-5阶精炼、突破消耗)
3. 圣遗物套装属性与词条规格 (2件套、4件套、主词条池、副词条4档强化机制)
4. 战斗底层特殊机制规则与公式 (七大乘区、90级基数 1446.85、抗打断乘算、枫丹生命之契、纳塔夜魂值)
"""

import hashlib
import json
import os
import sys
import psycopg2
from psycopg2.extras import Json

PG_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

def calc_hash(data: dict) -> str:
    """计算规范 JSON 字符串的 SHA-256 哈希值"""
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def get_characters():
    """原神核心角色全维度数值数据字典 (优先载入全量 121 位角色导出数据)"""
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out', 'all_genshin_characters.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data and len(data) > 0:
                print(f"[load] 成功载入全量 {len(data)} 位角色数值数据！")
                return data

    return [
        {
            "name": "那维莱特",
            "title": "谕告的潮音",
            "rarity": 5,
            "element": "水",
            "weapon_type": "法器",
            "region": "枫丹",
            "arkhe": "芒性",
            "avatar_url": "https://uploadstatic.mihoyo.com/ys-obc/2023/09/26/122176465/3273e91d575797374dc74c2ae77f0a80_1650383794101423403.png",
            "splash_url": "https://uploadstatic.mihoyo.com/ys-obc/2023/09/26/122176465/f7daeb0f316bf4f603c4daea5c517fd1_740700818277253335.png",
            "base_stats": [
                {"level": "1", "hp": 1144, "atk": 16, "def": 45, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20", "hp": 2967, "atk": 42, "def": 116, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20+", "hp": 3948, "atk": 56, "def": 154, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40", "hp": 5909, "atk": 83, "def": 231, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40+", "hp": 6605, "atk": 93, "def": 258, "crit_rate": "5.0%", "crit_dmg": "59.6%"},
                {"level": "50", "hp": 7601, "atk": 107, "def": 297, "crit_rate": "5.0%", "crit_dmg": "59.6%"},
                {"level": "50+", "hp": 8529, "atk": 120, "def": 333, "crit_rate": "5.0%", "crit_dmg": "69.2%"},
                {"level": "60", "hp": 9535, "atk": 134, "def": 372, "crit_rate": "5.0%", "crit_dmg": "69.2%"},
                {"level": "60+", "hp": 10230, "atk": 144, "def": 400, "crit_rate": "5.0%", "crit_dmg": "69.2%"},
                {"level": "70", "hp": 11246, "atk": 158, "def": 439, "crit_rate": "5.0%", "crit_dmg": "69.2%"},
                {"level": "70+", "hp": 11942, "atk": 168, "def": 466, "crit_rate": "5.0%", "crit_dmg": "78.8%"},
                {"level": "80", "hp": 12970, "atk": 182, "def": 506, "crit_rate": "5.0%", "crit_dmg": "78.8%"},
                {"level": "80+", "hp": 13665, "atk": 192, "def": 533, "crit_rate": "5.0%", "crit_dmg": "88.4%"},
                {"level": "90", "hp": 14695, "atk": 208, "def": 576, "crit_rate": "5.0%", "crit_dmg": "88.4%"}
            ],
            "special_ascension_stat": {
                "stat_name": "暴击伤害",
                "stages": {"40+": "9.6%", "50+": "19.2%", "70+": "28.8%", "80+": "38.4%"}
            },
            "ascension_materials": [
                {"tier": "突破20级", "items": "涤净青金碎屑 x1, 幽光星星 x3, 异海凝珠 x3, 摩拉 x20000"},
                {"tier": "突破40级", "items": "涤净青金断片 x3, 原海鳞角 x2, 幽光星星 x10, 异海凝珠 x15, 摩拉 x40000"},
                {"tier": "突破50级", "items": "涤净青金断片 x6, 原海鳞角 x4, 幽光星星 x20, 异海之块 x12, 摩拉 x60000"},
                {"tier": "突破60级", "items": "涤净青金块 x3, 原海鳞角 x8, 幽光星星 x30, 异海之块 x18, 摩拉 x80000"},
                {"tier": "突破70级", "items": "涤净青金块 x6, 原海鳞角 x12, 幽光星星 x45, 异色结晶石 x12, 摩拉 x100000"},
                {"tier": "突破80级", "items": "涤净青金 x6, 原海鳞角 x20, 幽光星星 x60, 异色结晶石 x24, 摩拉 x120000"}
            ],
            "talents": [
                {
                    "name": "普通攻击·如水从平",
                    "type": "NORMAL_ATTACK",
                    "description": "挥舞法杖驱动水流进行至多三段的攻击。重击·衡平推击：蓄力释放洪流，每0.4秒造成基于生命值上限的水元素范围伤害，若生命值高于50%则持续扣除最大生命值8%。",
                    "scaling": {
                        "charged_beam_lv1": "7.32% 最大生命值",
                        "charged_beam_lv6": "10.61% 最大生命值",
                        "charged_beam_lv10": "14.47% 最大生命值",
                        "stamina_cost": "0点 (源水之滴吸收瞬间释放)",
                        "hp_drain_per_sec": "8.0% 当前生命值 (至50%停止)"
                    }
                },
                {
                    "name": "元素战技·泪水啊，我必偿还",
                    "type": "ELEMENTAL_SKILL",
                    "description": "降下激浪造成水元素范围伤害，命中敌人后生成3枚源水之滴。间歇降下芒性灵息之刺。",
                    "scaling": {
                        "skill_dmg_lv1": "12.86% 最大生命值",
                        "skill_dmg_lv10": "23.15% 最大生命值",
                        "cooldown": "12.0秒",
                        "droplet_count": "3枚 (每枚回血16%最大生命值)",
                        "particles": "生成 4 颗水元素微粒",
                        "arkhe_interval": "9.0秒一次芒性水伤"
                    }
                },
                {
                    "name": "元素爆发·潮水啊，我已归来",
                    "type": "ELEMENTAL_BURST",
                    "description": "释放滔天狂澜造成基于生命上限的水元素范围伤害，短暂间隙后在前方降下两道水瀑，并在范围内生成6枚源水之滴。",
                    "scaling": {
                        "burst_dmg_lv10": "40.0% 最大生命值 (一段) + 22.2%*2 (瀑流)",
                        "energy_cost": "70点",
                        "cooldown": "18.0秒",
                        "droplet_count": "6枚 (配合战技共9枚，可持续满蓄重击3次)"
                    }
                }
            ],
            "passives": [
                {"name": "古海微光", "unlock": "突破等级 20", "desc": "队伍中角色触发蒸发、冻结、感电、绽放、水扩散或水结晶反应时，提升衡平推击伤害110%/125%/160%，至多叠3层。"},
                {"name": "至高裁决", "unlock": "突破等级 60", "desc": "基于生命值超出上限30%的部分，每1%使水元素伤害提升0.6%，至多提升30%水伤。"},
                {"name": "汇聚如浪", "unlock": "固有天赋", "desc": "队伍中所有角色在枫丹水下冲刺移动速度提高30%。"}
            ],
            "constellations": [
                {"c": 1, "name": "尊荣的创生", "desc": "登场时直接获得一层古海微光反应层数；施放重击·衡平推击期间抗打断能力提升至绝对霸体（抗打断系数为0）。"},
                {"c": 2, "name": "律法的戒饬", "desc": "古海微光每层提高重击·衡平推击暴击伤害14%，至多提升42%暴击伤害。"},
                {"c": 3, "name": "古昔的拟相", "desc": "普通攻击·如水从平技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 4, "name": "悲悯的救赎", "desc": "在前台受到治疗时，生成 1 枚源水之滴，每 4 秒至多触发一次。"},
                {"c": 5, "name": "公理的判决", "desc": "元素爆发·潮水啊，我已归来技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 6, "name": "忿怒的酬偿", "desc": "施放重击时吸收周围源水之滴，每吸收1枚延长重击时间1秒并释放两道额外洪流，造成基于最大生命值10%的毁灭水伤。"}
            ],
            "special_mechanics": {
                "elemental_gauge": "1U 弱水 (重击每段判定具备独立附着计数器，遵循 2.5s / 3hits 规则)",
                "icd_rule": "重击衡平推击遵循 2.5s / 3hits 标准ICD，源水之滴生成与吸收无内置CD",
                "poise_damage": "重击每段削韧值 15，战技激浪削韧值 100",
                "interruption_resistance": "0命蓄力期间抗打断系数为 0.5 (可被打断)，1命解锁后抗打断系数降为 0.0 (绝对霸体)",
                "arkhe_property": "芒性 (Pneuma)，9秒内置冷却",
                "hitlag_extension": "法器远程攻击无肉体卡肉，输出窗口不受近战卡肉延时干扰"
            },
            "recommendations": {
                "weapons": {"bis": "万世流涌大典 (专武)", "alternative_5s": "碧落之珑 / 四风原典", "budget_4s": "遗祀玉珑 (大月卡) / 试作金珀 (锻造神器)"},
                "artifacts": {"bis_set": "逐影猎人 4件套 (+15%普攻重击增伤，生命变动+36%暴击率)", "alt_set": "沉沦之心 4件套 / 2水伤+2生命"},
                "main_stats": {"sands": "生命值百分比", "goblet": "水元素伤害加成% / 生命值百分比", "circlet": "暴击伤害% (带逐影猎人时避免暴击率溢出)"},
                "sub_stats": "暴击伤害 > 生命值百分比 > 暴击率 > 元素充能效率 (120%~130%)"
            },
            "version": "5.0"
        },
        {
            "name": "芙宁娜",
            "title": "不休独舞",
            "rarity": 5,
            "element": "水",
            "weapon_type": "单手剑",
            "region": "枫丹",
            "arkhe": "芒荒双属性",
            "avatar_url": "https://uploadstatic.mihoyo.com/ys-obc/2023/11/08/122176465/3273e91d575797374dc74c2ae77f0a80_1650383794101423403.png",
            "splash_url": "https://uploadstatic.mihoyo.com/ys-obc/2023/11/08/122176465/f7daeb0f316bf4f603c4daea5c517fd1_740700818277253335.png",
            "base_stats": [
                {"level": "1", "hp": 1205, "atk": 19, "def": 54, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20", "hp": 3125, "atk": 49, "def": 141, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20+", "hp": 4157, "atk": 65, "def": 187, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40", "hp": 6222, "atk": 97, "def": 280, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40+", "hp": 6956, "atk": 109, "def": 313, "crit_rate": "9.8%", "crit_dmg": "50.0%"},
                {"level": "50", "hp": 8004, "atk": 125, "def": 361, "crit_rate": "9.8%", "crit_dmg": "50.0%"},
                {"level": "50+", "hp": 8982, "atk": 140, "def": 405, "crit_rate": "14.6%", "crit_dmg": "50.0%"},
                {"level": "60", "hp": 10041, "atk": 157, "def": 452, "crit_rate": "14.6%", "crit_dmg": "50.0%"},
                {"level": "60+", "hp": 10774, "atk": 168, "def": 485, "crit_rate": "14.6%", "crit_dmg": "50.0%"},
                {"level": "70", "hp": 11843, "atk": 185, "def": 534, "crit_rate": "14.6%", "crit_dmg": "50.0%"},
                {"level": "70+", "hp": 12576, "atk": 196, "def": 567, "crit_rate": "19.4%", "crit_dmg": "50.0%"},
                {"level": "80", "hp": 13658, "atk": 213, "def": 615, "crit_rate": "19.4%", "crit_dmg": "50.0%"},
                {"level": "80+", "hp": 14391, "atk": 224, "def": 648, "crit_rate": "24.2%", "crit_dmg": "50.0%"},
                {"level": "90", "hp": 15307, "atk": 244, "def": 696, "crit_rate": "24.2%", "crit_dmg": "50.0%"}
            ],
            "special_ascension_stat": {
                "stat_name": "暴击率",
                "stages": {"40+": "4.8%", "50+": "9.6%", "70+": "14.4%", "80+": "19.2%"}
            },
            "ascension_materials": [
                {"tier": "突破20级", "items": "涤净青金碎屑 x1, 湖光铃兰 x3, 骗骗花蜜 x3, 摩拉 x20000"},
                {"tier": "突破40级", "items": "涤净青金断片 x3, 超越之水 x2, 湖光铃兰 x10, 骗骗花蜜 x15, 摩拉 x40000"},
                {"tier": "突破50级", "items": "涤净青金断片 x6, 超越之水 x4, 湖光铃兰 x20, 微光花蜜 x12, 摩拉 x60000"},
                {"tier": "突破60级", "items": "涤净青金块 x3, 超越之水 x8, 湖光铃兰 x30, 微光花蜜 x18, 摩拉 x80000"},
                {"tier": "突破70级", "items": "涤净青金块 x6, 超越之水 x12, 湖光铃兰 x45, 原素花蜜 x12, 摩拉 x100000"},
                {"tier": "突破80级", "items": "涤净青金 x6, 超越之水 x20, 湖光铃兰 x60, 原素花蜜 x24, 摩拉 x120000"}
            ],
            "talents": [
                {
                    "name": "普通攻击·独舞之邀",
                    "type": "NORMAL_ATTACK",
                    "description": "进行至多四段连续剑击。重击可切换芒荒始基力形态并变更发型与服饰。",
                    "scaling": {"arkhe_switch": "芒荒重击自由切换", "stamina": "20点"}
                },
                {
                    "name": "元素战技·孤心沙龙",
                    "type": "ELEMENTAL_SKILL",
                    "description": "荒性：召唤乌瑟勋爵、海薇玛夫人、谢贝蕾妲少姐进行高频水元素攻击，消耗生命高于50%队友血量获得全队增伤。芒性：召唤众水歌者为前台角色持续回复巨额生命。",
                    "scaling": {
                        "salon_dmg_multiplier": "110%/120%/130%/140% (根据消耗队伍生命人数)",
                        "duration": "30.0秒 (极长待机)",
                        "cooldown": "20.0秒 (全程无缝覆盖)",
                        "healing_lv10": "最大生命值 8.16% + 943 (众水歌者)"
                    }
                },
                {
                    "name": "元素爆发·万民齐欢",
                    "type": "ELEMENTAL_BURST",
                    "description": "激发狂欢之力，全队生命值每变动1%（受到伤害或治疗）即可积攒1点气氛值，基于气氛值向全队提供高额全局增伤与受治疗加成。",
                    "scaling": {
                        "fanfare_max_stacks": "300点气氛值 (0命) / 400点 (1命)",
                        "dmg_bonus_per_stack_lv10": "0.25% 全局增伤 (300点满层 = 75% 全局增伤)",
                        "healing_bonus_per_stack_lv10": "0.10% 受治疗加成 (满层 = 30%)",
                        "energy_cost": "60点",
                        "duration": "18.0秒",
                        "cooldown": "15.0秒"
                    }
                }
            ],
            "passives": [
                {"name": "停不了的圆舞", "unlock": "突破等级 20", "desc": "前台角色受到非芙宁娜造成的溢出治疗时，芙宁娜在后续4秒内为全队回复两次生命值（每次为各自生命上限的2%）。"},
                {"name": "无人听的自白", "unlock": "突破等级 60", "desc": "基于生命值超出上限的部分，每1000点最大生命值使孤心沙龙伤害提升0.7%（至多28%），众水歌者治疗间隔缩短0.4%（至多16%）。"},
                {"name": "瀚海亦舞台", "unlock": "固有天赋", "desc": "异色原海异种能力冷却时间减少30%。"}
            ],
            "constellations": [
                {"c": 1, "name": "「爱是个顽皮的小孩」", "desc": "施放万民齐欢时立即获得150点气氛值，并将气氛值上限提升至400点（最高增伤提升至100%）。"},
                {"c": 2, "name": "「女人都善变，宛如水中的浮萍」", "desc": "万民齐欢期间气氛值积攒效率提升250%，超出上限的气氛值每点转化为芙宁娜最大生命值0.35%（至多提高140%生命上限）。"},
                {"c": 3, "name": "「秘密，藏在我的眼里」", "desc": "元素爆发·万民齐欢技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 4, "name": "「若非身在幽谷，怎知生命珍贵」", "desc": "孤心沙龙成员命中敌人或众水歌者治疗时，为芙宁娜恢复 4 点元素能量，每 5 秒至多触发一次。"},
                {"c": 5, "name": "「如今我已知晓，那人的名讳是…」", "desc": "元素战技·孤心沙龙技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 6, "name": "「诸君听我颂，这爱之歌！」", "desc": "施放战技后获得超强水元素附魔，前6次普攻/重击/下落造成相当于生命上限18%的水伤，并根据芒荒形态提供全队瞬发治疗或额外暴击增伤。"}
            ],
            "special_mechanics": {
                "elemental_gauge": "沙龙成员为 1U 弱水，海薇玛夫人独立附着，乌瑟勋爵遵循 3次命中 附着",
                "icd_rule": "沙龙召唤物各自拥有独立的元素附着计时器，挂水频率极高且全自动索敌",
                "poise_damage": "谢贝蕾妲少姐削韧 100，乌瑟勋爵削韧 80",
                "interruption_resistance": "普通抗打断系数 1.0",
                "arkhe_property": "芒/荒双重始基力自由切换 (全游戏唯二具备双始基力的角色)",
                "hitlag_extension": "后台召唤物协同攻击，不受前台近战卡肉限制，持续时间恒定 30 秒"
            },
            "recommendations": {
                "weapons": {"bis": "静水流涌之辉 (专武)", "alternative_5s": "磐岩结绿 / 圣显之钥", "budget_4s": "腐殖之剑 / 水仙十字圣剑 / 灰河渡手 (钓鱼武器)"},
                "artifacts": {"bis_set": "黄金剧团 4件套 (+70%后台元素战技极致增伤)", "alt_set": "2千岩+2花海 / 4千岩牢固"},
                "main_stats": {"sands": "生命值百分比 / 元素充能效率 (单水队伍需充能沙)", "goblet": "生命值百分比 / 水元素伤害加成%", "circlet": "暴击伤害% / 暴击率%"},
                "sub_stats": "元素充能效率 (160%~200%保证大招无缝) > 暴击伤害 > 暴击率 > 生命百分比"
            },
            "version": "5.0"
        },
        {
            "name": "钟离",
            "title": "尘世闲游",
            "rarity": 5,
            "element": "岩",
            "weapon_type": "长柄武器",
            "region": "璃月",
            "arkhe": "无",
            "avatar_url": "https://uploadstatic.mihoyo.com/ys-obc/2021/04/16/122176465/5c149b5c2560ce01b96497f1fbc73177_8116568297746272522.png",
            "splash_url": "https://uploadstatic.mihoyo.com/ys-obc/2021/04/16/122176465/9211ca54bdfbe4b611e0dc4e3416ca39_2475510619557434771.png",
            "base_stats": [
                {"level": "1", "hp": 1144, "atk": 20, "def": 57, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20", "hp": 2967, "atk": 51, "def": 149, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20+", "hp": 3948, "atk": 67, "def": 198, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40", "hp": 5909, "atk": 101, "def": 296, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40+", "hp": 6605, "atk": 113, "def": 332, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "50", "hp": 7601, "atk": 130, "def": 381, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "50+", "hp": 8529, "atk": 145, "def": 428, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "60", "hp": 9535, "atk": 163, "def": 478, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "60+", "hp": 10230, "atk": 175, "def": 514, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "70", "hp": 11246, "atk": 191, "def": 564, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "70+", "hp": 11942, "atk": 203, "def": 599, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "80", "hp": 12970, "atk": 221, "def": 651, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "80+", "hp": 13665, "atk": 233, "def": 686, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "90", "hp": 14695, "atk": 251, "def": 738, "crit_rate": "5.0%", "crit_dmg": "50.0%"}
            ],
            "special_ascension_stat": {
                "stat_name": "岩元素伤害加成",
                "stages": {"40+": "7.2%", "50+": "14.4%", "70+": "21.6%", "80+": "28.8%"}
            },
            "ascension_materials": [
                {"tier": "突破20级", "items": "坚牢黄玉碎屑 x1, 石珀 x3, 史莱姆凝液 x3, 摩拉 x20000"},
                {"tier": "突破40级", "items": "坚牢黄玉断片 x3, 玄岩之塔 x2, 石珀 x10, 史莱姆凝液 x15, 摩拉 x40000"},
                {"tier": "突破50级", "items": "坚牢黄玉断片 x6, 玄岩之塔 x4, 石珀 x20, 史莱姆清 x12, 摩拉 x60000"},
                {"tier": "突破60级", "items": "坚牢黄玉块 x3, 玄岩之塔 x8, 石珀 x30, 史莱姆清 x18, 摩拉 x80000"},
                {"tier": "突破70级", "items": "坚牢黄玉块 x6, 玄岩之塔 x12, 石珀 x45, 史莱姆原浆 x12, 摩拉 x100000"},
                {"tier": "突破80级", "items": "坚牢黄玉 x6, 玄岩之塔 x20, 石珀 x60, 史莱姆原浆 x24, 摩拉 x120000"}
            ],
            "talents": [
                {
                    "name": "普通攻击·岩雨",
                    "type": "NORMAL_ATTACK",
                    "description": "进行至多六段的连续枪击。第5段普攻后踢枪回旋造成多段枪雨伤害。",
                    "scaling": {"combo_hits": "6段", "hit_5_multi": "4段踢枪"}
                },
                {
                    "name": "元素战技·地心",
                    "type": "ELEMENTAL_SKILL",
                    "description": "点按：召唤岩脊共鸣。长按：生成全游戏最强护盾「玉璋护盾」，吸收量对全属性伤害及物理伤害有150%吸收效果，并使周围敌人全元素与物理抗性降低20%。",
                    "scaling": {
                        "shield_base_lv10": "2712 + 最大生命值 23.0%",
                        "shield_absorption": "150% 全元素伤害与物理伤害吸收效果",
                        "res_shred": "降低周围敌人 20% 所有元素抗性与物理抗性",
                        "duration": "20.0秒 (全程覆盖)",
                        "cooldown": "点按4.0秒 / 长按12.0秒"
                    }
                },
                {
                    "name": "元素爆发·天星",
                    "type": "ELEMENTAL_BURST",
                    "description": "降下巨大的星岩，对坠落范围内的敌人造成巨额岩元素伤害，并施加长达数秒的石化状态。",
                    "scaling": {
                        "burst_dmg_lv10": "900% 基础攻击倍率 + 最大生命值 33% 附加提升",
                        "petrification_duration_lv10": "4.0秒",
                        "energy_cost": "40点 (超低能耗)",
                        "cooldown": "12.0秒"
                    }
                }
            ],
            "passives": [
                {"name": "悬岩宸断", "unlock": "突破等级 20", "desc": "玉璋护盾受到伤害时产生坚璧效果，使护盾强效提升5%，至多叠加5次。"},
                {"name": "炊金馔玉", "unlock": "突破等级 60", "desc": "基于最大生命值提升伤害：普攻提高1.39%，地心共鸣提高1.9%，天星提高33.0%。"},
                {"name": "晶石命理", "unlock": "固有天赋", "desc": "锻造长柄武器时，返还15%消耗的矿石。"}
            ],
            "constellations": [
                {"c": 1, "name": "岩者，六合引之为骨", "desc": "地心的岩脊至多可以同时存在 2 株。"},
                {"c": 2, "name": "石者，八荒韫玉而明", "desc": "施放天星时，为队伍中所有角色（包括联机队友）施加玉璋护盾。"},
                {"c": 3, "name": "圭璋，暝仍不移其晖", "desc": "元素战技·地心技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 4, "name": "黄琮，破而坚固在德", "desc": "天星的影响范围扩大 20%，石化状态的持续时间延长 2 秒。"},
                {"c": 5, "name": "苍璧，撼岩一说天动", "desc": "元素爆发·天星技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 6, "name": "金玉，礼予天地四方", "desc": "玉璋护盾受到伤害时，将伤害的 40% 转化为当前角色的生命值回复，单次回复量不超过最大生命值的 8%。"}
            ],
            "special_mechanics": {
                "elemental_gauge": "天星天降具有全游戏罕见的 4U 超强岩元素附着，石化破韧极强",
                "icd_rule": "地心岩脊共鸣遵循 2.5s / 3hits 标准ICD，天星每一次必定附着",
                "poise_damage": "天星削韧值 400 (可击破绝大多数大世界狂暴怪霸体)",
                "interruption_resistance": "玉璋护盾生效期间，前台角色抗打断系数为 0.0 (真正绝对霸体，免疫击飞)",
                "arkhe_property": "无始基力",
                "hitlag_extension": "普攻踢枪具有物理打击感，玉璋护盾无需近战判定即生效"
            },
            "recommendations": {
                "weapons": {"bis": "贯虹之槊 / 护摩之杖", "alternative_5s": "和璞鸢 / 天空之脊", "budget_4s": "黑缨枪 (纯血护盾神枪，生命+46.9%) / 西风长枪 (全队充能)"},
                "artifacts": {"bis_set": "千岩牢固 4件套 (+20%生命，共鸣持续刷新全队+20%攻击与+30%护盾强效)", "alt_set": "2千岩+2花海 (纯血流) / 4宗室"},
                "main_stats": {"sands": "生命值百分比", "goblet": "生命值百分比 (纯盾) / 岩伤加成% (副C流)", "circlet": "生命值百分比 (纯盾) / 暴击率% (副C)"},
                "sub_stats": "生命值百分比 > 生命值固定值 > 元素充能效率 (130%) > 暴击率"
            },
            "version": "5.0"
        },
        {
            "name": "雷电将军",
            "title": "一心净土",
            "rarity": 5,
            "element": "雷",
            "weapon_type": "长柄武器",
            "region": "稻妻",
            "arkhe": "无",
            "avatar_url": "https://uploadstatic.mihoyo.com/ys-obc/2021/09/01/122176465/6bc9c51cefbff1a2bcfc23e80ec4a9e1_865768569858548177.png",
            "splash_url": "https://uploadstatic.mihoyo.com/ys-obc/2021/09/01/122176465/5ad61e0500a89d70ceb20977e80ceaa8_1762198083818617838.png",
            "base_stats": [
                {"level": "1", "hp": 1005, "atk": 26, "def": 61, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20", "hp": 2606, "atk": 68, "def": 158, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "20+", "hp": 3467, "atk": 90, "def": 211, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40", "hp": 5189, "atk": 135, "def": 315, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "40+", "hp": 5800, "atk": 151, "def": 352, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "50", "hp": 6675, "atk": 174, "def": 405, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "50+", "hp": 7489, "atk": 195, "def": 454, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "60", "hp": 8373, "atk": 218, "def": 508, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "60+", "hp": 8984, "atk": 234, "def": 545, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "70", "hp": 9875, "atk": 257, "def": 599, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "70+", "hp": 10486, "atk": 273, "def": 636, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "80", "hp": 11389, "atk": 296, "def": 691, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "80+", "hp": 12000, "atk": 312, "def": 728, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
                {"level": "90", "hp": 12907, "atk": 337, "def": 789, "crit_rate": "5.0%", "crit_dmg": "50.0%"}
            ],
            "special_ascension_stat": {
                "stat_name": "元素充能效率",
                "stages": {"40+": "8.0%", "50+": "16.0%", "70+": "24.0%", "80+": "32.0%"}
            },
            "ascension_materials": [
                {"tier": "突破20级", "items": "最胜紫晶碎屑 x1, 天云草实 x3, 破旧的刀镡 x3, 摩拉 x20000"},
                {"tier": "突破40级", "items": "最胜紫晶断片 x3, 雷霆数珠 x2, 天云草实 x10, 破旧的刀镡 x15, 摩拉 x40000"},
                {"tier": "突破50级", "items": "最胜紫晶断片 x6, 雷霆数珠 x4, 天云草实 x20, 影打刀镡 x12, 摩拉 x60000"},
                {"tier": "突破60级", "items": "最胜紫晶块 x3, 雷霆数珠 x8, 天云草实 x30, 影打刀镡 x18, 摩拉 x80000"},
                {"tier": "突破70级", "items": "最胜紫晶块 x6, 雷霆数珠 x12, 天云草实 x45, 名刀镡 x12, 摩拉 x100000"},
                {"tier": "突破80级", "items": "最胜紫晶 x6, 雷霆数珠 x20, 天云草实 x60, 名刀镡 x24, 摩拉 x120000"}
            ],
            "talents": [
                {
                    "name": "普通攻击·源流",
                    "type": "NORMAL_ATTACK",
                    "description": "进行至多五段连续枪击。",
                    "scaling": {"combo": "5段普攻"}
                },
                {
                    "name": "元素战技·神变·恶曜开眼",
                    "type": "ELEMENTAL_SKILL",
                    "description": "造成雷元素伤害并为全队附加雷罚恶曜之眼。队友造成伤害时协同造成雷伤；基于队友大招能量上限提升大招伤害（每点能量提升0.3%大招伤害）。",
                    "scaling": {
                        "burst_dmg_boost": "每点能量上限提升 0.30% 元素爆发伤害 (90能量大招提升27%)",
                        "duration": "25.0秒 (超长待机)",
                        "cooldown": "10.0秒",
                        "coordinate_dmg": "每0.9秒一次协同雷伤"
                    }
                },
                {
                    "name": "元素爆发·奥义·梦想真说",
                    "type": "ELEMENTAL_BURST",
                    "description": "汇聚万千愿力，斩出无想的一刀（巨额雷元素范围伤害），随后进入梦想一心状态（普攻转化为雷元素附魔剑击，每刀为全队回复元素能量）。",
                    "scaling": {
                        "slash_dmg_lv10": "721.4% 基础倍率 + 愿力层数加成 (满愿力总倍率超 1100%)",
                        "energy_restoration_per_hit": "2.5点 (7秒内至多触发5次，全队回能约 25 点)",
                        "energy_cost": "90点 (全游戏最高档)",
                        "cooldown": "18.0秒",
                        "duration": "7.0秒"
                    }
                }
            ],
            "passives": [
                {"name": "千万的愿望", "unlock": "突破等级 20", "desc": "队伍中角色获得元素微粒或晶球时，诸愿百眼之轮积攒 2 层愿力。"},
                {"name": "殊胜之御体", "unlock": "突破等级 60", "desc": "超出100%的元素充能效率部分，每1%使梦想一心能量恢复提高0.4%，雷元素伤害加成提高0.4%。"},
                {"name": "天下名物狩", "unlock": "固有天赋", "desc": "突破单手剑和长柄武器时，消耗摩拉减少50%。"}
            ],
            "constellations": [
                {"c": 1, "name": "恶曜之明", "desc": "诸愿百眼之轮积攒愿力速度提升：雷元素角色大招愿力积攒提升80%，其他元素提升20%。"},
                {"c": 2, "name": "斩铁断金", "desc": "核心质变命座：奥义·梦想真说的梦想一刀与梦想一心状态下的攻击，无视敌人 60% 的防御力（实质提升约44%独立总伤害）。"},
                {"c": 3, "name": "真影旧事", "desc": "元素爆发·奥义·梦想真说技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 4, "name": "誓奉行", "desc": "梦想一心状态结束后，全队除雷电将军外的所有角色攻击力提升 30%，持续 10 秒。"},
                {"c": 5, "name": "凶将显形", "desc": "元素战技·神变·恶曜开眼技能等级提高 3 级，最高提升至 15 级。"},
                {"c": 6, "name": "负愿行", "desc": "梦想一心状态下普攻命中敌人，使全队除雷电将军外所有角色的大招冷却时间缩短 1 秒，至多缩短 5 秒。"}
            ],
            "special_mechanics": {
                "elemental_gauge": "第一刀梦想一刀具有 2U 强雷附着，梦想一心平A为 1U 弱雷附着 (2.5s/3hits)",
                "icd_rule": "恶曜之眼协同攻击遵循 2.5s / 3hits 独立ICD",
                "poise_damage": "梦想一刀削韧 300，破韧能力极强",
                "interruption_resistance": "梦想一心7秒开启期间，抗打断系数降为 0.0 (绝对霸体，无法被打断)",
                "arkhe_property": "无始基力",
                "hitlag_extension": "关键手感机制：近战梦想一心连续挥刀卡肉可将原 7 秒输出窗口实质延长至 8.2~8.5 秒！"
            },
            "recommendations": {
                "weapons": {"bis": "薙草之稻光 (专武，充能转攻击与大招充能)", "alternative_5s": "护摩之杖 / 和璞鸢 / 天空之脊", "budget_4s": "「渔获」 (钓鱼满精神器，+32%大招增伤+12%大招暴击)"},
                "artifacts": {"bis_set": "绝缘之旗印 4件套 (基于充能效率25%转化为大招增伤，最高75%增伤)", "alt_set": "千岩牢固 (超绽放精通流) / 饰金之梦 (全精通雷神)"},
                "main_stats": {"sands": "元素充能效率% (专武) / 攻击力% (渔获)", "goblet": "雷元素伤害加成% / 攻击力% (充能高于270%选雷伤杯)", "circlet": "暴击率% / 暴击伤害%"},
                "sub_stats": "暴击率 / 暴击伤害 > 元素充能效率 (基准270%) > 攻击力百分比"
            },
            "version": "5.0"
        }
    ]

def get_weapons():
    """官方核心武器库全量数值与精炼阶梯"""
    all_weapons_path = os.path.join(os.path.dirname(__file__), "../out/all_genshin_weapons.json")
    if os.path.exists(all_weapons_path):
        with open(all_weapons_path, "r", encoding="utf-8") as f:
            full_weapons = json.load(f)
            print(f"[load] 成功载入全量 {len(full_weapons)} 把武器数值数据！")
            return full_weapons

    return [
        {
            "name": "万世流涌大典",
            "type": "法器",
            "rarity": 5,
            "icon_url": "https://uploadstatic.mihoyo.com/ys-obc/2023/09/26/122176465/weapons/tome_of_eternal_flow.png",
            "base_atk_curve": [
                {"level": "1", "atk": 44}, {"level": "20", "atk": 110}, {"level": "40", "atk": 238},
                {"level": "60", "atk": 388}, {"level": "80", "atk": 497}, {"level": "90", "atk": 542}
            ],
            "sub_stat": {
                "stat_name": "暴击伤害",
                "values": {"1": "19.2%", "20": "33.9%", "40": "55.3%", "60": "76.7%", "80": "84.3%", "90": "88.2%"}
            },
            "refinements": [
                {"rank": "精炼 1阶", "desc": "生命值提升16%；生命值发生变动时，重击伤害提升14%，至多叠加3层，持续4秒；叠满3层时恢复8点元素能量。"},
                {"rank": "精炼 2阶", "desc": "生命值提升20%；重击伤害提升18%，至多叠3层；叠满恢复9点元素能量。"},
                {"rank": "精炼 3阶", "desc": "生命值提升24%；重击伤害提升22%，至多叠3层；叠满恢复10点元素能量。"},
                {"rank": "精炼 4阶", "desc": "生命值提升28%；重击伤害提升26%，至多叠3层；叠满恢复11点元素能量。"},
                {"rank": "精炼 5阶", "desc": "生命值提升32%；重击伤害提升30%，至多叠加3层，重击伤害总计提升90%；叠满恢复12点元素能量。"}
            ],
            "ascension_materials": [
                {"type": "枫丹秘境", "name": "纯圣露滴的真粹系列"},
                {"type": "精英素材", "name": "浊水裂帛 / 浊水幻灵"},
                {"type": "怪物素材", "name": "幽邃异合体"}
            ],
            "version": "5.0"
        },
        {
            "name": "护摩之杖",
            "type": "长柄武器",
            "rarity": 5,
            "icon_url": "https://uploadstatic.mihoyo.com/ys-obc/2021/02/23/122176465/weapons/staff_of_homa.png",
            "base_atk_curve": [
                {"level": "1", "atk": 46}, {"level": "20", "atk": 122}, {"level": "40", "atk": 261},
                {"level": "60", "atk": 421}, {"level": "80", "atk": 563}, {"level": "90", "atk": 608}
            ],
            "sub_stat": {
                "stat_name": "暴击伤害",
                "values": {"1": "14.4%", "20": "25.4%", "40": "41.5%", "60": "57.6%", "80": "63.2%", "90": "66.2%"}
            },
            "refinements": [
                {"rank": "精炼 1阶", "desc": "生命值提升20%；提供基于最大生命值0.8%的攻击力加成；当生命值低于50%时，额外提高1%最大生命值的攻击力。"},
                {"rank": "精炼 2阶", "desc": "生命值提升25%；基于最大生命值1.0%提升攻击；低于50%额外提升1.2%。"},
                {"rank": "精炼 3阶", "desc": "生命值提升30%；基于最大生命值1.2%提升攻击；低于50%额外提升1.4%。"},
                {"rank": "精炼 4阶", "desc": "生命值提升35%；基于最大生命值1.4%提升攻击；低于50%额外提升1.6%。"},
                {"rank": "精炼 5阶", "desc": "生命值提升40%；基于最大生命值1.6%提升攻击；低于50%额外提升1.8%生命上限攻击。"}
            ],
            "ascension_materials": [
                {"type": "璃月秘境", "name": "漆黑陨铁系列"},
                {"type": "精英素材", "name": "地脉的旧枝 / 地脉枯叶"},
                {"type": "怪物素材", "name": "史莱姆凝液"}
            ],
            "version": "5.0"
        },
        {
            "name": "薙草之稻光",
            "type": "长柄武器",
            "rarity": 5,
            "icon_url": "https://uploadstatic.mihoyo.com/ys-obc/2021/09/01/122176465/weapons/engulfing_lightning.png",
            "base_atk_curve": [
                {"level": "1", "atk": 46}, {"level": "20", "atk": 122}, {"level": "40", "atk": 261},
                {"level": "60", "atk": 421}, {"level": "80", "atk": 563}, {"level": "90", "atk": 608}
            ],
            "sub_stat": {
                "stat_name": "元素充能效率",
                "values": {"1": "12.0%", "20": "21.2%", "40": "34.6%", "60": "48.0%", "80": "52.7%", "90": "55.1%"}
            },
            "refinements": [
                {"rank": "精炼 1阶", "desc": "攻击力获得提升，提升程度相当于元素充能效率超出100%部分的28%，至多提升80%；施放元素爆发后的12秒内，元素充能效率提升30%。"},
                {"rank": "精炼 2阶", "desc": "超出部分35%转化为攻击，至多90%；开大充能+35%。"},
                {"rank": "精炼 3阶", "desc": "超出部分42%转化为攻击，至多100%；开大充能+40%。"},
                {"rank": "精炼 4阶", "desc": "超出部分49%转化为攻击，至多110%；开大充能+45%。"},
                {"rank": "精炼 5阶", "desc": "超出部分56%转化为攻击，至多120%；施放元素爆发后元素充能效率提升50%。"}
            ],
            "ascension_materials": [
                {"type": "稻妻秘境", "name": "今昔剧画之鬼人系列"},
                {"type": "精英素材", "name": "混沌真眼系列"},
                {"type": "怪物素材", "name": "破旧的刀镡"}
            ],
            "version": "5.0"
        }
    ]

def get_artifact_sets():
    """官方核心圣遗物套装属性与词条规约"""
    all_artifacts_path = os.path.join(os.path.dirname(__file__), "../out/all_genshin_artifacts.json")
    if os.path.exists(all_artifacts_path):
        with open(all_artifacts_path, "r", encoding="utf-8") as f:
            full_artifacts = json.load(f)
            print(f"[load] 成功载入全量 {len(full_artifacts)} 套圣遗物数据！")
            return full_artifacts

    return [
        {
            "name": "逐影猎人",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://uploadstatic.mihoyo.com/ys-obc/2023/08/16/122176465/artifacts/marechaussee_hunter.png",
            "two_piece_bonus": "普通攻击与重击造成的伤害提高 15%。",
            "four_piece_bonus": "当前生命值提升或降低时，暴击率提升 12%，该效果持续 5 秒，至多叠加 3 次（最高提供 36% 暴击率）。",
            "pieces": [
                {"slot": "生之花", "name": "猎人的胸花", "main_stat_rule": "固定生命值 4780 (20级)"},
                {"slot": "死之羽", "name": "杰作的序曲", "main_stat_rule": "固定攻击力 311 (20级)"},
                {"slot": "时之沙", "name": "督训的晷针", "main_stat_rule": "生命值% (46.6%) / 攻击力% (46.6%) / 防御力% (58.3%) / 充能% (51.8%) / 精通 (187)"},
                {"slot": "空之杯", "name": "前辈的遗眷", "main_stat_rule": "七大元素伤害加成% (46.6%) / 物理伤害加成% (58.3%) / 攻击% / 生命% / 精通"},
                {"slot": "理之冠", "name": "老兵的容颜", "main_stat_rule": "暴击率% (31.1%) / 暴击伤害% (62.2%) / 治疗加成% (35.9%) / 生命% / 攻击%"}
            ],
            "rules_reference": {
                "sub_stat_pool": ["暴击率", "暴击伤害", "攻击力百分比", "元素充能效率", "元素精通", "生命值百分比", "防御力百分比", "固定攻击力", "固定生命值", "固定防御力"],
                "sub_stat_tiers_4star_and_5star": {
                    "crit_rate": ["2.7%", "3.1%", "3.5%", "3.9%"],
                    "crit_dmg": ["5.4%", "6.2%", "7.0%", "7.8%"],
                    "atk_percent": ["4.1%", "4.7%", "5.3%", "5.8%"],
                    "energy_recharge": ["4.5%", "5.2%", "5.8%", "6.5%"],
                    "elemental_mastery": [16, 19, 21, 23],
                    "hp_percent": ["4.1%", "4.7%", "5.3%", "5.8%"],
                    "def_percent": ["5.1%", "5.8%", "6.6%", "7.3%"]
                }
            },
            "version": "5.0"
        },
        {
            "name": "绝缘之旗印",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://uploadstatic.mihoyo.com/ys-obc/2021/07/21/122176465/artifacts/emblem_of_severed_fate.png",
            "two_piece_bonus": "元素充能效率提高 20%。",
            "four_piece_bonus": "基于元素充能效率的 25%，提高元素爆发造成的伤害。至多通过这种方式获得 75% 元素爆发伤害提升（充能达到 300% 时吃满）。",
            "pieces": [
                {"slot": "生之花", "name": "明威之镡", "main_stat_rule": "固定生命值 4780"},
                {"slot": "死之羽", "name": "切玉之羽", "main_stat_rule": "固定攻击力 311"},
                {"slot": "时之沙", "name": "雷云之笼", "main_stat_rule": "充能效率% (51.8%) / 攻击力% / 精通"},
                {"slot": "空之杯", "name": "绯花之壶", "main_stat_rule": "元素伤害加成% / 攻击力%"},
                {"slot": "理之冠", "name": "华饰之兜", "main_stat_rule": "暴击率% / 暴击伤害%"}
            ],
            "rules_reference": {
                "max_dmg_bonus_calc": "min(充能效率 * 0.25, 0.75)"
            },
            "version": "5.0"
        }
    ]

def get_mechanic_rules():
    """原神官方战斗底层计算公式与特殊机制字典"""
    return [
        {
            "category": "DAMAGE_FORMULA",
            "title": "七大独立伤害乘区计算模型",
            "formula": "FinalDamage = (BaseStat * SkillMultiplier + FlatBonus) * (1 + DamageBonus) * (1 + CritDMG) * ReactionMultiplier * DefMultiplier * ResMultiplier",
            "parameters": {
                "multipliers": [
                    {"name": "基础数值区 (Base)", "desc": "基础攻击白值*(1+攻击%) + 固定攻击力，或生命/防御等效面板"},
                    {"name": "倍率乘区 (Skill Mult)", "desc": "技能Talent百分比"},
                    {"name": "基础伤害提升区 (Flat Dmg Bonus)", "desc": "申鹤冰翎、云堇飞云旗阵、闲云仙力加成直接附加在基础区后"},
                    {"name": "增伤乘区 (Damage Bonus)", "desc": "全伤害加成% + 元素伤害加成% + 普攻/重击/战技/大招增伤%"},
                    {"name": "暴击乘区 (Crit DMG)", "desc": "暴击时为 1 + 暴击伤害%，未暴击为 1"},
                    {"name": "增幅反应乘区 (Amplifying)", "desc": "蒸发(1.5x/2.0x)、融化(1.5x/2.0x)乘 (1 + 2.78*EM/(EM+1400) + 反应系数)"},
                    {"name": "防御乘区 (DEF)", "desc": "(Lv_char+100) / ((Lv_char+100) + (Lv_enemy+100)*(1-减防%)*(1-无视防%))"},
                    {"name": "抗性乘区 (RES)", "desc": "分段函数：RES<0 为 1-RES/2；0<=RES<=0.75 为 1-RES；RES>0.75 为 1/(1+4*RES)"}
                ]
            }
        },
        {
            "category": "LEVEL_MULTIPLIER",
            "title": "90级剧变与激化反应基数常数表",
            "formula": "ReactionDamage = BaseMultiplier * LevelCoefficient(Lv) * (1 + 16*EM/(EM+2000) + ReactionBonus)",
            "parameters": {
                "level_90_constant": 1446.85,
                "reaction_multipliers": {
                    "超导 (Superconduct)": 0.5,
                    "扩散 (Swirl)": 0.6,
                    "感电 (Electro-Charged)": 1.2,
                    "碎冰 (Shatter)": 1.5,
                    "超载 (Overloaded)": 2.0,
                    "绽放 (Bloom)": 2.0,
                    "烈绽放 (Burgeon)": 3.0,
                    "超绽放 (Hyperbloom)": 3.0,
                    "燃烧 (Burning)": 0.25
                },
                "additive_catalyze": {
                    "超激化 (Aggravate)": "1.15 * 1446.85 * (1 + 5*EM/(EM+1200)) 直接附加于基础攻击区",
                    "蔓激化 (Spread)": "1.25 * 1446.85 * (1 + 5*EM/(EM+1200)) 直接附加于基础攻击区"
                }
            }
        },
        {
            "category": "ICD_SYSTEM",
            "title": "元素附着量与内置冷却 (ICD) 规约",
            "formula": "Default ICD: 2.5 seconds or 3 hits cooldown timer",
            "parameters": {
                "gauge_units": {
                    "1U (弱元素)": "衰减时长 9.5秒，绝大多数技能普攻附着量",
                    "2U (强元素)": "衰减时长 12.0秒，重云Q、班尼特E、北斗E",
                    "4U (超强元素)": "衰减时长 17.0秒，钟离天星、雷神梦想一刀"
                },
                "reaction_consumption_ratio": {
                    "水打火 (正向蒸发)": "消耗 2.0 倍火附着",
                    "火打水 (反向蒸发)": "消耗 0.5 倍水附着 (极易持续打工)",
                    "火打冰 (正向融化)": "消耗 2.0 倍冰附着",
                    "冰打火 (反向融化)": "消耗 0.5 倍火附着"
                },
                "zero_icd_exceptions": ["香菱旋火轮 (圈圈附着)", "胡桃重击 (枪枪蒸发)", "珊瑚宫心海水母 (次次挂水)"]
            }
        },
        {
            "category": "POISE_SYSTEM",
            "title": "韧性、削韧与抗打断机制",
            "formula": "TotalInterruptionCoeff = Coeff_A * Coeff_B (乘算叠加，越小越霸体)",
            "parameters": {
                "interruption_coefficients": {
                    "普通角色受击": 1.0,
                    "行秋雨帘剑": 0.3,
                    "北斗雷兽之盾": 0.5,
                    "双重叠加 (行秋+北斗)": "0.3 * 0.5 = 0.15 (几乎不可被打断)",
                    "绝对霸体 (钟离盾/雷神开大/优菈开大)": "0.0 (绝对免控，无视任何受击击飞)"
                }
            }
        },
        {
            "category": "REGION_SYSTEM",
            "title": "枫丹生命之契与纳塔夜魂系统机制",
            "formula": "BondOfLife = MaxHP * Percentage; NightsoulPoints = Current / Max",
            "parameters": {
                "bond_of_life": "红血条机制：阻止受到的治疗，溢出治疗优先清偿契约；清偿或维持高契约时激活伤害质变提升（阿蕾奇诺/克洛琳德）",
                "nightsoul_points": "纳塔角色特有夜魂加持条（上限通常为60或100点），消耗夜魂值释放高机动移动与连击",
                "nightsoul_burst": "队伍中角色造成元素伤害时触发夜魂进发，队伍纳塔角色越多触发CD从18s缩减至9s"
            }
        }
    ]

def main():
    print("=== 开始同步原神全维度数值数据至 PostgreSQL 数据库 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # 1. 角色数值入库
    print("[1/4] 写入原神角色全量成长、倍率与机制数据...")
    chars = get_characters()
    for ch in chars:
        h = calc_hash(ch)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region, arkhe,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version
            ) VALUES (
                2, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                title = EXCLUDED.title,
                rarity = EXCLUDED.rarity,
                element = EXCLUDED.element,
                weapon_type = EXCLUDED.weapon_type,
                region = EXCLUDED.region,
                arkhe = EXCLUDED.arkhe,
                avatar_url = EXCLUDED.avatar_url,
                splash_url = EXCLUDED.splash_url,
                base_stats = EXCLUDED.base_stats,
                special_ascension_stat = EXCLUDED.special_ascension_stat,
                ascension_materials = EXCLUDED.ascension_materials,
                talents = EXCLUDED.talents,
                passives = EXCLUDED.passives,
                constellations = EXCLUDED.constellations,
                special_mechanics = EXCLUDED.special_mechanics,
                recommendations = EXCLUDED.recommendations,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            ch['name'], ch['title'], ch['rarity'], ch['element'], ch['weapon_type'], ch['region'], ch['arkhe'],
            ch['avatar_url'], ch['splash_url'], Json(ch['base_stats']), Json(ch['special_ascension_stat']),
            Json(ch['ascension_materials']), Json(ch['talents']), Json(ch['passives']), Json(ch['constellations']),
            Json(ch['special_mechanics']), Json(ch['recommendations']), h, ch['version']
        ))
        print(f"  ✓ 角色入库成功: {ch['name']} ({ch['title']}) - Hash: {h[:8]}")

    # 2. 武器数值入库
    print("[2/4] 写入原神官方武器成长与精炼阶梯数据...")
    weapons = get_weapons()
    for w in weapons:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                2, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                type = EXCLUDED.type,
                rarity = EXCLUDED.rarity,
                icon_url = EXCLUDED.icon_url,
                base_atk_curve = EXCLUDED.base_atk_curve,
                sub_stat = EXCLUDED.sub_stat,
                refinements = EXCLUDED.refinements,
                ascension_materials = EXCLUDED.ascension_materials,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(w['base_atk_curve']),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))
        print(f"  ✓ 武器入库成功: {w['name']} - Hash: {h[:8]}")

    # 3. 圣遗物套装入库
    print("[3/4] 写入原神圣遗物套装与词条规约数据...")
    artifacts = get_artifact_sets()
    for art in artifacts:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                2, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                rarity_min = EXCLUDED.rarity_min,
                rarity_max = EXCLUDED.rarity_max,
                icon_url = EXCLUDED.icon_url,
                two_piece_bonus = EXCLUDED.two_piece_bonus,
                four_piece_bonus = EXCLUDED.four_piece_bonus,
                pieces = EXCLUDED.pieces,
                rules_reference = EXCLUDED.rules_reference,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            art['name'], art['rarity_min'], art['rarity_max'], art['icon_url'],
            art['two_piece_bonus'], art['four_piece_bonus'], Json(art['pieces']), Json(art['rules_reference']),
            h, art['version']
        ))
        print(f"  ✓ 圣遗物套装入库成功: {art['name']} - Hash: {h[:8]}")

    # 4. 底层战斗机制规则入库
    print("[4/4] 写入原神底层战斗乘区、常数与机制模型...")
    rules = get_mechanic_rules()
    for r in rules:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                2, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (
            r['category'], r['title'], r['formula'], Json(r['parameters'])
        ))
        print(f"  ✓ 战斗机制入库成功: [{r['category']}] {r['title']}")

    conn.commit()
    conn.close()
    print("=== 原神全量数值体系入库完成！ ===")

if __name__ == '__main__':
    main()
