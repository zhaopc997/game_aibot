#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无畏契约 (Valorant) 全量数值体系落库与同步脚本
game_id = 17

包含:
1. 10 位核心特工 Agents (捷风、幽影、雷兹、贤者、猎枭、雷娜、奇乐、不死鸟、尚勃勒、蝰蛇)
   - 官方定位 (决斗者/控场者/先锋/守卫)、生命值与护甲模型
   - C/Q/E 战术技能机制与 X 终极大招伤害与充能点数
2. 10 把全核心枪械武器 (狂徒、幻影、冥驹、恶灵、鬼魅、警长、捍卫者、奥丁、狂怒、短炮)
   - 头/身/腿衰减伤害、射速、弹匣容量、穿透力、后坐力恢复时间
3. 4 大战术防具与护甲套装 (重型护甲、轻型护甲、全战术技能充能套件、爆能器拆装套件)
4. 5 大底层射击与战术机制 (急停射击静止判定、经济系统连败补偿公式、穿墙物理衰减、烟雾弹与视线遮蔽、护甲66%吸收模型)
5. 4 篇高阶攻略与百科词条
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

def get_valorant_characters():
    return [
        {
            "name": "捷风 (Jett)",
            "title": "风之舞者·致命利刃",
            "rarity": 5,
            "element": "风疾",
            "weapon_type": "决斗者 (Duelist)",
            "region": "韩国·首尔",
            "avatar_url": "https://media.valorant-api.com/agents/add6443a-41bd-e414-f6ad-e58d267f4e95/displayicon.png",
            "splash_url": "https://media.valorant-api.com/agents/add6443a-41bd-e414-f6ad-e58d267f4e95/fullportrait.png",
            "base_stats": [
                {"level": "基础", "hp": 100, "shield": 50, "total_ehp": 150, "speed": 100, "run_speed": 6.75}
            ],
            "special_ascension_stat": {"stat_name": "机动位移", "values": {"特征": "长距离无惯性突进滑行"}},
            "ascension_materials": [{"tier": "特工契约", "items": "第一章至第十章解锁专属短炮与称号"}],
            "talents": [
                {"name": "C - 瞬云 (Cloudburst)", "type": "NORMAL_ATTACK", "description": "投掷一颗气流弹，在碰撞后展开为遮蔽视线的短暂烟雾球体（持续 2.5 秒），飞行途中可按住技能键引导烟雾转弯。", "scaling": "充能 2 次，单价 200 誉币"},
                {"name": "Q - 气流升腾 (Updraft)", "type": "ELEMENTAL_SKILL", "description": "借助风力瞬间高高跃向空中，占领高箱或在空中完成空中跳杀。", "scaling": "充能 1 次，单价 150 誉币"},
                {"name": "E - 逐风 (Tailwind)", "type": "ELEMENTAL_BURST", "description": "激活风力准备状态（持续 7.5 秒），再次按下按键立即沿移动方向进行瞬间冲刺突进，击杀2名敌人后重置充能。", "scaling": "招牌技能，每回合免费 1 次，2杀刷新"},
                {"name": "X - 飓刃 (Blade Storm)", "type": "PASSIVE_TALENT", "description": "装备 5 把精准致命的风暴飞刀。左键单发投掷（爆头必杀 150 伤害，击杀立即刷新全部飞刀）；右键投掷全部剩余飞刀。", "scaling": "消耗 8 点终极点数，爆头 150 / 躯干 50 / 腿部 42"}
            ],
            "passives": [{"name": "漂移 (Drift)", "desc": "在空中按住跳跃键可进入滑翔状态，完全免疫坠落伤害。"}],
            "constellations": [],
            "special_mechanics": {
                "core_flow": "决斗拉枪线核心：开逐风准备 -> 瞬云封烟进点 -> 气流冲刺穿烟清点 -> 大招飞刀移动不降精准度！"
            },
            "recommendations": {
                "weapons": {"bis": "冥驹 (Operator) / 狂徒 (Vandal)"},
                "artifacts": {"bis_set": "重型护甲 + 全套技能"}
            },
            "version": "9.06"
        },
        {
            "name": "幽影 (Omen)",
            "title": "暗影幽魂·全图控场",
            "rarity": 5,
            "element": "暗影",
            "weapon_type": "控场者 (Controller)",
            "region": "未知领域",
            "avatar_url": "https://media.valorant-api.com/agents/8e253930-4c05-31dd-1b6c-968525494517/displayicon.png",
            "splash_url": "https://media.valorant-api.com/agents/8e253930-4c05-31dd-1b6c-968525494517/fullportrait.png",
            "base_stats": [{"level": "基础", "hp": 100, "shield": 50, "total_ehp": 150, "speed": 100, "run_speed": 6.75}],
            "special_ascension_stat": {"stat_name": "暗影潜行", "values": {"特征": "30秒自动回能暗影烟雾"}},
            "ascension_materials": [{"tier": "特工契约", "items": "幽影专属鬼魅皮肤"}],
            "talents": [
                {"name": "C - 暗影步 (Shrouded Step)", "type": "NORMAL_ATTACK", "description": "引导短暂时间后，传送到最远 15 米外的目标可见位置，用于骗声音或转移枪线。", "scaling": "充能 2 次，单价 100 誉币"},
                {"name": "Q - 迷乱 (Paranoia)", "type": "ELEMENTAL_SKILL", "description": "向前发射一道穿透墙体的暗影盲波，被击中的所有敌人视野距离急剧缩减并丧失听觉，持续 2 秒。", "scaling": "充能 1 次，单价 250 誉币"},
                {"name": "E - 暗魇 (Dark Cover)", "type": "ELEMENTAL_BURST", "description": "进入暗影相位视野，向远距离指定坐标释放空心暗影烟雾，持续 15 秒，每 30 秒自动充能 1 颗。", "scaling": "招牌技能，常备 2 颗，自动冷却恢复"},
                {"name": "X - 暗影宿命 (From the Shadows)", "type": "PASSIVE_TALENT", "description": "调出全图小地图，传送到地图上的任意选定位置。传送期间显现为暗影实体（可被击散取消），传送成功完成终极背刺。", "scaling": "消耗 7 点终极点数，可按键安全取消"}
            ],
            "passives": [{"name": "虚空视界", "desc": "施放暗魇时可穿透障碍物直观查看落点高低差。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "进攻封单向烟与过路烟，残局利用暗影宿命假传送捡包或绕后偷袭。"},
            "recommendations": {"weapons": {"bis": "狂徒 (Vandal) / 幻影 (Phantom)"}, "artifacts": {"bis_set": "重型护甲"}},
            "version": "9.06"
        },
        {
            "name": "雷兹 (Raze)",
            "title": "狂轰滥炸·爆破专家",
            "rarity": 5,
            "element": "爆轰",
            "weapon_type": "决斗者 (Duelist)",
            "region": "巴西·萨尔瓦多",
            "avatar_url": "https://media.valorant-api.com/agents/f94c3b30-42be-e959-889c-5aa313dba261/displayicon.png",
            "splash_url": "https://media.valorant-api.com/agents/f94c3b30-42be-e959-889c-5aa313dba261/fullportrait.png",
            "base_stats": [{"level": "基础", "hp": 100, "shield": 50, "total_ehp": 150, "speed": 100, "run_speed": 6.75}],
            "special_ascension_stat": {"stat_name": "爆炸跳跃", "values": {"特征": "炸药包双弹射极限进点"}},
            "ascension_materials": [{"tier": "特工契约", "items": "雷兹专属经典手枪皮肤"}],
            "talents": [
                {"name": "C - 巡查车 (Boom Bot)", "type": "NORMAL_ATTACK", "description": "部署地面自走巡查车，遇墙反弹；发现前方扇形视野内的敌人后会加速冲锋锁定并自爆造成高额范围伤害。", "scaling": "充能 1 次，单价 300 誉币"},
                {"name": "Q - 惊喜翻腾 (Blast Pack)", "type": "ELEMENTAL_SKILL", "description": "投掷一枚炸药包，黏在表面后可手动引爆，将雷兹弹射向空中形成高机动位移，对敌人造成轻微击退与伤害。", "scaling": "充能 2 次，单价 200 誉币"},
                {"name": "E - 彩雷飞溅 (Paint Shells)", "type": "ELEMENTAL_BURST", "description": "投掷一枚集束手雷，初次爆炸后分裂出4枚小型子母雷连续二次轰炸，清点利器。", "scaling": "招牌技能，每回合免费 1 次，2杀刷新"},
                {"name": "X - 晚安焰火 (Showstopper)", "type": "PASSIVE_TALENT", "description": "扛起重型单兵火箭筒，发射一枚造成毁灭性大范围爆炸伤害的巨型火箭弹，正面命中必定瞬秒满血满甲敌人！", "scaling": "消耗 8 点终极点数，中心伤害 150+"}
            ],
            "passives": [{"name": "炸药抗性", "desc": "雷兹自身受到惊喜翻腾炸药包伤害大幅降低并转化为强劲推力。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "双炸药包超级跳跃空中开大，配合集束手雷封死拆包点或狭窄转角。"},
            "recommendations": {"weapons": {"bis": "狂徒 (Vandal) / 判官 (Judge)"}, "artifacts": {"bis_set": "重型护甲"}},
            "version": "9.06"
        },
        {
            "name": "贤者 (Sage)",
            "title": "静谧壁垒·生命源泉",
            "rarity": 5,
            "element": "冰晶",
            "weapon_type": "守卫 (Sentinel)",
            "region": "中国·陕西",
            "avatar_url": "https://media.valorant-api.com/agents/569fdd95-4d10-43ab-ca70-79becc718b46/displayicon.png",
            "splash_url": "https://media.valorant-api.com/agents/569fdd95-4d10-43ab-ca70-79becc718b46/fullportrait.png",
            "base_stats": [{"level": "基础", "hp": 100, "shield": 50, "total_ehp": 150, "speed": 100, "run_speed": 6.75}],
            "special_ascension_stat": {"stat_name": "复活与治疗", "values": {"特征": "唯二起死回生战略终极技能"}},
            "ascension_materials": [{"tier": "特工契约", "items": "贤者专属鬼魅皮肤"}],
            "talents": [
                {"name": "C - 屏障法球 (Barrier Orb)", "type": "NORMAL_ATTACK", "description": "筑起一道包含4个独立节段的坚固冰晶墙，可封堵通道或垫高身位架奇特枪线，阻挡视线与火力。", "scaling": "充能 1 次，单价 400 誉币，生命值 800"},
                {"name": "Q - 减速法球 (Slow Orb)", "type": "ELEMENTAL_SKILL", "description": "投掷一颗减速晶球，碎裂后在地面形成减速区域，走入其中的敌人移动速度降低 50% 且踏冰发出巨大声响。", "scaling": "充能 2 次，单价 200 誉币"},
                {"name": "E - 治疗法球 (Healing Orb)", "type": "ELEMENTAL_BURST", "description": "瞄准受伤队友或自身施放治疗，使队友在 5 秒内回复至多 100 点生命值（自身回复 30 点）。", "scaling": "招牌技能，冷却时间 45 秒"},
                {"name": "X - 再起 (Resurrection)", "type": "PASSIVE_TALENT", "description": "瞄准倒地阵亡队友的遗骨引导施法，在短暂延迟后将其以 100 点满生命值复活重返战局！", "scaling": "消耗 8 点终极点数，逆转人数劣势神技"}
            ],
            "passives": [{"name": "晶石感知", "desc": "准星对准队友时可透视其当前生命值状态。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "防守开局冰墙封主路拖延RUSH，残局复活核心打手形成人数压制。"},
            "recommendations": {"weapons": {"bis": "狂徒 (Vandal) / 幻影 (Phantom)"}, "artifacts": {"bis_set": "重型护甲"}},
            "version": "9.06"
        },
        {
            "name": "猎枭 (Sova)",
            "title": "极地神射·透视猎手",
            "rarity": 5,
            "element": "雷电",
            "weapon_type": "先锋 (Initiator)",
            "region": "俄罗斯·塞维洛莫尔斯克",
            "avatar_url": "https://media.valorant-api.com/agents/320b2a48-4d9b-a075-30f1-1f93a9b638fa/displayicon.png",
            "splash_url": "https://media.valorant-api.com/agents/320b2a48-4d9b-a075-30f1-1f93a9b638fa/fullportrait.png",
            "base_stats": [{"level": "基础", "hp": 100, "shield": 50, "total_ehp": 150, "speed": 100, "run_speed": 6.75}],
            "special_ascension_stat": {"stat_name": "侦察穿透", "values": {"特征": "全图定点几何箭与隔墙轰击"}},
            "ascension_materials": [{"tier": "特工契约", "items": "猎枭专属警长手枪皮肤"}],
            "talents": [
                {"name": "C - 枭眼无人机 (Owl Drone)", "type": "NORMAL_ATTACK", "description": "操纵一架可飞行的侦察无人机，点击左键发射侦察飞镖，命中敌人后持续标记其真实轮廓。", "scaling": "充能 1 次，单价 400 誉币"},
                {"name": "Q - 震荡箭 (Shock Bolt)", "type": "ELEMENTAL_SKILL", "description": "拉弓射出一支爆裂电能箭，命中后炸裂造成范围电击伤害，可设置最多 2 次遇墙反弹。", "scaling": "充能 2 次，单价 150 誉币，最高 75 伤害"},
                {"name": "E - 寻敌箭 (Recon Bolt)", "type": "ELEMENTAL_BURST", "description": "射出一支声呐声波箭，落地后激活脉冲声波，直接侦测并高亮显示视线范围内的所有敌人轮廓。", "scaling": "招牌技能，每 40 秒自动冷却恢复"},
                {"name": "X - 狂猎之怒 (Hunter's Fury)", "type": "PASSIVE_TALENT", "description": "装备战弓蓄力，最多发射 3 道贯穿全地图墙体的超远距离毁灭能量冲击波，造成 80 点重创并标记敌人。", "scaling": "消耗 8 点终极点数，穿墙杀人与远程拖延拆包"}
            ],
            "passives": [{"name": "几何测算", "desc": "右键可在 0/1/2 次反弹之间切换，蓄力条精确控制射程。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "背地图几何点位开局寻敌箭探点，残局后退开大穿墙阻截拆包。"},
            "recommendations": {"weapons": {"bis": "狂徒 (Vandal) / 奥丁 (Odin)"}, "artifacts": {"bis_set": "重型护甲"}},
            "version": "9.06"
        },
        {
            "name": "雷娜 (Reyna)",
            "title": "幽冥女皇·噬灵杀神",
            "rarity": 5,
            "element": "幽魂",
            "weapon_type": "决斗者 (Duelist)",
            "region": "墨西哥",
            "avatar_url": "https://media.valorant-api.com/agents/a3bfb854-4347-657b-7b03-4f947a4f2d8f/displayicon.png",
            "splash_url": "https://media.valorant-api.com/agents/a3bfb854-4347-657b-7b03-4f947a4f2d8f/fullportrait.png",
            "base_stats": [{"level": "基础", "hp": 100, "shield": 50, "total_ehp": 150, "speed": 100, "run_speed": 6.75}],
            "special_ascension_stat": {"stat_name": "杀戮滚雪球", "values": {"特征": "击杀即刻无敌位移或超额回血"}},
            "ascension_materials": [{"tier": "特工契约", "items": "雷娜专属狂怒手枪皮肤"}],
            "talents": [
                {"name": "C - 睥睨 (Lear)", "type": "NORMAL_ATTACK", "description": "掷出一只可穿透掩体的幽魂虚灵之眼，直视眼睛的敌人将陷入视野受限致盲状态（可被敌方打碎）。", "scaling": "充能 2 次，单价 250 誉币"},
                {"name": "Q - 噬灵 (Devour)", "type": "ELEMENTAL_SKILL", "description": "吸收倒下敌人留下的灵魂晶球，在短时间内迅速恢复至 150 点满血满甲状态，超出部分转化为临时护甲。", "scaling": "与 E 技能共用 2 次充能，单价 100 誉币"},
                {"name": "E - 逐魂 (Dismiss)", "type": "ELEMENTAL_BURST", "description": "消耗灵魂晶球进入无形虚化状态，获得短暂无敌判定与移动加速，大招期间更可完全隐身！", "scaling": "拉脱枪线无伤撤出重围神技"},
                {"name": "X - 女皇降临 (Empress)", "type": "PASSIVE_TALENT", "description": "激活狂暴嗜血状态，射速提高 15%、换弹速度提高 25%，噬灵自动触发且无限次使用逐魂隐身，每次击杀刷新大招时长！", "scaling": "消耗 8 点终极点数，顶级单兵通关大招"}
            ],
            "passives": [{"name": "灵魂收割", "desc": "击杀或参与击杀 3 秒内留下一颗悬浮 3 秒的灵魂晶球。"}],
            "constellations": [],
            "special_mechanics": {"core_flow": "极度考验纯枪法的滚雪球特工：拿首杀 -> 逐魂脱身拉开身位 -> 噬灵补满血甲 -> 开大狂暴连杀！"},
            "recommendations": {"weapons": {"bis": "狂徒 (Vandal) / 警长 (Sheriff)"}, "artifacts": {"bis_set": "重型护甲"}},
            "version": "9.06"
        }
    ]

def get_valorant_weapons():
    return [
        {
            "name": "狂徒 (Vandal)",
            "type": "突击步枪",
            "rarity": 5,
            "icon_url": "https://media.valorant-api.com/weapons/9c82e19d-4575-0200-1a81-3eacf00cf872/displayicon.png",
            "base_atk_curve": {"头": 160, "躯干": 40, "腿部": 34},
            "sub_stat": {"type": "弹匣与射速", "values": {"弹匣": "25发", "备弹": "75发", "射速": "9.75发/秒", "穿透": "中等穿透"}},
            "refinements": [
                {"rank": 1, "desc": "全距离无衰减！任何距离命中头部必定造成 160 点纯伤害，一枪秒杀满血满甲特工。急停单点首发精准度极高。"},
                {"rank": 2, "desc": "连发第 4 发起后坐力剧烈横向摆动，核心打法为 2~3 发急停速射或单点爆头。"}
            ],
            "ascension_materials": [{"tier": "商城售价", "items": "2,900 誉币"}],
            "version": "9.06"
        },
        {
            "name": "幻影 (Phantom)",
            "type": "消音步枪",
            "rarity": 5,
            "icon_url": "https://media.valorant-api.com/weapons/ee8da937-434c-fd07-8e78-eb90a775b156/displayicon.png",
            "base_atk_curve": {"0-15m头": 156, "15-30m头": 140, "30m+头": 124, "0-15m身": 39, "15-30m身": 35, "30m+身": 31},
            "sub_stat": {"type": "消音与弹道", "values": {"弹匣": "30发", "备弹": "90发", "射速": "11.0发/秒", "特性": "无枪口火焰/弹道穿烟隐形"}},
            "refinements": [
                {"rank": 1, "desc": "15米内爆头 156 必秒；全消音设计，穿烟射击不会暴露子弹轨迹，且扫射压枪稳定性远优于狂徒。"},
                {"rank": 2, "desc": "适合控场者（如幽影、蝰蛇）在烟雾中打伏击，以及近距离狭窄点位泼水压制。"}
            ],
            "ascension_materials": [{"tier": "商城售价", "items": "2,900 誉币"}],
            "version": "9.06"
        },
        {
            "name": "冥驹 (Operator)",
            "type": "重型狙击步枪",
            "rarity": 5,
            "icon_url": "https://media.valorant-api.com/weapons/a03b24d3-4319-996d-0f8c-94eac02437d3/displayicon.png",
            "base_atk_curve": {"头": 255, "躯干": 150, "腿部": 120},
            "sub_stat": {"type": "开镜倍率", "values": {"弹匣": "5发", "备弹": "10发", "倍率": "2.5x / 5.0x 双倍镜", "穿透": "极高穿透"}},
            "refinements": [
                {"rank": 1, "desc": "终极一枪毙命武器！命中上半身任何部位（头部或躯干）保底造成 150 点致命伤害，瞬间击杀满甲敌人。"},
                {"rank": 2, "desc": "移动中射击弹道极度散乱，必须在完全停步或架枪状态下开火。捷风与尚勃勒核心大狙。"}
            ],
            "ascension_materials": [{"tier": "商城售价", "items": "4,700 誉币"}],
            "version": "9.06"
        },
        {
            "name": "警长 (Sheriff)",
            "type": "重型左轮手枪",
            "rarity": 4,
            "icon_url": "https://media.valorant-api.com/weapons/e3367f0f-44f3-8ac7-9c3f-c1f0ee3b5735/displayicon.png",
            "base_atk_curve": {"0-30m头": 159, "30m+头": 145, "0-30m身": 55, "30m+身": 50},
            "sub_stat": {"type": "经济局神器", "values": {"弹匣": "6发", "备弹": "24发", "穿透": "高穿透"}},
            "refinements": [
                {"rank": 1, "desc": "30米内爆头 159 必秒满甲！经济局以小博大、一发翻盘的代表武器。"},
                {"rank": 2, "desc": "急停要求极高，首发命中后需等待准星完全收缩后方可打出第二发高精度射击。"}
            ],
            "ascension_materials": [{"tier": "商城售价", "items": "800 誉币"}],
            "version": "9.06"
        },
        {
            "name": "恶灵 (Spectre)",
            "type": "微型冲锋枪",
            "rarity": 3,
            "icon_url": "https://media.valorant-api.com/weapons/462080d1-4035-2937-7c09-27aa2a5c27a7/displayicon.png",
            "base_atk_curve": {"0-15m头": 78, "15m+头": 66, "0-15m身": 26, "15m+身": 22},
            "sub_stat": {"type": "机动近战", "values": {"弹匣": "30发", "备弹": "90发", "射速": "13.3发/秒", "特性": "消音奔跑射击惩罚低"}},
            "refinements": [
                {"rank": 1, "desc": "第二回合强起局与半买局的核心冲锋枪，近距离奔跑急停结合泼水容错率极高。"}
            ],
            "ascension_materials": [{"tier": "商城售价", "items": "1,600 誉币"}],
            "version": "9.06"
        },
        {
            "name": "鬼魅 (Ghost)",
            "type": "消音手枪",
            "rarity": 3,
            "icon_url": "https://media.valorant-api.com/weapons/1baa85b4-4c70-1284-64bb-6481dfc3bb4e/displayicon.png",
            "base_atk_curve": {"0-30m头": 105, "30m+头": 87, "0-30m身": 30, "30m+身": 25},
            "sub_stat": {"type": "手枪局统治者", "values": {"弹匣": "15发", "备弹": "45发", "特性": "全消音高单点精度"}},
            "refinements": [
                {"rank": 1, "desc": "手枪局绝对统治武器！爆头造成 105 点伤害，直接秒杀不买甲或购买轻甲的敌人。"}
            ],
            "ascension_materials": [{"tier": "商城售价", "items": "500 誉币"}],
            "version": "9.06"
        }
    ]

def get_valorant_artifacts():
    return [
        {
            "name": "重型护甲套装 (Heavy Shields)",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://media.valorant-api.com/themes/heavy_shields.png",
            "two_piece_bonus": "提供 50 点额外护甲值，使特工总有效生命值提升至 150 HP。",
            "four_piece_bonus": "护甲吸收特工受到伤害的 66%，直至护甲值耗尽。长枪局全甲出装必备标准。",
            "pieces": [
                {"slot": "头胸防护", "name": "凯夫拉复合重装胸甲", "main_stat": "50 护甲耐久"},
                {"slot": "战术绑带", "name": "防弹高抗拉纤维战术挂具", "main_stat": "66% 伤害吸收"}
            ],
            "version": "9.06"
        },
        {
            "name": "轻型护甲套件 (Light Shields)",
            "rarity_min": 2,
            "rarity_max": 3,
            "icon_url": "https://media.valorant-api.com/themes/light_shields.png",
            "two_piece_bonus": "提供 25 点额外护甲值，使特工总生命值达到 125 HP。",
            "four_piece_bonus": "吸收受到伤害的 66%。性价比极高，常用于半买局或省钱买大狙局。",
            "pieces": [
                {"slot": "轻质防弹", "name": "轻量化陶瓷插板背心", "main_stat": "25 护甲耐久"}
            ],
            "version": "9.06"
        },
        {
            "name": "爆能器战术套件 (Spike Kit)",
            "rarity_min": 5,
            "rarity_max": 5,
            "icon_url": "https://media.valorant-api.com/themes/spike_kit.png",
            "two_piece_bonus": "安装爆能器耗时固定 4.0 秒，安装成功后全队获得 300 誉币额外奖励。",
            "four_piece_bonus": "拆除爆能器耗时 7.0 秒，达到 3.5 秒时锁定拆除进度半格判定。引爆倒计时 45 秒。",
            "pieces": [
                {"slot": "爆能核心", "name": "辐能聚变爆能核心", "main_stat": "爆破范围 40 米必杀"}
            ],
            "version": "9.06"
        }
    ]

def get_valorant_mechanics():
    return [
        {
            "category": "射击物理",
            "title": "急停射击 (Counter-Strafing) 与静止扩散判定",
            "formula": "Speed <= 30% Base_Speed -> Spread_Angle = 0 (Pinpoint First Bullet Accuracy)",
            "parameters": {
                "input": "向左按 A 移动时，松开 A 并瞬间轻点 D 键，角色在 0.05 秒内静止停步",
                "accuracy": "静止瞬间准星扩散角归零，狂徒/幻影首发子弹 100% 绝对命中准星中心点",
                "penalty": "奔跑或跳跃中开枪扩散角扩大 500%~1200%，子弹随机飞向天花板"
            }
        },
        {
            "category": "竞技经济",
            "title": "无畏契约回合经济算法与连败补偿公式",
            "formula": "Round_Reward: Win = +3,000 | Loss_1 = +1,400 | Loss_2 = +1,900 | Loss_3 = +2,400 | Loss_4+ = +2,900",
            "parameters": {
                "kill": "每次击杀敌人获得 +200 誉币",
                "plant": "进攻方成功安装爆能器，全队所有人获得 +300 誉币奖励",
                "cap": "誉币存储上限为 9,000 誉币",
                "full_buy": "全买线标准：枪械 2,900 + 重甲 1,000 + 全技能 400~600 = 保底需 4,300 誉币"
            }
        },
        {
            "category": "穿透物理",
            "title": "穿墙等级与材质减伤物理模型",
            "formula": "Penetration_Level * Material_Thickness = Wallbang_Damage (High/Med/Low)",
            "parameters": {
                "high_penetration": "冥驹、奥丁、警长拥有高穿透，可轻松穿透厚木板、集装箱铁皮与瓦砾墙体",
                "med_penetration": "狂徒、幻影拥有中等穿透，可穿透单层木门和轻型薄箱",
                "damage_loss": "穿墙后根据材质厚度衰减 20%~60% 的基础伤害，高穿武器穿墙爆头仍可一枪致命"
            }
        },
        {
            "category": "伤害吸收",
            "title": "护甲 66% 伤害吸收双层生命模型",
            "formula": "Flesh_Dmg = Total_Dmg * 34% | Shield_Dmg = Total_Dmg * 66%",
            "parameters": {
                "absorption": "当特工身上有护甲时，受到伤害的 66% 由护甲承担，34% 扣除肉体 HP",
                "depletion": "当护甲耐久归零后，后续所有伤害 100% 直接作用于 100 点血量直到阵亡",
                "headshot_math": "狂徒 160 点爆头伤害：护甲承受 105.6（耗尽50甲），血量承受 110 点（超过100HP直接阵亡）"
            }
        }
    ]

def get_valorant_guides_and_wikis():
    guides = [
        {
            "title": "无畏契约萌新枪法蜕变：急停身法与预瞄爆头线教学",
            "type": "GENERAL",
            "difficulty": "BEGINNER",
            "tags": ["急停射击", "爆头线", "狂徒", "预瞄", "枪法教学"],
            "summary": "详细拆解反向按键急停原理、靶场练习方法，以及主流地图中箱子水平爆头线预瞄定位核心技巧。",
            "content": {
                "sections": [
                    {"title": "一、反向按键急停核心动作", "text": "往左走按住A，遇到敌人松开A的瞬间立刻轻敲一下D！此时角色速度立刻归零，按下左键首发子弹100%命中准星中心。"},
                    {"title": "二、架枪爆头线规律", "text": "瓦罗兰特所有特工身高模型完全一致！地图上的绝大部分绿色单人箱、墙体线槽都正好等于特工站立时的头部水平线。"}
                ]
            },
            "like_count": 2100,
            "useful_count": 1850
        },
        {
            "title": "控场之王幽影 (Omen) 进阶：全图单向烟与大招战术解析",
            "type": "CHARACTER",
            "difficulty": "ADVANCED",
            "tags": ["幽影", "单向烟", "暗影宿命", "大招背刺", "控场位"],
            "summary": "掌握幽影每 30 秒免费烟雾的最佳封烟落点，教你利用高低落差封出只看敌人脚踝的无敌单向烟。",
            "content": {
                "sections": [
                    {"title": "一、单向烟原理", "text": "利用箱子边沿或门框，将烟雾球中心架在高处。敌人进门时视野全被烟雾遮挡，而你在低处能清晰看到敌人的双脚，一枪秒杀。"},
                    {"title": "二、大招传送核心思路", "text": "残局 1v2 时，在 B 点踩包瞬间开大传送到 A 点捡包下包；或者传送至敌方出生点抓回防背身。"}
                ]
            },
            "like_count": 1780,
            "useful_count": 1540
        }
    ]
    wikis = [
        {
            "title": "无畏契约武器分类与购买指南",
            "content": "武器分为手枪、冲锋枪、霰弹枪、步枪、狙击枪与重机枪。步枪中狂徒无距离衰减爆头一枪死；幻影消音近战高射速；冥驹为重型大狙命中上半身必秒。"
        },
        {
            "title": "爆能器 (Spike) 安装与拆除规则",
            "content": "进攻方携带有爆能器，在包点内长按 4 秒即可安装完成，安装后进入 45 秒引爆倒计时。防守方拆包耗时 7 秒，拆除达到一半（3.5秒）时获得阶段保留。"
        }
    ]
    return guides, wikis

def sync_all():
    print("=== 开始同步 无畏契约 (Valorant) 全量数据 (game_id = 17) ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    chars = get_valorant_characters()
    print(f"正在写入 {len(chars)} 位特工数据...")
    for c in chars:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version, created_at, updated_at
            ) VALUES (
                17, %s, %s, %s, %s, %s, %s,
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

    weaps = get_valorant_weapons()
    print(f"正在写入 {len(weaps)} 把枪械武器数据...")
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
                17, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(curve),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    arts = get_valorant_artifacts()
    print(f"正在写入 {len(arts)} 套护甲与战术套件数据...")
    for a in arts:
        h = calc_hash(a)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference, data_hash, version, created_at, updated_at
            ) VALUES (
                17, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (
            a['name'], a['rarity_min'], a['rarity_max'], a['icon_url'],
            a['two_piece_bonus'], a['four_piece_bonus'], Json(a['pieces']), Json({}), h, a['version']
        ))

    mechs = get_valorant_mechanics()
    print(f"正在写入 {len(mechs)} 条战斗机制与公式...")
    for m in mechs:
        cur.execute("""
            INSERT INTO game_mechanic_rule (game_id, category, title, formula, parameters, created_at, updated_at)
            VALUES (17, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    guides, wikis = get_valorant_guides_and_wikis()
    print(f"正在写入 {len(guides)} 篇攻略与 {len(wikis)} 条百科词条...")
    for g in guides:
        cur.execute("""
            INSERT INTO guide (
                game_id, version_id, title, author_id, type, difficulty,
                tags, summary, content, status, like_count, useful_count, verify_count,
                created_at, updated_at
            ) VALUES (
                17, NULL, %s, 1, %s, %s,
                %s, %s, %s, 'PUBLISHED', %s, %s, 15,
                NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (g['title'], g['type'], g['difficulty'], Json(g['tags']), g['summary'], Json(g['content']), g['like_count'], g['useful_count']))

    for wk in wikis:
        cur.execute("""
            INSERT INTO wiki_entry (game_id, title, content, last_updated)
            VALUES (17, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (wk['title'], wk['content']))

    conn.commit()
    conn.close()
    print("=== 无畏契约 (game_id = 17) 全量数据写入完成！ ===")

if __name__ == '__main__':
    sync_all()
