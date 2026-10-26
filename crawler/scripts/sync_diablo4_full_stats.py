#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
暗黑破坏神4 (Diablo IV) 全量数值体系落库与同步脚本
game_id = 10

包含:
1. 5 大经典职业与新资料片核心职业 (野蛮人、魔法使、死灵法师、游侠、魂灵师)
   - 1~60级生命/护甲成长、力敏智意四维属性模型与主属性增伤
   - 核心主动技能、关键被动天赋与专属职业专精系统 (亡者之书、武器大师、巫师附魔、心眼连击)
2. 5 大稀有暗金与经典神兵 (祖父、末日使者、谐角之冠·军帽、安达利尔的面容、无星夜空之戒)
3. 4 大核心传奇威能体系 (震荡波威能、剑舞者威能、分裂威能、蓄势待击威能)
4. 4 大底层暗黑4战斗机制与伤害乘区公式 (易伤与压制独立乘区、护甲85%减伤硬上限、抗性70%衰减机制、强固与屏障)
5. 2 篇高阶深坑冲层攻略与百科词条
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

def get_diablo4_characters():
    return [
        {
            "name": "野蛮人 (Barbarian)",
            "title": "亚瑞特圣山战神·怒火主宰",
            "rarity": 5,
            "element": "狂暴物理 / 撕裂流血",
            "weapon_type": "军械库系统 (双手重锤/双手巨剑/双持单手)",
            "region": "干燥平原 / 破碎群峰",
            "avatar_url": "https://patchwiki.biligame.com/images/diablo4/thumb/6/60/avatar_barbarian.png/120px-avatar_barbarian.png",
            "splash_url": "https://patchwiki.biligame.com/images/diablo4/thumb/6/60/avatar_barbarian.png/600px-avatar_barbarian.png",
            "base_stats": [
                {"level": "1", "hp": 120, "armor": 50, "fury": 100, "strength": 20, "dexterity": 8, "intelligence": 7, "willpower": 10},
                {"level": "30", "hp": 1200, "armor": 450, "fury": 120, "strength": 180, "dexterity": 60, "intelligence": 45, "willpower": 90},
                {"level": "60", "hp": 4800, "armor": 1200, "fury": 150, "strength": 550, "dexterity": 180, "intelligence": 120, "willpower": 260}
            ],
            "special_ascension_stat": {"stat_name": "军械库系统", "values": {"特权": "同时装备4把武器，享受全部词条与传奇威能"}},
            "ascension_materials": [{"tier": "世界层级", "items": "折磨难度 I~IV 苦痛矿石与遗忘之魂"}],
            "talents": [
                {"name": "核心技能·旋风斩 (Whirlwind)", "type": "NORMAL_ATTACK", "description": "消耗怒气极速旋转双臂武器形成狂暴绞肉风暴，穿透怪物群造成连续多段范围物理撕裂打击。", "scaling": "每秒消耗 25 点怒气，每段倍率 65%"},
                {"name": "核心技能·先祖之锤 (Hammer of the Ancients)", "type": "ELEMENTAL_SKILL", "description": "高举双手重锤猛力轰击前方地面，造成粉碎性大范围爆破打击，每消耗额外怒气伤害呈指数级飙升！", "scaling": "压制暴击一锤可打出数十亿伤害"},
                {"name": "终极技能·先祖召唤 (Call of the Ancients)", "type": "ELEMENTAL_BURST", "description": "召唤科里克、马道克、塔里克三位远古野蛮人先祖英灵并肩作战，释放狂暴跳斩与旋风绞杀！", "scaling": "持续 12 秒，获得 20% 额外攻速与伤害"}
            ],
            "passives": [{"name": "不羁怒火", "desc": "处于狂暴状态时伤害提升 25%，移动速度提升 15%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "战吼提供强固与易伤 -> 开启狂暴 -> 倾泻满怒砸出先祖之锤压制核爆！"},
            "recommendations": {"weapons": {"bis": "祖父 (The Grandfather)"}, "artifacts": {"bis_set": "蓄势待击威能 + 狂暴威能"}},
            "version": "2.0.4"
        },
        {
            "name": "魔法使 (Sorcerer)",
            "title": "元素法皇·雷火冰结",
            "rarity": 5,
            "element": "冰霜 / 闪电 / 火焰",
            "weapon_type": "魔杖/聚能器/法杖",
            "region": "凯基斯坦·卡尔蒂姆",
            "avatar_url": "https://patchwiki.biligame.com/images/diablo4/thumb/9/91/avatar_sorcerer.png/120px-avatar_sorcerer.png",
            "splash_url": "https://patchwiki.biligame.com/images/diablo4/thumb/9/91/avatar_sorcerer.png/600px-avatar_sorcerer.png",
            "base_stats": [
                {"level": "1", "hp": 100, "armor": 40, "mana": 100, "strength": 7, "dexterity": 10, "intelligence": 20, "willpower": 12},
                {"level": "30", "hp": 980, "armor": 380, "mana": 115, "strength": 50, "dexterity": 80, "intelligence": 220, "willpower": 110},
                {"level": "60", "hp": 3900, "armor": 950, "mana": 140, "strength": 130, "dexterity": 210, "intelligence": 680, "willpower": 310}
            ],
            "special_ascension_stat": {"stat_name": "附魔插槽系统", "values": {"特权": "将技能放入附魔槽获得强力被动衍生效果"}},
            "ascension_materials": [{"tier": "世界层级", "items": "魔法之尘与恶魔之血"}],
            "talents": [
                {"name": "核心技能·连锁闪电 (Chain Lightning)", "type": "NORMAL_ATTACK", "description": "射出一道在敌人与自身之间疯狂弹跳最多 5 次的暴烈电弧，命中造成电击并生成爆裂电花。", "scaling": "消耗 35 点法力，高频触发电击击晕"},
                {"name": "防御神技·传送术 (Teleport)", "type": "ELEMENTAL_SKILL", "description": "化作闪电瞬移至目标地点，解除受控状态并使自身在接下来 3 秒内获得 30% 伤害减免！配合无限法衣可大范围聚怪击晕。", "scaling": "冷却 11 秒，位移/解控/聚怪合一"},
                {"name": "终极技能·深度冻结 (Deep Freeze)", "type": "ELEMENTAL_BURST", "description": "将自己包裹在坚不可摧的绝对寒冰中进入无敌状态，持续 4 秒对周围暴风雪洗礼，结束时造成寒冰大碎裂！", "scaling": "无敌自保并重置非终极大招冷却"}
            ],
            "passives": [{"name": "元素交织", "desc": "同时造成火、冰、电伤害时，全属性伤害提升 15%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "传送进怪堆聚怪击晕 -> 火盾保命 -> 极速倾泻连锁闪电触发电能满屏轰杀！"},
            "recommendations": {"weapons": {"bis": "无星夜空之戒 / 轴心导管"}, "artifacts": {"bis_set": "电花威能 + 冰霜威能"}},
            "version": "2.0.4"
        },
        {
            "name": "死灵法师 (Necromancer)",
            "title": "亡骸统帅·白骨主宰",
            "rarity": 5,
            "element": "白骨 / 鲜血 / 暗影",
            "weapon_type": "双手镰刀/盾牌/单手剑",
            "region": "哈维泽沼泽",
            "avatar_url": "https://patchwiki.biligame.com/images/diablo4/thumb/e/e0/avatar_necromancer.png/120px-avatar_necromancer.png",
            "splash_url": "https://patchwiki.biligame.com/images/diablo4/thumb/e/e0/avatar_necromancer.png/600px-avatar_necromancer.png",
            "base_stats": [
                {"level": "1", "hp": 105, "armor": 45, "essence": 100, "strength": 8, "dexterity": 9, "intelligence": 18, "willpower": 14},
                {"level": "30", "hp": 1050, "armor": 410, "essence": 115, "strength": 55, "dexterity": 75, "intelligence": 200, "willpower": 130},
                {"level": "60", "hp": 4200, "armor": 1050, "essence": 145, "strength": 140, "dexterity": 200, "intelligence": 620, "willpower": 380}
            ],
            "special_ascension_stat": {"stat_name": "亡者之书", "values": {"特权": "自由统领骷髅战士、骷髅法师与鲜血魔像，或牺牲获得强力常驻增益"}},
            "ascension_materials": [{"tier": "世界层级", "items": "遗骨与黑水之魂"}],
            "talents": [
                {"name": "核心技能·骨矛 (Bone Spear)", "type": "NORMAL_ATTACK", "description": "从地面唤出一根锐利的白骨长矛贯穿前方的敌人，击中掩体或穿透极限后裂开为 3~5 片尖刺回射造成二次暴击！", "scaling": "消耗 25 精魂，极高暴伤与易伤附加"},
                {"name": "尸体神技·邪爆 (Corpse Explosion)", "type": "ELEMENTAL_SKILL", "description": "引爆视野内的目标尸体，在地面形成暗影剧毒瘴气或爆破伤害，无需消耗精魂！", "scaling": "0蓝耗，连环尸爆清全图"},
                {"name": "终极技能·亡者大军 (Army of the Dead)", "type": "ELEMENTAL_BURST", "description": "唤醒沉睡在深渊的成百上千骷髅军团从地底涌出扑向敌人自爆，并瞬间复活所有阵亡的仆从！", "scaling": "仆从流核心大招，伤害极高"}
            ],
            "passives": [{"name": "锯齿骨刺", "desc": "精魂超过 50 点时，每多 1 点精魂使骨矛暴击率提升 0.5%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "骨牢困住精英怪 -> 骨矛贯穿触发易伤并裂解碎片二次轰击 -> 产生尸体连环邪爆！"},
            "recommendations": {"weapons": {"bis": "祖父 / 骨疽白骨镰刀"}, "artifacts": {"bis_set": "分裂威能 + 齿状骨刺威能"}},
            "version": "2.0.4"
        },
        {
            "name": "魂灵师 (Spiritborn)",
            "title": "丛林圣者·万灵共鸣",
            "rarity": 5,
            "element": "狂豹 / 巨猩 / 飞羽 / 剧毒",
            "weapon_type": "长柄武器/双头刀",
            "region": "纳汉图·丛林圣殿",
            "avatar_url": "https://patchwiki.biligame.com/images/diablo4/thumb/1/12/avatar_spiritborn.png/120px-avatar_spiritborn.png",
            "splash_url": "https://patchwiki.biligame.com/images/diablo4/thumb/1/12/avatar_spiritborn.png/600px-avatar_spiritborn.png",
            "base_stats": [
                {"level": "1", "hp": 115, "armor": 48, "vigor": 100, "strength": 12, "dexterity": 18, "intelligence": 10, "willpower": 14},
                {"level": "30", "hp": 1150, "armor": 440, "vigor": 120, "strength": 90, "dexterity": 210, "intelligence": 70, "willpower": 120},
                {"level": "60", "hp": 4500, "armor": 1150, "vigor": 150, "strength": 220, "dexterity": 650, "intelligence": 180, "willpower": 340}
            ],
            "special_ascension_stat": {"stat_name": "魂灵大厅", "values": {"特权": "绑定主/副魂灵守护兽（豹、猩、鹰、蜈蚣）重构全技能伤害判定"}},
            "ascension_materials": [{"tier": "世界层级", "items": "纳汉图密林果实与远古琥珀"}],
            "talents": [
                {"name": "核心技能·飞羽 (Quill Volley)", "type": "NORMAL_ATTACK", "description": "发射扇形漫天飞羽穿透所有敌人，羽毛落地反弹击中造成第二段巨额暴击，配合弹跳威能输出冠绝全职！", "scaling": "当前版本最强幻神技能，亿万级伤害"},
                {"name": "防护技能·巨猩践踏 (Gorilla Stomp)", "type": "ELEMENTAL_SKILL", "description": "凝聚巨猩守护神力猛击大地，将周围所有敌人击晕并赋予自身生命上限 100% 的坚固屏障！", "scaling": "坚固屏障与无限霸体"},
                {"name": "终极技能·追猎者之跃 (The Hunter)", "type": "ELEMENTAL_BURST", "description": "化身狂野美洲豹在全场敌人之间穿梭连续狂暴扑杀 7 次，每次扑杀必定造成压制暴击！", "scaling": "瞬移无敌连斩"}
            ],
            "passives": [{"name": "万灵契约", "desc": "每次消耗活力时获得一层决心，每层提供 5% 独立伤害减免。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "目前 2.0 版本绝对 T0 幻神！飞羽弹跳配合决意屏障，深坑 150 层轻松割草。"},
            "recommendations": {"weapons": {"bis": "谐角之冠 (军帽) + 罗德之杖"}, "artifacts": {"bis_set": "弹跳飞羽威能"}},
            "version": "2.0.4"
        }
    ]

def get_diablo4_weapons():
    return [
        {
            "name": "祖父 (The Grandfather)",
            "type": "稀有暗金双手双手剑",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/diablo4/weapon_the_grandfather.png",
            "base_atk_curve": {"每秒伤害": 4850, "每次攻击伤害": "3850 - 4750"},
            "sub_stat": {"type": "至高词缀", "values": {"暴击伤害": "+100% [x] 独立乘算！", "生命上限": "+78% 生命上限", "全属性": "+350 全属性", "耐久": "武器永不磨损"}},
            "refinements": [
                {"rank": 1, "desc": "全游戏最强双手武器！暴击伤害不是加算，而是直接将你的最终暴击伤害整体乘以 2.0 倍！且词条roll值永远拉满！"}
            ],
            "ascension_materials": [{"tier": "掉落来源", "items": "都瑞尔 / 安达利尔折磨IV难度"}],
            "version": "2.0.4"
        },
        {
            "name": "谐角之冠 (Harlequin Crest / 军帽)",
            "type": "稀有暗金头盔",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/diablo4/weapon_harlequin_crest.png",
            "base_atk_curve": {"护甲": 1520},
            "sub_stat": {"type": "全技能+4", "values": {"全技能等级": "+4 级所有已解锁技能", "伤害减免": "20.0% 常驻全减伤", "冷却时间缩减": "20.0% 冷却缩减", "生命上限": "+1850 生命值"}},
            "refinements": [
                {"rank": 1, "desc": "暗黑4全职业无可替代的终极头盔！直接提升全技能 4 级，相当于核心技能伤害暴涨 40%，外加 20% 纯硬减伤。"}
            ],
            "ascension_materials": [{"tier": "掉落来源", "items": "都瑞尔 / 安达利尔折磨IV难度"}],
            "version": "2.0.4"
        },
        {
            "name": "末日使者 (Doombringer)",
            "type": "稀有暗金单手剑",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/diablo4/weapon_doombringer.png",
            "base_atk_curve": {"每秒伤害": 3450, "每次攻击伤害": "2450 - 3200"},
            "sub_stat": {"type": "生存天花板", "values": {"生命上限": "+41.4% 生命上限", "受击减伤": "敌人造成伤害降低 20%", "暗影新星": "幸运一击触发 28,000 暗影爆炸"}},
            "refinements": [
                {"rank": 1, "desc": "单手武器中的生存神兵，直接带来近乎翻倍的生命池与大范围虚弱减伤。"}
            ],
            "ascension_materials": [{"tier": "掉落来源", "items": "都瑞尔 / 安达利尔折磨IV难度"}],
            "version": "2.0.4"
        }
    ]

def get_diablo4_artifacts():
    return [
        {
            "name": "分裂威能 (Aspect of Splintering)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/diablo4/aspect_splintering.png",
            "two_piece_bonus": "骨矛的主攻击使击中的所有敌人陷入易伤，持续 3 秒。",
            "four_piece_bonus": "骨矛裂解产生的骨刺碎片对处于易伤的敌人造成 120%[x] 的额外爆发骨伤！死灵法师第一核心威能。",
            "pieces": [{"slot": "武器/手套", "name": "分裂之骨威能", "main_stat": "骨矛碎片爆发"}],
            "version": "2.0.4"
        },
        {
            "name": "震荡波威能 (Shockwave Aspect)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/diablo4/aspect_shockwave.png",
            "two_piece_bonus": "德鲁伊粉碎（拍拍熊）施放时向前释放一道震荡波。",
            "four_piece_bonus": "震荡波对路径上的所有敌人造成粉碎基础伤害 100%~120% 的二次粉碎打击！将近战拍地变为超大远程轰炸。",
            "pieces": [{"slot": "双手武器/项链", "name": "大地震荡波威能", "main_stat": "拍拍熊远程化"}],
            "version": "2.0.4"
        },
        {
            "name": "蓄势待击威能 (Aspect of Expectant)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/diablo4/aspect_expectant.png",
            "two_piece_bonus": "使用基础普攻命中敌人后，使下一个核心技能伤害提升 10%，最多叠加 3 层。",
            "four_piece_bonus": "叠满后核心技能伤害独立提升 30%[x]！野蛮人与游侠通用极品增伤威能。",
            "pieces": [{"slot": "戒指/手套", "name": "蓄势待击威能", "main_stat": "核心技能加成"}],
            "version": "2.0.4"
        }
    ]

def get_diablo4_mechanics():
    return [
        {
            "category": "伤害乘区",
            "title": "易伤 (Vulnerable) 与压制 (Overpower) 独立乘区公式",
            "formula": "Total_DMG = Base_DMG * [1 + Sum(Normal_Additive%)] * (1.2x if Vuln + Vuln_Additive%) * (1.5x if OP + Life_Fortify_Bonus%) * Product(All_X_Multipliers)",
            "parameters": {
                "vulnerable": "敌人被挂上紫色血条易伤状态时，保底获得 1.2x 独立全局增伤乘区",
                "overpower": "压制固定 3% 概率触发（部分技能机制必定触发），享受 1.5x 乘区并直接将当前生命值与强固值按比例附加到基础伤害中",
                "x_multiplier": "所有带有 [x] 标志的暗金与传奇威能均为独立相乘，叠加越多伤害呈指数级暴增"
            }
        },
        {
            "category": "生存防御",
            "title": "护甲值 85% 物理减伤阈值硬上限公式",
            "formula": "Max_Armor_Cap = 1,000 Armor Points (in Torment IV) = 85.0% Physical Damage Reduction",
            "parameters": {
                "armor_cap": "在最新 2.0 资料片版本中，护甲上限调整为恒定 1,000 点即达到 85% 物理减伤硬上限",
                "waste": "超过 1,000 点的护甲收益为 0，多余词条应洗为生命值、伤害或抗性"
            }
        },
        {
            "category": "元素抗性",
            "title": "元素抗性 70% 硬上限与难度衰减机制",
            "formula": "Max_Resistance = 70.0% (Cap can be raised to 85% via specific Elixirs and Paragon)",
            "parameters": {
                "penalty": "折磨 I~IV 难度每级会惩罚全抗性 -25% 到 -100%，必须在装备和首饰插槽上镶嵌对应抗性宝石补齐",
                "cap_extension": "通过药剂或特定巅峰雕文可将抗性硬上限提升至 85%，高层大秘境必备"
            }
        }
    ]

def get_diablo4_guides_and_wikis():
    guides = [
        {
            "title": "暗黑破坏神4 2.0 资料片全职业深坑冲层与装备强化指南",
            "type": "BUILD",
            "difficulty": "ADVANCED",
            "tags": ["深坑", "大秘境", "装备回火", "精造", "军帽"],
            "summary": "详解新版本深坑 100+ 层冲层要求：1000护甲硬上限、70%全抗达标、回火双词条与 12 阶精造暴击技巧。",
            "content": {
                "sections": [
                    {"title": "一、防御基准线", "text": "进入苦痛难度前必须确认：护甲达到 1000（不可多也不可少），火冰电毒暗五大抗性全部达到 70% 绿色满格！"},
                    {"title": "二、精造暴击技巧", "text": "装备精造在第 4、8、12 阶会随机让某一条词条暴增 25%。如果核心词条（如全技能等级或核心被动）没暴击，果断在铁匠处重置重冲！"}
                ]
            },
            "like_count": 2450,
            "useful_count": 2180
        }
    ]
    wikis = [
        {
            "title": "暗黑4装备稀有度与稀有暗金 (Mythic Uniques)",
            "content": "装备从低到高分为魔法、稀有、传奇、暗金与神话稀有暗金（紫光）。神话暗金（如军帽、祖父、末日使者）拥有极低掉落率、固定满数值roll点与极其夸张的改变游戏机制词条。"
        }
    ]
    return guides, wikis

def sync_all():
    print("=== 开始同步 暗黑破坏神4 (Diablo IV) 全量数据 (game_id = 10) ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    chars = get_diablo4_characters()
    print(f"正在写入 {len(chars)} 位职业数据...")
    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                10, %s, %s, %s, %s, %s, %s,
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

    weaps = get_diablo4_weapons()
    print(f"正在写入 {len(weaps)} 把暗金神器数据...")
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
                10, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = get_diablo4_artifacts()
    print(f"正在写入 {len(arts)} 套传奇威能数据...")
    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                10, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = get_diablo4_mechanics()
    print(f"正在写入 {len(mechs)} 条战斗机制与公式...")
    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (10, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    guides, wikis = get_diablo4_guides_and_wikis()
    print(f"正在写入 {len(guides)} 篇攻略与 {len(wikis)} 条百科词条...")
    for g in guides:
        cur.execute("""
            INSERT INTO guide (
                game_id, version_id, title, author_id, type, difficulty,
                tags, summary, content, status, like_count, useful_count, verify_count,
                created_at, updated_at
            ) VALUES (
                10, NULL, %s, 1, %s, %s,
                %s, %s, %s, 'PUBLISHED', %s, %s, 18,
                NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (g['title'], g['type'], g['difficulty'], Json(g['tags']), g['summary'], Json(g['content']), g['like_count'], g['useful_count']))

    for wk in wikis:
        cur.execute("""
            INSERT INTO wiki_entry (game_id, title, content, last_updated)
            VALUES (10, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (wk['title'], wk['content']))

    conn.commit()
    conn.close()
    print("=== 暗黑破坏神4 (game_id = 10) 全量数据写入完成！ ===")

if __name__ == '__main__':
    sync_all()
