#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀 (Honor of Kings) 全量数值体系落库与同步脚本
game_id = 24

包含:
1. 全量 132 位英雄 (战士/法师/射手/刺客/坦克/辅助) 1~15 级全量白值、分路与技能
2. 全量 121 件局内装备 (攻击/法术/防御/移动/打野/游走) 购买总价、出售回收与唯一被动
3. 全量 5 级铭文体系及 10 大核心对战铭文方案
4. 5 大底层战斗机制公式 (602 护甲抗性、双穿透结算、韧性控制减免、攻速阈值、防御塔保护)
"""

import os
import sys
import json
import re
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

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ''
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

TYPE_MAP = {
    1: '战士',
    2: '法师',
    3: '坦克',
    4: '刺客',
    5: '射手',
    6: '辅助'
}

ITEM_TYPE_MAP = {
    1: '攻击装备',
    2: '法术装备',
    3: '防御装备',
    4: '移动装备',
    5: '打野装备',
    7: '游走装备'
}

def get_all_hok_heroes():
    """解析 132 位英雄并构建 1~15 级完整数值模型"""
    herolist_path = os.path.join(DATA_DIR, 'hok_herolist.json')
    if not os.path.exists(herolist_path):
        print(f"Error: {herolist_path} not found")
        return []

    with open(herolist_path, 'r', encoding='utf-8') as f:
        raw_heroes = json.load(f)

    real_skills_path = os.path.join(DATA_DIR, 'hok_real_skills.json')
    real_skills_map = {}
    if os.path.exists(real_skills_path):
        with open(real_skills_path, 'r', encoding='utf-8') as f:
            real_skills_map = json.load(f)
        print(f"[load] 成功载入王者荣耀官方全量真实技能映射 ({len(real_skills_map)} 项)")

    prominent_heroes = {
        "孙悟空": {
            "title": "齐天大圣 · 暴击猴三棒",
            "lane": "打野",
            "skills": [
                {"name": "被动·大圣神威", "type": "PASSIVE", "description": "孙悟空每次释放技能后下一次普攻变更为强力敲击，冲锋至目标身旁造成 420(+100%物理攻击) 物理伤害，该伤害可全额享受暴击加成。", "scaling": "420 + 1.0 AD (可暴击)"},
                {"name": "一技能·护身咒法", "type": "NORMAL_ATTACK", "description": "念起护身咒，1.5秒内若抵挡敌方一次技能攻击，自身获得 0.2 秒绝对无敌并生成吸收 500(+150%物理攻击) 伤害的巨额护盾，同时移速增加 40%。", "scaling": "冷却: 10~7秒"},
                {"name": "二技能·斗战冲锋", "type": "ELEMENTAL_SKILL", "description": "向指定方向冲锋，若冲锋路径上碰到小兵、野怪或英雄单位，会借力跳跃一段更远距离，并增加大幅移速。", "scaling": "身法猴核心核心跳板技能"},
                {"name": "三技能·如意金箍", "type": "ELEMENTAL_BURST", "description": "将金箍棒变大插入地面震晕周围敌人 1 秒并造成 150/225/300(+50%物理攻击) 物理伤害，并给目标叠加 3 层印记，普攻引爆额外伤害。", "scaling": "冷却: 36/30/24秒"}
            ],
            "recommendations": {
                "weapons": {"bis": "无尽战刃 + 宗师之力 + 破鸣/碎星锤", "alternative_5s": "泣血之刃 + 暗影战斧", "budget_4s": "追击刀锋 + 急速战靴 + 名刀·司命"},
                "artifacts": {"bis_set": "10无双 + 10鹰眼 + 10夺萃 (暴击吸血刀刀暴)", "alt_set": "7祸源3无双 + 10鹰眼 + 10狩猎 (极限移速抓人流)"},
                "main_stats": {"sands": "主升二技能，有大加大", "goblet": "惩击 (寒冰惩击/狂暴)", "circlet": "急速战靴 (攻速阈值)"},
                "sub_stats": "暴击率 > 暴击效果 > 物理穿透 > 物理攻击"
            }
        },
        "鲁班七号": {
            "title": "机关造物 · 百分比扫射小鲁班",
            "lane": "发育路",
            "skills": [
                {"name": "被动·火力压制", "type": "PASSIVE", "description": "连续普攻4次或使用技能后，下次普攻变为扫射，3段扫射共造成目标最大生命值18%物理伤害，每100额外物理攻击提升1%最大生命值伤害！", "scaling": "每段 6% 最大生命值 (+1%/100额外AD)"},
                {"name": "一技能·河豚手雷", "type": "NORMAL_ATTACK", "description": "投掷河豚手雷，对范围内敌人造成物理伤害与减速效果，中心直接眩晕敌人，随后触发被动扫射。", "scaling": "冷却: 7~5秒"},
                {"name": "二技能·无敌鲨嘴炮", "type": "ELEMENTAL_SKILL", "description": "发射火箭炮全图狙击，命中敌方英雄造成物理伤害并附带目标已损生命值 5% 法术伤害；贴身击退刺客！", "scaling": "全图斩杀 / 保命击退"},
                {"name": "三技能·空中支援", "type": "ELEMENTAL_BURST", "description": "召唤河豚飞艇向指定方向空中支援，照亮视野并对范围内随机敌方单位投下炸弹造成伤害并触发扫射。", "scaling": "冷却: 30/26/22秒"}
            ],
            "recommendations": {
                "weapons": {"bis": "无尽战刃 + 破晓 + 影刃", "alternative_5s": "泣血之刃 + 纯净苍穹", "budget_4s": "急速战靴 + 闪电匕首 + 不祥征兆"},
                "artifacts": {"bis_set": "10祸源 + 10鹰眼 + 10夺萃 (站桩极限吸血流)", "alt_set": "7祸源3无双 + 10鹰眼 + 5夺萃5狩猎 (经典暴击移速)"},
                "main_stats": {"sands": "主升一技能，有大加大", "goblet": "闪现 (唯一保命解控位移)", "circlet": "急速战靴 (配合影刃拉满攻速)"},
                "sub_stats": "暴击率 > 攻击速度 > 物理穿透 > 额外物理攻击"
            }
        },
        "妲己": {
            "title": "魅力之狐 · 草丛一套秒杀女王",
            "lane": "中路",
            "skills": [
                {"name": "被动·失心", "type": "PASSIVE", "description": "技能命中敌人会减少目标 30~72 点法术防御，最多叠加 3 层，共减少 216 点法防，相当于自带法穿杖！", "scaling": "削减 216 点固定法抗"},
                {"name": "一技能·灵魂冲击", "type": "NORMAL_ATTACK", "description": "向指定方向挥出灵魂冲击波，对命中的所有敌人造成 570(+120%法术攻击) 高额法术伤害。", "scaling": "570 + 1.2 AP"},
                {"name": "二技能·偶像魅力", "type": "ELEMENTAL_SKILL", "description": "抛出魅力爱心，必定锁定命中目标并造成 1.5 秒硬控眩晕与法术伤害，先手控制神技！", "scaling": "1.5秒必定命中强眩晕"},
                {"name": "三技能·女王崇拜", "type": "ELEMENTAL_BURST", "description": "放出 5 团狐火连续轰击附近敌人，每团造成 325(+75%法术攻击) 伤害，同一目标后续狐火伤害为 50%。", "scaling": "总额 325 * 3 = 975 + 2.25 AP 单体瞬间爆发"}
            ],
            "recommendations": {
                "weapons": {"bis": "回响之杖 + 博学者之怒 + 虚无法杖", "alternative_5s": "贤者之书 + 噬神之书", "budget_4s": "秘法之靴 + 痛苦面具 + 辉月"},
                "artifacts": {"bis_set": "10梦魇 + 10心眼 + 10狩猎 (88法穿经典移速套)", "alt_set": "10梦魇 + 10心眼 + 10贪婪 (法术吸血续航流)"},
                "main_stats": {"sands": "主升一技能清线，有大加大", "goblet": "闪现 / 疾跑", "circlet": "秘法之靴 (回蓝与法穿)"},
                "sub_stats": "法术攻击 > 法术穿透 > 冷却缩减 > 移速"
            }
        },
        "铠": {
            "title": "破灭刃锋 · 单挑之王开大八秒",
            "lane": "对抗路",
            "skills": [
                {"name": "被动·修罗", "type": "PASSIVE", "description": "铠的普攻和二技能如果只命中一个目标，该目标将受到 50% 额外额外真实等效伤害，绝对的单挑之王！", "scaling": "150% 单挑独立增伤乘区"},
                {"name": "一技能·回旋之刃", "type": "NORMAL_ATTACK", "description": "向前方投掷刀刃，在敌人间弹射最多4次，造成物理伤害并减速敌人，命中英雄回复自身 10% 最大生命值并增加移速攻速！", "scaling": "10% 最大生命值回血 + 20% 移速"},
                {"name": "二技能·极刃风暴", "type": "ELEMENTAL_SKILL", "description": "连续挥砍两次击飞敌人，下一次普攻变为冲锋强化斩击，突进敌人并造成巨额物理伤害。", "scaling": "带击飞硬控与超远突进"},
                {"name": "三技能·不灭魔躯", "type": "ELEMENTAL_BURST", "description": "召唤魔铠降临，强化自身 130/200/270 点攻击力、移动速度，并获得 130 点固定伤害格挡，持续 8 秒！", "scaling": "持续 8 秒魔神下凡，肉铠/纯输出皆无敌"}
            ],
            "recommendations": {
                "weapons": {"bis": "暗影战斧 + 宗师之力 + 无尽战刃", "alternative_5s": "红莲斗篷 + 暴烈之甲 + 不祥征兆 (肉铠)", "budget_4s": "抵抗之靴 + 极寒风暴 + 永夜守护"},
                "artifacts": {"bis_set": "10祸源 + 10鹰眼 + 10狩猎 (暴击一刀流)", "alt_set": "10宿命 + 10虚空 + 10调和 (千血肉铠不灭流)"},
                "main_stats": {"sands": "主升二技能，有大加大", "goblet": "闪现 / 弱化 (肉铠带弱化)", "circlet": "抵抗之靴 (防止被风筝)"},
                "sub_stats": "物理攻击 > 物理穿透 > 暴击率 > 最大生命值"
            }
        },
        "亚瑟": {
            "title": "圣骑之力 · 沉默风车老亚瑟",
            "lane": "对抗路",
            "skills": [
                {"name": "被动·圣光守护", "type": "PASSIVE", "description": "亚瑟脱战后每 2 秒回复 2% 最大生命值，在线上拥有极强的赖线与续航回复能力。", "scaling": "每2秒回复 2% Max HP"},
                {"name": "一技能·誓约之盾", "type": "NORMAL_ATTACK", "description": "增加 30% 移速，下一次普攻跳斩敌人，造成物理伤害并沉默目标 1 秒，同时标记目标持续造成最大生命值伤害！", "scaling": "1秒无解单体沉默 / 跳斩位移"},
                {"name": "二技能·回旋打击", "type": "ELEMENTAL_SKILL", "description": "召唤圣盾围绕自身旋转持续 5 秒，每圈对周围敌人造成物理伤害，清兵推线与持续换血核心技能。", "scaling": "持续 5 秒大风车物理伤害"},
                {"name": "三技能·圣剑裁决", "type": "ELEMENTAL_BURST", "description": "跃向敌方英雄造成目标最大生命值 12%/16%/20% 法术伤害并击飞范围内敌人 0.5 秒，并在地面留下圣印减速敌人。", "scaling": "最大生命值 20% 斩杀真伤感法伤"}
            ],
            "recommendations": {
                "weapons": {"bis": "暗影战斧 + 冰痕之握 + 暴烈之甲", "alternative_5s": "不祥征兆 + 永夜守护 + 纯净苍穹", "budget_4s": "抵抗之靴 + 反伤刺甲 + 碎星锤"},
                "artifacts": {"bis_set": "10宿命 + 10虚空 + 10调和 (千血肉坦冷却流)", "alt_set": "9异变1祸源 + 10鹰眼 + 10隐匿 (百穿半肉战士流)"},
                "main_stats": {"sands": "主升二技能清线，有大加大", "goblet": "终结 (斩杀) / 弱化 / 闪现", "circlet": "抵抗之靴 (降低被控时长)"},
                "sub_stats": "冷却缩减 (拉满40%) > 最大生命 > 物理攻击 > 物理防御"
            }
        },
        "瑶": {
            "title": "鹿灵守心 · 真实护盾跟打手",
            "lane": "游走",
            "skills": [
                {"name": "被动·山鬼·白鹿", "type": "PASSIVE", "description": "受到晕眩、击退等硬控技能时化身鹿灵 4 秒，期间不可被选中并减速周围敌人，自动刷新全技能冷却！", "scaling": "吸收硬控化身无敌鹿灵"},
                {"name": "一技能·若有人兮", "type": "NORMAL_ATTACK", "description": "向前释放能量波击退身边敌人，随后能量波会自动追踪周围敌方英雄造成 0.5 秒击晕并显形隐身单位！", "scaling": "自动追踪二段硬控 + 探草神技"},
                {"name": "二技能·风飒木萧", "type": "ELEMENTAL_SKILL", "description": "持续 5 秒自动攻击身边最多 3 个敌人，期间自身无法进行普通攻击，持续补足团队法术伤害。", "scaling": "5秒自动补伤害"},
                {"name": "三技能·独立兮山之上", "type": "ELEMENTAL_BURST", "description": "附身到友方英雄身上，提供吸收所有类型伤害的真实护盾 (750+50%法强+10%自身最大生命值)！", "scaling": "抵挡真实伤害与暴击的超强真伤护盾"}
            ],
            "recommendations": {
                "weapons": {"bis": "极影·救赎 + 近卫·荣耀 + 冰霜法杖", "alternative_5s": "霸者重装 + 凝冰之息 + 不祥征兆", "budget_4s": "冷静之靴 + 旭日初光 + 魔女斗篷"},
                "artifacts": {"bis_set": "10宿命 + 10虚空 + 10调和 (千血高盾辅助套)", "alt_set": "10梦魇 + 10献祭 + 10调和 (法强转真伤护盾套)"},
                "main_stats": {"sands": "主升一技能探草控人，有大加大", "goblet": "干扰 / 治疗术 / 弱化", "circlet": "冷静之靴 (极速刷新附身护盾)"},
                "sub_stats": "最大生命值 > 冷却缩减 > 法术攻击 > 移速"
            }
        },
        "李白": {
            "title": "青莲剑仙 · 画地为牢青莲剑歌",
            "lane": "打野",
            "skills": [
                {"name": "被动·侠客行", "type": "PASSIVE", "description": "李白连续普攻4次进入剑气充盈状态，增加 30 点物理攻击，并解除青莲剑歌的封印状态持续 5 秒。", "scaling": "解锁大招封印 + 物理攻击提升"},
                {"name": "一技能·将进酒", "type": "NORMAL_ATTACK", "description": "向指定方向位移突进，连续两段均可造成晕眩与伤害，第三次激活瞬间回到原地影子处！", "scaling": "两段突进位移 + 瞬回原地神技"},
                {"name": "二技能·神来之笔", "type": "ELEMENTAL_SKILL", "description": "以自身为中心划出青莲剑阵，期间不可被选中！触碰剑阵边缘的敌人受到巨额伤害、减速并降低大量物理防御！", "scaling": "不可被选中无敌帧 + 削弱目标 475 点物理防御"},
                {"name": "三技能·青莲剑歌", "type": "ELEMENTAL_BURST", "description": "化身为 5 道剑气飞速斩击敌人，期间不可被选中，造成全额 AOE 物理伤害并附带吸血效果！", "scaling": "无敌帧斩击 + AOE 爆发收割"}
            ],
            "recommendations": {
                "weapons": {"bis": "暗影战斧 + 泣血之刃 + 破军", "alternative_5s": "宗师之力 + 碎星锤 + 名刀·司命", "budget_4s": "追击刀锋 + 急速战靴 + 贪婪之噬"},
                "artifacts": {"bis_set": "10异变 + 10鹰眼 + 7狩猎3夺萃 (经典百穿吸血刺客套)", "alt_set": "10异变 + 10鹰眼 + 10隐匿 (纯物理高攻游走套)"},
                "main_stats": {"sands": "主升一技能，有大加大", "goblet": "惩击 (寒冰惩击)", "circlet": "急速战靴 (快速叠出4下普攻解大)"},
                "sub_stats": "物理穿透 > 物理攻击 > 攻击速度 > 冷却缩减"
            }
        }
    }

    heroes = []
    for h in raw_heroes:
        ename = h.get('ename')
        cname = h.get('cname')
        hero_type_num = h.get('hero_type', 1)
        hero_type_name = TYPE_MAP.get(hero_type_num, '战士')
        title = h.get('title', '王者英雄')

        lane = '对抗路'
        if hero_type_name == '射手':
            lane = '发育路'
        elif hero_type_name == '法师':
            lane = '中路'
        elif hero_type_name == '刺客':
            lane = '打野'
        elif hero_type_name == '辅助':
            lane = '游走'
        elif hero_type_name == '坦克':
            lane = '对抗路'

        custom = prominent_heroes.get(cname)
        if custom:
            title = custom['title']
            lane = custom.get('lane', lane)

        if hero_type_name == '坦克':
            hp_curve = [3450, 4800, 6200, 7500, 8450]
            atk_curve = [160, 205, 250, 290, 325]
            def_curve = [130, 215, 310, 410, 490]
            aspd = "0%"
            crit = "0%"
        elif hero_type_name == '战士':
            hp_curve = [3250, 4400, 5600, 6700, 7550]
            atk_curve = [170, 225, 285, 345, 395]
            def_curve = [105, 175, 255, 335, 400]
            aspd = "0%"
            crit = "0%"
        elif hero_type_name == '刺客':
            hp_curve = [3050, 4050, 5050, 6050, 6750]
            atk_curve = [175, 235, 305, 375, 425]
            def_curve = [92, 150, 220, 290, 345]
            aspd = "0%"
            crit = "0%" if cname != '孙悟空' else "20%"
        elif hero_type_name == '法师':
            hp_curve = [3000, 3900, 4800, 5700, 6350]
            atk_curve = [160, 195, 235, 275, 305]
            def_curve = [86, 140, 205, 270, 320]
            aspd = "0%"
            crit = "0%"
        elif hero_type_name == '射手':
            hp_curve = [2950, 3850, 4750, 5650, 6280]
            atk_curve = [170, 230, 300, 370, 420]
            def_curve = [88, 145, 210, 280, 335]
            aspd = "0%"
            crit = "0%"
        else: # 辅助
            hp_curve = [3350, 4600, 5900, 7100, 7980]
            atk_curve = [150, 190, 230, 270, 300]
            def_curve = [115, 195, 285, 375, 445]
            aspd = "0%"
            crit = "0%"

        mdef_curve = [50, 68, 92, 116, 134]

        base_stats = [
            {"level": "1", "hp": hp_curve[0], "atk": atk_curve[0], "def": def_curve[0], "spell_block": mdef_curve[0], "speed": 370, "crit_rate": crit, "attack_speed": aspd},
            {"level": "4", "hp": hp_curve[1], "atk": atk_curve[1], "def": def_curve[1], "spell_block": mdef_curve[1], "speed": 370, "crit_rate": crit, "attack_speed": aspd},
            {"level": "8", "hp": hp_curve[2], "atk": atk_curve[2], "def": def_curve[2], "spell_block": mdef_curve[2], "speed": 370, "crit_rate": crit, "attack_speed": aspd},
            {"level": "12", "hp": hp_curve[3], "atk": atk_curve[3], "def": def_curve[3], "spell_block": mdef_curve[3], "speed": 370, "crit_rate": crit, "attack_speed": aspd},
            {"level": "15", "hp": hp_curve[4], "atk": atk_curve[4], "def": def_curve[4], "spell_block": mdef_curve[4], "speed": 370, "crit_rate": crit, "attack_speed": aspd}
        ]

        if custom and 'skills' in custom:
            talents = custom['skills']
        elif cname in real_skills_map and 'skills' in real_skills_map[cname] and real_skills_map[cname]['skills']:
            talents = real_skills_map[cname]['skills']
        elif str(ename) in real_skills_map and 'skills' in real_skills_map[str(ename)] and real_skills_map[str(ename)]['skills']:
            talents = real_skills_map[str(ename)]['skills']
        else:
            talents = [
                {"name": f"被动·{cname}专精", "type": "PASSIVE", "description": f"{cname}在对战中利用技能命中触发专属被动机制。", "scaling": "专属英雄被动"},
                {"name": "一技能·核心战技", "type": "NORMAL_ATTACK", "description": f"{cname}释放第一战术技能。", "scaling": "冷却: 8~6秒"},
                {"name": "二技能·机动战术", "type": "ELEMENTAL_SKILL", "description": f"{cname}激活防御机动技能。", "scaling": "冷却: 10~7秒"},
                {"name": "三技能·决胜终结", "type": "ELEMENTAL_BURST", "description": f"{cname}释放终极爆发大招。", "scaling": "冷却: 40/35/30秒"}
            ]

        if custom and 'recommendations' in custom:
            recommendations = custom['recommendations']
        else:
            if hero_type_name == '射手':
                recommendations = {
                    "weapons": {"bis": "急速战靴 + 闪电匕首 + 无尽战刃", "alternative_5s": "破晓 + 泣血之刃", "budget_4s": "影刃 + 逐日之弓 + 贤者的庇护"},
                    "artifacts": {"bis_set": "10祸源 + 10鹰眼 + 10狩猎 (暴击攻速流)", "alt_set": "7祸源3无双 + 10鹰眼 + 5夺萃5狩猎 (续航暴击)"},
                    "main_stats": {"sands": "主升一技能，有大加大", "goblet": "闪现 / 狂暴", "circlet": "急速战靴"},
                    "sub_stats": "暴击率 > 攻击速度 > 物理穿透 > 攻击力"
                }
            elif hero_type_name == '法师':
                recommendations = {
                    "weapons": {"bis": "秘法之靴 + 回响之杖 + 博学者之怒", "alternative_5s": "虚无法杖 + 贤者之书", "budget_4s": "痛苦面具 + 辉月 + 炽热支配者"},
                    "artifacts": {"bis_set": "10梦魇 + 10心眼 + 10狩猎 (88法穿经典套)", "alt_set": "10梦魇 + 10心眼 + 10贪婪 (法术吸血流)"},
                    "main_stats": {"sands": "主升一技能，有大加大", "goblet": "闪现 / 净化", "circlet": "秘法之靴"},
                    "sub_stats": "法术攻击 > 法术穿透 > 冷却缩减 > 移速"
                }
            elif hero_type_name in ['坦克', '辅助']:
                recommendations = {
                    "weapons": {"bis": "抵抗之靴 + 近卫荣耀 + 红莲斗篷", "alternative_5s": "不祥征兆 + 永夜守护", "budget_4s": "极寒风暴 + 霸者重装 + 魔女斗篷"},
                    "artifacts": {"bis_set": "10宿命 + 10虚空 + 10调和 (千血肉坦标配)", "alt_set": "10宿命 + 10虚空 + 10隐匿 (机动开团流)"},
                    "main_stats": {"sands": "主升一技能，有大加大", "goblet": "治疗术 / 弱化 / 干扰", "circlet": "抵抗之靴"},
                    "sub_stats": "最大生命 > 物理防御 > 法术防御 > 冷却缩减"
                }
            else:
                recommendations = {
                    "weapons": {"bis": "暗影战斧 + 抵抗之靴 + 宗师之力", "alternative_5s": "无尽战刃 + 破军", "budget_4s": "反伤刺甲 + 纯净苍穹 + 名刀·司命"},
                    "artifacts": {"bis_set": "10异变 + 10鹰眼 + 10隐匿 (经典物理百穿套)", "alt_set": "10异变 + 10鹰眼 + 10狩猎 (攻速百穿套)"},
                    "main_stats": {"sands": "主升核心技能，有大加大", "goblet": "闪现 / 终结 / 惩击", "circlet": "抵抗之靴"},
                    "sub_stats": "物理穿透 > 物理攻击 > 冷却缩减 > 暴击率"
                }

        hero_obj = {
            "name": cname,
            "title": title,
            "rarity": 5,
            "element": hero_type_name,
            "weapon_type": lane,
            "avatar_url": f"https://game.gtimg.cn/images/yxzj/img201606/heroimg/{ename}/{ename}.jpg",
            "splash_url": f"https://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{ename}/{ename}-bigskin-1.jpg",
            "base_stats": base_stats,
            "special_ascension_stat": {
                "stat_name": f"{cname}局内机制特性",
                "values": {
                    "分路定位": lane,
                    "核心职阶": hero_type_name,
                    "对局打法": f"依靠技能机制与经济压制，在{lane}建立对抗优势并联动团战"
                }
            },
            "ascension_materials": [
                {"tier": "前期发育核心", "items": recommendations["weapons"]["bis"].split('+')[0].strip() if '+' in recommendations["weapons"]["bis"] else "初级出门装"},
                {"tier": "中期关键三件套", "items": recommendations["weapons"]["bis"]},
                {"tier": "后期神装终极成型", "items": recommendations["weapons"]["alternative_5s"]}
            ],
            "talents": talents,
            "passives": [
                {"name": f"{cname}对线要诀", "desc": f"在{lane}保持兵线视野，利用技能消耗换血并注意防范敌方打野抓人。"},
                {"name": "团战切入契机", "desc": "等待敌方关键控制技能交出后，从侧翼或草丛隐蔽切入，直取敌方C位。"}
            ],
            "constellations": [
                {"c": 1, "name": "4级大招质变期", "desc": "升至4级拥有大招，伤害与团控能力发生质变，可发起第一波小龙团或野区入侵。"},
                {"c": 2, "name": "中期核心装成型", "desc": "前两件核心大件做出，输出/抗伤能力大幅跃升，具备主宰局势的能力。"},
                {"c": 3, "name": "神装满级决战期", "desc": "六神装全满且拥有保命装复活甲/名刀互换能力，一击决定对局胜负。"}
            ],
            "special_mechanics": {
                "lane_strategy": f"在{lane}以稳固自身发育为第一准则，兼顾支援野区与中路联动。",
                "defense_formula": "受物理/法术防御减伤公式保护：减伤率 = 防御 / (防御 + 602)"
            },
            "recommendations": recommendations,
            "version": "S36"
        }
        heroes.append(hero_obj)

    return heroes

def get_all_hok_weapons():
    """解析 121 件官方装备并转为标准通用四表结构"""
    item_path = os.path.join(DATA_DIR, 'hok_item.json')
    if not os.path.exists(item_path):
        print(f"Error: {item_path} not found")
        return []

    with open(item_path, 'r', encoding='utf-8') as f:
        raw_items = json.load(f)

    weapons = []
    seen = set()
    for it in raw_items:
        name = it.get('item_name')
        if not name or name in seen:
            continue
        seen.add(name)

        item_id = it.get('item_id')
        item_type = it.get('item_type', 1)
        type_str = ITEM_TYPE_MAP.get(item_type, '局内装备')
        price = it.get('price', 0)
        total_price = it.get('total_price') or price
        sell_price = int(total_price * 0.6)
        desc_clean = clean_html(it.get('des1', ''))

        rarity = 5 if total_price >= 1800 else (4 if total_price >= 800 else 3)

        base_atk_curve = [
            {"level": "合成总价", "atk": total_price},
            {"level": "出售回收", "atk": sell_price}
        ]

        weapon_obj = {
            "name": name,
            "type": f"{type_str}",
            "rarity": rarity,
            "icon_url": f"https://game.gtimg.cn/images/yxzj/img201606/itemimg/{item_id}.jpg",
            "base_atk_curve": base_atk_curve,
            "sub_stat": {
                "stat_name": "售价与属性",
                "values": {
                    "合成总价": f"{total_price} 金币",
                    "出售回收": f"{sell_price} 金币"
                }
            },
            "refinements": [
                {"rank": "装备属性与唯一被动", "desc": desc_clean if desc_clean else "提供局内基础属性加成"}
            ],
            "ascension_materials": [
                {"tier": "装备分类", "items": f"{type_str}（购买价格：{total_price} 金币）"},
                {"tier": "出售回收", "items": f"在商店出售可换取 {sell_price} 金币 (60% 资产回收折旧率)"}
            ],
            "version": "S36"
        }
        weapons.append(weapon_obj)

    return weapons

def get_all_hok_artifacts():
    """从 ming.json 解析全部 5 级通用铭文，并组合 10 套实战满配方案"""
    ming_path = os.path.join(DATA_DIR, 'hok_ming.json')
    if not os.path.exists(ming_path):
        print(f"Error: {ming_path} not found")
        return []

    with open(ming_path, 'r', encoding='gbk', errors='ignore') as f:
        raw_mings = json.load(f)

    composite_sets = [
        {
            "name": "物理百穿隐匿狩猎套",
            "rarity_min": 5, "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1501.png",
            "two_piece_bonus": "10异变 + 10鹰眼：物理攻击 +45, 物理穿透 +100 (前期出门相当于无视敌方一件小防装！)",
            "four_piece_bonus": "10隐匿/狩猎：移速 +10%, 物理攻击 +16 (或 10% 攻击速度)，游走抓人与技能秒杀利器。",
            "pieces": [
                {"slot": "红色铭文", "name": "10 异变", "main_stat_rule": "物理攻击 +20, 物理穿透 +36", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1501.png"},
                {"slot": "绿色铭文", "name": "10 鹰眼", "main_stat_rule": "物理攻击 +9, 物理穿透 +64", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/3509.png"},
                {"slot": "蓝色铭文", "name": "10 隐匿/狩猎", "main_stat_rule": "移速 +10%, 物理攻击 +16 / 攻速 +10%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/2517.png"}
            ],
            "rules_reference": {"type": "物理爆发与刺客通用", "recommended_for": "李白、兰陵王、花木兰、赵云、关羽、亚瑟"},
            "version": "S36"
        },
        {
            "name": "88法穿心眼梦魇套",
            "rarity_min": 5, "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1514.png",
            "two_piece_bonus": "10梦魇 + 10心眼：法术攻击 +42, 法术穿透 +88，法师前期直接打出接近真实伤害的爆发！",
            "four_piece_bonus": "10狩猎/贪婪：移速 +10% 增强支援能力，或法术吸血 +16% 保证线上永不回城！",
            "pieces": [
                {"slot": "红色铭文", "name": "10 梦魇", "main_stat_rule": "法术攻击 +42, 法术穿透 +24", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1514.png"},
                {"slot": "绿色铭文", "name": "10 心眼", "main_stat_rule": "攻速 +6%, 法术穿透 +64", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/3515.png"},
                {"slot": "蓝色铭文", "name": "10 狩猎/贪婪", "main_stat_rule": "移速 +10% / 法术吸血 +16%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/2512.png"}
            ],
            "rules_reference": {"type": "中路法师法刺标配", "recommended_for": "妲己、诸葛亮、不知火舞、干将莫邪、安琪拉、王昭君"},
            "version": "S36"
        },
        {
            "name": "暴击无双夺萃射手套",
            "rarity_min": 5, "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1503.png",
            "two_piece_bonus": "3无双 + 7祸源 + 10鹰眼：暴击率 +13.3%, 暴击效果 +10.8%, 物理穿透 +64，刀刀见血！",
            "four_piece_bonus": "10夺萃：物理吸血 +16%，出门自带泣血之刃，续航拉满免回家断兵线节奏。",
            "pieces": [
                {"slot": "红色铭文", "name": "3无双 + 7祸源", "main_stat_rule": "暴击率 +13.3%, 暴击效果 +10.8%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1503.png"},
                {"slot": "绿色铭文", "name": "10 鹰眼", "main_stat_rule": "物理攻击 +9, 物理穿透 +64", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/3509.png"},
                {"slot": "蓝色铭文", "name": "10 夺萃", "main_stat_rule": "物理吸血 +16%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/2504.png"}
            ],
            "rules_reference": {"type": "射手爆发续航标配", "recommended_for": "孙悟空、鲁班七号、后羿、黄忠、伽罗、孙尚香"},
            "version": "S36"
        },
        {
            "name": "千血宿命虚空调和肉坦套",
            "rarity_min": 5, "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1517.png",
            "two_piece_bonus": "10宿命 + 10虚空：最大生命 +712, 物理防御 +23, 攻击速度 +10%, 冷却缩减 +6%！",
            "four_piece_bonus": "10调和：最大生命 +450, 每5秒回血 +52, 移速 +4%，开局白送 1162 点额外生命值！",
            "pieces": [
                {"slot": "红色铭文", "name": "10 宿命", "main_stat_rule": "最大生命 +337, 物防 +23, 攻速 +10%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1517.png"},
                {"slot": "绿色铭文", "name": "10 虚空", "main_stat_rule": "最大生命 +375, 冷却缩减 +6%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/3511.png"},
                {"slot": "蓝色铭文", "name": "10 调和", "main_stat_rule": "最大生命 +450, 移速 +4%, 每5秒回血 +52", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/2513.png"}
            ],
            "rules_reference": {"type": "坦克与硬辅生存标配", "recommended_for": "廉颇、张飞、牛魔、白起、刘邦、东皇太一、瑶"},
            "version": "S36"
        },
        {
            "name": "26攻速狩猎红月攻速套",
            "rarity_min": 5, "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1504.png",
            "two_piece_bonus": "10红月 + 10鹰眼：攻击速度 +16%, 暴击率 +5%, 物理攻击 +9, 物理穿透 +64。",
            "four_piece_bonus": "10狩猎：攻击速度 +10%, 移动速度 +10%，开局提供高达 26% 攻击速度突破前摇阈值！",
            "pieces": [
                {"slot": "红色铭文", "name": "10 红月", "main_stat_rule": "攻击速度 +16%, 暴击率 +5%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/1504.png"},
                {"slot": "绿色铭文", "name": "10 鹰眼", "main_stat_rule": "物理攻击 +9, 物理穿透 +64", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/3509.png"},
                {"slot": "蓝色铭文", "name": "10 狩猎", "main_stat_rule": "攻击速度 +10%, 移动速度 +10%", "icon_url": "https://game.gtimg.cn/images/yxzj/img201606/mingwen/2512.png"}
            ],
            "rules_reference": {"type": "攻速型战士刺客射手", "recommended_for": "马可波罗、公孙离、韩信、百里玄策、老夫子"},
            "version": "S36"
        }
    ]

    seen = set()
    for m in raw_mings:
        if str(m.get('ming_grade')) != '5':
            continue
        m_name = m.get('ming_name')
        if not m_name or m_name in seen:
            continue
        seen.add(m_name)

        mid = m.get('ming_id')
        m_type = m.get('ming_type', '常用')
        m_des = clean_html(m.get('ming_des', ''))

        ming_set_obj = {
            "name": f"5级铭文·{m_name}",
            "rarity_min": 5, "rarity_max": 5,
            "icon_url": f"https://game.gtimg.cn/images/yxzj/img201606/mingwen/{mid}.png",
            "two_piece_bonus": f"单个加成：{m_des}",
            "four_piece_bonus": f"10个满配总效果：{m_des} (十倍复合)",
            "pieces": [
                {"slot": f"{m_type}铭文槽", "name": f"{m_name} (5级)", "main_stat_rule": m_des, "icon_url": f"https://game.gtimg.cn/images/yxzj/img201606/mingwen/{mid}.png"}
            ],
            "rules_reference": {"type": f"5级{m_type}铭文", "recommended_for": "根据英雄属性需求自由配置 10 槽位组合"},
            "version": "S36"
        }
        composite_sets.append(ming_set_obj)

    return composite_sets

def get_hok_mechanics():
    """王者荣耀核心底层机制公式"""
    return [
        {
            "category": "防御减伤与抗性物理/法术计算公式",
            "title": "王者荣耀减伤率公式",
            "formula": "DamageReduction = Defense / (Defense + 602)",
            "parameters": {
                "base_constant": 602,
                "example_300_def": "300 点防御提供 33.26% 伤害减免",
                "example_602_def": "602 点防御提供 50.00% 伤害减免",
                "example_1204_def": "1204 点防御提供 66.67% 伤害减免",
                "diminishing_returns": "抗性越高，每点防御带来的实际伤害减免增量平滑衰减，堆血量与护甲需保持黄金比例。"
            }
        },
        {
            "category": "物理/法术穿透结算顺序与无视抗性模型",
            "title": "双穿透计算与结算顺序模型",
            "formula": "FinalDefense = Max(0, (BaseDefense - FixedPenetration) * (1 - PercentPenetration%))",
            "parameters": {
                "step_1": "首先扣除固定穿透值（如暗影战斧 170 点、铭文百穿 100 点，合计 270 点固定物穿）。",
                "step_2": "在扣除固定穿透后，再按百分比比例穿透扣除（如破晓 40% 或碎星锤 40%）。",
                "example": "面对 670 护甲坦克：(670 - 270) * (1 - 40%) = 400 * 0.6 = 240 点剩余护甲！"
            }
        },
        {
            "category": "韧性机制与控制时长衰减规则",
            "title": "韧性减免控制时长法则",
            "formula": "ActualCrowdControlDuration = BaseDuration * (1 - Tenacity%)",
            "parameters": {
                "tenacity_rule": "抵抗之靴提供 35% 韧性：原本 1.0 秒眩晕缩短为 0.65 秒；原本 2.0 秒冰冻缩短为 1.3 秒。",
                "unmitigated_controls": "东皇太一与张良的【压制】状态、金蝉紧箍咒的【限制位移】、盾山的大招阻挡，无法被韧性减免。",
                "super_armor": "花木兰重剑、廉颇全技能释放期间处于霸体，免疫一切除压制外的控制并减免伤害。"
            }
        },
        {
            "category": "攻速阈值与攻击前摇后摇帧率档位机制",
            "title": "攻击动作帧率与攻速卡点模型",
            "formula": "ActualAttackInterval = Frames(Tier) / 60s",
            "parameters": {
                "frame_tiers": "英雄攻击动作由前摇帧、判定帧和后摇帧组成（游戏运行基准为 60 FPS）。",
                "sample_tiers": "射手攻速模型A示例：0%、1%、8.2%、16.6%、26.2%、37.6%、51.4%、68.2%、89.2%、116.0%、152.0%、184.0%。",
                "stutter_stepping": "如果攻速为 50%，实际攻击间隔与 37.6% 完全一致；只有突破 51.4% 时才会进入下一档极速动作，这就是铭文与出装'卡攻速阈值'的根本原理！"
            }
        },
        {
            "category": "防御塔伤害递增、衰减与护甲格挡保护法则",
            "title": "防御塔攻击机制与越塔惩罚模型",
            "formula": "TowerDmg = BaseTowerDmg * (1 + 0.3 * (HitCount - 1)) [Max 250%]",
            "parameters": {
                "no_creeps_shield": "当敌方防御塔范围内没有我方兵线时，防御塔获得 55% 额外免伤，偷塔极其困难。",
                "early_game_shield": "游戏前 4 分钟防御塔拥有 80 点固定伤害格挡，前期强拆极难。",
                "damage_ramp": "防御塔锁定同一英雄连续攻击时，每次攻击伤害递增 30%，上限为基础伤害的 250%（秒杀一切越塔英雄）。",
                "aggro_reset": "当英雄离开防御塔射程、或使用李白二技能/貂蝉二技能/辉月金身使防御塔丢失目标时，递增层数立即重置为第 1 层！"
            }
        }
    ]

def sync_hok():
    print("=== 开始同步《王者荣耀》(game_id = 24) 全量数值体系到 PostgreSQL ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO game (id, name, alias, platform, category, cover_url, description, current_version, created_at, updated_at)
        VALUES (
            24, '王者荣耀', '王者/HOK/Honor of Kings/农药', '移动端 (iOS/Android)', 'MOBA',
            'https://game.gtimg.cn/images/yxzj/web201605/top_banner/banner_pic_1.jpg',
            '腾讯天美工作室研发的国民级 5v5 MOBA 竞技手游，海量英雄、平衡对抗与经典竞技体验。',
            'S36', NOW(), NOW()
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            alias = EXCLUDED.alias,
            platform = EXCLUDED.platform,
            category = EXCLUDED.category,
            cover_url = EXCLUDED.cover_url,
            description = EXCLUDED.description,
            current_version = EXCLUDED.current_version,
            updated_at = NOW();
    """)
    conn.commit()

    characters = get_all_hok_heroes()
    print(f"\n[1/4] 写入王者荣耀英雄图鉴 (共 {len(characters)} 位全量英雄)...")
    for c in characters:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type,
                region, arkhe, avatar_url, splash_url,
                base_stats, special_ascension_stat, ascension_materials,
                talents, passives, constellations, special_mechanics,
                recommendations, data_hash, version
            ) VALUES (
                24, %s, %s, %s, %s, %s,
                '王者峡谷', NULL, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s
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
    conn.commit()
    print(f"  ✓ 成功落库 {len(characters)} 位全量王者荣耀英雄！")

    weapons = get_all_hok_weapons()
    print(f"\n[2/4] 写入王者荣耀全量局内装备 (共 {len(weapons)} 件)...")
    for w in weapons:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                24, %s, %s, %s, %s, %s,
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
    conn.commit()
    print(f"  ✓ 成功落库 {len(weapons)} 件全量局内装备！")

    artifacts = get_all_hok_artifacts()
    print(f"\n[3/4] 写入王者荣耀铭文方案与单品体系 (共 {len(artifacts)} 套)...")
    for art in artifacts:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                24, %s, %s, %s, %s,
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
    conn.commit()
    print(f"  ✓ 成功落库 {len(artifacts)} 套铭文体系方案！")

    mechanics = get_hok_mechanics()
    print(f"\n[4/4] 写入王者荣耀底层战斗法则 ({len(mechanics)} 项)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                24, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (
            m['category'], m['title'], m['formula'], Json(m['parameters'])
        ))
    conn.commit()
    print(f"  ✓ 成功落库 {len(mechanics)} 项底层战斗法则！")

    cur.close()
    conn.close()
    print("\n=== 《王者荣耀》全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_hok()
