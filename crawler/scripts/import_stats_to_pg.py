#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 crawler/out/stats/ 下采集的游戏数值属性导入到 PostgreSQL wiki_entry 表。
幂等执行：已存在的 (game_id, title) 记录将更新其 content 与 last_updated。
"""

import json
import os
import sys
from pathlib import Path
from db_base import get_db_conn, logger

ROOT = Path(__file__).resolve().parent.parent.parent
STATS_DIR = ROOT / 'crawler' / 'out' / 'stats'

def import_game_stats(conn, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    game_id = data['game_id']
    game_name = data['game_name']
    cur = conn.cursor()

    imported_count = 0

    def upsert_entry(t, c):
        nonlocal imported_count
        cur.execute("SELECT id FROM wiki_entry WHERE game_id = %s AND title = %s", (game_id, t))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE wiki_entry SET content = %s, last_updated = NOW() WHERE id = %s", (c, row[0]))
        else:
            cur.execute("INSERT INTO wiki_entry (game_id, title, content, last_updated) VALUES (%s, %s, %s, NOW())", (game_id, t, c))
        imported_count += 1

    # 1. 导入角色成长面板
    for c in data.get('characters', []):
        title = f"【角色属性】{c['name']}：全等级基础成长面板与数值突破"
        content = c.get('markdown', '')
        upsert_entry(title, content)

    # 2. 导入装备/武器属性
    for eq in data.get('equipment', []):
        title = f"【装备属性】{eq['name']}：强化阶段数值与专属效果"
        content = eq.get('markdown', '')
        upsert_entry(title, content)

    # 3. 导入套装属性
    for st in data.get('sets', []):
        title = f"【套装机制】{st['name']}：套装加成与机制配队"
        content = st.get('markdown', '')
        upsert_entry(title, content)

    conn.commit()
    print(f"[import] {game_name} (ID: {game_id}): 成功同步导入 {imported_count} 条数值百科词条")

def main():
    if not STATS_DIR.exists():
        print(f"[import] 错误: {STATS_DIR} 不存在，请先运行 crawl_game_stats.py")
        sys.exit(1)

    logger.info("连接 PostgreSQL 数据库...")
    conn = get_db_conn()
    try:
        files = sorted(STATS_DIR.glob('*_stats.json'))
        for f in files:
            import_game_stats(conn, f)
        print("[import] 全部游戏数值属性百科词条导入完成！")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
