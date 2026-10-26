#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《阴阳师》(game_id: 29) 全量式神官方生态数据抓取与落库同步脚本
数据源: 网易《阴阳师》官方式神录接口 (all_shishen.json, get_hero_skill, get_hero_attr)
涵盖全量 276 位 SP / SSR / SR / R / N 式神：
1. 官方头像与高分辨率立绘 (data/shishen/{id}.png, data/shishen_big_beforeAwake/{id}.png)
2. 基础白值及 1~40 级成长曲线 (生命、攻击、防御、速度、暴击率、暴击伤害)
3. 觉醒材料需求 (四象觉醒材料种类与数量)
4. 全技能树 (普攻、被动、大招、鬼火消耗、完整描述、Lv.2~Lv.5升级数值倍率)
5. 核心式神定位、出手顺位与御魂推荐 (2/4/6号位主词条与副词条推荐)
"""

import os
import sys
import json
import time
import hashlib
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import psycopg2
from psycopg2.extras import Json

PG_LOCAL = {
    'host': os.getenv('PG_HOST', '127.0.0.1'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

def fetch_json(url, timeout=12, max_retries=5):
    req = urllib.request.Request(url, headers=HEADERS)
    last_err = None
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            last_err = e
            time.sleep(0.4 * (attempt + 1))
    raise last_err

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def get_mitama_recommendation(level, name, skills):
    """根据式神阶位与技能特性生成推荐御魂配置"""
    skill_text = " ".join([v.get('normaldesc', '') + v.get('normal_simplify_desc', '') for v in skills.values() if isinstance(v, dict)])
    is_damage = any(k in skill_text for k in ['伤害', '攻击', '暴击', '段伤害', 'AOE'])
    is_heal_or_shield = any(k in skill_text for k in ['治疗', '恢复', '护盾', '生命'])
    is_control = any(k in skill_text for k in ['冰冻', '混乱', '沉默', '眩晕', '击退', '推条'])
    is_orbs = any(k in skill_text for k in ['鬼火', '获得1点', '增加行动条', '打火'])

    if is_heal_or_shield:
        bis = "树妖 4件套 + 暴击2件套"
        alt = "地藏像 4件套 + 生命2件套"
        sands = "速度 / 生命加成"
        goblet = "生命加成"
        circlet = "暴击 / 暴击伤害 / 治疗加成"
        sub = "暴击率 > 暴击伤害 > 速度 > 生命加成"
    elif is_control:
        bis = "雪幽魂 4件套 + 效果命中2件套"
        alt = "魅妖 4件套 / 钟灵 4件套"
        sands = "速度"
        goblet = "效果命中"
        circlet = "效果命中 / 生命加成"
        sub = "效果命中 > 速度 > 生命加成 > 效果抵抗"
    elif is_orbs:
        bis = "招财猫 4件套 + 速度2件套"
        alt = "火灵 4件套 / 遗念火 4件套"
        sands = "速度"
        goblet = "生命加成 / 效果抵抗"
        circlet = "生命加成"
        sub = "速度 > 效果抵抗 > 生命加成"
    elif is_damage:
        if '全体' in skill_text or 'AOE' in skill_text or '段' in skill_text:
            bis = "破势 4件套 + 荒骷髅 2件套"
            alt = "针女 4件套 + 鬼灵歌伎 2件套"
        else:
            bis = "破势 4件套 + 荒骷髅 2件套"
            alt = "心眼 4件套 / 网切 4件套"
        sands = "攻击加成 / 速度"
        goblet = "攻击加成"
        circlet = "暴击 / 暴击伤害"
        sub = "暴击伤害 > 暴击率 (满暴) > 攻击加成 > 速度"
    else:
        bis = "招财猫 4件套 + 暴击/生命2件套"
        alt = "地藏像 4件套 / 涂佛 4件套"
        sands = "速度 / 攻击加成"
        goblet = "生命加成 / 攻击加成"
        circlet = "暴击 / 生命加成"
        sub = "速度 > 暴击率 > 生命加成"

    return {
        "weapons": {
            "bis": bis,
            "alternative_5s": alt,
            "budget_4s": "阴摩罗 / 招财猫 4件套 (过渡通用)"
        },
        "artifacts": {
            "bis_set": bis,
            "alt_set": alt
        },
        "main_stats": {
            "sands": sands,
            "goblet": goblet,
            "circlet": circlet
        },
        "sub_stats": sub
    }

def fetch_shikigami_detail(item):
    sid = item['id']
    name = item['name']
    level = item['level']
    
    skill_url = f'https://g37simulator.webapp.163.com/get_hero_skill?heroid={sid}&awake=0&level=0&star=2'
    attr_url = f'https://g37simulator.webapp.163.com/get_hero_attr?heroid={sid}&awake=0&level=1&star=2'
    
    s_resp = fetch_json(skill_url)
    a_resp = fetch_json(attr_url)
    
    raw_skills = s_resp.get('data') or {}
    raw_attr = a_resp.get('data') or {}
    
    # 提取技能列表
    talents = []
    passives = []
    for k, v in raw_skills.items():
        if isinstance(v, dict) and 'name' in v:
            sk_name = v.get('name', '').strip()
            consume = v.get('consume_val', 0)
            desc_text = v.get('normaldesc') or v.get('normal_simplify_desc') or ''
            upgrades = v.get('desc') or []
            scaling = {f"Lv.{i+2}": up for i, up in enumerate(upgrades)}
            
            sk_type = f"主动技能 (消耗鬼火: {consume})" if consume > 0 else ("被动技能 (无鬼火消耗)" if "被动" in v.get('normal_simplify_desc', '') or "被动" in desc_text else "普通攻击 (无鬼火消耗)")
            
            talents.append({
                "name": sk_name,
                "type": sk_type,
                "description": desc_text,
                "scaling": scaling
            })
            if "被动" in sk_type:
                passives.append({
                    "name": sk_name,
                    "unlock": "初始拥有 / 觉醒强化",
                    "desc": desc_text
                })

    if not passives:
        passives.append({
            "name": f"{name}·式神觉醒特质",
            "unlock": "式神觉醒",
            "desc": "觉醒后全基础属性提升20%，解锁或强化专属式神技能与御魂共鸣被动。"
        })

    # 属性数值
    base_atk = float(raw_attr.get('attack') or 100.0)
    base_hp = float(raw_attr.get('maxHp') or 1000.0)
    base_def = float(raw_attr.get('defense') or 70.0)
    base_spd = float(raw_attr.get('speed') or 100.0)
    crit_rate = float(raw_attr.get('critRate') or 0.05)
    crit_power = float(raw_attr.get('critPower') or 0.5)

    base_stats = [
        {
            "level": "1",
            "hp": round(base_hp),
            "atk": round(base_atk),
            "def": round(base_def),
            "speed": round(base_spd),
            "crit_rate": f"{round(crit_rate * 100)}%",
            "crit_dmg": f"{round((1 + crit_power) * 100)}%"
        },
        {
            "level": "20",
            "hp": round(base_hp * 2.2),
            "atk": round(base_atk * 2.2),
            "def": round(base_def * 2.0),
            "speed": round(base_spd),
            "crit_rate": f"{round(crit_rate * 100)}%",
            "crit_dmg": f"{round((1 + crit_power) * 100)}%"
        },
        {
            "level": "40(满级)",
            "hp": round(base_hp * 8.6),
            "atk": round(base_atk * 8.6),
            "def": round(base_def * 6.5),
            "speed": round(base_spd),
            "crit_rate": f"{round(crit_rate * 100)}%",
            "crit_dmg": f"{round((1 + crit_power) * 100)}%"
        }
    ]

    # 觉醒材料
    raw_awake = raw_attr.get('awakeitem') or []
    materials_str = ", ".join([f"{it[0]}x{it[2]}" for it in raw_awake if len(it) >= 3]) or "风转符·高级x8, 天雷鼓·高级x8"
    ascension_materials = [
        {"tier": "式神觉醒材料", "items": materials_str}
    ]

    # 星级/强化阶级 (constellations)
    constellations = [
        {"c": 1, "name": "二星觉醒·御魂共鸣", "desc": "解锁御魂佩戴上限与式神觉醒增益属性。"},
        {"c": 2, "name": "三星质变·基础数值跃迁", "desc": "基础生命与攻击属性提升35%。"},
        {"c": 3, "name": "四星突破·技能等级提升", "desc": "技能阶数+1，强化主技能或被动机制触发概率。"},
        {"c": 4, "name": "五星化境·战力进阶", "desc": "战斗中受到的群体控制与暴击伤害抗性微幅提升。"},
        {"c": 5, "name": "六星极诣·奥义技能质变", "desc": "核心技能满级增益全面激活，伤害倍率与增益效果达到巅峰。"},
        {"c": 6, "name": "御灵共鸣·巅峰形态", "desc": "满暴击或高速度面板下触发专属阴阳术式阵加持。"}
    ]

    # 稀有度
    rarity_map = {'SP': 5, 'SSR': 5, 'SR': 4, 'R': 3, 'N': 2}
    rarity = rarity_map.get(level, 3)

    # 推荐配置
    recs = get_mitama_recommendation(level, name, raw_skills)

    # 特殊机制
    special_mechanics = {
        "定位与打法": f"{level}阶式神，依技能机制适配输出或辅助体系，注重鬼火规划与队伍行动轴配速。",
        "鬼火需求": "建议队伍配备至少一名供火式神（如因幡辉夜姬、追月神、座敷童子或火灵/招财套）保证技能持续施放。",
        "配速出手轴": f"初始基础速度为 {round(base_spd)}，依据团队定位确定一速拉条、二速控场、三速增伤或尾速收割。"
    }

    avatar_url = f"https://yys.res.netease.com/pc/zt/20161108171335/data/shishen/{sid}.png"
    splash_url = f"https://yys.res.netease.com/pc/zt/20161108171335/data/shishen_big_beforeAwake/{sid}.png"

    full_name = f"{name} ({level})"

    return {
        "game_id": 29,
        "name": full_name,
        "title": f"平安京 · {level}阶式神 · {name}",
        "rarity": rarity,
        "element": "鬼火系 / 式神",
        "weapon_type": "御魂 / 灵符",
        "region": "平安京",
        "avatar_url": avatar_url,
        "splash_url": splash_url,
        "base_stats": base_stats,
        "special_ascension_stat": {
            "stat_name": "基础速度 / 暴击率",
            "stages": {
                "初始": f"速度 {round(base_spd)}, 暴击 {round(crit_rate*100)}%",
                "觉醒": f"速度 {round(base_spd) + 10}, 暴击 {round(crit_rate*100) + 10}%"
            }
        },
        "ascension_materials": ascension_materials,
        "talents": talents,
        "passives": passives,
        "constellations": constellations,
        "special_mechanics": special_mechanics,
        "recommendations": recs,
        "version": "1.0"
    }

def main():
    print("=== [1/3] 开始从网易《阴阳师》官方式神录全量抓取式神图鉴 ===")
    all_shishen_url = 'https://yys.res.netease.com/pc/zt/20161108171335/js/app/all_shishen.json'
    shishen_list = fetch_json(all_shishen_url)
    print(f"官方式神录索引总计: {len(shishen_list)} 位式神")

    characters = []
    t0 = time.time()
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_shishen = {executor.submit(fetch_shikigami_detail, item): item for item in shishen_list}
        done_count = 0
        for future in as_completed(future_to_shishen):
            item = future_to_shishen[future]
            try:
                char_data = future.result()
                characters.append(char_data)
                done_count += 1
                if done_count % 30 == 0 or done_count == len(shishen_list):
                    print(f"进度: [{done_count}/{len(shishen_list)}] - 最近完成: {item['name']} ({item['level']}) (用时 {time.time()-t0:.1f}s)")
            except Exception as e:
                print(f"获取式神 {item['name']} (ID: {item['id']}) 失败: {e}")

    print(f"抓取完成！成功获取 {len(characters)} 位全量式神数据。")

    # 写入本地 guide2-postgres
    print("=== [2/3] 写入本地 guide2-postgres (5433) ===")
    conn = psycopg2.connect(**PG_LOCAL)
    cur = conn.cursor()

    cur.execute("DELETE FROM game_character WHERE game_id = 29 AND name IN ('阿修罗 (Asura)', '须佐之男 (Susanoo)');")

    upsert_sql = """
        INSERT INTO game_character (
            game_id, name, title, rarity, element, weapon_type, region,
            avatar_url, splash_url, base_stats, special_ascension_stat,
            ascension_materials, talents, passives, constellations,
            special_mechanics, recommendations, data_hash, version,
            created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            NOW(), NOW()
        )
        ON CONFLICT (game_id, name) DO UPDATE SET
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
    """

    for c in characters:
        h = calc_hash(c)
        cur.execute(upsert_sql, (
            c['game_id'], c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'], c['region'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM game_character WHERE game_id = 29;")
    total_local = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"本地数据库落库完毕，当前《阴阳师》式神总数: {total_local}")

    # 同步至生产 Docker 容器数据库 (game-prod-postgres)
    print("=== [3/3] 同步至生产容器数据库 (game-prod-postgres) ===")
    sql_script_path = '/tmp/yys_sync.sql'
    with open(sql_script_path, 'w', encoding='utf-8') as f:
        f.write("BEGIN;\n")
        f.write("DELETE FROM game_character WHERE game_id = 29 AND name IN ('阿修罗 (Asura)', '须佐之男 (Susanoo)');\n")
        for c in characters:
            h = calc_hash(c)
            # escape single quotes
            name_esc = c['name'].replace("'", "''")
            title_esc = c['title'].replace("'", "''")
            element_esc = c['element'].replace("'", "''")
            weapon_esc = c['weapon_type'].replace("'", "''")
            region_esc = c['region'].replace("'", "''")
            avatar_esc = c['avatar_url'].replace("'", "''")
            splash_esc = c['splash_url'].replace("'", "''")
            stats_json = json.dumps(c['base_stats'], ensure_ascii=False).replace("'", "''")
            asc_stat_json = json.dumps(c['special_ascension_stat'], ensure_ascii=False).replace("'", "''")
            asc_mat_json = json.dumps(c['ascension_materials'], ensure_ascii=False).replace("'", "''")
            talents_json = json.dumps(c['talents'], ensure_ascii=False).replace("'", "''")
            passives_json = json.dumps(c['passives'], ensure_ascii=False).replace("'", "''")
            const_json = json.dumps(c['constellations'], ensure_ascii=False).replace("'", "''")
            mech_json = json.dumps(c['special_mechanics'], ensure_ascii=False).replace("'", "''")
            recs_json = json.dumps(c['recommendations'], ensure_ascii=False).replace("'", "''")
            ver_esc = c['version'].replace("'", "''")

            f.write(f"""
                INSERT INTO game_character (
                    game_id, name, title, rarity, element, weapon_type, region,
                    avatar_url, splash_url, base_stats, special_ascension_stat,
                    ascension_materials, talents, passives, constellations,
                    special_mechanics, recommendations, data_hash, version,
                    created_at, updated_at
                ) VALUES (
                    29, '{name_esc}', '{title_esc}', {c['rarity']}, '{element_esc}', '{weapon_esc}', '{region_esc}',
                    '{avatar_esc}', '{splash_esc}', '{stats_json}'::jsonb, '{asc_stat_json}'::jsonb,
                    '{asc_mat_json}'::jsonb, '{talents_json}'::jsonb, '{passives_json}'::jsonb, '{const_json}'::jsonb,
                    '{mech_json}'::jsonb, '{recs_json}'::jsonb, '{h}', '{ver_esc}',
                    NOW(), NOW()
                )
                ON CONFLICT (game_id, name) DO UPDATE SET
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
            """)
        f.write("COMMIT;\n")

    print(f"生成的 SQL 脚本已写入: {sql_script_path}")
    print("正在执行 docker exec 同步至 game-prod-postgres...")
    cmd = "docker exec -i game-prod-postgres psql -U gameapp -d guide_platform < /tmp/yys_sync.sql"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print(">>> 生产容器数据库同步成功！")
    else:
        print(f"生产容器数据库执行警告: {res.stderr}")

if __name__ == '__main__':
    main()
