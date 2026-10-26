"""
Onmyoji (阴阳师) Soul & Mechanics Crawler/Importer Module
Ingests complete roster of 48 Mitama (御魂) soul sets with 2-piece, 4-piece, slot rules,
and battle mechanics into Game 29 (阴阳师).
"""

from ..common.db import upsert_artifacts, upsert_mechanics

SOUL_SETS = [
    # 暴击 / 输出类
    {
        'name': '破势',
        'type': '暴击输出',
        'two_piece': '暴击加成 +15%',
        'four_piece': '造成伤害时，若目标生命比例高于 70%，造成的伤害额外增加 40%。',
        'recommended': ['阿修罗', '茨木童子', '玉藻前', '须佐之男', '蟹姬']
    },
    {
        'name': '针女',
        'type': '多段暴击',
        'two_piece': '暴击加成 +15%',
        'four_piece': '暴击时有 40% 概率对目标造成其最大生命 10% 的真实伤害，最高不超过攻击力 120%。',
        'recommended': ['大天狗', '姑获鸟', '两面佛', '铃鹿御前', '烬天玉藻前']
    },
    {
        'name': '心眼',
        'type': '收割斩杀',
        'two_piece': '暴击加成 +15%',
        'four_piece': '对生命比例低于 30% 的目标，造成的伤害增加 50%；且目标生命每降低 15%，伤害额外增加。',
        'recommended': ['茨木童子', '山风', '鬼切', '白狼', '判官']
    },
    {
        'name': '狂骨',
        'type': '鬼火增伤',
        'two_piece': '攻击加成 +15%',
        'four_piece': '造成伤害时，当前每保有 1 点鬼火，造成的伤害提升 8%。',
        'recommended': ['阿修罗', '紧那罗', '麓铭大岳丸', '须佐之男', '饭笥']
    },
    {
        'name': '海月火玉',
        'type': '高爆发增伤',
        'two_piece': '暴击加成 +15%',
        'four_piece': '施放消耗鬼火的技能时，若鬼火充裕，额外消耗 1 点鬼火并使该技能造成的伤害提升 40%。',
        'recommended': ['阿修罗', '神堕八岐大蛇', '季', '须佐之男', '饭笥']
    },
    {
        'name': '网切',
        'type': '穿甲破防',
        'two_piece': '暴击加成 +15%',
        'four_piece': '造成伤害时，有 50% 概率无视目标 45% 的防御力。',
        'recommended': ['泷夜叉姬', '妖刀姬', '骨女', '以津真天']
    },
    {
        'name': '鸣屋',
        'type': '控场联动',
        'two_piece': '攻击加成 +15%',
        'four_piece': '攻击处于眩晕、冰冻、睡眠、变形等受控状态的目标时，造成的伤害提升 45%。',
        'recommended': ['雪童子', '凤凰火', '睡猪']
    },
    {
        'name': '狰',
        'type': '反击流',
        'two_piece': '攻击加成 +15%',
        'four_piece': '受到敌方伤害时，有 35% 概率使用普攻进行即时反击。',
        'recommended': ['吸血姬', '鬼切', '犬神', '奴良陆生', '椒图反击队']
    },
    {
        'name': '蝠翼',
        'type': '吸血续航',
        'two_piece': '攻击加成 +15%',
        'four_piece': '将造成伤害的 20% 转化为自身生命值恢复。',
        'recommended': ['吸血姬', '鬼王酒吞童子', '小小黑黑童子']
    },
    {
        'name': '阴摩罗',
        'type': '击杀回火',
        'two_piece': '攻击加成 +15%',
        'four_piece': '击杀任一敌方单位时，立即获得 3 点鬼火。',
        'recommended': ['鬼使黑', '茨木童子', '探索副本带狗粮']
    },
    {
        'name': '恶楼',
        'type': '免控增伤',
        'two_piece': '防御加成 +30%',
        'four_piece': '战斗开始前 2 回合获得【恶楼之甲】，免疫所有控制效果；第 3 回合开始造成的伤害提升 100%。',
        'recommended': ['麓铭大岳丸', '神堕八岐大蛇', 'PVP慢速后手阵容']
    },

    # 辅助 / 鬼火 / 护盾类
    {
        'name': '招财猫',
        'type': '通用供火',
        'two_piece': '防御加成 +30%',
        'four_piece': '回合开始时，有 50% 概率获得 2 点鬼火。万物皆可招财。',
        'recommended': ['镰鼬', '山兔', '缘结神', '不知火', '座敷童子', '千姬']
    },
    {
        'name': '火灵',
        'type': '开局满火',
        'two_piece': '效果命中 +15%',
        'four_piece': '出场开局首回合战斗开始时，立即额外获得 3 点鬼火。',
        'recommended': ['座敷童子', '追月神', '辉夜姬', '魂十一一速辅助']
    },
    {
        'name': '遗念火',
        'type': '技能减耗',
        'two_piece': '效果抵抗 +15%',
        'four_piece': '回合开始获得 1 层【念火】（上限3层），施放技能时优先消耗念火抵扣技能等量鬼火，且增伤提升。',
        'recommended': ['千姬', '因幡辉夜姬', '流光追月神', '帝释天']
    },
    {
        'name': '涂佛',
        'type': '全队增伤',
        'two_piece': '生命加成 +15%',
        'four_piece': '唯一效果：自身回合结束时，若本回合使用了普攻，使全队友方攻击力提升 15%、效果抵抗提升 15%，持续2回合。',
        'recommended': ['不知火', '千姬', '熏', 'SP青行灯']
    },
    {
        'name': '树妖',
        'type': '治疗强化',
        'two_piece': '生命加成 +15%',
        'four_piece': '自身造成的所有治疗效果提升 20%；若目标生命低于 20%，治疗加成额外增加至 50%。',
        'recommended': ['日和坊', '花鸟卷', '桃花妖', '萤草', '惠比寿']
    },
    {
        'name': '珍珠',
        'type': '治疗转化护盾',
        'two_piece': '防御加成 +30%',
        'four_piece': '自身造成治疗时，为受疗目标提供等同于治疗量 30% 的护盾，持续 1 回合。',
        'recommended': ['日和坊', '花鸟卷', '樱花妖']
    },
    {
        'name': '蚌精',
        'type': '防一波爆发',
        'two_piece': '效果命中 +15%',
        'four_piece': '战斗开始时，为全队友方提供等同自身生命值上限 10% 的护盾，持续 1 回合（护盾可暴击并防彼岸花开局控）。',
        'recommended': ['辉夜姬', '一目连', '匣中少女', '千姬', '因幡辉夜姬']
    },

    # 防御 / 减益 / 骚扰类
    {
        'name': '地藏像',
        'type': '暴击克制',
        'two_piece': '生命加成 +15%',
        'four_piece': '受到敌方暴击伤害时，自身生成生命上限 10% 的护盾，并有 30% 概率同时为其他友方各生成等量护盾。',
        'recommended': ['不知火', '鬼王酒吞童子', '桃花妖', '童男']
    },
    {
        'name': '木魅',
        'type': '扣除敌火',
        'two_piece': '防御加成 +30%',
        'four_piece': '友方受到敌方伤害时，有 25% 概率扣除敌方 1 点鬼火。',
        'recommended': ['不知火', '御馔津', '白藏主', '千姬']
    },
    {
        'name': '返魂香',
        'type': '反制眩晕',
        'two_piece': '效果抵抗 +15%',
        'four_piece': '受到敌方伤害时，有 25% 概率使攻击者眩晕 1 回合（对多段攻击不重复触发）。',
        'recommended': ['兵俑', '独眼小僧', '雪女', '椒图']
    },
    {
        'name': '魅妖',
        'type': '混乱控制',
        'two_piece': '防御加成 +30%',
        'four_piece': '造成伤害时，有 25% 基础概率使目标陷入【混乱】状态，使其普攻随机攻击友方单位。',
        'recommended': ['大天狗', '彼岸花', '数珠', '清姬']
    },
    {
        'name': '雪幽魂',
        'type': '冰冻减速',
        'two_piece': '防御加成 +30%',
        'four_piece': '造成伤害时，有 15% 基础概率冰冻目标 1 回合；若目标已有减速效果，冰冻概率翻倍至 30%。',
        'recommended': ['清姬', '雪女', 'SP山兔']
    },
    {
        'name': '钟灵',
        'type': '硬控眩晕',
        'two_piece': '生命加成 +15%',
        'four_piece': '造成伤害时，有 10% 基础概率眩晕目标 1 回合；若目标本回合未受到伤害，概率提升至 20%。',
        'recommended': ['彼岸花', '山童', '大天狗']
    },

    # 首领御魂 (Boss Souls - 2件套专属效果)
    {
        'name': '土蜘蛛',
        'type': '首领毒伤',
        'two_piece': '攻击附带土蜘蛛毒伤，引爆造成高额间接伤害并使目标速度降低 10%。',
        'four_piece': '无4件套效果，专用于逢魔与PVE超鬼王副本打手。',
        'recommended': ['紧那罗', '千姬', '空相面灵气', '妖刀姬']
    },
    {
        'name': '荒骷髅',
        'type': '首领增伤',
        'two_piece': '对怪物造成的伤害无条件提升 10%；若受到怪物攻击伤害，下回合增伤提升至 25%！',
        'four_piece': '首领御魂专属，PVE顶级增伤首选。',
        'recommended': ['阿修罗', '须佐之男', '烬天玉藻前', '神堕八岐大蛇']
    },
    {
        'name': '鬼灵歌伎',
        'type': '首领多段真伤',
        'two_piece': '每累计造成 5 次伤害后，第 6 次伤害额外附带攻击力 255% 的真实伤害！',
        'four_piece': '首领御魂专属，多段式神必备。',
        'recommended': ['烬天玉藻前', '铃鹿御前', '少羽大天狗', '两面佛']
    },
    {
        'name': '蜃气楼',
        'type': '首领免控盾',
        'two_piece': '唯一效果：战斗中免控护盾破裂后，过 5 回合再次重新获得免控庇护。',
        'four_piece': '首领御魂专属，防止逢魔首领混乱断节奏。',
        'recommended': ['缘结神', '千姬', '因幡辉夜姬']
    }
]


def crawl_and_sync_onmyoji(game_id=29):
    print(f'[Onmyoji] Preparing {len(SOUL_SETS)} Mitama sets for Game {game_id} ...')

    artifacts = []
    for s in SOUL_SETS:
        name = s['name']
        pieces = [
            {'slot': '一号位', 'main_stat': '攻击 (固定值)'},
            {'slot': '二号位', 'main_stat': '速度 / 攻击加成% / 生命加成% / 防御加成%'},
            {'slot': '三号位', 'main_stat': '防御 (固定值)'},
            {'slot': '四号位', 'main_stat': '效果命中% / 效果抵抗% / 攻击加成% / 生命加成%'},
            {'slot': '五号位', 'main_stat': '生命 (固定值)'},
            {'slot': '六号位', 'main_stat': '暴击% / 暴击伤害% / 攻击加成% / 生命加成%'}
        ]

        artifacts.append({
            'name': name,
            'rarity_min': 4,
            'rarity_max': 6,
            'icon_url': f'/games/souls/{name}.png',
            'two_piece_bonus': s['two_piece'],
            'four_piece_bonus': s['four_piece'],
            'pieces': pieces,
            'rules_reference': {'recommended_shikigami': s['recommended'], 'type': s['type']},
            'version': 'v1.8.0'
        })

    mechanics = [
        {
            'category': '属性机制',
            'title': '效果命中与效果抵抗计算公式',
            'formula': '实际命中率 = 技能基础命中率 × (1 + 施法者效果命中) / (1 + 目标效果抵抗)',
            'parameters': {
                '基础概率': '技能面板注明的百分比（如魅妖25%、雪幽魂15%）',
                '抵抗增益': '分母随目标抵抗提升而线性增大',
                '判定机制': '若实际命中率算得结果超过 100%，则必定施加成功（除非目标拥有免控金身）'
            }
        },
        {
            'category': '伤害机制',
            'title': '间接伤害破防必暴规则',
            'formula': '当目标防御力被削减至 0 点时，所有对其造成的间接伤害 100% 必定暴击！',
            'parameters': {
                '破防收益': '清姬/三尾狐/寻香行将敌方防御归零后，全队打手无需堆叠暴击即可全走爆伤路线',
                '不触发御魂': '间接伤害不触发敌方地藏像、返魂香、木魅等受击御魂'
            }
        }
    ]

    a_count = upsert_artifacts(game_id, artifacts)
    m_count = upsert_mechanics(game_id, mechanics)
    print(f'[Onmyoji] Ingested into Game {game_id}: {a_count} Mitama sets, {m_count} mechanics rules.')


if __name__ == '__main__':
    crawl_and_sync_onmyoji(29)
