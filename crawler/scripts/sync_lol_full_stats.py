#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英雄联盟 (League of Legends) 全量数值体系落库与同步脚本
包含:
1. 全量 173 位英雄 (基础成长属性1-18级、被动与QWER技能倍率、机制标签、出装与符文推荐)
2. 全量 200+ 件召唤师峡谷/大乱斗装备 (售价、属性曲线、唯一被动/主动、合成路线)
3. 5 大符文系与基石符文 (精密、主宰、巫术、坚决、启迪)
4. 5 大底层战斗公式与常数模型 (护甲/魔抗减伤、穿甲计算次序、韧性衰减、普攻前摇、重伤真伤)
"""

import os
import sys
import time
import json
import re
import hashlib
import concurrent.futures
import requests
import psycopg2
from psycopg2.extras import Json

PG_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

OUT_DIR = os.path.join(os.path.dirname(__file__), "../out")
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def clean_html(text: str) -> str:
    if not text:
        return ""
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# 英雄所属符文之地城邦映射字典
CHAMPION_REGION_MAP = {
    # 艾欧尼亚
    "亚索": "艾欧尼亚", "永恩": "艾欧尼亚", "阿狸": "艾欧尼亚", "李青": "艾欧尼亚", "劫": "艾欧尼亚",
    "阿卡丽": "艾欧尼亚", "艾瑞莉娅": "艾欧尼亚", "烬": "艾欧尼亚", "凯南": "艾欧尼亚", "卡尔玛": "艾欧尼亚",
    "易": "艾欧尼亚", "慎": "艾欧尼亚", "辛德拉": "艾欧尼亚", "韦鲁斯": "艾欧尼亚", "霞": "艾欧尼亚",
    "洛": "艾欧尼亚", "瑟提": "艾欧尼亚", "凯隐": "艾欧尼亚", "锐雯": "艾欧尼亚", "莉莉娅": "艾欧尼亚",
    "孙悟空": "艾欧尼亚",
    # 德玛西亚
    "盖伦": "德玛西亚", "拉克丝": "德玛西亚", "嘉文四世": "德玛西亚", "赵信": "德玛西亚", "菲奥娜": "德玛西亚",
    "薇恩": "德玛西亚", "波比": "德玛西亚", "奎因": "德玛西亚", "加里奥": "德玛西亚", "塞拉斯": "德玛西亚",
    "莫甘娜": "德玛西亚", "凯尔": "德玛西亚", "希瓦娜": "德玛西亚", "卢锡安": "德玛西亚", "娑娜": "德玛西亚",
    # 诺克萨斯
    "德莱厄斯": "诺克萨斯", "德莱文": "诺克萨斯", "卡特琳娜": "诺克萨斯", "斯维因": "诺克萨斯", "泰隆": "诺克萨斯",
    "乐芙兰": "诺克萨斯", "弗拉基米尔": "诺克萨斯", "赛恩": "诺克萨斯", "卡西奥佩娅": "诺克萨斯", "克烈": "诺克萨斯",
    "萨米拉": "诺克萨斯", "贝蕾亚": "诺克萨斯", "安妮": "诺克萨斯", "阿利斯塔": "诺克萨斯", "芮尔": "诺克萨斯",
    # 皮尔特沃夫
    "杰斯": "皮尔特沃夫", "凯特琳": "皮尔特沃夫", "蔚": "皮尔特沃夫", "黑默丁格": "皮尔特沃夫", "奥莉安娜": "皮尔特沃夫",
    "卡蜜尔": "皮尔特沃夫", "伊泽瑞尔": "皮尔特沃夫", "萨勒芬妮": "皮尔特沃夫",
    # 祖安
    "金克丝": "祖安", "艾克": "祖安", "沃里克": "祖安", "辛吉德": "祖安", "维克托": "祖安",
    "图奇": "祖安", "扎克": "祖安", "布里茨": "祖安", "蒙多医生": "祖安", "厄加特": "祖安",
    "迦娜": "祖安", "泽丽": "祖安", "雷娜塔 · 格拉斯克": "祖安",
    # 弗雷尔卓德
    "艾希": "弗雷尔卓德", "瑟庄妮": "弗雷尔卓德", "丽桑卓": "弗雷尔卓德", "布隆": "弗雷尔卓德", "奥拉夫": "弗雷尔卓德",
    "沃利贝尔": "弗雷尔卓德", "奥恩": "弗雷尔卓德", "艾尼维亚": "弗雷尔卓德", "特朗德尔": "弗雷尔卓德", "蛮族之王": "弗雷尔卓德",
    "泰达米尔": "弗雷尔卓德", "努努和威朗普": "弗雷尔卓德", "古拉加斯": "弗雷尔卓德", "乌迪尔": "弗雷尔卓德",
    # 恕瑞玛
    "阿兹尔": "恕瑞玛", "内瑟斯": "恕瑞玛", "雷克顿": "恕瑞玛", "泽拉斯": "恕瑞玛", "希维尔": "恕瑞玛",
    "阿木木": "恕瑞玛", "拉莫斯": "恕瑞玛", "斯卡纳": "恕瑞玛", "雷克塞": "恕瑞玛", "奎桑提": "恕瑞玛", "纳亚菲利": "恕瑞玛",
    # 巨神峰
    "潘森": "巨神峰", "蕾欧娜": "巨神峰", "黛安娜": "巨神峰", "塔里克": "巨神峰", "佐伊": "巨神峰",
    "索拉卡": "巨神峰", "厄斐琉斯": "巨神峰", "奥瑞利安 · 索尔": "巨神峰",
    # 暗影岛
    "锤石": "暗影岛", "赫卡里姆": "暗影岛", "卡莉丝塔": "暗影岛", "佛耶戈": "暗影岛", "格温": "暗影岛",
    "约里克": "暗影岛", "茂凯": "暗影岛", "卡尔萨斯": "暗影岛", "伊利斯": "暗影岛", "薇古丝": "暗影岛",
    # 比尔吉沃特
    "厄运小姐": "比尔吉沃特", "普朗克": "比尔吉沃特", "崔斯特": "比尔吉沃特", "格雷福斯": "比尔吉沃特", "派克": "比尔吉沃特",
    "诺提勒斯": "比尔吉沃特", "俄洛伊": "比尔吉沃特", "塔姆 · 肯奇": "比尔吉沃特", "菲兹": "比尔吉沃特",
    # 班德尔城
    "提莫": "班德尔城", "崔丝塔娜": "班德尔城", "璐璐": "班德尔城", "维迦": "班德尔城", "兰博": "班德尔城",
    "库奇": "班德尔城", "吉格斯": "班德尔城", "悠米": "班德尔城", "克烈": "班德尔城",
    # 虚空
    "卡莎": "虚空", "卡兹克": "虚空", "玛尔扎哈": "虚空", "科加斯": "虚空", "维克兹": "虚空",
    "卡萨丁": "虚空", "卑尔维斯": "虚空", "克格莫": "虚空",
    # 以绪塔尔
    "奇亚娜": "以绪塔尔", "妮蔻": "以绪塔尔", "雷恩加尔": "以绪塔尔", "奈德丽": "以绪塔尔", "米利欧": "以绪塔尔",
    "墨菲特": "以绪塔尔", "婕拉": "以绪塔尔",
    # 符文之地 / 独立漫游
    "巴德": "符文之地", "布兰德": "符文之地", "纳尔": "符文之地", "阿木木": "符文之地", "斯维因": "符文之地",
    "费德提克": "符文之地", "夜曲": "符文之地", "魔腾": "符文之地", "贾克斯": "符文之地", "基兰": "符文之地",
    "希维尔": "符文之地", "斯莫德": "符文之地", "梅尔": "符文之地", "安蓓萨": "符文之地"
}

ROLE_CN_MAP = {
    'fighter': '战士',
    'mage': '法师',
    'assassin': '刺客',
    'marksman': '射手',
    'tank': '坦克',
    'support': '辅助'
}

def fetch_all_champions():
    """从腾讯官方接口抓取并处理全量 173 位英雄数据"""
    print("[LoL] 正在从腾讯官方英雄列表接口获取全量英雄...")
    hero_list_url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
    res = requests.get(hero_list_url, headers=HEADERS, timeout=15)
    raw_heroes = res.json().get('hero', [])
    print(f"[LoL] 成功获取到 {len(raw_heroes)} 位英雄基础档案，正在并行拉取技能与数值成长...")

    def fetch_hero_detail(h):
        hid = h['heroId']
        url = f"https://game.gtimg.cn/images/lol/act/img/js/hero/{hid}.js"
        for attempt in range(4):
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                time.sleep(0.3 * (attempt + 1))
        print(f"Failed to fetch hero {hid} after retries")
        return None

    detail_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for res in executor.map(fetch_hero_detail, raw_heroes):
            if res:
                detail_results.append(res)

    print(f"[LoL] 成功获取 {len(detail_results)} 位英雄详细技能与成长数据，正在格式化为规范数值模型...")

    champions = []
    for d in detail_results:
        hero = d.get('hero', {})
        skins = d.get('skins', [])
        spells = d.get('spells', [])

        name = hero.get('title', '').strip() or hero.get('name', '').strip()
        title = hero.get('name', '').strip()
        alias = hero.get('alias', '')

        # 角色定位
        roles = [ROLE_CN_MAP.get(r, r) for r in hero.get('roles', [])]
        primary_role = roles[0] if roles else '战士'

        # 攻击方式与类型
        attack_range = float(hero.get('attackrange', 175) or 175)
        dmg_type = hero.get('damageType', 'kPhysical')
        dmg_str = "物理" if "Physical" in dmg_type else "法术" if "Magic" in dmg_type else "混合"
        range_str = "远程" if attack_range >= 350 else "近战"
        weapon_type = f"{range_str}·{dmg_str}"

        # 所属地区城邦
        region = CHAMPION_REGION_MAP.get(name, "符文之地")

        # 稀有度星级 (按操作难度和英雄机制划分 3~5 星)
        diff = int(hero.get('difficulty', 5) or 5)
        if diff >= 7 or name in ["亚索", "永恩", "劫", "李青", "阿卡丽", "卡莎", "锐雯", "薇恩", "德莱文"]:
            rarity = 5
        elif diff >= 4:
            rarity = 4
        else:
            rarity = 3

        # 头像与立绘
        avatar_url = ""
        splash_url = ""
        if skins:
            avatar_url = skins[0].get('iconImg') or ""
            splash_url = skins[0].get('mainImg') or ""
        if not avatar_url:
            avatar_url = f"https://game.gtimg.cn/images/lol/act/img/champion/{alias}.png"

        # 1~18 级基础属性成长计算 (Riot 公式)
        hp_base = float(hero.get('hp', 600) or 600)
        hp_per = float(hero.get('hpperlevel', 100) or 100)
        ad_base = float(hero.get('attackdamage', 60) or 60)
        ad_per = float(hero.get('attackdamageperlevel', 3.0) or 3.0)
        arm_base = float(hero.get('armor', 30) or 30)
        arm_per = float(hero.get('armorperlevel', 4.0) or 4.0)
        mr_base = float(hero.get('spellblock', 30) or 30)
        mr_per = float(hero.get('spellblockperlevel', 1.5) or 1.5)
        as_base = float(hero.get('attackspeed', 0.65) or 0.65)
        as_per = float(hero.get('attackspeedperlevel', 3.0) or 3.0)
        ms = float(hero.get('movespeed', 340) or 340)

        base_stats = []
        # 18 个完整等级曲线
        for lvl in range(1, 19):
            # Riot 成长系数公式: f(n) = (n - 1) * (0.7025 + 0.0175 * (n - 1))
            factor = (lvl - 1) * (0.7025 + 0.0175 * (lvl - 1)) if lvl > 1 else 0
            cur_hp = round(hp_base + hp_per * factor)
            cur_ad = round(ad_base + ad_per * factor, 1)
            cur_arm = round(arm_base + arm_per * factor, 1)
            cur_mr = round(mr_base + mr_per * factor, 1)
            cur_as = round(as_base * (1 + (as_per * factor) / 100), 3)

            base_stats.append({
                "level": str(lvl),
                "hp": cur_hp,
                "atk": cur_ad,
                "def": cur_arm,
                "spell_block": cur_mr,
                "attack_speed": f"{cur_as:.3f}",
                "crit_rate": "0.0%",
                "crit_dmg": "175.0%"
            })

        # 突破专长/成长特性
        special_ascension_stat = {
            "stat_name": f"{primary_role}定位成长核心",
            "stages": {
                "1": f"基础射程 {int(attack_range)} | 基础移速 {int(ms)}",
                "6": "核心机制质变 (终极技能R解锁)",
                "11": "2级大招进化 (中后期团战接管)",
                "16": "3级大招峰值 (终极团战爆发)",
                "18": f"满级白值 (血量 {base_stats[-1]['hp']} / 攻击 {base_stats[-1]['atk']})"
            }
        }

        # 技能与天赋 (被动 + QWER)
        talents = []
        passives_list = []
        for s in spells:
            s_key = s.get('spellKey', '').lower()
            s_name = s.get('name', '')
            desc = s.get('description', '') or s.get('dynamicDescription', '')
            desc_clean = clean_html(desc)

            cd = s.get('cooldown', '') or s.get('cooldownburn', '')
            cost = s.get('cost', '') or s.get('costburn', '')
            icon = s.get('abilityIconPath', '')

            scaling = {}
            if cd:
                scaling["cooldown"] = f"{cd} 秒"
            if cost and cost != "0":
                scaling["cost"] = f"{cost} 消耗"
            if s.get('range'):
                scaling["range"] = str(s.get('range'))

            if s_key == 'passive':
                talents.append({
                    "name": f"被动技能·{s_name}",
                    "type": "PASSIVE",
                    "description": desc_clean,
                    "scaling": scaling
                })
                passives_list.append({
                    "name": s_name,
                    "unlock": "英雄被动",
                    "desc": desc_clean
                })
            elif s_key == 'q':
                talents.append({
                    "name": f"Q技能·{s_name}",
                    "type": "NORMAL_ATTACK",
                    "description": desc_clean,
                    "scaling": scaling
                })
            elif s_key in ['w', 'e']:
                talents.append({
                    "name": f"{s_key.upper()}技能·{s_name}",
                    "type": "ELEMENTAL_SKILL",
                    "description": desc_clean,
                    "scaling": scaling
                })
            elif s_key == 'r':
                talents.append({
                    "name": f"终极技能R·{s_name}",
                    "type": "ELEMENTAL_BURST",
                    "description": desc_clean,
                    "scaling": scaling
                })

        # 核心技能机制/技巧 (对应 constellations)
        constellations = [
            {"c": 1, "name": "1级对线换血核心", "desc": f"利用基础射程({int(attack_range)})与前排兵抢线，掌握1级技能压制节奏与换血拉扯。"},
            {"c": 2, "name": "2级抢先抢二斩杀线", "desc": "抢2抢先升级，连招配合小兵仇恨建立兵线优势与血量压制。"},
            {"c": 3, "name": "6级终极技能质变", "desc": "解锁终极技能R，伤害和控制产生质的飞跃，进入高威胁单杀与游走期。"},
            {"c": 4, "name": "神话/核心成装成型", "desc": "第一件核心大件完成后，输出/坦度曲线大幅跃升，具备独立掌线与小龙团主导权。"},
            {"c": 5, "name": "11级终极技能2阶", "desc": "大招冷却时间大幅缩短，伤害基础倍率提升，团战影响力全面覆盖。"},
            {"c": 6, "name": "16级神装团战峰值", "desc": "大招升至满级，全套技能倍率拉满，成为团战胜负手与核心战略支点。"}
        ]

        # 战斗隐藏机制参数 (ICD/前摇/射程/移速)
        special_mechanics = {
            "attack_range": f"{int(attack_range)} 码 ({range_str})",
            "move_speed": f"{int(ms)} 码/秒",
            "base_attack_speed": f"{as_base} 基础攻速 (成长: +{as_per}%/级)",
            "primary_role": f"{primary_role} (综合评级: 伤害 {hero.get('damage', 5)} / 坦度 {hero.get('durability', 5)} / 机动 {hero.get('mobility', 5)})",
            "resource_type": "法力值 (Mana)" if float(hero.get('mp', 0) or 0) > 0 else "怒气/能量/无消耗",
            "damage_attribute": f"{dmg_str}输出为主"
        }

        # 官方推荐配装与符文建议
        if primary_role in ['射手', 'assassin', '刺客']:
            rec_weapons = {"bis": "无尽之刃 + 收集者 + 疾射火炮", "alternative_5s": "多米尼克领主的致意 / 凡性的提醒", "budget_4s": "守护天使 / 水银弯刀"}
            rec_arts = {"bis_set": "精密系·致命节奏 / 强攻", "alt_set": "启迪系·神奇之鞋 + 饼干配送"}
            rec_main = {"sands": "主Q副E (有R点R)", "goblet": "召唤师技能: 闪现 + 治疗 / 疾跑", "circlet": "鞋子: 狂战士胫甲"}
        elif primary_role in ['法师']:
            rec_weapons = {"bis": "卢登的伙伴 + 灭世者的死亡之帽 + 影焰", "alternative_5s": "虚空之杖 / 兰德里的折磨", "budget_4s": "中娅沙漏 / 女妖面纱"}
            rec_arts = {"bis_set": "巫术系·奥术彗星 / 相位猛冲", "alt_set": "启迪系·三重药剂 + 星界洞悉"}
            rec_main = {"sands": "主Q副W (有R点R)", "goblet": "召唤师技能: 闪现 + 传送 / 点燃", "circlet": "鞋子: 法师之靴"}
        elif primary_role in ['坦克']:
            rec_weapons = {"bis": "日炎圣盾 + 狂徒铠甲 + 荆棘之甲", "alternative_5s": "无终恨意 / 冰脉护手", "budget_4s": "自然之力 / 兰顿之兆"}
            rec_arts = {"bis_set": "坚决系·不灭之握 / 余震", "alt_set": "精密系·气定神闲 + 传说:韧性"}
            rec_main = {"sands": "主Q副W (有R点R)", "goblet": "召唤师技能: 闪现 + 传送", "circlet": "鞋子: 铁板靴 / 水银之靴"}
        else: # 战士 / 辅助
            rec_weapons = {"bis": "三相之力 + 黑色切割者 + 斯特拉克的挑战护手", "alternative_5s": "死亡之舞 / 贪欲九头蛇", "budget_4s": "守护天使 / 玛莫提乌斯之噬"}
            rec_arts = {"bis_set": "精密系·征服者", "alt_set": "坚决系·复苏之风 + 坚定"}
            rec_main = {"sands": "主Q副E (有R点R)", "goblet": "召唤师技能: 闪现 + 传送 / 点燃", "circlet": "鞋子: 铁板靴"}

        recommendations = {
            "weapons": rec_weapons,
            "artifacts": rec_arts,
            "main_stats": rec_main,
            "sub_stats": "符文碎片: 适应之力 / 攻击速度 + 适应之力 + 成长生命值"
        }

        champions.append({
            "name": name,
            "title": title,
            "rarity": rarity,
            "element": primary_role,
            "weapon_type": weapon_type,
            "region": region,
            "arkhe": None,
            "avatar_url": avatar_url,
            "splash_url": splash_url,
            "base_stats": base_stats,
            "special_ascension_stat": special_ascension_stat,
            "ascension_materials": [
                {"tier": "1级出门", "items": "多兰系列基础装 + 生命药水"},
                {"tier": "首次回城", "items": "锯齿短匕 / 暴风之剑 / 遗失的章节 / 提亚马特"},
                {"tier": "核心成装", "items": "首件神话核心装 + 2阶抗性/攻速鞋"},
                {"tier": "三件套", "items": "核心三件套完成 (具备终极团战主宰力)"}
            ],
            "talents": talents,
            "passives": passives_list,
            "constellations": constellations,
            "special_mechanics": special_mechanics,
            "recommendations": recommendations,
            "version": "14.19"
        })

    out_file = os.path.join(OUT_DIR, "all_lol_champions.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    print(f"[LoL] 成功保存 {len(champions)} 位英雄全量数值到: {out_file}")
    return champions

def fetch_all_items():
    """从腾讯官方装备库获取 Summoner's Rift / ARAM 装备数据"""
    print("\n[LoL] 正在获取全量装备数据...")
    items_url = "https://game.gtimg.cn/images/lol/act/img/js/items/items.js"
    res = requests.get(items_url, headers=HEADERS, timeout=15).json()
    raw_items = res.get('items', [])

    item_map = {str(it['itemId']): it for it in raw_items}

    valid_items = []
    seen_names = set()

    for it in raw_items:
        name = it.get('name', '').strip()
        maps = it.get('maps', [])
        price = int(it.get('total', 0) or it.get('price', 0) or 0)

        if not name or name.startswith('deprecated') or name in seen_names:
            continue
        if price <= 0:
            continue
        # 只保留峡谷和大乱斗装备
        if not ('召唤师峡谷' in maps or '嚎哭深渊' in maps or len(maps) == 0):
            continue

        seen_names.add(name)

        # 装备分类
        types = it.get('types', [])
        tag = it.get('tag', '')
        if any(t in ['Damage', 'CriticalStrike', 'AttackSpeed', 'LifeSteal', 'ArmorPenetration'] for t in types):
            item_type = "物理攻击装备"
        elif any(t in ['SpellDamage', 'Mana', 'ManaRegen', 'MagicPenetration'] for t in types):
            item_type = "法术强度装备"
        elif any(t in ['Health', 'Armor', 'SpellBlock', 'HealthRegen'] for t in types):
            item_type = "坦克防御装备"
        elif any(t in ['Boots'] for t in types):
            item_type = "鞋子与移速"
        elif any(t in ['Support', 'GoldPer'] for t in types):
            item_type = "辅助与功能装备"
        else:
            item_type = "通用装备"

        # 星级评定 (按售价: >=2800 为 5星成装, >=1000 为 4星中件, <1000 为 3星基础小件)
        if price >= 2800:
            rarity = 5
        elif price >= 1000:
            rarity = 4
        else:
            rarity = 3

        desc_raw = it.get('description', '') or it.get('item_desc', '')
        desc_clean = clean_html(desc_raw)

        # 合成配方解析
        from_ids = it.get('from', [])
        recipe_materials = []
        if from_ids:
            for fid in from_ids:
                if str(fid) in item_map:
                    p_it = item_map[str(fid)]
                    recipe_materials.append(f"{p_it.get('name')} ({p_it.get('total', 0)} G)")
        
        ascension_materials = []
        if recipe_materials:
            ascension_materials.append({
                "tier": "合成路径",
                "items": " + ".join(recipe_materials)
            })
        ascension_materials.append({
            "tier": "总售价/出售价",
            "items": f"总价 {price} 金币 | 出售回收 {it.get('sell', 0)} 金币"
        })

        # 属性曲线模拟 (买入成本与属性收益)
        base_atk_curve = [
            {"level": "合成总价", "atk": price},
            {"level": "出售回收", "atk": int(it.get('sell', 0) or 0)},
        ]

        sub_stat = {
            "stat_name": "装备主属性",
            "values": {
                "售价": f"{price} G",
                "分类": item_type,
                "概要": it.get('plaintext', '') or desc_clean[:25]
            }
        }

        refinements = []
        if desc_clean:
            refinements.append({
                "rank": "装备属性与唯一被动",
                "desc": desc_clean
            })

        valid_items.append({
            "name": name,
            "type": item_type,
            "rarity": rarity,
            "icon_url": it.get('iconPath', ''),
            "base_atk_curve": base_atk_curve,
            "sub_stat": sub_stat,
            "refinements": refinements,
            "ascension_materials": ascension_materials,
            "version": "14.19"
        })

    out_file = os.path.join(OUT_DIR, "all_lol_items.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(valid_items, f, ensure_ascii=False, indent=2)
    print(f"[LoL] 成功保存 {len(valid_items)} 件装备全量数值到: {out_file}")
    return valid_items

def get_lol_runes():
    """构建英雄联盟五大核心符文体系 (Runes Reforged)"""
    return [
        {
            "name": "精密系 (Precision) · 强化攻击与持续伤害",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/7201_Precision.png",
            "two_piece_bonus": "【基石符文】征服者 / 致命节奏 / 强攻：提供极致的普攻持续输出与自适应攻击力/法强加成。",
            "four_piece_bonus": "【次级符文联动】凯旋(击杀回血+金币) + 传说:血统/欢欣(攻速/吸血) + 致命一击/坚毅不倒(残血斩杀/逆境反杀)。",
            "pieces": [
                {"slot": "基石槽位", "name": "征服者 / 强攻 / 致命节奏", "main_stat_rule": "持续交火叠满获得巨额自适应之力与生命偷取", "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/8010_Conqueror.png"},
                {"slot": "英雄槽位", "name": "凯旋 (Triumph)", "main_stat_rule": "参与击杀英雄回复 10% 已损失生命值并提供 20 金币"},
                {"slot": "传说槽位", "name": "传说：欢欣 / 血统 / 韧性", "main_stat_rule": "通过击杀小兵与英雄永久积攒攻击速度/吸血/韧性"},
                {"slot": "战斗槽位", "name": "致命一击 / 坚毅不倒", "main_stat_rule": "对生命值低于 40% 的英雄造成额外 8% 伤害"},
                {"slot": "属性碎片", "name": "自适应之力 x2 + 抗性/成长生命", "main_stat_rule": "+9 自适应之力, +10% 攻速, +65~200 成长生命值"}
            ],
            "rules_reference": {
                "primary_tree": "Precision",
                "recommended_for": "ADC、战士、持攻刺客 (亚索、李青、金克丝、德莱文)"
            },
            "version": "14.19"
        },
        {
            "name": "主宰系 (Domination) · 爆发猎杀与快速接近",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/7200_Domination.png",
            "two_piece_bonus": "【基石符文】电刑 / 黑暗收割 / 丛刃：在极短时间内对单一目标倾泻毁灭性爆发伤害。",
            "four_piece_bonus": "【次级符文联动】恶意中伤/猛然冲击(位移破甲) + 眼球收集器(永久攻击/法强) + 寻宝猎人/终极猎人(大招急速与经济)。",
            "pieces": [
                {"slot": "基石槽位", "name": "电刑 / 黑暗收割 / 丛刃", "main_stat_rule": "3次独立攻击命中劈落闪电爆发 (50~220 + 40%额外AD + 25%AP)", "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/8112_Electrocute.png"},
                {"slot": "恶意槽位", "name": "猛然冲击 (Sudden Impact)", "main_stat_rule": "突进/闪现后获得持续 4 秒的穿甲与法术穿透"},
                {"slot": "追踪槽位", "name": "眼球收集器 (Eyeball Collection)", "main_stat_rule": "参与击杀英雄收集眼球，满层提供 30 点自适应之力"},
                {"slot": "猎手槽位", "name": "终极猎人 / 寻宝猎人", "main_stat_rule": "为终极技能提供至多 31 点技能急速，加快团战大招节奏"},
                {"slot": "属性碎片", "name": "自适应之力 + 移速/成长生命", "main_stat_rule": "+9 自适应之力, +2% 移速, +65~200 成长生命值"}
            ],
            "rules_reference": {
                "primary_tree": "Domination",
                "recommended_for": "爆发刺客、突进收割英雄 (劫、卡特琳娜、阿卡丽、泰隆)"
            },
            "version": "14.19"
        },
        {
            "name": "巫术系 (Sorcery) · 强化技能与法力资源",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/7202_Sorcery.png",
            "two_piece_bonus": "【基石符文】奥术彗星 / 相位猛冲 / 召唤:艾黎：提供远程技能消耗与高机动爆发移速。",
            "four_piece_bonus": "【次级符文联动】法力流系带(持续回蓝) + 超然(技能急速与击杀减CD) + 焦灼/风暴聚集(对线压制/后期成神)。",
            "pieces": [
                {"slot": "基石槽位", "name": "奥术彗星 / 相位猛冲", "main_stat_rule": "技能命中降下彗星造成范围法伤，或3次命中获得巨额移速与减速抗性", "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/8229_ArcaneComet.png"},
                {"slot": "资源槽位", "name": "法力流系带 (Manaflow Band)", "main_stat_rule": "技能命中永久提升 25 点最大法力值，满层持续回复已损失法力"},
                {"slot": "效能槽位", "name": "超然 (Transcendence)", "main_stat_rule": "5/8级获得技能急速，11级后击杀普通技能冷却缩短 20%"},
                {"slot": "威力槽位", "name": "风暴聚集 (Gathering Storm)", "main_stat_rule": "每 10 分钟获得随时间指数暴增的自适应法强/攻击力"},
                {"slot": "属性碎片", "name": "技能急速 + 自适应之力 + 成长生命", "main_stat_rule": "+8 技能急速, +9 自适应之力, +65~200 成长生命值"}
            ],
            "rules_reference": {
                "primary_tree": "Sorcery",
                "recommended_for": "远程法师、拉扯射手 (阿狸、拉克丝、维克托、奥莉安娜)"
            },
            "version": "14.19"
        },
        {
            "name": "坚决系 (Resolve) · 耐久防御与强力控制",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/7204_Resolve.png",
            "two_piece_bonus": "【基石符文】不灭之握 / 余震 / 守护者：提供近战普攻换血偷血、控制爆发双抗护盾与队友保护。",
            "four_piece_bonus": "【次级符文联动】护盾猛击/爆破(推塔神器) + 复苏之风/骸骨镀层(对线减伤) + 过度生长/坚定(无限生命与抗性)。",
            "pieces": [
                {"slot": "基石槽位", "name": "不灭之握 (Grasp of the Undying)", "main_stat_rule": "战斗每4秒下次平A造成额外魔法伤害，回复2%最大生命并永久增加血量", "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/8437_GraspOfTheUndying.png"},
                {"slot": "攻城槽位", "name": "爆破 (Demolish)", "main_stat_rule": "靠近敌方防御塔充能，释放巨额爆破伤害快速吃镀层拆塔"},
                {"slot": "抗性槽位", "name": "骸骨镀层 / 复苏之风", "main_stat_rule": "受到敌方伤害后，后续 3 次攻击伤害降低 30~60 点"},
                {"slot": "活力槽位", "name": "过度生长 (Overgrowth)", "main_stat_rule": "附近小兵野怪阵亡时永久提升最大生命值，达到阈值额外+3.5%生命"},
                {"slot": "属性碎片", "name": "成长生命值 + 护甲/魔抗", "main_stat_rule": "+65~200 成长生命值, +6 护甲 / +8 魔法抗性"}
            ],
            "rules_reference": {
                "primary_tree": "Resolve",
                "recommended_for": "重装战士、坦克、硬控辅助 (盖伦、德莱厄斯、墨菲特、蕾欧娜)"
            },
            "version": "14.19"
        },
        {
            "name": "启迪系 (Inspiration) · 创造性工具与经济超越",
            "rarity_min": 4,
            "rarity_max": 5,
            "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/7203_Whimsy.png",
            "two_piece_bonus": "【基石符文】先攻 / 冰川增幅：抢先出手偷取大量金币与真实伤害加成，或群体范围减速敌军。",
            "four_piece_bonus": "【次级符文联动】神奇之鞋(白嫖高移速鞋) + 三重药剂/饼干配送(赖线神器) + 星界洞悉(召唤师技能与装备极速)。",
            "pieces": [
                {"slot": "基石槽位", "name": "先攻 (First Strike)", "main_stat_rule": "抢先进入交战提供 8% 额外真实伤害，并将伤害转化为等额金币", "icon_url": "https://game.gtimg.cn/images/lol/act/img/runes/8369_FirstStrike.png"},
                {"slot": "发明槽位", "name": "神奇之鞋 (Magical Footwear)", "main_stat_rule": "12分钟自动获得免费轻灵之靴，并永久额外提供 +10 移动速度"},
                {"slot": "补给槽位", "name": "饼干配送 / 三重药剂", "main_stat_rule": "前6分钟赠送回复生命与法力的点心，食用永久增加 40 最大法力"},
                {"slot": "奇迹槽位", "name": "星界洞悉 (Cosmic Insight)", "main_stat_rule": "+18 召唤师技能急速，+10 装备主动技能急速"},
                {"slot": "属性碎片", "name": "技能急速 + 自适应之力 + 移速", "main_stat_rule": "+8 技能急速, +9 自适应之力, +2% 移动速度"}
            ],
            "rules_reference": {
                "primary_tree": "Inspiration",
                "recommended_for": "发育型打野、刺客偷钱流、功能性辅助 (伊泽瑞尔、卡牌大师、卡尔玛)"
            },
            "version": "14.19"
        }
    ]

def get_lol_mechanics():
    """构建英雄联盟底层战斗乘区与公式常数模型"""
    return [
        {
            "category": "DAMAGE_FORMULA",
            "title": "护甲与魔法抗性减伤计算模型",
            "formula": "有效承伤百分比 = 100 / (100 + 抗性) ； 减伤百分比 = 抗性 / (100 + 抗性)",
            "parameters": {
                "100点抗性": "提供 50.0% 减伤率 (等效使最大生命值翻倍，即有效承伤EHP为200%)",
                "200点抗性": "提供 66.7% 减伤率 (有效承伤EHP为300%)",
                "300点抗性": "提供 75.0% 减伤率 (有效承伤EHP为400%)",
                "负抗性机制": "当抗性<0时，增伤百分比 = 2 - 100 / (100 - 抗性)"
            }
        },
        {
            "category": "PENETRATION_SYSTEM",
            "title": "穿甲与护甲/法术穿透计算次序模型",
            "formula": "严格四步判定: ①百分比抗性削减 ➔ ②固定抗性削减 ➔ ③百分比抗性穿透 ➔ ④固定穿甲(Lethality)",
            "parameters": {
                "Step_1_百分比削减": "如黑色切割者 (至多削减敌方 30% 护甲，全队收益)",
                "Step_2_固定削减": "如库奇E技能 (直接削减目标护甲魔抗)",
                "Step_3_百分比穿透": "如多米尼克领主的致意 (自身无视敌方 35% 额外护甲)",
                "Step_4_穿甲换算": "固定穿甲 = Lethality * (0.6 + 0.4 * 自身等级 / 18)"
            }
        },
        {
            "category": "TENACITY_SYSTEM",
            "title": "韧性、控制衰减与无法减免的强控规约",
            "formula": "受控实际时长 = 基础受控时长 * (1 - 韧性A) * (1 - 韧性B) * (1 - 韧性C)",
            "parameters": {
                "乘算叠减": "水银之靴(30%) + 传说:韧性(20%) = 1 - (0.7 * 0.8) = 44% 综合韧性",
                "不可减免控制": "击飞 (Knockup)、击退 (Knockback)、压制 (Suppression) 绝对不受韧性缩短",
                "最低持续限制": "所有控制效果被韧性减免后的实际生效时长不会低于 0.5 秒"
            }
        },
        {
            "category": "ATTACK_FRAME_SYSTEM",
            "title": "攻速收益、前摇时间与重置普攻判定",
            "formula": "前摇时间 = 基础前摇帧 / (当前攻速 / 基础攻速) ； 攻击周期 = 1.0 / 当前攻速",
            "parameters": {
                "常规攻速上限": "2.50 次/秒 (致命节奏、贝蕾亚暴走等特例技能可突破上限)",
                "后摇取消 (Animation Cancel)": "普攻伤害判定生效后，通过移动(走砍走A)或施法取消无伤害的收刀后摇",
                "普攻重置技能 (Auto-Reset)": "如内瑟斯Q、贾克斯W、蔚E，施法后立即重置攻击计时器触发双连击"
            }
        },
        {
            "category": "TRUE_DAMAGE_AND_GRIEVOUS",
            "title": "重伤治疗抑制与真实伤害机制规约",
            "formula": "实际受治疗量 = 理论治疗量 * (1 - 重伤比例) ； 真实伤害 = 面板理论数值 (无视任何抗性减免)",
            "parameters": {
                "基础重伤": "40% 治疗与生命偷取削减 (死刑宣告、湮灭宝珠、棘刺背心)",
                "真实伤害特性": "完全无视敌方护甲、魔法抗性与常规减伤(如虚弱、减伤被动)，仅能被护盾格挡",
                "最大生命真伤": "如薇恩W、菲奥娜破绽，造成目标最大生命值真实伤害，为游戏终极克坦机制"
            }
        }
    ]

def sync_all_to_postgres():
    """将英雄联盟全量数据落库写入 PostgreSQL (game_id = 6)"""
    print("\n========================================================")
    print("=== 开始向 PostgreSQL 写入英雄联盟全量数值体系 (game_id = 6) ===")
    print("========================================================")

    champions = fetch_all_champions()
    items = fetch_all_items()
    runes = get_lol_runes()
    mechanics = get_lol_mechanics()

    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # 1. 写入英雄数据 (game_character)
    print(f"\n[1/4] 写入英雄联盟全量英雄数据 ({len(champions)} 位)...")
    for ch in champions:
        h = calc_hash(ch)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type, region, arkhe,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, passives, constellations,
                special_mechanics, recommendations, data_hash, version
            ) VALUES (
                6, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (game_id, name) DO UPDATE SET
                title = EXCLUDED.title,
                rarity = EXCLUDED.rarity,
                element = EXCLUDED.element,
                weapon_type = EXCLUDED.weapon_type,
                region = EXCLUDED.region,
                arkhe = EXCLUDED.arkhe,
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
            ch['name'], ch['title'], ch['rarity'], ch['element'], ch['weapon_type'], ch['region'], ch['arkhe'],
            ch['avatar_url'], ch['splash_url'], Json(ch['base_stats']), Json(ch['special_ascension_stat']),
            Json(ch['ascension_materials']), Json(ch['talents']), Json(ch['passives']), Json(ch['constellations']),
            Json(ch['special_mechanics']), Json(ch['recommendations']), h, ch['version']
        ))

    print(f"  ✓ 成功落库 {len(champions)} 位英雄！")

    # 2. 写入装备数据 (game_weapon)
    print(f"\n[2/4] 写入英雄联盟全量装备数据 ({len(items)} 件)...")
    for w in items:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                6, %s, %s, %s, %s, %s,
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
            w['name'], w['type'], w['rarity'], w['icon_url'], Json(w['base_atk_curve']),
            Json(w['sub_stat']), Json(w['refinements']), Json(w['ascension_materials']), h, w['version']
        ))

    print(f"  ✓ 成功落库 {len(items)} 件装备！")

    # 3. 写入符文体系 (game_artifact_set)
    print(f"\n[3/4] 写入英雄联盟五大符文体系 ({len(runes)} 系)...")
    for art in runes:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                6, %s, %s, %s, %s,
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

    print(f"  ✓ 成功落库 {len(runes)} 系符文！")

    # 4. 写入战斗机制与公式 (game_mechanic_rule)
    print(f"\n[4/4] 写入英雄联盟核心战斗公式与机制模型 ({len(mechanics)} 条)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                6, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))

    print(f"  ✓ 成功落库 {len(mechanics)} 项底层战斗机制！")

    conn.commit()
    conn.close()
    print("\n=== 英雄联盟全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_all_to_postgres()
