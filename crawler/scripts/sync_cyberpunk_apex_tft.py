#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赛博朋克2077 (game_id = 12)、Apex 英雄 (game_id = 16) 与 云顶之弈 (game_id = 19)
全量数值体系落库与同步脚本
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

def sync_cyberpunk(cur):
    print("--- 正在同步 赛博朋克2077 (game_id = 12) ---")
    chars = [
        {
            "name": "V·斯安威逊时停武士 (Sandevistan Samurai)",
            "title": "夜之城传奇·时停一闪",
            "rarity": 5,
            "element": "反应/肉体/技术",
            "weapon_type": "武士刀/螳螂刀",
            "region": "夜之城·沃森区",
            "avatar_url": "https://patchwiki.biligame.com/images/cbpk/thumb/avatar_v_samurai.png/120px-avatar_v_samurai.png",
            "splash_url": "https://patchwiki.biligame.com/images/cbpk/thumb/avatar_v_samurai.png/600px-avatar_v_samurai.png",
            "base_stats": [
                {"level": "1", "hp": 100, "stamina": 100, "armor": 50, "speed": 100},
                {"level": "30", "hp": 450, "stamina": 180, "armor": 520, "speed": 125},
                {"level": "60", "hp": 850, "stamina": 260, "armor": 1250, "speed": 150}
            ],
            "special_ascension_stat": {"stat_name": "斯安威逊时停", "values": {"时间减速": "时间流速降低 85%，持续期间近战伤害暴击率提升 100%"}},
            "ascension_materials": [{"tier": "义体过载", "items": "幽冥犬空投物资与不朽义体组件"}],
            "talents": [
                {"name": "义体主动·斯安威逊 (Sandevistan)", "type": "ELEMENTAL_BURST", "description": "启动军用科技‘远地点’斯安威逊，将周围世界时间流速降低 85%，自身行动速度不受影响，击杀敌人延长时停时长并返还冷却！", "scaling": "近战刀刀处决，极速穿梭战场"},
                {"name": "刀剑终结·斩首 (Finisher: Bladetornado)", "type": "NORMAL_ATTACK", "description": "对失衡或低生命值敌人施放处决斩首，恢复自身 25% 生命值并恢复全部耐力。", "scaling": "绝对无敌处决动作"},
                {"name": "闪避弹反·子弹时间 (Bullet Deflect)", "type": "ELEMENTAL_SKILL", "description": "拔出武士刀格挡正面敌人的子弹射击，并将子弹精准反弹回射击者头部！", "scaling": "弹反枪械子弹"}
            ],
            "passives": [{"name": "边缘行者 (Edgerunner)", "desc": "突破义体容量上限，获得狂暴过载增益，低血量时有概率陷入暴怒亢奋。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "开斯安威逊进入时停 -> 冲刺突进连续斩首处决 -> 反弹子弹秒杀狙击手！"},
            "recommendations": {"weapons": {"bis": "觉 (Satori) + 白虎 (Byakko)"}, "artifacts": {"bis_set": "远地点义体套件"}},
            "version": "2.2"
        },
        {
            "name": "V·网络黑客魔偶大师 (Netrunner Master)",
            "title": "深网幽灵·无形死神",
            "rarity": 5,
            "element": "智力/技术",
            "weapon_type": "网络接入仓/智能武器",
            "region": "夜之城·太平洲",
            "avatar_url": "https://patchwiki.biligame.com/images/cbpk/thumb/avatar_v_netrunner.png/120px-avatar_v_netrunner.png",
            "splash_url": "https://patchwiki.biligame.com/images/cbpk/thumb/avatar_v_netrunner.png/600px-avatar_v_netrunner.png",
            "base_stats": [
                {"level": "1", "hp": 90, "ram": 8, "armor": 30, "int": 6},
                {"level": "30", "hp": 380, "ram": 22, "armor": 410, "int": 15},
                {"level": "60", "hp": 720, "ram": 42, "armor": 980, "int": 20}
            ],
            "special_ascension_stat": {"stat_name": "RAM 回复", "values": {"特权": "杀敌极速回复 RAM，黑客魔偶连锁扩散"}},
            "ascension_materials": [{"tier": "魔偶插槽", "items": "5阶++ 快速破解组件"}],
            "talents": [
                {"name": "黑客魔偶·赛博精神病 (Cyberpsychosis)", "type": "NORMAL_ATTACK", "description": "向敌方网络神经上传病毒魔偶，迫使其陷入赛博精神病狂暴攻击其身旁的所有同伴，并在身边无敌人时自我终结！", "scaling": "控制最高阶兵种内讧"},
                {"name": "致命魔偶·突触熔断 (Synapse Burnout)", "type": "ELEMENTAL_SKILL", "description": "过载目标的大脑神经突触，直接造成巨额电磁伤害，若目标已经处于易伤状态则必定造成暴击秒杀！", "scaling": "单体最高爆发魔偶"},
                {"name": "超频机制·生命换取RAM (Overclock)", "type": "ELEMENTAL_BURST", "description": "激活脑机超频状态，当 RAM 耗尽时允许消耗自身生命值作为 RAM 强制连续上传高阶魔偶！", "scaling": "无限瞬发魔偶灭团"}
            ],
            "passives": [{"name": "魔偶队列", "desc": "单个目标允许连续排队上传最多 4 个魔偶，触发连锁爆轰。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "远程侵入监控摄像头 -> 开启超频 -> 批量上传传感染病与赛博精神病，全楼人死光不见踪影！"},
            "recommendations": {"weapons": {"bis": "厄瑞玻斯 (Erebus) + 应龙 (Yinglong)"}, "artifacts": {"bis_set": "网络奥秘接入仓"}},
            "version": "2.2"
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
                12, %s, %s, %s, %s, %s, %s,
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
            "name": "觉 (Satori)",
            "type": "不朽武士刀",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/cbpk/weapon_satori.png",
            "base_atk_curve": {"秒伤": 380, "单次伤害": 165},
            "sub_stat": {"type": "极高暴伤", "values": {"暴击伤害": "+500% 暴击伤害！", "特性": "荒坂三郎随身佩刀"}},
            "refinements": [{"rank": 1, "desc": "暴击伤害极其夸张，配合斯安威逊时停 100% 暴击率，一刀出鞘可直接斩杀首领！"}],
            "ascension_materials": [{"tier": "获取方式", "items": "序章偷货任务乘直升机前往荒坂三郎停机坪获取"}],
            "version": "2.2"
        },
        {
            "name": "守望 (Overwatch)",
            "type": "不朽动能狙击步枪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/cbpk/weapon_overwatch.png",
            "base_atk_curve": {"秒伤": 420, "单次伤害": 680},
            "sub_stat": {"type": "自带消音与穿透", "values": {"消音": "完全静音消音器", "穿墙": "穿透极厚混凝土掩体"}},
            "refinements": [{"rank": 1, "desc": "帕南赠送的不朽狙击枪，全游戏极少数既拥有全消音又具备超强穿墙能力的重型大狙。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "完成帕南支线任务‘救出索尔’获得"}],
            "version": "2.2"
        }
    ]

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
                12, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    # 义体
    arts = [
        {
            "name": "军用科技‘远地点’斯安威逊 (Militech Apogee Sandevistan)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/cbpk/cyberware_apogee.png",
            "two_piece_bonus": "减缓时间 85%，持续时间最高可达 10 秒；暴击率提升 20%，暴击伤害提升 15%。",
            "four_piece_bonus": "时停期间击杀敌人返还 20% 时停时长，并回复 20% 耐力！无限续杯的时停神器。",
            "pieces": [{"slot": "操作系统", "name": "远地点斯安威逊 Mk.5", "main_stat": "时间减速85%"}],
            "version": "2.2"
        }
    ]
    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                12, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    cur.execute("""
        INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
        VALUES (12, '义体系统', '赛博朋克2077 义体容量与边缘行者机制',
                'Cyberware_Capacity_Cost <= Max_Capacity (Overclock: Allows +50 Overcharge via Edgerunner Perk)',
                '{"capacity":"每件义体占用一定容量点数，超过上限需点出技术天赋边缘行者，过载进入狂暴状态","armor":"护甲值主要由皮下护甲与骨骼义体提供"}', NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (12, '赛博朋克2077 2.0 斯安威逊时停飞刀刀剑流全配装', 1, 'BUILD', 'ADVANCED', '["斯安威逊", "刀剑流", "觉", "远地点", "毕业配置"]',
                '详解2.0版本近战刀剑配点：反应20、技术20、肉体20，配合白虎与觉实现无缝时停空中飞渡。',
                '{"sections":[{"title":"一、核心义体选择","text":"操作系统无脑选【军用科技远地点斯安威逊】，骨骼选择致密骨髓和微型转子提升近战攻速，腿部必带强化肌腱二段跳。"},{"title":"二、输出手法","text":"空中二段跳下落开时停，疾跑重击突进斩首，处决回血并刷新时停时长，真正做到子弹停滞、一骑当千！"}]}',
                'PUBLISHED', 2650, 2320, 18, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 赛博朋克2077 同步完成 ---")

def sync_apex(cur):
    print("--- 正在同步 Apex 英雄 (game_id = 16) ---")
    chars = [
        {
            "name": "恶灵 (Wraith)",
            "title": "跨维度突击手·虚空行者",
            "rarity": 5,
            "element": "虚空相位",
            "weapon_type": "突击位",
            "region": "边境星系",
            "avatar_url": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2019/01/legends-character-tiles/apex-grid-tile-legends-wraith.png.adapt.crop16x9.png",
            "splash_url": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2019/01/legends-character-tiles/apex-grid-tile-legends-wraith.png.adapt.crop16x9.png",
            "base_stats": [{"level": "基础", "hp": 100, "shield": 100, "total_ehp": 200}],
            "special_ascension_stat": {"stat_name": "虚空相位", "values": {"特权": "完全无敌进入相位空间"}},
            "ascension_materials": [{"tier": "传奇代币", "items": "12,000 传奇代币解锁"}],
            "talents": [
                {"name": "战术技能·踏入虚空 (Into the Void)", "type": "ELEMENTAL_SKILL", "description": "在短暂启动后遁入虚空相位，处于完全无敌判定并大幅提速，持续 4 秒，期间免疫一切外界伤害与毒圈侵蚀。", "scaling": "脱战与转点绝对无敌"},
                {"name": "绝招·空间裂隙 (Dimensional Rift)", "type": "ELEMENTAL_BURST", "description": "放置两个相连的单向高速传送门，持续 45 秒。全队所有玩家或倒地队友均可进入传送门瞬间跨越 100 米转移安全区！", "scaling": "战术转点神技"}
            ],
            "passives": [{"name": "虚空之声 (Voices from the Void)", "desc": "当有敌人的枪口瞄准恶灵或附近有陷阱时，耳边低语提前向全队预警。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "探点被集火瞬间开踏入虚空无伤后撤，残局开传送门接应被困在圈外的倒地队友。"},
            "recommendations": {"weapons": {"bis": "R-99 / 和平捍卫者"}},
            "version": "Season 23"
        },
        {
            "name": "动力小子 (Octane)",
            "title": "高速瘾君子·特技狂人",
            "rarity": 5,
            "element": "极速突进",
            "weapon_type": "突击位",
            "region": "普萨玛忒",
            "avatar_url": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2019/01/legends-character-tiles/apex-grid-tile-legends-octane.png.adapt.crop16x9.png",
            "splash_url": "https://media.contentapi.ea.com/content/dam/apex-legends/images/2019/01/legends-character-tiles/apex-grid-tile-legends-octane.png.adapt.crop16x9.png",
            "base_stats": [{"level": "基础", "hp": 100, "shield": 100, "total_ehp": 200}],
            "special_ascension_stat": {"stat_name": "兴奋剂", "values": {"特权": "消耗生命极速奔跑，被动常驻脱战回血"}},
            "ascension_materials": [{"tier": "传奇代币", "items": "12,000 传奇代币解锁"}],
            "talents": [
                {"name": "战术技能·兴奋剂 (Stim)", "type": "NORMAL_ATTACK", "description": "注入超频兴奋剂，消耗 20 点生命值，在 6 秒内使奔跑速度提升 30%（冲刺提升 40%），且完全解除减速负面状态！", "scaling": "几乎无CD秒按"},
                {"name": "绝招·发射护垫 (Launch Pad)", "type": "ELEMENTAL_BURST", "description": "部署一个强力弹跳垫，踏上者直接被猛烈抛射向空中，并在空中可进行二次二段跳变向！", "scaling": "全队高速进圈与高地抢点"}
            ],
            "passives": [{"name": "快速修复 (Swift Mend)", "desc": "脱离战斗后每秒自动恢复 1.5 点生命值，无需使用注射器。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "扎针提速滑铲抢装备，利用跳板直接弹射飞过房区贴脸近战喷子喷爆！"},
            "recommendations": {"weapons": {"bis": "平行步枪 / 獒犬霰弹枪"}},
            "version": "Season 23"
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
                16, %s, %s, %s, %s, %s, %s,
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
            "name": "R-301 卡宾枪 (Carbine)",
            "type": "突击步枪",
            "rarity": 4,
            "icon_url": "https://media.contentapi.ea.com/content/dam/apex-legends/common/weapons/r301.png",
            "base_atk_curve": {"爆头": 25, "躯干": 14, "腿部": 11},
            "sub_stat": {"type": "精准轻型", "values": {"射速": "810 RPM", "弹匣": "18/28发", "弹道": "极度平稳近乎无后坐力"}},
            "refinements": [{"rank": 1, "desc": "中远距离统治级全自动步枪，激光枪一般的垂直后坐力，新手与职业选手的最稳利刃。"}],
            "ascension_materials": [{"tier": "配件", "items": "轻型弹匣、枪托、枪口补偿器、1~3倍镜"}],
            "version": "Season 23"
        },
        {
            "name": "和平捍卫者 (Peacekeeper / PK)",
            "type": "杠杆霰弹枪",
            "rarity": 4,
            "icon_url": "https://media.contentapi.ea.com/content/dam/apex-legends/common/weapons/peacekeeper.png",
            "base_atk_curve": {"全中头部": 121, "全中躯干": 99, "单颗弹丸": 9},
            "sub_stat": {"type": "精确收束", "values": {"弹匣": "5发", "特性": "右键开镜自动聚能收束弹丸"}},
            "refinements": [{"rank": 1, "desc": "转角贴脸近战的神！开镜聚能后在 20 米距离依旧能打出 99 点高额爆发。"}],
            "ascension_materials": [{"tier": "配件", "items": "霰弹枪枪栓、1倍幻影准星"}],
            "version": "Season 23"
        }
    ]

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
                16, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    cur.execute("""
        INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
        VALUES (16, '移动身法', 'Apex 英雄 蹬墙跳 (Wall Bounce) 与滑铲跳物理模型',
                'Slide(滑铲) -> Jump(起跳) -> Hit_Wall_Let_Go_WASD -> Jump_Again = Wall_Bounce (Extreme Aerial Evasion)',
                '{"superglide":"攀爬上箱子最高点瞬间同时按下跳跃和蹲伏键触发超滑，瞬间获得超高初始动能","air_strafe":"空中松开W按A/D配合平滑转动鼠标实现空中90度无惯性拐弯"}', NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (16, 'Apex英雄身法蜕变：从滑铲跳到蹬墙跳实战教学', 1, 'GENERAL', 'MEDIUM', '["身法", "滑铲跳", "蹬墙跳", "恶灵", "近战教学"]',
                '详细拆解近距离近战换弹时的蹬墙跳规避技巧，以及如何利用箱子完成空中转体反打。',
                '{"sections":[{"title":"一、蹬墙跳口诀","text":"滑铲蓄力起跳 -> 接近墙面瞬间松开所有移动键（W/A/S/D全部松开！）-> 身体贴墙瞬间猛按一下跳跃键，角色瞬间反弹弹飞两米高！"}]}',
                'PUBLISHED', 2980, 2670, 20, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- Apex 英雄 同步完成 ---")

def sync_tft(cur):
    print("--- 正在同步 云顶之弈 (game_id = 19) ---")
    weaps = [
        {
            "name": "无尽之刃 (Infinity Edge)",
            "type": "成装道具",
            "rarity": 4,
            "icon_url": "https://patchwiki.biligame.com/images/lol/item_infinity_edge.png",
            "base_atk_curve": {"攻击力": "+35%", "暴击率": "+35%"},
            "sub_stat": {"type": "暴击质变", "values": {"被动": "使携带者的物理技能必定能够造成暴击"}},
            "refinements": [{"rank": 1, "desc": "由暴风大剑 + 拳套合成。物理输出核心必备大件。"}],
            "ascension_materials": [{"tier": "合成散件", "items": "暴风大剑 + 拳套"}],
            "version": "Set 12"
        },
        {
            "name": "灭世者的死亡之帽 (Rabadon's Deathcap)",
            "type": "成装道具",
            "rarity": 4,
            "icon_url": "https://patchwiki.biligame.com/images/lol/item_deathcap.png",
            "base_atk_curve": {"法术强度": "+50", "额外法强": "+20%"},
            "sub_stat": {"type": "法系核爆", "values": {"被动": "提供高额法强加成并附加额外伤害"}},
            "refinements": [{"rank": 1, "desc": "由无用大棒 + 无用大棒合成。法核主C最直接暴力的伤害大件。"}],
            "ascension_materials": [{"tier": "合成散件", "items": "无用大棒 + 无用大棒"}],
            "version": "Set 12"
        },
        {
            "name": "鬼索的狂暴之刃 (Guinsoo's Rageblade / 羊刀)",
            "type": "成装道具",
            "rarity": 4,
            "icon_url": "https://patchwiki.biligame.com/images/lol/item_rageblade.png",
            "base_atk_curve": {"攻击速度": "+15%", "法术强度": "+10"},
            "sub_stat": {"type": "无限攻速", "values": {"被动": "每次攻击永久叠加 5% 攻速，无上限"}},
            "refinements": [{"rank": 1, "desc": "由反曲之弓 + 无用大棒合成。后排普攻流主C残局战神装备。"}],
            "ascension_materials": [{"tier": "合成散件", "items": "反曲之弓 + 无用大棒"}],
            "version": "Set 12"
        }
    ]

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
                19, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    cur.execute("""
        INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
        VALUES (19, '经济运营', '云顶之弈 利息 (Interest) 与连胜连败收益机制',
                'Base_Gold = 5 + Interest(10% Current Gold, max 5) + Streak_Gold(1~3 for 2~5+ Win/Loss)',
                '{"interest":"每留存 10 金币，下回合开始结算额外 1 金币利息，存到 50 金币吃满 5 金币最大利息","fast_eight":"在3-2升6人口，4-1升7人口，4-2升8人口大搜四费核心主C"}', NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (19, '云顶之弈运营速八教学：连胜过渡与4-2大D锁血法则', 1, 'BUILD', 'MEDIUM', '["云顶之弈", "运营教学", "速八", "利息", "连胜过渡"]',
                '教会你如何控好每回合血量与经济，在4-2升8级大搜两星四费卡完成完美锁血转阵容。',
                '{"sections":[{"title":"一、前期留牌核心","text":"2-1拉4级，2-5拉5级，用前排双斗士/双守卫搭配后排双射手/双法师打工，装备不要烂在备战席，合成日炎/电刀直接保连胜！"}]}',
                'PUBLISHED', 3120, 2800, 22, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 云顶之弈 同步完成 ---")

def sync_all():
    print("=== 开始同步 赛博朋克2077、Apex英雄与云顶之弈 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    sync_cyberpunk(cur)
    sync_apex(cur)
    sync_tft(cur)
    conn.commit()
    conn.close()
    print("=== 三款游戏同步完毕！ ===")

if __name__ == '__main__':
    sync_all()
