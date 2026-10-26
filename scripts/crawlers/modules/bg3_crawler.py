"""
Baldur's Gate 3 (博德之门3) Companions, Legendary Weapons, Build Gear & D&D 5e Rules Crawler
Ingests Origin companions, legendary Act 3 weapons, tavern brawler / smite gear builds,
and 5th edition D&D rules into Game 11 (博德之门3).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

COMPANIONS = [
    {
        'name': '阿斯代伦 (Astarion)',
        'title': '吸血鬼衍体 · 游荡者刺客/飞升真祖',
        'rarity': 5,
        'element': '暗影刺杀 (Shadow Assassin)',
        'weapon_type': '双持短剑 / 手弩',
        'region': '博德之门上城区',
        'arkhe': '吸血鬼之吻',
        'skills': [
            {'name': '偷袭 (Sneak Attack)', 'type': 'ELEMENTAL_SKILL', 'scaling': '额外高额骰子真伤', 'description': '当对目标拥有优势或有队友在目标身旁时发动，造成巨量额外偷袭物理穿透伤害！'},
            {'name': '飞升真祖狂暴 (Ascendant Bite)', 'type': 'ELEMENTAL_BURST', 'scaling': '附加1d10死灵真伤', 'description': '完成卡扎多尔血祭仪式完成飞升！所有普通攻击与技能永久附加 1d10 额外死灵伤害与吸血！'}
        ],
        'passives': [
            {'name': '吸血鬼之吻', 'description': '吸取活人鲜血获得【快乐】状态，所有检定与攻击骰 +1'},
            {'name': '狡黠动作', 'description': '可将疾走、撤离、隐藏作为附赠动作施放'}
        ]
    },
    {
        'name': '影心 (Shadowheart)',
        'title': '莎尔圣女/塞伦涅光明牧师 · 庇护灵体守卫',
        'rarity': 5,
        'element': '神圣光耀/暗夜幽影 (Radiant/Shadow)',
        'weapon_type': '权杖 / 盾牌',
        'region': '哀伤之邸',
        'arkhe': '神圣干预',
        'skills': [
            {'name': '灵体守卫 (Spirit Guardians)', 'type': 'ELEMENTAL_SKILL', 'scaling': '3d8光耀/暗蚀光环', 'description': '召唤漫天光明或幽暗灵体环绕自身，任何进入光环的敌人立刻减速并承受每回合 3d8 神圣切割爆发！割草神技！'},
            {'name': '神圣干预 (Divine Intervention)', 'type': 'ELEMENTAL_BURST', 'scaling': '神明降世/终生一次', 'description': '呼唤神明直接降下奇迹！召唤传奇武器【信徒权杖】或为全场友军瞬间满血复活复苏！'}
        ],
        'passives': [
            {'name': '引导神力', 'description': '消耗神力发动莎尔的暗影潜行或光明牧师的破晓驱散'},
            {'name': '神圣庇护', 'description': '为队友施加剑刃结界与生命祝福'}
        ]
    },
    {
        'name': '盖尔 (Gale of Waterdeep)',
        'title': '深水城大魔导师 · 塑能轰炸/密斯特拉选民',
        'rarity': 5,
        'element': '全系奥术 (Arcane Magic)',
        'weapon_type': '传奇法杖 (Staff)',
        'region': '深水城',
        'arkhe': '耐色瑞尔宝珠',
        'skills': [
            {'name': '火球术 (Fireball)', 'type': 'ELEMENTAL_SKILL', 'scaling': '8d6范围火焰大核爆', 'description': '指向目标区域轰出一颗压缩炽热火球，造成 8d6 巨额范围火焰伤害，塑能系塑形可完全免疫误伤队友！'},
            {'name': '连锁闪电 (Chain Lightning)', 'type': 'ELEMENTAL_BURST', 'scaling': '10d8雷电弹射蒸发', 'description': '射出狂暴高压闪电在多达4个敌人之间弹射，配合法师潮湿易伤机制打出翻倍超百点瞬间清屏伤害！'}
        ],
        'passives': [
            {'name': '法术位槽恢复', 'description': '在短休中通过奥术回想快速恢复消耗的环位法术位'},
            {'name': '耐色瑞尔自爆', 'description': '胸前封印耐色瑞尔毁灭宝珠，拥有毁灭整片大地的禁忌力量'}
        ]
    },
    {
        'name': '卡菈克 (Karlach)',
        'title': '地狱狂蛮人 · 地狱引擎酒馆投掷流战神',
        'rarity': 5,
        'element': '狂暴烈焰 (Hellfire Rage)',
        'weapon_type': '三叉戟 / 巨斧',
        'region': '阿弗纳斯第一地狱',
        'arkhe': '地狱引擎',
        'skills': [
            {'name': '狂暴投掷 (Frenzied Throw)', 'type': 'ELEMENTAL_SKILL', 'scaling': '超重投掷击倒击碎', 'description': '进入地狱狂暴形态，作为附赠动作抓起地上的尸体、地精敌人或传奇三叉戟投掷砸出，必定击倒目标并造成碾压真伤！'},
            {'name': '酒馆殴斗重碾 (Tavern Brawler Smash)', 'type': 'ELEMENTAL_BURST', 'scaling': '双倍力量调整值算伤', 'description': '结合【酒馆殴斗者】专长，将超高力量调整值翻倍算入攻击命中与伤害，一回合投掷4~6次摧枯拉朽！'}
        ],
        'passives': [
            {'name': '硬币过热', 'description': '消耗灵魂钱币点燃地狱引擎，所有物理攻击附加烈焰真伤'},
            {'name': '坚忍狂暴', 'description': '狂暴期间获得对物理钝击、穿刺、挥砍伤害的 50% 减伤减半抗性！'}
        ]
    },
    {
        'name': '莱埃泽尔 (Lae\'zel)',
        'title': '吉斯洋基战神 · 巨武器大师动作如潮一轮六刀',
        'rarity': 5,
        'element': '灵能星光 (Githyanki Psionics)',
        'weapon_type': '吉斯洋基大剑 (Greatsword)',
        'region': '星界吉斯洋基养育间',
        'arkhe': '星界跳跃',
        'skills': [
            {'name': '动作如潮 (Action Surge)', 'type': 'ELEMENTAL_SKILL', 'scaling': '重置动作/爆发翻倍', 'description': '突破生理极限，立刻额外获得一个全新的完整主动作！在一回合内连续打出多达 6~9 次巨剑重击！'},
            {'name': '卓越战术打击 (Battle Master Maneuver)', 'type': 'ELEMENTAL_BURST', 'scaling': '反击/缴械/摔绊三连', 'description': '消耗卓越骰打出摔绊攻击击倒敌人使其受制，紧接巨武器大师绝命跳劈！一回合秒杀红龙与Boss！'}
        ],
        'passives': [
            {'name': '巨武器大师 (-5/+10)', 'description': '攻击骰减5换取攻击命中伤害暴增 +10 必定重创'},
            {'name': '吉斯灵能飞跃', 'description': '跳跃距离提升三倍，如离弦之箭跨越整个战场'}
        ]
    },
    {
        'name': '明萨拉 (Minthara Baenre)',
        'title': '卓尔圣武士 · 复仇之誓致命至圣斩',
        'rarity': 5,
        'element': '至圣光耀 (Divine Smite)',
        'weapon_type': '单手战锤 / 巨剑',
        'region': '幽暗地域魔索布莱城',
        'arkhe': '至圣斩',
        'skills': [
            {'name': '至圣斩 (Divine Smite)', 'type': 'ELEMENTAL_SKILL', 'scaling': '消耗法术位爆发极境', 'description': '近战武器命中瞬间引爆圣武士誓言法术位，倾泻万道金色耀光造成极高额外光耀伤害！若暴击则至圣斩骰子全部翻倍！'},
            {'name': '复仇审判 (Vow of Enmity)', 'type': 'ELEMENTAL_BURST', 'scaling': '10回合必定优势判定', 'description': '对指定敌方立下复仇誓言，此后 10 回合内对该目标的所有攻击骰均无条件享有【优势】双骰投掷！'}
        ],
        'passives': [
            {'name': '守护灵光', 'description': '为自身与附近队友提供等同于魅力调整值的所有豁免检定加值！'},
            {'name': '至圣健壮', 'description': '免疫疾病与恐惧'}
        ]
    }
]

LEGENDARY_WEAPONS = [
    {'name': '尼鲁纳 (Nyrulna)', 'type': '传奇三叉戟', 'rarity': 5, 'base_atk': '1d8+3 (穿刺+雷电)', 'sub_stat': '投掷后自动飞回手中', 'refine': '微风连接：投掷击中时引发大范围雷霆雷电风暴爆炸；持有者移动速度增加3米，免疫一切坠落摔伤伤害！'},
    {'name': '洛山达之血 (Blood of Lathander)', 'type': '传奇单手权杖', 'rarity': 5, 'base_atk': '1d6+3 (钝击+晨曦光耀)', 'sub_stat': '6米光耀盲目不死生物', 'refine': '洛山达的祝福：生命降至0点时立即免疫死亡并恢复 2d6 生命值，同时为周围队友恢复体力；附带6环法术【日曜术】！'},
    {'name': '玛科赫什基 (Markoheshkir)', 'type': '传奇全能法杖', 'rarity': 5, 'base_atk': '法术难度等级+1，法术攻击+1', 'sub_stat': '奥术蓄能法术位免费', 'refine': '克雷斯卡之恩赐：吸收冰火雷酸毒各系元素形态；【凯瑟里克之盾】：施放下一个任意高环法术时完全不消耗任何法术位！'},
    {'name': '博德安的巨人杀手 (Balduran\'s Giantslayer)', 'type': '传奇巨剑', 'rarity': 5, 'base_atk': '2d6+3 (挥砍+双倍力量)', 'sub_stat': '力量调整值翻倍附加伤害', 'refine': '巨人杀手：命中敌人附加两倍力量修正！【巨人形态】：体型暴增变大，获得27点临时生命值与巨额物理增伤！'},
    {'name': '致命一击 (Knife of the Undermountain King)', 'type': '珍奇短剑', 'rarity': 4, 'base_atk': '1d6+2 (穿刺)', 'sub_stat': '暴击骰子阈值降低至19', 'refine': '暗影伏击：攻击优势时重骰较低伤害；暴击所需骰值降低 1 点，刺客双持暴击流核心神兵。'}
]

BUILD_GEAR = [
    {
        'name': '酒馆殴斗投掷神装套 (Tavern Brawler Build)',
        'two_piece': '核心专长：酒馆殴斗者 (Tavern Brawler)',
        'four_piece': '投掷物品或徒手攻击时，力量调整值加成翻倍计入命中骰与伤害骰，配合尼鲁纳一回合造成超300点稳定远程轰炸！',
        'pieces': ['夸席特之戒', '火花手套', '无羁重甲']
    },
    {
        'name': '至圣斩核爆圣骑士套 (Smite Paladin Build)',
        'two_piece': '暴击骰阈值降低与神圣重甲',
        'four_piece': '将至圣斩绑定暴击被动触发，配合豁免灵光与巨武器大师，一击打出破百点光耀核爆秒杀主脑信徒！',
        'pieces': ['坚固重甲', '复仇之誓圣徽', '救世者之盾']
    }
]

MECHANICS = [
    {
        'category': 'D&D 5e 核心',
        'title': '二十面骰 (d20) 命中、优势与劣势法则',
        'formula': '命中检定 = 1d20 + 熟练加值 + 属性调整值 (力量/敏捷) vs 目标护甲等级 (AC)',
        'parameters': {
            '优势 (Advantage)': '投掷两颗二十面骰，取其中数值较高的一颗作为最终结果（命中率大幅飙升）',
            '劣势 (Disadvantage)': '投掷两颗二十面骰，强制取其中数值较低的一颗',
            '大成功/大失败': '投出自然 20 为必定暴击命中（伤害骰翻倍）；投出自然 1 为必定未命中'
        }
    },
    {
        'category': '战术偷袭',
        'title': '受惊轮 (Surprise Round) 与潜伏暗杀机制',
        'formula': '在未被敌人视野察觉时发动先手攻击触发【受惊】',
        'parameters': {
            '受惊状态': '受惊的敌人在整整第一个战斗回合内完全无法采取任何行动或动作，任由全队白打一轮'
        }
    },
    {
        'category': '法术规则',
        'title': '专注机制 (Concentration) 与法术位管理',
        'formula': '同一时间一名施法者只能维持 1 个专注法术（如加速术、灵体守卫、祝福术）',
        'parameters': {
            '专注受击检定': '维持专注的角色受到伤害时，必须进行体质豁免检定（难度为10或所受伤害一半），失败则专注法术中断'
        }
    }
]


def crawl_and_sync_bg3(game_id=11):
    print(f'[Baldur\'s Gate 3] Preparing Companions, Legendary Weapons & D&D Rules for Game {game_id} ...')

    characters = []
    for c in COMPANIONS:
        characters.append({
            'name': c['name'],
            'title': c['title'],
            'rarity': c['rarity'],
            'element': c['element'],
            'weapon_type': c['weapon_type'],
            'region': c['region'],
            'arkhe': c['arkhe'],
            'avatar_url': f'/games/bg3/{c["name"].split()[0]}.png',
            'splash_url': '',
            'base_stats': [
                {'level': '1级林地初遇', 'str': 16, 'dex': 14, 'con': 14, 'int': 10, 'wis': 12, 'cha': 10},
                {'level': '12级决战博德安', 'str': 24, 'dex': 18, 'con': 20, 'int': 16, 'wis': 16, 'cha': 22}
            ],
            'talents': c['skills'],
            'passives': c['passives'],
            'constellations': [],
            'special_mechanics': {'circuit': c['arkhe']},
            'recommendations': {'best_weapon': '尼鲁纳 / 玛科赫什基 / 博德安巨人杀手', 'best_build': '酒馆殴斗投掷流 / 至圣斩骑士'},
            'version': 'Patch 7'
        })

    weapons = []
    for w in LEGENDARY_WEAPONS:
        weapons.append({
            'name': w['name'],
            'type': w['type'],
            'rarity': w['rarity'],
            'icon_url': f'/games/bg3_weapons/{w["name"].split()[0]}.png',
            'base_atk_curve': {'damage_profile': w['base_atk']},
            'sub_stat': {'enchantment': w['sub_stat']},
            'refinements': {'legendary_perk': w['refine']},
            'ascension_materials': {'type': '博德之门第三章传奇宝箱 / 击败神明选民获取'},
            'version': 'Patch 7'
        })

    artifacts = []
    for b in BUILD_GEAR:
        artifacts.append({
            'name': b['name'],
            'rarity_min': 5,
            'rarity_max': 5,
            'icon_url': f'/games/bg3_builds/{b["name"].split()[0]}.png',
            'two_piece_bonus': b['two_piece'],
            'four_piece_bonus': b['four_piece'],
            'pieces': [{'slot': p, 'effect': '专长增幅'} for p in b['pieces']],
            'rules_reference': {'description': 'D&D 5e 专长与构筑配置'},
            'version': 'Patch 7'
        })

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    a_count = upsert_artifacts(game_id, artifacts)
    m_count = upsert_mechanics(game_id, MECHANICS)
    print(f'[Baldur\'s Gate 3] Ingested into Game {game_id}: {c_count} companions, {w_count} weapons, {a_count} builds, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_bg3(11)
