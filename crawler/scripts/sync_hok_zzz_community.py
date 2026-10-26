#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀 (game_id = 24) 与 绝区零 (game_id = 25) 攻略与百科补全新建脚本

为两款热门手游填充高质量高水准的社区攻略 (Guides) 与百科词条 (Wiki Entries)，
彻底解决前端页面攻略/百科 Tab 为空的问题。
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import Json

PG_CONFIG = {
    'host': os.getenv('PG_HOST', '127.0.0.1'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

def sync_hok_community(cur):
    print("--- 正在补充 王者荣耀 (game_id = 24) 攻略与百科 ---")
    guides = [
        {
            "title": "S36赛季野区节奏全景指南：打野速4路线与控龙开节奏",
            "type": "BUILD",
            "difficulty": "MEDIUM",
            "tags": ["打野", "野区节奏", "控龙", "S36赛季", "意识教学"],
            "summary": "详细拆解当前版本打野刷野路线选择（红开刷到蓝还是蓝开保射手）、1分钟中路河道蟹抢夺、两分钟暴君刷新与越塔时机。",
            "content": {
                "sections": [
                    {"title": "一、刷野路线决策", "text": "1. 蓝开路线：适合需要蓝Buff减CD且对抗路在下方的对局，刷完全部野区正好2分05秒升4级就地抓对抗路。\n2. 红开路线：目前最推荐！红Buff附带减速与真伤，刷完全部野区正好抓敌方发育路射手，配合队友拿一血！"},
                    {"title": "二、控龙节奏", "text": "2分钟首条暴君为全队提供伤害增益，4分钟防御塔保护机制消失时必须集合推塔；10分钟暗影主宰带来三波主宰先锋，是破高地的关键质变点！"}
                ]
            },
            "like_count": 3400,
            "useful_count": 2980
        },
        {
            "title": "对抗路兵线博弈哲学：卡线、抢二与传送阵支援法则",
            "type": "CHARACTER",
            "difficulty": "ADVANCED",
            "tags": ["对抗路", "单挑博弈", "卡线", "抢二级", "亚瑟", "孙策"],
            "summary": "对抗路决定胜负的往往不是英雄克制，而是前 30 秒的兵线理解。教你如何卡兵线让对手吃不到经验与经济。",
            "content": {
                "sections": [
                    {"title": "一、抢二核心逻辑", "text": "出门买铁剑，第一波兵线的后排两个弩兵血量最脆，快速击杀后排两只兵即可瞬间升到2级，利用技能压制逼退对手或直接单杀！"},
                    {"title": "二、传送阵使用时机", "text": "清理完兵线后利用边路原初法阵在 1.5 秒内传送至暴君坑支援团战，形成以多打少的局部碾压，之后回线兵线正好进塔。"}
                ]
            },
            "like_count": 2800,
            "useful_count": 2450
        },
        {
            "title": "射手自保与团战走位：从对线压制到破晓成型全流程",
            "type": "GENERAL",
            "difficulty": "EASY",
            "tags": ["射手", "鲁班七号", "孙尚香", "走位", "破晓"],
            "summary": "解析射手对线期如何防止被刺客越塔强杀，如何通过小地图观察敌方打野红蓝Buff推断其Gank动向。",
            "content": {
                "sections": [
                    {"title": "一、看小地图知生死", "text": "若敌方打野红开，且中路法师往发育路靠拢，在 1分20秒~1分40秒 必须缩在防御塔后吃兵，切忌贪线！"},
                    {"title": "二、出装核心原则", "text": "前中期核心三大件（急速战靴、末世/无尽战刃、影刃），在敌方坦克护甲超过 600 后立即预购【穿云弓】过渡至【破晓】，团战永远只输出离你最近的目标。"}
                ]
            },
            "like_count": 3900,
            "useful_count": 3560
        },
        {
            "title": "辅助游走开团圣经：大乔电梯流与硬辅开视野指南",
            "type": "BUILD",
            "difficulty": "MEDIUM",
            "tags": ["辅助", "大乔", "张飞", "视野布控", "开团"],
            "summary": "掌握开局帮中路抢线、转进敌方野区探视野、大乔宿命之海回城瞬间开大招全队满血集结的无解战术。",
            "content": {
                "sections": [
                    {"title": "一、开局思路", "text": "1级买学识宝石帮中路法师快速扔技能清完第一波兵，然后立刻转进敌方野区卡视野看敌方打野是红开还是蓝开，信号标记给全队。"},
                    {"title": "二、大乔电梯流连招", "text": "在龙坑或高地推塔时，提前在安全侧放下二技能宿命之海，队友在残血乘电梯回城的瞬间，大乔按下大招漩涡之门，全队0.1秒满血传送回战场！"}
                ]
            },
            "like_count": 3150,
            "useful_count": 2890
        }
    ]

    wikis = [
        {
            "title": "王者峡谷中立生物与击杀Buff详解",
            "content": "中立生物分为蔚蓝魔道（蓝Buff，提供法力回复与20%冷却缩减）、猩红石像（红Buff，普攻附带减速与真实伤害）、暴君（提升全队物理与法术攻击）、暗影主宰（召唤三波强化主宰先锋飞龙）、风暴龙王（20分钟刷新，击杀获得基于最大生命值30%的极厚雷电护盾，并对周围所有目标释放引雷天罚）。"
        },
        {
            "title": "王者荣耀防御与穿透计算机制",
            "content": "承伤公式为：伤害减免百分比 = 防御值 / (防御值 + 602)。在计算护甲穿透时，系统判定顺序为：【固定数值穿透】优先抵扣，剩余护甲再进行【百分比穿透】计算。因此暗影战斧（固定穿透）适合打脆皮，破晓（40%穿透）适合打高护甲前排坦克。"
        },
        {
            "title": "防御塔机制与保护机制",
            "content": "防御塔在前 4 分钟拥有【格挡护盾】与精灵保护，英雄普通攻击受到的伤害降低 50%。防御塔具有无兵线保护机制，周围没有己方小兵进入时对英雄伤害大幅削减 90%。防御塔单体连续射击同一英雄时伤害成倍递增。"
        }
    ]

    for g in guides:
        cur.execute("""
            INSERT INTO guide (
                game_id, version_id, title, author_id, type, difficulty,
                tags, summary, content, status, like_count, useful_count, verify_count,
                created_at, updated_at
            ) VALUES (
                24, NULL, %s, 1, %s, %s,
                %s, %s, %s, 'PUBLISHED', %s, %s, 25,
                NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (g['title'], g['type'], g['difficulty'], Json(g['tags']), g['summary'], Json(g['content']), g['like_count'], g['useful_count']))

    for wk in wikis:
        cur.execute("""
            INSERT INTO wiki_entry (game_id, title, content, last_updated)
            VALUES (24, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (wk['title'], wk['content']))
    print("--- 王者荣耀 社区数据补充完毕 ---")

def sync_zzz_community(cur):
    print("--- 正在补充 绝区零 (game_id = 25) 攻略与百科 ---")
    guides = [
        {
            "title": "式舆防卫战剧变节点第7层S级速通：艾莲乔纯冰队输出手法",
            "type": "BUILD",
            "difficulty": "ADVANCED",
            "tags": ["式舆防卫战", "深渊", "艾莲乔", "苍角", "莱卡恩", "纯冰队"],
            "summary": "深剖绝区零当前版本天花板配队：莱卡恩极速打入失衡，苍角展旗传递全队1000点攻击力，艾莲乔鲨卷风驻场暴力收割手法。",
            "content": {
                "sections": [
                    {"title": "一、三人循环核心链路", "text": "1. 莱卡恩驻场打出蓄力狼拳削减敌方失衡值，在敌人失衡值达到 95% 时切苍角；\n2. 苍角施放强化特殊技展旗进入涡流状态，触发全队攻击力增益；\n3. 触发连携技：苍角 -> 莱卡恩 -> 艾莲乔登场！"},
                    {"title": "二、艾莲乔爆发输出", "text": "艾莲乔变奏登场后立即施放连携技，随后长按闪避进入巡游冲刺剪刀状态，连续输入3段急冻修剪法，接强化特殊技【鲨卷风】打出巨额碎冰暴击！"}
                ]
            },
            "like_count": 2780,
            "useful_count": 2490
        },
        {
            "title": "朱鸢以太击破流爆发：失衡爆发期一弹千伤教学",
            "type": "CHARACTER",
            "difficulty": "MEDIUM",
            "tags": ["朱鸢", "青衣", "妮可", "以太队", "特勤弹药"],
            "summary": "针对朱鸢特殊机制【特勤弹药】的装填与爆发打法：青衣快速打出失衡易伤，妮可减防黑洞聚怪，朱鸢压制射击瞬间倾泻 9 发强化弹。",
            "content": {
                "sections": [
                    {"title": "一、弹药积攒技巧", "text": "非失衡期不要随意消耗特勤弹药！通过朱鸢的普通攻击第三段、闪避反击以及连携技积攒满 9 颗弹药。"},
                    {"title": "二、失衡期爆发打法", "text": "怪物失衡后，妮可先手强化特殊技打出黑洞聚怪并施加 40% 以太减防，朱鸢连携登场按住方向键下+攻击键进行连环压制扫射，伤害直接拉满！"}
                ]
            },
            "like_count": 2340,
            "useful_count": 2080
        },
        {
            "title": "简·杜物理紊乱异常流构筑：狂乱突刺与双属性反应机制",
            "type": "BUILD",
            "difficulty": "ADVANCED",
            "tags": ["简杜", "物理异常", "紊乱反应", "赛斯", "格莉丝"],
            "summary": "详细解析简·杜狂热状态下的极限闪避无敌帧判定，以及配合格莉丝/柏妮思打出【紊乱 (Disorder)】双属性异常爆破的机制。",
            "content": {
                "sections": [
                    {"title": "一、狂热心流维持", "text": "简杜通过极速闪避反击与强化特殊技进入【狂热】状态，攻击速度大幅飙升，且物理强击积蓄值速度提升 100%，极速打出物理强击重创。"},
                    {"title": "二、紊乱反应爆发", "text": "当目标已经处于一种属性异常（如感电或灼烧）时，简杜若瞬间引爆物理强击，将覆盖产生【紊乱】效果，立即结算前一异常的全部剩余伤害并追加额外紊乱高伤！"}
                ]
            },
            "like_count": 2980,
            "useful_count": 2670
        }
    ]

    wikis = [
        {
            "title": "绝区零失衡值 (Daze) 与连携技机制",
            "content": "敌人生命条下方有失衡值槽（Daze）。击破型代理人（如青衣、莱卡恩、安比）的技能拥有极高失衡倍率。失衡值达到 100% 时怪物陷入瘫痪失衡状态，受击伤害倍率提升（基础 150%~200%）。此时使用重击打中精英怪会触发【连携技】，队伍中其他代理人可无缝切入释放强力终结招式。"
        },
        {
            "title": "属性异常积蓄与紊乱 (Disorder) 反应",
            "content": "对敌人造成属性伤害会累积属性异常积蓄值。满值后触发属性异常：【灼烧】持续火伤、【感电】受击触发落雷、【冻结/碎冰】打断行动并暴击、【侵蚀】附加额外以太伤害、【强击】打断动作并造成巨额物理伤害。若在一种异常持续期间快速叠满另一种异常，将触发【紊乱】反应，产生毁天灭地的爆发！"
        },
        {
            "title": "驱动盘 (Drive Discs) 搭配与强化规则",
            "content": "每个代理人可装备 6 个驱动盘（激活 4件套 + 2件套效果）。1/2/3 号位主属性固定为生命、攻击、防御；4号位可选暴击/暴伤/异常精通；5号位可选属性伤害加成/穿透率；6号位可选冲击力/能量恢复/异常掌控。"
        }
    ]

    for g in guides:
        cur.execute("""
            INSERT INTO guide (
                game_id, version_id, title, author_id, type, difficulty,
                tags, summary, content, status, like_count, useful_count, verify_count,
                created_at, updated_at
            ) VALUES (
                25, NULL, %s, 1, %s, %s,
                %s, %s, %s, 'PUBLISHED', %s, %s, 22,
                NOW(), NOW()
            ) ON CONFLICT DO NOTHING;
        """, (g['title'], g['type'], g['difficulty'], Json(g['tags']), g['summary'], Json(g['content']), g['like_count'], g['useful_count']))

    for wk in wikis:
        cur.execute("""
            INSERT INTO wiki_entry (game_id, title, content, last_updated)
            VALUES (25, %s, %s, NOW())
            ON CONFLICT DO NOTHING;
        """, (wk['title'], wk['content']))
    print("--- 绝区零 社区数据补充完毕 ---")

def sync_all():
    print("=== 开始同步 王者荣耀 与 绝区零 社区数据 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    sync_hok_community(cur)
    sync_zzz_community(cur)
    conn.commit()
    conn.close()
    print("=== 王者荣耀 与 绝区零 社区数据同步完成！ ===")

if __name__ == '__main__':
    sync_all()
