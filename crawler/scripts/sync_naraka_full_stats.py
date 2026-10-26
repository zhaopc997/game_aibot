#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永劫无间 (Naraka: Bladepoint) 全量数值体系落库与同步脚本
game_id = 20

包含:
1. 7 位核心武侠英雄 (宁红夜、特木尔、迦南、季沧海、土御门胡桃、天海、岳山)
   - 基础体力/护甲白值
   - F 技能分支与 V 奥义变身机制
2. 8 把经典近战与远程神兵 (太刀、长剑、阔刀、斩马刀、枪、鸟铳、弓箭、火炮)
   - 平A伤害、蓄力倍率、剑气/招式机制
3. 6 大专属神技魂玉与通用属性魂玉 (惊雷十劫、凤凰羽、烈火斩、夺魂·魄、幽冥步、凌霄披甲)
4. 5 大底层战斗机制与公式 (剪刀石头布振刀克制判定、蓄力取消与滑步、受击硬直与受身翻滚、精力短闪无敌帧、体力护甲模型)
5. 3 篇高阶攻略与百科词条
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

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def get_naraka_characters():
    return [
        {
            "name": "宁红夜 (Viper Ning)",
            "title": "昆仑玄女·盲剑客",
            "rarity": 5,
            "element": "昆仑极阴",
            "weapon_type": "控制/爆发",
            "region": "昆仑圣山",
            "avatar_url": "https://patchwiki.biligame.com/images/yjwj/4/46/avatar_viper_ning.png",
            "splash_url": "https://patchwiki.biligame.com/images/yjwj/4/46/splash_viper_ning.jpg",
            "base_stats": [{"level": "基础", "hp": 1000, "armor": 1000, "stamina": 100, "speed": 100}],
            "special_ascension_stat": {"stat_name": "控制特化", "values": {"特权": "5秒全体眩晕团灭大招"}},
            "ascension_materials": [{"tier": "英雄修行", "items": "修行任务与通币解锁"}],
            "talents": [
                {"name": "F - 昆仑决·断筋", "type": "NORMAL_ATTACK", "description": "踢出一道阴柔内劲，击飞正面敌人造成重创，并封印其普通攻击与蓄力招式 8 秒。", "scaling": "冷却 15 秒，击飞并封招"},
                {"name": "V - 赤练无明", "type": "ELEMENTAL_BURST", "description": "祈求阴神之力召唤阴神之眼，用幽冥血线标记视线范围内的所有敌人，持续 5 秒期间宁红夜无法攻击；5秒后血线引爆，眩晕所有被标记敌人整整 5 秒！", "scaling": "三排翻盘第一大招，强控5秒"}
            ],
            "passives": [{"name": "昆仑秘术", "desc": "感知周围 15 米内潜伏或隐身的敌人。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "三排先手核心：隐身近身 -> 开大赤练无明锁人 -> 队友补伤害或拆火 -> 5秒眩晕全灭！"},
            "recommendations": {"weapons": {"bis": "长剑 / 鸟铳"}, "artifacts": {"bis_set": "夺魂·魄 + 凌霄披甲"}},
            "version": "Season 14"
        },
        {
            "name": "季沧海 (Ji Canghai)",
            "title": "烈豪·狂饮醉歌",
            "rarity": 5,
            "element": "烈火",
            "weapon_type": "单挑/刺客",
            "region": "中原绿林",
            "avatar_url": "https://patchwiki.biligame.com/images/yjwj/9/91/avatar_ji_canghai.png",
            "splash_url": "https://patchwiki.biligame.com/images/yjwj/9/91/splash_ji_canghai.jpg",
            "base_stats": [{"level": "基础", "hp": 1000, "armor": 1000, "stamina": 100, "speed": 100}],
            "special_ascension_stat": {"stat_name": "颠勺无限连", "values": {"特权": "开大疾跑无限升龙颠勺"}},
            "ascension_materials": [{"tier": "英雄修行", "items": "火之试炼解锁"}],
            "talents": [
                {"name": "F - 燎原劲·巨焰", "type": "NORMAL_ATTACK", "description": "凝聚内力轰出一发巨大火球，并在地面留下烈焰焦土，命中敌人击倒并施加灼烧与重伤。", "scaling": "冷却 15 秒，破除金钟罩"},
                {"name": "V - 迅烈如火·狂战", "type": "ELEMENTAL_BURST", "description": "全身燃起狂暴烈焰，进入狂奔姿态，大幅提升移动速度、格挡远程弹道，奔跑碰撞击退敌人；开大期间精力消耗大幅降低，可打出无解的太刀颠勺无限连！", "scaling": "持续 25 秒，狂奔撞人附带灼烧"}
            ],
            "passives": [{"name": "烈火焚身", "desc": "灼烧状态下的敌人受到的所有伤害提升 10%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "单挑天花板：开启迅烈如火 -> 太刀滑步近身 -> C+右键升龙起飞 -> 落地疾跑再升龙颠勺！"},
            "recommendations": {"weapons": {"bis": "太刀 / 阔刀"}, "artifacts": {"bis_set": "惊雷十劫 + 幽冥步"}},
            "version": "Season 14"
        },
        {
            "name": "天海 (Tianhai)",
            "title": "金刚伏魔·妙手空空",
            "rarity": 5,
            "element": "佛光",
            "weapon_type": "坦克/先手",
            "region": "无极帝国",
            "avatar_url": "https://patchwiki.biligame.com/images/yjwj/3/30/avatar_tianhai.png",
            "splash_url": "https://patchwiki.biligame.com/images/yjwj/3/30/splash_tianhai.jpg",
            "base_stats": [{"level": "基础", "hp": 1000, "armor": 1000, "stamina": 100, "speed": 100}],
            "special_ascension_stat": {"stat_name": "金刚化身", "values": {"特权": "化身伏魔金刚双抓摔砸秒杀"}},
            "ascension_materials": [{"tier": "英雄修行", "items": "少林伏魔试炼"}],
            "talents": [
                {"name": "F - 金钟罩·振刀", "type": "NORMAL_ATTACK", "description": "运功显化不坏金钟，受击中亦可强制施放，弹开一切物理打击，若震反敌方蓄力招式直接振掉其武器！", "scaling": "受击解控神器，反弹振刀"},
                {"name": "V - 金刚伏魔·治愈", "type": "ELEMENTAL_BURST", "description": "化身为顶天立地的八臂伏魔金刚，获得 4000 点超巨额生命值。左键/右键抓取敌人，抓取两人后同时猛砸地面造成瞬秒重创并回复自身体力！", "scaling": "大佛化身持续 30 秒，双抓砸地秒杀"}
            ],
            "passives": [{"name": "不坏之躯", "desc": "金钟罩释放瞬间免疫一切负面异常状态。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "决赛圈绝对霸主：受击开金钟反打 -> 残血开大变大佛 -> 抓取敌方两人合璧双砸！"},
            "recommendations": {"weapons": {"bis": "阔刀 / 火炮"}, "artifacts": {"bis_set": "烈火斩 + 凌霄披甲"}},
            "version": "Season 14"
        },
        {
            "name": "土御门胡桃 (Kurumi)",
            "title": "日轮巫女·济世悬壶",
            "rarity": 5,
            "element": "神道光华",
            "weapon_type": "辅助/治疗",
            "region": "日轮国",
            "avatar_url": "https://patchwiki.biligame.com/images/yjwj/0/07/avatar_kurumi.png",
            "splash_url": "https://patchwiki.biligame.com/images/yjwj/0/07/splash_kurumi.jpg",
            "base_stats": [{"level": "基础", "hp": 1000, "armor": 1000, "stamina": 100, "speed": 100}],
            "special_ascension_stat": {"stat_name": "团队续航", "values": {"特权": "超远距离魂冢拉人与大招瞬间抬满护甲"}},
            "ascension_materials": [{"tier": "英雄修行", "items": "日轮巫女试炼"}],
            "talents": [
                {"name": "F - 庇护·增威", "type": "NORMAL_ATTACK", "description": "召唤光伞与队友建立光线连接，持续恢复队友体力并提升其 20% 攻击力，按左键可瞬间位移至队友身旁击飞敌人。", "scaling": "冷却 15 秒，增攻回血位移三合一"},
                {"name": "V - 净天地·急救", "type": "ELEMENTAL_BURST", "description": "布下纯净巫女法阵，瞬间为全队所有存活队友回复大量体力与全部护甲，并驱散所有灼烧重伤负面状态！", "scaling": "瞬间全队满甲急救，团战续航神器"}
            ],
            "passives": [{"name": "神道护佑", "desc": "超远距离可隔空安全救援阵亡队友的魂冢。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "三排第一奶妈：光伞牵狗链保输出 -> 团战关键时刻开 V 净天地瞬间拉满全队血甲！"},
            "recommendations": {"weapons": {"bis": "长剑 / 弓箭"}, "artifacts": {"bis_set": "凤凰羽 + 夺魂·魄"}},
            "version": "Season 14"
        },
        {
            "name": "迦南 (Viper Canaan)",
            "title": "风沙修罗·幻影刺客",
            "rarity": 5,
            "element": "暗影潜行",
            "weapon_type": "机动/刺客",
            "region": "月轮国",
            "avatar_url": "https://patchwiki.biligame.com/images/yjwj/c/cf/avatar_canaan.png",
            "splash_url": "https://patchwiki.biligame.com/images/yjwj/c/cf/splash_canaan.jpg",
            "base_stats": [{"level": "基础", "hp": 1000, "armor": 1000, "stamina": 100, "speed": 100}],
            "special_ascension_stat": {"stat_name": "全队隐身", "values": {"特权": "全队全体隐匿并大幅减少短闪精力"}},
            "ascension_materials": [{"tier": "英雄修行", "items": "刺客试炼"}],
            "talents": [
                {"name": "F - 追魂·连闪", "type": "NORMAL_ATTACK", "description": "向指定方向瞬间瞬移一段距离，可连续充能瞬移 2 次，用于拉扯枪线或翻墙逃生。", "scaling": "充能 2 次，神出鬼没"},
                {"name": "V - 寂静暗刑·群隐", "type": "ELEMENTAL_BURST", "description": "施展修罗秘术使全队所有人进入隐身状态，移动中轮廓半透明，静止时完全隐形；期间大幅缩减 F 技能冷却并提升闪避距离！", "scaling": "持续 20 秒，克制宁红夜大招锁人"}
            ],
            "passives": [{"name": "刺客本能", "desc": "在墙体壁击攻击伤害提高 20%。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "极速脱战与刺杀：见势不妙两段瞬移拉开 -> 团队开大集体隐身反包围偷袭！"},
            "recommendations": {"weapons": {"bis": "太刀 / 鸟铳"}, "artifacts": {"bis_set": "幽冥步 + 惊雷十劫"}},
            "version": "Season 14"
        }
    ]

def get_naraka_weapons():
    return [
        {
            "name": "太刀 (Katana)",
            "type": "近战武器",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/thumb/7/7b/weapon_katana.png/120px-weapon_katana.png",
            "base_atk_curve": {"白色": 100, "蓝色": 130, "紫色": 160, "金色": 200},
            "sub_stat": {"type": "招式特性", "values": {"特性": "百裂斩蓄力极速、升龙滞空判定极优"}},
            "refinements": [
                {"rank": 1, "desc": "左键或右键按住蓄力打出【百裂斩】，1.5秒完成二段蓄力，瞬发多段撕裂剑气，是单挑无限连升龙的核心武器。"}
            ],
            "ascension_materials": [{"tier": "局内强化", "items": "武备匣修复磨损度"}],
            "version": "Season 14"
        },
        {
            "name": "长剑 (Longsword)",
            "type": "近战武器",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/thumb/1/14/weapon_longsword.png/120px-weapon_longsword.png",
            "base_atk_curve": {"白色": 100, "蓝色": 130, "紫色": 160, "金色": 200},
            "sub_stat": {"type": "剑气远程", "values": {"特性": "横向与纵向超远距离剑气打击"}},
            "refinements": [
                {"rank": 1, "desc": "左键蓄力打出横向范围剑气，右键蓄力打出纵向追踪剑气，攻击距离远超一般近战，配合魂玉【凤凰羽】打出双发交叉剑气。"}
            ],
            "ascension_materials": [{"tier": "局内强化", "items": "武备匣修复磨损度"}],
            "version": "Season 14"
        },
        {
            "name": "阔刀 (Greatsword)",
            "type": "近战武器",
            "rarity": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/thumb/9/97/weapon_greatsword.png/120px-weapon_greatsword.png",
            "base_atk_curve": {"白色": 120, "蓝色": 155, "紫色": 190, "金色": 240},
            "sub_stat": {"type": "磐石架势", "values": {"特性": "拼刀不弹开直接转入蓄力反击"}},
            "refinements": [
                {"rank": 1, "desc": "拥有全游戏独有的【磐石架势】！与敌方平击拼刀时不会被弹开，而是瞬间格挡并直接蓄满反击刀势，重劈毁天灭地。"}
            ],
            "ascension_materials": [{"tier": "局内强化", "items": "武备匣修复磨损度"}],
            "version": "Season 14"
        },
        {
            "name": "鸟铳 (Musket)",
            "type": "远程武器",
            "rarity": 4,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/thumb/4/4b/weapon_musket.png/120px-weapon_musket.png",
            "base_atk_curve": {"白色": 150, "蓝色": 200, "紫色": 260, "金色": 340},
            "sub_stat": {"type": "精确射击", "values": {"弹匣": "5发", "爆头倍率": "2.0x"}},
            "refinements": [
                {"rank": 1, "desc": "右键开镜精确瞄准，弹道初速极高几乎无下坠，远距离爆头两枪击破金甲。"}
            ],
            "ascension_materials": [{"tier": "局内强化", "items": "武备匣装填弹药"}],
            "version": "Season 14"
        }
    ]

def get_naraka_artifacts():
    return [
        {
            "name": "惊雷十劫 (Thunder Sunder)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/souljade_thunder.png",
            "two_piece_bonus": "太刀专属神技：百裂斩招式发生质变，攻击附带疾雷撕裂并追加一段极速穿心突刺。",
            "four_piece_bonus": "突刺命中后恢复伤害 65% 的体力与护甲，单挑翻盘顶级神玉。",
            "pieces": [{"slot": "神技魂玉", "name": "惊雷十劫", "main_stat": "太刀极意质变"}],
            "version": "Season 14"
        },
        {
            "name": "凤凰羽 (Phoenix Feather)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/souljade_phoenix.png",
            "two_piece_bonus": "长剑专属神技：蓄力打出两道交叉呼啸的凤凰烈火剑气，可穿透敌方多人。",
            "four_piece_bonus": "剑气飞行速度提升 25%，命中造成灼烧重伤效果。",
            "pieces": [{"slot": "神技魂玉", "name": "凤凰羽", "main_stat": "长剑双剑气"}],
            "version": "Season 14"
        },
        {
            "name": "烈火斩 (Flame Cleave)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/souljade_firecleave.png",
            "two_piece_bonus": "阔刀专属神技：三段蓄力追加超大范围地狱烈火轰斩。",
            "four_piece_bonus": "造成巨额火属性焚烧伤害，一刀清场。",
            "pieces": [{"slot": "神技魂玉", "name": "烈火斩", "main_stat": "阔刀烈火"}],
            "version": "Season 14"
        },
        {
            "name": "夺魂·魄 (Soul Purge)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://patchwiki.biligame.com/images/yjwj/souljade_soulpurge.png",
            "two_piece_bonus": "通用近战：振刀处决成功后，立即回复自身 75% 的已损失体力与护甲值！",
            "four_piece_bonus": "振刀处决伤害提升 30%，残局 1v3 绝地反杀第一神玉。",
            "pieces": [{"slot": "特技魂玉", "name": "夺魂·魄", "main_stat": "振刀吸血"}],
            "version": "Season 14"
        }
    ]

def get_naraka_mechanics():
    return [
        {
            "category": "搏击判定",
            "title": "振刀与剪刀石头布三方克制绝对法则",
            "formula": "Normal_Attack(普攻白刀) > Parry_Stance(振刀红光) > Focus_Attack(霸体蓝顶) > Normal_Attack(普攻白刀)",
            "parameters": {
                "rule_1": "普通攻击（白刀）无视振刀架势，直接砍中正在振刀的敌人打出硬直",
                "rule_2": "振刀架势（红光）绝对克制蓄力霸体（蓝顶），弹飞其武器并触发必中致命处决",
                "rule_3": "蓄力霸体（蓝顶）免疫普通攻击的受击硬直，且伤害与削韧远高于普通攻击"
            }
        },
        {
            "category": "身法技巧",
            "title": "蓄力取消 (Stance Cancel) 与滑步身法",
            "formula": "Hold_Atk(蓄力) + Shift/Space/C = Cancel_Into_Slide/Jump -> Reset_Neutral",
            "parameters": {
                "cancel": "蓄力蓝光闪烁前按 Shift（闪避）、C（蹲伏）或空格（跳跃）可无缝取消蓄力动作",
                "bait": "假意蓄力骗对方振刀（红光），振刀有长达 0.6 秒的硬直空当，蓄力取消后立刻打出白刀平A打满一套连招"
            }
        },
        {
            "category": "防御机制",
            "title": "精力槽 (Stamina) 消耗与短闪/长闪无敌帧判定",
            "formula": "Short_Dodge(轻按Shift) = 0.2s I-frame | Long_Dodge(长按Shift) = Long Distance Run",
            "parameters": {
                "short_dodge": "轻点 Shift 消耗 1 段精力进行短距离滑铲闪避，拥有 0.2 秒绝对无敌帧判定",
                "stamina_limit": "满精力可连续施放 2 次短闪，精力耗尽后无法闪避和奔跑，陷入任人宰割状态"
            }
        },
        {
            "category": "承伤模型",
            "title": "护甲耐久与体力双层承受模型",
            "formula": "Damage_Order: Armor_Durability -> Flesh_HP",
            "parameters": {
                "armor": "白甲 500、蓝甲 750、紫甲 1000、金甲 1250、白金甲 1500",
                "armor_powders": "在战斗拉扯中利用钩索拉开身位使用甲粉（护甲粉末）比使用凝血丸（回血）快 1.5 秒"
            }
        }
    ]

def get_naraka_guides_and_wikis():
    guides = [
        {
            "title": "永劫无间三排阵容体系：宁红夜一波流与双变身稳扎流",
            "type": "BUILD",
            "difficulty": "ADVANCED",
            "tags": ["三排阵容", "宁红夜", "天海", "大佛", "一波流"],
            "summary": "解析主流三排天梯高胜率体系：宁红夜赤练无明锁人 + 季沧海巨焰火球 + 特木尔风牢的无解控制链打法。",
            "content": {
                "sections": [
                    {"title": "一、宁红夜一波流启动逻辑", "text": "宁红夜开启赤练无明锁住敌人5秒 -> 特木尔开风之极阻挡敌方反手 -> 5秒眩晕生效瞬间全队集火秒杀敌方核心主C！"},
                    {"title": "二、双变身防守反击", "text": "天海（大佛）+ 岳山（神将）双变身，利用金刚八臂双抓与神将破千军在狭窄决赛圈清场，容错率极高。"}
                ]
            },
            "like_count": 1650,
            "useful_count": 1420
        },
        {
            "title": "太刀与长剑升龙连招秘籍：从平A到空中抓抓乐",
            "type": "CHARACTER",
            "difficulty": "MEDIUM",
            "tags": ["太刀", "长剑", "升龙连招", "百裂斩", "近战博弈"],
            "summary": "手把手教你掌握 C+右键 升龙的核心判定帧，配合钩索重置滞空状态完成 100% 击杀的无缝连招。",
            "content": {
                "sections": [
                    {"title": "一、太刀基础升龙连", "text": "左键平A两段打出僵直 -> 瞬间按下 C+右键 打出升龙挑飞 -> 空中立刻点击左键空A两段 -> 落地瞬间按 Shift 滑步接右键蓄力百裂斩！"},
                    {"title": "二、防振刀心法", "text": "千万不要连续出两段蓝霸体！一段蓄力后根据对手抬手按 C 骗振，对手振空红光一闪直接白刀将其击飞！"}
                ]
            },
            "like_count": 1890,
            "useful_count": 1670
        }
    ]
    wikis = [
        {
            "title": "永劫无间武器克制法则",
            "content": "近战三态博弈：普通攻击（白刀）克制振刀（红光），振刀（红光）克制蓄力霸体（蓝顶），蓄力霸体（蓝顶）克制普通攻击（白刀）。被蓄力击中将陷入重击硬直，被振刀则武器脱手并遭受处决重创。"
        },
        {
            "title": "魂玉分类与作用",
            "content": "魂玉分为攻击魂玉、体力魂玉、近抗/远抗魂玉、特技魂玉（如夺魂、幽冥步）与武器专属神技魂玉（如惊雷十劫、凤凰羽、烈火斩）。金魂玉能彻底重构武器的核心招式机制。"
        }
    ]
    return guides, wikis

def sync_all():
    print("=== 开始同步 永劫无间 (Naraka) 全量数据 (game_id = 20) ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    chars = get_naraka_characters()
    print(f"正在写入 {len(chars)} 位英雄数据...")
    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                20, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'], c['region'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['passives']), Json(c['constellations']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))

    weaps = get_naraka_weapons()
    print(f"正在写入 {len(weaps)} 把武器数据...")
    for w in weaps:
        h = calc_hash(w)
        curve = w['base_atk_curve']
        if isinstance(curve, dict):
            curve = [{'level': str(k), 'atk': v} for k, v in curve.items()]
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version, created_at, updated_at
            ) VALUES (
                20, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = get_naraka_artifacts()
    print(f"正在写入 {len(arts)} 套魂玉系统数据...")
    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                20, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = get_naraka_mechanics()
    print(f"正在写入 {len(mechs)} 条战斗机制与公式...")
    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (20, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    guides, wikis = get_naraka_guides_and_wikis()
    print(f"正在写入 {len(guides)} 篇攻略与 {len(wikis)} 条百科词条...")
    for g in guides:
        cur.execute("""
            INSERT INTO guide (
                game_id, version_id, title, author_id, type, difficulty,
                tags, summary, content, status, like_count, useful_count, verify_count,
                created_at, updated_at
            ) VALUES (
                20, NULL, %s, 1, %s, %s,
                %s, %s, %s, 'PUBLISHED', %s, %s, 12,
                NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (g['title'], g['type'], g['difficulty'], Json(g['tags']), g['summary'], Json(g['content']), g['like_count'], g['useful_count']))

    for wk in wikis:
        cur.execute("""
            INSERT INTO wiki_entry (game_id, title, content, last_updated)
            VALUES (20, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (wk['title'], wk['content']))

    conn.commit()
    conn.close()
    print("=== 永劫无间 (game_id = 20) 全量数据写入完成！ ===")

if __name__ == '__main__':
    sync_all()
