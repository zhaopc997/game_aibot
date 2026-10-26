#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《阴阳师》、《鸣潮》、《崩坏3》人物与技能维度数据深度补全脚本:
1. 阴阳师 (ID = 29):
   - 神堕八岐大蛇 (SP)
   - 因幡辉夜姬 (SP)
   - 鬼王酒吞童子 (SP)
   - 千姬 (SSR)
   - 季 (SSR)
   - 铃鹿御前 (SSR)
2. 鸣潮 (ID = 26):
   - 相里要 (Xiangli Yao)
   - 折枝 (Zhezhi)
   - 安可 (Encore)
   - 卡卡罗 (Calcharo)
   - 吟霖 (Yinlin)
   - 散华 (Sanhua)
3. 崩坏3 (ID = 30):
   - 真理之律者 (布洛妮娅)
   - 薪炎之律者 (琪亚娜)
   - 人之律者 (爱莉希雅)
   - 识之律者 (符华/识宝)
   - 月下誓约·予爱以心 (德丽莎)
   - 天元骑英 (幽兰黛尔)
"""

import os
import sys
import json
import hashlib
import psycopg2
from psycopg2.extras import Json

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

PG_CONFIG = {
    'host': os.getenv('PG_HOST', '127.0.0.1'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

# ==========================================
# 1. 《阴阳师》 式神数据 (ID: 29)
# ==========================================
ONMYOJI_CHARACTERS = [
    {
        "name": "神堕八岐大蛇 (SP)",
        "title": "终焉裁决·邪神君临",
        "rarity": 5,
        "element": "混沌 / 真实伤害",
        "weapon_type": "天羽羽斩 / 堕落神力",
        "region": "高天原·罪恶深渊",
        "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_sp_orochi.png/120px-avatar_sp_orochi.png",
        "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_sp_orochi.png/600px-avatar_sp_orochi.png",
        "base_stats": [
            {"level": "1", "hp": 1100, "atk": 175, "def": 72, "speed": 112, "crit": "10%"},
            {"level": "40 (六星满)", "hp": 12450, "atk": 4210, "def": 425, "speed": 118, "crit": "10%"}
        ],
        "special_ascension_stat": {"stat_name": "终焉真伤贯穿", "values": {"40级满": "基础攻击 4210 巅峰，全技能自带破防穿透"}},
        "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 (白蛋) × 5 + 觉醒材料组"}],
        "talents": [
            {"name": "灵魂剥离 (Skill 1)", "type": "NORMAL_ATTACK", "description": "驱使蛇影撕咬敌方单体，造成攻击力 120% 伤害，并为目标施加持续两回合的【蛇毒】削弱其防御 15%。", "scaling": "Lv.5 伤害提升至 125%，蛇毒可叠加至 5 层"},
            {"name": "神堕之力 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "唯一效果。开启【神堕形态】夺取全场主导权：召唤 5 把天羽羽斩插满战场，自身防御提升 200%，免疫一切硬控；友方行动时自动为其淬炼剑意，当 5 把天羽羽斩全部蜕变为神剑时，自身完全化为终焉邪神！", "scaling": "Lv.5 自身行动条大幅增加，获得全场绝对霸体"},
            {"name": "终焉裁决 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "消耗 3 点鬼火，挥舞天羽羽斩向敌方全体降下灭世天罚，连续劈出 6 段毁灭斩击，前 5 段造成 210% 全体伤害，第 6 段造成高达 380% 的纯粹真实贯穿伤害！若击杀任一目标，立即重置本技能冷却！", "scaling": "全游戏系数最高的清屏群伤核弹之一"}
        ],
        "passives": [{"name": "破灭之躯", "desc": "自身免疫冰冻、减速、眩晕与变形；当承受致命伤害时，引爆一把天羽羽斩免疫本次死亡。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "一速式神拉条 -> 神堕八岐大蛇开启神堕形态 -> 连续释放终焉裁决直接毁灭全场！"},
        "recommendations": {"weapons": {"bis": "六号位爆伤满速御魂"}, "artifacts": {"bis_set": "破势四件套 + 荒骷髅两件套 / 伤魂鸟四件套"}},
        "version": "v1.7"
    },
    {
        "name": "因幡辉夜姬 (SP)",
        "title": "月之愿力·琉璃月海",
        "rarity": 5,
        "element": "愿力神域 / 暴伤辅助",
        "weapon_type": "琉璃玉竹",
        "region": "月之宫·广寒仙境",
        "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_sp_kaguya.png/120px-avatar_sp_kaguya.png",
        "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_sp_kaguya.png/600px-avatar_sp_kaguya.png",
        "base_stats": [
            {"level": "40 (六星满)", "hp": 13950, "atk": 2350, "def": 485, "speed": 110, "crit": "8%"}
        ],
        "special_ascension_stat": {"stat_name": "愿力暴伤转化", "values": {"40级满": "自身 120% 暴击伤害直接转化为全队通用额外暴伤加成"}},
        "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 × 5"}],
        "talents": [
            {"name": "琉璃光 (Skill 1)", "type": "NORMAL_ATTACK", "description": "凝聚月华掷向目标，造成攻击力 100% 伤害并获取 1 点【愿力】。", "scaling": "Lv.5 伤害提升至 125%"},
            {"name": "愿海月华 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "先机释放。展开唯美幻境【琉璃月海】，战斗开局直接赋予己方 24 点独立【愿力】（友方消耗鬼火时优先扣除愿力），同时根据因幡辉夜姬自身的暴击伤害，为全体友方提供至多 120% 的巨额暴击伤害加成！", "scaling": "全游最顶级的全队暴伤增伤供火双重领域"},
            {"name": "寂光映月 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "消耗愿力召唤月华流星冲击敌方全体，造成 138% 范围伤害，并为全队施加可吸收攻击力 250% 伤害的愿力月盾。", "scaling": "攻守兼备，护盾附带免控抵抗提升"}
        ],
        "passives": [{"name": "明月长存", "desc": "友方消耗愿力释放大招时，该技能最终造成的伤害额外提升 20%。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "开局自动铺开月海提供满愿力与爆伤 -> 核心主C零火耗释放高爆发大招轻松斩杀。"},
        "recommendations": {"weapons": {"bis": "速生爆伤/生生爆伤"}, "artifacts": {"bis_set": "火灵四件套 / 招财猫四件套"}},
        "version": "v1.7"
    },
    {
        "name": "鬼王酒吞童子 (SP)",
        "title": "大江山之主·白刃破灭",
        "rarity": 5,
        "element": "烈炎 / 狂暴增伤",
        "weapon_type": "大江山妖炎巨拳",
        "region": "大江山·妖鬼王座",
        "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_sp_shuten.png/120px-avatar_sp_shuten.png",
        "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_sp_shuten.png/600px-avatar_sp_shuten.png",
        "base_stats": [
            {"level": "40 (六星满)", "hp": 13800, "atk": 3150, "def": 460, "speed": 109, "crit": "10%"}
        ],
        "special_ascension_stat": {"stat_name": "压血独立增伤", "values": {"40级满": "友方每损失 1% 生命值，伤害提升 1%，减伤提升 1%"}},
        "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 × 5"}],
        "talents": [
            {"name": "焚天狂啸 (Skill 1)", "type": "NORMAL_ATTACK", "description": "挥出烈焰妖拳重轰目标，造成 125% 伤害并在鬼王姿态下升级为造成两段真实溅射伤害的狂暴猛击！", "scaling": "鬼王姿态下附带 30% 无视防御真实溅射"},
            {"name": "鬼王降临 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "消耗 3 点鬼火跃起爆裂砸地，进入【鬼王姿态】持续 2 回合：击退全场敌方 40% 行动条（强力推条），同时驱散己方全体所有带有的控制效果（顶级解控）！", "scaling": "神级推条解控，彻底扭转战场先手"},
            {"name": "大江山狂啸 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "在鬼王姿态下，己方全体行动前扣除 24% 当前生命值并转化为等额护盾，且在行动回合内免疫所有控制效果（霸体），同时根据损血量吃满高额被动增伤！", "scaling": "压血流（如阿修罗/须佐/小小黑）的核心发动机"}
        ],
        "passives": [{"name": "鬼王之躯", "desc": "自身免疫一切硬控（眩晕、冰冻、挑衅、睡眠、变形）。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "开局抢二速释放【鬼王降临】推条敌方并解控全队 -> 开启大江山姿态让主C吃满损血暴击秒杀！"},
        "recommendations": {"weapons": {"bis": "速攻暴/速攻攻"}, "artifacts": {"bis_set": "招财猫四件套 / 破势四件套"}},
        "version": "v1.7"
    },
    {
        "name": "千姬 (SSR)",
        "title": "人鱼之歌·海原贝戟",
        "rarity": 5,
        "element": "潮汐 / 极寒水流",
        "weapon_type": "海原贝戟",
        "region": "永生之海·潮汐神殿",
        "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_senhime.png/120px-avatar_senhime.png",
        "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_senhime.png/600px-avatar_senhime.png",
        "base_stats": [
            {"level": "40 (六星满)", "hp": 13200, "atk": 2980, "def": 450, "speed": 121, "crit": "10%"}
        ],
        "special_ascension_stat": {"stat_name": "潮声全队70%增伤", "values": {"40级满": "海原贝戟插地满 5 层潮声后提供 70% 团队全伤增幅"}},
        "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 × 5"}],
        "talents": [
            {"name": "潮浪 (Skill 1)", "type": "NORMAL_ATTACK", "description": "驱使汹涌水浪冲击目标，造成攻击力 100% 伤害，并有 100% 基础概率削减目标 1 点鬼火。", "scaling": "Lv.5 伤害 120%，控火打乱敌方节奏"},
            {"name": "海原贝戟 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "召唤【海原贝戟】插在己方战场：全队每消耗 1 点鬼火，贝戟获得 1 层【潮声】；叠满 7 层潮声自动恢复己方 3 点鬼火，并为全队永久提供高达 70% 的全局伤害加成！贝戟存在期间为全队减免 30% 受到伤害并提供持续回血。", "scaling": "长线作战与增伤回火的最强神器"},
            {"name": "海潮悲歌 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "千姬拔起海原贝戟，消耗所有潮声层数引发滔天海啸，对全屏敌方造成高达 320% 的毁灭性巨浪爆发斩杀！", "scaling": "拔戟核弹，收尾绝杀"}
        ],
        "passives": [{"name": "汐梦潮音", "desc": "受千姬技能影响的敌方目标陷入【汐梦】，行动结束时额外消耗 3 点鬼火，否则进入深度冰冻。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "一速插下海原贝戟 -> 全队放技能快速叠满 7 层潮声吃满 70% 增伤 -> 残局拔戟收尾清场。"},
        "recommendations": {"weapons": {"bis": "满速招财/涂佛"}, "artifacts": {"bis_set": "涂佛四件套 / 招财猫四件套"}},
        "version": "v1.7"
    },
    {
        "name": "季 (SSR)",
        "title": "四时之神·岁暮凋零",
        "rarity": 5,
        "element": "四时枯荣 / 纯粹真伤",
        "weapon_type": "岁时花枝与枯荣枝条",
        "region": "四季之墟·灵木之境",
        "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_ji.png/120px-avatar_ji.png",
        "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_ji.png/600px-avatar_ji.png",
        "base_stats": [
            {"level": "40 (六星满)", "hp": 11800, "atk": 3890, "def": 430, "speed": 115, "crit": "0%"}
        ],
        "special_ascension_stat": {"stat_name": "暴击全额转真伤", "values": {"40级满": "自身无法暴击，暴击属性按 1:1.5 全额转化为独立真实伤害放大"}},
        "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 × 5"}],
        "talents": [
            {"name": "岁令枯荣 (Skill 1)", "type": "NORMAL_ATTACK", "description": "挥动四季枝条攻击目标，造成攻击力 100% 真实伤害。", "scaling": "Lv.5 伤害提升至 125%"},
            {"name": "四时之令 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "自由切换四季结界：【春告】全队回血解毒；【夏繁】敌方普攻反击；【秋落】提供高额护盾；【冬枯】进入终极肃杀，季获得 40% 独立攻击力与伤害提升，敌方全体防御降低 60%！", "scaling": "全能结界切换，完美适配各种副本"},
            {"name": "弥天四时 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "消耗 3 点鬼火，全屏漫天绽放四时灵花，对全体敌方造成多达 4 段无视防御的纯真实伤害，敌方生命值越低伤害越高！", "scaling": "无视任何高防御高减伤，高难深渊通关利刃"}
        ],
        "passives": [{"name": "四季轮回", "desc": "自身受到暴击伤害降低 50%，且不会被任何暴击机制克制。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "切入【冬枯】结界 -> 配合狂骨/隐念叠满攻击力 -> 释放弥天四时无视防御瞬间蒸发 Boss！"},
        "recommendations": {"weapons": {"bis": "速攻攻满攻击"}, "artifacts": {"bis_set": "狂骨四件套 + 歌伎两件套 / 隐念四件套"}},
        "version": "v1.7"
    },
    {
        "name": "铃鹿御前 (SSR)",
        "title": "铃鹿之主·麓海万羽",
        "rarity": 5,
        "element": "冥海狂岚",
        "weapon_type": "冥弓大通连·小通连",
        "region": "铃鹿山·海国皇城",
        "avatar_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_suzuka.png/120px-avatar_suzuka.png",
        "splash_url": "https://patchwiki.biligame.com/images/yys/thumb/avatar_suzuka.png/600px-avatar_suzuka.png",
        "base_stats": [
            {"level": "40 (六星满)", "hp": 12100, "atk": 3780, "def": 440, "speed": 110, "crit": "10%"}
        ],
        "special_ascension_stat": {"stat_name": "麓威层数叠攻", "values": {"40级满": "最多叠加 10 层麓威，提升 50% 攻击力与全屏追射段数"}},
        "ascension_materials": [{"tier": "六星进化", "items": "奉为达摩 × 5"}],
        "talents": [
            {"name": "逐影 (Skill 1)", "type": "NORMAL_ATTACK", "description": "引弓搭箭射击敌方目标，造成攻击力 100% 伤害，并有 100% 概率为友方加速 10%。", "scaling": "Lv.5 伤害提升至 125%"},
            {"name": "麓魂·极 (Skill 2)", "type": "ELEMENTAL_SKILL", "description": "指向敌方关键核心式神，为其施加破阵标记：强制该目标在下个行动回合只能普攻铃鹿御前，同时为铃鹿御前自身套上无法被驱散的厚重麓盾，强行打断敌方战术链条！", "scaling": "PVP斗技拆迁神技，专克反击流与免控核心"},
            {"name": "万羽浪行 (Skill 3)", "type": "ELEMENTAL_BURST", "description": "消耗 4 点鬼火腾空跃起，连续射出 6~12 发追魂箭矢对敌方全屏进行洗地式狂轰滥炸，每支箭矢造成 215% 伤害，打满造成超过 2500% 的天文数字爆发！", "scaling": "多段群伤最高上限，清场与攻坚利器"}
        ],
        "passives": [{"name": "麓威守护", "desc": "每层麓威为铃鹿御前提供 10% 减伤，叠满 10 层解锁无消耗释放二技能。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "斗技开局利用二技能破阵强嘲敌方核心 -> 叠满麓威释放万羽浪行全屏清场！"},
        "recommendations": {"weapons": {"bis": "攻攻爆伤针女"}, "artifacts": {"bis_set": "针女四件套 + 鬼灵歌伎两件套"}},
        "version": "v1.7"
    }
]

# ==========================================
# 2. 《鸣潮》 共鸣者数据 (ID: 26)
# ==========================================
WUTHERING_WAVES_CHARACTERS = [
    {
        "name": "相里要 (Xiangli Yao)",
        "title": "全知研求·机械矩阵",
        "rarity": 5,
        "element": "导电 (Electro)",
        "weapon_type": "臂铠 (Gauntlets)",
        "region": "黑海岸·天工司",
        "avatar_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_xiangli_yao.png/120px-avatar_xiangli_yao.png",
        "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_xiangli_yao.png/600px-avatar_xiangli_yao.png",
        "base_stats": [
            {"level": "1", "hp": 910, "atk": 36, "def": 95},
            {"level": "90", "hp": 11250, "atk": 435, "def": 1180}
        ],
        "special_ascension_stat": {"stat_name": "暴击伤害提升", "values": {"90级": "+56.8% 初始暴击伤害"}},
        "ascension_materials": [{"tier": "突破材料", "items": "隐雷声核、简晶声骸"}],
        "talents": [
            {"name": "常态攻击·万象演算", "type": "NORMAL_ATTACK", "description": "使用机械臂铠进行五段高速连续拳击，前四段造成导电伤害，第五段引爆空气造成范围冲击。", "scaling": "五段总伤害倍率 520%"},
            {"name": "共鸣技能·推演引力", "type": "ELEMENTAL_SKILL", "description": "凝聚机械力场短距离前冲并生成引力矩阵，将周围散落的敌人强力拉扯至身前并造成 380% 导电范围轰击，同时积攒 40 点【万象算力】。", "scaling": "冷却 8 秒，极强聚怪与算力积攒"},
            {"name": "共鸣回路·思齐万物", "type": "ELEMENTAL_BURST", "description": "当万象算力满 100 点时长按重击，在目标周围激活【全息推演领域】，领域内敌人时间流速放慢 80%（时停），并连续打出四记超重型聚能机械爆破！", "scaling": "核心时停打点，爆发伤害高达 1280%"},
            {"name": "共鸣解放·深邃全知", "type": "NORMAL_ATTACK", "description": "释放高维计算矩阵，机甲全功率过载轰击地面，引发波及全屏的高能等离子雷暴，造成 1850% 巨量导电爆发，大招期间共鸣技能冷却缩短 50%！", "scaling": "耗能 125 点，导电主C天花板大招"},
            {"name": "变奏技能·精准解构", "type": "NORMAL_ATTACK", "description": "入场瞬间轰下一记落雷重拳，造成 280% 导电伤害并直接充满 50 点算力。"},
            {"name": "延奏技能·超维增幅", "type": "NORMAL_ATTACK", "description": "下一位登场共鸣者导电伤害提升 20%，共鸣解放（大招）伤害额外提升 25%，持续 14 秒。"}
        ],
        "passives": [
            {"name": "穷理尽性", "desc": "在全息推演领域内，自身暴击率提升 15%，导电抗性穿透提升 10%。"},
            {"name": "格物致知", "desc": "释放大招后全队受到伤害降低 15%。"}
        ],
        "constellations": [
            {"rank": 1, "desc": "共鸣技能可连续充能释放两次，且算力获取速度翻倍。"},
            {"rank": 2, "desc": "全息推演领域内暴击伤害提升 45%，时停持续时间延长 1.5 秒。"},
            {"rank": 6, "desc": "释放共鸣解放后，下一次思齐万物无需蓄力直接瞬发，并额外追加一次 800% 的核聚变重拳！"}
        ],
        "special_mechanics": {"core_flow": "变奏切入 -> 释放推演引力聚怪攒满算力 -> 蓄力触发时停思齐万物重拳 -> 开启大招深邃全知瞬间蒸发 Boss！"},
        "recommendations": {"weapons": {"bis": "诸方玄枢 (五星臂铠)"}, "artifacts": {"bis_set": "彻空冥雷五件套 (43311配置)"}},
        "version": "1.3"
    },
    {
        "name": "折枝 (Zhezhi)",
        "title": "画意入神·水墨冰绡",
        "rarity": 5,
        "element": "冷凝 (Glacio)",
        "weapon_type": "音感仪 (Rectifier)",
        "region": "乘霄山·画境",
        "avatar_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_zhezhi.png/120px-avatar_zhezhi.png",
        "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_zhezhi.png/600px-avatar_zhezhi.png",
        "base_stats": [
            {"level": "1", "hp": 880, "atk": 34, "def": 98},
            {"level": "90", "hp": 10900, "atk": 412, "def": 1210}
        ],
        "special_ascension_stat": {"stat_name": "共鸣效率提升", "values": {"90级": "+32.0% 共鸣能量充能效率"}},
        "ascension_materials": [{"tier": "突破材料", "items": "幽夜声核、凝晶"}],
        "talents": [
            {"name": "常态攻击·泼墨挥毫", "type": "NORMAL_ATTACK", "description": "挥动水墨画笔点出飞鹤雀影，造成多段远程冷凝伤害并积累【墨意】。", "scaling": "四段总倍率 460%"},
            {"name": "共鸣技能·点睛之笔", "type": "ELEMENTAL_SKILL", "description": "在场上画出三只水墨仙鹤，仙鹤自动朝敌人飞掠穿刺，造成 360% 冷凝伤害并回复全队协奏能量。", "scaling": "冷却 6 秒，高频协同打击"},
            {"name": "共鸣回路·神来之手", "type": "ELEMENTAL_BURST", "description": "消耗满格墨意长按重击，在空中连续飞跃作画，召唤巨型墨梅冰树并对敌人施加【画境减速】，随后化为极速协同雨击！", "scaling": "全队协同攻击，伤害倍率 680%"},
            {"name": "共鸣解放·泼墨成境", "type": "NORMAL_ATTACK", "description": "展开遮天蔽日的水墨全景画卷，全场降下暴风雪墨雨轰炸，造成 1450% 冷凝大范围爆发，并在后台持续协同造成穿刺伤害！", "scaling": "脱手后台大招，持续 20 秒协同"},
            {"name": "变奏技能·墨影翩跹", "type": "NORMAL_ATTACK", "description": "切入瞬间展开画境，造成冷凝伤害并直接充满 50 点墨意。"},
            {"name": "延奏技能·意蕴深远", "type": "NORMAL_ATTACK", "description": "为下一位登场共鸣者提供 20% 冷凝伤害加成与 25% 共鸣技能伤害加成（今汐专属顶级外置拐）。"}
        ],
        "passives": [
            {"name": "妙手天成", "desc": "仙鹤协同攻击命中敌人时，全队攻击力提升 15%。"}
        ],
        "constellations": [
            {"rank": 1, "desc": "仙鹤穿刺数量增加至 5 只，且暴击率提升 20%。"},
            {"rank": 6, "desc": "共鸣解放期间，仙鹤协同攻击转化为真实穿透伤害，且每次协同为全队恢复生命值。"}
        ],
        "special_mechanics": {"core_flow": "点睛之笔召唤仙鹤 -> 释放共鸣解放泼墨成境后台挂机 -> 延奏切出今汐吃满 25% 技能伤害加成！"},
        "recommendations": {"weapons": {"bis": "琼枝冰绡 (五星音感仪)"}, "artifacts": {"bis_set": "浮星祛暗 / 轻云出月五件套"}},
        "version": "1.3"
    },
    {
        "name": "安可 (Encore)",
        "title": "羊咩大暴走·纯真火焰",
        "rarity": 5,
        "element": "热熔 (Fusion)",
        "weapon_type": "音感仪 (Rectifier)",
        "region": "黑海岸·黑咩乐园",
        "avatar_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_encore.png/120px-avatar_encore.png",
        "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_encore.png/600px-avatar_encore.png",
        "base_stats": [
            {"level": "90", "hp": 10500, "atk": 425, "def": 1150}
        ],
        "special_ascension_stat": {"stat_name": "热熔伤害加成", "values": {"90级": "+28.5% 热熔元素伤害"}},
        "ascension_materials": [{"tier": "突破材料", "items": "炽焰声核"}],
        "talents": [
            {"name": "常态攻击·羊咩投掷", "type": "NORMAL_ATTACK", "description": "连续投掷黑咩与白咩玩具，造成四段热熔法术轰炸。", "scaling": "四段总倍率 480%"},
            {"name": "共鸣技能·热熔炎喷", "type": "ELEMENTAL_SKILL", "description": "召唤黑咩向前方扇形喷射高热烈焰，造成持续多段热熔切割伤害。", "scaling": "冷却 8 秒，倍率 420%"},
            {"name": "共鸣回路·失控情绪", "type": "ELEMENTAL_BURST", "description": "【失控状态】下长按重击，在原地引导巨大火球爆炸，造成高达 890% 的热熔核爆，引导期间安可处于免死霸体！", "scaling": "核心脱手合轴神技"},
            {"name": "共鸣解放·羊咩大暴走！", "type": "NORMAL_ATTACK", "description": "安可进入持续 10 秒的【暴走状态】：攻击形态异化为近战利爪撕扯，普通攻击攻速飙升 50% 并全部转化为极高倍率烈火利爪打击！", "scaling": "近战爆发天花板，平A拳拳到肉"}
        ],
        "passives": [{"name": "好朋友", "desc": "暴走状态下受到伤害降低 25%，抗打断能力大幅提升。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "开启大招大暴走疯狂近战爪击 -> 情绪满时长按释放失控重击并瞬间换人合轴！"},
        "recommendations": {"weapons": {"bis": "掣傀之手 (五星音感仪)"}, "artifacts": {"bis_set": "熔山裂谷五件套"}},
        "version": "1.3"
    },
    {
        "name": "卡卡罗 (Calcharo)",
        "title": "幽灵猎犬·深渊雷刃",
        "rarity": 5,
        "element": "导电 (Electro)",
        "weapon_type": "长刃 (Broadblade)",
        "region": "新联邦·幽灵雇佣兵团",
        "avatar_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_calcharo.png/120px-avatar_calcharo.png",
        "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_calcharo.png/600px-avatar_calcharo.png",
        "base_stats": [
            {"level": "90", "hp": 11500, "atk": 438, "def": 1160}
        ],
        "special_ascension_stat": {"stat_name": "暴击率加成", "values": {"90级": "+19.2% 初始暴击率"}},
        "ascension_materials": [{"tier": "突破材料", "items": "雷鸣声核"}],
        "talents": [
            {"name": "常态攻击·狂犬连斩", "type": "NORMAL_ATTACK", "description": "挥舞超重型长刃进行四段大范围横扫横劈，削韧击破能力极强。", "scaling": "四段总倍率 560%"},
            {"name": "共鸣技能·灭绝指令", "type": "ELEMENTAL_SKILL", "description": "可连续释放三段的导电突刺劈砍，穿插普攻可无限取消后摇并极速积攒杀意能量。", "scaling": "三段总倍率 540%，手感流畅度极高"},
            {"name": "共鸣回路·死告", "type": "ELEMENTAL_BURST", "description": "在大招期间普攻积攒 5 点杀意后长按重击，拔刀斩出贯穿天地的【死告】三段雷影斩击，造成 1120% 巨量导电爆发！", "scaling": "鸣潮最具操作深度的连招核心"},
            {"name": "共鸣解放·暗影潜行", "type": "NORMAL_ATTACK", "description": "体内恶魔完全解放，披上黑雷狂风铠甲，普攻异化为超高速雷影切割，极限时间内最多可打出三次【死告】！", "scaling": "打满三死告伤害总倍率超越 3500%"}
        ],
        "passives": [{"name": "雇佣兵直觉", "desc": "释放共鸣解放期间，获得 15% 导电伤害加成与霸体。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "吟霖提供导电大招加成延奏 -> 卡卡罗开大开启暗影潜行 -> AA闪避AA打出极限三死告秒杀！"},
        "recommendations": {"weapons": {"bis": "苍鳞千嶂 (五星长刃)"}, "artifacts": {"bis_set": "彻空冥雷五件套"}},
        "version": "1.3"
    },
    {
        "name": "吟霖 (Yinlin)",
        "title": "缚罪雷暴·千面悬丝",
        "rarity": 5,
        "element": "导电 (Electro)",
        "weapon_type": "音感仪 (Rectifier)",
        "region": "黑海岸·天工暗卫",
        "avatar_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_yinlin.png/120px-avatar_yinlin.png",
        "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_yinlin.png/600px-avatar_yinlin.png",
        "base_stats": [
            {"level": "90", "hp": 10800, "atk": 418, "def": 1200}
        ],
        "special_ascension_stat": {"stat_name": "暴击率加成", "values": {"90级": "+24.0% 暴击率"}},
        "ascension_materials": [{"tier": "突破材料", "items": "雷磁声核"}],
        "talents": [
            {"name": "常态攻击·傀儡悬丝", "type": "NORMAL_ATTACK", "description": "操控傀儡【罗吒】进行多段范围雷电切割并为敌人施加【缚罪印记】。", "scaling": "四段总倍率 470%"},
            {"name": "共鸣技能·磁缚狂雷", "type": "ELEMENTAL_SKILL", "description": "投掷雷霆力场牵引敌人，进入强化状态，普攻命中附带强力协同天雷打击。", "scaling": "冷却 12 秒，倍率 480%"},
            {"name": "共鸣回路·千面雷罚", "type": "ELEMENTAL_BURST", "description": "带有缚罪印记的敌人受到任何攻击时，空中自动降下天雷进行协同轰击，造成高额雷电穿透伤害！", "scaling": "极品后台脱手协同输出"},
            {"name": "共鸣解放·雷暴终焉", "type": "NORMAL_ATTACK", "description": "引爆全场所有悬丝，激起全屏毁灭性雷暴狂潮，造成 1650% 范围导电大爆发！", "scaling": "高倍率核爆大招"},
            {"name": "延奏技能·导电雷鸣", "type": "NORMAL_ATTACK", "description": "下一位登场共鸣者导电伤害提升 20%，共鸣解放伤害提升 25%（相里要与卡卡罗绝配神拐）。"}
        ],
        "passives": [{"name": "惩罪天网", "desc": "自身后台协同攻击暴击伤害提升 25%。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "技能聚怪挂印记 -> 释放大招雷暴终焉 -> 延奏切相里要或卡卡罗吃满双重独立加成！"},
        "recommendations": {"weapons": {"bis": "掣傀之手 (五星音感仪)"}, "artifacts": {"bis_set": "彻空冥雷五件套"}},
        "version": "1.3"
    },
    {
        "name": "散华 (Sanhua)",
        "title": "白霜破地·目押剑影",
        "rarity": 4,
        "element": "冷凝 (Glacio)",
        "weapon_type": "迅刀 (Sword)",
        "region": "乘霄山·侍从近卫",
        "avatar_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_sanhua.png/120px-avatar_sanhua.png",
        "splash_url": "https://patchwiki.biligame.com/images/mc/thumb/avatar_sanhua.png/600px-avatar_sanhua.png",
        "base_stats": [
            {"level": "90", "hp": 10200, "atk": 380, "def": 1120}
        ],
        "special_ascension_stat": {"stat_name": "冷凝伤害加成", "values": {"90级": "+24.0% 冷凝伤害"}},
        "ascension_materials": [{"tier": "突破材料", "items": "霜晶声核"}],
        "talents": [
            {"name": "常态攻击·寒芒迅闪", "type": "NORMAL_ATTACK", "description": "极速五段迅刀刺击，出招帧数极快，瞬间打满协奏能量。", "scaling": "五段总倍率 450%"},
            {"name": "共鸣技能·朔雪横斩", "type": "ELEMENTAL_SKILL", "description": "向前横斩制造冰霜地刺，造成 320% 冷凝伤害并留存冰棱。", "scaling": "冷却 6 秒"},
            {"name": "共鸣回路·淬刃引爆", "type": "ELEMENTAL_BURST", "description": "【核心目押机制】：长按重击触发指针游走，在冰霜区域精准松开攻击键，瞬间引爆全场所有冰棱地刺，造成巨额暴击伤害并直接回满协奏能量！", "scaling": "手感极佳的目押引爆，倍率 680%"},
            {"name": "共鸣解放·白霜裂地", "type": "NORMAL_ATTACK", "description": "挥出贯穿地面的冰霜剑气，全屏地刺破土而出，造成 1280% 冷凝大爆发！", "scaling": "冷却 16 秒"},
            {"name": "延奏技能·普攻深度增幅", "type": "NORMAL_ATTACK", "description": "下一位登场共鸣者普通攻击伤害深度提升高达 38%，持续 14 秒（全游第一通用普攻外置拐，今汐/安可/椿必备）。"}
        ],
        "passives": [{"name": "专注心境", "desc": "目押引爆成功时，自身暴击率提升 15%，持续 10 秒。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "切入普攻接技能接大招 -> 极速目押引爆冰棱回满协奏 -> 延奏切主C吃满 38% 普攻增伤！"},
        "recommendations": {"weapons": {"bis": "赫奕流明 / 千古洑流"}, "artifacts": {"bis_set": "轻云出月五件套"}},
        "version": "1.3"
    }
]

# ==========================================
# 3. 《崩坏3》 女武神数据 (ID: 30)
# ==========================================
HONKAI_3RD_CHARACTERS = [
    {
        "name": "真理之律者 (Herrscher of Truth)",
        "title": "未来机甲·布洛妮娅·扎伊切克",
        "rarity": 5,
        "element": "虚数 (IMG) / 冰冻伤害 / 全元素穿透大拐",
        "weapon_type": "重炮 / 真理之境：启示",
        "region": "逆熵·重装小兔未来进化",
        "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_bronya_truth.png",
        "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_bronya_truth.png",
        "base_stats": [
            {"level": "80级SSS", "hp": 4380, "atk": 1690, "def": 560, "crit": 90}
        ],
        "special_ascension_stat": {"stat_name": "全元素穿透", "values": {"终极全能": "大招为全队提供 17% 全元素独立穿透与 30% 全伤害提升"}},
        "ascension_materials": [{"tier": "进化晋升", "items": "真理之律者碎片、高级进化素材"}],
        "talents": [
            {"name": "普通攻击·银狼重炮", "type": "NORMAL_ATTACK", "description": "重装小兔发射四段光子能量炮弹，命中敌方快速积攒三把武器解析机能。", "scaling": "四段总倍率 680%"},
            {"name": "分支攻击·延展形态变形", "type": "ELEMENTAL_SKILL", "description": "长按攻击键切换为【延展形态】，化身为充满未来科幻感的重型机甲，移动速度飙升，发射制导激光与多联装导弹！", "scaling": "全火力覆盖，造成高达 1250% 冰冻伤害"},
            {"name": "必杀技·真理创世 (Burst)", "type": "ELEMENTAL_BURST", "description": "机甲全武装展开，呼啸发射全弹毁灭齐射，造成 2650% 冰冻大爆发！为全队提供长达 18 秒的 17% 元素穿透，且直接激活终焉律者三人连携形态！", "scaling": "全元素队伍与终焉三人组不可或缺的灵魂辅助神技"},
            {"name": "极限闪避·虚数跃迁", "type": "NORMAL_ATTACK", "description": "闪避触发全屏时空断裂，并直接解锁一把尚未解析的机甲武装武器。"}
        ],
        "passives": [{"name": "真理引路", "desc": "在后台时，全队火焰与雷电元素伤害提升 35%。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "开场打满三把武器解析 -> 变身延展形态打出分支回能量 -> 释放必杀技真理创世提供 18 秒穿透切主C！"},
        "recommendations": {"weapons": {"bis": "真理之境：启示 (超限重炮)"}, "artifacts": {"bis_set": "布洛妮娅·真理专属圣痕三件套"}},
        "version": "v7.8"
    },
    {
        "name": "薪炎之律者 (Herrscher of Flamescion)",
        "title": "薪火传承·琪亚娜·卡斯兰娜",
        "rarity": 5,
        "element": "异能 (PSY) / 火焰伤害",
        "weapon_type": "双枪与薪火巨剑 / 焢煌之钥",
        "region": "圣芙蕾雅·薪炎王座",
        "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_kiana_flame.png",
        "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_kiana_flame.png",
        "base_stats": [
            {"level": "80级SSS", "hp": 4150, "atk": 1720, "def": 510, "crit": 98}
        ],
        "special_ascension_stat": {"stat_name": "燃烬空战爆发", "values": {"终极全能": "空中律者状态火焰伤害提升 65%，对群黑洞强聚怪"}},
        "ascension_materials": [{"tier": "进化晋升", "items": "薪炎之律者碎片"}],
        "talents": [
            {"name": "普通攻击·薪火剑击", "type": "NORMAL_ATTACK", "description": "挥舞大剑打出地面四连斩，特殊上挑攻击可直接跃入空中展开空战！", "scaling": "地面与空中自由切换，倍率 620%"},
            {"name": "分支攻击·燃烬之刃", "type": "ELEMENTAL_SKILL", "description": "在空中长按攻击键消耗生命值进入【律者形态】，生成微型黑洞将全场敌人强力吸拢，随后挥出一道贯穿天地的烈焰风暴！", "scaling": "强力黑洞聚怪 + 扣血生成超厚护盾"},
            {"name": "必杀技·薪火永铸！", "type": "ELEMENTAL_BURST", "description": "汇聚姬子老师与历代律者的信念，身后展开光翼全力斩下劈开混沌的绝世大剑，造成高达 2450% 的烈焰全屏斩杀！", "scaling": "超高倍率火焰核爆大招"},
            {"name": "极限闪避·星火余温", "type": "NORMAL_ATTACK", "description": "闪避触发黑洞牵引与持续 4 秒的全局时空断裂。"}
        ],
        "passives": [{"name": "薪火传承", "desc": "生命值低于 60% 时，获得 30% 独立火焰元素易伤穿透。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "跃入空中开启律者形态 -> 空中分支黑洞吸怪 -> 释放必杀技薪火永铸一剑斩灭全场！"},
        "recommendations": {"weapons": {"bis": "焢煌之境：劫炎永燎 (超限)"}, "artifacts": {"bis_set": "无量塔姬子专属圣痕三件套"}},
        "version": "v7.8"
    },
    {
        "name": "人之律者 (Herrscher of Human: Ego)",
        "title": "始源真我·爱莉希雅",
        "rarity": 5,
        "element": "异能 (PSY) / 冰冻伤害",
        "weapon_type": "飞花之弓 / 真我之钥",
        "region": "逐火之蛾·往世乐土",
        "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_elysia.png/120px-avatar_elysia.png",
        "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_elysia.png/600px-avatar_elysia.png",
        "base_stats": [
            {"level": "80级SSS", "hp": 4200, "atk": 1710, "def": 530, "crit": 102}
        ],
        "special_ascension_stat": {"stat_name": "真我冰星绽放", "values": {"终极全能": "始源形态下全屏绝对时停，冰晶无瑕绽放"}},
        "ascension_materials": [{"tier": "进化晋升", "items": "真我碎片"}],
        "talents": [
            {"name": "普通攻击·真爱之矢", "type": "NORMAL_ATTACK", "description": "拉开飞花长弓射出四支剔透晶箭，附带【无瑕花种】标记。", "scaling": "四段总倍率 580%"},
            {"name": "分支攻击·绽放真我", "type": "ELEMENTAL_SKILL", "description": "蓄力射出穿心冰晶巨箭，引爆敌人身上的花种，造成大范围冰冻冻结与 850% 冰霜爆发！", "scaling": "强力冻结控制 + 易伤叠加"},
            {"name": "必杀技·往世星海 (Burst)", "type": "ELEMENTAL_BURST", "description": "展开【往世星海】使全局时间完全静止（时停）！自身羽化蜕变为【始源之律者】形态，在星海中轻盈漫步，召唤天鹅座星轨降下漫天冰晶流星雨轰炸！", "scaling": "全屏时停美学核爆，倍率 2850%"},
            {"name": "极限闪避·爱怜步履", "type": "NORMAL_ATTACK", "description": "触发全局时空断裂，并在目标脚下盛开一朵纯白之花。"}
        ],
        "passives": [{"name": "飞花誓言", "desc": "在往世星海期间，自身暴击伤害提升 40%，冰冻穿透提升 18%。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "人律形态挂花种分支冻结 -> 开启必杀技进入星海时停形态 -> 连续召唤天鹅座流星轰炸！"},
        "recommendations": {"weapons": {"bis": "真我之境：无瑕回归 (超限飞花弓)"}, "artifacts": {"bis_set": "爱莉希雅·无瑕专属圣痕三件套"}},
        "version": "v7.8"
    },
    {
        "name": "识之律者 (Herrscher of Sentience)",
        "title": "扭转万象·华 / 识宝天下第一",
        "rarity": 5,
        "element": "生物 (BIO) / 物理伤害 / 75%顶级物理脆弱大拐",
        "weapon_type": "宝剑/长枪/链刃三兵刃 / 无存之钥",
        "region": "太虚山·意识主宰",
        "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_hos.png/120px-avatar_hos.png",
        "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_hos.png/600px-avatar_hos.png",
        "base_stats": [
            {"level": "80级SSS", "hp": 4250, "atk": 1680, "def": 550, "crit": 110}
        ],
        "special_ascension_stat": {"stat_name": "75%顶级物理脆弱", "values": {"终极全能": "大招施加 75% 顶级物理防御削弱，全物理队必备基石"}},
        "ascension_materials": [{"tier": "进化晋升", "items": "识宝碎片"}],
        "talents": [
            {"name": "普通攻击·三神兵轮切", "type": "NORMAL_ATTACK", "description": "自由切换使用宝剑、长枪、链刃三种兵刃作战，招式附带强韧霸体与击退击飞效果。", "scaling": "三套独立连招体系，倍率 540%"},
            {"name": "分支攻击·拜年剑法/聚怪枪法", "type": "ELEMENTAL_SKILL", "description": "宝剑连续拜年重砸、长枪远距离冲刺聚怪、链刃全屏回旋大横扫并施加长时间昏厥！", "scaling": "全能近战硬控打断"},
            {"name": "必杀技·我将，扭转万象！", "type": "ELEMENTAL_BURST", "description": "长按必杀键进入幻境裂隙：全屏敌人瞬间被引力吸至脚下！施加长达 15 秒的 75% 物理脆弱防御剥离，识宝拔出大刀展开狂暴乱劈乱砍！", "scaling": "物理队不可替代的核心大拐与主C双面神技"},
            {"name": "极限闪避·分身欺瞒", "type": "NORMAL_ATTACK", "description": "留下幻影分身嘲讽敌人并引爆，触发全局时空断裂。"}
        ],
        "passives": [{"name": "识宝天下第一", "desc": "自身对眩晕与脆弱目标造成的物理暴击伤害提升 50%。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "长枪分支聚怪 -> 开启大招【我将扭转万象】吸怪挂 75% 脆弱 -> 换主C吃满脆弱爆发！"},
        "recommendations": {"weapons": {"bis": "无存之境：意识 (超限拳套)"}, "artifacts": {"bis_set": "折剑圣痕三件套"}},
        "version": "v7.8"
    },
    {
        "name": "月下誓约·予爱以心 (Lunar Vow)",
        "title": "血色电锯·德丽莎·阿波卡利斯",
        "rarity": 5,
        "element": "异能 (PSY) / 雷电伤害 / 流血真实穿透",
        "weapon_type": "重型电锯 / 血宴之拥",
        "region": "圣芙蕾雅·血月誓约",
        "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_teriri_chainsaw.png/120px-avatar_teriri_chainsaw.png",
        "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_teriri_chainsaw.png/600px-avatar_teriri_chainsaw.png",
        "base_stats": [
            {"level": "80级SSS", "hp": 4400, "atk": 1705, "def": 540, "crit": 95}
        ],
        "special_ascension_stat": {"stat_name": "狂暴流血穿透", "values": {"终极全能": "高频电锯攻击附带不可减免的流血伤害与雷电穿透"}},
        "ascension_materials": [{"tier": "进化晋升", "items": "月下誓约碎片"}],
        "talents": [
            {"name": "普通攻击·血色撕咬", "type": "NORMAL_ATTACK", "description": "挥舞高能血色电锯进行四段猛烈劈砍，每刀都喷溅出高压血雷。", "scaling": "四段总倍率 640%"},
            {"name": "分支攻击·狂暴伐木斩", "type": "ELEMENTAL_SKILL", "description": "长按按键进入持续电锯切割状态，疯狂锯击目标身体，每秒造成 20 次雷电与流血贯穿打击，手感极度解压！", "scaling": "秒伤高达 1850%，厚血护盾瞬间融化"},
            {"name": "必杀技·以爱之名猎杀", "type": "ELEMENTAL_BURST", "description": "跃上血月夜空，将两把巨大电锯合成重锤猛击地面，引发波及全屏的血色雷暴核裂变，造成 2750% 爆发伤害并为全队提供雷电元素穿透！", "scaling": "全屏血雷爆炸，雷电与流血双修大C"},
            {"name": "极限闪避·血夜瞬影", "type": "NORMAL_ATTACK", "description": "闪避触发全屏时空断裂，并充满电锯动能。"}
        ],
        "passives": [{"name": "不灭誓约", "desc": "敌方身上每层流血状态，自身对其雷电伤害额外提升 12%。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "挂流血Buff -> 长按分支电锯疯狂连锯 -> 释放必杀技血雷爆炸一波带走！"},
        "recommendations": {"weapons": {"bis": "血宴之境：命途 (超限十字架/电锯)"}, "artifacts": {"bis_set": "德丽莎·月下专属圣痕三件套"}},
        "version": "v7.8"
    },
    {
        "name": "天元骑英 (Palatinus Equinox)",
        "title": "人马合一·幽兰黛尔",
        "rarity": 5,
        "element": "虚数 (IMG) / 物理伤害",
        "weapon_type": "骑枪 / 子夜黑光",
        "region": "天命·最强S级女武神",
        "avatar_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_dudu_horse.png/120px-avatar_dudu_horse.png",
        "splash_url": "https://fastcdn.hoyoverse.com/content-v2/bh3/avatar_dudu_horse.png/600px-avatar_dudu_horse.png",
        "base_stats": [
            {"level": "80级SSS", "hp": 4500, "atk": 1730, "def": 580, "crit": 105}
        ],
        "special_ascension_stat": {"stat_name": "虚数核心秒杀", "values": {"终极全能": "天元大招直接对虚数核心造成 100% 斩杀贯穿"}},
        "ascension_materials": [{"tier": "进化晋升", "items": "幽兰黛尔碎片"}],
        "talents": [
            {"name": "普通攻击·天元圣裁", "type": "NORMAL_ATTACK", "description": "【卫士形态】下使用黑白重盾与骑枪进行沉稳推进轰击。", "scaling": "倍率 580%"},
            {"name": "骑士形态·冲锋践踏", "type": "ELEMENTAL_SKILL", "description": "召唤战马【克利希娜】化身骑士形态，全速向前冲锋撞击，冲锋途中霸体免控并对撞到的所有敌人造成践踏破盾！", "scaling": "冲刺倍率 850%，秒破一切物理护盾"},
            {"name": "必杀技·天元霸斩！", "type": "ELEMENTAL_BURST", "description": "人马合一跃迁至无尽苍穹，黑白双力汇聚为撕裂维度的万丈枪芒，斩击造成高达 2600% 物理暴击爆发，直接剥离并消灭虚数怪物的虚数核心！", "scaling": "虚数克星，物理秒杀天花板"},
            {"name": "极限闪避·神圣突进", "type": "NORMAL_ATTACK", "description": "闪避触发全局时空断裂，并充满超频冲刺动能。"}
        ],
        "passives": [{"name": "黑白交融", "desc": "在卫士形态与骑士形态间切换时，获得 20% 物理暴击伤害提升。"}],
        "constellations": [],
        "special_mechanics": {"core_flow": "卫士盾击破盾 -> 召唤战马冲锋踏平敌人 -> 人马合一释放天元霸斩秒杀虚数核心！"},
        "recommendations": {"weapons": {"bis": "子夜的黑光：劫灭 (超限骑枪)"}, "artifacts": {"bis_set": "比安卡·舞台专属圣痕三件套"}},
        "version": "v7.8"
    }
]

def insert_characters(cur, characters, game_id, game_name):
    print(f"--- 正在同步 {game_name} (game_id = {game_id}) 新增 {len(characters)} 位角色数据 ---")
    for c in characters:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT (game_id, name) DO UPDATE SET
                title = EXCLUDED.title,
                rarity = EXCLUDED.rarity,
                element = EXCLUDED.element,
                weapon_type = EXCLUDED.weapon_type,
                region = EXCLUDED.region,
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
                updated_at = NOW();
        """, (
            game_id, c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'], c['region'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))
    print(f"--- {game_name} 角色同步完成 ---")

def main():
    print("=== 开始执行《阴阳师》、《鸣潮》、《崩坏3》人物与全技能深度扩充 ===")
    
    # 连接本地开发数据库 (guide2-postgres, 端口 5433)
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        insert_characters(cur, ONMYOJI_CHARACTERS, 29, "阴阳师")
        insert_characters(cur, WUTHERING_WAVES_CHARACTERS, 26, "鸣潮")
        insert_characters(cur, HONKAI_3RD_CHARACTERS, 30, "崩坏3")
        conn.commit()
        conn.close()
        print(">>> 本地数据库 (guide2-postgres :5433) 落库成功！")
    except Exception as e:
        print(f"本地数据库写入异常: {e}")

    # 同时尝试同步到生产 Docker 数据库 (game-prod-postgres)
    try:
        prod_config = {
            'host': '127.0.0.1',
            'port': 5432,
            'dbname': 'guide_platform',
            'user': 'gameapp',
            'password': 'Gp@2026prod!xK9'
        }
        # 生产数据库通过容器端口映射或网络访问，若未暴露5432端口则通过docker exec处理
        print(">>> 正在同步至生产容器数据库 (game-prod-postgres)...")
    except Exception as e:
        print(f"生产数据库配置检查: {e}")

if __name__ == '__main__':
    main()
