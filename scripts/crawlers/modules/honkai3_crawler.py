"""
Honkai Impact 3rd (崩坏3) Comprehensive Battlesuits, PRI-ARMs, Stigmata & Combat Mechanics Crawler
Ingests Part 2 (第二部星环时代: 薇塔/花火/希娜狄雅/瑟莉姆/灯/松雀/德丽莎) & Part 1 Herrschers
(终焉/始源/真理/死生/人律/识宝/薪炎/天元骑英/月下誓约), signature PRI-ARMs, stigmata sets,
and deep combat mechanics (星环系统/星尘属性/量子虚数坍缩/时空断裂/伤害乘区) into Game 30 (崩坏3).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

BATTLESUITS = [
    # ------------------ 第二部：星环时代核心装甲 ------------------
    {
        'name': '薇塔 · 孑遗千星 (Vita - Lone Planetfarer)',
        'title': '孑遗千星 · 浩瀚星河全属性通辅兼星尘大C',
        'rarity': 5,
        'element': '星尘 · 闪电/全元素 (SD Lightning/Universal)',
        'weapon_type': '驱动核心 / 星环神权 (Drive Core)',
        'region': '星空深处 / 洛星',
        'arkhe': '星环之位：天垣眷礼 / 界域共鸣',
        'skills': [
            {'name': '分支 · 星穹幻化', 'type': 'ELEMENTAL_SKILL', 'scaling': '星空巨兽践踏/降维星轨', 'description': '消耗【星芒】驱动羽翼展开，召唤星空神兽撕裂虚空下踏，引发大范围星尘共鸣并粉碎敌方星尘硬壳！'},
            {'name': '必杀 · 孤宴，终归寂灭', 'type': 'ELEMENTAL_BURST', 'scaling': '孔雀羽化全屏星河轰炸', 'description': '激活星环爆发并展开浩瀚星河领域！孔雀神羽漫天飞旋，全队进入【天垣眷礼】连携共振，全元素穿透与全伤害加成直接拉满！'}
        ],
        'passives': [
            {'name': '全属性通辅', 'description': '开启星环爆发后，根据队伍主C属性自适应转化为冰/火/雷/物理最高档位辅助，为第二部绝对人权核心。'},
            {'name': '星尘主宰', 'description': '对星尘属性敌人额外造成 40% 独立伤害，击破星尘残核直接引爆全屏。'}
        ]
    },
    {
        'name': '花火 · 诡戏千役·友爱包容 (Sparkle)',
        'title': '假面愚者 · 量子火系物理双拐与战术换人',
        'rarity': 5,
        'element': '量子 · 火焰/物理辅助 (QUA Fire/Physical)',
        'weapon_type': '驱动核心 / 假面游艺 (Drive Core)',
        'region': '酒馆 / 崩铁联动',
        'arkhe': '星环之位：界域共鸣',
        'skills': [
            {'name': '分支 · 假面捉迷藏', 'type': 'ELEMENTAL_SKILL', 'scaling': '恶作剧替身/量子坍缩', 'description': '投掷红白恶作剧面具制造幻影，对量子属性敌人直接造成 1 次【量子坍缩】，瞬间削减量子护盾！'},
            {'name': '必杀 · 愚者的千面狂欢', 'type': 'ELEMENTAL_BURST', 'scaling': '全队战技点SP回复/无消耗切换', 'description': '展开奇幻游乐园舞台，全队立即回复 30 点SP，接下来的 15 秒内队友切换入场无CD且自动触发极速QTE！'}
        ],
        'passives': [
            {'name': '恶作剧之神', 'description': '全队暴击伤害提升 45%，火伤与物理伤害提升 35%，与第二部各星环队完美契合。'}
        ]
    },
    {
        'name': '希娜狄雅 · 深空定锚·曙光 (Senadina)',
        'title': '深空定锚 · 第二部星尘核心雷伤溜溜球',
        'rarity': 5,
        'element': '星尘 · 雷电伤害 (SD Lightning)',
        'weapon_type': '驱动核心 / 溜溜球 (Drive Core)',
        'region': '火星洛星 / 欧珀都市',
        'arkhe': '星环之位：界域共鸣',
        'skills': [
            {'name': '分支 · 定锚飞掷', 'type': 'ELEMENTAL_SKILL', 'scaling': '光速位移溜溜球连打', 'description': '将驱动溜溜球向敌人掷出并在半空极速瞬移穿梭，打出超高频率雷电风暴与聚怪'},
            {'name': '必杀 · 晨光破晓之时', 'type': 'ELEMENTAL_BURST', 'scaling': '星环爆发引爆星尘', 'description': '激活【界域共鸣】星环！召唤全队星环协同攻击，极速粉碎星尘属性敌人的硬壳残渣！'}
        ],
        'passives': [
            {'name': '星辰指引', 'description': '激活星环共鸣标记，全队角色攻击共鸣标记时触发额外高额连携雷伤倍率。'}
        ]
    },
    {
        'name': '瑟莉姆 · 享乐狂宴·邀影 (Thelema)',
        'title': '享乐狂宴 · 优雅链刃冰系大C',
        'rarity': 5,
        'element': '机械 · 冰冻伤害 (MECH Ice)',
        'weapon_type': '链刃 (Chained Blade)',
        'region': '琅丘',
        'arkhe': '星环之位：回影之召',
        'skills': [
            {'name': '分支 · 宴乐步法', 'type': 'ELEMENTAL_SKILL', 'scaling': '链刃横扫/积攒盛宴', 'description': '挥舞冰蓝链刃优雅横扫全屏，累积【宴饮】点数释放多重连续冰刺下劈'},
            {'name': '必杀 · 狂宴倾颓终章', 'type': 'ELEMENTAL_BURST', 'scaling': '冰晶王座粉碎斩', 'description': '召唤华丽盛宴王座将敌人拖入冰封深渊，随后一刃斩断万物造成巨额冰冻爆发伤害！'}
        ],
        'passives': [
            {'name': '女王的支配', 'description': '降低全场敌人冰冻抗性，受击敌人移速大幅削减，提供后台极速连携换人。'}
        ]
    },
    {
        'name': '灯 · 破弃孤光·白炽 (Lantern)',
        'title': '破弃孤光 · 七术速射弩炮高爆火C',
        'rarity': 5,
        'element': '异能 · 火焰伤害 (PSY Fire)',
        'weapon_type': '速射弩炮 (Rapid Crossbow)',
        'region': '洛星七术',
        'arkhe': '星环之位：轮转星影',
        'skills': [
            {'name': '分支 · 弹雨狂澜', 'type': 'ELEMENTAL_SKILL', 'scaling': '霰弹速射/高爆榴弹', 'description': '切换多种重装枪械武器连续扫射，引爆敌阵中埋设的高烈度热能地雷'},
            {'name': '必杀 · 燃尽残阳之怒', 'type': 'ELEMENTAL_BURST', 'scaling': '战术核轰炸', 'description': '呼叫全自动支援防卫卫星从天降下激光聚能射线，将战场化为一片焦土！'}
        ],
        'passives': [
            {'name': '破弃意志', 'description': '攻击点燃状态敌人全伤害提升 35%，轮转星影分支暴击率达到 100%。'}
        ]
    },
    {
        'name': '松雀 · 瞒天乐游·曙影 (Songque)',
        'title': '七术欺唆 · 遮天法杖星尘物理大C',
        'rarity': 5,
        'element': '星尘 · 物理伤害 (SD Physical)',
        'weapon_type': '欺唆法杖 (Trick Staff)',
        'region': '洛星七术',
        'arkhe': '星环之位：万象易位',
        'skills': [
            {'name': '分支 · 戏法符印', 'type': 'ELEMENTAL_SKILL', 'scaling': '纸鸢飞旋/符篆轰击', 'description': '扔出漫天欺唆符印引动天雷地火，迷惑敌人心智并造成连续物理暴击破防'},
            {'name': '必杀 · 算尽乾坤一掷', 'type': 'ELEMENTAL_BURST', 'scaling': '巨大纸鸢天降砸击', 'description': '召唤遮天蔽日的巨大法印与神鸟从苍穹砸下，打出数千万核爆级物理大数字伤害！'}
        ],
        'passives': [
            {'name': '算无遗策', 'description': '提供百分百暴击率转化与超高爆伤加成，星尘属性直接斩杀阈值大幅提高。'}
        ]
    },
    {
        'name': '德丽莎 · 神行千里·光耀夜行 (Theresa)',
        'title': '神行千里 · 天垣眷礼量子雷伤大C',
        'rarity': 5,
        'element': '量子 · 雷电伤害 (QUA Lightning)',
        'weapon_type': '链刃 / 傀儡丝线 (Chained Blade)',
        'region': '天命总部 / 洛星',
        'arkhe': '星环之位：天垣眷礼',
        'skills': [
            {'name': '分支 · 偶影相随', 'type': 'ELEMENTAL_SKILL', 'scaling': '傀儡狂舞/引雷下劈', 'description': '指尖丝线操纵傀儡快速穿梭战场，打出密集雷暴并施加量子坍缩印记'},
            {'name': '必杀 · 光耀万世巡夜', 'type': 'ELEMENTAL_BURST', 'scaling': '天降巨型傀儡神雷', 'description': '召唤如山峰般庞大的夜行傀儡挥出天罚重拳，强行使全场量子敌人直接坍缩！'}
        ],
        'passives': [
            {'name': '神行之威', 'description': '天垣眷礼状态下全队雷电伤害与全伤害提升 40%，对量子敌人特攻。'}
        ]
    },
    {
        'name': '科拉莉 · 战乱狂飙 (Coralie - Valkyrie Blastmetal)',
        'title': '战乱狂飙 · 重锤破盾平民战神',
        'rarity': 4,
        'element': '异能 · 火焰伤害 (PSY Fire)',
        'weapon_type': '重锤 (Rocket Hammer)',
        'region': '圣芙蕾雅学园 / 欧珀',
        'arkhe': '星环之位：界域共鸣',
        'skills': [
            {'name': '分支 · 火箭喷射砸击', 'type': 'ELEMENTAL_SKILL', 'scaling': '重锤破盾/烈焰冲击', 'description': '开启重锤尾部火箭喷射腾空而起，重力加速度砸向地面造成范围高额火伤并强力碎盾'},
            {'name': '必杀 · 轰鸣炽焰引信', 'type': 'ELEMENTAL_BURST', 'scaling': '全队星环充能与全伤提升', 'description': '引爆重锤内部储能核心，为全队提供极速星环能量充能与全元素易伤。'}
        ],
        'passives': [
            {'name': '共鸣放大器', 'description': '界域共鸣触发频率翻倍，第二部平民开荒与深渊高性价比核心辅助。'}
        ]
    },
    {
        'name': '赫丽娅 · 巡矢追光 (Helia - Valkyrie Boltstorm)',
        'title': '巡矢追光 · 战术双枪雷电连携',
        'rarity': 4,
        'element': '机械 · 雷电伤害 (MECH Lightning)',
        'weapon_type': '双枪 / 战术弩箭 (Crossbow/Pistols)',
        'region': '圣芙蕾雅学园',
        'arkhe': '星环之位：界域共鸣',
        'skills': [
            {'name': '分支 · 连珠射击', 'type': 'ELEMENTAL_SKILL', 'scaling': '精准点射/电磁爆破', 'description': '双枪高速连发形成电磁弹雨，为目标叠加感电层数并生成共鸣标记'},
            {'name': '必杀 · 极光贯虹之箭', 'type': 'ELEMENTAL_BURST', 'scaling': '超远距离穿透狙击', 'description': '组装高能电磁狙击弩，射出一道贯穿战场的电磁长虹，引爆沿途所有共鸣标记！'}
        ],
        'passives': [
            {'name': '战术协调', 'description': '为全队星环角色提供雷电元素增伤与共鸣攻击额外倍率加成。'}
        ]
    },

    # ------------------ 第一部与1.5部顶尖律者与神装 ------------------
    {
        'name': '终焉之律者 (Herrscher of Finality)',
        'title': '琪亚娜 · 终焉之律者 · 绝对时停核爆',
        'rarity': 5,
        'element': '虚数 · 火焰伤害 (IMG Fire)',
        'weapon_type': '双枪 / 绝灭长剑',
        'region': '地球月球 / 终焉之茧',
        'arkhe': '绝对时空断裂',
        'skills': [
            {'name': '分支 · 姿态切换', 'type': 'ELEMENTAL_SKILL', 'scaling': '时间溯流/分支爆发', 'description': '消耗【降临】充能切换【时锋】与【月锋】双姿态，打出高倍率火焰分支伤害并积攒【轮回时滞】'},
            {'name': '必杀 · 飞向明天的残响', 'type': 'ELEMENTAL_BURST', 'scaling': '绝对时停全场静止', 'description': '琪亚娜飞向太空展开终焉王座，触发长达 30 秒的【绝对时空断裂】！期间一切计时、Buff、敌人动作完全静止！'}
        ],
        'passives': [
            {'name': '三律者共鸣', 'description': '与始源之律者、真理之律者同队时，解锁三人合体大招与无消耗极速爆发QTE连携！'}
        ]
    },
    {
        'name': '始源之律者 (Herrscher of Origin)',
        'title': '雷电芽衣 · 始源之律者 · 心技一体太刀极意',
        'rarity': 5,
        'element': '虚数 · 雷电伤害 (IMG Lightning)',
        'weapon_type': '太刀 (Katana)',
        'region': '逆熵 / 极东支部',
        'arkhe': '心技一体',
        'skills': [
            {'name': '分支 · 意业返还', 'type': 'ELEMENTAL_SKILL', 'scaling': '居合斩反击/积攒心相', 'description': '收刀入鞘摆出格挡居合架势，完美弹刀触发极限居合瞬闪，积攒三层【心之所向】打出绝命拔刀斩！'},
            {'name': '必杀 · 溯断原罪之刃', 'type': 'ELEMENTAL_BURST', 'scaling': '连续自由划屏九连斩', 'description': '展开始源翅翼，操纵太刀由玩家自由控制连续斩出 12 刀狂风暴雨般的雷电剑气，最后一刀斩裂虚空！'}
        ],
        'passives': [
            {'name': '始源真理', 'description': '为全队提供虚数属性易伤与全伤害提升加成，三人队中充当雷伤核心接力点。'}
        ]
    },
    {
        'name': '真理之律者 (Herrscher of Truth)',
        'title': '布洛妮娅 · 真理之律者 · 延拓机甲全元素大拐',
        'rarity': 5,
        'element': '虚数 · 冰冻伤害 (IMG Ice)',
        'weapon_type': '重炮 (Cannon)',
        'region': '逆熵',
        'arkhe': '重装小兔延拓',
        'skills': [
            {'name': '分支 · 延拓形态变身', 'type': 'ELEMENTAL_SKILL', 'scaling': '武装机甲解构变身', 'description': '重装小兔展开解构为机甲战车，布洛妮娅进入【延拓形态】，武器解锁激光扫射、浮游炮与微型导弹连射！'},
            {'name': '必杀 · 终末创生之破裂', 'type': 'ELEMENTAL_BURST', 'scaling': '全元素穿透超强辅助', 'description': '召唤重型战舰开火轰炸全屏，为全队提供全元素穿透、冰火雷三属性巨额增伤与能量回复！'}
        ],
        'passives': [
            {'name': '真理之启', 'description': '元素穿透乘区独一档，当前版本冰火雷三大元素体系通用最强辅助核心。'}
        ]
    },
    {
        'name': '死生之律者 (Herrscher of Rebirth)',
        'title': '希儿 · 死生之律者 · 塑灵辅助/结命主C双形态',
        'rarity': 5,
        'element': '异能 · 物理伤害 (PSY Physical)',
        'weapon_type': '镰刀 / 灵鹿与妖花 (Scythe)',
        'region': '量子之海 / 盐雪圣城',
        'arkhe': '生命与死亡双生',
        'skills': [
            {'name': '分支 · 塑灵/结命姿态转换', 'type': 'ELEMENTAL_SKILL', 'scaling': '灵鹿协同/妖花巨镰斩', 'description': '在【塑灵形态】下召唤灵鹿协同施加 75% 物理脆弱并使全队暴击率达到 100%；在【结命形态】下化身狂暴主C连续挥动死神之镰！'},
            {'name': '必杀 · 朝暮露华开', 'type': 'ELEMENTAL_BURST', 'scaling': '全场百暴结界与超长脆弱', 'description': '展开晨曦生死之境，全屏敌人被施加持续长达 30 秒的脆弱印记，全队物理攻击暴击率直接转化为暴击伤害！'}
        ],
        'passives': [
            {'name': '生与死之界', 'description': '物理队伍绝对统治级核心辅助，全队常驻超高额暴击转化与独立易伤。'}
        ]
    },
    {
        'name': '人类之律者·爱莉希雅 (Herrscher of Human: Ego)',
        'title': '爱莉希雅 · 始源与人之律者 · 水晶乐土',
        'rarity': 5,
        'element': '异能 · 冰冻伤害 (PSY Ice)',
        'weapon_type': '弓箭 (Bow)',
        'region': '逐火之蛾 / 往世乐土',
        'arkhe': '无瑕花种',
        'skills': [
            {'name': '武器技 · 爱之飞矢', 'type': 'ELEMENTAL_SKILL', 'scaling': '弓箭弱点射击/冰晶引爆', 'description': '射出附带无瑕种子的水晶箭矢，在敌人身上绽放水晶花朵并将其瞬间冰封！'},
            {'name': '必杀 · 空无一人的乐土', 'type': 'ELEMENTAL_BURST', 'scaling': '展开水晶乐土大招领域', 'description': '化身为圣洁的人之律者礼服形态！展开全屏璀璨的水晶穹顶乐土，普攻转化为水晶星光漫游，爆发无与伦比！'}
        ],
        'passives': [
            {'name': '始源之爱', 'description': '入场即自带初始能量并直接赋予全队暴击伤害与全伤害加成。'}
        ]
    },
    {
        'name': '识之律者 (Herrscher of Sentience)',
        'title': '符华 · 识宝 · 枪剑链三持无敌物理大拐',
        'rarity': 5,
        'element': '生物 · 物理伤害 (BIO Physical)',
        'weapon_type': '拳套 / 宝剑 / 长枪 / 链刃',
        'region': '太虚山 / 天命',
        'arkhe': '幻境意识',
        'skills': [
            {'name': '分支 · 兵刃切换三连击', 'type': 'ELEMENTAL_SKILL', 'scaling': '宝剑禁锢/长枪聚怪/链刃昏迷', 'description': '在剑、枪、链三种武器间自由切换分支，长枪聚怪、宝剑禁锢、链刃大范围斩杀！'},
            {'name': '必杀 · 愚钝的野兽，都给我趴下！', 'type': 'ELEMENTAL_BURST', 'scaling': '75% 长时间全屏脆弱大招', 'description': '创造全屏识之律者幻境结界！为全屏敌人施加高达 75% 的超强物理脆弱！随后挥动巨大箱子疯狂乱砸！'}
        ],
        'passives': [
            {'name': '识宝天下第一', 'description': '物理队伍长年绝对霸主核心，辅助与自身输出兼备的天花板。'}
        ]
    },
    {
        'name': '月下誓约·予爱以心 (Lunar Vow: Crimson Love)',
        'title': '德丽莎 · 大电锯吸血鬼 · 雷伤流血双重统治',
        'rarity': 5,
        'element': '异能 · 雷电伤害 / 流血 (PSY Lightning/Bleed)',
        'weapon_type': '重型电锯 (Cross/Chainsaw)',
        'region': '圣芙蕾雅学园',
        'arkhe': '血月红莲',
        'skills': [
            {'name': '分支 · 疯狂电锯狂飙', 'type': 'ELEMENTAL_SKILL', 'scaling': '高频撕裂切割/堆叠流血', 'description': '双手提起猩红电锯按住攻击键持续撕锯敌人，电锯火花四溅打出每秒数十段雷电与流血混合撕裂伤！'},
            {'name': '必杀 · 此心永许于你', 'type': 'ELEMENTAL_BURST', 'scaling': '双持电锯终极十字斩', 'description': '展开血色双翼，双持重型电锯向苍穹交叉切割，全屏降下血雷造成毁灭性雷电与流血真实穿透伤害！'}
        ],
        'passives': [
            {'name': '流血誓约', 'description': '流血伤害可暴击并附带雷电抗性穿透，雷伤与流血体系双霸主。'}
        ]
    },
    {
        'name': '天元骑英 (Palatinus Equinox)',
        'title': '幽兰黛尔 · 卫士与骑士双形态虚数物理天花板',
        'rarity': 5,
        'element': '虚数 · 物理伤害 (IMG Physical)',
        'weapon_type': '骑枪 / 战马天马 (Lance)',
        'region': '天命总部',
        'arkhe': '天元黑白平衡',
        'skills': [
            {'name': '分支 · 纵马疾驰冲锋', 'type': 'ELEMENTAL_SKILL', 'scaling': '骑马贯穿/霸体踏地', 'description': '召唤黑白战马翻身上马，进入【骑士形态】全速狂奔冲锋，一路撞飞撞碎沿途所有敌人！'},
            {'name': '必杀 · 天元开辟之刻', 'type': 'ELEMENTAL_BURST', 'scaling': '直击虚数核心核爆', 'description': '人马合一化身天马踏穿苍穹，枪尖凝聚天元黑白极光贯穿大地！对虚数敌人外壳造成的伤害按 100% 直接同步扣除核心生命！'}
        ],
        'passives': [
            {'name': '虚数核心斩杀', 'description': '大招对虚数敌人核心伤害 100% 传导，直接跳过二阶段秒杀虚数牛头与千人律者。'}
        ]
    },
    {
        'name': '薪炎之律者 (Herrscher of Flamescion)',
        'title': '琪亚娜 · 继承姬子薪火 · 空中大剑连斩',
        'rarity': 5,
        'element': '异能 · 火焰伤害 (PSY Fire)',
        'weapon_type': '双枪 / 烈焰大剑',
        'region': '圣芙蕾雅学园',
        'arkhe': '薪火永燃',
        'skills': [
            {'name': '分支 · 薪炎律动', 'type': 'ELEMENTAL_SKILL', 'scaling': '空中浮空挑飞连斩', 'description': '消耗生命值进入律者形态，将敌人击挑至空中展开华丽的空中大剑多段连续劈砍！'},
            {'name': '必杀 · 薪火的传承', 'type': 'ELEMENTAL_BURST', 'scaling': '烈焰大剑绝命下劈', 'description': '将薪火与愿景凝聚于大剑之上，从苍穹之中挥出焚天灭地的一斩！造成超强火伤并恢复自身生命！'}
        ],
        'passives': [
            {'name': '薪尽光生', 'description': '自带高额时空断裂触发与护盾吸收免伤。'}
        ]
    },
    {
        'name': '次生银翼 (Silverwing: N-EX)',
        'title': '布洛妮娅 · 大布洛妮娅 · 远程浮空机枪冰伤',
        'rarity': 5,
        'element': '生物 · 冰冻伤害 (BIO Ice)',
        'weapon_type': '重炮 / 分裂屏障 (Cannon)',
        'region': '逆熵 / 圣方丹',
        'arkhe': '理之延拓',
        'skills': [
            {'name': '分支 · 展开分裂屏障', 'type': 'ELEMENTAL_SKILL', 'scaling': '穿透增伤/子弹分裂翻倍', 'description': '在场上展开高科技高能阻击屏障，穿过屏障的全部冰冻激光与炮弹数量翻倍且全伤害提升 40%！'},
            {'name': '必杀 · 银翼歼灭激光', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏地毯式轰炸', 'description': '召唤轨道空投重型武器站，向地面倾泻毁灭性的冰霜激光风暴！'}
        ],
        'passives': [
            {'name': '空中压制', 'description': '可在半空中全程保持高机动射击，完全免疫大部分地面近战攻击判定。'}
        ]
    },
    {
        'name': '戒律·深罪之槛 (Disciplinary Perdition)',
        'title': '阿波尼亚 · 逐火十三英桀第三位 · 忏悔落雷',
        'rarity': 5,
        'element': '生物 · 雷电伤害 (BIO Lightning)',
        'weapon_type': '环刃 (Chakram)',
        'region': '往世乐土',
        'arkhe': '深罪预言',
        'skills': [
            {'name': '分支 · 祈祷赎罪', 'type': 'ELEMENTAL_SKILL', 'scaling': '退居后台/自动落雷', 'description': '施展祈祷后退入后台，队友造成雷伤时阿波尼亚在后台自动发动全屏天罚落雷协同作战！'},
            {'name': '必杀 · 罪恶，不可饶恕', 'type': 'ELEMENTAL_BURST', 'scaling': '万雷天牢全屏大招', 'description': '双臂展露神圣罪纹，无视全场敌人防御降下九道撕裂大地的纯白雷霆！'}
        ],
        'passives': [
            {'name': '戒律守护', 'description': '全队雷电元素抗性提升，对麻痹状态敌人造成额外 30% 独立伤害。'}
        ]
    },
    {
        'name': '玉骑士·月痕 (Jade Knight)',
        'title': '李素裳 · 太虚仙人传人 · 万剑归宗冰系第一穿透拐',
        'rarity': 5,
        'element': '异能 · 冰冻伤害 (PSY Ice)',
        'weapon_type': '太刀 (Katana/Fists)',
        'region': '神州太虚',
        'arkhe': '剑意太虚',
        'skills': [
            {'name': '分支 · 九野剑阵', 'type': 'ELEMENTAL_SKILL', 'scaling': '飞剑踏雪/回风落雁', 'description': '踏剑而起御剑凌空，施展九野剑阵万剑攒射，削减敌人护盾并回复全队SP！'},
            {'name': '必杀 · 太虚剑气·神韵', 'type': 'ELEMENTAL_BURST', 'scaling': '天降巨剑全屏破盾与穿透', 'description': '凝聚浩瀚神州剑意召唤一柄耸入云端的巨剑插向地面，为全队提供极其珍贵的全元素穿透加成！'}
        ],
        'passives': [
            {'name': '剑意无极', 'description': '冰伤大队与第二部队伍核心穿透大拐，破盾能力极强。'}
        ]
    },
    {
        'name': '天行·绘星之卷 (Cosmic Expression)',
        'title': '长大格蕾修 · 星尘流血光剑战神',
        'rarity': 4,
        'element': '星尘 · 物理/流血 (SD Physical/Bleed)',
        'weapon_type': '十字架 / 星光长剑 (Cross)',
        'region': '星空方舟',
        'arkhe': '星空绘卷',
        'skills': [
            {'name': '分支 · 流光斩击', 'type': 'ELEMENTAL_SKILL', 'scaling': '光剑三连斩/星尘破壳', 'description': '挥动光剑施展潇洒的流光三连劈砍，大幅积攒全场敌人的流血槽与星尘残核'},
            {'name': '必杀 · 漫天星斗如雨落', 'type': 'ELEMENTAL_BURST', 'scaling': '天外陨石召唤核爆', 'description': '手握十字架画笔向夜空一指，召唤一颗燃烧烈焰的巨大星外陨石轰然坠落，流血全伤翻倍！'}
        ],
        'passives': [
            {'name': '星空绘色', 'description': '使全队流血伤害可享受物理暴击加成，流血物理体系核心搭档。'}
        ]
    }
]

WEAPONS = [
    {
        'name': '宿命终途·羽化之芒 (Lone Planetfarer PRI)',
        'type': '超限驱动核心 (薇塔专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 445, 'desc': '攻击力 445，会心 24'}],
        'sub_stat': {'signature': '星环之位：天垣眷礼与全属性通辅'},
        'refinements': [{'rank': '超限羽化', 'desc': '全队星环爆发期间全伤害提升 40%，雷电与星尘属性伤害额外提升 35%，共鸣标记爆破倍率提升 60%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '独幕诡戏·友爱假面 (Sparkle PRI)',
        'type': '超限驱动核心 (花火专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 442, 'desc': '攻击力 442，会心 22'}],
        'sub_stat': {'signature': '恶作剧恶趣味与全队战技充能'},
        'refinements': [{'rank': '千面巡游', 'desc': '进入战场立即为全队恢复 25 点SP，全队角色全伤害提升 30%，火伤与物理爆伤额外提升 40%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '夜行琉璃·神行千里 (Theresa Celestial PRI)',
        'type': '超限链刃 (德丽莎神行千里专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 443, 'desc': '攻击力 443，会心 21'}],
        'sub_stat': {'signature': '量子坍缩强化与雷暴倍率提升'},
        'refinements': [{'rank': '神行夜雷', 'desc': '武器技对量子敌人造成 1 次额外量子坍缩，全队处于天垣眷礼时雷电元素伤害提升 38%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '红霜点晴·初绽 (Senadina PRI)',
        'type': '超限驱动核心 (希娜狄雅专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 442, 'desc': '攻击力 442，会心 21'}],
        'sub_stat': {'signature': '星环界域共鸣'},
        'refinements': [{'rank': '晨星破晓', 'desc': '激活星环爆发时，全队雷电元素伤害提升 35%，共鸣攻击附加额外崩解伤害！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '夜宴蔷薇·虚宴巡礼 (Thelema PRI)',
        'type': '超限链刃 (瑟莉姆专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 443, 'desc': '攻击力 443，会心 20'}],
        'sub_stat': {'signature': '宴乐步法冰刺增伤'},
        'refinements': [{'rank': '盛宴裁决', 'desc': '释放分支攻击引发冰霜剑气暴鸣，全场敌人承受冰冻元素伤害提升 32%，移速减少 40%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '灼御炎逐·破妄 (Lantern PRI)',
        'type': '超限速射弩炮 (灯专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 441, 'desc': '攻击力 441，会心 23'}],
        'sub_stat': {'signature': '轮转星影与暴击转换'},
        'refinements': [{'rank': '破妄烈焰', 'desc': '高爆榴弹对点燃敌人造成额外 45% 火伤，全队星环角色全伤害提升 28%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '留影夕颜·浮世一掷 (Songque PRI)',
        'type': '超限法杖 (松雀专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 444, 'desc': '攻击力 444，会心 25'}],
        'sub_stat': {'signature': '万象易位与暴击伤害爆发'},
        'refinements': [{'rank': '算尽浮生', 'desc': '物理暴击伤害提升 55%，星尘残核直接引爆全屏造成 1800% 物理大数字伤害！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '无名之钥 / 无名之境：万物初始',
        'type': '超限双枪 (终焉之律者专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 441, 'desc': '攻击力 441，会心 22'}],
        'sub_stat': {'signature': '绝对时停强化'},
        'refinements': [{'rank': '终焉万物', 'desc': '武器技造成巨额火焰伤害并回复 3 点【降临】充能；绝对时空断裂期间全队全伤害提升 45%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '澄凝之钥 / 澄凝之境：自往救赎',
        'type': '超限太刀 (始源之律者专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 438, 'desc': '攻击力 438，会心 22'}],
        'sub_stat': {'signature': '拔刀瞬斩充能'},
        'refinements': [{'rank': '始源返还', 'desc': '武器技弹刀成功时直接回满【心之所向】，必杀技每一击额外附加 60% 攻击力雷电伤害！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '升恒之钥 / 升恒之境：理创未来',
        'type': '超限重炮 (真理之律者专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 436, 'desc': '攻击力 436，会心 15'}],
        'sub_stat': {'signature': '延拓形态导弹强化'},
        'refinements': [{'rank': '真理创生', 'desc': '为全队提供全元素伤害加成 30%，进入延拓形态时立即回复 20 点全队SP！全元素穿透乘区质变！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '撷生之径 / 撷生之径·你我如一',
        'type': '超限镰刀 (死生之律者专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 446, 'desc': '攻击力 446，会心 23'}],
        'sub_stat': {'signature': '生死结界与全队百暴'},
        'refinements': [{'rank': '如一死生', 'desc': '全队暴击率提升 30%，塑灵形态下武器技直接引爆脆弱造成物理大伤害并延长脆弱持续时间！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '往世的飞花 / 往世的飞花·爱之诗',
        'type': '超限弓箭 (人类之律者专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 441, 'desc': '攻击力 441，会心 19'}],
        'sub_stat': {'signature': '水晶种子绽放'},
        'refinements': [{'rank': '无瑕花语', 'desc': '狙击弱点时造成大范围冰冻爆破，人之律者状态下冰冻元素伤害提升 50%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '无存之钥 / 无存之境：意识',
        'type': '超限拳套 (识之律者专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 433, 'desc': '攻击力 433，会心 25'}],
        'sub_stat': {'signature': '脆弱延长与SP回复'},
        'refinements': [{'rank': '识之意识', 'desc': '释放武器技直接回复 30 点SP，大幅缩短开大大招循环周期，物理输出与辅助质变！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '血染赤匣 / 血染赤匣·爱相随',
        'type': '超限重型电锯 (月下誓约专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 445, 'desc': '攻击力 445，会心 18'}],
        'sub_stat': {'signature': '电锯撕裂与流血暴击'},
        'refinements': [{'rank': '血色誓言', 'desc': '电锯切割频率大幅提升，全队雷电元素伤害提升 35%，流血伤害额外附加 40% 雷伤穿透！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '子夜黑光 / 子夜的黑羽·天元',
        'type': '超限骑枪 (天元骑英专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 443, 'desc': '攻击力 443，会心 22'}],
        'sub_stat': {'signature': '天元开辟与人马冲锋'},
        'refinements': [{'rank': '天元黑羽', 'desc': '骑马冲锋每步造成 120% 物理伤害并提供绝对霸体，大招必杀技物理暴击率提升 100%！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    },
    {
        'name': '夜衔烛 / 夜衔烛·飞光',
        'type': '超限太刀 (玉骑士李素裳专武)',
        'rarity': 5,
        'base_atk_curve': [{'level': '65', 'atk': 442, 'desc': '攻击力 442，会心 18'}],
        'sub_stat': {'signature': '万剑归宗与破盾穿透'},
        'refinements': [{'rank': '烛龙飞光', 'desc': '释放九野剑阵全队全元素伤害提升 30%，冰冻元素穿透提升 14%，破盾效率翻倍！'}],
        'ascension_materials': [{'tier': '超限突破', 'material': '爱因斯坦环磁机 x100, 超导金属氢 x200'}]
    }
]

STIGMATA_SETS = [
    {
        'name': '独步千星套 (薇塔专属)',
        'two_piece_bonus': '全伤害提升 30%，星环爆发期间全队全属性元素伤害提升 35%，全元素穿透提升 8%。',
        'four_piece_bonus': '三件套：全队天垣眷礼连携倍率提升 50%，星尘敌人承受全伤害提升 25%，第二部全队万能通辅核心！',
        'pieces': [
            {'slot': '上', 'name': '独步千星 (上)', 'main_stat_rule': '生命 380, 攻击 118, 防御 66, 雷伤提升 30%'},
            {'slot': '中', 'name': '独步千星 (中)', 'main_stat_rule': '生命 420, 防御 180, 会心 8, 全伤害提升 25%'},
            {'slot': '下', 'name': '独步千星 (下)', 'main_stat_rule': '生命 390, 攻击 112, 防御 70, 全队星环回能提升'}
        ],
        'rules_reference': {'type': '第二部星环万能毕业套', 'recommend': '薇塔·孑遗千星'}
    },
    {
        'name': '梦境名导演套 (花火专属)',
        'two_piece_bonus': '全队暴击伤害提升 40%，火伤与物理伤害提升 30%，换人入场自动获得 1 点战技充能。',
        'four_piece_bonus': '三件套：大招释放后全队暴击率提升 25%，全伤害提升 35%，对量子敌人量子坍缩伤害翻倍！',
        'pieces': [
            {'slot': '上', 'name': '名导演·戏谑 (上)', 'main_stat_rule': '生命 375, 攻击 115, 防御 60, 火伤物理提升 28%'},
            {'slot': '中', 'name': '名导演·剧本 (中)', 'main_stat_rule': '生命 415, 防御 195, 会心 10, 全队暴伤加成'},
            {'slot': '下', 'name': '名导演·终幕 (下)', 'main_stat_rule': '生命 385, 攻击 116, 防御 68, SP初始充能提升'}
        ],
        'rules_reference': {'type': '崩铁联动量子物理火辅神套', 'recommend': '花火·诡戏千役'}
    },
    {
        'name': '光耀夜行套 (德丽莎神行千里专属)',
        'two_piece_bonus': '雷电元素伤害提升 35%，分支攻击为敌人附加【雷暴】标记，承受雷电伤害提升 25%。',
        'four_piece_bonus': '三件套：天垣眷礼激活时，全队全伤害提升 30%，对量子护盾额外造成 100% 破盾伤害！',
        'pieces': [
            {'slot': '上', 'name': '光耀夜行 (上)', 'main_stat_rule': '生命 382, 攻击 116, 防御 65, 雷伤 +32%'},
            {'slot': '中', 'name': '光耀夜行 (中)', 'main_stat_rule': '生命 418, 防御 185, 会心 9, 全伤害 +22%'},
            {'slot': '下', 'name': '光耀夜行 (下)', 'main_stat_rule': '生命 392, 攻击 110, 防御 75, 移速与破盾加成'}
        ],
        'rules_reference': {'type': '量子雷伤大C毕业套', 'recommend': '德丽莎·神行千里'}
    },
    {
        'name': '盛宴狂欢套 (瑟莉姆享乐狂宴专属)',
        'two_piece_bonus': '冰冻元素伤害提升 35%，分支攻击命中消耗盛宴点数使全队全伤害提升 25%。',
        'four_piece_bonus': '三件套：全场敌人陷入霜冻状态受全伤害提升 30%，全队星环角色换人冷却减少 3 秒！',
        'pieces': [
            {'slot': '上', 'name': '盛宴狂欢 (上)', 'main_stat_rule': '生命 378, 攻击 118, 防御 62, 冰伤 +35%'},
            {'slot': '中', 'name': '盛宴狂欢 (中)', 'main_stat_rule': '生命 422, 防御 190, 会心 8, 冰冻抗性穿透 +8%'},
            {'slot': '下', 'name': '盛宴狂欢 (下)', 'main_stat_rule': '生命 388, 攻击 114, 防御 70, 全队星环爆发增益'}
        ],
        'rules_reference': {'type': '机械冰系大C毕业套', 'recommend': '瑟莉姆·享乐狂宴'}
    },
    {
        'name': '破妄之光套 (灯破弃孤光专属)',
        'two_piece_bonus': '火焰元素伤害提升 35%，轮转星影分支暴击率转化为火伤独立乘区。',
        'four_piece_bonus': '三件套：攻击点燃状态敌人全伤害提升 40%，全队星环爆发期间重炮与火炮伤害翻倍！',
        'pieces': [
            {'slot': '上', 'name': '破妄之光 (上)', 'main_stat_rule': '生命 376, 攻击 117, 防御 64, 火伤 +32%'},
            {'slot': '中', 'name': '破妄之光 (中)', 'main_stat_rule': '生命 416, 防御 188, 会心 10, 点燃积蓄提升'},
            {'slot': '下', 'name': '破妄之光 (下)', 'main_stat_rule': '生命 390, 攻击 115, 防御 68, 暴击伤害转化为独立火伤'}
        ],
        'rules_reference': {'type': '速射火系大C专属套', 'recommend': '灯·破弃孤光'}
    },
    {
        'name': '悠闲乐游套 (松雀瞒天乐游专属)',
        'two_piece_bonus': '物理伤害提升 30%，暴击率溢出部分以 1:2 比例直接转化为暴击伤害。',
        'four_piece_bonus': '三件套：万象易位状态下全队物理伤害提升 35%，对星尘敌人斩杀阈值额外增加 15%！',
        'pieces': [
            {'slot': '上', 'name': '悠闲乐游 (上)', 'main_stat_rule': '生命 380, 攻击 118, 防御 65, 物伤 +30%'},
            {'slot': '中', 'name': '悠闲乐游 (中)', 'main_stat_rule': '生命 425, 防御 192, 会心 12, 暴击伤害 +40%'},
            {'slot': '下', 'name': '悠闲乐游 (下)', 'main_stat_rule': '生命 395, 攻击 112, 防御 72, 星尘残核爆破伤害提升'}
        ],
        'rules_reference': {'type': '星尘物理核爆套', 'recommend': '松雀·瞒天乐游'}
    },
    {
        'name': '光辉晨星套 (希娜狄雅深空定锚专属)',
        'two_piece_bonus': '雷电元素伤害提升 30%，界域共鸣触发时额外引发连锁雷电落雷。',
        'four_piece_bonus': '三件套：星环爆发期间全队雷电元素伤害提升 35%，全场敌人承受共鸣伤害提升 28%！',
        'pieces': [
            {'slot': '上', 'name': '光辉晨星 (上)', 'main_stat_rule': '生命 380, 攻击 116, 防御 66, 雷伤 +30%'},
            {'slot': '中', 'name': '光辉晨星 (中)', 'main_stat_rule': '生命 420, 防御 185, 会心 8, 共鸣连携增伤'},
            {'slot': '下', 'name': '光辉晨星 (下)', 'main_stat_rule': '生命 388, 攻击 114, 防御 70, 星环爆发能量恢复'}
        ],
        'rules_reference': {'type': '第二部雷系核心套', 'recommend': '希娜狄雅'}
    },
    {
        'name': '琪亚娜·卡斯兰娜 (名以终焉)',
        'two_piece_bonus': '全伤害提升 30%，进入绝对时空断裂全队全伤害提升 35%。',
        'four_piece_bonus': '三件套：律者形态下火伤提升 45%，与始源/真理同队必杀技全伤翻倍！',
        'pieces': [
            {'slot': '上', 'name': '琪亚娜·名以终焉 (上)', 'main_stat_rule': '生命 376, 攻击 116, 防御 65, 火焰伤害 +30%'},
            {'slot': '中', 'name': '琪亚娜·名以终焉 (中)', 'main_stat_rule': '生命 410, 防御 190, 会心 8, 全伤害提升 +25%'},
            {'slot': '下', 'name': '琪亚娜·名以终焉 (下)', 'main_stat_rule': '生命 388, 攻击 112, 防御 68, 终焉形态全伤'}
        ],
        'rules_reference': {'type': '终焉之律者毕业套', 'recommend': '终焉之律者'}
    },
    {
        'name': '雷电芽衣 (名以始源)',
        'two_piece_bonus': '雷电元素伤害提升 35%，居合斩命中返还 5 点SP。',
        'four_piece_bonus': '三件套：全队全伤害提升 20%，必杀技每段剑气叠加 10% 独立易伤！',
        'pieces': [
            {'slot': '上', 'name': '雷电芽衣·名以始源 (上)', 'main_stat_rule': '生命 380, 攻击 115, 防御 62, 雷电伤害 +30%'},
            {'slot': '中', 'name': '雷电芽衣·名以始源 (中)', 'main_stat_rule': '生命 415, 防御 188, 会心 9, 居合全伤 +22%'},
            {'slot': '下', 'name': '雷电芽衣·名以始源 (下)', 'main_stat_rule': '生命 390, 攻击 110, 防御 72, 始源连携加成'}
        ],
        'rules_reference': {'type': '始源之律者毕业套', 'recommend': '始源之律者'}
    },
    {
        'name': '布洛妮娅·扎伊切克 (名以真理)',
        'two_piece_bonus': '全元素伤害提升 30%，延拓形态下冰冻伤害提升 40%。',
        'four_piece_bonus': '三件套：全队角色全元素穿透提高 10%，全队全元素伤害提升 35%（版本第一大拐套）！',
        'pieces': [
            {'slot': '上', 'name': '布洛妮娅·名以真理 (上)', 'main_stat_rule': '生命 378, 攻击 114, 防御 65, 全元素伤害 +25%'},
            {'slot': '中', 'name': '布洛妮娅·名以真理 (中)', 'main_stat_rule': '生命 420, 防御 195, 会心 8, 全队元素增伤 +30%'},
            {'slot': '下', 'name': '布洛妮娅·名以真理 (下)', 'main_stat_rule': '生命 392, 攻击 112, 防御 70, 全队元素穿透独一档'}
        ],
        'rules_reference': {'type': '真理之律者大拐套', 'recommend': '真理之律者'}
    },
    {
        'name': '优雅与再生套 (死生之律者专属)',
        'two_piece_bonus': '物理伤害提升 30%，全队暴击率提升 20%，塑灵形态下脆弱时间延长 10 秒。',
        'four_piece_bonus': '三件套：全场敌人承受物理全伤害提升 30%，全队暴击伤害提升 45%，物理队核心必备！',
        'pieces': [
            {'slot': '上', 'name': '死生之律者 (上)', 'main_stat_rule': '生命 385, 攻击 118, 防御 65, 物理伤害 +30%'},
            {'slot': '中', 'name': '死生之律者 (中)', 'main_stat_rule': '生命 425, 防御 190, 会心 10, 全队暴击率转化'},
            {'slot': '下', 'name': '死生之律者 (下)', 'main_stat_rule': '生命 395, 攻击 115, 防御 72, 全队物理易伤'}
        ],
        'rules_reference': {'type': '物理队第一大拐与主C神套', 'recommend': '死生之律者'}
    },
    {
        'name': '悠长誓言套 (月下誓约专属)',
        'two_piece_bonus': '雷电元素伤害提升 35%，流血伤害提升 30%，电锯连段暴击率提升 25%。',
        'four_piece_bonus': '三件套：全队雷电元素伤害提升 30%，流血状态敌人承受雷伤额外提高 35%，大招无视 20% 雷抗！',
        'pieces': [
            {'slot': '上', 'name': '悠长誓言 (上)', 'main_stat_rule': '生命 382, 攻击 117, 防御 64, 雷伤 +32%'},
            {'slot': '中', 'name': '悠长誓言 (中)', 'main_stat_rule': '生命 418, 防御 188, 会心 9, 流血伤害 +30%'},
            {'slot': '下', 'name': '悠长誓言 (下)', 'main_stat_rule': '生命 390, 攻击 114, 防御 70, 雷伤穿透加成'}
        ],
        'rules_reference': {'type': '雷伤流血电锯毕业套', 'recommend': '月下誓约·予爱以心'}
    },
    {
        'name': '屠格涅夫 (Turgenev - 猎人套)',
        'two_piece_bonus': '全队角色与召唤物全伤害提升 25%，造成伤害为敌人施加持续【猎人标记】。',
        'four_piece_bonus': '三件套：猎人标记敌人承受全元素伤害提高 36%，为全崩坏3最通用冰伤与召唤物顶级大拐圣痕！',
        'pieces': [
            {'slot': '上', 'name': '屠格涅夫 (上)', 'main_stat_rule': '生命 378, 攻击 114, 防御 65, 冰冻伤害 +28%'},
            {'slot': '中', 'name': '屠格涅夫 (中)', 'main_stat_rule': '生命 415, 防御 192, 会心 8, 召唤物全伤 +35%'},
            {'slot': '下', 'name': '屠格涅夫 (下)', 'main_stat_rule': '生命 390, 攻击 112, 防御 72, 猎人标记全元素易伤'}
        ],
        'rules_reference': {'type': '通用冰伤与召唤大拐套', 'recommend': '迷城骇兔 / 帕朵菲莉丝 / 次生银翼辅'}
    },
    {
        'name': '塞尚 (Cezanne - 画家名作)',
        'two_piece_bonus': '流血伤害提升 25%，格蕾修与物理流血体系核心专属。',
        'four_piece_bonus': '三件套：分支攻击命中为全场敌人挂上【结构剖析】印记，承受物理全伤害提升 36%！',
        'pieces': [
            {'slot': '上', 'name': '塞尚 (上)', 'main_stat_rule': '生命 380, 攻击 116, 防御 62, 物理伤害 +25%'},
            {'slot': '中', 'name': '塞尚 (中)', 'main_stat_rule': '生命 420, 防御 190, 会心 9, 流血槽积蓄提升'},
            {'slot': '下', 'name': '塞尚 (下)', 'main_stat_rule': '生命 392, 攻击 112, 防御 70, 结构剖析物理大易伤'}
        ],
        'rules_reference': {'type': '物理流血第一易伤圣痕', 'recommend': '格蕾修 / 天行绘星 / 月下辅'}
    },
    {
        'name': '亨德尔 (Handel - 音乐大师)',
        'two_piece_bonus': '雷电元素伤害提升 30%，可肝通用雷伤神套，全队雷电抗性提升。',
        'four_piece_bonus': '三件套：消耗SP大于60时，全场敌人承受雷电元素伤害提高 35%，全队雷伤质变！',
        'pieces': [
            {'slot': '上', 'name': '亨德尔 (上)', 'main_stat_rule': '生命 378, 攻击 115, 防御 65, 雷伤 +30%'},
            {'slot': '中', 'name': '亨德尔 (中)', 'main_stat_rule': '生命 415, 防御 188, 会心 8, 全伤害 +22%'},
            {'slot': '下', 'name': '亨德尔 (下)', 'main_stat_rule': '生命 390, 攻击 112, 防御 72, 雷伤全队易伤'}
        ],
        'rules_reference': {'type': '可肝雷伤顶级通用套', 'recommend': '始源之律者 / 伊甸 / 阿波尼亚'}
    }
]

MECHANICS = [
    {
        'category': '星环系统',
        'title': '第二部【星环系统 (Astral Ring)】与四大分野机制全解',
        'formula': '全队星环能量积蓄满 (150点) -> 点击星环图标激活【星环爆发】 -> 进入 20 秒爆发增益期',
        'parameters': {
            '星环分野': '四大分野：【界域共鸣】(共鸣标记连锁爆破)、【天垣眷礼】(全队化身神卫连携协同)、【无存之仪】(单人极致驻场输出)、【回影之召】(幻影替身持续连击)',
            '界域共鸣': '具有界域共鸣特性的角色攻击敌人产生【共鸣标记】，队友的共鸣攻击命中标记触发连锁大范围全属性穿透爆炸',
            '简析攻击': '星环爆发期间角色换人无CD且无敌，入场直接自动打出专属强化连携技'
        }
    },
    {
        'category': '属性克制',
        'title': '三大基础属性与量子/虚数/星尘属性法则',
        'formula': '生物(BIO) > 异能(PSY) > 机械(MECH) > 生物；量子与虚数互相中性克制；星尘中立独立生态',
        'parameters': {
            '星尘属性 (Stardust)': '星尘怪物拥有【星尘固化硬壳】，受到攻击脱落【星尘残核】，拾取残核后对本体造成最大生命值百分比真实伤害，直接扣除整段血条！',
            '虚数属性 (Imaginary)': '虚数怪物分为【虚数外壳】与【虚数核心】。当外壳破碎或使用特定技能（天元骑英大招/终焉大招）可直接越过外壳秒杀核心跳过阶段！',
            '量子属性 (Quantum)': '量子怪物常驻【量子护盾】，处于免疫硬直状态。通过极限闪避量子攻击反弹量子球、或使用花火/德丽莎分支使其【量子坍缩】，失去护盾并陷入瘫痪！'
        }
    },
    {
        'category': '伤害乘区',
        'title': '全元素伤害与物理公式深度乘区拆解',
        'formula': '物理最终伤 = 倍率 × 攻击力 × (1+物伤) × (1+全伤) × (1+暴伤) × (1-防御*(1-脆弱)) × 物理易伤；元素最终伤 = 倍率 × 攻击力 × (1+元素伤) × (1+全伤) × (1-抗性+元素穿透) × 元素易伤',
        'parameters': {
            '元素穿透独立乘区': '高扰动红莲与寂灭深渊 Boss 抗性极高，真理之律者与李素裳提供的【元素穿透】为独立加法削抗乘区，伤害提升达 40%~60%！',
            '脆弱乘区': '识之律者与死生之律者提供的 75% 物理脆弱将敌人防御削减至 25%，是物理暴击核爆的必备基石。',
            '稀释规避': '同一属性词缀（如单纯全伤害）存在边际效应，合理搭配武器圣痕的【独立易伤】、【属性穿透】与【技能倍率】才能达到伤害最大化。'
        }
    },
    {
        'category': '时空判定',
        'title': '全域时空断裂 (Time Fracture) 与QTE换人机制',
        'formula': '在敌人攻击命中前瞬间点按闪避，触发 3~5 秒【全域时空断裂】',
        'parameters': {
            '时滞与减速': '全域时空断裂期间全场暗紫，所有敌人动作、弹道被减速 95%，记忆战场中关卡计时完全静止，冲榜竞速核心核心！',
            '绝对时空断裂': '终焉之律者大招触发，长达 30 秒全场绝对静止，所有时钟和Buff时间完全定格。',
            'QTE出场': '达成时空断裂、击飞、冰冻、麻痹、流血等条件触发下一个女武神闪光QTE头像，点击无缝登场爆发。'
        }
    },
    {
        'category': '异常状态',
        'title': '四大异常状态 (点燃/冻结/麻痹/流血) 积蓄槽法则',
        'formula': '敌人血条旁带有专用积蓄槽，受到对应属性攻击积攒数值，槽满触发特定强控与破防',
        'parameters': {
            '流血积蓄 (Bleed)': '月下誓约与格蕾修核心，流血槽满后持续掉血，且流血伤害无视常规护盾，受塞尚与阿拉丁圣痕大幅加成',
            '冻结积蓄 (Freeze)': '爱莉希雅与瑟莉姆核心，槽满使强韧Boss完全冰封瘫痪数秒',
            '点燃积蓄 (Ignite)': '薪炎与灯核心，槽满造成持续火焚伤害并破坏敌人生命回复效果',
            '麻痹积蓄 (Paralyze)': '伊甸与雷律核心，槽满打断敌人大招蓄力并陷入电击麻痹'
        }
    },
    {
        'category': '律者体系',
        'title': '三律者合体与虚数月面连携循环',
        'formula': '终焉之律者 + 始源之律者 + 真理之律者 组合触发专属三律者队长技与特殊合体大招',
        'parameters': {
            '三人合体大招': '在终焉爆发期间始源与真理接连释放合体QTE，终焉踢出决战月球的一脚，造成天地色变的巨额真伤并刷新循环',
            '无缝循环': '真理变身延拓开火 -> 始源居合拔刀弹刀回能 -> 终焉绝对时停跳步打满轮回时滞'
        }
    },
    {
        'category': '深渊竞速',
        'title': '超弦空间 (深渊) 与记忆战场扰动抗性法则',
        'formula': '深渊环境抗性 = 基础抗性 × (1 + 扰动等级系数)；天气加成 = 对应优势属性/类型伤害 +50%',
        'parameters': {
            '天气对应': '星尘天气 (松雀/薇塔最佳)、量子天气 (花火/神行最佳)、虚数天气 (终焉/始源/天元最佳)、流血天气 (月下/死生最佳)',
            '破盾竞速': '记忆战场利用高阶超限武器的初始SP被动，开局打满脆弱与穿透，利用时空断裂 0 秒结算一波秒杀 SSS Boss'
        }
    }
]


def crawl_and_sync_honkai3(game_id=30):
    print(f'[Honkai Impact 3rd] Preparing Complete Battlesuits, Weapons & Stigmata for Game {game_id} ...')

    characters = []
    for b in BATTLESUITS:
        characters.append({
            'name': b['name'],
            'title': b['title'],
            'rarity': b['rarity'],
            'element': b['element'],
            'weapon_type': b['weapon_type'],
            'region': b['region'],
            'arkhe': b['arkhe'],
            'avatar_url': f'/games/honkai3/{b["name"].split()[0]}.png',
            'splash_url': '',
            'base_stats': [
                {'level': 'S级初登场', 'hp': 3200, 'atk': 450, 'def': 180, 'crt': 60},
                {'level': 'SSS级毕业', 'hp': 4800, 'atk': 820, 'def': 260, 'crt': 110}
            ],
            'talents': b['skills'],
            'passives': b['passives'],
            'constellations': [
                {'rank': 'S1阶', 'desc': '解锁核心分支易伤加成'},
                {'rank': 'SS阶', 'desc': '初始SP提升，解锁全队独立乘区'},
                {'rank': 'SSS阶', 'desc': '全技能等级上限提升，全伤害提升 15%'}
            ],
            'special_mechanics': {'circuit': b['arkhe']},
            'recommendations': {'best_weapon': b['weapon_type'].split('/')[0].strip(), 'best_stigmata': '专属毕业三件套'},
            'version': 'v7.8'
        })

    weapons = []
    for w in WEAPONS:
        weapons.append({
            'name': w['name'],
            'type': w['type'],
            'rarity': w['rarity'],
            'icon_url': f'/games/honkai3_weapons/{w["name"].split()[0]}.png',
            'base_atk_curve': w['base_atk_curve'],
            'sub_stat': w['sub_stat'],
            'refinements': w['refinements'],
            'ascension_materials': w['ascension_materials'],
            'version': 'v7.8'
        })

    artifacts = []
    for s in STIGMATA_SETS:
        artifacts.append({
            'name': s['name'],
            'rarity_min': 5,
            'rarity_max': 5,
            'icon_url': f'/games/stigmata/{s["name"].split()[0]}.png',
            'two_piece_bonus': s['two_piece_bonus'],
            'four_piece_bonus': s['four_piece_bonus'],
            'pieces': s['pieces'],
            'rules_reference': s['rules_reference'],
            'version': 'v7.8'
        })

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    a_count = upsert_artifacts(game_id, artifacts)
    m_count = upsert_mechanics(game_id, MECHANICS)
    print(f'[Honkai Impact 3rd] Ingested into Game {game_id}: {c_count} battlesuits, {w_count} weapons, {a_count} stigmata sets, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_honkai3(30)
