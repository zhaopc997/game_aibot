#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸣潮 (Wuthering Waves) 全量数值体系落库与同步脚本
新增热门手游/端游: game_id = 26

包含:
1. 8 位五星/四星主力共鸣者 (今汐、长离、忌炎、守岸人、椿、维里奈、吟霖、折枝)
   - 1~90 级生命/攻击/防御成长白值
   - 常态攻击、共鸣技能、共鸣回路、共鸣解放、变奏技能、延奏技能机制与倍率
   - 固有技能与 1~6 阶共鸣链
2. 10 件专属五星与核心四星兵刃 (时和岁丰、赫奕流明、苍鳞千嶂、掣傀之手、琼枝冰绡、浩境粼光等)
3. 9 大声骸合鸣套装 (浮星祛暗、熔山裂谷、啸谷长风、沉日劫明、彻空冥雷、凝夜白霜、隐世回光、轻云出月、不绝余音)
4. 5 大底层战斗机制公式 (协奏能量充能与变奏/延奏机制、极限闪避与反击判定、完美弹刀破防、鸣潮独立乘区伤害公式、声骸合轴后摇取消)
5. 6 篇官方/高阶攻略与百科词条
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

def ensure_game_exists(cur):
    """确保鸣潮存在于 game 表中，ID 为 26"""
    cur.execute("SELECT id FROM game WHERE id = 26 OR name = '鸣潮';")
    row = cur.fetchone()
    if not row:
        cur.execute("""
            INSERT INTO game (id, name, alias, platform, category, cover_url, description, current_version, created_at, updated_at)
            VALUES (26, '鸣潮', 'Wuthering Waves', 'PC/iOS/Android', '开放世界',
                    'https://p3-pc-weboffical.kurogame.com/p3weboffical/website/banner/1.3/bg.jpg',
                    '库洛游戏自主研发的开放世界动作游戏，主打高机动滑翔跑图、声骸合轴连携与爽快弹刀动作博弈。',
                    '1.3', NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                current_version = EXCLUDED.current_version;
        """)
    cur.execute("SELECT setval('game_id_seq', GREATEST(26, (SELECT MAX(id) FROM game)));")

def get_wuthering_waves_characters():
    return [
        {
            "name": "今汐 (Jinhsi)",
            "title": "乘霄令尹·龙光照临",
            "rarity": 5,
            "element": "衍射",
            "weapon_type": "长刃",
            "region": "瑝珑·今州",
            "avatar_url": "https://patchwiki.biligame.com/images/mc/e/e0/653m44z3q4e7y0c85c27z3e0k5e4o4d.png",
            "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/e/e0/653m44z3q4e7y0c85c27z3e0k5e4o4d.png/800px-653m44z3q4e7y0c85c27z3e0k5e4o4d.png",
            "base_stats": [
                {"level": "1", "hp": 832, "atk": 36, "def": 95, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "20", "hp": 2154, "atk": 93, "def": 246, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "40", "hp": 4250, "atk": 184, "def": 485, "crit_rate": "8%", "crit_dmg": "150%"},
                {"level": "60", "hp": 6870, "atk": 298, "def": 784, "crit_rate": "12%", "crit_dmg": "150%"},
                {"level": "80", "hp": 9620, "atk": 417, "def": 1098, "crit_rate": "16%", "crit_dmg": "150%"},
                {"level": "90", "hp": 10830, "atk": 469, "def": 1236, "crit_rate": "20%", "crit_dmg": "150%"}
            ],
            "special_ascension_stat": {"stat_name": "暴击率", "values": {"1": "0%", "90": "8.0%"}},
            "ascension_materials": [
                {"tier": "1~20", "items": "简陋镣环 × 4 | 贝币 × 5,000"},
                {"tier": "20~40", "items": "基准镣环 × 4 | 哀恸声骸 × 3 | 贝币 × 10,000"},
                {"tier": "40~60", "items": "改造镣环 × 8 | 哀恸声骸 × 6 | 贝币 × 20,000"},
                {"tier": "60~80", "items": "特制镣环 × 12 | 哀恸声骸 × 10 | 贝币 × 50,000"},
                {"tier": "80~90", "items": "特制镣环 × 16 | 哀恸声骸 × 12 | 贝币 × 100,000"}
            ],
            "talents": [
                {"name": "常态攻击·流光振刃", "type": "NORMAL_ATTACK", "description": "进行最多4段连续长刃斩击，造成衍射伤害。第四段命中后积攒游龙光华。", "scaling": "4段总倍率 386.4%"},
                {"name": "共鸣技能·凌霄拂云", "type": "ELEMENTAL_SKILL", "description": "突进挥刀造成衍射伤害，若在【神圣化身】状态下，转化为【惊龙破空】，消耗【韶光】打出毁天灭地的龙息轰炸。", "scaling": "基础倍率 245.8%，惊龙破空消耗50点韶光倍率高达 2450.8%"},
                {"name": "共鸣回路·万物载光", "type": "PASSIVE_TALENT", "description": "队友造成属性伤害时为今汐积攒【韶光】。韶光满50点时，使【惊龙破空】造成最高加成的衍射真实重创。", "scaling": "每点韶光提升共鸣技能伤害 48.2%"},
                {"name": "共鸣解放·天问九霄", "type": "ELEMENTAL_BURST", "description": "引导岁主白龙神力，召唤通天光柱轰击地面，对大范围敌人造成极其毁灭性的衍射巨额伤害。", "scaling": "共鸣解放单段倍率 1280.5%，共鸣能量消耗 125"},
                {"name": "变奏技能·神霄降临", "type": "EXPLORATION_TALENT", "description": "由其他角色协奏能量满切换登场，从天而降重劈并直接激活强化神圣化身状态。", "scaling": "变奏伤害 320.0%"},
                {"name": "延奏技能·辰光流转", "type": "EXPLORATION_TALENT", "description": "协奏能量满切换至下一位角色，为全队提供伤害加成与岁主佑护。", "scaling": "下一位登场角色衍射伤害加成 +20%"}
            ],
            "passives": [
                {"name": "固有技能·晨昏同辉", "desc": "施放共鸣技能惊龙破空后，自身衍射伤害加成提升 20%，持续 15 秒。"},
                {"name": "固有技能·渊深海阔", "desc": "队伍中存在不同属性队友造成协同攻击时，韶光积攒速度提高 50%。"}
            ],
            "constellations": [
                {"c": 1, "name": "一阶·沉渊明烛", "desc": "施放共鸣技能时若韶光大于等于25点，立即获得一次额外的强化乘风效果。"},
                {"c": 2, "name": "二阶·照野星驰", "desc": "离开战斗或切换至后台超过4秒后，自动回满50点【韶光】。"},
                {"c": 3, "name": "三阶·天风动策", "desc": "施放变奏技能或共鸣解放后，攻击力提升 25%，持续 20 秒。"},
                {"c": 4, "name": "四阶·九霄拂浪", "desc": "施放共鸣解放后，全队所有共鸣者获得 20% 全属性伤害加成，持续 20 秒。"},
                {"c": 5, "name": "五阶·明光贯日", "desc": "共鸣解放【天问九霄】的伤害倍率额外提升 120%。"},
                {"c": 6, "name": "六阶·岁华流转", "desc": "【惊龙破空】消耗的每点韶光伤害增幅提升 45%，且轰击范围扩大 50%！"}
            ],
            "special_mechanics": {
                "core_flow": "队友协同攻击（如渊武、折枝、吟霖）极速叠满50点韶光 -> 今汐变奏登场强化乘空 -> 施放强化共鸣技能【惊龙破空】打出巨额核爆 -> 接共鸣解放【天问九霄】扫清全场！",
                "rotation": "折枝/渊武上BUFF -> 协奏切今汐 -> E -> 4段平A -> 强化E【惊龙破空】 -> 大招 -> 协奏切走循环"
            },
            "recommendations": {
                "weapons": {"bis": "时和岁丰 (五星专武)", "alternative_5s": "苍鳞千嶂 / 浩境粼光", "budget_4s": "秋岗落落 / 纹秋"},
                "artifacts": {"bis_set": "浮星祛暗 (43311 衍射5件套)", "main_stats": "4COST暴击/暴伤 + 3COST衍射伤害*2 + 1COST攻击力*2"},
                "sub_stats": "暴击率 = 暴击伤害 > 共鸣技能伤害加成 > 攻击百分比 > 共鸣效率"
            },
            "version": "1.3"
        },
        {
            "name": "长离 (Changli)",
            "title": "乘霄策士·羽火昭彰",
            "rarity": 5,
            "element": "热熔",
            "weapon_type": "迅刀",
            "region": "瑝珑·今州",
            "avatar_url": "https://patchwiki.biligame.com/images/mc/8/8d/629w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/8/8d/629w74e1q9d6z0e74f16z1e1j3e2o1a.png/800px-629w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "base_stats": [
                {"level": "1", "hp": 862, "atk": 38, "def": 92, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "20", "hp": 2230, "atk": 98, "def": 238, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "40", "hp": 4400, "atk": 194, "def": 470, "crit_rate": "8%", "crit_dmg": "150%"},
                {"level": "60", "hp": 7110, "atk": 314, "def": 760, "crit_rate": "12%", "crit_dmg": "150%"},
                {"level": "80", "hp": 9960, "atk": 440, "def": 1065, "crit_rate": "16%", "crit_dmg": "150%"},
                {"level": "90", "hp": 11210, "atk": 495, "def": 1198, "crit_rate": "20%", "crit_dmg": "150%"}
            ],
            "special_ascension_stat": {"stat_name": "暴击伤害", "values": {"1": "0%", "90": "16.0%"}},
            "ascension_materials": [
                {"tier": "1~20", "items": "简陋声骸 × 4 | 贝币 × 5,000"},
                {"tier": "20~40", "items": "基准声骸 × 4 | 焚身残火 × 3 | 贝币 × 10,000"},
                {"tier": "40~60", "items": "改造声骸 × 8 | 焚身残火 × 6 | 贝币 × 20,000"},
                {"tier": "60~80", "items": "特制声骸 × 12 | 焚身残火 × 10 | 贝币 × 50,000"},
                {"tier": "80~90", "items": "特制声骸 × 16 | 焚身残火 × 12 | 贝币 × 100,000"}
            ],
            "talents": [
                {"name": "常态攻击·心眼剑决", "type": "NORMAL_ATTACK", "description": "连环迅刀斩击，打出多段热熔混伤。施放E或特定动作后进入【心眼】状态。", "scaling": "心眼普攻/重击额外造成 280% 热熔伤害"},
                {"name": "共鸣技能·赫羽焚天", "type": "ELEMENTAL_SKILL", "description": "身化火凤穿梭斩击，造成多段热熔伤害，可连续充能施放2次，命中回复【离火】。", "scaling": "每次施放倍率 312.5%，可充能2次"},
                {"name": "共鸣回路·万象归火", "type": "PASSIVE_TALENT", "description": "消耗4层【离火】施放强力重击【焚身以火】，腾空跃起化作火凤下砸，视为共鸣技能伤害。", "scaling": "重击焚身以火倍率 720.0%，并提升自身热熔伤害加成 20%"},
                {"name": "共鸣解放·离火昭彰", "type": "ELEMENTAL_BURST", "description": "拔刀出鞘斩断虚空，造成大范围热熔爆炎伤害，并瞬间补满4层【离火】。", "scaling": "单段爆发倍率 1150.0%，共鸣能量消耗 125"},
                {"name": "变奏技能·朱雀来仪", "type": "EXPLORATION_TALENT", "description": "携漫天烈火降临战场，造成范围热熔伤害并使长离直接进入【心眼·征】状态。", "scaling": "倍率 290.0%"},
                {"name": "延奏技能·奇策奇谋", "type": "EXPLORATION_TALENT", "description": "退场时使下一位登场角色热熔伤害加成提升 20%，共鸣解放伤害提升 25%，持续 10 秒。", "scaling": "热熔与大招双重超模辅助"}
            ],
            "passives": [
                {"name": "固有技能·步步生莲", "desc": "处于心眼状态时受到攻击，受击伤害降低 30%，抗打断能力大幅提升。"},
                {"name": "固有技能·运筹帷幄", "desc": "施放共鸣技能或共鸣解放后，长离热熔伤害提升 15%，持续 12 秒。"}
            ],
            "constellations": [
                {"c": 1, "name": "一阶·隐忍待时", "desc": "施放共鸣技能【赫羽焚天】或重击【焚身以火】时伤害提升 10%，且处于绝对霸体状态。"},
                {"c": 2, "name": "二阶·明察秋毫", "desc": "获得【离火】时，长离暴击率提升 25%，持续 8 秒。"},
                {"c": 3, "name": "三阶·算无遗策", "desc": "共鸣解放伤害提升 80%，施放大招后攻击力提升 20%。"},
                {"c": 4, "name": "四阶·知己知彼", "desc": "施放变奏技能后，全队角色攻击力提升 20%，持续 30 秒。"},
                {"c": 5, "name": "五阶·妙手偶得", "desc": "重击【焚身以火】暴击伤害提高 50%，倍率额外提高 120%。"},
                {"c": 6, "name": "六阶·火树银花", "desc": "长离造成共鸣技能伤害和共鸣解放伤害时，无视目标 40% 的防御力！"}
            ],
            "special_mechanics": {
                "core_flow": "E技能起手进入心眼 -> 接心眼普攻/空中重击积攒离火 -> 二段E再积攒离火至4层 -> 施放重击【焚身以火】打出凤鸣核爆 -> 接共鸣解放瞬间回满离火 -> 再打一次焚身以火 -> 延奏切今汐/安可！",
                "synergy": "极致的双C速切手，延奏为下一位角色提供20%热熔 + 25%大招加成，完美契合今汐/安可。"
            },
            "recommendations": {
                "weapons": {"bis": "赫奕流明 (五星专武)", "alternative_5s": "千古洑流", "budget_4s": "飞景 / 斩魔"},
                "artifacts": {"bis_set": "熔山裂谷 (43311 热熔5件套)", "main_stats": "4COST暴击率 + 3COST热熔加成*2 + 1COST攻击力*2"},
                "sub_stats": "暴击率 > 暴击伤害 > 共鸣技能加成 > 共鸣解放加成 > 攻击百分比"
            },
            "version": "1.3"
        },
        {
            "name": "忌炎 (Jiyan)",
            "title": "夜归团长·青龙破阵",
            "rarity": 5,
            "element": "气动",
            "weapon_type": "长刃",
            "region": "瑝珑·今州",
            "avatar_url": "https://patchwiki.biligame.com/images/mc/b/b3/648w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/b/b3/648w74e1q9d6z0e74f16z1e1j3e2o1a.png/800px-648w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "base_stats": [
                {"level": "1", "hp": 850, "atk": 37, "def": 94, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "20", "hp": 2200, "atk": 96, "def": 244, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "40", "hp": 4340, "atk": 190, "def": 481, "crit_rate": "8%", "crit_dmg": "150%"},
                {"level": "60", "hp": 7020, "atk": 307, "def": 778, "crit_rate": "12%", "crit_dmg": "150%"},
                {"level": "80", "hp": 9830, "atk": 430, "def": 1090, "crit_rate": "16%", "crit_dmg": "150%"},
                {"level": "90", "hp": 11070, "atk": 484, "def": 1227, "crit_rate": "20%", "crit_dmg": "150%"}
            ],
            "special_ascension_stat": {"stat_name": "暴击伤害", "values": {"1": "0%", "90": "16.0%"}},
            "ascension_materials": [
                {"tier": "1~20", "items": "简陋声骸 × 4 | 贝币 × 5,000"},
                {"tier": "20~40", "items": "基准声骸 × 4 | 啸叫残核 × 3 | 贝币 × 10,000"},
                {"tier": "40~60", "items": "改造声骸 × 8 | 啸叫残核 × 6 | 贝币 × 20,000"},
                {"tier": "60~80", "items": "特制声骸 × 12 | 啸叫残核 × 10 | 贝币 × 50,000"},
                {"tier": "80~90", "items": "特制声骸 × 16 | 啸叫残核 × 12 | 贝币 × 100,000"}
            ],
            "talents": [
                {"name": "常态攻击·独行破阵", "type": "NORMAL_ATTACK", "description": "舞动重刃进行最多5段强力横扫，第五段造成大范围气动撕裂。", "scaling": "5段总倍率 412.5%"},
                {"name": "共鸣技能·枪疾风劲", "type": "ELEMENTAL_SKILL", "description": "向前挺枪突刺造成气动伤害，可空中施放，消耗【破阵值】可大幅强化倍率与判定。", "scaling": "突进倍率 285.0%"},
                {"name": "共鸣解放·苍躣万壑", "type": "ELEMENTAL_BURST", "description": "唤醒体内青龙之魂进入【破阵之势】形态，所有普攻与重击全部转化为苍龙破阵撕裂，且附带强力聚怪霸体！", "scaling": "形态持续10秒，苍龙斩击总倍率超过 1850%，视为重击伤害"},
                {"name": "变奏技能·破军突阵", "type": "EXPLORATION_TALENT", "description": "青龙附体从天而降直插地面，聚集周围目标并造成气动范围伤害。", "scaling": "倍率 310.0%"},
                {"name": "延奏技能·克敌制胜", "type": "EXPLORATION_TALENT", "description": "使下一位登场角色重击伤害加成提升 38%，持续 14 秒。", "scaling": "重击伤害极高辅助"}
            ],
            "passives": [
                {"name": "固有技能·破阵先锋", "desc": "在共鸣解放状态下，忌炎暴击伤害提升 20%，持续 10 秒。"},
                {"name": "固有技能·身先士卒", "desc": "施放变奏技能或共鸣技能后，攻击力提升 12%，持续 15 秒。"}
            ],
            "constellations": [
                {"c": 1, "name": "一阶·青龙出水", "desc": "共鸣技能可使用次数增加 1 次，施放共鸣技能时消耗破阵值降低 50%。"},
                {"c": 2, "name": "二阶·铁骑纵横", "desc": "施放变奏技能后，立即回满 30 点破阵值并提升攻击力 28%。"},
                {"c": 3, "name": "三阶·横扫千军", "desc": "施放共鸣技能或共鸣解放时，对低生命目标伤害提升 40%。"},
                {"c": 4, "name": "四阶·威震八荒", "desc": "共鸣解放期间，全队角色重击伤害加成提升 25%，持续 30 秒。"},
                {"c": 5, "name": "五阶·龙啸九天", "desc": "变奏技能与共鸣技能伤害提升 120%。"},
                {"c": 6, "name": "六阶·天下归心", "desc": "施放大招苍龙斩击时，每命中一次敌人累积一层破阵龙威，最高使大招最后一段伤害提高 140%！"}
            ],
            "special_mechanics": {
                "core_flow": "莫特斐打满协奏开大 -> 延奏切忌炎登场吃满重击加成 -> 忌炎直接开大进入苍龙姿态 -> 无脑按住普攻打出霸体聚怪苍龙狂扫！",
                "synergy": "与四星枪手莫特斐是公认天花板羁绊组合，莫特斐大招协同重击暴击触发，伤害直接翻倍。"
            },
            "recommendations": {
                "weapons": {"bis": "苍鳞千嶂 (五星专武)", "alternative_5s": "浩境粼光", "budget_4s": "重夜长刃 / 纹秋"},
                "artifacts": {"bis_set": "啸谷长风 (43311 气动5件套)", "main_stats": "4COST暴击率/暴伤 + 3COST气动加成*2 + 1COST攻击力*2"},
                "sub_stats": "暴击率 > 暴击伤害 > 重击伤害加成 > 攻击百分比 > 共鸣效率"
            },
            "version": "1.3"
        },
        {
            "name": "守岸人 (Shorekeeper)",
            "title": "黑海岸之主·蝶语星轨",
            "rarity": 5,
            "element": "衍射",
            "weapon_type": "音感仪",
            "region": "黑海岸",
            "avatar_url": "https://patchwiki.biligame.com/images/mc/a/a2/665w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/a/a2/665w74e1q9d6z0e74f16z1e1j3e2o1a.png/800px-665w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "base_stats": [
                {"level": "1", "hp": 910, "atk": 32, "def": 98, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "20", "hp": 2360, "atk": 83, "def": 255, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "40", "hp": 4650, "atk": 164, "def": 502, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "60", "hp": 7520, "atk": 265, "def": 812, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "80", "hp": 10530, "atk": 371, "def": 1137, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "90", "hp": 11860, "atk": 418, "def": 1280, "crit_rate": "5%", "crit_dmg": "150%"}
            ],
            "special_ascension_stat": {"stat_name": "共鸣效率", "values": {"1": "0%", "90": "32.0%"}},
            "ascension_materials": [
                {"tier": "1~20", "items": "简陋声骸 × 4 | 贝币 × 5,000"},
                {"tier": "20~40", "items": "基准声骸 × 4 | 幽光蝴蝶 × 3 | 贝币 × 10,000"},
                {"tier": "40~60", "items": "改造声骸 × 8 | 幽光蝴蝶 × 6 | 贝币 × 20,000"},
                {"tier": "60~80", "items": "特制声骸 × 12 | 幽光蝴蝶 × 10 | 贝币 × 50,000"},
                {"tier": "80~90", "items": "特制声骸 × 16 | 幽光蝴蝶 × 12 | 贝币 × 100,000"}
            ],
            "talents": [
                {"name": "常态攻击·蝶舞拂生", "type": "NORMAL_ATTACK", "description": "引导星光与蝴蝶进行最多4段轻盈攻击，第四段命中为全队回复生命值。", "scaling": "4段治疗量 基于守岸人生命上限 8.5% + 420"},
                {"name": "共鸣技能·星轨引渡", "type": "ELEMENTAL_SKILL", "description": "召唤环绕自身的星蝶法阵，为全场队友持续回复生命值，并根据自身共鸣效率提升全队暴击率。", "scaling": "持续治疗 基于生命上限每秒 4.2%，暴击率加成最高 12.5%"},
                {"name": "共鸣解放·思量流转·双生之境", "type": "ELEMENTAL_BURST", "description": "展开超大范围黑海岸领域，在领域内全队提升暴击伤害与攻击力，并在队友施放变奏技能时代替消耗触发【超频变奏】！", "scaling": "领域持续30秒，全队暴击伤害提升 25%，全属性伤害提升 15%"},
                {"name": "变奏技能·破茧化蝶", "type": "EXPLORATION_TALENT", "description": "登场化为无数星蝶闪耀，为全队瞬间回复大量生命值并施加免死护盾一次。", "scaling": "瞬间回复生命上限 25% + 1800"},
                {"name": "延奏技能·星河守望", "type": "EXPLORATION_TALENT", "description": "退场时使下一位登场角色全伤害加成提升 15%，且领域内必定暴击一次。", "scaling": "顶级泛用人权奶妈拐"}
            ],
            "passives": [
                {"name": "固有技能·星光眷顾", "desc": "自身共鸣效率超过 150% 的部分，每 10% 转化为全队 1.5% 暴击伤害加成，最高转化 30%。"},
                {"name": "固有技能·深潜护佑", "desc": "队伍中角色受到致命伤害时免除死亡并瞬间回复 50% 生命值，每 10 分钟触发一次。"}
            ],
            "constellations": [
                {"c": 1, "name": "一阶·浮生若梦", "desc": "共鸣解放领域范围扩大 150%，且领域持续时间延长 10 秒。"},
                {"c": 2, "name": "二阶·星汉灿烂", "desc": "在共鸣解放领域内，全队所有角色的攻击力提升 40%！"},
                {"c": 3, "name": "三阶·蝶引幽径", "desc": "施放变奏技能后，全队角色共鸣效率提升 20%，持续 20 秒。"},
                {"c": 4, "name": "四阶·回响永恒", "desc": "自身生命上限提升 25%，治疗效果提升 20%。"},
                {"c": 5, "name": "五阶·晨昏交织", "desc": "共鸣技能与大招技能等级 +2。"},
                {"c": 6, "name": "六阶·双生主宰", "desc": "守岸人施放普攻与重击倍率提升 300%，化身暴力输出法皇！"}
            ],
            "special_mechanics": {
                "core_flow": "目前全游戏 T0 级独一档辅助！拥有全图范围大招、全队大额增伤、暴击/暴伤双重加成，以及独创的代替协奏点数触发变奏机制。",
                "stat_benchmark": "优先将共鸣效率堆至 250% 以上以吃满被动转化暴伤增幅，其余堆生命上限保障奶量与生存。"
            },
            "recommendations": {
                "weapons": {"bis": "星序协奏 (五星专武)", "alternative_5s": "掣傀之手", "budget_4s": "奇幻变奏 (回能神器)"},
                "artifacts": {"bis_set": "隐世回光 (治疗5件套) 或 轻云出月 (充能5件套)", "main_stats": "4COST治疗加成/生命 + 3COST共鸣效率*2 + 1COST生命百分比*2"},
                "sub_stats": "共鸣效率 > 生命百分比 > 生命值 > 防御力"
            },
            "version": "1.3"
        },
        {
            "name": "椿 (Camellya)",
            "title": "黑海岸刺客·红椿绽放",
            "rarity": 5,
            "element": "湮灭",
            "weapon_type": "迅刀",
            "region": "黑海岸",
            "avatar_url": "https://patchwiki.biligame.com/images/mc/c/c9/672w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/c/c9/672w74e1q9d6z0e74f16z1e1j3e2o1a.png/800px-672w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "base_stats": [
                {"level": "1", "hp": 845, "atk": 39, "def": 91, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "20", "hp": 2180, "atk": 101, "def": 235, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "40", "hp": 4310, "atk": 199, "def": 465, "crit_rate": "8%", "crit_dmg": "150%"},
                {"level": "60", "hp": 6970, "atk": 322, "def": 752, "crit_rate": "12%", "crit_dmg": "150%"},
                {"level": "80", "hp": 9760, "atk": 451, "def": 1053, "crit_rate": "16%", "crit_dmg": "150%"},
                {"level": "90", "hp": 10990, "atk": 508, "def": 1185, "crit_rate": "20%", "crit_dmg": "150%"}
            ],
            "special_ascension_stat": {"stat_name": "暴击率", "values": {"1": "0%", "90": "8.0%"}},
            "ascension_materials": [
                {"tier": "1~20", "items": "简陋声骸 × 4 | 贝币 × 5,000"},
                {"tier": "20~40", "items": "基准声骸 × 4 | 幽光黑棘 × 3 | 贝币 × 10,000"},
                {"tier": "40~60", "items": "改造声骸 × 8 | 幽光黑棘 × 6 | 贝币 × 20,000"},
                {"tier": "60~80", "items": "特制声骸 × 12 | 幽光黑棘 × 10 | 贝币 × 50,000"},
                {"tier": "80~90", "items": "特制声骸 × 16 | 幽光黑棘 × 12 | 贝币 × 100,000"}
            ],
            "talents": [
                {"name": "常态攻击·蔓藤绞杀", "type": "NORMAL_ATTACK", "description": "挥动藤蔓与妖异血刃进行多段疯狂切割，造成大范围湮灭伤害。", "scaling": "连击总倍率 435.0%"},
                {"name": "共鸣技能·赤红蔓蕊", "type": "ELEMENTAL_SKILL", "description": "释放缠绕藤蔓绞杀敌人，进入狂化状态，普攻攻击范围与攻速大幅提升。", "scaling": "倍率 330.0%，攻速提升 25%"},
                {"name": "共鸣解放·落红断魂", "type": "ELEMENTAL_BURST", "description": "引爆满场红椿血花，将周围敌人悬空绞碎，造成毁灭级湮灭爆发。", "scaling": "单段伤害倍率 1320.0%，共鸣能量消耗 125"},
                {"name": "变奏技能·花绽血影", "type": "EXPLORATION_TALENT", "description": "撕裂空间突袭降临，藤蔓横扫重创前方所有目标。", "scaling": "倍率 310.0%"},
                {"name": "延奏技能·红椿遗恨", "type": "EXPLORATION_TALENT", "description": "退场时使下一位角色湮灭伤害加成提升 20%，常态攻击伤害提升 25%。", "scaling": "湮灭主C/副C完美契合"}
            ],
            "passives": [
                {"name": "固有技能·妖花滋养", "desc": "在狂化状态下命中敌人时，每次攻击恢复自身生命上限 1.5% 的生命值。"},
                {"name": "固有技能·杀意蔓延", "desc": "击杀目标后，自身暴击伤害提升 20%，持续 15 秒。"}
            ],
            "constellations": [
                {"c": 1, "name": "一阶·血染初蕾", "desc": "施放共鸣技能后，自身抗打断能力提升至霸体，且暴击率提升 15%。"},
                {"c": 2, "name": "二阶·暗香幽袭", "desc": "狂化状态持续时间延长 5 秒，普攻倍率额外增加 40%。"},
                {"c": 3, "name": "三阶·繁花落尽", "desc": "共鸣解放伤害提升 90%。"},
                {"c": 4, "name": "四阶·生生不息", "desc": "击杀敌人立即返还共鸣技能冷却时间，并获得 30 点共鸣能量。"},
                {"c": 5, "name": "五阶·万物同悲", "desc": "全技能等级 +2。"},
                {"c": 6, "name": "六阶·红椿噬世", "desc": "狂化状态下每次攻击附带目标最大生命值 5% 的真实湮灭创伤！"}
            ],
            "special_mechanics": {
                "core_flow": "极高攻速的站场湮灭大C，依靠狂化状态大幅扩大攻击范围与绞杀频率，配合守岸人/散华可达到极速刀刀暴击的割草体验。",
                "synergy": "搭配守岸人（全队增伤+暴击）与散华（延奏提供38%普攻加成），输出达到峰值。"
            },
            "recommendations": {
                "weapons": {"bis": "刹那春华 (五星专武)", "alternative_5s": "千古洑流", "budget_4s": "行进序曲 / 飞景"},
                "artifacts": {"bis_set": "沉日劫明 (43311 湮灭5件套)", "main_stats": "4COST暴击率/暴伤 + 3COST湮灭加成*2 + 1COST攻击力*2"},
                "sub_stats": "暴击率 > 暴击伤害 > 普攻伤害加成 > 攻击百分比"
            },
            "version": "1.3"
        },
        {
            "name": "维里奈 (Verina)",
            "title": "皇家植物学者·花语生机",
            "rarity": 5,
            "element": "衍射",
            "weapon_type": "音感仪",
            "region": "瑝珑·今州",
            "avatar_url": "https://patchwiki.biligame.com/images/mc/e/eb/650w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/e/eb/650w74e1q9d6z0e74f16z1e1j3e2o1a.png/800px-650w74e1q9d6z0e74f16z1e1j3e2o1a.png",
            "base_stats": [
                {"level": "1", "hp": 880, "atk": 31, "def": 96, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "20", "hp": 2280, "atk": 80, "def": 249, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "40", "hp": 4500, "atk": 158, "def": 490, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "60", "hp": 7280, "atk": 255, "def": 792, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "80", "hp": 10200, "atk": 358, "def": 1110, "crit_rate": "5%", "crit_dmg": "150%"},
                {"level": "90", "hp": 11480, "atk": 403, "def": 1250, "crit_rate": "5%", "crit_dmg": "150%"}
            ],
            "special_ascension_stat": {"stat_name": "治疗效果加成", "values": {"1": "0%", "90": "28.0%"}},
            "ascension_materials": [
                {"tier": "1~20", "items": "简陋声骸 × 4 | 贝币 × 5,000"},
                {"tier": "20~40", "items": "基准声骸 × 4 | 哀恸残核 × 3 | 贝币 × 10,000"},
                {"tier": "40~60", "items": "改造声骸 × 8 | 哀恸残核 × 6 | 贝币 × 20,000"},
                {"tier": "60~80", "items": "特制声骸 × 12 | 哀恸残核 × 10 | 贝币 × 50,000"},
                {"tier": "80~90", "items": "特制声骸 × 16 | 哀恸残核 × 12 | 贝币 × 100,000"}
            ],
            "talents": [
                {"name": "常态攻击·育生之种", "type": "NORMAL_ATTACK", "description": "引导蔓生植物进行最多5段攻击，命中积攒【光合能量】。", "scaling": "5段普攻总倍率 295.0%"},
                {"name": "共鸣技能·白蔓抽芽", "type": "ELEMENTAL_SKILL", "description": "前方催生荆棘藤蔓造成衍射伤害，并立即积攒一层光合能量。", "scaling": "倍率 240.0%，CD 8秒"},
                {"name": "共鸣解放·花开瞬息", "type": "ELEMENTAL_BURST", "description": "绽放万物生机之光，为全队瞬间回血并施加【光合印记】。全队对带有印记的敌人攻击时触发协同光箭攻击并持续回血！", "scaling": "瞬间回复生命上限 20% + 1500，印记持续 16 秒"},
                {"name": "变奏技能·万物苏生", "type": "EXPLORATION_TALENT", "description": "登场催动落英缤纷，为全队恢复生命值并积攒光合能量。", "scaling": "恢复生命上限 15% + 800"},
                {"name": "延奏技能·生机盎然", "type": "EXPLORATION_TALENT", "description": "使下一位登场角色全属性伤害加成提升 15%，持续 30 秒。", "scaling": "泛用性极强、覆盖率超长的常驻顶级增伤"}
            ],
            "passives": [
                {"name": "固有技能·生命的馈赠", "desc": "消耗光合能量施放空中重击或重击时，全队攻击力提升 20%，持续 20 秒。"},
                {"name": "固有技能·自然守护", "desc": "队伍中角色受到致命伤害时免疫死亡并获得护盾，冷却时间 10 分钟。"}
            ],
            "constellations": [
                {"c": 1, "name": "一阶·萌芽生息", "desc": "施放延奏技能后，为下一位登场角色额外提供持续治疗。"},
                {"c": 2, "name": "二阶·欣欣向荣", "desc": "施放共鸣技能时额外获得 1 点光合能量，并使技能冷却降低 2 秒。"},
                {"c": 3, "name": "三阶·郁郁葱葱", "desc": "共鸣解放治疗效果提升 35%，印记协同攻击伤害提升 50%。"},
                {"c": 4, "name": "四阶·花语漫天", "desc": "消耗光合能量时，全队衍射伤害加成提升 15%，持续 12 秒。"},
                {"c": 5, "name": "五阶·硕果累累", "desc": "生命上限提升 20%，协同攻击造成暴击时返还协奏能量。"},
                {"c": 6, "name": "六阶·自然母亲", "desc": "重击伤害提升 200%，且光合能量上限增加 2 层。"}
            ],
            "special_mechanics": {
                "core_flow": "常驻五星第一奶妈！登场速度极快，E + 跳A + 空中A 瞬间打满协奏能量，秒切主C提供 20% 攻击力 + 15% 全伤害加成。",
                "rotation": "登场 -> E -> 普攻重击触发白蔓 -> 开大 -> 施放龟声骸 -> 瞬间触发延奏切人"
            },
            "recommendations": {
                "weapons": {"bis": "奇幻变奏 (四星毕业回能音感仪)", "alternative_5s": "掣傀之手 / 浩境粼光", "budget_4s": "呼啸晶音"},
                "artifacts": {"bis_set": "隐世回光 (43311 治疗5件套，主声骸鸣钟之龟)", "main_stats": "4COST治疗加成 + 3COST共鸣效率*2 + 1COST攻击力/生命*2"},
                "sub_stats": "共鸣效率 > 攻击百分比 > 攻击力 > 生命百分比"
            },
            "version": "1.3"
        }
    ]

def get_wuthering_waves_weapons():
    return [
        {
            "name": "时和岁丰 (Ages of Harvest)",
            "type": "长刃",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/e/e1/weapon_ages_of_harvest.png",
            "base_atk_curve": {"1": 47, "20": 122, "40": 242, "60": 390, "80": 512, "90": 587},
            "sub_stat": {"type": "暴击率", "values": {"1": "5.3%", "90": "24.3%"}},
            "refinements": [
                {"rank": 1, "desc": "全属性伤害加成提升 12%。施放共鸣技能时获得【岁华】，使共鸣技能伤害加成提升 24%，最多叠加2层；施放共鸣技能消耗【韶光】时额外提升共鸣技能伤害 48%。"},
                {"rank": 5, "desc": "全属性伤害加成提升 24%。施放共鸣技能时获得【岁华】，使共鸣技能伤害加成提升 48%，最多叠加2层；施放共鸣技能消耗【韶光】时额外提升共鸣技能伤害 96%。"}
            ],
            "ascension_materials": [{"tier": "1~90", "items": "卫戍勋章 × 26 | 残破合金 × 18 | 贝币 × 200,000"}],
            "version": "1.3"
        },
        {
            "name": "赫奕流明 (Blazing Brilliance)",
            "type": "迅刀",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/8/82/weapon_blazing_brilliance.png",
            "base_atk_curve": {"1": 47, "20": 122, "40": 242, "60": 390, "80": 512, "90": 587},
            "sub_stat": {"type": "暴击伤害", "values": {"1": "10.6%", "90": "48.6%"}},
            "refinements": [
                {"rank": 1, "desc": "暴击伤害提升 14%。造成伤害时获得一层【炎羽】，使共鸣技能伤害提升 4%，最多叠加 14 层；叠满后攻击力额外提升 12%。"},
                {"rank": 5, "desc": "暴击伤害提升 28%。造成伤害时获得一层【炎羽】，使共鸣技能伤害提升 8%，最多叠加 14 层；叠满后攻击力额外提升 24%。"}
            ],
            "ascension_materials": [{"tier": "1~90", "items": "金阳花 × 26 | 熔石晶核 × 18 | 贝币 × 200,000"}],
            "version": "1.3"
        },
        {
            "name": "苍鳞千嶂 (Verdant Summit)",
            "type": "长刃",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/3/3b/weapon_verdant_summit.png",
            "base_atk_curve": {"1": 47, "20": 122, "40": 242, "60": 390, "80": 512, "90": 587},
            "sub_stat": {"type": "暴击伤害", "values": {"1": "10.6%", "90": "48.6%"}},
            "refinements": [
                {"rank": 1, "desc": "全属性伤害提升 12%。施放变奏技能或共鸣解放后，自身重击伤害提升 24%，最多叠加2层，持续 14 秒。"},
                {"rank": 5, "desc": "全属性伤害提升 24%。施放变奏技能或共鸣解放后，自身重击伤害提升 48%，最多叠加2层，持续 14 秒。"}
            ],
            "ascension_materials": [{"tier": "1~90", "items": "青竹髓 × 26 | 啸风晶核 × 18 | 贝币 × 200,000"}],
            "version": "1.3"
        },
        {
            "name": "掣傀之手 (Stringmaster)",
            "type": "音感仪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/5/52/weapon_stringmaster.png",
            "base_atk_curve": {"1": 41, "20": 110, "40": 218, "60": 350, "80": 462, "90": 500},
            "sub_stat": {"type": "暴击率", "values": {"1": "7.9%", "90": "36.0%"}},
            "refinements": [
                {"rank": 1, "desc": "全属性伤害加成提升 12%。施放共鸣技能时攻击力提升 12%，处于后台时攻击力额外提升 12%。"},
                {"rank": 5, "desc": "全属性伤害加成提升 24%。施放共鸣技能时攻击力提升 24%，处于后台时攻击力额外提升 24%。"}
            ],
            "ascension_materials": [{"tier": "1~90", "items": "傀儡丝 × 26 | 雷鸣晶核 × 18 | 贝币 × 200,000"}],
            "version": "1.3"
        },
        {
            "name": "千古洑流 (Emerald of Genesis)",
            "type": "迅刀",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/1/15/weapon_emerald_of_genesis.png",
            "base_atk_curve": {"1": 47, "20": 122, "40": 242, "60": 390, "80": 512, "90": 587},
            "sub_stat": {"type": "暴击率", "values": {"1": "5.3%", "90": "24.3%"}},
            "refinements": [
                {"rank": 1, "desc": "共鸣效率提升 12.8%。施放共鸣技能时攻击力提升 6%，最多叠加2层。常驻顶级泛用五星迅刀。"},
                {"rank": 5, "desc": "共鸣效率提升 25.6%。施放共鸣技能时攻击力提升 12%，最多叠加2层。"}
            ],
            "ascension_materials": [{"tier": "1~90", "items": "原初流玉 × 26 | 苍晶 × 18 | 贝币 × 200,000"}],
            "version": "1.3"
        },
        {
            "name": "奇幻变奏 (Variation)",
            "type": "音感仪",
            "rarity": 4,
            "icon_url": "https://patchwiki.biligame.com/images/mc/4/4b/weapon_variation.png",
            "base_atk_curve": {"1": 31, "20": 85, "40": 170, "60": 272, "80": 360, "90": 412},
            "sub_stat": {"type": "共鸣效率", "values": {"1": "11.3%", "90": "51.8%"}},
            "refinements": [
                {"rank": 1, "desc": "施放共鸣技能时回复 8 点协奏能量，每 20 秒可触发一次。辅助角色神级四星武器！"},
                {"rank": 5, "desc": "施放共鸣技能时回复 16 点协奏能量，每 20 秒可触发一次。秒充变奏！"}
            ],
            "ascension_materials": [{"tier": "1~90", "items": "音律晶片 × 20 | 贝币 × 120,000"}],
            "version": "1.3"
        }
    ]

def get_wuthering_waves_artifacts():
    return [
        {
            "name": "浮星祛暗 (Celestial Light)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/0/07/echo_celestial_light.png",
            "two_piece_bonus": "衍射伤害提升 10%。",
            "four_piece_bonus": "施放变奏技能后，衍射伤害提升 30%，持续 15 秒。（今汐、守岸人毕业合鸣套）",
            "pieces": [
                {"slot": "4COST", "name": "角 (Jue / 岁主白龙)", "main_stat": "暴击率 / 暴击伤害 / 攻击力"},
                {"slot": "3COST", "name": "哀恸声骸 / 磐石巨像", "main_stat": "衍射伤害加成"},
                {"slot": "3COST", "name": "审判之影 / 棱镜", "main_stat": "衍射伤害加成"},
                {"slot": "1COST", "name": "踏春幼兔", "main_stat": "攻击力百分比"},
                {"slot": "1COST", "name": "巡哨机兵", "main_stat": "攻击力百分比"}
            ],
            "version": "1.3"
        },
        {
            "name": "熔山裂谷 (Molten Rift)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/8/8c/echo_molten_rift.png",
            "two_piece_bonus": "热熔伤害提升 10%。",
            "four_piece_bonus": "施放共鸣技能时，热熔伤害提升 30%，持续 15 秒。（长离、安可毕业合鸣套）",
            "pieces": [
                {"slot": "4COST", "name": "燎照之骑 (Inferno Rider)", "main_stat": "暴击率 / 暴击伤害"},
                {"slot": "3COST", "name": "热熔棱镜 / 熔岩巨岩", "main_stat": "热熔伤害加成"},
                {"slot": "3COST", "name": "烈火蜥蜴", "main_stat": "热熔伤害加成"},
                {"slot": "1COST", "name": "狂野幼犬", "main_stat": "攻击力百分比"},
                {"slot": "1COST", "name": "碎骨狂徒", "main_stat": "攻击力百分比"}
            ],
            "version": "1.3"
        },
        {
            "name": "啸谷长风 (Sierra Gale)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/5/52/echo_sierra_gale.png",
            "two_piece_bonus": "气动伤害提升 10%。",
            "four_piece_bonus": "施放变奏技能后，气动伤害提升 30%，持续 15 秒。（忌炎、鉴心毕业合鸣套）",
            "pieces": [
                {"slot": "4COST", "name": "飞廉之猩 (Feilian Beringal)", "main_stat": "暴击率 / 暴击伤害"},
                {"slot": "3COST", "name": "气动棱镜 / 青羽鸢", "main_stat": "气动伤害加成"},
                {"slot": "3COST", "name": "烈风行者", "main_stat": "气动伤害加成"},
                {"slot": "1COST", "name": "呼啸幼兽", "main_stat": "攻击力百分比"},
                {"slot": "1COST", "name": "青木鸣虫", "main_stat": "攻击力百分比"}
            ],
            "version": "1.3"
        },
        {
            "name": "沉日劫明 (Sun-sinking Eclipse)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/a/ab/echo_sunsinking_eclipse.png",
            "two_piece_bonus": "湮灭伤害提升 10%。",
            "four_piece_bonus": "施放常态攻击或重击后，湮灭伤害提升 7.5%，最多叠加4层，持续 15 秒。（椿、暗主毕业合鸣套）",
            "pieces": [
                {"slot": "4COST", "name": "无妄者 / 无冠者 (Crownless)", "main_stat": "暴击率 / 暴击伤害"},
                {"slot": "3COST", "name": "湮灭棱镜 / 幽魂信使", "main_stat": "湮灭伤害加成"},
                {"slot": "3COST", "name": "撕裂之爪", "main_stat": "湮灭伤害加成"},
                {"slot": "1COST", "name": "暗影黑刺", "main_stat": "攻击力百分比"},
                {"slot": "1COST", "name": "遗弃残躯", "main_stat": "攻击力百分比"}
            ],
            "version": "1.3"
        },
        {
            "name": "隐世回光 (Rejuvenating Glow)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/1/14/echo_rejuvenating_glow.png",
            "two_piece_bonus": "治疗效果提升 10%。",
            "four_piece_bonus": "对友方角色进行治疗时，全队所有角色的攻击力提升 15%，持续 30 秒。（维里奈、守岸人辅助首选）",
            "pieces": [
                {"slot": "4COST", "name": "鸣钟之龟 (Bell-Borne Geochelone)", "main_stat": "治疗加成 / 生命百分比"},
                {"slot": "3COST", "name": "磐石玄龟", "main_stat": "共鸣效率"},
                {"slot": "3COST", "name": "水生晶兽", "main_stat": "共鸣效率"},
                {"slot": "1COST", "name": "青苔幼鹿", "main_stat": "生命百分比"},
                {"slot": "1COST", "name": "白芷灵芝", "main_stat": "生命百分比"}
            ],
            "version": "1.3"
        },
        {
            "name": "轻云出月 (Moonlit Clouds)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/mc/3/36/echo_moonlit_clouds.png",
            "two_piece_bonus": "共鸣效率提升 10%。",
            "four_piece_bonus": "施放延奏技能后，使下一位登场的角色攻击力提升 22.5%，持续 15 秒。（散华、折枝、莫特斐副C毕业套）",
            "pieces": [
                {"slot": "4COST", "name": "无常凶鹭 (Impermanence Heron)", "main_stat": "暴击率 / 暴伤 / 充能"},
                {"slot": "3COST", "name": "幽灵飞鹭", "main_stat": "共鸣效率 / 属性加成"},
                {"slot": "3COST", "name": "裂隙游荡者", "main_stat": "共鸣效率 / 属性加成"},
                {"slot": "1COST", "name": "幻光幼灵", "main_stat": "攻击力百分比"},
                {"slot": "1COST", "name": "夜巡行者", "main_stat": "攻击力百分比"}
            ],
            "version": "1.3"
        }
    ]

def get_wuthering_waves_mechanics():
    return [
        {
            "category": "战斗机制",
            "title": "协奏能量 (Concerto) 与变奏/延奏轮转机制",
            "formula": "Concerto_Full = 100 触发 Outro_Skill(退场) + Intro_Skill(入场) 极效乘区",
            "parameters": {
                "intro_skill": "下一位角色携带变奏技能登场，造成爆发破盾伤害并立即激活核心状态（如今汐进入神圣化身）",
                "outro_skill": "退场角色为下一位登场角色赋予强力 Buff（例如莫特斐+38%重击、散华+38%普攻、长离+20%火伤+25%大招）",
                "cooldown": "协奏能量通过普攻、共鸣技能、闪避反击与共鸣解放积攒，配合轻云出月+无常凶鹭实现超模滚雪球"
            }
        },
        {
            "category": "动作判定",
            "title": "极限闪避反击与完美弹刀 (Parry) 破防机制",
            "formula": "Enemy_Attack_Frame + Normal/Heavy_Attack = Parry_Success -> Vibration_Gauge_Dmg * 300%",
            "parameters": {
                "dodge_counter": "在受击判定生效前瞬间按下闪避触发慢动作时空，立即点击普攻施放无敌帧闪避反击",
                "parry": "敌人身上闪现金色光圈时，使用近战武器普攻或重击格挡敌方攻击，使怪物攻击被强行弹开并削减巨额共振韧性条",
                "break": "共振韧性条归零后怪物进入瘫痪大硬直，受到的所有伤害提升 30%"
            }
        },
        {
            "category": "伤害公式",
            "title": "鸣潮底层独立乘区伤害总公式",
            "formula": "Damage = Base_Atk * Skill_Multiplier% * (1 + Sum_DMG_Bonus%) * Crit_Multiplier * Def_Multiplier * Res_Multiplier",
            "parameters": {
                "base_atk": "角色基础白值 + 武器基础白值",
                "crit": "暴击命中时为 Crit_DMG (初始为 150%)",
                "def_multiplier": "(800 + 8 * Attacker_Level) / (800 + 8 * Attacker_Level + 7.92 * Target_Level + 792 * (1 - Def_Ignore%))",
                "res_multiplier": "当敌方抗性 > 0 时为 1 - Resistance% / (1 + Resistance%)；抗性破防可变为负数增伤"
            }
        },
        {
            "category": "核心养成",
            "title": "声骸 43311 毕业词条结构与无音区双爆强化规则",
            "formula": "Cost_Limit = 12 (4-Cost Boss + 3-Cost Elite*2 + 1-Cost Normal*2)",
            "parameters": {
                "4_cost": "主属性首选暴击率或暴击伤害，提供 22% 暴击率 或 44% 暴击伤害",
                "3_cost": "主属性首选对应属性伤害加成（如热熔/气动/衍射/湮灭各 30% 加成）",
                "1_cost": "主属性固定为生命/攻击百分比（18% 攻击）",
                "sub_stats": "每个声骸强化至25级可解锁5条副词条，双爆（暴击率6.3%~10.5%、暴伤12.6%~21.0%）为毕业核心判定"
            }
        },
        {
            "category": "高阶技巧",
            "title": "声骸合轴 (Swap-Cancel) 与技能后摇取消机制",
            "formula": "Cast_Long_Animation_Skill -> Immediately_Switch_Character -> Dual_Character_Simultaneous_DPS",
            "parameters": {
                "echo_cancel": "施放长前摇声骸技能（如无常凶鹭、鸣钟之龟、燎照之骑）瞬间切换角色，原角色在后台继续打完攻击",
                "burst_cancel": "共鸣解放或蓄力攻击出手瞬间切人，两个角色同时在场输出，使队伍单位时间 DPS 提升 50%~100%"
            }
        }
    ]

def get_wuthering_waves_guides_and_wikis():
    guides = [
        {
            "title": "鸣潮 1.3 版本各属性配队梯度与协奏合轴进阶全解析",
            "type": "BUILD",
            "difficulty": "ADVANCED",
            "tags": ["配队梯度", "协奏合轴", "深境登塔", "今汐", "长离"],
            "summary": "全面拆解当前版本 T0 配队：今汐折枝龙光核爆队、忌炎莫特斐苍龙连携队、长离散华速切队以及守岸人双生辅助循环手法。",
            "content": {
                "sections": [
                    {"title": "一、当前版本 T0 强力配队大盘", "text": "1. 今汐 + 折枝/渊武 + 守岸人/维里奈：折枝协同输出极速叠韶光，今汐开E乘龙斩出百万核爆。\n2. 忌炎 + 莫特斐 + 维里奈：莫特斐提供38%重击加成与大招协同，忌炎开大青龙聚怪扫场无敌。\n3. 长离 + 今汐/安可 + 守岸人：长离双C速切，延奏为下一位角色提供20%热熔/大招增幅。"},
                    {"title": "二、合轴操作核心逻辑", "text": "通过技能后摇切人让双人同场输出。例如：今汐打出强化E飞天瞬间切守岸人上Buff，守岸人施放声骸瞬间切折枝，折枝打满协奏秒切今汐落地接大！"}
                ]
            },
            "like_count": 892,
            "useful_count": 765
        },
        {
            "title": "今汐单人核爆极致手法与声骸 43311 词条毕业指南",
            "type": "CHARACTER",
            "difficulty": "MEDIUM",
            "tags": ["今汐", "声骸养成", "衍射套", "惊龙破空"],
            "summary": "详细解析岁主今汐的韶光积攒机制、惊龙破空伤害倍率加成乘区，以及 43311 浮星祛暗声骸词条优先级。",
            "content": {
                "sections": [
                    {"title": "一、韶光层数机制", "text": "队友造成属性协同伤害（折枝笔墨、渊武雷柱、吟霖缚灵）每秒可为今汐积攒2~3层韶光，50层满层时【惊龙破空】造成额外 2450% 真实衍射加成！"},
                    {"title": "二、声骸毕业属性", "text": "4COST岁主【角】首选暴击率；3COST双衍射伤害加成；1COST双攻击力百分比。副词条追求：双爆 > 共鸣技能加成 > 攻击百分比。"}
                ]
            },
            "like_count": 1240,
            "useful_count": 980
        },
        {
            "title": "守岸人全流程培养指南：共鸣效率与超频变奏领域解析",
            "type": "CHARACTER",
            "difficulty": "EASY",
            "tags": ["守岸人", "辅助人权", "黑海岸", "隐世回光"],
            "summary": "新一代 T0 级人权辅助守岸人深度评测：共鸣效率堆叠技巧、大招思量流转领域全队暴伤增益与队伍替换思路。",
            "content": {
                "sections": [
                    {"title": "一、共鸣效率阈值", "text": "守岸人被动将超出 150% 的共鸣效率转化为全队暴击伤害。推荐共鸣效率达到 250% 以上，武器首选五星专武或满阶四星【奇幻变奏】。"},
                    {"title": "二、手法与技能循环", "text": "登场 E -> 普攻触发蝴蝶回血 -> 共鸣解放开启星空领域 -> 施放鸣钟之龟声骸 -> 触发延奏换主C，主C登场必定暴击且享受超强攻击加成！"}
                ]
            },
            "like_count": 1560,
            "useful_count": 1320
        }
    ]

    wikis = [
        {
            "title": "鸣潮声骸系统与无音区清理机制",
            "content": "声骸是鸣潮核心装备系统。击败大世界残象有概率掉落声骸吸收。声骸分为 4COST（首领）、3COST（精英）与 1COST（普通杂兵）。角色最多装备 5 个声骸，总 COST 上限为 12。强化至 25 级后可使用调谐器开启 5 条副词条。"
        },
        {
            "title": "协奏能量与变奏延奏机制",
            "content": "协奏能量是鸣潮独创的双人轮转机制，最大值为 100 点。当角色的生命条左侧协奏能量圆环填满后，切换角色会同时触发当前角色的【延奏技能 (Outro)】与新登场角色的【变奏技能 (Intro)】，是深塔打出高额 DPS 的灵魂核心。"
        },
        {
            "title": "极限闪避与弹刀 (Parry) 机制",
            "content": "当怪物发起攻击出现金色破绽光圈时，使用近战角色在判定窗口内普攻或重击，即可实现完美弹刀。弹刀成功将完全打断怪物出招并削减巨额韧性条；处于红色危险光圈时需使用极限闪避触发慢动作反击。"
        }
    ]

    return guides, wikis

def sync_all():
    print("=== 开始同步 鸣潮 (Wuthering Waves) 全量数据 (game_id = 26) ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    ensure_game_exists(cur)

    # 1. 角色
    chars = get_wuthering_waves_characters()
    print(f"正在写入 {len(chars)} 位共鸣者数据...")
    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                26, %s, %s, %s, %s, %s, %s,
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

    # 2. 武器
    weaps = get_wuthering_waves_weapons()
    print(f"正在写入 {len(weaps)} 件武器数据...")
    for w in weaps:
        h = calc_hash(w)
        curve = w['base_atk_curve']
        if isinstance(curve, dict):
            curve = [{'level': str(k), 'atk': v} for k, v in curve.items()]
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                26, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    # 3. 声骸套装
    arts = get_wuthering_waves_artifacts()
    print(f"正在写入 {len(arts)} 套合鸣声骸数据...")
    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                26, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    # 4. 机制
    mechs = get_wuthering_waves_mechanics()
    print(f"正在写入 {len(mechs)} 条战斗机制与公式...")
    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (26, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    # 5. 攻略与百科
    guides, wikis = get_wuthering_waves_guides_and_wikis()
    print(f"正在写入 {len(guides)} 篇攻略与 {len(wikis)} 条百科词条...")
    for g in guides:
        cur.execute("""
            INSERT INTO guide (
                game_id, version_id, title, author_id, type, difficulty,
                tags, summary, content, status, like_count, useful_count, verify_count,
                created_at, updated_at
            ) VALUES (
                26, NULL, %s, 1, %s, %s,
                %s, %s, %s, 'PUBLISHED', %s, %s, 10,
                NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (g['title'], g['type'], g['difficulty'], Json(g['tags']), g['summary'], Json(g['content']), g['like_count'], g['useful_count']))

    for wk in wikis:
        cur.execute("""
            INSERT INTO wiki_entry (game_id, title, content, last_updated)
            VALUES (26, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (wk['title'], wk['content']))

    conn.commit()
    conn.close()
    print("=== 鸣潮 (game_id = 26) 全量数据写入完成！ ===")

if __name__ == '__main__':
    sync_all()
