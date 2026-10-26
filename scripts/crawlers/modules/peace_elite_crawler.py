"""
Peace Elite (和平精英) Full Arsenal, Superbody Roles & Combat Rules Crawler Module
Ingests complete firearm database, attachments, armor mitigation formulas,
and Superbody (超体对抗) class characters into Game 27 (和平精英).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_mechanics
)

# 枪械库
FIREARMS = [
    # 突击步枪 (Assault Rifles)
    {
        'name': 'M416 (突击步枪)',
        'type': '突击步枪',
        'rarity': 4,
        'caliber': '5.56mm',
        'damage': 41,
        'fire_rate': '0.086秒/发',
        'mag': '30/40发',
        'velocity': '880m/s',
        'slots': ['枪口', '握把', '弹夹', '瞄具', '战术枪托'],
        'desc': '最为全面稳定的主流步枪，满配后后坐力极低，中近距离压枪扫射首选。'
    },
    {
        'name': 'AKM (突击步枪)',
        'type': '突击步枪',
        'rarity': 4,
        'caliber': '7.62mm',
        'damage': 48,
        'fire_rate': '0.100秒/发',
        'mag': '30/40发',
        'velocity': '715m/s',
        'slots': ['枪口', '弹夹', '瞄具'],
        'desc': '高单发威力步枪，近战爆发凶猛，但垂直后坐力巨大，考验玩家压枪基本功。'
    },
    {
        'name': 'Beryl M762 (猛男枪)',
        'type': '突击步枪',
        'rarity': 4,
        'caliber': '7.62mm',
        'damage': 46,
        'fire_rate': '0.086秒/发',
        'mag': '30/40发',
        'velocity': '740m/s',
        'slots': ['枪口', '握把', '弹夹', '瞄具'],
        'desc': '兼具 7.62mm 高伤害与高射速的近战杀器，近战 DPS 极高，被玩家誉为猛男枪。'
    },
    {
        'name': 'Groza (空投狗杂)',
        'type': '空投突击步枪',
        'rarity': 5,
        'caliber': '7.62mm',
        'damage': 48,
        'fire_rate': '0.080秒/发',
        'mag': '30/40发',
        'velocity': '715m/s',
        'slots': ['枪口(仅消音)', '弹夹', '瞄具'],
        'desc': '空投专属神枪，超高射速与7.62子弹致命伤害，近战对枪之王。'
    },
    {
        'name': 'AUG (空投步枪)',
        'type': '空投突击步枪',
        'rarity': 5,
        'caliber': '5.56mm',
        'damage': 41,
        'fire_rate': '0.085秒/发',
        'mag': '30/40发',
        'velocity': '940m/s',
        'slots': ['枪口', '握把', '弹夹', '瞄具'],
        'desc': '弹道极其平稳的空投无托步枪，水平散布极小，远距离扫射极具统治力。'
    },
    {
        'name': 'SCAR-L (突击步枪)',
        'type': '突击步枪',
        'rarity': 3,
        'caliber': '5.56mm',
        'damage': 41,
        'fire_rate': '0.096秒/发',
        'mag': '30/40发',
        'velocity': '870m/s',
        'slots': ['枪口', '握把', '弹夹', '瞄具'],
        'desc': '未满配状态下稳定性优于M416，射速略慢但容错率高。'
    },

    # 栓动狙击枪 (Bolt-Action Sniper Rifles)
    {
        'name': 'AWM (空投重狙)',
        'type': '栓动狙击枪',
        'rarity': 5,
        'caliber': '.300 马格南',
        'damage': 105,
        'fire_rate': '1.85秒/发',
        'mag': '5/7发',
        'velocity': '910m/s',
        'slots': ['枪口', '弹夹', '瞄具', '托腮板'],
        'desc': '全图最强单发威力狙击枪，无视三级头盔，命中头部一击必杀！'
    },
    {
        'name': 'Kar98k (毛瑟狙击步枪)',
        'type': '栓动狙击枪',
        'rarity': 4,
        'caliber': '7.62mm',
        'damage': 79,
        'fire_rate': '1.90秒/发',
        'mag': '5发 (内置)',
        'velocity': '760m/s',
        'slots': ['枪口', '瞄具', '托腮板/子弹袋'],
        'desc': '经典栓动狙击枪，全图刷新，可一枪击破二级头盔。'
    },
    {
        'name': 'M24 (狙击步枪)',
        'type': '栓动狙击枪',
        'rarity': 4,
        'caliber': '7.62mm',
        'damage': 82,
        'fire_rate': '1.80秒/发',
        'mag': '5/7发',
        'velocity': '790m/s',
        'slots': ['枪口', '弹夹', '瞄具', '托腮板'],
        'desc': '威力强于98k的现代狙击枪，换弹迅速且支持扩容弹夹。'
    },

    # 射手步枪 (DMR)
    {
        'name': 'Mk14 (空投妹控)',
        'type': '连发狙击枪',
        'rarity': 5,
        'caliber': '7.62mm',
        'damage': 61,
        'fire_rate': '0.090秒/发',
        'mag': '10/20发',
        'velocity': '853m/s',
        'slots': ['枪口', '弹夹', '瞄具', '托腮板'],
        'desc': '拥有全自动模式的空投连狙，趴下展开两脚架后后坐力骤降，近战爆发与远距连点兼备。'
    },
    {
        'name': 'SKS (连发狙击步枪)',
        'type': '连发狙击枪',
        'rarity': 3,
        'caliber': '7.62mm',
        'damage': 53,
        'fire_rate': '0.100秒/发',
        'mag': '10/20发',
        'velocity': '800m/s',
        'slots': ['枪口', '握把', '弹夹', '瞄具', '托腮板'],
        'desc': '对配件依赖度高，满配轻型握把后点射手感极为舒适。'
    },
    {
        'name': 'Mini14 (轻型狙击枪)',
        'type': '连发狙击枪',
        'rarity': 3,
        'caliber': '5.56mm',
        'damage': 46,
        'fire_rate': '0.100秒/发',
        'mag': '20/30发',
        'velocity': '990m/s',
        'slots': ['枪口', '弹夹', '瞄具'],
        'desc': '全枪械最高的子弹初速（990m/s），弹道极直下坠微弱，移动靶极易命中。'
    },

    # 冲锋枪 (SMG)
    {
        'name': 'UMP45 (冲锋枪)',
        'type': '冲锋枪',
        'rarity': 3,
        'caliber': '.45口径',
        'damage': 41,
        'fire_rate': '0.092秒/发',
        'mag': '25/35发',
        'velocity': '360m/s',
        'slots': ['枪口', '握把', '弹夹', '瞄具'],
        'desc': '近战肢体伤害系数高，后坐力柔和易控，贴脸腰射神器。'
    },
    {
        'name': 'Vector (短剑)',
        'type': '冲锋枪',
        'rarity': 3,
        'caliber': '9mm',
        'damage': 31,
        'fire_rate': '0.055秒/发',
        'mag': '19/33发',
        'velocity': '350m/s',
        'slots': ['枪口', '握把', '弹夹', '瞄具', '战术枪托'],
        'desc': '极限极速射速（0.055秒/发），近身瞬秒敌人，但极度依赖快速扩容弹夹。'
    },

    # 霰弹枪与机枪
    {
        'name': 'DBS (双管霰弹枪)',
        'type': '霰弹枪',
        'rarity': 4,
        'caliber': '12号口径',
        'damage': 26 * 9,
        'fire_rate': '泵动双发连喷',
        'mag': '14发',
        'velocity': '360m/s',
        'slots': ['瞄具'],
        'desc': '攻楼与近距离腰射统治级大杀器，两发泵动连喷可瞬间击倒任何防具目标。'
    },
    {
        'name': 'M249 (大菠萝机枪)',
        'type': '轻机枪',
        'rarity': 4,
        'caliber': '5.56mm',
        'damage': 40,
        'fire_rate': '0.075秒/发',
        'mag': '75/150发',
        'velocity': '915m/s',
        'slots': ['弹夹', '瞄具', '战术枪托'],
        'desc': '载具杀手，扩容后容弹量高达150发，火力压制与扫车之王。'
    }
]

# 超体对抗核心职业角色
SUPERBODY_CLASSES = [
    {
        'name': '指挥官 (Commander)',
        'title': '超体核心 · 战术指挥官',
        'role': '战术团队增益',
        'passive': '全队能量消耗降低，自身获得护甲加成',
        'skills': [
            {'name': '战术护盾', 'type': 'ELEMENTAL_SKILL', 'scaling': 'CD: 25秒', 'description': '部署单向防弹能量屏障阻挡子弹射击'},
            {'name': '空投集结', 'type': 'ELEMENTAL_BURST', 'scaling': '大招消耗: 100能量', 'description': '召唤空投信标，投放高级战术补给与全队强力攻击力增幅光环'}
        ]
    },
    {
        'name': '火箭骑士 (Rocket Knight)',
        'title': '空中突击 · 火箭骑士',
        'role': '垂直机动与高空打击',
        'passive': '下落过程可减速滑翔并获得高空腰射稳定加成',
        'skills': [
            {'name': '火箭升空', 'type': 'ELEMENTAL_SKILL', 'scaling': 'CD: 18秒', 'description': '启动背部喷气装置垂直跃起冲向数十米高空'},
            {'name': '空地流星轰炸', 'type': 'ELEMENTAL_BURST', 'scaling': '大招消耗: 100能量', 'description': '锁定地面扇形区域发射微型火箭弹群，造成毁灭性AOE爆炸伤害'}
        ]
    },
    {
        'name': '次元极客 (Dimension Geek)',
        'title': '空间跳跃 · 次元极客',
        'role': '战术转移与物资调配',
        'passive': '背包容量增加 100 点，拾取物资速度翻倍',
        'skills': [
            {'name': '相位信标', 'type': 'ELEMENTAL_SKILL', 'scaling': 'CD: 20秒', 'description': '向前方投掷空间定位锚点，再次激活瞬间瞬移传送至信标位置'},
            {'name': '次元传送门', 'type': 'ELEMENTAL_BURST', 'scaling': '大招消耗: 100能量', 'description': '架设全队双向穿透的时空传送门，完成超远距离安全战术转点'}
        ]
    },
    {
        'name': '闪电尖兵 (Flash Soldier)',
        'title': '极致突刺 · 闪电尖兵',
        'role': '近战冲锋突破手',
        'passive': '冲刺速度提高 15%，持冲锋枪/霰弹枪移动无减速惩罚',
        'skills': [
            {'name': '超光速冲刺', 'type': 'ELEMENTAL_SKILL', 'scaling': 'CD: 12秒', 'description': '向前瞬爆突进 15 米，期间处于半隐身残影免伤状态'},
            {'name': '雷霆领域', 'type': 'ELEMENTAL_BURST', 'scaling': '大招消耗: 100能量', 'description': '释放电磁脉冲使半径 20 米内所有敌方武器瘫痪封禁开火 3 秒'}
        ]
    }
]


def crawl_and_sync_peace_elite(game_id=27):
    print(f'[Peace Elite] Preparing {len(FIREARMS)} firearms & {len(SUPERBODY_CLASSES)} roles ...')

    weapons = []
    for f in FIREARMS:
        weapons.append({
            'name': f['name'],
            'type': f['type'],
            'rarity': f['rarity'],
            'icon_url': f'/games/weapons/{f["name"].split()[0]}.png',
            'base_atk_curve': {
                'damage': f['damage'],
                'fire_rate': f['fire_rate'],
                'magazine': f['mag'],
                'bullet_velocity': f['velocity']
            },
            'sub_stat': {'caliber': f['caliber'], 'supported_slots': f['slots']},
            'refinements': {'performance': f['desc']},
            'ascension_materials': {'category': f['type']},
            'version': 'v1.27'
        })

    characters = []
    for c in SUPERBODY_CLASSES:
        characters.append({
            'name': c['name'],
            'title': c['title'],
            'rarity': 5,
            'element': c['role'],
            'weapon_type': '超体武器',
            'region': '和平精英超体空间',
            'arkhe': '超体战术晶体',
            'avatar_url': '',
            'splash_url': '',
            'base_stats': [{'hp': 100, 'armor': 100, 'speed': '高机动'}],
            'talents': c['skills'],
            'passives': [{'name': '专属被动', 'description': c['passive']}],
            'constellations': [],
            'special_mechanics': {'tactical_role': c['role']},
            'recommendations': {'recommended_guns': ['M416', 'Beryl M762', 'DBS']},
            'version': 'v1.27'
        })

    mechanics = [
        {
            'category': '防具减伤',
            'title': '头盔与护甲伤害吸收公式',
            'formula': '实际受创伤害 = 裸身伤害 × (1 - 防具减伤比)',
            'parameters': {
                '一级头/甲': '减伤 30%，耐久 80/200',
                '二级头/甲': '减伤 40%，耐久 150/220',
                '三级头/甲': '减伤 55%，耐久 230/250（三级头免除栓狙爆头秒杀）',
                '部位伤害系数': '头部 2.5倍，身体 1.0倍，四肢 0.5倍'
            }
        },
        {
            'category': '毒圈规则',
            'title': '信号值衰减与安全区收缩时间表',
            'formula': '信号值降为0直接淘汰，受圈外阶段扣血倍率线性增加',
            'parameters': {
                '阶段1~3': '较慢衰减，使用能量饮料/急救包即可稳定抗毒进圈',
                '阶段4~6': '每秒扣减信号值高额递增，必须依赖止痛药与信号电池',
                '决战圈': '每秒衰减超高，暴露圈外5秒内即告淘汰'
            }
        }
    ]

    w_count = upsert_weapons(game_id, weapons)
    c_count = upsert_characters(game_id, characters)
    m_count = upsert_mechanics(game_id, mechanics)
    print(f'[Peace Elite] Ingested into Game {game_id}: {c_count} roles, {w_count} firearms, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_peace_elite(27)
