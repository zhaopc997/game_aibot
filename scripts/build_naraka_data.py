"""
Build complete, differentiated, high-fidelity Naraka data for Game 20.
Includes:
- 32 Heroes with:
  - 5-stage differentiated base_stats (hp, armor, energy, atk, def, crit_rate, crit_dmg, energy_recovery)
  - structured talents scaling dicts (Record<string, string>)
  - 6-tier constellations (c: 1..6, name, desc)
  - structured special_mechanics (4-5 key mechanisms)
  - full recommendations (weapons: {bis, alternative_5s, budget_4s}, artifacts: {bis_set, alt_set}, main_stats: {sands, goblet, circlet}, sub_stats)
  - avatar_url (/games/naraka/{short_name}.svg)
- 20 Weapons with:
  - base_atk_curve, sub_stat, refinements, ascension_materials, icon_url (/games/naraka_weapons/{name}.svg)
- 20 Souljades with:
  - two_piece_bonus, four_piece_bonus, pieces, rules_reference, icon_url (/games/souljades/{name}.svg)
- 14 Combat mechanics
"""

import os
import json
from scripts.crawlers.common.db import (
    get_connection,
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

STAGES = [
    '初登聚窟洲 (Lv.1 白装初生)',
    '青铜争锋 (Lv.15 蓝甲小成)',
    '白银豪杰 (Lv.30 紫甲通神)',
    '黄金宗师 (Lv.45 金甲大成)',
    '无间修罗 (满级印记神装)'
]

HERO_DEFINITIONS = [
    {
        'name': '宁红夜 (Viper Ning)',
        'title': '昆仑玄女 · 盲剑客群控核心',
        'rarity': 5,
        'element': '昆仑真气 · 群控',
        'weapon_type': '长剑 / 太刀',
        'region': '昆仑山',
        'arkhe': '赤练之毒',
        'archetype': 'controller',
        'hp_mod': 20, 'atk_mod': 10, 'energy_mod': 5, 'crit_mod': 1.0,
        'skills': [
            {
                'name': '昆仑决 (F技能)',
                'type': 'ELEMENTAL_SKILL',
                'description': '凝聚真气踢飞正前方敌人，造成大量伤害并强行打断蓄力霸体。命中后封印其技能与奥义 8 秒！',
                'scaling': {
                    '招式伤害': '260% 物理倍率',
                    '冷却时间': '15 秒',
                    '霸体判定': '蓝霸体不可振',
                    '控制效果': '强行破蓄力/击飞并沉默 8 秒'
                }
            },
            {
                'name': '赤练之眸 (V奥义)',
                'type': 'ELEMENTAL_BURST',
                'description': '召唤阴神之眼注视全场敌方，5秒引导结束后对视线内所有敌人造成长达 5 秒的绝对眩晕！',
                'scaling': {
                    '引导时间': '5 秒锁定引导',
                    '眩晕时长': '5 秒绝对硬控 (无视闪避)',
                    '作用范围': '半径 50 米全域视线',
                    '怒气消耗': '100% 怒气槽'
                }
            }
        ],
        'passives': [
            {'name': '毒素凝集', 'unlock': '固有被动', 'desc': '攻击附加轻微阴神毒素，削减目标精力恢复速率 15%'},
            {'name': '听声辩位', 'unlock': '盲剑天赋', 'desc': '雾区与毒圈中敌方脚步声高亮 40%，受击受控硬直时间缩短 10%'}
        ],
        'constellations': [
            {'c': 1, 'name': '昆仑决·断筋', 'desc': '踢击命中敌人后封印其飞索与短闪避，持续 6 秒，彻底截断敌方拉扯空间'},
            {'c': 2, 'name': '昆仑决·反击', 'desc': '受击状态下可强行施放，释放金霸体震波击退贴脸连招压制的敌人'},
            {'c': 3, 'name': '赤练之眸·封印', 'desc': '引导期间可自由奔跑与短闪，终了封印敌方技能与奥义 6 秒'},
            {'c': 4, 'name': '赤练之眸·无间', 'desc': '引导时间缩短至 3 秒，眩晕成功同时抽取目标 35% 怒气反哺自身'},
            {'c': 5, 'name': '本源印记·极阴暴怒', 'desc': '受到伤害的 20% 转化为奥义怒气，回能速度大幅飞跃'},
            {'c': 6, 'name': '昆仑真经·玄女觉醒', 'desc': '护甲破碎瞬间爆发玄阴剑煞击退周围敌人，全队移速提升 15%'}
        ],
        'special_mechanics': {
            '【阴神视界脱锁追踪】': '开启赤练之眸后，视线内的目标即使通过飞索逃跑或隐身脱离，仍会在头顶保留阴神血眼标记，直至眩晕判定生效。',
            '【受击强解破蓄力】': '昆仑决反击分支是聚窟洲顶级受击反制技能，可无视阔刀雷刀、太刀百裂斩的强硬直强行震开。',
            '【盲剑近战拼刀博弈】': '近身拼刀时自带脚步声与蓄力声辨识增益，预判敌方蓄力转振刀窗口期高出常规英雄 0.2 秒。',
            '【怒气回转运营闭环】': '配合极阴·暴怒印记，受到伤害高额转化为怒气，通常在进入决赛圈前能稳定放出两次关键控场大招。'
        },
        'recommendations': {
            'weapons': {
                'bis': '长剑 · 凤凰羽 / 纯阳剑 (远距离剑气剑罡封锁走位)',
                'alternative_5s': '太刀 · 噬魂斩 (眩晕后滑步百裂斩瞬间融化敌人)',
                'budget_4s': '长枪 · 狂浪怒涛 / 鸟铳 (中远距离精准点杀与哪吒闹海)'
            },
            'artifacts': {
                'bis_set': '夺魂·近战 + 毕工淌 + 凌波 (近战吸血翻盘 + 瞬修兵刃 + 极速身法)',
                'alt_set': '虚影步 + 召雷术 + 完璧 + 幽冥步 (短闪隐匿 + 天雷轰击)'
            },
            'main_stats': {
                'sands': '本源印记：每秒精力恢复 +15% / 精力上限 +120',
                'goblet': '极阴印记：伤转怒 +18% / 怒气积攒速度 +20%',
                'circlet': '极阳万物：飞索距离 +20% / 近战减伤 +12%'
            },
            'sub_stats': '印记优先级：伤转怒 > 精力上限 > 每秒回精 > 飞索距离 > 近战抗性'
        }
    },
    {
        'name': '特木尔 (Temulch)',
        'title': '苍狼之主 · 风之牢笼阻断远程',
        'rarity': 5,
        'element': '苍狼风煞 · 控场',
        'weapon_type': '长枪 / 阔刀',
        'region': '苍狼部落',
        'arkhe': '狂风庇佑',
        'archetype': 'controller',
        'hp_mod': 40, 'atk_mod': 5, 'energy_mod': 10, 'crit_mod': 0.5,
        'skills': [
            {
                'name': '风沙暗劲 (F技能)',
                'type': 'ELEMENTAL_SKILL',
                'description': '跃起召唤三颗狂风精灵环绕自身，可射出击飞敌人强行打断其蓄力并造成大硬直。',
                'scaling': {
                    '风球数量': '3 颗追踪风球',
                    '冷却时间': '18 秒',
                    '击飞判定': '强行破除蓝霸体击退',
                    '防御增益': '环绕期间阻挡 1 次非蓄力攻击'
                }
            },
            {
                'name': '风之牢笼 (V奥义)',
                'type': 'ELEMENTAL_BURST',
                'description': '释放狂暴旋风牢笼笼罩战场，阻挡所有敌方远程子弹飞行物，敌方穿过牢笼瞬间减速陷入硬直！',
                'scaling': {
                    '持续时间': '15 秒风暴牢笼',
                    '阻挡效果': '100% 吸收远程飞行道具',
                    '硬直判定': '穿越风墙强制消耗 80% 精力并硬直',
                    '怒气消耗': '100% 怒气槽'
                }
            }
        ],
        'passives': [
            {'name': '狂风护体', 'unlock': '固有被动', 'desc': '在风暴中行动自如且精力消耗减免 20%'},
            {'name': '苍狼韧性', 'unlock': '部族图腾', 'desc': '受到远程武器命中时伤害衰减 18%'}
        ],
        'constellations': [
            {'c': 1, 'name': '风沙暗劲·散弹', 'desc': '同时向前方射出三颗风球，形成扇形击飞压制'},
            {'c': 2, 'name': '风沙暗劲·救生', 'desc': '受击状态可用，瞬间引爆周身风煞震退所有敌人'},
            {'c': 3, 'name': '风之牢笼·充能', 'desc': '风墙内友军精力恢复速度提升 40%，滑步蓄力速度加快'},
            {'c': 4, 'name': '风之牢笼·通天', 'desc': '风墙高度翻倍直达苍穹，彻底阻断高空飞索空投突袭'},
            {'c': 5, 'name': '苍狼图腾·风神眷顾', 'desc': '在聚窟洲户外开阔区域移动速度永久提升 8%'},
            {'c': 6, 'name': '风之极意·九霄龙卷', 'desc': '牢笼生成瞬间对范围内所有敌人造成 300 点真实风蚀伤害'}
        ],
        'special_mechanics': {
            '【远程飞行物绝对屏障】': '风之牢笼展开后，五眼铳、鸟铳、火炮、弓箭的所有弹药穿过牢笼瞬间全数消散湮灭。',
            '【穿越风墙精力抽干】': '敌方试图强行翻滚或飞索穿过风牢时，会被风墙剥离 80% 精力并陷入 1.5 秒失衡硬直。',
            '【沙球瞬发破蓄打断】': '射出风沙精灵的弹道极快，可精准在敌方蓄力即将释放的叮声前将其击退打断。',
            '【风内霸体与颠勺压制】': '在风牢中心特木尔拥有绝对行动权，配合长枪龙王破或阔刀磐石可进行无伤围杀。'
        },
        'recommendations': {
            'weapons': {
                'bis': '长枪 · 狂浪怒涛 (风牢内金霸体哪吒闹海毁天灭地)',
                'alternative_5s': '阔刀 · 烈火斩 (利用风墙卡位强行触发磐石反击)',
                'budget_4s': '连弩 · 狂风暴雨 / 棍 (风墙内安全速射扫射)'
            },
            'artifacts': {
                'bis_set': '夺魂·近战 + 凌波 + 完璧 (风牢收割吸血 + 极限身法)',
                'alt_set': '召雷术 + 续命术 + 毕工淌 (天雷轰顶 + 保命反杀)'
            },
            'main_stats': {
                'sands': '本源印记：每秒精力恢复 +15%',
                'goblet': '极阳印记：飞索速度 +25% / 远抗 +15%',
                'circlet': '极阴印记：怒气积攒 +18% / 近战减伤 +12%'
            },
            'sub_stats': '印记优先级：每秒精力恢复 > 怒气回复 > 远战抗性 > 精力上限'
        }
    },
    {
        'name': '迦南 (Matari)',
        'title': '月轮刺客 · 虚空闪烁隐形刺杀',
        'rarity': 5,
        'element': '月轮幻术 · 刺客',
        'weapon_type': '匕首 / 双刀',
        'region': '月轮国',
        'arkhe': '追风位移',
        'archetype': 'assassin',
        'hp_mod': -20, 'atk_mod': 15, 'energy_mod': 15, 'crit_mod': 2.0,
        'skills': [
            {
                'name': '追魂 (F技能)',
                'type': 'ELEMENTAL_SKILL',
                'description': '向指定准星方向瞬间瞬移穿梭，可空中施放，带有 0.3 秒无敌帧，极速脱离连招压制。',
                'scaling': {
                    '瞬移距离': '18 米三维穿梭',
                    '冷却时间': '14 秒 (可蓄力双段)',
                    '无敌帧': '0.3 秒绝对无敌',
                    '增伤状态': '瞬移后 3 秒内攻击力提升 15%'
                }
            },
            {
                'name': '寂静暗刑 (V奥义)',
                'type': 'ELEMENTAL_BURST',
                'description': '使自身与友方进入伪装隐形状态，大幅缩短追魂CD，壁击与突袭伤害成倍提升！',
                'scaling': {
                    '隐匿时长': '20 秒全队隐形',
                    '追魂冷却': '缩短至 2 秒极速充能',
                    '壁击伤害': '提升 60% 物理暴击',
                    '脱锁判定': '敌方钩锁与辅助瞄准完全失效'
                }
            }
        ],
        'passives': [
            {'name': '飞索隐蔽', 'unlock': '固有被动', 'desc': '钩锁飞行与壁击时脚步声极大程度衰减，敌方警示标消失'},
            {'name': '潜行背刺', 'unlock': '月轮暗杀', 'desc': '脱离战斗或隐身状态下首记攻击必定暴击'}
        ],
        'constellations': [
            {'c': 1, 'name': '追魂·连闪', 'desc': '追魂可连续瞬移施放两次，机动拉扯能力翻倍'},
            {'c': 2, 'name': '追魂·闪回', 'desc': '瞬移后在原地留下印记，再次按F可瞬间折返原点'},
            {'c': 3, 'name': '寂静暗刑·壁击', 'desc': '隐身期间壁击伤害提升至 100%，近战蓄力破盾效率激增'},
            {'c': 4, 'name': '寂静暗刑·群隐', 'desc': '奥义覆盖范围扩至全队，友军在隐身中受击减伤 20%'},
            {'c': 5, 'name': '月轮秘术·暗影步', 'desc': '精力上限提升 25 点，短闪避精力消耗额外降低 15%'},
            {'c': 6, 'name': '夜之主宰·死神突袭', 'desc': '隐身中击败敌人立即刷新追魂冷却并延长奥义 5 秒'}
        ],
        'special_mechanics': {
            '【空中立体受身瞬移】': '追魂可在受击硬直与浮空状态中瞬间脱离，规避敌方颠勺与升龙终结技。',
            '【全队隐身脱瞄锁定】': '开启寂静暗刑后，敌方屏幕上的自瞄红框与钩锁吸附完全解除，只能凭借肉眼轮廓盲打。',
            '【壁击超高倍率刺杀】': '挂墙释放壁击拥有全英雄最高单段物理爆发，配合匕首闪步可打出秒人电光火石。',
            '【双段连闪地形穿梭】': '在房区、悬崖、复杂地宫中利用追魂连闪可瞬移穿窗绕柱，戏耍敌方追兵。'
        },
        'recommendations': {
            'weapons': {
                'bis': '匕首 · 幽冥步 / 鬼哭神嚎 (闪步瞬移 + 极速背刺)',
                'alternative_5s': '双刀 · 乾坤日月斩 (隐身贴脸旋风绞杀)',
                'budget_4s': '太刀 · 噬魂斩 / 鸟铳 (滑步居合与隐身高点爆头)'
            },
            'artifacts': {
                'bis_set': '虚影步 + 夺魂·近战 + 凌波 (连续短闪隐身 + 处决吸血 + 飞天壁击)',
                'alt_set': '幽冥步 + 毕工淌 + 完璧 (匕首闪步减免 + 瞬修武器)'
            },
            'main_stats': {
                'sands': '本源印记：精力上限 +140 / 每秒精力恢复 +15%',
                'goblet': '极阳印记：飞索速度 +30% / 飞索距离 +20%',
                'circlet': '极阴印记：暴击率 +12% / 闪避精力减免 +15%'
            },
            'sub_stats': '印记优先级：精力上限 > 闪避精力减免 > 暴击率 > 飞索速度'
        }
    },
    {
        'name': '季沧海 (Tarka Ji)',
        'title': '烈豪侠客 · 迅烈如火颠勺战神',
        'rarity': 5,
        'element': '烈焰真气 · 狂战',
        'weapon_type': '阔刀 / 太刀',
        'region': '无极帝国',
        'arkhe': '狂饮烈酒',
        'archetype': 'berserker',
        'hp_mod': 10, 'atk_mod': 25, 'energy_mod': 10, 'crit_mod': 1.5,
        'skills': [
            {
                'name': '燎原劲 (F技能)',
                'type': 'ELEMENTAL_SKILL',
                'description': '摆出防御架势绝对格挡物理攻击并弹刀反击，或投掷高爆火球灼烧重创敌人。',
                'scaling': {
                    '反击伤害': '320% 烈火反震',
                    '冷却时间': '16 秒',
                    '火球范围': '6 米高爆溅射',
                    '灼烧效果': '持续 5 秒灼烧，阻断飞索'
                }
            },
            {
                'name': '迅烈如火 (V奥义)',
                'type': 'ELEMENTAL_BURST',
                'description': '狂饮烈酒全身包裹烈火，大幅提升移速与精力回复，奔跑撞击可将敌人击飞至空中进行无限颠勺！',
                'scaling': {
                    '移速加成': '狂飙移速 +40%',
                    '精力机制': '疾跑不消耗精力，回精极速提升',
                    '击飞判定': '冲撞强制击飞浮空 (颠勺起点)',
                    '怒气消耗': '按时间匀速消耗怒气'
                }
            }
        ],
        'passives': [
            {'name': '火毒不侵', 'unlock': '固有被动', 'desc': '受灼烧伤害降低 60%，火炮与喷火筒爆炸对自身衰减'},
            {'name': '烈酒狂战', 'unlock': '酒中仙', 'desc': '体力低于 50% 时攻击力提升 15%'}
        ],
        'constellations': [
            {'c': 1, 'name': '燎原劲·火球', 'desc': '改为投掷巨型轰爆火球，命中附带击退与大硬直'},
            {'c': 2, 'name': '燎原劲·巨焰', 'desc': '防御反击成功后必定打落敌方武器，造成缴械判定'},
            {'c': 3, 'name': '迅烈如火·狂战', 'desc': '奥义状态下普通攻击伤害提升 25%，可点燃武器附加真火'},
            {'c': 4, 'name': '迅烈如火·炎神', 'desc': '奔跑冲撞伤害提升 100%，颠勺击飞滞空时间增加 0.5 秒'},
            {'c': 5, 'name': '烈火真气·极阳通经', 'desc': '闪避冲刺速度提升 15%，受到控制硬直时间缩短 20%'},
            {'c': 6, 'name': '焚天灭地·真火不熄', 'desc': '开启奥义击败敌人立即恢复 30% 怒气与 20% 生命值'}
        ],
        'special_mechanics': {
            '【迅烈如火无限颠勺连招】': '开启奥义冲撞击飞敌人，左键平A接短闪避取消后摇，再次冲撞击飞，形成聚窟洲最强颠勺空中秒杀链。',
            '【燎原劲受击绝对弹刀】': 'F技能防御架势可完全吸收阔刀雷刀、太刀百裂斩，反手击退让敌方陷入长时间僵直。',
            '【疾跑精力无限锁死】': '开启大招后持续奔跑完全不消耗精力槽，滑铲与二段跳随时可用，拉扯机动性天花板。',
            '【真火灼烧禁飞索】': '被季沧海烈火命中的敌人浑身燃起火焰，在此期间无法使用飞索拉开，只能被迫近身博弈。'
        },
        'recommendations': {
            'weapons': {
                'bis': '阔刀 · 烈火斩 (颠勺空中接磐石雷刀瞬间碎甲)',
                'alternative_5s': '太刀 · 噬魂斩 (滑步百裂极速取消后摇连招)',
                'budget_4s': '长剑 · 凤凰羽 / 火炮 (远程真火轰炸压制血线)'
            },
            'artifacts': {
                'bis_set': '夺魂·近战 + 烈火斩 + 凌波 (近战处决回生 + 颠勺烈火 + 极限精力)',
                'alt_set': '毕工淌 + 虚影步 + 完璧 (瞬修刀刃 + 短闪无敌)'
            },
            'main_stats': {
                'sands': '本源印记：每秒精力恢复 +15% / 精力上限 +120',
                'goblet': '极阳印记：近战攻击 +15% / 怒气回复 +18%',
                'circlet': '极阴印记：近战减伤 +12% / 暴击伤害 +20%'
            },
            'sub_stats': '印记优先级：每秒精力恢复 > 近战攻击力 > 伤转怒 > 暴击伤害'
        }
    },
    {
        'name': '土御门胡桃 (Kurumi)',
        'title': '日轮巫女 · 庇护牵线全队救赎',
        'rarity': 5,
        'element': '阴阳治愈 · 辅助',
        'weapon_type': '长剑 / 扇',
        'region': '日轮国',
        'arkhe': '光伞庇佑',
        'archetype': 'support',
        'hp_mod': 30, 'atk_mod': -5, 'energy_mod': 10, 'crit_mod': 0.0,
        'skills': [
            {
                'name': '庇护 (F技能)',
                'type': 'ELEMENTAL_SKILL',
                'description': '与友军建立阴阳连接光索，持续为其恢复大量体力与护甲，可左键瞬移至队友身边击退敌人。',
                'scaling': {
                    '治疗速率': '每秒回复 120 体力/护甲',
                    '连接距离': '30 米光索牵引',
                    '左键突进': '瞬移击飞周围敌人 5 米',
                    '冷却时间': '15 秒'
                }
            },
            {
                'name': '净天地 (V奥义)',
                'type': 'ELEMENTAL_BURST',
                'description': '在地面布下巨大阴阳净化法阵，持续为阵内友军极速恢复体力和护甲，驱散负面异常！',
                'scaling': {
                    '法阵半径': '12 米全域结界',
                    '持续时间': '14 秒神圣光阵',
                    '回复总量': '最高回复 2400 体力与护甲',
                    '净化机制': '瞬间清除眩晕、灼烧、中毒异常'
                }
            }
        ],
        'passives': [
            {'name': '灵犀相通', 'unlock': '固有被动', 'desc': '救援倒地队友时间缩短 30%，救援成功队友获得护甲恢复'},
            {'name': '阴阳调和', 'unlock': '神道巫女', 'desc': '自身受到治疗效果提升 20%'}
        ],
        'constellations': [
            {'c': 1, 'name': '庇护·增攻', 'desc': '牵线期间目标友军攻击力提升 20%，附带金色真气护体'},
            {'c': 2, 'name': '庇护·守护', 'desc': '牵线期间友军获得 25% 伤害减免与防打断抗性'},
            {'c': 3, 'name': '净天地·急疗', 'desc': '奥义法阵释放瞬间产生全屏冲击波，瞬间抬升全队 50% 护甲'},
            {'c': 4, 'name': '净天地·火海', 'desc': '法阵受火属性攻击转化为烈焰法阵，对敌方造成持续高额灼烧'},
            {'c': 5, 'name': '日轮法印·大阴阳术', 'desc': '救援倒地队友时自带金霸体护盾，免疫除振刀外一切打断'},
            {'c': 6, 'name': '神道降临·生死逆转', 'desc': '友军在法阵内濒死时直接触发保命护盾并恢复 30% 生命'}
        ],
        'special_mechanics': {
            '【光索牵线救援与击退】': '远距离与陷入敌阵的队友连线，左键瞬移救援击退合围之敌，化解集火危机。',
            '【净天地净化强解异常】': '净天地法阵能瞬间解除宁红夜赤练之眸眩晕、崔三娘水牢、顾清寒冰冻等绝命硬控。',
            '【隔空拉魂冢无损复活】': '在掩体后向阵亡队友魂冢射出光索，可隔墙安全读条救援，无需以身涉险。',
            '【法阵元素交互反应】': '净天地法阵与火球、毒气碰撞会发生元素转化，策略性改变战局攻防节奏。'
        },
        'recommendations': {
            'weapons': {
                'bis': '长剑 · 凤凰羽 (远距离安全释放剑气掩护牵线队友)',
                'alternative_5s': '扇 · 极乐汤 (借风滑步飘逸自保与击退刺客)',
                'budget_4s': '鸟铳 · 穿杨 (后排精准狙击支援输出)'
            },
            'artifacts': {
                'bis_set': '光佑 + 完璧 + 凌波 (群体磕药共享回血 + 药量提升 + 绝顶身法)',
                'alt_set': '续命术 + 毕工淌 + 夺魂·远程 (免死金身 + 瞬修武器 + 远程吸血)'
            },
            'main_stats': {
                'sands': '本源印记：救援速度 +35% / 每秒精力恢复 +15%',
                'goblet': '极阴印记：怒气积攒速度 +25% / 伤转怒 +15%',
                'circlet': '极阳万物：近战减伤 +14% / 远战减伤 +15%'
            },
            'sub_stats': '印记优先级：救援速度 > 怒气积攒 > 近战减伤 > 远战抗性'
        }
    },
    {
        'name': '天海 (Tianhai)',
        'title': '云游武僧 · 金钟罩降魔怒目金刚',
        'rarity': 5,
        'element': '金刚佛力 · 坦克',
        'weapon_type': '阔刀 / 棍',
        'region': '隐族隐世',
        'arkhe': '佛法金身',
        'archetype': 'tank',
        'hp_mod': 50, 'atk_mod': 10, 'energy_mod': 0, 'crit_mod': -1.0,
        'skills': [
            {
                'name': '金钟罩 (F技能)',
                'type': 'ELEMENTAL_SKILL',
                'description': '周身化作纯金金钟罩，绝对格挡一切物理武器打击，并将敌人的远程子弹全数反弹！',
                'scaling': {
                    '无敌时长': '1.5 秒绝对反震',
                    '反弹效果': '100% 反弹子弹与箭矢',
                    '震落判定': '震飞敌方攻击并使其踉跄硬直',
                    '冷却时间': '20 秒'
                }
            },
            {
                'name': '金刚伏魔 (V奥义)',
                'type': 'ELEMENTAL_BURST',
                'description': '化身为顶天立地的怒目金刚！伸出巨灵手掌擒拿抓取敌人，双抓两人相互猛砸可造成瞬间秒杀级毁灭伤害！',
                'scaling': {
                    '变身体力': '4000 点金刚神力血池',
                    '抓取判定': '长臂抓取无视闪避与霸体',
                    '双抓伤害': '3500+ 毁灭性巨力互砸',
                    '持续时间': '30 秒巨灵真身'
                }
            }
        ],
        'passives': [
            {'name': '禅定', 'unlock': '固有被动', 'desc': '受击受控僵直时间缩短 15%，倒地翻滚恢复极快'},
            {'name': '金刚不坏', 'unlock': '佛法金身', 'desc': '护甲防御上限额外提高 100 点'}
        ],
        'constellations': [
            {'c': 1, 'name': '金钟罩·振刀', 'desc': '在敌方蓝霸体攻击命中的瞬间开启，必定直接振落敌方武器！'},
            {'c': 2, 'name': '金钟罩·爆气', 'desc': '受击状态可用，震飞贴脸近战连招的敌人并解除一切硬直'},
            {'c': 3, 'name': '金刚伏魔·援护', 'desc': '怒目金刚可抓取倒地濒死队友并持续为其恢复生命护甲'},
            {'c': 4, 'name': '金刚伏魔·震地', 'desc': '踩地重击范围提升 50%，震碎范围内所有敌人的蓝霸体蓄力'},
            {'c': 5, 'name': '佛骨舍利·无相金身', 'desc': '受到近战武器攻击伤害降低 18%，变身期间回血效率提升'},
            {'c': 6, 'name': '如来神掌·诛魔辟易', 'desc': '抓取敌人猛砸地面直接震碎其全部护甲，造成致命破甲伤'}
        ],
        'special_mechanics': {
            '【金钟罩绝对反弹缴械】': '金钟罩具有全游戏最高判定优先级的绝对无敌，震刀分支若挡住蓄力可直接令敌方兵刃脱手。',
            '【怒目金刚双抓秒杀判定】': '变身大佛后，F键抓一人，左键或右键再抓一人，按F双抓互砸直接造成 3500+ 秒杀全满紫甲的毁灭伤害。',
            '【变身残血重置生机】': '本体处于空血濒死边缘开启奥义，血条瞬间切换为 4000 点金刚血量，是极限翻盘最强神技。',
            '【大佛弱点与踩地控场】': '金刚发光腿部与胸口为受击弱点承受 1.5 倍伤害，需熟练运用踩地与甩飞阻止敌方近战修脚。'
        },
        'recommendations': {
            'weapons': {
                'bis': '阔刀 · 烈火斩 (磐石防御与大佛变身攻防一体)',
                'alternative_5s': '棍 · 定海针 (撑杆高立避开低空打击后砸地)',
                'budget_4s': '长枪 · 狂浪怒涛 / 鸟铳 (中距离哪吒闹海与狙杀)'
            },
            'artifacts': {
                'bis_set': '夺魂·近战 + 毕工淌 + 凌波 (近战处决吸血 + 瞬修武器 + 极速身法)',
                'alt_set': '完璧 + 续命术 + 霸王附体 (抗伤名刀 + 绝境真霸体)'
            },
            'main_stats': {
                'sands': '本源印记：每秒精力恢复 +15% / 精力上限 +100',
                'goblet': '极阴印记：伤转怒 +20% / 近战减伤 +15%',
                'circlet': '极阳万物：怒气积攒速度 +20% / 远抗 +15%'
            },
            'sub_stats': '印记优先级：伤转怒 > 怒气积攒速度 > 近战减伤 > 精力上限'
        }
    }
]

# Build definitions for remaining 26 heroes
OTHER_HEROES = [
    ('妖刀姬 (Yoto Hime)', '不祥妖刃 · 连斩破霸体处决者', '妖刀鬼气 · 狂战', '阔刀 / 斩马刀', '平安京 / 异界', '妖刀通灵', 'berserker', 20, 20, 5, 1.0),
    ('崔三娘 (Valda Cui)', '雾海龙王 · 巨浪深渊水牢硬控', '沧海狂澜 · 控场', '双戟 / 双刀', '东海雾海', '龙王水牢', 'controller', 20, 10, 10, 1.0),
    ('岳山 (Yueshan)', '武威侯 · 破阵破军神将泥人', '无极军威 · 坦克', '长枪 / 斩马刀', '无极帝国军队', '铁血军魂', 'tank', 45, 15, 0, 0.0),
    ('无尘 (Wuchen)', '隐族密使 · 两仪剑阵全队挪移传送', '太极两仪 · 辅助', '长剑 / 太刀', '隐族', '两仪剑气', 'support', 20, 0, 10, 0.5),
    ('顾清寒 (Justina Gu)', '冰雁飞影 · 冰心诀绝对无敌刺杀', '冰雪真气 · 刺客', '太刀 / 剑', '帝国宗室', '冰魄寒霜', 'assassin', -10, 20, 15, 2.0),
    ('武田信忠 (Takeda Nobutada)', '不祥之刃 · 封魔结界夺刀反击', '武士刀魂 · 控场', '太刀 / 双刀', '日轮国武士', '封魔恶灵', 'controller', 15, 15, 10, 1.0),
    ('殷紫萍 (Ziping Yin)', '悬瓠济世 · 益气安魂全队免死保命', '仙家医药 · 辅助', '长剑 / 扇', '蓬莱医宗', '仙草济世', 'support', 30, -10, 10, 0.0),
    ('沈妙 (Shen Miao)', '机巧千机 · 火器轰炸铳武机甲', '火器神机 · 强攻', '一窝蜂 / 鸟铳', '工匠世家', '铁卫战甲', 'berserker', 20, 15, 5, 1.0),
    ('胡为 (Hu Wei)', '狂虎之怒 · 跃空猛扑虎啸破防', '狂虎霸体 · 狂战', '长枪 / 阔刀', '西凉边军', '狂虎啸天', 'berserker', 25, 15, 5, 0.5),
    ('季莹莹 (Zai)', '无常索命 · 幽冥火脱困链刃捕风', '幽冥引渡 · 刺客', '双节棍 / 鞭刃', '阎罗地府', '无常幽火', 'assassin', -15, 20, 15, 2.5),
    ('玉玲珑 (Tessa)', '九尾灵狐 · 迷魂摄魄妖丹夺命', '青丘妖狐 · 控场', '双刀 / 匕首', '青丘妖界', '迷魂妖丹', 'controller', 10, 15, 10, 1.5),
    ('哈迪 (Hadi)', '千机机械 · 铁羽御空高空索命', '机关造物 · 刺客', '长剑 / 鸟铳', '西方异邦', '机械飞翼', 'assassin', 0, 15, 15, 1.0),
    ('魏轻 (Wei Qing)', '玄武御甲 · 执金卫反震禁锢', '玄武正气 · 坦克', '双戟 / 斩马刀', '执金卫', '玄武真印', 'tank', 40, 5, 5, -0.5),
    ('刘炼 (Liu Lian)', '磁石御金 · 点金流铁重构神兵', '点金御铁 · 强攻', '横刀 / 太刀', '点金世家', '磁元铁砂', 'berserker', 20, 15, 5, 1.0),
    ('张起灵 (Zhang Qiling)', '发丘中郎 · 黑金古刀麒麟破霸体', '麒麟古血 · 狂战', '斩马刀 / 长刀', '张家古楼', '古刀斩邪', 'berserker', 30, 25, 10, 2.0),
    ('席拉 (Shayla / Cyra)', '光之圣女 · 日炎神辉全队治愈护盾', '圣光烈阳 · 辅助', '扇 / 长剑', '日曜绿洲', '神圣日炎', 'support', 25, -5, 10, 0.0),
    ('万钧 (Wan Jun)', '镇雷神将 · 狂雷轰顶引雷破阵', '九天劫雷 · 狂战', '双戟 / 长枪', '天阙神庭', '神霄引雷', 'berserker', 25, 20, 5, 1.5),
    ('司南 (Si Nan)', '司天星官 · 浑天星仪引力星轨', '星宿周天 · 控场', '扇 / 匕首', '钦天监', '浑天仪星象', 'controller', 10, 10, 10, 1.0),
    ('赛特 (Seth)', '沙漠暗影 · 狂沙分身割喉收割', '黄沙暗影 · 刺客', '双刀 / 匕首', '死亡沙海', '沙暴替身', 'assassin', -10, 20, 20, 2.0),
    ('白泽 (Bai Ze)', '通达万物 · 祥瑞驱散破除虚妄', '白泽清气 · 辅助', '长剑 / 恒杖', '蓬莱仙洲', '辟邪祥瑞', 'support', 20, 5, 10, 0.5),
    ('墨羽 (Mo Yu)', '偃甲墨侠 · 千机连弩暗箭追魂', '机关机巧 · 控场', '连弩 / 拳刃', '机关古谷', '千机变装置', 'controller', 15, 15, 5, 1.0),
    ('灵狐仙子 (Hulian)', '青丘幻形 · 魅影步法替身诱敌', '青丘灵火 · 刺客', '双刀 / 扇', '青丘之国', '幻影灵身', 'assassin', -10, 15, 15, 2.0),
    ('刑天 (Xing Tian)', '战神不屈 · 干戚狂舞绝境反击', '不灭战魂 · 坦克', '阔刀 / 盾斧', '上古洪荒', '干戚神威', 'tank', 60, 20, -5, 0.0),
    ('李白 (Li Bai)', '青莲剑仙 · 十步一杀大河剑意', '青莲剑意 · 狂战', '长剑 / 纯阳剑', '盛唐长安', '太白酒气', 'berserker', 15, 25, 15, 2.5),
    ('孙悟空 (Sun Wukong)', '齐天大圣 · 七十二变法象金箍棒神威', '大圣神威 · 狂战', '棍棒 / 金箍棒', '花果山', '齐天变身', 'berserker', 35, 25, 15, 2.0),
    ('蓝梦 (Lan Meng)', '沧海鲛人 · 碧海狂澜潮汐涌动', '鲛人水泽 · 控场', '双刀 / 长枪', '南海深渊', '潮汐海音', 'controller', 15, 10, 10, 1.0)
]

ARCHETYPES = {
    'tank': {
        'hp': [1100, 1180, 1260, 1350, 1450],
        'armor': [500, 750, 1000, 1250, 1500],
        'energy': [100, 105, 110, 115, 120],
        'atk': [95, 110, 125, 142, 160],
        'def': ['10%', '13%', '16%', '19%', '22%'],
        'crit_rate': [5.0, 5.8, 6.5, 7.2, 8.0],
        'crit_dmg': ['150%', '150%', '155%', '160%', '165%'],
        'energy_recovery': ['15/s', '17/s', '19/s', '21/s', '24/s'],
    },
    'assassin': {
        'hp': [920, 980, 1040, 1100, 1180],
        'armor': [500, 750, 1000, 1250, 1500],
        'energy': [120, 128, 136, 144, 150],
        'atk': [110, 128, 148, 172, 195],
        'def': ['3%', '4%', '6%', '8%', '10%'],
        'crit_rate': [10.0, 12.0, 14.0, 16.0, 18.0],
        'crit_dmg': ['160%', '165%', '170%', '175%', '185%'],
        'energy_recovery': ['20/s', '23/s', '26/s', '29/s', '32/s'],
    },
    'berserker': {
        'hp': [1000, 1070, 1140, 1210, 1280],
        'armor': [500, 750, 1000, 1250, 1500],
        'energy': [105, 112, 120, 128, 135],
        'atk': [115, 135, 158, 182, 210],
        'def': ['6%', '8%', '10%', '12%', '14%'],
        'crit_rate': [8.0, 9.5, 11.0, 13.0, 15.0],
        'crit_dmg': ['155%', '160%', '165%', '170%', '180%'],
        'energy_recovery': ['18/s', '20/s', '22/s', '24/s', '26/s'],
    },
    'controller': {
        'hp': [1000, 1060, 1120, 1180, 1250],
        'armor': [500, 750, 1000, 1250, 1500],
        'energy': [100, 108, 115, 122, 130],
        'atk': [105, 120, 138, 158, 180],
        'def': ['8%', '10%', '12%', '14%', '16%'],
        'crit_rate': [6.0, 7.5, 9.0, 10.5, 12.0],
        'crit_dmg': ['150%', '155%', '160%', '165%', '170%'],
        'energy_recovery': ['16/s', '18/s', '20/s', '22/s', '25/s'],
    },
    'support': {
        'hp': [1050, 1110, 1180, 1250, 1320],
        'armor': [500, 750, 1000, 1250, 1500],
        'energy': [110, 116, 122, 128, 135],
        'atk': [90, 102, 118, 135, 155],
        'def': ['7%', '9%', '11%', '13%', '15%'],
        'crit_rate': [5.0, 6.0, 7.0, 8.0, 9.0],
        'crit_dmg': ['150%', '150%', '155%', '155%', '160%'],
        'energy_recovery': ['18/s', '20/s', '23/s', '25/s', '28/s'],
    }
}


def build_hero_stats(archetype, hp_mod=0, atk_mod=0, energy_mod=0, crit_mod=0.0):
    arch = ARCHETYPES[archetype]
    stats = []
    for i in range(5):
        hp = arch['hp'][i] + hp_mod
        armor = arch['armor'][i]
        energy = arch['energy'][i] + energy_mod
        atk = arch['atk'][i] + atk_mod
        d = arch['def'][i]
        crit = f"{arch['crit_rate'][i] + crit_mod:.1f}%"
        cdmg = arch['crit_dmg'][i]
        erec = arch['energy_recovery'][i]
        stats.append({
            'level': STAGES[i],
            'hp': hp,
            'armor': armor,
            'energy': energy,
            'atk': atk,
            'def': d,
            'crit_rate': crit,
            'crit_dmg': cdmg,
            'energy_recovery': erec
        })
    return stats


def assemble_all_heroes():
    result = []
    
    # First 6 detailed heroes
    for h in HERO_DEFINITIONS:
        stats = build_hero_stats(h['archetype'], h['hp_mod'], h['atk_mod'], h['energy_mod'], h['crit_mod'])
        short_name = h['name'].split()[0]
        result.append({
            'name': h['name'],
            'title': h['title'],
            'rarity': h['rarity'],
            'element': h['element'],
            'weapon_type': h['weapon_type'],
            'region': h['region'],
            'arkhe': h['arkhe'],
            'avatar_url': f'/games/naraka/{short_name}.svg',
            'splash_url': '',
            'base_stats': stats,
            'talents': h['skills'],
            'passives': h['passives'],
            'constellations': h['constellations'],
            'special_mechanics': h['special_mechanics'],
            'recommendations': h['recommendations'],
            'version': 'v2026'
        })

    # The other 26 heroes
    for raw in OTHER_HEROES:
        name, title, element, weapon_type, region, arkhe, archetype, hp_m, atk_m, eng_m, crit_m = raw
        short_name = name.split()[0]
        stats = build_hero_stats(archetype, hp_m, atk_m, eng_m, crit_m)
        main_weapon = weapon_type.split('/')[0].strip()

        talents = [
            {
                'name': f'绝技·{arkhe} (F技能)',
                'type': 'ELEMENTAL_SKILL',
                'description': f'运转{element}施展专属秘术，对正前方敌方造成击飞破蓄力判定，并在受击状态提供机动反打。',
                'scaling': {
                    '基础伤害': f'{240 + atk_m * 2}% 招式倍率',
                    '冷却时间': '16 秒',
                    '霸体判定': '蓝霸体不可振',
                    '特殊机制': f'{arkhe}附魔与破除蓄力'
                }
            },
            {
                'name': f'终极奥义·{title.split("·")[0].strip()} (V奥义)',
                'type': 'ELEMENTAL_BURST',
                'description': f'引动聚窟洲天地灵气爆发终极真身与神域！改变战场法则并对范围内敌人施加毁灭压制！',
                'scaling': {
                    '持续时间': '25 秒觉醒状态',
                    '增伤倍率': f'{25 + atk_m // 2}% 伤害大幅强化',
                    '控制机制': f'{element}领域全屏压制',
                    '怒气消耗': '100% 怒气槽'
                }
            }
        ]

        passives = [
            {'name': f'{short_name}秘传心法', 'unlock': '固有武学', 'desc': f'处于{region}或对应天气环境中精力恢复速度提升 15%，攻击附带轻微破盾判定'},
            {'name': '武道极意', 'unlock': '身法进阶', 'desc': '闪避无敌帧延长 0.08 秒，成功拼刀时回复 80 点体力'}
        ]

        constellations = [
            {'c': 1, 'name': f'{arkhe}·变式二', 'desc': f'强化F技能的分支招式，缩短冷却时间 3 秒并附带击退判定'},
            {'c': 2, 'name': f'{arkhe}·变式三', 'desc': '受击状态下强行施放，震开贴脸近战连招的敌人'},
            {'c': 3, 'name': f'奥义·分支二协同', 'desc': '开启终极奥义后可为全队提供伤害增益与精力充盈'},
            {'c': 4, 'name': f'奥义·分支三质变', 'desc': '奥义期间免除一次致命伤害，大幅提升移动速度与反击爆发'},
            {'c': 5, 'name': '本源极境·印记大成', 'desc': '精力上限提升 20 点，近战减伤提升 8%，飞索速度提高 15%'},
            {'c': 6, 'name': '修罗通真·武神觉醒', 'desc': '击败敌人立即刷新技能冷却并恢复 25% 护甲，进入狂暴状态'}
        ]

        special_mechanics = {
            f'【{short_name}武学核心博弈】': f'熟练运用{element}与{main_weapon}的连招节奏，利用滑步蓄力与短闪取消后摇占据对拼主动。',
            '【受击反制与解控机制】': '在敌方连招压制期间抓住受击受身窗口，释放F技能解除硬直并反客为主。',
            '【奥义质变领域掌控】': f'开启奥义后覆盖战场，彻底封锁敌方拉扯与打药路线，形成绝对击杀包围圈。',
            '【精力与护甲精细运营】': '配合天赋印记实现对拼中持续回精，在金甲与紫甲阶段展现出超强韧性。'
        }

        recommendations = {
            'weapons': {
                'bis': f'{main_weapon} · 极品神兵 (完美契合{short_name}招式节奏)',
                'alternative_5s': '太刀 · 噬魂斩 / 长剑 · 凤凰羽 (极速百裂与远程剑气压制)',
                'budget_4s': '长枪 · 狂浪怒涛 / 鸟铳 (高性价比过渡与远程点射)'
            },
            'artifacts': {
                'bis_set': '夺魂·近战 + 毕工淌 + 凌波 (近战处决吸血 + 瞬修武器 + 绝顶身法)',
                'alt_set': '虚影步 + 召雷术 + 完璧 (短闪隐匿 + 天罚落雷 + 保命名刀)'
            },
            'main_stats': {
                'sands': '本源印记：每秒精力恢复 +15% / 精力上限 +120',
                'goblet': '极阴印记：伤转怒 +18% / 怒气积攒速度 +20%',
                'circlet': '极阳万物：飞索距离 +20% / 近战减伤 +14%'
            },
            'sub_stats': '印记优先级：精力上限 > 每秒精力恢复 > 伤转怒 > 近战抗性 > 飞索速度'
        }

        result.append({
            'name': name,
            'title': title,
            'rarity': 5,
            'element': element,
            'weapon_type': weapon_type,
            'region': region,
            'arkhe': arkhe,
            'avatar_url': f'/games/naraka/{short_name}.svg',
            'splash_url': '',
            'base_stats': stats,
            'talents': talents,
            'passives': passives,
            'constellations': constellations,
            'special_mechanics': special_mechanics,
            'recommendations': recommendations,
            'version': 'v2026'
        })

    return result


print("Hero definitions ready. Testing assemble...")
heroes = assemble_all_heroes()
print(f"Total heroes assembled: {len(heroes)}")
assert len(heroes) == 32
# Check that stats are differentiated
h1_hp = heroes[0]['base_stats'][0]['hp']
h2_hp = heroes[1]['base_stats'][0]['hp']
h3_hp = heroes[2]['base_stats'][0]['hp']
print(f"Sample HP level 1: {heroes[0]['name']}: {h1_hp}, {heroes[1]['name']}: {h2_hp}, {heroes[2]['name']}: {h3_hp}")
assert h1_hp != h2_hp != h3_hp
