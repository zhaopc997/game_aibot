"""
TFT & Golden Spatula (金铲铲之战 / 云顶之弈) Full Comprehensive Data Ingestion Module
Covers all core game attributes:
1. 英雄 (Champions): 63 S13 champions with 1/2/3-star scaling, skills, traits, BiS items
2. 装备 (Items): Components, Standard craftables, Radiant items, Ornn artifacts, Emblems
3. 羁绊 (Traits): 38 traits with tier thresholds and specific scaling effects
4. 强化符文 (Augments): Silver, Gold, Prismatic, and Hero Augments
5. 特殊机制 (Special Mechanics): The Anomaly (异常突变), Portals, Pool Sizes, Odds, Economy
6. 阵容 (Meta Team Comps): S-Tier & A-Tier lineups with comp codes, BiS items, and leveling tempos
"""

import json
import os
import re
import urllib.request
from ..common.db import (
    get_connection,
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

CACHE_FILE = '/tmp/tft_zh_cn.json'
SOURCE_URL = 'https://raw.communitydragon.org/latest/cdragon/tft/zh_cn.json'


def clean_desc(desc: str) -> str:
    if not desc:
        return ''
    cleaned = re.sub(r'<[^>]+>', '', desc)
    cleaned = re.sub(r'%i:[^%]+%', '', cleaned)
    cleaned = re.sub(r'@[^@]+@', '', cleaned)
    return cleaned.strip()


def load_tft_data():
    if not os.path.exists(CACHE_FILE):
        print(f'[TFT] Downloading {SOURCE_URL} ...')
        urllib.request.urlretrieve(SOURCE_URL, CACHE_FILE)
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# Curated BiS items mapping for key champions
CHAMPION_BIS = {
    '凯特琳': '朔极之矛 + 无尽之刃 + 最后的轻语 / 巨人捕手',
    '蔚': '斯特拉克的挑战护手 + 泰坦的坚决 + 正义之手',
    '洛里斯': '狂徒铠甲 + 棘刺背心 + 巨龙之爪',
    '乐芙兰': '朔极之矛 + 灭世者的死亡之帽 + 珠光护手',
    '玛尔扎哈': '斯塔缇克电刃 + 莫雷洛秘典 + 朔极之矛',
    '安蓓萨': '泰坦的坚决 + 饮血剑 + 夜之锋刃',
    '德莱文': '鬼索的狂暴之刃 + 无尽之刃 + 最后的轻语',
    '金克丝': '鬼索的狂暴之刃 + 巨人捕手 + 无尽之刃',
    '艾克': '日炎斗篷 + 泰坦的坚决 + 正义之手',
    '爆爆': '朔极之矛 + 珠光护手 + 纳什之牙',
    '蔚奥莱': '泰坦的坚决 + 饮血剑 + 正义之手',
    '范德尔': '狂徒铠甲 + 日炎斗篷 + 救赎',
    '希尔科': '朔极之矛 + 珠光护手 + 纳什之牙',
    '蒙多医生': '狂徒铠甲 + 棘刺背心 + 坚定之心',
    '塞薇卡': '斯特拉克的挑战护手 + 泰坦的坚决 + 饮血剑',
    '杰斯': '泰坦的坚决 + 饮血剑 + 正义之手 / 无尽之刃',
    '兰博': '日炎斗篷 + 离子火花 + 狂徒铠甲',
    '黑默丁格': '朔极之矛 + 大天使之杖 + 珠光护手',
    '莫德凯撒': '狂徒铠甲 + 巨龙之爪 + 棘刺背心',
    '卡西奥佩娅': '鬼索的狂暴之刃 + 大天使之杖 + 科技枪',
    '麦迪': '无尽之刃 + 最后的轻语 + 朔极之矛',
    '芮尔': '离子火花 + 石像鬼石板甲 + 日炎斗篷'
}

CURATED_EQUIPMENT = [
    # 基础散件
    {'name': '暴风大剑 (B.F. Sword)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+10 攻击力', 'sub_stat': '基础物理散件', 'refine': '提供基础攻击力，用于合成无尽之刃、最后的轻语、饮血剑、青龙刀等。'},
    {'name': '反曲之弓 (Recurve Bow)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+10% 攻击速度', 'sub_stat': '基础攻速散件', 'refine': '提供攻击速度加成，用于合成羊刀、电刀、红霸符、轻语等。'},
    {'name': '无用大棒 (Needlessly Large Rod)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+10 法术强度', 'sub_stat': '基础法系散件', 'refine': '提供法术强度，用于合成大帽、法爆、羊刀、离子火花、鬼书等。'},
    {'name': '女神之泪 (Tear of the Goddess)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+15 法力值', 'sub_stat': '基础回蓝散件', 'refine': '提供开局初始法力值，用于合成青龙刀、大天使、正义之手、蓝霸符等。'},
    {'name': '锁子甲 (Chain Vest)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+20 护甲', 'sub_stat': '基础护甲散件', 'refine': '提供物理防御抗性，用于合成反甲、日炎、泰坦、坚定之心等。'},
    {'name': '负极斗篷 (Negatron Cloak)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+20 魔法抗性', 'sub_stat': '基础魔抗散件', 'refine': '提供魔法抗性，用于合成龙牙、离子火花、饮血剑、石像鬼石板甲等。'},
    {'name': '巨人腰带 (Giant\'s Belt)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+150 生命值', 'sub_stat': '基础生命散件', 'refine': '提供高额初始血量，用于合成狂徒铠甲、日炎、救赎、纳什之牙等。'},
    {'name': '拳套 (Sparring Gloves)', 'type': '基础散件', 'rarity': 1, 'base_atk': '+20% 暴击率', 'sub_stat': '基础暴击散件', 'refine': '提供暴击几率，用于合成无尽、法爆、正义之手、水银、破防者等。'},
    {'name': '金铲铲 (Spatula)', 'type': '基础散件', 'rarity': 4, 'base_atk': '+全属性加成', 'sub_stat': '转职核心金铲铲', 'refine': '全能转职核心，可与散件合成执法官、黑玫、征服者、极客等各系转职纹章。'},
    {'name': '金锅锅 (Frying Pan)', 'type': '基础散件', 'rarity': 4, 'base_atk': '+全属性加成', 'sub_stat': '双城特色转职金锅锅', 'refine': '双城特色特殊转职工具，与金铲铲合成可获得战术家之冠（+1人口上限）。'},

    # 核心标准成装
    {'name': '无尽之刃 (Infinity Edge)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+35% 攻击力, +35% 暴击率', 'sub_stat': '合成: 大剑 + 拳套', 'refine': '技能伤害可以造成暴击！若暴击率溢出，每 1% 溢出暴击率转化为 1% 暴击伤害。物理主C核心。'},
    {'name': '最后的轻语 (Last Whisper)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+15% 攻击力, +25% 攻速, +20% 暴击', 'sub_stat': '合成: 反曲之弓 + 拳套', 'refine': '造成的物理伤害会对目标施加 30% 护甲击碎效果，持续 3 秒。破甲必备！'},
    {'name': '灭世者的死亡之帽 (Rabadon\'s Deathcap)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+50 法术强度', 'sub_stat': '合成: 大棒 + 大棒', 'refine': '额外获得 20% 伤害增幅！简单粗暴提升法系主C的极限核爆伤害。'},
    {'name': '珠光护手 (Jeweled Gauntlet / 法爆)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+35 法强, +35% 暴击率', 'sub_stat': '合成: 大棒 + 拳套', 'refine': '技能造成的法术伤害与真实伤害可以暴击！法系秒人第一核心神器。'},
    {'name': '朔极之矛 (Spear of Shojin / 青龙刀)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+20 攻击力, +20 法强, +15 法力', 'sub_stat': '合成: 大剑 + 女神之泪', 'refine': '每次普通攻击额外回复 5 点法力值。大招流主C（凯特琳/乐芙兰/爆爆）必备启动神装。'},
    {'name': '鬼索的狂暴之刃 (Guinsoo\'s Rageblade / 羊刀)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+10% 攻击速度, +10 法术强度', 'sub_stat': '合成: 反曲之弓 + 大棒', 'refine': '每次普通攻击永久叠加 5% 额外攻击速度，无叠加层数上限！持续普攻流绝对核心。'},
    {'name': '泰坦的坚决 (Titan\'s Resolve)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+20 护甲, +10% 攻速', 'sub_stat': '合成: 锁子甲 + 反曲之弓', 'refine': '攻击或受到伤害时叠加 2% 攻击力与法强（最多叠加25层）；满层额外获得 20 护甲与 20 魔抗。战士神装。'},
    {'name': '狂徒铠甲 (Warmog\'s Armor)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+800 最大生命值', 'sub_stat': '合成: 腰带 + 腰带', 'refine': '获得 8% 额外最大生命值加成！前排主坦第一血量支撑大件。'},
    {'name': '棘刺背心 (Bramble Vest / 反甲)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+65 护甲', 'sub_stat': '合成: 锁子甲 + 锁子甲', 'refine': '使受到的暴击伤害减免 8%；受到普通攻击时对周围敌人反弹魔法伤害并施加重伤。'},
    {'name': '巨龙之爪 (Dragon\'s Claw / 龙牙)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+75 魔法抗性', 'sub_stat': '合成: 负极斗篷 + 负极斗篷', 'refine': '每 2 秒为自身恢复 5% 最大生命值。对抗法师大军核心防具。'},
    {'name': '离子火花 (Ionic Spark)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+25 魔抗, +15 法强, +200 生命', 'sub_stat': '合成: 大棒 + 负极斗篷', 'refine': '使周围 2 格内敌人降低 30% 魔法抗性；敌人在附近施放技能时会受到相当于其法力值 160% 的电击伤害。'},
    {'name': '日炎斗篷 (Sunfire Cape)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+20 护甲, +250 生命值', 'sub_stat': '合成: 锁子甲 + 腰带', 'refine': '每 2 秒对 2 格内一名敌人造成最大生命值 1% 灼烧真实伤害，并施加 33% 减疗重伤持续 10 秒。'},
    {'name': '救赎 (Redemption)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+150 生命值, +15 法力值', 'sub_stat': '合成: 女神之泪 + 腰带', 'refine': '每 5 秒为周围 1 格内的所有友军回复 15% 已损失生命值，并提供持续 5 秒的 10% 群体范围伤害减免。'},
    {'name': '正义之手 (Hand of Justice)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+15% 攻击力, +15 法强, +15% 全能吸血', 'sub_stat': '合成: 女神之泪 + 拳套', 'refine': '战斗开始随机将攻击力/法强翻倍提升至 30%，或将全能吸血翻倍提升至 30%！通用极佳。'},
    {'name': '饮血剑 (Bloodthirster)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+20 攻击力, +20 魔抗, +20% 全能吸血', 'sub_stat': '合成: 大剑 + 负极斗篷', 'refine': '生命值降至 40% 时，立即获得相当于 25% 最大生命值的护盾持续 5 秒。近战主C保命神器。'},
    {'name': '夜之锋刃 (Edge of Night)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+25 攻击力, +20 护甲', 'sub_stat': '合成: 大剑 + 锁子甲', 'refine': '生命值首次降至 60% 时短暂进入隐形状态，免疫所有控制并无法被敌人选定，随后获得 30% 额外攻击速度！'},
    {'name': '纳什之牙 (Nashor\'s Tooth)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+30 法术强度, +10% 攻击速度, +150 生命', 'sub_stat': '合成: 反曲之弓 + 腰带', 'refine': '施放技能后，获得持续 5 秒的 40% 额外攻击速度加成！大幅加快下一次技能充能。'},
    {'name': '坚定之心 (Steadfast Heart)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+250 生命值, +20 护甲, +20% 暴击', 'sub_stat': '合成: 锁子甲 + 拳套', 'refine': '承受的所有伤害减免 8%；当自身生命高于 50% 时，减伤幅度提升至 15%！顶尖防装。'},
    {'name': '蓝霸符 (Blue Buff)', 'type': '标准成装', 'rarity': 3, 'base_atk': '+20 攻击力, +20 法强, +20 法力值', 'sub_stat': '合成: 女神之泪 + 女神之泪', 'refine': '技能的最大法力消耗降低 10 点！每次击杀目标后，造成的所有伤害提升 8% 持续 8 秒。短蓝条弈子专属神装。'},

    # 奥恩神器与光明装备
    {'name': '中娅悖论 (Zhonya\'s Paradox)', 'type': '奥恩神器', 'rarity': 5, 'base_atk': '+45 法强, +30 护甲, +30 魔抗', 'sub_stat': '奥恩铁匠铺打造', 'refine': '生命降至 40% 时进入 3 秒金身无敌状态！期间无法被攻击且生成金币。'},
    {'name': '魔蕴 (Manazane)', 'type': '奥恩神器', 'rarity': 5, 'base_atk': '+15 法力值, +15 攻击力, +15 法强', 'sub_stat': '奥恩铁匠铺打造', 'refine': '每场战斗首次施放技能后，在接下来的 5 秒内极速恢复 120 点额外法力值！连续开大大招连发！'},
    {'name': '狙击手的专注 (Sniper\'s Focus)', 'type': '奥恩神器', 'rarity': 5, 'base_atk': '+15% 攻击力, +15 法强, +1 攻击距离', 'sub_stat': '奥恩铁匠铺打造', 'refine': '攻击距离提升 1 格；携带者与目标每相距 1 格，造成的伤害提升 9% 独立乘区！'},
    {'name': '光明狂徒铠甲 (Warmog\'s Pride)', 'type': '光明装备', 'rarity': 5, 'base_atk': '+1600 最大生命值', 'sub_stat': '光明军械库掉落', 'refine': '提供极其恐怖的 1600 点生命上限，且每秒回复 1% 最大生命值！血条无尽。'},
    {'name': '光明鬼索狂暴之刃 (Guinsoo\'s Reckoning)', 'type': '光明装备', 'rarity': 5, 'base_atk': '+20% 攻击速度, +20 法强', 'sub_stat': '光明军械库掉落', 'refine': '每次普攻叠加 10% 攻击速度（双倍速率），残局化身为全自动激光炮！'},

    # 转职纹章
    {'name': '执法官纹章 (Enforcer Emblem)', 'type': '羁绊纹章', 'rarity': 4, 'base_atk': '+150 生命值', 'sub_stat': '金铲铲 + 锁子甲', 'refine': '携带者获得【执法官】羁绊，开局获得护盾并标记敌方核心通缉！'},
    {'name': '黑色玫瑰纹章 (Black Rose Emblem)', 'type': '羁绊纹章', 'rarity': 4, 'base_atk': '+20% 暴击率', 'sub_stat': '金铲铲 + 拳套', 'refine': '携带者获得【黑色玫瑰】羁绊，加速唤醒并强化塞恩！'},
    {'name': '极客纹章 (Scrap Emblem)', 'type': '羁绊纹章', 'rarity': 4, 'base_atk': '+10 法术强度', 'sub_stat': '金铲铲 + 大棒', 'refine': '携带者获得【极客】羁绊，自带散件变临时成装并享受全队厚护盾。'},
    {'name': '铁血征服者纹章 (Conqueror Emblem)', 'type': '羁绊纹章', 'rarity': 4, 'base_atk': '+10 攻击力', 'sub_stat': '金铲铲 + 暴风大剑', 'refine': '携带者获得【铁血征服者】羁绊，击杀敌人叠层享受战利品开箱收益。'}
]

META_COMPS = [
    {
        'name': '【S级阵容】6执法官微光狙神凯特琳',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '核心羁绊: 6执法官 2狙神 2监察 2格斗家',
        'four_piece_bonus': '主C凯特琳 (青龙刀+无尽+轻语) | 主坦洛里斯 (狂徒+反甲+龙牙) | 副C蔚 (血手+泰坦+正义)',
        'pieces': [
            {'role': '主C', 'unit': '凯特琳 (4费)', 'items': '青龙刀 + 无尽之刃 + 最后的轻语'},
            {'role': '副C', 'unit': '蔚 (4费)', 'items': '斯特拉克的挑战护手 + 泰坦的坚决 + 正义之手'},
            {'role': '主坦', 'unit': '洛里斯 (3费)', 'items': '狂徒铠甲 + 棘刺背心 + 巨龙之爪'},
            {'role': '挂件', 'unit': '麦迪 (1费), 卡蜜尔 (2费), 崔斯特 (2费), 斯特卜 (1费), 安蓓萨 (4费)'}
        ],
        'rules_reference': {
            'strategy': '2阶段连胜过渡，3-2升6人口保血，4-2升8人口大搜两星凯特琳与蔚锁血，5阶段升9挂杰斯开大成执法官阵容。'
        }
    },
    {
        'name': '【S级阵容】黑玫九五死灵大军',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '核心羁绊: 5/7黑色玫瑰 2先知 2统领 2法师 2双形战士',
        'four_piece_bonus': '主C乐芙兰 (青龙刀+大帽+法爆) | 主坦伊莉丝/塞恩 (狂徒+日炎+救赎) | 副C玛尔扎哈 (电刀+鬼书)',
        'pieces': [
            {'role': '主C', 'unit': '乐芙兰 (5费)', 'items': '朔极之矛 + 灭世者的死亡之帽 + 珠光护手'},
            {'role': '主坦', 'unit': '塞恩 / 伊莉丝 (4费)', 'items': '狂徒铠甲 + 日炎斗篷 + 救赎'},
            {'role': '副C', 'unit': '玛尔扎哈 (5费)', 'items': '斯塔缇克电刃 + 莫雷洛秘典'},
            {'role': '核心', 'unit': '卡西奥佩娅 (3费), 弗拉基米尔 (2费), 莫甘娜 (1费), 塞薇卡 (5费), 杰斯 (5费)'}
        ],
        'rules_reference': {
            'strategy': '前期利用3黑玫召唤塞恩连胜积累能量，4-5升8人口搜卡，5-2升9人口找全员二星橙卡完成终极死灵九五。'
        }
    },
    {
        'name': '【S级阵容】6征服者安蓓萨德莱文',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '核心羁绊: 6铁血征服者 2迅击战士 2监察 2搏击手',
        'four_piece_bonus': '主C安蓓萨 (泰坦+饮血剑+夜之锋刃) | 副C德莱文 (羊刀+无尽+轻语) | 主坦芮尔 (离子+板甲+日炎)',
        'pieces': [
            {'role': '主C', 'unit': '安蓓萨 (4费)', 'items': '泰坦的坚决 + 饮血剑 + 夜之锋刃'},
            {'role': '副C', 'unit': '德莱文 (1费追三)', 'items': '鬼索的狂暴之刃 + 无尽之刃 + 最后的轻语'},
            {'role': '主坦', 'unit': '芮尔 (2费)', 'items': '离子火花 + 石像鬼石板甲 + 日炎斗篷'},
            {'role': '挂件', 'unit': '塞薇卡 (5费), 盖伦 (4费), 蔚 (4费), 德莱厄斯 (1费)'}
        ],
        'rules_reference': {
            'strategy': '连胜击杀快速积攒征服者层数解锁战利品宝箱，爆大量金币与成装，中期锁血能力独一档。'
        }
    },
    {
        'name': '【A+级阵容】极客伏击爆爆金克丝',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '核心羁绊: 6极客 2伏击专家 2炮手 2搏击手',
        'four_piece_bonus': '主C金克丝 (羊刀+巨杀+无尽) | 副坦兰博/艾克 (日炎+泰坦+正义) | 爆爆 (单散件刷成装)',
        'pieces': [
            {'role': '主C', 'unit': '金克丝 (5费)', 'items': '鬼索的狂暴之刃 + 巨人捕手 + 无尽之刃'},
            {'role': '主坦', 'unit': '兰博 (5费) / 艾克 (4费)', 'items': '日炎斗篷 + 泰坦的坚决 + 正义之手'},
            {'role': '前置', 'unit': '爆爆 (1费), 特朗德尔 (1费), 普朗克 (3费), 蔚奥莱 (1费)'}
        ],
        'rules_reference': {
            'strategy': '极客散件收益最大化，全员厚盾，4-1搜出核心，稳进前三。'
        }
    },
    {
        'name': '【A+级阵容】炼金男爵微光收菜流',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '核心羁绊: 5/7炼金男爵 2先知 2格斗家 2统领',
        'four_piece_bonus': '主C希尔科 (青龙刀+法爆+纳什) | 副C塞薇卡 (血手+泰坦) | 主坦蒙多 (狂徒+反甲)',
        'pieces': [
            {'role': '主C', 'unit': '希尔科 (4费)', 'items': '朔极之矛 + 珠光护手 + 纳什之牙'},
            {'role': '副C', 'unit': '塞薇卡 (5费)', 'items': '斯特拉克的挑战护手 + 泰坦的坚决'},
            {'role': '主坦', 'unit': '蒙多医生 (4费)', 'items': '狂徒铠甲 + 棘刺背心'},
            {'role': '挂件', 'unit': '烈娜塔 (2费), 辛吉德 (1费), 荏妮 (2费), 史密奇 (2费)'}
        ],
        'rules_reference': {
            'strategy': '3阶段走连败攒微光，300层以上提款收菜，获取全套光明装与神级突变一波转连胜吃鸡。'
        }
    },
    {
        'name': '【A级阵容】赌狗家人蔚奥莱爆爆',
        'rarity_min': 4,
        'rarity_max': 4,
        'two_piece_bonus': '核心羁绊: 4家人 2搏击手 2极客 2执法官',
        'four_piece_bonus': '蔚奥莱 (泰坦+饮血+正义) | 爆爆 (青龙刀+法爆+纳什) | 范德尔 (狂徒+日炎)',
        'pieces': [
            {'role': '主C', 'unit': '蔚奥莱 (1费三星)', 'items': '泰坦的坚决 + 饮血剑 + 正义之手'},
            {'role': '副C', 'unit': '爆爆 (1费三星)', 'items': '朔极之矛 + 珠光护手 + 纳什之牙'},
            {'role': '主坦', 'unit': '范德尔 (2费三星)', 'items': '狂徒铠甲 + 日炎斗篷'},
            {'role': '挂件', 'unit': '艾克 (4费), 蔚 (4费), 麦迪 (1费)'}
        ],
        'rules_reference': {
            'strategy': '3-1在4级卡40金币慢D三星，一费三星全出后直奔高人口。'
        }
    }
]

SPECIAL_MECHANICS = [
    {
        'category': '赛季核心机制',
        'title': '【异常突变 (The Anomaly)】机制详解与效果池',
        'formula': '在阶段 4-6 开启异常突变舱，花费 1 金币每次无限刷新，为一名弈子赋予永久专属质变能力',
        'parameters': {
            '核心机制': '全场每位玩家可将一名弈子放入突变舱，在 60+ 种突变效果中选择一项锁定，全场仅生效一次且无法撤回',
            '输出型突变': '【能量过载】(释放技能后立即回复50%法力值)、【狂暴火球】(攻击附加范围烈焰溅射)、【终极飞升】(战斗15秒后伤害提升200%)、【连击狂热】(每次普攻叠加攻速)',
            '防御型突变': '【巨型体型】(生命值提升1000且体型巨大践踏敌人)、【适应性外骨骼】(承受伤害降低30%且自愈)、【不屈之盾】(半血时提供永久免死厚盾)',
            '特殊型突变': '【金色收获】(突变弈子击杀掉落金币)、【便携异常点】(复制突变效果给另一弈子)'
        }
    },
    {
        'category': '对局环境',
        'title': '开局城邦传送门与奇遇投票机制',
        'formula': '阶段 1-1 全体玩家投票选出本局核心游戏规则环境',
        'parameters': {
            '迅捷蟹水潭': '所有野怪回合变为提供巨额金币与装备的黄金巨蟹，全员经济爆棚',
            '棱彩开局': '第一个海克斯强化必定为彩色/棱彩阶梯（升级咯、对冲基金等）',
            '黄金开局': '本局所有海克斯强化统一为高战力金色阶梯',
            '奥恩锻炉': '游戏开始时直接自选一件强力奥恩神器'
        }
    },
    {
        'category': '抽卡与概率',
        'title': '卡池总量与各等级商店刷新概率阶梯矩阵',
        'formula': '单张卡池总量: 1费(22张) | 2费(20张) | 3费(17张) | 4费(10张) | 5费(9张)',
        'parameters': {
            '4级 (赌1费)': '1费 55% | 2费 30% | 3费 15% | 4/5费 0%',
            '6级 (赌2费)': '1费 30% | 2费 40% | 3费 25% | 4费 5% | 5费 0%',
            '7级 (追3费)': '1费 19% | 2费 35% | 3费 35% | 4费 10% | 5费 1%',
            '8级 (四费核心)': '1费 18% | 2费 25% | 3费 32% | 4费 22% | 5费 3% (4-2大搜节点)',
            '9级 (大成九五)': '1费 10% | 2费 20% | 3费 25% | 4费 35% | 5费 10% (五费二星)',
            '10级 (三星五费)': '1费 5% | 2费 10% | 3费 20% | 4费 40% | 5费 25%'
        }
    },
    {
        'category': '经济模型',
        'title': '金币复利与连胜连败收益公式',
        'formula': '总收入 = 基础收入(5) + 利息收入(最多5) + 胜场奖励(1) + 连胜/连败梯度奖励',
        'parameters': {
            '利息规则': '每存 10 金币产生 1 金币利息，存满 50 金币吃满最高 5 金币利息',
            '连胜梯度': '2~3连胜+1金币，4连胜+2金币，5连胜以上+3金币',
            '连败收益': '2~3连败+1金币，4连败+2金币，5连败以上+3金币（连败需保血线）'
        }
    },
    {
        'category': '装备合成',
        'title': '选秀轮盘与金铲铲/金锅锅双转职配方',
        'formula': '金铲铲 + 散件 = 对应羁绊纹章；金铲铲 + 金锅锅 = 战术家之冠 (+1 人口)',
        'parameters': {
            '金铲铲合成': '锁子甲->执法官 | 拳套->黑色玫瑰 | 大棒->极客 | 大剑->征服者',
            '金锅锅合成': '腰带->监察 | 斗篷->哨兵 | 女神泪->先知',
            '重铸与拆卸': '装备拆卸器可在不卖棋子的情况下取下全部装备；装备重铸器随机重置同阶装备'
        }
    },
    {
        'category': '升星机制',
        'title': '棋子升星属性倍率与三星质变机制',
        'formula': '3个1星合成2星 (生命值1.8x, 攻击力1.5x)；3个2星合成3星 (生命值3.24x, 攻击力2.25x)',
        'parameters': {
            '四费三星': '技能倍率飙升 5~8 倍，可造成毁灭性清场',
            '五费三星': '技能倍率提升至 9999+，附带全屏秒杀真伤与视觉霸屏特效，基本锁定吃鸡'
        }
    }
]


def crawl_and_sync_tft(game_ids=[28, 19]):
    data = load_tft_data()
    version = 'v14.23 (S13双城传说)'

    # 1. Parse Set 13 Champions
    s13 = data.get('sets', {}).get('13', {})
    champions = []
    for c in s13.get('champions', []):
        traits = c.get('traits', [])
        cost = c.get('cost', 0)
        name = (c.get('name') or '').strip()
        if not traits or cost <= 0 or not name:
            continue

        raw_stats = c.get('stats', {})
        base_hp = raw_stats.get('hp') or 600
        base_ad = raw_stats.get('damage') or 50
        armor = raw_stats.get('armor') or 30
        mr = raw_stats.get('magicResist') or 30
        as_val = raw_stats.get('attackSpeed') or 0.65
        range_val = raw_stats.get('range') or 1
        init_mana = raw_stats.get('initialMana') or 0
        max_mana = raw_stats.get('mana') or 100

        stats_data = [
            {'level': '1星', 'hp': int(base_hp), 'atk': int(base_ad), 'armor': int(armor), 'mr': int(mr), 'attack_speed': round(as_val, 2), 'range': f'{int(range_val)}格'},
            {'level': '2星', 'hp': int(base_hp * 1.8), 'atk': int(base_ad * 1.5), 'armor': int(armor), 'mr': int(mr), 'attack_speed': round(as_val, 2), 'range': f'{int(range_val)}格'},
            {'level': '3星', 'hp': int(base_hp * 3.24), 'atk': int(base_ad * 2.25), 'armor': int(armor), 'mr': int(mr), 'attack_speed': round(as_val, 2), 'range': f'{int(range_val)}格'}
        ]

        ability = c.get('ability', {})
        ab_name = ability.get('name', '棋子技能')
        ab_desc = clean_desc(ability.get('desc', ''))
        talents = [
            {
                'name': ab_name,
                'type': 'ELEMENTAL_BURST',
                'scaling': f'法力值: {int(init_mana)}/{int(max_mana)}',
                'description': ab_desc
            }
        ]

        icon_path = c.get('icon', '')
        avatar_url = f'https://raw.communitydragon.org/latest/game/{icon_path.lower()}' if icon_path else ''
        bis_items = CHAMPION_BIS.get(name, '狂徒铠甲 / 正义之手 / 珠光护手')

        champions.append({
            'name': name,
            'title': f'{cost}费 · {"/".join(traits)}',
            'rarity': min(max(cost, 1), 5),
            'element': ' / '.join(traits),
            'weapon_type': '近战 (1格)' if range_val <= 1 else ('近战 (2格)' if range_val <= 2 else f'远程 ({int(range_val)}格)'),
            'region': traits[0] if traits else '双城之战',
            'arkhe': f'{int(init_mana)}/{int(max_mana)} 蓝条',
            'avatar_url': avatar_url,
            'splash_url': avatar_url,
            'base_stats': stats_data,
            'talents': talents,
            'passives': [{'name': '特质羁绊', 'description': ' / '.join(traits)}],
            'constellations': [],
            'special_mechanics': {'traits': traits, 'cost': cost, 'range': range_val},
            'recommendations': {'best_items': bis_items, 'preferred_role': '核心主C' if cost >= 4 else ('前排主坦' if '格斗家' in traits or '监察' in traits or '哨兵' in traits else '过渡输出')},
            'version': version
        })

    # 2. Parse Traits (38 Set 13 Traits)
    traits_list = []
    for tr in s13.get('traits', []):
        t_name = (tr.get('name') or '').strip()
        t_desc = clean_desc(tr.get('desc') or '')
        effects = tr.get('effects', [])
        if not t_name or not effects:
            continue

        tier_descs = []
        pieces = []
        for eff in effects:
            min_u = eff.get('minUnits', 0)
            variables = eff.get('variables', {})
            desc_piece = f'({min_u}) 人数激活: {variables}'
            pieces.append({'units': min_u, 'effect': desc_piece})
            tier_descs.append(f'({min_u}) 阶段: {t_desc[:120]}')

        icon_path = tr.get('icon', '')
        icon_url = f'https://raw.communitydragon.org/latest/game/{icon_path.lower()}' if icon_path else ''

        traits_list.append({
            'name': f'【羁绊】{t_name}',
            'rarity_min': 2,
            'rarity_max': 5,
            'icon_url': icon_url,
            'two_piece_bonus': tier_descs[0] if tier_descs else t_desc[:100],
            'four_piece_bonus': tier_descs[-1] if len(tier_descs) > 1 else (tier_descs[0] if tier_descs else t_desc[:120]),
            'pieces': pieces,
            'rules_reference': {'description': t_desc},
            'version': version
        })

    # 3. Parse Augments (强化符文)
    augments_list = []
    for it in data.get('items', []):
        if not it.get('isAugment'):
            continue
        api = it.get('apiName') or ''
        name = (it.get('name') or '').strip()
        desc = clean_desc(it.get('desc') or '')
        icon = (it.get('icon') or '').lower()

        # Only Set 13 or famous universal augments
        is_s13 = api.startswith('TFT13_')
        is_universal = any(k in name for k in ['升级咯', '对冲基金', '门票', '潘朵拉', '珠光莲花', '药剂师', '治疗法球', '飞升', '卓尔不群', '代谢增速', '背水一战'])
        if not (is_s13 or is_universal) or not name or not desc or name.startswith('TFT'):
            continue

        tier_name = '银色强化'
        rarity_val = 2
        if '_ii.' in icon or '_ii_' in icon or 'tier2' in icon or 'gold' in icon:
            tier_name = '金色强化'
            rarity_val = 4
        elif '_iii.' in icon or '_iii_' in icon or 'tier3' in icon or 'prismatic' in icon:
            tier_name = '棱彩强化'
            rarity_val = 5

        icon_url = f'https://raw.communitydragon.org/latest/game/{icon}' if icon else ''

        augments_list.append({
            'name': f'【符文】{name} ({tier_name})',
            'rarity_min': rarity_val,
            'rarity_max': rarity_val,
            'icon_url': icon_url,
            'two_piece_bonus': f'阶梯: {tier_name}',
            'four_piece_bonus': desc,
            'pieces': [{'type': tier_name, 'name': name}],
            'rules_reference': {'apiName': api},
            'version': version
        })

    # 4. Meta Comps
    comps_list = []
    for comp in META_COMPS:
        comps_list.append({
            'name': comp['name'],
            'rarity_min': comp['rarity_min'],
            'rarity_max': comp['rarity_max'],
            'icon_url': '/games/tft_meta_comp.png',
            'two_piece_bonus': comp['two_piece_bonus'],
            'four_piece_bonus': comp['four_piece_bonus'],
            'pieces': comp['pieces'],
            'rules_reference': comp['rules_reference'],
            'version': version
        })

    # Combined Artifact Sets (Traits + Augments + Meta Comps)
    all_artifact_sets = traits_list + augments_list + comps_list

    # 5. Clean Equipment
    weapons_list = []
    for eq in CURATED_EQUIPMENT:
        weapons_list.append({
            'name': eq['name'],
            'type': eq['type'],
            'rarity': eq['rarity'],
            'icon_url': f'/games/tft_items/{eq["name"].split()[0]}.png',
            'base_atk_curve': {'stats': eq['base_atk']},
            'sub_stat': {'recipe': eq['sub_stat']},
            'refinements': {'effect': eq['refine']},
            'ascension_materials': {'type': '选秀 / 野怪回合掉落 / 武器库'},
            'version': version
        })

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for gid in game_ids:
                # Clean old junk weapons
                cur.execute('DELETE FROM game_weapon WHERE game_id = %s', (gid,))
                # Clean old artifact sets (traits)
                cur.execute('DELETE FROM game_artifact_set WHERE game_id = %s', (gid,))
                # Clean old mechanic rules
                cur.execute('DELETE FROM game_mechanic_rule WHERE game_id = %s', (gid,))
            conn.commit()
    finally:
        conn.close()

    for gid in game_ids:
        print(f'[TFT] Ingesting comprehensive dataset into Game ID {gid} ...')
        c_count = upsert_characters(gid, champions)
        w_count = upsert_weapons(gid, weapons_list)
        a_count = upsert_artifacts(gid, all_artifact_sets)
        m_count = upsert_mechanics(gid, SPECIAL_MECHANICS)
        print(f'[TFT] Done Game {gid}: {c_count} champions, {w_count} curated items, {a_count} traits/augments/comps, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_tft([28, 19])
