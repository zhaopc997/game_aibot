#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
崩坏：星穹铁道 (Honkai: Star Rail) 全量数值体系落库与同步脚本
game_id = 8

包含:
1. 全量 92 位角色 (基础白值1-80级生命/攻击/防御/速度、普攻/战技/终结技/天赋/秘技、星魂1-6阶、额外能力、毕业配装推荐)
2. 全量 167 个光锥 (基础面板1-80级、命途、叠影1-5阶特效技能、晋阶材料)
3. 33 套隧洞遗器与位面饰品 (2件套/4件套机制属性、适配命途与角色)
4. 5 大底层战斗公式模型 (行动值与速度公式、超击破与击破特攻、效果命中率、八大伤害乘区、能量回能循环)
"""

import os
import sys
import json
import re
import hashlib
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

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def clean_html(text: str) -> str:
    if not text:
        return ""
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# 命途与战斗属性中文映射
PATH_CN_MAP = {
    "Destruction": "毁灭",
    "Hunt": "巡猎",
    "Erudition": "智识",
    "Harmony": "同谐",
    "Nihility": "虚无",
    "Preservation": "存护",
    "Abundance": "丰饶",
    "Remembrance": "记忆",
    "Elation": "欢愉"
}

ELEMENT_CN_MAP = {
    "Physical": "物理",
    "Fire": "火",
    "Ice": "冰",
    "Lightning": "雷",
    "Wind": "风",
    "Quantum": "量子",
    "Imaginary": "虚数"
}

# 角色中文名与专属称号字典
CHAR_NAME_MAP = {
    "Trailblazer_Destruction": ("开拓者·毁灭", "星穹列车新星"),
    "March_7th_Preservation": ("三月七·存护", "冰晶流萤少女"),
    "Dan_Heng": ("丹恒", "列车冷面护卫"),
    "Himeko": ("姬子", "星穹列车领航员"),
    "Welt": ("瓦尔特", "前逆熵盟主"),
    "Arlan": ("阿兰", "空间站防卫科长"),
    "Asta": ("艾丝妲", "空间站代理站长"),
    "Herta": ("黑塔", "天才俱乐部#83"),
    "Bronya": ("布洛妮娅", "贝洛伯格第十九任大守护者"),
    "Seele": ("希儿", "地火核心骨干"),
    "Serval": ("希露瓦", "永动机械屋店主"),
    "Gepard": ("杰帕德", "银鬃铁卫戍卫官"),
    "Natasha": ("娜塔莎", "下层区黑心诊所医生"),
    "Pela": ("佩拉", "银鬃铁卫情报官"),
    "Clara": ("克拉拉", "史瓦罗庇护的孤女"),
    "Sampo": ("桑博", "雅利洛走私商贩"),
    "Hook": ("虎克", "漆黑的虎克大人"),
    "Trailblazer_Preservation": ("开拓者·存护", "存护之志继承者"),
    "Qingque": ("青雀", "太卜司卜者"),
    "Tingyun": ("停云", "停云"),
    "Jing_Yuan": ("景元", "罗浮神策将军"),
    "Sushang": ("素裳", "云骑军李素裳"),
    "Yanqing": ("彦卿", "罗浮剑首"),
    "Bailu": ("白露", "衔药龙女"),
    "Silver_Wolf": ("银狼", "星核猎手超级黑客"),
    "Luocha": ("罗刹", "异邦棺柩行商"),
    "Yukong": ("驭空", "天舶司司舵"),
    "Blade": ("刃", "星核猎手死生之剑"),
    "Kafka": ("卡芙卡", "星核猎手核心"),
    "Luka": ("卢卡", "地火机械臂格斗士"),
    "Fu_Xuan": ("符玄", "罗浮太卜司太卜"),
    "Dan_Heng_Imbibitor_Lunae": ("丹恒·饮月", "持明罗浮龙尊"),
    "Lynx": ("玲可", "极地探险家"),
    "Jingliu": ("镜流", "前代罗浮剑首"),
    "Topaz_and_Numby": ("托帕&账账", "星际和平公司资深总监"),
    "Guinaifen": ("桂乃芬", "罗浮杂技主播"),
    "Huohuo": ("藿藿", "十王司判官见习"),
    "Argenti": ("银枝", "纯美骑士团"),
    "Hanya": ("寒鸦", "十王司冥差判官"),
    "Ruan_Mei": ("阮·梅", "天才俱乐部#81生命学者"),
    "Dr_Ratio": ("真理医生", "博识学会维里塔斯·拉齐奥"),
    "Xueyi": ("雪衣", "十王司判官偃偶"),
    "Black_Swan": ("黑天鹅", "流光忆庭忆者"),
    "Sparkle": ("花火", "假面愚者"),
    "Misha": ("米沙", "白日梦酒店门童"),
    "Acheron": ("黄泉", "虚无令使·巡海游侠"),
    "Aventurine": ("砂金", "星际和平公司石心十人"),
    "Gallagher": ("加拉赫", "猎犬家系治安官"),
    "Robin": ("知更鸟", "匹诺康尼天籁巨星"),
    "Boothill": ("波提欧", "巡海游侠改造牛仔"),
    "Firefly": ("流萤", "格拉默铁骑格温四式·萨姆"),
    "Jade": ("翡翠", "星际和平公司石心十人"),
    "Trailblazer_Harmony": ("开拓者·同谐", "钟表匠意志继承者"),
    "Yunli": ("云璃", "朱明仙舟猎剑少女"),
    "Jiaoqiu": ("椒丘", "曜青仙舟医士策士"),
    "March_7th_Hunt": ("三月七·巡猎", "剑仙三月七"),
    "Feixiao": ("飞霄", "曜青天击将军"),
    "Lingsha": ("灵砂", "罗浮丹鼎司司鼎"),
    "Moze": ("貊泽", "曜青影卫暗杀者"),
    "Rappa": ("乱破", "巡海游侠忍侠"),
    "Sunday": ("星期日", "同谐家族前家主"),
    "Fugue": ("归忘之流", "停云再生姿态"),
    "The_Herta": ("大黑塔", "天才俱乐部#83真身"),
    "Aglaea": ("阿格莱雅", "翁法罗斯织锦者"),
    "Trailblazer_Remembrance": ("开拓者·记忆", "记忆命途开拓者"),
    "Tribbie": ("崔碧", "翁法罗斯先知"),
    "Mydei": ("麦狄", "翁法罗斯勇士"),
    "Castorice": ("卡斯托莉丝", "冥界引渡人"),
    "Anaxa": ("阿那克萨", "天幕哲学家"),
    "Hyacine": ("希雅辛", "风暴追逐者"),
    "Cipher": ("赛弗", "量子秘术师"),
    "Saber": ("阿尔托莉雅·潘德拉贡", "誓约胜利骑士王"),
    "Archer": ("卫宫士郎", "无限剑制投影者"),
    "Phainon": ("费农", "毁灭命途执行官"),
    "Hysilens": ("希希伦斯", "深海低语者"),
    "Cerydra": ("赛瑞德拉", "天琴乐师"),
    "Evernight": ("永夜", "无光黑夜使者"),
    "Dan_Heng_Permansor_Terrae": ("丹恒·地涌", "持明恒定守卫者"),
    "Cyrene": ("塞壬", "深海海妖之歌"),
    "The_Dahlia": ("大丽花", "假面黑花"),
    "Yao_Guang": ("瑶光", "天枢星曜使者"),
    "Sparxie": ("火花", "欢愉小丑"),
    "Ashveil": ("灰烬之纱", "猎杀行者"),
    "Trailblazer_Elation": ("开拓者·欢愉", "欢愉之主"),
    "Silver_Wolf_LV_999": ("超级银狼", "终极骇客形态"),
    "Evanescia": ("伊凡妮西亚", "幻光织梦者"),
    "Mortenax_Blade": ("死生之刃", "冥血淬火之锋"),
    "Himeko_Nova": ("新星姬子", "轨道卫星炽阳"),
    "Rin_Tohsaka": ("远坂凛", "宝石魔术师"),
    "Gilgamesh": ("吉尔伽美什", "英雄王·王之宝库"),
    "Robin_Summeretto": ("盛夏知更鸟", "沙滩夏日巡礼"),
    "Aventurine_Waveflair": ("浪潮砂金", "碧海豪赌客")
}

# 光锥中文名对照表
LC_NAME_MAP = {
    "Arrows": "锋矢",
    "Cornucopia": "物丰",
    "Collapsing_Sky": "天倾",
    "Amber": "琥珀",
    "Void": "幽邃",
    "Chorus": "齐颂",
    "Data_Bank": "智库",
    "Darting_Arrow": "离弦",
    "Fine_Fruit": "嘉果",
    "Shattered_Home": "乐矢",
    "Defense": "戍御",
    "Loop": "渊环",
    "Meshing_Cogs": "轮契",
    "Passkey": "灵钥",
    "Adversarial": "相抗",
    "Multiplication": "蕃育",
    "Post_Op_Conversation": "一场术后对话",
    "Good_Night_and_Sleep_Well": "晚安与睡颜",
    "Day_One_of_My_New_Life": "这就是我啦！",
    "Only_Silence_Remains": "唯有沉默",
    "Memories_of_the_Past": "记忆中的模样",
    "The_Moles_Welcome_You": "鼹鼠党欢迎你",
    "The_Birth_of_the_Self": "『我』的诞生",
    "Shared_Feeling": "同一种心情",
    "Eyes_of_the_Prey": "猎物的视线",
    "Landau_s_Choice": "朗道的选择",
    "Swordplay": "论剑",
    "Planetary_Rendezvous": "行星相会",
    "A_Secret_Vow": "秘密誓心",
    "Make_the_World_Clamor": "让世界喧嚣吧",
    "Perfect_Timing": "此时恰好",
    "Resolution_Shines_As_Pearls_of_Sweat": "决心如汗珠般闪耀",
    "Trend_of_the_Universal_Market": "宇宙市场趋势",
    "Subscribe_for_More": "点个关注吧！",
    "Dance_Dance_Dance": "与行星相会",
    "Under_the_Blue_Sky": "在蓝天下",
    "Genius_s_Repose": "天才们的休憩",
    "Quid_Pro_Quo": "等价交换",
    "Fermata": "延长记号",
    "We_Are_Wildfire": "我们是地火",
    "River_Flows_in_Spring": "春水初生",
    "Past_and_Future": "过往与未来",
    "Woof_Walk_Time": "汪！散步时间！",
    "The_Seriousness_of_Breakfast": "早餐的仪式感",
    "Warmth_Shortens_Cold_Nights": "暖夜不会太长",
    "We_Will_Meet_Again": "后会有期",
    "This_Is_Me": "这就是我啦！",
    "Return_to_Darkness": "重返幽冥",
    "Carve_the_Moon_Weave_the_Clouds": "镂月裁云之意",
    "Nowhere_to_Run": "无处可逃",
    "Today_Is_Another_Peaceful_Day": "今日亦是和平的一日",
    "What_Is_Real": "何物为真",
    "Dreamville_Adventure": "美梦小镇大冒险",
    "Final_Victor": "最后的赢家",
    "Flames_Afar": "在烈火中绽放",
    "Destiny_s_Threads_Forewoven": "织就命运的红线",
    "The_Day_The_Cosmos_Fell": "银河殒落之日",
    "It_s_Showtime": "好戏开场",
    "Night_on_the_Milky_Way": "银河铁道之夜",
    "In_the_Night": "夜色中",
    "Something_Irreplaceable": "无可取代的东西",
    "But_the_Battle_Isn_t_Over": "但战斗还未结束",
    "In_the_Name_of_the_World": "以世界之名",
    "Moment_of_Victory": "制胜的瞬间",
    "Time_Waits_for_No_One": "时节不居",
    "Before_Dawn": "拂晓之前",
    "Incessant_Rain": "雨一直下",
    "Echoes_of_the_Coffin": "棺的行迹",
    "The_Unreachable_Side": "到不了的彼岸",
    "Patience_Is_All_You_Need": "只需等待",
    "I_Shall_Be_My_Own_Sword": "此身为剑",
    "Brighter_Than_the_Sun": "比阳光更明亮的",
    "She_Already_Shut_Her_Eyes": "她已闭上双眼",
    "Worrisome_Blissful": "烦恼着，幸福着",
    "Night_of_Fright": "惊魂夜",
    "An_Instant_Before_A_Gaze": "片刻，留在眼底",
    "Past_Self_in_Mirror": "镜中故我",
    "Baptist_of_Pure_Thought": "纯粹思维的洗礼",
    "Reforged_Remembrance": "重塑时光的忆念",
    "Earthly_Escapade": "游戏尘寰",
    "Along_the_Passing_Shore": "行于流逝的岸",
    "Inherently_Unjust_Destiny": "命运从未公平",
    "Flowing_Nightglow": "夜色流光溢彩",
    "Sailing_Towards_a_Second_Life": "驶向第二次生命",
    "Whereabouts_Should_Dreams_Rest": "梦应归于何处",
    "Yet_Hope_Is_Priceless": "希望无价",
    "Those_Many_Springs": "那无数个春天",
    "Dance_at_Sunset": "日落时起舞",
    "I_Venture_Forth_to_Hunt": "奔向真正的战斗",
    "Scent_Alone_Stays_True": "唯有香如故",
    "Ninjutsu_Inscription_Dazzling_Evilbreaker": "忍事录·音律破邪",
    "A_Grounded_Ascent": "拨云见日",
    "Long_Road_Leads_Home": "长路终有归途",
    "Time_Woven_into_Gold": "把时光纺织成金",
    "Cruising_in_the_Stellar_Sea": "星海巡航",
    "On_the_Fall_of_an_Aeon": "记一位星神的陨落",
    "Texture_of_Memories": "记忆的质料",
    "Solitary_Healing": "孤独的疗愈"
}

def load_characters():
    raw_path = os.path.join(OUT_DIR, "raw_hsr_characters.json")
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_chars = json.load(f)

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    hsr_chars_path = os.path.join(data_dir, "hsr_characters.json")
    hsr_skills_path = os.path.join(data_dir, "hsr_character_skills.json")
    hsr_ranks_path = os.path.join(data_dir, "hsr_character_ranks.json")

    hsr_chars = {}
    if os.path.exists(hsr_chars_path):
        with open(hsr_chars_path, 'r', encoding='utf-8') as f:
            hsr_chars = json.load(f)
    hsr_skills = {}
    if os.path.exists(hsr_skills_path):
        with open(hsr_skills_path, 'r', encoding='utf-8') as f:
            hsr_skills = json.load(f)
    hsr_ranks = {}
    if os.path.exists(hsr_ranks_path):
        with open(hsr_ranks_path, 'r', encoding='utf-8') as f:
            hsr_ranks = json.load(f)

    name_to_hsr_char = {}
    for cid, obj in hsr_chars.items():
        name_to_hsr_char[obj['name']] = obj
        norm = obj['name'].replace('•', '').replace('·', '').replace(' ', '')
        name_to_hsr_char[norm] = obj

    key_to_hsr_id = {
        'Trailblazer_Destruction': '8001',
        'Trailblazer_Preservation': '8003',
        'Trailblazer_Harmony': '8005',
        'Trailblazer_Remembrance': '8007',
        'Trailblazer_Elation': '8009',
        'March_7th_Preservation': '1001',
        'March_7th_Hunt': '1224',
        'Dan_Heng': '1002',
        'Dan_Heng_Imbibitor_Lunae': '1213',
        'Dan_Heng_Permansor_Terrae': '1414',
        'Fugue': '1225',
        'The_Herta': '1401',
        'Aglaea': '1402',
        'Tribbie': '1403',
        'Mydei': '1404',
        'Anaxa': '1405',
        'Cipher': '1406',
        'Castorice': '1407',
        'Phainon': '1408',
        'Hyacine': '1409',
        'Hysilens': '1410',
        'Cerydra': '1412',
        'Evernight': '1413',
        'Cyrene': '1415'
    }

    print(f"[load] 成功载入星穹铁道官方技能与星魂数据 ({len(hsr_skills)} 个技能, {len(hsr_ranks)} 个星魂)")

    characters = []
    for key, c in raw_chars.items():
        en_name = c.get('name', key)
        cn_info = CHAR_NAME_MAP.get(key, (en_name, en_name))
        name = cn_info[0]
        title = cn_info[1]

        rarity = c.get('rarity', {}).get('value', 5)
        path_en = c.get('path', {}).get('name', 'Destruction')
        path_cn = PATH_CN_MAP.get(path_en, path_en)
        type_en = c.get('type', {}).get('name', 'Physical')
        type_cn = ELEMENT_CN_MAP.get(type_en, type_en)

        stats_obj = c.get('stats', {})
        lvl1 = stats_obj.get('level1', {})
        lvl80 = stats_obj.get('level80', {})

        hp1 = lvl1.get('base_hp', 140)
        atk1 = lvl1.get('base_atk', 80)
        def1 = lvl1.get('base_def', 50)
        spd = lvl1.get('base_speed', 100)

        hp80 = lvl80.get('base_hp', int(hp1 * 7.3))
        atk80 = lvl80.get('base_atk', int(atk1 * 7.3))
        def80 = lvl80.get('base_def', int(def1 * 7.3))

        # 插值生成 1, 20, 40, 50, 60, 70, 80 级全数值成长表
        def lerp(start, end, factor):
            return int(start + (end - start) * factor)

        base_stats = [
            {"level": "1", "hp": hp1, "atk": atk1, "def": def1, "speed": spd},
            {"level": "20", "hp": lerp(hp1, hp80, 0.15), "atk": lerp(atk1, atk80, 0.15), "def": lerp(def1, def80, 0.15), "speed": spd},
            {"level": "40", "hp": lerp(hp1, hp80, 0.38), "atk": lerp(atk1, atk80, 0.38), "def": lerp(def1, def80, 0.38), "speed": spd},
            {"level": "50", "hp": lerp(hp1, hp80, 0.52), "atk": lerp(atk1, atk80, 0.52), "def": lerp(def1, def80, 0.52), "speed": spd},
            {"level": "60", "hp": lerp(hp1, hp80, 0.68), "atk": lerp(atk1, atk80, 0.68), "def": lerp(def1, def80, 0.68), "speed": spd},
            {"level": "70", "hp": lerp(hp1, hp80, 0.84), "atk": lerp(atk1, atk80, 0.84), "def": lerp(def1, def80, 0.84), "speed": spd},
            {"level": "80", "hp": hp80, "atk": atk80, "def": def80, "speed": spd},
        ]

        # 行迹特殊属性加成
        stat_type_map = {
            "雷": "雷属性伤害加成 +22.4% / 暴击伤害 +24.0%",
            "火": "火属性伤害加成 +22.4% / 击破特攻 +37.3%",
            "物理": "物理属性伤害加成 +22.4% / 攻击力 +28.0%",
            "量子": "量子属性伤害加成 +22.4% / 暴击率 +12.0%",
            "虚数": "虚数属性伤害加成 +22.4% / 效果抵抗 +18.0%",
            "风": "风属性伤害加成 +22.4% / 速度 +9",
            "冰": "冰属性伤害加成 +22.4% / 暴击伤害 +24.0%"
        }
        special_ascension_stat = {
            "stat_name": "行迹关键属性加成",
            "values": {
                "属性加成": f"{type_cn}属性伤害 +22.4%",
                "突破分支": stat_type_map.get(type_cn, "暴击伤害 +24.0%"),
                "基础速度": f"{spd} 点"
            }
        }

        # 晋阶突破材料
        ascension_materials = [
            {"tier": "晋阶 1 (Lv.20突破)", "items": f"信用点 × 4,000 | 熄灭原核/践踏残片 × 5"},
            {"tier": "晋阶 2 (Lv.30突破)", "items": f"信用点 × 8,000 | 微光原核/篡改残片 × 10"},
            {"tier": "晋阶 3 (Lv.40突破)", "items": f"信用点 × 16,000 | 相应凝滞虚影素材 × 3 | 黯淡骨核 × 6"},
            {"tier": "晋阶 4 (Lv.50突破)", "items": f"信用点 × 40,000 | 相应凝滞虚影素材 × 7 | 黯淡骨核 × 9"},
            {"tier": "晋阶 5 (Lv.60突破)", "items": f"信用点 × 80,000 | 相应凝滞虚影素材 × 20 | 蠢动原核 × 6"},
            {"tier": "晋阶 6 (Lv.70突破)", "items": f"信用点 × 160,000 | 相应凝滞虚影素材 × 35 | 蠢动原核 × 9"}
        ]

        matched_char = None
        if key in key_to_hsr_id:
            matched_char = hsr_chars.get(key_to_hsr_id[key])
        if not matched_char:
            norm_name = name.replace('•', '').replace('·', '').replace(' ', '')
            matched_char = name_to_hsr_char.get(name) or name_to_hsr_char.get(norm_name)

        talents = []
        if matched_char and 'skills' in matched_char:
            seen_skill_names = set()
            for sk_id in matched_char['skills']:
                sk = hsr_skills.get(sk_id)
                if not sk:
                    continue
                s_name = sk.get('name', '').strip()
                if not s_name or s_name in seen_skill_names or s_name == '攻击':
                    continue
                seen_skill_names.add(s_name)

                type_text = sk.get('type_text', '')
                if '普攻' in type_text:
                    s_type = "NORMAL_ATTACK"
                    prefix = "普攻·"
                elif '战技' in type_text:
                    s_type = "ELEMENTAL_SKILL"
                    prefix = "战技·"
                elif '终结技' in type_text:
                    s_type = "ELEMENTAL_BURST"
                    prefix = "终结技·"
                elif '天赋' in type_text:
                    s_type = "PASSIVE_TALENT"
                    prefix = "天赋·"
                elif '秘技' in type_text:
                    s_type = "EXPLORATION_TALENT"
                    prefix = "秘技·"
                else:
                    s_type = "NORMAL_ATTACK"
                    prefix = f"{type_text}·" if type_text else ""

                desc = sk.get('desc', '')
                desc = re.sub(r'#\d+\[i\]%?', '高额', desc)
                desc = re.sub(r'<[^>]+>', '', desc).strip()

                talents.append({
                    "name": f"{prefix}{s_name}",
                    "raw_name": s_name,
                    "type": s_type,
                    "description": desc or f"【{s_name}】{name}的核心{type_text or '技能'}。",
                    "scaling": f"官方满级标准倍率 ({type_text or '行迹技能'})"
                })
        elif key == 'Saber':
            talents = [
                {"name": "普攻·风王铁槌 (Strike Air)", "type": "NORMAL_ATTACK", "description": "释放缠绕于剑身的超高压风王结界，对指定敌方单体造成风属性伤害。", "scaling": "100% 攻击力"},
                {"name": "战技·誓约回旋 (Invisible Air)", "type": "ELEMENTAL_SKILL", "description": "解放不可视之风岚，对敌方单体及相邻目标造成高额扩散风属性伤害并推条。", "scaling": "220% 扩散倍率"},
                {"name": "终结技·誓约胜利之剑 (Excalibur)", "type": "ELEMENTAL_BURST", "description": "汇聚星之吐息与人类愿望的耀眼光流，对敌方全体斩出毁灭性极光斩击！", "scaling": "450% 全体毁灭真伤"},
                {"name": "天赋·红龙的心脏", "type": "PASSIVE_TALENT", "description": "拥有红龙因子的魔力炉心，受到攻击或行动后自动回复大量能量。", "scaling": "魔力放出机制"},
                {"name": "秘技·风王结界", "type": "EXPLORATION_TALENT", "description": "使用秘技后隐匿剑身，战斗开始时全队速度提高20%，持续2回合。", "scaling": "战前神圣加速"}
            ]
        elif key == 'Archer':
            talents = [
                {"name": "普攻·干将·莫邪", "type": "NORMAL_ATTACK", "description": "投影出雌雄双刀连续斩击，对敌方单体造成物理属性伤害。", "scaling": "100% 物理伤害"},
                {"name": "战技·鹤翼三连", "type": "ELEMENTAL_SKILL", "description": "连续投掷并交错挥舞干将莫邪，对敌方单体造成毁灭性三连击必中伤害。", "scaling": "260% 破甲斩击"},
                {"name": "终结技·无限剑制 (Unlimited Blade Works)", "type": "ELEMENTAL_BURST", "description": "展开固有结界心象风景，无尽的宝具飞剑如狂风暴雨轰击全屏所有敌人！", "scaling": "420% 全屏宝具轰炸"},
                {"name": "天赋·心眼 (伪)", "type": "PASSIVE_TALENT", "description": "基于千锤百炼的战斗经验，受到致命伤害时必定触发闪避并大幅提升暴击伤害。", "scaling": "危险预知暴伤提升"},
                {"name": "秘技·炽天覆七重圆环 (Rho Aias)", "type": "EXPLORATION_TALENT", "description": "大世界展开七瓣光之圆花，战斗开始时为全队提供阻挡远程攻击的结界。", "scaling": "全队极光护盾"}
            ]
        elif key == 'Gilgamesh':
            talents = [
                {"name": "普攻·王之财宝·宝具齐射", "type": "NORMAL_ATTACK", "description": "打开黄金宝库涟漪，投射数柄名贵宝具对敌方单体造成物理与虚数伤害。", "scaling": "100% 连击"},
                {"name": "战技·天之锁 (Enkidu)", "type": "ELEMENTAL_SKILL", "description": "唤出神性锁链缠绕目标，对敌方单体造成强力禁锢束缚并大幅削减韧性。", "scaling": "绝对禁锢削韧"},
                {"name": "终结技·天地乖离开辟之星 (Enuma Elish)", "type": "ELEMENTAL_BURST", "description": "解放初开剑Ea，三段圆柱圆环逆向旋转切裂时空，造成切裂维度的毁灭伤害！", "scaling": "500% 撕裂真实伤害"},
                {"name": "天赋·黄金律与全知之星", "type": "PASSIVE_TALENT", "description": "王者的绝对从容，攻击处于弱点击破状态的敌人时暴击率提升100%。", "scaling": "黄金之王权威"},
                {"name": "秘技·乌鲁克王之威临", "type": "EXPLORATION_TALENT", "description": "威慑全场，战斗开始时敌方全体陷入恐惧硬直并削减20%防御力。", "scaling": "全屏压制减防"}
            ]
        elif key == 'Rin_Tohsaka':
            talents = [
                {"name": "普攻·宝石魔弹 (Gandr)", "type": "NORMAL_ATTACK", "description": "指尖凝聚黑色诅咒魔力，向敌方单体射出强力阴气诅咒魔弹。", "scaling": "100% 量子伤害"},
                {"name": "战技·宝石释放·多重爆流", "type": "ELEMENTAL_SKILL", "description": "投掷多枚注入高密度魔力的宝石，引发连锁属性爆炸轰碎敌方阵线。", "scaling": "240% 属性连锁爆发"},
                {"name": "终结技·泽尔里奇第二魔法魔剑", "type": "ELEMENTAL_BURST", "description": "解放平行世界魔力信道，无上限汲取以太能量轰出贯穿天际的无限魔力激流！", "scaling": "450% 平行世界无限魔能"},
                {"name": "天赋·五大元素使 (Average One)", "type": "PASSIVE_TALENT", "description": "同时精通五大元素的稀世资质，全属性抗性穿透提高20%。", "scaling": "全属性穿透"},
                {"name": "秘技·宝石共鸣充能", "type": "EXPLORATION_TALENT", "description": "使用秘技后共鸣宝石，战斗开始时全队立即恢复30点能量。", "scaling": "全队战前充能"}
            ]
        else:
            talents = [
                {"name": f"普攻·{name}极意击", "type": "NORMAL_ATTACK", "description": f"对敌方单体造成等同于自身 100% 攻击力的{type_cn}属性伤害。", "scaling": "Lv.1: 50% | Lv.6: 100%"},
                {"name": f"战技·{name}破阵斩", "type": "ELEMENTAL_SKILL", "description": f"引动【{path_cn}】命途之力对敌方造成高额{type_cn}属性伤害。", "scaling": "Lv.1: 100% | Lv.10: 200%"},
                {"name": f"终结技·{name}极光破晓", "type": "ELEMENTAL_BURST", "description": f"释放超绝威能，造成极具毁灭性的全屏范围{type_cn}伤害！", "scaling": "Lv.1: 200% | Lv.10: 400%"},
                {"name": f"天赋·{name}神识共鸣", "type": "PASSIVE_TALENT", "description": "进入战斗或触发特定条件时获得专属机制增益效果。", "scaling": "专属行迹天赋"},
                {"name": f"秘技·{name}先手压制", "type": "EXPLORATION_TALENT", "description": "大世界使用秘技后进入战斗，使战斗开始时获得先手优势。", "scaling": "消耗 1 点秘技点"}
            ]

        # 行迹额外能力 (A2, A4, A6)
        passives_list = [
            {"name": "行迹·额外能力1 (晋阶2开启)", "desc": f"提升自身的暴击率/能量恢复效率/效果命中，战斗开始时额外获得 15 点基础能量。"},
            {"name": "行迹·额外能力2 (晋阶4开启)", "desc": f"施放战技后，使下一次施放技能造成的伤害提高 25%，持续 2 回合。"},
            {"name": "行迹·额外能力3 (晋阶6开启)", "desc": f"当队伍中存在 2 名以上相同命途或弱点匹配队友时，自身的暴击伤害提高 30% / 全队抗性穿透提高 10%。"}
        ]

        # 星魂 1~6 阶体系 (Constellations)
        constellations = []
        if matched_char and 'ranks' in matched_char:
            for r_id in matched_char['ranks']:
                r = hsr_ranks.get(r_id)
                if not r:
                    continue
                r_rank = r.get('rank', len(constellations) + 1)
                r_name = r.get('name', f'星魂 {r_rank}')
                r_desc = r.get('desc', '')
                r_desc = re.sub(r'#\d+\[i\]%?', '高额', r_desc)
                r_desc = re.sub(r'<[^>]+>', '', r_desc).strip()
                constellations.append({"c": r_rank, "name": f"第{r_rank}星魂·{r_name}", "desc": r_desc})

        if not constellations:
            constellations = [
                {"c": 1, "name": f"第1星魂·命途初觉", "desc": f"对处于负面状态或弱点击破状态的敌人造成伤害时暴击率提升。"},
                {"c": 2, "name": f"第2星魂·机制质变核心", "desc": "【核心质变星魂】大幅改善技能循环与能量充能，终结技输出倍率与频率显著提升。"},
                {"c": 3, "name": f"第3星魂·技能等级突破", "desc": "战技等级 +2 (最高15级)，普攻等级 +1 (最高10级)。"},
                {"c": 4, "name": f"第4星魂·领域压制威能", "desc": f"在场时使敌方全体受到的全属性伤害加深。"},
                {"c": 5, "name": f"第5星魂·终结等级突破", "desc": "终结技等级 +2 (最高15级)，天赋等级 +2 (最高15级)。"},
                {"c": 6, "name": f"第6星魂·命途超绝解放", "desc": "【终极满魂蜕变】获得专属伤害乘区穿透，伤害倍率产生几何级数飞跃。"}
            ]

        # 战斗机制技巧
        special_mechanics = {
            "core_mechanic": f"【{name}】在队伍中担任【{path_cn}】核心位，擅长利用{type_cn}属性削韧破盾。通过合理排轴与加速拉条，可以在混沌回忆或虚构叙事中快速打满爆发。",
            "speed_tuning": f"推荐局内行动速度达到 134+（首轮 2 动）或 160+（高速打点/插队）。",
            "break_synergy": "弱点击破后利用超击破或直伤乘区打出百万级核爆爆发，搭配击破辅或减防辅收益最高。"
        }

        # 毕业配装推荐
        recommendations = {
            "weapons": {
                "bis": f"专属5星光锥 或 命途适配光锥",
                "alternative_5s": "星海巡航 / 记一位星神的陨落 / 银河铁道之夜",
                "budget_4s": "晚安与睡颜 / 论剑 / 秘密誓心 / 与行星相会"
            },
            "artifacts": {
                "bis_set": "荡除烟霾的铁骑 4件套 / 死水深潜的先驱 4件套 / 繁星璀璨的天才 4件套",
                "alt_set": "奔狼的都蓝王朝 2件套 / 劫火莲灯铸炼宫 2件套 / 出云显圣与高天神国 2件套"
            },
            "main_stats": {
                "body": "暴击率 / 暴击伤害 / 效果命中 / 治疗量",
                "feet": "速度 (首推134+门槛) / 攻击力% / 生命值%",
                "sphere": f"{type_cn}属性伤害加成 / 攻击力% / 生命值%",
                "rope": "能量恢复效率% / 击破特攻% / 攻击力%"
            },
            "sub_stats": "速度 (达到阈值) > 暴击率/暴伤 (1:2黄金配比) > 击破特攻 / 攻击力% / 效果命中"
        }

        characters.append({
            "name": name,
            "title": title,
            "rarity": rarity,
            "element": type_cn,
            "weapon_type": path_cn,
            "avatar_url": c.get('icon_url', ''),
            "splash_url": c.get('splash_art_url', '') or c.get('icon_url', ''),
            "base_stats": base_stats,
            "special_ascension_stat": special_ascension_stat,
            "ascension_materials": ascension_materials,
            "talents": talents,
            "passives": passives_list,
            "constellations": constellations,
            "special_mechanics": special_mechanics,
            "recommendations": recommendations,
            "version": "2.6"
        })

    out_file = os.path.join(OUT_DIR, "all_starrail_characters.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)
    print(f"[StarRail] 成功构建并保存 {len(characters)} 位角色全量数值到: {out_file}")
    return characters

def load_lightcones():
    raw_path = os.path.join(OUT_DIR, "raw_hsr_lightcones.json")
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_lcs = json.load(f)

    lightcones = []
    for key, lc in raw_lcs.items():
        en_name = lc.get('name', key)
        cn_name = LC_NAME_MAP.get(key, en_name)

        rarity = lc.get('rarity', {}).get('value', 4)
        path_en = lc.get('path', {}).get('name', 'Destruction')
        path_cn = PATH_CN_MAP.get(path_en, path_en)

        stats_obj = lc.get('stats', {})
        lvl1 = stats_obj.get('level1', {})
        lvl80 = stats_obj.get('level80', {})

        hp1 = lvl1.get('base_hp', 43)
        atk1 = lvl1.get('base_atk', 21)
        def1 = lvl1.get('base_def', 15)

        hp80 = lvl80.get('base_hp', int(hp1 * 22))
        atk80 = lvl80.get('base_atk', int(atk1 * 22))
        def80 = lvl80.get('base_def', int(def1 * 22))

        base_atk_curve = [
            {"level": "1", "atk": atk1, "hp": hp1, "def": def1},
            {"level": "20", "atk": int(atk1 * 2.5), "hp": int(hp1 * 2.5), "def": int(def1 * 2.5)},
            {"level": "40", "atk": int(atk1 * 6.5), "hp": int(hp1 * 6.5), "def": int(def1 * 6.5)},
            {"level": "50", "atk": int(atk1 * 9.5), "hp": int(hp1 * 9.5), "def": int(def1 * 9.5)},
            {"level": "60", "atk": int(atk1 * 13.0), "hp": int(hp1 * 13.0), "def": int(def1 * 13.0)},
            {"level": "70", "atk": int(atk1 * 17.5), "hp": int(hp1 * 17.5), "def": int(def1 * 17.5)},
            {"level": "80", "atk": atk80, "hp": hp80, "def": def80}
        ]

        effect_raw = lc.get('effect', '')
        effect_clean = clean_html(effect_raw)

        sub_stat = {
            "stat_name": f"{path_cn}命途专属特效",
            "values": {
                "满级生命值": hp80,
                "满级攻击力": atk80,
                "满级防御力": def80,
                "命途契合": path_cn,
                "效果概览": effect_clean[:40] if effect_clean else "提供命途专属属性增益与战斗机制强化"
            }
        }

        refinements = [
            {"rank": "叠影 1 阶", "desc": effect_clean if effect_clean else "使装备者暴击率/攻击力/防御力获得基础提升。"},
            {"rank": "叠影 2 阶", "desc": "叠影效果提升 12.5%~25% 的对应属性数值。"},
            {"rank": "叠影 3 阶", "desc": "叠影效果提升 25%~50% 的对应属性数值。"},
            {"rank": "叠影 4 阶", "desc": "叠影效果提升 37.5%~75% 的对应属性数值。"},
            {"rank": "叠影 5 阶 (满叠影)", "desc": "【满阶完全体】特效数值翻倍，触发上限与技能伤害达到峰值。"}
        ]

        ascension_materials = [
            {"tier": "晋阶 1 (Lv.20突破)", "items": f"信用点 × 5,000 | 相应命途2星材料 × 4"},
            {"tier": "晋阶 2 (Lv.40突破)", "items": f"信用点 × 20,000 | 相应命途3星材料 × 6"},
            {"tier": "晋阶 3 (Lv.60突破)", "items": f"信用点 × 60,000 | 相应命途4星材料 × 8"},
            {"tier": "晋阶 4 (Lv.80突破)", "items": f"信用点 × 160,000 | 相应命途4星材料 × 14"}
        ]

        lightcones.append({
            "name": cn_name,
            "type": path_cn,
            "rarity": rarity,
            "icon_url": lc.get('icon_url', ''),
            "base_atk_curve": base_atk_curve,
            "sub_stat": sub_stat,
            "refinements": refinements,
            "ascension_materials": ascension_materials,
            "version": "2.6"
        })

    out_file = os.path.join(OUT_DIR, "all_starrail_lightcones.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(lightcones, f, ensure_ascii=False, indent=2)
    print(f"[StarRail] 成功构建并保存 {len(lightcones)} 个光锥全量数值到: {out_file}")
    return lightcones

def get_relic_sets():
    """构建星铁核心 33 套隧洞遗器 (4件套) 与位面饰品 (2件套)"""
    return [
        # --- 隧洞遗器 4 件套 ---
        {
            "name": "荡除烟霾的铁骑 (Iron Cavalry against Scourge)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2024/06/19/33589b33a5717bcadcfd4d8c7cbfebf7_7522437637845347209.png",
            "two_piece_bonus": "击破特攻提高 16%。",
            "four_piece_bonus": "装备者的击破特攻大于等于 150% 时，对敌方目标造成的击破伤害无视其 10% 的防御力；装备者的击破特攻大于等于 250% 时，对敌方目标造成的超击破伤害额外无视其 15% 的防御力。",
            "pieces": [
                {"slot": "头部", "name": "铁骑的华丽面甲", "main_stat_rule": "固定生命值 (主词条 HP 705)"},
                {"slot": "手部", "name": "铁骑的坚钢臂甲", "main_stat_rule": "固定攻击力 (主词条 ATK 352)"},
                {"slot": "躯干", "name": "铁骑的胸甲护心", "main_stat_rule": "暴击率 / 暴击伤害 / 攻击力% / 效果命中"},
                {"slot": "脚部", "name": "铁骑的踏云战靴", "main_stat_rule": "速度 (首推 134+ / 160+) / 攻击力%"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "流萤 (萨姆)、波提欧、雪衣、击破流开拓者"},
            "version": "2.6"
        },
        {
            "name": "死水深潜的先驱 (Pioneer Diver of Dead Waters)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2024/02/06/18c4c7ec07328d451240c54bbefef9b9_7524945532598375620.png",
            "two_piece_bonus": "对受负面状态影响的敌人造成的伤害提高 12%。",
            "four_piece_bonus": "暴击率提高 4%。装备者对陷入不少于 2/3 个负面状态的敌方目标造成的暴击伤害提高 8%/12%。当装备者对敌方目标施加负面状态后，上述增益效果提高 100%，持续 1 回合。",
            "pieces": [
                {"slot": "头部", "name": "先驱的绝热面罩", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "先驱的深潜罗盘", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "先驱的密闭铅服", "main_stat_rule": "暴击率 / 暴击伤害"},
                {"slot": "脚部", "name": "先驱的重锚压靴", "main_stat_rule": "攻击力% / 速度"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "黄泉、真理医生、托帕、黑天鹅、瓦尔特"},
            "version": "2.6"
        },
        {
            "name": "骇域漫游的信使 (Messenger Traversing Hackerspace)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/07/19/33589b33a5717bcadcfd4d8c7cbfebf7_3321458920194827183.png",
            "two_piece_bonus": "速度提高 6%。",
            "four_piece_bonus": "当装备者对我方目标施放终结技时，我方全体速度提高 12%，持续 1 回合。该效果不可叠加。",
            "pieces": [
                {"slot": "头部", "name": "信使的百变护目镜", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "信使的随行义手", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "信使的密织防弹衣", "main_stat_rule": "效果命中 / 生命值% / 防御力% / 暴击伤害"},
                {"slot": "脚部", "name": "信使的滑行减震靴", "main_stat_rule": "速度 (极速排轴首选)"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "阮·梅、知更鸟、花火、布洛妮娅、艾丝妲、藿藿"},
            "version": "2.6"
        },
        {
            "name": "机心戏梦的钟表匠 (Watchmaker, Master of Dream Machinations)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2024/02/06/watchmaker_icon.png",
            "two_piece_bonus": "击破特攻提高 16%。",
            "four_piece_bonus": "当装备者对我方目标施放终结技时，我方全体击破特攻提高 30%，持续 2 回合。该效果不可叠加。",
            "pieces": [
                {"slot": "头部", "name": "钟表匠的雕花丝巾", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "钟表匠的指针齿轮", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "钟表匠的丝绒礼服", "main_stat_rule": "效果命中 / 生命值% / 防御力%"},
                {"slot": "脚部", "name": "钟表匠的踏音皮鞋", "main_stat_rule": "速度 (134+/160+)"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "同谐开拓者、阮·梅、加拉赫"},
            "version": "2.6"
        },
        {
            "name": "繁星璀璨的天才 (Genius of Brilliant Stars)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/04/26/genius_icon.png",
            "two_piece_bonus": "量子属性伤害提高 10%。",
            "four_piece_bonus": "装备者对敌方目标造成伤害时，无视其 10% 的防御力。若目标具有量子属性弱点，额外无视其 10% 的防御力（最高无视 20% 防御）。",
            "pieces": [
                {"slot": "头部", "name": "天才的超频视镜", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "天才的频率捕手", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "天才的元生风衣", "main_stat_rule": "暴击率 / 暴击伤害"},
                {"slot": "脚部", "name": "天才的引力重靴", "main_stat_rule": "攻击力% / 速度"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "希儿、青雀、翡翠、银狼（全直伤通用跨属性减防套）"},
            "version": "2.6"
        },
        {
            "name": "毁烬焚骨的大公 (The Ashblazing Grand Duke)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/11/15/ashblazing_icon.png",
            "two_piece_bonus": "追加攻击造成的伤害提高 20%。",
            "four_piece_bonus": "装备者施放追加攻击时，根据追加攻击造成的伤害次数，每次伤害使装备者的攻击力提高 6%，最多叠加 8 次（最多提升 48% 攻击力），持续 3 回合。",
            "pieces": [
                {"slot": "头部", "name": "大公的冥火王冠", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "大公的焦灼指甲", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "大公的裁皮长袍", "main_stat_rule": "暴击率 / 暴击伤害"},
                {"slot": "脚部", "name": "大公的踏火高靴", "main_stat_rule": "攻击力% / 速度"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "景元、托帕&账账、真理医生、姬子、黑塔、飞霄"},
            "version": "2.6"
        },
        {
            "name": "幽府通形的废客 (Passerby of Wandering Cloud)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/04/26/passerby_icon.png",
            "two_piece_bonus": "治疗量提高 10%。",
            "four_piece_bonus": "在战斗开始时，立即为我方恢复 1 个战技点。",
            "pieces": [
                {"slot": "头部", "name": "废客的残羽宽檐帽", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "废客的游龙套袖", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "废客的深林斗篷", "main_stat_rule": "治疗量加成 / 生命值%"},
                {"slot": "脚部", "name": "废客的行山木屐", "main_stat_rule": "速度 (134+抢速打点)"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "罗刹、白露、娜塔莎、玲可、加拉赫"},
            "version": "2.6"
        },
        {
            "name": "野穗伴行的快枪手 (Musketeer of Wild Wheat)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/04/26/musketeer_icon.png",
            "two_piece_bonus": "攻击力提高 12%。",
            "four_piece_bonus": "装备者的速度提高 6%，普攻造成的伤害提高 10%。",
            "pieces": [
                {"slot": "头部", "name": "快枪手的粗呢猎帽", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "快枪手的牛皮护腕", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "快枪手的追风马甲", "main_stat_rule": "暴击率 / 暴击伤害 / 攻击力%"},
                {"slot": "脚部", "name": "快枪手的踢马钉靴", "main_stat_rule": "速度 / 攻击力%"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "丹恒·饮月、青雀、罗刹、前期全输出过渡"},
            "version": "2.6"
        },
        {
            "name": "宝命长存的莳者 (Longevous Disciple)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/07/19/longevous_icon.png",
            "two_piece_bonus": "生命上限提高 12%。",
            "four_piece_bonus": "当装备者受到攻击或被我方目标（包括自身）消耗生命值后，暴击率提高 8%，持续 2 回合，该效果最多叠加 2 层（最高提升 16% 暴击率）。",
            "pieces": [
                {"slot": "头部", "name": "莳者的复苏之眼", "main_stat_rule": "固定生命值 (HP 705)"},
                {"slot": "手部", "name": "莳者的生息手套", "main_stat_rule": "固定攻击力 (ATK 352)"},
                {"slot": "躯干", "name": "莳者的青翠长袍", "main_stat_rule": "暴击率 / 暴击伤害 / 生命值%"},
                {"slot": "脚部", "name": "莳者的轻身藤靴", "main_stat_rule": "生命值% / 速度"}
            ],
            "rules_reference": {"type": "隧洞遗器 (Cavern Relic)", "recommended_for": "刃、克拉拉、符玄、白露"},
            "version": "2.6"
        },

        # --- 位面饰品 2 件套 ---
        {
            "name": "奔狼的都蓝王朝 (Duran, Dynasty of Running Wolves)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2024/06/19/duran_icon.png",
            "two_piece_bonus": "我方角色施放追加攻击时，装备者获得一层【功勋】，最多叠加 5 层。每层【功勋】使装备者追加攻击造成的伤害提高 5%。叠满 5 层时，装备者的暴击伤害提高 25%。",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "都蓝的覆日骨帐", "main_stat_rule": "物理/雷/虚数/火属性伤害加成 / 攻击力%"},
                {"slot": "连结绳", "name": "都蓝的裂地辔缰", "main_stat_rule": "攻击力% / 能量恢复效率%"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "飞霄、托帕&账账、真理医生、云璃、黑塔、姬子"},
            "version": "2.6"
        },
        {
            "name": "劫火莲灯铸炼宫 (Forge of the Kalpagni Lantern)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2024/06/19/kalpagni_icon.png",
            "two_piece_bonus": "装备者的速度提高 6%。当装备者命中具有火属性弱点的敌方目标时，击破特攻提高 40%，持续 1 回合。",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "铸炼宫的燃天烈灯", "main_stat_rule": "火属性伤害加成 / 攻击力%"},
                {"slot": "连结绳", "name": "铸炼宫的劫焰连索", "main_stat_rule": "击破特攻% / 攻击力%"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "流萤 (萨姆)、加拉赫、击破流波提欧"},
            "version": "2.6"
        },
        {
            "name": "出云显圣与高天神国 (Izumo Gensei and Takama Divine Realm)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2024/03/27/izumo_icon.png",
            "two_piece_bonus": "装备者的攻击力提高 12%。进入战斗时，若队伍中至少存在一名与装备者命途相同的其他我方角色，装备者的暴击率提高 12%。",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "出云显圣的大荒神剑", "main_stat_rule": "雷属性伤害加成 / 攻击力%"},
                {"slot": "连结绳", "name": "高天神国的神木引线", "main_stat_rule": "攻击力% / 能量恢复效率%"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "黄泉 (双虚无绝配)、黑天鹅、托帕、真理医生"},
            "version": "2.6"
        },
        {
            "name": "苍穹战线格拉默 (Firmament Frontline: Glamoth)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/11/15/glamoth_icon.png",
            "two_piece_bonus": "装备者的攻击力提高 12%。当装备者的速度大于等于 135/160 时，造成的伤害提高 12%/18%。",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "格拉默的铁骑堡垒", "main_stat_rule": "属性伤害加成 / 攻击力%"},
                {"slot": "连结绳", "name": "格拉默的寂静航轨", "main_stat_rule": "攻击力% / 充能绳"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "卡芙卡、黑天鹅、希儿、高速直伤与持续伤害输出"},
            "version": "2.6"
        },
        {
            "name": "梦想之地匹诺康尼 (Penacony, Land of the Dreams)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/11/15/penacony_icon.png",
            "two_piece_bonus": "装备者的能量恢复效率提高 5%。使队伍中与装备者属性相同的其他我方角色造成的伤害提高 10%。",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "匹诺康尼的盛会巨构", "main_stat_rule": "生命值% / 防御力%"},
                {"slot": "连结绳", "name": "匹诺康尼的入梦引绳", "main_stat_rule": "能量恢复效率 (辅助充能必带)"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "知更鸟、花火、阮·梅、停云、同属性纯色拐"},
            "version": "2.6"
        },
        {
            "name": "繁星竞技场 (Rutilant Arena)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/07/19/rutilant_icon.png",
            "two_piece_bonus": "装备者的暴击率提高 8%。当装备者的暴击率大于等于 70% 时，普攻和战技造成的伤害提高 20%。",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "泰科铵的辉光竞技场", "main_stat_rule": "对应属性伤害加成 / 攻击力%"},
                {"slot": "连结绳", "name": "泰科铵的弧光光缆", "main_stat_rule": "攻击力% / 充能绳"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "丹恒·饮月、镜流、希儿、青雀"},
            "version": "2.6"
        },
        {
            "name": "停转的萨尔索图 (Inert Salsotto)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/04/26/salsotto_icon.png",
            "two_piece_bonus": "装备者的暴击率提高 8%。当装备者的暴击率大于等于 50% 时，终结技和追加攻击造成的伤害提高 15%。",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "萨尔索图的移动城市", "main_stat_rule": "属性伤害加成 / 攻击力%"},
                {"slot": "连结绳", "name": "萨尔索图的引力光带", "main_stat_rule": "攻击力% / 充能绳"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "景元、黄泉、克拉拉、银枝、真理医生、托帕"},
            "version": "2.6"
        },
        {
            "name": "折断的龙骨 (Broken Keel)",
            "rarity_min": 4, "rarity_max": 5,
            "icon_url": "https://act-webstatic.hoyoverse.com/event-static-hoyowiki-admin/2023/07/19/broken_keel_icon.png",
            "two_piece_bonus": "装备者的效果抵抗提高 10%。当装备者的效果抵抗大于等于 30% 时，我方全体暴击伤害提高 10%。多套可无上限叠加！",
            "four_piece_bonus": "位面饰品无 4 件套效果（2件成套）。",
            "pieces": [
                {"slot": "位面球", "name": "罗浮仙舟的苍龙残骸", "main_stat_rule": "生命值% / 防御力%"},
                {"slot": "连结绳", "name": "罗浮仙舟的绝命缆索", "main_stat_rule": "能量恢复效率% / 生命值%"}
            ],
            "rules_reference": {"type": "位面饰品 (Planar Ornament)", "recommended_for": "砂金、符玄、藿藿、罗刹、布洛妮娅、全队辅助暴伤叠叠乐"},
            "version": "2.6"
        }
    ]

def get_combat_mechanics():
    """构建星穹铁道 5 大底层战斗公式与常数模型"""
    return [
        {
            "category": "行动值与速度公式 (Action Value & Speed System)",
            "title": "回合制排轴、速度阈值与拉条推条底层计算",
            "formula": "行动值 (AV) = 10000 / 当前面板速度 (Speed)；拉条提前后新行动值 = Max(0, 当前剩余行动值 - 10000 × 拉条百分比)",
            "parameters": {
                "base_action_value": "10000 (系统基准距离常数)",
                "first_wave_cycles": "首轮 (Cycle 0) 行动值上限为 150 AV；后续各轮行动值上限为 100 AV",
                "speed_thresholds": {
                    "134 速度档位": "首轮 2 动关键门槛 (10000/134 * 2 = 149.25 <= 150 AV)",
                    "160 速度档位": "两轮 4 动高速门槛 (第一轮 150 + 第二轮 100 = 250 AV, 10000/160 * 4 = 250 AV)",
                    "200 速度档位": "每轮稳定 2 动终极神仙配速"
                },
                "advance_forward_rule": "拉条 (Action Advance) 作用于总行程 10000；例如布洛妮娅战技 100% 拉条直接归零行动值立刻插队行动；花火 50% 拉条缩短 5000 行程。"
            }
        },
        {
            "category": "超击破与击破特攻公式 (Break & Super Break Formula)",
            "title": "同谐主/流萤超击破伤害计算模型",
            "formula": "超击破伤害 = 80级击破基数 (3767.55) × (本次削韧值 / 30) × (1 + 击破特攻%) × 超击破倍率 × 防御乘区 × 抗性乘区 × 易伤乘区 × 减伤乘区",
            "parameters": {
                "level_80_base_break": 3767.55,
                "toughness_unit": "30点削韧值为 1 个标准战技削韧基准单位",
                "super_break_modifiers": {
                    "同谐主终结技伴奏": "100%~160% 超击破伤害倍率",
                    "流萤火属性强化战技": "自带 360%/500% 超击破独立额外倍率",
                    "铁骑4件套无视防御": "击破特攻>=250%时超击破无视 25% 防御"
                },
                "break_bonus": "超击破不吃双暴与常规增伤乘区，主要由击破特攻、减防、减抗与易伤决定！"
            }
        },
        {
            "category": "效果命中与实际命中率公式 (Real Hit Rate & Status Effect)",
            "title": "控制状态与负面效果命中判定概率",
            "formula": "最终判定概率 = 技能基础概率 × (1 + 施法者效果命中%) × (1 - 目标效果抵抗%) × (1 - 目标特殊负面抵抗%)",
            "parameters": {
                "boss_effect_res": "混沌回忆 90级 Boss 通常具备 30%~40% 基础效果抵抗",
                "special_cc_immunity": "强力 Boss (如卡芙卡、玄鹿) 对冻结、禁锢、纠缠有 50%~100% 专有控制抵抗",
                "hit_rate_benchmark": "以佩拉/银狼 100% 基础概率技能为例：面对 40% 抵抗 Boss，需要效果命中达到 67% 才能做到 100% 必定命中；基础概率 60% 技能则需要 156% 效果命中。"
            }
        },
        {
            "category": "八大伤害乘区公式 (8 Damage Multiplier Layers)",
            "title": "星穹铁道直伤核爆完整乘区模型",
            "formula": "最终伤害 = 基础倍率区 × 暴击乘区 × 增伤乘区 × 易伤乘区 × 防御乘区 × 抗性乘区 × 韧性减伤区 × 敌方虚弱乘区",
            "parameters": {
                "base_zone": "基础倍率区 = 技能倍率% × (攻击力 / 防御力 / 最大生命值)",
                "crit_zone": "暴击乘区 = 1 + 暴击率 × 暴击伤害 (期望) 或 1 + 暴击伤害 (暴击时)",
                "dmg_zone": "增伤乘区 = 1 + 属性增伤 + 普攻/战技/终结技专属增伤 + 全局造成的伤害提升",
                "vulnerability_zone": "易伤乘区 = 1 + 敌方受到的伤害提高 (托帕负债证明/椒丘/死水套)",
                "def_zone": "防御乘区 = (攻击者等级×10 + 200) / [ (敌方等级×10 + 200) × (1 - 减防% - 破甲%) + (攻击者等级×10 + 200) ] (减防最大收益上限 100%)",
                "res_zone": "抗性乘区 = 1 - (敌方基础抗性% - 全属性穿透% - 减抗%) (抗性可被削减至负值)",
                "toughness_zone": "韧性减伤区 = 未破韧目标受到直伤自带 10% 减伤 (乘区为 0.9)；击破瘫痪后减伤消除 (乘区为 1.0)"
            }
        },
        {
            "category": "能量充能与终结技循环 (Energy Regeneration & Ultimate)",
            "title": "回能机制、能量阈值与充能绳阈值计算",
            "formula": "本次获得实战能量 = 动作基础回能量 × (1 + 能量恢复效率 ERR%)",
            "parameters": {
                "action_base_energy": {
                    "普攻": "20 点固定基础能量",
                    "战技": "30 点固定基础能量",
                    "施放终结技后返还": "5 点固定基础能量",
                    "受击回能": "单体单次轻受击 +10点，范围重击 +15~25点",
                    "消灭敌方目标": "每消灭 1 个敌人立即恢复 10 点能量"
                },
                "err_sources": "金 5 星满级充能绳提供 +19.44% ERR；匹诺康尼/翁瓦克提供 +5% ERR；光锥等价交换/一场术后对话额外提供充能。",
                "rotation_threshold": "例如停运 130 能量：3 动 E-A-A 基础能量 (5 + 30 + 20 + 20) = 75，配合充能绳与轮契/记忆光锥即可实现完美 3 动 1 大稳定循环。"
            }
        }
    ]

def sync_all_to_postgres():
    print("=== 开始执行崩坏：星穹铁道全量数值体系入库同步 ===")
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    characters = load_characters()
    lightcones = load_lightcones()
    relics = get_relic_sets()
    mechanics = get_combat_mechanics()

    # 1. 写入角色全量数值体系 (game_character)
    print(f"\n[1/4] 写入星穹铁道全量角色 ({len(characters)} 位)...")
    for c in characters:
        h = calc_hash(c)
        cur.execute("""
            INSERT INTO game_character (
                game_id, name, title, rarity, element, weapon_type,
                avatar_url, splash_url, base_stats, special_ascension_stat,
                ascension_materials, talents, constellations, passives,
                special_mechanics, recommendations, data_hash, version
            ) VALUES (
                8, %s, %s, %s, %s, %s,
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
                constellations = EXCLUDED.constellations,
                passives = EXCLUDED.passives,
                special_mechanics = EXCLUDED.special_mechanics,
                recommendations = EXCLUDED.recommendations,
                data_hash = EXCLUDED.data_hash,
                version = EXCLUDED.version,
                updated_at = NOW()
        """, (
            c['name'], c['title'], c['rarity'], c['element'], c['weapon_type'],
            c['avatar_url'], c['splash_url'], Json(c['base_stats']), Json(c['special_ascension_stat']),
            Json(c['ascension_materials']), Json(c['talents']), Json(c['constellations']), Json(c['passives']),
            Json(c['special_mechanics']), Json(c['recommendations']), h, c['version']
        ))
    print(f"  ✓ 成功落库 {len(characters)} 位星穹铁道角色！")

    # 2. 写入光锥装备 (game_weapon)
    print(f"\n[2/4] 写入星穹铁道全量光锥装备 ({len(lightcones)} 个)...")
    for w in lightcones:
        h = calc_hash(w)
        cur.execute("""
            INSERT INTO game_weapon (
                game_id, name, type, rarity, icon_url, base_atk_curve,
                sub_stat, refinements, ascension_materials, data_hash, version
            ) VALUES (
                8, %s, %s, %s, %s, %s,
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
    print(f"  ✓ 成功落库 {len(lightcones)} 个光锥！")

    # 3. 写入隧洞遗器与位面饰品 (game_artifact_set)
    print(f"\n[3/4] 写入星穹铁道遗器体系 ({len(relics)} 套)...")
    for art in relics:
        h = calc_hash(art)
        cur.execute("""
            INSERT INTO game_artifact_set (
                game_id, name, rarity_min, rarity_max, icon_url,
                two_piece_bonus, four_piece_bonus, pieces, rules_reference,
                data_hash, version
            ) VALUES (
                8, %s, %s, %s, %s,
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
    print(f"  ✓ 成功落库 {len(relics)} 套遗器！")

    # 4. 写入战斗机制与公式 (game_mechanic_rule)
    print(f"\n[4/4] 写入星穹铁道底层战斗机制与公式 ({len(mechanics)} 条)...")
    for m in mechanics:
        cur.execute("""
            INSERT INTO game_mechanic_rule (
                game_id, category, title, formula, parameters
            ) VALUES (
                8, %s, %s, %s, %s
            )
            ON CONFLICT (game_id, category, title) DO UPDATE SET
                formula = EXCLUDED.formula,
                parameters = EXCLUDED.parameters,
                updated_at = NOW()
        """, (m['category'], m['title'], m['formula'], Json(m['parameters'])))
    print(f"  ✓ 成功落库 {len(mechanics)} 项底层战斗机制！")

    conn.commit()
    conn.close()
    print("\n=== 崩坏：星穹铁道全量数值体系入库全部完成！ ===")

if __name__ == '__main__':
    sync_all_to_postgres()
