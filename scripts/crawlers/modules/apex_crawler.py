"""
Apex Legends (Apex 英雄) Legends, Weapons, Gear & Movement Mechanics Crawler
Ingests competitive tactical legends, firearm armory, Evo shields & hop-ups,
and movement tech rules into Game 16 (Apex 英雄).
"""

from ..common.db import (
    upsert_characters,
    upsert_weapons,
    upsert_artifacts,
    upsert_mechanics
)

LEGENDS = [
    {
        'name': '恶灵 (Wraith)',
        'title': '跨维度跃迁者 · 虚空刺客先锋',
        'rarity': 5,
        'element': '虚空相位 (Void Phase)',
        'weapon_type': '突击步枪 / 冲锋枪',
        'region': '外域辛迪加',
        'arkhe': '维度预警',
        'skills': [
            {'name': '踏入虚空 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '无敌相位穿梭', 'description': '进入虚空相位避开一切伤害判定并提升移动速度，免疫毒气与子弹，脱离险境核心神技'},
            {'name': '维度裂隙 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '虚空传送双向传送门', 'description': '用传送门连接两处地点维持 45 秒，全队可瞬间通过传送门安全转移进圈或切入战场'}
        ],
        'passives': [{'name': '虚空之声', 'description': '当敌方准星瞄准或有陷阱时，虚空低语会提前报警预警'}]
    },
    {
        'name': '寻血猎犬 (Bloodhound)',
        'title': '科技寻血追踪者 · 终极透视扫描',
        'rarity': 5,
        'element': '旧日神灵科技 (Sonar Pulse)',
        'weapon_type': '狙击步枪 / 霰弹枪',
        'region': '塔罗斯',
        'arkhe': '猎人之眼',
        'skills': [
            {'name': '上帝之眼 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '扇形全透视扫描', 'description': '发出一道短程声呐脉冲，透视穿透墙壁建筑物，高亮标记扫描范围内所有敌方身位与陷阱'},
            {'name': '狂野猎犬 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '热成像狂暴移速', 'description': '变身狂暴猎犬，移速大幅提升 30%，视野转为黑白并高亮红色标记敌人，大幅缩短Q技能CD'}
        ],
        'passives': [{'name': '追踪者', 'description': '地面与掩体上会显示敌人留下的脚印、开门、滑铲与流血痕迹时间'}]
    },
    {
        'name': '直布罗陀 (Gibraltar)',
        'title': '装甲要塞堡垒 · 护盾圆顶轰炸救援',
        'rarity': 5,
        'element': '防御要塞 (Defensive Fortress)',
        'weapon_type': '轻机枪 / 霰弹枪',
        'region': '慰藉星',
        'arkhe': '枪盾护体',
        'skills': [
            {'name': '保护圆顶 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '无敌能量穹顶罩', 'description': '投掷圆顶护盾阻挡一切外部子弹与迫击炮轰炸，在罩内救援队友速度大幅提升'},
            {'name': '防御性轰炸 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '密集迫击炮空袭', 'description': '呼叫密集的迫击炮火覆盖目标区域，造成毁灭级伤害并大幅减速震荡区域内敌人'}
        ],
        'passives': [{'name': '枪盾', 'description': '开镜瞄准时自动展开手臂能量枪盾，抵挡正面 50 点子弹伤害；附带坚固大体型减伤 15%'}]
    },
    {
        'name': '探路者 (Pathfinder)',
        'title': '机械先锋前哨 · 飞天抓钩立体机动',
        'rarity': 5,
        'element': '机械动力 (Grapple Physics)',
        'weapon_type': '狙击枪 / 冲锋枪',
        'region': '普萨玛忒',
        'arkhe': '侦察信标',
        'skills': [
            {'name': '抓钩 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '高物理动量摆荡', 'description': '射出抓钩勾住掩体或地面，借由离心力与滑铲打出超远抛物线大跳，位移上限极高'},
            {'name': '滑索枪 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '超长滑索架设', 'description': '射出一道超长高空滑索供全队快速跨越峡谷地形或飞上制高点房顶'}
        ],
        'passives': [{'name': '内线情报', 'description': '扫描调查信标可立即刷新大招并永久缩短大招冷却时间'}]
    },
    {
        'name': '动力小子 (Octane)',
        'title': '高速瘾君子 · 兴奋剂无限加速跳板',
        'rarity': 5,
        'element': '兴奋狂飙 (Stim Rush)',
        'weapon_type': '冲锋枪 / 霰弹枪',
        'region': '普萨玛忒',
        'arkhe': '极速狂奔',
        'skills': [
            {'name': '兴奋剂 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '消耗少量生命加速40%', 'description': '注射刺激剂瞬间解除减速效果，移动速度提升 40%，几乎无CD可频繁使用'},
            {'name': '发射跳板 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '弹射跳板双段二段跳', 'description': '投掷高弹跳板，踩踏可垂直大跳或低伏远跳，并在空中激活二段跳改变空中轨迹'}
        ],
        'passives': [{'name': '快速修复', 'description': '脱离战斗时，每秒自动缓慢恢复自身生命值'}]
    },
    {
        'name': '地平线 (Horizon)',
        'title': '重力操控学者 · 重力电梯与黑洞控场',
        'rarity': 5,
        'element': '奇点重力 (Singularity Gravity)',
        'weapon_type': '突击步枪 / 冲锋枪',
        'region': '奥林匹斯',
        'arkhe': '太空漫游',
        'skills': [
            {'name': '重力电梯 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '垂直气流托举射击', 'description': '投掷纽特发生器制造垂直重力流，将全队垂直升至数十米高空居高临下开镜射击'},
            {'name': '黑洞 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '超强引力坍缩黑洞', 'description': '投掷微型奇点黑洞，将周围所有敌人猛烈吸聚至黑洞中心，配合铝热剂和手雷打出团灭蒸发！'}
        ],
        'passives': [{'name': '太空漫步', 'description': '高空坠落完全没有任何着地僵直缓冲，且在空中拥有极佳转向操控性'}]
    },
    {
        'name': '瓦尔基里 (Valkyrie)',
        'title': '复仇女武神 · 喷气背包高空自由巡航',
        'rarity': 5,
        'element': '泰坦喷气核心 (Titan VTOL)',
        'weapon_type': '射手步枪 / 突击步枪',
        'region': '边境天使',
        'arkhe': '垂直起降',
        'skills': [
            {'name': '飞弹集群 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '12枚微型导弹轰炸', 'description': '射出火箭弹弹幕地毯式轰炸目标矩形区域，造成伤害并致盲眩晕敌人'},
            {'name': '天际之跃 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '全队再部署高空跳伞', 'description': '携全体队友一飞冲天直入云霄，随后展开跳伞喷气装置进行超长距离战略再部署进圈！'}
        ],
        'passives': [{'name': 'VTOL 喷气机', 'description': '按住跳跃键消耗燃料在空中自由悬浮飞行'}]
    },
    {
        'name': '催化剂 (Catalyst)',
        'title': '铁磁流体防护师 · 漆黑面纱阻断视野',
        'rarity': 5,
        'element': '铁磁流体 (Ferrofluid)',
        'weapon_type': '霰弹枪 / 冲锋枪',
        'region': '北方之星',
        'arkhe': '磁流封门',
        'skills': [
            {'name': '穿透尖刺 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '铺设地刺陷阱', 'description': '在地面铺设铁磁流体刺毯，敌人踩中将剧烈减速并持续承受伤害'},
            {'name': '漆黑面纱 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '百米透视阻断暗影墙', 'description': '升起一道巨大的铁磁流体巨墙！完全阻隔敌方视野并免疫一切透视扫描（寻血猎犬/希尔），穿过黑墙的敌人将失明减速！'}
        ],
        'passives': [{'name': '路障强化', 'description': '可用铁磁流体加固或重建被破坏的门，阻挡敌方冲门'}]
    },
    {
        'name': '导线 (Conduit)',
        'title': '泰坦辐射护盾先锋 · 救命临时蓝盾充能',
        'rarity': 5,
        'element': '泰坦反应堆辐射 (Reactor Energy)',
        'weapon_type': '突击步枪 / 冲锋枪',
        'region': '联想群岛',
        'arkhe': '急救护盾',
        'skills': [
            {'name': '辐射传送 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '为队友极速补充临时护甲', 'description': '向队友和自己发射能量流，瞬间生成大量临时临时护盾，挽救残血队友于水火！'},
            {'name': '能量干扰 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '干扰地雷封路屏障', 'description': '投掷一排泰坦干扰泰坦节点，形成大面积禁区，进入的敌人将被电击减速并持续碎盾'}
        ],
        'passives': [{'name': '救星之速', 'description': '当跑向超出战术技能范围的队友时，移动速度大幅提升'}]
    },
    {
        'name': '虚空特工 (Alter)',
        'title': '跨界折跃刺客 · 穿墙隧道与倒地传送',
        'rarity': 5,
        'element': '维度撕裂 (Void Rift)',
        'weapon_type': '冲锋枪 / 霰弹枪',
        'region': '多元宇宙',
        'arkhe': '穿墙裂隙',
        'skills': [
            {'name': '虚空行径 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '在建筑物墙面开洞穿越', 'description': '在坚固墙壁或天花板上开启一条单向虚空隧道，瞬间穿墙偷袭或逃脱'},
            {'name': '虚空枢纽 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '远程信标/倒地全队召回', 'description': '放置折跃枢纽，全队任何成员倒地或按键均可远程被召唤传送回枢纽处安全扶起！'}
        ],
        'passives': [{'name': '死者视界', 'description': '可透视看到死亡死亡死亡死亡箱子并远程拾取一件战利品'}]
    },
    {
        'name': '命脉 (Lifeline)',
        'title': '战地军医救护 · 全自动救援无人机',
        'rarity': 5,
        'element': '战地救护 (Combat Medic)',
        'weapon_type': '冲锋枪 / 突击步枪',
        'region': '普萨玛忒',
        'arkhe': '无人机救援',
        'skills': [
            {'name': 'D.O.C.治疗无人机 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '范围极速回血', 'description': '部署医疗无人机，持续为附近全体友军恢复生命值'},
            {'name': '空投补给舱 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '呼叫高级防护空投箱', 'description': '呼叫包含升级护甲核心、大型电池、医疗箱和高阶配件的精准补给舱'}
        ],
        'passives': [{'name': '战地医疗兵', 'description': '部署无人机自动救援倒地队友，命脉自身仍可自由移动持枪射击防守！'}]
    },
    {
        'name': '罗芭 (Loba)',
        'title': '上流高雅神偷 · 瞬移手环与黑市吸物',
        'rarity': 5,
        'element': '折跃珠宝 (Warp Tech)',
        'weapon_type': '突击步枪 / 冲锋枪',
        'region': '索拉斯',
        'arkhe': '黑市网络',
        'skills': [
            {'name': '盗贼之友 (Q战术技能)', 'type': 'ELEMENTAL_SKILL', 'scaling': '投掷跳跃手环瞬移', 'description': '投掷折跃手环，飞出后立刻瞬移到手环落地点，越过掩体与高台'},
            {'name': '黑市精品店 (Z绝招)', 'type': 'ELEMENTAL_BURST', 'scaling': '展开超大范围自动提货机', 'description': '展开便携黑市杖，将周围数百米内的所有战利品物资（高阶甲/配件/弹药）吸入，无限取弹药并任选2件高级装备！'}
        ],
        'passives': [{'name': '识宝之眼', 'description': '可直接透视穿墙看到附近的紫色与金色稀有装备'}]
    }
]

FIREARMS = [
    {'name': 'R-301 卡宾枪', 'type': '轻型突击步枪', 'rarity': 5, 'base_atk': '单发伤害 14，射速 810 RPM', 'sub_stat': '极佳后坐力控制与中距离稳定性', 'refine': '万能中远距离激光枪，连发手感极其柔顺。'},
    {'name': 'VK-47 平行步枪 (Flatline)', 'type': '重型突击步枪', 'rarity': 5, 'base_atk': '单发伤害 19，射速 600 RPM', 'sub_stat': '单发高伤害与优异腰射散布', 'refine': '贴脸腰射与中距离扫射的神级重型步枪，压枪熟练后DPS极高。'},
    {'name': 'R-99 冲锋枪', 'type': '轻型冲锋枪', 'rarity': 5, 'base_atk': '单发伤害 12，射速 1080 RPM', 'sub_stat': '超高射速秒人融化', 'refine': '一梭子近身贴脸瞬间将敌人护甲秒碎，近战爆发代表。'},
    {'name': 'CAR 冲锋枪', 'type': '双口径冲锋枪', 'rarity': 5, 'base_atk': '单发伤害 13，射速 930 RPM', 'sub_stat': '兼容重型与轻型弹药及弹匣', 'refine': '通用性极强，弹药永不缺货，贴脸扫射爆发恐怖。'},
    {'name': '电能冲锋枪 (Volt)', 'type': '能量冲锋枪', 'rarity': 5, 'base_atk': '单发伤害 15，射速 720 RPM', 'sub_stat': '极小弹道下坠与高稳定性', 'refine': '子弹初速极快，中近距离极其致命的能量SMG。'},
    {'name': '和平捍卫者 (Peacekeeper)', 'type': '霰弹枪', 'rarity': 5, 'base_atk': '单发全中 99 伤害 (星形弹丸)', 'sub_stat': '精准收束聚能', 'refine': '开镜瞄准蓄力收束弹丸，中距离打出接近百血的一枪碎甲！'},
    {'name': '敖犬散弹枪 (Mastiff)', 'type': '霰弹枪', 'rarity': 5, 'base_atk': '横向一条线弹丸分布，伤害 88', 'sub_stat': '掩体闪击峰值伤害', 'refine': '经典的打一枪缩回掩体的peek神器，房区近战统治者。'},
    {'name': '辅助手枪 (Wingman)', 'type': '狙击/重型手枪', 'rarity': 5, 'base_atk': '单发爆头 75 伤害，躯干 45', 'sub_stat': '穿颅器高额爆头倍率', 'refine': '高手信仰之枪，无视移速惩罚，三枪爆头瞬秒紫甲。'},
    {'name': '克雷贝尔 (Kraber .50-Cal)', 'type': '空投毁灭狙击步枪', 'rarity': 5, 'base_atk': '单发爆头 280+ (一枪绝命)', 'sub_stat': '穿甲无视护甲秒杀', 'refine': '全游戏最强秒杀武器，命中头部直接击倒任何品质护甲的敌人！'},
    {'name': '复仇女神 (Nemesis Burst AR)', 'type': '能量突击步枪', 'rarity': 5, 'base_atk': '四连发点射，射速充能升温', 'sub_stat': '满充能转全自动极速点射', 'refine': '随着射击充能条上升，后坐力归零且射速飞升，中远距离统治级火力！'},
    {'name': '长弓 DMR', 'type': '狙击步枪', 'rarity': 4, 'base_atk': '单发 55，射速稳定', 'sub_stat': '连续精准连发压制', 'refine': '容错率高的半自动狙击步枪，适合压制敌方换甲。'},
    {'name': '哨兵狙击枪 (Sentinel)', 'type': '栓动狙击步枪', 'rarity': 4, 'base_atk': '单发 70，充能后 88', 'sub_stat': '消耗小型电池强化充能', 'refine': '注入护甲电池激活高能充能状态，击碎任何护甲并伴随清脆雷鸣！'}
]

EQUIPMENT = [
    {'name': '进化护甲 (Evo Shield)', 'two_piece': '核心护甲', 'four_piece': '通过造成伤害累计进化：白(150) -> 蓝(200) -> 紫(225) -> 红(250红甲)', 'pieces': ['护甲核心', '进化增幅']},
    {'name': '金色头盔 (Gold Helmet)', 'two_piece': '减少 20% 爆头伤害', 'four_piece': '使战术技能 (Q) 与绝招 (Z) 的冷却时间大幅缩短 25%！', 'pieces': ['金色头部防具']},
    {'name': '金色击倒护盾 (Gold Knockdown Shield)', 'two_piece': '展开抵挡 750 点正面伤害', 'four_piece': '救援队友时，被救起的队友直接恢复 50 点生命值与 50 点护甲！', 'pieces': ['金色救援核心']},
    {'name': '涡轮增压器 (Turbocharger)', 'two_piece': '适配哈沃克步枪 / 专注轻机枪', 'four_piece': '彻底消除武器射击前摇蓄力升温时间，开火瞬间立刻达到最高射速！', 'pieces': ['专属插件']},
    {'name': '穿颅器 (Skullpiercer Rifles)', 'two_piece': '适配小帮手 / 30-30 / 长弓', 'four_piece': '大幅提升爆头伤害系数 35%，一发爆头破万物！', 'pieces': ['爆头特化插件']}
]

MECHANICS = [
    {
        'category': '身法进阶',
        'title': '蹬墙跳与超级滑铲物理动量机制',
        'formula': '滑铲跳跃 + 贴近墙面松开W并按跳跃键触发【蹬墙跳 (Wall Bounce)】',
        'parameters': {
            '蹬墙跳': '利用攀爬重置物理动量，瞬间折射飞向反方向，规避敌方准星追踪',
            '超级滑铲 (Superglide)': '在攀爬到墙顶边缘的极限 1 帧内同时按跳跃与下蹲，获得超过 2 倍基础移速的超音速弹射！',
            'Tap-strafe (滚轮转向)': '利用滚轮前进指令绑定，在空中完成 180 度无减速锐角变向'
        }
    },
    {
        'category': '护甲核心',
        'title': '护甲核心拾取与超量护盾机制',
        'formula': '拾取高阶护甲核心获得超量护甲，超量护甲在 30 秒内缓慢衰退至常态',
        'parameters': {
            '换甲机制': '击败敌人后立即打开其死亡箱拾取新鲜护甲核心，0秒瞬间回满全部护甲（Armor Swap）！'
        }
    },
    {
        'category': '毒圈规则',
        'title': '风暴环缩圈与热能护盾防御',
        'formula': '第一圈(2%/s) -> 第二圈(4%/s) -> 第三圈(8%/s) -> 第四/五圈(12%/s~25%/s秒杀)',
        'parameters': {
            '热能护盾': '投掷后生成半球形保护罩，在毒圈内短暂免疫风暴伤害并加速治疗使用'
        }
    }
]


def crawl_and_sync_apex(game_id=16):
    print(f'[Apex Legends] Preparing Legends, Firearms & Gear for Game {game_id} ...')

    characters = []
    for l in LEGENDS:
        characters.append({
            'name': l['name'],
            'title': l['title'],
            'rarity': l['rarity'],
            'element': l['element'],
            'weapon_type': l['weapon_type'],
            'region': l['region'],
            'arkhe': l['arkhe'],
            'avatar_url': f'/games/apex/{l["name"].split()[0]}.png',
            'splash_url': '',
            'base_stats': [
                {'level': '白甲状态', 'hp': 100, 'shield': 50, 'speed': '7.4 m/s'},
                {'level': '红甲满装', 'hp': 100, 'shield': 125, 'speed': '7.4 m/s'}
            ],
            'talents': l['skills'],
            'passives': l['passives'],
            'constellations': [],
            'special_mechanics': {'circuit': l['arkhe']},
            'recommendations': {'best_weapon': l['weapon_type'].split('/')[0].strip(), 'best_gear': '进化护甲 / 金色头盔'},
            'version': 'S23'
        })

    weapons = []
    for f in FIREARMS:
        weapons.append({
            'name': f['name'],
            'type': f['type'],
            'rarity': f['rarity'],
            'icon_url': f'/games/apex_weapons/{f["name"].split()[0]}.png',
            'base_atk_curve': {'damage_profile': f['base_atk']},
            'sub_stat': {'handling': f['sub_stat']},
            'refinements': {'performance': f['refine']},
            'ascension_materials': {'type': '战利品配件 / 制造器复制'},
            'version': 'S23'
        })

    artifacts = []
    for e in EQUIPMENT:
        artifacts.append({
            'name': e['name'],
            'rarity_min': 4,
            'rarity_max': 5,
            'icon_url': f'/games/apex_gear/{e["name"].split()[0]}.png',
            'two_piece_bonus': e['two_piece'],
            'four_piece_bonus': e['four_piece'],
            'pieces': [{'slot': p, 'effect': '生存辅助'} for p in e['pieces']],
            'rules_reference': {'description': '高级防具可通过制造站或击倒敌人升级'},
            'version': 'S23'
        })

    c_count = upsert_characters(game_id, characters)
    w_count = upsert_weapons(game_id, weapons)
    a_count = upsert_artifacts(game_id, artifacts)
    m_count = upsert_mechanics(game_id, MECHANICS)
    print(f'[Apex Legends] Ingested into Game {game_id}: {c_count} legends, {w_count} weapons, {a_count} gear sets, {m_count} mechanics.')


if __name__ == '__main__':
    crawl_and_sync_apex(16)
