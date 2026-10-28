"""
Fingertip Pixel City (指尖像素城) Comprehensive Crawler & Data Importer Module
Ingests 20 Void/SP & Mythic heroes, 12 exclusive relics (专属圣物), 6 rune sets (阵奕符文),
and 4 core combat mechanics into Game 32 (指尖像素城).
"""

from ..common.db import (
    get_connection,
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

GAME_ID = 32

HERO_DEFINITIONS = [
    {
        'key': 'qinglong',
        'name': '青龙 (Azure Dragon)',
        'title': '雷霆神裔 · 虚空唯一T0强力输出',
        'rarity': 5,
        'element': '雷霆 · 虚空神兽',
        'weapon_type': '专属圣物: 终焉之眼',
        'region': '四象天域 / 虚空界',
        'arkhe': '雷霆万钧',
        'hp': 3200, 'atk': 450, 'def': 180, 'crit': '15%', 'spd': 105,
        'hp_max': 18000000, 'atk_max': 2400000, 'def_max': 850000, 'crit_max': '55%', 'spd_max': 150,
        'skills': [
            {'name': '苍雷狂舞 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '群体穿甲/怒气积累', 'description': '引动九天狂雷轰击敌方前排，造成320%雷霆伤害并附带20%穿甲，回复自身30点怒气。'},
            {'name': '九霄龙吟破 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏核爆/斩杀重置', 'description': '消耗100点怒气，召唤虚空青龙真身降临，对敌方全体造成680%毁灭雷伤并无视50%护盾；若击杀任意目标立即刷新大招并回满怒气！'}
        ],
        'passive': '进入战斗全队暴击伤害+30%，自身处于虚空免疫控制状态。',
        'constellations': [
            {'rank': '1痕', 'name': '龙魂觉醒', 'desc': '释放绝技后暴击率额外提升20%，持续整场战斗。'},
            {'rank': '2痕', 'name': '惊雷贯体', 'desc': '普通攻击追加2段雷电连锁溅射，造成80%真实伤害。'},
            {'rank': '3痕', 'name': '虚空法则', 'desc': '核心怒气终结技伤害倍率提升45%。'},
            {'rank': '4痕', 'name': '破军龙威', 'desc': '敌方生命高于70%时造成额外60%真实伤害。'},
            {'rank': '5痕', 'name': '狂暴雷域', 'desc': '击杀目标立即回复100点怒气并重置技能冷却。'},
            {'rank': '6痕', 'name': '万象神主', 'desc': '濒死时触发雷龙护体，无敌2回合且全属性提升100%。'}
        ],
        'mechanic': '核心流程: 队友减怒控场 -> 青龙释放大招【九霄龙吟破】全屏清场 -> 触发连斩！',
        'recs': {'bis_weapon': '终焉之眼', 'bis_rune': '爆裂 4 件套 + 虚空噬魂 2 件套'}
    },
    {
        'key': 'kaguya',
        'name': '辉夜姬 (Kaguya)',
        'title': '月华神女 · 怒气压制天花板',
        'rarity': 5,
        'element': '光辉 · 神明仙灵',
        'weapon_type': '专属圣物: 月神吊坠',
        'region': '月之神殿',
        'arkhe': '月夜封怒',
        'hp': 3600, 'atk': 280, 'def': 220, 'crit': '10%', 'spd': 120,
        'hp_max': 21000000, 'atk_max': 1500000, 'def_max': 1100000, 'crit_max': '35%', 'spd_max': 165,
        'skills': [
            {'name': '月影清辉 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '单体减怒/易伤', 'description': '挥洒月华射线，降低敌方主C 40点怒气并施加持续2回合的25%易伤标记。'},
            {'name': '蓬莱永夜 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏灭怒/群体禁怒', 'description': '展开月之结界，扣除敌方全体60点怒气，并使其在接下来的2回合内无法通过任何途径获取怒气！'}
        ],
        'passive': '受击时偷取攻击者15点怒气转移给己方怒气最高的友军。',
        'constellations': [
            {'rank': '1痕', 'name': '月蚀初现', 'desc': '开局为全队提供20点初始怒气。'},
            {'rank': '2痕', 'name': '神辉庇佑', 'desc': '友军释放怒气技后，为其提供等同自身最大生命25%的屏障。'},
            {'rank': '3痕', 'name': '月华流转', 'desc': '绝技降低目标怒气提升至60点。'},
            {'rank': '4痕', 'name': '封绝禁锢', 'desc': '大招禁怒持续时间延长1回合。'},
            {'rank': '5痕', 'name': '镜花水月', 'desc': '受到致命伤害时代替友军承受并立即回满怒气。'},
            {'rank': '6痕', 'name': '永恒明月', 'desc': '敌方每次尝试释放绝技，全队获得10%全伤害减免。'}
        ],
        'mechanic': '顶端局防越战核心：配合雪女实现绝对控怒闭环，敌方全程打不出怒气技。',
        'recs': {'bis_weapon': '月神吊坠', 'bis_rune': '怒气压制 4 件套 + 生命回响 2 件套'}
    },
    {
        'key': 'yukionna',
        'name': '雪女 (Yuki Onna)',
        'title': '霜天雪魄 · 极致冰控与双减',
        'rarity': 5,
        'element': '冰霜 · 极地幽灵',
        'weapon_type': '专属圣物: 寒冰雪花片',
        'region': '极北冰原',
        'arkhe': '冰封千里',
        'hp': 3100, 'atk': 380, 'def': 190, 'crit': '12%', 'spd': 112,
        'hp_max': 17500000, 'atk_max': 1950000, 'def_max': 920000, 'crit_max': '40%', 'spd_max': 152,
        'skills': [
            {'name': '冰锥连射 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '减速/概率冰冻', 'description': '射出3枚幽蓝冰锥，降低命中目标30%行动速度并有40%概率将其完全冰冻。'},
            {'name': '极寒暴风雪 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏冰冻/怒气削减', 'description': '召唤暴风雪洗劫全场，造成450%冰霜伤害，对全体敌方施加【深度冰冻】并削减35点怒气。'}
        ],
        'passive': '攻击处于冰冻状态的敌人时，造成额外50%真实伤害并吸取其10点怒气。',
        'constellations': [
            {'rank': '1痕', 'name': '霜花初凝', 'desc': '冰冻概率提升20%。'},
            {'rank': '2痕', 'name': '寒气入骨', 'desc': '被冰冻的目标防御力降低35%。'},
            {'rank': '3痕', 'name': '绝对零度', 'desc': '大招伤害提升40%，冰冻时间延长1回合。'},
            {'rank': '4痕', 'name': '雪魄护盾', 'desc': '自身生命低于50%时生成坚冰护盾。'},
            {'rank': '5痕', 'name': '暴雪漫天', 'desc': '进入战斗立即触发一次无消耗暴风雪。'},
            {'rank': '6痕', 'name': '冰凰降世', 'desc': '全队冰系角色伤害提升35%，冰控效果无法被抵抗。'}
        ],
        'mechanic': '与辉夜姬组成国家级减怒控场队，牢牢锁死敌方大招。',
        'recs': {'bis_weapon': '寒冰雪花片', 'bis_rune': '怒气压制 4 件套 + 疾风连击 2 件套'}
    },
    {
        'key': 'volka',
        'name': '沃尔卡 (Volka)',
        'title': '烈焰主宰 · 灼烧真伤爆发核心',
        'rarity': 5,
        'element': '烈焰 · 狂暴战士',
        'weapon_type': '专属圣物: 炎魔炽羽',
        'region': '熔岩火山',
        'arkhe': '红莲业火',
        'hp': 3400, 'atk': 460, 'def': 195, 'crit': '16%', 'spd': 108,
        'hp_max': 19000000, 'atk_max': 2450000, 'def_max': 900000, 'crit_max': '52%', 'spd_max': 148,
        'skills': [
            {'name': '裂地熔岩斩 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '叠火/引燃', 'description': '挥舞烈焰巨剑砸裂大地，对前排造成380%火伤，并附加3层不可驱散的【红莲灼烧】。'},
            {'name': '业火焚天 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏引爆/百分比真伤', 'description': '引爆敌方全体身上的所有灼烧状态，每层灼烧造成目标最大生命值8%的真实伤害！'}
        ],
        'passive': '火克冰特化：对冰属性敌人造成双倍伤害，并免疫冰冻与减速效果。',
        'constellations': [
            {'rank': '1痕', 'name': '炎魄注入', 'desc': '灼烧伤害提升30%。'},
            {'rank': '2痕', 'name': '熔火战甲', 'desc': '受击时反弹1层灼烧并提升自身5%攻击力。'},
            {'rank': '3痕', 'name': '地脉喷涌', 'desc': '大招引爆基础倍率提升50%。'},
            {'rank': '4痕', 'name': '火神共鸣', 'desc': '与凤凰同时在场时，全队火伤提升25%。'},
            {'rank': '5痕', 'name': '不灭火种', 'desc': '击杀目标后灼烧效果传染给全体存活敌人。'},
            {'rank': '6痕', 'name': '灭世炽炎', 'desc': '灼烧真实伤害上限提升至自身攻击力的10倍。'}
        ],
        'mechanic': '高配火系爆发：配合凤凰、饕餮实现火克冰五十亿越战。',
        'recs': {'bis_weapon': '炎魔炽羽', 'bis_rune': '爆裂 4 件套 + 疾风连击 2 件套'}
    },
    {
        'key': 'phoenix',
        'name': '凤凰 (Phoenix)',
        'title': '九天朱雀 · 涅槃免死与全员增幅',
        'rarity': 5,
        'element': '烈焰 · 神兽庇护',
        'weapon_type': '专属圣物: 炎魔炽羽',
        'region': '不死火山',
        'arkhe': '涅槃重生',
        'hp': 3500, 'atk': 360, 'def': 210, 'crit': '14%', 'spd': 115,
        'hp_max': 19800000, 'atk_max': 1850000, 'def_max': 1050000, 'crit_max': '38%', 'spd_max': 158,
        'skills': [
            {'name': '炽翼旋风 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '群体增益/火伤', 'description': '扇动火翼卷起烈焰风暴，造成260%火伤，并使己方全体火系角色伤害提升25%。'},
            {'name': '朱雀神佑 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '群体免死/全队回血', 'description': '施放朱雀神光，使己方全员获得【涅槃护身】状态（免疫一次致命伤害并回复30%生命）。'}
        ],
        'passive': '自身死亡时立即满血复活（每场战斗生效1次），并对敌方全体造成400%火伤。',
        'constellations': [
            {'rank': '1痕', 'name': '神羽初丰', 'desc': '复活时额外回复50点怒气。'},
            {'rank': '2痕', 'name': '烈焰庇佑', 'desc': '全队受到致命伤害时触发的免死屏障强度翻倍。'},
            {'rank': '3痕', 'name': '朱雀啼鸣', 'desc': '大招伤害与治疗效果提升35%。'},
            {'rank': '4痕', 'name': '火之眷属', 'desc': '友军造成的灼烧伤害提升40%。'},
            {'rank': '5痕', 'name': '无尽炽芒', 'desc': '复活后攻击力永久提升50%。'},
            {'rank': '6痕', 'name': '永生真灵', 'desc': '全员免死触发后立刻驱散所有控制效果。'}
        ],
        'mechanic': '火系核心发动机：提供强力免死护盾与全队火系增伤。',
        'recs': {'bis_weapon': '炎魔炽羽', 'bis_rune': '神圣屏障 4 件套 + 生命回响 2 件套'}
    },
    {
        'key': 'camilla',
        'name': '卡米拉 (Camilla)',
        'title': '猩红血刃 · 破盾斩杀无情收割',
        'rarity': 5,
        'element': '暗夜 · 致命刺客',
        'weapon_type': '专属圣物: 弑神之刃',
        'region': '古堡暗界',
        'arkhe': '猩红瞬狱',
        'hp': 2950, 'atk': 510, 'def': 165, 'crit': '22%', 'spd': 125,
        'hp_max': 16000000, 'atk_max': 2750000, 'def_max': 780000, 'crit_max': '65%', 'spd_max': 170,
        'skills': [
            {'name': '影袭穿刺 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '切后排/破盾', 'description': '瞬移至敌方生命最低的目标身后进行两段穿刺，造成420%暗影伤害并直接粉碎其护盾。'},
            {'name': '瞬狱断罪斩 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '无视护盾/极限斩杀', 'description': '拔刀斩击，对目标造成850%巨额伤害；若目标生命低于35%，则触发无视屏障与防御的一刀必杀！'}
        ],
        'passive': '血气狂欢：每击败一个敌方目标，提升自身20%攻击力与15%暴击伤害，最多叠加5层。',
        'constellations': [
            {'rank': '1痕', 'name': '暗刃嗜血', 'desc': '斩杀线提升至40%生命。'},
            {'rank': '2痕', 'name': '幽冥疾行', 'desc': '击杀目标后立即隐身1回合，无法被选为攻击目标。'},
            {'rank': '3痕', 'name': '血影狂乱', 'desc': '大招伤害倍率提升50%。'},
            {'rank': '4痕', 'name': '护盾崩解', 'desc': '攻击拥有护盾的目标时，造成额外80%伤害。'},
            {'rank': '5痕', 'name': '连环断罪', 'desc': '大招成功斩杀后立即返还80点怒气。'},
            {'rank': '6痕', 'name': '死神化身', 'desc': '敌方全体生命低于50%时，卡米拉所有攻击必定暴击。'}
        ],
        'mechanic': '单C核弹流：配合狐狸六回合技能循环，锁定残血一刀清台。',
        'recs': {'bis_weapon': '弑神之刃', 'bis_rune': '虚空噬魂 4 件套 + 爆裂 2 件套'}
    },
    {
        'key': 'taotie',
        'name': '饕餮 (Taotie)',
        'title': '吞天巨兽 · 吞怒吸盾混沌肉盾',
        'rarity': 5,
        'element': '混沌 · 凶兽前排',
        'weapon_type': '专属圣物: 混沌法球',
        'region': '九幽混沌',
        'arkhe': '吞噬万物',
        'hp': 4200, 'atk': 240, 'def': 260, 'crit': '5%', 'spd': 98,
        'hp_max': 26000000, 'atk_max': 1200000, 'def_max': 1400000, 'crit_max': '20%', 'spd_max': 135,
        'skills': [
            {'name': '吞噬冲击 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '吸盾/嘲讽', 'description': '张开巨口撕咬敌方前排，将目标身上50%护盾转化为自身生命，并强行嘲讽2回合。'},
            {'name': '气吞九霄 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '吞噬怒气/全队屏障', 'description': '张开混沌黑洞吞噬敌方全体各25点怒气，转化为全体友军等额的混沌护盾。'}
        ],
        'passive': '受到的所有伤害降低30%，每损失10%生命额外获得5%减伤与10%防御加成。',
        'constellations': [
            {'rank': '1痕', 'name': '胃纳乾坤', 'desc': '吸收敌方护盾转化率提升至100%。'},
            {'rank': '2痕', 'name': '混沌逆流', 'desc': '受击时有30%概率令攻击者陷入眩晕1回合。'},
            {'rank': '3痕', 'name': '暴食之躯', 'desc': '基础最大生命值提升40%。'},
            {'rank': '4痕', 'name': '黑洞引力', 'desc': '大招吞噬怒气提升至35点。'},
            {'rank': '5痕', 'name': '凶兽真容', 'desc': '濒死时恢复50%最大生命并吞噬所有负面状态。'},
            {'rank': '6痕', 'name': '不朽凶魂', 'desc': '为全体队友分担50%伤害，自身减伤提升至60%。'}
        ],
        'mechanic': '高端局常青树坦克：配合辉夜姬构成怒气双封锁，前排牢不可破。',
        'recs': {'bis_weapon': '混沌法球', 'bis_rune': '神圣屏障 4 件套 + 生命回响 2 件套'}
    },
    {
        'key': 'athena',
        'name': '雅典娜 (Athena)',
        'title': '圣辉女神 · 破盾长矛神圣穿透',
        'rarity': 5,
        'element': '光辉 · 虚空战神',
        'weapon_type': '专属圣物: 虚空破晓矛',
        'region': '奥林匹斯 / 虚空圣域',
        'arkhe': '圣矛破障',
        'hp': 3350, 'atk': 470, 'def': 200, 'crit': '18%', 'spd': 118,
        'hp_max': 18500000, 'atk_max': 2350000, 'def_max': 980000, 'crit_max': '50%', 'spd_max': 160,
        'skills': [
            {'name': '圣辉突刺 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '特化破盾/盲目', 'description': '掷出圣辉长矛贯穿敌阵，对护盾造成300%特化破坏伤害，并附带2回合致盲。'},
            {'name': '胜利神裁 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '贯穿穿甲/屏障粉碎', 'description': '召唤胜利神矛降临，对敌方全体造成550%神圣伤害，彻底瓦解敌方全员全部护盾，并将过量破盾伤害转化为真实伤害！'}
        ],
        'passive': '对所有拥有护盾的敌人，雅典娜所有攻击无视其100%防御。',
        'constellations': [
            {'rank': '1痕', 'name': '智慧启迪', 'desc': '开局全队获得20%破盾伤害加成。'},
            {'rank': '2痕', 'name': '胜利光环', 'desc': '破盾成功后，为全队施加20%攻击力增幅。'},
            {'rank': '3痕', 'name': '裁决之锋', 'desc': '大招伤害提升40%，附带眩晕效果。'},
            {'rank': '4痕', 'name': '金铠神光', 'desc': '自身受到攻击时有50%概率免疫伤害。'},
            {'rank': '5痕', 'name': '神罚贯穿', 'desc': '长矛对后排单位造成额外50%伤害。'},
            {'rank': '6痕', 'name': '战神归位', 'desc': '大招击碎护盾后立刻触发全屏圣辉追击。'}
        ],
        'mechanic': '护盾克星：针对高护盾阵容的神兵利器，瞬间破盾破防。',
        'recs': {'bis_weapon': '虚空破晓矛', 'bis_rune': '爆裂 4 件套 + 疾风连击 2 件套'}
    },
    {
        'key': 'horus',
        'name': '荷鲁斯 (Horus)',
        'title': '太阳神王 · 黄金助战免控光环',
        'rarity': 5,
        'element': '光辉 · 太阳古神',
        'weapon_type': '专属圣物: 太阳神圣翼',
        'region': '太阳神庙',
        'arkhe': '日冕护佑',
        'hp': 3500, 'atk': 320, 'def': 230, 'crit': '12%', 'spd': 110,
        'hp_max': 20000000, 'atk_max': 1650000, 'def_max': 1150000, 'crit_max': '30%', 'spd_max': 155,
        'skills': [
            {'name': '日耀光辉 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '助战触发/免控', 'description': '位于助战位时，第1/3/5回合开局自动施放日耀，为己方全队清除全部控制并附加2回合免控。'},
            {'name': '太阳神威 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏致盲/神圣增幅', 'description': '召唤太阳烈焰轰炸全场，造成420%光辉伤害并使敌方命中率降低50%，全队伤害提升30%。'}
        ],
        'passive': '首选助战特化：位于助战位时，全队主属性提升20%，且无法被任何刺客索敌。',
        'constellations': [
            {'rank': '1痕', 'name': '旭日东升', 'desc': '助战提供的全队伤害减免提升至15%。'},
            {'rank': '2痕', 'name': '荷鲁斯之眼', 'desc': '看穿敌方隐身与闪避，全队命中率提升100%。'},
            {'rank': '3痕', 'name': '日冕辐射', 'desc': '大招伤害与增益效果提升35%。'},
            {'rank': '4痕', 'name': '辉光领域', 'desc': '友军释放怒气技能时追加太阳轰炸。'},
            {'rank': '5痕', 'name': '太阳神冠', 'desc': '助战回合免控时间延长至整场战斗。'},
            {'rank': '6痕', 'name': '万物之光', 'desc': '己方任意角色阵亡时代替其复活并满血登场。'}
        ],
        'mechanic': '顶尖助战神将：无需下场即可为全队提供免控、增伤与生存光环。',
        'recs': {'bis_weapon': '太阳神圣翼', 'bis_rune': '神圣屏障 4 件套 + 生命回响 2 件套'}
    },
    {
        'key': 'venus',
        'name': '维纳斯 (Venus)',
        'title': '爱与美神 · 圣水回春群体魅惑',
        'rarity': 5,
        'element': '流水 · 爱恋仙灵',
        'weapon_type': '专属圣物: 永恒圣杯',
        'region': '玫瑰圣泉',
        'arkhe': '倾世之魅',
        'hp': 3450, 'atk': 290, 'def': 215, 'crit': '10%', 'spd': 116,
        'hp_max': 19500000, 'atk_max': 1550000, 'def_max': 1080000, 'crit_max': '28%', 'spd_max': 162,
        'skills': [
            {'name': '圣泉甘露 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '群体治疗/减伤', 'description': '洒下玫瑰圣水，立即为全体友军回复自身攻击力280%的生命，并提供持续2回合的20%减伤。'},
            {'name': '爱神倾心 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '强力魅惑/敌方互搏', 'description': '释放倾世爱意，对敌方全体造成350%伤害，并有60%概率【魅惑】攻击最高的2名敌人互相残杀！'}
        ],
        'passive': '每回合开始为生命最低的友军生成等同于自身最大生命30%的爱之护盾。',
        'constellations': [
            {'rank': '1痕', 'name': '玫瑰芬芳', 'desc': '治疗效果提升30%，治疗暴击率翻倍。'},
            {'rank': '2痕', 'name': '绝美姿容', 'desc': '被攻击时使攻击者攻击力降低25%。'},
            {'rank': '3痕', 'name': '圣水涌动', 'desc': '大招魅惑概率提升至85%。'},
            {'rank': '4痕', 'name': '花海守护', 'desc': '友军护盾破碎时立即触发一次全体治疗。'},
            {'rank': '5痕', 'name': '爱之永恒', 'desc': '魅惑持续时间增加1回合。'},
            {'rank': '6痕', 'name': '美神降临', 'desc': '全队受到致命伤害时立即免疫并回满生命（全场1次）。'}
        ],
        'mechanic': '顶尖奶妈与反控：魅惑能让敌方高攻击主C瞬间倒戈自相残杀。',
        'recs': {'bis_weapon': '永恒圣杯', 'bis_rune': '生命回响 4 件套 + 神圣屏障 2 件套'}
    },
    {
        'key': 'luna',
        'name': '露娜 (Luna)',
        'title': '月蚀暗灵 · 暴击隐匿瞬杀爆发',
        'rarity': 5,
        'element': '暗夜 · 月影刺客',
        'weapon_type': '专属圣物: 弑神之刃',
        'region': '月影幽谷',
        'arkhe': '月蚀之刃',
        'hp': 3050, 'atk': 490, 'def': 175, 'crit': '25%', 'spd': 122,
        'hp_max': 16800000, 'atk_max': 2650000, 'def_max': 820000, 'crit_max': '68%', 'spd_max': 168,
        'skills': [
            {'name': '月弧暗斩 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '高暴击/破防', 'description': '挥出黑色月牙光刃，造成380%暴击伤害并降低目标40%物理抗性。'},
            {'name': '月蚀永夜斩 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '背刺暴击/隐匿重置', 'description': '遁入暗影背刺敌方后排核心，造成750%致命暴击伤害，暴击后立即进入【隐匿】并回复50点怒气！'}
        ],
        'passive': '暴击伤害额外提升50%，处于隐匿状态下暴击率必定为100%。',
        'constellations': [
            {'rank': '1痕', 'name': '夜幕潜行', 'desc': '进入战斗自动获得2回合隐匿。'},
            {'rank': '2痕', 'name': '碎月锋芒', 'desc': '暴击时追加目标最大生命10%真实伤害。'},
            {'rank': '3痕', 'name': '月影幽光', 'desc': '大招伤害倍率提升45%。'},
            {'rank': '4痕', 'name': '影舞连环', 'desc': '击杀目标后隐匿状态不解除。'},
            {'rank': '5痕', 'name': '暗夜君临', 'desc': '全队刺客职业暴击伤害提升40%。'},
            {'rank': '6痕', 'name': '极夜死神', 'desc': '大招造成伤害的50%转化为自身永久攻击力。'}
        ],
        'mechanic': '刺客爆发天花板：隐匿状态下必定暴击，专门点杀敌方后排核心。',
        'recs': {'bis_weapon': '弑神之刃', 'bis_rune': '爆裂 4 件套 + 虚空噬魂 2 件套'}
    },
    {
        'key': 'igla',
        'name': '伊格拉 (Igla)',
        'title': '自然灵尊 · 草木甘霖奶量增伤',
        'rarity': 5,
        'element': '自然 · 治愈神侍',
        'weapon_type': '专属圣物: 永恒圣杯',
        'region': '世界树之冠',
        'arkhe': '生机焕发',
        'hp': 3550, 'atk': 300, 'def': 225, 'crit': '8%', 'spd': 106,
        'hp_max': 20500000, 'atk_max': 1600000, 'def_max': 1120000, 'crit_max': '25%', 'spd_max': 146,
        'skills': [
            {'name': '世界树之赐 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '群体回血/增伤', 'description': '召唤生命光雨，回复全员生命，并根据超量治疗转化为全员25%伤害加成。'},
            {'name': '生生不息 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '群体复苏/全属性提升', 'description': '唤醒古树神魂，使己方全员获得持续3回合的持续生命恢复，且全属性提升30%！'}
        ],
        'passive': '友方受到致命伤害时，自动为其锁血1点并立即触发一次满额治疗。',
        'constellations': [
            {'rank': '1痕', 'name': '灵种发芽', 'desc': '溢出的治疗量100%转化为护盾。'},
            {'rank': '2痕', 'name': '自然律动', 'desc': '被动锁血触发后该友军获得1回合无敌。'},
            {'rank': '3痕', 'name': '森林庇护', 'desc': '大招持续回血量提升50%。'},
            {'rank': '4痕', 'name': '蔓藤荆棘', 'desc': '受到近战攻击时使攻击者定身1回合。'},
            {'rank': '5痕', 'name': '神木之灵', 'desc': '全队自然属性英雄生命上限提升30%。'},
            {'rank': '6痕', 'name': '生机永驻', 'desc': '伊格拉在场时，全队受治疗与护盾效果翻倍。'}
        ],
        'mechanic': '平民与高难通关神器：超高治疗量转化全队增伤，0痕即可上阵。',
        'recs': {'bis_weapon': '永恒圣杯', 'bis_rune': '生命回响 4 件套 + 神圣屏障 2 件套'}
    },
    {
        'key': 'change',
        'name': '嫦娥 (Chang\'e)',
        'title': '广寒仙子 · 月宫清辉群体沉睡',
        'rarity': 5,
        'element': '流水 · 月宫玄仙',
        'weapon_type': '专属圣物: 灵霄玄天镜',
        'region': '广寒宫',
        'arkhe': '月影婆娑',
        'hp': 3250, 'atk': 350, 'def': 195, 'crit': '12%', 'spd': 114,
        'hp_max': 18000000, 'atk_max': 1800000, 'def_max': 950000, 'crit_max': '32%', 'spd_max': 156,
        'skills': [
            {'name': '广寒清风 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '减速/驱散', 'description': '挥动轻纱拂过敌阵，驱散前排所有增益状态并降低其30%攻击速度。'},
            {'name': '月华梦境 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '群体沉睡/伤害加深', 'description': '引动月宫寒光照耀战场，对敌方全体造成400%伤害并施加【沉睡】2回合（无法行动且受到的伤害提升40%）。'}
        ],
        'passive': '友方攻击处于沉睡状态的敌人时，不会打破沉睡并造成暴击。',
        'constellations': [
            {'rank': '1痕', 'name': '玉兔呈祥', 'desc': '开局使敌方攻击最高的单位直接陷入沉睡。'},
            {'rank': '2痕', 'name': '霓裳羽衣', 'desc': '自身闪避率提升30%，闪避后回复20点怒气。'},
            {'rank': '3痕', 'name': '寒宫月影', 'desc': '大招沉睡概率提升至100%。'},
            {'rank': '4痕', 'name': '月华净化', 'desc': '友军受控时自动释放月华为其解控。'},
            {'rank': '5痕', 'name': '太阴之息', 'desc': '全队受到水/月系伤害降低30%。'},
            {'rank': '6痕', 'name': '绝代仙华', 'desc': '大招结算时对所有苏醒目标造成800%梦境破碎真伤。'}
        ],
        'mechanic': '强力群体睡眠控制：限制敌方行动，为己方主C争取输出窗口。',
        'recs': {'bis_weapon': '灵霄玄天镜', 'bis_rune': '怒气压制 4 件套 + 疾风连击 2 件套'}
    },
    {
        'key': 'sphinx',
        'name': '斯芬克斯 (Sphinx)',
        'title': '风之谜灵 · 狮身沉默风暴控场',
        'rarity': 5,
        'element': '疾风 · 远古神兽',
        'weapon_type': '专属圣物: 太阳神圣翼',
        'region': '古漠金字塔',
        'arkhe': '风暴谜语',
        'hp': 3400, 'atk': 390, 'def': 205, 'crit': '15%', 'spd': 121,
        'hp_max': 18800000, 'atk_max': 2050000, 'def_max': 1020000, 'crit_max': '42%', 'spd_max': 166,
        'skills': [
            {'name': '狂风利爪 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '击退/破甲', 'description': '双爪撕裂狂风扑击，击退目标并造成340%风伤，同时破除其30%护甲。'},
            {'name': '致命谜语风暴 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '群体沉默/技能封锁', 'description': '召唤灭世龙卷风肆虐敌阵，对敌方全体造成480%风属性伤害，并施加长达2回合的【绝对沉默】！'}
        ],
        'passive': '被沉默的敌方单位受到的所有伤害提升35%，且无法闪避任何攻击。',
        'constellations': [
            {'rank': '1痕', 'name': '沙漠之眼', 'desc': '暴击率提升15%，开局获得30点怒气。'},
            {'rank': '2痕', 'name': '风暴锁链', 'desc': '沉默结束时目标受到其已损生命20%的额外伤害。'},
            {'rank': '3痕', 'name': '神兽威严', 'desc': '大招伤害提升40%。'},
            {'rank': '4痕', 'name': '狂风护体', 'desc': '受到暴击伤害降低50%。'},
            {'rank': '5痕', 'name': '狮王咆哮', 'desc': '绝技升级为攻击一列敌方目标。'},
            {'rank': '6痕', 'name': '虚空风暴', 'desc': '大招使敌方全体护甲清零，持续2回合。'}
        ],
        'mechanic': '前排群体沉默核心：直接封锁敌方绝技与被动触发，压制法系阵容。',
        'recs': {'bis_weapon': '太阳神圣翼', 'bis_rune': '疾风连击 4 件套 + 爆裂 2 件套'}
    },
    {
        'key': 'titan',
        'name': '泰坦 (Titan)',
        'title': '远古泰坦 · 钢铁巨壁反震眩晕',
        'rarity': 5,
        'element': '大地 · 重装巨神',
        'weapon_type': '专属圣物: 泰坦神盾',
        'region': '泰坦巨峰',
        'arkhe': '不动明王',
        'hp': 4500, 'atk': 220, 'def': 290, 'crit': '5%', 'spd': 95,
        'hp_max': 28000000, 'atk_max': 1100000, 'def_max': 1550000, 'crit_max': '15%', 'spd_max': 130,
        'skills': [
            {'name': '巨岩重踏 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '群体眩晕/破甲', 'description': '重踏大地掀起石浪，对前排造成280%土系伤害并有50%概率眩晕1回合。'},
            {'name': '泰坦神壁 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '巨额护盾/反震真伤', 'description': '展开远古神壁，为全体友军生成自身最大生命45%的坚石护盾，护盾受击反弹30%真实伤害！'}
        ],
        'passive': '受到的单次伤害最多不超过自身最大生命的15%，杜绝被任何刺客秒杀。',
        'constellations': [
            {'rank': '1痕', 'name': '大地共鸣', 'desc': '护盾受击反震伤害提升至50%。'},
            {'rank': '2痕', 'name': '坚岩之躯', 'desc': '防御力提升35%，免疫击退与浮空。'},
            {'rank': '3痕', 'name': '重盾无双', 'desc': '大招护盾量提升至最大生命的60%。'},
            {'rank': '4痕', 'name': '山岳守护', 'desc': '后排友军减伤提升20%。'},
            {'rank': '5痕', 'name': '巨人之怒', 'desc': '护盾破碎时对全屏敌人造成600%反伤冲击。'},
            {'rank': '6痕', 'name': '大地不灭', 'desc': '全队处于护盾保护下时免疫所有减益状态。'}
        ],
        'mechanic': '极致防爆坦克：单次伤害锁血，反弹真伤重创敌方刺客。',
        'recs': {'bis_weapon': '泰坦神盾', 'bis_rune': '神圣屏障 4 件套 + 生命回响 2 件套'}
    },
    {
        'key': 'luoshen',
        'name': '洛神 (Goddess Luo)',
        'title': '凌波仙女 · 水润万物净化解控',
        'rarity': 5,
        'element': '流水 · 洛水洛仙',
        'weapon_type': '专属圣物: 灵霄玄天镜',
        'region': '洛水仙境',
        'arkhe': '凌波微步',
        'hp': 3300, 'atk': 310, 'def': 205, 'crit': '10%', 'spd': 115,
        'hp_max': 18800000, 'atk_max': 1680000, 'def_max': 1050000, 'crit_max': '30%', 'spd_max': 160,
        'skills': [
            {'name': '洛水波澜 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '水流涤荡/净化', 'description': '召唤洛水清泉涤荡友军，驱散其身上的全部减速与冰冻，并回复20%已损生命。'},
            {'name': '水月惊鸿 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全队解控/免控屏障', 'description': '化身惊鸿拂过全场，清除己方全体所有负面状态与控制，并赋予持续2回合的水灵免控屏障！'}
        ],
        'passive': '友方只要成功清除负面状态，该友军攻击力与暴击率提升20%，持续2回合。',
        'constellations': [
            {'rank': '1痕', 'name': '翩若惊鸿', 'desc': '自身闪避率提升25%，闪避时为全队回血。'},
            {'rank': '2痕', 'name': '婉若游龙', 'desc': '大招消耗怒气减少20点。'},
            {'rank': '3痕', 'name': '洛水神韵', 'desc': '治疗效果提升40%。'},
            {'rank': '4痕', 'name': '水月镜花', 'desc': '为全队提供20%水属性与全元素抗性。'},
            {'rank': '5痕', 'name': '春水回潮', 'desc': '受到致命伤害时自动进入虚无状态2回合。'},
            {'rank': '6痕', 'name': '神洛降世', 'desc': '全队处于水灵屏障下时，造成的所有伤害提升35%。'}
        ],
        'mechanic': '顶级净化解控核心：彻底破解减怒队与冰冻控制流。',
        'recs': {'bis_weapon': '灵霄玄天镜', 'bis_rune': '生命回响 4 件套 + 神圣屏障 2 件套'}
    },
    {
        'key': 'hela',
        'name': '海拉 (Hela)',
        'title': '冥府主宰 · 死亡凋零禁疗收割',
        'rarity': 5,
        'element': '暗夜 · 冥府女皇',
        'weapon_type': '专属圣物: 弑神之刃',
        'region': '冥府幽渊',
        'arkhe': '死亡宣告',
        'hp': 3100, 'atk': 480, 'def': 180, 'crit': '20%', 'spd': 118,
        'hp_max': 17200000, 'atk_max': 2550000, 'def_max': 860000, 'crit_max': '58%', 'spd_max': 164,
        'skills': [
            {'name': '死亡之手 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '禁疗/持续扣血', 'description': '召唤幽魂之爪撕裂目标，造成360%暗伤并施加不可驱散的【禁疗】（无法回复生命）。'},
            {'name': '冥界风暴 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏凋零/残血收割', 'description': '开启冥界大门，对敌方全体造成520%死亡伤害；目标生命越低伤害越高，最高造成3倍额外伤害！'}
        ],
        'passive': '敌方阵亡任意单位，海拉立即恢复30点怒气并提高15%攻击力。',
        'constellations': [
            {'rank': '1痕', 'name': '黄泉路引', 'desc': '禁疗效果扩散至目标周围单位。'},
            {'rank': '2痕', 'name': '冥火附刃', 'desc': '普攻附加目标已损生命15%的真实伤害。'},
            {'rank': '3痕', 'name': '亡者哀鸣', 'desc': '大招伤害提升45%。'},
            {'rank': '4痕', 'name': '凋零诅咒', 'desc': '敌方死亡时对全体敌方造成自爆伤害。'},
            {'rank': '5痕', 'name': '灵魂收割', 'desc': '击杀目标后直接刷新大招冷却。'},
            {'rank': '6痕', 'name': '冥界君临', 'desc': '敌方全员生命恢复效果永久降低80%。'}
        ],
        'mechanic': '奶妈队克星：强效禁疗遏制敌方续航，残血极高爆发收割。',
        'recs': {'bis_weapon': '弑神之刃', 'bis_rune': '虚空噬魂 4 件套 + 爆裂 2 件套'}
    },
    {
        'key': 'tamamo',
        'name': '玉藻前 (Tamamo no Mae)',
        'title': '绝代妖狐 · 六回合循环技能永动',
        'rarity': 5,
        'element': '百妖 · 九尾天狐',
        'weapon_type': '专属圣物: 月神吊坠',
        'region': '青丘妖界',
        'arkhe': '九尾神算',
        'hp': 3200, 'atk': 420, 'def': 185, 'crit': '18%', 'spd': 124,
        'hp_max': 17800000, 'atk_max': 2250000, 'def_max': 910000, 'crit_max': '48%', 'spd_max': 168,
        'skills': [
            {'name': '狐火连珠 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '多段法伤/回怒', 'description': '吐出5道青丘狐火随机轰炸敌人，造成400%妖力法伤，每道狐火命中回复全队5点怒气。'},
            {'name': '九尾天妖阵 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '循环充能/全队重置', 'description': '展开六回合神算天狐阵，为己方全员瞬间充能50点怒气，并使全队绝技冷却减少1回合！'}
        ],
        'passive': '六回合循环机制：第6回合全队技能伤害提升100%，且怒气获取效率翻倍。',
        'constellations': [
            {'rank': '1痕', 'name': '灵狐巧变', 'desc': '开局全队获得30点初始怒气。'},
            {'rank': '2痕', 'name': '魅惑狐瞳', 'desc': '受击时有35%概率令攻击者眩晕1回合。'},
            {'rank': '3痕', 'name': '青丘妖法', 'desc': '大招充能怒气提升至70点。'},
            {'rank': '4痕', 'name': '天狐之怒', 'desc': '狐火对主C暴击伤害提升40%。'},
            {'rank': '5痕', 'name': '妖圣无双', 'desc': '全队百妖阵营英雄攻击力提升30%。'},
            {'rank': '6痕', 'name': '永动神环', 'desc': '大招施放后自身立刻恢复100点怒气。'}
        ],
        'mechanic': '六回合循环核心电池：配合卡米拉单C实现大招无缝连发。',
        'recs': {'bis_weapon': '月神吊坠', 'bis_rune': '疾风连击 4 件套 + 怒气压制 2 件套'}
    },
    {
        'key': 'ikamonkey',
        'name': '伊卡猴 (Ika Monkey)',
        'title': '虚空灵猴 · 千变分身当头棒击',
        'rarity': 5,
        'element': '虚空 · 斗战神明',
        'weapon_type': '专属圣物: 定海金箍',
        'region': '花果虚空',
        'arkhe': '齐天斗战',
        'hp': 3450, 'atk': 440, 'def': 210, 'crit': '16%', 'spd': 116,
        'hp_max': 19200000, 'atk_max': 2300000, 'def_max': 1020000, 'crit_max': '45%', 'spd_max': 158,
        'skills': [
            {'name': '分身突袭 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '召唤分身/分担伤害', 'description': '拔毫毛召唤2个拥有自身60%属性的分身共同战斗，分身能继承全部普攻特效。'},
            {'name': '乾坤一棒 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '巨额破防/直线定身', 'description': '金箍棒化作参天巨柱凌空砸下，对一整列敌人造成620%暴击物理伤害并定身2回合！'}
        ],
        'passive': '拥有2个以上分身在场时，本体受到伤害降低40%，且暴击伤害提升35%。',
        'constellations': [
            {'rank': '1痕', 'name': '猴王灵动', 'desc': '分身属性继承比例提升至85%。'},
            {'rank': '2痕', 'name': '金刚不坏', 'desc': '免疫所有控制状态，生命低于30%时生成巨额护盾。'},
            {'rank': '3痕', 'name': '惊天一棍', 'desc': '大招伤害倍率提升50%。'},
            {'rank': '4痕', 'name': '幻影迷踪', 'desc': '分身消亡时对周围敌人造成自爆真实伤害。'},
            {'rank': '5痕', 'name': '斗战胜佛', 'desc': '本体击杀目标立刻多召唤1个强力狂暴分身。'},
            {'rank': '6痕', 'name': '齐天破晓', 'desc': '大招100%打断敌方正在蓄力或准备释放的大招。'}
        ],
        'mechanic': '分身群殴战术：依靠分身吸收伤害与高伤定身，搅乱敌方阵型。',
        'recs': {'bis_weapon': '定海金箍', 'bis_rune': '爆裂 4 件套 + 疾风连击 2 件套'}
    },
    {
        'key': 'september',
        'name': '九月痕 (September Scar)',
        'title': '影刃刺客 · 多段突刺强效灭怒',
        'rarity': 5,
        'element': '暗夜 · 影忍刺杀',
        'weapon_type': '专属圣物: 弑神之刃',
        'region': '暗影孤岛',
        'arkhe': '九月幽痕',
        'hp': 3000, 'atk': 475, 'def': 170, 'crit': '22%', 'spd': 126,
        'hp_max': 16500000, 'atk_max': 2500000, 'def_max': 800000, 'crit_max': '62%', 'spd_max': 172,
        'skills': [
            {'name': '影刃疾风斩 (绝技)', 'type': 'NORMAL_ATTACK', 'scaling': '连击减怒/出血', 'description': '瞬间刺出4连击造成360%暗影伤害，每段暴击削减目标10点怒气并附加出血状态。'},
            {'name': '九痕断魂阵 (怒气大招)', 'type': 'ELEMENTAL_BURST', 'scaling': '单体绝杀/清空怒气', 'description': '结印锁定敌方主C，化作九道残影穿梭斩击，造成780%巨额单体伤害并彻底清空其全部怒气！'}
        ],
        'passive': '对怒气低于50点的敌人，九月痕攻击暴击率提升30%，并造成40%额外真实伤害。',
        'constellations': [
            {'rank': '1痕', 'name': '残月初痕', 'desc': '大招清空怒气后，使其下回合回怒效率降低80%。'},
            {'rank': '2痕', 'name': '影遁瞬闪', 'desc': '击杀目标后立即刷新绝技。'},
            {'rank': '3痕', 'name': '九刃归一', 'desc': '大招伤害倍率提升45%。'},
            {'rank': '4痕', 'name': '泣血刺痕', 'desc': '出血伤害翻倍，且出血状态无法被驱散。'},
            {'rank': '5痕', 'name': '灭度幽芒', 'desc': '暴击伤害提升50%。'},
            {'rank': '6痕', 'name': '终焉夜影', 'desc': '开局必定首位出手并无消耗施放一次大招。'}
        ],
        'mechanic': '减怒队强力辅C：与雪女配合实战，精准压制敌方核心怒气。',
        'recs': {'bis_weapon': '弑神之刃', 'bis_rune': '怒气压制 4 件套 + 爆裂 2 件套'}
    }
]

RELIC_DEFINITIONS = [
    {
        'name': '终焉之眼 (Eye of Extinction)',
        'type': '虚空限定圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/eye_of_extinction.svg',
        'base_atk': 350000,
        'sub_stat': '暴击率 +28.5% · 暴击伤害 +65%',
        'refine': '虚空裁决：青龙专属。造成的暴击伤害无视目标50%护盾与防御，击杀目标后吸取其全部剩余怒气。',
        'ascension_materials': '虚空结晶、终焉神石'
    },
    {
        'name': '永恒圣杯 (Eternal Grail)',
        'type': '神圣限定圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/eternal_grail.svg',
        'base_atk': 220000,
        'sub_stat': '生命上限 +35% · 治疗效果 +40%',
        'refine': '神圣恩赐：战斗开局全队获得30点初始怒气与等同生命上限30%的屏障，持续整场。',
        'ascension_materials': '圣洁之水、天使羽毛'
    },
    {
        'name': '寒冰雪花片 (Frost Snowflake)',
        'type': '极地专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/frost_snowflake.svg',
        'base_atk': 280000,
        'sub_stat': '效果命中 +35% · 冰霜伤害 +45%',
        'refine': '极霜侵袭：雪女专属。冰冻触发概率翻倍，攻击处于受控状态的敌人时减怒效果提升100%。',
        'ascension_materials': '万年玄冰、凛冬碎晶'
    },
    {
        'name': '炎魔炽羽 (Blazing Plume)',
        'type': '熔岩专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/blazing_plume.svg',
        'base_atk': 360000,
        'sub_stat': '攻击力 +32% · 火焰伤害 +50%',
        'refine': '红莲爆发：沃尔卡/凤凰专属。灼烧叠加上限由5层提升至10层，引爆时额外造成50%真伤。',
        'ascension_materials': '炎魔之角、烈焰核心'
    },
    {
        'name': '弑神之刃 (Godslayer Blade)',
        'type': '暗杀专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/godslayer_blade.svg',
        'base_atk': 380000,
        'sub_stat': '暴击伤害 +70% · 护甲穿透 +30%',
        'refine': '残血斩杀：卡米拉/露娜专属。对生命低于35%的目标造成的所有伤害提升100%并无视护盾。',
        'ascension_materials': '暗影精魄、饮血石'
    },
    {
        'name': '泰坦神盾 (Aegis of Titan)',
        'type': '守护专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/aegis_of_titan.svg',
        'base_atk': 180000,
        'sub_stat': '防御力 +45% · 伤害减免 +25%',
        'refine': '不动巨峰：泰坦/饕餮专属。自身生成的护盾厚度提升60%，受到攻击时反震30%真实伤害。',
        'ascension_materials': '泰坦重岩、金刚原矿'
    },
    {
        'name': '月神吊坠 (Lunaria Pendant)',
        'type': '神明专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/lunaria_pendant.svg',
        'base_atk': 240000,
        'sub_stat': '速度 +35 · 初始怒气 +25',
        'refine': '月夜幽影：辉夜姬/玉藻前专属。受击时偷取攻击者15点怒气转给自己，且释放技能后怒气保留20点。',
        'ascension_materials': '月之碎屑、幽光宝玉'
    },
    {
        'name': '混沌法球 (Orb of Chaos)',
        'type': '混沌凶兽圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/orb_of_chaos.svg',
        'base_atk': 210000,
        'sub_stat': '生命上限 +40% · 异常抗性 +50%',
        'refine': '万象吞噬：饕餮专属。受到致命伤害时免疫并进入暴食状态，将受到的下三次攻击转化为治疗。',
        'ascension_materials': '混沌黑核、凶兽獠牙'
    },
    {
        'name': '太阳神圣翼 (Wings of Ra)',
        'type': '光辉专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/wings_of_ra.svg',
        'base_atk': 260000,
        'sub_stat': '全属性 +18% · 全队减伤 +15%',
        'refine': '神翼庇护：荷鲁斯/斯芬克斯专属。位于助战位时，首回合必定触发全队全员免控。',
        'ascension_materials': '太阳真金、荷鲁斯神辉'
    },
    {
        'name': '虚空破晓矛 (Void Dawn Spear)',
        'type': '裁决专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/void_dawn_spear.svg',
        'base_atk': 370000,
        'sub_stat': '对护盾伤害 +150% · 穿透 +35%',
        'refine': '圣辉神断：雅典娜专属。攻击破除护盾后引发全屏圣光爆炸，对敌方全体造成400%真实伤害。',
        'ascension_materials': '破晓神铁、虚空星尘'
    },
    {
        'name': '灵霄玄天镜 (Lingxiao Mirror)',
        'type': '仙灵专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/lingxiao_mirror.svg',
        'base_atk': 230000,
        'sub_stat': '效果抵抗 +60% · 冷却缩减 +15%',
        'refine': '清辉涤浊：嫦娥/洛神专属。友方受到控制时有80%概率自动净化解控（每回合触发3次）。',
        'ascension_materials': '九天玄玉、仙泉灵露'
    },
    {
        'name': '定海金箍 (Subduing Hoop)',
        'type': '斗战专属圣物',
        'rarity': 5,
        'icon_url': '/games/pixel_relics/subduing_hoop.svg',
        'base_atk': 350000,
        'sub_stat': '暴击率 +25% · 击退效果 +50%',
        'refine': '定海乾坤：伊卡猴专属。大招暴击时必定将目标眩晕2回合，且分身攻击力提升50%。',
        'ascension_materials': '天外神铁、如意金晶'
    }
]

RUNE_DEFINITIONS = [
    {
        'name': '爆裂符文套 (Burst Rune Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'icon_url': '/games/pixel_runes/burst_set.svg',
        'two_piece_bonus': '暴击率 +15%',
        'four_piece_bonus': '暴击伤害 +50%，攻击触发暴击时追加 20% 真实伤害，不吃防御与护盾减免。',
        'pieces': ['爆裂印记·天', '爆裂印记·地', '爆裂印记·玄', '爆裂印记·黄'],
        'rules_reference': {'适用职业': '输出主C (青龙/沃尔卡/卡米拉/露娜)', '强化方向': '暴击率、暴击伤害、攻击力%'}
    },
    {
        'name': '怒气压制套 (Rage Suppress Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'icon_url': '/games/pixel_runes/rage_suppress_set.svg',
        'two_piece_bonus': '效果命中 +20%',
        'four_piece_bonus': '释放怒气技后，削减敌方全体 25 点怒气，并使其受到的伤害提升 15%，持续 2 回合。',
        'pieces': ['压制符石·阳', '压制符石·阴', '压制符石·乾', '压制符石·坤'],
        'rules_reference': {'适用职业': '控场/减怒 (辉夜姬/雪女/斯芬克斯/九月痕)', '强化方向': '效果命中、速度、生命值%'}
    },
    {
        'name': '神圣屏障套 (Divine Barrier Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'icon_url': '/games/pixel_runes/divine_barrier_set.svg',
        'two_piece_bonus': '生命上限 +20%',
        'four_piece_bonus': '战斗开局为全体友军生成等同自身最大生命 35% 的神圣屏障，持续 3 回合，屏障破裂时全员回血15%。',
        'pieces': ['圣障之护·生', '圣障之护·死', '圣障之护·荣', '圣障之护·枯'],
        'rules_reference': {'适用职业': '重装坦克/护盾辅助 (泰坦/饕餮/凤凰/维纳斯)', '强化方向': '生命值%、防御力%、抗性'}
    },
    {
        'name': '疾风连击套 (Gale Combo Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'icon_url': '/games/pixel_runes/gale_combo_set.svg',
        'two_piece_bonus': '攻击速度 +25%',
        'four_piece_bonus': '普通攻击有 35% 概率立即追击一次无消耗绝技，并获得 15 点怒气。',
        'pieces': ['连击迅印·风', '连击迅印·雷', '连击迅印·云', '连击迅印·雨'],
        'rules_reference': {'适用职业': '连击型辅C/刺客 (玉藻前/斯芬克斯/伊卡猴)', '强化方向': '速度、攻击力、破甲'}
    },
    {
        'name': '虚空噬魂套 (Void Soul Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'icon_url': '/games/pixel_runes/void_soul_set.svg',
        'two_piece_bonus': '护甲穿透 +18%',
        'four_piece_bonus': '击杀任意敌方目标后，立即恢复 100 点满额怒气并提升 30% 攻击力，持续 2 回合。',
        'pieces': ['噬魂宝玉·魂', '噬魂宝玉·魄', '噬魂宝玉·灵', '噬魂宝玉·曜'],
        'rules_reference': {'适用职业': '残血收割刺客 (卡米拉/海拉/九月痕)', '强化方向': '攻击力%、暴击率、暴伤'}
    },
    {
        'name': '生命回响套 (Echo of Life Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'icon_url': '/games/pixel_runes/echo_of_life_set.svg',
        'two_piece_bonus': '受治疗效果 +25%',
        'four_piece_bonus': '释放治疗或护盾技能时，额外为目标驱散 1 个负面减益状态，并附加持续生命恢复。',
        'pieces': ['回春灵符·青', '回春灵符·赤', '回春灵符·白', '回春灵符·黑'],
        'rules_reference': {'适用职业': '纯奶妈/辅助 (伊格拉/洛神/维纳斯)', '强化方向': '治疗效果、生命%、效果抵抗'}
    }
]

MECHANIC_RULES = [
    {
        'category': '怒气循环与减怒压制机制',
        'title': 'Rage Engine & Energy Suppression (怒气引擎与封怒闭环)',
        'formula': '怒气上限 = 100 点 | 普攻回怒 = +25 点 | 受击回怒 = +10 点 | 绝技回怒 = +15~30 点',
        'parameters': {
            '核心机制': '角色怒气达到100点即可在回合内施放毁天灭地的终结大招。减怒队通过辉夜姬（扣除全员60怒并禁怒）+ 雪女（全屏冰冻减35怒）使敌方大招全场哑火。',
            '越战法则': '在战力落后数十亿的高难挑战中，只要精准压制敌方主C怒气，即可打破数值压制实现以弱胜强。'
        }
    },
    {
        'category': '护盾屏障与破盾斩杀法则',
        'title': 'Shield Barrier & Slay Threshold (屏障厚度与无视防斩杀)',
        'formula': '受伤害 = min(伤害量, 屏障值) 先扣屏障 | 卡米拉斩杀条件 = 目标HP < 35% 时触发斩杀',
        'parameters': {
            '屏障吸收': '屏障等同于第二生命条，普通伤害被屏障全额吸收；破盾英雄（雅典娜）对屏障造成300%特化破坏伤害。',
            '无视斩杀': '卡米拉、海拉等刺客的斩杀技能无视护盾屏障直接判定本体剩余血量，达到斩杀线一击必杀。'
        }
    },
    {
        'category': '元素相克与阵奕光环羁绊',
        'title': 'Elemental Triangle & Synergy Aura (五行克制与阵营共鸣)',
        'formula': '克制关系 = 火克冰 (增伤100%) -> 冰克雷 (增伤30%) -> 雷克火 (增伤20%) | 光暗虚空互相克制',
        'parameters': {
            '火克冰法则': '火系爆发（沃尔卡+凤凰）对冰系敌人造成双倍火伤且免疫冰冻，形成绝对克制。',
            '阵奕羁绊': '上阵同阵营英雄激活阵奕光环：3神明全队生命+15%，3虚空全队暴伤+25%，5同系全员攻击+30%、免伤+20%。'
        }
    },
    {
        'category': '助战系统与神兽护佑法则',
        'title': 'Support Assist & Sacred Beast Blessing (外援助战与神兽庇佑)',
        'formula': '助战位效果 = 不占上场人数，第1/3/5回合开局自动施放被动光环与援护特技',
        'parameters': {
            '荷鲁斯助战': '将荷鲁斯置于助战位，无需亲自登场承受伤害，即可在开局提供全队免控与太阳神辉减伤。',
            '神兽加成': '黄金圣狮、青鸾神兽提供全局属性光环，并在首回合清除己方减速与负面减益。'
        }
    }
]


def register_game_if_not_exists():
    """Ensure Game 32 exists in game table."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO game (id, name, alias, platform, category, cover_url, description, current_version, created_at, updated_at)
                VALUES (
                    32,
                    '指尖像素城',
                    'Pixel City/指尖像素/像素城',
                    '移动端 (微信小游戏/iOS/Android)',
                    '放置卡牌RPG',
                    '/games/pixel_city/cover.svg',
                    '超人气像素风策略放置卡牌手游。以神话与虚空异界为背景，融合阵奕布阵、怒气循环博弈、破盾斩杀与专属圣物体系。玩家可自由搭配青龙、辉夜姬、雅典娜等数十位SP神将，越战挑战通天塔、阵奕虚空与跨服竞技巅峰赛！',
                    'V2.4.0 虚空降临',
                    NOW(), NOW()
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    alias = EXCLUDED.alias,
                    platform = EXCLUDED.platform,
                    category = EXCLUDED.category,
                    cover_url = EXCLUDED.cover_url,
                    description = EXCLUDED.description,
                    current_version = EXCLUDED.current_version,
                    updated_at = NOW();
            """)
            cur.execute("SELECT setval('game_id_seq', GREATEST((SELECT MAX(id) FROM game), 32));")
            conn.commit()
            print('[Pixel City] Game 32 metadata registered.')
    finally:
        conn.close()


def crawl_and_sync_pixel_city(game_id=32):
    print(f'[Pixel City] Preparing 20 Heroes, 12 Relics, 6 Runes & 4 Mechanics for Game {game_id} ...')

    register_game_if_not_exists()

    characters = []
    for h in HERO_DEFINITIONS:
        stages = [
            {'level': '初入像素城 (Lv.1)', 'hp': h['hp'], 'atk': h['atk'], 'def': h['def'], 'crit': h['crit'], 'speed': h['spd'], 'spd': h['spd']},
            {'level': '通天启蒙 (Lv.100)', 'hp': int(h['hp_max'] * 0.05), 'atk': int(h['atk_max'] * 0.05), 'def': int(h['def_max'] * 0.05), 'crit': '25%', 'speed': h['spd'] + 10, 'spd': h['spd'] + 10},
            {'level': '阵奕试炼 (Lv.200)', 'hp': int(h['hp_max'] * 0.20), 'atk': int(h['atk_max'] * 0.20), 'def': int(h['def_max'] * 0.20), 'crit': '35%', 'speed': h['spd'] + 20, 'spd': h['spd'] + 20},
            {'level': '虚空涅槃 (Lv.300)', 'hp': int(h['hp_max'] * 0.55), 'atk': int(h['atk_max'] * 0.55), 'def': int(h['def_max'] * 0.55), 'crit': '45%', 'speed': h['spd'] + 30, 'spd': h['spd'] + 30},
            {'level': '巅峰封神 (Lv.400)', 'hp': h['hp_max'], 'atk': h['atk_max'], 'def': h['def_max'], 'crit': h['crit_max'], 'speed': h['spd_max'], 'spd': h['spd_max']}
        ]

        characters.append({
            'name': h['name'],
            'title': h['title'],
            'rarity': h['rarity'],
            'element': h['element'],
            'weapon_type': h['weapon_type'],
            'region': h['region'],
            'arkhe': h['arkhe'],
            'avatar_url': f'/games/pixel_city/{h["key"]}.svg',
            'splash_url': f'/games/pixel_city/{h["key"]}.svg',
            'base_stats': stages,
            'special_ascension_stat': {'stat_name': '破阶特化', 'values': {'400级': f'{h["element"]}核心属性全翻倍'}},
            'ascension_materials': [{'tier': '破界阶梯', 'items': '星钻、进阶石、虚空神石、招募精魄'}],
            'talents': h['skills'],
            'passives': [{'name': '专属真神被动', 'description': h['passive']}],
            'constellations': h['constellations'],
            'special_mechanics': {'core_flow': h['mechanic']},
            'recommendations': {'weapons': {'bis': h['recs']['bis_weapon']}, 'artifacts': {'bis_set': h['recs']['bis_rune']}},
            'version': 'V2.4.0'
        })

    weapons = []
    for r in RELIC_DEFINITIONS:
        weapons.append({
            'name': r['name'],
            'type': r['type'],
            'rarity': r['rarity'],
            'icon_url': r['icon_url'],
            'base_atk_curve': [
                {'level': '1阶初解', 'atk': int(r['base_atk'] * 0.1), 'desc': '基础圣物解锁'},
                {'level': '5阶中成', 'atk': int(r['base_atk'] * 0.4), 'desc': '激活全属性提升'},
                {'level': '10阶满炼', 'atk': r['base_atk'], 'desc': '激活专属真神特效'}
            ],
            'sub_stat': {'bonus': r['sub_stat']},
            'refinements': [{'rank': '专属特效', 'desc': r['refine']}],
            'ascension_materials': [{'tier': '圣物精炼', 'material': r['ascension_materials']}],
            'version': 'V2.4.0'
        })

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    a_count = upsert_artifacts(game_id, RUNE_DEFINITIONS)
    m_count = upsert_mechanics(game_id, MECHANIC_RULES)
    print(f'[Pixel City] Successfully synced into Game {game_id}: {c_count} heroes, {w_count} relics, {a_count} rune sets, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_pixel_city(32)
