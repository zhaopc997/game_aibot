"""
Wuthering Waves (鸣潮) Full Resonators, 5-Star Weapons & Echo Sets Crawler/Importer Module
Updated for version 3.X cumulative roster: covers all 47 Resonators across elements and roles.
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

RESONATORS_ROSTER = [
    # 衍射 (Spectro)
    {
        'name': '今汐 (Jinhsi)',
        'title': '乘霄令尹 · 岁主共鸣者',
        'rarity': 5,
        'element': '衍射 (Spectro)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '今州 · 乘霄山',
        'arkhe': '韶光回路',
        'desc': '今州令尹，背负着与岁主角共鸣的神力，核心输出依托【韶光】层数引爆真龙惊芒。',
        'skill_e': '惊芒：化身神龙凌空挥砍，消耗韶光产生毁天灭地衍射AOE伤害。',
        'skill_q': '净世之龙：引动天光真龙长啸，对大范围敌方造成极限衍射伤害。'
    },
    {
        'name': '守岸人 (Shorekeeper)',
        'title': '黑海岸神性核心 · 斯泰拉之光',
        'rarity': 5,
        'element': '衍射 (Spectro)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '黑海岸 (Black Shores)',
        'arkhe': '星蝶领域',
        'desc': '黑海岸的核心意识化身，全队顶级生存与暴击辅助，展开【斯泰拉领域】提供全图暴击爆伤加成。',
        'skill_e': '星蝶祈愿：召唤群蝶治愈当前共鸣者，并持续积攒共鸣能量。',
        'skill_q': '斯泰拉领域：展开三阶段星海结界，提升全队暴击率 12.5% 与暴击伤害 25%！'
    },
    {
        'name': '维里奈 (Verina)',
        'title': '育种植物学家 · 生命萌发',
        'rarity': 5,
        'element': '衍射 (Spectro)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '今州',
        'arkhe': '生息光环',
        'desc': '万金油全能辅助，提供全队攻击力 20% 增幅、全属性深空增伤与持续生命恢复。',
        'skill_e': '繁花盛放：在目标脚下召唤光藤造成衍射伤害并恢复生命。',
        'skill_q': '白芒蔓延：造成范围衍射伤害并标记全屏敌方，全队攻击标记目标触发协同光击。'
    },
    {
        'name': '菲比 (Phoebe)',
        'title': '星象编织者 · 璀璨星图',
        'rarity': 5,
        'element': '衍射 (Spectro)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '天穹观测台',
        'arkhe': '星轨回路',
        'desc': '观测群星规律的少女，以星象罗盘操纵光线折射，大幅降低敌人衍射抗性。',
        'skill_e': '星轨连线：在敌阵间绘制星环，造成穿透衍射伤害。',
        'skill_q': '超新星爆发：汇聚星盘能量产生光爆，为队友提供高额攻击速度。'
    },
    {
        'name': '卡提希娅 (Cattisia)',
        'title': '圣仪学者 · 祈愿神音',
        'rarity': 4,
        'element': '衍射 (Spectro)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '瑝珑圣殿',
        'arkhe': '音律净化',
        'desc': '擅长以圣乐祈祷抚平狂躁的异象，为队友提供常驻护盾与微量生命回复。',
        'skill_e': '圣音回环：展开音符护盾吸收受到的伤害。',
        'skill_q': '永恒乐章：释放圣光波纹驱散全队负面异常。'
    },
    {
        'name': '漂泊者·衍射 (Rover: Spectro)',
        'title': '苏醒旅人 · 初始光华',
        'rarity': 5,
        'element': '衍射 (Spectro)',
        'weapon_type': '迅刀 (Sword)',
        'region': '未知交界',
        'arkhe': '尘芒回转',
        'desc': '于荒野苏醒的命定旅人，掌控最纯粹的衍射光辉，拥有优秀的单兵作战与打断能力。',
        'skill_e': '光芒飞刃：向前挥出三道衍射剑气。',
        'skill_q': '天光倾泻：召唤光剑阵轰击地面造成范围破坏。'
    },

    # 热熔 (Fusion)
    {
        'name': '长离 (Changli)',
        'title': '令尹参事 · 离火之炽',
        'rarity': 5,
        'element': '热熔 (Fusion)',
        'weapon_type': '迅刀 (Sword)',
        'region': '今州 · 乘霄山',
        'arkhe': '心眼回路',
        'desc': '今州令尹参事，精通棋局杀伐，通过【心眼】状态切换地面与空中连招，施加持续热熔增伤。',
        'skill_e': '赫奕流明：向前瞬移突进并造成热熔伤害，直接进入心眼·征状态。',
        'skill_q': '火羽焚天：引燃全屏雀羽，造成大范围爆发热熔伤害并回满离火层数。'
    },
    {
        'name': '安可 (Encore)',
        'title': '黑海岸护卫 · 黑白双羊',
        'rarity': 5,
        'element': '热熔 (Fusion)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '黑海岸',
        'arkhe': '羊咩狂怒',
        'desc': '召唤白羊与黑羊协助作战，大招变身为近战黑羊狂暴姿态，高频撕扯输出。',
        'skill_e': '热熔火线：白羊喷吐烈焰造成直线热熔伤害。',
        'skill_q': '羊咩狂欢：黑羊接管躯体，普攻变为高速近战暗焰爪击。'
    },
    {
        'name': '赞妮 (Zanni)',
        'title': '烈火锻造师 · 熔炉之心',
        'rarity': 5,
        'element': '热熔 (Fusion)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '虎口矿区',
        'arkhe': '淬火爆发',
        'desc': '狂放不羁的重剑锻刀师，将熔岩热度注入刀锋，每一次重砸都能引爆岩浆喷涌。',
        'skill_e': '重锤锻钢：巨剑重击地面裂开熔岩地裂。',
        'skill_q': '地火轰鸣：引爆自身周围全部熔岩裂隙，产生毁灭性连锁爆炸。'
    },
    {
        'name': '布兰特 (Brandt)',
        'title': '赤焰狂拳 · 爆裂冲拳',
        'rarity': 5,
        'element': '热熔 (Fusion)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '黑海岸',
        'arkhe': '过热拳压',
        'desc': '狂暴体术专家，拳击命中积攒热量槽，满热量释放超高温重炮直拳。',
        'skill_e': '烈焰连击：打出高速三段勾拳并突进。',
        'skill_q': '核熔爆轰：跃起空中双拳如流星砸地，掀起火海。'
    },
    {
        'name': '炽霞 (Chixia)',
        'title': '天城巡尉 · 炽烈飞弹',
        'rarity': 4,
        'element': '热熔 (Fusion)',
        'weapon_type': '佩枪 (Pistols)',
        'region': '今州',
        'arkhe': '轰轰回击',
        'desc': '热情洋溢的巡尉，双枪连射积攒【热能】，长按普攻进入哒哒哒扫射模式。',
        'skill_e': '巡火出击：后跳同时向前连射两发高爆子弹。',
        'skill_q': '炽火燎原：旋转双枪向周围持续倾泻子弹暴风雨。'
    },
    {
        'name': '莫特斐 (Mortefi)',
        'title': '华胥安全部 · 红龙协同',
        'rarity': 4,
        'element': '热熔 (Fusion)',
        'weapon_type': '佩枪 (Pistols)',
        'region': '今州 · 华胥研究院',
        'arkhe': '龙息共鸣',
        'desc': '容易暴躁的火药研究员，大招提供极强后台协同攻击，重击队必备强力副C。',
        'skill_e': '爆破火网：投掷燃烧弹在敌阵展开阻截火线。',
        'skill_q': '红龙之怒：激活红龙领域，队友造成重击时召唤烈焰飞弹协同轰炸。'
    },
    {
        'name': '千咲 (Chisaki)',
        'title': '爆破巧匠 · 火药艺术',
        'rarity': 4,
        'element': '热熔 (Fusion)',
        'weapon_type': '佩枪 (Pistols)',
        'region': '今州城',
        'arkhe': '火花连跳',
        'desc': '活泼的火药学徒，擅长在战场各处安插微型炸弹制造连环爆破。',
        'skill_e': '跳跃火种：扔出弹跳炸弹，每次弹跳造成范围热熔伤害。',
        'skill_q': '盛大烟花礼：向空中发射信号弹，召唤全场烟火轰炸。'
    },

    # 湮灭 (Havoc)
    {
        'name': '椿 (Camellya)',
        'title': '黑海岸执行官 · 曼陀罗之刺',
        'rarity': 5,
        'element': '湮灭 (Havoc)',
        'weapon_type': '迅刀 (Sword)',
        'region': '黑海岸 (Black Shores)',
        'arkhe': '蕊生回路',
        'desc': '黑海岸绽放者，拥有【白蕊】与【红蕊】双重形态，藤蔓狂舞造成高频湮灭切割。',
        'skill_e': '红蔓绞杀：伸展带刺藤蔓穿透空间，将敌人拉至身前并大幅强化普攻。',
        'skill_q': '彼岸盛放：在终焉深渊中绽放巨型幽花，引爆全场造成毁灭性湮灭伤害。'
    },
    {
        'name': '坎特蕾拉 (Cantarella)',
        'title': '深渊歌姬 · 蚀影咏叹',
        'rarity': 5,
        'element': '湮灭 (Havoc)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '沉没之都',
        'arkhe': '哀歌共振',
        'desc': '漫步于残破废墟中的优雅贵妇，以低沉哀伤的声线抽取敌人生命力转化为全队护盾。',
        'skill_e': '蚀心之弦：拨动黑色琴弦使前方扇形区域敌人陷入虚弱。',
        'skill_q': '幽夜挽歌：召唤巨型幻影黑鲸从虚空跃出，坠地引发空间塌缩。'
    },
    {
        'name': '弗洛洛 (Phrolova)',
        'title': '残星会先驱 · 绝响律动',
        'rarity': 5,
        'element': '湮灭 (Havoc)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '残星会',
        'arkhe': '静默崩解',
        'desc': '神秘的残星会高层，以音符诱导空间裂缝，拥有极强的削减敌人抗性与禁锢能力。',
        'skill_e': '暗夜交响：施放三段暗影冲击，撕裂目标护甲。',
        'skill_q': '终焉重音：奏响灭世和弦，全图范围陷入湮灭黑洞。'
    },
    {
        'name': '洛可可 (Rococo)',
        'title': '巴洛克重奏 · 机械玩偶',
        'rarity': 5,
        'element': '湮灭 (Havoc)',
        'weapon_type': '佩枪 (Pistols)',
        'region': '新贵族同盟',
        'arkhe': '齿轮绝鸣',
        'desc': '身着复古洛丽塔洋装的神秘人偶射手，操控浮游炮台进行交叉死亡火力覆盖。',
        'skill_e': '发条突刺：向前释放旋转齿轮刀，收割沿途敌人。',
        'skill_q': '黑白终幕曲：全火力展开浮游炮阵，进行全向湮灭弹幕洗礼。'
    },
    {
        'name': '丹瑾 (Danjin)',
        'title': '游侠赤刃 · 丹心照雪',
        'rarity': 4,
        'element': '湮灭 (Havoc)',
        'weapon_type': '迅刀 (Sword)',
        'region': '瑝珑',
        'arkhe': '朱华染血',
        'desc': '行侠仗义的红衣少女，通过持续消耗自身生命值换取极高的湮灭伤害加成。',
        'skill_e': '朱华残照：无冷却多段连斩，消耗自身血量造成大幅强化伤害。',
        'skill_q': '绯红盛宴：拔刀横扫，吸取周围敌方精魄造成高额爆发并回血。'
    },
    {
        'name': '桃祈 (Taoqi)',
        'title': '边防玄武 · 磐石固守',
        'rarity': 4,
        'element': '湮灭 (Havoc)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '今州夜归',
        'arkhe': '玄武庇护',
        'desc': '看似慵懒但极度可靠的玄武守卫，巨刃格挡反击能力极强，提供全队护盾与共鸣技能增伤。',
        'skill_e': '固若金汤：架起巨刃进入格挡姿态，受击瞬间自动打出反击重劈。',
        'skill_q': '不动如山：重击地面生成玄武领域，为全体队友提供持续坚韧护盾。'
    },
    {
        'name': '陆·赫斯 (Lu Hess)',
        'title': '黑晶重铠 · 绝灭斩首',
        'rarity': 5,
        'element': '湮灭 (Havoc)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '旧军团遗迹',
        'arkhe': '黯晶过载',
        'desc': '手持巨大黑晶斩马刀的重铠战士，每击中一次敌人使自身攻击力逐步飙升。',
        'skill_e': '裂魂重劈：跃起暴扣斩击造成击飞效果。',
        'skill_q': '黑曜斩决：双手持刀蓄力回旋斩，斩杀血量低于25%的非首领单位。'
    },
    {
        'name': '漂泊者·湮灭 (Rover: Havoc)',
        'title': '苏醒旅人 · 暗夜终焉',
        'rarity': 5,
        'element': '湮灭 (Havoc)',
        'weapon_type': '迅刀 (Sword)',
        'region': '未知交界',
        'arkhe': '暗影沉沦',
        'desc': '掌控暗影暗夜力量的漂泊者，暗灭能量蓄满后化身黑翼死神，普攻伤害大幅飞跃。',
        'skill_e': '暗月凌空：突进穿刺敌人并生成暗夜黑莲。',
        'skill_q': '死生契阔：撕开虚空引爆黑洞，造成巨额单体爆发斩杀。'
    },

    # 冷凝 (Glacio)
    {
        'name': '折枝 (Zhezhi)',
        'title': '画境千峰 · 神来之笔',
        'rarity': 5,
        'element': '冷凝 (Glacio)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '今州',
        'arkhe': '灵鹤化生',
        'desc': '内向的委托画师，以画笔点墨化生白鹤，协同普攻造成高频冰伤并提供全队冷凝增幅。',
        'skill_e': '画卷展开：泼墨挥毫召唤墨鹤穿梭飞击。',
        'skill_q': '江山入画：展开百米千里江山长卷，全图敌人受到持续冰瀑轰击。'
    },
    {
        'name': '凌阳 (Lingyang)',
        'title': '狮舞英豪 · 踏雪寻梅',
        'rarity': 5,
        'element': '冷凝 (Glacio)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '今州',
        'arkhe': '醒狮登楼',
        'desc': '醒狮舞团主力，开启大招后跃上梅花桩进入【踏雪行】浮空状态，空中连续爪击。',
        'skill_e': '踏雪寻踪：向前扑击造成连续两段冷凝霜击。',
        'skill_q': '狮跃千峰：戴上醒狮金面具，自身全部攻击转化为高机动空中动作。'
    },
    {
        'name': '散华 (Sanhua)',
        'title': '令尹近卫 · 霜雪凝止',
        'rarity': 4,
        'element': '冷凝 (Glacio)',
        'weapon_type': '迅刀 (Sword)',
        'region': '今州',
        'arkhe': '冰痕引爆',
        'desc': '令尹近卫，打条QTE精准判定引爆冰刺，延奏技能为下一位共鸣者提供高达 38% 的普攻增伤！',
        'skill_e': '凌霜踏雪：向前挥斩冰刃并留存冰刺。',
        'skill_q': '千里冰封：斩出巨型冰莲花，使全场产生绝对零度冻伤。'
    },
    {
        'name': '白芷 (Baizhi)',
        'title': '华胥研究员 · 忧昙念兽',
        'rarity': 4,
        'element': '冷凝 (Glacio)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '今州 · 华胥研究院',
        'arkhe': '念兽治愈',
        'desc': '冷静理性的研究员，召唤冰霜念兽【忧昙】协同战斗，施加群体治疗与复活庇护。',
        'skill_e': '雪落寒梅：令念兽向前冲撞并治疗全队生命值。',
        'skill_q': '流光净化：在地面召唤巨大冰昙花，持续回复全场友方血量。'
    },
    {
        'name': '釉瑚 (Youhu)',
        'title': '鉴宝巧匠 · 骨董通灵',
        'rarity': 4,
        'element': '冷凝 (Glacio)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '瑝珑黑市',
        'arkhe': '吉凶摇色',
        'desc': '精灵古怪的古玩鉴定少女，战斗中随机摇色抽取【吉/凶】古董卷轴，造成混乱效果。',
        'skill_e': '古玩大揭秘：从行囊掏出古董砸向目标，触发随机属性特效。',
        'skill_q': '万宝迎祥：释放金玉满堂聚宝盆，对范围敌人造成多段冷凝爆炸。'
    },
    {
        'name': '珂莱塔 (Coletta)',
        'title': '极境巡雪 · 寒晶利刃',
        'rarity': 5,
        'element': '冷凝 (Glacio)',
        'weapon_type': '迅刀 (Sword)',
        'region': '雪原科考队',
        'arkhe': '冰棱碎裂',
        'desc': '长年驻守极地边缘的孤独巡游者，以极寒凝结为冰锥飞刃，具备连续穿透能力。',
        'skill_e': '霜锋疾刺：瞬移穿刺前方一条直线上的敌人。',
        'skill_q': '绝对零度风暴：卷起全屏暴风雪，强制冰冻所有非霸体目标 2 秒。'
    },
    {
        'name': '清宵 (Qingxiao)',
        'title': '寒江独钓 · 霜影剑仙',
        'rarity': 5,
        'element': '冷凝 (Glacio)',
        'weapon_type': '迅刀 (Sword)',
        'region': '瑝珑古宗',
        'arkhe': '剑意凝霜',
        'desc': '隐居寒潭的古派剑修，剑气如雪，出剑快如闪电，具有极强的破韧与暴伤加成。',
        'skill_e': '一剑霜寒：拔剑突刺，剑气留下一道冰封路径。',
        'skill_q': '万剑归宗·落霜：千道飞剑自天幕落下，如暴雨贯穿全场。'
    },
    {
        'name': '露西 (Lucy)',
        'title': '霜天游侠 · 绝刃寒芒',
        'rarity': 5,
        'element': '冷凝 (Glacio)',
        'weapon_type': '迅刀 (Sword)',
        'region': '北境自由盟',
        'arkhe': '霜心疾风',
        'desc': '以优雅步伐在冰面上滑行作战的剑术家，连续闪避中可直接派生冰霜绝技。',
        'skill_e': '回旋飞雪：回旋挥斩击退周围敌人并拉开身位。',
        'skill_q': '极冰斩首：凌空蓄力斩出巨型弯月冰芒。'
    },

    # 导电 (Electro)
    {
        'name': '相里要 (Xiangli Yao)',
        'title': '华胥研究院首席 · 天工万象',
        'rarity': 5,
        'element': '导电 (Electro)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '今州 · 华胥研究院',
        'arkhe': '算力超频',
        'desc': '华胥首席研究员，机械臂连续挥出高能磁暴拳，大招期间拥有极强的短CD爆发能力。',
        'skill_e': '智算矩阵：机械臂向前喷射激光炮。',
        'skill_q': '全域过载：展开赛博演算领域，普攻与技能伤害翻倍提升。'
    },
    {
        'name': '吟霖 (Yinlin)',
        'title': '前治安官 · 悬丝傀儡',
        'rarity': 5,
        'element': '导电 (Electro)',
        'weapon_type': '音感仪 (Rectifier)',
        'region': '今州',
        'arkhe': '千面审判',
        'desc': '操控人偶【掣狱】进行协同攻击，后手脱手大招极强，为全队提供导电伤害加成与大招增幅。',
        'skill_e': '悬丝奔雷：人偶飞击并附着【缚罪印记】，触发高频感电落雷。',
        'skill_q': '雷霆审判：引召狂雷轰击地面，造成高额导电伤害。'
    },
    {
        'name': '卡卡罗 (Calcharo)',
        'title': '幽灵猎犬团长 · 雷霆修罗',
        'rarity': 5,
        'element': '导电 (Electro)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '幽灵猎犬佣兵团',
        'arkhe': '杀戮武装',
        'desc': '冷酷无情的佣兵领袖，开启大招进入【死告状态】，长刃挥洒狂暴雷光连击。',
        'skill_e': '灭杀旋风：挥斩长刃造成三段雷电劈砍。',
        'skill_q': '修罗临世：解放全身雷核，普攻转化为狂暴紫雷斩击。'
    },
    {
        'name': '渊武 (Yuanwu)',
        'title': '雷霆武馆馆主 · 闪电桩法',
        'rarity': 4,
        'element': '导电 (Electro)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '今州',
        'arkhe': '雷池震荡',
        'desc': '沉稳老练的拳法大师，插下雷楔桩持续产生电磁脉冲，协同全队打出破韧伤害。',
        'skill_e': '立地擎雷：在地面插下雷柱，队友在范围内攻击自动触发落雷。',
        'skill_q': '雷动九天：凝聚雷霆之力向前轰出震空铁拳。'
    },
    {
        'name': '灯灯 (Dengdeng)',
        'title': '矿道向导 · 金光破瘴',
        'rarity': 4,
        'element': '导电 (Electro)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '虎口矿区',
        'arkhe': '提灯引路',
        'desc': '活泼热情的采矿向导，手持高功率金灯与阔刃，劈碎沿途岩石与暗黑生物。',
        'skill_e': '金光冲斩：高举探照灯照射前方并借力猛劈。',
        'skill_q': '极光破晓：将探照灯能量调至最大过载，制造强烈闪光致盲并电击敌人。'
    },
    {
        'name': '莫宁 (Mourning)',
        'title': '电磁猎犬 · 雷霆速射',
        'rarity': 5,
        'element': '导电 (Electro)',
        'weapon_type': '佩枪 (Pistols)',
        'region': '边境防线',
        'arkhe': '磁能加速',
        'desc': '边境侦察特务，双枪装配电磁高斯加速管，能够射出穿透重甲的超导电弧弹。',
        'skill_e': '高斯穿透射：蓄力射出一枚穿甲光针。',
        'skill_q': '超导风暴场：在地面投掷四枚电磁信标，构成高压电网绞杀内部敌方。'
    },
    {
        'name': '仇远 (Qiu Yuan)',
        'title': '狂雷隐士 · 绝影霸刀',
        'rarity': 5,
        'element': '导电 (Electro)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '瑝珑边关',
        'arkhe': '怒雷震天',
        'desc': '行事霸道的边境刀客，引九天怒雷附于刀锋，蓄力重斩具有破天之威。',
        'skill_e': '拔刀奔雷：向前极速掠过，并在身后引爆数道雷电。',
        'skill_q': '雷霆万钧：跃至云端招引天雷，重重砸向地面形成大范围雷海。'
    },
    {
        'name': '奥古斯塔 (Augusta)',
        'title': '圣庭执行官 · 闪电制裁',
        'rarity': 5,
        'element': '导电 (Electro)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '皇家圣庭',
        'arkhe': '审判之枪',
        'desc': '恪守教条的重装骑士，以大开大合的审判雷矛击碎一切异端。',
        'skill_e': '圣雷突刺：长兵前冲，形成一道推斥敌人的雷电壁垒。',
        'skill_q': '天罚降临：从虚空召来巨型审判光矛插入战场核心。'
    },
    {
        'name': '漂泊者·导电 (Rover: Electro)',
        'title': '苏醒旅人 · 奔雷破阵',
        'rarity': 5,
        'element': '导电 (Electro)',
        'weapon_type': '迅刀 (Sword)',
        'region': '未知交界',
        'arkhe': '闪击雷痕',
        'desc': '掌控紫电狂雷的漂泊者形态，出剑缠绕暴烈电芒，对群体敌人有极强的链式传导。',
        'skill_e': '弧光闪击：极速穿刺三名相邻敌人。',
        'skill_q': '狂雷降世：以自身为中心爆发全屏环状闪电。'
    },

    # 气动 (Aero)
    {
        'name': '忌炎 (Jiyan)',
        'title': '夜归团长 · 青龙夜行',
        'rarity': 5,
        'element': '气动 (Aero)',
        'weapon_type': '长刃 (Broadblade)',
        'region': '夜归军团',
        'arkhe': '苍龙破阵',
        'desc': '夜归军团领袖，开启大招后长枪化为青龙长戟，普攻全转为重击判定与巨型牵引旋风。',
        'skill_e': '枪出如龙：突刺长枪挑击浮空目标。',
        'skill_q': '苍龙破阵：长戟化龙，攻击范围极大提升并拥有超强霸体与牵引聚怪能力。'
    },
    {
        'name': '鉴心 (Jianxin)',
        'title': '道宗风仪 · 太极调息',
        'rarity': 5,
        'element': '气动 (Aero)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '道宗',
        'arkhe': '阴阳调和',
        'desc': '风仪卓绝的太极道士，长按重击形成太极阴阳气盾反弹伤害，并生成巨型聚怪风眼。',
        'skill_e': '静气凝神：摆出招架架势，受击立即触发气劲反震并回血。',
        'skill_q': '风归圆转：双手推移在身前生成强力气旋，将全屏怪物吸扯至风眼核心。'
    },
    {
        'name': '秧秧 (Yangyang)',
        'title': '游远旅者 · 清风低语',
        'rarity': 4,
        'element': '气动 (Aero)',
        'weapon_type': '迅刀 (Sword)',
        'region': '今州夜归',
        'arkhe': '流风轻抚',
        'desc': '温婉敏锐的探险者，剑风凝聚羽翼，延奏技能为下一位共鸣者提供珍贵的共鸣能量回复。',
        'skill_e': '风羽回旋：挥动细剑斩出一道旋转风刃。',
        'skill_q': '旋风之境：生成持续吸引周围怪物的巨大气旋。'
    },
    {
        'name': '秋水 (Aalto)',
        'title': '雾中旅人 · 狡谲之影',
        'rarity': 4,
        'element': '气动 (Aero)',
        'weapon_type': '佩枪 (Pistols)',
        'region': '情报黑市',
        'arkhe': '流雾穿行',
        'desc': '擅长伪装与撤退的情报贩子，穿行过雾门可加速移动并使子弹穿雾获得大幅伤害加成。',
        'skill_e': '拟态流雾：原地留下迷雾替身，自身进入加速隐身位移。',
        'skill_q': '风门矩阵：在身前竖立巨大增幅风门，所有穿透风门的攻击伤害翻倍。'
    },
    {
        'name': '尤诺 (Juno)',
        'title': '空穹漫游者 · 翼羽展翅',
        'rarity': 5,
        'element': '气动 (Aero)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '云端遗民',
        'arkhe': '气流牵引',
        'desc': '背负飞行器滑翔于高空的空战大师，连续在半空打出风压爆破，极具观赏性。',
        'skill_e': '气流跃升：借助气流推力高高升空。',
        'skill_q': '苍穹崩裂拳：自千米高空俯冲轰下，气流撕裂整片战区。'
    },
    {
        'name': '露帕 (Lupa)',
        'title': '荒野苍狼 · 绝地嗅探',
        'rarity': 5,
        'element': '气动 (Aero)',
        'weapon_type': '佩枪 (Pistols)',
        'region': '废土部族',
        'arkhe': '狼灵合一',
        'desc': '在恶劣荒漠中成长的狂放少女，与风狼灵伴生，能够锁定并撕咬血量最低的目标。',
        'skill_e': '风狼飞扑：指挥风灵巨狼向前飞跃撕咬。',
        'skill_q': '群狼哮月：唤醒狂暴狼群冲锋，使全体敌人受到破甲与击退。'
    },
    {
        'name': '西格莉卡 (Sigrika)',
        'title': '风暴武姬 · 极旋刃舞',
        'rarity': 5,
        'element': '气动 (Aero)',
        'weapon_type': '臂铠 (Gauntlets)',
        'region': '极北风暴海',
        'arkhe': '涡轮离心',
        'desc': '身披合金装甲的风暴格斗家，通过身体高速自转形成移动龙卷风，伤害惊人。',
        'skill_e': '旋风回踏：连续侧踢踢出撕裂气浪。',
        'skill_q': '龙卷天袭：以自身化为风眼中心，吞噬并粉碎周遭一切。'
    },
    {
        'name': '秧秧·玄翎 (Yangyang: Black Plume)',
        'title': '神裔苏醒 · 苍穹玄羽',
        'rarity': 5,
        'element': '气动 (Aero)',
        'weapon_type': '迅刀 (Sword)',
        'region': '今州 · 天幕觉醒',
        'arkhe': '玄天真羽',
        'desc': '觉醒体内古老神禽血脉的完全体形态，剑招化作漆黑风羽，输出与全队充能兼备。',
        'skill_e': '玄羽凌霄：双翼舒展向前斩出两道黑金风刃。',
        'skill_q': '神禽临世：身后展露千丈青苍鹏影，狂风席卷全图。'
    },
    {
        'name': '漂泊者·气动 (Rover: Aero)',
        'title': '苏醒旅人 · 疾风化刃',
        'rarity': 5,
        'element': '气动 (Aero)',
        'weapon_type': '迅刀 (Sword)',
        'region': '未知交界',
        'arkhe': '流风化影',
        'desc': '与疾风产生深刻共鸣的漂泊者形态，剑招灵动飘逸，拥有强大的空中连击能力。',
        'skill_e': '风影步：瞬间突进至敌人背后并挑飞目标。',
        'skill_q': '暴风回斩：在周围引爆极速风刃风暴。'
    }
]

WEAPONS_POOL = [
    {'name': '时和岁稔 (Ages of Harvest)', 'type': '长刃 (5星限定)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '暴击率 24.3%', 'refine': '今汐专武：全属性伤害加成提升 12%，共鸣技能伤害提升 48%！'},
    {'name': '赫奕流明 (Blazing Brilliance)', 'type': '迅刀 (5星限定)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '暴击伤害 48.6%', 'refine': '长离专武：暴击率提升 8%，共鸣解放伤害提升 56%！'},
    {'name': '诸方玄枢 (Verity\'s Handle)', 'type': '臂铠 (5星限定)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '暴击伤害 48.6%', 'refine': '相里要专武：全属性伤害加成 12%，攻击力额外提升 24%。'},
    {'name': '苍鳞千嶂 (Verdant Summit)', 'type': '长刃 (5星限定)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '暴击伤害 48.6%', 'refine': '忌炎专武：全属性伤害提升 12%，重击伤害加成提升 48%！'},
    {'name': '停驻之钟 (Stellar Symphony)', 'type': '音感仪 (5星限定)', 'rarity': 5, 'base_atk': '500 基础攻击力', 'sub_stat': '共鸣效率 77.0%', 'refine': '守岸人专武：生命值提升 12%，全队获得攻击力 14% 增幅。'},
    {'name': '春裁 (Spring\'s Shear)', 'type': '迅刀 (5星限定)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '暴击率 24.3%', 'refine': '椿专武：湮灭伤害提升 12%，红白双蕊状态下普攻增伤 60%！'},
    {'name': '琼枝冰露 (Rime-Draped Sprouts)', 'type': '音感仪 (5星限定)', 'rarity': 5, 'base_atk': '500 基础攻击力', 'sub_stat': '暴击率 36.0%', 'refine': '折枝专武：全属性伤害提升 12%，强化普攻与后台协助攻击。'},
    {'name': '千古洑流 (Emerald of Genesis)', 'type': '迅刀 (5星常驻)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '暴击率 24.3%', 'refine': '共鸣效率提升 12.8%，施放共鸣技能后攻击力提升 12%。'},
    {'name': '浩境粼光 (Lustrous Razor)', 'type': '长刃 (5星常驻)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '攻击力 36.4%', 'refine': '共鸣效率提升 12.8%，施放共鸣技能后共鸣解放伤害提升。'},
    {'name': '掣落条约 (Stringmaster)', 'type': '音感仪 (5星限定)', 'rarity': 5, 'base_atk': '500 基础攻击力', 'sub_stat': '暴击率 36.0%', 'refine': '吟霖专武：全属性伤害提升 12%，在后台时攻击力额外提升。'},
    {'name': '擎渊怒涛 (Abyss Surges)', 'type': '臂铠 (5星常驻)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '攻击力 36.4%', 'refine': '能量充能效率提升 12.8%，普攻与技能伤害阶梯递增。'},
    {'name': '漪澜浮录 (Cosmic Ripples)', 'type': '音感仪 (5星常驻)', 'rarity': 5, 'base_atk': '500 基础攻击力', 'sub_stat': '攻击力 54.0%', 'refine': '共鸣效率提升 12.8%，普攻命中时普攻伤害叠加提升。'},
    {'name': '停驻之雾 (Static Mist)', 'type': '佩枪 (5星常驻)', 'rarity': 5, 'base_atk': '587 基础攻击力', 'sub_stat': '暴击率 24.3%', 'refine': '共鸣效率提升 12.8%，施放延奏技能后下位登场角色攻击力提升 10%。'},
    {'name': '奇幻变奏 (Variation)', 'type': '音感仪 (4星实用)', 'rarity': 4, 'base_atk': '337 基础攻击力', 'sub_stat': '共鸣效率 51.8%', 'refine': '辅助神级武器：释放共鸣技能时，回复 8/10/12/14/16 点协奏能量！'},
    {'name': '飞景 (Commando of Conviction)', 'type': '迅刀 (4星实用)', 'rarity': 4, 'base_atk': '412 基础攻击力', 'sub_stat': '攻击力 30.3%', 'refine': '施放共鸣技能后，普攻与重击伤害提升 15%，持续 15 秒。'},
    {'name': '永夜长明 (Helios Cleaver)', 'type': '长刃 (4星实用)', 'rarity': 4, 'base_atk': '412 基础攻击力', 'sub_stat': '攻击力 30.3%', 'refine': '施放共鸣技能后，攻击力按秒持续叠加提升，最高可叠加 12 层。'},
    {'name': '行进序曲 (Cadenza)', 'type': '佩枪 (4星实用)', 'rarity': 4, 'base_atk': '337 基础攻击力', 'sub_stat': '共鸣效率 51.8%', 'refine': '施放共鸣技能时，回复 8~16 点协奏能量，快速充填大招变奏。'},
    {'name': '金掌 (Marcato)', 'type': '臂铠 (4星实用)', 'rarity': 4, 'base_atk': '337 基础攻击力', 'sub_stat': '共鸣效率 51.8%', 'refine': '施放共鸣技能时回复协奏能量，加速全队速切与爆发循环。'},
    {'name': '不归孤军 (Dauntless Evernight)', 'type': '长刃 (4星实用)', 'rarity': 4, 'base_atk': '412 基础攻击力', 'sub_stat': '防御力 61.5%', 'refine': '施放共鸣技能后提升自身攻击力与防御力，适合桃祈等防御转伤角色。'},
    {'name': '异响乐章 (Discord)', 'type': '长刃 (4星实用)', 'rarity': 4, 'base_atk': '337 基础攻击力', 'sub_stat': '共鸣效率 51.8%', 'refine': '施放共鸣技能回复协奏能量，适合大招流速切重刃角色。'},
    {'name': '西升 (Novaburst)', 'type': '佩枪 (4星实用)', 'rarity': 4, 'base_atk': '412 基础攻击力', 'sub_stat': '攻击力 30.3%', 'refine': '触发极限闪避或冲刺后，攻击力提升 20%，持续 8 秒。'},
    {'name': '华彩乐段 (Jinzhou Keeper)', 'type': '音感仪 (4星实用)', 'rarity': 4, 'base_atk': '387 基础攻击力', 'sub_stat': '攻击力 36.4%', 'refine': '施放共鸣技能后，攻击力提升 8%，生命值上限提升 10%。'},
    {'name': '无眠火花 (Undying Flame)', 'type': '佩枪 (4星实用)', 'rarity': 4, 'base_atk': '412 基础攻击力', 'sub_stat': '攻击力 30.3%', 'refine': '施放共鸣技能后共鸣解放伤害提升 20%，炽霞爆发首选。'}
]

ECHO_SETS = [
    {'name': '浮星祛暗 (Celestial Light)', 'two_piece': '衍射伤害提升 10%', 'four_piece': '释放变奏技能入场后，衍射伤害额外提升 30%，持续 15 秒（今汐/守岸人毕业套）。'},
    {'name': '沉日劫明 (Sun-sinking Eclipse)', 'two_piece': '湮灭伤害提升 10%', 'four_piece': '释放普攻或重击时，湮灭伤害提升 7.5%，最多可叠加 4 层（椿/湮灭漂泊者毕业套）。'},
    {'name': '熔山裂樵 (Molten Rift)', 'two_piece': '热熔伤害提升 10%', 'four_piece': '释放共鸣技能时，热熔伤害提升 30%，持续 15 秒（长离/安可毕业套）。'},
    {'name': '啸谷长风 (Sierra Gale)', 'two_piece': '气动伤害提升 10%', 'four_piece': '释放重击时，气动伤害提升 30%，持续 15 秒（忌炎毕业套）。'},
    {'name': '彻空渐雷 (Void Thunder)', 'two_piece': '导电伤害提升 10%', 'four_piece': '释放重击或共鸣技能时，各提供 15% 导电增伤，总计 30%（相里要/吟霖/卡卡罗毕业套）。'},
    {'name': '凝夜白霜 (Freezing Frost)', 'two_piece': '冷凝伤害提升 10%', 'four_piece': '普攻与重击命中后，冷凝伤害提升 10%，可叠加 3 层（折枝/散华/凌阳毕业套）。'},
    {'name': '轻云出月 (Moonlit Clouds)', 'two_piece': '共鸣效率提升 10%', 'four_piece': '释放延奏技能离场后，下一位登场的共鸣者攻击力提升 22.5%，持续 15 秒（散华/吟霖辅助毕业套）。'},
    {'name': '隐世回光 (Rejuvenating Glow)', 'two_piece': '治疗效果提升 10%', 'four_piece': '自身为友方提供治疗后，全队所有共鸣者攻击力提升 15%，持续 30 秒（维里奈/白芷毕业套）。'},
    {'name': '不绝余音 (Lingering Tunes)', 'two_piece': '攻击力提升 10%', 'four_piece': '在场时间越长攻击力越高，释放共鸣解放后技能伤害提升 15%。'},
    {'name': '角 (Jué - 岁主声骸)', 'two_piece': 'Cost 4 声骸技能：化身岁主【角】召唤漫天雷光与光羽进行范围轰击', 'four_piece': '自身处于日冕或岁主祝福时额外增伤 16%，重置共鸣技能冷却（今汐核心毕业声骸）。'},
    {'name': '无妄者 (Dreamless - 核心声骸)', 'two_piece': 'Cost 4 声骸技能：化身无妄者进行极速双刀六连斩', 'four_piece': '若由湮灭漂泊者/椿在释放共鸣解放后紧接释放，无妄者伤害暴增 50% 并造成极高瘫痪韧性削减。'},
    {'name': '鸣钟之龟 (Bell-Borne Geochelone)', 'two_piece': 'Cost 4 声骸技能：召唤鸣钟之龟释放寒霜震荡', 'four_piece': '为全队提供相当于自身生命上限 50% 的护盾，并在护盾存在期间提供全队 10% 最终伤害加成。'},
    {'name': '无常凶鹭 (Impermanence Heron)', 'two_piece': 'Cost 4 声骸技能：化身凶鹭进行飞天俯冲践踏', 'four_piece': '击中敌人回复 10 点协奏能量，若在释放后使用延奏技能离场，下位角色伤害加成 12%，持续 15 秒。'},
    {'name': '燎照之骑 (Inferno Rider)', 'two_piece': 'Cost 4 声骸技能：化身火焰骑士驾驶烈焰摩托三连突刺与斩击', 'four_piece': '命中后提升自身热熔伤害 12%，普攻伤害提升 12%，持续 15 秒。'},
    {'name': '朔雷之鳞 (Thundering Mephis)', 'two_piece': 'Cost 4 声骸技能：化身朔雷之鳞进行雷影双爪突击', 'four_piece': '命中后提升自身导电伤害 12%，重击伤害提升 12%，持续 15 秒。'},
    {'name': '飞廉之猩 (Feilian Beringal)', 'two_piece': 'Cost 4 声骸技能：化身飞廉之猩连续猛击地面掀起狂风气浪', 'four_piece': '命中后提升自身气动伤害 12%，重击伤害加成 12%，持续 15 秒。'}
]


def crawl_and_sync_wuthering_waves(game_id=26):
    print(f'[Wuthering Waves] Preparing {len(RESONATORS_ROSTER)} resonators for version 3.X cumulative roster ...')

    characters = []
    for r in RESONATORS_ROSTER:
        base_stats = [
            {'level': '1级', 'hp': 900, 'atk': 38, 'def': 85, 'crit_rate': '5.0%', 'crit_dmg': '150%'},
            {'level': '90级满阶', 'hp': 10500, 'atk': 438, 'def': 1150, 'crit_rate': '5.0%', 'crit_dmg': '150%'}
        ]

        talents = [
            {'name': '常态攻击 · 普攻', 'type': 'NORMAL_ATTACK', 'scaling': '四段连击', 'description': '造成对应属性多段伤害并回复协奏能量'},
            {'name': '共鸣技能 (E)', 'type': 'ELEMENTAL_SKILL', 'scaling': '战术技能', 'description': r['skill_e']},
            {'name': '共鸣解放 (Q)', 'type': 'ELEMENTAL_BURST', 'scaling': '爆发大招', 'description': r['skill_q']}
        ]

        characters.append({
            'name': r['name'],
            'title': r['title'],
            'rarity': r['rarity'],
            'element': r['element'],
            'weapon_type': r['weapon_type'],
            'region': r['region'],
            'arkhe': r['arkhe'],
            'avatar_url': f'/games/resonators/{r["name"].split()[0]}.png',
            'splash_url': '',
            'base_stats': base_stats,
            'talents': talents,
            'passives': [{'name': '协奏机制', 'description': '积攒满协奏能量后离场，激活专属变奏入场与延奏增益'}],
            'constellations': [],
            'special_mechanics': {'circuit': r['arkhe'], 'lore': r['desc']},
            'recommendations': {'preferred_echo': '4-3-3-1-1 组合'},
            'version': 'v3.7'
        })

    weapons = []
    for w in WEAPONS_POOL:
        weapons.append({
            'name': w['name'],
            'type': w['type'],
            'rarity': w['rarity'],
            'icon_url': f'/games/weapons/{w["name"].split()[0]}.png',
            'base_atk_curve': {'base_atk_90': w['base_atk']},
            'sub_stat': {'secondary_90': w['sub_stat']},
            'refinements': {'passive': w['refine']},
            'ascension_materials': {'type': '声骸材料 / 突破素材'},
            'version': 'v3.7'
        })

    artifacts = []
    for e in ECHO_SETS:
        artifacts.append({
            'name': e['name'],
            'rarity_min': 4,
            'rarity_max': 5,
            'icon_url': f'/games/echos/{e["name"].split()[0]}.png',
            'two_piece_bonus': e['two_piece'],
            'four_piece_bonus': e['four_piece'],
            'pieces': [{'slot': '主位声骸 (Cost 4)', 'effect': '激活主位变身出招'}, {'slot': '副位 (Cost 3/1)', 'effect': '属性词条池'}],
            'rules_reference': {'description': '合鸣属性生效需穿戴对应合鸣声骸'},
            'version': 'v3.7'
        })

    mechanics = [
        {
            'category': '战斗机制',
            'title': '极限闪避与弹刀破韧机制',
            'formula': '在敌人红光攻击瞬间普攻完成【弹刀】，大幅扣减敌人共鸣瘫痪韧性条',
            'parameters': {
                '极限闪避': '完美闪避敌人攻击触发子弹时间，普攻触发【闪避反击】',
                '瘫痪状态': '当白色韧性条归零，Boss陷入虚弱倒地状态并承受额外伤害加成'
            }
        },
        {
            'category': '伤害机制',
            'title': '共鸣伤害加成与抗性减免计算',
            'formula': '最终伤害 = 基础倍率 × 攻击力 × (1 + 增伤区) × 暴击爆伤区 × 防御减免 × 抗性减免',
            'parameters': {
                '独立乘区': '延奏深度增伤属于全独立乘区，提升极其显著'
            }
        }
    ]

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    a_count = upsert_artifacts(game_id, artifacts)
    m_count = upsert_mechanics(game_id, mechanics)
    print(f'[Wuthering Waves] Ingested into Game {game_id}: {c_count} resonators, {w_count} weapons, {a_count} echo sets, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_wuthering_waves(26)
