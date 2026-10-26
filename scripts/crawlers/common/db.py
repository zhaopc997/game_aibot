"""
Database helper module for game guide crawlers.
Provides robust upsert functionality into PostgreSQL for game entities.
"""

import hashlib
import json
import os
import psycopg2
from psycopg2.extras import Json

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5433'))
DB_NAME = os.getenv('DB_NAME', 'guide_platform')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def compute_hash(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def ensure_list_of_dicts(val, default_key='desc') -> list:
    """Ensures value is a list of dicts suitable for Jackson List<Map<String, Object>>."""
    if val is None:
        return []
    if isinstance(val, list):
        res = []
        for item in val:
            if isinstance(item, dict):
                res.append(item)
            elif isinstance(item, str):
                res.append({'name': item, default_key: item, 'slot': item})
            else:
                res.append({default_key: str(item)})
        return res
    if isinstance(val, dict):
        if not val:
            return []
        return [val]
    if isinstance(val, str) and val.strip():
        return [{'name': val, default_key: val}]
    return []


def ensure_dict(val) -> dict:
    """Ensures value is a dict suitable for Jackson Map<String, Object>."""
    if val is None:
        return {}
    if isinstance(val, dict):
        return val
    if isinstance(val, list):
        return {'items': val}
    if isinstance(val, str) and val.strip():
        return {'value': val}
    return {}


def upsert_characters(game_id: int, characters: list):
    """
    Upserts a list of characters for a given game_id.
    Each character is a dict with keys:
    - name, title, rarity, element, weapon_type, region, arkhe,
      avatar_url, splash_url, base_stats, talents, passives,
      constellations, special_mechanics, recommendations, version
    """
    if not characters:
        return 0

    sql = """
    INSERT INTO game_character (
        game_id, name, title, rarity, element, weapon_type, region, arkhe,
        avatar_url, splash_url, base_stats, talents, passives,
        constellations, special_mechanics, recommendations, data_hash, version,
        created_at, updated_at
    ) VALUES (
        %(game_id)s, %(name)s, %(title)s, %(rarity)s, %(element)s, %(weapon_type)s, %(region)s, %(arkhe)s,
        %(avatar_url)s, %(splash_url)s, %(base_stats)s, %(talents)s, %(passives)s,
        %(constellations)s, %(special_mechanics)s, %(recommendations)s, %(data_hash)s, %(version)s,
        NOW(), NOW()
    )
    ON CONFLICT (game_id, name) DO UPDATE SET
        title = EXCLUDED.title,
        rarity = EXCLUDED.rarity,
        element = EXCLUDED.element,
        weapon_type = EXCLUDED.weapon_type,
        region = EXCLUDED.region,
        arkhe = EXCLUDED.arkhe,
        avatar_url = COALESCE(EXCLUDED.avatar_url, game_character.avatar_url),
        splash_url = COALESCE(EXCLUDED.splash_url, game_character.splash_url),
        base_stats = EXCLUDED.base_stats,
        talents = EXCLUDED.talents,
        passives = EXCLUDED.passives,
        constellations = EXCLUDED.constellations,
        special_mechanics = EXCLUDED.special_mechanics,
        recommendations = EXCLUDED.recommendations,
        data_hash = EXCLUDED.data_hash,
        version = EXCLUDED.version,
        updated_at = NOW();
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for c in characters:
                row = {
                    'game_id': game_id,
                    'name': c.get('name', '未命名'),
                    'title': c.get('title', ''),
                    'rarity': c.get('rarity', 1),
                    'element': c.get('element', ''),
                    'weapon_type': c.get('weapon_type', ''),
                    'region': c.get('region', ''),
                    'arkhe': c.get('arkhe', ''),
                    'avatar_url': c.get('avatar_url', ''),
                    'splash_url': c.get('splash_url', ''),
                    'base_stats': Json(ensure_list_of_dicts(c.get('base_stats'), 'stat')),
                    'talents': Json(ensure_list_of_dicts(c.get('talents') or c.get('skills'), 'talent')),
                    'passives': Json(ensure_list_of_dicts(c.get('passives'), 'passive')),
                    'constellations': Json(ensure_list_of_dicts(c.get('constellations'), 'constellation')),
                    'ascension_materials': Json(ensure_list_of_dicts(c.get('ascension_materials'), 'material')),
                    'special_ascension_stat': Json(ensure_dict(c.get('special_ascension_stat'))),
                    'special_mechanics': Json(ensure_dict(c.get('special_mechanics'))),
                    'recommendations': Json(ensure_dict(c.get('recommendations'))),
                    'data_hash': compute_hash(c),
                    'version': c.get('version', 'v1.0')
                }
                cur.execute(sql, row)
        conn.commit()
        return len(characters)
    finally:
        conn.close()


def upsert_weapons(game_id: int, weapons: list):
    """
    Upserts a list of weapons/items for a given game_id.
    """
    if not weapons:
        return 0

    sql = """
    INSERT INTO game_weapon (
        game_id, name, type, rarity, icon_url, base_atk_curve,
        sub_stat, refinements, ascension_materials, data_hash, version,
        created_at, updated_at
    ) VALUES (
        %(game_id)s, %(name)s, %(type)s, %(rarity)s, %(icon_url)s, %(base_atk_curve)s,
        %(sub_stat)s, %(refinements)s, %(ascension_materials)s, %(data_hash)s, %(version)s,
        NOW(), NOW()
    )
    ON CONFLICT (game_id, name) DO UPDATE SET
        type = EXCLUDED.type,
        rarity = EXCLUDED.rarity,
        icon_url = COALESCE(EXCLUDED.icon_url, game_weapon.icon_url),
        base_atk_curve = EXCLUDED.base_atk_curve,
        sub_stat = EXCLUDED.sub_stat,
        refinements = EXCLUDED.refinements,
        ascension_materials = EXCLUDED.ascension_materials,
        data_hash = EXCLUDED.data_hash,
        version = EXCLUDED.version,
        updated_at = NOW();
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for w in weapons:
                base_atk = w.get('base_atk_curve')
                if not base_atk and w.get('base_atk'):
                    base_atk = [{'level': '1', 'atk': 0, 'desc': str(w.get('base_atk'))}]

                refinements = w.get('refinements')
                if not refinements and w.get('refine'):
                    refinements = [{'rank': '精炼/效果', 'desc': str(w.get('refine'))}]

                sub_stat = w.get('sub_stat')
                if isinstance(sub_stat, str):
                    sub_stat = {'desc': sub_stat}

                row = {
                    'game_id': game_id,
                    'name': w.get('name', '未命名'),
                    'type': w.get('type', ''),
                    'rarity': w.get('rarity', 1),
                    'icon_url': w.get('icon_url', ''),
                    'base_atk_curve': Json(ensure_list_of_dicts(base_atk, 'atk')),
                    'sub_stat': Json(ensure_dict(sub_stat)),
                    'refinements': Json(ensure_list_of_dicts(refinements, 'desc')),
                    'ascension_materials': Json(ensure_list_of_dicts(w.get('ascension_materials'), 'material')),
                    'data_hash': compute_hash(w),
                    'version': w.get('version', 'v1.0')
                }
                cur.execute(sql, row)
        conn.commit()
        return len(weapons)
    finally:
        conn.close()


def upsert_artifacts(game_id: int, artifacts: list):
    """
    Upserts artifact/soul/synergy sets for a given game_id.
    """
    if not artifacts:
        return 0

    sql = """
    INSERT INTO game_artifact_set (
        game_id, name, rarity_min, rarity_max, icon_url,
        two_piece_bonus, four_piece_bonus, pieces, rules_reference,
        data_hash, version, created_at, updated_at
    ) VALUES (
        %(game_id)s, %(name)s, %(rarity_min)s, %(rarity_max)s, %(icon_url)s,
        %(two_piece_bonus)s, %(four_piece_bonus)s, %(pieces)s, %(rules_reference)s,
        %(data_hash)s, %(version)s, NOW(), NOW()
    )
    ON CONFLICT (game_id, name) DO UPDATE SET
        rarity_min = EXCLUDED.rarity_min,
        rarity_max = EXCLUDED.rarity_max,
        icon_url = COALESCE(EXCLUDED.icon_url, game_artifact_set.icon_url),
        two_piece_bonus = EXCLUDED.two_piece_bonus,
        four_piece_bonus = EXCLUDED.four_piece_bonus,
        pieces = EXCLUDED.pieces,
        rules_reference = EXCLUDED.rules_reference,
        data_hash = EXCLUDED.data_hash,
        version = EXCLUDED.version,
        updated_at = NOW();
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for a in artifacts:
                row = {
                    'game_id': game_id,
                    'name': a.get('name', '未命名'),
                    'rarity_min': a.get('rarity_min', 1),
                    'rarity_max': a.get('rarity_max', 5),
                    'icon_url': a.get('icon_url', ''),
                    'two_piece_bonus': a.get('two_piece_bonus', ''),
                    'four_piece_bonus': a.get('four_piece_bonus', ''),
                    'pieces': Json(ensure_list_of_dicts(a.get('pieces'), 'slot')),
                    'rules_reference': Json(ensure_dict(a.get('rules_reference'))),
                    'data_hash': compute_hash(a),
                    'version': a.get('version', 'v1.0')
                }
                cur.execute(sql, row)
        conn.commit()
        return len(artifacts)
    finally:
        conn.close()


def upsert_mechanics(game_id: int, mechanics: list):
    """
    Upserts mechanic rules for a given game_id.
    """
    if not mechanics:
        return 0

    sql = """
    INSERT INTO game_mechanic_rule (
        game_id, category, title, formula, parameters, created_at, updated_at
    ) VALUES (
        %(game_id)s, %(category)s, %(title)s, %(formula)s, %(parameters)s, NOW(), NOW()
    )
    ON CONFLICT (game_id, category, title) DO UPDATE SET
        formula = EXCLUDED.formula,
        parameters = EXCLUDED.parameters,
        updated_at = NOW();
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for m in mechanics:
                row = {
                    'game_id': game_id,
                    'category': m.get('category', '机制'),
                    'title': m.get('title', '未命名规则'),
                    'formula': m.get('formula', ''),
                    'parameters': Json(m.get('parameters', {}))
                }
                cur.execute(sql, row)
        conn.commit()
        return len(mechanics)
    finally:
        conn.close()
