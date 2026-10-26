"""
Valorant Crawler Module
Fetches all agents, weapons, abilities and gun stats from official valorant-api.com (in zh-CN).
Ingests into Game 17 (Valorant).
"""

import requests
from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_mechanics
)

AGENTS_URL = 'https://valorant-api.com/v1/agents?isPlayableCharacter=true&language=zh-CN'
WEAPONS_URL = 'https://valorant-api.com/v1/weapons?language=zh-CN'


def crawl_and_sync_valorant(game_id=17):
    print(f'[Valorant] Fetching agents from {AGENTS_URL} ...')
    resp_agents = requests.get(AGENTS_URL, timeout=15).json()
    raw_agents = resp_agents.get('data', [])

    characters = []
    for a in raw_agents:
        name = a.get('displayName', '').strip()
        if not name:
            continue

        role_info = a.get('role') or {}
        role_name = role_info.get('displayName', '特工')
        desc = a.get('description', '')
        avatar_url = a.get('displayIcon', '')
        splash_url = a.get('fullPortrait', avatar_url)

        # Parse abilities
        talents = []
        passives = []
        for ab in a.get('abilities', []):
            ab_slot = ab.get('slot', '')
            ab_name = ab.get('displayName', '')
            ab_desc = ab.get('description', '')
            ab_icon = ab.get('displayIcon', '')

            item = {
                'name': ab_name,
                'slot': ab_slot,
                'description': ab_desc,
                'icon_url': ab_icon
            }

            if ab_slot == 'Passive':
                passives.append(item)
            else:
                item['type'] = 'ELEMENTAL_BURST' if ab_slot == 'Ultimate' else 'ELEMENTAL_SKILL'
                item['scaling'] = '终极技能' if ab_slot == 'Ultimate' else f'战术技能 ({ab_slot})'
                talents.append(item)

        base_stats = [
            {
                'level': '基础属性',
                'hp': 100,
                'shield': '可购买 轻甲(+25) / 重甲(+50)',
                'speed': '标准移动速度 5.4m/s',
                'role': role_name
            }
        ]

        characters.append({
            'name': name,
            'title': f'{role_name} · {a.get("developerName", name)}',
            'rarity': 5,
            'element': role_name,
            'weapon_type': '全枪械适配',
            'region': '无畏契约协议基地',
            'arkhe': '源工辐射源',
            'avatar_url': avatar_url,
            'splash_url': splash_url,
            'base_stats': base_stats,
            'talents': talents,
            'passives': passives,
            'constellations': [],
            'special_mechanics': {'role': role_name, 'character_desc': desc},
            'recommendations': {'recommended_weapons': ['狂徒 Vandal', '幻影 Phantom', '冥驹 Operator']},
            'version': 'EP9'
        })

    print(f'[Valorant] Fetching weapons from {WEAPONS_URL} ...')
    resp_weapons = requests.get(WEAPONS_URL, timeout=15).json()
    raw_weapons = resp_weapons.get('data', [])

    weapons = []
    for w in raw_weapons:
        name = w.get('displayName', '').strip()
        if not name:
            continue

        shop_data = w.get('shopData') or {}
        category_text = shop_data.get('categoryText', '主武器')
        cost = shop_data.get('cost', 0)
        weapon_stats = w.get('weaponStats') or {}
        icon_url = w.get('displayIcon', '')

        # Damage ranges
        damage_ranges = weapon_stats.get('damageRanges', [])
        clean_ranges = []
        for dr in damage_ranges:
            clean_ranges.append({
                'range': f"{dr.get('rangeStartMeters')}-{dr.get('rangeEndMeters')}米",
                'head': dr.get('headDamage'),
                'body': dr.get('bodyDamage'),
                'leg': dr.get('legDamage')
            })

        weapons.append({
            'name': name,
            'type': category_text,
            'rarity': 4 if cost >= 2900 else 3,
            'icon_url': icon_url,
            'base_atk_curve': {
                'cost': f'{cost} 誉币',
                'magazine': weapon_stats.get('magazineSize', 30),
                'fire_rate': weapon_stats.get('fireRate', 0),
                'reload_time': f"{weapon_stats.get('reloadTimeSeconds', 0)}秒",
                'wall_penetration': weapon_stats.get('wallPenetration', 'Medium')
            },
            'sub_stat': {'damage_profiles': clean_ranges},
            'refinements': {'first_bullet_accuracy': weapon_stats.get('firstBulletAccuracy', 0)},
            'ascension_materials': {'category': category_text, 'price': cost},
            'version': 'EP9'
        })

    # Mechanics
    mechanics = [
        {
            'category': '经济系统',
            'title': '回合胜负与连败经济机制',
            'formula': '胜利+3000，首败+1900，二连败+2400，三连败及以上封顶+2900；下包+300',
            'parameters': {
                '胜利收益': '全队每人获得 3000 誉币',
                '失败底线': '1900 / 2400 / 2900 阶梯奖励',
                '存活失败惩罚': '进攻方未下包且存活保枪仅得 1000 誉币'
            }
        },
        {
            'category': '枪法机制',
            'title': '急停与首发散布射击准度公式',
            'formula': '移动中射击散布极大，松开移动键或反向急停至移动速度<30%时恢复首发100%精准度',
            'parameters': {
                '急停要求': '完全静止状态下扩散角最小',
                '跑打惩罚': '移动时扩散角度增加 5.0 度以上',
                '下蹲增益': '下蹲状态轻微降低后坐力与恢复时间'
            }
        }
    ]

    print(f'[Valorant] Ingesting into Game ID {game_id} ...')
    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    m_count = upsert_mechanics(game_id, mechanics)
    print(f'[Valorant] Done Game {game_id}: {c_count} agents, {w_count} weapons, {m_count} mechanics')


if __name__ == '__main__':
    crawl_and_sync_valorant(17)
