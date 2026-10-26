#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四大高热度经典神作数据全面入库同步脚本:
1. 空洞骑士 (Hollow Knight) - game_id = 14
2. 以撒的结合：忏悔 (The Binding of Isaac: Repentance) - game_id = 15
3. 荒野大镖客2 (Red Dead Redemption 2) - game_id = 13
4. 炉石传说 (Hearthstone) - game_id = 18

包含:
- 核心角色/形态/职业/流派 (game_character)
- 经典神兵/骨钉/枪械/武器道具 (game_weapon)
- 护符/饰品/套装/变身体系 (game_artifact_set)
- 底层机制算法与伤害公式 (game_mechanic_rule)
- 权威攻略 (guide) 与百科词条 (wiki_entry)
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
# 1. 空洞骑士 (Hollow Knight, ID = 14)
# ==========================================
def sync_hollow_knight(cur):
    print("--- 正在同步 空洞骑士 (Hollow Knight, game_id = 14) ---")
    gid = 14
    chars = [
        {
            "name": "小骑士·纯粹剑圣流 (The Knight - Pure Nail)",
            "title": "圣巢救赎者·虚空之子",
            "rarity": 5,
            "element": "虚空 / 纯物理",
            "weapon_type": "骨钉 (Nail)",
            "region": "圣巢·德特茅斯",
            "avatar_url": "https://patchwiki.biligame.com/images/hk/thumb/4/4b/avatar_knight.png/120px-avatar_knight.png",
            "splash_url": "https://patchwiki.biligame.com/images/hk/thumb/4/4b/avatar_knight.png/600px-avatar_knight.png",
            "base_stats": [
                {"level": "初始", "hp": 5, "soul": 99, "nail_dmg": 5, "speed": 100},
                {"level": "中期", "hp": 7, "soul": 132, "nail_dmg": 13, "speed": 100},
                {"level": "毕业", "hp": 9, "soul": 198, "nail_dmg": 21, "speed": 100}
            ],
            "special_ascension_stat": {"stat_name": "剑技与骨钉强化", "values": {"骨钉技艺": "强力斩、旋风斩、冲刺斩三大剑技"}},
            "ascension_materials": [{"tier": "骨钉匠", "items": "苍白矿石 × 6 + 6000 吉欧"}],
            "talents": [
                {"name": "强力斩 (Great Slash)", "type": "NORMAL_ATTACK", "description": "按住攻击键聚气蓄力，松开向前挥出一记超大范围的圆弧重斩，造成骨钉伤害 2.5 倍的纯物理爆发伤害！", "scaling": "纯粹骨钉下造成 52.5 点爆发伤害"},
                {"name": "旋风斩 (Cyclone Slash)", "type": "ELEMENTAL_SKILL", "description": "蓄力后松开原地回旋暴风挥砍，连按攻击键可延长旋转时间，最多造成 3~7 次连续切割伤害。", "scaling": "打满最高造成 147 点巨额切割伤害"},
                {"name": "冲刺斩 (Dash Slash)", "type": "ELEMENTAL_BURST", "description": "在暗影冲刺或普通冲刺中释放蓄力斩，向前滑行极远距离横扫，贯穿直线上的所有敌人。", "scaling": "造成 2.5 倍骨钉伤害，安全距离清怪神器"}
            ],
            "passives": [{"name": "虚空之心 (Void Heart)", "desc": "将体内的虚空合而为一，虚空生物不再敌对，解开深渊最深沉的真结局。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "骨钉下劈 (Pogo) 重置冲刺与二段跳 -> 蓄力强力斩拉扯身位 -> 配合快速劈砍站桩极速平砍秒杀首领！"},
            "recommendations": {"weapons": {"bis": "纯粹骨钉 (Pure Nail)"}, "artifacts": {"bis_set": "坚固力量 + 快速劈砍 + 骄傲印记"}},
            "version": "1.5.78"
        },
        {
            "name": "小骑士·萨满法皇流 (The Knight - Shaman Caster)",
            "title": "深渊幽魂·毁灭术士",
            "rarity": 5,
            "element": "灵魂 / 暗影法术",
            "weapon_type": "暗影法术 / 蜗牛萨满之力",
            "region": "遗忘十字路·祖峰",
            "avatar_url": "https://patchwiki.biligame.com/images/hk/thumb/5/52/avatar_knight_spell.png/120px-avatar_knight_spell.png",
            "splash_url": "https://patchwiki.biligame.com/images/hk/thumb/5/52/avatar_knight_spell.png/600px-avatar_knight_spell.png",
            "base_stats": [
                {"level": "毕业法皇", "hp": 9, "soul": 198, "spell_dmg_bonus": "+50%", "speed": 100}
            ],
            "special_ascension_stat": {"stat_name": "法术伤害加成", "values": {"萨满之石加成": "全法术伤害提升 33%~50%，范围大幅扩大"}},
            "ascension_materials": [{"tier": "暗影法术升级", "items": "灵魂圣所、遗废盆地、皇家水道黑涌升级"}],
            "talents": [
                {"name": "黑暗降临 (Descending Dark / 下砸)", "type": "ELEMENTAL_SKILL", "description": "消耗 33 灵魂腾空向下猛砸地面，激起毁灭性的暗影震波，造成 60 点暗影伤害，并赋予小骑士长达 0.4 秒的绝对无敌帧判定！", "scaling": "神级保命与输出核心，无敌帧躲避一切 Boss 全屏杀"},
                {"name": "深渊尖啸 (Abyss Shriek / 尖叫)", "type": "ELEMENTAL_BURST", "description": "向正上方撕心裂肺发出 4 段惨烈深渊灵魂尖啸，在萨满之石加成下造成高达 120 点天文数字级对空爆发！", "scaling": "空中 Boss 融化器，两发尖啸秒杀梦魇格林"},
                {"name": "暗影之魂 (Shade Soul / 黑波)", "type": "NORMAL_ATTACK", "description": "向前释放一道穿透墙体与物体的巨大幽影之魂，击退路径上的目标并最多造成 2~3 段 40 点贯穿伤害。", "scaling": "穿透击退多段判定，单发最高 80 点伤害"}
            ],
            "passives": [{"name": "法术扭曲", "desc": "法术消耗灵魂由 33 点降低至 24 点。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "平A快速回魂 -> 观察 Boss 出招跳起释放黑暗降临无敌帧硬顶伤害 -> 钻入 Boss 腹底按住向上键释放深渊尖啸瞬间核爆！"},
            "recommendations": {"weapons": {"bis": "纯粹骨钉"}, "artifacts": {"bis_set": "萨满之石 + 法术扭曲者 + 噬魂者"}},
            "version": "1.5.78"
        },
        {
            "name": "大黄蜂 (Hornet)",
            "title": "圣巢守护者·丝之歌主角",
            "rarity": 5,
            "element": "丝线飞针",
            "weapon_type": "缝针与丝线 (Needle & Silk)",
            "region": "苍绿之径 / 深邃巢穴",
            "avatar_url": "https://patchwiki.biligame.com/images/hk/thumb/8/86/avatar_hornet.png/120px-avatar_hornet.png",
            "splash_url": "https://patchwiki.biligame.com/images/hk/thumb/8/86/avatar_hornet.png/600px-avatar_hornet.png",
            "base_stats": [{"level": "巅峰", "hp": 8, "silk": 100, "speed": 135}],
            "special_ascension_stat": {"stat_name": "丝线机动", "values": {"特权": "空中丝线钩爪极速位移与飞针弹射"}},
            "ascension_materials": [{"tier": "纺织之女", "items": "野兽赫拉血统与编织者之茧"}],
            "talents": [
                {"name": "缝针飞掷 (Gossamer Storm)", "type": "NORMAL_ATTACK", "description": "向前全力掷出骨针缝线贯穿前方，并在空中拉扯丝线将自身瞬间拉向目标或墙面。", "scaling": "长距离穿透与钩爪位移"},
                {"name": "丝线风暴 (Silk Burst)", "type": "ELEMENTAL_BURST", "description": "释放周身编织的数十道锋锐蚕丝形成致命的绞杀力场，将周围所有触碰的敌怪撕裂切碎！", "scaling": "360度全方位范围近身防护防御"}
            ],
            "passives": [{"name": "吉陀的敏捷", "desc": "移动与奔跑速度比小骑士快 35%，冲刺距离更长。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "极高敏捷的机动刺客，在空中翻滚拉扯，通过丝线针击控场后极速近身收割。"},
            "recommendations": {"weapons": {"bis": "纯净缝针"}},
            "version": "1.5.78"
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
                14, %s, %s, %s, %s, %s, %s,
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
            "name": "纯粹骨钉 (Pure Nail)",
            "type": "骨钉 (近战刀刃)",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hk/weapon_pure_nail.png",
            "base_atk_curve": [
                {"level": "旧骨钉 (旧)", "atk": 5},
                {"level": "锋利骨钉 (+1)", "atk": 9},
                {"level": "引导骨钉 (+2)", "atk": 13},
                {"level": "螺旋骨钉 (+3)", "atk": 17},
                {"level": "纯粹骨钉 (+4终极)", "atk": 21}
            ],
            "sub_stat": {"type": "物理伤害", "values": {"基础单发": "21 点伤害", "配合坚固力量": "31.5 点单发伤害"}},
            "refinements": [
                {"rank": 1, "desc": "圣巢骨钉匠的毕生杰作！刀刃无瑕纯净，攻击范围大幅扩大，每一次挥砍均伴随金属铮鸣。"}
            ],
            "ascension_materials": [{"tier": "升级素材", "items": "收集全圣巢 6 块苍白矿石交付泪水之城骨钉匠"}],
            "version": "1.5.78"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                14, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "剑圣平砍流护符组 (Pure Strength Charm Set)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hk/charm_strength.png",
            "two_piece_bonus": "【坚固力量 + 快速劈砍】：骨钉平砍伤害提升 50%，攻击后摇缩减 40%，实现极速站桩刀光！",
            "four_piece_bonus": "【骄傲印记 + 稳固坚石】：攻击距离提升 25%，挥刀完全消除自身受击后退击退，压制 Boss 动弹不得。",
            "pieces": [
                {"slot": "槽位1 (3点)", "name": "坚固力量 (Unbreakable Strength)", "main_stat": "骨钉伤害 +50%"},
                {"slot": "槽位2 (3点)", "name": "快速劈砍 (Quick Slash)", "main_stat": "挥砍速度 +40%"},
                {"slot": "槽位3 (3点)", "name": "骄傲印记 (Mark of Pride)", "main_stat": "攻击距离 +25%"},
                {"slot": "槽位4 (1点)", "name": "稳固坚石 (Steady Body)", "main_stat": "攻击反冲击退免疫"}
            ],
            "version": "1.5.78"
        },
        {
            "name": "萨满法术核爆护符组 (Shaman Caster Charm Set)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hk/charm_shaman.png",
            "two_piece_bonus": "【萨满之石 + 法术扭曲者】：法术伤害提升 33%~50% 且范围扩大，法术灵魂消耗从 33 点直降至 24 点！",
            "four_piece_bonus": "【噬魂者 + 幼虫之歌】：平A每次获取灵魂量翻倍，受到伤害自动转化为法术灵魂，无限下砸无敌帧！",
            "pieces": [
                {"slot": "核心槽 (3点)", "name": "萨满之石 (Shaman Stone)", "main_stat": "法伤 +50% 与范围扩大"},
                {"slot": "增幅槽 (2点)", "name": "法术扭曲者 (Spell Twister)", "main_stat": "法术耗魂 -27%"},
                {"slot": "回魂槽 (4点)", "name": "噬魂者 (Soul Eater)", "main_stat": "平A吸魂 +19点"}
            ],
            "version": "1.5.78"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                14, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "动作物理",
            "title": "骨钉下劈 (Nail Pogo) 滞空重置与物理反弹判定",
            "formula": "Airborne + Downward_Slash_Hit = Vertical_Rebound_Velocity + Reset(Dash & Monarch_Wings)",
            "parameters": {
                "pogo": "在空中按住向下键挥动骨钉砍中敌人、尖刺、发光紫蘑菇时，产生强劲的反弹向上动力",
                "reset": "下劈成功瞬间立刻刷新冲刺与二段跳（蛾翼披风与帝王之翼），实现无限空中滞空踏刺跳跃（苦痛之路核心技巧）"
            }
        },
        {
            "category": "无敌判定",
            "title": "黑暗降临 (Descending Dark) 0.4秒绝对无敌帧机制",
            "formula": "Desolate_Dive/Descending_Dark = 0.4s Absolute Invulnerability Frame (I-frame)",
            "parameters": {
                "iframe": "下砸落地瞬间获得 0.4 秒无敌，免疫任何 Boss 的碰撞伤害与全屏弹幕",
                "damage": "下砸本体造成 15 点伤害，随后的暗影震波造成 30+15 点伤害，萨满加成后总计 88 点伤害"
            }
        },
        {
            "category": "规则限制",
            "title": "护符过载 (Overcharmed) 双倍受击承伤惩罚机制",
            "formula": "Notch_Used > Max_Notches(11) -> Damage_Taken = Normal_DMG * 200%",
            "parameters": {
                "overcharmed": "当护符槽已满时连续狂按强行装入额外护符，可强行激活，但小骑士承受的所有伤害翻倍（掉1血变掉2血，掉2血变掉4血猝死）",
                "radiant_mode": "在神居光辉级 (Radiant) 战斗中由于一击必死，过载无任何负面影响，是全带攻击护符的白嫖神技"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (14, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (14, '空洞骑士神圣巢穴五门 (P5) 全首领逃课与无上辐光通关指南', 1, 'BUILD', 'ADVANCED', '["空洞骑士", "五门", "无上辐光", "下砸无敌帧", "纯粹骨钉"]',
                '详细拆解寻神者万神殿第5门连战42位首领的核心补血点、护符配置切换以及无上辐光全阶段规避手法。',
                '{"sections":[{"title":"一、五门毕业护符推荐","text":"坚固力量 + 快速劈砍 + 萨满之石 + 幼虫之歌。集平砍极速爆发与深渊尖啸融化首领于一身，中途温泉长椅可换回血套。"},{"title":"二、无上辐光三阶段终局","text":"第一阶段腹底深渊尖啸极速压血；第四阶段浮空平台留心光柱与飞剑，多利用下砸无敌帧躲避垂直光矛；爬天梯阶段斜向冲刺诱骗激光！"}]}',
                'PUBLISHED', 4500, 4120, 30, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (14, '圣巢苍白矿石 (Pale Ore) 全6块获取位置',
                '苍白矿石用于将骨钉从旧骨钉强化至纯粹骨钉。获取途径：1.安息之地先知收集300精华；2.古老盆地电梯井左侧；3.水晶山峰圣巢之冠雕像顶端；4.深邃巢穴击败诺斯克 (Nosk) 巢穴深处；5.王国边缘愚人斗兽场征服者试炼获胜；6.拯救全圣巢31只幼虫后由虫爷爷赠送。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 空洞骑士 同步完成 ---")

# ==========================================
# 2. 以撒的结合：忏悔 (Repentance, ID = 15)
# ==========================================
def sync_isaac(cur):
    print("--- 正在同步 以撒的结合：忏悔 (game_id = 15) ---")
    gid = 15
    chars = [
        {
            "name": "以撒 (Isaac)",
            "title": "命运骰子·原初之子",
            "rarity": 5,
            "element": "六面骰 D6 命运重塑",
            "weapon_type": "原版泪弹",
            "region": "地下室 / 子宫 / 虚空",
            "avatar_url": "https://patchwiki.biligame.com/images/isaac/thumb/avatar_isaac.png/120px-avatar_isaac.png",
            "splash_url": "https://patchwiki.biligame.com/images/isaac/thumb/avatar_isaac.png/600px-avatar_isaac.png",
            "base_stats": [
                {"level": "初始", "hearts": "3红心", "dmg": 3.5, "tears": 2.73, "speed": 1.0, "range": 6.5, "luck": 0.0}
            ],
            "special_ascension_stat": {"stat_name": "六面骰 D6", "values": {"特权": "每6房间充能，重置房间内所有道具底座"}},
            "ascension_materials": [{"tier": "击杀成就", "items": "击败以撒解锁 D6 初始携带"}],
            "talents": [
                {"name": "主动道具·六面骰 (The D6)", "type": "ELEMENTAL_BURST", "description": "掷出命运的六面骰，将当前房间内地面上的所有被动与主动道具随机重置为同道具池的全新道具！", "scaling": "6格充能，化垃圾为神装的逆天改命神器"}
            ],
            "passives": [{"name": "泪弹射击", "desc": "基础伤害乘数 1.0x，泪弹基础初速平稳。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "前期控血进恶魔房/天使房 -> 垃圾道具用 D6 摇成神圣之心/硫磺火/科技X -> 轻松割草！"},
            "recommendations": {"weapons": {"bis": "硫磺火 (Brimstone) + 科技 X"}},
            "version": "Repentance+"
        },
        {
            "name": "游魂 (The Lost)",
            "title": "虚无亡灵·白袍死神",
            "rarity": 5,
            "element": "圣洁幽魂 / 飞行幽灵",
            "weapon_type": "幽灵穿石泪弹",
            "region": "深渊虚空",
            "avatar_url": "https://patchwiki.biligame.com/images/isaac/thumb/avatar_the_lost.png/120px-avatar_the_lost.png",
            "splash_url": "https://patchwiki.biligame.com/images/isaac/thumb/avatar_the_lost.png/600px-avatar_the_lost.png",
            "base_stats": [
                {"level": "无血条", "hearts": "0 (一触即死)", "dmg": 3.5, "tears": 2.73, "speed": 1.0, "flight": "永久飞行", "spectral": "泪弹穿墙"}
            ],
            "special_ascension_stat": {"stat_name": "神圣斗篷", "values": {"特权": "每个房间免费抵挡 1 次受击伤害，恶魔交易全部免费！"}},
            "ascension_materials": [{"tier": "贪婪捐款机", "items": "捐献 879 硬币解锁初始携带神圣斗篷"}],
            "talents": [
                {"name": "主动道具·永恒六面骰 (Eternal D6)", "type": "ELEMENTAL_BURST", "description": "2格充能重置道具，但有 30% 概率使道具彻底消失化为青烟。", "scaling": "超快CD高风险重置"}
            ],
            "passives": [
                {"name": "免费恶魔交易", "desc": "由于没有红心，进入恶魔房可直接 0 代价白拿所有恶魔道具（硫磺火、猫套等）！"},
                {"name": "幽灵之躯", "desc": "常驻飞行能力，泪弹天然穿透障碍物与岩石。"}
            ],
            "constellations": [],
            "special_mechanics": {"core_flow": "极度考验走位操作的上限之神：利用岩石掩体输出 -> 破盾后立刻清屏或换房间重置护盾！"},
            "recommendations": {"weapons": {"bis": "神圣之心 (Godhead) + 妈妈的刀"}},
            "version": "Repentance+"
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
                15, %s, %s, %s, %s, %s, %s,
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
            "name": "硫磺火 (Brimstone)",
            "type": "特殊泪弹质变道具",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/isaac/item_brimstone.png",
            "base_atk_curve": [
                {"level": "基础蓄力", "atk": "单次发射持续造成 13 次高频激光切割，总倍率 13x 角色攻击力"}
            ],
            "sub_stat": {"type": "恶魔房至尊", "values": {"特性": "穿透全屏障碍物与全部敌人，判定范围极大"}},
            "refinements": [
                {"rank": 1, "desc": "蓄力后吐出贯穿全屏的粗大血红恶魔激光束，配合追踪效果直接清空整间怪物！"}
            ],
            "ascension_materials": [{"tier": "获取池", "items": "恶魔房交易 2 红心 / 堕落者首领掉落"}],
            "version": "Repentance+"
        },
        {
            "name": "神圣之心 (Godhead)",
            "type": "神圣光环泪弹道具",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/isaac/item_godhead.png",
            "base_atk_curve": [
                {"level": "神圣之光", "atk": "基础攻击 +0.5，泪弹外圈附加超大蓝色神圣光环，每秒造成 30 次范围光灼"}
            ],
            "sub_stat": {"type": "天使房至尊", "values": {"追踪效果": "自动朝视线内所有敌人急速追踪"}},
            "refinements": [
                {"rank": 1, "desc": "以撒最难解锁的神器！泪弹本身自带极强跟踪与大范围高频神圣光环杀伤。"}
            ],
            "ascension_materials": [{"tier": "解锁方式", "items": "使用游魂 (The Lost) 完成全难度通关标记"}],
            "version": "Repentance+"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                15, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "嗝儿猫变身套装 (Guppy Transformation)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/isaac/guppy_trans.png",
            "two_piece_bonus": "收集任意 3 件嗝儿猫系列道具（猫头、猫爪、猫尾、猫身、死猫、九命猫等）。",
            "four_piece_bonus": "化身为嗝儿猫！获得永久飞行能力，且自身任何泪弹/激光击中敌人时，100% 必定生成一只攻击力等于角色基础伤害 2 倍的强力攻击蓝苍蝇！瞬间铺满上百只苍蝇秒杀 Boss！",
            "pieces": [
                {"slot": "道具1", "name": "嗝儿猫的头 (Guppy's Head)", "main_stat": "1格充能生成2~4只蓝苍蝇"},
                {"slot": "道具2", "name": "嗝儿猫的爪子 (Guppy's Paw)", "main_stat": "消耗1红心兑换3蓝心"},
                {"slot": "道具3", "name": "死猫 (Dead Cat)", "main_stat": "获得 9 条命复活机会"}
            ],
            "version": "Repentance+"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                15, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "房间概率",
            "title": "恶魔房与天使房置换概率判定模型",
            "formula": "Base_Chance = 100% (No Red Heart DMG in current floor) -> Devil/Angel Split: Angel% = (1 - Devil_Taken) * 50%",
            "parameters": {
                "red_heart_damage": "在当前楼层受到红心伤害，恶魔房开启概率直接暴跌 99% 或 50%（魂心/黑心受伤不扣除概率）",
                "angel_guarantee": "跳过第一间恶魔房（不进行任何交易），后续楼层天使房开启置换概率飙升至 100%"
            }
        },
        {
            "category": "伤害公式",
            "title": "以撒底层泪弹伤害与射速非线性计算公式",
            "formula": "Final_Damage = 3.5 * Sqrt(Base_Damage_Up * 1.2 + 1) * Damage_Multiplier (e.g. Magic Mushroom * 1.5x)",
            "parameters": {
                "diminishing_returns": "攻击力平加词条存在平方根收益递减机制，只有乘法倍率（如魔法菇、板球首级、狂暴）才能让伤害突破数百",
                "tear_delay": "射速计算：Tears_Per_Second = 30 / (Tear_Delay + 1)，最高可突破基础软上限达到激光速射"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (15, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (15, '以撒忏悔真结局全路线指南：见证者 (Mother) 与祸兽 (The Beast) 开启方法', 1, 'GENERAL', 'ADVANCED', '["以撒", "忏悔", "见证者", "祸兽", "真结局"]',
                '详细梳理表下水道、金刀碎片拼装、陵墓献祭以及回家 (Home) 拿红钥匙解锁全部里角色与挑战祸兽的完整解密流程。',
                '{"sections":[{"title":"一、见证者 Mother 路线","text":"1. 下水道烧2个钥匙进门；2. 矿洞点亮3个黄色火盆进矿车拿刀柄；3. 陵墓献祭2颗心进异界逃脱暗影怪拿刀刃合成白刀；4. 击败尸宫 Mother！"},{"title":"二、祸兽 The Beast 路线","text":"在深渊击败妈腿拿拍立得 -> 传送出房间进入传送门开白门 -> 回到第一层回到 Home 见妈妈的床 -> 拿起红钥匙在走廊打开暗墙解锁里角色 -> 电视机开启祸兽横版格斗！"}]}',
                'PUBLISHED', 4890, 4520, 35, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (15, '以撒的结合 核心变身形态 (Transformations) 汇总',
                '收集3件特定属性道具可触发强力变身：1. 嗝儿猫 (Guppy)：获得飞行与命中出蓝苍蝇；2. 苍蝇王 (Beelzebub)：苍蝇免疫并变为己方蓝苍蝇；3. 撒旦 (Leviathan)：+2黑心与飞行；4. 炽天使 (Seraphim)：+3魂心与飞行；5. 书虫 (Bookworm)：25%几率双发泪弹；6. 蜘蛛宝宝 (Spider Baby)：受到伤害生成群蛛。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 以撒的结合：忏悔 同步完成 ---")

# ==========================================
# 3. 荒野大镖客2 (RDR2, ID = 13)
# ==========================================
def sync_rdr2(cur):
    print("--- 正在同步 荒野大镖客2 (game_id = 13) ---")
    gid = 13
    chars = [
        {
            "name": "亚瑟·摩根 (Arthur Morgan)",
            "title": "范德林德帮第一神枪手·救赎之魂",
            "rarity": 5,
            "element": "死神之眼 / 极速拔枪",
            "weapon_type": "双持左轮 / 连发步枪 / 霰弹枪",
            "region": "新汉诺威·瓦伦丁",
            "avatar_url": "https://patchwiki.biligame.com/images/rdr2/thumb/avatar_arthur.png/120px-avatar_arthur.png",
            "splash_url": "https://patchwiki.biligame.com/images/rdr2/thumb/avatar_arthur.png/600px-avatar_arthur.png",
            "base_stats": [
                {"level": "8级核心满级", "health_core": "100%", "stamina_core": "100%", "deadeye_core": "100%", "hp_bar": 100, "stamina_bar": 100, "deadeye_bar": 100}
            ],
            "special_ascension_stat": {"stat_name": "死神之眼 (Dead Eye)", "values": {"等级": "5级死眼：手动标记红点、高亮弱点与致命器官"}},
            "ascension_materials": [{"tier": "挑战升级", "items": "完成神射手、武器大师、生存家等 9 大挑战"}],
            "talents": [
                {"name": "死神之眼·弱点透视 (Dead Eye Mastery)", "type": "ELEMENTAL_BURST", "description": "按下右摇杆/按键进入时间极度减速的死神之眼境界，透视敌人全身心肺脑致命器官红点，瞬间标记多达 12 处弱点并闪电拔枪瞬秒！", "scaling": "时间减速 80%，出膛必杀"},
                {"name": "腰射速射 (Hipfire Quickdraw)", "type": "NORMAL_ATTACK", "description": "不瞄准直接连续猛力扣动击锤进行极速腰射，0.8 秒内将左轮手枪内全部 6 发弹药倾泻在正面敌人身上！", "scaling": "近距离连射爆发极高"},
                {"name": "套索捕缚 (Lasso Takedown)", "type": "ELEMENTAL_SKILL", "description": "挥舞牛仔套索精准套住骑马或奔跑的目标，将其从马背拽下并捆绑制服。", "scaling": "抓捕活口与悬赏必备"}
            ],
            "passives": [{"name": "鹰眼洞察", "desc": "静止或潜行时开启鹰眼，透视猎物气味踪迹、草药发光与动物足迹。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "嚼烟草嚼块补满死神之眼 -> 拔枪开启死神之眼标记敌方全员头部 -> 退出瞬间子弹全出团灭敌军！"},
            "recommendations": {"weapons": {"bis": "兰卡斯特连发步枪 + 斯科菲尔德左轮"}, "artifacts": {"bis_set": "传说公鹿角饰品 + 东部传说背包"}},
            "version": "1.32"
        },
        {
            "name": "约翰·马斯顿 (John Marston)",
            "title": "边境浪子·最后的名侠",
            "rarity": 5,
            "element": "荒野亡命徒",
            "weapon_type": "双动左轮 / 杠杆步枪",
            "region": "西伊丽莎白·黑水镇 / 比彻之愿",
            "avatar_url": "https://patchwiki.biligame.com/images/rdr2/thumb/avatar_john.png/120px-avatar_john.png",
            "splash_url": "https://patchwiki.biligame.com/images/rdr2/thumb/avatar_john.png/600px-avatar_john.png",
            "base_stats": [
                {"level": "尾声完全体", "health_core": "100%", "stamina_core": "100%", "deadeye_core": "100%"}
            ],
            "special_ascension_stat": {"stat_name": "荒野生存", "values": {"特权": "承载亚瑟的遗志与东部传说所有装备"}},
            "ascension_materials": [{"tier": "尾声章节", "items": "建立比彻之愿牧场完成复仇"}],
            "talents": [
                {"name": "极速拔枪决斗 (Duelist)", "type": "NORMAL_ATTACK", "description": "在牛仔正午决斗中轻按开火键缓慢蓄力拔枪槽，在出鞘瞬间精确开火爆头击杀对手。", "scaling": "决斗绝对胜者"}
            ],
            "passives": [{"name": "旱鸭子", "desc": "落入深水区域体力值以极高速度扣除。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "继承亚瑟全部枪械与全收集物品，在尾声横扫雪山完成终极救赎。"},
            "recommendations": {"weapons": {"bis": "利奇菲尔德连发步枪"}},
            "version": "1.32"
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
                13, %s, %s, %s, %s, %s, %s,
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
            "name": "兰卡斯特连发步枪 (Lancaster Repeater)",
            "type": "连发步枪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/rdr2/weapon_lancaster.png",
            "base_atk_curve": [
                {"level": "基础面板", "atk": 62, "range": 75, "fire_rate": 70, "reload": 65, "accuracy": 82}
            ],
            "sub_stat": {"type": "综合最强", "values": {"弹仓": "14发", "特性": "精准度极高且射速飞快"}},
            "refinements": [
                {"rank": 1, "desc": "全游戏手感最好的主力长枪！14发弹仓容错率极高，开死神之眼连点爆头毫无后坐力。"}
            ],
            "ascension_materials": [{"tier": "枪匠升级", "items": "线膛枪管、加长枪管、雕花与改良瞄具"}],
            "version": "1.32"
        },
        {
            "name": "斯科菲尔德左轮手枪 (Schofield Revolver)",
            "type": "重型左轮",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/rdr2/weapon_schofield.png",
            "base_atk_curve": [
                {"level": "基础面板", "atk": 70, "range": 55, "fire_rate": 60, "reload": 58, "accuracy": 75}
            ],
            "sub_stat": {"type": "单发重击", "values": {"弹巢": "6发", "特性": "破损度低、击中躯干伤害极高"}},
            "refinements": [
                {"rank": 1, "desc": "最经典的牛仔配枪！瓦伦丁医生后院暗室抢劫即可在第二章极早免费获得。"}
            ],
            "ascension_materials": [{"tier": "枪匠升级", "items": "枪油保养、乌木握柄、珍珠雕花"}],
            "version": "1.32"
        },
        {
            "name": "滚轮闭锁式狙击步枪 (Rolling Block)",
            "type": "重型长管狙击枪",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/rdr2/weapon_rollingblock.png",
            "base_atk_curve": [
                {"level": "狙击威力", "atk": 95, "range": 95, "accuracy": 90}
            ],
            "sub_stat": {"type": "一枪致命", "values": {"弹容量": "1发单发装填", "特性": "超远距离猎杀传说大体型野兽"}},
            "refinements": [
                {"rank": 1, "desc": "远距离一枪倒地，猎杀传说灰熊、传说美洲野牛与远距离狙击哨兵的终极神兵。"}
            ],
            "ascension_materials": [{"tier": "枪匠升级", "items": "高倍瞄准镜"}],
            "version": "1.32"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                13, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "东部传说背包与神级饰品组 (Legend of the East Satchel & Trinkets)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/rdr2/satchel_legend.png",
            "two_piece_bonus": "【东部传说背包】：全背包所有物品（补药、贵重物、原料、补给）容量上限从 5 件直接扩充至 99 件！完全告别背包装满烦恼！",
            "four_piece_bonus": "【传说公鹿角 + 传说鳄鱼齿饰品】：剥皮判定皮毛品质提升 1 个星级；死神之眼核心消耗速度永久降低 10%。",
            "pieces": [
                {"slot": "神级背包", "name": "东部传说背包 (Satchel)", "main_stat": "全物品容量上限 99"},
                {"slot": "狩猎饰品", "name": "传说公鹿角饰品 (Buck Trinket)", "main_stat": "打猎3星皮毛概率质变"},
                {"slot": "战斗护符", "name": "传说鳄鱼齿护符 (Alligator Talisman)", "main_stat": "死眼消耗降低 10%"}
            ],
            "version": "1.32"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                13, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "生存体系",
            "title": "大镖客2 核心值 (Core) 与环形能量条 (Bar) 双层消耗模型",
            "formula": "Core_Percent -> Determines Regeneration Rate of Outside_Bar (Health, Stamina, Dead Eye)",
            "parameters": {
                "inner_core": "内部核心（心形/闪电/眼睛图标内部）决定生命、耐力和死神之眼的自动回复速度",
                "outer_bar": "外圈圆环条是实际消耗的即时蓄力槽，受到攻击扣除外环血量，外环归零直接扣除核心并猝死",
                "maintenance": "吃优质炖汤、烤大肉维持核心金色，嚼优质烟草保证死神之眼秒回"
            }
        },
        {
            "category": "狩猎物理",
            "title": "狩猎 3星完美皮毛 (Perfect Pelt) 口径匹配机制",
            "formula": "Clean_Kill_Headshot + Matched_Caliber + 3-Star_Animal = Perfect_Pelt",
            "parameters": {
                "small_game": "小型动物（松鼠、蛇、青蛙）：必须使用改良小型捕猎箭 (Small Game Arrow)",
                "varmint": "微型/中小型（兔子、獾、臭鼬、鸟类）：必须使用 .22 捕猎步枪 (Varmint Rifle)",
                "medium_large": "中大型动物（鹿、狼、美洲狮、熊、鳄鱼）：必须使用栓动步枪/弹头步枪精准命中头部"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (13, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (13, '荒野大镖客2 第二章速刷东部传说背包与神级白马全流程', 1, 'GENERAL', 'MEDIUM', '["大镖客2", "东部传说背包", "皮毛狩猎", "白阿拉伯马", "第二章封神"]',
                '教会你如何在第二章离开雪山后，停留在马掌望台营地将全属性拉满、做出99容量神级背包并捕获伊莎贝拉湖纯白阿拉伯马。',
                '{"sections":[{"title":"一、第一优先级：做东部传说背包","text":"去黑市买皮革制作工具，优先猎杀传说公鹿制作公鹿角饰品！随后狩猎完美鹿皮、野猪皮、美洲狮皮、河狸皮交给皮尔逊，99容量背包做完游戏体验提升10倍！"},{"title":"二、伊莎贝拉湖白阿拉伯马","text":"第二章直接骑马前往西北部伊莎贝拉雪湖左侧，慢步靠近按呼唤键安抚，骑上后向反方向拉摇杆驯服，获得极高加速度神驹！"}]}',
                'PUBLISHED', 5200, 4850, 40, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (13, '荒野大镖客2 荣誉值系统与专属特权',
                '荣誉值从 -8 到 +8 浮动。高荣誉值（+6以上）特权：1. 全圣丹尼斯与各地枪匠铺、杂货店购买所有物品享受 50% 骨折折扣；2. 解锁英雄握柄等专属武器外观；3. 最终章解锁亚瑟安详走向夕阳的真结局；低荣誉值则解锁歹徒握柄与黑水镇专属对话。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 荒野大镖客2 同步完成 ---")

# ==========================================
# 4. 炉石传说 (Hearthstone, ID = 18)
# ==========================================
def sync_hearthstone(cur):
    print("--- 正在同步 炉石传说 (Hearthstone, game_id = 18) ---")
    gid = 18
    chars = [
        {
            "name": "吉安娜·普罗德摩尔 (法师 - Jaina Proudmoore)",
            "title": "肯瑞托大法师·冰霜与奥术",
            "rarity": 5,
            "element": "冰霜 / 奥术 / 火焰",
            "weapon_type": "英雄技能·二级火焰冲击",
            "region": "达拉然",
            "avatar_url": "https://patchwiki.biligame.com/images/hs/thumb/avatar_jaina.png/120px-avatar_jaina.png",
            "splash_url": "https://patchwiki.biligame.com/images/hs/thumb/avatar_jaina.png/600px-avatar_jaina.png",
            "base_stats": [
                {"level": "天梯满血", "hp": 30, "armor": 0, "max_mana": 10}
            ],
            "special_ascension_stat": {"stat_name": "法术共鸣", "values": {"法术强度": "法强加成法术直伤，冰冻控场延缓敌方随从回合"}},
            "ascension_materials": [{"tier": "千胜头像", "items": "法师天梯累计获得 1000 场对战胜利"}],
            "talents": [
                {"name": "英雄技能·火焰冲击 (Fireblast)", "type": "NORMAL_ATTACK", "description": "消耗 2 点法力值，造成 1 点任意伤害（可点随从亦可点英雄，补刀神技）。", "scaling": "无视嘲讽，精准点杀"},
                {"name": "标志法术·火球术 (Fireball)", "type": "ELEMENTAL_SKILL", "description": "消耗 4 点法力值，造成 6 点巨额火焰直伤打击！法师斩杀的核心组件。", "scaling": "4费6点高性价比直伤"},
                {"name": "终极奥秘·寒冰屏障 (Ice Block / 冰箱)", "type": "ELEMENTAL_BURST", "description": "消耗 3 点法力值挂起奥秘。当你的英雄受到致死伤害时，免疫该伤害并使你的英雄在当前回合完全【免疫所有伤害】！", "scaling": "苟命一回合逆风翻盘神级奥秘"}
            ],
            "passives": [{"name": "法力燃烧", "desc": "法术卡牌消耗可通过法力龙、露娜的口袋银河进行费用减免。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "前期奥秘与冰环控场 -> 挂冰箱自保 -> 后期法强安东尼无限火球或露娜雷诺宇宙斩杀！"},
            "recommendations": {"weapons": {"bis": "艾露尼斯 (Aluneth) / 唤醒之杖"}},
            "version": "30.4"
        },
        {
            "name": "加尔鲁什·地狱咆哮 (战士 - Garrosh Hellscream)",
            "title": "部落酋长·防战叠甲之神",
            "rarity": 5,
            "element": "重甲防御 / 受伤激怒",
            "weapon_type": "英雄技能·全副武装 (Tank Up!)",
            "region": "奥格瑞玛",
            "avatar_url": "https://patchwiki.biligame.com/images/hs/thumb/avatar_garrosh.png/120px-avatar_garrosh.png",
            "splash_url": "https://patchwiki.biligame.com/images/hs/thumb/avatar_garrosh.png/600px-avatar_garrosh.png",
            "base_stats": [
                {"level": "防战极限", "hp": 30, "armor": 100, "max_mana": 10}
            ],
            "special_ascension_stat": {"stat_name": "叠甲无上限", "values": {"特权": "护甲值可无限累加突破 100+，盾猛打出百点爆发"}},
            "ascension_materials": [{"tier": "千胜头像", "items": "战士天梯累计获得 1000 场对战胜利"}],
            "talents": [
                {"name": "英雄技能·全副武装 (Armor Up!)", "type": "NORMAL_ATTACK", "description": "消耗 2 点法力值，获得 2 点护甲值（图哈特/强化技能后获得 4 点护甲）。", "scaling": "堆叠海量有效生命池"},
                {"name": "标志法术·盾牌猛击 (Shield Slam)", "type": "ELEMENTAL_SKILL", "description": "消耗 1 点法力值，对一个随从造成等同于你当前护甲值的巨额伤害！", "scaling": "1费消灭任何泰坦或大表哥首领"},
                {"name": "清场神技·绝命乱斗 (Brawl)", "type": "ELEMENTAL_BURST", "description": "消耗 5 点法力值，让战场上所有随从进行惨烈混战，最终仅有 1 个随机随从幸存！", "scaling": "无视圣盾与血量的终极清场"}
            ],
            "passives": [{"name": "激怒本能", "desc": "随从受到伤害未死亡时触发激怒加攻效果。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "铜皮铁骨防守反击：解光对手所有资源 -> 叠满上百护甲 -> 疲劳拖死对手！"},
            "recommendations": {"weapons": {"bis": "血吼 (Gorehowl) / 炽炎战斧"}},
            "version": "30.4"
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
                18, %s, %s, %s, %s, %s, %s,
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
            "name": "血吼 (Gorehowl)",
            "type": "战士传奇武器",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hs/weapon_gorehowl.png",
            "base_atk_curve": [
                {"level": "基础手牌", "atk": 7, "durability": 1}
            ],
            "sub_stat": {"type": "一斧斩千军", "values": {"特性": "攻击随从改为降低1点攻击力而不消耗耐久度"}},
            "refinements": [
                {"rank": 1, "desc": "地狱咆哮父子的传奇战斧！攻击敌方随从时不扣除 1 点耐久，而是改为攻击力 -1，一把武器可连续劈死 7 个敌方中高费随从！"}
            ],
            "ascension_materials": [{"tier": "合成造价", "items": "400 奥术之尘合成"}],
            "version": "30.4"
        },
        {
            "name": "弑君 (Kingsbane)",
            "type": "潜行者不朽武器",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hs/weapon_kingsbane.png",
            "base_atk_curve": [
                {"level": "无限成长", "atk": 1, "durability": 3}
            ],
            "sub_stat": {"type": "亡语保留附魔", "values": {"特性": "洗入牌库时永久保留涂油、吸血、剧毒等所有Buff"}},
            "refinements": [
                {"rank": 1, "desc": "弑君贼的核心灵魂！通过致命药膏、吸血药膏无限强化，后期一刀 15 攻吸血且永不疲劳死亡！"}
            ],
            "ascension_materials": [{"tier": "合成造价", "items": "1600 奥术之尘合成"}],
            "version": "30.4"
        }
    ]

    for w in weaps:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                18, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalize_curve(w['base_atk_curve'])),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = [
        {
            "name": "宇宙流派套牌构筑体系 (Highlander Reno Set)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/hs/set_highlander.png",
            "two_piece_bonus": "套牌中没有重复相同的单卡（全为单张）。",
            "four_piece_bonus": "【雷诺·杰克逊】：生命值直接回满 30 点！【孤胆孤影雷诺】：战吼消灭全场敌方随从并将对手战场空位限制为 1 个！控场与回复天花板。",
            "pieces": [
                {"slot": "核心随从 (6费)", "name": "雷诺·杰克逊 (Reno Jackson)", "main_stat": "战吼将生命值回满"},
                {"slot": "英雄卡牌 (8费)", "name": "孤胆孤影雷诺 (Reno Lone Ranger)", "main_stat": "彻底清场并封锁格子"}
            ],
            "version": "30.4"
        }
    ]

    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                18, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = [
        {
            "category": "结算机制",
            "title": "炉石传说 战吼与亡语事件结算队列优先级",
            "formula": "Play_Card -> Battlecry_Phase -> Enter_Play -> Trigger_Secrets -> Death_Phase(Deathrattle Queue)",
            "parameters": {
                "battlecry": "战吼在随从正式进入战场前优先结算，若战吼破坏了触发条件，按进场队列依次处理",
                "deathrattle": "多个随从同时阵亡时，按照它们进入战场的先后时间顺序（先入先出）依次结算亡语效果"
            }
        },
        {
            "category": "伤害疲劳",
            "title": "抽牌疲劳伤害累进函数",
            "formula": "Fatigue_Damage(N) = N (where N is the N-th empty draw, direct face damage bypassing armor reduction)",
            "parameters": {
                "fatigue": "抽空牌库后每次尝试抽牌受到递增直伤（1点、2点、3点...第10次直接扣55血），是防战与疲劳控制卡组斩杀底牌"
            }
        }
    ]

    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (18, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    cur.execute("""
        INSERT INTO guide (game_id, title, author_id, type, difficulty, tags, summary, content, status, like_count, useful_count, verify_count, created_at, updated_at)
        VALUES (18, '炉石传说 传说段位宇宙战与宇宙法控场留牌全攻略', 1, 'BUILD', 'ADVANCED', '["炉石传说", "宇宙战", "雷诺", "防战", "法力曲线"]',
                '详解当前天梯高胜率宇宙套牌运营：起手留牌策略、对阵快攻洗低费解牌、对阵慢速保留雷诺与导演翻盘时机。',
                '{"sections":[{"title":"一、对阵快攻起手留牌","text":"必留炽炎战斧、盾猛、全清理裂地波；法师必留远古谜团、异议、奥术箭，不贪高费，前4费按住对面攻势即可轻松获胜。"},{"title":"二、雷诺使用时机","text":"雷诺不要见残血就打！尽量等到骗出对面核心超展开（如亡语满场或铺满巨人）时打出孤胆孤影雷诺彻底除外清场！"}]}',
                'PUBLISHED', 4100, 3750, 25, NOW(), NOW())
        ON CONFLICT DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO wiki_entry (game_id, title, content, last_updated)
        VALUES (18, '炉石传说 经典关键词 (Keywords) 效果一览',
                '1. 战吼：从手牌打出时立即生效；2. 亡语：随从阵亡时触发；3. 圣盾：首次受到伤害时免疫；4. 嘲讽：敌方随从必须先攻击具有嘲讽的目标；5. 剧毒：造成任何伤害直接消灭目标随从；6. 吸血：造成的伤害转化为英雄生命值；7. 突袭：登场当回合可攻击敌方随从（不可打脸）；8. 冲锋：登场当回合可攻击任何目标；9. 发现：三选一一张符合条件的卡牌。', NOW())
        ON CONFLICT DO NOTHING;
    """)
    print("--- 炉石传说 同步完成 ---")

def sync_all():
    print("=== 开始同步四大高热度经典神作数据 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    sync_hollow_knight(cur)
    sync_isaac(cur)
    sync_rdr2(cur)
    sync_hearthstone(cur)
    conn.commit()
    conn.close()
    print("=== 四大高热度神作全量数据同步完成！ ===")

if __name__ == '__main__':
    sync_all()
