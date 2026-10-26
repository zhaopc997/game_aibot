#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
王者荣耀 132 位英雄腾讯官方真实技能数据采集脚本
数据源: https://pvp.qq.com/web201605/herodetail/{ename}.shtml
"""

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(CURRENT_DIR), 'data')
HEROLIST_PATH = os.path.join(DATA_DIR, 'hok_herolist.json')
OUT_PATH = os.path.join(DATA_DIR, 'hok_real_skills.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Referer': 'https://pvp.qq.com/'
}

def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').strip()
    return text

def fetch_hero_skills(session, hero_info):
    ename = hero_info['ename']
    cname = hero_info.get('cname', str(ename))
    url = f"https://pvp.qq.com/web201605/herodetail/{ename}.shtml"

    for attempt in range(4):
        try:
            resp = session.get(url, headers=HEADERS, timeout=12)
            if resp.status_code == 200:
                resp.encoding = 'gbk'
                html = resp.text

                names = re.findall(r'<p class="skill-name"><b>(.*?)</b><span>(.*?)</span>', html)
                descs = re.findall(r'<p class="skill-desc">(.*?)</p>', html)

                valid_skills = []
                for n, d in zip(names, descs):
                    raw_name = clean_text(n[0])
                    raw_cd = clean_text(n[1])
                    raw_desc = clean_text(d)
                    if raw_name:
                        valid_skills.append({
                            'raw_name': raw_name,
                            'cd': raw_cd,
                            'desc': raw_desc
                        })

                if not valid_skills:
                    return {'ename': ename, 'cname': cname, 'success': False, 'skills': []}

                formatted_skills = []
                skill_count = len(valid_skills)

                for idx, sk in enumerate(valid_skills):
                    raw_name = sk['raw_name']
                    raw_cd = sk['cd'].replace('冷却值：', '').strip()
                    raw_desc = sk['desc']

                    if idx == 0:
                        sk_type = "PASSIVE"
                        prefix = "被动·"
                        scaling = "被动固有特性" if (not raw_cd or raw_cd == '0') else f"冷却: {raw_cd}秒"
                    elif idx == 1:
                        sk_type = "NORMAL_ATTACK"
                        prefix = "一技能·"
                        scaling = f"冷却: {raw_cd}秒" if raw_cd else "核心战技"
                    elif idx == 2:
                        sk_type = "ELEMENTAL_SKILL"
                        prefix = "二技能·"
                        scaling = f"冷却: {raw_cd}秒" if raw_cd else "核心机动/防御"
                    elif idx == 3 and skill_count == 4:
                        sk_type = "ELEMENTAL_BURST"
                        prefix = "三技能·"
                        scaling = f"冷却: {raw_cd}秒 (终极大招)" if raw_cd else "终极爆发"
                    elif idx == 3 and skill_count > 4:
                        sk_type = "ELEMENTAL_SKILL"
                        prefix = "三技能·"
                        scaling = f"冷却: {raw_cd}秒" if raw_cd else "进阶战技"
                    else:
                        sk_type = "ELEMENTAL_BURST"
                        prefix = "四技能·"
                        scaling = f"冷却: {raw_cd}秒 (终极大招)" if raw_cd else "终极大招"

                    formatted_skills.append({
                        'name': f"{prefix}{raw_name}",
                        'raw_name': raw_name,
                        'type': sk_type,
                        'description': raw_desc,
                        'scaling': scaling
                    })

                return {'ename': ename, 'cname': cname, 'success': True, 'skills': formatted_skills}
        except Exception as e:
            time.sleep(0.5 * (attempt + 1))

    return {'ename': ename, 'cname': cname, 'success': False, 'skills': []}

def main():
    if not os.path.exists(HEROLIST_PATH):
        print(f"Error: {HEROLIST_PATH} not found!")
        sys.exit(1)

    with open(HEROLIST_PATH, 'r', encoding='utf-8') as f:
        herolist = json.load(f)

    print(f"Loaded {len(herolist)} heroes from {HEROLIST_PATH}. Fetching real skills...")
    session = create_session()

    results = {}
    success_count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_hero = {executor.submit(fetch_hero_skills, session, h): h for h in herolist}
        for future in as_completed(future_to_hero):
            h = future_to_hero[future]
            try:
                res = future.result()
                if res['success']:
                    results[res['cname']] = res
                    results[str(res['ename'])] = res
                    success_count += 1
                    print(f"  ✓ [{res['cname']}] 抓取成功 ({len(res['skills'])} 技能): {[s['name'] for s in res['skills']]}")
                else:
                    print(f"  ✗ [{h.get('cname')}] (ename={h.get('ename')}) 抓取失败")
            except Exception as exc:
                print(f"  ✗ [{h.get('cname')}] 发生异常: {exc}")

    print(f"\n抓取完成！成功: {success_count}/{len(herolist)}")

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"已保存全量真实技能至: {OUT_PATH}")

if __name__ == '__main__':
    main()
