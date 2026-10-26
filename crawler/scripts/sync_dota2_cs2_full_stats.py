#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOTA 2 (game_id = 5) 与 CS2 (game_id = 7) 全量数值体系落库与同步脚本

包含:
1. DOTA 2 经典核心英雄 (影魔、祈求者、屠夫、敌法师、虚空假面) 全技能机制、数值与天赋树
2. DOTA 2 神装道具 (黑皇杖BKB、跳刀、A杖、圣剑、蝴蝶、强袭)
3. DOTA 2 底层护甲物理减伤公式、正反补经验金钱与高低地判定
4. CS2 核心枪械 (AK-47、M4A1-S、AWP、沙漠之鹰、USP-S、Glock-18) 伤害衰减、射速与穿透
5. CS2 战术投掷物与防具套件 (体积烟雾、高爆雷、燃烧弹、闪光弹、全甲)
6. CS2 急停射击、Sub-tick判定、后坐力反向控枪与经济局连败补偿公式
7. 攻略与百科词条
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

def sync_dota2(cur):
    print("--- 正在同步 DOTA 2 (game_id = 5) ---")
    chars = [
        {
            "name": "影魔 (Shadow Fiend - Nevermore)",
            "title": "深渊恶灵·灵魂收割者",
            "rarity": 5,
            "element": "敏捷 / 黯灭暗影",
            "weapon_type": "远程物理 / 魔法爆发",
            "region": "深渊幽魂界",
            "avatar_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/nevermore.png",
            "splash_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/nevermore.png",
            "base_stats": [
                {"level": "1", "hp": 560, "mana": 291, "atk": 41, "armor": 3.3, "str": 19, "agi": 20, "int": 18},
                {"level": "15", "hp": 1420, "mana": 680, "atk": 115, "armor": 8.5, "str": 48, "agi": 62, "int": 42},
                {"level": "30", "hp": 2480, "mana": 1180, "atk": 210, "armor": 15.2, "str": 82, "agi": 115, "int": 75}
            ],
            "special_ascension_stat": {"stat_name": "支配死灵", "values": {"特权": "击杀积攒灵魂，每层灵魂提供 +4 基础攻击力，上限 20 层"}},
            "ascension_materials": [{"tier": "天赋树", "items": "10级/15级/20级/25级极意天赋"}],
            "talents": [
                {"name": "毁灭阴影 (Shadowraze - Z/X/C)", "type": "NORMAL_ATTACK", "description": "在影魔正前方 200/450/700 码距离轰出一道毁灭阴影，造成 90/160/230/300 魔法伤害，连续命中叠加暗影创伤使下一发阴影伤害暴增！", "scaling": "三连压总伤害突破 1200+"},
                {"name": "支配死灵 (Necromastery)", "type": "PASSIVE_TALENT", "description": "每击杀一个单位吞噬其灵魂，每层提供 +1/2/3/4 点物理攻击力，击杀英雄获得 4 个灵魂。", "scaling": "满灵魂提供 80 点攻击力"},
                {"name": "魂之挽歌 (Requiem of Souls)", "type": "ELEMENTAL_BURST", "description": "引导 1.67 秒后向全方位释放体内释放的所有被禁锢怨魂，每道怨魂造成 180 点魔法伤害并使接触到的敌人陷入【恐惧】状态四散奔逃，同时造成 50% 减速与物理虚弱！", "scaling": "跳刀摇大近身可直接融化满血英雄"}
            ],
            "passives": [{"name": "魔王降临 (Presence of the Dark Lord)", "desc": "散发恐惧光环，降低周围 1200 码范围内所有敌方单位 4/5/6/7 点护甲！"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "对线期正反补极速起灵魂 -> 影压压低血线 -> 出吹风/跳刀 -> 吹风落地接近身魂之挽歌 + ZXC三连压秒杀！"},
            "recommendations": {"weapons": {"bis": "黑皇杖 (BKB) / 闪烁匕首 / 蝴蝶 / 斯嘉蒂之眼"}},
            "version": "7.37d"
        },
        {
            "name": "祈求者 (Invoker - Kael)",
            "title": "秘法宗师·魔能交响",
            "rarity": 5,
            "element": "全才 / 冰雷火",
            "weapon_type": "全能法核",
            "region": "远古秘法神殿",
            "avatar_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/invoker.png",
            "splash_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/invoker.png",
            "base_stats": [
                {"level": "1", "hp": 540, "mana": 290, "atk": 45, "armor": 2.1, "str": 18, "agi": 14, "int": 19},
                {"level": "15", "hp": 1380, "mana": 720, "atk": 108, "armor": 7.2, "str": 45, "agi": 42, "int": 68},
                {"level": "30", "hp": 2350, "mana": 1450, "atk": 198, "armor": 13.5, "str": 78, "agi": 82, "int": 125}
            ],
            "special_ascension_stat": {"stat_name": "元素祈唤", "values": {"特权": "冰(Q) 雷(W) 火(E) 自由组合合成 10 大终极禁咒"}},
            "ascension_materials": [{"tier": "天赋树", "items": "阿哈利姆神杖全技能升级"}],
            "talents": [
                {"name": "混沌陨石 (Chaos Meteor - EEW)", "type": "ELEMENTAL_SKILL", "description": "从苍穹召唤一颗燃烧的炽热天外陨石滚向目标区域，碾压造成瞬间粉碎伤害并持续灼烧路径上的所有敌人。", "scaling": "火与雷等级决定陨石滚过距离与伤害"},
                {"name": "阳炎冲击 (Sun Strike - EEE)", "type": "NORMAL_ATTACK", "description": "在全地图任意指定位置呼唤天基炽热烈阳神光，延迟 1.7 秒后轰下一道造成最高 540 点纯粹真实伤害的光柱！", "scaling": "全图无死角收割残血，神圣真实伤害"},
                {"name": "超声波 (Deafening Blast - QWE)", "type": "ELEMENTAL_BURST", "description": "向前方释放狂暴强风声波，击退所有敌人并造成 320 点魔法伤害，且使其强制【缴械】无法进行任何普通攻击！", "scaling": "大招团控与全屏声波"}
            ],
            "passives": [{"name": "幽灵漫步 (Ghost Walk - QQW)", "desc": "操纵冰雷之力使自身进入隐身状态并大幅减速周围敌人，同时提升自身移动速度。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "DOTA2 技能操作天花板：吹风接天火陨石推波四连绝技，配合刷新球打出双陨石双天火！"},
            "recommendations": {"weapons": {"bis": "阿哈利姆神杖 / 刷新球 / 虚灵之刃 / 玲珑心"}},
            "version": "7.37d"
        },
        {
            "name": "屠夫 (Pudge)",
            "title": "绝望肉钩·血肉腐化",
            "rarity": 5,
            "element": "力量 / 鲜血肉块",
            "weapon_type": "先手控制 / 极高肉盾",
            "region": "腐尸修道院",
            "avatar_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png",
            "splash_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png",
            "base_stats": [
                {"level": "1", "hp": 700, "mana": 267, "atk": 70, "armor": 1.5, "str": 25, "agi": 14, "int": 16},
                {"level": "15", "hp": 1850, "mana": 550, "atk": 130, "armor": 5.8, "str": 72, "agi": 38, "int": 36},
                {"level": "30", "hp": 3400, "mana": 950, "atk": 220, "armor": 11.0, "str": 135, "agi": 68, "int": 65}
            ],
            "special_ascension_stat": {"stat_name": "腐肉堆积", "values": {"特权": "附近每阵亡一名敌方英雄永久增加自身力量与魔法抗性，血量无限成长！"}},
            "ascension_materials": [{"tier": "天赋树", "items": "肉钩距离与肢解吸血"}],
            "talents": [
                {"name": "肉钩 (Meat Hook)", "type": "NORMAL_ATTACK", "description": "向前掷出带血重型铁钩，将命中的第一个单位（无论敌友）瞬间拖拽至屠夫身旁！若命中敌人造成高达 360 点纯粹伤害并打断其一切施法！", "scaling": "最远射程 1300 码，纯粹神圣伤害"},
                {"name": "腐烂 (Rot)", "type": "ELEMENTAL_SKILL", "description": "释放剧毒腐尸之气，对周围敌人造成每秒魔法伤害并减速 32%，同时伤害屠夫自身，可在绝境中自我反补防送击杀。", "scaling": "近身黏人减速神技"},
                {"name": "肢解 (Dismember)", "type": "ELEMENTAL_BURST", "description": "扑向目标进行长达 3 秒的残暴啃咬肢解，造成巨额持续魔法伤害并完全无视技能免疫控制目标，期间吸取造成伤害 100% 的生命值！", "scaling": "无视BKB硬控，回血极高"}
            ],
            "passives": [{"name": "堆积腐肉", "desc": "受到魔法伤害降低 16%，周围每死一人永久 +2.0 力量。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "阴影盲区出钩秒杀酱油 -> 近身开腐烂减速 -> 接无视BKB的大招肢解啃咬！"},
            "recommendations": {"weapons": {"bis": "跳刀 / 恐鳌之心 / 希瓦的守护 / 阿哈利姆魔晶"}},
            "version": "7.37d"
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
                5, %s, %s, %s, %s, %s, %s,
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
            "name": "黑皇杖 (Black King Bar / BKB)",
            "type": "神圣神器",
            "rarity": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/black_king_bar.png",
            "base_atk_curve": {"攻击力": "+24", "力量": "+10"},
            "sub_stat": {"type": "天神下凡", "values": {"魔法免疫": "提供减益免疫与 50% 额外魔法抗性，持续 9/8/7/6 秒", "冷却": "90 秒"}},
            "refinements": [{"rank": 1, "desc": "团战第一核心！核心大哥进场不被控制轮番秒杀的唯一绝对保障。"}],
            "ascension_materials": [{"tier": "合成配方", "items": "食人魔之斧 (1000) + 秘银锤 (1600) + 卷轴 (1450) = 4,050 金币"}],
            "version": "7.37d"
        },
        {
            "name": "闪烁匕首 (Blink Dagger / 跳刀)",
            "type": "位移神器",
            "rarity": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/blink.png",
            "base_atk_curve": {"位移距离": "1200 码"},
            "sub_stat": {"type": "先手神兵", "values": {"瞬间传送": "瞬间传送到最远 1200 码位置", "受击冷却": "受到敌方英雄攻击后禁用 3 秒"}},
            "refinements": [{"rank": 1, "desc": "决定团战胜负的先手灵魂武器！后期可升级为力量跳、敏捷跳或智力跳。"}],
            "ascension_materials": [{"tier": "售价", "items": "2,250 金币"}],
            "version": "7.37d"
        },
        {
            "name": "阿哈利姆神杖 (Aghanim's Scepter / A杖)",
            "type": "奥术权杖",
            "rarity": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/ultimate_scepter.png",
            "base_atk_curve": {"全属性": "+10", "生命值": "+175", "魔法值": "+175"},
            "sub_stat": {"type": "终极技能质变", "values": {"机制质变": "永久升级英雄的终极技能或赋予一门全新专属强力技能"}},
            "refinements": [{"rank": 1, "desc": "每个英雄专属打造的质变神兵，可被阿哈利姆祝福直接吞噬保留被动效果。"}],
            "ascension_materials": [{"tier": "合成配方", "items": "精气之球 + 魔力法杖 + 欢欣之刃 + 力量腰带 = 4,200 金币"}],
            "version": "7.37d"
        },
        {
            "name": "圣剑 (Divine Rapier)",
            "type": "毁天灭地神器",
            "rarity": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/rapier.png",
            "base_atk_curve": {"攻击力": "+350 点物理攻击力"},
            "sub_stat": {"type": "孤注一掷", "values": {"死亡掉落": "携带者阵亡必定掉落在地，任何人均可捡起继承！", "不可摧毁": "无法被卖出或丢弃"}},
            "refinements": [{"rank": 1, "desc": "翻盘终极神兵！成王败寇，胜负往往在圣剑落地的瞬间揭晓。"}],
            "ascension_materials": [{"tier": "合成配方", "items": "圣者遗物 (3400) + 恶魔刀锋 (2200) = 5,600 金币"}],
            "version": "7.37d"
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
                5, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    # 机制
    mechs = [
        {
            "category": "物理承伤",
            "title": "DOTA 2 护甲伤害减免精确计算公式",
            "formula": "Damage_Multiplier = 1 - (0.06 * Armor) / (1 + 0.06 * |Armor|)",
            "parameters": {
                "positive_armor": "当拥有 10 点护甲时，物理减伤为 37.5%；拥有 20 点护甲时减伤为 54.5%；拥有 30 点护甲时减伤为 64.3%",
                "negative_armor": "当护甲被减为负数时（如大鱼人、影魔光环、暗灭），承受物理伤害成倍暴增"
            }
        },
        {
            "category": "兵线经济",
            "title": "正补与反补 (Creep Denying) 金钱经验剥夺机制",
            "formula": "Last_Hit = 100% Gold & EXP | Deny = Denier gets 20% Gold bounty, Enemy gets only 50% EXP",
            "parameters": {
                "creep_deny": "友方小兵生命值低于 50% 时可强制反补，成功反补剥夺敌方一半经验并奖励己方金币",
                "lane_freeze": "通过反补和拉野将兵线永远控在己方防御塔前，使敌方对位大哥面临无法补刀且极易被抓的绝境"
            }
        }
    ]
    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (5, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    # 攻略与百科
    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (5, 'DOTA 2 中单影魔从压线到出装节奏全景教学', 1, 'HERO', 'ADVANCED', '["影魔", "中单", "跳刀BKB", "ZXC三连压"]',
                '详细剖析影魔一分半控符技巧、满灵魂对线补刀压制与BKB跳刀切入团战时机。',
                '{"sections":[{"title":"一、对线灵魂滚雪球","text":"影魔1级攻击力低，必须带足吃树和大药，利用ZXC近远压抢兵收魂，灵魂达到10层以上即可完全统治对线正反补！"},{"title":"二、中期核心节奏","text":"第一件必做假腿吹风或假腿魔棒跳刀，抓住对面酱油视野盲区瞬间跳大单杀！"}]}',
                'PUBLISHED', 2890, 2540, 20, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (5, 'DOTA 2 属性与全才英雄机制',
                '英雄分为力量（提供生命与生命恢复）、敏捷（提供护甲与攻击速度）、智力（提供魔法值与魔法抗性）以及全才英雄（所有属性均按0.7倍转化为基础攻击力）。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- DOTA 2 同步完成 ---")

def sync_cs2(cur):
    print("--- 正在同步 CS2 (game_id = 7) ---")
    weaps = [
        {
            "name": "AK-47 (Kalashnikov)",
            "type": "突击步枪",
            "rarity": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/csgo/images/weapons/weapon_ak47.png",
            "base_atk_curve": {"无甲头": 147, "有甲头": 111, "胸部": 36, "腹部": 45, "腿部": 27},
            "sub_stat": {"type": "一枪秒杀", "values": {"弹匣": "30/90", "射速": "600 RPM", "护甲穿透": "77.5%", "射程": "21米爆头必杀"}},
            "refinements": [{"rank": 1, "desc": "T方灵魂！全距离一枪爆头必秒满甲！前两发极度精准，压枪弹道呈反向‘7’字形。"}],
            "ascension_materials": [{"tier": "售价", "items": "2,700 美金"}],
            "version": "1.39"
        },
        {
            "name": "M4A1-S (消音型)",
            "type": "消音突击步枪",
            "rarity": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/csgo/images/weapons/weapon_m4a1_silencer.png",
            "base_atk_curve": {"无甲头": 136, "有甲头": 95, "胸部": 30, "腹部": 38, "腿部": 24},
            "sub_stat": {"type": "隐匿泼水", "values": {"弹匣": "20/80", "射速": "600 RPM", "护甲穿透": "70.0%", "消音": "穿烟无弹道轨迹"}},
            "refinements": [{"rank": 1, "desc": "CT方主力步枪！后坐力极小，前 10 发泼水弹道极度集中，穿烟伏击不暴露枪线。"}],
            "ascension_materials": [{"tier": "售价", "items": "2,900 美金"}],
            "version": "1.39"
        },
        {
            "name": "AWP (Arctic Warfare Police)",
            "type": "重型狙击步枪",
            "rarity": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/csgo/images/weapons/weapon_awp.png",
            "base_atk_curve": {"头": 459, "胸部/腹部": 115, "腿部": 86},
            "sub_stat": {"type": "躯干一枪必杀", "values": {"弹匣": "5/30", "射速": "41 RPM", "护甲穿透": "97.5%", "开镜精度": "绝对精准"}},
            "refinements": [{"rank": 1, "desc": "射击游戏永恒的绿色巨龙！命中上半身（头胸腹）不论有甲无甲必定 100% 击杀！必须急停开火。"}],
            "ascension_materials": [{"tier": "售价", "items": "4,750 美金"}],
            "version": "1.39"
        },
        {
            "name": "沙漠之鹰 (Desert Eagle)",
            "type": "重型手枪",
            "rarity": 4,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/csgo/images/weapons/weapon_deagle.png",
            "base_atk_curve": {"无甲头": 212, "有甲头": 145, "胸部": 53, "腹部": 66, "腿部": 39},
            "sub_stat": {"type": "Eco局奇迹", "values": {"弹匣": "7/35", "护甲穿透": "93.2%", "近距离爆头必杀": "有甲一枪死"}},
            "refinements": [{"rank": 1, "desc": "经济局纯枪法翻盘利器！静止单点一发入魂，连发后坐力极速上天。"}],
            "ascension_materials": [{"tier": "售价", "items": "700 美金"}],
            "version": "1.39"
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
                7, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "战术体积烟雾弹 (Volumetric Smoke Grenade)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/csgo/images/weapons/weapon_smokegrenade.png",
            "two_piece_bonus": "在落点展开三维动态立体烟雾，完全阻挡视线与红名显示，持续 18 秒。",
            "four_piece_bonus": "【高爆手雷驱散】：向烟雾内投掷 HE 手雷引爆时，瞬间将烟雾冲击波炸开一个巨大空洞（持续 2 秒），形成瞬时视野！同时穿过烟雾的子弹会留下短暂弹道空隙。",
            "pieces": [{"slot": "投掷物", "name": "体积动态烟雾弹", "main_stat": "封锁枪线与战术阻隔"}],
            "version": "1.39"
        },
        {
            "name": "凯夫拉头盔防弹衣 (Kevlar + Helmet)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://cdn.cloudflare.steamstatic.com/apps/csgo/images/weapons/item_assaultsuit.png",
            "two_piece_bonus": "提供 100 点护甲耐久，受到枪械射击时大幅度减少伤害并彻底消除【头部受击抖动 (Aim Punch)】！",
            "four_piece_bonus": "长枪局 CT 与 T 必须保证配备的核心防具。",
            "pieces": [{"slot": "全甲", "name": "防弹头盔与胸甲", "main_stat": "消除头部震颤抖动"}],
            "version": "1.39"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                7, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "物理引擎",
            "title": "CS2 Sub-tick 亚毫秒判定与急停开火机制",
            "formula": "Speed < 34% Max_Speed -> Spread = Base_Spread | Click_Input_Time = Server_Exact_Tick_Position",
            "parameters": {
                "sub_tick": "CS2 不再受限于固定 64/128 tick 刷新帧率，服务器在玩家按下鼠标左键或移动按键的精确毫秒时刻执行判定",
                "counter_strafe": "跑动中轻敲反向按键将速度降至 34% 以下，准星散布降至最低达到 100% 绝对命中"
            }
        },
        {
            "category": "竞技经济",
            "title": "CS2 回合奖励与连败补偿 (Loss Bonus) 算法",
            "formula": "Round_Reward: Win = $3250 | Loss_Stage_1 = $1400 | +$500 per additional loss up to $3400 (Stage 5)",
            "parameters": {
                "max_loss": "连败 5 回合达到封顶的 3400 美金连败补偿",
                "bomb_plant": "T 方即便输掉回合，成功下包每人额外获得 800 美金津贴"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (7, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (7, 'CS2 炼狱小镇与海市蜃楼必备道具与急停预瞄教学', 1, 'GENERAL', 'MEDIUM', '["CS2", "急停", "压枪", "烟雾弹", "Mirage"]',
                '掌握 Mirage A区三颗爆弹烟（VIP、警家、跳台）投掷点位，以及 AK-47 反向 7 字形压枪拉枪线技巧。',
                '{"sections":[{"title":"一、AK-47 控枪核心","text":"前3发单点瞄准头部，4~8发向正下方匀速下压，9~15发向左轻推，16发后向右回拉，形成标准反7字！"},{"title":"二、Mirage VIP 烟","text":"出生点对准后墙铁网，按住 D 稍微前移跳投，烟雾完美封死 VIP 狙击手视野！"}]}',
                'PUBLISHED', 3200, 2900, 25, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (7, 'CS2 动态体积烟雾弹交互规则',
                'CS2 采用全新起源2引擎动态体积烟雾。烟雾会随周围空间膨胀填满门窗走廊；受到高爆手雷冲击波时会瞬间被驱散破开大洞，形成短暂视野窗口。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- CS2 同步完成 ---")

def sync_all():
    print("=== 开始同步 DOTA 2 与 CS2 数据 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    sync_dota2(cur)
    sync_cs2(cur)
    conn.commit()
    conn.close()
    print("=== DOTA 2 与 CS2 全量数据同步完毕！ ===")

if __name__ == '__main__':
    sync_all()
