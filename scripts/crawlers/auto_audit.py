"""
Autonomous Data Quality & Health Inspection Engine (自动排查与巡检引擎)
Audits all 31 games against genre-specific blueprints, detects anomalies,
dirty data, attribute omissions, and generates actionable diagnosis reports.
"""

import json
import psycopg2
from .common.db import get_connection

GENRE_BLUEPRINTS = {
    '自走棋': {
        'min_chars': 50,
        'min_weapons': 25,
        'min_artifacts': 30,
        'min_mechanics': 3,
        'required_subtypes': ['符文', '阵容', '羁绊'],
        'description': '自走棋必须包含：弈子(>=50)、装备(>=25)、特质羁绊、强化符文、主流上分阵容、特殊机制'
    },
    '策略自走棋': {
        'min_chars': 50,
        'min_weapons': 25,
        'min_artifacts': 30,
        'min_mechanics': 3,
        'required_subtypes': ['符文', '阵容', '羁绊'],
        'description': '自走棋必须包含：弈子(>=50)、装备(>=25)、特质羁绊、强化符文、主流上分阵容、特殊机制'
    },
    '开放世界': {
        'min_chars': 35,
        'min_weapons': 20,
        'min_artifacts': 10,
        'min_mechanics': 3,
        'description': '开放世界/抽卡必须包含：角色全图鉴(>=35)、专属与高星武器(>=20)、圣遗物/声骸(>=10)、战斗机制'
    },
    'RPG': {
        'min_chars': 15,
        'min_weapons': 10,
        'min_artifacts': 5,
        'min_mechanics': 3,
        'description': 'RPG游戏必须包含：核心角色/同伴、核心武器装备、套装/遗器、机制规则'
    },
    'ARPG': {
        'min_chars': 6,
        'min_weapons': 6,
        'min_artifacts': 3,
        'min_mechanics': 3,
        'description': 'ARPG必须包含：职业/全法术形态、传奇武器、暗金装备/套装、战斗机制'
    },
    'CRPG': {
        'min_chars': 6,
        'min_weapons': 5,
        'min_artifacts': 2,
        'min_mechanics': 3,
        'description': 'CRPG必须包含：全职业与起源同伴、传奇神兵、构筑Build、D&D机制'
    },
    'MOBA': {
        'min_chars': 30,
        'min_weapons': 20,
        'min_artifacts': 3,
        'min_mechanics': 3,
        'description': 'MOBA必须包含：主流全定位英雄(>=30)、全核心出装(>=20)、特殊圣物/符文、对线经济机制'
    },
    'FPS': {
        'min_chars': 10,
        'min_weapons': 12,
        'min_artifacts': 2,
        'min_mechanics': 2,
        'description': 'FPS竞技必须包含：特工/传奇、枪械库(>=12)、防具/配件、身法弹道机制'
    },
    '动作': {
        'min_chars': 12,
        'min_weapons': 10,
        'min_artifacts': 6,
        'min_mechanics': 3,
        'description': '动作竞技必须包含：全英雄(>=12)、近战与远程武器(>=10)、核心魂玉、拼刀博弈机制'
    },
    '3D动作': {
        'min_chars': 10,
        'min_weapons': 6,
        'min_artifacts': 5,
        'min_mechanics': 3,
        'description': '3D动作动作必须包含：主力装甲角色、超限专属武器、专属圣痕套、星环时空机制'
    },
    '复古神秘学RPG': {
        'min_chars': 15,
        'min_weapons': 8,
        'min_artifacts': 1,
        'min_mechanics': 3,
        'description': '二次元卡牌必须包含：高阶神秘学家(>=15)、六星心相、四象灵智生克机制'
    },
    '和风RPG': {
        'min_chars': 50,
        'min_weapons': 1,
        'min_artifacts': 20,
        'min_mechanics': 3,
        'description': '和风式神录必须包含：主流全阶式神(>=50)、全套御魂(>=20)、御魂计算机制'
    },
    '战术竞技': {
        'min_chars': 4,
        'min_weapons': 15,
        'min_artifacts': 1,
        'min_mechanics': 2,
        'description': '吃鸡战术竞技必须包含：特种作战兵种、全枪械库(>=15)、配件机制'
    },
    '放置卡牌RPG': {
        'min_chars': 15,
        'min_weapons': 10,
        'min_artifacts': 5,
        'min_mechanics': 3,
        'description': '放置卡牌策略必须包含：虚空/神明英雄(>=15)、专属圣物(>=10)、阵奕符文(>=5)、战斗机制(>=3)'
    }
}

DEFAULT_BLUEPRINT = {
    'min_chars': 5,
    'min_weapons': 5,
    'min_artifacts': 2,
    'min_mechanics': 2,
    'description': '标准基础蓝图'
}


def run_autonomous_audit():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Fetch all games
            cur.execute('SELECT id, name, category, cover_url FROM game ORDER BY id ASC')
            games = cur.fetchall()

            audit_results = []

            for gid, name, cat, cover in games:
                bp = GENRE_BLUEPRINTS.get(cat, DEFAULT_BLUEPRINT)
                issues = []
                score = 100

                # Check Cover
                if not cover or not cover.strip():
                    issues.append('【高危】缺失游戏封面 cover_url')
                    score -= 20
                elif not (cover.startswith('/games/') or cover.startswith('http')):
                    issues.append(f'【低危】封面路径不规范: {cover}')
                    score -= 5

                # Check Characters
                cur.execute('SELECT count(*), jsonb_agg(talents), jsonb_agg(recommendations) FROM game_character WHERE game_id = %s', (gid,))
                c_row = cur.fetchone()
                c_cnt = c_row[0]
                talents_list = c_row[1] or []
                recs_list = c_row[2] or []

                if c_cnt < bp['min_chars']:
                    deficit = bp['min_chars'] - c_cnt
                    issues.append(f'【严重】角色/英雄数量严重不足: 当前 {c_cnt} 位，蓝图标准至少 {bp["min_chars"]} 位 (缺失 {deficit} 位)')
                    score -= min(35, deficit * 3)

                # Check Character Details Integrity
                empty_talents = sum(1 for t in talents_list if not t or len(t) == 0)
                if empty_talents > 0 and c_cnt > 0:
                    pct = int(empty_talents / c_cnt * 100)
                    if pct > 30:
                        issues.append(f'【中危】{empty_talents} 位角色 ({pct}%) 技能天赋 (talents) 字段为空')
                        score -= 15

                # Check Weapons
                cur.execute('SELECT count(*), count(DISTINCT type) FROM game_weapon WHERE game_id = %s', (gid,))
                w_cnt, w_types = cur.fetchone()

                if w_cnt < bp['min_weapons']:
                    deficit = bp['min_weapons'] - w_cnt
                    issues.append(f'【严重】武器/装备数量不足: 当前 {w_cnt} 件，蓝图标准至少 {bp["min_weapons"]} 件')
                    score -= min(25, deficit * 2)

                # Check Weapons Noise / Dirty Data
                if w_cnt > 400 and cat not in ['MOBA', '自走棋']:
                    issues.append(f'【高危】武器装备数量异常暴增 ({w_cnt}件)，疑似爬虫混入脏数据/Token！')
                    score -= 30

                cur.execute('''
                    SELECT count(*) FROM game_weapon 
                    WHERE game_id = %s AND (
                        name ILIKE '%%test%%' OR name ILIKE '%%dummy%%' OR name ILIKE '%%金币%%' OR name ILIKE '%%星%%费%%'
                    )
                ''', (gid,))
                dirty_w = cur.fetchone()[0]
                if dirty_w > 0:
                    issues.append(f'【高危】装备表中存在 {dirty_w} 条临时/噪音脏数据 (如含金币、测试或星级费率Token)')
                    score -= 20

                # Check Artifacts / Sets / Augments / Comps
                cur.execute('SELECT count(*), jsonb_agg(name) FROM game_artifact_set WHERE game_id = %s', (gid,))
                a_row = cur.fetchone()
                a_cnt = a_row[0]
                a_names = a_row[1] or []

                if a_cnt < bp['min_artifacts']:
                    issues.append(f'【严重】套装/圣遗物/羁绊数量不足: 当前 {a_cnt} 套，标准至少 {bp["min_artifacts"]} 套')
                    score -= 20

                # Check Genre Specific Subtypes (e.g. Autochess must have 符文, 阵容, 羁绊)
                if 'required_subtypes' in bp:
                    for req in bp['required_subtypes']:
                        has_req = any(req in name_item for name_item in a_names)
                        if not has_req:
                            issues.append(f'【严重】自走棋品类缺失关键子维度数据: 缺失【{req}】')
                            score -= 25

                # Check Mechanics
                cur.execute('SELECT count(*) FROM game_mechanic_rule WHERE game_id = %s', (gid,))
                m_cnt = cur.fetchone()[0]
                if m_cnt < bp['min_mechanics']:
                    issues.append(f'【中危】特殊核心机制规则过少: 当前 {m_cnt} 条，标准至少 {bp["min_mechanics"]} 条')
                    score -= 10

                score = max(0, min(100, score))
                level = 'HEALTHY' if score >= 85 else ('WARNING' if score >= 60 else 'CRITICAL')

                audit_results.append({
                    'id': gid,
                    'name': name,
                    'category': cat,
                    'chars': c_cnt,
                    'weapons': w_cnt,
                    'artifacts': a_cnt,
                    'mechanics': m_cnt,
                    'score': score,
                    'level': level,
                    'issues': issues
                })

            print('\n' + '=' * 100)
            print(f'{"ID":<3} | {"游戏名称":<14} | {"品类":<8} | {"角色":<4} | {"武器":<4} | {"套装":<4} | {"机制":<4} | {"健康分":<6} | {"状态":<8}')
            print('-' * 100)
            for res in audit_results:
                badge = '🟢 优良' if res['level'] == 'HEALTHY' else ('🟡 告警' if res['level'] == 'WARNING' else '🔴 严重')
                print(f'{res["id"]:<3} | {res["name"]:<14} | {res["category"]:<8} | {res["chars"]:<4} | {res["weapons"]:<4} | {res["artifacts"]:<4} | {res["mechanics"]:<4} | {res["score"]:<6} | {badge}')
            print('=' * 100 + '\n')

            # Print Actionable Defect List
            criticals = [r for r in audit_results if r['level'] == 'CRITICAL']
            warnings = [r for r in audit_results if r['level'] == 'WARNING']

            print(f'=== 自动排查诊断汇总 ===')
            print(f'已扫描游戏: {len(audit_results)} 款 | 🟢 优良: {len(audit_results) - len(criticals) - len(warnings)} | 🟡 告警: {len(warnings)} | 🔴 严重缺陷: {len(criticals)}\n')

            if criticals or warnings:
                print('--- 自动生成的缺陷诊断与待修复清单 (Actionable Defect List) ---')
                for r in criticals + warnings:
                    print(f'\n[{r["level"]}] ID {r["id"]} - 《{r["name"]}》 (品类: {r["category"]}, 健康分: {r["score"]}分):')
                    for issue in r['issues']:
                        print(f'  ❌ {issue}')

    finally:
        conn.close()


if __name__ == '__main__':
    run_autonomous_audit()
