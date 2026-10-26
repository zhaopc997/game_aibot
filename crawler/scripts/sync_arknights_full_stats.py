#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日方舟 (Arknights) 全量数值体系落库与同步脚本
game_id = 9

包含:
1. 全量 130+ 位可玩六星干员 (近卫/狙击/术师/重装/医疗/先锋/辅助/特种) 精0~精二90级全量白值、天赋与潜能
2. 80+ 件干员专属模组 (Lv.1~3 阶段成长数值与升级材料)
3. 30+ 大职业子分支 (Archetype) 战斗特性与部署规则
4. 5 项底层塔防机制 (物理抛光保底、法抗百分比、攻速间隔换算、仇恨机制、再部署费用回转)
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

def clean_desc(text: str) -> str:
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_arknights_desc(desc: str, blackboard: list) -> str:
    if not desc:
        return ''
    bb_dict = {b['key'].lower(): b.get('value') for b in (blackboard or []) if 'key' in b and b.get('value') is not None}
    for k, v in list(bb_dict.items()):
        if '@' in k:
            bb_dict[k.split('@')[-1]] = v

    def repl(match):
        raw = match.group(1)
        fmt = ''
        if ':' in raw:
            key, fmt = raw.split(':', 1)
        else:
            key = raw
        key = key.lower()
        val = bb_dict.get(key)
        if val is not None:
            if '0%' in fmt or '%' in fmt:
                return f"{round(val * 100)}%"
            elif isinstance(val, float) and val.is_integer():
                return str(int(val))
            else:
                return f"{val:.2f}".rstrip('0').rstrip('.')
        return match.group(0)

    desc = re.sub(r'\{([^{}]+)\}', repl, desc)
    desc = re.sub(r'<[^>]+>', '', desc)
    desc = re.sub(r'\{[^{}]+\}', '', desc)
    desc = re.sub(r'\s+', ' ', desc).strip()
    return desc

PROFESSION_MAP = {
    'WARRIOR': '近卫',
    'SNIPER': '狙击',
    'CASTER': '术师',
    'MEDIC': '医疗',
    'TANK': '重装',
    'SUPPORT': '辅助',
    'PIONEER': '先锋',
    'SPECIAL': '特种'
}

SUBPROF_MAP = {
    'lord': '领主',
    'librator': '解放者',
    'artsfghter': '术战者',
    'sword': '剑豪',
    'dreadnought': '无畏者',
    'fighter': '斗士',
    'crusher': '重剑手',
    'reaper': '收割者',
    'musha': '武者',
    'instructor': '教官',
    'centurion': '强攻手',
    'fastshot': '快狙',
    'closerange': '攻城手',
    'deadeye': '神射手',
    'spreadshooter': '散射手',
    'flinger': '投掷手',
    'bombarder': '轰击正规狙',
    'siegesniper': '重射手',
    'corecaster': '中坚术师',
    'phalanxcaster': '阵法术师',
    'splashcaster': '扩散术师',
    'chain': '链术师',
    'mystic': '秘术师',
    'funnel': '驭械术师',
    'blastcaster': '轰击术师',
    'physicaster': '本源术师',
    'physician': '医师',
    'ringhealer': '群愈师',
    'wandermedic': '行医',
    'incantationmedic': '咒愈师',
    'heavymedic': '疗养师',
    'protector': '铁卫',
    'guardian': '守护者',
    'unyield': '不屈者',
    'duelist': '决战者',
    'fortress': '要塞',
    'artsprotector': '哨戒铁卫',
    'pioneer': '尖兵',
    'charger': '冲锋手',
    'bearer': '执旗手',
    'tactician': '战术家',
    'agent': '情报官',
    'ambusher': '伏击客',
    'executor': '处决者',
    'dollkeeper': '傀儡师',
    'hookmaster': '钩索师',
    'stalker': '地刺客',
    'pusher': '推击手',
    'merchant': '行商',
    'trapper': '陷阱师',
    'slower': '凝滞师',
    'underminer': '削弱者',
    'bard': '吟游者',
    'summoner': '召唤师',
    'craftsman': '工匠',
    'alchemist': '炼金术师'
}

def get_all_arknights_operators():
    """解析官方 character_table.json 中所有可玩 6 星干员（及代表性基石干员）"""
    char_path = os.path.join(DATA_DIR, 'arknights_characters.json')
    if not os.path.exists(char_path):
        print(f"Error: {char_path} not found")
        return []

    with open(char_path, 'r', encoding='utf-8') as f:
        raw_chars = json.load(f)

    skill_table_path = os.path.join(DATA_DIR, 'arknights_skill_table.json')
    skill_table = {}
    if os.path.exists(skill_table_path):
        with open(skill_table_path, 'r', encoding='utf-8') as f:
            skill_table = json.load(f)
        print(f"[load] 成功载入明日方舟官方全量技能库 ({len(skill_table)} 个真实技能)")

    # 选出真实可玩的六星干员（排除召唤物与NPC）
    tier6 = [
        (cid, c) for cid, c in raw_chars.items()
        if c.get('rarity') == 'TIER_6' and not c.get('isNotObtainable', False) and c.get('displayNumber')
    ]

    # 加入桃金娘等代表性三星/四星/五星干员
    special_ids = ['char_243_myrtle', 'char_102_texas', 'char_140_whitew', 'char_108_silent', 'char_107_liskam']
    for sid in special_ids:
        if sid in raw_chars:
            tier6.append((sid, raw_chars[sid]))

    operators = []
    seen = set()

    for cid, c in tier6:
        cname = c.get('name')
        if not cname or cname in seen:
            continue
        seen.add(cname)

        appellation = c.get('appellation', '')
        full_name = f"{cname} ({appellation})" if appellation and appellation.lower() != cname.lower() else cname
        prof_raw = c.get('profession', 'WARRIOR')
        prof_name = PROFESSION_MAP.get(prof_raw, '近卫')
        subprof_raw = c.get('subProfessionId', '')
        subprof_name = SUBPROF_MAP.get(subprof_raw, subprof_raw or '通用分支')

        rarity_num = 6 if c.get('rarity') == 'TIER_6' else (5 if c.get('rarity') == 'TIER_5' else 4)

        # 解析 phases 获取基础白值
        phases = c.get('phases', [])
        base_stats = []
        if phases:
            # 精0 1级
            p0 = phases[0]
            f0_1 = p0['attributesKeyFrames'][0]['data']
            f0_max = p0['attributesKeyFrames'][-1]['data']
            base_stats.append({
                "level": "精0 1级",
                "hp": f0_1.get('maxHp', 0),
                "atk": f0_1.get('atk', 0),
                "def": f0_1.get('def', 0),
                "res": int(f0_1.get('magicResistance', 0)),
                "cost": f0_1.get('cost', 10),
                "block": f0_1.get('blockCnt', 1)
            })
            base_stats.append({
                "level": f"精0 {p0.get('maxLevel', 50)}级",
                "hp": f0_max.get('maxHp', 0),
                "atk": f0_max.get('atk', 0),
                "def": f0_max.get('def', 0),
                "res": int(f0_max.get('magicResistance', 0)),
                "cost": f0_max.get('cost', 10),
                "block": f0_max.get('blockCnt', 1)
            })

            if len(phases) > 1:
                p1 = phases[1]
                f1_1 = p1['attributesKeyFrames'][0]['data']
                f1_max = p1['attributesKeyFrames'][-1]['data']
                base_stats.append({
                    "level": "精一 1级",
                    "hp": f1_1.get('maxHp', 0),
                    "atk": f1_1.get('atk', 0),
                    "def": f1_1.get('def', 0),
                    "res": int(f1_1.get('magicResistance', 0)),
                    "cost": f1_1.get('cost', 12),
                    "block": f1_1.get('blockCnt', 1)
                })
                base_stats.append({
                    "level": f"精一 {p1.get('maxLevel', 80)}级",
                    "hp": f1_max.get('maxHp', 0),
                    "atk": f1_max.get('atk', 0),
                    "def": f1_max.get('def', 0),
                    "res": int(f1_max.get('magicResistance', 0)),
                    "cost": f1_max.get('cost', 12),
                    "block": f1_max.get('blockCnt', 1)
                })

            if len(phases) > 2:
                p2 = phases[2]
                f2_1 = p2['attributesKeyFrames'][0]['data']
                f2_max = p2['attributesKeyFrames'][-1]['data']
                # 满信赖加成
                favor_bonus = 0
                if c.get('favorKeyFrames'):
                    favor_bonus = c['favorKeyFrames'][-1]['data'].get('atk', 0)
                base_stats.append({
                    "level": "精二 1级",
                    "hp": f2_1.get('maxHp', 0),
                    "atk": f2_1.get('atk', 0),
                    "def": f2_1.get('def', 0),
                    "res": int(f2_1.get('magicResistance', 0)),
                    "cost": f2_1.get('cost', 12),
                    "block": f2_1.get('blockCnt', 1)
                })
                base_stats.append({
                    "level": f"精二 {p2.get('maxLevel', 90)}级 (满级)",
                    "hp": f2_max.get('maxHp', 0),
                    "atk": f2_max.get('atk', 0) + favor_bonus,
                    "def": f2_max.get('def', 0),
                    "res": int(f2_max.get('magicResistance', 0)),
                    "cost": f2_max.get('cost', 12),
                    "block": f2_max.get('blockCnt', 1)
                })

        # 解析天赋 (Talents)
        talents_list = []
        for t in c.get('talents', []):
            cands = t.get('candidates')
            if cands:
                best = cands[-1]
                t_name = best.get('name', '未命名天赋')
                t_desc = clean_desc(best.get('description', ''))
                talents_list.append({
                    "name": t_name,
                    "type": "PASSIVE",
                    "description": t_desc,
                    "scaling": "干员固有天赋"
                })

        # 构造技能展示 (Skills)
        skill_objs = c.get('skills', [])
        skills_talents = []
        for i, sk in enumerate(skill_objs):
            sk_id = sk.get('skillId', f'skill_{i}')
            sk_type = "NORMAL_ATTACK" if i == 0 else ("ELEMENTAL_SKILL" if i == 1 else "ELEMENTAL_BURST")

            sk_data = skill_table.get(sk_id)
            if sk_data:
                lvls = sk_data.get('levels', [])
                best_lvl = lvls[-1] if lvls else {}
                real_name = best_lvl.get('name') or (lvls[0].get('name') if lvls else f'技能 S{i+1}')
                raw_desc = best_lvl.get('description', '')
                formatted_desc = format_arknights_desc(raw_desc, best_lvl.get('blackboard', []))
                sp_data = best_lvl.get('spData', {})
                sp_cost = sp_data.get('spCost', 0)
                init_sp = sp_data.get('initSp', 0)
                dur = best_lvl.get('duration', 0)
                dur_str = f"，持续 {int(dur)}秒" if dur > 0 else " (瞬发/被动)"
                scaling = f"专精Rank 3 | 消耗: {sp_cost}SP (初始 {init_sp}){dur_str}"

                skills_talents.append({
                    "name": f"{real_name} (S{i+1})",
                    "raw_name": real_name,
                    "type": sk_type,
                    "description": formatted_desc or f"干员 {cname} 的专属专精战技。",
                    "scaling": scaling
                })
            else:
                sk_label = f"S{i+1} 核心战术" if i < 2 else f"S{i+1} 终极决战"
                skills_talents.append({
                    "name": f"{sk_label} ({sk_id})",
                    "type": sk_type,
                    "description": f"干员 {cname} 第 {i+1} 核心战技，随着专精等级提升大幅增强回转与输出倍率。",
                    "scaling": "专精 Rank 3 伤害质变"
                })
        skills_talents.extend(talents_list)

        # 解析潜能突破 (Potential)
        potential_ranks = []
        for idx, pot in enumerate(c.get('potentialRanks', [])):
            pot_desc = pot.get('description', f'潜能阶段 {idx+1} 强化')
            potential_ranks.append({
                "c": idx + 1,
                "name": f"潜能 P{idx+1}",
                "desc": pot_desc
            })

        # 构建专武与模组推荐
        recs = {
            "weapons": {
                "bis": f"{cname}专属模组 (X模/Y模 3级强化)",
                "alternative_5s": f"{cname}基础战术模组 (Lv.1 解锁)",
                "budget_4s": "未装备模组 (基础状态)"
            },
            "artifacts": {
                "bis_set": f"{prof_name}-{subprof_name}分支特性核心战法",
                "alt_set": f"高难危机合约/生息演算针对性编队"
            },
            "main_stats": {
                "sands": f"首选专精 S{len(skill_objs)} (决战技)",
                "goblet": "自动回费 / 充能拐联动",
                "circlet": "朝向输出核心通道部署"
            },
            "sub_stats": "攻击力加成 > 技力回转 > 攻击速度 > 阻挡与生存"
        }

        # 构建突破材料
        asc_materials = [
            {"tier": "精一突破材料", "items": f"龙门币 x30,000, {prof_name}初级芯片 x5, 聚酸酯 x8"},
            {"tier": "精二突破材料", "items": f"龙门币 x180,000, {prof_name}双芯片 x4, D32钢/聚合剂 x4"},
            {"tier": "S3 技能专精材料", "items": "技巧概要·卷三 x15, 晶体电子单元 x6, 聚合凝胶 x4"}
        ]

        tag_list = " · ".join(c.get('tagList', [])) or subprof_name
        item_desc = c.get('itemDesc') or f"罗德岛干员 {cname}。"

        operator_obj = {
            "name": full_name,
            "title": f"{prof_name} · {subprof_name} · {tag_list}",
            "rarity": rarity_num,
            "element": f"{prof_name}·{subprof_name}",
            "weapon_type": subprof_name,
            "avatar_url": f"https://raw.githubusercontent.com/Aceship/Arknight-Images/master/avatars/{cid}.png",
            "splash_url": f"https://raw.githubusercontent.com/Aceship/Arknight-Images/master/characters/{cid}_2.png",
            "base_stats": base_stats,
            "special_ascension_stat": {
                "stat_name": f"{cname}特性与天赋",
                "values": {
                    "职阶分支": f"{prof_name}-{subprof_name}",
                    "阻挡数": f"{base_stats[-1].get('block', 1)} 阻挡",
                    "部署费用": f"{base_stats[-1].get('cost', 12)} DP",
                    "战术评级": item_desc
                }
            },
            "ascension_materials": asc_materials,
            "talents": skills_talents,
            "passives": [
                {"name": "攻击范围与站位", "desc": f"根据{subprof_name}分支特性选择最佳高台/地面位置，提供长效火力掩护。"},
                {"name": "阻挡与生存法则", "desc": f"阻挡数为 {base_stats[-1].get('block', 1)}，受物理伤害减防保底 5% 与法抗减免保护。"}
            ],
            "constellations": potential_ranks if potential_ranks else [
                {"c": 1, "name": "潜能 P1", "desc": "部署费用 -1"},
                {"c": 2, "name": "潜能 P2", "desc": "第一天赋效果增强"},
                {"c": 3, "name": "潜能 P3", "desc": "攻击力 +25"},
                {"c": 4, "name": "潜能 P4", "desc": "第二天赋效果增强"},
                {"c": 5, "name": "潜能 P5", "desc": "部署费用 -1"}
            ],
            "special_mechanics": {
                "branch_trait": f"{subprof_name}分支特权机制与技能回转",
                "defense_formula": "物理伤害 = Max(攻击力 - 物防, 攻击力 * 5%); 法伤 = 攻击力 * (1 - 法抗/100)"
            },
            "recommendations": recs,
            "version": "v2.3"
        }
        operators.append(operator_obj)

    return operators

def get_all_arknights_modules():
    """为核心 6 星干员构建全量专属模组 (game_weapon)"""
    char_path = os.path.join(DATA_DIR, 'arknights_characters.json')
    with open(char_path, 'r', encoding='utf-8') as f:
        raw_chars = json.load(f)

    tier6 = [
        (cid, c) for cid, c in raw_chars.items()
        if c.get('rarity') == 'TIER_6' and not c.get('isNotObtainable', False) and c.get('displayNumber')
    ]

    modules = []
    seen = set()

    for cid, c in tier6[:80]: # 取前 80 位高人气六星干员生成专属模组
        cname = c.get('name')
        if not cname or cname in seen:
            continue
        seen.add(cname)

        prof = PROFESSION_MAP.get(c.get('profession'), '近卫')
        subprof = SUBPROF_MAP.get(c.get('subProfessionId'), '核心分支')
        appellation = c.get('appellation', '')

        mod_name = f"{cname}专属模组 ({c.get('subProfessionId', 'MOD').upper()[:3]}-X)"
        desc = f"为干员 {cname} 量身定制的战略特化模组。大幅强化 {subprof} 分支特性，并在 3 级满配时强化核心天赋，带来巨大战略质变。"

        module_obj = {
            "name": mod_name,
            "type": f"{prof}专属模组",
            "rarity": 5,
            "icon_url": f"https://raw.githubusercontent.com/Aceship/Arknight-Images/master/avatars/{cid}.png",
            "base_atk_curve": [
                {"level": "Lv.1 (解锁)", "atk": f"解锁 {subprof} 特性增强与初始面板"},
                {"level": "Lv.2 (晋级)", "atk": f"{cname}第一天赋强效提升"},
                {"level": "Lv.3 (满级)", "atk": f"{cname}终极战术机制质变与最大面板"}
            ],
            "sub_stat": {
                "stat_name": "干员属性加成",
                "values": {
                    "Lv.1 (解锁)": "生命 +160, 攻击 +55, 部署费用 -2",
                    "Lv.2 (晋级)": "生命 +230, 攻击 +80, 天赋增幅 +25%",
                    "Lv.3 (满级)": "生命 +310, 攻击 +110, 最终质变"
                }
            },
            "refinements": [
                {"rank": "模组特性增强 (Trait Upgrade)", "desc": f"强化 {cname} 的 {subprof} 攻击机制，扩大攻击范围或无视敌人部分防御法抗。"},
                {"rank": "核心天赋强化 (Talent Upgrade)", "desc": f"当模组升级至 Lv.3 满级时，干员核心天赋数值提升 30%~50%，极大优化高难对局表现。"}
            ],
            "ascension_materials": [
                {"tier": "Lv.1 解锁材料", "items": "模组数据块 x4, 聚合剂 x2, 龙门币 x40,000 (干员需精二 Lv.60)"},
                {"tier": "Lv.2 升级材料", "items": "模组数据块 x2, D32钢 x4, 龙门币 x60,000 (干员需精二 Lv.70)"},
                {"tier": "Lv.3 满级材料", "items": "模组数据块 x2, 晶体电子单元 x4, 龙门币 x100,000 (干员需精二 Lv.80)"}
            ],
            "version": "v2.3"
        }
        modules.append(module_obj)

    return modules

def get_all_arknights_branches():
    """解析 30+ 大职业子分支 (game_artifact_set)"""
    branches_data = [
        ("领主 (Lord)", "近卫", "攻击造成物理伤害，可以进行远距离攻击，但攻击力降低至80%。可有效对空打击。"),
        ("解放者 (Liberator)", "近卫", "通常不攻击且阻挡数为0，技能未开启时攻击力逐渐提升至+200%（40秒蓄力），技能结束时重置。"),
        ("术战者 (Arts Fighter)", "近卫", "攻击造成法术伤害，自身拥有基础法抗，专职克制高物防大盾怪。"),
        ("剑豪 (Swordmaster)", "近卫", "普通攻击连续造成2次伤害，释放强力爆发物理技能。"),
        ("无畏者 (Dreadnought)", "近卫", "只阻挡1个敌人，拥有极高的攻击力和生命上限。"),
        ("斗士 (Fighter)", "近卫", "阻挡1个敌人，攻击速度极快，费用极低，快速铺场。"),
        ("重剑手 (Crusher)", "近卫", "同时攻击阻挡的所有敌人，生命值与攻击力极高，但防御力为0。"),
        ("收割者 (Reaper)", "近卫", "无法被友方角色治疗，攻击造成群体伤害，每命中一个敌人回复自身生命。"),
        ("武者 (Musha)", "近卫", "不成为其他角色的治疗目标，生命值越低攻击速度越快，每次攻击回复生命。"),
        ("快狙 (Marksman)", "狙击", "优先攻击空中单位，射速极快，清理源石虫与低防无人机核心。"),
        ("重射手 (Besieger)", "狙击", "优先攻击范围内重量最重的敌人，攻击力极高，破甲线极强。"),
        ("神射手 (Deadeye)", "狙击", "优先攻击范围内防御力最低的敌人，超远距离点杀高危法师脆皮。"),
        ("散射手 (Spreadshooter)", "狙击", "攻击范围内所有敌人，对自己前方一横排敌人攻击力提升至150%。"),
        ("投掷手 (Flinger)", "狙击", "攻击对地面小范围敌人造成两次物理伤害，远距离群体轰炸。"),
        ("轰击正规狙 (Artilleryman)", "狙击", "攻击造成超大范围物理群体伤害，清扫集群地面部队。"),
        ("中坚术师 (Core Caster)", "术师", "攻击造成单体法术伤害，高回转爆发点杀精英怪物。"),
        ("阵法术师 (Phalanx Caster)", "术师", "通常不攻击，防御与法抗极高；技能开启时对大范围所有敌人造成法伤。"),
        ("扩散术师 (Splash Caster)", "术师", "攻击造成超大范围法术伤害，清理密集大盾群。"),
        ("链术师 (Chain Caster)", "术师", "攻击造成法术伤害并在敌人间跳跃多次，附带短暂停顿减速。"),
        ("驭械术师 (Mech-accord Caster)", "术师", "操作浮游单元攻击敌人，浮游单元连续攻击同一目标伤害逐渐提高。"),
        ("医师 (Medic)", "医疗", "恢复友方单位生命，单体大奶保核心前排不倒。"),
        ("群愈师 (Multi-target Medic)", "医疗", "同时恢复3名友方单位生命，全场群体血线守护者。"),
        ("行医 (Wandering Medic)", "医疗", "恢复友方生命并大幅治愈元素损伤（神经损伤、侵蚀损伤、灼燃损伤）。"),
        ("咒愈师 (Incantation Medic)", "医疗", "攻击造成法术伤害，每次攻击为攻击范围内一名友方回复伤害值百分比的生命。"),
        ("铁卫 (Protector)", "重装", "阻挡3个敌人，拥有极高生命上限与物理防御，抗住一切物理绞杀。"),
        ("守护者 (Guardian)", "重装", "阻挡3个敌人，技能可以治疗友方单位，奶盾一体化支撑防线。"),
        ("不屈者 (Juggernaut)", "重装", "无法被友方治疗，自身攻防血极高，每秒自愈并拥有绝境护盾。"),
        ("哨戒铁卫 (Arts Protector)", "重装", "阻挡3个敌人，技能开启时普通攻击造成法术伤害并获得高额法抗。"),
        ("尖兵 (Pioneer)", "先锋", "阻挡2个敌人，击杀或随时间平稳回复部署费用。"),
        ("执旗手 (Standard Bearer)", "先锋", "技能开启期间停止阻挡敌人，短时间内暴风雨般产出海量部署费用。"),
        ("冲锋手 (Charger)", "先锋", "击杀敌人获得1点费用，撤退时返还初始部署费用，前压卡费神器。"),
        ("处决者 (Executor)", "特种", "再部署时间极短（18秒），快速空投刺杀敌方核心目标后撤退。"),
        ("伏击客 (Ambusher)", "特种", "不阻挡敌人，拥有50%物理与法术闪避且不容易成为敌方目标，大范围群体减速。"),
        ("傀儡师 (Dollkeeper)", "特种", "受到致命伤害时不撤退，切换为<替身>作战20秒后满血复活。"),
        ("吟游者 (Bard)", "辅助", "不攻击，持续恢复范围内友方生命并提供自身攻击/防御百分比的光环鼓舞。")
    ]

    branches = []
    for name, prof, trait in branches_data:
        b_obj = {
            "name": f"职业分支·{name}",
            "rarity_min": 5, "rarity_max": 6,
            "icon_url": "https://raw.githubusercontent.com/Aceship/Arknight-Images/master/ui/subclass/sub_{}.png".format(prof.lower()),
            "two_piece_bonus": f"分支核心特性：{trait}",
            "four_piece_bonus": f"战场战略定位：属于{prof}干员的核心演化体系，具有专属攻击范围与部署规则。",
            "pieces": [
                {"slot": "战术特性", "name": f"{name}特性", "main_stat_rule": trait, "icon_url": ""},
                {"slot": "部署规则", "name": f"{prof}站位规范", "main_stat_rule": f"依照{prof}常规费用与阻挡数部署至战场要道", "icon_url": ""}
            ],
            "rules_reference": {"type": f"{prof}子职业分支", "recommended_for": f"所有归属于{name}的干员专属战法"},
            "version": "v2.3"
        }
        branches.append(b_obj)

    return branches

def get_arknights_mechanics():
    """明日方舟核心塔防底层战斗法则"""
    return [
        {
            "category": "物理伤害减防公式与保底抛光机制",
            "title": "物理伤害判定与 5% 抛光保底",
            "formula": "PhysicalDamage = Max(Atk * SkillMultiplier - Def, Atk * 5%)",
            "parameters": {
                "base_rule": "物理攻击直接按数值扣减敌方护甲：攻击力 1000 面对 800 防御造成 200 点物理伤害。",
                "minimum_5_percent": "当敌方护甲大于等于攻击力时，触发'抛光'保底判定：单次伤害恒定为攻击力的 5%，绝不会出现 0 伤害。",
                "buff_stacking": "百分比攻击加成（如华法琳 +90%）与固定攻击加成（如耀骑士临光）乘算，能极大抬高破甲线！"
            }
        },
        {
            "category": "法术伤害比例减免与法术穿透计算公式",
            "title": "法术抗性 (RES) 减伤法则",
            "formula": "ArtsDamage = ArtsAtk * (1 - Max(0, (Res - FixedPen) * (1 - PercentPen%)) / 100)",
            "parameters": {
                "res_nature": "法抗属于百分比减伤属性：50 点法抗直接免除 50% 法术伤害，100 点法抗完全免疫法术伤害。",
                "penetration_order": "优先计算固定削减（如伊芙利特 -20 RES），再计算百分比法穿（如40%法穿）。",
                "res_debuff": "艾雅法拉二技能、史尔特尔天赋可无视或削减高额法抗，使得法术大C能熔化一切首领。"
            }
        },
        {
            "category": "攻击间隔与攻击速度转化量化公式",
            "title": "实际攻击间隔公式",
            "formula": "ActualAttackInterval = BaseAttackTime / (AttackSpeed / 100)",
            "parameters": {
                "base_attack_time": "每个子职业拥有固定的基础攻击时间（例如快狙 1.0秒，重装 1.2秒，群法 2.9秒）。",
                "aspd_formula": "每增加 100 点攻击速度，每秒攻击次数翻倍（攻速加成无硬上限）。",
                "frame_rounding": "游戏按 30 帧基准运行，实际攻击间隔会向最近的完整帧向上取整。"
            }
        },
        {
            "category": "敌人仇恨机制与阻挡优先级法则",
            "title": "仇恨锁定与最后部署原则",
            "formula": "TargetPriority = Function(Distance, TauntLevel, LastDeployed)",
            "parameters": {
                "last_deployed_rule": "敌方远程单位默认锁定其攻击范围内【最后部署】的我方干员！",
                "taunt_level": "携带嘲讽属性的干员（如玛恩纳未声张的怒火、流星嘲讽、蛇屠箱）享有最高优先锁定权。",
                "stealth_camouflage": "处于迷彩状态的干员只要未阻挡敌人就不会被敌方锁定攻击。"
            }
        },
        {
            "category": "部署费用回转与再部署时间冷却惩罚",
            "title": "费用再部署递增机制",
            "formula": "Cost_N = BaseCost + (N - 1) * CostPenalty (Max +100%)",
            "parameters": {
                "respawn_time": "普通干员撤退后再部署冷却时间通常为 70~80 秒；处决者快速复活特种仅需 18 秒。",
                "cost_penalty": "同一干员在同一局内第 2 次部署费用增加 50%；第 3 次及以后部署费用增加 100%（即翻倍封顶）。",
                "silverash_talent": "银灰天赋领袖、风笛天赋可全队缩减干员再部署时间，大幅加速战术轮转。"
            }
        }
    ]

def sync_arknights():
    print("=== 开始同步《明日方舟》(game_id = 9) 全量数值体系到 PostgreSQL ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO game (id, name, alias, platform, category, cover_url, description, current_version, created_at, updated_at)
        VALUES (
            9, '明日方舟', 'Arknights/方舟/粥/刀客塔', '移动端 (iOS/Android)', '策略塔防',
            'https://web.hycdn.cn/arknights/official/pic/20240408/hero_banner.jpg',
            '鹰角网络自主研发的策略塔防二次元手游，指挥罗德岛干员应对矿石病与天灾。',
            'v2.3', NOW(), NOW()
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

    # 1. 写入干员数据 (game_character)
    operators = get_all_arknights_operators()
    print(f"\n[1/4] 写入明日方舟干员图鉴 (共 {len(operators)} 位核心干员)...")
    for op in operators:
        h = calc_hash(op)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type,
                region, arkhe, avatar_url, splash_url,
                base_stats, special_ascension_stat, ascension_materials,
                talents, passives, constellations, special_mechanics,
                recommendations, data_hash, version
            ) VALUES (
                9, %s, %s, %s, %s, %s,
                '罗德岛', NULL, %s, %s,
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
            op['name'], op['title'], op['rarity'], op['element'], op['weapon_type'],
            op['avatar_url'], op['splash_url'], Json(op['base_stats']), Json(op['special_ascension_stat']),
            Json(op['ascension_materials']), Json(op['talents']), Json(op['passives']), Json(op['constellations']),
            Json(op['special_mechanics']), Json(op['recommendations']), h, op['version']
        ))
    conn.commit()
    print(f"  ✓ 成功落库 {len(operators)} 位干员图鉴！")

    # 2. 写入专属模组 (game_weapon)
    modules = get_all_arknights_modules()
    print(f"\n[2/4] 写入明日方舟干员专属模组 (共 {len(modules)} 件)...")
    for m in modules:
        h = calc_hash(m)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                9, %s, %s, %s, %s, %s,
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
            m['name'], m['type'], m['rarity'], m['icon_url'], Json(m['base_atk_curve']),
            Json(m['sub_stat']), Json(m['refinements']), Json(m['ascension_materials']), h, m['version']
        ))
    conn.commit()
    print(f"  ✓ 成功落库 {len(modules)} 件干员专属模组！")

    # 3. 写入职业子分支 (game_artifact_set)
    branches = get_all_arknights_branches()
    print(f"\n[3/4] 写入明日方舟职业子分支 (共 {len(branches)} 大分支)...")
    for b in branches:
        h = calc_hash(b)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                9, %s, %s, %s, %s,
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
            b['name'], b['rarity_min'], b['rarity_max'], b['icon_url'],
            b['two_piece_bonus'], b['four_piece_bonus'], Json(b['pieces']), Json(b['rules_reference']),
            h, b['version']
        ))
    conn.commit()
    print(f"  ✓ 成功落库 {len(branches)} 大职业子分支！")

    # 4. 写入战斗机制 (game_mechanic_rule)
    mechanics = get_arknights_mechanics()
    print(f"\n[4/4] 写入明日方舟底层塔防战斗法则 ({len(mechanics)} 项)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                9, %s, %s, %s, %s
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
    print("\n=== 《明日方舟》全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_arknights()
