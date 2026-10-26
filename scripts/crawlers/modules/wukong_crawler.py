"""
Black Myth: Wukong (黑神话：悟空) Comprehensive Game Data Module
Ingests Spells (法术), Transformations (变身/化身), Bosses & Elites (妖王/头目/精魄),
Legendary Staffs (兵刃神兵), Armors/Vessels (披挂防具/法宝), and Combat Mechanics (棍法识破/架势法则)
into Game 4 (黑神话：悟空).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

BOSSES_AND_TRANSFORMATIONS = [
    # 核心流派与形态
    {
        'name': '天命人 · 识破棍圣 (The Destined One)',
        'title': '花果山天命人 · 六根重聚者',
        'rarity': 5,
        'element': '全系变身 / 仙术神通',
        'weapon_type': '神兵棍棒 (劈棍/立棍/戳棍)',
        'region': '花果山 / 交界西行',
        'arkhe': '意根气力',
        'talents': [
            {'name': '奇术 · 定身法', 'type': 'ELEMENTAL_SKILL', 'scaling': '法力消耗: 60', 'description': '虚空画咒定住敌方肉身神魂数秒，蓄力重击破定可造成爆裂额外增伤！'},
            {'name': '身法 · 聚形散气', 'type': 'ELEMENTAL_SKILL', 'scaling': '法力消耗: 45', 'description': '留下白气假身吸引敌方仇恨，真身隐匿潜行，潜行破隐一击 100% 暴击并造成巨额破隐加成！'},
            {'name': '身法 · 铜头铁臂', 'type': 'ELEMENTAL_SKILL', 'scaling': '法力消耗: 30', 'description': '金石化身格挡敌方正面攻击，弹刀震飞轻武器敌人并使其陷入大硬直！'},
            {'name': '毫毛 · 身外身法', 'type': 'ELEMENTAL_BURST', 'scaling': '法力消耗: 120', 'description': '拔一把毫毛吹出数十位分身猴群，群起挥棍围攻并复制本体技能！'},
            {'name': '奇术 · 禁字诀', 'type': 'ELEMENTAL_BURST', 'scaling': '法力消耗: 全部', 'description': '封禁自身全部法术与法宝，将全部法力值与气力上限按高额比例转化为永久物理攻击力与暴击率！'}
        ],
        'passives': [
            {'name': '变身 · 赤潮 (广智)', 'description': '变身狼妖广智，手持烈焰双头赤刀高速挥砍，附带烈火焚烧积表'},
            {'name': '变身 · 金 (寅虎)', 'description': '化身威严寅虎，手握玄铁巨刃展开霸体招架反击，刀意滔天'}
        ],
        'base_stats': [{'level': '90', 'hp': 820, 'mp': 360, 'stamina': 320, 'atk': 165, 'def': 140}],
        'recommendations': {'weapon': '如意金箍棒', 'armor': '大圣神珍披挂套', 'vessel': '芭蕉扇', 'spirit': '幽魂'}
    },
    {
        'name': '天命人 · 齐天大圣模式 (Great Sage Reborn)',
        'title': '神珍披挂全激活 · 齐天大圣全盛姿态',
        'rarity': 5,
        'element': '齐天神意',
        'weapon_type': '如意金箍棒',
        'region': '花果山水帘洞',
        'arkhe': '大圣神意',
        'talents': [
            {'name': '大圣轻棍终极连段', 'type': 'NORMAL_ATTACK', 'scaling': '5段大开大合连击', 'description': '完全改写轻棍攻击动捕模组，挥舞金箍棒施展大开大合的大圣招式，范围巨大且附带残影！'},
            {'name': '大圣四阶擎天劈棍', 'type': 'ELEMENTAL_BURST', 'scaling': '气力消耗: 4段', 'description': '金箍棒暴长百丈捅穿云霄，重重砸向地面引发大范围金色冲击波，造成毁灭级伤害！'}
        ],
        'passives': [
            {'name': '神珍共鸣', 'description': '装备凤翅紫金冠、锁子黄金甲、点翠飞龙釬、藕丝步云履四件套时常驻激活。'},
            {'name': '神意回流', 'description': '攻击命中时大幅加快气力恢复速度，翻滚闪避带金色云雾残影。'}
        ]
    },
    # 传奇妖王 Boss
    {
        'name': '妖王 · 虎先锋 (Tiger Vanguard)',
        'title': '黄风大圣麾下第一先锋 · 卧虎寺血池主宰',
        'rarity': 5,
        'element': '血气刀术 / 铜头石化',
        'weapon_type': '虎魄长刀 / 赤手空拳',
        'region': '黄风岭 · 卧虎寺',
        'arkhe': '血煞之气',
        'talents': [
            {'name': '血池石化 · 铜头铁臂', 'type': 'BOSS_SKILL', 'scaling': '格挡硬直', 'description': '化作石雕之身抵挡一切攻击，随后瞬间拔刀血影突刺斩杀！'},
            {'name': '血影闪 · 连环斩击', 'type': 'BOSS_BURST', 'scaling': '高爆发多段', 'description': '身形化作血雾消失，在天命人四周进行多重瞬移血斩，最后重重跃起劈砍！'}
        ],
        'passives': [
            {'name': '拳刀双绝', 'description': '近身拳法猛击接续长刀斩击，攻击衔接极为紧密，弹刀反击窗口苛刻。'}
        ]
    },
    {
        'name': '妖王 · 黄风大圣 (Yellow Wind Sage)',
        'title': '黄风岭之主 · 操纵三昧神风者',
        'rarity': 5,
        'element': '三昧神风 / 地裂风暴',
        'weapon_type': '三股钢叉 / 佛头法宝',
        'region': '黄风岭 · 黄风阵',
        'arkhe': '狂风风眼',
        'talents': [
            {'name': '漫天黄沙 · 三昧神风', 'type': 'BOSS_BURST', 'scaling': '全屏风暴', 'description': '引动天地失色的三昧神风，形成巨大狂风龙卷阻隔视线并造成持续击飞，需【定风珠】定住风眼！'},
            {'name': '佛头地动 · 巨力轰砸', 'type': 'BOSS_SKILL', 'scaling': '巨额物理震波', 'description': '双手举起巨大石佛佛首，向天命人猛烈砸击引发裂地冲击波。'}
        ],
        'passives': [
            {'name': '风势护体', 'description': '神风环绕期间天命人无法蓄力，定风珠可瞬间破除其护体神风并使其陷入大瘫痪。'}
        ]
    },
    {
        'name': '妖王 · 百眼魔君 (Hundred-Eyed Demon Lord)',
        'title': '盘丝岭黄花观观主 · 千目金光道长',
        'rarity': 5,
        'element': '毒雾剧毒 / 百目金光幻境',
        'weapon_type': '雷火拂尘 / 蜈蚣巨足',
        'region': '盘丝岭 · 黄花观',
        'arkhe': '金光邪目',
        'talents': [
            {'name': '千目齐睁 · 黄帝金光罩', 'type': 'BOSS_BURST', 'scaling': '天地异色结界', 'description': '肋下千眼齐齐睁开，天色转为暗黄金光，大幅压制天命人气力上限与移速，需【绣花针】破去幻境！'},
            {'name': '地脉毒雷 · 遁地突袭', 'type': 'BOSS_SKILL', 'scaling': '毒雷混合伤害', 'description': '庞大蜈蚣躯体潜入地下，引爆沿途毒雷陷阱后从地底破土冲天扑杀！'}
        ],
        'passives': [
            {'name': '百目幻境', 'description': '金光结界内天命人攻击大幅削弱，绣花针破除后可令其千眼尽盲并瘫痪。'}
        ]
    },
    {
        'name': '妖王 · 黄眉 (Yellowbrow)',
        'title': '小西天雷音寺之主 · 金钹假佛',
        'rarity': 5,
        'element': '雷电金刚 / 佛光幻术',
        'weapon_type': '人种袋 / 金钹金刚杵',
        'region': '小西天 · 小雷音寺',
        'arkhe': '假佛雷音',
        'talents': [
            {'name': '金身不坏 · 绝对弹刀', 'type': 'BOSS_SKILL', 'scaling': '全免物理伤', 'description': '通体化为赤金之躯，免疫轻攻击与识破，唯有三段蓄力重击或特定法宝方能敲破金身！'},
            {'name': '人种袋收纳 · 雷音业报', 'type': 'BOSS_BURST', 'scaling': '因果业火雷击', 'description': '祭出后天人种袋遮天蔽日，将天命人吸入其内施加业障轰击！'}
        ],
        'passives': [
            {'name': '度化心魔', 'description': '战斗中不断以佛偈言语攻心，施加神念干扰与雷电迟滞。'}
        ]
    },
    {
        'name': '妖王 · 夜叉王 / 红孩儿 (Red Boy / Yaksha King)',
        'title': '火焰山魔王 · 吞食牛魔血脉化身夜叉',
        'rarity': 5,
        'element': '三昧真火 / 业火刀刃',
        'weapon_type': '夜叉血刃',
        'region': '火焰山 · 火云洞',
        'arkhe': '业火凶煞',
        'talents': [
            {'name': '业火红莲 · 三昧火海', 'type': 'BOSS_BURST', 'scaling': '持续火焚积表', 'description': '释放焚尽虚空的三昧真火，全场地面化作滚烫熔岩，持续造成极高火灼真伤！'},
            {'name': '夜叉狂刃 · 极速乱舞', 'type': 'BOSS_SKILL', 'scaling': '高机动连续追击', 'description': '手持巨大夜叉骨刃进行大范围高速穿梭滑斩，剑气附带高温烈焰。'}
        ],
        'passives': [
            {'name': '绝命战意', 'description': '生命值低于 50% 时进入狂暴形态，攻击速度与火属性增伤大幅暴涨。'}
        ]
    },
    {
        'name': '妖王 · 小黄龙 (Yellow Loong)',
        'title': '亢金四龙之首 · 傲骨龙裔剑圣',
        'rarity': 5,
        'element': '真龙雷霆 / 飞剑突刺',
        'weapon_type': '飞龙宝枪 / 龙雷双剑',
        'region': '盘丝岭 · 堕龙壁',
        'arkhe': '亢金龙雷',
        'talents': [
            {'name': '龙雷冲天 · 空中三连俯冲', 'type': 'BOSS_BURST', 'scaling': '极速三段雷闪', 'description': '悬浮半空积蓄雷霆，以肉眼难辨的速度向天命人进行连续三次超远距离空中折线雷霆俯冲！'},
            {'name': '雷芒刀阵 · 完美看破', 'type': 'BOSS_SKILL', 'scaling': '反击秒杀', 'description': '单手持枪傲立场中摆出反击架势，若在此期间贸然攻击将遭遇毁天灭地的雷光反击刺杀！'}
        ],
        'passives': [
            {'name': '龙威压制', 'description': '雷蛰状态下天命人受到伤害翻倍，闪避时机要求极高，为全游戏最强单挑 Boss 之一。'}
        ]
    },
    {
        'name': '妖王 · 二郎神 · 杨戬 (Erlang Shen)',
        'title': '昭惠显圣二郎真君 · 梅山之巅终极战神',
        'rarity': 5,
        'element': '天眼神光 / 万剑归宗 / 法相天地',
        'weapon_type': '三尖两刃神枪 / 哮天神犬',
        'region': '梅山 · 隐·紫云山隐藏地图',
        'arkhe': '神仙无上法',
        'talents': [
            {'name': '天眼金光 · 照破虚妄', 'type': 'BOSS_SKILL', 'scaling': '神圣光束穿透', 'description': '额间天目睁开射出贯穿全场的烈日金光，无视闪避无敌帧，击中直接击飞破除隐身！'},
            {'name': '万刃归宗 · 飞剑暴风雨', 'type': 'BOSS_BURST', 'scaling': '上百把飞剑雨', 'description': '三尖两刃枪幻化出数百把金色神剑铺天盖地攒射而下，随后本体凌空暴劈！'},
            {'name': '法相天地 · 巨神对决', 'type': 'BOSS_BURST', 'scaling': '天地异象巨战', 'description': '化身万丈巨人法相，与巨猿形态天命人在冰峰绝顶展开惊天地泣鬼神的史诗决战！'}
        ],
        'passives': [
            {'name': '不坏白盾', 'description': '常驻高韧性神力白盾，唯有识破连击、芭蕉扇神风或高爆发蓄力重棍方能击破白盾造成硬直。'}
        ]
    },
    {
        'name': '妖王 · 大圣残躯 (Great Sage Broken Body)',
        'title': '齐天大圣遗留肉身 · 终极六根意志考验',
        'rarity': 5,
        'element': '齐天大圣全系武艺',
        'weapon_type': '如意金箍棒',
        'region': '花果山 · 水帘洞石卵内',
        'arkhe': '大圣神魂',
        'talents': [
            {'name': '反夺定身法 · 借力打力', 'type': 'BOSS_SKILL', 'scaling': '反弹定身', 'description': '若天命人对其施放定身法，大圣残躯将抬手拂袖反弹定身咒，将天命人定在原地！'},
            {'name': '四大架势随心转换', 'type': 'BOSS_BURST', 'scaling': '棍法极致', 'description': '熟练运用劈棍立棍戳棍，甚至能在立棍顶端饮酒嘲讽，招式灵动霸道绝伦！'}
        ],
        'passives': [
            {'name': '武艺之巅', 'description': '精通天命人所拥有的一切招式并以更高阶的形态打出，是整场西行终极试炼之峰。'}
        ]
    },
    # 精英头目与变身
    {
        'name': '头目 · 幽魂 (Wandering Wight)',
        'title': '苍狼林怨念大头高僧',
        'rarity': 4,
        'element': '金钟重压 / 纯阳震地',
        'weapon_type': '巨头铁颅 / 罗汉掌',
        'region': '黑风山 · 苍狼林',
        'arkhe': '怨煞精魄',
        'talents': [
            {'name': '大头猛砸 · 震天头槌', 'type': 'BOSS_SKILL', 'scaling': '巨额破韧', 'description': '向前猛烈踏步后运起全身力气甩出大头砸击，震裂地面引发大冲击波！'}
        ],
        'passives': [
            {'name': '精魄掉落', 'description': '击败后可吸收【精魄·幽魂】，装备常驻+30防御力，主动施放可化身大头施展巨力头槌！'}
        ]
    },
    {
        'name': '头目 · 广智 (Guangzhi)',
        'title': '黑风山苍狼刀僧 · 赤潮之主',
        'rarity': 4,
        'element': '烈火双头刀',
        'weapon_type': '赤潮双头刃',
        'region': '黑风山 · 苍狼林林外',
        'arkhe': '烈火狼意',
        'talents': [
            {'name': '旋风烈火斩', 'type': 'BOSS_SKILL', 'scaling': '多段火焰连击', 'description': '高速旋转双头刀划出火焰刀轮，快速堆叠火灼异常状态！'}
        ],
        'passives': [
            {'name': '变身法门', 'description': '击败后天命人习得【赤潮】变身，战局中随时可化身广智进行烈焰近战。'}
        ]
    },
    {
        'name': '头目 · 寅虎 (Yin Tiger)',
        'title': '六六村铸剑神将 · 威严刀圣',
        'rarity': 5,
        'element': '玄铁刀气 / 霸体弹反',
        'weapon_type': '玄铁斩马巨刃',
        'region': '六六村 · 画卷洞天',
        'arkhe': '虎神刀意',
        'talents': [
            {'name': '霸体架招 · 迎锋反击', 'type': 'BOSS_SKILL', 'scaling': '刀阵格挡', 'description': '以巨刃立于身前招架，反制对手攻击并挥出巨大月牙刀气！'}
        ],
        'passives': [
            {'name': '变身 · 金 (寅虎)', 'description': '切磋击败后获得【变身·金】，可化身寅虎手持巨刀施展霸体斩。'}
        ]
    },
    {
        'name': '头目 · 灵虚子 (Lingxuzi)',
        'title': '观音禅院白狼巨兽',
        'rarity': 4,
        'element': '苍狼扑咬 / 高台伏击',
        'weapon_type': '狼爪尖牙',
        'region': '黑风山 · 观音禅院',
        'arkhe': '古刹兽性',
        'talents': [
            {'name': '飞檐走壁 · 高空扑杀', 'type': 'BOSS_SKILL', 'scaling': '范围巨兽震击', 'description': '跃上禅院残破大殿屋顶，锁定目标后凶猛扑砸而下！'}
        ],
        'passives': [
            {'name': '惧火之躯', 'description': '受火属性攻击（如广智赤潮或辟火罩）时受击硬直明显加大。'}
        ]
    },
    {
        'name': '头目 · 毒敌大王 (Scorpionlord)',
        'title': '紫云山隐秘毒蝎之主',
        'rarity': 5,
        'element': '剧毒蝎尾 / 双螯狂暴',
        'weapon_type': '毒蝎双螯 / 倒马毒桩',
        'region': '紫云山 · 绕仙居',
        'arkhe': '倒马剧毒',
        'talents': [
            {'name': '倒马毒桩 · 致命尾刺', 'type': 'BOSS_BURST', 'scaling': '极速三段破防刺', 'description': '蝎尾倒钩以迅雷不及掩耳之势连续穿刺，附带致命剧毒持续掉血！'}
        ],
        'passives': [
            {'name': '酩酊酒意', 'description': '狂暴横扫大开大合，破霸体要求极高。'}
        ]
    }
]

STAFFS_AND_WEAPONS = [
    {
        'name': '如意金箍棒 (Ruyi Jingu Bang)',
        'type': '神珍棍棒',
        'rarity': 5,
        'base_atk_curve': [{'level': '90', 'atk': 135, 'desc': '攻击力 135，暴击率 6%'}],
        'sub_stat': {'effect': '第四段气力蓄力无时间消退限制，常驻保持！'},
        'refinements': [{'rank': '定海神针', 'desc': '棍长随心，通体金光，蓄力打出第 4 阶绝命重棍时引动金光万道，伤害摧枯拉朽！'}],
        'ascension_materials': [{'tier': '主线终章', 'material': '水帘洞深处石卵继承大圣神珍'}]
    },
    {
        'name': '三尖两刃枪 (Tri-point Double-edged Spear)',
        'type': '神珍长枪',
        'rarity': 5,
        'base_atk_curve': [{'level': '90', 'atk': 135, 'desc': '攻击力 135，暴击率 6%'}],
        'sub_stat': {'effect': '突刺切手技强化，所有戳棍动作附加神圣剑气！'},
        'refinements': [{'rank': '二郎真君神兵', 'desc': '将所有戳棍切手技动作演化为连续飞剑攒射，剑气如龙贯穿敌人！'}],
        'ascension_materials': [{'tier': '隐·梅山', 'material': '击败二郎神·杨戬后铸造'}]
    },
    {
        'name': '混铁棍 (Dark Iron Staff)',
        'type': '特品棍棒',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 110, 'desc': '攻击力 110，防御力 +30'}],
        'sub_stat': {'effect': '厚重沉凝：根据自身当前总防御力数值按比例额外提升攻击力！'},
        'refinements': [{'rank': '牛魔混铁', 'desc': '重甲高防御配装流派终极毕业武器，防御越高攻击力越爆炸。'}],
        'ascension_materials': [{'tier': '火焰山·避水洞', 'material': '击败碧水金睛兽掉落玄铁铸造'}]
    },
    {
        'name': '飞龙宝杖 (Staff of Blazing Wind)',
        'type': '特品长杖',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 108, 'desc': '攻击力 108，暴击率 4%'}],
        'sub_stat': {'effect': '蓄力重击引动雷鸣飞龙，召唤龙形闪电冲击波。'},
        'refinements': [{'rank': '亢金飞龙', 'desc': '蓄力重击打出时飞龙显形撕咬，额外附加雷属性范围伤害。'}],
        'ascension_materials': [{'tier': '黄风岭隐关', 'material': '击败亢金龙掉落神料'}]
    },
    {
        'name': '楮白枪 (Spikestaff)',
        'type': '特品枪矛',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 75, 'desc': '攻击力 75，攻击速度提升'}],
        'sub_stat': {'effect': '轻棍中穿插退步戳刺，极大提高变招灵活性与出招帧数。'},
        'refinements': [{'rank': '灵动枪法', 'desc': '枪矛类武器独有模组，切手技气力消耗降低 20%。'}],
        'ascension_materials': [{'tier': '小西天·苦海', 'material': '击败白枪道僧掉落'}]
    },
    {
        'name': '几丁棍 (Chitin Staff)',
        'type': '特品毒棍',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 80, 'desc': '攻击力 80，暴击率 5%'}],
        'sub_stat': {'effect': '攻击附带毒素伤害积表，使目标持续中毒。'},
        'refinements': [{'rank': '百足毒刺', 'desc': '对中毒状态敌人造成的重击伤害额外提升 25%。'}],
        'ascension_materials': [{'tier': '盘丝洞底层', 'material': '击败百足虫掉落毒刺'}]
    },
    {
        'name': '鳞棍 · 蟠龙 (Loongwhorl Ribbon Staff)',
        'type': '特品龙棍',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 70, 'desc': '攻击力 70，劈棍伤害提升'}],
        'sub_stat': {'effect': '劈棍蓄力猛砸时引动水浪雷鸣波纹。'},
        'refinements': [{'rank': '龙威激荡', 'desc': '立棍撑杆跳劈时附加范围激波。'}],
        'ascension_materials': [{'tier': '赤髯龙隐关', 'material': '击败黑风山赤髯龙'}]
    },
    {
        'name': '业火杖 (Flaming Rod)',
        'type': '特品火杖',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 100, 'desc': '攻击力 100，火属性增伤'}],
        'sub_stat': {'effect': '重击在地面留下一道烈火熔岩裂隙。'},
        'refinements': [{'rank': '三昧炽烈', 'desc': '处于火焚状态下的敌人受到的识破伤害提升 30%。'}],
        'ascension_materials': [{'tier': '火焰山·丹灶谷', 'material': '击败火焰山火兽掉落'}]
    },
    {
        'name': '狼牙棒 (Spiked Club)',
        'type': '特品重棒',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 80, 'desc': '攻击力 80，防御力 +20'}],
        'sub_stat': {'effect': '强韧度大幅提高，轻棍连击中不易被打断。'},
        'refinements': [{'rank': '狂徒重击', 'desc': '蓄力重棍期间获得霸体效果，硬抗敌人攻击施展反击。'}],
        'ascension_materials': [{'tier': '小西天·雪山径', 'material': '击败无量蝠或黄眉侍从'}]
    },
    {
        'name': '兽棍 · 熊罴 (Bear Bone Staff)',
        'type': '特品兽骨棍',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 85, 'desc': '攻击力 85，暴击率 4%'}],
        'sub_stat': {'effect': '身法【聚形散气】潜行破隐一击暴击伤害额外翻倍！'},
        'refinements': [{'rank': '黑风散气', 'desc': '破隐一击命中后迅速恢复 1 点气力段数。'}],
        'ascension_materials': [{'tier': '黑风洞顶', 'material': '击败黑风大王 / 黑熊精'}]
    },
    {
        'name': '铜云棒 (Cloud-Patterned Staff)',
        'type': '仙品棍棒',
        'rarity': 4,
        'base_atk_curve': [{'level': '90', 'atk': 95, 'desc': '攻击力 95，气力恢复提升'}],
        'sub_stat': {'effect': '翻滚闪避消耗的气力减少 15%。'},
        'refinements': [{'rank': '祥云流风', 'desc': '闪避后轻击出招速度提升，手感极其轻快流畅。'}],
        'ascension_materials': [{'tier': '六六村铸造', 'material': '寅虎处打造'}]
    },
    {
        'name': '出云棍 (Cloud Prowler)',
        'type': '良品长棍',
        'rarity': 3,
        'base_atk_curve': [{'level': '90', 'atk': 60, 'desc': '攻击力 60，初期开荒神兵'}],
        'sub_stat': {'effect': '轻击连段伤害逐段递增 5%。'},
        'refinements': [{'rank': '轻巧顺手', 'desc': '适合前期熟悉三大棍法架势切换的基础神兵。'}],
        'ascension_materials': [{'tier': '第一回开荒', 'material': '黑风山土地庙打造'}]
    }
]

ARMORS_AND_VESSELS = [
    {
        'name': '大圣神珍披挂套 (齐天大圣套)',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '释放法术或切手技后，短时间内大幅提升暴击率 12% 与气力恢复速度。',
        'four_piece_bonus': '凑齐凤翅紫金冠、锁子黄金甲、点翠飞龙釬、藕丝步云履四件套，可永久激活【大圣形态】，轻棍连击动作转化为大圣飘逸大开大合招式，四段蓄力不退！',
        'pieces': [
            {'slot': '头冠', 'name': '凤翅紫金冠', 'main_stat_rule': '防御力 +45，法力上限 +60，暴击率 +3%'},
            {'slot': '衣甲', 'name': '锁子黄金甲', 'main_stat_rule': '防御力 +110，气力恢复速度 +15%'},
            {'slot': '臂甲', 'name': '点翠飞龙釬', 'main_stat_rule': '防御力 +38，暴击伤害 +18%'},
            {'slot': '腿甲', 'name': '藕丝步云履', 'main_stat_rule': '防御力 +52，移速增加，翻滚无敌帧增加'}
        ],
        'rules_reference': {'set_type': '大圣神珍毕业套', 'unlock': '花果山主线收齐四大披挂'}
    },
    {
        'name': '赭黄套装 (Ochre Armor Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '消耗气力施展重击后，大幅减少下一次定身法或聚形散气的冷却时间。',
        'four_piece_bonus': '破定击中敌人时，根据敌人受创硬直瞬间恢复 1 段完整气力，并附加土属性石崩伤害！',
        'pieces': [
            {'slot': '头盔', 'name': '赭黄头盔', 'main_stat_rule': '防御力 +32，气力上限 +25'},
            {'slot': '战袍', 'name': '赭黄战袍', 'main_stat_rule': '防御力 +82，石化抗性 +15'},
            {'slot': '臂甲', 'name': '赭黄臂甲', 'main_stat_rule': '防御力 +28，破霸体伤害 +10%'},
            {'slot': '护腿', 'name': '赭黄护腿', 'main_stat_rule': '防御力 +36，减少蓄力体力消耗'}
        ],
        'rules_reference': {'set_type': '第二回黄风岭套装', 'unlock': '击败虎先锋与石先锋打造'}
    },
    {
        'name': '行者套装 (Pilgrim Set)',
        'rarity_min': 3,
        'rarity_max': 5,
        'two_piece_bonus': '疾跑时每秒积攒气力，并在疾跑中可直接消耗气力施展滑铲飞踢重击！',
        'four_piece_bonus': '脱战与跑图移动速度提升 25%，疾跑十秒后进入【神行】状态，下一击轻棍或重击伤害暴增 100%！跑图刷怪首选。',
        'pieces': [
            {'slot': '戒箍', 'name': '行者戒箍', 'main_stat_rule': '防御力 +20，移速 +5%'},
            {'slot': '直裰', 'name': '行者直裰', 'main_stat_rule': '防御力 +55，疾跑体力消耗减半'},
            {'slot': '护腕', 'name': '行者护腕', 'main_stat_rule': '防御力 +18，气力回复 +8%'},
            {'slot': '绑腿', 'name': '行者绑腿', 'main_stat_rule': '防御力 +24，跑速增加'}
        ],
        'rules_reference': {'set_type': '开荒跑图神器', 'unlock': '黑风山土地庙初期打造'}
    },
    {
        'name': '乌金套装 (Ebony Gold Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '身法【聚形散气】冷却时间减少 4 秒。',
        'four_piece_bonus': '聚形散气在原地留下的白气假身会产生黑风爆裂，对周围敌人造成大范围暗影冲击并将其击退！',
        'pieces': [
            {'slot': '头冠', 'name': '乌金皂罗袍', 'main_stat_rule': '防御力 +78，法力值 +40'},
            {'slot': '臂甲', 'name': '乌金护臂', 'main_stat_rule': '防御力 +26，潜行破隐伤害 +20%'},
            {'slot': '步履', 'name': '乌金步履', 'main_stat_rule': '防御力 +34，隐匿持续时间延长'}
        ],
        'rules_reference': {'set_type': '刺客隐匿流', 'unlock': '击败黑熊精获取'}
    },
    {
        'name': '龙鳞套装 (Dragon Scale Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '雷蛰抗性大幅提升，受到雷属性攻击伤害减半。',
        'four_piece_bonus': '天命人自身武器攻击附加雷属性伤害，施展劈棍雷闪时引发落雷轰顶，对抗龙系敌人特攻！',
        'pieces': [
            {'slot': '战袍', 'name': '龙鳞战袍', 'main_stat_rule': '防御力 +92，雷抗性 +30'},
            {'slot': '护手', 'name': '龙鳞护手', 'main_stat_rule': '防御力 +30，雷属性增伤 +15%'},
            {'slot': '胫甲', 'name': '龙鳞胫甲', 'main_stat_rule': '防御力 +40，免疫落雷硬直'}
        ],
        'rules_reference': {'set_type': '亢金雷龙抗性套装', 'unlock': '击败小黄龙与亢金龙打造'}
    },
    {
        'name': '厌火套装 (Yaksha Fiend Set)',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '自身处于低血量（低于 50%）时，暴击率提升 15%，攻击力提升 20%。',
        'four_piece_bonus': '血量越低防御力转化为攻击力的比例越高，红血背水一战极限反杀流核心神装！',
        'pieces': [
            {'slot': '恶鬼面', 'name': '夜叉恶鬼面', 'main_stat_rule': '防御力 +35，暴击率 +5%'},
            {'slot': '战袍', 'name': '厌火战袍', 'main_stat_rule': '防御力 +88，背水伤害加成'},
            {'slot': '臂甲', 'name': '厌火臂甲', 'main_stat_rule': '防御力 +30，生命偷取 +3%'},
            {'slot': '护腿', 'name': '厌火护腿', 'main_stat_rule': '防御力 +38，濒死霸体'}
        ],
        'rules_reference': {'set_type': '夜叉狂暴背水套', 'unlock': '击败夜叉王打造'}
    },
    # 法宝四大神物 (Vessels)
    {
        'name': '四大法宝 · 定风珠 (Wind Tamer)',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '常驻被动属性：提升天命人基础减伤率 5%，免疫强风迟滞。',
        'four_piece_bonus': '主动催动：祭出定风珠定住漫天神风，完全压制全场风暴环境，大幅提升自身霸体强韧度并令黄风大圣瘫痪！',
        'pieces': [
            {'slot': '定风珠本源', 'name': '定风神珠', 'main_stat_rule': '减伤率 +5%，定住狂风'}
        ],
        'rules_reference': {'set_type': '第二回隐藏法宝', 'unlock': '完成斯哈哩国黄金之国任务'}
    },
    {
        'name': '四大法宝 · 辟火罩 (Fireproof Cloak)',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '常驻被动属性：完全免疫一切地面火焚伤害，火抗性提升 50 点。',
        'four_piece_bonus': '主动催动：展开烈火神罩，周围敌人持续受到烈火灼烧，天命人在此期间气力极速回复！克制黑熊精与灵虚子。',
        'pieces': [
            {'slot': '辟火罩真身', 'name': '金襕辟火罩', 'main_stat_rule': '火免疫，缓慢回气'}
        ],
        'rules_reference': {'set_type': '第一回隐藏法宝', 'unlock': '敲响旧观音禅院三口铜钟进入隐藏地图'}
    },
    {
        'name': '四大法宝 · 绣花针 (Weaver Needle)',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '常驻被动属性：暴击率提升 4%，暴击伤害提升 10%。',
        'four_piece_bonus': '主动催动：绣花针飞射凌空化作流光，自动寻敌连续穿刺目标弱点破除霸体，并破除百眼魔君千目金光结界！',
        'pieces': [
            {'slot': '绣花针神器', 'name': '毗蓝婆绣花针', 'main_stat_rule': '暴击提升，破除金光'}
        ],
        'rules_reference': {'set_type': '第四回隐藏法宝', 'unlock': '击败紫云山晦月魔君后获得'}
    },
    {
        'name': '四大法宝 · 芭蕉扇 (Plantain Fan)',
        'rarity_min': 5,
        'rarity_max': 5,
        'two_piece_bonus': '常驻被动属性：攻击气力消耗减少 10%，气力恢复速度提升 15%。',
        'four_piece_bonus': '主动催动：挥动至宝芭蕉扇扇出贯穿全场的毁灭龙卷风，强行吹散二郎神与各大 Boss 的神力霸体护盾并造成超长大硬直！',
        'pieces': [
            {'slot': '芭蕉扇至宝', 'name': '太阴芭蕉扇', 'main_stat_rule': '龙卷强控，破神力白盾'}
        ],
        'rules_reference': {'set_type': '第五回通关法宝', 'unlock': '火焰山终章击败夜叉王后获得'}
    },
    # 精魄神物
    {
        'name': '精魄 · 幽魂 (大头头目精魄)',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '被动属性：永久提升天命人基础防御力 30 点。',
        'four_piece_bonus': '化身技：消耗元气化身为巨头幽魂，运足巨力向前猛烈头槌轰砸，造成毁灭级破韧伤害与大硬直！',
        'pieces': [
            {'slot': '元气炼化', 'name': '大头精魄元神', 'main_stat_rule': '防御力 +30'},
            {'slot': '头目本源', 'name': '幽魂舍利', 'main_stat_rule': '头槌巨力破韧'}
        ],
        'rules_reference': {'set_type': '防御与破霸体精魄', 'unlock': '黑风山苍狼林击败幽魂'}
    },
    {
        'name': '精魄 · 虎先锋 (猛虎精魄)',
        'rarity_min': 4,
        'rarity_max': 5,
        'two_piece_bonus': '被动属性：识破与斩棍反击伤害额外提升 15%。',
        'four_piece_bonus': '化身技：化身巨虎高高跃起，向前方狠狠扑抓撕咬，附带血影击退效果！',
        'pieces': [
            {'slot': '虎魄精粹', 'name': '虎先锋精魄', 'main_stat_rule': '识破斩棍增伤 15%'}
        ],
        'rules_reference': {'set_type': '切手技强化精魄', 'unlock': '卧虎寺血池击败虎先锋'}
    }
]

MECHANICS = [
    {
        'category': '战斗机制',
        'title': '劈棍切手技【识破】与【斩棍式】判定法则',
        'formula': '轻棍连招中预判敌方命中瞬间输入【轻棍 + 重棍】消耗 1 段气力触发【识破】',
        'parameters': {
            '无敌帧判定': '识破动作期间享有完全无敌判定，免疫包括投技在内的所有敌方判定',
            '斩棍反击': '识破判定成功后立即按重击顺畅衔接【斩棍式】，造成 3.5 倍攻击力的暴击伤害并强行打断 Boss 连招节奏',
            '气力返还': '成功命中后视天赋技能可返还 0.5~1 段气力点数'
        }
    },
    {
        'category': '棍势机制',
        'title': '四段棍势蓄力与三大架势切换体系',
        'formula': '轻击连段/识破/闪避积攒气力段数（1~4点），消耗气力点释放对应阶级重击',
        'parameters': {
            '劈棍 (Smash Stance)': '奔跑中可蓄力，跳起高空擎天重砸，单发爆发伤害最高，核心破盾与处决架势',
            '立棍 (Pillar Stance)': '撑棍登高而立，完全规避地面扩散波与下盘横扫攻击，可在高处打出360度旋转踢击与高空落棍',
            '戳棍 (Thrust Stance)': '拉开身位后撤步蓄力直刺，射程极远，可在绝对安全距离针对高危 Boss 进行无伤磨血'
        }
    },
    {
        'category': '身法机制',
        'title': '极限闪避与残影聚形法则',
        'formula': '在敌人攻击命中前 150ms 内按下闪避键触发【极限闪避】',
        'parameters': {
            '白气残影': '原地留下一具惟妙惟肖的白气假身，短暂吸引敌方后续攻击动作',
            '气力暴涨': '极限闪避成功瞬间一次性回复约 20% 最大气力值并积攒大半段棍势点数',
            '行者套共鸣': '装备行者套时极限闪避可直接刷新神行加速 Buff'
        }
    },
    {
        'category': '神通常用',
        'title': '禁字诀：属性极致转化算法',
        'formula': '攻击力加成 = (当前法力上限 * 0.18) + (当前气力上限 * 0.12)；暴击率加成 = 法力上限 * 0.02%',
        'parameters': {
            '封印代价': '施放后本场战斗完全封禁法术（定身/散气/铜头/毫毛）与所有法宝/变身',
            '持续时间': '持续至本场景战局结束或打坐调息，不可中途主动取消',
            '实战定位': '纯物理近战流派巅峰，适合熟练掌握识破弹反的高玩一棍秒杀 Boss'
        }
    },
    {
        'category': '法术机制',
        'title': '身外身法猴群复制与仇恨仇断法则',
        'formula': '拔毫毛吹出 6~12 位灵猴分身围攻敌人，每位分身继承天命人 45% 基础属性',
        'parameters': {
            '招式复制': '本体施放定身法时全部分身同步施放定身加长控制时间；本体蓄力劈棍时分身同步起跳合击',
            '仇恨牵引': '分身具有极高仇恨优先级，可强行拉扯 Boss 视线令天命人从容喝药调息'
        }
    },
    {
        'category': '机制法则',
        'title': '定身法定息时间递减与破定伤害倍率',
        'formula': '定息基础时间 = 8 秒；受击判定为【破定】时基础增伤 +40%',
        'parameters': {
            'Boss抗性递减': '对同一 Boss 连续使用定身法，第 2 次控制时间衰减至 60%，第 3 次衰减至 30%，随后进入 60 秒免疫冷却',
            '铜头震飞联动': '铜头铁臂成功弹刀后立即跟进定身法，控制时间增加 25%'
        }
    }
]


def crawl_and_sync_wukong(game_id=4):
    print(f'[Wukong] Preparing Black Myth data for Game {game_id} ...')
    c_count = upsert_characters(game_id, BOSSES_AND_TRANSFORMATIONS)
    w_count = upsert_weapons(game_id, STAFFS_AND_WEAPONS)
    a_count = upsert_artifacts(game_id, ARMORS_AND_VESSELS)
    m_count = upsert_mechanics(game_id, MECHANICS)
    print(f'[Wukong] Ingested into Game {game_id}: {c_count} bosses/chars, {w_count} weapons, {a_count} armors/vessels, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_wukong(4)
