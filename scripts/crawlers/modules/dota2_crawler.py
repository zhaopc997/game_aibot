"""
DOTA 2 (刀塔2) Heroes, Items, Neutral Artifacts & Competitive Mechanics Crawler
Ingests competitive heroes across 4 attributes (力量/敏捷/智力/全才), core tier-5 items,
neutral drops & Aegis, and esports game mechanics into Game 5 (DOTA 2).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

HEROES = [
    {
        'name': '影魔 (Shadow Fiend - Nevermore)',
        'title': '奈文摩尔 · 毁灭阴影灵魂收割者',
        'rarity': 5,
        'element': '敏捷 (Agility)',
        'weapon_type': '远程灵魂攻击',
        'region': '深渊裂隙',
        'arkhe': '灵魂收集',
        'skills': [
            {'name': '毁灭阴影 (Z/X/C 三炮)', 'type': 'ELEMENTAL_SKILL', 'scaling': '近/中/远三段AOE', 'description': '向前方200/450/700距离轰出毁灭黑影，连续命中伤害逐层叠加翻倍，中路压制核心！'},
            {'name': '魂之挽歌 (Requiem of Souls)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏灵魂爆发/恐惧', 'description': '引爆体内收集的所有亡魂形成黑色风暴，释放灵魂波造成巨额魔法伤害，并使范围内敌人陷入恐惧逃窜！'}
        ],
        'passives': [
            {'name': '支配死灵', 'description': '击杀小兵或英雄收集灵魂，每个灵魂永久提供额外物理攻击力'},
            {'name': '魔王降临', 'description': '降低周围所有敌方单位的基础护甲'}
        ]
    },
    {
        'name': '祈求者 (Invoker - Kael)',
        'title': '卡尔 · 掌控冰雷火十种法术的大魔导师',
        'rarity': 5,
        'element': '全才 (Universal)',
        'weapon_type': '元素魔法长袍',
        'region': '魔法议会',
        'arkhe': '元素祈唤',
        'skills': [
            {'name': '元素祈唤 (Invoke)', 'type': 'ELEMENTAL_SKILL', 'scaling': '十种法术任意组合', 'description': '融合当前冰(Q)、雷(W)、火(E)三颗元素球，瞬间召唤出【混沌陨石】、【强袭飓风】、【超声波】、【天火】、【电磁脉冲】等10种终极法术！'},
            {'name': '阳炎冲击 (Sun Strike)', 'type': 'ELEMENTAL_BURST', 'scaling': '全地图全图狙杀真伤', 'description': '在全地图任意位置召唤天火打击，造成极高纯粹神圣伤害，神杖升级后可释放全屏天火降临！'}
        ],
        'passives': [{'name': '元素精通', 'description': '冰球提供生命恢复，雷球提供移速与攻速，火球提供基础攻击力'}]
    },
    {
        'name': '帕吉 (Pudge - 屠夫)',
        'title': '屠夫 · 神钩肉山致命肢解',
        'rarity': 5,
        'element': '力量 (Strength)',
        'weapon_type': '血腥肉钩与切肉刀',
        'region': '瘟疫荒原',
        'arkhe': '堆积腐肉',
        'skills': [
            {'name': '肉钩 (Meat Hook)', 'type': 'ELEMENTAL_SKILL', 'scaling': '1300码超远穿刺神钩', 'description': '掷出夺命血腥肉钩，命中目标将其强行拉拽至帕吉面前，并造成高额纯粹真实伤害！盲钩与预判翻盘核心！'},
            {'name': '肢解 (Dismember)', 'type': 'ELEMENTAL_BURST', 'scaling': '持续咬噬眩晕吸血', 'description': '跳在敌人身上疯狂撕咬，造成长时间无视魔法免疫的强力压制与眩晕，根据帕吉力量值造成高倍率撕裂伤害并回血！'}
        ],
        'passives': [
            {'name': '腐烂 (Rot)', 'description': '散发剧毒瘟疫自残并极速减速周围敌人'},
            {'name': '堆积腐肉', 'description': '周围每死一个敌方英雄，永久增加帕吉的基础力量与魔法抗性！后期血量过万！'}
        ]
    },
    {
        'name': '敌法师 (Anti-Mage - Magina)',
        'title': '玛吉纳 · 闪烁切入法力虚空核爆',
        'rarity': 5,
        'element': '敏捷 (Agility)',
        'weapon_type': '月刃双刀',
        'region': '星隐寺',
        'arkhe': '法力损毁',
        'skills': [
            {'name': '闪烁 (Blink)', 'type': 'ELEMENTAL_SKILL', 'scaling': '4秒超短CD全图瞬移', 'description': '极短冷却瞬间瞬移至 1200 码范围内任意位置，刷钱与切入后排核心神技'},
            {'name': '法力虚空 (Mana Void)', 'type': 'ELEMENTAL_BURST', 'scaling': '法力缺失百分比AOE核爆', 'description': '将敌人残缺的法力值转化为大爆炸！目标缺失的蓝量越多，爆炸造成的范围魔法伤害越恐怖，经常打出一击瞬间蒸发敌阵！'}
        ],
        'passives': [
            {'name': '法力损毁', 'description': '每次普攻削减敌人大量魔法值并造成等量额外物理伤害'},
            {'name': '法术反制', 'description': '被动提供巨额魔法抗性，主动开启生成护盾反弹指向性法术！'}
        ]
    },
    {
        'name': '剑圣 (Juggernaut - Yurnero)',
        'title': '尤涅若 · 遮面之岛最后传人 · 无敌斩',
        'rarity': 5,
        'element': '敏捷 (Agility)',
        'weapon_type': '龙泉神剑',
        'region': '遮面之岛',
        'arkhe': '剑刃风暴',
        'skills': [
            {'name': '剑刃风暴 (Blade Fury)', 'type': 'ELEMENTAL_SKILL', 'scaling': '魔法免疫旋转切割', 'description': '高速旋转挥舞利刃，期间处于完全魔法免疫状态并对周围敌人造成连续切割伤害，可配合TP逃生！'},
            {'name': '无敌斩 (Omnislash)', 'type': 'ELEMENTAL_BURST', 'scaling': '无敌瞬移连续斩杀', 'description': '尤涅若跃向敌阵，自身处于绝对无敌状态连续瞬移斩杀敌人，斩击附带攻击特效并造成致命暴击！'}
        ],
        'passives': [
            {'name': '治疗守卫', 'description': '召唤百分比群体回血守卫，短时间让全队回满血'},
            {'name': '剑舞', 'description': '普攻拥有极高几率造成 180% 暴击伤害'}
        ]
    },
    {
        'name': '幻影刺客 (Phantom Assassin - Mortred)',
        'title': '莫特雷斯 · 魅影面纱 450% 绝命大红字暴击',
        'rarity': 5,
        'element': '敏捷 (Agility)',
        'weapon_type': '绝命回旋飞镖与双刃',
        'region': '魅影之纱',
        'arkhe': '恩赐解脱',
        'skills': [
            {'name': '窒碍短匕 (Stifling Dagger)', 'type': 'ELEMENTAL_SKILL', 'scaling': '远距离飞镖减速/触发特效', 'description': '掷出涂毒短匕造成减速并完美继承攻击特效与暴击！一镖暴击直接秒杀辅助！'},
            {'name': '幻影突袭 (Phantom Strike)', 'type': 'ELEMENTAL_SKILL', 'scaling': '穿透虚空超速突进', 'description': '瞬间突进到敌方身后，获得极高攻击速度加成，持续挥舞双刃疯狂连砍！'}
        ],
        'passives': [
            {'name': '魅影无形', 'description': '获得高达 50% 的物理闪避，且在小地图上隐匿自身头像消失！'},
            {'name': '恩赐解脱 (Coup de Grace)', 'type': 'ELEMENTAL_BURST', 'scaling': '450% 终极暴击大红字', 'description': '攻击有几率造成高达 450% 的毁灭级大红字暴击伤害！刀刀见血瞬间蒸发！'}
        ]
    },
    {
        'name': '斯温 (Sven - 流浪剑客)',
        'title': '流浪剑客 · 开启神之力量真男人一刀清屏',
        'rarity': 5,
        'element': '力量 (Strength)',
        'weapon_type': '守夜人大剑',
        'region': '守夜骑士团',
        'arkhe': '神之力量',
        'skills': [
            {'name': '风暴之锤 (Storm Hammer)', 'type': 'ELEMENTAL_SKILL', 'scaling': '飞锤范围晕眩', 'description': '掷出附带风暴力量的神铁飞锤，眩晕目标及其周围所有敌人，驱散增益状态'},
            {'name': '神之力量 (God\'s Strength)', 'type': 'ELEMENTAL_BURST', 'scaling': '基础攻击力提升 200%', 'description': '斯温发出震怒咆哮全身化为血红巨神！攻击力瞬间暴增 200%，配合分裂大剑一刀劈碎整个敌方阵容！'}
        ],
        'passives': [
            {'name': '巨力挥舞 (Great Cleave)', 'description': '普攻附带高达 100% 的大范围物理狂暴分裂伤害'},
            {'name': '战吼 (Warcry)', 'description': '为周围友军提供高额护甲与移动速度加成'}
        ]
    },
    {
        'name': '水晶室女 (Crystal Maiden - Rylai)',
        'title': '莉莱 · 冰霜女巫极寒领域与全队回蓝',
        'rarity': 5,
        'element': '智力 (Intelligence)',
        'weapon_type': '冰晶权杖',
        'region': '蓝心冰川',
        'arkhe': '奥术光环',
        'skills': [
            {'name': '冰封禁制 (Frostbite)', 'type': 'ELEMENTAL_SKILL', 'scaling': '绝对冻结定身缠绕', 'description': '将敌人冰封在冰棺中使其无法移动或普攻，并持续承受冰冻魔法伤害'},
            {'name': '极寒领域 (Freezing Field)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏暴风雪冰爆', 'description': '在自身周围引导漫天暴风雪与巨型冰锥爆炸，造成超强群体减速与毁灭魔法爆发！配合BKB团战利器！'}
        ],
        'passives': [
            {'name': '奥术光环 (Arcane Aura)', 'description': '为全地图所有友方英雄提供持续的魔法恢复速率加成，对自身效果翻倍！'},
            {'name': '水晶新星', 'description': '大范围冰霜爆破，减速敌人攻击与移动速度'}
        ]
    },
    {
        'name': '虚空假面 (Faceless Void - Darkterror)',
        'title': '暗恐 · 时间结界大罩子世界暂停',
        'rarity': 5,
        'element': '敏捷 (Agility)',
        'weapon_type': '时间权杖与战锤',
        'region': '超维空间',
        'arkhe': '时间锁定',
        'skills': [
            {'name': '时间漫游 (Time Walk)', 'type': 'ELEMENTAL_SKILL', 'scaling': '时间倒流血量回溯', 'description': '冲向目标地点，并立即逆转回溯过去 2 秒内承受的全部伤害！'},
            {'name': '时间结界 (Chronosphere)', 'type': 'ELEMENTAL_BURST', 'scaling': '绝对时停时间结界大罩子', 'description': '撕裂时空创造一个巨大半球体结界！结界内除虚空假面本人外，所有敌方、友方、防御塔、弹道完全暂停静止 5 秒！'}
        ],
        'passives': [
            {'name': '时间锁定 (Time Lock)', 'description': '攻击有几率让敌人陷入时间暂停晕眩，并触发二次额外普攻打击'},
            {'name': '时间膨胀', 'description': '延长附近敌人处于冷却中技能的冷却时间并造成减速'}
        ]
    },
    {
        'name': '变体精灵 (Morphling)',
        'title': '水人 · 属性全转敏捷波浪秒杀',
        'rarity': 5,
        'element': '敏捷 (Agility)',
        'weapon_type': '水流涌动核心',
        'region': '坠星之泪',
        'arkhe': '属性变换',
        'skills': [
            {'name': '波浪形态 (Waveform)', 'type': 'ELEMENTAL_SKILL', 'scaling': '无敌水流穿梭位移', 'description': '化身为无敌的狂暴波浪向前汹涌冲刺，对穿过的所有敌人造成高额伤害并位移'},
            {'name': '变体攻击 (Adaptive Strike)', 'type': 'ELEMENTAL_SKILL', 'scaling': '敏捷击杀/力量眩晕', 'description': '基于当前敏捷打出毁天灭地的高额纯伤害，或基于力量打出长达 3 秒的重度眩晕'},
            {'name': '形态变化 (Morph)', 'type': 'ELEMENTAL_BURST', 'scaling': '完美复制敌方英雄', 'description': '化身为敌方任意英雄的复制体，完美窃取并使用其所有基础小技能！'}
        ],
        'passives': [{'name': '属性变换 (转血转敏)', 'description': '在力量与敏捷之间任意实时调配属性点！濒死时全转力量瞬间回满血，输出时全转敏捷攻速破表！'}]
    }
]

ITEMS = [
    {'name': '黑皇杖 (Black King Bar - BKB)', 'type': '神器防具', 'rarity': 5, 'base_atk': '+10 力量, +24 攻击力', 'sub_stat': '天神下凡魔法免疫', 'refine': '主动开启【天神下凡】：体型变大并获得持续 9/8/7/6 秒的完全魔法免疫与纯粹伤害抗性，后期团战开团绝对核心！'},
    {'name': '闪烁匕首 (Blink Dagger - 跳刀)', 'type': '先手神器', 'rarity': 5, 'base_atk': '先手跨越位移', 'sub_stat': '1200码瞬间瞬移', 'refine': '瞬间瞬移至指定地点，受英雄伤害后禁用 3 秒；牛头、屠夫、猛犸、影魔开团秒人必备神器！'},
    {'name': '阿哈利姆神杖 (Aghanim\'s Scepter - A杖)', 'type': '终极质变神器', 'rarity': 5, 'base_atk': '+10 全属性, +175 生命, +175 魔法', 'sub_stat': '重做并升阶核心大招', 'refine': '彻底强化或重做英雄的终极大招，甚至解锁全新的第 5、第 6 个独立技能！'},
    {'name': '圣剑 (Divine Rapier)', 'type': '绝命武器', 'rarity': 5, 'base_atk': '+350 超高物理攻击力', 'sub_stat': '死亡掉落规则', 'refine': '全刀塔攻击力最高绝命神兵！持有者阵亡时圣剑必定掉落于地面，敌方可捡起占为己有，翻盘与崩盘一念之间！'},
    {'name': '斯嘉蒂之眼 (Eye of Skadi - 冰眼)', 'type': '全能神器', 'rarity': 5, 'base_atk': '+22 全属性, +220 生命, +220 魔法', 'sub_stat': '极寒冰霜减速减疗', 'refine': '普攻附加极度寒霜，大幅降低敌方移动速度与攻击速度，并直接砍掉目标 40% 的生命回复与吸血效果！'},
    {'name': '蝴蝶 (Butterfly)', 'type': '敏捷神兵', 'rarity': 5, 'base_atk': '+35 敏捷, +30 攻击速度, +25 攻击力', 'sub_stat': '35% 物理闪避', 'refine': '敏捷核心终极毕业神装，提供巨额物理闪避与攻速爆发，逼迫敌方必须做出金箍棒才能克制！'},
    {'name': '强袭装甲 (Assault Cuirass)', 'type': '光环铠甲', 'rarity': 5, 'base_atk': '+10 护甲, +30 攻击速度', 'sub_stat': '攻防一体战意光环', 'refine': '为友军全体提供 +5 护甲与 +30 攻速光环；降低周围所有敌方建筑与英雄 5 点护甲，推塔团战质变！'},
    {'name': '辉耀 (Radiance)', 'type': '灼烧神剑', 'rarity': 5, 'base_atk': '+55 物理攻击力', 'sub_stat': '60/s 全屏神圣灼烧与致盲', 'refine': '开启后周身散发神圣烈焰，每秒灼烧周围所有敌人造成 60 点魔法伤害，并使其物理普攻出现 15% 丢失致盲！'},
    {'name': '血棘 (Bloodthorn)', 'type': '暴击沉默神杖', 'rarity': 5, 'base_atk': '+60 攻击力, +20 智力, +60 攻速', 'sub_stat': '破隐沉默与必定暴击', 'refine': '对敌人施加灵魂禁锢沉默 5 秒，期间所有友军对其进行的普攻必定造成 130% 暴击并附加额外魔法穿透！'},
    {'name': '邪恶镰刀 (Scythe of Vyse - 羊刀)', 'type': '终极硬控杖', 'rarity': 5, 'base_atk': '+35 智力, +10 力量, +10 敏捷', 'sub_stat': '瞬间变形小绵羊', 'refine': '瞬间将敌方核心英雄变成一只行动迟缓的小绵羊 3.5 秒！期间无法施法、无法普攻、禁用一切被动与闪避！'}
]

NEUTRAL_ARTIFACTS = [
    {
        'name': '不朽之守护 (Aegis of the Immortal - 复活甲)',
        'two_piece': '击杀肉山 Roshan 掉落核心掉落物',
        'four_piece': '持有者受到致命斩杀伤害时，在原地化为金色墓碑，5 秒后原地满血满蓝满状态满血复活！决胜关键！',
        'pieces': ['肉山巢穴掉落', '持续时间 5 分钟']
    },
    {
        'name': '阿哈利姆魔晶 (Aghanim\'s Shard)',
        'two_piece': '15分钟解锁购买或击杀肉山掉落',
        'four_piece': '永久吸收为英雄被动，深度强化某个小技能并赋予全新技能连携词缀！',
        'pieces': ['1400金币吸收', '永久质变词条']
    },
    {
        'name': '刷新球 (Refresher Orb)',
        'two_piece': '重置英雄所有技能与道具冷却',
        'four_piece': '消耗大量魔法，瞬间刷新包括BKB、跳刀、终极大招在内的全部冷却时间，连续打出双大招毁天灭地！',
        'pieces': ['神秘法杖', '坚韧球合成']
    }
]

MECHANICS = [
    {
        'category': '对线基本功',
        'title': '正补与反补金钱经验差机制',
        'formula': '敌方小兵残血普攻命中得金钱经验 (Last-Hit)；我方小兵半血以下普攻击杀为反补 (Deny)',
        'parameters': {
            '反补压制': '成功反补后，敌方英雄只能获得极微量残存经验，且我方可获得额外金币奖励，实现中路无解压制',
            '仇恨拉扯': '右键点击敌方英雄吸引小兵仇恨走位，将兵线稳妥拉回己方高坡安全区'
        }
    },
    {
        'category': '野区经济',
        'title': '兵线卡兵与拉野多野囤积机制',
        'formula': '在野怪每分钟刷新时刻（53~55秒）将野怪仇恨拉出营地判定框，实现【单矿变多矿（Stack）】',
        'parameters': {
            '囤野屯矿': '辅助为核心一号位囤积4~5波远古大野，核心开启狂战斧或AOE技能清野，经济瞬间反超一万！'
        }
    },
    {
        'category': '竞技规则',
        'title': '买活机制 (Buyback) 与买活金钱损益',
        'formula': '买活花费 = 200 + (英雄财产总和 / 13) + 冷却时间衰减惩罚',
        'parameters': {
            '买活惩罚': '买活后复活时间延长 25 秒，且在买活后一段时间内获取金币速率降低 60%，非基地关键团不买活'
        }
    },
    {
        'category': '肉山争夺',
        'title': '肉山坑 Roshan 与不朽之守护刷新',
        'formula': '肉山死亡后在 8~11 分钟内随机时间在肉山坑重生，根据昼夜交替在天辉夜魇双坑迁徙',
        'parameters': {
            '二代肉山': '掉落不朽之守护 + 奶酪 (使用瞬间回满2500生命与1500魔法)',
            '三代肉山': '掉落不朽之守护 + 奶酪 + 刷新球碎片 / A杖祝福'
        }
    }
]


def crawl_and_sync_dota2(game_id=5):
    print(f'[DOTA 2] Preparing Heroes, Core Items & Esports Mechanics for Game {game_id} ...')

    characters = []
    for h in HEROES:
        characters.append({
            'name': h['name'],
            'title': h['title'],
            'rarity': h['rarity'],
            'element': h['element'],
            'weapon_type': h['weapon_type'],
            'region': h['region'],
            'arkhe': h['arkhe'],
            'avatar_url': f'/games/dota2/{h["name"].split()[0]}.png',
            'splash_url': '',
            'base_stats': [
                {'level': '1级出门', 'hp': 620, 'mp': 310, 'atk': 52, 'armor': 3.2},
                {'level': '30级神装', 'hp': 3450, 'mp': 1850, 'atk': 380, 'armor': 28.5}
            ],
            'talents': h['skills'],
            'passives': h['passives'],
            'constellations': [],
            'special_mechanics': {'circuit': h['arkhe']},
            'recommendations': {'best_item': '黑皇杖 (BKB) / 闪烁匕首 (跳刀)'},
            'version': '7.37'
        })

    weapons = []
    for item in ITEMS:
        weapons.append({
            'name': item['name'],
            'type': item['type'],
            'rarity': item['rarity'],
            'icon_url': f'/games/dota_items/{item["name"].split()[0]}.png',
            'base_atk_curve': {'stats': item['base_atk']},
            'sub_stat': {'active': item['sub_stat']},
            'refinements': {'ability': item['refine']},
            'ascension_materials': {'type': '神秘商店 / 基地商人购买合成'},
            'version': '7.37'
        })

    artifacts = []
    for a in NEUTRAL_ARTIFACTS:
        artifacts.append({
            'name': a['name'],
            'rarity_min': 5,
            'rarity_max': 5,
            'icon_url': f'/games/dota_neutral/{a["name"].split()[0]}.png',
            'two_piece_bonus': a['two_piece'],
            'four_piece_bonus': a['four_piece'],
            'pieces': [{'slot': p, 'effect': '特殊战局效果'} for p in a['pieces']],
            'rules_reference': {'description': '击杀肉山或野怪掉落'},
            'version': '7.37'
        })

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    a_count = upsert_artifacts(game_id, artifacts)
    m_count = upsert_mechanics(game_id, MECHANICS)
    print(f'[DOTA 2] Ingested into Game {game_id}: {c_count} heroes, {w_count} items, {a_count} neutral artifacts, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_dota2(5)
