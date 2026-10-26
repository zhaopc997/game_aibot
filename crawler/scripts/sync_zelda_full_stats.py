#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
塞尔达传说：王国之泪 (The Legend of Zelda: Tears of the Kingdom) 全量数值体系落库与同步脚本
game_id = 3

包含:
1. 林克 6 大核心能力形态与贤者传承体系 (左纳乌机械师、人马屠夫、潜行刺客、元素法皇、贤者军团、极速滑翔特工)
   - 4~40 颗心之容器 (红心血量)、1~3 圈精力耐力轮、1~16 节左纳乌能源电池
   - 劳鲁右臂四大核心神技 (究极手、余料建造、通天术、倒转乾坤) 与蓝图、四大神殿贤者盟约
2. 14 件海拉鲁传奇神兵与余料融合底材 (大师之剑觉醒、兽神弓5连发、七宝匕首翻倍、近卫双手剑濒死绝境、卓拉湿润枪)
3. 6 大防具套装体系 (鬼神套装、左纳乌能源套、滑翔无跌落伤套、潜行套、织梦勇者套、异次元恶灵骨增伤套)
4. 5 大底层物理引擎与战斗机制 (余料额外耐久与八爪怪翻新、林克时间与盾反、3倍碎冰元素乘区、骑乘人马0耐久消耗、左纳乌电量衰减)
"""

import os
import sys
import json
import hashlib
import psycopg2
from psycopg2.extras import Json

PG_CONFIG = {
    'host': os.getenv('PG_HOST', '127.0.0.1'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

OUT_DIR = os.path.join(os.path.dirname(__file__), "../out")
os.makedirs(OUT_DIR, exist_ok=True)

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def get_zelda_characters():
    """构建塞尔达传说：王国之泪 林克 6 大能力形态与贤者传承体系"""
    return [
        {
            "name": "林克·人马屠夫近战大师 (Lynel Slayer / Flurry Rush)",
            "title": "海拉鲁第一剑士与时缓突刺之神",
            "rarity": 5,
            "element": "时空突击",
            "weapon_type": "单手剑/双手剑/兽神弓",
            "avatar_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Link_Artwork.png/250px-TotK_Link_Artwork.png",
            "splash_url": "https://images.nintendolife.com/7b5871f3bcf07/zelda-tears-of-the-kingdom.large.jpg",
            "base_stats": [
                {"level": "初始·初始空岛", "hp": 12, "hearts": "3 颗心", "stamina": "1 圈 (5段)", "battery": "1 节 (3格)", "atk": 10, "def": 3, "flurry_rush_hits": 7},
                {"level": "前期·四方启程", "hp": 28, "hearts": "7 颗心", "stamina": "1.4 圈 (7段)", "battery": "2 节 (6格)", "atk": 25, "def": 12, "flurry_rush_hits": 7},
                {"level": "中期·神殿二解", "hp": 60, "hearts": "15 颗心", "stamina": "2 圈 (10段)", "battery": "4 节 (12格)", "atk": 55, "def": 28, "flurry_rush_hits": 7},
                {"level": "中后期·地下拓荒", "hp": 100, "hearts": "25 颗心", "stamina": "2.6 圈 (13段)", "battery": "8 节 (24格)", "atk": 95, "def": 48, "flurry_rush_hits": 7},
                {"level": "后期·贤者齐聚", "hp": 140, "hearts": "35 颗心", "stamina": "3 圈满圈 (15段)", "battery": "12 节 (36格)", "atk": 135, "def": 68, "flurry_rush_hits": 7},
                {"level": "毕业·大师封神", "hp": 160, "hearts": "40 颗满心", "stamina": "3 圈金色额外充盈", "battery": "16 节满电 (48格蓝色)", "atk": 180, "def": 84, "flurry_rush_hits": 7}
            ],
            "special_ascension_stat": {
                "stat_name": "剑圣近战核心机制",
                "values": {
                    "林克时间": "受击前 0.2 秒完美闪避进入时缓，连刺 7 刀享受 100% 暴击",
                    "人马骑乘特权": "跳上人马背部攻击【绝对不消耗任何武器耐久度】",
                    "濒死绝境双倍": "近卫双手剑破损红光闪烁时，攻击力直接翻倍至 200+ 攻！"
                }
            },
            "ascension_materials": [
                {"tier": "神庙祝福之光", "items": "累计通关 152 座神庙 | 兑换 38 次心之容器/精力槽"},
                {"tier": "地下左纳乌矿石", "items": "击败地底人马获得大核心 | 制炼 16 节全满蓝色电池"},
                {"tier": "大妖精之泉强化", "items": "唤醒米·兹罗等四大妖精 | 鬼神防具强化至 ★★★★ 满星"}
            ],
            "talents": [
                {"name": "绝对身法·完美闪避与林克时间 (Flurry Rush)", "type": "NORMAL_ATTACK", "description": "看准敌方挥砍或突刺瞬间，向后空翻或左右侧跳；时间流速瞬间慢放 20 倍，林克极速突进施展 7 连斩突刺大爆发！", "scaling": "时缓持续 3.5 秒，7 段全额暴击"},
                {"name": "绝对防御·完美盾反 (Perfect Guard)", "type": "ELEMENTAL_SKILL", "description": "在攻击接触盾牌瞬间按 A 挥击盾牌，完全化解物理冲击并弹开守护者/人马激光，造成对手大幅失衡硬直！", "scaling": "盾牌 0 耐久消耗，必定破除霸体"},
                {"name": "人马杀手·五连发爆头连珠箭", "type": "ELEMENTAL_BURST", "description": "手持兽神弓跃起进入空中时慢时间，连续射出 5 连发附带吉波得之骨或炸弹花的穿云箭，正面直击弱点必定击晕！", "scaling": "单箭 32 攻 × 5 支 = 160 基础面伤 + 附加余料伤害"},
                {"name": "绝境压榨·濒死骑乘斩", "type": "EXPLORATION_TALENT", "description": "将近卫双手剑砍至只剩 1 点耐久濒死红光闪烁（触发绝境攻击翻倍），骑上被击晕的人马背部连砍 6 刀，刀刀致命且耐久绝对不掉！", "scaling": "单次骑乘爆发突破 1200+ 物理真伤"}
            ],
            "passives": [
                {"name": "鬼神神力", "desc": "佩戴鬼神套装时攻击力达到最高第 3 档（增伤 1.5 倍），蓄力旋风斩精力消耗降低 50%。"},
                {"name": "破损觉醒", "desc": "近卫武器处于即将损坏状态时，伤害结算翻倍。"},
                {"name": "弱点重击", "desc": "弓箭命中怪物面部核心弱点时，必定发出暴击音效并产生双倍伤害。"}
            ],
            "constellations": [
                {"c": 1, "name": "风之贤者丘栗爆头誓约", "desc": "风之神殿解放，丘栗在大世界提供顺风滑翔推进，战斗中自动高精度弓箭爆头敌人。"},
                {"c": 2, "name": "火之贤者阿沅碎石猛冲", "desc": "火之神殿解放，阿沅化身烈焰炮弹粉碎矿石岩石，撞飞重甲敌人。"},
                {"c": 3, "name": "水之贤者希多无敌水盾", "desc": "水之神殿解放，希多赋予绝对抵挡一次攻击的水之护盾，并使卓拉长枪攻击翻倍！"},
                {"c": 4, "name": "雷之贤者露珠天劫雷击", "desc": "雷之神殿解放，展开全场金色雷鸣领域，射箭引爆九天神雷造成毁灭雷暴！"},
                {"c": 5, "name": "魂之贤者米涅鲁魔像高达", "desc": "魂之神殿解放，骑乘古老魔像，背装火箭风扇，双臂装配大炮与激光头！"},
                {"c": 6, "name": "海拉鲁救世英杰觉醒", "desc": "集齐 4 个贤者的遗志强化全部盟约，贤者普攻伤害提升 1.3 倍，化身不可战胜之王！"}
            ],
            "special_mechanics": {
                "kill_lynel": "空中开伞拉弓进入林克时间 -> 射脸爆头让人马跪地 -> 掏出濒死近卫双手剑按 A 骑上马背砍 6 刀 (0耐久消耗) -> 人马甩飞瞬间在空中再次掏弓回头射 3 发后脑勺 -> 落地瞬间人马倒地！"
            },
            "recommendations": {
                "weapons": {"bis": "兽神弓 (5连发) + 濒死近卫双手剑 (融合白银刃角 208攻)", "alternative_5s": "七宝匕首 (融合刃角 138攻) / 卓拉长枪 (湿润 154攻)", "bow": "兽神弓 / 大鹫弓"},
                "artifacts": {"bis_set": "鬼神套装 (4星强化，攻击力提升 1.5 倍)", "alt_set": "蛮族套装 / 异次元恶灵套 (骨武器 1.8 倍)"},
                "main_stats": {"priority": "精力耐力 (优先拉满3圈) > 心之容器 (拉到30+) > 电池容量 (16节满电)"}
            },
            "version": "1.2.1"
        },
        {
            "name": "林克·左纳乌空天机械师 (Zonai Mechanical Engineer)",
            "title": "蓝图高达创造者与轰炸机建造大师",
            "rarity": 5,
            "element": "左纳乌工程",
            "weapon_type": "左纳乌单手剑/大炮杖",
            "avatar_url": "https://zeldawiki.wiki/images/thumb/5/5a/TotK_Zonai_Survey_Team_Artwork.png/250px-TotK_Zonai_Survey_Team_Artwork.png",
            "splash_url": "https://image.api.playstation.com/vulcan/ap/rnd/202110/2000/phvVT0qZfcRms5qDAk0SI3CM.png",
            "base_stats": [
                {"level": "前期·基础零件", "hp": 30, "hearts": "8 颗心", "stamina": "1.6 圈", "battery": "3 节 (9格)", "atk": 20, "def": 15, "zonai_efficiency": "+20%"},
                {"level": "中期·蓝图获得", "hp": 65, "hearts": "16 颗心", "stamina": "2.2 圈", "battery": "6 节 (18格)", "atk": 45, "def": 30, "zonai_efficiency": "+40%"},
                {"level": "后期·轰炸编队", "hp": 110, "hearts": "28 颗心", "stamina": "2.8 圈", "battery": "12 节 (36格)", "atk": 85, "def": 55, "zonai_efficiency": "+75%"},
                {"level": "毕业·无敌高达", "hp": 160, "hearts": "40 颗心", "stamina": "3 圈满圈", "battery": "16 节满电 (48格超导蓝电)", "atk": 150, "def": 84, "zonai_efficiency": "+100% (耗电减半)"}
            ],
            "special_ascension_stat": {
                "stat_name": "左纳乌工程核心特权",
                "values": {
                    "自动建造": "蓝图消耗矿石或胶水在 0.5 秒内凭空生成 21 零件复合高达",
                    "节能大师": "穿戴左纳乌能源套使全场装置耗电速率降低 50%",
                    "火力饱和": "追踪轮 + 头部发射器 + 8 联装光线头 + 4 联装大炮实现全自动寻敌狂轰滥炸"
                }
            },
            "ascension_materials": [
                {"tier": "中央大废矿", "items": "击败可盖大人获得蓝图技能 | 特殊设计图纸"},
                {"tier": "扭蛋机胶囊", "items": "操纵杆 / 大炮 / 光线头 / 追踪轮 / 火箭 / 风扇机"},
                {"tier": "左纳乌能源套装", "items": "左纳乌空岛宝箱获取 | 大妖精强化"}
            ],
            "talents": [
                {"name": "究极工程·蓝图一键成型 (Autobuild)", "type": "ELEMENTAL_BURST", "description": "调出收藏夹中的经典蓝图（如双风扇飞行摩托、8 炮巡逻高达），消耗左纳乌能源矿石或现存胶囊，瞬间凝聚完成部署！", "scaling": "0.5 秒瞬间落成，随时随地展开战斗阵地"},
                {"name": "超神操控·究极手 (Ultrahand)", "type": "NORMAL_ATTACK", "description": "隔空抓取重达万斤的物体并自由旋转、拼接结合，制造无懈可击的物理陷阱或高空桥梁。", "scaling": "最大连接 21 个物理实体，结合强度极高"},
                {"name": "时空回溯·倒转乾坤 (Recall)", "type": "ELEMENTAL_SKILL", "description": "锁定任意移动过的物体使其沿时间轨迹倒流运动，将 Boss 投掷的巨石原路砸回，或乘坐坠落的遗迹石升入万丈高空！", "scaling": "倒流时间最长可达 20 秒，破除一切投射攻击"},
                {"name": "地底飞天·通天术 (Ascend)", "type": "EXPLORATION_TALENT", "description": "向上发射绿色光线穿透头顶岩壁，直接由地底、洞穴垂直跃升至地面甚至山巅！", "scaling": "穿透无限厚度垂直实体，逃课神技"}
            ],
            "passives": [
                {"name": "能源超导", "desc": "左纳乌能源套装使电池充能速度提升 100%，耗电速度减半。"},
                {"name": "高热隔离", "desc": "在火山等极热或极寒环境下，左纳乌装置不会因环境失控引爆。"},
                {"name": "零件强化", "desc": "武器融合左纳乌核心零件时，基础耐久度额外提升 25 点。"}
            ],
            "constellations": [
                {"c": 1, "name": "双风扇飞行摩托诞生", "desc": "1 操纵杆 + 2 风扇机仅耗 9 矿石，以 0.05 极低耗电畅游海拉鲁天空与地底。"},
                {"c": 2, "name": "自走陆战机甲 (Homunculus Tank)", "desc": "追踪轮搭载头部发射器与冰霜喷头，全自动冻结并撞飞群怪。"},
                {"c": 3, "name": "天基激光轨道炮", "desc": "浮空石搭载 12 联装光线头悬浮 Boss 头顶，30 秒融化三头巨龙古栗欧克。"},
                {"c": 4, "name": "16 节全满蓝色超导电池", "desc": "地底挖矿大成，48 格电池在节能套装下可持续运转 15 分钟以上！"},
                {"c": 5, "name": "格鲁德战斗高达", "desc": "蓝图收藏终极机甲，林克站桩喝茶，机甲单挑幻影加侬。"},
                {"c": 6, "name": "左纳乌科技创世神", "desc": "超越海拉鲁物理法则，用科技征服一切神魔！"}
            ],
            "special_mechanics": {
                "bomber_tactic": "遭遇高难 Boss -> 掏出蓝图 0.5 秒召唤天基光线炮台或战车 -> 爬上操纵杆启动 -> 激光大炮自动追踪轰炸，林克只需站在后方欣赏烟花！"
            },
            "recommendations": {
                "weapons": {"bis": "强力左纳乌长枪 (融合光线头/大炮) + 队长魔像核心角", "alternative_5s": "魔法大杖 (三重大炮融合)"},
                "artifacts": {"bis_set": "左纳乌能源套装 (4星强化，电池消耗速度减半 + 充能翻倍)"},
                "main_stats": {"priority": "电池格数 (优先拉满 16 节) > 精力耐力 > 心之容器"}
            },
            "version": "1.2.1"
        },
        {
            "name": "林克·潜行刺客夜袭流 (Stealth Assassin / Night Blade)",
            "title": "希卡影武者与8倍背刺死神",
            "rarity": 5,
            "element": "潜行暗杀",
            "weapon_type": "单手剑/戒心小刀",
            "avatar_url": "https://zeldawiki.wiki/images/thumb/a/ad/TotK_Stealth_Set.png/200px-TotK_Stealth_Set.png",
            "splash_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Link_Artwork.png/250px-TotK_Link_Artwork.png",
            "base_stats": [
                {"level": "前期·希卡潜行", "hp": 30, "hearts": "8 颗心", "stamina": "1.8 圈", "battery": "3 节", "atk": 25, "def": 10, "sneak_level": "Lv.3 (静音满级)"},
                {"level": "中期·烟雾暗杀", "hp": 65, "hearts": "16 颗心", "stamina": "2.4 圈", "battery": "6 节", "atk": 60, "def": 25, "sneak_level": "Lv.3"},
                {"level": "后期·冰冻死神", "hp": 110, "hearts": "28 颗心", "stamina": "3 圈满圈", "battery": "10 节", "atk": 110, "def": 45, "sneak_level": "Lv.3"},
                {"level": "毕业·十六倍杀", "hp": 160, "hearts": "40 颗心", "stamina": "3 圈满圈", "battery": "16 节", "atk": 170, "def": 60, "sneak_level": "Lv.3 (夜间移动速度提升)"}
            ],
            "special_ascension_stat": {
                "stat_name": "潜行暗杀核心机制",
                "values": {
                    "背刺偷袭倍率": "接近未察觉敌人背后按 Y 触发背刺，直接造成 8 倍物理暴击伤害！",
                    "戒心小刀特权": "戒心小刀自带偷袭特权，背刺倍率达到极其恐怖的 16 倍！",
                    "烟雾蘑菇脱战": "扔出烟雾蘑菇原地生成浓雾，周围所有敌人立刻陷入致盲失忆，可当面绕背连续背刺！"
                }
            },
            "ascension_materials": [
                {"tier": "卡卡利科村防具店", "items": "潜行面罩 / 潜行紧身服 / 潜行紧身裤 | 解决梅朵奶奶支线降价"},
                {"tier": "地底深渊采集", "items": "烟雾蘑菇 × 99 | 混乱花 × 50 | 炸弹花 × 99"},
                {"tier": "希卡遗迹调查", "items": "戒心小刀 (未腐蚀版本) | 斩风大剑"}
            ],
            "talents": [
                {"name": "致命一击·背刺偷袭 (Sneakstrike)", "type": "NORMAL_ATTACK", "description": "悄无声息潜行至敌人背后，敌人头上出现【偷袭】提示瞬间按 Y 键发动致死打击，直接造成基础面板 8 倍伤害！", "scaling": "普通武器 8 倍，戒心小刀 16 倍极效伤害"},
                {"name": "暗影障目·烟雾蘑菇战法", "type": "ELEMENTAL_SKILL", "description": "将烟雾蘑菇扔在脚下或绑在箭头发射，瞬间爆发大范围白色迷雾，敌人陷入问号硬直，当面直接转到背后连环背刺！", "scaling": "烟雾持续 10 秒，群怪瞬间失去视野"},
                {"name": "借刀杀人·混乱花狂化", "type": "ELEMENTAL_BURST", "description": "向怪物据点发射混乱花，使白银莫力布林与首领陷入自相残杀狂暴，在远处坐山观虎斗。", "scaling": "持续 30 秒，怪物优先攻击同伴"},
                {"name": "破冰核爆·碎冰背刺", "type": "EXPLORATION_TALENT", "description": "用冰冻果实或冷气蜥蜴角先行冻结敌人（触发 3 倍伤害易伤），再实施背刺，乘算打出高达 24 倍天文数字伤害！", "scaling": "3倍碎冰 × 8倍背刺 = 24 倍物理终极湮灭！"}
            ],
            "passives": [
                {"name": "无声行者", "desc": "穿戴潜行套装时奔跑不会发出任何声音，可直接疾跑接近昆虫蜥蜴与怪物而不被惊扰。"},
                {"name": "夜行猎手", "desc": "夜晚（21:00 ~ 05:00）移动速度提升 30%。"},
                {"name": "骨武器精通", "desc": "佩戴异次元恶灵套装时，吉波得之骨与骨类武器攻击力额外提升 1.8 倍。"}
            ],
            "constellations": [
                {"c": 1, "name": "卡卡利科潜行服入手", "desc": "全套潜行服入手，大世界抓独角仙、精力蛙如探囊取物。"},
                {"c": 2, "name": "烟雾蘑菇链式背刺", "desc": "掌握背刺后立刻转身再丢烟雾蘑菇，单人无伤屠杀整个白银怪物营地。"},
                {"c": 3, "name": "戒心小刀 16 倍杀神", "desc": "获得戒心小刀并融合白银人马刃角，单发背刺突破 2000+ 伤害！"},
                {"c": 4, "name": "异次元恶灵套解放", "desc": "迷宫三神庙通关获得异次元恶灵套装，骨攻击 1.8 倍 + 潜行满级。"},
                {"c": 5, "name": "冰冻 24 倍核爆", "desc": "冰冻 + 背刺瞬间秒杀一切非 Boss 精英怪。"},
                {"c": 6, "name": "海拉鲁暗影幽灵", "desc": "整个海拉鲁大陆没有一个怪物能在发现林克的前提下活着！"}
            ],
            "special_mechanics": {
                "loop": "朝怪群射一发烟雾蘑菇 -> 快步绕到白银敌人背后按 Y 背刺 8 倍伤害 -> 敌人倒地瞬间再次扔烟雾蘑菇 -> 起身再背刺循环直至清场，全程 0 掉血 0 惊动！"
            },
            "recommendations": {
                "weapons": {"bis": "戒心小刀 (融合白银刃角，16倍背刺神器)", "alternative_5s": "残破腐蚀近卫剑 / 斩风大剑"},
                "artifacts": {"bis_set": "潜行套装 (静音奔跑 + 夜间提速)", "alt_set": "异次元恶灵套装 (骨攻击提升 1.8 倍)"},
                "main_stats": {"priority": "精力耐力 > 潜行等级 > 心之容器"}
            },
            "version": "1.2.1"
        },
        {
            "name": "林克·元素反应与环境法皇 (Elemental Sorcerer)",
            "title": "红蓝宝石法杖与大范围气候爆轰师",
            "rarity": 5,
            "element": "元素魔法",
            "weapon_type": "魔法杖/复合长枪",
            "avatar_url": "https://zeldawiki.wiki/images/thumb/6/69/TotK_Magic_Rod_Model.png/200px-TotK_Magic_Rod_Model.png",
            "splash_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Link_Artwork.png/250px-TotK_Link_Artwork.png",
            "base_stats": [
                {"level": "前期·属性初识", "hp": 30, "hearts": "8 颗心", "stamina": "1.6 圈", "battery": "3 节", "atk": 22, "def": 12, "elemental_range": "标准"},
                {"level": "中期·宝石法杖", "hp": 65, "hearts": "16 颗心", "stamina": "2.2 圈", "battery": "6 节", "atk": 50, "def": 28, "elemental_range": "扩散"},
                {"level": "后期·三灾合一", "hp": 110, "hearts": "28 颗心", "stamina": "2.8 圈", "battery": "10 节", "atk": 90, "def": 52, "elemental_range": "超大范围"},
                {"level": "毕业·天候之神", "hp": 160, "hearts": "40 颗心", "stamina": "3 圈满圈", "battery": "16 节", "atk": 160, "def": 84, "elemental_range": "全图气候压制"}
            ],
            "special_ascension_stat": {
                "stat_name": "元素反应机制",
                "values": {
                    "蓝宝石绝对冻结": "挥舞蓝宝石法杖发射三颗冰霜法球，接触目标必定冻结，受物理重击触发 3 倍碎冰伤害",
                    "红宝石火海陨石": "发射巨大烈焰火球引爆草地生成上升气流，直接秒杀冰属性全部敌人",
                    "黄宝石雷霆导电": "水面或雨天释放电击产生超大范围导电电场，麻痹全场并缴械敌人武器"
                }
            },
            "ascension_materials": [
                {"tier": "矿石采集", "items": "红宝石 × 30 | 蓝宝石 × 30 | 黄宝石 × 30 | 钻石 × 10"},
                {"tier": "魔法手杖", "items": "魔法大杖 (Magic Rod) | 魔法长杖 | 魔法剑"},
                {"tier": "环境防具", "items": "耐火套装 | 利特羽绒保暖套 | 橡胶耐电套"}
            ],
            "talents": [
                {"name": "极寒冰霜·蓝宝石三连法球", "type": "ELEMENTAL_SKILL", "description": "法杖挥出三枚极寒冰球，超大范围冰冻全场非 Boss 单位，使其受到的下一次物理攻击直接翻 3 倍！", "scaling": "绝对冰冻 5 秒，附带 3 倍碎冰乘区"},
                {"name": "烈焰轰顶·红宝石大火球", "type": "ELEMENTAL_BURST", "description": "发射巨大烈焰飞弹引发剧烈爆炸与火海，点燃周围一切可燃物并产生强劲上升气流，林克可立刻开伞飞天！", "scaling": "超大爆炸范围，秒杀一切冰雪蜥蜴与冰雪莫力布林"},
                {"name": "连锁雷暴·黄宝石电磁球", "type": "NORMAL_ATTACK", "description": "发射金色电球，遇到雨天或水域瞬间扩散数十米强电场，强制令所有手持金属兵刃的敌人惨叫缴械！", "scaling": "强制掉落武器，麻痹 3 秒"},
                {"name": "陨石天降·大炮长枪连发", "type": "EXPLORATION_TALENT", "description": "长枪融合左纳乌大炮，按住投掷键以准星精确瞄准超远距离敌人进行迫击炮轰击！", "scaling": "迫击炮精度射击，粉碎矿石与敌人"}
            ],
            "passives": [
                {"name": "气候大师", "desc": "穿戴对应环境套装时，免疫极端严寒、极热、燃烧与雷击判定。"},
                {"name": "上升气流", "desc": "任何火焰引燃草地后必定生成上升气流，按 X 即可展开滑翔伞进入林克时间。"},
                {"name": "元素秒杀法则", "desc": "火属性攻击命中冰系怪物必定 1 击秒杀；冰属性命中火系怪物必定 1 击秒杀！"}
            ],
            "constellations": [
                {"c": 1, "name": "魔法大杖融合宝石", "desc": "在海拉鲁平原神庙获得魔法大杖，告别单发果实，进入连发法球时代。"},
                {"c": 2, "name": "火冰相克极致秒杀", "desc": "雪山用火秒怪，火山用冰秒怪，无需任何多余操作。"},
                {"c": 3, "name": "雷暴雨天神罚", "desc": "雨天手持橡胶套，往怪堆丢铁剑引九天落雷轰炸。"},
                {"c": 4, "name": "三属性巨龙角收集", "desc": "收集奥尔龙、聂尔龙、费罗龙的犄角，余料融合获得永不熄灭的属性光芒。"},
                {"c": 5, "name": "全天候无敌抗性", "desc": "全环境防具 4 星满级，无视一切海拉鲁严酷气候。"},
                {"c": 6, "name": "海拉鲁元素自然之神", "desc": "呼风唤雨引动雷火冰霜，掌控自然之威！"}
            ],
            "special_mechanics": {
                "freeze_shatter": "蓝宝石法球冰冻敌人 -> 切换高攻双手剑或锤子蓄力重砸 -> 触发【3倍碎冰伤害乘区】爆出极高伤害 -> 接红宝石火球解除冰冻并引燃 -> 循环秒杀！"
            },
            "recommendations": {
                "weapons": {"bis": "魔法大杖 (融合蓝宝石/红宝石/黄宝石)", "alternative_5s": "卓拉长枪 (融合三龙犄角)"},
                "artifacts": {"bis_set": "耐火套 / 利特羽绒套 / 橡胶防电套 (应对各极端环境)"},
                "main_stats": {"priority": "宝石储备数量 > 精力耐力 > 电池容量"}
            },
            "version": "1.2.1"
        },
        {
            "name": "林克·极速滑翔特工流 (Skyfall Speedrunner)",
            "title": "空岛俯冲大师与跌落免伤特技神探",
            "rarity": 4,
            "element": "高空气流",
            "weapon_type": "滑翔翼/利特长弓",
            "avatar_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Glide_Set.png/200px-TotK_Glide_Set.png",
            "splash_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Link_Artwork.png/250px-TotK_Link_Artwork.png",
            "base_stats": [
                {"level": "Lv.1 探索者", "hp": 20, "hearts": "5 颗心", "stamina": "1.4 圈", "battery": "2 节", "atk": 15, "def": 6, "dive_mobility": "高"},
                {"level": "Lv.2 鸟望塔飞天", "hp": 50, "hearts": "13 颗心", "stamina": "2.0 圈", "battery": "5 节", "atk": 40, "def": 20, "dive_mobility": "极高"},
                {"level": "Lv.3 跌落免伤觉醒", "hp": 90, "hearts": "23 颗心", "stamina": "2.6 圈", "battery": "8 节", "atk": 75, "def": 40, "dive_mobility": "【绝对免疫跌落伤害】"},
                {"level": "Lv.4 天地贯穿神行", "hp": 160, "hearts": "40 颗心", "stamina": "3 圈满圈", "battery": "16 节", "atk": 140, "def": 60, "dive_mobility": "超音速俯冲"}
            ],
            "special_ascension_stat": {
                "stat_name": "滑翔特工核心特权",
                "values": {
                    "跌落完全免伤": "滑翔套 2 星强化后激活套装效果：从 3000 米天空直坠地面【掉血为 0 点】！",
                    "俯冲机动性": "空中俯冲按住 R 键极速转向穿环，水平位移速度提升 2.5 倍",
                    "空降突袭": "从天而降直接重砸 Boss 头顶，无缝衔接下落重击"
                }
            },
            "ascension_materials": [
                {"tier": "三座试炼空岛", "items": "刚之试炼 / 勇之试炼 / 柔之试炼 俯冲穿环获取滑翔全套"},
                {"tier": "大妖精强化", "items": "蝙蝠眼球 / 卡卡利科特产 | 升级至 ★★ 解锁跌落免伤"}
            ],
            "talents": [
                {"name": "超音速俯冲·天火陨石坠", "type": "EXPLORATION_TALENT", "description": "从万米高空收伞垂直俯冲，在即将撞击地面瞬间不按伞直接脸着地，激起巨额烟尘但人物毫发无损！", "scaling": "高度无上限，跌落伤害恒为 0"},
                {"name": "空战制霸·空中林克时间", "type": "ELEMENTAL_SKILL", "description": "在俯冲滑翔过程中随时按 ZR 拔弓，直接进入长达数秒的空中时缓，将空中的飞龙古栗欧克三颗头颅逐一射爆！", "scaling": "空中随时进入林克时间，视角无死角"}
            ],
            "passives": [
                {"name": "跌落免伤 (Impact Proof)", "desc": "无论以何种角度从何种高度坠落碰撞任何地面，受到的伤害绝对为 0！"},
                {"name": "顺风滑翔", "desc": "风之贤者丘栗在大世界滑翔中随时提供喷气加速推进。"}
            ],
            "constellations": [
                {"c": 1, "name": "滑翔套装齐聚", "desc": "完成三座勇气空岛俯冲挑战，集齐滑翔面罩、衣服与裤子。"},
                {"c": 2, "name": "二星觉醒·跌落免伤", "desc": "大妖精强化至二星，彻底告别开伞失败摔死的惨剧。"},
                {"c": 6, "name": "海拉鲁自由之翼", "desc": "鸟望塔一飞冲天直入地底深渊，穿云破雾随心所欲！"}
            ],
            "special_mechanics": {
                "glide_drop": "鸟望塔弹射升空 -> 穿戴滑翔套按住 R 极速俯冲飞往目的地 -> 不开伞直接头铁砸向目标地面 -> 0 掉血帅气落地！"
            },
            "recommendations": {
                "weapons": {"bis": "大鹫弓 / 兽神弓", "alternative_5s": "利特轻量长弓"},
                "artifacts": {"bis_set": "滑翔套装 (★★ 强化解锁跌落完全免伤)"},
                "main_stats": {"priority": "精力耐力 (飞得更远) > 心之容器"}
            },
            "version": "1.2.1"
        },
        {
            "name": "林克·贤者军团化身之主 (Sages Alliance Avatar)",
            "title": "五大贤者灵魂誓约与军团指挥官",
            "rarity": 5,
            "element": "神圣誓约",
            "weapon_type": "大师之剑/贤者魔像",
            "avatar_url": "https://zeldawiki.wiki/images/thumb/8/87/TotK_Master_Sword_Artwork.png/250px-TotK_Master_Sword_Artwork.png",
            "splash_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Link_Artwork.png/250px-TotK_Link_Artwork.png",
            "base_stats": [
                {"level": "神殿一解", "hp": 40, "hearts": "10 颗心", "stamina": "1.6 圈", "battery": "3 节", "atk": 30, "def": 18, "allies": "丘栗"},
                {"level": "神殿二解", "hp": 75, "hearts": "19 颗心", "stamina": "2.2 圈", "battery": "6 节", "atk": 65, "def": 35, "allies": "丘栗 + 阿沅"},
                {"level": "神殿三解", "hp": 115, "hearts": "29 颗心", "stamina": "2.8 圈", "battery": "10 节", "atk": 100, "def": 55, "allies": "丘栗 + 阿沅 + 希多"},
                {"level": "五贤者大成", "hp": 160, "hearts": "40 颗心", "stamina": "3 圈满圈", "battery": "16 节", "atk": 180, "def": 84, "allies": "丘栗 + 阿沅 + 希多 + 露珠 + 米涅鲁 (全员遗志强化)"}
            ],
            "special_ascension_stat": {
                "stat_name": "贤者军团战术特权",
                "values": {
                    "五位一体围殴": "五位贤者幽灵分身全程跟随自动协同作战，吸引首领仇恨与持续输出",
                    "遗志强化": "投入 20 个贤者的遗志，使 5 大贤者普攻伤害永久提高 1.3 倍！",
                    "驱魔圣剑觉醒": "大师之剑在瘴气地底与加侬 Boss 战常驻觉醒 60 攻且耐久翻倍"
                }
            },
            "ascension_materials": [
                {"tier": "四神殿解放", "items": "风/火/水/雷四秘石传承誓约"},
                {"tier": "魂之神殿魔像", "items": "搬运四个部件组装米涅鲁机甲魔像"},
                {"tier": "拔出大师之剑", "items": "登顶白龙头部拔出驱魔圣剑 (需两圈完整精力)"}
            ],
            "talents": [
                {"name": "驱魔圣剑·真大师之剑 (Awakened Master Sword)", "type": "NORMAL_ATTACK", "description": "由白龙千年泪水洗礼的神圣之剑。面对瘴气敌人、地底生物及最终魔王加侬时，剑刃泛起耀眼圣光，基础攻击力从 30 跃升至 60 攻，且耐久度大幅提升！", "scaling": "觉醒 60 攻，满血按 R 可发射神圣穿透剑气"},
                {"name": "贤者协同·全军出击", "type": "ELEMENTAL_BURST", "description": "吹响口哨呼唤贤者，丘栗爆头强行打断、阿沅滚球破防、希多水盾抵挡致命伤、露珠降天雷轰顶、米涅鲁重拳压制！", "scaling": "全员协同，林克甚至无需亲自出手"},
                {"name": "剑气纵横·满心剑气波", "type": "ELEMENTAL_SKILL", "description": "生命值全满状态下挥动大师之剑，向正前方发射半月形神圣剑气，远距离切割敌人并打出僵直。", "scaling": "佩戴勇者套装剑气伤害翻倍"}
            ],
            "passives": [
                {"name": "海拉鲁救世主", "desc": "与贤者共同作战时，自身受到的伤害降低 15%。"},
                {"name": "神圣光环", "desc": "大师之剑对瘴气覆盖的怪物造成 1.5 倍神圣增伤。"},
                {"name": "白龙恩泽", "desc": "靠近大师之剑觉醒状态时，瘴气侵蚀爱心恢复速度加快 50%。"}
            ],
            "constellations": [
                {"c": 1, "name": "两圈精力拔出圣剑", "desc": "在天空中追逐飞翔的白龙，消耗两圈耐力拔出大师之剑。"},
                {"c": 2, "name": "贤者遗志搜集·丘栗强化", "desc": "收集 4 个贤者的遗志，丘栗爆头输出达到神级水准。"},
                {"c": 3, "name": "贤者遗志搜集·阿沅强化", "desc": "阿沅冲撞伤害暴涨，撞击白银精英怪产生巨大僵直。"},
                {"c": 4, "name": "贤者遗志搜集·希多与露珠", "desc": "水盾更持久，天雷伤害达上千级大范围电击。"},
                {"c": 5, "name": "贤者遗志搜集·米涅鲁机甲", "desc": "魂之贤者魔像装配大炮与冰霜喷头，横行霸道。"},
                {"c": 6, "name": "六位一体·光复海拉鲁", "desc": "五位贤者誓约加上林克，彻底驱散魔王加侬的万年瘴气！"}
            ],
            "special_mechanics": {
                "boss_fight": "面对加侬与幻影军团 -> 展开希多水盾抵挡首发招式 -> 露珠天雷轰碎杂兵盾牌 -> 阿沅冲撞撞翻 Boss -> 丘栗精准爆头打出失衡 -> 大师之剑觉醒 60 攻连续斩击！"
            },
            "recommendations": {
                "weapons": {"bis": "觉醒大师之剑 (融合白银刃角 115攻) + 兽神弓", "alternative_5s": "七宝匕首 / 碎岩巨剑"},
                "artifacts": {"bis_set": "织梦勇者套装 / 旷野之勇者套装 (大师剑剑气威力提升 100%)"},
                "main_stats": {"priority": "贤者遗志 (全满 20 个) > 2圈拔剑精力 > 40 颗红心"}
            },
            "version": "1.2.1"
        }
    ]

def get_zelda_weapons():
    """构建塞尔达传说：王国之泪 14 件神兵与余料融合底材"""
    return [
        {
            "name": "大师之剑 (Master Sword)",
            "type": "单手剑",
            "rarity": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/8/87/TotK_Master_Sword_Artwork.png/200px-TotK_Master_Sword_Artwork.png",
            "base_atk_curve": {
                "常规状态": "物理攻击 30 (基础耐久 40，可自由余料建造)",
                "瘴气/加侬觉醒": "物理攻击 60 (剑刃泛出神圣绿光，耐久度与伤害翻倍，满血发射剑气)",
                "融合白银刃角": "综合面板高达 85 攻 (觉醒时高达 115 攻！)"
            },
            "sub_stat": {
                "stat_name": "圣剑特权与修复机制",
                "ratings": "耐久耗尽不破碎，进入 10 分钟自我修复 CD 后满血复活！",
                "requirements": "需 2 圈完整精力耐力方可从白龙头上拔出"
            },
            "refinements": {
                "skill_name": "神圣驱魔与余料共鸣",
                "fp_cost": "0 消耗 (满血按 R 发射剑气)",
                "effect": "对瘴气魔物（幻影加侬、瘴气之手、魔王加侬）具有绝对神圣克制；融合任何余料建造底材均可获得攻击加成与 25 点额外耐久度。"
            },
            "ascension_materials": {
                "type": "白龙头部拔剑",
                "catalyst_list": "净化德库树长老消除地底幻影加侬 -> 标记白龙轨迹 -> 消耗 2 圈精力拔剑"
            },
            "version": "1.2.1"
        },
        {
            "name": "兽神弓·五连发 (Savage Lynel Bow)",
            "type": "弓",
            "rarity": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/4/41/TotK_Savage_Lynel_Bow_Model.png/200px-TotK_Savage_Lynel_Bow_Model.png",
            "base_atk_curve": {
                "未改装三连": "32 × 3 = 96 基础面伤",
                "岩石八爪怪改装五连发": "32 × 5 = 160 毁灭面伤 (耐久度 45，单次射击只消耗 1 支箭！)"
            },
            "sub_stat": {
                "stat_name": "弓箭散射特性",
                "ratings": "5 箭齐射，每一箭均独立继承绑定的余料效果！",
                "requirements": "击败白银莱尼尔 (白银人马) 掉落"
            },
            "refinements": {
                "skill_name": "连珠箭雨爆破",
                "fp_cost": "消耗 1 支木箭",
                "effect": "绑定炸弹花时单次射击发射 5 颗炸弹，瞬间造成数千范围毁灭爆破；绑定吉波得之骨时 5 箭单轮输出突破 360+ 点超高真伤！"
            },
            "ascension_materials": {
                "type": "白银人马掉落",
                "catalyst_list": "地下黑白人马角斗场击破五连人马获取"
            },
            "version": "1.2.1"
        },
        {
            "name": "七宝匕首 (Scimitar of the Seven)",
            "type": "单手剑",
            "rarity": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/7/77/TotK_Scimitar_of_the_Seven_Model.png/200px-TotK_Scimitar_of_the_Seven_Model.png",
            "base_atk_curve": {
                "单体裸刀": "基础物理攻击 28 (耐久度 60)",
                "融合白银莱尼尔刃角": "28 + (55 × 2) = 138 点超高攻击力！(全海拉鲁最高攻击单手剑之一)"
            },
            "sub_stat": {
                "stat_name": "格鲁德兵刃独门词缀",
                "ratings": "【强力余料建造效果翻倍】：融合的任何素材攻击力直接 × 2 计算！",
                "requirements": "完成格鲁德小镇蕾珠支线打造获得"
            },
            "refinements": {
                "skill_name": "七宝传承神威",
                "fp_cost": "常驻生效",
                "effect": "耐久度高达 60，攻击速度极快且手感极佳；由于余料攻击翻倍特性，融合莫鲁德拉吉的下颚可同时享受骨武器 1.8 倍与七宝翻倍双重叠加！"
            },
            "ascension_materials": {
                "type": "格鲁德珠宝匠打造",
                "catalyst_list": "格鲁德匕首 + 格鲁德盾 + 钻石 × 4 + 打火石 × 10"
            },
            "version": "1.2.1"
        },
        {
            "name": "近卫双手剑·绝境濒死 (Royal Guard's Claymore)",
            "type": "双手剑",
            "rarity": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/5/52/TotK_Royal_Guard%27s_Claymore_Model.png/200px-TotK_Royal_Guard%27s_Claymore_Model.png",
            "base_atk_curve": {
                "未损坏状态": "基础攻击 39 (融合白银刃角 = 94 攻)",
                "绝境濒死破损红光闪烁": "攻击力翻倍结算！最终面板突破 208 点！(人马背部专武)"
            },
            "sub_stat": {
                "stat_name": "独门词缀·绝境倍率",
                "ratings": "【濒死绝境翻倍】：当耐久度剩余最后 3 点红光闪烁时，攻击力直接翻倍！",
                "requirements": "海拉鲁城堡主殿或牢房拾取未腐蚀版本"
            },
            "refinements": {
                "skill_name": "人马杀手骑乘专用",
                "fp_cost": "在人马背上挥刀攻击消耗 0 耐久！",
                "effect": "平时绝不出鞘；待人马被弓箭爆头跪地后，跳上马背挥刀 6 连斩，利用 208 极高面板单轮打掉 1200+ 血量，且耐久度永远卡在最后 1 点永不损坏！"
            },
            "ascension_materials": {
                "type": "海拉鲁城堡搜寻",
                "catalyst_list": "城堡主殿二楼塞尔达房间 / 地下王室密室"
            },
            "version": "1.2.1"
        },
        {
            "name": "卓拉长枪 (Zora Spear)",
            "type": "长枪",
            "rarity": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/b/b8/TotK_Zora_Spear_Model.png/200px-TotK_Zora_Spear_Model.png",
            "base_atk_curve": {
                "干燥状态": "基础攻击 11 (融合白银刃角 = 66 攻)",
                "沾水湿润状态": "伤害直接翻倍！达到极其狂暴的 154 点长枪连续突刺！"
            },
            "sub_stat": {
                "stat_name": "独门词缀·水之祝福",
                "ratings": "【湿润攻击翻倍】：沾水、雨天、游泳后或开启希多水盾时，伤害直接 × 2！",
                "requirements": "卓拉领地神庙与水井中拾取"
            },
            "refinements": {
                "skill_name": "希多水盾常驻联动",
                "fp_cost": "触碰水之贤者希多启动水盾",
                "effect": "希多水盾不仅能完全免疫一次攻击，更能为林克提供长达 60 秒的常驻【湿润状态】，使卓拉长枪持续处于 154 攻的极速突刺爆发中！"
            },
            "ascension_materials": {
                "type": "卓拉领地打造与拾取",
                "catalyst_list": "卓拉长枪 + 钻石 × 3 + 燧石"
            },
            "version": "1.2.1"
        },
        {
            "name": "碎岩巨剑 (Boulder Breaker)",
            "type": "双手剑",
            "rarity": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/6/6a/TotK_Boulder_Breaker_Model.png/200px-TotK_Boulder_Breaker_Model.png",
            "base_atk_curve": {
                "基础面板": "基础物理 38 (耐久度 60，融合耐受力极强)",
                "融合高级岩石/角": "面板可达 80~110 攻，碎石粉碎效率海拉鲁第一！"
            },
            "sub_stat": {
                "stat_name": "独门词缀·粉碎一击",
                "ratings": "【粉碎特性】：对矿石、岩石盔甲、岩石巨人造成的破坏力提升 300%！",
                "requirements": "鼓隆城铁匠铺打造"
            },
            "refinements": {
                "skill_name": "破甲震地击",
                "fp_cost": "常驻生效",
                "effect": "一刀直接敲碎岩石巨人的坚硬岩石弱点，对身穿岩石铠甲的白银莱尼尔能一击直接敲碎整套外壳破防！"
            },
            "ascension_materials": {
                "type": "鼓隆城铁匠打造",
                "catalyst_list": "劈石棒 + 钻石 × 3 + 燧石 × 5"
            },
            "version": "1.2.1"
        },
        {
            "name": "王者之剑 (Royal Broadsword)",
            "type": "单手剑",
            "rarity": 4,
            "icon_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Royal_Broadsword_Model.png/200px-TotK_Royal_Broadsword_Model.png",
            "base_atk_curve": {
                "平时普攻": "基础攻击 24 (融合刃角 = 79 攻)",
                "林克时间突击": "伤害直接翻倍！达到 158 点突进暴击斩！"
            },
            "sub_stat": {
                "stat_name": "独门词缀·突击时空",
                "ratings": "【时缓突击翻倍】：在林克时间 (Flurry Rush) 突进时，攻击力直接翻倍！",
                "requirements": "海拉鲁城堡与各地骑士遗迹宝箱"
            },
            "refinements": {
                "skill_name": "完美闪避增幅",
                "fp_cost": "完美闪避触发",
                "effect": "专为喜欢后空翻和侧跳的近战达人设计，在 7 刀连斩中刀刀享受 158 极高伤害！"
            },
            "ascension_materials": {
                "type": "全图骑士宝箱",
                "catalyst_list": "海拉鲁城堡密道或地底幽灵手持未腐蚀版本"
            },
            "version": "1.2.1"
        },
        {
            "name": "戒心小刀 (Eightfold Blade)",
            "type": "单手剑",
            "rarity": 4,
            "icon_url": "https://zeldawiki.wiki/images/thumb/5/5e/TotK_Eightfold_Blade_Model.png/200px-TotK_Eightfold_Blade_Model.png",
            "base_atk_curve": {
                "正面普攻": "基础攻击 15 (手感极佳)",
                "背刺偷袭 (Sneakstrike)": "直接触发极其恐怖的 16 倍背刺伤害！(融合白银刃角单刀破 2000+！)"
            },
            "sub_stat": {
                "stat_name": "独门词缀·无影忍杀",
                "ratings": "【刺客专属 16 倍背刺】：偷袭背刺倍率由标准的 8 倍翻倍至 16 倍！",
                "requirements": "卡卡利科村或依盖队基地击败刺客获取"
            },
            "refinements": {
                "skill_name": "依盖队暗杀术",
                "fp_cost": "背刺触发",
                "effect": "配合烟雾蘑菇当面绕背，单刀一击直接抹杀白银莫力布林与白银蜥蜴战士，伤害碾压一切神兵！"
            },
            "ascension_materials": {
                "type": "希卡遗迹与依盖队掉落",
                "catalyst_list": "依盖队干部击败掉落"
            },
            "version": "1.2.1"
        }
    ]

def get_zelda_artifacts():
    """构建塞尔达传说：王国之泪 6 大核心防具套装体系"""
    return [
        {
            "name": "鬼神套装 (Fierce Deity Armor Set)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/b/be/TotK_Fierce_Deity_Set.png/200px-TotK_Fierce_Deity_Set.png",
            "two_piece_bonus": "【攻击力提升 Lv.2】：全身物理攻击力提升 1.3 倍。",
            "four_piece_bonus": "【鬼神终极降临】：攻击力提升至最高的 Lv.3 (伤害乘区直接 × 1.5 倍)！★★ 强化解锁套装特效：蓄力攻击精力消耗降低 50%！",
            "pieces": [
                {"slot": "头部", "name": "鬼神帽子 (Fierce Deity Mask)", "main_stat_rule": "防御力 3~20 | 攻击力提升 Lv.1"},
                {"slot": "胸甲", "name": "鬼神服 (Fierce Deity Armor)", "main_stat_rule": "防御力 3~20 | 攻击力提升 Lv.1"},
                {"slot": "腿甲", "name": "鬼神靴 (Fierce Deity Boots)", "main_stat_rule": "防御力 3~20 | 攻击力提升 Lv.1"},
                {"slot": "武器联动", "name": "鬼神大剑 (Fierce Deity Sword)", "main_stat_rule": "基础物攻 38 | 耐久度 60"}
            ],
            "rules_reference": {
                "type": "全海拉鲁顶级输出战力防具",
                "recommended_for": "对抗白银莱尼尔、格利德克三头龙、魔王加侬主战首选"
            },
            "version": "1.2.1"
        },
        {
            "name": "左纳乌能源套装 (Zonaite Armor Set)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://zeldawiki.wiki/images/thumb/5/5a/TotK_Zonai_Survey_Team_Artwork.png/200px-TotK_Zonai_Survey_Team_Artwork.png",
            "two_piece_bonus": "【左纳乌能耗降低 Lv.2】：装置耗电速度延缓 35%。",
            "four_piece_bonus": "【无限能源超导】：左纳乌装置能耗直接减半 (-50%)！★★ 强化解锁套装特效：电池充能恢复速度暴增 100%！配合蓝电可驱动机甲飞行轰炸十几分钟不熄火！",
            "pieces": [
                {"slot": "头部", "name": "左纳乌头盔 (Zonaite Helm)", "main_stat_rule": "防御力 4~28 | 能源效率提升"},
                {"slot": "胸甲", "name": "左纳乌胸甲 (Zonaite Waistguard)", "main_stat_rule": "防御力 4~28 | 能源效率提升"},
                {"slot": "腿甲", "name": "左纳乌胫甲 (Zonaite Shin Guards)", "main_stat_rule": "防御力 4~28 | 能源效率提升"}
            ],
            "rules_reference": {
                "type": "空天机械师与开高达必备神器",
                "recommended_for": "飞行摩托跨海探索、全自动激光轰炸机甲、天基轨道炮"
            },
            "version": "1.2.1"
        },
        {
            "name": "滑翔套装 (Glide Armor Set)",
            "rarity_min": 4,
            "rarity_max": 4,
            "icon_url": "https://zeldawiki.wiki/images/thumb/7/7b/TotK_Glide_Set.png/200px-TotK_Glide_Set.png",
            "two_piece_bonus": "【俯冲机动性大幅提升】：空中俯冲转向更灵敏，滑翔水平推进距离提升 40%。",
            "four_piece_bonus": "【神技·跌落完全免伤 (Impact Proof)】：★★ 强化解锁绝对免伤！从万米高空直接砸入地面【掉血为 0 点】，完全不需要开伞！",
            "pieces": [
                {"slot": "头部", "name": "滑翔面罩 (Glide Mask)", "main_stat_rule": "防御力 3~20 | 空中机动强化"},
                {"slot": "胸甲", "name": "滑翔紧身服 (Glide Shirt)", "main_stat_rule": "防御力 3~20 | 空中机动强化"},
                {"slot": "腿甲", "name": "滑翔紧身裤 (Glide Tights)", "main_stat_rule": "防御力 3~20 | 空中机动强化"}
            ],
            "rules_reference": {
                "type": "探索大世界与深渊神级体验",
                "recommended_for": "鸟望塔弹射、空岛跳伞穿环、地底深渊直坠不减速"
            },
            "version": "1.2.1"
        },
        {
            "name": "潜行套装 (Stealth Armor Set)",
            "rarity_min": 4,
            "rarity_max": 4,
            "icon_url": "https://zeldawiki.wiki/images/thumb/a/ad/TotK_Stealth_Set.png/200px-TotK_Stealth_Set.png",
            "two_piece_bonus": "【静音行动 Lv.2】：移动噪音大幅削减，靠近昆虫不易惊扰。",
            "four_piece_bonus": "【满级隐身杀戮】：静音行动拉满 Lv.3，疾跑完全无声！★★ 强化解锁：夜间移动速度提高 30%！背后偷袭享受 8 倍极限暴击！",
            "pieces": [
                {"slot": "头部", "name": "潜行面罩 (Stealth Mask)", "main_stat_rule": "防御力 2~16 | 隐蔽度提升"},
                {"slot": "胸甲", "name": "潜行紧身服 (Stealth Chest Guard)", "main_stat_rule": "防御力 2~16 | 隐蔽度提升"},
                {"slot": "腿甲", "name": "潜行紧身裤 (Stealth Tights)", "main_stat_rule": "防御力 2~16 | 隐蔽度提升"}
            ],
            "rules_reference": {
                "type": "抓虫抓青蛙与刺客暗杀必备",
                "recommended_for": "烟雾蘑菇背刺流、开荒捉捕稀有素材"
            },
            "version": "1.2.1"
        },
        {
            "name": "织梦勇者套装 (Hero of Awakening Set)",
            "rarity_min": 4,
            "rarity_max": 4,
            "icon_url": "https://zeldawiki.wiki/images/thumb/1/1a/TotK_Mask_of_Awakening_Model.png/200px-TotK_Mask_of_Awakening_Model.png",
            "two_piece_bonus": "【攻击力提升 Lv.1】：基础物理输出提升 20%。",
            "four_piece_bonus": "【大师之剑剑气强化】：★★ 强化解锁：大师之剑满心发射的剑气伤害直接翻倍 (+100%)！变身可爱大头娃娃勇者！",
            "pieces": [
                {"slot": "头部", "name": "织梦之勇者面具 (Mask of Awakening)", "main_stat_rule": "防御力 3~20 | 攻击力提升"},
                {"slot": "胸甲", "name": "织梦之勇者服 (Tunic of Awakening)", "main_stat_rule": "防御力 3~20 | 攻击力提升"},
                {"slot": "腿甲", "name": "织梦之勇者裤 (Trousers of Awakening)", "main_stat_rule": "防御力 3~20 | 攻击力提升"}
            ],
            "rules_reference": {
                "type": "复古经典勇者情怀与剑气流",
                "recommended_for": "大师之剑远程剑气狙击"
            },
            "version": "1.2.1"
        },
        {
            "name": "异次元恶灵套装 (Evil Spirit Armor Set)",
            "rarity_min": 4,
            "rarity_max": 4,
            "icon_url": "https://zeldawiki.wiki/images/thumb/1/1e/TotK_Evil_Spirit_Set.png/200px-TotK_Evil_Spirit_Set.png",
            "two_piece_bonus": "【静音行动 Lv.2】：潜行移动声响极小。",
            "four_piece_bonus": "【神威·骨武器攻击力大幅提升】：全套激活骨武器攻击力直接提升至 1.8 倍！配合莫鲁德拉吉的下颚 (骨素材) 融合武器，打出海拉鲁单击最高峰值！且骷髅怪物不会主动攻击自身！",
            "pieces": [
                {"slot": "头部", "name": "异次元恶灵头盔 (Evil Spirit Mask)", "main_stat_rule": "防御力 4 (不可升级) | 潜行提升"},
                {"slot": "胸甲", "name": "异次元恶灵铠甲 (Evil Spirit Armor)", "main_stat_rule": "防御力 4 (不可升级) | 潜行提升"},
                {"slot": "腿甲", "name": "异次元恶灵护腿 (Evil Spirit Greaves)", "main_stat_rule": "防御力 4 (不可升级) | 潜行提升"}
            ],
            "rules_reference": {
                "type": "极限伤害竞速邪道骨武器神装",
                "recommended_for": "配合莫鲁德拉吉下颚骨 + 料理 3 攻，打出一击秒杀人马万伤核爆"
            },
            "version": "1.2.1"
        }
    ]

def get_zelda_mechanics():
    """构建塞尔达传说：王国之泪 5 大底层物理与战斗机制"""
    return [
        {
            "category": "余料建造与耐久度翻新机制 (Fuse & Durability Mechanics)",
            "title": "武器耐久额外加成、一始村无损分解与岩石八爪怪翻新",
            "formula": "全新武器首次融合余料：基础耐久度额外获得 +25 点隐藏耐久 (大多数武器上限为原有耐久+25)。",
            "parameters": {
                "octorok_repair": {
                    "rule": "死亡之山附近的【岩石八爪怪】会吸入面前物品；将快要损坏的武器丢在它面前被它吸入，八爪怪咀嚼后吐出：耐久度完全恢复为 100%，且随机洗出【攻击力+10】或【五连发】金色极品词缀！",
                    "reset_frequency": "每只八爪怪在每次红月刷新后可翻新 1 次武器。"
                },
                "tarrey_town_breakapart": {
                    "rule": "一始村普珀达处支付 20 卢比，可将武器与余料无损拆解为两件完好物品，珍贵素材 (如白银刃角、钻石) 可无限循环利用！"
                }
            }
        },
        {
            "category": "林克时间与完美盾反判定 (Flurry Rush & Perfect Guard)",
            "title": "0.2 秒时间窗口、时缓 20 倍与 7 连暴击判定",
            "formula": "触发条件：敌方武器判定框触及林克受击框前 0.15~0.25 秒内，纵斩输入侧跳翻滚、横扫输入后空翻；判定成功进入 3.5 秒时缓并连击 7 刀。",
            "parameters": {
                "perfect_guard": "受击瞬间按 A 挥盾，完全反弹除巨型核爆外的任何物理与法术攻击，且盾牌绝对不消耗耐久度！",
                "flurry_rush_bonus": "配合【王者之剑】，在林克时间内突击造成的伤害直接翻倍 (× 200%)。"
            }
        },
        {
            "category": "元素相克与碎冰乘区模型 (Elemental Synergy & Shatter Damage)",
            "title": "冰冻 3 倍物理碎冰、火冰属性对立一击必杀与导电电场",
            "formula": "碎冰伤害 = 物理攻击力 × 3.0 (首击解除冰冻同时造成 3 倍巨额爆发)；火遇冰系怪 / 冰遇火系怪必定 1 击秒杀！",
            "parameters": {
                "freeze_multiplier": "任何被冰冻的目标承受的第一下物理攻击直接享受 300% 伤害乘区！配合背刺更可达到 24 倍天文伤害！",
                "electric_disarm": "雷电属性击中手持金属武器的敌人，强制使其麻痹 3 秒并必定掉落手持兵刃！"
            }
        },
        {
            "category": "骑乘人马机制与耐久完全豁免 (Lynel Mounting Mechanics)",
            "title": "人马跪地判定、骑马攻击 0 耐久消耗与空中回头射箭",
            "formula": "弓箭命中人马面部弱点造成硬直跪地 -> 靠近按 A 跃上马背 -> 连续挥刀攻击 6 次；骑乘状态下任何武器攻击【完全不消耗任何耐久度】！",
            "parameters": {
                "zero_durability": "由于耐久绝对不减，可使用仅剩最后 1 点耐久的【濒死红光近卫双手剑】(触发绝境 2 倍伤害，面板达 208 攻) 进行无损斩杀！",
                "dismount_arrow": "被人马甩飞至空中的瞬间按 ZR 拔弓，可在空中进入林克时间回头向人马后脑勺再补 3~5 箭！"
            }
        },
        {
            "category": "左纳乌能耗速率与超导电池模型 (Zonai Energy Drain Rate)",
            "title": "装置功耗叠加公式、大核心超导与节能套装耗电模型",
            "formula": "每秒总耗电量 = ∑(单个激活装置功耗) × (1 - 左纳乌套装节能%)；全套左纳乌套能耗降低 50%。",
            "parameters": {
                "device_power_consumption": {
                    "操纵杆": "0.01 格/秒 (极低，几乎不耗电)",
                    "风扇机": "0.05 格/秒",
                    "大炮": "每次开火消耗 0.4 格",
                    "光线头": "0.15 格/秒持续高能消耗"
                },
                "large_zonai_charge": "食用【大颗左纳乌能源】，在后续一段时间内所有装置运转完全不消耗电量 (无限蓝超导模式)！"
            }
        }
    ]

def sync_all_to_postgres():
    """主同步执行函数：连接 Postgres 并幂等落库"""
    print("=== 开始同步《塞尔达传说：王国之泪》(game_id = 3) 全量数值体系到 PostgreSQL ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    characters = get_zelda_characters()
    weapons = get_zelda_weapons()
    artifacts = get_zelda_artifacts()
    mechanics = get_zelda_mechanics()

    # 1. 写入角色能力形态 (game_character)
    print(f"\n[1/4] 写入王国之泪林克能力形态 ({len(characters)} 个)...")
    for c in characters:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version
            ) VALUES (
                3, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                title = EXCLUDED.title,
                rarity = EXCLUDED.rarity,
                element = EXCLUDED.element,
                weapon_type = EXCLUDED.weapon_type,
                avatar_url = EXCLUDED.avatar_url,
                splash_url = EXCLUDED.splash_url,
                base_stats = EXCLUDED.base_stats,
                special_ascension_stat = EXCLUDED.special_ascension_stat,
                ascension_materials = EXCLUDED.ascension_materials,
                talents = EXCLUDED.talents,
                passives = EXCLUDED.passives,
                constellations = EXCLUDED.constellations,
                special_mechanics = EXCLUDED.special_mechanics,
                recommendations = EXCLUDED.recommendations,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))
    print(f"  ✓ 成功落库 {len(characters)} 个林克能力形态！")

    # 2. 写入神兵与余料底材 (game_weapon)
    print(f"\n[2/4] 写入王国之泪神兵与余料建造底材 ({len(weapons)} 件)...")
    for w in weapons:
        # 标准化为 List[Dict] 以兼容后端 JPA List<Map<String, Object>> 实体反序列化
        raw_curve = w['base_atk_curve']
        if isinstance(raw_curve, dict):
            normalized_curve = [{"level": k, "atk": v} for k, v in raw_curve.items()]
        elif isinstance(raw_curve, list):
            normalized_curve = raw_curve
        else:
            normalized_curve = []

        raw_ref = w['refinements']
        if isinstance(raw_ref, dict):
            rank = raw_ref.get("skill_name") or "神兵特性"
            fp = raw_ref.get("fp_cost")
            desc = f"【条件】{fp}。{raw_ref.get('effect', '')}" if fp else raw_ref.get('effect', '')
            normalized_ref = [{"rank": rank, "desc": desc}]
        elif isinstance(raw_ref, list):
            normalized_ref = raw_ref
        else:
            normalized_ref = []

        raw_mat = w['ascension_materials']
        if isinstance(raw_mat, dict):
            normalized_mat = [{"tier": raw_mat.get("type", "获取方式与刷新机制"), "items": raw_mat.get("catalyst_list", "")}]
        elif isinstance(raw_mat, list):
            normalized_mat = raw_mat
        else:
            normalized_mat = []

        w_payload = {
            **w,
            'base_atk_curve': normalized_curve,
            'refinements': normalized_ref,
            'ascension_materials': normalized_mat
        }
        h = calc_hash(w_payload)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                3, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                type = EXCLUDED.type,
                rarity = EXCLUDED.rarity,
                icon_url = EXCLUDED.icon_url,
                base_atk_curve = EXCLUDED.base_atk_curve,
                sub_stat = EXCLUDED.sub_stat,
                refinements = EXCLUDED.refinements,
                ascension_materials = EXCLUDED.ascension_materials,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(normalized_curve),
            Json(w['sub_stat']), Json(normalized_ref), Json(normalized_mat), h, w['version']
        ))
    print(f"  ✓ 成功落库 {len(weapons)} 件神兵与余料底材！")

    # 3. 写入防具套装 (game_artifact_set)
    print(f"\n[3/4] 写入王国之泪防具套装体系 ({len(artifacts)} 套)...")
    for art in artifacts:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                3, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                rarity_min = EXCLUDED.rarity_min,
                rarity_max = EXCLUDED.rarity_max,
                icon_url = EXCLUDED.icon_url,
                two_piece_bonus = EXCLUDED.two_piece_bonus,
                four_piece_bonus = EXCLUDED.four_piece_bonus,
                pieces = EXCLUDED.pieces,
                rules_reference = EXCLUDED.rules_reference,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            art['name'], art['rarity_min'], art['rarity_max'], art['icon_url'],
            art['two_piece_bonus'], art['four_piece_bonus'], Json(art['pieces']), Json(art['rules_reference']),
            h, art['version']
        ))
    print(f"  ✓ 成功落库 {len(artifacts)} 套核心防具套装！")

    # 4. 写入底层物理机制 (game_mechanic_rule)
    print(f"\n[4/4] 写入王国之泪底层物理引擎与战斗机制 ({len(mechanics)} 条)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                3, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))
    print(f"  ✓ 成功落库 {len(mechanics)} 项底层物理机制！")

    conn.commit()
    conn.close()
    print("\n=== 《塞尔达传说：王国之泪》全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_all_to_postgres()
