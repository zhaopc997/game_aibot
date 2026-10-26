#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黑神话：悟空 (Black Myth: Wukong) 全量数值体系落库与同步脚本
game_id = 4

包含:
1. 天命人核心流派与形态 (劈棍法、立棍法、戳棍法、禁字法、救命毫毛化身、齐天大圣形态，1-100级属性成长、核心天赋技能、六根觉醒)
2. 全量 16+ 神珍/特品兵刃 (基础面板、独门妙用、暴击/攻击属性、铸造材料)
3. 8 大核心披挂套装 (大圣套、赭黄套、行者套、乌金套、龙鳞套、厌火套、昆蚨套、百戏套 2件/4件机制词缀)
4. 5 大底层战斗机制公式 (棍势倍率成长、识破无敌帧判定、四灾异常阈值与克制、气力消耗与完美闪避、六根天资觉醒)
"""

import os
import sys
import json
import hashlib
import psycopg2
from psycopg2.extras import Json

PG_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
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

def get_wukong_characters():
    """构建黑神话：悟空 天命人 6 大流派形态体系"""
    return [
        {
            "name": "天命人·劈棍法 (Smash Stance)",
            "title": "斩棍切手·雷霆万钧",
            "rarity": 5,
            "element": "劈棍法",
            "weapon_type": "长棍",
            "avatar_url": "https://image.gcores.com/wukong_smash_stance.png",
            "splash_url": "https://image.gcores.com/wukong_splash_art.jpg",
            "base_stats": [
                {"level": "1", "hp": 300, "atk": 45, "def": 0, "speed": 100, "stamina": 220, "mana": 180, "crit_rate": "3%"},
                {"level": "20", "hp": 380, "atk": 70, "def": 40, "speed": 100, "stamina": 260, "mana": 210, "crit_rate": "6%"},
                {"level": "40", "hp": 480, "atk": 110, "def": 90, "speed": 100, "stamina": 310, "mana": 250, "crit_rate": "10%"},
                {"level": "60", "hp": 580, "atk": 160, "def": 150, "speed": 100, "stamina": 360, "mana": 290, "crit_rate": "14%"},
                {"level": "80", "hp": 680, "atk": 220, "def": 210, "speed": 100, "stamina": 410, "mana": 340, "crit_rate": "18%"},
                {"level": "100", "hp": 750, "atk": 280, "def": 260, "speed": 100, "stamina": 460, "mana": 380, "crit_rate": "22%"}
            ],
            "special_ascension_stat": {
                "stat_name": "流派核心武学特权",
                "values": {
                    "核心特权": "识破无敌帧 (切手技斩棍式)",
                    "重击特性": "奔跑蓄力打出四段天火重劈",
                    "暴击伤害": "+175% 初始暴伤"
                }
            },
            "ascension_materials": [
                {"tier": "第一回·黑风山", "items": "火光金/蚕丝/绵布 | 灵蕴 × 10,000"},
                {"tier": "第二回·黄风岭", "items": "铁中血/冷先荆/石精 | 灵蕴 × 30,000"},
                {"tier": "第三回·小西天", "items": "交加叶/镔铁砂/寒冻残髓 | 灵蕴 × 60,000"},
                {"tier": "第四回·盘丝岭", "items": "金花玉萼/倒马毒钩/宿丝 | 灵蕴 × 100,000"},
                {"tier": "第五回·火焰山", "items": "大力铁角/火灵砂/罗刹金甲 | 灵蕴 × 150,000"},
                {"tier": "第六回·花果山", "items": "大圣通天神珍材料/万年玄铁 | 灵蕴 × 250,000"}
            ],
            "talents": [
                {"name": "基础切手·斩棍式 (破棍式)", "type": "NORMAL_ATTACK", "description": "轻棍连击中看准敌方出招瞬间输入重击，化解对手攻势并处于绝对无敌判定，造成极高失衡与重创反击。", "scaling": "切手消耗 1 点棍势，造成 320% 伤害与 100% 僵直"},
                {"name": "奔跑蓄力·天崩地裂", "type": "ELEMENTAL_SKILL", "description": "在高速奔跑中凝聚天地元气，蓄满 3~4 段棍势后跃入苍穹凌空重击，引发方圆十丈的大地震裂。", "scaling": "4段蓄力倍率 1450%，必定震翻非霸体精英与首领"},
                {"name": "奇术·定身法", "type": "ELEMENTAL_BURST", "description": "口念真言抬手一指，瞬间将视野内的敌人定在原地动弹不得；在破隐或敌方出招瞬间定身延长硬直时间。", "scaling": "消耗法力 60 点，基础定身 4.5 秒，打碎破定造成额外 20% 暴击伤害"},
                {"name": "核心天赋·识破贯通", "type": "PASSIVE_TALENT", "description": "识破成功后大幅返还本次攻击消耗的气力，并在 3 秒内使自身攻击力提升 20%。", "scaling": "永久生效，气力返还 50%"},
                {"name": "化身·幽魂大头重击", "type": "EXPLORATION_TALENT", "description": "化身巨头幽魂以额头猛撞地面，造成大范围毁灭冲击并大幅提升天命人基础防御力。", "scaling": "常驻防御 +30 点，撞击造成 650% 物理重击"}
            ],
            "passives": [
                {"name": "行者身法·迅捷奔突", "desc": "疾跑时气力消耗降低 30%，奔跑中蓄力不衰减移动速度。"},
                {"name": "意气风发·见切知机", "desc": "识破斩棍式若精准命中对手弱点，立即额外赠送 1 段棍势。"},
                {"name": "绝顶凌霄·霸体金身", "desc": "四段蓄力起跳下劈全过程中获得绝对刚体霸体，免疫一切打断。"}
            ],
            "constellations": [
                {"c": 1, "name": "眼看喜·秉意不移", "desc": "识破斩棍式的判定时间窗口延长 0.08 秒，成功后额外造成 15% 伤害。"},
                {"c": 2, "name": "耳听怒·听风辨位", "desc": "完美闪避时留下残影并额外恢复半段棍势，同时引爆气爆震退近身敌人。"},
                {"c": 3, "name": "鼻嗅爱·气随心动", "desc": "气力上限提升 40 点，处于低气力时气力恢复速率提高 35%。"},
                {"c": 4, "name": "舌尝思·含灵化生", "desc": "饮用葫芦仙酿时，恢复全部气力并在 10 秒内提升 15% 暴击率。"},
                {"c": 5, "name": "身本忧·金刚不坏", "desc": "受到致死伤害时免死一次并触发铜头铁壁反震，冷却时间 180 秒。"},
                {"c": 6, "name": "意见欲·胜佛真意", "desc": "第四段棍势伤害提升 40%，且击中首领时必定造成长时间倒地大硬直！"}
            ],
            "special_mechanics": {
                "core_flow": "轻棍1~3段平A垫刀积攒棍势 -> 观察首领抬手瞬间重击识破斩棍式打出无敌帧 -> 奔跑拉开身位蓄满3~4段棍势飞天重劈砸碎霸体！",
                "stamina_control": "时刻保留至少 20% 气力用于翻滚闪避，切忌盲目平A打空气耗空绿条。"
            },
            "recommendations": {
                "weapons": {"bis": "如意金箍棒 (神珍)", "alternative_5s": "混铁棍 / 三尖两刃枪", "budget_4s": "鳞棍·蟠龙 / 狼牙棒"},
                "artifacts": {"bis_set": "大圣套装 (4件套)", "alt_set": "赭黄套装 / 乌金套装"},
                "main_stats": {"priority": "攻击力 > 暴击率 > 暴击伤害 > 气力上限 > 防御力"}
            },
            "version": "1.0.9"
        },
        {
            "name": "天命人·立棍法 (Pillar Stance)",
            "title": "风云卷地·绝顶凌虚",
            "rarity": 5,
            "element": "立棍法",
            "weapon_type": "长棍",
            "avatar_url": "https://image.gcores.com/wukong_pillar_stance.png",
            "splash_url": "https://image.gcores.com/wukong_splash_art.jpg",
            "base_stats": [
                {"level": "1", "hp": 300, "atk": 42, "def": 10, "speed": 100, "stamina": 240, "mana": 180, "crit_rate": "3%"},
                {"level": "40", "hp": 480, "atk": 105, "def": 105, "speed": 100, "stamina": 340, "mana": 250, "crit_rate": "8%"},
                {"level": "80", "hp": 680, "atk": 210, "def": 230, "speed": 100, "stamina": 460, "mana": 340, "crit_rate": "15%"},
                {"level": "100", "hp": 750, "atk": 270, "def": 280, "speed": 100, "stamina": 520, "mana": 380, "crit_rate": "18%"}
            ],
            "special_ascension_stat": {
                "stat_name": "立棍绝技特权",
                "values": {
                    "对地免疫": "攀棍登顶绝对规避地面震荡波与扫堂腿",
                    "大范围群伤": "风云转持续横扫全场小怪",
                    "终结一击": "江海翻高空超远砸击"
                }
            },
            "ascension_materials": [{"tier": "六回周目晋阶", "items": "随章节推进获得飞龙宝杖材料与大力铁角"}],
            "talents": [
                {"name": "攀棍登顶·高耸入云", "type": "ELEMENTAL_SKILL", "description": "将神木长棍插入地面，借力攀爬至数丈高空，敌方地面范围技能完全无法触及自身。", "scaling": "攀棍高度随棍势段数增加，最高攀至4段高空"},
                {"name": "风云转·旋风扫叶", "type": "NORMAL_ATTACK", "description": "在棍顶以脚蹬长棍急速旋转，向四周发射旋风风刃，横扫包围自身的群敌。", "scaling": "持续消耗气力，每秒造成 180% 范围穿透伤害"},
                {"name": "江海翻·破空下砸", "type": "ELEMENTAL_BURST", "description": "借长棍重力势能向前倾倒，携万钧之力重重砸击正前方极远目标，引发雷鸣轰顶。", "scaling": "倍率高达 1100%，附带极强范围破防效果"}
            ],
            "passives": [
                {"name": "高瞻远瞩", "desc": "攀在棍上时每秒自动恢复 5% 棍势。"},
                {"name": "铜筋铁骨", "desc": "立棍状态下受到的远程投射物伤害降低 50%。"}
            ],
            "constellations": [
                {"c": 1, "name": "耳听怒·听风借力", "desc": "从棍顶跳下施展江海翻时，暴击率提高 20%。"},
                {"c": 6, "name": "意见欲·神龙降世", "desc": "施展江海翻时召来九天神雷，造成大范围雷蛰麻痹与天劫伤害。"}
            ],
            "special_mechanics": {"counter_play": "克制亢金龙、百眼魔君、小黄龙等大量大范围地面爆炸与尾部横扫技能。"},
            "recommendations": {
                "weapons": {"bis": "飞龙宝杖 (神珍)", "alternative_5s": "如意金箍棒", "budget_4s": "鳞棍·亢金"},
                "artifacts": {"bis_set": "龙鳞套装 (4件套)", "alt_set": "大圣套装"}
            },
            "version": "1.0.9"
        },
        {
            "name": "天命人·戳棍法 (Thrust Stance)",
            "title": "凤穿花影·退寸进尺",
            "rarity": 5,
            "element": "戳棍法",
            "weapon_type": "长棍/神枪",
            "avatar_url": "https://image.gcores.com/wukong_thrust_stance.png",
            "splash_url": "https://image.gcores.com/wukong_splash_art.jpg",
            "base_stats": [
                {"level": "1", "hp": 300, "atk": 48, "def": 0, "speed": 100, "stamina": 230, "mana": 180, "crit_rate": "5%"},
                {"level": "40", "hp": 480, "atk": 118, "def": 85, "speed": 100, "stamina": 320, "mana": 250, "crit_rate": "12%"},
                {"level": "80", "hp": 680, "atk": 235, "def": 195, "speed": 100, "stamina": 420, "mana": 340, "crit_rate": "22%"},
                {"level": "100", "hp": 750, "atk": 295, "def": 240, "speed": 100, "stamina": 480, "mana": 380, "crit_rate": "30%"}
            ],
            "special_ascension_stat": {
                "stat_name": "突刺特权",
                "values": {
                    "超远射程": "退寸进尺安全距离突刺压制",
                    "飞剑贯通": "搭配三尖两刃枪触发万剑穿心",
                    "暴击拉满": "终极面板暴击率可达 70%+"
                }
            },
            "ascension_materials": [{"tier": "三尖两刃枪专精", "items": "通关梅山击败二郎显圣真君获取神珍"}],
            "talents": [
                {"name": "切手·退寸进尺", "type": "NORMAL_ATTACK", "description": "在轻棍连击中迅速向后滑步闪避对手攻击，随后枪头一转如毒蛇吐信向正前方突刺数丈。", "scaling": "后撤自带完全无敌帧，反刺伤害 350%"},
                {"name": "凤穿花·连环穿刺", "type": "ELEMENTAL_SKILL", "description": "连续向前刺出数十记疾风暴雨般的枪芒，将目标定在原地动弹不得。", "scaling": "每次突刺附带穿透与破甲"},
                {"name": "蓄力突刺·神枪破晓", "type": "ELEMENTAL_BURST", "description": "超远距离瞬间前冲贯穿直线上所有敌人，直击首领要害产生巨额暴击。", "scaling": "射程达 15 米，暴击倍率提升 50%"}
            ],
            "passives": [{"name": "寸劲穿甲", "desc": "戳棍重击无视目标 25% 基础防御力。"}],
            "constellations": [{"c": 6, "name": "意见欲·枪人合一", "desc": "突刺暴击时引动飞剑暴雨，造成持续 5 秒的绝对压制。"}],
            "special_mechanics": {"tactics": "适合对抗高机动、攻击欲望强烈的首领（如大圣残躯、小黄龙、寅虎），利用射程拉扯折磨对手。"},
            "recommendations": {
                "weapons": {"bis": "三尖两刃枪 (神珍)", "alternative_5s": "如意金箍棒", "budget_4s": "楮白枪"},
                "artifacts": {"bis_set": "赭黄套装 (4件套)", "alt_set": "厌火套装"}
            },
            "version": "1.0.9"
        },
        {
            "name": "天命人·禁字法流派 (Spell Binder Master)",
            "title": "断法绝尘·神力通天",
            "rarity": 5,
            "element": "禁字法",
            "weapon_type": "长棍",
            "avatar_url": "https://image.gcores.com/wukong_spellbinder.png",
            "splash_url": "https://image.gcores.com/wukong_splash_art.jpg",
            "base_stats": [
                {"level": "1", "hp": 300, "atk": 80, "def": 20, "speed": 100, "stamina": 300, "mana": 0, "crit_rate": "15%"},
                {"level": "100", "hp": 750, "atk": 480, "def": 300, "speed": 100, "stamina": 600, "mana": 0, "crit_rate": "42%"}
            ],
            "special_ascension_stat": {
                "stat_name": "禁字诀通天属性转化",
                "values": {
                    "法力转化攻击": "100 点最大法力值永久转化为 45 点基础攻击力",
                    "气力转化暴击": "100 点最大气力值转化为 8% 暴击率与 20% 暴伤",
                    "极限纯体修": "封印所有奇术法宝，换取全游戏最恐怖直伤平A与重棍"
                }
            },
            "ascension_materials": [{"tier": "第三回苦海北岸", "items": "完成不能和尚支线习得禁字法神通"}],
            "talents": [
                {"name": "禁字诀·封元纳力", "type": "ELEMENTAL_SKILL", "description": "将体内全部法力与气力封锁，肉身经络蜕变为纯金刚之体，攻击力、暴击率与移动速度大幅暴增，直到死亡或调息方休。", "scaling": "开启瞬间攻击力 +150~280，暴击率 +20%~35%"},
                {"name": "金刚重棍·一击破天", "type": "ELEMENTAL_BURST", "description": "在禁字诀神力加持下施展四段重棍，直接打出 10,000+ 物理核爆伤害。", "scaling": "直伤伤害乘区翻倍"}
            ],
            "passives": [{"name": "不坏之躯", "desc": "禁字状态下受到攻击受击硬直降低 50%。"}],
            "constellations": [{"c": 6, "name": "绝顶金身", "desc": "每次普通攻击暴击额外增加 5 点永久伤害（本场战斗持续）。"}],
            "special_mechanics": {"tactics": "进 Boss 房前先穿满蓝量披挂开启禁字法，将攻击力撑到极致，再换上高防装备（如混铁棍+大圣套），化身一拳超人！"},
            "recommendations": {
                "weapons": {"bis": "混铁棍 (神珍 防御转攻击)", "alternative_5s": "如意金箍棒", "budget_4s": "狼牙棒"},
                "artifacts": {"bis_set": "行者套装 (4件套 奔跑重劈倍增)", "alt_set": "大圣套装"}
            },
            "version": "1.0.9"
        },
        {
            "name": "天命人·身外身化身流 (A Pluck of Many)",
            "title": "毫毛散尽·群猴围攻",
            "rarity": 5,
            "element": "身外身法",
            "weapon_type": "长棍",
            "avatar_url": "https://image.gcores.com/wukong_clones.png",
            "splash_url": "https://image.gcores.com/wukong_splash_art.jpg",
            "base_stats": [
                {"level": "1", "hp": 300, "atk": 45, "def": 0, "speed": 100, "stamina": 220, "mana": 220, "crit_rate": "4%"},
                {"level": "100", "hp": 750, "atk": 260, "def": 250, "speed": 100, "stamina": 450, "mana": 450, "crit_rate": "20%"}
            ],
            "special_ascension_stat": {
                "stat_name": "猴子猴孙集群威能",
                "values": {
                    "分身数量": "召唤 4~6 只同等伤害猴毛分身",
                    "定身联动": "猴群与定身术形成无限围殴连击",
                    "法力消耗": "对法力上限与回蓝要求极高"
                }
            },
            "ascension_materials": [{"tier": "黄风岭击败沙大郎", "items": "习得身外身法"}],
            "talents": [
                {"name": "身外身法·猴子猴孙", "type": "ELEMENTAL_BURST", "description": "拔下一把救命毫毛吹向空中，幻化出 6 个具有自身 80% 攻击力与血量的猴毛分身，集体冲锋围殴首领。", "scaling": "消耗法力 120 点，持续 20 秒，压制一切人形 Boss"},
                {"name": "聚形散气·金蝉脱壳", "type": "ELEMENTAL_SKILL", "description": "原地留下白雾假身吸引仇恨，自身进入潜行隐身并提升移速，破隐一击造成 200% 暴击伤害。", "scaling": "破隐重棍必定暴击"}
            ],
            "passives": [{"name": "同气连枝", "desc": "分身每次攻击为本体恢复 2 点气力与少量生命。"}],
            "constellations": [{"c": 6, "name": "千变万化", "desc": "分身可以使用本体掌握的切手技和蓄力劈击！"}],
            "special_mechanics": {"tactics": "开场聚形散气隐身 -> 猴毛分身全招 -> 定身术定住首领 -> 6猴齐殴瞬间蒸发半条血！"},
            "recommendations": {
                "weapons": {"bis": "昆棍·通天 (神珍)", "alternative_5s": "如意金箍棒", "budget_4s": "几丁棍"},
                "artifacts": {"bis_set": "赭黄套装 (4件套 聚形散气暴击)", "alt_set": "百戏套装"}
            },
            "version": "1.0.9"
        },
        {
            "name": "天命人·齐天大圣模式 (The Great Sage Complete)",
            "title": "斗战胜佛·齐天神威",
            "rarity": 5,
            "element": "大圣神威",
            "weapon_type": "如意金箍棒",
            "avatar_url": "https://image.gcores.com/wukong_great_sage.png",
            "splash_url": "https://image.gcores.com/wukong_splash_art.jpg",
            "base_stats": [
                {"level": "1", "hp": 500, "atk": 100, "def": 50, "speed": 120, "stamina": 350, "mana": 300, "crit_rate": "10%"},
                {"level": "100", "hp": 1000, "atk": 450, "def": 380, "speed": 120, "stamina": 600, "mana": 500, "crit_rate": "35%"}
            ],
            "special_ascension_stat": {
                "stat_name": "真身完全体神威",
                "values": {
                    "棍势特权": "第四段棍势永不消退 (如意金箍棒独门妙用)",
                    "动作模组": "全套齐天大圣专属行云流水神级动作",
                    "天地同寿": "全属性四灾抗性额外提高 30 点"
                }
            },
            "ascension_materials": [{"tier": "第六回通关与周目轮回", "items": "集齐凤翅紫金冠、锁子黄金甲、点翠飞龙釬、藕丝步云履、如意金箍棒"}],
            "talents": [
                {"name": "大圣真身·天地风云", "type": "NORMAL_ATTACK", "description": "如意金箍棒暴长百丈，挥舞间带起金光狂飙风暴，横扫千军如卷席。", "scaling": "普攻范围覆盖全场，平A自带 250% 伤害倍率"},
                {"name": "神威天火·四段终极重劈", "type": "ELEMENTAL_BURST", "description": "第四段棍势随时随地挥出，金箍棒化身撑天巨柱从九霄云外轰然砸落，毁灭一切妖邪。", "scaling": "伤害倍率 2000%，附带金色神圣神雷冲击波"}
            ],
            "passives": [{"name": "定海神针", "desc": "在任何情况下不会被打断或击飞。"}],
            "constellations": [{"c": 6, "name": "齐天大圣·圆满归位", "desc": "六根全满，三周目终成斗战胜佛！"}],
            "special_mechanics": {"tactics": "全套大圣神装激活专属动作模组与金箍棒神威，体验无敌战神快感。"},
            "recommendations": {
                "weapons": {"bis": "如意金箍棒 (唯一神兵)", "alternative_5s": "三尖两刃枪", "budget_4s": "混铁棍"},
                "artifacts": {"bis_set": "大圣套装 (完整4件套)", "alt_set": "赭黄套装"}
            },
            "version": "1.0.9"
        }
    ]

def get_wukong_weapons():
    """构建黑神话：悟空 全量核心神珍与特品兵刃"""
    return [
        {
            "name": "如意金箍棒",
            "type": "神珍兵刃",
            "rarity": 5,
            "icon_url": "https://image.gcores.com/wukong_weapon_jingubang.png",
            "base_atk_curve": [
                {"level": "获得面板", "atk": 135, "crit_rate": "6%", "def": 0},
                {"level": "大圣神装加成", "atk": 180, "crit_rate": "10%", "def": 50}
            ],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "神珍",
                    "基础攻击力": 135,
                    "暴击率": "+6%",
                    "独门妙用": "第四段棍势可永久维持，不再随时间减削衰减；挥舞时附带定海神针金光风暴。",
                    "典故": "那块铁，挽着些儿就死，磕着些儿就亡，挨挨儿皮破，擦擦儿筋伤！"
                }
            },
            "refinements": [
                {"rank": "独门妙用 (神珍特权)", "desc": "第四段棍势可永久维持，不再随时间自然削减。挥舞时引发金色神威。"},
                {"rank": "大圣套装共鸣", "desc": "集齐凤翅紫金冠、锁子黄金甲等全套大圣防具，解锁齐天大圣专属动作模组与神级连段。"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "花果山击败水帘洞前大圣残躯前置，于石卵瀑布中取得"}],
            "version": "1.0.9"
        },
        {
            "name": "三尖两刃枪",
            "type": "神珍兵刃",
            "rarity": 5,
            "icon_url": "https://image.gcores.com/wukong_weapon_sanjian.png",
            "base_atk_curve": [
                {"level": "获得面板", "atk": 135, "crit_rate": "8%", "def": 0},
                {"level": "飞剑齐发", "atk": 175, "crit_rate": "12%", "def": 0}
            ],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "神珍",
                    "基础攻击力": 135,
                    "暴击率": "+8%",
                    "独门妙用": "使出突刺棍法与切手技打中对手时，会从虚空中射出无数飞剑贯通穿透目标！",
                    "典故": "二郎真君降伏妖魔的神兵利刃，枪头分三叉，两面开刃。"
                }
            },
            "refinements": [
                {"rank": "独门妙用 (神珍特权)", "desc": "轻棍连击与戳棍突刺终结式发射飞剑伤敌；切手技打中对手飞剑会产生贯通暴击。"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "通关隐藏地图梅山，击败二郎显圣真君与四大天王后铸造"}],
            "version": "1.0.9"
        },
        {
            "name": "混铁棍",
            "type": "神珍兵刃",
            "rarity": 5,
            "icon_url": "https://image.gcores.com/wukong_weapon_huntiegun.png",
            "base_atk_curve": [
                {"level": "获得面板", "atk": 110, "crit_rate": "0%", "def": 40},
                {"level": "防御转化后", "atk": 230, "crit_rate": "0%", "def": 40}
            ],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "神珍",
                    "基础攻击力": 110,
                    "防御力": "+40",
                    "独门妙用": "根据防御力的高低按比例大幅提升攻击力与受击霸体！防御堆至 400+ 时攻击力超越一切神兵。",
                    "典故": "牛魔王随身重兵，刚硬无比，势不可挡。"
                }
            },
            "refinements": [
                {"rank": "独门妙用 (防御转攻击)", "desc": "自身防御力的 30% 转化为等额面板攻击力。堆防即堆伤，容错率与爆发登峰造极。"}
            ],
            "ascension_materials": [{"tier": "获取方式", "items": "第五回击败火焰山牛魔王，集齐大力铁角铸造"}],
            "version": "1.0.9"
        },
        {
            "name": "昆棍·通天",
            "type": "神珍兵刃",
            "rarity": 5,
            "icon_url": "https://image.gcores.com/wukong_weapon_kungun.png",
            "base_atk_curve": [{"level": "获得面板", "atk": 140, "crit_rate": "9%", "def": 0}],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "神珍",
                    "基础攻击力": 140,
                    "暴击率": "+9%",
                    "独门妙用": "蓄力重棍命中时引发全场剧毒爆裂，造成百分比真实毒伤。",
                    "典故": "盘丝岭百眼魔君与千足虫百毒凝炼之天工神物。"
                }
            },
            "refinements": [{"rank": "独门妙用", "desc": "蓄力重棍击中附带剧毒的目标时引爆毒素，造成大范围百分比真实伤害。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "通关第四回紫云山，击败晦月魔君与百眼魔君获取金花玉萼铸造"}],
            "version": "1.0.9"
        },
        {
            "name": "飞龙宝杖",
            "type": "神珍兵刃",
            "rarity": 5,
            "icon_url": "https://image.gcores.com/wukong_weapon_feilong.png",
            "base_atk_curve": [{"level": "获得面板", "atk": 108, "crit_rate": "0%", "def": 0}],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "神珍",
                    "基础攻击力": 108,
                    "独门妙用": "大幅提升立棍伤害；蓄力施展江海翻下砸时，引动九天神雷轰顶造成大范围雷蛰麻痹。",
                    "典故": "黄风大圣击杀灵吉菩萨座下飞龙所得之龙脊骨杖。"
                }
            },
            "refinements": [{"rank": "独门妙用", "desc": "立棍风云转与江海翻伤害提升 25%，下砸附带强力雷电轰鸣。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "击败第二回隐藏 Boss 赤髯龙、小骊龙并完成飞龙铸造"}],
            "version": "1.0.9"
        },
        {
            "name": "狼牙棒",
            "type": "特品兵刃",
            "rarity": 4,
            "icon_url": "https://image.gcores.com/wukong_weapon_langyabang.png",
            "base_atk_curve": [{"level": "获得面板", "atk": 80, "crit_rate": "5%", "def": 0}],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "特品",
                    "基础攻击力": 80,
                    "暴击率": "+5%",
                    "独门妙用": "识破或暴击时额外获得一段棍势并恢复 15 点气力。"
                }
            },
            "refinements": [{"rank": "独门妙用", "desc": "暴击命中敌人迅速回气并充能棍势。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "第三回击败小西天黄眉大王座下黄袍员外与白面妖僧"}],
            "version": "1.0.9"
        },
        {
            "name": "鳞棍·蟠龙",
            "type": "特品兵刃",
            "rarity": 4,
            "icon_url": "https://image.gcores.com/wukong_weapon_panlong.png",
            "base_atk_curve": [{"level": "获得面板", "atk": 70, "crit_rate": "4%", "def": 0}],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "特品",
                    "基础攻击力": 70,
                    "暴击率": "+4%",
                    "独门妙用": "一定程度增加所有蓄力重棍的伤害与破防值。"
                }
            },
            "refinements": [{"rank": "独门妙用", "desc": "蓄力重棍造成的伤害提升 15%。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "击败黑风山赤髯龙后在土地庙铸造"}],
            "version": "1.0.9"
        },
        {
            "name": "几丁棍",
            "type": "特品兵刃",
            "rarity": 4,
            "icon_url": "https://image.gcores.com/wukong_weapon_jidingun.png",
            "base_atk_curve": [{"level": "获得面板", "atk": 80, "crit_rate": "5%", "def": 0}],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "特品",
                    "基础攻击力": 80,
                    "独门妙用": "蓄力重棍击中敌人按伤害百分比吸血生命值，提供超强推图续航。"
                }
            },
            "refinements": [{"rank": "独门妙用", "desc": "四段重棍命中恢复已损失生命值的 20%。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "盘丝岭击败右手虫铸造"}],
            "version": "1.0.9"
        },
        {
            "name": "楮白枪",
            "type": "特品兵刃",
            "rarity": 4,
            "icon_url": "https://image.gcores.com/wukong_weapon_chubaiqiang.png",
            "base_atk_curve": [{"level": "获得面板", "atk": 75, "crit_rate": "0%", "def": 0}],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {
                    "品阶": "特品",
                    "基础攻击力": 75,
                    "独门妙用": "大幅提升戳棍法射程与退寸进尺穿透伤害。"
                }
            },
            "refinements": [{"rank": "独门妙用", "desc": "戳棍退步抽击与突刺伤害提升 20%。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "第三回极乐谷击败亢金星君与小人国支线"}],
            "version": "1.0.9"
        },
        {
            "name": "兽棍·熊罴",
            "type": "特品兵刃",
            "rarity": 4,
            "icon_url": "https://image.gcores.com/wukong_weapon_xiongba.png",
            "base_atk_curve": [{"level": "获得面板", "atk": 65, "crit_rate": "4%", "def": 0}],
            "sub_stat": {
                "stat_name": "兵刃独门妙用",
                "values": {"品阶": "特品", "基础攻击力": 65, "独门妙用": "重棍造成暴击时引发大地震荡波，击退周围杂兵。"}
            },
            "refinements": [{"rank": "独门妙用", "desc": "暴击产生地刺震波。"}],
            "ascension_materials": [{"tier": "获取方式", "items": "第一回击败黑风大王黑熊精获取熊罴之皮铸造"}],
            "version": "1.0.9"
        },
        {
            "name": "柳木棍",
            "type": "凡品兵刃",
            "rarity": 3,
            "icon_url": "https://image.gcores.com/wukong_weapon_liumugun.png",
            "base_atk_curve": [{"level": "初始面板", "atk": 30, "crit_rate": "0%", "def": 0}],
            "sub_stat": {
                "stat_name": "初入江湖木棍",
                "values": {"品阶": "凡品", "基础攻击力": 30, "独门妙用": "天命人初入花果山降妖除魔初始兵刃。"}
            },
            "refinements": [{"rank": "基础性能", "desc": "平平无奇的柳木长棍，韧性尚佳。"}],
            "ascension_materials": [{"tier": "初始获得", "items": "开局自带"}],
            "version": "1.0.9"
        }
    ]

def get_wukong_armors():
    """构建黑神话：悟空 核心披挂套装与词缀体系"""
    return [
        {
            "name": "大圣套装 (The Great Sage Set)",
            "rarity_min": 5, "rarity_max": 5,
            "icon_url": "https://image.gcores.com/wukong_armor_dasheng.png",
            "two_piece_bonus": "【神珍定海】使出切手技时获得霸体，并在短时间内大幅提高防御力与全属性抗性。",
            "four_piece_bonus": "【齐天大圣】集齐大圣神兵与披挂，进入齐天大圣形态！蓄力达到四段棍势时蜕变为齐天大圣神威，攻击附带毁天灭地的神力震波并大幅回复气力。",
            "pieces": [
                {"slot": "头冠", "name": "凤翅紫金冠", "main_stat_rule": "防御力 +48 | 暴击率 +4% | 火焚/雷蛰抗性 +8"},
                {"slot": "衣甲", "name": "锁子黄金甲", "main_stat_rule": "防御力 +96 | 伤害减免 +10% | 四灾全抗性 +16"},
                {"slot": "臂甲", "name": "点翠飞龙釬", "main_stat_rule": "防御力 +32 | 攻击力 +15 | 气力消耗降低 8%"},
                {"slot": "腿甲", "name": "藕丝步云履", "main_stat_rule": "防御力 +38 | 移速提高 10% | 翻滚气力降低 15%"}
            ],
            "rules_reference": {
                "type": "神珍披挂套装 (Godly Armor Set)",
                "recommended_for": "全流派毕业终极首选，与如意金箍棒绝配，激活大圣动作模组"
            },
            "version": "1.0.9"
        },
        {
            "name": "赭黄套装 (Ochre Armor Set)",
            "rarity_min": 4, "rarity_max": 4,
            "icon_url": "https://image.gcores.com/wukong_armor_zhehuang.png",
            "two_piece_bonus": "消耗棍势时获得高额伤害减免，消耗段数越多减免越高（4段减免高达 40%）。",
            "four_piece_bonus": "化身技或聚形散气解除瞬间，短时间内造成的所有伤害提升 25%，若破隐攻击暴击则返还消耗的法力值。",
            "pieces": [
                {"slot": "头冠", "name": "赭黄金胄", "main_stat_rule": "防御力 +34 | 气力上限 +15"},
                {"slot": "衣甲", "name": "赭黄密甲", "main_stat_rule": "防御力 +68 | 毒瘴/火焚抗性 +8"},
                {"slot": "臂甲", "name": "赭黄臂甲", "main_stat_rule": "防御力 +24 | 暴击伤害 +12%"},
                {"slot": "腿甲", "name": "赭黄行缠", "main_stat_rule": "防御力 +28 | 闪避气力消耗 -10%"}
            ],
            "rules_reference": {"type": "特品披挂套装", "recommended_for": "隐身潜行流、戳棍法、破隐暴击一拳流"},
            "version": "1.0.9"
        },
        {
            "name": "行者套装 (Pilgrim Set)",
            "rarity_min": 3, "rarity_max": 4,
            "icon_url": "https://image.gcores.com/wukong_armor_xingzhe.png",
            "two_piece_bonus": "奔跑时大幅降低气力消耗（降低 50%）。",
            "four_piece_bonus": "保持疾跑数秒后，天命人脚下生风，下一次破隐或重棍造成的攻击力提升 60%~100%（推图跑图与奔跑蓄力首选神器）！",
            "pieces": [
                {"slot": "头冠", "name": "行者戒箍", "main_stat_rule": "防御力 +20 | 移速提高 5%"},
                {"slot": "衣甲", "name": "行者直裰", "main_stat_rule": "防御力 +40 | 气力恢复速度 +15%"},
                {"slot": "臂甲", "name": "行者护手", "main_stat_rule": "防御力 +14 | 蓄力时间缩短 10%"},
                {"slot": "腿甲", "name": "行者绑腿", "main_stat_rule": "防御力 +18 | 奔跑不耗精力"}
            ],
            "rules_reference": {"type": "特品披挂套装", "recommended_for": "劈棍法奔跑蓄力流、禁字法一拳超人、大地图探索跑图"},
            "version": "1.0.9"
        },
        {
            "name": "乌金套装 (Ebony Gold Set)",
            "rarity_min": 4, "rarity_max": 4,
            "icon_url": "https://image.gcores.com/wukong_armor_wujin.png",
            "two_piece_bonus": "铜头铁臂成功反震后使敌人陷入严重硬直僵直。",
            "four_piece_bonus": "格挡反震成功后立即恢复 1 段棍势，并在前方地面引发火焚烈焰爆炸。",
            "pieces": [
                {"slot": "头冠", "name": "乌金面具", "main_stat_rule": "防御力 +28 | 火焚抗性 +12"},
                {"slot": "衣甲", "name": "乌金铠", "main_stat_rule": "防御力 +56 | 受到火伤降低 20%"},
                {"slot": "臂甲", "name": "乌金臂甲", "main_stat_rule": "防御力 +20 | 反震伤害 +35%"},
                {"slot": "腿甲", "name": "乌金行缠", "main_stat_rule": "防御力 +24 | 霸体持续时间 +20%"}
            ],
            "rules_reference": {"type": "特品披挂套装", "recommended_for": "铜头铁臂拼刀流、高防御反击流"},
            "version": "1.0.9"
        },
        {
            "name": "龙鳞套装 (Dragon Scale Set)",
            "rarity_min": 4, "rarity_max": 4,
            "icon_url": "https://image.gcores.com/wukong_armor_longlin.png",
            "two_piece_bonus": "使出切手技识破时自身处于绝对无敌金身状态，完全不受外部流弹打扰。",
            "four_piece_bonus": "识破成功后立即恢复 1 段棍势并向前方引动雷霆裂地，对大范围首领施加雷蛰易伤状态。",
            "pieces": [
                {"slot": "头冠", "name": "玄铁双角冠", "main_stat_rule": "防御力 +30 | 雷蛰抗性 +15"},
                {"slot": "衣甲", "name": "龙鳞战袍", "main_stat_rule": "防御力 +62 | 识破判定窗口 +0.05s"},
                {"slot": "臂甲", "name": "龙鳞臂甲", "main_stat_rule": "防御力 +22 | 暴击率 +5%"},
                {"slot": "腿甲", "name": "龙鳞履", "main_stat_rule": "防御力 +26 | 雷属性伤害 +15%"}
            ],
            "rules_reference": {"type": "特品披挂套装", "recommended_for": "立棍法与劈棍识破流、飞龙宝杖绝配"},
            "version": "1.0.9"
        },
        {
            "name": "厌火套装 (Yaksha Fiend Set)",
            "rarity_min": 4, "rarity_max": 4,
            "icon_url": "https://image.gcores.com/wukong_armor_yanhuo.png",
            "two_piece_bonus": "生命值越低，攻击力与暴击率越高（残血逆境战神，生命低于 30% 时攻击力提升 35%）。",
            "four_piece_bonus": "残血状态下攻击造成的破防失衡与硬直打断翻倍，化身修罗狂战！",
            "pieces": [
                {"slot": "头冠", "name": "夜叉面具", "main_stat_rule": "防御力 +25 | 暴伤 +15%"},
                {"slot": "衣甲", "name": "厌火战铠", "main_stat_rule": "防御力 +50 | 残血增伤 +25%"},
                {"slot": "臂甲", "name": "厌火臂甲", "main_stat_rule": "防御力 +18 | 暴击率 +8%"},
                {"slot": "腿甲", "name": "厌火行缠", "main_stat_rule": "防御力 +22 | 攻击速度 +10%"}
            ],
            "rules_reference": {"type": "特品披挂套装", "recommended_for": "极限残血刀尖舔血流、速通大神高难度竞速首选"},
            "version": "1.0.9"
        }
    ]

def get_wukong_mechanics():
    """构建黑神话：悟空 5 大底层战斗机制与公式"""
    return [
        {
            "category": "棍势积累与重棍倍率机制 (Focus Multiplier System)",
            "title": "0-4段棍势阶梯成长与终极天火伤害倍率",
            "formula": "最终重棍伤害 = 基础攻击力 × 棍势倍率系数 × (1 + 暴击伤害%) × 防御破防乘区 × (1 + 识破增益% + 披挂词缀增伤%)",
            "parameters": {
                "focus_multipliers": {
                    "0段棍势 (轻击派生)": "100% 伤害基准 (平A伤害)",
                    "1段棍势 (消耗1豆)": "240% 伤害倍率，产生轻度失衡",
                    "2段棍势 (消耗2豆)": "480% 伤害倍率，强行打断普通怪物技能",
                    "3段棍势 (消耗3豆)": "850% 伤害倍率，击倒并破除精英霸体",
                    "4段棍势 (四段天火终极重劈)": "1450% 毁灭倍率，引发全屏地震，强行压制并震翻绝大多数 Boss 首领！"
                },
                "decay_rule": "1~3段棍势在非战斗或停手 5 秒后开始逐渐衰减；第4段棍势若无如意金箍棒独门妙用，将在 8 秒内极速衰减归零。"
            }
        },
        {
            "category": "识破与无敌帧判定机制 (See Through & I-Frame Window)",
            "title": "切手技斩棍式的时间窗口、无敌帧与硬直打断判定",
            "formula": "判定触发条件：在敌方判定框接触天命人受击框前 0.15~0.25 秒内，轻棍连段中输入重击；成功触发金色火花音效并进入 0.6 秒完全无敌帧。",
            "parameters": {
                "window_ms": "判定前摇约 150ms~250ms (佩戴大圣套或龙鳞套可略微放宽至 300ms)",
                "iframe_duration": "成功后获得 0.6 秒无敌帧，免疫包括地面冲击波、远程法术在内的所有判定",
                "hyperarmor_break": "对敌方强霸体首领施加 100% 硬直破防惩罚，打断 Boss 正在蓄力的前摇招式"
            }
        },
        {
            "category": "四灾异常状态与克制机制 (Four Banes: Burn, Chill, Shock, Poison)",
            "title": "火焚、寒冻、雷蛰、毒瘴异常量化与对应法宝克制",
            "formula": "异常累积进度 = 受到对应属性伤害量 / 目标基础四灾抗性值；叠满 100% 后触发灾伤持续效果。",
            "parameters": {
                "fire_burn": "火焚：每秒按目标最大生命值 2.5% 扣除真伤，天命人翻滚 3 次可扑灭；克制法宝【避火罩】。",
                "ice_chill": "寒冻：大幅降低气力恢复速度 60%，叠满后绝对冻结 2.5 秒，受重击触发碎冰额外 40% 伤害。",
                "lightning_shock": "雷蛰：受到所有物理与法术攻击伤害增加 25%，且每次受击产生雷爆连锁伤害；克制法宝【定风珠】与辟雷散。",
                "poison_bane": "毒瘴：持续扣血并在地面留毒，降低移动速度 15%，解毒需饮用定痛膏。"
            }
        },
        {
            "category": "气力消耗与完美闪避机制 (Stamina & Perfect Dodge Mechanics)",
            "title": "绿条耐力恢复公式、极限闪避残影与精力耗尽脱力惩罚",
            "formula": "完美闪避判定：攻击命中前 0.12 秒内输入翻滚闪避，触发时钟慢动作、风声残影与半段棍势恢复。",
            "parameters": {
                "action_stamina_cost": {
                    "轻棍一段": "消耗 15 点气力",
                    "翻滚闪避": "消耗 25 点气力",
                    "疾跑奔突": "每秒消耗 18 点气力",
                    "攀棍滞空": "每秒消耗 12 点气力"
                },
                "exhaustion_penalty": "气力清零后天命人动作变慢无法翻滚闪避，陷入气竭硬直 1.2 秒（极高暴毙风险）！",
                "recovery_rate": "停止消耗后 0.4 秒开始以每秒 60 点的基础速率高速回气。"
            }
        },
        {
            "category": "六根天资觉醒机制 (Six Senses / Relics Inheritance)",
            "title": "眼看喜、耳听怒、鼻嗅爱、舌尝思、身本忧、意见欲周目三阶点法",
            "formula": "六根点数 = 周目通关数 (最多 3 周目激活全部 18 个被动觉醒分支)。",
            "parameters": {
                "sense_1_eye": "眼看喜：【秉意不移】(识破无敌放宽) / 【眼观六路】(识破暴击率+10%) / 【慧眼明彻】(洞察弱点增伤)",
                "sense_2_ear": "耳听怒：【听风辨位】(闪避残影气爆) / 【声如轰雷】(铜头铁臂眩晕) / 【耳根清净】(降低受控时长)",
                "sense_3_nose": "鼻嗅爱：【气随心动】(气力上限与回气+35%) / 【芳气袭人】(化身伤害提升) / 【闻香知味】(药材效果翻倍)",
                "sense_4_tongue": "舌尝思：【含灵化生】(饮酒回气+暴击) / 【留香日久】(酒膏增益时间延长) / 【甘露滋养】(持续回血)",
                "sense_5_body": "身本忧：【金刚不坏】(免死一次) / 【健步如飞】(奔跑速度+15%) / 【皮糙肉厚】(减伤+12%)",
                "sense_6_mind": "意见欲：【胜佛真意】(齐天大圣模式神威终极激活，四段棍势毁天灭地)"
            }
        }
    ]

def sync_all_to_postgres():
    print("=== 开始执行黑神话：悟空 全量数值体系入库同步 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    characters = get_wukong_characters()
    weapons = get_wukong_weapons()
    armors = get_wukong_armors()
    mechanics = get_wukong_mechanics()

    # 1. 写入天命人核心流派与形态 (game_character)
    print(f"\n[1/4] 写入黑神话悟空天命流派 ({len(characters)} 个形态)...")
    for c in characters:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, constellations, passives,
                special_mechanics, recommendations, data_hash, version
            ) VALUES (
                4, %s, %s, %s, %s, %s,
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
                constellations = EXCLUDED.constellations,
                passives = EXCLUDED.passives,
                special_mechanics = EXCLUDED.special_mechanics,
                recommendations = EXCLUDED.recommendations,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['constellations']), Json(c['passives']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))
    print(f"  ✓ 成功落库 {len(characters)} 个黑神话流派形态！")

    # 2. 写入神珍兵刃 (game_weapon)
    print(f"\n[2/4] 写入黑神话悟空神珍/特品兵刃 ({len(weapons)} 件)...")
    for w in weapons:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                4, %s, %s, %s, %s, %s,
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
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(w['base_atk_curve']),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))
    print(f"  ✓ 成功落库 {len(weapons)} 件兵刃！")

    # 3. 写入披挂套装 (game_artifact_set)
    print(f"\n[3/4] 写入黑神话悟空披挂套装 ({len(armors)} 套)...")
    for art in armors:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                4, %s, %s, %s, %s,
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
    print(f"  ✓ 成功落库 {len(armors)} 套披挂防具！")

    # 4. 写入战斗机制与公式 (game_mechanic_rule)
    print(f"\n[4/4] 写入黑神话悟空底层战斗机制与公式 ({len(mechanics)} 条)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                4, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))
    print(f"  ✓ 成功落库 {len(mechanics)} 项底层战斗机制！")

    conn.commit()
    conn.close()
    print("\n=== 黑神话：悟空全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_all_to_postgres()
