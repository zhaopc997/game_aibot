#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全库游戏数据终极补全与全维度覆盖同步脚本:
1. 恐鬼症 (Phasmophobia, ID = 22) - 全维度补全 (调查员/探测设备/防鬼圣物/猎杀机制/攻略/百科)
2. 火线战姬 (Machine Maiden, ID = 23) - 全维度补全 (机娘战姬/机甲神兵/核心矩阵/力场热量机制/攻略/百科)
3. DOTA 2 (ID = 5) - 补齐核心神装体系 (game_artifact_set)
4. CS2 (ID = 7) - 补齐战术角色定位 (game_character)
5. Apex 英雄 (ID = 16) - 补齐护甲与装备体系 (game_artifact_set)
6. 云顶之弈 (ID = 19) - 补齐核心弈子与海克斯强化体系 (game_character, game_artifact_set)
7. 塞尔达传说：王国之泪 (ID = 3) - 补充蓝图组装实战攻略与左纳乌科技百科 (guide, wiki_entry)
"""

import os
import sys
import json
import hashlib
import psycopg2
from psycopg2.extras import Json

PG_CONFIG = {
    'host': os.getenv('PG_HOST', '127.0.0.1'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def normalize_curve(curve):
    if isinstance(curve, dict):
        return [{"level": str(k), "atk": v} for k, v in curve.items()]
    return curve

# ==========================================
# 1. 恐鬼症 (Phasmophobia, ID = 22)
# ==========================================
def sync_phasmophobia(cur):
    print("--- 正在补全 恐鬼症 (Phasmophobia, game_id = 22) ---")
    gid = 22

    # 角色 / 调查员
    chars = [
        {
            "name": "超自然先锋调查员 (Lead Investigator)",
            "title": "前线探测·灵异直面者",
            "rarity": 5,
            "element": "幽灵学 / 绝境生还",
            "weapon_type": "专业灵异探测设备",
            "region": "罗伯茨通灵事务所",
            "avatar_url": "https://patchwiki.biligame.com/images/phas/thumb/avatar_investigator.png/120px-avatar_investigator.png",
            "splash_url": "https://patchwiki.biligame.com/images/phas/thumb/avatar_investigator.png/600px-avatar_investigator.png",
            "base_stats": [
                {"level": "调查员", "sanity": 100, "stamina": 100, "sprint_duration": "3.0s", "inventory_slots": 3}
            ],
            "special_ascension_stat": {"stat_name": "胆量与黑暗抗性", "values": {"理智流失降低": "处于黑暗中每秒理智流失减少 30%"}},
            "ascension_materials": [{"tier": "执照晋阶", "items": "噩梦难度通关调查日志"}],
            "talents": [
                {"name": "极速排查 (Rapid Evidence Gathering)", "type": "NORMAL_ATTACK", "description": "手持手电筒与 EMF 探测仪在房间内快速穿梭，通过测温仪探测零下低温、紫外线灯照出绿色指纹，并在 60 秒内锁定鬼房位置！", "scaling": "快速定位核心鬼房"},
                {"name": "点燃圣木 (Smudge Stick / 驱逐)", "type": "ELEMENTAL_SKILL", "description": "在鬼魂进入猎杀模式并朝自身冲刺时点燃圣木，致盲鬼魂长达 5 秒并强迫其改变移动方向，拯救自身与队友的生命！", "scaling": "猎杀绝境保命核心神器"},
                {"name": "防鬼十字架守护 (Crucifix Block)", "type": "ELEMENTAL_BURST", "description": "在鬼房地面精准布置三阶十字架，当鬼魂企图在 5 米范围内开启猎杀时，十字架自燃并彻底阻止本次猎杀！", "scaling": "抵挡至多 2 次致命猎杀"}
            ],
            "passives": [{"name": "冷静心智", "desc": "目睹灵异事件（鬼叫、现形闪烁）时，理智值扣除降低 50%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "开局进屋测温与听脚步锁定鬼房 -> 摆放点阵投影仪与通灵盒采集三大核心证据 -> 猎杀开始躲入壁橱关掉手电静音保命！"},
            "recommendations": {"weapons": {"bis": "三阶 EMF 探测仪 + 高灵敏通灵盒"}, "artifacts": {"bis_set": "防鬼圣物套件 (三阶十字架+醒脑丸)"}},
            "version": "v0.10"
        }
    ]

    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                22, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'], c['region'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))

    # 武器 / 探测装备
    weaps = [
        {
            "name": "三阶 EMF 5 级电磁探测仪 (EMF Reader T3)",
            "type": "电磁场超自然探测仪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/phas/item_emf_t3.png",
            "base_atk_curve": [
                {"level": "探测范围", "range_meters": 7.0, "sound_indicator": "高精度电子滴答声", "accuracy": "100%"}
            ],
            "sub_stat": {"type": "证据判定", "values": {"EMF 5级证据": "探测到 5 级红灯亮起即确认 EMF 5 核心证据"}},
            "refinements": [
                {"rank": 1, "desc": "可同时监测方向与距离，在 7 米开外即可准确感知鬼魂互动并发出蜂鸣报警。"}
            ],
            "ascension_materials": [{"tier": "升级花费", "items": "3000 美金与等级解锁"}],
            "version": "v0.10"
        },
        {
            "name": "高灵敏通灵盒 (Spirit Box T3)",
            "type": "无线电声波通灵仪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/phas/item_spiritbox_t3.png",
            "base_atk_curve": [
                {"level": "响应范围", "range_meters": 5.0, "response_rate": "高", "display": "LED 文字显示"}
            ],
            "sub_stat": {"type": "通灵回应", "values": {"语音判定": "关灯后在鬼房按下对讲键提问，鬼魂发出冰冷回应"}},
            "refinements": [
                {"rank": 1, "desc": "降噪算法极佳，即便在鬼房外隔墙也能清晰捕捉到鬼魂的低语回答。"}
            ],
            "ascension_materials": [{"tier": "升级花费", "items": "2500 美金"}],
            "version": "v0.10"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                22, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    # 套装 / 圣物
    arts = [
        {
            "name": "专业防鬼圣物套件 (Ghost Defense Relic Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/phas/set_crucifix.png",
            "two_piece_bonus": "点燃圣木后致盲鬼魂时间由 5 秒延长至 7.5 秒（恶魔除外）。",
            "four_piece_bonus": "十字架防猎杀半径扩大至 5 米（对恶魔可达 7 米），服下醒脑丸瞬间恢复 40% 理智值并赋予 10 秒理智不减锁。",
            "pieces": [
                {"slot": "圣物防具", "name": "三阶防鬼十字架 (Crucifix T3)", "main_stat": "抵御 2 次猎杀 / 半径 5 米"},
                {"slot": "救命药品", "name": "高浓缩醒脑丸 (Sanity Medication T3)", "main_stat": "恢复 40% 理智 / 持续缓释"},
                {"slot": "驱逐香料", "name": "净化圣木 (Smudge Sticks T3)", "main_stat": "致盲 7.5 秒 / 减慢鬼速"}
            ],
            "version": "v0.10"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                22, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    # 机制规则
    mechs = [
        {
            "category": "猎杀机制",
            "title": "恐鬼症 全队平均理智值与猎杀触发概率阈值",
            "formula": "Hunt_Trigger_Check = (Average_Team_Sanity <= Ghost_Threshold) -> Random_Tick(Interval=5s, Prob=15%~60%)",
            "parameters": {
                "demon": "恶魔 (Demon) 具有特殊早猎杀特性，可在 70% 甚至任意理智值无视条件开启猎杀",
                "normal": "常规鬼魂在全队平均理智低于 50% 时进入猎杀窗口；巨灵、御灵、幽灵等在 50% 以下触发",
                "hunting_rules": "猎杀期间大门锁死，手电狂闪，鬼魂根据视线与麦克风声音加速追杀调查员"
            }
        },
        {
            "category": "证据算法",
            "title": "恐鬼症 7 大证据排查与 24 种幽灵识别树模型",
            "formula": "Ghost_Identity = Unique_Intersection(Evidence_1, Evidence_2, Evidence_3)",
            "parameters": {
                "evidences": "7大核心证据：EMF 5级、通灵盒、指纹/紫外线、幽灵宝珠、鬼魂之书、低温/刺骨寒冷、点阵投影 (D.O.T.S)"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (22, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    # 攻略
    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (22, '恐鬼症 噩梦/疯狂难度单人与四人全证据排查与安全溜鬼全攻略', 1, 'BUILD', 'ADVANCED', '["恐鬼症", "Phasmophobia", "噩梦难度", "溜鬼技巧", "理智管理"]',
                '详解高难度排查精要：开局进屋听声辩位速锁鬼房、避难柜子杂物清理、猎杀时静音关手电与围绕餐桌圆形溜鬼手顺。',
                '{"sections":[{"title":"一、开局进门与理智保护","text":"进屋第一时间开主廊大灯抑制理智衰减，手持测温枪与强光手电巡视各房间，当温度骤降至 5 度以下时即可确定鬼房。"},{"title":"二、猎杀逃生与躲避藏匿点","text":"一旦大门锁死手电闪烁，立刻松开开火键关闭所有电子设备，跑入壁橱将门往内拉，严禁发出任何麦克风噪音！"}]}',
                'PUBLISHED', 3200, 2800, 18, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    # 百科
    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (22, '恐鬼症 24 种幽灵隐藏特性速查大全',
                '1. 恶魔 (Demon)：极其好斗，70% 理智即可主动猎杀，圣木驱逐效果仅持续 60 秒；2. 亡魂 (Revenant)：看到活人时移动速度翻倍至 3.0 m/s，空旷走廊极度致命；3. 巨灵 (Jinn)：配电盘开启时拥有神速冲刺，但靠近玩家时减速；4. 拟魂 (The Mimic)：拥有假幽灵宝珠，能模拟全游戏任何幽灵的行动特性；5. 骚灵 (Poltergeist)：能同时抓起抛出房间内大量杂物，造成大额理智冲击。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 恐鬼症 补全完成 ---")

# ==========================================
# 2. 火线战姬 (Machine Maiden, ID = 23)
# ==========================================
def sync_machine_maiden(cur):
    print("--- 正在补全 火线战姬 (Machine Maiden, game_id = 23) ---")
    gid = 23

    chars = [
        {
            "name": "【赤红天穹】阿斯特丽德 (Astrid)",
            "title": "高机动光刃突击战姬·天际绯红",
            "rarity": 5,
            "element": "等离子高热 (Thermal / Plasma)",
            "weapon_type": "高周波等离子光刃",
            "region": "极光重工·第三战姬近卫军",
            "avatar_url": "https://patchwiki.biligame.com/images/hx/thumb/avatar_astrid.png/120px-avatar_astrid.png",
            "splash_url": "https://patchwiki.biligame.com/images/hx/thumb/avatar_astrid.png/600px-avatar_astrid.png",
            "base_stats": [
                {"level": "1", "hp": 1200, "atk": 180, "def": 75, "energy": 100},
                {"level": "90", "hp": 480000, "atk": 26000, "def": 9500, "energy": 250}
            ],
            "special_ascension_stat": {"stat_name": "推进器过载机动", "values": {"90级": "冲刺速度提升 40%，闪避无敌帧增加 0.25 秒"}},
            "ascension_materials": [{"tier": "机体突破", "items": "超导合金骨架、纳米修复液"}],
            "talents": [
                {"name": "超频光刃弧斩", "type": "NORMAL_ATTACK", "description": "挥舞高周波光刃进行四段光速斩击，并在终结段喷射等离子火焰引发剧烈爆炸！", "scaling": "四段总倍率 620%"},
                {"name": "粒子突进推进 (Dash Thrust)", "type": "ELEMENTAL_SKILL", "description": "推进器全功率爆发向前方瞬移穿刺，击穿路径上一切机械装甲，造成 780% 热能切割伤害并赋予目标【熔甲】状态！", "scaling": "冷却 8 秒，极强位移突进技能"},
                {"name": "天基破晓斩 (Dawn Blade Burst)", "type": "ELEMENTAL_BURST", "description": "拔出身后展开的巨型高能光刃，蓄力跃迁至半空斩下千米裂隙，造成高达 2400% 的核聚变全屏斩灭！", "scaling": "满热量时伤害提升 50%"}
            ],
            "passives": [{"name": "动力回冲", "desc": "击破机械敌兵核心时，立刻恢复 20 点机体能量并降低技能 CD 1 秒。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "粒子突进穿刺切入怪堆 -> 叠满热能槽激活超频状态 -> 释放天基破晓斩核爆清屏！"},
            "recommendations": {"weapons": {"bis": "灭星者等离子光剑"}, "artifacts": {"bis_set": "反物质超导聚能核心套件"}},
            "version": "v1.2"
        },
        {
            "name": "【绝对零度】艾蕾娜 (Elena)",
            "title": "重装防御炮垒战姬·寒霜壁垒",
            "rarity": 5,
            "element": "液氮极寒 (Cryo)",
            "weapon_type": "天基重型动能炮",
            "region": "北方同盟·泰坦要塞",
            "avatar_url": "https://patchwiki.biligame.com/images/hx/thumb/avatar_elena.png/120px-avatar_elena.png",
            "splash_url": "https://patchwiki.biligame.com/images/hx/thumb/avatar_elena.png/600px-avatar_elena.png",
            "base_stats": [
                {"level": "90", "hp": 550000, "atk": 22000, "def": 14000, "energy": 200}
            ],
            "special_ascension_stat": {"stat_name": "力场厚度", "values": {"90级": "能量偏转护盾吸伤量 +50%"}},
            "ascension_materials": [{"tier": "机体突破", "items": "重装复合装甲板"}],
            "talents": [
                {"name": "绝对零度力场", "type": "ELEMENTAL_SKILL", "description": "在脚下展开直径 15 米的冰冻偏转力场，免疫击退击飞并使进入力场的敌兵移动速度降低 70%！", "scaling": "提供全队 40% 减伤护盾"},
                {"name": "极冻灭绝轰击", "type": "ELEMENTAL_BURST", "description": "重炮变形驻锄架设，倾泻三发重型冷冻集束弹，冻结全屏目标 3 秒并造成 1850% 范围伤害！", "scaling": "强力硬控 + 大范围轰炸"}
            ],
            "passives": [{"name": "重型装甲", "desc": "正面受到伤害降低 25%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "展开绝对零度力场提供全队免控减伤 -> 架起重炮进行三发极冻轰击压制 Boss。"},
            "recommendations": {"weapons": {"bis": "天基动能轨道重炮"}, "artifacts": {"bis_set": "重装泰坦复合矩阵"}},
            "version": "v1.2"
        }
    ]

    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                23, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'], c['region'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))

    weaps = [
        {
            "name": "灭星者等离子光剑 (Star-Buster Plasma Blade)",
            "type": "高周波单手光刃",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hx/weapon_star_buster.png",
            "base_atk_curve": [
                {"level": "1", "atk": 180, "crit": 50},
                {"level": "90", "atk": 26000, "crit": 8500}
            ],
            "sub_stat": {"type": "热能超频输出", "values": {"特性": "过热状态下每次斩击额外附带 30% 真实热能伤害"}},
            "refinements": [
                {"rank": 1, "desc": "斩击机械首领时无视其 30% 能量护盾，刀刀切入合金骨架。"}
            ],
            "ascension_materials": [{"tier": "90级升阶", "items": "微型聚变核心"}],
            "version": "v1.2"
        },
        {
            "name": "天基动能轨道重炮 (Orbital Kinetic Cannon)",
            "type": "天基反物质轨道重炮",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hx/weapon_kinetic_cannon.png",
            "base_atk_curve": [
                {"level": "1", "atk": 195, "crit": 35},
                {"level": "90", "atk": 28500, "crit": 6200}
            ],
            "sub_stat": {"type": "重火力破盾", "values": {"特性": "炮弹对能量护盾造成 250% 额外破防伤害"}},
            "refinements": [
                {"rank": 1, "desc": "重炮驻锄形态下蓄力时间减半，弹道初速达到 5 马赫，秒破全图防空掩体。"}
            ],
            "ascension_materials": [{"tier": "90级升阶", "items": "反重力线圈"}],
            "version": "v1.2"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                23, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "反物质超导聚能核心套件 (Antimatter Superconductor Matrix)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hx/set_antimatter.png",
            "two_piece_bonus": "全机甲热能与动能伤害提升 25%。",
            "four_piece_bonus": "进入超频过热状态时，不会进入强制排热硬直，反而获得 10 秒的 40% 攻击力暴击率狂暴增益！",
            "pieces": [
                {"slot": "中央动力舱", "name": "反物质反应炉", "main_stat": "攻击力 +35% / 能量上限 +100"},
                {"slot": "侧翼推进器", "name": "矢量光子翼", "main_stat": "冲刺速度 +25% / 暴击伤害 +50%"}
            ],
            "version": "v1.2"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                23, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "热量算法",
            "title": "火线战姬 机体热量超载与排热冷却惩罚公式",
            "formula": "Heat_Accumulation = Action_Heat_Rate * Time - Passive_Cooling_Rate, Overheat_Threshold = 100",
            "parameters": {
                "overheat": "机体热量在 80~100 区间激活超频增伤，一旦超过 100 触发机体锁死排热 3 秒（无法移动攻击），需精准控温"
            }
        },
        {
            "category": "力场机制",
            "title": "火线战姬 能量偏转力场减伤算法",
            "formula": "Damage_Absorbed = Incoming_Damage * (1 - Shield_Efficiency(70%)), Over_Drain_Penalty = 0.5s Stun",
            "parameters": {
                "shield": "战姬前置力场可吸收高额能量子弹，力场耗尽前战姬本体生命值完全受到保护"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (23, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))
    print("--- 火线战姬 补全完成 ---")

# ==========================================
# 3. DOTA 2 (ID = 5) - 补齐核心神装体系
# ==========================================
def sync_dota2_artifacts(cur):
    print("--- 正在补齐 DOTA 2 (game_id = 5) 神装套装体系 ---")
    arts = [
        {
            "name": "物理爆发核弹神装体系 (Physical Hypercarry Sacred Build)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/dota2/set_rapier.png",
            "two_piece_bonus": "【圣剑 + 黯灭】：攻击力直接提升 410 点，攻击削弱目标 6 点护甲，配合暴击一刀秒杀敌方后排酱油。",
            "four_piece_bonus": "【大炮 + 大雷锤 + 撒旦之邪力】：30% 概率触发 2.4 倍致命一击，开启撒旦 6 秒内获得 175% 极限吸血与强驱散！",
            "pieces": [
                {"slot": "核心攻击武器", "name": "圣剑 (Divine Rapier)", "main_stat": "攻击力 +350 / 死亡必掉落"},
                {"slot": "破甲副手", "name": "黯灭 (Desolator)", "main_stat": "攻击力 +60 / 削甲 -6"},
                {"slot": "暴击神装", "name": "代达罗斯之殇 (Daedalus / 大炮)", "main_stat": "攻击力 +88 / 2.4倍暴击"},
                {"slot": "生存保障", "name": "撒旦之邪力 (Satanic)", "main_stat": "攻击力 +38 / 生命值 +500 / 极限吸血"}
            ],
            "version": "7.37d"
        },
        {
            "name": "全能生存控制魔免套件 (Black King Bar & Blink Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/dota2/set_bkb.png",
            "two_piece_bonus": "【闪烁匕首 + 黑皇杖 (BKB)】：先手 1200 码瞬间切入战场，开启天神下凡魔免 9 秒，免疫一切眩晕减速控制打满输出。",
            "four_piece_bonus": "配合阿哈利姆神杖 (A杖) 与刷新球，技能机制产生终极质变并可连续释放两次团灭级毁天灭地大招！",
            "pieces": [
                {"slot": "切入核心", "name": "闪烁匕首 (Blink Dagger)", "main_stat": "瞬移 1200 码 / 3秒受击冷却"},
                {"slot": "魔免核心", "name": "黑皇杖 (Black King Bar)", "main_stat": "天神下凡魔法免疫 / 攻击力 +24"},
                {"slot": "机制质变", "name": "阿哈利姆神杖 (Aghanim's Scepter)", "main_stat": "全属性 +10 / 生命魔法大幅提升 / 强化大招"}
            ],
            "version": "7.37d"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                5, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))
    print("--- DOTA 2 套装补齐完成 ---")

# ==========================================
# 4. CS2 (ID = 7) - 补齐战术角色定位
# ==========================================
def sync_cs2_characters(cur):
    print("--- 正在补齐 CS2 (game_id = 7) 战术角色定位 ---")
    chars = [
        {
            "name": "战术突破手 (Entry Fragger)",
            "title": "第一枪线·撕裂防线者",
            "rarity": 5,
            "element": "极限急停 / 第一枪爆头",
            "weapon_type": "AK-47 / 加利尔",
            "region": "反恐精英与恐怖分子行动组",
            "avatar_url": "https://patchwiki.biligame.com/images/cs/thumb/avatar_entry.png/120px-avatar_entry.png",
            "splash_url": "https://patchwiki.biligame.com/images/cs/thumb/avatar_entry.png/600px-avatar_entry.png",
            "base_stats": [
                {"level": "职业选手", "hp": 100, "headshot_rate": "68%", "reaction_time": "165ms"}
            ],
            "special_ascension_stat": {"stat_name": "急停准星秒定", "values": {"特长": "拉出掩体瞬间急停第一发命中率 90%"}},
            "ascension_materials": [{"tier": "特训", "items": "Top 20 选手勋章"}],
            "talents": [
                {"name": "预瞄拉枪爆头", "type": "NORMAL_ATTACK", "description": "利用闪光弹掩护大拉出掩体，准心预瞄敌人头部预瞄点，首发子弹 0.18 秒内完成爆头首杀！", "scaling": "AK-47 爆头一枪直接消灭"},
                {"name": "人头互换", "type": "ELEMENTAL_SKILL", "description": "在正面遭遇多个交叉火力时，确保第一时间击杀首个敌人为身后的补枪队友创造 4v4 均势残局。", "scaling": "突破破点核心任务"}
            ],
            "passives": [{"name": "钢铁神经", "desc": "在全白闪光前瞬间背闪，闪光致盲时间减少 60%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "配合队友道具封烟闪光 -> 第一时间大拉清查近点死角 -> 首发爆头撕开包点防线！"},
            "recommendations": {"weapons": {"bis": "AK-47 (爆头140直死)"}, "artifacts": {"bis_set": "防弹衣与头盔套装"}},
            "version": "1.39"
        },
        {
            "name": "残局主点狙击手 (AWPer)",
            "title": "一枪定乾坤·绿宝石死神",
            "rarity": 5,
            "element": "架枪抽靶 / 残局残血博弈",
            "weapon_type": "AWP 重型狙击步枪",
            "region": "经典防守点位 (Mirage / Inferno)",
            "avatar_url": "https://patchwiki.biligame.com/images/cs/thumb/avatar_awper.png/120px-avatar_awper.png",
            "splash_url": "https://patchwiki.biligame.com/images/cs/thumb/avatar_awper.png/600px-avatar_awper.png",
            "base_stats": [
                {"level": "职业狙击手", "hp": 100, "awp_accuracy": "92%", "reaction_time": "150ms"}
            ],
            "special_ascension_stat": {"stat_name": "甩枪架点反应", "values": {"特长": "超短缝隙架枪与瞬镜甩枪"}},
            "ascension_materials": [{"tier": "特训", "items": "Major 锦标赛 MVP"}],
            "talents": [
                {"name": "致命一枪架点 (One-Shot Kill)", "type": "NORMAL_ATTACK", "description": "手持 4750 绿宝石重狙架死过点缝隙，敌人只要露出身躯任何部分（非腿部）直接一枪击毙！", "scaling": "躯干命中 115 伤害直接倒地"},
                {"name": "瞬镜甩枪 (Flick Shot)", "type": "ELEMENTAL_SKILL", "description": "开镜瞬间手腕极速甩动准星，在敌人飞扑拉枪线途中空中直接截杀！", "scaling": "超高难度残局 1v2 翻盘神技"}
            ],
            "passives": [{"name": "冷静心流", "desc": "1v3 残局时听音辨位距离提升 20%，脚步声方位无延迟反馈。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "开局抢占中路架枪首杀 -> 掩护队友转点防守 -> 残局依靠雷包倒计时与烟雾弹完成单人拆包翻盘！"},
            "recommendations": {"weapons": {"bis": "AWP + 沙漠之鹰"}, "artifacts": {"bis_set": "防弹衣与战术投掷物套件"}},
            "version": "1.39"
        }
    ]

    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                7, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'], c['region'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))
    print("--- CS2 战术角色补齐完成 ---")

# ==========================================
# 5. Apex 英雄 (ID = 16) - 补齐护甲套件
# ==========================================
def sync_apex_artifacts(cur):
    print("--- 正在补齐 Apex 英雄 (game_id = 16) 护甲套件 ---")
    arts = [
        {
            "name": "红色进化护盾套装 (Red Evo Shield Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/apex/shield_red.png",
            "two_piece_bonus": "护盾最大容量达到 125 点（全游最高 5 格红甲），总有效生命值提升至 225 点！",
            "four_piece_bonus": "造成 750 点伤害由紫甲进化为红甲，配合绝招加速剂让终极技能冷却加快 35%，对枪容错率天花板。",
            "pieces": [
                {"slot": "身体护甲", "name": "红色进化护甲 (Red Evo Armor)", "main_stat": "护盾容量 125 点 / 伤害进化"},
                {"slot": "生存套件", "name": "凤凰治疗包 (Phoenix Kit)", "main_stat": "10秒满血满甲全部重置"}
            ],
            "version": "Season 23"
        },
        {
            "name": "传奇黄金战术防具套件 (Gold Mythic Armor Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/apex/shield_gold.png",
            "two_piece_bonus": "【金甲】：小型护甲电池和注射器恢复量翻倍（一小电直接回满 2 格甲，2.5秒快速满血反打）。",
            "four_piece_bonus": "【金头 + 金包】：战术技能与绝招冷却大幅缩减 20%，背包装载电池药品弹药数量上限额外提升。",
            "pieces": [
                {"slot": "头部神装", "name": "黄金头盔 (Gold Helmet)", "main_stat": "战术技能与大招 CD 缩短 20%"},
                {"slot": "身体神装", "name": "黄金防弹甲 (Gold Body Shield)", "main_stat": "小电池小注射器恢复效率翻倍"},
                {"slot": "战术背包", "name": "黄金背包 (Gold Backpack)", "main_stat": "大容量物资额外堆叠"}
            ],
            "version": "Season 23"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                16, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))
    print("--- Apex 英雄 护甲套件补齐完成 ---")

# ==========================================
# 6. 云顶之弈 (ID = 19) - 补齐弈子与海克斯
# ==========================================
def sync_tft_missing(cur):
    print("--- 正在补齐 云顶之弈 (game_id = 19) 弈子与海克斯强化体系 ---")
    chars = [
        {
            "name": "大成九五至尊主C弈子 (TFT Fast-9 Carries)",
            "title": "五费全二星·毁天灭地天花板",
            "rarity": 5,
            "element": "魔法与秘术 / 传奇羁绊",
            "weapon_type": "神装成装体系",
            "region": "云顶之弈·S12魔法乱斗",
            "avatar_url": "https://patchwiki.biligame.com/images/lol/item_infinity_edge.png",
            "splash_url": "https://patchwiki.biligame.com/images/lol/item_infinity_edge.png",
            "base_stats": [
                {"level": "1星", "hp": 1100, "atk": 80, "armor": 50, "mr": 50},
                {"level": "2星", "hp": 2200, "atk": 160, "armor": 65, "mr": 65},
                {"level": "3星", "hp": 5000, "atk": 400, "armor": 120, "mr": 120}
            ],
            "special_ascension_stat": {"stat_name": "全屏法术清场", "values": {"全员五费": "技能覆盖全场造成 3000 点毁灭伤害"}},
            "ascension_materials": [{"tier": "运营门槛", "items": "5-2 冲上 9 级并储备 50 金币搜卡"}],
            "talents": [
                {"name": "奥术狂澜全屏清场", "type": "ELEMENTAL_BURST", "description": "打满法力值后倾泻全屏奥术彗星，消灭一切四费未成形阵容！", "scaling": "两星伤害高达 2800 点"}
            ],
            "passives": [{"name": "羁绊联动", "desc": "根据场上五费英雄羁绊，全队获得攻击速度、暴击与全能吸血。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "前期依靠低费强力两星打工连胜吃满 50 利息 -> 4-2 升 8 级保血 -> 5-2 冲 9 级大搜转全员五费！"},
            "recommendations": {"weapons": {"bis": "鬼索的狂暴之刃 + 灭世者的死亡之帽 + 大天使之杖"}, "artifacts": {"bis_set": "棱彩阶海克斯强化套件"}},
            "version": "Set 12"
        }
    ]

    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                19, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'], c['region'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))

    arts = [
        {
            "name": "海克斯科技棱彩强化套件 (Prismatic Hexcore Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/lol/item_infinity_edge.png",
            "two_piece_bonus": "【升级咯！】：购买经验值时额外获得 3 点经验，且最大等级上限提升至 10 级。",
            "four_piece_bonus": "【生日礼物 / 对冲基金】：每回合利息上限翻倍至 10 金币，且每次升级获得一件成装和金币，战力与经济全面拉满。",
            "pieces": [
                {"slot": "棱彩强化", "name": "升级咯！(Level Up!)", "main_stat": "升级消耗减少，直达 10 级"},
                {"slot": "经济强化", "name": "对冲基金 (Hedge Fund)", "main_stat": "利息上限提高至 10 金币"}
            ],
            "version": "Set 12"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                19, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))
    print("--- 云顶之弈 补齐完成 ---")

# ==========================================
# 7. 塞尔达传说：王国之泪 (ID = 3) - 补充深度攻略与百科
# ==========================================
def sync_zelda_guides(cur):
    print("--- 正在补充 塞尔达传说：王国之泪 (game_id = 3) 深度攻略与百科 ---")
    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (3, '王国之泪 蓝图高达与全地形强袭飞行器组装建造实战手册', 1, 'BUILD', 'ADVANCED', '["塞尔达传说", "王国之泪", "究极手", "蓝图", "左纳乌高达", "飞行摩托"]',
                '详解究极手与蓝图高阶实战：两风扇一操纵杆低消耗飞行摩托制作、自动锁定敌人的自律战斗高达设计与大矿石采集路线。',
                '{"sections":[{"title":"一、最省电飞行摩托组装标准","text":"使用 1 个操纵杆和 2 个左纳乌风扇，以 45 度前后倾斜角粘贴对齐，消耗仅 3 格左纳乌能源即可横跨海拉鲁全境与浮空岛。"},{"title":"二、自律战斗高达设计","text":"利用魔像头部配合光线头与大炮，魔像头部会自动瞄准半径 30 米内的白银人马与首领，实现人坐车上、高达自动清场的全自动收割！"}]}',
                'PUBLISHED', 4900, 4400, 35, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (3, '王国之泪 左纳乌装置扭蛋机全地图分布与扭蛋配方百科',
                '1. 左纳乌扭蛋机：遍布海拉鲁空岛与地底，投入魔像角或左纳乌能源即可抽取便携式胶囊；2. 关键装置：翼（滑翔）、风扇机（推进）、操纵杆（精准驾驶转向）、火箭（垂直秒冲）、大炮（高爆破壁开矿）、电池（延长续航）；3. 蓝图系统：地下中央大废矿解锁，可记录多达 30 种历史造物，消耗左纳乌矿石一秒全自动无缝复原！', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 塞尔达传说：王国之泪 补充完成 ---")

# ==========================================
# 主执行入口
# ==========================================
def sync_all():
    print("=== 开始执行全库游戏数据终极补全 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    sync_phasmophobia(cur)
    sync_machine_maiden(cur)
    sync_dota2_artifacts(cur)
    sync_cs2_characters(cur)
    sync_apex_artifacts(cur)
    sync_tft_missing(cur)
    sync_zelda_guides(cur)

    conn.commit()
    conn.close()
    print("=== 全库游戏数据终极补全全部成功落地！ ===")

if __name__ == '__main__':
    sync_all()
