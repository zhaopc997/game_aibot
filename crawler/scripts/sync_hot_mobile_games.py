#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六大热门手游数据全面入库与生态同步脚本:
1. 幻塔 (Tower of Fantasy) - game_id = 21 (补全空缺生态)
2. 和平精英 (Game for Peace) - game_id = 27 (全新引入)
3. 金铲铲之战 (Battle of the Golden Spatula) - game_id = 28 (全新引入)
4. 阴阳师 (Onmyoji) - game_id = 29 (全新引入)
5. 崩坏3 (Honkai Impact 3rd) - game_id = 30 (全新引入)
6. 重返未来：1999 (Reverse: 1999) - game_id = 31 (全新引入)

包含:
- 游戏元数据与基础信息 (game)
- 核心角色/拟态/式神/女武神/棋子 (game_character)
- 专属武器/枪械/心相/神装 (game_weapon)
- 意志/防具/御魂/圣痕/共鸣 (game_artifact_set)
- 底层机制算法与战斗公式 (game_mechanic_rule)
- 深度权威攻略 (guide) 与百科词条 (wiki_entry)
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
# 0. 注册并初始化新游戏元数据
# ==========================================
def register_games(cur):
    print("--- 正在检查并注册热门手游基础信息 ---")
    new_games = [
        (27, '和平精英', 'PUBG Mobile/吃鸡/特种兵/和平', '移动端 (iOS/Android)', '战术竞技', 'https://patchwiki.biligame.com/images/gp/thumb/banner.png/600px-banner.png', '腾讯光子工作室群自研打造的国民级战术竞技射击手游，虚幻4引擎研发，极致视听感受，百人同场竞技与真实弹道射击。', '1.27'),
        (28, '金铲铲之战', '铲铲/TFT手游/云顶之弈手游', '移动端 (iOS/Android)', '策略自走棋', 'https://patchwiki.biligame.com/images/jcc/thumb/banner.png/600px-banner.png', '腾讯官方授权的正版自走棋手游，八名玩家共同进行一场各自为战的博弈对抗，招兵买马、融合英雄、提升战力与排兵布阵。', 'S12'),
        (29, '阴阳师', 'Onmyoji/痒痒鼠/平安京', '移动端 (iOS/Android/PC)', '和风RPG', 'https://patchwiki.biligame.com/images/yys/thumb/banner.png/600px-banner.png', '网易游戏自研的和风回合制 RPG 手游，人鬼共生的平安时代，豪华声优阵容、百种式神收集与深度御魂养成。', 'v1.7'),
        (30, '崩坏3', 'BH3/Honkai 3/崩崩崩', 'PC/移动端', '3D动作', 'https://fastcdn.hoyoverse.com/content-v2/bh3/102001/banner.jpg', '米哈游自主研发的 3D 全视角动作手游，点燃国创动作游戏之魂，次世代卡通渲染、无限分支连招、极限闪避与主机级打击感。', 'v7.8'),
        (31, '重返未来：1999', 'Reverse 1999/1999/重返未来', 'PC/移动端', '复古神秘学RPG', 'https://patchwiki.biligame.com/images/re1999/thumb/banner.png/600px-banner.png', '深蓝互动研发的复古神秘学策略 RPG 手游，穿梭于暴雨引发的时代倒退之中，探寻历史真相，全英配音与独特视觉美学。', 'v2.2')
    ]
    for gid, name, alias, plat, cat, cover, desc, ver in new_games:
        cur.execute("""
            INSERT INTO game (id, name, alias, platform, category, cover_url, description, current_version, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                alias = EXCLUDED.alias,
                platform = EXCLUDED.platform,
                category = EXCLUDED.category,
                cover_url = EXCLUDED.cover_url,
                description = EXCLUDED.description,
                current_version = EXCLUDED.current_version,
                updated_at = NOW();
        """, (gid, name, alias, plat, cat, cover, desc, ver))

    # 更新序列至最大 id
    cur.execute("SELECT setval('game_id_seq', (SELECT MAX(id) FROM game));")
    print("--- 热门手游基础元数据注册完毕 ---")

# ==========================================
# 1. 幻塔 (Tower of Fantasy, ID = 21)
# ==========================================
def sync_tower_of_fantasy(cur):
    print("--- 正在同步 幻塔 (Tower of Fantasy, game_id = 21) ---")
    gid = 21

    chars = [
        {
            "name": "凛夜·影织 (Lin - Shadow Weaver)",
            "title": "维拉潜影·异能核心",
            "rarity": 5,
            "element": "异能 (Altered)",
            "weapon_type": "扇子 / 影织",
            "region": "维拉·镜都",
            "avatar_url": "https://patchwiki.biligame.com/images/ht/thumb/avatar_lin.png/120px-avatar_lin.png",
            "splash_url": "https://patchwiki.biligame.com/images/ht/thumb/avatar_lin.png/600px-avatar_lin.png",
            "base_stats": [
                {"level": "1", "hp": 1165, "atk": 178, "crit": 124, "def": 78},
                {"level": "90", "hp": 486000, "atk": 25800, "crit": 14200, "def": 8900}
            ],
            "special_ascension_stat": {"stat_name": "异能全伤提升", "values": {"90级": "+28.5% 全元素伤害"}},
            "ascension_materials": [{"tier": "突破材料", "items": "纳米涂层、强效原能结晶"}],
            "talents": [
                {"name": "映月之镜 (Skill)", "type": "ELEMENTAL_SKILL", "description": "在自身周围生成持续 20 秒的【映月之境】。在境中自身跳跃能力提升，滞空消耗耐力降低 50%，伤害提升 15%，并根据所搭配的两把武器元素激活专属异能共鸣强化！", "scaling": "冷却 30 秒，强力脱手增伤领域"},
                {"name": "重力回旋 (Discharge)", "type": "ELEMENTAL_BURST", "description": "武器充能满或触发幻想时间切入时，在目标处生成强大的引力奇点，吸引周围大范围目标并造成高达 980% 的异能范围爆发伤害！", "scaling": "充能消耗 1000 点，强力聚怪核爆"},
                {"name": "轻羽飞扇 (Normal)", "type": "NORMAL_ATTACK", "description": "挥舞折扇进行五段攻击，空中可释放下落重击与滞空悬浮轰炸。", "scaling": "段数总倍率 480%"}
            ],
            "passives": [{"name": "异能共鸣", "desc": "搭配任意两把同属性武器时，额外激活该元素的强力专属共鸣Buff。"}],
            "constellations": [
                {"rank": 1, "desc": "映月之境内普通攻击转化为范围爆炸，伤害提升 15%。"},
                {"rank": 3, "desc": "映月之境内每秒生成一枚红莲花，触碰引爆造成 150% 范围伤害。"},
                {"rank": 6, "desc": "映月之境拥有两次充能，且在境内释放武器连携技获得额外充能提升。"}
            ],
            "special_mechanics": {"core_flow": "切出凛夜释放【映月之境】 -> 触发全元素共鸣与增伤 -> 切主C打满爆发 -> 充能满切回释放引力连携！"},
            "recommendations": {"weapons": {"bis": "影织 (Shadow Weaver)"}, "artifacts": {"bis_set": "凛夜意志四件套"}},
            "version": "3.8"
        },
        {
            "name": "菲欧娜·月星飞鸢 (Fiona)",
            "title": "茵纳斯执政官·潮汐之女",
            "rarity": 5,
            "element": "异能 (Altered)",
            "weapon_type": "散流双刃 / 月星飞鸢",
            "region": "溟海·茵纳斯",
            "avatar_url": "https://patchwiki.biligame.com/images/ht/thumb/avatar_fiona.png/120px-avatar_fiona.png",
            "splash_url": "https://patchwiki.biligame.com/images/ht/thumb/avatar_fiona.png/600px-avatar_fiona.png",
            "base_stats": [
                {"level": "1", "hp": 1210, "atk": 172, "crit": 130, "def": 82},
                {"level": "90", "hp": 498000, "atk": 25200, "crit": 14600, "def": 9200}
            ],
            "special_ascension_stat": {"stat_name": "治疗与终极增伤", "values": {"90级": "+30% 散流增伤与全队生命保护"}},
            "ascension_materials": [{"tier": "突破材料", "items": "纳米涂层、强效原能结晶"}],
            "talents": [
                {"name": "激流狂涌 (Skill)", "type": "ELEMENTAL_SKILL", "description": "召唤双刃水影，向前发射多道水流激波，造成 650% 异能伤害，并附带可自选配置的两套专属水系散流拟态散式（如聚水、涡流、救赎）。", "scaling": "自选战术散式，多功能辅助神技"},
                {"name": "惊涛拍岸 (Discharge)", "type": "ELEMENTAL_BURST", "description": "连携切入制造巨大水瀑，对全屏敌方施加【水蚀】标记，使目标受到伤害提升 12%，并持续为全队恢复巨额生命值。", "scaling": "群体净化 + 易伤 + 治疗"}
            ],
            "passives": [{"name": "潮汐庇佑", "desc": "在任何水域或溟海战斗时，移动速度提升 30%，技能伤害提升 10%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "配置【聚水】与【涡流】散式 -> 开场释放激流狂涌聚怪并挂易伤水蚀 -> 提供霸体与高额全伤加成。"},
            "recommendations": {"weapons": {"bis": "月星飞鸢"}, "artifacts": {"bis_set": "菲欧娜意志四件套"}},
            "version": "3.8"
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
                21, %s, %s, %s, %s, %s, %s,
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
            "name": "影织 (Shadow Weaver)",
            "type": "异能武器 / 远程折扇",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/ht/weapon_shadow_weaver.png",
            "base_atk_curve": [
                {"level": "1", "atk": 178, "shatter": 11.5, "charge": 11.5},
                {"level": "90", "atk": 25800, "shatter": 11.5, "charge": 11.5}
            ],
            "sub_stat": {"type": "异能充能与破防", "values": {"破防度": "11.50 (S阶)", "充能度": "11.50 (S阶)"}},
            "refinements": [
                {"rank": 1, "desc": "在映月之境内，所有武器获得异能通用攻击力加成，完美兼容所有元素阵容。"}
            ],
            "ascension_materials": [{"tier": "90级突破", "items": "磁能棒、原能结晶"}],
            "version": "3.8"
        },
        {
            "name": "月星飞鸢 (Moonstar Falcon)",
            "type": "异能武器 / 散流双刃",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/ht/weapon_moonstar.png",
            "base_atk_curve": [
                {"level": "1", "atk": 172, "shatter": 13.0, "charge": 13.0},
                {"level": "90", "atk": 25200, "shatter": 13.0, "charge": 13.0}
            ],
            "sub_stat": {"type": "全能生存与破防", "values": {"破防度": "13.00 (SS阶)", "充能度": "13.00 (SS阶)"}},
            "refinements": [
                {"rank": 1, "desc": "释放武器技能时获得免控护盾与 15% 最终全伤加成。"}
            ],
            "ascension_materials": [{"tier": "90级突破", "items": "纳米涂层、原能结晶"}],
            "version": "3.8"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                21, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "凛夜意志四件套 (Lin Matrix Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/ht/matrix_lin.png",
            "two_piece_bonus": "在映月之境内每次造成伤害获得一层攻击力提升，最多叠加 5 层，全攻击力提升 18%。",
            "four_piece_bonus": "在映月之境内移动时获得【移速与伤害加成】，最终全元素伤害提升 22%，且该效果在后台亦可生效。",
            "pieces": [
                {"slot": "心 (Mind)", "name": "凛夜·潜行之思", "main_stat": "生命 + 暴击"},
                {"slot": "信 (Memory)", "name": "凛夜·誓言之信", "main_stat": "全攻击 + 异能攻击"},
                {"slot": "想 (Belief)", "name": "凛夜·镜都之望", "main_stat": "暴击率 + 破防"},
                {"slot": "念 (Emotion)", "name": "凛夜·红莲之念", "main_stat": "全伤害加成"}
            ],
            "version": "3.8"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                21, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "战斗机制",
            "title": "幻塔 极限闪避触发【幻想时间】判定模型",
            "formula": "Trigger_Phantasia = (Enemy_Hit_Window_Active == TRUE) AND (Player_Dodge_Input <= 0.2s) -> Global_Time_Slowdown(0.1x, Duration=4.0s)",
            "parameters": {
                "phantasia": "敌人攻击命中前 0.2 秒内闪避成功即可触发全屏时停区域，敌人动作慢放 90%，并瞬间将当前所有武器充能补满至 1000 点",
                "cooldown": "幻想时间全队内置冷却时间为 15 秒（不可连续无限触发）"
            }
        },
        {
            "category": "伤害数值",
            "title": "武器破盾系数与充能值循环算法",
            "formula": "Actual_Shatter = Base_Shatter_Ratio * (1 + Elemental_Resonance_Bonus) * Shield_Weakness_Multiplier",
            "parameters": {
                "shatter": "怪物护盾激活时减伤 50%，需使用破防评级 S (10.0+) 的武器迅速击破护盾，击破瞬间造成硬直并返还大额充能"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (21, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (21, '幻塔 起源深渊 25+ 层异能双拐爆发与极限破盾手法全解', 1, 'BUILD', 'ADVANCED', '["幻塔", "起源深渊", "凛夜", "菲欧娜", "破盾合轴"]',
                '详解高层深渊词条应对：凛夜映月之境开场、菲欧娜双散式提供霸体与水蚀易伤、主C快速融化 Boss 护盾手法。',
                '{"sections":[{"title":"一、深渊起手合轴节奏","text":"开场先切菲欧娜释放技能激活散式加成，随后切凛夜开启【映月之境】，瞬间铺开全屏异能领域并吃满攻击力加成！"},{"title":"二、高危护盾速破策略","text":"怪物出盾警告读条前，预留一把 S 阶破防武器充能，利用极限闪避触发幻想时间瞬间破盾，避免 Boss 释放全屏秒杀大招。"}]}',
                'PUBLISHED', 3600, 3180, 20, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (21, '幻塔 武器元素共鸣与拟态特性激活规则',
                '1. 强攻共鸣：装备两把强攻武器，最终伤害提升 10%（组队时提升 40%）；2. 坚毅共鸣：装备两把防守武器，减伤提升 25%，破盾效率提升 60%；3. 恩赐共鸣：装备两把治疗武器，治疗量提升 100%（组队时为队友提供霸体）；4. 均衡共鸣：三系均衡，全属性综合提升；5. 异能共鸣：根据搭配的其它元素武器自适应切换最佳强化形态。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 幻塔 同步完成 ---")

# ==========================================
# 2. 和平精英 (Game for Peace, ID = 27)
# ==========================================
def sync_game_for_peace(cur):
    print("--- 正在同步 和平精英 (Game for Peace, game_id = 27) ---")
    gid = 27

    chars = [
        {
            "name": "突破攻楼突击手 (Rusher)",
            "title": "正面交火先锋·刚枪王",
            "rarity": 5,
            "element": "战术突破 / 近战瞬秒",
            "weapon_type": "突击步枪 / 冲锋枪",
            "region": "经典海岛·P城/基地",
            "avatar_url": "https://patchwiki.biligame.com/images/gp/thumb/avatar_rusher.png/120px-avatar_rusher.png",
            "splash_url": "https://patchwiki.biligame.com/images/gp/thumb/avatar_rusher.png/600px-avatar_rusher.png",
            "base_stats": [
                {"level": "特种兵", "hp": 100, "signal_energy": 100, "move_speed": 100, "sprint_speed": 135}
            ],
            "special_ascension_stat": {"stat_name": "贴脸腰射散布降低", "values": {"特长": "近战侧身闪身枪秒伤与破门首击"}},
            "ascension_materials": [{"tier": "特训进阶", "items": "王牌段位积分、刚枪勋章"}],
            "talents": [
                {"name": "预瞄闪身枪 (Pre-aim Peek)", "type": "NORMAL_ATTACK", "description": "利用掩体侧身探头，准心预瞄头部，拉出瞬间完成 3~5 发精准短点射，随即回拉掩体规避还击。", "scaling": "头部暴击伤害 2.3 倍，近距离瞬间击倒"},
                {"name": "瞬爆雷攻楼 (Airburst Grenade)", "type": "ELEMENTAL_SKILL", "description": "捏住破片手雷读秒至 1.5 秒松手抛入二楼死角窗口，落地瞬间爆炸不给敌人任何反应时间！", "scaling": "核心爆心范围 100 点真实直死伤害"},
                {"name": "滑铲拜佛跳枪 (Combat Slide)", "type": "ELEMENTAL_BURST", "description": "正面交火中急停接趴下，瞬间改变受击判定框，避开敌方爆头线并持续倾泻火力。", "scaling": "极大干扰敌方拉枪准星轨迹"}
            ],
            "passives": [{"name": "钢铁神经", "desc": "血量低于 30% 时移动速度微幅提升，救援倒地队友时间减少 1 秒。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "探查房区脚步声 -> 投掷烟雾封锁枪线 -> 瞬爆雷盲点压制 -> 侧身闪身枪冲锋连射清除敌人！"},
            "recommendations": {"weapons": {"bis": "M416 (满配红点) + Vector (扩容冲锋枪)"}, "artifacts": {"bis_set": "三级防具神装套件"}},
            "version": "1.27"
        },
        {
            "name": "超远距离狙击手 (Sniper)",
            "title": "千米穿杨·鹰眼死神",
            "rarity": 5,
            "element": "远距侦察 / 致命点杀",
            "weapon_type": "栓动狙击枪 / 射手步枪",
            "region": "沙漠米拉玛 / 雨林萨诺",
            "avatar_url": "https://patchwiki.biligame.com/images/gp/thumb/avatar_sniper.png/120px-avatar_sniper.png",
            "splash_url": "https://patchwiki.biligame.com/images/gp/thumb/avatar_sniper.png/600px-avatar_sniper.png",
            "base_stats": [
                {"level": "特种兵", "hp": 100, "signal_energy": 100, "aim_stability": 95}
            ],
            "special_ascension_stat": {"stat_name": "高倍镜屏息稳定性", "values": {"特长": "屏息时间延长 50%，弹道下坠修正感知"}},
            "ascension_materials": [{"tier": "特训进阶", "items": "鹰眼勋章、高地架枪大师"}],
            "talents": [
                {"name": "马格南致命穿杨", "type": "NORMAL_ATTACK", "description": "手持 AWM 装填 .300 马格南子弹，无视任何防具等级，命中头部一击必杀！", "scaling": "单发头部爆头伤害高达 300 点，哪怕满耐久三级头也直接粉碎"},
                {"name": "测距下坠修正", "type": "ELEMENTAL_SKILL", "description": "利用八倍镜密位密位刻度快速测量目标距离（200m、400m、600m），抬高枪口准星精准抵消重力下坠。", "scaling": "超视距 400 米外精准点杀跑毒敌人"}
            ],
            "passives": [{"name": "吉利伪装", "desc": "在草丛中卧倒时隐蔽度提升 80%，极大降低被敌方远点开镜察觉概率。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "占领安全区制高点反斜面 -> 八倍镜侦察转移载具 -> 预判提前量一枪爆头击倒敌方头领！"},
            "recommendations": {"weapons": {"bis": "AWM (八倍镜+消音) + Mk14 妹控"}, "artifacts": {"bis_set": "吉利服潜行套件"}},
            "version": "1.27"
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
                27, %s, %s, %s, %s, %s, %s,
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
            "name": "M416 突击步枪 (满配件激光枪)",
            "type": "5.56mm 全自动突击步枪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/gp/weapon_m416.png",
            "base_atk_curve": [
                {"level": "裸枪状态", "atk": 41, "recoil": "较高", "mag": 30},
                {"level": "满配状态", "atk": 41, "recoil": "极低(激光枪)", "mag": 40}
            ],
            "sub_stat": {"type": "弹道与配件槽", "values": {"配件槽数": "枪口、握把、弹匣、枪托、瞄准镜 5槽全齐"}},
            "refinements": [
                {"rank": 1, "desc": "装配战术枪托与垂直握把后，水平与垂直后坐力大幅衰减，中近距离 4 倍镜压枪稳如激光！"}
            ],
            "ascension_materials": [{"tier": "满配条件", "items": "补偿器 + 垂直握把 + 快速扩容 + 战术枪托"}],
            "version": "1.27"
        },
        {
            "name": "AWM 栓动狙击枪 (空投神器)",
            "type": ".300 马格南重型栓动狙击枪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/gp/weapon_awm.png",
            "base_atk_curve": [
                {"level": "单发伤害", "atk": 105, "headshot": 300, "bullet_speed": 910}
            ],
            "sub_stat": {"type": "贯穿力与初速", "values": {"子弹初速": "910 m/s 超高初速，弹道平直几乎无下坠"}},
            "refinements": [
                {"rank": 1, "desc": "空投专属王者！无论敌人是否佩戴三级头盔，命中头部一击必杀！"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "空投补给箱限量产出 (附带20发马格南弹)"}],
            "version": "1.27"
        },
        {
            "name": "Vector 维克托冲锋枪",
            "type": ".45 ACP 战术冲锋枪",
            "rarity": 4,
            "icon_url": "https://patchwiki.biligame.com/images/gp/weapon_vector.png",
            "base_atk_curve": [
                {"level": "极限射速", "atk": 31, "rpm": 1100, "dps": 568}
            ],
            "sub_stat": {"type": "近战秒伤", "values": {"射速": "1100发/分，近战贴脸 0.2 秒内融化敌人"}},
            "refinements": [
                {"rank": 1, "desc": "短道冲锋之王，装配扩容弹匣后弹容量由 19 发提升至 33 发，攻楼与反打近战利器。"}
            ],
            "ascension_materials": [{"tier": "核心配件", "items": "快速扩容弹匣、激光瞄准器"}],
            "version": "1.27"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                27, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "三级神装防具套件 (Tier 3 Military Armor)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/gp/set_tier3.png",
            "two_piece_bonus": "减免 55% 受到的枪械伤害，防御耐久度高达 230 点，头部可硬抗 98K 爆头不倒地。",
            "four_piece_bonus": "配合三级背包，背包装载容量上限直接提升至 270 点，可随身携带 5 颗手雷、4 颗烟雾弹及充足弹药药品。",
            "pieces": [
                {"slot": "头部防具", "name": "三级头盔 (Spetsnaz Helmet)", "main_stat": "头部减伤 55% / 耐久 230"},
                {"slot": "身体防具", "name": "三级防弹衣 (Military Vest)", "main_stat": "躯干减伤 55% / 耐久 250"},
                {"slot": "战术背包", "name": "三级背包 (Large Backpack)", "main_stat": "容量 +270 / 迷彩隐蔽"}
            ],
            "version": "1.27"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                27, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "毒圈机制",
            "title": "和平精英 信号接收区阶段递进缩圈与衰减公式",
            "formula": "Signal_Drain_Rate(Phase) = Base_Rate * (Phase ^ 1.65) * (Distance_To_Safe_Zone_Ratio)",
            "parameters": {
                "phase1_4": "前4圈信号值扣减缓慢（1~3点/秒），可用饮料和止痛药平稳抵消",
                "phase5_8": "决赛圈阶段每秒扣除 8~18 点信号值，并在 0 信号值时立即倒地出局，必须依托载具提前进圈占位"
            }
        },
        {
            "category": "弹道算法",
            "title": "真实弹道下坠与水平垂直后坐力衰减模型",
            "formula": "Bullet_Height(t) = V0_y * t - 0.5 * g * (t^2), Horizontal_Spread = Random(-1, 1) * Recoil_Coefficient",
            "parameters": {
                "recoil": "垂直后坐力随着持续扫射呈线性抬升，前 5 发子弹精度最高，后 15 发需要匀速向下拉动屏幕压枪，配合陀螺仪微调命中率最高"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (27, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (27, '和平精英 海岛图军事基地刚枪与转点速冲无敌战神全解', 1, 'BUILD', 'ADVANCED', '["和平精英", "海岛图", "军事基地", "无敌战神", "压枪手法"]',
                '详解高分排位运营思路：C字楼跳伞速落技巧、三号楼十字架卡点、高架架枪视野封锁与快艇海路转圈运营路线。',
                '{"sections":[{"title":"一、高低架视野压制","text":"落地抢占高架制高点，持有红点或全息即可对 C 楼露头敌人进行抽靶，配合队友拉枪线实现瓮中捉鳖。"},{"title":"二、决赛圈载具掩体搭建","text":"进入第 6 阶段后切忌徒步跑毒，驾驶吉普车进入圈内反斜面并射爆轮胎，可搭建绝对安全的钢制物理掩体。"}]}',
                'PUBLISHED', 4500, 3980, 30, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (27, '和平精英 常用枪械配件与弹药口径兼容大全',
                '1. 5.56mm 系：M416、SCAR-L、AUG、Mini14，初速快弹道平直，适合中距离全自动扫射；2. 7.62mm 系：AKM、M762、Kar98k、AWM（空投），单发单核伤害极高但垂直后坐力巨大；3. 枪口配件：枪口补偿器降低垂直与水平后坐力，消焰器消除枪口火光，消音器极大降低声响并隐蔽枪声指示；4. 握把选择：垂直握把抑制垂直抬手，轻型握把提升单点稳定性，半截式握把提升扫射连贯性。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 和平精英 同步完成 ---")

# ==========================================
# 3. 金铲铲之战 (Battle of the Golden Spatula, ID = 28)
# ==========================================
def sync_battle_of_the_golden_spatula(cur):
    print("--- 正在同步 金铲铲之战 (Battle of the Golden Spatula, game_id = 28) ---")
    gid = 28

    chars = [
        {
            "name": "大成九五至尊 (Fast-9 Legendary)",
            "title": "终极天花板·全五费大成",
            "rarity": 5,
            "element": "全能神话 / 传奇羁绊",
            "weapon_type": "九五豪华主C神装",
            "region": "金铲铲·S12魔法乱斗",
            "avatar_url": "https://patchwiki.biligame.com/images/jcc/thumb/avatar_fast9.png/120px-avatar_fast9.png",
            "splash_url": "https://patchwiki.biligame.com/images/jcc/thumb/avatar_fast9.png/600px-avatar_fast9.png",
            "base_stats": [
                {"level": "1星", "hp": 1100, "atk": 85, "armor": 50, "mr": 50},
                {"level": "2星", "hp": 2200, "atk": 155, "armor": 60, "mr": 60},
                {"level": "3星", "hp": 4500, "atk": 350, "armor": 100, "mr": 100}
            ],
            "special_ascension_stat": {"stat_name": "羁绊质变与技能倍率", "values": {"全员五费": "技能覆盖全屏毁灭打击"}},
            "ascension_materials": [{"tier": "成型门槛", "items": "速升 9 级，至少 50 金币搜牌储备"}],
            "talents": [
                {"name": "终极大招全屏轰炸", "type": "ELEMENTAL_BURST", "description": "法力值打满后向全屏敌人倾泻奥术洪流，造成 2500 点魔法伤害并使目标眩晕 2 秒！", "scaling": "二星即可毁灭任何常规四费体系"},
                {"name": "前排坚壁屹立不倒", "type": "NORMAL_ATTACK", "description": "五费坦克弈子获得高额最大生命值护盾并嘲讽周围 3 格敌人。", "scaling": "提供长达 8 秒绝对安全输出环境"}
            ],
            "passives": [{"name": "高阶压制", "desc": "敌方每阵亡一名弈子，己方全员获得 10% 攻击速度与法强提升。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "前期依靠强力低费打工锁血吃满 50 利息 -> 4-2 升 8 级保血 -> 5-2 冲 9 级大搜转全员五费大成！"},
            "recommendations": {"weapons": {"bis": "鬼索的狂暴之刃 + 灭世者的死亡之帽 + 狂徒铠甲"}, "artifacts": {"bis_set": "棱彩阶升级咯海克斯套件"}},
            "version": "S12"
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
                28, %s, %s, %s, %s, %s, %s,
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
            "name": "鬼索的狂暴之刃 (Guinsoo's Rageblade / 羊刀)",
            "type": "攻速成长神装",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/jcc/item_rageblade.png",
            "base_atk_curve": [
                {"level": "基础面板", "atk": 10, "ap": 15, "as": "+15%"}
            ],
            "sub_stat": {"type": "无上限叠攻速", "values": {"叠层效果": "每次普通攻击永久增加 5% 攻击速度，无限叠层"}},
            "refinements": [
                {"rank": 1, "desc": "残局无解输出神器！后排主 C 必备，战斗持续 10 秒后攻速达到 5.0 上限，疯狂回蓝释放大招。"}
            ],
            "ascension_materials": [{"tier": "合成配方", "items": "无用大棒 + 反曲之弓"}],
            "version": "S12"
        },
        {
            "name": "狂徒铠甲 (Warmog's Armor)",
            "type": "终极生命值防具",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/jcc/item_warmogs.png",
            "base_atk_curve": [
                {"level": "坦度加成", "hp": 1000, "bonus_hp": "+12% 最大生命值"}
            ],
            "sub_stat": {"type": "血量扩充", "values": {"特性": "直接提供 1000 点巨额额外生命值并放大百分比"}},
            "refinements": [
                {"rank": 1, "desc": "前排主坦核心件，配合坚定之心或救赎，让单顶前排吸收万点伤害。"}
            ],
            "ascension_materials": [{"tier": "合成配方", "items": "巨人腰带 + 巨人腰带"}],
            "version": "S12"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                28, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "棱彩阶符文强化套件 (Prismatic Augment Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/jcc/augment_prismatic.png",
            "two_piece_bonus": "【升级咯！】：购买经验值时额外提供 3 点经验，且可以升至 10 级。",
            "four_piece_bonus": "【对冲基金】：每回合利息上限提升至 10 金币（本金满 100 金币），经济碾压全场速登九五。",
            "pieces": [
                {"slot": "经济强化", "name": "对冲基金 (Hedge Fund)", "main_stat": "利息上限翻倍至 10 金币"},
                {"slot": "经验强化", "name": "升级咯！(Level Up!)", "main_stat": "升级消耗大幅减少，直通 10 级"},
                {"slot": "战力强化", "name": "棱彩门票 (Prismatic Ticket)", "main_stat": "每次搜牌 50% 概率免费"}
            ],
            "version": "S12"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                28, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "经济机制",
            "title": "金铲铲之战 基础利息与连胜连败复利收益函数",
            "formula": "Round_Income = Base(5) + Interest(min(floor(Gold/10), 5)) + Streak_Bonus(2~3=1g, 4=2g, 5+=3g) + Victory_Gold(1g)",
            "parameters": {
                "interest": "手中每保留 10 金币，下回合开始结算额外 1 金币利息（上限 5 金币，特定海克斯可达 10 金币）",
                "streak": "连胜或连败均可获得额外经济补偿，最忌讳一胜一负经济崩盘"
            }
        },
        {
            "category": "抽卡概率",
            "title": "人口等级各费率卡牌刷新概率阶梯矩阵",
            "formula": "Prob_Matrix(Level, Tier): L7(19/35/35/10/1%), L8(18/25/32/22/3%), L9(10/15/25/35/15%), L10(5/10/20/40/25%)",
            "parameters": {
                "fast_9": "9级五费卡刷新概率由8级的3%暴增至15%，是搜出两星五费大成九五的黄金质变点"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (28, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (28, '金铲铲 S12 魔法乱斗大师王者速8冲9大成九五运营全解', 1, 'BUILD', 'ADVANCED', '["金铲铲", "S12", "九五之尊", "速8", "经济运营"]',
                '详解开局留牌与节奏把控：2-1 升 4、2-5 升 5、3-2 升 6 保连胜；4-1 升 7 稳血、4-2 升 8 级大搜基础四费锁血，5-2 直冲 9 级大换阵。',
                '{"sections":[{"title":"一、前期打工与保利息","text":"不要强行玩死阵容！前期来什么两星用什么，给肉装日炎或羊刀打工，保持血量在 80 点以上进入四阶段。"},{"title":"二、九五大搜换阵技巧","text":"上 9 级后先在备战席买下所有搜到的五费卡（米利欧、泽拉斯、诺拉、斯莫德），待成对两星后一回合快速完成全盘大换血！"}]}',
                'PUBLISHED', 4800, 4200, 32, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (28, '金铲铲之战 经典金铲铲与金锅锅转职合成表大全',
                '1. 金铲铲 + 大剑 = 狂暴战士转职；2. 金铲铲 + 反曲弓 = 猎手转职；3. 金铲铲 + 锁子甲 = 重装战士转职；4. 金铲铲 + 负极斗篷 = 魔战士转职；5. 金铲铲 + 无用大棒 = 术士转职；6. 金铲铲 + 女神泪 = 学者转职；7. 金铲铲 + 拳套 = 潜行者转职；8. 金铲铲 + 金铲铲 = 自然之力 (人口上限 +1)；9. 金锅锅 + 基础装备合成对应新赛季次生特色羁绊。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 金铲铲之战 同步完成 ---")

# ==========================================
# 4. 阴阳师 (Onmyoji, ID = 29)
# ==========================================
def sync_onmyoji(cur):
    print("--- 正在同步 阴阳师 (Onmyoji, game_id = 29) ---")
    gid = 29

    chars = [
        {
            "name": "阿修罗 (Asura)",
            "title": "深渊魔王·战神天刑",
            "rarity": 5,
            "element": "狂怒 / 暗黑炼狱",
            "weapon_type": "狱火骨刃",
            "region": "深渊·鬼域天域",
            "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_asura.png/120px-avatar_asura.png",
            "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_asura.png/600px-avatar_asura.png",
            "base_stats": [
                {"level": "1", "hp": 980, "atk": 160, "def": 68, "speed": 110, "crit": "10%"},
                {"level": "40 (六星满)", "hp": 11393, "atk": 4127, "def": 379, "speed": 113, "crit": "10%"}
            ],
            "special_ascension_stat": {"stat_name": "S级攻击成长天花板", "values": {"40级满": "基础攻击 4127 傲视全服"}},
            "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 (白蛋) × 5 + 觉醒符印"}],
            "talents": [
                {"name": "炼狱虐杀 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "消耗 3 点鬼火，狂暴轰击目标造成 315% 伤害，随后对其余全体敌方进行多段骨刃横扫，每段造成 63% 全体伤害并消耗理性值！", "scaling": "魂土15s挖粮核弹，一击秒杀前两回目"},
                {"name": "天刑疾火 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "开局拥有 9 点理性值，每点理性值提升 6% 最终伤害。理性值为 0 时失去理智无差别疯狂连击。", "scaling": "开局自带最高 54% 独立满增伤"}
            ],
            "passives": [{"name": "狂骨压制", "desc": "击杀敌方目标时立即恢复 3 点理性值。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "一速拉条式神抢先手 -> 增伤式神提供攻击加成 -> 阿修罗释放炼狱虐杀一键秒全场！"},
            "recommendations": {"weapons": {"bis": "满速爆伤破势六号位"}, "artifacts": {"bis_set": "破势四件套 + 歌伎两件套"}},
            "version": "v1.7"
        },
        {
            "name": "须佐之男 (Susanoo)",
            "title": "处刑之神·天羽羽斩",
            "rarity": 5,
            "element": "神圣雷霆",
            "weapon_type": "雷神巨剑",
            "region": "高天原·神域",
            "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_susanoo.png/120px-avatar_susanoo.png",
            "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_susanoo.png/600px-avatar_susanoo.png",
            "base_stats": [
                {"level": "40 (六星满)", "hp": 10850, "atk": 4015, "def": 410, "speed": 115, "crit": "12%"}
            ],
            "special_ascension_stat": {"stat_name": "天羽羽斩神罚", "values": {"单体斩杀": "六把雷剑锁定消灭免死目标"}},
            "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 × 5"}],
            "talents": [
                {"name": "天羽羽斩·崩灭 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "凝聚六把天羽羽斩连续贯穿目标，造成 6 段高达 480% 的单体雷电轰击，目标阵亡后化为雷剑封印其复活能力！", "scaling": "PVP斗技单体点杀最高倍率"}
            ],
            "passives": [{"name": "雷霆神威", "desc": "行动前自动获得雷盾，免疫首次受到的致命伤害。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "配合千姬、SP鬼吞 -> 须佐天羽羽斩单点秒杀敌方核心输出 -> 雷剑插地永久封印复活！"},
            "recommendations": {"weapons": {"bis": "针女/网切 满爆伤"}, "artifacts": {"bis_set": "针女四件套 + 鬼灵歌伎两件套"}},
            "version": "v1.7"
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
                29, %s, %s, %s, %s, %s, %s,
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
            "name": "极品御魂六位阵 (满速爆伤神装)",
            "type": "式神御魂六格阵位",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yys/mitama_array.png",
            "base_atk_curve": [
                {"level": "+0", "atk": 80, "speed": 2, "crit_dmg": "8%"},
                {"level": "+15 (满强化)", "atk": 486, "speed": 18, "crit_dmg": "89%"}
            ],
            "sub_stat": {"type": "极限副词条", "values": {"一速天花板": "2号位双速满强化 +18 速度神话"}},
            "refinements": [
                {"rank": 1, "desc": "斗技与竞速的核心生命线！全套 +18 速度将式神速度推至 280+，抢下一速直接奠定胜局。"}
            ],
            "ascension_materials": [{"tier": "+15 消耗", "items": "青吉鬼、金币 50 万"}],
            "version": "v1.7"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                29, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "破势御魂四件套 (Shadow Mitama Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yys/mitama_shadow.png",
            "two_piece_bonus": "暴击率提升 15%。",
            "four_piece_bonus": "对生命值高于 70% 的目标，造成的所有伤害额外提升 40%（独立全局乘算乘区）。",
            "pieces": [
                {"slot": "壹号位", "name": "破势·天命", "main_stat": "固定攻击力 +486"},
                {"slot": "贰号位", "name": "破势·狂风", "main_stat": "速度 / 攻击加成 55%"},
                {"slot": "肆号位", "name": "破势·玄雷", "main_stat": "效果命中 / 攻击加成 55%"},
                {"slot": "陆号位", "name": "破势·极星", "main_stat": "暴击伤害 +89% (满爆伤)"}
            ],
            "version": "v1.7"
        },
        {
            "name": "招财猫御魂四件套 (Fortune Cat Mitama Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yys/mitama_fortune_cat.png",
            "two_piece_bonus": "防御力加成 30%。",
            "four_piece_bonus": "式神回合开始时，有 50% 概率直接获得 2 点宝贵的鬼火，全游唯一通用永动机御魂。",
            "pieces": [
                {"slot": "核心位", "name": "招财猫全套", "main_stat": "万物皆可招财，辅助与控场标配"}
            ],
            "version": "v1.7"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                29, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "行动条机制",
            "title": "阴阳师 行动条配速与拉条超车插队判定算法",
            "formula": "Action_Progress = (Shikigami_Speed / Max_Speed_On_Field) * 100%, Push_Bar = Action_Progress + Push_Value(30%)",
            "parameters": {
                "cut_in": "拉条式神（如镰鼬、山兔）增加目标 30% 行动条，如果溢出 100% 且速度高于敌方剩余进度，则触发超车插队先手行动"
            }
        },
        {
            "category": "减伤公式",
            "title": "阴阳师 经典防御减伤与伤害计算模型",
            "formula": "Damage_Taken = Raw_Damage * (300 / (300 + Defense)) * Crit_Damage * (1 + Damage_Bonus_Multiplier)",
            "parameters": {
                "defense": "300点基础防御提供 50% 减伤，当面对高防 Boss 时，穿透防御（如网切、SP修罗）收益呈指数级放大"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (29, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (29, '阴阳师 魂十一 (悲鸣) 15秒全自动超极速挖粮阵容配置全解', 1, 'BUILD', 'ADVANCED', '["阴阳师", "魂十一", "悲鸣", "阿修罗", "饭笥", "15秒速刷"]',
                '详解御魂副本高效率全自动挂机配队：一速阿修罗破势破心压血线、二速饭笥食灵自动开宴会斩杀黑晴明与八岐大蛇。',
                '{"sections":[{"title":"一、式神配速硬性阈值","text":"阿修罗速度必须大于 158 且小于 162，确保在第一回目大天狗之前出手，攻击力*暴伤指标需突破 23000 方可一击清屏。"},{"title":"二、饭笥收尾判定","text":"饭笥携带狂骨荒骷髅，在阿修罗第三回目压低大蛇血量至 50% 以下时触发储备爆发，无需动画即可瞬秒通关！"}]}',
                'PUBLISHED', 4100, 3650, 28, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (29, '阴阳师 御魂副词条强化概率与极限速度天花板百科',
                '1. 六星御魂初始拥有 2~4 条副词条，强化至 +3/+6/+9/+12/+15 时各随机增加一次副词条数值；2. 极限速度：初始 3 点速度，连续 5 次强化全部命中速度且均为 +3，极限理论单件速度为 3 + 5*3 = +18 速度；3. 斗技一速门槛：六件套全 +17 以上，配合式神 115 基础速度，全队总速度超越 278 点即可抢占绝对一速先机。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 阴阳师 同步完成 ---")

# ==========================================
# 5. 崩坏3 (Honkai Impact 3rd, ID = 30)
# ==========================================
def sync_honkai_impact_3rd(cur):
    print("--- 正在同步 崩坏3 (Honkai Impact 3rd, game_id = 30) ---")
    gid = 30

    chars = [
        {
            "name": "终焉之律者 (Herrscher of Finality)",
            "title": "地球之神·琪亚娜·卡斯兰娜",
            "rarity": 5,
            "element": "虚数 (IMG) / 火焰伤害",
            "weapon_type": "双枪 / 无名之钥",
            "region": "圣芙蕾雅 / 月球终焉",
            "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/102001/avatar_kiana.png",
            "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/102001/avatar_kiana.png",
            "base_stats": [
                {"level": "80级SSS", "hp": 4350, "atk": 1680, "def": 540, "crit": 95}
            ],
            "special_ascension_stat": {"stat_name": "绝对时空断裂", "values": {"终极权能": "暂停关卡计时与敌人一切行动"}},
            "ascension_materials": [{"tier": "进化晋升", "items": "终焉之律者碎片、高级进化素材"}],
            "talents": [
                {"name": "绝对时空断裂 (Time Regression)", "type": "ELEMENTAL_SKILL", "description": "积攒时锋能量长按闪避键释放，创造绝对时空断裂！关卡倒计时完全停止，全场敌人绝对静止，持续 30 秒进行多重分支狂轰滥炸！", "scaling": "深渊锁时间神技，争分夺秒拉满分"},
                {"name": "为了明天 (Discharge / Burst)", "type": "ELEMENTAL_BURST", "description": "消耗 100 SP 跃入高空，召唤月球引力发动行星级终结重击，造成高达 3250% 火焰元素伤害并直接斩杀虚数核心！", "scaling": "虚数怪物核心直接剥离斩杀"}
            ],
            "passives": [{"name": "三生万物", "desc": "与始源之律者、真理之律者同队时，解锁特殊三人连携爆发形态，大幅提升全队全伤害。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "真理之律者开大提供元素穿透 -> 始源之律者出场爆发挂易伤 -> 终焉之律者 QTE 砸下进入绝对时空断裂清场！"},
            "recommendations": {"weapons": {"bis": "无名之境：宿命 (超限)"}, "artifacts": {"bis_set": "名为终焉之名专属圣痕三件套"}},
            "version": "v7.8"
        },
        {
            "name": "始源之律者 (Herrscher of Origin)",
            "title": "人之律者·雷电芽衣",
            "rarity": 5,
            "element": "虚数 (IMG) / 雷电伤害",
            "weapon_type": "太刀 / 澄凝之境",
            "region": "逐火之蛾·往世乐土",
            "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/102001/avatar_mei.png",
            "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/102001/avatar_mei.png",
            "base_stats": [
                {"level": "80级SSS", "hp": 4200, "atk": 1650, "def": 520, "crit": 105}
            ],
            "special_ascension_stat": {"stat_name": "心意真刀流", "values": {"雷电穿透": "+20% 独立雷伤元素穿透"}},
            "ascension_materials": [{"tier": "进化晋升", "items": "始源之律者碎片"}],
            "talents": [
                {"name": "雷电极斩 (Burst)", "type": "ELEMENTAL_BURST", "description": "释放大招进入连续居合斩击模式，划过屏幕连续劈出 12 刀极光雷斩，造成 2800% 雷电爆发伤害！", "scaling": "极速居合连击，手感天花板"}
            ],
            "passives": [{"name": "飞羽连心", "desc": "极限闪避触发全局时空断裂，并充满心之所向动能条。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "极速闪避触发时空 -> 闪避居合收刀回能量 -> 释放大招划屏十二连斩。"},
            "recommendations": {"weapons": {"bis": "澄凝之境：自往"}, "artifacts": {"bis_set": "雷电芽衣专属圣痕三件套"}},
            "version": "v7.8"
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
                30, %s, %s, %s, %s, %s, %s,
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
            "name": "无名之钥 / 无名之境：宿命 (超限武器)",
            "type": "超限双枪武器",
            "rarity": 5,
            "icon_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/weapon_anon.png",
            "base_atk_curve": [
                {"level": "50级", "atk": 298, "crit": 32},
                {"level": "65级 (超限满)", "atk": 436, "crit": 64}
            ],
            "sub_stat": {"type": "火伤与终焉强化", "values": {"被动": "终焉之律者装备时分支伤害提升 45%，绝对时空断裂持续时间延长"}},
            "refinements": [
                {"rank": 1, "desc": "释放武器主动造成 800% 火焰伤害，并直接为动能槽充能两格，实现秒发分支攻击。"}
            ],
            "ascension_materials": [{"tier": "超限材料", "items": "超导金属、爱因斯坦环磁机"}],
            "version": "v7.8"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                30, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "琪亚娜·卡斯兰娜专属圣痕三件套 (Kiana Kaslana Stigmata)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/stigmata_kiana.png",
            "two_piece_bonus": "全伤害提升 35%，分支攻击命中敌人使其受到火焰伤害额外提升 30%。",
            "four_piece_bonus": "在绝对时空断裂期间，全队全伤害提升 40%，且击杀虚数怪物时直接斩杀虚数核心。",
            "pieces": [
                {"slot": "上位 (Top)", "name": "琪亚娜·终焉·上", "main_stat": "火焰伤害 +40%"},
                {"slot": "中位 (Mid)", "name": "琪亚娜·终焉·中", "main_stat": "全伤害 +30% / 减伤 20%"},
                {"slot": "下位 (Bot)", "name": "琪亚娜·终焉·下", "main_stat": "全元素穿透 +18%"}
            ],
            "version": "v7.8"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                30, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "闪避判定",
            "title": "崩坏3 极限闪避触发全局时空断裂机制",
            "formula": "Time_Fracture = (Enemy_Attack_Active == TRUE) AND (Dodge_Pressed == TRUE) -> Global_Time_Dilation(0.05x, Duration=3.0s)",
            "parameters": {
                "fracture": "全场敌人动作放慢 95%，计时器大幅变慢，并立即激活后台女武神的 QTE 出场连携开关"
            }
        },
        {
            "category": "属性克制",
            "title": "崩坏3 属性闭环克制与增伤系数",
            "formula": "Damage_Multiplier = Base * (Countered ? 1.30 : (Neutral ? 1.0 : 0.70))",
            "parameters": {
                "triangle": "机械克制生物、生物克制异能、异能克制机械；量子与虚数互相独立互不干扰，虚数直接击杀核心机制"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (30, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (30, '崩坏3 超弦空间红莲寂灭律者三人组爆发循环手顺全解', 1, 'BUILD', 'ADVANCED', '["崩坏3", "超弦空间", "终焉之律者", "始源", "真理", "红莲寂灭"]',
                '详解终焉三人组轮切爆发：真理机甲形态开启全队元素穿透、始源QTE接大招快速挂雷电易伤、终焉登场开启绝对时空断裂打满分支。',
                '{"sections":[{"title":"一、前置铺垫与穿透buff","text":"真理之律者开场两段分支迅速攒满动能，释放大招切换形态提供长达 18 秒的 17% 元素穿透，此为整套爆发的乘区基石。"},{"title":"二、终焉绝对时空断裂","text":"终焉切入后立即长按闪避键开启绝对时空断裂，关卡倒计时暂停，依次打出紫焰与金煌双分支，随后释放行星级大招一发带走关底首领！"}]}',
                'PUBLISHED', 3900, 3450, 26, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (30, '崩坏3 角色属性克制与超限武器研发系统百科',
                '1. 属性克制：生物、异能、机械构成经典三克制闭环，克制造成 130% 伤害，被克制造成 70% 伤害；量子与虚数具有坍缩与核心机制，星尘属性具备剥离碎核特性；2. 超限武器系统：舰长等级达到 81 级后解锁，可将满级 50 级初始五星武器突破为 65 级超限形态，赋予全额新被动技能与更高面板攻击力。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 崩坏3 同步完成 ---")

# ==========================================
# 6. 重返未来：1999 (Reverse: 1999, ID = 31)
# ==========================================
def sync_reverse_1999(cur):
    print("--- 正在同步 重返未来：1999 (Reverse: 1999, game_id = 31) ---")
    gid = 31

    chars = [
        {
            "name": "6 (Six)",
            "title": "启示者·智之极点",
            "rarity": 6,
            "element": "智 (Intelligence)",
            "weapon_type": "神秘术 / 智慧权杖",
            "region": "阿派朗学派·第一道命题",
            "avatar_url": "https://patchwiki.biligame.com/images/re1999/thumb/avatar_six.png/120px-avatar_six.png",
            "splash_url": "https://patchwiki.biligame.com/images/re1999/thumb/avatar_six.png/600px-avatar_six.png",
            "base_stats": [
                {"level": "洞悉三 60级", "hp": 7180, "atk": 1150, "def": 680, "crit_tech": 320}
            ],
            "special_ascension_stat": {"stat_name": "全能灵光增益", "values": {"灵光上限": "最多持有 6 点灵光，自动消耗净化队友并爆发"}},
            "ascension_materials": [{"tier": "洞悉三", "items": "狂人絮语、善恶之果、金爪钥匙"}],
            "talents": [
                {"name": "责任 (Skill 1)", "type": "NORMAL_ATTACK", "description": "单体攻击造成 200% 精神创伤，并根据敌方身上的减益状态数量造成额外爆发，若自身拥有 4 点灵光则消耗灵光施加全属性抗性削弱！", "scaling": "集输出与破抗于一体"},
                {"name": "执纪 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "为己方全体施加随机 2 种强力增益（反弹、增伤、穿透、护盾），并净化全队 2 个异常状态，消耗灵光使效果翻倍！", "scaling": "全游戏最强群体解控与增益"},
                {"name": "漫长的启示 (Ultimate)", "type": "ELEMENTAL_BURST", "description": "消耗 5 点激情释放至终仪式，单体造成 700% 精神创伤，并赋予全队持续 2 回合的【受创减免】与【创伤加成】。", "scaling": "辅助核弹，攻守兼备"}
            ],
            "passives": [{"name": "不言的戒律", "desc": "回合结束时，若队友身上的减益状态被净化，自身获得 1 点灵光与 1 点激情。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "平稳积攒灵光 -> 敌方施加高危Debuff时释放【执纪】瞬间全队净化反打 -> 激情打满释放至终仪式锁定胜局！"},
            "recommendations": {"weapons": {"bis": "心相：漫长悄悄话"}, "artifacts": {"bis_set": "思维拓扑暴击共鸣拼图盘"}},
            "version": "v2.2"
        },
        {
            "name": "曲娘 (Jiu Niangzi)",
            "title": "沛然莫御·九娘子",
            "rarity": 6,
            "element": "岩 (Mineral)",
            "weapon_type": "神秘术 / 酒器与算筹",
            "region": "东土大荒·沛县",
            "avatar_url": "https://patchwiki.biligame.com/images/re1999/thumb/avatar_quniang.png/120px-avatar_quniang.png",
            "splash_url": "https://patchwiki.biligame.com/images/re1999/thumb/avatar_quniang.png/600px-avatar_quniang.png",
            "base_stats": [
                {"level": "洞悉三 60级", "hp": 6890, "atk": 1280, "def": 640, "crit_tech": 450}
            ],
            "special_ascension_stat": {"stat_name": "酒意暴击加成", "values": {"暴击创伤": "暴击率转化酒意，伤害翻倍"}},
            "ascension_materials": [{"tier": "洞悉三", "items": "不凋之花、银矿石"}],
            "talents": [
                {"name": "更尽一杯 (Skill 1)", "type": "NORMAL_ATTACK", "description": "单体现实创伤攻击，消耗【酒意】转化为额外追加打击，打满最高造成 450% 巨量单体伤害！", "scaling": "岩系第一单体大核"},
                {"name": "提真味 (Ultimate)", "type": "ELEMENTAL_BURST", "description": "至终仪式释放大荒酒阵，造成全屏 400% 现实创伤，并根据自身酒意层数引发二次大爆炸！", "scaling": "清场与攻坚双料顶级倍率"}
            ],
            "passives": [{"name": "醉翁之意", "desc": "行动点消耗后自动获得 2 层酒意，酒意层数提高自身暴击率与暴击创伤。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "前期存卡叠加酒意 -> 配合辅助施加易伤 -> 一回合连续释放满酒意【更尽一杯】瞬间蒸发 Boss！"},
            "recommendations": {"weapons": {"bis": "心相：敲响沉钟 / 美丽新世界"}, "artifacts": {"bis_set": "高暴击共鸣盘"}},
            "version": "v2.2"
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
                31, %s, %s, %s, %s, %s, %s,
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
            "name": "漫长悄悄话 (Long Quiet Chat)",
            "type": "六星心相 (Psychube)",
            "rarity": 6,
            "icon_url": "https://patchwiki.biligame.com/images/re1999/psychube_whisper.png",
            "base_atk_curve": [
                {"level": "1级", "atk": 65, "hp": 480},
                {"level": "60级 (满增幅)", "atk": 380, "hp": 2900}
            ],
            "sub_stat": {"type": "术法威力与净化增益", "values": {"特性": "术法威力提升 18%，净化状态后全伤害提升 12%"}},
            "refinements": [
                {"rank": 1, "desc": "智属性与全能辅助专属神装，极大强化团队续航与反打能力。"}
            ],
            "ascension_materials": [{"tier": "心相升阶", "items": "微尘、利齿子儿、偏振"}],
            "version": "v2.2"
        },
        {
            "name": "美丽新世界 (Brave New World)",
            "type": "六星心相 (Psychube)",
            "rarity": 6,
            "icon_url": "https://patchwiki.biligame.com/images/re1999/psychube_bnw.png",
            "base_atk_curve": [
                {"level": "1级", "atk": 70, "hp": 450},
                {"level": "60级 (满增幅)", "atk": 410, "hp": 2750}
            ],
            "sub_stat": {"type": "仪式威力加成", "values": {"特性": "仪式威力提升 18%，释放仪式后下一张普通咒语伤害提升 40%"}},
            "refinements": [
                {"rank": 1, "desc": "爆发输出手通用天花板心相，曲娘与大招流主 C 必备。"}
            ],
            "ascension_materials": [{"tier": "心相升阶", "items": "偏振材料"}],
            "version": "v2.2"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                31, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "思维拓扑暴击共鸣盘 (Critical Resonance Grid)",
            "rarity_min": 6,
            "rarity_max": 6,
            "icon_url": "https://patchwiki.biligame.com/images/re1999/resonance_grid.png",
            "two_piece_bonus": "共鸣 10 阶拼图全满：暴击率提升 25%，暴击创伤提升 35%。",
            "four_piece_bonus": "共鸣 15 阶究极质变：造成现实/精神创伤时，若触发暴击额外附带目标当前生命值 8% 的穿透创伤。",
            "pieces": [
                {"slot": "核心拼块", "name": "十字双生核心", "main_stat": "攻击力 +180 / 暴击创伤 +20%"},
                {"slot": "侧翼拼块", "name": "直角敏锐拓扑", "main_stat": "暴击率 +15% / 穿透率 +10%"}
            ],
            "version": "v2.2"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                31, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "合卡机制",
            "title": "重返未来1999 神秘术合卡升阶与激情获取模型",
            "formula": "Card_Rank_Up: (1-Star + 1-Star = 2-Star) -> Moxie +1, Action_Cast_Card -> Moxie +1, Total_Moxie(5) -> Ultimate_Generated",
            "parameters": {
                "moxie": "每打出一张咒语卡获得 1 点激情，同名同星级卡牌移动合成升阶额外奖励 1 点激情，满 5 点激情下回合必然生成至终仪式卡牌"
            }
        },
        {
            "category": "灵感克制",
            "title": "灵感四相循环与智沉互克闭环",
            "formula": "Beast -> Plant -> Star -> Mineral -> Beast (30% Damage Bonus, 15% Reduction), Spirit <-> Intelligence (Mutual 30% Bonus)",
            "parameters": {
                "counter": "兽克木、木克星、星克岩、岩克兽（克制方造成 130% 创伤并获得 15% 减伤）；灵与智互相克制，互为双向 30% 增伤"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (31, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (31, '重返未来1999 深眠域高层满星克制配队与激情连大爆发全解', 1, 'BUILD', 'ADVANCED', '["重返未来1999", "深眠域", "曲娘", "6", "激情合卡", "满星通关"]',
                '详解人工梦游深眠域攻略：合卡升星赚取多点激情、司辰技能洗牌与移动卡牌节奏把控、曲娘单核满酒意暴击秒杀关底首领。',
                '{"sections":[{"title":"一、第一回合调控手牌","text":"首回合切忌无脑乱打！优先将两张 1 阶卡牌向中间移动合并为 2 阶，消耗 1 点行动力净赚 1 点激情，第二回合即可直接开出大招！"},{"title":"二、6 与曲娘的黄金联动","text":"6 的二技能【执纪】为曲娘提供大量穿透与受创减免，曲娘叠满酒意后打出 2 阶【更尽一杯】，直接暴击秒杀关底小怪并打残首领！"}]}',
                'PUBLISHED', 4300, 3800, 29, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (31, '重返未来1999 灵感克制与创伤类型判定全百科',
                '1. 灵感克制：兽、木、星、岩四相循环相克，克制方造成伤害提高 30%，受到被克制方伤害降低 15%；灵与智自成体系互克，双向增伤 30%；2. 创伤类型：现实创伤（受现实防御抵消）与精神创伤（受精神防御抵消），本源创伤（无视防御与减伤的绝对真实创伤）；3. 异常状态分为控制（眩晕、石化、缴械、缄默）与负面状态（中毒、腐蚀、虚弱），控制状态下无法释放对应卡牌。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 重返未来：1999 同步完成 ---")

# ==========================================
# 主执行入口
# ==========================================
def sync_all():
    print("=== 开始同步六大热门手游数据 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    register_games(cur)
    sync_tower_of_fantasy(cur)
    sync_game_for_peace(cur)
    sync_battle_of_the_golden_spatula(cur)
    sync_onmyoji(cur)
    sync_honkai_impact_3rd(cur)
    sync_reverse_1999(cur)
    conn.commit()
    conn.close()
    print("=== 六大热门手游全量数据同步完成！ ===")

if __name__ == '__main__':
    sync_all()
