"""验证入库结果(临时调试用)。"""
import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / 'crawler' / '.env')

conn = psycopg2.connect(
    host=os.getenv('PG_HOST', 'localhost'),
    port=int(os.getenv('PG_PORT', 5433)),
    dbname=os.getenv('PG_DB', 'guide_platform'),
    user=os.getenv('PG_USER', 'postgres'),
    password=os.getenv('PG_PASSWORD', 'postgres'),
)
cur = conn.cursor()
cur.execute("""
    SELECT g.id, g.title, g.status, g.type, g.like_count, g.tags::text,
           cs.source_type, cs.source_url, cs.source_title
    FROM guide g
    JOIN content_source cs ON cs.guide_id = g.id
    WHERE cs.source_type = 'BILI_VIDEO'
    ORDER BY g.id
""")
rows = cur.fetchall()
print(f"📊 B 站采集入库数: {len(rows)}\n")
for r in rows:
    print(f"  [{r[0]}] {r[1][:60]}")
    print(f"      status={r[2]}  type={r[3]}  likes={r[4]}  tags={r[5]}")
    print(f"      source: {r[6]} | {r[7]}")
    print(f"      meta:   {r[8]}")
    print()

# 再看 guide.content(steps)jsonb 结构
cur.execute("""
    SELECT id, title, jsonb_pretty(content::jsonb)
    FROM guide
    WHERE id IN (SELECT guide_id FROM content_source WHERE source_type = 'BILI_VIDEO')
    LIMIT 1
""")
row = cur.fetchone()
if row:
    print(f"📦 样例 guide.content(guide_id={row[0]}, {row[1][:30]}…):")
    print(row[2][:600])
