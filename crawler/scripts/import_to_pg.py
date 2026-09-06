"""
把 crawler/out/ 下的 JSON 文件导入到 PostgreSQL。

幂等:已存在 (source_url) 的 content_source 会跳过。
已存在的 guide 通过 (game_id, title) 判定重复。

用法:  python crawler/scripts/import_to_pg.py [out_dir]
"""
import json
import os
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / 'crawler' / '.env')

PG = dict(
    host=os.getenv('PG_HOST', 'localhost'),
    port=int(os.getenv('PG_PORT', 5433)),
    dbname=os.getenv('PG_DB', 'guide_platform'),
    user=os.getenv('PG_USER', 'postgres'),
    password=os.getenv('PG_PASSWORD', 'postgres'),
)
AUTHOR_ID = int(os.getenv('CRAWLER_AUTHOR_ID', 1))


def transform(item: dict) -> dict:
    """把爬虫 item 转成 guide 行的字段。"""
    # content JSONB:每条分 P 转一个 step
    pages = item.get('pages') or []
    steps = []
    for p in pages:
        steps.append({
            'step_id': p.get('part_index'),
            'title': p.get('title') or f'P{p.get("part_index")}',
            'description': '',
            'images': [item['cover_url']] if item.get('cover_url') else [],
            'video': item.get('url', ''),
        })
    if not steps:
        # 没分 P 就一个 step,放整体视频
        steps.append({
            'step_id': 1,
            'title': item.get('title', '视频'),
            'description': item.get('description', '')[:200],
            'images': [item['cover_url']] if item.get('cover_url') else [],
            'video': item.get('url', ''),
        })

    return {
        'game_id':   item['game_id'],
        'title':     item['title'][:255],
        'summary':   (item.get('description') or '')[:500],
        'content':   json.dumps({'steps': steps}, ensure_ascii=False),
        'tags':      json.dumps(['B站', item['game_name']], ensure_ascii=False),
        'author_id': AUTHOR_ID,
        'type':      'MANUAL',
        'status':    'DRAFT',  # 人工审核后再 PUBLISHED
    }


def import_one(cur, item: dict) -> str:
    """返回: 'inserted' / 'skipped' / 'error'"""
    bv = item.get('bv_id', '?')
    source_url = item.get('url')

    # 1. 先查重:source_url 存在 → 跳过
    cur.execute('SELECT id FROM content_source WHERE source_url = %s', (source_url,))
    if cur.fetchone():
        return 'skipped'

    # 2. 查重:同 game_id + title 也跳过
    cur.execute(
        'SELECT id FROM guide WHERE game_id = %s AND title = %s',
        (item['game_id'], item['title'][:255])
    )
    if cur.fetchone():
        return 'skipped'

    # 3. 插 guide
    g = transform(item)
    cur.execute("""
        INSERT INTO guide (game_id, title, summary, content, tags, author_id, type, status)
        VALUES (%(game_id)s, %(title)s, %(summary)s, %(content)s::jsonb, %(tags)s::jsonb,
                %(author_id)s, %(type)s, %(status)s)
        RETURNING id
    """, g)
    guide_id = cur.fetchone()[0]

    # 4. 插 content_source
    cur.execute("""
        INSERT INTO content_source
            (guide_id, source_type, source_url, source_title, license_note)
        VALUES (%s, 'BILI_VIDEO', %s, %s, %s)
    """, (
        guide_id, source_url,
        f"UP: {item.get('up_name', '?')} (BV:{bv})",
        f"采集自 B 站 UP:{item.get('up_name', '?')},版权属原作者,仅作学习用途"
    ))

    return 'inserted'


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'crawler' / 'out'
    if not out_dir.exists():
        print(f"❌ 目录不存在: {out_dir}")
        sys.exit(1)

    files = sorted(out_dir.glob('**/*.json'))
    if not files:
        print(f"⚠️  目录无 JSON: {out_dir}")
        return

    print(f"→ 准备导入 {len(files)} 条 from {out_dir}")
    inserted = skipped = errored = 0

    try:
        with psycopg2.connect(
            host=PG['host'],
            port=PG['port'],
            dbname=PG['dbname'],
            user=PG['user'],
            password=PG['password'],
        ) as conn:
            with conn.cursor() as cur:
                for f in files:
                    try:
                        item = json.loads(f.read_text(encoding='utf-8'))
                        result = import_one(cur, item)
                        if result == 'inserted':
                            inserted += 1
                            print(f"  ✅ {item.get('game_slug','?')}/{item.get('bv_id','?')}.json  inserted")
                        else:
                            skipped += 1
                            print(f"  ⏭️  {item.get('game_slug','?')}/{item.get('bv_id','?')}.json  skipped (重复)")
                    except Exception as e:
                        errored += 1
                        print(f"  ❌ {f.relative_to(ROOT)} error: {e}")
                conn.commit()
    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
        sys.exit(1)

    print(f"\n📊 完成: inserted={inserted}, skipped={skipped}, errored={errored}")


if __name__ == '__main__':
    main()
