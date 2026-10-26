#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
艾尔登法环 (Elden Ring) 全量数值体系落库与同步脚本
game_id = 1

包含:
1. 褪色者 7 大核心流派构筑体系 (力信骑士、纯敏出血流、智力法皇、纯力特大剑跳劈、智敏魔剑士、感应龙飨狂信徒、1级无用之人)
   - 1~150 级生命力/专注/耐力/力敏智信感白值成长、强韧度与减伤属性
   - 专属核心战技/法术/祷告、被动天赋与大卢恩/护符槽质变
2. 16 件交界地神兵与圣印/法杖触媒 (基础面板、力敏智信感补正评级、0~+10/+25强化、战技消耗)
3. 6 大传奇护符构筑体系与披挂套装 (战技爆发、极致防御、法皇奥术、异常状态增伤、耐力循环、罗刹神威套)
4. 5 大底层魂系战斗机制与公式 (削韧失衡处决、异常状态爆发、属性软硬上限与双手1.5倍力气、负重与翻滚无敌帧、防御与减伤双层模型)
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

OUT_DIR = os.path.join(os.path.dirname(__file__), "../out")
os.makedirs(OUT_DIR, exist_ok=True)

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def get_elden_ring_characters():
    """构建艾尔登法环 7 大褪色者核心流派与构筑体系"""
    return [
        {
            "name": "褪色者·力信圣骑士 (Strength / Faith Paladin)",
            "title": "黄金律法与熔炉掠夺者",
            "rarity": 5,
            "element": "力信流派",
            "weapon_type": "大剑/圣印记",
            "avatar_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/blasphemous_blade_weapon_elden_ring_wiki_guide_200px.png",
            "splash_url": "https://image.api.playstation.com/vulcan/ap/rnd/202110/2000/phvVT0qZfcRms5qDAk0SI3CM.png",
            "base_stats": [
                {"level": "1", "hp": 414, "atk": 65, "def": 50, "fp": 78, "stamina": 96, "poise": 15, "vigor": 12, "mind": 10, "endurance": 13, "strength": 16, "dexterity": 12, "intelligence": 9, "faith": 14, "arcane": 9},
                {"level": "30", "hp": 800, "atk": 140, "def": 75, "fp": 95, "stamina": 108, "poise": 32, "vigor": 25, "mind": 14, "endurance": 18, "strength": 22, "dexterity": 14, "intelligence": 9, "faith": 20, "arcane": 9},
                {"level": "60", "hp": 1334, "atk": 260, "def": 105, "fp": 120, "stamina": 122, "poise": 51, "vigor": 38, "mind": 18, "endurance": 24, "strength": 32, "dexterity": 15, "intelligence": 9, "faith": 32, "arcane": 9},
                {"level": "90", "hp": 1654, "atk": 410, "def": 128, "fp": 145, "stamina": 134, "poise": 68, "vigor": 48, "mind": 22, "endurance": 28, "strength": 40, "dexterity": 16, "intelligence": 9, "faith": 45, "arcane": 9},
                {"level": "120", "hp": 1821, "atk": 560, "def": 142, "fp": 175, "stamina": 142, "poise": 82, "vigor": 55, "mind": 26, "endurance": 32, "strength": 48, "dexterity": 17, "intelligence": 9, "faith": 60, "arcane": 9},
                {"level": "150", "hp": 1900, "atk": 690, "def": 155, "fp": 200, "stamina": 150, "poise": 95, "vigor": 60, "mind": 30, "endurance": 35, "strength": 54, "dexterity": 18, "intelligence": 9, "faith": 70, "arcane": 9}
            ],
            "special_ascension_stat": {
                "stat_name": "力信核心构筑特权",
                "values": {
                    "战技核心": "掠夺之火超长距离熔岩轰炸",
                    "吸血特权": "每次击中恢复 4% HP + 40，击杀敌人恢复 10% HP + 100",
                    "双重BUFF": "黄金树立誓 (+15% 全增伤/减伤) + 夏玻利利之吼 (+25% 极效增伤)"
                }
            },
            "ascension_materials": [
                {"tier": "前期·宁姆格福与啜泣半岛", "items": "圣杯露滴 × 4 | 黄金种子 × 6 | 强化石[1~3]"},
                {"tier": "中期·湖之利耶尼亚与雷亚卢卡利亚", "items": "圣杯露滴 × 3 | 黄金种子 × 5 | 丧色锻造石[4~6]"},
                {"tier": "中后期·亚坛高原与王城罗德尔", "items": "圣杯露滴 × 3 | 黄金种子 × 6 | 亵渎君王追忆"},
                {"tier": "后期·巨人山顶与圣树分支", "items": "古龙岩锻造石 | 玛莲妮亚的花瓣 | 丧色古龙岩"},
                {"tier": "毕业·法姆·亚兹拉与黄金树幽影", "items": "古龙岩丧色锻造石 × 2 | 黄金树幽影庇佑 Lv.20"}
            ],
            "talents": [
                {"name": "专属战技·掠夺之火 (Taker's Flames)", "type": "ELEMENTAL_SKILL", "description": "高举亵渎圣剑燃起烈焰向前方地面释放狂暴熔岩火柱，造成巨额火属性混合打击并强行击倒人型 Boss，且命中即吸血。", "scaling": "消耗 23 点 FP，伤害受信仰极高补正，击中回血 4% HP + 40"},
                {"name": "核心奇迹·黄金树立誓 (Golden Vow)", "type": "ELEMENTAL_BURST", "description": "高举圣印记向黄金树祈祷，使自身与周围同伴的攻击力提升 15%，全属性减伤率提升 10%，持续 80 秒。", "scaling": "消耗 47 点 FP，与所有武器战灰完美叠加"},
                {"name": "爆发祷告·熔炉百相之角与尾", "type": "NORMAL_ATTACK", "description": "引动初始熔炉原初之力，头顶化出巨角极速突进挑飞敌人，随后摆动巨尾进行大范围重扫。", "scaling": "蓄力伤害提升 35%，造成 45 点极高削韧硬直"},
                {"name": "核心天赋·黄金恩泽与续航", "type": "PASSIVE_TALENT", "description": "信仰每提升 10 点，圣印记圣职补正效率提升 8%，每击杀一名敌人额外返还 5 点专注值与 10% 最大生命值。", "scaling": "被动常驻生效"},
                {"name": "灵药混合·火破裂与岩刺破露滴", "type": "EXPLORATION_TALENT", "description": "饮用特制灵药，使火属性伤害提高 20%，同时大幅提升重击与战技的削韧失衡判定 30%，持续 3 分钟。", "scaling": "每次在赐福休整后自动充能 1 次"}
            ],
            "passives": [
                {"name": "熔炉强韧", "desc": "施展掠夺之火与熔炉百相祷告时获得强韧霸体，承受 50 点以下攻击不被打断。"},
                {"name": "神圣祝福", "desc": "生命值低于 20% 时，自动触发缓慢回血并使火抗与圣抗提高 30%。"},
                {"name": "信仰共鸣", "desc": "佩戴黄金树圣印记时，治愈类与增益类祷告持续时间延长 25%。"}
            ],
            "constellations": [
                {"c": 1, "name": "记忆空格解放·第1~2格", "desc": "在圆桌厅堂通过记忆石扩充祷告槽位，可同时装备黄金树立誓与黑焰护身。"},
                {"c": 2, "name": "护符皮袋拓展·第2槽", "desc": "击败恶兆妖鬼玛尔基特，解锁第 2 个护符槽位，佩戴亚历山大碎片。"},
                {"c": 3, "name": "葛瑞克的大卢恩恩惠", "desc": "神授塔激活葛瑞克大卢恩，使用弯弧后全属性全方位增加 5 点！"},
                {"c": 4, "name": "护符皮袋拓展·第3槽", "desc": "获得两个大卢恩觐见双指，解锁第 3 个护符槽位，佩戴龙徽大盾护符。"},
                {"c": 5, "name": "护符皮袋终极解放·第4槽", "desc": "王城击败初始之王葛孚雷幻影，解锁全部 4 槽，达成护符神装闭环！"},
                {"c": 6, "name": "玛莲妮亚的大卢恩/幽影庇佑", "desc": "受击后反击可夺回损失的血量，在交界地与幽影地化身不灭掠夺战神！"}
            ],
            "special_mechanics": {
                "combat_loop": "战前拍黄金树立誓 + 夏玻利利之吼 -> 饮用火破裂+岩刺露滴 -> 中距离连续复读掠夺之火强行打翻Boss压起身 -> 贴脸处决或重击收割！",
                "poise_control": "亵渎圣剑拥有极强击飞判定，除玛莲妮亚等极少超霸体外，绝大多数人形骑士与精英怪均会被单发轰翻倒地！"
            },
            "recommendations": {
                "weapons": {"bis": "亵渎圣剑 +10 (Blasphemous Blade)", "alternative_5s": "黄金律法大剑 / 玛利喀斯的黑剑", "catalyst": "黄金树圣印记 / 爪痕圣印记"},
                "artifacts": {"bis_set": "亚历山大碎片 + 龙徽大盾护符 + 鲜火对蝎 + 珍珠龙徽护符+2", "alt_set": "熔炉骑士树形套装 (强化熔炉祷告 15%)"},
                "main_stats": {"priority": "信仰 (60~80) > 生命力 (60) > 力气 (40~54双手) > 专注 (25~30) > 耐力 (30+穿重甲)"}
            },
            "version": "1.14"
        },
        {
            "name": "褪色者·纯敏神秘出血流 (Dexterity Bleed / Arcane)",
            "title": "鲜血王朝与切腹死斗者",
            "rarity": 5,
            "element": "出血流派",
            "weapon_type": "双刀/双头剑",
            "avatar_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/rivers_of_blood_weapon_elden_ring_wiki_guide_200px.png",
            "splash_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/godskin_peeler_weapon_elden_ring_wiki_guide_200px.png",
            "base_stats": [
                {"level": "1", "hp": 396, "atk": 70, "def": 45, "fp": 70, "stamina": 105, "poise": 10, "vigor": 11, "mind": 9, "endurance": 14, "strength": 12, "dexterity": 16, "intelligence": 9, "faith": 8, "arcane": 14},
                {"level": "30", "hp": 780, "atk": 160, "def": 70, "fp": 80, "stamina": 115, "poise": 20, "vigor": 24, "mind": 11, "endurance": 17, "strength": 14, "dexterity": 25, "intelligence": 9, "faith": 8, "arcane": 22},
                {"level": "60", "hp": 1300, "atk": 290, "def": 98, "fp": 95, "stamina": 125, "poise": 35, "vigor": 37, "mind": 13, "endurance": 22, "strength": 16, "dexterity": 38, "intelligence": 9, "faith": 8, "arcane": 36},
                {"level": "90", "hp": 1620, "atk": 440, "def": 120, "fp": 110, "stamina": 135, "poise": 48, "vigor": 48, "mind": 15, "endurance": 25, "strength": 18, "dexterity": 50, "intelligence": 9, "faith": 8, "arcane": 48},
                {"level": "120", "hp": 1820, "atk": 610, "def": 135, "fp": 130, "stamina": 142, "poise": 60, "vigor": 56, "mind": 18, "endurance": 28, "strength": 18, "dexterity": 60, "intelligence": 9, "faith": 8, "arcane": 62},
                {"level": "150", "hp": 1900, "atk": 750, "def": 148, "fp": 150, "stamina": 150, "poise": 72, "vigor": 60, "mind": 20, "endurance": 30, "strength": 18, "dexterity": 70, "intelligence": 9, "faith": 8, "arcane": 80}
            ],
            "special_ascension_stat": {
                "stat_name": "出血流派极效机制",
                "values": {
                    "出血爆发": "15% 目标最大生命值 + 100~200 真实伤害",
                    "多段连斩": "双持双头剑跳劈单次打出 4 段判定，瞬叠 400+ 出血值",
                    "鲜血欢愉": "触发出血瞬间获得 20% 极效物理攻击力提升，持续 20 秒"
                }
            },
            "ascension_materials": [
                {"tier": "前期·鲜血指头试炼", "items": "白面具支线 | 纯血骑士勋章 | 鲜血君王立誓"},
                {"tier": "中期·亚坛高原与格密尔火山", "items": "切腹战灰 | 神皮剥制剑 | 丧色石[7]"},
                {"tier": "后期·巨人山顶安歇教堂", "items": "尸山血海 +10 | 白面具头盔 | 鲜血君王追忆"}
            ],
            "talents": [
                {"name": "核心战灰·切腹 (Seppuku)", "type": "NORMAL_ATTACK", "description": "将兵刃刺入自身腹部附上鲜血，以少量生命为代价，使武器增加 30 点基础物攻并暴增 84 点出血累积，持续 60 秒。", "scaling": "自损少量 HP，每次攻击附带极高额外出血"},
                {"name": "专属战技·尸横遍野 (Corpse Piler)", "type": "ELEMENTAL_SKILL", "description": "以血焰缠绕武士刀挥舞连续拔刀斩，展开最多 6 连击的巨大血焰刀光，刀刃与刀气双重命中瞬爆出血！", "scaling": "消耗 17+9+9 点 FP，全额命中百分百引爆大出血"},
                {"name": "双跳劈·血旋龙卷风", "type": "ELEMENTAL_BURST", "description": "双持神秘质变双头剑滞空下劈，瞬间打出 4 段切割判定，无论是推图群怪还是巨型 Boss 均直接融化！", "scaling": "空中 4 段判定，伤害与出血累积翻倍"},
                {"name": "核心天赋·鲜血君王之宴", "type": "PASSIVE_TALENT", "description": "当视野内任何单位（含自身）陷入出血状态时，自身攻击力立刻暴增 20%，且该增益可与白面具 10% 增益完全乘算叠加！", "scaling": "攻击力提升 1.2 × 1.1 = 1.32 倍！"}
            ],
            "passives": [
                {"name": "感应致死", "desc": "感应属性每提高 10 点，武器自带与质变附带的异常状态累积效率提升 12%。"},
                {"name": "疾风连击", "desc": "连续命中时触发攻击力阶梯提升（配合腐败翼剑徽章与米莉森义手最高 +24% 攻击力）。"},
                {"name": "血焰灼烧", "desc": "血焰攻击命中敌人后，持续 2 秒造成延时出血累积，阻断敌人韧性自然恢复。"}
            ],
            "constellations": [
                {"c": 1, "name": "鲜血初拥·血指契约", "desc": "在利耶尼亚获得纯血骑士勋章，提早进入蒙格温王朝提款刷魂。"},
                {"c": 2, "name": "切腹双持解放", "desc": "左右手武器均附上切腹战灰，跳劈出血效率翻倍。"},
                {"c": 3, "name": "白面具与欢愉共振", "desc": "佩戴白面具与鲜血君王的欢愉，出血触发后获得 32% 纯物理净增伤！"},
                {"c": 4, "name": "千刀万剐·双头剑成型", "desc": "神皮剥制剑神秘质变强化至 +25，单次跳劈伤害突破 3500+！"},
                {"c": 5, "name": "尸山血海满强化", "desc": "尸山血海达到 +10，在中距离利用尸横遍野安全收割首领。"},
                {"c": 6, "name": "蒙格温王朝血神降临", "desc": "感应达到 80 软上限，交界地任何非免疫出血 Boss 均在 10 秒内被抽干血条！"}
            ],
            "special_mechanics": {
                "rotation": "战前双切腹（左手切腹收刀 -> 右手切腹）-> 触发鲜血君王欢愉+白面具 32% 增攻 -> 奔跑跳跃下劈 4 刀瞬爆出血 -> 接尸横遍野处决！"
            },
            "recommendations": {
                "weapons": {"bis": "神皮剥制剑 (神秘切腹) + 尸山血海 +10", "alternative_5s": "艾雷诺拉双头刀 / 逆刺 / 剥尸曲剑", "catalyst": "龙飨印记"},
                "artifacts": {"bis_set": "鲜血君王欢愉 + 腐败翼剑徽章 + 米莉森义手 + 钩爪护符", "alt_set": "白面具 (出血增伤10%) + 猛禽黑羽 (跳劈增伤10%)"},
                "main_stats": {"priority": "感应 (60~80) > 灵巧 (50~70) > 生命力 (60) > 耐力 (25~30) > 力量 (满足拿武器即可)"}
            },
            "version": "1.14"
        },
        {
            "name": "褪色者·纯智法皇奥术师 (Pure Intelligence Sorcerer)",
            "title": "卡利亚月之女王与起源天文学家",
            "rarity": 5,
            "element": "智力法术",
            "weapon_type": "辉石杖/特大剑",
            "avatar_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/dark_moon_greatsword_weapon_elden_ring_wiki_guide_200px.png",
            "splash_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/carian_regal_scepter_weapon_elden_ring_wiki_guide_200px.png",
            "base_stats": [
                {"level": "1", "hp": 380, "atk": 55, "def": 42, "fp": 95, "stamina": 90, "poise": 8, "vigor": 10, "mind": 15, "endurance": 10, "strength": 10, "dexterity": 12, "intelligence": 18, "faith": 7, "arcane": 9},
                {"level": "30", "hp": 720, "atk": 130, "def": 65, "fp": 125, "stamina": 100, "poise": 15, "vigor": 22, "mind": 20, "endurance": 12, "strength": 12, "dexterity": 14, "intelligence": 34, "faith": 7, "arcane": 9},
                {"level": "60", "hp": 1200, "atk": 240, "def": 90, "fp": 170, "stamina": 110, "poise": 28, "vigor": 35, "mind": 26, "endurance": 15, "strength": 16, "dexterity": 16, "intelligence": 52, "faith": 7, "arcane": 9},
                {"level": "90", "hp": 1550, "atk": 380, "def": 112, "fp": 220, "stamina": 120, "poise": 40, "vigor": 45, "mind": 32, "endurance": 18, "strength": 16, "dexterity": 18, "intelligence": 68, "faith": 7, "arcane": 9},
                {"level": "120", "hp": 1750, "atk": 520, "def": 128, "fp": 270, "stamina": 130, "poise": 55, "vigor": 52, "mind": 38, "endurance": 22, "strength": 16, "dexterity": 18, "intelligence": 80, "faith": 7, "arcane": 9},
                {"level": "150", "hp": 1900, "atk": 680, "def": 140, "fp": 320, "stamina": 140, "poise": 68, "vigor": 60, "mind": 40, "endurance": 25, "strength": 16, "dexterity": 18, "intelligence": 85, "faith": 7, "arcane": 9}
            ],
            "special_ascension_stat": {
                "stat_name": "纯智法皇核心机制",
                "values": {
                    "法术加成": "卡利亚权杖 80 智力法杖加成高达 373 点",
                    "无限核爆": "蓝秘密露滴 15 秒内所有魔法消耗 0 点 FP",
                    "暗月剑气": "暗月大剑附魔后重击发射冰霜剑气，0 FP 消耗且极高削韧"
                }
            },
            "ascension_materials": [
                {"tier": "前期·驿站街遗迹与瑟濂老师", "items": "陨石杖 | 岩石球法术 | 卷轴交付"},
                {"tier": "中期·魔法学院与卡利亚城寨", "items": "满月女王追忆 | 卡利亚权杖 +10 | 菈妮暗月"},
                {"tier": "后期·格密尔火山与月光祭坛", "items": "起源魔法·彗星亚兹勒 | 毁灭流星 | 暗月大剑 +10"}
            ],
            "talents": [
                {"name": "超位起源魔法·彗星亚兹勒 (Comet Azur)", "type": "ELEMENTAL_BURST", "description": "引导交界地宇宙原初洪流，向前方持续喷射毁灭性蓝色光束巨炮，配合无限蓝露滴可直接 10 秒秒杀几乎一切首领！", "scaling": "每秒消耗 40 FP，伤害随引导时间几何级数倍增"},
                {"name": "专属战技·月光剑 (Moonlight Greatsword)", "type": "ELEMENTAL_SKILL", "description": "高举暗月大剑沐浴冰冷暗月光芒，使武器攻击力提高 65 点并附加 100 冻伤值；持续期间重击释放超远穿透剑气！", "scaling": "战技 32 FP，剑气不耗蓝，蓄力单发削韧 35 点"},
                {"name": "传奇魔法·菈妮的暗月 (Ranni's Dark Moon)", "type": "NORMAL_ATTACK", "description": "召唤一轮巨大冰冷暗月缓缓撞击敌人，打碎一切敌方法术并在命中后使敌方魔抗永久降低 10%，附加高额冻伤值。", "scaling": "消耗 62 FP，命中即施加 10% 减抗 + 冻伤 20% 增伤"},
                {"name": "辉石重炮·罗蕾塔的大弓", "type": "EXPLORATION_TALENT", "description": "具现化出纯净魔力巨弓射出穿云光箭，超长射程可在 Boss 警戒范围外实施先发制人超视距狙杀。", "scaling": "超远射程，蓄力伤害提升 40%"}
            ],
            "passives": [
                {"name": "卡利亚权杖增幅", "desc": "装备卡利亚权杖时，月亮系魔法伤害提升 10%。"},
                {"name": "冻伤碎冰", "desc": "敌人陷入冻伤状态时立即受到最大生命值 10% 伤害，并在后续 30 秒内承受全属性伤害提升 20%。"},
                {"name": "理智壁障", "desc": "智力达到 80 点时，获得高额魔法减伤与极强法术专注。"}
            ],
            "constellations": [
                {"c": 1, "name": "陨石手杖与岩石球", "desc": "前期直接白嫖陨石杖，岩石球三连发打崩一切 Boss 韧性。"},
                {"c": 2, "name": "卡利亚女王传承", "desc": "击败雷亚卢卡利亚学院满月女王，兑换卡利亚权杖。"},
                {"c": 3, "name": "亚兹勒洪流觉醒", "desc": "在火山获得彗星亚兹勒，开启无限蓝站桩激光炮时代。"},
                {"c": 4, "name": "群星菈妮誓约", "desc": "完成菈妮完整支线，在月光祭坛获得暗月大剑并缔结群星结局。"},
                {"c": 5, "name": "智力 80 登峰造极", "desc": "法术加成达到 373 顶峰，魔法师块与魔力对蝎双增伤到位。"},
                {"c": 6, "name": "法皇绝对领域", "desc": "魔法领域 (Terra Magica) 脚下画阵，阵内所有法术与暗月剑气伤害再暴增 35%！"}
            ],
            "special_mechanics": {
                "comet_oneshot": "进门前喝灵药 (蓝秘密露滴无限蓝 + 魔力破裂露滴+20%魔伤) -> 进门脚下放魔法领域 (+35%魔伤) -> 召唤大哥或骨灰吸引仇恨 -> 蓄力彗星亚兹勒持续喷射 15 秒直接秒杀！"
            },
            "recommendations": {
                "weapons": {"bis": "暗月大剑 +10 + 卡利亚权杖 +10", "alternative_5s": "名刀月隐 / 丧失杖 / 死王子杖", "catalyst": "卡利亚权杖 / 水母盾 (战技+20%伤害)"},
                "artifacts": {"bis_set": "魔法师块护符 + 魔法师球护符 + 魔力对蝎 + 葛孚雷的肖像", "alt_set": "雪魔女尖顶帽 (冰霜魔法增伤10%) + 魔法教授大衣"},
                "main_stats": {"priority": "智力 (80) > 生命力 (60) > 专注值 (38~40) > 耐力 (20~25) > 敏捷 (加到施法极速)"}
            },
            "version": "1.14"
        },
        {
            "name": "褪色者·纯力特大巨剑跳劈流 (Colossal Giant Crusher)",
            "title": "狮子斩与重击压制之王",
            "rarity": 5,
            "element": "纯物理纯力",
            "weapon_type": "特大剑/特大武器",
            "avatar_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/greatsword_weapon_elden_ring_wiki_guide_200px.png",
            "splash_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/giant-crusher_weapon_elden_ring_wiki_guide_200px.png",
            "base_stats": [
                {"level": "1", "hp": 430, "atk": 80, "def": 55, "fp": 60, "stamina": 110, "poise": 25, "vigor": 13, "mind": 8, "endurance": 15, "strength": 18, "dexterity": 10, "intelligence": 7, "faith": 8, "arcane": 8},
                {"level": "30", "hp": 850, "atk": 180, "def": 85, "fp": 70, "stamina": 125, "poise": 45, "vigor": 26, "mind": 9, "endurance": 22, "strength": 30, "dexterity": 11, "intelligence": 7, "faith": 8, "arcane": 8},
                {"level": "60", "hp": 1380, "atk": 320, "def": 115, "fp": 80, "stamina": 140, "poise": 65, "vigor": 40, "mind": 10, "endurance": 30, "strength": 45, "dexterity": 12, "intelligence": 7, "faith": 8, "arcane": 8},
                {"level": "90", "hp": 1680, "atk": 510, "def": 138, "fp": 90, "stamina": 155, "poise": 85, "vigor": 50, "mind": 11, "endurance": 38, "strength": 60, "dexterity": 12, "intelligence": 7, "faith": 8, "arcane": 8},
                {"level": "120", "hp": 1850, "atk": 690, "def": 155, "fp": 100, "stamina": 165, "poise": 105, "vigor": 58, "mind": 12, "endurance": 45, "strength": 70, "dexterity": 12, "intelligence": 7, "faith": 8, "arcane": 8},
                {"level": "150", "hp": 1900, "atk": 850, "def": 170, "fp": 110, "stamina": 175, "poise": 120, "vigor": 60, "mind": 13, "endurance": 50, "strength": 80, "dexterity": 12, "intelligence": 7, "faith": 8, "arcane": 8}
            ],
            "special_ascension_stat": {
                "stat_name": "纯力重击核心特权",
                "values": {
                    "双手持握": "力气数值直接享受 1.5 倍增益 (54力气等同于81力气)",
                    "狮子斩强霸体": "起跳下砸全程处于无限韧性霸体判定，免疫击飞打断",
                    "单发失衡": "一次狮子斩打出 42 点削韧，两次必定使任何 Boss 跪地失衡处决！"
                }
            },
            "ascension_materials": [
                {"tier": "盖利德大商队", "items": "巨剑 (Guts Greatsword) | 强化石"},
                {"tier": "亚坛高原城边村", "items": "巨人粉碎短剑 (Giant-Crusher) | 狮子斩战灰"},
                {"tier": "王城地下大山羊", "items": "大山羊套装 | 龙徽大盾护符 | 丧色石"}
            ],
            "talents": [
                {"name": "核心战灰·狮子斩 (Lion's Claw)", "type": "ELEMENTAL_SKILL", "description": "向前翻腾凌空跃起，将重达千钧的特大剑重重砸向地面，造成毁天灭地的范围震荡与巨量削韧，施展期间自身完全霸体！", "scaling": "消耗 20 点 FP，削韧 42 点，造成 380% 武器攻击伤害"},
                {"name": "战狂战吼·战吼与夸耀咆哮", "type": "ELEMENTAL_BURST", "description": "仰天发出狂暴怒吼，提升自身攻击力 15% 并将重击动作替换为狂暴突进重砸！", "scaling": "消耗 16 点 FP，持续 40 秒强化重击模组"},
                {"name": "崩山重击·特大跳劈", "type": "NORMAL_ATTACK", "description": "双持巨剑跃入半空借重力势能下劈，单次跳劈造成极强冲击力，直接将小型敌人拍入泥土！", "scaling": "跳劈倍率 165%，失衡积蓄极高"},
                {"name": "处决一击·内脏暴击", "type": "EXPLORATION_TALENT", "description": "敌人被打至失衡跪地发出清脆音效时，贴身按普通攻击打出致命处决，造成超高穿透物理真伤！", "scaling": "处决倍率高达 450%"}
            ],
            "passives": [
                {"name": "钢铁之躯", "desc": "穿戴大山羊套装时强韧度突破 100+，普通轻中型攻击完全无法造成自身硬直。"},
                {"name": "重击震荡", "desc": "特大武器下砸未直接命中时，地面的冲击震波亦能造成 25% 伤害与打断。"},
                {"name": "无情处决", "desc": "处决成功后立即恢复 15% 最大精力量并进入 1 秒无敌帧。"}
            ],
            "constellations": [
                {"c": 1, "name": "巨剑入手·烙印勇士", "desc": "在盖利德野狗守护的大马车箱中白嫖巨剑，厚重质变开启。"},
                {"c": 2, "name": "狮子斩装配", "desc": "盖利德要塞击败狮子混种夺得狮子斩，告别前后摇挨打。"},
                {"c": 3, "name": "双手 54 力气阈值", "desc": "达到 54 力气，双手持握自动达到 81 力气软上限，伤害飙升。"},
                {"c": 4, "name": "大山羊百韧护体", "desc": "击败大角特拉格斯获得大山羊套装与大山羊护符，强韧度无人能敌。"},
                {"c": 5, "name": "巨人粉碎巨锤神化", "desc": "武器强化至 +25，单次战技伤害破 3000，Boss 两刀一跪。"},
                {"c": 6, "name": "交界地压制之神", "desc": "狮子斩复读无脑通关一周目至八周目，纯力量的美学！"}
            ],
            "special_mechanics": {
                "loop": "进门前吼叫增攻 -> 骑脸 Boss 连续施展 2 次狮子斩（霸体硬顶 Boss 招式）-> Boss 必定跪地失衡 -> 掏出慈悲短剑或巨剑正脸处决 -> 起身继续狮子斩循环！"
            },
            "recommendations": {
                "weapons": {"bis": "巨剑 +25 (厚重质变·狮子斩) / 巨人粉碎短剑", "alternative_5s": "碎星大剑 / 遗迹大剑 / 玛利喀斯的黑剑"},
                "artifacts": {"bis_set": "亚历山大碎片 + 龙徽大盾护符 + 大山羊护符 + 绿龟护符", "alt_set": "大山羊重装铠甲套 (强韧度第一)"},
                "main_stats": {"priority": "力气 (66~80) > 生命力 (60) > 耐力 (50穿重甲不超重) > 力量满足即可"}
            },
            "version": "1.14"
        },
        {
            "name": "褪色者·智敏魔剑士 (Intelligence / Dexterity Spellblade)",
            "title": "名刀月隐与居合拔刀见切大师",
            "rarity": 5,
            "element": "智敏魔武",
            "weapon_type": "武士刀/魔剑",
            "avatar_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/moonveil_weapon_elden_ring_wiki_guide_200px.png",
            "splash_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/sorcerer_rogiers_set_elden_ring_wiki_guide_200px.png",
            "base_stats": [
                {"level": "1", "hp": 400, "atk": 68, "def": 48, "fp": 85, "stamina": 100, "poise": 12, "vigor": 11, "mind": 12, "endurance": 13, "strength": 12, "dexterity": 15, "intelligence": 16, "faith": 8, "arcane": 9},
                {"level": "30", "hp": 760, "atk": 155, "def": 72, "fp": 110, "stamina": 112, "poise": 22, "vigor": 24, "mind": 16, "endurance": 16, "strength": 12, "dexterity": 22, "intelligence": 26, "faith": 8, "arcane": 9},
                {"level": "60", "hp": 1260, "atk": 280, "def": 98, "fp": 140, "stamina": 124, "poise": 38, "vigor": 36, "mind": 20, "endurance": 20, "strength": 12, "dexterity": 32, "intelligence": 40, "faith": 8, "arcane": 9},
                {"level": "90", "hp": 1600, "atk": 430, "def": 120, "fp": 175, "stamina": 135, "poise": 50, "vigor": 48, "mind": 25, "endurance": 24, "strength": 12, "dexterity": 42, "intelligence": 55, "faith": 8, "arcane": 9},
                {"level": "120", "hp": 1800, "atk": 590, "def": 136, "fp": 210, "stamina": 142, "poise": 62, "vigor": 55, "mind": 30, "endurance": 26, "strength": 12, "dexterity": 50, "intelligence": 68, "faith": 8, "arcane": 9},
                {"level": "150", "hp": 1900, "atk": 730, "def": 148, "fp": 240, "stamina": 150, "poise": 75, "vigor": 60, "mind": 32, "endurance": 28, "strength": 12, "dexterity": 55, "intelligence": 80, "faith": 8, "arcane": 9}
            ],
            "special_ascension_stat": {
                "stat_name": "智敏拔刀特权",
                "values": {
                    "瞬发居合": "收刀入鞘瞬间 0.1 秒拔刀打出光芒剑气",
                    "削韧兼备": "居合重斩削韧值高达 30 点，三发必失衡",
                    "魔物双修": "近战刀刃造成物理+出血，刀气造成大范围高额魔力伤害"
                }
            },
            "ascension_materials": [
                {"tier": "盖利德盖尔坑道", "items": "熔岩土龙掉落·名刀月隐 | 强化素材"},
                {"tier": "魔法学院雷亚卢卡利亚", "items": "辉剑圆阵法术 | 罗杰尔刺剑 | 丧色石"},
                {"tier": "卡利亚庄园", "items": "卡利亚骑士剑 | 丧色古龙岩"}
            ],
            "talents": [
                {"name": "专属战技·隙间月影 (Transient Moonlight)", "type": "ELEMENTAL_SKILL", "description": "收刀入鞘摆出居合架势，输入轻攻击释放横向超宽魔力刀光，输入重攻击释放纵向破空裂地剑气，出手极快兼具极高削韧与伤害！", "scaling": "轻斩 15 FP 宽范围横扫，重斩 20 FP 超高削韧纵劈"},
                {"name": "协同法术·辉剑圆阵 (Carian Phalanx)", "type": "NORMAL_ATTACK", "description": "在头顶召唤多柄辉剑自动悬浮，发现敌人时自动飞出贯穿对手，造成 40 点极高连环削韧，配合拔刀斩直接当场跪地！", "scaling": "消耗 20 点 FP，破韧神器"},
                {"name": "暗杀奇术·黑夜彗星", "type": "ELEMENTAL_BURST", "description": "施展半透明不可见魔力彗星，敌方 AI 完全无法判定躲避，百发百中！", "scaling": "敌人不读指令闪避，绝对命中"},
                {"name": "格挡反击·卡利亚式奉还", "type": "EXPLORATION_TALENT", "description": "挥动盾牌化解敌方魔法与物理攻击，并将敌方魔法转化为三枚反伤辉剑极速射回！", "scaling": "完全吸收敌方法术并返还 3 倍反击伤害"}
            ],
            "passives": [
                {"name": "居合专注", "desc": "处于收刀架势时受到轻微攻击不解除架势。"},
                {"name": "魔导共鸣", "desc": "武器造成的魔力伤害与法术造成的魔力伤害共享魔力对蝎加成。"},
                {"name": "剑气破空", "desc": "居合刀刃与剑气贴脸同时命中时，伤害享受 1.35 倍近战补偿！"}
            ],
            "constellations": [
                {"c": 1, "name": "名刀月隐出鞘", "desc": "在盖利德盖尔坑道击败熔岩土龙获得名刀月隐。"},
                {"c": 2, "name": "卡利亚徽章减耗", "desc": "在军师伊吉处购买卡利亚徽章，隙间月影 FP 消耗降低 25%。"},
                {"c": 3, "name": "辉剑圆阵协同", "desc": "掌握辉剑圆阵，进门先挂剑阵再突刺拔刀，起手必破韧。"},
                {"c": 4, "name": "罗杰尔刺剑魔力共振", "desc": "穿戴罗杰尔套装，使所有魔力战技伤害提升 8%。"},
                {"c": 5, "name": "智敏双修 80/50 达成", "desc": "智力 80 刀气输出登顶，灵巧 50 出手速度与近战伤害拉满。"},
                {"c": 6, "name": "交界地绝影剑圣", "desc": "无论面对神皮双人组还是女武神，中距离居合重斩直接见切压制！"}
            ],
            "special_mechanics": {
                "combo": "中距离悬浮辉剑圆阵 -> 踏步向前收刀摆架势 -> 居合重击拔刀纵向剑气 -> 剑阵与月影同时命中造成 70 点超强削韧直接失衡 -> 贴脸重击处决！"
            },
            "recommendations": {
                "weapons": {"bis": "名刀月隐 +10 (Moonveil)", "alternative_5s": "暗月大剑 / 罗杰尔刺剑 / 冰壳斧", "catalyst": "卡利亚权杖 / 丧失杖"},
                "artifacts": {"bis_set": "亚历山大碎片 + 魔力对蝎 + 卡利亚徽章 + 龙徽大盾护符", "alt_set": "魔法剑士套装 (强化魔力战技 8%)"},
                "main_stats": {"priority": "智力 (60~80) > 灵巧 (40~50) > 生命力 (60) > 专注 (25) > 耐力 (25)"}
            },
            "version": "1.14"
        },
        {
            "name": "褪色者·感应龙飨狂信徒 (Arcane Dragon Communion)",
            "title": "龙心狂饮者与猩红龙雷咆哮者",
            "rarity": 5,
            "element": "感应龙飨",
            "weapon_type": "龙飨圣印记/大剑",
            "avatar_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/dragon_communion_seal_weapon_elden_ring_wiki_guide_200px.png",
            "splash_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/mohgwyns_sacred_spear_weapon_elden_ring_wiki_guide_200px.png",
            "base_stats": [
                {"level": "1", "hp": 410, "atk": 62, "def": 46, "fp": 80, "stamina": 98, "poise": 10, "vigor": 12, "mind": 11, "endurance": 12, "strength": 12, "dexterity": 12, "intelligence": 9, "faith": 15, "arcane": 16},
                {"level": "30", "hp": 780, "atk": 150, "def": 70, "fp": 105, "stamina": 110, "poise": 20, "vigor": 24, "mind": 15, "endurance": 15, "strength": 14, "dexterity": 14, "intelligence": 9, "faith": 22, "arcane": 28},
                {"level": "60", "hp": 1280, "atk": 270, "def": 95, "fp": 135, "stamina": 122, "poise": 32, "vigor": 36, "mind": 19, "endurance": 18, "strength": 16, "dexterity": 14, "intelligence": 9, "faith": 28, "arcane": 44},
                {"level": "90", "hp": 1610, "atk": 420, "def": 118, "fp": 170, "stamina": 132, "poise": 45, "vigor": 48, "mind": 24, "endurance": 20, "strength": 18, "dexterity": 14, "intelligence": 9, "faith": 30, "arcane": 60},
                {"level": "120", "hp": 1810, "atk": 580, "def": 134, "fp": 200, "stamina": 140, "poise": 58, "vigor": 55, "mind": 28, "endurance": 22, "strength": 20, "dexterity": 14, "intelligence": 9, "faith": 32, "arcane": 75},
                {"level": "150", "hp": 1900, "atk": 710, "def": 145, "fp": 230, "stamina": 148, "poise": 70, "vigor": 60, "mind": 32, "endurance": 24, "strength": 24, "dexterity": 14, "intelligence": 9, "faith": 36, "arcane": 80}
            ],
            "special_ascension_stat": {
                "stat_name": "龙飨感应核心机制",
                "values": {
                    "双重补正": "龙飨印记重量为0，受感应S级与信仰B级双重极高补正",
                    "龙吼增幅": "龙飨印记额外常驻提升 15% 龙飨祷告威力",
                    "全屏腐败": "艾格基斯的腐败单次长喷即可给 Boss 挂满全额猩红腐败"
                }
            },
            "ascension_materials": [
                {"tier": "漂流墓地边境英雄墓地", "items": "龙飨圣印记 (0重量神器)"},
                {"tier": "大龙飨教堂", "items": "飞龙亚基尔心脏 | 腐败龙艾格基斯心脏"},
                {"tier": "蒙格温王朝神庙", "items": "蒙格温圣矛 +10 | 鲜血君王追忆"}
            ],
            "talents": [
                {"name": "超位龙飨·艾格基斯的腐败 (Ekzykes's Decay)", "type": "ELEMENTAL_BURST", "description": "具现化出远古腐败巨龙首级，跃入半空向全场大范围倾泻高浓度猩红腐败云雾，直接给全屏敌人施加重度猩红腐败，按最大生命值每秒持续融化血条！", "scaling": "消耗 48 点 FP，持续扣除目标 30% 以上总生命值"},
                {"name": "破灭龙吼·波利斯之冰龙吐息", "type": "ELEMENTAL_SKILL", "description": "化出冰霜巨龙首级喷吐极寒龙息，瞬间使敌人陷入冻伤状态并打断前摇招式。", "scaling": "单发秒叠冻伤，造成 20% 易伤"},
                {"name": "王朝核爆·授血仪式 (Bloodboon Ritual)", "type": "NORMAL_ATTACK", "description": "手持蒙格温圣矛向上刺穿虚空三次，连续三次引爆全屏范围无视地形的授血狂潮，伤害随出血次数成几何级数暴涨！", "scaling": "全屏穿墙无视障碍物，三段必引爆大出血"},
                {"name": "龙爪重击·原初龙撕裂", "type": "EXPLORATION_TALENT", "description": "以巨大龙爪拍击地面，附带极强重击压制与打飞效果。", "scaling": "消耗 24 点 FP，强硬直判定"}
            ],
            "passives": [
                {"name": "真龙血脉", "desc": "龙飨祷告对非古龙类敌人造成额外 10% 真实压制伤害。"},
                {"name": "腐败蔓延", "desc": "敌人处于猩红腐败状态时，移动速度降低 20%，且其攻击力削弱 10%。"},
                {"name": "感应神恩", "desc": "感应属性提升同时大幅增加大世界装备与稀有素材掉落率 (Discovery +180)。"}
            ],
            "constellations": [
                {"c": 1, "name": "边境墓地龙印入手", "desc": "开局下墓地石剑钥匙直奔龙飨圣印记，拿到 0 重量神器。"},
                {"c": 2, "name": "大龙飨教堂圣职", "desc": "击杀飞龙与腐败龙，兑换高级龙吼吐息。"},
                {"c": 3, "name": "腐败吐息挂毒无脑流", "desc": "面对所有高难 Boss，开场一口腐败长喷，骑马绕圈即可坐看血条归零。"},
                {"c": 4, "name": "蒙格温圣矛血爆仪式", "desc": "拿到圣矛，在地下王朝或任何转角隔墙开战技直接清屏。"},
                {"c": 5, "name": "感应 80 极境", "desc": "祷告加成突破 360+，龙飨吐息伤害达万级单发。"},
                {"c": 6, "name": "古龙霸主化身", "desc": "兼具火/冰/雷/腐败四大属性龙吼，随心所欲克制交界地一切生灵！"}
            ],
            "special_mechanics": {
                "boss_melt": "开局召骨灰吸引 Boss 仇恨 -> 蓄力艾格基斯腐败吐息直接叠满猩红腐败 -> 切换波利斯冰息叠满冻伤 -> 掏出蒙格温圣矛隔墙或贴身连续三段授血仪式直接引爆清场！"
            },
            "recommendations": {
                "weapons": {"bis": "龙飨圣印记 +10 + 蒙格温圣矛 +10", "alternative_5s": "玛利喀斯黑剑 / 蚁刺细剑", "catalyst": "龙飨圣印记 (双持双龙印可叠加 1.15 × 1.15 = 1.32 倍加成)"},
                "artifacts": {"bis_set": "群聚信徒立誓布 + 鲜血君王欢愉 + 咆哮护符 + 龙徽大盾护符", "alt_set": "白面具 + 猛禽黑羽"},
                "main_stats": {"priority": "感应 (60~80) > 信仰 (30~45) > 生命力 (60) > 专注 (30) > 力量 (满足武器)"}
            },
            "version": "1.14"
        },
        {
            "name": "褪色者·1级无用之人全能者 (Wretch Level 1 Base)",
            "title": "一无所有与翻滚无伤战神",
            "rarity": 4,
            "element": "全能基准",
            "weapon_type": "棍棒/单手盾",
            "avatar_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/club_weapon_elden_ring_wiki_guide_200px.png",
            "splash_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/wretch_class_elden_ring_wiki_guide_200px.png",
            "base_stats": [
                {"level": "1", "hp": 414, "atk": 50, "def": 40, "fp": 78, "stamina": 96, "poise": 0, "vigor": 10, "mind": 10, "endurance": 10, "strength": 10, "dexterity": 10, "intelligence": 10, "faith": 10, "arcane": 10},
                {"level": "30", "hp": 760, "atk": 120, "def": 65, "fp": 90, "stamina": 108, "poise": 10, "vigor": 20, "mind": 12, "endurance": 15, "strength": 18, "dexterity": 15, "intelligence": 10, "faith": 10, "arcane": 10},
                {"level": "60", "hp": 1250, "atk": 230, "def": 90, "fp": 110, "stamina": 120, "poise": 20, "vigor": 35, "mind": 14, "endurance": 20, "strength": 25, "dexterity": 20, "intelligence": 10, "faith": 10, "arcane": 10},
                {"level": "90", "hp": 1550, "atk": 360, "def": 110, "fp": 130, "stamina": 130, "poise": 30, "vigor": 45, "mind": 16, "endurance": 24, "strength": 35, "dexterity": 25, "intelligence": 10, "faith": 10, "arcane": 10},
                {"level": "120", "hp": 1750, "atk": 500, "def": 125, "fp": 150, "stamina": 140, "poise": 40, "vigor": 52, "mind": 18, "endurance": 28, "strength": 45, "dexterity": 32, "intelligence": 10, "faith": 10, "arcane": 10},
                {"level": "150", "hp": 1900, "atk": 650, "def": 140, "fp": 175, "stamina": 150, "poise": 50, "vigor": 60, "mind": 20, "endurance": 32, "strength": 55, "dexterity": 40, "intelligence": 10, "faith": 10, "arcane": 10}
            ],
            "special_ascension_stat": {
                "stat_name": "无用之人特权",
                "values": {
                    "全能基板": "全属性 10 点基准，洗点没有任何废点浪费，随意转职任何流派",
                    "轻滚阈值": "裸装负重低于 30%，享受 13 帧极速翻滚无敌帧与极远位移",
                    "红羽增伤": "红羽七刃剑残血增伤 20%，大神 1 级无伤通关标配"
                }
            },
            "ascension_materials": [
                {"tier": "新手诞生", "items": "一根木棒 | 一面小皮盾 | 满腔孤勇"}
            ],
            "talents": [
                {"name": "基础战技·野蛮咆哮", "type": "NORMAL_ATTACK", "description": "发出野蛮咆哮提升自身基础攻击力 10%，重击派生为三段疯狂挥棒追击。", "scaling": "消耗 16 点 FP，大幅提升棍棒重击倍率"},
                {"name": "格挡绝技·小盾完美弹反 (Parry)", "type": "ELEMENTAL_SKILL", "description": "在敌方挥刀瞬间挥动小皮盾弹开兵刃，强制清空人型敌人韧性并造成绝对失衡处决！", "scaling": "判定窗口极宽，弹反处决造成 500% 暴击伤害"}
            ],
            "passives": [
                {"name": "轻装敏捷", "desc": "装备重量低于 30% 时，翻滚精力消耗降低 20%，位移距离提升 15%。"}
            ],
            "constellations": [
                {"c": 1, "name": "初心不灭", "desc": "一根木棒敲翻大树守卫，证明技术的含金量。"},
                {"c": 6, "name": "无伤封神", "desc": "不升一级通关交界地与幽影地，登顶艾尔登之王！"}
            ],
            "special_mechanics": {
                "guide": "适合追求最纯粹硬核动作战斗体验的大神玩家，或准备随时用泪滴幼体洗点转型其他 6 大流派的百搭底子。"
            },
            "recommendations": {
                "weapons": {"bis": "棍棒 +25 / 猎犬长牙", "alternative_5s": "任何顺手兵刃"},
                "artifacts": {"bis_set": "红羽七刃剑 + 蓝色舞娘 + 腐败翼剑徽章 + 绿色龟护符"},
                "main_stats": {"priority": "完全自定义分配，无任何预设限制"}
            },
            "version": "1.14"
        }
    ]

def get_elden_ring_weapons():
    """构建艾尔登法环 16 件交界地神兵与圣印/法杖触媒"""
    return [
        {
            "name": "亵渎圣剑 (Blasphemous Blade)",
            "type": "大剑",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/blasphemous_blade_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物攻 121 / 火攻 78 (合计 199)",
                "+3": "物攻 175 / 火攻 112 (合计 287)",
                "+6": "物攻 228 / 火攻 146 (合计 374)",
                "+9": "物攻 282 / 火攻 180 (合计 462)",
                "+10": "物攻 296 / 火攻 191 (合计 487，补正后单发面板突破 850+！)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 C | 灵巧 C | 信仰 B (火焰极高补正)",
                "requirements": "力气 22 | 灵巧 15 | 信仰 21"
            },
            "refinements": {
                "skill_name": "专属战技·掠夺之火 (Taker's Flames)",
                "fp_cost": "23 FP",
                "effect": "高举大剑燃起亵渎烈火砸向地面，向前方发出超宽超长距离熔岩火柱。造成毁灭性火属性打击并强行击翻敌人。命中即恢复 4% HP + 40 点生命值；佩戴击杀敌人常驻恢复 10% HP + 100 点生命值！"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器 (+0 ~ +10)",
                "catalyst_list": "丧色锻造石 [1] ~ [9] 各 1 颗 + 古龙岩丧色锻造石 1 颗 + 亵渎君王追忆换取"
            },
            "version": "1.14"
        },
        {
            "name": "尸山血海 (Rivers of Blood)",
            "type": "刀",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/rivers_of_blood_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物攻 76 / 火攻 76 (合计 152，出血 30)",
                "+5": "物攻 130 / 火攻 130 (合计 260，出血 42)",
                "+10": "物攻 186 / 火攻 186 (合计 372，出血 52，感应补正后实战单刀出血 78+)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 E | 灵巧 B | 感应 B (出血与火伤双加成)",
                "requirements": "力气 12 | 灵巧 18 | 感应 20"
            },
            "refinements": {
                "skill_name": "专属战技·尸横遍野 (Corpse Piler)",
                "fp_cost": "17 (连续追加 9 + 9) FP",
                "effect": "引动血焰进行极速拔刀多段斩击。第一段二连斩 -> 第二段三连斩 -> 第三段终结下劈，斩击附带超长血焰刀气，贴身刀刃与刀气命中可瞬间引爆大出血！"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "巨人山顶安歇教堂击败血指老翁掉落"
            },
            "version": "1.14"
        },
        {
            "name": "暗月大剑 (Dark Moon Greatsword)",
            "type": "大剑",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/dark_moon_greatsword_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物攻 82 / 魔力 98 (合计 180，冻伤 55)",
                "+5": "物攻 142 / 魔力 170 (合计 312，冻伤 55)",
                "+10": "物攻 200 / 魔力 240 (合计 440，附魔后重击单发剑气伤害轻松突破 1800+！)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 D | 灵巧 D | 智力 B (魔力极高加成)",
                "requirements": "力气 16 | 灵巧 11 | 智力 38"
            },
            "refinements": {
                "skill_name": "专属战技·月光剑 (Moonlight Greatsword)",
                "fp_cost": "32 FP",
                "effect": "高举大剑沐浴冰冷暗月光芒，使武器魔力攻击力提升 65 点，附带冻伤值暴增至 100。在 60 秒持续时间内，蓄力重击可发射穿透性超强月光剑气，剑气不耗蓝且单发削韧高达 35 点！"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "完成群星魔女菈妮专属誓约支线，在月光祭坛大维克教堂地底赠予暗月戒指获得"
            },
            "version": "1.14"
        },
        {
            "name": "名刀月隐 (Moonveil)",
            "type": "刀",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/moonveil_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物攻 73 / 魔力 87 (合计 160，出血 50)",
                "+5": "物攻 125 / 魔力 150 (合计 275，出血 50)",
                "+10": "物攻 178 / 魔力 213 (合计 391，出血 50，居合重斩实战面板近千)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 E | 灵巧 B | 智力 B (智敏双修第一神器)",
                "requirements": "力气 12 | 灵巧 18 | 智力 23"
            },
            "refinements": {
                "skill_name": "专属战技·隙间月影 (Transient Moonlight)",
                "fp_cost": "轻击 15 FP / 重击 20 FP",
                "effect": "收刀入鞘摆出居合拔刀架势。轻击拔刀释放宽幅横向光波；重击拔刀释放极速纵向破空光刀，刀气兼具极远距离与 30 点极高削韧，三次居合必使首领失衡！"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "盖利德盖尔坑道击败熔岩土龙掉落"
            },
            "version": "1.14"
        },
        {
            "name": "巨剑·厚重质变 (Guts Greatsword)",
            "type": "特大剑",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/greatsword_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物理攻击 164",
                "+10": "物理攻击 250",
                "+20": "物理攻击 310",
                "+25 (厚重)": "基础物理 345 (力气 A 补正，80 力气双手持握面板突破 930+ 纯物理攻击！)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+25满级)",
                "ratings": "力气 A (厚重质变) | 灵巧 D",
                "requirements": "力气 31 | 灵巧 12"
            },
            "refinements": {
                "skill_name": "自由装配战灰·狮子斩 (Lion's Claw)",
                "fp_cost": "20 FP",
                "effect": "翻腾下砸造成 380% 攻击伤害与 42 点削韧，施放全过程获得无限强韧度霸体，免疫一切普通攻击硬直打断！"
            },
            "ascension_materials": {
                "type": "普通锻造石强化武器 (+0 ~ +25)",
                "catalyst_list": "锻造石 [1] ~ [8] 各 12 颗 + 古龙岩锻造石 1 颗"
            },
            "version": "1.14"
        },
        {
            "name": "卡利亚权杖 (Carian Regal Scepter)",
            "type": "辉石杖",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/carian_regal_scepter_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "魔法加成 162 (智力要求 60)",
                "+5": "魔法加成 255",
                "+10": "魔法加成 373 (80 智力下综合加成最高的常规无负面法杖)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 E | 灵巧 E | 智力 S (满级最高智力补正)",
                "requirements": "力气 8 | 灵巧 10 | 智力 60"
            },
            "refinements": {
                "skill_name": "专属特效与战技·旋转武器",
                "fp_cost": "常驻生效 / 战技 15 FP",
                "effect": "常驻使所有满月类魔法（菈妮暗月、蕾娜菈满月）造成的伤害提升 10%。施放战技可使权杖在身前高速自转，持续切割逼近的敌人并造成高额削韧。"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "击败满月女王蕾娜菈，使用满月女王追忆在圆桌厅堂兑换"
            },
            "version": "1.14"
        },
        {
            "name": "龙飨圣印记 (Dragon Communion Seal)",
            "type": "圣印记",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/dragon_communion_seal_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "祈祷加成 150 (重量 0.0)",
                "+5": "祈祷加成 260",
                "+10": "祈祷加成 387 (45 信仰 + 80 感应下拥有全游戏最高梯队的祈祷加成！)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "信仰 B | 感应 S (极高感应补正与异常放大)",
                "requirements": "信仰 10 | 感应 10"
            },
            "refinements": {
                "skill_name": "专属特效·龙飨威能加持",
                "fp_cost": "常驻生效",
                "effect": "装备此圣印记施展所有龙飨祷告（腐败吐息、冰龙息、辉石龙息、亚基尔龙焰等）时，伤害直接提升 15%！左右手各持一个可叠加 32% 增伤。"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "新手出生地漂流墓地插石剑钥匙进入边境英雄墓地拾取"
            },
            "version": "1.14"
        },
        {
            "name": "蒙格温圣矛 (Mohgwyn's Sacred Spear)",
            "type": "大矛",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/mohgwyns_sacred_spear_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物攻 96 / 火攻 62 (合计 158，出血 33)",
                "+10": "物攻 235 / 火攻 151 (合计 386，出血 73，战技范围血爆秒杀一切)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 C | 灵巧 D | 感应 B",
                "requirements": "力气 24 | 灵巧 14 | 感应 27"
            },
            "refinements": {
                "skill_name": "专属战技·授血仪式 (Bloodboon Ritual)",
                "fp_cost": "20 (连续追加 20 + 20) FP",
                "effect": "高举圣矛刺向虚空，连续三次引爆无视墙壁与障碍物的全屏巨大血焰血爆，每段引爆附带极高火属性与超高出血判定，群怪与大体型 Boss 瞬间暴毙！"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "蒙格温王朝击败鲜血君王蒙格兑换"
            },
            "version": "1.14"
        },
        {
            "name": "玛莲妮亚的义手刀 (Hand of Malenia)",
            "type": "刀",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/hand_of_malenia_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物理攻击 115 (出血 50)",
                "+10": "物理攻击 281 (出血 50，灵巧 B 补正，全刀类中最长攻击距离)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 E | 灵巧 B (纯敏捷顶级长刀)",
                "requirements": "力气 16 | 灵巧 48"
            },
            "refinements": {
                "skill_name": "专属战技·水鸟乱舞 (Waterfowl Dance)",
                "fp_cost": "12 (追加 9 + 9) FP",
                "effect": "跃入空中悬停后连续施展三段疾风骤雨般的超高速连斩剑刃风暴，不仅斩击判定极密且能轻易压制人型 Boss，连段全中伤害数千！"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "击败圣树腐败女神玛莲妮亚兑换"
            },
            "version": "1.14"
        },
        {
            "name": "猎犬长牙 (Bloodhound's Fang)",
            "type": "大曲剑",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/bloodhounds_fang_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物理攻击 141 (出血 55)",
                "+10": "物理攻击 345 (出血 55，力 C 灵 B，附带跳劈 10% 额外隐性加成！)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "力气 C | 灵巧 B",
                "requirements": "力气 18 | 灵巧 17"
            },
            "refinements": {
                "skill_name": "专属战技·猎犬剑技 (Bloodhound's Finesse)",
                "fp_cost": "8 (追加 12) FP",
                "effect": "向上跃起施展强力上挑后借助后坐力后空翻拉开距离；后空翻途中按重击可瞬间隐身突进打出终结重斩，全程附带极高无敌帧！"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "宁姆格福无主猎犬封印监牢击败猎犬骑士达瑞威尔掉落 (开局保送通关神兵)"
            },
            "version": "1.14"
        },
        {
            "name": "黄金树圣印记 (Erdtree Seal)",
            "type": "圣印记",
            "rarity": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/erdtree_seal_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "祈祷加成 160 (重量 0.0)",
                "+10": "祈祷加成 353 (80 纯信仰下最高加成无负面圣印记)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+10满级)",
                "ratings": "信仰 S (纯信仰最高补正)",
                "requirements": "信仰 40"
            },
            "refinements": {
                "skill_name": "纯粹黄金树祈祷加持",
                "fp_cost": "常驻生效",
                "effect": "重量完全为 0，80 纯信仰下治愈类祷告（如黄金树恩惠、王之治愈）与攻击性祷告（黄金树立誓、古龙雷击）收益最大化。"
            },
            "ascension_materials": {
                "type": "丧色锻造石强化武器",
                "catalyst_list": "牢狱教堂外牢房内拾取"
            },
            "version": "1.14"
        },
        {
            "name": "神皮剥制剑·神秘质变 (Godskin Peeler)",
            "type": "双头剑",
            "rarity": 4,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/godskin_peeler_weapon_elden_ring_wiki_guide_200px.png",
            "base_atk_curve": {
                "+0": "物理攻击 121",
                "+25 (神秘)": "物理攻击 254 (感应 A 补正，附带出血 120，双持跳劈 4 段判定瞬爆出血)"
            },
            "sub_stat": {
                "stat_name": "属性补正等级 (+25满级)",
                "ratings": "力气 D | 灵巧 D | 感应 A",
                "requirements": "力气 17 | 灵巧 22"
            },
            "refinements": {
                "skill_name": "自由装配战灰·黑焰龙卷 / 切腹",
                "fp_cost": "20 FP",
                "effect": "黑焰龙卷旋转产生多段百分比生命值灼烧火焰；装配切腹后单次跳劈直接积累 400+ 出血值。"
            },
            "ascension_materials": {
                "type": "普通锻造石强化武器",
                "catalyst_list": "阿尔特高原风车村击败神皮贵族掉落"
            },
            "version": "1.14"
        }
    ]

def get_elden_ring_artifacts():
    """构建艾尔登法环 6 大传奇护符与防具构筑套装体系"""
    return [
        {
            "name": "亚历山大与战技连击护符组 (Warrior Jar & Successive Attacks)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/shard_of_alexander_talisman_elden_ring_wiki_guide_200px.png",
            "two_piece_bonus": "【亚历山大碎片核心】：所有武器战灰与专属战技造成的伤害直接提高 15%！",
            "four_piece_bonus": "【腐败翼剑与米莉森义手共鸣】：连续命中时物理攻击力阶梯提升至最高 +24%，且敏捷属性额外常驻 +5 点！",
            "pieces": [
                {"slot": "护符位1", "name": "亚历山大的碎片 (Shard of Alexander)", "main_stat_rule": "武器战技伤害提升 15%"},
                {"slot": "护符位2", "name": "腐败翼剑徽章 (Rotten Winged Sword Insignia)", "main_stat_rule": "连续攻击攻击力阶梯提升 (6% -> 8% -> 13%)"},
                {"slot": "护符位3", "name": "米莉森的义手 (Millicent's Prosthesis)", "main_stat_rule": "灵巧 +5 | 连续攻击力提升 (4% -> 6% -> 11%)"},
                {"slot": "护符位4", "name": "钩爪护符 (Claw Talisman)", "main_stat_rule": "跳跃攻击 (跳劈) 伤害直接提升 15%"}
            ],
            "rules_reference": {
                "type": "战技输出流终极构筑",
                "recommended_for": "亵渎圣剑、尸山血海、名刀月隐、双头剑跳劈、巨剑狮子斩"
            },
            "version": "1.14"
        },
        {
            "name": "龙徽大盾与全境生存护符组 (Dragoncrest & Absolute Defense)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/dragoncrest_greatshield_talisman_elden_ring_wiki_guide_200px.png",
            "two_piece_bonus": "【龙徽大盾减伤】：物理减伤率极大幅提升 20%（在 PVP 中为 5%）！",
            "four_piece_bonus": "【金刚不坏防御体系】：物理减伤 +20%，全魔力/火/雷/圣属性减伤率额外提升 +8%，最大生命值提升 8%，强韧度提高 33%！",
            "pieces": [
                {"slot": "护符位1", "name": "龙徽大盾护符 (Dragoncrest Greatshield Talisman)", "main_stat_rule": "物理减伤率直接 +20%"},
                {"slot": "护符位2", "name": "珍珠龙徽护符 +2 (Pearldrake Talisman +2)", "main_stat_rule": "全非物理属性减伤率 +8%"},
                {"slot": "护符位3", "name": "红琥珀链坠 +2 (Crimson Amber Medallion +2)", "main_stat_rule": "最大生命值上限 +8%"},
                {"slot": "护符位4", "name": "大山羊护符 (Bull-Goat's Talisman)", "main_stat_rule": "强韧度 (Poise) 直接提升 33%"}
            ],
            "rules_reference": {
                "type": "高难防暴毙与容错构筑",
                "recommended_for": "对抗女武神、黑剑玛利喀斯、拉达冈与艾尔登之兽高伤 Boss"
            },
            "version": "1.14"
        },
        {
            "name": "卡利亚法皇奥术护符组 (Sorcery Potency & Fast Casting)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/graven-mass_talisman_elden_ring_wiki_guide_200px.png",
            "two_piece_bonus": "【魔法师块奥术共振】：所有魔法造成的伤害提升 8%，与魔法师球护符同时佩戴可乘算提升 12.3%！",
            "four_piece_bonus": "【极速法皇炮台】：魔法增伤 12.3%，魔力属性伤害额外提升 12%，缩短施法前摇至 70 敏捷极速上限，蓄力魔法伤害再提升 15%！",
            "pieces": [
                {"slot": "护符位1", "name": "魔法师块护符 (Graven-Mass Talisman)", "main_stat_rule": "魔法伤害提升 8%"},
                {"slot": "护符位2", "name": "魔力对蝎 (Magic Scorpion Charm)", "main_stat_rule": "魔力攻击力提升 12% (物理承伤增加 10%)"},
                {"slot": "护符位3", "name": "拉达冈的肖像 (Radagon Icon)", "main_stat_rule": "虚拟增加 30 点灵巧，大幅缩短施法咏唱时间"},
                {"slot": "护符位4", "name": "葛孚雷的肖像 (Godfrey Icon)", "main_stat_rule": "蓄力魔法、蓄力战技与蓄力祷告伤害提升 15%"}
            ],
            "rules_reference": {
                "type": "纯智法师与暗月大剑毕业护符",
                "recommended_for": "彗星亚兹勒、暗月剑气、毁灭流星、菈妮的暗月"
            },
            "version": "1.14"
        },
        {
            "name": "鲜血君王与腐败异常增伤护符组 (Blood & Rot Exultation)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/lord_of_bloods_exultation_talisman_elden_ring_wiki_guide_200px.png",
            "two_piece_bonus": "【鲜血君王的欢愉】：周围发生出血时，自身攻击力立刻提高 20%，持续 20 秒！",
            "four_piece_bonus": "【双重异常狂怒】：出血与猩红腐败触发后攻击力分别提升 20%，可同时触发叠加至 1.44 倍净物理增攻！",
            "pieces": [
                {"slot": "护符位1", "name": "鲜血君王的欢愉 (Lord of Blood's Exultation)", "main_stat_rule": "周围出血时攻击力 +20%"},
                {"slot": "护符位2", "name": "腐败眷属的欢愉 (Kindred of Rot's Exultation)", "main_stat_rule": "周围陷入中毒/腐败时攻击力 +20%"},
                {"slot": "护符位3", "name": "绿龟护符 (Green Turtle Talisman)", "main_stat_rule": "精力恢复速度 +8/s (+17.7%)"},
                {"slot": "防具核心", "name": "白面具头盔 (White Mask)", "main_stat_rule": "周围出血时攻击力额外 +10%"}
            ],
            "rules_reference": {
                "type": "双刀出血与龙飨腐败终极增伤搭配",
                "recommended_for": "尸山血海、双神皮剥制剑、逆刺、蒙格温圣矛"
            },
            "version": "1.14"
        },
        {
            "name": "绿龟与耐力循环运转护符组 (Stamina & FP Sustainability)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/green_turtle_talisman_elden_ring_wiki_guide_200px.png",
            "two_piece_bonus": "【精力急速复苏】：精力耐力条每秒恢复速度提升 17.7%（绿龟护符）。",
            "four_piece_bonus": "【战技狂轰滥炸】：战技 FP 消耗降低 25%（卡利亚徽章），生命/耐力/装备重量上限各提升 3%/9%/8%（黄金树的恩惠+2）！",
            "pieces": [
                {"slot": "护符位1", "name": "绿龟护符 (Green Turtle Talisman)", "main_stat_rule": "精力恢复速度提升 17.7%"},
                {"slot": "护符位2", "name": "卡利亚徽章 (Carian Filigreed Crest)", "main_stat_rule": "战技专注值 (FP) 消耗降低 25%"},
                {"slot": "护符位3", "name": "黄金树的恩惠 +2 (Erdtree's Favor +2)", "main_stat_rule": "HP +4% | 耐力 +9.6% | 负重上限 +8%"},
                {"slot": "护符位4", "name": "大壶众武护符 (Great-Jar's Arsenal)", "main_stat_rule": "装备重量上限直接增加 19%"}
            ],
            "rules_reference": {
                "type": "重甲重武器推图续航必备",
                "recommended_for": "狮子斩连发、名刀月隐频繁居合、大盾防守反击"
            },
            "version": "1.14"
        },
        {
            "name": "罗刹修罗狂战神威套装 (Rakshasa Armor of Ruin)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://eldenring.wiki.fextralife.com/file/Elden-Ring/rakshasa_set_elden_ring_shadow_of_the_erdtree_guide_200px.png",
            "two_piece_bonus": "【修罗刀锋】：穿戴每件罗刹防具使全身所有类型伤害直接提升 2%（2件套提升 4%）。",
            "four_piece_bonus": "【舍生忘死狂暴】：4件全套使全伤害总计提升 8%，代价为自身受到攻击承受伤害增加 8%，化身极端输出修罗战神！",
            "pieces": [
                {"slot": "头盔", "name": "罗刹头盔 (Rakshasa Helm)", "main_stat_rule": "全增伤 +2% | 物理减伤 -2%"},
                {"slot": "胸甲", "name": "罗刹铠甲 (Rakshasa Armor)", "main_stat_rule": "全增伤 +2% | 物理减伤 -2%"},
                {"slot": "臂甲", "name": "罗刹臂甲 (Rakshasa Gauntlets)", "main_stat_rule": "全增伤 +2% | 物理减伤 -2%"},
                {"slot": "腿甲", "name": "罗刹腿甲 (Rakshasa Greaves)", "main_stat_rule": "全增伤 +2% | 物理减伤 -2%"}
            ],
            "rules_reference": {
                "type": "黄金树幽影 DLC 顶级狂战防具",
                "recommended_for": "竞速速通、跳劈爆发、战技一击秒杀流"
            },
            "version": "1.14"
        }
    ]

def get_elden_ring_mechanics():
    """构建艾尔登法环 5 大底层魂系战斗机制与数学计算模型"""
    return [
        {
            "category": "削韧累积与失衡处决机制 (Poise & Stagger Mechanics)",
            "title": "武器削韧值、隐藏强韧度衰减与致命处决倍率",
            "formula": "敌人失衡判定：当前累积韧性伤害 >= 目标最大强韧度 (如玛莲妮亚 80点、拉达冈 120点)；失衡后进入 3~5 秒大硬直跪地状态，处决伤害 = 武器面板 × 处决倍率系数 × (1 - 目标防御吸收率)。",
            "parameters": {
                "poise_decay_window": "停止受击 6 秒后，敌方隐藏强韧度开始以每秒 10% 速率极速恢复；若用小刀或飞刀间隙蹭刀，可强行重置 6 秒衰减计时器！",
                "weapon_poise_damage": {
                    "特大武器重击/狮子斩": "36~42 点单次削韧 (两次必倒绝大多数 Boss)",
                    "大剑跳劈 / 居合拔刀重斩": "25~30 点单次削韧",
                    "单手剑/直剑轻击": "5~8 点单次削韧",
                    "岩石球法术 (全命中)": "37.5 点超强远程削韧",
                    "辉剑圆阵 (四剑全中)": "40 点破韧神器"
                },
                "critical_hit": "慈悲短剑拥有全游戏最高的 140 致命一击倍率，处决伤害冠绝交界地。"
            }
        },
        {
            "category": "异常状态累积与爆发机制 (Status Effects: Bleed, Frost, Rot)",
            "title": "出血真伤、冻伤减抗与猩红腐败衰减模型",
            "formula": "异常触发：每次命中累积异常值，当累计达到目标抗性阈值 (通常 150~600 点，随触发次数递增) 立即引爆对应状态。",
            "parameters": {
                "blood_loss": {
                    "effect": "出血引爆瞬间扣除目标最大生命值 15% + 100~200 点固定物理伤害 (精英/首领为 7%~10.5% 最大生命值)。",
                    "synergy": "触发瞬间激活【鲜血君王的欢愉】与【白面具】，自身攻击力提升 32%，持续 20 秒！"
                },
                "frostbite": {
                    "effect": "冻伤引爆扣除最大生命值 10% + 30 点固定伤害，并在后续 30 秒内使目标承受的所有伤害加深 20%！",
                    "reset_trick": "用任何火属性伤害攻击冻伤中的敌人，可立即解除冻伤状态，随后可立刻再次打满并引爆新一轮 10% 冻伤百分比扣血！"
                },
                "scarlet_rot": {
                    "effect": "重度猩红腐败 (如艾格基斯龙息) 每秒扣除目标最大生命值 0.33% + 13 点伤害，持续 90 秒，总计扣除约 30%~35% 总血量！"
                }
            }
        },
        {
            "category": "属性补正软硬上限法则 (Soft Caps & Scaling Formula)",
            "title": "生命力 40/60、力敏智信 50/80 阶梯收益与双手持握 1.5 倍力气",
            "formula": "双手持握实际力量 = 基础力气属性 × 1.5 (向下取整)；属性收益在突破软上限后斜率大幅减缓。",
            "parameters": {
                "two_hand_rule": "54 点力气双手持握时，系统结算为 54 × 1.5 = 81 点力气，直接跨越 80 软上限，因此纯力流派点到 54 即可达到最大性价比！",
                "vigor_caps": {
                    "1~40点": "生命值从 414 点直线暴增至 1450 点 (每点增加 30~48 点 HP，收益极高)",
                    "41~60点": "生命值从 1450 点平缓增长至 1900 点 (每点增加 15~26 点 HP，防暴毙推荐拉到 60)",
                    "61~99点": "收益断崖式跌落，39 点仅换来 200 点生命 (极度不推荐)"
                },
                "damage_caps": {
                    "20/50点": "第一、第二软上限，武器补正基础收益达标",
                    "80点": "最终黄金硬上限，智力/信仰/感应推荐点到 80"
                }
            }
        },
        {
            "category": "负重阈值与翻滚无敌帧机制 (Equip Load & I-Frames)",
            "title": "轻滚、中滚、超重惩罚与无敌帧 (I-Frames) 判定表",
            "formula": "负重比率 = 当前装备总重量 / 最大负重上限；翻滚无敌帧 (60 FPS 下)：轻滚与中滚均为 13 帧无敌，但轻滚位移更远后摇更短。",
            "parameters": {
                "light_load": {
                    "ratio": "负重比 < 30.0%",
                    "i_frames": "13 帧无敌时间 (第 1~13 帧完全免疫伤害与抓取)",
                    "recovery": "后摇极短，翻滚位移距离远，精力消耗 -20%"
                },
                "medium_load": {
                    "ratio": "30.0% <= 负重比 < 70.0% (全交界地绝大多数玩家的基准档位)",
                    "i_frames": "13 帧无敌时间",
                    "recovery": "正常后摇与位移，精力消耗标准"
                },
                "heavy_load": {
                    "ratio": "70.0% <= 负重比 < 100.0% (重滚/肥仔滚)",
                    "i_frames": "12 帧无敌时间",
                    "penalty": "后摇显著延长 50%，翻滚距离极短，精力恢复速率降低 20% (极高暴毙风险)！"
                },
                "overloaded": {
                    "ratio": "负重比 >= 100.0%",
                    "penalty": "完全无法跑步与翻滚，只能极度缓慢行走"
                }
            }
        },
        {
            "category": "防御力与减伤率双层过滤模型 (Defense & Damage Negation)",
            "title": "固定防御力与百分比减伤率的双重伤害结算公式",
            "formula": "最终承伤 = (来袭基础伤害 - 固定防御吸收阻力) × (1 - 物理/魔力减伤率%) × (1 - 护符增益减伤%)",
            "parameters": {
                "two_tier_filter": "第一层：人物属性带来的面板基础防御力对小伤害有极高抵扣，但对 Boss 上千的大伤害抵扣微弱；第二层：护甲与护符的百分比减伤率 (Damage Negation) 对高难大招起决定性减免！",
                "damage_negation_example": "若物理减伤率为 40%，配合【龙徽大盾护符】(+20% 物理减伤)，实际承伤乘区为 (1 - 0.40) × (1 - 0.20) = 0.48，即总减伤率提升至 52%！",
                "pvp_scaling_note": "龙徽大盾、对蝎护符等在 PVP 联机入侵时其减伤与增伤效果会被系统自动削减约 75%，防止数值崩坏。"
            }
        }
    ]

def sync_all_to_postgres():
    """主同步执行函数：连接 Postgres 并幂等落库"""
    print("=== 开始同步《艾尔登法环》(game_id = 1) 全量数值体系到 PostgreSQL ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    characters = get_elden_ring_characters()
    weapons = get_elden_ring_weapons()
    artifacts = get_elden_ring_artifacts()
    mechanics = get_elden_ring_mechanics()

    # 1. 写入角色流派 (game_character)
    print(f"\n[1/4] 写入艾尔登法环褪色者流派 ({len(characters)} 个)...")
    for c in characters:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version
            ) VALUES (
                1, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                title = EXCLUDED.title,
                rarity = EXCLUDED.rarity,
                element = EXCLUDED.element,
                weapon_type = EXCLUDED.weapon_type,
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
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))
    print(f"  ✓ 成功落库 {len(characters)} 个褪色者核心流派！")

    # 2. 写入武器与触媒 (game_weapon)
    print(f"\n[2/4] 写入艾尔登法环神兵与触媒 ({len(weapons)} 件)...")
    for w in weapons:
        # 标准化为 List[Dict] 以兼容后端 JPA List<Map<String, Object>> 实体反序列化
        raw_curve = w['base_atk_curve']
        if isinstance(raw_curve, dict):
            normalized_curve = [{"level": k, "atk": v} for k, v in raw_curve.items()]
        elif isinstance(raw_curve, list):
            normalized_curve = raw_curve
        else:
            normalized_curve = []

        raw_ref = w['refinements']
        if isinstance(raw_ref, dict):
            rank = raw_ref.get("skill_name") or "专属战技"
            fp = raw_ref.get("fp_cost")
            desc = f"【消耗】{fp}。{raw_ref.get('effect', '')}" if fp else raw_ref.get('effect', '')
            normalized_ref = [{"rank": rank, "desc": desc}]
        elif isinstance(raw_ref, list):
            normalized_ref = raw_ref
        else:
            normalized_ref = []

        raw_mat = w['ascension_materials']
        if isinstance(raw_mat, dict):
            normalized_mat = [{"tier": raw_mat.get("type", "强化途径"), "items": raw_mat.get("catalyst_list", "")}]
        elif isinstance(raw_mat, list):
            normalized_mat = raw_mat
        else:
            normalized_mat = []

        w_payload = {
            **w,
            'base_atk_curve': normalized_curve,
            'refinements': normalized_ref,
            'ascension_materials': normalized_mat
        }
        h = calc_hash(w_payload)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                1, %s, %s, %s, %s, %s,
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
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalized_curve),
            Json(w['sub_stat']), Json(normalized_ref), Json(normalized_mat), h, w['version']
        ))
    print(f"  ✓ 成功落库 {len(weapons)} 件神兵触媒！")

    # 3. 写入传奇护符与防具 (game_artifact_set)
    print(f"\n[3/4] 写入艾尔登法环传奇护符与防具套装 ({len(artifacts)} 套)...")
    for art in artifacts:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                1, %s, %s, %s, %s,
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
    print(f"  ✓ 成功落库 {len(artifacts)} 套传奇护符与防具！")

    # 4. 写入战斗机制与公式 (game_mechanic_rule)
    print(f"\n[4/4] 写入艾尔登法环底层战斗机制与公式 ({len(mechanics)} 条)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                1, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))
    print(f"  ✓ 成功落库 {len(mechanics)} 项底层战斗机制！")

    conn.commit()
    conn.close()
    print("\n=== 《艾尔登法环》全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_all_to_postgres()
