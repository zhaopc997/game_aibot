"""
Counter-Strike 2 (CS2) Full Weapon Arsenal & MR12 Economy Crawler Module
Ingests complete firearm database, grenade physics, and economy rules into Game 7 (CS2).
"""

from ..common.db import (
    upsert_weapons,
    upsert_mechanics
)

CS2_WEAPONS = [
    # 步枪类 (Rifles)
    {
        'name': 'AK-47 (自动突击步枪)',
        'type': 'T阵营主战步枪',
        'rarity': 5,
        'cost': '$2700',
        'damage': 36,
        'fire_rate': '600 RPM',
        'penetration': '200% (穿甲极强)',
        'mag': '30/90',
        'desc': '进攻方核心信仰神器，拥有极高单发爆头威力，命中任何带头盔敌人一枪秒杀！'
    },
    {
        'name': 'M4A1-S (消音突击步枪)',
        'type': 'CT阵营消音步枪',
        'rarity': 4,
        'cost': '$2900',
        'damage': 38,
        'fire_rate': '600 RPM',
        'penetration': '140%',
        'mag': '20/80',
        'desc': '消音枪管不显露雷达射击标记，且完全无弹道曳光弹轨迹，后坐力极度柔和易控。'
    },
    {
        'name': 'M4A4 (防卫突击步枪)',
        'type': 'CT阵营突击步枪',
        'rarity': 4,
        'cost': '$3000',
        'damage': 33,
        'fire_rate': '666 RPM',
        'penetration': '140%',
        'mag': '30/90',
        'desc': '拥有 30 发大弹夹与更快射速，适合守点多重交火压制，但破盔需两枪。'
    },
    {
        'name': 'AWP (重型狙击步枪)',
        'type': '重型反器材狙击枪',
        'rarity': 5,
        'cost': '$4750',
        'damage': 115,
        'fire_rate': '41 RPM',
        'penetration': '250%',
        'mag': '5/30',
        'desc': '绿色毁灭死神！击中腰部以上一击必杀！开镜架点拥有绝对一发制敌权威。'
    },
    {
        'name': 'SSG 08 (轻型鸟狙)',
        'type': '轻型狙击枪',
        'rarity': 3,
        'cost': '$1700',
        'damage': 88,
        'fire_rate': '48 RPM',
        'penetration': '170%',
        'mag': '10/90',
        'desc': '移速极快且滞空起跳开镜射击完全无扩散准星惩罚，经济局空中鸟狙探点神器。'
    },
    {
        'name': 'Galil AR (加利尔突击步枪)',
        'type': 'T阵营经济步枪',
        'rarity': 3,
        'cost': '$1800',
        'damage': 30,
        'fire_rate': '666 RPM',
        'penetration': '155%',
        'mag': '35/90',
        'desc': '进攻方低价位大容量长枪，35发容弹量在半起经济局表现突出。'
    },
    {
        'name': 'FAMAS (法玛斯步枪)',
        'type': 'CT阵营经济步枪',
        'rarity': 3,
        'cost': '$2050',
        'damage': 30,
        'fire_rate': '666 RPM',
        'penetration': '140%',
        'mag': '25/90',
        'desc': '防守方最便宜的步枪选择，支持三连发点射模式与全自动切换。'
    },

    # 手枪类 (Pistols)
    {
        'name': 'Desert Eagle (沙漠之鹰)',
        'type': '重型手枪',
        'rarity': 4,
        'cost': '$700',
        'damage': 53,
        'fire_rate': '267 RPM',
        'penetration': '186%',
        'mag': '7/35',
        'desc': '手枪局翻盘神器，精准一发爆头摧毁戴头盔敌人（一发入魂）。'
    },
    {
        'name': 'USP-S (消音手枪)',
        'type': 'CT阵营初始手枪',
        'rarity': 2,
        'cost': '免费/可买$200',
        'damage': 35,
        'fire_rate': '352 RPM',
        'penetration': '100%',
        'mag': '12/24',
        'desc': '首发精度极高，远距离轻点爆头两发致命，手枪局CT利器。'
    },
    {
        'name': 'Glock-18 (格洛克手枪)',
        'type': 'T阵营初始手枪',
        'rarity': 2,
        'cost': '免费/可买$200',
        'damage': 30,
        'fire_rate': '400 RPM',
        'penetration': '94%',
        'mag': '20/120',
        'desc': '移动射击散布小，20发大弹夹支持近身跳跃奔跑射击，支持三连发模式。'
    },

    # 冲锋枪类 (SMGs)
    {
        'name': 'MP9 (微型冲锋枪)',
        'type': 'CT冲锋枪',
        'rarity': 3,
        'cost': '$1250',
        'damage': 26,
        'fire_rate': '857 RPM',
        'penetration': '100%',
        'mag': '30/120',
        'desc': '移速极快且射速恐怖，CT方防Rush与反抓强起核心武器。'
    },
    {
        'name': 'MAC-10 (吹风机)',
        'type': 'T冲锋枪',
        'rarity': 3,
        'cost': '$1050',
        'damage': 29,
        'fire_rate': '800 RPM',
        'penetration': '115%',
        'mag': '30/100',
        'desc': '击杀获得双倍金币奖励（$600），奔跑射击弹道密集，经济局刷钱神器。'
    },

    # 投掷物类 (Utility Grenades)
    {
        'name': '烟雾弹 (CS2 容积烟雾)',
        'type': '战术投掷物',
        'rarity': 4,
        'cost': '$300',
        'damage': 0,
        'fire_rate': '一次性',
        'penetration': '阻断视线',
        'mag': '1枚',
        'desc': 'CS2 核心革命升级！完全动态物理体积交互烟雾，可被高爆手雷炸散开洞，可被穿透子弹暂时开出视野孔！'
    },
    {
        'name': '燃烧弹 / 燃烧瓶 (Molotov / Incendiary)',
        'type': '战术投掷物',
        'rarity': 4,
        'cost': '$400 / $500',
        'damage': 150,
        'fire_rate': '区域持续燃烧',
        'penetration': '直接破甲灼伤',
        'mag': '1枚',
        'desc': '封锁狭窄通道或清空死角必用道具，造成高额持续灼烧伤害并延缓进攻节奏。'
    }
]

CS2_MECHANICS = [
    {
        'category': '经济系统',
        'title': 'MR12 赛制经济连败补偿公式',
        'formula': '胜利+$3250(灭队)/+$3500(拆包/引爆)；连败阶梯：1败$1400，2败$1900，3败$2400，4败$2900，5败上限$3400',
        'parameters': {
            '安包奖励': '进攻方若安包但输掉回合，全队额外+$800补偿',
            '手枪局胜负': '赢下首局直接获得 $3250，败方得 $1400（保枪强起或纯ECO）',
            '击杀奖励': '散弹枪击杀 $900，冲锋枪击杀 $600，步枪击杀 $300，AWP击杀 $100'
        }
    },
    {
        'category': '网络与物理',
        'title': '子变步长 (Sub-Tick) 精准判定机制',
        'formula': '服务器在两帧之间记录玩家敲击键盘开火的精确时间戳，做到所见即所射',
        'parameters': {
            '急停判定': '完全静止前由于惯性滑步会有散布惩罚，松开A按D瞬间反向阻尼急停为 0 速度'
        }
    }
]


def crawl_and_sync_cs2(game_id=7):
    print(f'[CS2] Preparing {len(CS2_WEAPONS)} weapons and mechanics for Game {game_id} ...')

    weapons = []
    for w in CS2_WEAPONS:
        weapons.append({
            'name': w['name'],
            'type': w['type'],
            'rarity': w['rarity'],
            'icon_url': f'/games/weapons/{w["name"].split()[0]}.png',
            'base_atk_curve': {
                'cost': w['cost'],
                'damage': w['damage'],
                'fire_rate': w['fire_rate'],
                'penetration': w['penetration'],
                'magazine': w['mag']
            },
            'sub_stat': {'kill_award': '$300-$900'},
            'refinements': {'description': w['desc']},
            'ascension_materials': {'type': w['type']},
            'version': 'CS2 2024'
        })

    w_count = upsert_weapons(game_id, weapons)
    m_count = upsert_mechanics(game_id, CS2_MECHANICS)
    print(f'[CS2] Ingested into Game {game_id}: {w_count} weapons, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_cs2(7)
