#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博德之门3 (Baldur's Gate 3) 全量数值体系落库与同步脚本
game_id = 11

包含:
1. 6 大经典起源同伴角色 (影心、阿斯代伦、盖尔、莱埃泽尔、卡菈克、威尔)
   - 1~12 级生命成长、力敏体智信魅六维白值与豁免加值
   - 职业核心专长、法术环位、戏法与战斗大师战法
2. 6 件传奇/珍奇神兵 (博德安的巨人杀手、洛山达之血、生死离别、尼鲁纳、玛科赫什基、地狱火手弩)
3. 4 大核心构筑奇物套装 (酒馆斗殴投掷蛮荒套、雷电充能法皇套、辐射闪光回响套、奥术敏锐百发百中套)
4. 5 大 D&D 5e 底层规则机制公式 (D20检定与豁免公式、优势劣势双骰模型、动作资源与法术位机制、元素地表反应、法术豁免DC判定)
5. 3 篇荣誉模式攻略与百科词条
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

def get_bg3_characters():
    return [
        {
            "name": "影心 (Shadowheart)",
            "title": "莎尔与塞伦涅圣徒·诡术/光明牧师",
            "rarity": 5,
            "element": "神圣光辉 / 幽暗暗影",
            "weapon_type": "权杖/盾牌/法杖",
            "region": "博德之门·下城区",
            "avatar_url": "https://patchwiki.biligame.com/images/bg3/thumb/5/52/avatar_shadowheart.png/120px-avatar_shadowheart.png",
            "splash_url": "https://patchwiki.biligame.com/images/bg3/thumb/5/52/avatar_shadowheart.png/600px-avatar_shadowheart.png",
            "base_stats": [
                {"level": "1", "hp": 10, "ac": 15, "str": 13, "dex": 13, "con": 14, "int": 10, "wis": 17, "cha": 8},
                {"level": "4", "hp": 31, "ac": 17, "str": 13, "dex": 14, "con": 16, "int": 10, "wis": 18, "cha": 8},
                {"level": "8", "hp": 59, "ac": 19, "str": 13, "dex": 14, "con": 16, "int": 10, "wis": 20, "cha": 8},
                {"level": "12", "hp": 91, "ac": 22, "str": 13, "dex": 14, "con": 16, "int": 10, "wis": 22, "cha": 8}
            ],
            "special_ascension_stat": {"stat_name": "核心信条", "values": {"信仰": "莎尔夜之歌救赎 / 塞伦涅银月之光"}},
            "ascension_materials": [{"tier": "主线章节", "items": "第一章德鲁伊丛林 -> 第二章堕落暗影之地 -> 第三章哀伤之邸"}],
            "talents": [
                {"name": "引导神力·拂晓之光 (Radiance of the Dawn)", "type": "ELEMENTAL_BURST", "description": "驱散周围 9 米内所有魔法黑暗，对范围内所有敌怪造成 2d10 + 牧师等级 的纯光辉伤害，强力清场。", "scaling": "短休刷新引导神力，对不死生物与暗影生物造成致命打击"},
                {"name": "3环神术·灵体守卫 (Spirit Guardians)", "type": "ELEMENTAL_SKILL", "description": "召唤一圈旋转的光辉或暗影幽魂环绕周身，进入范围的敌人移动速度减半，并在每回合开始或接触时受到 3d8 光耀伤害！配合辐射闪光套直接将敌人全员盲目！", "scaling": "专注持续10回合，牧师最强神技"},
                {"name": "2环神术·灵体武器 (Spiritual Weapon)", "type": "NORMAL_ATTACK", "description": "消耗附赠动作召唤一柄飘浮的圣光重锤协同作战，不占用专注槽。", "scaling": "持续10回合，附赠动作输出神技"}
            ],
            "passives": [{"name": "莎尔的祝福", "desc": "在暗影蔽日的环境下进行潜行检定获得优势。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "战前开灵体守卫 -> 佩戴辐射法球装备 -> 疾跑冲入敌群疯狂叠辐射法球削减敌人命中率！"},
            "recommendations": {"weapons": {"bis": "洛山达之血 (Blood of Lathander)"}, "artifacts": {"bis_set": "辐射光球与回响套装"}},
            "version": "Patch 7"
        },
        {
            "name": "阿斯代伦 (Astarion)",
            "title": "苍白精灵·刺客/游侠",
            "rarity": 5,
            "element": "穿刺偷袭",
            "weapon_type": "双持手弩/短剑",
            "region": "博德之门·卡扎多尔宫殿",
            "avatar_url": "https://patchwiki.biligame.com/images/bg3/thumb/a/a2/avatar_astarion.png/120px-avatar_astarion.png",
            "splash_url": "https://patchwiki.biligame.com/images/bg3/thumb/a/a2/avatar_astarion.png/600px-avatar_astarion.png",
            "base_stats": [
                {"level": "1", "hp": 10, "ac": 14, "str": 8, "dex": 17, "con": 14, "int": 13, "wis": 13, "cha": 10},
                {"level": "4", "hp": 31, "ac": 16, "str": 8, "dex": 18, "con": 14, "int": 13, "wis": 13, "cha": 10},
                {"level": "8", "hp": 59, "ac": 18, "str": 8, "dex": 20, "con": 14, "int": 13, "wis": 13, "cha": 10},
                {"level": "12", "hp": 87, "ac": 20, "str": 8, "dex": 22, "con": 14, "int": 13, "wis": 13, "cha": 10}
            ],
            "special_ascension_stat": {"stat_name": "飞升吸血鬼", "values": {"特权": "每次攻击额外附加 1d10 黯蚀伤害"}},
            "ascension_materials": [{"tier": "主线章节", "items": "击败卡扎多尔完成黑天仪式"}],
            "talents": [
                {"name": "偷袭·远程/近战 (Sneak Attack)", "type": "NORMAL_ATTACK", "description": "在自身处于优势或目标周围 1.5 米内有盟友且自身未处于劣势时触发，造成武器伤害并额外附加最多 6d6 点致命偷袭伤害！", "scaling": "1级 1d6，11级高达 6d6 巨额物理爆发"},
                {"name": "吸血鬼衍生体撕咬 (Vampiric Bite)", "type": "ELEMENTAL_SKILL", "description": "消耗附赠动作吸取无助或被控制目标的鲜血，造成 2d4 穿刺伤害并回复等量生命值，自身获得【快乐】Buff（所有检定+1）。", "scaling": "每长休1次，提供常驻+1攻击与豁免"},
                {"name": "刺客本能·刺客伏击 (Assassinate)", "type": "PASSIVE_TALENT", "description": "对尚未行动的敌人发动攻击必定处于优势；且对受惊状态下的敌人命中的所有攻击必定转化为【暴击】！", "scaling": "先攻决胜，开战秒杀精英怪"}
            ],
            "passives": [{"name": "灵巧动作·疾跑/隐匿", "desc": "消耗附赠动作即可进行疾跑、撤退或隐藏。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "双持手弩隐匿开战 -> 触发敌人受惊 -> 附赠射击+主手射击全暴击秒杀！"},
            "recommendations": {"weapons": {"bis": "地狱火手弩 + 警觉手弩"}, "artifacts": {"bis_set": "奥术敏锐头盔套"}},
            "version": "Patch 7"
        },
        {
            "name": "盖尔 (Gale)",
            "title": "深水城法师·魔网法皇",
            "rarity": 5,
            "element": "全系奥术",
            "weapon_type": "传奇法杖/长袍",
            "region": "深水城",
            "avatar_url": "https://patchwiki.biligame.com/images/bg3/thumb/c/cf/avatar_gale.png/120px-avatar_gale.png",
            "splash_url": "https://patchwiki.biligame.com/images/bg3/thumb/c/cf/avatar_gale.png/600px-avatar_gale.png",
            "base_stats": [
                {"level": "1", "hp": 8, "ac": 12, "str": 8, "dex": 13, "con": 15, "int": 17, "wis": 10, "cha": 12},
                {"level": "4", "hp": 26, "ac": 13, "str": 8, "dex": 14, "con": 16, "int": 18, "wis": 10, "cha": 12},
                {"level": "8", "hp": 50, "ac": 15, "str": 8, "dex": 14, "con": 16, "int": 20, "wis": 10, "cha": 12},
                {"level": "12", "hp": 74, "ac": 18, "str": 8, "dex": 14, "con": 16, "int": 22, "wis": 10, "cha": 12}
            ],
            "special_ascension_stat": {"stat_name": "耐瑟瑞尔法球", "values": {"特权": "胸中毁灭法球与魔网女神祝福"}},
            "ascension_materials": [{"tier": "主线章节", "items": "吞噬魔法神器压制法球饥渴"}],
            "talents": [
                {"name": "3环塑能·火球术 (Fireball)", "type": "ELEMENTAL_SKILL", "description": "指尖射出炽热火花，在大范围区域引发毁灭火球爆轰，造成 8d6 点巨额火焰伤害（豁免成功伤害减半）。", "scaling": "法系清场代名词，升环施放每环增加 1d6"},
                {"name": "6环禁咒·链状闪电 (Chain Lightning)", "type": "ELEMENTAL_BURST", "description": "引动狂暴天雷轰击主目标，并跳跃连锁轰击周围 3 名其他目标，各造成 10d8 闪电伤害！在潮湿地表下伤害直接翻倍达到 20d8 毁天灭地！", "scaling": "配合潮湿状态水导电打出数百核爆"},
                {"name": "3环防御·法术反制 (Counterspell)", "type": "PASSIVE_TALENT", "description": "使用反应动作强行中断视野内施法者正在释放的法术，将其魔法直接湮灭打散。", "scaling": "封锁 Boss 关键大招神技"}
            ],
            "passives": [{"name": "塑能法术塑形", "desc": "施放火球术等范围魔法时自动避开队友，使盟友豁免必定成功且完全免疫伤害！"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "队友投掷水瓶制造大范围【潮湿】状态 -> 盖尔施放闪电束/链状闪电造成双倍导电雷暴！"},
            "recommendations": {"weapons": {"bis": "玛科赫什基 (Markoheshkir)"}, "artifacts": {"bis_set": "法术火花雷电充能套"}},
            "version": "Patch 7"
        },
        {
            "name": "莱埃泽尔 (Lae'zel)",
            "title": "吉斯洋基战神·战斗大师",
            "rarity": 5,
            "element": "纯粹武艺",
            "weapon_type": "巨剑/两手巨剑",
            "region": "吉斯星界星舰",
            "avatar_url": "https://patchwiki.biligame.com/images/bg3/thumb/2/23/avatar_laezel.png/120px-avatar_laezel.png",
            "splash_url": "https://patchwiki.biligame.com/images/bg3/thumb/2/23/avatar_laezel.png/600px-avatar_laezel.png",
            "base_stats": [
                {"level": "1", "hp": 12, "ac": 16, "str": 17, "dex": 13, "con": 15, "int": 10, "wis": 12, "cha": 8},
                {"level": "4", "hp": 38, "ac": 18, "str": 18, "dex": 14, "con": 16, "int": 10, "wis": 12, "cha": 8},
                {"level": "8", "hp": 74, "ac": 20, "str": 20, "dex": 14, "con": 16, "int": 10, "wis": 12, "cha": 8},
                {"level": "12", "hp": 110, "ac": 23, "str": 24, "dex": 14, "con": 16, "int": 10, "wis": 12, "cha": 8}
            ],
            "special_ascension_stat": {"stat_name": "星界武士", "values": {"特权": "动作如潮一回合砍出 6~9 刀"}},
            "ascension_materials": [{"tier": "主线章节", "items": "星界棱镜与洋基养育间"}],
            "talents": [
                {"name": "战士核心·动作如潮 (Action Surge)", "type": "ELEMENTAL_BURST", "description": "突破身体极限，立即额外获得 1 个完整的核心动作！短休即可刷新。", "scaling": "11级战士配合动作如潮单回合可砍出 6 记重斩！"},
                {"name": "战法·摔绊攻击 (Trip Attack)", "type": "NORMAL_ATTACK", "description": "消耗一枚战术骰，攻击附加 1d8 伤害并将目标击倒在地陷入倒地劣势。", "scaling": "击倒后所有近战攻击对该目标均拥有优势判定"},
                {"name": "专长·巨武器大师 (Great Weapon Master)", "type": "PASSIVE_TALENT", "description": "进行近战攻击时命中检定 -5，但命中伤害额外暴涨 +10 点！且暴击或击杀时奖励一次附赠动作攻击！", "scaling": "近战物理输出第一专长"}
            ],
            "passives": [{"name": "回气", "desc": "消耗附赠动作回复 1d10 + 战士等级 的生命值。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "巨剑涂油开狂怒 -> 摔绊攻击击倒首领 -> 动作如潮全开巨武器斩击一回合砍出 200+ 物理秒杀！"},
            "recommendations": {"weapons": {"bis": "博德安的巨人杀手 (Balduran's Giantslayer)"}, "artifacts": {"bis_set": "酒馆狂暴套"}},
            "version": "Patch 7"
        },
        {
            "name": "卡菈克 (Karlach)",
            "title": "地狱狂战士·狂怒之火",
            "rarity": 5,
            "element": "地狱烈焰",
            "weapon_type": "投掷三叉戟/巨斧",
            "region": "阿弗纳斯第一地狱",
            "avatar_url": "https://patchwiki.biligame.com/images/bg3/thumb/a/ad/avatar_karlach.png/120px-avatar_karlach.png",
            "splash_url": "https://patchwiki.biligame.com/images/bg3/thumb/a/ad/avatar_karlach.png/600px-avatar_karlach.png",
            "base_stats": [
                {"level": "1", "hp": 14, "ac": 14, "str": 17, "dex": 13, "con": 16, "int": 8, "wis": 12, "cha": 10},
                {"level": "4", "hp": 45, "ac": 15, "str": 18, "dex": 14, "con": 16, "int": 8, "wis": 12, "cha": 10},
                {"level": "8", "hp": 85, "ac": 17, "str": 20, "dex": 14, "con": 16, "int": 8, "wis": 12, "cha": 10},
                {"level": "12", "hp": 125, "ac": 19, "str": 24, "dex": 14, "con": 16, "int": 8, "wis": 12, "cha": 10}
            ],
            "special_ascension_stat": {"stat_name": "地狱引擎心脏", "values": {"特权": "地狱铁升级强化狂暴过载"}},
            "ascension_materials": [{"tier": "主线章节", "items": "寻找地狱铁交给戴摩修复心脏"}],
            "talents": [
                {"name": "野蛮人·狂乱狂暴 (Frenzy)", "type": "ELEMENTAL_BURST", "description": "点燃胸口地狱引擎进入狂乱狂暴，物理抗性翻倍，获得附赠动作狂暴打击与愤怒投掷！", "scaling": "受击钝击/穿刺/挥砍减伤 50%"},
                {"name": "愤怒投掷 (Enraged Throw)", "type": "NORMAL_ATTACK", "description": "消耗附赠动作抓起地面上的物品、武器或活生生的敌人用力掷出，命中将其击倒并造成巨额坠落粉碎物理伤害！", "scaling": "配合【酒馆斗殴者】专长伤害倍增"},
                {"name": "专长·酒馆斗殴者 (Tavern Brawler)", "type": "PASSIVE_TALENT", "description": "进行徒手攻击、临时武器攻击或投掷时，力量调整值双倍计入攻击检定与伤害检定！", "scaling": "命中率高达 95%，伤害直奔每发 40~60 点！"}
            ],
            "passives": [{"name": "无甲防御", "desc": "不穿护甲时，将体质调整值计入护甲等级 AC。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "狂暴开启 -> 拿起返回武器（如尼鲁纳或闪电三叉戟）-> 居高临下疯狂投掷，百发百中砸碎一切！"},
            "recommendations": {"weapons": {"bis": "尼鲁纳 (Nyrulna)"}, "artifacts": {"bis_set": "酒馆斗殴投掷蛮荒套"}},
            "version": "Patch 7"
        }
    ]

def get_bg3_weapons():
    return [
        {
            "name": "博德安的巨人杀手 (Balduran's Giantslayer)",
            "type": "两手巨剑",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/bg3/weapon_balduran_giantslayer.png",
            "base_atk_curve": {"基础": "2d6 挥砍 + 3", "强化": "+3 附魔武器"},
            "sub_stat": {"type": "巨人神威", "values": {"伤害加倍": "命中伤害检定额外附加双倍力量调整值", "对巨优势": "攻击大型以上生物获得优势"}},
            "refinements": [
                {"rank": 1, "desc": "专属武器战技【巨人形态】：体型变为巨大型，造成额外 1d6 武器伤害并获得 27 点临时生命值，力量检定必定占优！"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "第三章安苏巨龙巢穴试炼击败龙巫妖"}],
            "version": "Patch 7"
        },
        {
            "name": "洛山达之血 (The Blood of Lathander)",
            "type": "单手硬头锤",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/bg3/weapon_blood_of_lathander.png",
            "base_atk_curve": {"基础": "1d6 钝击 + 3", "强化": "+3 附魔武器"},
            "sub_stat": {"type": "晨曦荣光", "values": {"光耀盲目": "周围6米亡灵与恶魔若未能通过豁免则陷入目盲", "晨曦之光": "生命归零时免死并回复 2~12 HP"}},
            "refinements": [
                {"rank": 1, "desc": "充能 6 环神圣法术【烈阳射线】：发射一道纯净炽热的光芒，对直线上所有敌人造成 6d6 光耀伤害并彻底致盲！"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "第一章瑰晨修道院伊尔明斯特密室解密"}],
            "version": "Patch 7"
        },
        {
            "name": "尼鲁纳 (Nyrulna)",
            "type": "传奇三叉戟",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/bg3/weapon_nyrulna.png",
            "base_atk_curve": {"基础": "1d8+3 (单手) / 1d10+3 (双手) 穿刺 + 1d6 雷鸣", "强化": "+3 附魔武器"},
            "sub_stat": {"type": "投掷神器", "values": {"自动返回": "投掷出去后必定瞬间自动返回手中", "雷鸣爆轰": "掷出爆炸造成 3d4 雷鸣范围冲击"}},
            "refinements": [
                {"rank": 1, "desc": "持有者移动速度增加 3 米，跳跃距离翻倍，且免疫所有坠落跌落伤害！投掷流野蛮人终极毕业兵刃。"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "第三章末日马戏团转盘击败赤红软泥怪恐龙丛林"}],
            "version": "Patch 7"
        },
        {
            "name": "玛科赫什基 (Markoheshkir)",
            "type": "传奇法杖",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/bg3/weapon_markoheshkir.png",
            "base_atk_curve": {"基础": "1d6 钝击 + 2", "强化": "+2 附魔法杖"},
            "sub_stat": {"type": "奥术至高", "values": {"法术DC": "+1 法术攻击骰与法术豁免难度", "凯雷卡灵能": "长休免费释放一次任意环位已学法术"}},
            "refinements": [
                {"rank": 1, "desc": "【凯雷卡的恩赐】：自选元素亲和（电、火、冰、毒、酸），直接学会对应元素的两门顶级高环法术（如链状闪电）且造成该属性伤害附加额外充能！"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "第三章巫术杂货店罗罗坎法师塔隐形力场解密"}],
            "version": "Patch 7"
        }
    ]

def get_bg3_artifacts():
    return [
        {
            "name": "散打僧投掷蛮荒套装 (Tavern Brawler Thrower)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/bg3/set_thrower.png",
            "two_piece_bonus": "配合【酒馆斗殴者】专长，投掷命中率直接锁定在 90%~95%，无视距离劣势。",
            "four_piece_bonus": "配合夸塞魔手套与闪电三叉戟，每次投掷造成物理+雷电+力场三重伤害，单回合输出突破 150 点！",
            "pieces": [
                {"slot": "头盔", "name": "狂暴之角头盔", "main_stat": "狂暴时重击阈值 -1"},
                {"slot": "胸甲", "name": "灵巧之骨胸甲", "main_stat": "AC 15 + 全敏捷调整值"},
                {"slot": "手套", "name": "夸塞魔咆哮手套", "main_stat": "投掷伤害 +1d4"},
                {"slot": "靴子", "name": "狂奔冲刺之靴", "main_stat": "疾跑附赠动作"}
            ],
            "version": "Patch 7"
        },
        {
            "name": "法术火花雷电充能套 (Lightning Charge Spellsparkler)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/bg3/set_lightning.png",
            "two_piece_bonus": "施放法术或戏法造成伤害时获得 2 层【闪电充能】。充能期间攻击骰 +1，伤害 +1 闪电伤害。",
            "four_piece_bonus": "闪电充能达到 5 层时引爆，造成额外 1d8 纯闪电电击打击！配合魔法飞弹单轮倾泻引爆 5 次！",
            "pieces": [
                {"slot": "法杖", "name": "法术火花 (The Spellsparkler)", "main_stat": "施法叠加闪电充能"},
                {"slot": "护符", "name": "生机火花护符", "main_stat": "魔法飞弹多射一发"},
                {"slot": "靴子", "name": "奔水之靴", "main_stat": "水面带电免疫触电"}
            ],
            "version": "Patch 7"
        },
        {
            "name": "辐射光球与回响套 (Radiating Orb Reverb)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/bg3/set_radiant.png",
            "two_piece_bonus": "造成光耀伤害时附加【辐射法球】，每层使目标的攻击检定受到 -1 惩罚（最高叠加至 -10 绝对无法命中）！",
            "four_piece_bonus": "叠加 5 层回响冲击时引爆，敌人受到 1d4 雷鸣伤害并必须通过体质豁免否则直接倒地！",
            "pieces": [
                {"slot": "戒指", "name": "光耀指环", "main_stat": "发光时伤害 +2"},
                {"slot": "胸甲", "name": "明光护甲", "main_stat": "灵体守卫范围光爆"},
                {"slot": "手套", "name": "震荡手套", "main_stat": "附加回响层数"}
            ],
            "version": "Patch 7"
        }
    ]

def get_bg3_mechanics():
    return [
        {
            "category": "规则核心",
            "title": "D&D 5e 二十面骰 (D20) 命中判定与豁免检定公式",
            "formula": "Attack_Roll = 1d20 + Ability_Modifier + Proficiency_Bonus >= Target_AC (Armor Class)",
            "parameters": {
                "critical_hit": "掷出自然 20 (Natural 20) 必定命中且触发暴击，所有伤害骰翻倍结算",
                "critical_miss": "掷出自然 1 (Natural 1) 必定大失败脱靶，无视任何数值加值",
                "saving_throw": "DC = 8 + 施法者关键属性调整值 + 熟练加值；目标掷 1d20 + 豁免加值 >= DC 则通过"
            }
        },
        {
            "category": "概率模型",
            "title": "优势 (Advantage) 与劣势 (Disadvantage) 双骰模型",
            "formula": "Advantage = Max(D20_A, D20_B) | Disadvantage = Min(D20_A, D20_B)",
            "parameters": {
                "advantage": "投掷两枚 20 面骰取较高点数。相当于在命中率上增加平均 +3.325 ~ +5.0 点的期望提升！",
                "disadvantage": "投掷两枚 20 面骰取较低点数，大幅抑制命中率并降低暴击概率至 0.25%",
                "cancel": "无论有多少个优势和劣势来源，只要同时存在至少一个优势和一个劣势，两者直接相互抵消为正常掷骰"
            }
        },
        {
            "category": "元素连锁",
            "title": "元素地表与环境连锁反应机制",
            "formula": "Water + Lightning = Electrified_Surface (Double Lightning DMG to Wet Targets)",
            "parameters": {
                "wet_status": "潮湿 (Wet) 状态：使受影响的目标对【冰霜】与【闪电】伤害具有易伤（受到 200% 双倍伤害！）",
                "fire_grease": "油脂地表遇火即引爆为烈火焦土，对范围内所有生物造成二次爆炸火焰伤害",
                "frozen": "被完全冻结的目标受到钝击、雷鸣或力场伤害时产生击碎效应 (Shatter)"
            }
        },
        {
            "category": "战斗资源",
            "title": "动作、附赠动作与法术环位资源分配",
            "formula": "Per_Turn = 1 Action + 1 Bonus_Action + 1 Reaction + Movement_Speed",
            "parameters": {
                "action": "用于普通攻击、施放大法术、疾跑冲刺、协助倒地同伴",
                "bonus_action": "用于喝治疗药水、跳跃位移、附赠打击、开启狂暴或施放特定轻型神术",
                "spell_slots": "1环至6环法术位。长休恢复全部法术位；邪术师通过短休即可回满专属法术位"
            }
        }
    ]

def get_bg3_guides_and_wikis():
    guides = [
        {
            "title": "博德之门3 荣誉模式通关全书：从第一章到脑池决战",
            "type": "BUILD",
            "difficulty": "ADVANCED",
            "tags": ["荣誉模式", "通关指南", "传奇动作", "单档无存档"],
            "summary": "详细拆解荣誉模式下 Boss 传奇动作应对机制、逃跑撤离点预留、关键药水制作与最稳妥的逃课路线。",
            "content": {
                "sections": [
                    {"title": "一、荣誉模式三大铁律", "text": "1. 绝不盲目开战！永远留一名隐身盗贼或高机动角色在营地或战斗外待命。\n2. Boss 传奇动作必读：枭熊幼崽召唤、第二章米尔寇骨指禁疗光环必须预先用光耀或投掷击碎。"},
                    {"title": "二、四大真神阵容", "text": "1. 酒馆斗殴蛮荒投掷流卡菈克（百发百中输出核心）\n2. 散打僧（双持控制永动机）\n3. 光明领域影心（灵体守卫叠光球废掉 Boss 命中）\n4. 剑咏/诗帕（高AC高爆发全能位）"}
                ]
            },
            "like_count": 2890,
            "useful_count": 2540
        },
        {
            "title": "酒馆投掷流野蛮人：伤害破百且必中的逃课天花板",
            "type": "CHARACTER",
            "difficulty": "EASY",
            "tags": ["酒馆斗殴者", "卡菈克", "投掷蛮", "尼鲁纳", "三叉戟"],
            "summary": "4级选出【酒馆斗殴者】专长后即可成型的无脑强力流派，力量双倍加成，一回合掷死一切硬茬。",
            "content": {
                "sections": [
                    {"title": "一、专长核心机制", "text": "酒馆斗殴者将你的力量修正值两次加到攻击检定和伤害上！当你拥有20力量（+5调整值）时，直接额外赠送+10伤害和+10命中！"},
                    {"title": "二、毕业装备搭配", "text": "第一章地精营地买【返回长矛】；第三章换【尼鲁纳】；佩戴夸塞魔手套和狂暴之角头盔，单回合轻松投掷 4 次造成 200+ 物理大爆炸！"}
                ]
            },
            "like_count": 2340,
            "useful_count": 2100
        }
    ]
    wikis = [
        {
            "title": "博德之门3 豁免检定与法术DC",
            "content": "当法术施加在敌人身上时，敌人需要进行属性豁免检定（如敏捷、体质或感知）。敌人的 1d20 + 豁免加值 若低于施法者的法术豁免难度等级（DC = 8 + 施法属性加值 + 熟练加值），则受到完全法术伤害或控制效果。"
        },
        {
            "title": "休息机制：短休与长休",
            "content": "队伍每天可进行 2 次短休（恢复一半生命值与特定职业资源如邪术师法术位、武僧气点、战士动作如潮）；进行长休消耗 40 点（荣誉模式 80 点）营地补给，完全恢复生命值、法术位与全部技能充能，并推进营地剧情。"
        }
    ]
    return guides, wikis

def sync_all():
    print("=== 开始同步 博德之门3 (Baldur's Gate 3) 全量数据 (game_id = 11) ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    chars = get_bg3_characters()
    print(f"正在写入 {len(chars)} 位起源角色数据...")
    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                11, %s, %s, %s, %s, %s, %s,
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

    weaps = get_bg3_weapons()
    print(f"正在写入 {len(weaps)} 把传奇武器数据...")
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
                11, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = get_bg3_artifacts()
    print(f"正在写入 {len(arts)} 套构筑奇物套装数据...")
    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                11, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = get_bg3_mechanics()
    print(f"正在写入 {len(mechs)} 条战斗机制与公式...")
    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (11, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    guides, wikis = get_bg3_guides_and_wikis()
    print(f"正在写入 {len(guides)} 篇攻略与 {len(wikis)} 条百科词条...")
    for g in guides:
        cur.execute("""
            INSERT INTO guide (
                game_id, version_id, title, author_id, type, difficulty,
                tags, summary, content, status, like_count, useful_count, verify_count,
                created_at, updated_at
            ) VALUES (
                11, NULL, %s, 1, %s, %s,
                %s, %s, %s, 'PUBLISHED', %s, %s, 20,
                NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (g['title'], g['type'], g['difficulty'], Json(g['tags']), g['summary'], Json(g['content']), g['like_count'], g['useful_count']))

    for wk in wikis:
        cur.execute("""
            INSERT INTO wiki_entry (game_id, title, content, last_updated)
            VALUES (11, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (wk['title'], wk['content']))

    conn.commit()
    conn.close()
    print("=== 博德之门3 (game_id = 11) 全量数据写入完成！ ===")

if __name__ == '__main__':
    sync_all()
