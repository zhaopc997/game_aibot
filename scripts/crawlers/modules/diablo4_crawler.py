"""
Diablo IV (暗黑破坏神4) Classes, Mythic Uniques & Season Endgame Mechanics Crawler
Ingests all 6 classes (including Spiritborn 灵巫), mythic unique gear (军帽/祖父/泰瑞尔),
legendary aspects & paragon glyphs, and endgame mechanics into Game 10 (暗黑破坏神4).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

CLASSES = [
    {
        'name': '灵巫 (Spiritborn)',
        'title': '纳汉图丛林使者 · 四大神灵化身 (资料片新职业)',
        'rarity': 5,
        'element': '自然圣灵 (Jungle Spirit)',
        'weapon_type': '长柄战刃 / 战棍',
        'region': '纳汉图丛林',
        'arkhe': '圣灵殿堂',
        'skills': [
            {'name': '绝招 · 灵豹疾行猎杀 (The Hunter)', 'type': 'ELEMENTAL_SKILL', 'scaling': '极速残影跳跃斩杀', 'description': '召唤丛林美洲豹神灵显圣，化身为极速雷影连续在战场中穿梭飞扑猎杀，每一次撕咬均必定暴击！'},
            {'name': '绝招 · 猩猩撼地壁垒 (The Protector)', 'type': 'ELEMENTAL_BURST', 'scaling': '泰坦巨灵震地护盾', 'description': '引动大猩猩神兽降世，狂暴捶击大地粉碎全屏敌人的护甲，并为自身提供相当于生命上限 100% 的坚固障壁！'}
        ],
        'passives': [
            {'name': '圣灵殿堂 (Spirit Hall)', 'description': '选择美洲豹、大猩猩、飞鹰、巨蜈蚣作为第一与第二主神守护灵，将所有技能标签相互转化！'},
            {'name': '灵决律动', 'description': '连续攻击积攒凶猛与决心层数，移速与攻速突破上限'}
        ]
    },
    {
        'name': '野蛮人 (Barbarian)',
        'title': '亚瑞特峰战神 · 军械库四持重兵先祖重击',
        'rarity': 5,
        'element': '狂暴怒气 (Fury/Berserk)',
        'weapon_type': '双手巨剑 / 双手巨锤 / 单手双持',
        'region': '亚瑞特山脉草原',
        'arkhe': '军械库系统',
        'skills': [
            {'name': '先祖之锤 (Hammer of the Ancients)', 'type': 'ELEMENTAL_SKILL', 'scaling': '全怒气倾泻压制大核爆', 'description': '消耗全部怒气将巨锤猛砸向地面，造成惊天动地的范围物理压制伤害，配合压制机制一锤砸出上亿伤害！'},
            {'name': '钢铁之握 (Steel Grasp)', 'type': 'ELEMENTAL_SKILL', 'scaling': '三道铁链群聚易伤', 'description': '掷出三条带倒钩的坚固锁链，将远处所有精英与杂兵强行拉拽到身前，并施加 3 秒易伤与昏迷！'}
        ],
        'passives': [
            {'name': '军械库精通 (Arsenal)', 'description': '同时装备双手钝击、双手劈砍、两把单手武器，随时无缝切换获得不同武器专精词缀！'},
            {'name': '狂暴 (Berserking)', 'description': '进入狂暴状态，伤害提升 25%，移动速度提升 15%'}
        ]
    },
    {
        'name': '死灵法师 (Necromancer)',
        'title': '拉斯玛祭司 · 亡者之书亡灵大军与骨矛核弹',
        'rarity': 5,
        'element': '白骨与暗影 (Bone/Shadow/Blood)',
        'weapon_type': '死灵镰刀 / 聚灵骨盾',
        'region': '凯基斯坦东方沼泽',
        'arkhe': '亡者之书',
        'skills': [
            {'name': '骨矛 (Bone Spear)', 'type': 'ELEMENTAL_SKILL', 'scaling': '贯穿骨片连环反弹', 'description': '射出一根尖锐骨矛贯穿沿途所有敌人，命中后爆裂为数十片反弹骨片二次刺杀，暴击倍率极高！'},
            {'name': '尸爆 (Corpse Explosion)', 'type': 'ELEMENTAL_SKILL', 'scaling': '无消耗全屏连环引爆', 'description': '将地面上的怪物尸骸引爆，造成大范围物理爆炸或转化为滚滚暗影剧毒瘴气，清图极其舒爽！'}
        ],
        'passives': [
            {'name': '亡者之书 (Book of the Dead)', 'description': '可自定义骷髅战士、骷髅法师、白骨魔像的形态属性，或选择将其献祭获得巨额自身全属性提升！'},
            {'name': '精魂汲取', 'description': '每消耗一具尸体回复 6 点精魂并提供强效减伤'}
        ]
    },
    {
        'name': '游侠 (Rogue)',
        'title': '暗影刺客游侠 · 回旋刀锋与多重元素灌注',
        'rarity': 5,
        'element': '物理 / 剧毒 / 冰霜 / 暗影灌注',
        'weapon_type': '双持匕首 / 强力弓弩',
        'region': '凯基斯坦边境',
        'arkhe': '专精系统',
        'skills': [
            {'name': '回旋刀锋 (Twisting Blades)', 'type': 'ELEMENTAL_SKILL', 'scaling': '双刀穿刺回旋收割', 'description': '将附魔双刃刺入敌人体内，1.5秒后双刃呼啸回旋飞回游侠手中，沿途切割所有敌人并缩短技能冷却！'},
            {'name': '暗影步 (Shadow Step)', 'type': 'ELEMENTAL_SKILL', 'scaling': '瞬移背刺不可阻挡', 'description': '遁入暗影瞬间瞬移穿透到目标背后发动致命一击，获得不可阻挡状态并大幅提升暴击伤害！'}
        ],
        'passives': [
            {'name': '灌注系统 (Imbuement)', 'description': '可随时为下两次武器攻击附魔剧毒（持续融化）、冰霜（冻结控场）或暗影（群体连环尸爆）！'},
            {'name': '连击点数专精', 'description': '消耗连击点数使核心技能造成 3 倍以上伤害'}
        ]
    },
    {
        'name': '魔法使 (Sorcerer)',
        'title': '元素织能者 · 电矛连锁闪电与附魔插槽',
        'rarity': 5,
        'element': '火焰 / 冰霜 / 雷电 (Fire/Frost/Lightning)',
        'weapon_type': '法杖 / 聚能法器',
        'region': '维兹捷雷古城',
        'arkhe': '附魔插槽',
        'skills': [
            {'name': '闪电矛 (Lightning Spear)', 'type': 'ELEMENTAL_SKILL', 'scaling': '自动索敌弹射飞矛', 'description': '召唤一道狂暴闪电矛在全屏敌人间高速穿梭弹射，配合暗金项链触发满屏闪电风暴秒杀Boss！'},
            {'name': '火盾 (Flame Shield)', 'type': 'ELEMENTAL_SKILL', 'scaling': '绝对无敌与灼烧', 'description': '周身包裹熊熊烈火，在持续时间内免疫一切攻击伤害并免疫死亡，附带极速回血！'}
        ],
        'passives': [
            {'name': '附魔插槽 (Enchantment Slots)', 'description': '将任意主动技能拖入专属附魔槽，将其转化为全自动触发的强力被动特效（如自动火球、自动冰片）！'},
            {'name': '炽烈真火', 'description': '敌人处于燃烧状态时，魔法使对其造成的暴击伤害大幅提升'}
        ]
    },
    {
        'name': '德鲁伊 (Druid)',
        'title': '斯考斯格伦荒野守护者 · 熊人拍地与狂暴巨狼',
        'rarity': 5,
        'element': '风暴 / 大地 / 狼人 / 熊人',
        'weapon_type': '巨杖 / 双手战斧',
        'region': '斯考斯格伦',
        'arkhe': '灵物恩惠',
        'skills': [
            {'name': '粉碎 (Pulverize)', 'type': 'ELEMENTAL_SKILL', 'scaling': '拍地压制震撼波', 'description': '化身为狂暴巨熊双掌重击地面，引发大范围大地碎石震荡波，必定触发压制伤害碾碎敌阵！'},
            {'name': '风暴狂舞 (Tornado)', 'type': 'ELEMENTAL_BURST', 'scaling': '追踪多重狂暴龙卷风', 'description': '呼唤多股肆虐的风暴龙卷风在敌阵中无规则肆虐穿梭，配合狂狼变形造成持续性致命打击！'}
        ],
        'passives': [
            {'name': '灵物恩惠 (Spirit Boons)', 'description': '献祭德鲁伊灵物获得鹿（减伤）、鹰（攻速暴击）、狼（重置大招）、蛇（剧毒电击）四灵恩赐！'},
            {'name': '自然之怒', 'description': '释放大地技能有几率免费触发风暴技能，反之亦然'}
        ]
    }
]

MYTHIC_UNIQUES = [
    {'name': '谐角之冠 (Harlequin Crest - 军帽)', 'type': '神话暗金头盔', 'rarity': 5, 'base_atk': '伤害减免 20%', 'sub_stat': '全部技能等级 +4', 'refine': '全暗黑破坏神最强质变头盔！提供全技能+4、巨额全伤害减免20%、海量最大生命值与资源回复！任何职业终极毕业必带！'},
    {'name': '祖父 (The Grandfather)', 'type': '神话暗金双手剑', 'rarity': 5, 'base_atk': '+100% 暴击伤害', 'sub_stat': '暴击伤害全局翻倍乘区', 'refine': '不朽神兵：将玩家角色的所有暴击伤害直接乘以 2 倍独立放大！使武器完全不损失耐久度，提供上万点额外生命上限！'},
    {'name': '泰瑞尔之力 (Tyrael\'s Might)', 'type': '神话暗金胸甲', 'rarity': 5, 'base_atk': '+5% 全抗性上限', 'sub_stat': '生命满时发射神圣弹幕', 'refine': '正义天使圣铠：突破抗性上限至 85% 绝对免伤！生命健康时攻击会召唤漫天神圣星光弹幕轰炸敌人！'},
    {'name': '安达利尔的面容 (Andariel\'s Visage)', 'type': '神话暗金头盔', 'rarity': 5, 'base_atk': '+3% 击中吸血', 'sub_stat': '剧毒新星大爆发', 'refine': '攻击命中时有极高几率在目标脚下引爆超强剧毒新星，数秒造成数千万毒素融化伤害，击中吸血让血条永不下降！'},
    {'name': '迪博特的意志 (Tibault\'s Will)', 'type': '暗金独特裤子', 'rarity': 5, 'base_atk': '伤害提升 50%', 'sub_stat': '处于不可阻挡时伤害提升', 'refine': '当你获得不可阻挡状态时，立即恢复 50 点主要能量，并在接下来数秒内伤害提升 50% 独立乘区！'}
]

ASPECT_SETS = [
    {
        'name': '巅峰盘与雕文传奇配置 (Paragon Board & Glyphs)',
        'two_piece': '核心雕文：剥削 (Exploit) 与破坏 (Destruction)',
        'four_piece': '点亮巅峰盘传奇节点，攻击敌人立即施加 3 秒必中易伤，易伤乘区直接提升 50% 以上输出！',
        'pieces': ['传奇巅峰盘节点', '21级满级雕文槽位']
    }
]

MECHANICS = [
    {
        'category': '伤害乘区',
        'title': '易伤、压制与暴击三大独立增伤乘区',
        'formula': '最终伤害 = 基础技能倍率 × 武器伤害 × (1 + 通用A伤区) × 暴击爆伤区(1.5×) × 易伤区(1.2×) × 压制区',
        'parameters': {
            '易伤 (Vulnerable)': '血条变为紫色，基础享有 20% 绝对独立增伤乘区',
            '压制 (Overpower)': '跳出青蓝色或橙色巨额数字，基于生命值与坚固值加总造成瞬间爆裂真伤'
        }
    },
    {
        'category': '赛季终局',
        'title': '大秘境深渊 (The Pit) 与罗盘狂潮 (Infernal Hordes)',
        'formula': '深渊层数 1~150层，通关获取精铸升级材料 (Masterworking Materials)',
        'parameters': {
            '精铸升级': '将暗金装备强化至 12 级，在第4、8、12级随机将某一条核心词缀提升 25%！完美三次中同一词条质变！'
        }
    }
]


def crawl_and_sync_diablo4(game_id=10):
    print(f'[Diablo IV] Preparing Classes, Mythic Uniques & Endgame Mechanics for Game {game_id} ...')

    characters = []
    for c in CLASSES:
        characters.append({
            'name': c['name'],
            'title': c['title'],
            'rarity': c['rarity'],
            'element': c['element'],
            'weapon_type': c['weapon_type'],
            'region': c['region'],
            'arkhe': c['arkhe'],
            'avatar_url': f'/games/diablo4/{c["name"].split()[0]}.png',
            'splash_url': '',
            'base_stats': [
                {'level': '1级初入避难所', 'hp': 100, 'armor': 50, 'fury': 100},
                {'level': '100级巅峰满级', 'hp': 25000, 'armor': 9230, 'fury': 250}
            ],
            'talents': c['skills'],
            'passives': c['passives'],
            'constellations': [],
            'special_mechanics': {'circuit': c['arkhe']},
            'recommendations': {'best_gear': '谐角之冠 (军帽) / 祖父 / 泰瑞尔之力', 'best_aspect': '剥削雕文 / 迪博特的意志'},
            'version': 'v2.0 (憎恨之躯)'
        })

    weapons = []
    for u in MYTHIC_UNIQUES:
        weapons.append({
            'name': u['name'],
            'type': u['type'],
            'rarity': u['rarity'],
            'icon_url': f'/games/diablo_uniques/{u["name"].split()[0]}.png',
            'base_atk_curve': {'damage_profile': u['base_atk']},
            'sub_stat': {'mythic_stat': u['sub_stat']},
            'refinements': {'legendary_power': u['refine']},
            'ascension_materials': {'type': '璀璨回响 / 击杀都瑞尔与安达利尔掉落'},
            'version': 'v2.0'
        })

    artifacts = []
    for a in ASPECT_SETS:
        artifacts.append({
            'name': a['name'],
            'rarity_min': 5,
            'rarity_max': 5,
            'icon_url': f'/games/diablo_paragon/{a["name"].split()[0]}.png',
            'two_piece_bonus': a['two_piece'],
            'four_piece_bonus': a['four_piece'],
            'pieces': [{'slot': p, 'effect': '传奇乘区'} for p in a['pieces']],
            'rules_reference': {'description': '巅峰盘节点与雕文加成'},
            'version': 'v2.0'
        })

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    a_count = upsert_artifacts(game_id, artifacts)
    m_count = upsert_mechanics(game_id, MECHANICS)
    print(f'[Diablo IV] Ingested into Game {game_id}: {c_count} classes, {w_count} mythic uniques, {a_count} aspect sets, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_diablo4(10)
