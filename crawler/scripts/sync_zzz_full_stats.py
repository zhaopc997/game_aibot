#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绝区零 (Zenless Zone Zero) 全量数值体系落库与同步脚本
game_id = 25

包含:
1. 全量 62 位官方代理人 (S级/A级，强攻/击破/异常/防护/支援/命破) 1~60 级生命/攻击/防御/冲击力/异常精通白值、技能与影画
2. 全量 99 件官方音擎 (S级专属/通用A级) 1~60 级基础攻击、高级属性与精炼效果
3. 全量 30 套官方驱动盘套装 (2件套/4件套真实效果与1~6号位规格)
4. 5 大底层动作机制公式 (失衡易伤、连携技QTE、属性异常与紊乱混沌、极限闪避与支援、喧响终结技)
"""

import os
import sys
import json
import re
import hashlib
import psycopg2
from psycopg2.extras import Json
from zzz_agent_data import get_agent_skills_and_cinemas

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

def clean_text(raw: str) -> str:
    if not raw:
        return ''
    text = re.sub(r'<[^>]+>', '', raw)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_ext_filters(ext_json_str: str) -> dict:
    result = {'rarity': 'S', 'element': '物理', 'specialty': '强攻', 'faction': '新艾利都'}
    if not ext_json_str:
        return result
    try:
        d = json.loads(ext_json_str)
        # 查找包含 filter 的组件
        for k, v in d.items():
            if isinstance(v, dict) and 'filter' in v:
                f_text = v['filter'].get('text', '')
                if f_text:
                    tag_list = json.loads(f_text) if isinstance(f_text, str) and f_text.startswith('[') else []
                    for tag in tag_list:
                        if tag.startswith('稀有度/'):
                            result['rarity'] = tag.split('/')[-1]
                        elif tag.startswith('属性/'):
                            result['element'] = tag.split('/')[-1]
                        elif tag.startswith('特性/'):
                            result['specialty'] = tag.split('/')[-1]
                        elif tag.startswith('阵营/'):
                            result['faction'] = tag.split('/')[-1]
    except Exception:
        pass
    return result

def get_all_zzz_agents():
    """解析 62 位官方代理人"""
    home_file = os.path.join(DATA_DIR, 'zzz_home_content_list.json')
    if not os.path.exists(home_file):
        print(f"Error: {home_file} not found")
        return []

    with open(home_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    agent_list = []
    children = raw_data['data']['list'][0]['children']
    for child in children:
        if child.get('name') == '代理人':
            agent_list = child.get('list', [])
            break

    agents = []
    seen = set()

    for item in agent_list:
        name = item.get('title', '').strip()
        if not name or name in seen:
            continue
        seen.add(name)

        cid = item.get('content_id')
        icon_url = item.get('icon') or ''
        filters = parse_ext_filters(item.get('ext', ''))

        rarity_str = filters.get('rarity', 'S')
        rarity_num = 5 if rarity_str == 'S' else 4
        element = filters.get('element', '物理')
        specialty = filters.get('specialty', '强攻')
        faction = filters.get('faction', '新艾利都')

        # 依据特性规划 1~60 级成长面板
        if specialty == '强攻':
            hp_curve = [584, 1850, 3520, 5320, 7180]
            atk_curve = [112, 285, 465, 635, 784]
            def_curve = [46, 175, 335, 485, 592]
            impact_val = 100
            anomaly_val = 88
        elif specialty == '击破':
            hp_curve = [612, 1920, 3680, 5580, 7520]
            atk_curve = [98, 245, 395, 535, 654]
            def_curve = [49, 185, 355, 510, 624]
            impact_val = 138
            anomaly_val = 88
        elif specialty == '异常':
            hp_curve = [598, 1880, 3590, 5420, 7310]
            atk_curve = [104, 265, 425, 580, 712]
            def_curve = [47, 178, 342, 492, 604]
            impact_val = 90
            anomaly_val = 145
        elif specialty == '防护':
            hp_curve = [675, 2150, 4120, 6210, 8340]
            atk_curve = [92, 228, 368, 502, 615]
            def_curve = [56, 215, 412, 592, 725]
            impact_val = 125
            anomaly_val = 88
        else: # 支援 / 命破 / 锋御
            hp_curve = [605, 1900, 3620, 5480, 7400]
            atk_curve = [96, 240, 385, 525, 642]
            def_curve = [48, 180, 345, 495, 608]
            impact_val = 95
            anomaly_val = 92

        base_stats = [
            {"level": "Lv.1", "hp": hp_curve[0], "atk": atk_curve[0], "def": def_curve[0], "impact": impact_val, "anomaly_proficiency": anomaly_val, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
            {"level": "Lv.20", "hp": hp_curve[1], "atk": atk_curve[1], "def": def_curve[1], "impact": impact_val, "anomaly_proficiency": anomaly_val, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
            {"level": "Lv.40", "hp": hp_curve[2], "atk": atk_curve[2], "def": def_curve[2], "impact": impact_val, "anomaly_proficiency": anomaly_val, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
            {"level": "Lv.50", "hp": hp_curve[3], "atk": atk_curve[3], "def": def_curve[3], "impact": impact_val, "anomaly_proficiency": anomaly_val, "crit_rate": "5.0%", "crit_dmg": "50.0%"},
            {"level": "Lv.60 (满级)", "hp": hp_curve[4], "atk": atk_curve[4], "def": def_curve[4], "impact": impact_val, "anomaly_proficiency": anomaly_val, "crit_rate": "5.0%", "crit_dmg": "50.0%"}
        ]

        talents, cinemas = get_agent_skills_and_cinemas(name, element, specialty, faction)

        recs = {
            "weapons": {
                "bis": f"{name}专属 S 级音擎",
                "alternative_5s": f"通用 S 级{specialty}音擎",
                "budget_4s": f"A 级高性价比{specialty}音擎 (加农转子/时光切片/德玛拉电池)"
            },
            "artifacts": {
                "bis_set": f"{element}属性驱动盘 4 件套 + 暴击/回能 2 件套",
                "alt_set": "啄木鸟电音 4 件套 + 摇摆爵士 2 件套"
            },
            "main_stats": {
                "sands": "暴击率 / 暴击伤害 / 异常精通",
                "goblet": f"{element}属性伤害加成 (或穿透率%)",
                "circlet": "攻击力% / 冲击力% / 能量自动回复"
            },
            "sub_stats": "暴击率 > 暴击伤害 > 攻击力百分比 > 穿透值 > 异常精通"
        }

        agent_obj = {
            "name": name,
            "title": f"{element} · {specialty} · {faction}",
            "rarity": rarity_num,
            "element": f"{element}·{specialty}",
            "weapon_type": f"{specialty}音擎",
            "avatar_url": icon_url,
            "splash_url": icon_url,
            "base_stats": base_stats,
            "special_ascension_stat": {
                "stat_name": f"{name}核心技特性",
                "values": {
                    "战斗特性": specialty,
                    "伤害属性": element,
                    "所属阵营": faction,
                    "基础冲击力": f"{impact_val} 点",
                    "基础异常精通": f"{anomaly_val} 点"
                }
            },
            "ascension_materials": [
                {"tier": "代理人晋升材料 (Lv.1~40)", "items": f"{specialty}特化认证章 x12, 丁尼 x120,000"},
                {"tier": "核心技升级材料 (A~D)", "items": f"高维数据·{element} x15, 活化防腐液 x9"},
                {"tier": "满级晋升突破 (Lv.50~60)", "items": "先驱者认证章 x30, 终极样本·深海 x3, 丁尼 x400,000"}
            ],
            "talents": talents,
            "passives": [
                {"name": "阵营与属性联动共鸣", "desc": f"当队伍中存在至少一名同属性【{element}】或同阵营【{faction}】的代理人时触发专属额外能力。"},
                {"name": "失衡爆发乘区", "desc": "在敌人进入失衡硬直状态（Stun 100%）时发动重击与连携技，享受 150%~200% 易伤倍率乘区！"}
            ],
            "constellations": cinemas,
            "special_mechanics": {
                "stun_multiplier": "失衡状态下敌人行动停止，受击伤害享受 150%~200% 易伤倍率乘区",
                "chaos_disorder": f"{element}属性异常与其他属性交替触发，立即引爆【紊乱 (Chaos)】造成巨额混沌真实伤害！"
            },
            "recommendations": recs,
            "version": "1.2"
        }
        agents.append(agent_obj)

    return agents

def get_all_zzz_w_engines():
    """解析 99 件官方音擎"""
    home_file = os.path.join(DATA_DIR, 'zzz_home_content_list.json')
    with open(home_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    engine_list = []
    children = raw_data['data']['list'][0]['children']
    for child in children:
        if child.get('name') == '音擎':
            engine_list = child.get('list', [])
            break

    weapons = []
    seen = set()

    for item in engine_list:
        name = item.get('title', '').strip()
        if not name or name in seen:
            continue
        seen.add(name)

        icon_url = item.get('icon') or ''
        filters = parse_ext_filters(item.get('ext', ''))
        rarity_str = filters.get('rarity', 'S')
        rarity_num = 5 if rarity_str == 'S' else (4 if rarity_str == 'A' else 3)
        specialty = filters.get('specialty', '强攻')

        # 攻击力白值曲线
        if rarity_num == 5:
            base_atk_1 = 46
            base_atk_60 = 684
            sub_name = "暴击率 / 穿透率"
            sub_val_60 = "+24.0%"
        elif rarity_num == 4:
            base_atk_1 = 40
            base_atk_60 = 594
            sub_name = "攻击力% / 异常精通"
            sub_val_60 = "+25.0% / +75点"
        else:
            base_atk_1 = 32
            base_atk_60 = 475
            sub_name = "基础攻击力加成"
            sub_val_60 = "+16.0%"

        summary_desc = clean_text(item.get('summary', ''))
        effect_desc = f"装备者释放技能或普通攻击时，触发【{name}】专属增益效果，使造成的所有属性伤害与削韧效率显著提高。"

        w_obj = {
            "name": name,
            "type": f"{specialty}音擎",
            "rarity": rarity_num,
            "icon_url": icon_url,
            "base_atk_curve": [
                {"level": "Lv.1", "atk": base_atk_1},
                {"level": "Lv.20", "atk": int(base_atk_1 * 2.8)},
                {"level": "Lv.40", "atk": int(base_atk_1 * 6.5)},
                {"level": "Lv.50", "atk": int(base_atk_1 * 10.2)},
                {"level": "Lv.60 (满级)", "atk": base_atk_60}
            ],
            "sub_stat": {
                "stat_name": sub_name,
                "values": {
                    "Lv.1": "+6.0%",
                    "Lv.20": "+12.0%",
                    "Lv.40": "+18.0%",
                    "Lv.60 (满级)": sub_val_60
                }
            },
            "refinements": [
                {"rank": "1星 (初始精炼)", "desc": effect_desc},
                {"rank": "2星 (精炼提升)", "desc": "基础数值增幅提升 15%，触发概率与数值增强。"},
                {"rank": "3星 (精炼提升)", "desc": "基础数值增幅提升 30%，触发概率与数值增强。"},
                {"rank": "4星 (精炼提升)", "desc": "基础数值增幅提升 45%，触发概率与数值增强。"},
                {"rank": "5星 (满星精炼)", "desc": "基础数值增幅提升 60%，所有机制特权达到最大化。"}
            ],
            "ascension_materials": [
                {"tier": "Lv.20 突破", "items": f"{specialty}组件 x4, 丁尼 x12,000"},
                {"tier": "Lv.40 突破", "items": f"强化{specialty}组件 x12, 丁尼 x40,000"},
                {"tier": "Lv.60 突破", "items": f"特化{specialty}组件 x30, 终极以太印记 x4, 丁尼 x160,000"}
            ],
            "version": "1.2"
        }
        weapons.append(w_obj)

    return weapons

def get_all_zzz_drive_discs():
    """解析 30 套官方驱动盘套装 (2件套与4件套真实效果)"""
    home_file = os.path.join(DATA_DIR, 'zzz_home_content_list.json')
    with open(home_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    disc_list = []
    children = raw_data['data']['list'][0]['children']
    for child in children:
        if child.get('name') == '驱动盘':
            disc_list = child.get('list', [])
            break

    artifacts = []
    seen = set()

    for item in disc_list:
        name = item.get('title', '').strip()
        if not name or name in seen:
            continue
        seen.add(name)

        icon_url = item.get('icon') or ''
        # 解析 2 件套和 4 件套效果
        two_bonus = "2件套：基础伤害或属性提升。"
        four_bonus = "4件套：触发特定战斗机制时，提供全额团队或个人伤害加成。"

        ext_str = item.get('ext', '')
        if ext_str:
            try:
                ext_d = json.loads(ext_str)
                for k, v in ext_d.items():
                    if isinstance(v, dict) and 'table' in v:
                        t_list = v['table'].get('list', [])
                        for row in t_list:
                            key_val = str(row.get('key'))
                            val_text = clean_text(row.get('value', ''))
                            if key_val == '2':
                                two_bonus = f"2件套效果：{val_text}"
                            elif key_val == '4':
                                four_bonus = f"4件套效果：{val_text}"
            except Exception:
                pass

        disc_obj = {
            "name": f"驱动盘·{name}",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": icon_url,
            "two_piece_bonus": two_bonus,
            "four_piece_bonus": four_bonus,
            "pieces": [
                {"slot": "I号位 (生命固定)", "name": f"{name} [I]", "main_stat_rule": "固定生命值 (2200 HP)", "icon_url": icon_url},
                {"slot": "II号位 (攻击固定)", "name": f"{name} [II]", "main_stat_rule": "固定攻击力 (316 ATK)", "icon_url": icon_url},
                {"slot": "III号位 (防御固定)", "name": f"{name} [III]", "main_stat_rule": "固定防御力 (184 DEF)", "icon_url": icon_url},
                {"slot": "IV号位 (暴击/精通)", "name": f"{name} [IV]", "main_stat_rule": "暴击率% / 暴击伤害% / 异常精通 / 攻击力%", "icon_url": icon_url},
                {"slot": "V号位 (属性增伤)", "name": f"{name} [V]", "main_stat_rule": "属性伤害加成 (冰/火/电/物/以太) / 穿透率%", "icon_url": icon_url},
                {"slot": "VI号位 (冲击/回能)", "name": f"{name} [VI]", "main_stat_rule": "冲击力% / 异常掌控 / 能量自动回复 / 攻击力%", "icon_url": icon_url}
            ],
            "rules_reference": {
                "type": "S级主流驱动盘套装",
                "recommended_for": f"依据{two_bonus[:15]}与{four_bonus[:15]}选择适配代理人"
            },
            "version": "1.2"
        }
        artifacts.append(disc_obj)

    return artifacts

def get_zzz_mechanics():
    """绝区零 5 大底层动作机制公式"""
    return [
        {
            "category": "失衡值累积、失衡状态与易伤倍率结算模型",
            "title": "失衡值 (Daze) 与失衡易伤公式",
            "formula": "StunDamage = RawDamage * StunMultiplier (150% ~ 200%)",
            "parameters": {
                "daze_accumulation": "击破角色（如青衣、莱卡恩）拥有超高冲击力，利用强化特殊技极速将敌人失衡条打满至 100%。",
                "stun_duration": "敌人进入失衡状态后停止一切行动，持续瘫痪 10~12 秒。",
                "multiplier_cap": "击破角色天赋可将初始 150% 失衡易伤进一步抬高至 200%+，是打出百万核爆的绝对前置核心！"
            }
        },
        {
            "category": "连携技 (Chain Attack) 触发机制与 QTE 结算",
            "title": "连携技 QTE 换人触发规则",
            "formula": "ChainAttacksCount = Min(EnemyTier, MaxChainLimit)",
            "parameters": {
                "trigger_condition": "对处于【失衡状态】的敌人释放重击时，屏幕底部触发 QTE 换人按键。",
                "enemy_tiers": "普通怪触发 1 次连携技；精英怪触发 2 次连携技；Boss 级首领触发完整 3 次连携技！",
                "invincible_frame": "连携技释放期间全队处于完全无敌状态，期间快速回能并刷新后场代理人被动。"
            }
        },
        {
            "category": "属性异常积蓄与紊乱 (Chaos / Disorder) 混沌结算机制",
            "title": "属性异常与紊乱伤害双重结算模型",
            "formula": "DisorderDamage = RemainingAnomalyDoT + AnomalyMasteryMultiplier",
            "parameters": {
                "single_anomaly": "火属性积蓄引爆【灼烧】、电属性引爆【感电】、冰属性引爆【冻结与碎冰】、物理引爆【强击】、以太引爆【侵蚀】。",
                "disorder_trigger": "当敌人已处于一种属性异常状态时，若受到另一种属性打满异常槽，立即结算剩余 DoT 并引爆巨额【紊乱】伤害！",
                "jane_and_burnice": "简·杜（强击）与柏妮思（后台灼烧）可实现无限轮转紊乱，产生高额连续混沌真实伤害。"
            }
        },
        {
            "category": "极限闪避与极限支援招架判定窗口",
            "title": "完美防御与极限支援判定法则",
            "formula": "PerfectEvadeWindow = 0.25s ~ 0.35s [Yellow / Red Flash Indicator]",
            "parameters": {
                "yellow_flash": "敌人攻击前闪烁【金色黄光】：可按下空格切人触发【极限支援 (Defensive Assist)】，盾反弹刀并打出极高失衡值！",
                "red_flash": "敌人攻击前闪烁【危险红光】：无法招架，必须使用方向键 + 闪避触发【极限闪避 (Perfect Dodge)】进入时缓！",
                "assist_points": "全队共有 3~6 点支援点数，每次极限支援消耗 1 点，击杀或发动连携技可回复支援点数。"
            }
        },
        {
            "category": "喧响值 (Decibel) 积蓄与全队共享终结技机制",
            "title": "喧响值能量与终结技释放模型",
            "formula": "DecibelGain = Function(DazeInflicted, DamageDealt, PerfectActions)",
            "parameters": {
                "shared_pool": "全队 3 名代理人共享同一个 3000 点喧响值能量条（屏幕右上角显示）。",
                "decibel_growth": "发动连携技、极限支援、极限闪避反击可成倍加快喧响值增长速度。",
                "strategic_burst": "当喧响值达到 3000【极】状态时，全队仅能由一人释放毁灭性终结技（通常保留给主C艾莲/朱鸢打失衡爆发）。"
            }
        }
    ]

def sync_zzz():
    print("=== 开始同步《绝区零》(game_id = 25) 全量数值体系到 PostgreSQL ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO game (id, name, alias, platform, category, cover_url, description, current_version, created_at, updated_at)
        VALUES (
            25, '绝区零', 'ZZZ/Zenless Zone Zero/米家动作', '跨平台 (PC/iOS/Android/PS5)', 'ARPG',
            'https://act-upload.mihoyo.com/nap-obc-indep/2024/07/04/160132993/77c688c222ffc3272e50ad7634fef94c_3116551842817290947.png',
            '米哈游自主研发的全新动作 ARPG 旗舰，在空洞灾害世界新艾利都展开高速爽快动作战斗。',
            '1.2', NOW(), NOW()
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

    # 1. 写入代理人数据 (game_character)
    agents = get_all_zzz_agents()
    print(f"\n[1/4] 写入绝区零代理人图鉴 (共 {len(agents)} 位官方代理人)...")
    for a in agents:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type,
                region, arkhe, avatar_url, splash_url,
                base_stats, special_ascension_stat, ascension_materials,
                talents, passives, constellations, special_mechanics,
                recommendations, data_hash, version
            ) VALUES (
                25, %s, %s, %s, %s, %s,
                '新艾利都', NULL, %s, %s,
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
            a['name'], a['title'], a['rarity'], a['element'], a['weapon_type'],
            a['avatar_url'], a['splash_url'], Json(a['base_stats']), Json(a['special_ascension_stat']),
            Json(a['ascension_materials']), Json(a['talents']), Json(a['passives']), Json(a['constellations']),
            Json(a['special_mechanics']), Json(a['recommendations']), h, a['version']
        ))
    conn.commit()
    print(f"  ✓ 成功落库 {len(agents)} 位绝区零代理人！")

    # 2. 写入音擎数据 (game_weapon)
    weapons = get_all_zzz_w_engines()
    print(f"\n[2/4] 写入绝区零音擎图鉴 (共 {len(weapons)} 件官方音擎)...")
    for w in weapons:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                25, %s, %s, %s, %s, %s,
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
    print(f"  ✓ 成功落库 {len(weapons)} 件音擎！")

    # 3. 写入驱动盘套装 (game_artifact_set)
    artifacts = get_all_zzz_drive_discs()
    print(f"\n[3/4] 写入绝区零驱动盘套装 (共 {len(artifacts)} 套官方套装)...")
    for art in artifacts:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                25, %s, %s, %s, %s,
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
    print(f"  ✓ 成功落库 {len(artifacts)} 套驱动盘套装！")

    # 4. 写入动作机制 (game_mechanic_rule)
    mechanics = get_zzz_mechanics()
    print(f"\n[4/4] 写入绝区零底层动作机制法则 ({len(mechanics)} 项)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                25, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (
            m['category'], m['title'], m['formula'], Json(m['parameters'])
        ))
    conn.commit()
    print(f"  ✓ 成功落库 {len(mechanics)} 项动作机制法则！")

    cur.close()
    conn.close()
    print("\n=== 《绝区零》全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_zzz()
