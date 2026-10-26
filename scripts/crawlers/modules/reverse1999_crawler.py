"""
Reverse: 1999 (重返未来：1999) Arcanists, Psychubes & Afflatus Crawler Module
Ingests 6-star and 5-star Arcanists (神秘学家), 6-star Psychubes (六星心相),
and Afflatus (四象灵智生克与律动机制) into Game 31 (重返未来：1999).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

ARCANISTS = [
    {
        'name': '37 (Thirty-Seven)',
        'title': '阿派朗学派圣女 · 数的真理',
        'rarity': 6,
        'element': '智 (Intellect)',
        'weapon_type': '几何算力',
        'region': '阿派朗学派 (Apeiron)',
        'arkhe': '灵光计数',
        'passive': '受数指引：友方造成额外行动/追击时积攒【灵光】；满 5 点灵光自动触发【补充算式】全屏本源真伤追击！',
        'skills': [
            {'name': '神秘术 · 三角法则', 'type': 'ELEMENTAL_SKILL', 'scaling': '群攻/本源创伤', 'description': '引动正四面体矩阵轰击 2 名敌方，造成精神创伤与高额额外本源真伤'},
            {'name': '神秘术 · 曲线映射', 'type': 'ELEMENTAL_SKILL', 'scaling': '自身坚固/增益', 'description': '获得【坚固】护盾并使全队暴击率提升 20%，持续 2 回合'},
            {'name': '至终仪式 · 数的显现', 'type': 'ELEMENTAL_BURST', 'scaling': '全队本源创伤加成', 'description': '显现真理几何神像，使全队进入【数之领地】，全队攻击附带 37% 本源伤害'}
        ]
    },
    {
        'name': '牙仙 (Tooth Fairy)',
        'title': '基金会牙医 · 暴击降抗人权奶妈',
        'rarity': 6,
        'element': '星 (Star)',
        'weapon_type': '乳齿收纳盒',
        'region': '拉普拉斯科算中心',
        'arkhe': '乳齿倾听',
        'passive': '乳牙收集：友方施放技能每造成一次暴击收集 1 颗乳牙；满 3 颗乳牙在回合开始自动投掷，降低全屏敌人 15% 抗暴率与 15% 暴击防御！',
        'skills': [
            {'name': '神秘术 · 齿音调弄', 'type': 'ELEMENTAL_SKILL', 'scaling': '单体创伤/混乱', 'description': '造成精神创伤，暴击后使目标陷入【明昧】状态降低受暴击门槛'},
            {'name': '神秘术 · 空腔药膏', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体治疗/驱散', 'description': '立即恢复全队高额生命值，若产生暴击净化全队全部减益状态！'},
            {'name': '至终仪式 · 坏齿童话', 'type': 'ELEMENTAL_BURST', 'scaling': '群体驱散/大暴击', 'description': '造成超强星属性精神创伤，暴击后净化友方全员所有受控异常状态'}
        ]
    },
    {
        'name': '露西 (Lucy)',
        'title': '首位智械共生 · 聚能超频主C',
        'rarity': 6,
        'element': '星 (Star)',
        'weapon_type': '聚变核心动力',
        'region': '拉普拉斯特别研发部',
        'arkhe': '超频电能',
        'passive': '电荷蓄积：敌方或友方退场时立即吸收电能获得【激昂】，大幅提升现实创伤与暴击伤害',
        'skills': [
            {'name': '神秘术 · 加速电荷', 'type': 'ELEMENTAL_SKILL', 'scaling': '现实创伤/弹射', 'description': '发射脉冲弹丸连续在敌阵中弹射穿透造成高额现实创伤'},
            {'name': '神秘术 · 动能充能', 'type': 'ELEMENTAL_SKILL', 'scaling': '自身暴击提升', 'description': '展开能量回旋力场，强化下回合技能出牌阶级'},
            {'name': '至终仪式 · 聚变之星', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏毁灭光炮', 'description': '超频蓄能轰出星云毁灭光束，消灭敌人后无消耗免费追击一次神秘术！'}
        ]
    },
    {
        'name': '伊索尔德 (Isolde)',
        'title': '维也纳歌剧首席 · 预燃激昂拐',
        'rarity': 6,
        'element': '灵 (Spirit)',
        'weapon_type': '血色歌剧花束',
        'region': '奥地利维也纳',
        'arkhe': '预热音符',
        'passive': '终幕前奏：每回合行动开始时为全体敌方施加【预燃】，热度达到阶段自动引爆全屏血色音符',
        'skills': [
            {'name': '神秘术 · 咏叹调', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体削减现实防御', 'description': '高亢歌声撕裂敌方防线，使敌方现实防御降低 25%'},
            {'name': '神秘术 · 独幕剧', 'type': 'ELEMENTAL_SKILL', 'scaling': '单体创伤/预燃', 'description': '造成现实创伤并根据预燃层数产生翻倍爆发伤害'},
            {'name': '至终仪式 · 爱的终曲', 'type': 'ELEMENTAL_BURST', 'scaling': '领域展开/终章引爆', 'description': '进入【终幕狂想】形态，此后友方每一次攻击均协同引爆音符爆鸣！'}
        ]
    },
    {
        'name': '槲寄生 (Druvis III)',
        'title': '林地守护者 · 永久石化控场',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '橡木古木长杖',
        'region': '森林同盟',
        'arkhe': '生灵石化',
        'passive': '林木生息：木属性友方享受生命吸血与再生加成',
        'skills': [
            {'name': '神秘术 · 风中絮语', 'type': 'ELEMENTAL_SKILL', 'scaling': '二阶石化硬控', 'description': '升至二阶或三阶出牌时，必定使目标陷入【石化】状态无法行动！'},
            {'name': '神秘术 · 早安白日', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体穿透创伤', 'description': '藤蔓穿透大地造成高额精神创伤'},
            {'name': '至终仪式 · 沉默的森林', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏净化与石化', 'description': '唤醒整片古林压制全场敌方，驱散敌方全部增益状态'}
        ]
    },
    {
        'name': '曲娘 (Jiu Niangzi)',
        'title': '沛县九娘 · 追击核爆天花板',
        'rarity': 6,
        'element': '岩 (Mineral)',
        'weapon_type': '陈年酒酿葫芦',
        'region': '沛县',
        'arkhe': '酒气酿造',
        'passive': '尽欢颜：回合开始积攒【酒浆】，根据酒浆层数追加单体与群体超强现实创伤！',
        'skills': [
            {'name': '神秘术 · 斟尽觞', 'type': 'ELEMENTAL_SKILL', 'scaling': '现实创伤/消耗酒浆', 'description': '将陈酿烈酒泼洒向敌方，消耗至多 3 滴酒浆造成连环暴击追加创伤'},
            {'name': '神秘术 · 提神浆', 'type': 'ELEMENTAL_SKILL', 'scaling': '自我充盈/攻击提升', 'description': '畅饮琼浆为自身提供攻击力加成与每回合酒浆持续产出'},
            {'name': '至终仪式 · 醉吟平泉赋', 'type': 'ELEMENTAL_BURST', 'scaling': '单体毁灭醉击', 'description': '酒意达到巅峰倾泻而下，对指定敌方造成毁灭级现实重创'}
        ]
    },
    {
        'name': '葛天 (Getian)',
        'title': '沛县祭司 · 识骨识天骨笛',
        'rarity': 6,
        'element': '兽 (Beast)',
        'weapon_type': '苍骨神笛',
        'region': '沛县',
        'arkhe': '骨相卜测',
        'passive': '骨笛长鸣：进入【骨相】结界，使全场敌方承受现实创伤大幅加深，配合现实C爆发',
        'skills': [
            {'name': '神秘术 · 卜于骨', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体现实创伤', 'description': '引动兽骨回响轰击敌阵，使目标现实防御削弱'},
            {'name': '神秘术 · 问于天', 'type': 'ELEMENTAL_SKILL', 'scaling': '自身戒备/激情充填', 'description': '吹响骨笛积聚天地灵气，快速恢复自身与核心队友激情'},
            {'name': '至终仪式 · 唯见山川与云霓', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏领域铺设', 'description': '张开山川云霓领域，敌方受击时额外引动骨刺穿刺打击'}
        ]
    },
    {
        'name': '6 (Six)',
        'title': '阿派朗学派领袖 · 启示净化万金油',
        'rarity': 6,
        'element': '智 (Intellect)',
        'weapon_type': '几何权杖',
        'region': '阿派朗学派',
        'arkhe': '知识解构',
        'passive': '真理裁决：友方释放咒语时随机赋予多种强力正面状态，敌方施放技能施加虚弱与减益',
        'skills': [
            {'name': '神秘术 · 惩戒指令', 'type': 'ELEMENTAL_SKILL', 'scaling': '单体精神创伤/减益', 'description': '造成精神创伤并给敌方施加减防、受创加深等负面效果'},
            {'name': '神秘术 · 辩证法则', 'type': 'ELEMENTAL_SKILL', 'scaling': '全队净化/增益', 'description': '清除友方数层负面减益状态，并随机赋予攻击加成与受创减免'},
            {'name': '至终仪式 · 启示录的序章', 'type': 'ELEMENTAL_BURST', 'scaling': '群体大招/爆发', 'description': '基于目标身上的减益状态数量按乘区产生翻倍精神伤害'}
        ]
    },
    {
        'name': '卡卡尼亚 (Kakania)',
        'title': '维也纳心理催眠学者 · 承伤转换核心',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '潜意识水镜',
        'region': '维也纳',
        'arkhe': '移情共感',
        'passive': '移情：替友方承受巨量伤害存储于【共情】池中，并在反击时将存储伤害化为真伤倾泻！',
        'skills': [
            {'name': '神秘术 · 潜意识映射', 'type': 'ELEMENTAL_SKILL', 'scaling': '本源伤害/共情返还', 'description': '消耗自身共情池数值，对敌方单体造成巨额真实本源伤害'},
            {'name': '神秘术 · 联想疗法', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体治疗/减伤护盾', 'description': '为友方提供生命恢复并构建心灵共振减伤力场'},
            {'name': '至终仪式 · 梦的解析', 'type': 'ELEMENTAL_BURST', 'scaling': '全队攻击跃升/群体承伤', 'description': '全面解放潜意识领域，根据友方生命差值大幅飙升全队攻击力'}
        ]
    },
    {
        'name': '维拉 (Vila)',
        'title': '鲁萨尔卡歌仙 · 精神队专属大拐',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '水仙鲁特琴',
        'region': '极北之地',
        'arkhe': '水仙之歌',
        'passive': '鲁萨尔卡之祝：开局即赋予全队强力鼓舞，精神属性技能暴击率与暴击创伤翻倍提升！',
        'skills': [
            {'name': '神秘术 · 远行之歌', 'type': 'ELEMENTAL_SKILL', 'scaling': '精神增幅/激情回复', 'description': '唱诵远方歌谣，提升队友精神创伤并恢复 1 点关键激情'},
            {'name': '神秘术 · 湖水叮咚', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体持续治疗', 'description': '湖水甘霖润泽友方，提供持续每回合回血与受创减免'},
            {'name': '至终仪式 · 故乡的晨曦', 'type': 'ELEMENTAL_BURST', 'scaling': '精神队究极神辅', 'description': '展开晨曦光芒领域，使核心精神主C暴击伤害提高 50% 以上'}
        ]
    },
    {
        'name': '马库斯 (Marcus)',
        'title': '霍夫曼的读者 · 木系升阶永动机',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '典藏手抄本',
        'region': '维也纳',
        'arkhe': '精读批注',
        'passive': '精读：每当出牌技能达到二阶或三阶时，返还行动点并积攒灵光自动抽牌！',
        'skills': [
            {'name': '神秘术 · 纸页翻覆', 'type': 'ELEMENTAL_SKILL', 'scaling': '精神创伤/自动升阶', 'description': '飞舞纸页划破敌阵，命中后自身下一张手牌自动跃升 1 阶'},
            {'name': '神秘术 · 墨迹未干', 'type': 'ELEMENTAL_SKILL', 'scaling': '精神穿透', 'description': '高额精神创伤并根据技能阶数产生大幅攻击力加成'},
            {'name': '至终仪式 · 烛光下的批注', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏精神大招', 'description': '书本展开文字风暴，对全体敌方造成高额伤害并强制升阶所有手牌'}
        ]
    },
    {
        'name': '梅兰妮 (Melania)',
        'title': '神偷拉米雷斯 · 偷心大盗偷激情',
        'rarity': 6,
        'element': '兽 (Beast)',
        'weapon_type': '巧手魔术礼帽',
        'region': '伦敦',
        'arkhe': '巧取豪夺',
        'passive': '巧计谋划：释放至终仪式后获得【巧计】状态，永久叠加至终仪式伤害加成！',
        'skills': [
            {'name': '神秘术 · 乘隙而入', 'type': 'ELEMENTAL_SKILL', 'scaling': '精神创伤/偷取激情', 'description': '灵巧突击造成精神创伤，偷取目标 1 点激情充盈自身！'},
            {'name': '神秘术 · 提线木偶', 'type': 'ELEMENTAL_SKILL', 'scaling': '单体创伤/自我蓄势', 'description': '木偶戏线缠绕敌方造成伤害并为自身施加减伤护甲'},
            {'name': '至终仪式 · 离奇闹剧', 'type': 'ELEMENTAL_BURST', 'scaling': '核弹级单体仪式', 'description': '策划一场精妙偷盗闹剧，造成极高额精神创伤并让下一次仪式翻倍'}
        ]
    },
    {
        'name': '洁西卡 (Jessica)',
        'title': '绿湖的鹿角少女 · 毒系核心主C',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '绿湖鹿角拐杖',
        'region': '绿湖营地',
        'arkhe': '剧毒蔓延',
        'passive': '林中幽灵：若敌方身上存在【中毒】状态，洁西卡对其造成的所有伤害提升 40%！',
        'skills': [
            {'name': '神秘术 · 白鹿的轻跃', 'type': 'ELEMENTAL_SKILL', 'scaling': '现实创伤/中毒结算', 'description': '轻盈飞踢命中敌方，目标每层中毒额外触发 100% 毒素引爆伤害'},
            {'name': '神秘术 · 善意的捉弄', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体施毒', 'description': '召唤幽绿孢子笼罩敌方，连续施加多层中毒状态持续 3 回合'},
            {'name': '至终仪式 · 绿湖的平静之下', 'type': 'ELEMENTAL_BURST', 'scaling': '群体毒爆', 'description': '掀起绿湖毒雾狂潮，对全体敌方造成毁灭性现实创伤并续刷新毒素时间'}
        ]
    },
    {
        'name': '苏芙比 (Sotheby)',
        'title': '豪门天真大小姐 · 群体持续回血毒药师',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '炼金药剂瓶',
        'region': '伦敦卡文迪许家族',
        'arkhe': '药剂调配',
        'passive': '调配天才：回合结束时若自身处于【持续恢复】状态，额外为全队结算生命治愈',
        'skills': [
            {'name': '神秘术 · 三倍浓缩毒液', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体中毒', 'description': '扔出高烈度毒液试管，对 2 名敌方施加【中毒】状态'},
            {'name': '神秘术 · 浓缩精华剂', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体延时持续回血', 'description': '为全队施加【持续恢复】状态，每回合行动开始恢复生命值'},
            {'name': '至终仪式 · 它们整齐盛开', 'type': 'ELEMENTAL_BURST', 'scaling': '瞬间结算全部毒素与治疗', 'description': '引爆全场药剂！立即结算敌方身上剩余全部中毒伤害，并立即结算全队持续回血！'}
        ]
    },
    {
        'name': '百夫长 (Centurion)',
        'title': '角斗场不败冠军 · 满激情核爆战神',
        'rarity': 6,
        'element': '兽 (Beast)',
        'weapon_type': '黄金拳套',
        'region': '古罗马竞技场',
        'arkhe': '狂热激情',
        'passive': '辣酱爱好：自身激情越高，所有技能造成的现实创伤越高；满激情时输出毁天灭地！',
        'skills': [
            {'name': '神秘术 · 迎头痛击', 'type': 'ELEMENTAL_SKILL', 'scaling': '单体创伤/激情增伤', 'description': '重拳出击，自身每有 1 点激情额外提升 20% 现实伤害'},
            {'name': '神秘术 · 户外维加斯', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体创伤/自身回血', 'description': '挥掷金币爆击敌阵，若暴击则回复自身可观生命值'},
            {'name': '至终仪式 · 真正的维加斯秀', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏现实毁灭爆破', 'description': '引爆华丽烟火与金币雨，对敌方全员造成极强现实重创'}
        ]
    },
    {
        'name': '星锑 (Regulus)',
        'title': '摇滚海盗船长 · 全队暴击与全体闪避',
        'rarity': 6,
        'element': '星 (Star)',
        'weapon_type': '摇滚黑胶唱片机',
        'region': '海上电台',
        'arkhe': '躁动摇滚',
        'passive': '听我摇滚：若回合未行动，进入【躁动摇滚】状态，下回合暴击率暴增 50% 且溢出转爆伤！',
        'skills': [
            {'name': '神秘术 · 摇滚乐手', 'type': 'ELEMENTAL_SKILL', 'scaling': '精神创伤/消减激情', 'description': '音浪冲击敌方，暴击时削减敌方 1 点关键大招激情'},
            {'name': '神秘术 · 飞碟来了', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体穿透精神伤害', 'description': '抛掷荧光唱片飞碟在敌阵穿梭切割造成精神创伤'},
            {'name': '至终仪式 · 狂热光波与流星', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏闪避无敌大招', 'description': '全屏精神轰炸，并赋予全队友方【闪避】状态：免疫敌方除大招外的下一次非仪式攻击！'}
        ]
    },
    {
        'name': '未锈铠 (A Knight)',
        'title': '中世纪圆桌幽灵骑士 · 击杀连斩永动机',
        'rarity': 6,
        'element': '灵 (Spirit)',
        'weapon_type': '幽灵双手重剑',
        'region': '卡美洛古战场',
        'arkhe': '骑士誓言',
        'passive': '怜悯：敌方生命越低自身伤害越高，成功击败目标立即大幅补充自身激情',
        'skills': [
            {'name': '神秘术 · 公正', 'type': 'ELEMENTAL_SKILL', 'scaling': '单体现实创伤', 'description': '圣剑斩击敌方，消灭敌方时自身获得 1 点额外激情'},
            {'name': '神秘术 · 荣耀', 'type': 'ELEMENTAL_SKILL', 'scaling': '群攻现实创伤', 'description': '横扫剑气造成群体现实创伤'},
            {'name': '至终仪式 · 骑士荣耀的证词', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏圣剑斩杀', 'description': '召唤幽灵圣剑从天劈下！若击杀任一敌方，赋予全队【激昂】创伤加深 50%！'}
        ]
    },
    {
        'name': '蓝手帕 (Blue Semaphore)',
        'title': '海洋探照灯学者 · 剧毒激昂辅C',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '海蓝旗语信号机',
        'region': '灯塔科算站',
        'arkhe': '信号破译',
        'passive': '信标指引：回合开始为敌方挂上标记，全队毒系与本源伤害提高 30%',
        'skills': [
            {'name': '神秘术 · 旗语信号', 'type': 'ELEMENTAL_SKILL', 'scaling': '精神创伤/标记', 'description': '挥动旗语施加信号标记，使敌方受创加深'},
            {'name': '神秘术 · 迷雾回响', 'type': 'ELEMENTAL_SKILL', 'scaling': '群体穿透/毒素蔓延', 'description': '引动雾气造成精神创伤并扩散中毒层数'},
            {'name': '至终仪式 · 破晓之蓝的光束', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏灯塔光芒', 'description': '照射全屏打破一切潜行与抗性，引爆所有标记'}
        ]
    },
    {
        'name': '洛佩拉 (Lopera)',
        'title': '热熔火炮先锋 · 暴击引燃主C',
        'rarity': 6,
        'element': '兽 (Beast)',
        'weapon_type': '重装魔导榴弹炮',
        'region': '工坊联盟',
        'arkhe': '爆裂重炮',
        'passive': '热能爆发：每次造成暴击累积热能，满热能下一次攻击 100% 暴击并造成连带溅射',
        'skills': [
            {'name': '神秘术 · 榴弹轰击', 'type': 'ELEMENTAL_SKILL', 'scaling': '现实创伤/溅射', 'description': '发射重型榴弹穿透前排并在敌阵中爆炸'},
            {'name': '神秘术 · 快速装填', 'type': 'ELEMENTAL_SKILL', 'scaling': '弹药强化/攻击提升', 'description': '装填高爆穿甲弹药，暴击伤害提升 35%'},
            {'name': '至终仪式 · 毁灭狂潮终结曲', 'type': 'ELEMENTAL_BURST', 'scaling': '重炮地毯式轰炸', 'description': '呼叫重炮全覆盖轰炸，造成巨额现实创伤并消减敌方护盾'}
        ]
    },
    {
        'name': '泥鯭的士 (An-an Lee)',
        'title': '香港降妖少女 · 随心变幻鬼才辅C',
        'rarity': 6,
        'element': '木 (Plant)',
        'weapon_type': '桃木除妖剑与符纸',
        'region': '香港九龙',
        'arkhe': '鬼马符箓',
        'passive': '时来运转：处于【休息中】状态时受创减免；处于【作法中】状态时伤害与穿透大幅提升！',
        'skills': [
            {'name': '神秘术 · 聚灵白符', 'type': 'ELEMENTAL_SKILL', 'scaling': '现实创伤/升阶增伤', 'description': '抛出除妖符纸，高阶技能附带眩晕控制判定'},
            {'name': '神秘术 · 百般解脱', 'type': 'ELEMENTAL_SKILL', 'scaling': '全队增益/坚固加攻', 'description': '施法赋予全队创伤加成与受创减免，极其坚挺全面'},
            {'name': '至终仪式 · 捉鬼专家急急如律令', 'type': 'ELEMENTAL_BURST', 'scaling': '全屏符阵爆破', 'description': '念诵九字真言引动天雷地火，对敌方全员造成强力现实创伤并为自身手牌升阶'}
        ]
    }
]

PSYCHUBES = [
    {'name': '漫长宵日 (Long Night)', 'type': '6星专武心相', 'rarity': 6, 'base_atk': '攻击力 +410, 生命值 +2600', 'sub_stat': '暴击率 +16%', 'refine': '记忆印刻：自身造成本源创伤时，伤害额外提升 24%；释放至终仪式后暴击伤害提升 32%！'},
    {'name': '美丽的旧世界 (Brave New World)', 'type': '6星通用爆发心相', 'rarity': 6, 'base_atk': '攻击力 +380, 生命值 +2800', 'sub_stat': '至终仪式威力 +18%', 'refine': '记忆印刻：施放至终仪式后，下一次普通神秘术技能伤害大幅提升 40%！'},
    {'name': '大娱乐家 (That Inquisitive Dear)', 'type': '6星治疗专精心相', 'rarity': 6, 'base_atk': '攻击力 +350, 生命值 +3200', 'sub_stat': '治疗率 +18%', 'refine': '记忆印刻：施放减益型神秘术后，为生命最低友方恢复施法者攻击力 96% 的生命值！'},
    {'name': '掌声如雷鸣 (Thunderous Applause)', 'type': '6星暴击专精心相', 'rarity': 6, 'base_atk': '攻击力 +410, 生命值 +2500', 'sub_stat': '暴击率 +16%', 'refine': '记忆印刻：单体神秘术产生暴击时，自身暴击创伤提高 32%，红弩箭/百夫长核心心相！'},
    {'name': '夜色温柔 (Blasphemer of Night)', 'type': '6星状态增伤心相', 'rarity': 6, 'base_atk': '攻击力 +390, 生命值 +2700', 'sub_stat': '术法威力 +18%', 'refine': '记忆印刻：当目标拥有 2 个以上【状态异常】时，自身对其造成伤害提升 24%，毒队/控制队毕业！'},
    {'name': '必要的记录 (Necessary Record)', 'type': '6星通用吸血心相', 'rarity': 6, 'base_atk': '攻击力 +410, 生命值 +2600', 'sub_stat': '创伤加成 +12%', 'refine': '记忆印刻：击败敌方目标时，为自身恢复攻击力 120% 的生命值，持久战神级续航心相。'},
    {'name': '跳房子游戏 (Hopscotch)', 'type': '6星清杂爆发心相', 'rarity': 6, 'base_atk': '攻击力 +390, 生命值 +2700', 'sub_stat': '术法威力 +18%', 'refine': '记忆印刻：每击杀 1 名敌方目标，至终仪式威力提升 8%，最多可叠加 4 层。'},
    {'name': '步入光芒 (Into the Light)', 'type': '6星精神专属心相', 'rarity': 6, 'base_atk': '攻击力 +410, 生命值 +2600', 'sub_stat': '穿透率 +16%', 'refine': '记忆印刻：自身造成精神创伤时无视目标 20% 精神防御，曲娘/37精神队高配心相。'},
    {'name': '沉默与向往 (Silence and Longing)', 'type': '6星追击特化心相', 'rarity': 6, 'base_atk': '攻击力 +400, 生命值 +2650', 'sub_stat': '追击伤害 +20%', 'refine': '记忆印刻：自身施放额外行动追击技能时，暴击率提升 15%，暴击创伤提升 30%。'},
    {'name': '敲响钟声 (Toll the Bell)', 'type': '6星辅助生存心相', 'rarity': 6, 'base_atk': '攻击力 +340, 生命值 +3400', 'sub_stat': '受创减免 +14%', 'refine': '记忆印刻：回合开始时生命低于 50% 则为全队施加 15% 最大生命的护盾。'}
]

MECHANICS = [
    {
        'category': '属性生克',
        'title': '四象灵智属性克制规则',
        'formula': '克制方造成伤害提升 30%，受克制方造成伤害降低 30%',
        'parameters': {
            '四象循环': '兽克木，木克岩，岩克星，星克兽',
            '灵智对立': '灵与智双向互相克制对方 30% 伤害',
            '激情机制': '每次出牌获得 1 点激情，满 5 点激情下回合自动抽取至终仪式专属大招手牌'
        }
    },
    {
        'category': '咒语合成',
        'title': '神秘术合成升阶与行动点消耗',
        'formula': '相邻相同阶数咒语自动融合升阶；主动拖动移动合成消耗 1 点行动力',
        'parameters': {
            '一阶咒语': '基础效果，常规技能倍率',
            '二阶咒语': '倍率显著提升，通常解锁硬控（石化/眩晕/封印）或强力附加词缀',
            '三阶咒语': '终极效果，提供全队群体增益或毁天灭地高额创伤'
        }
    },
    {
        'category': '共鸣系统',
        'title': '角色心智共鸣拼图属性加成',
        'formula': '摆放不同形状的共鸣模块块面，最大化暴击率、创伤加成与攻击力收益',
        'parameters': {
            '共鸣10阶': '标准毕业门槛，解锁所有核心拼图槽位',
            '共鸣15阶': '满练度极限，全属性突破'
        }
    }
]


def crawl_and_sync_reverse1999(game_id=31):
    print(f'[Reverse: 1999] Preparing Arcanists & Psychubes for Game {game_id} ...')

    characters = []
    for a in ARCANISTS:
        characters.append({
            'name': a['name'],
            'title': a['title'],
            'rarity': a['rarity'],
            'element': a['element'],
            'weapon_type': a['weapon_type'],
            'region': a['region'],
            'arkhe': a['arkhe'],
            'avatar_url': f'/games/arcanists/{a["name"].split()[0]}.png',
            'splash_url': '',
            'base_stats': [
                {'level': '洞悉一', 'hp': 2500, 'atk': 380, 'def': 180, 'crit_rate': '10%'},
                {'level': '洞悉三满阶', 'hp': 7800, 'atk': 1250, 'def': 650, 'crit_rate': '18%'}
            ],
            'talents': a['skills'],
            'passives': [{'name': '洞悉传承', 'description': a['passive']}],
            'constellations': [],
            'special_mechanics': {'circuit': a['arkhe']},
            'recommendations': {'best_psychube': '漫长宵日 / 美丽新世界 / 掌声如雷鸣'},
            'version': 'v2.2'
        })

    weapons = []
    for p in PSYCHUBES:
        weapons.append({
            'name': p['name'],
            'type': p['type'],
            'rarity': p['rarity'],
            'icon_url': f'/games/psychubes/{p["name"].split()[0]}.png',
            'base_atk_curve': {'base': p['base_atk']},
            'sub_stat': {'bonus': p['sub_stat']},
            'refinements': {'imprint': p['refine']},
            'ascension_materials': {'type': '贪婪 / 意志解析材料'},
            'version': 'v2.2'
        })

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    m_count = upsert_mechanics(game_id, MECHANICS)
    print(f'[Reverse: 1999] Ingested into Game {game_id}: {c_count} arcanists, {w_count} psychubes, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_reverse1999(31)
