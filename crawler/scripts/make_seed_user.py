"""
创建 system bot 用户(author_id=1),供爬虫入库使用。

注意:user_role 是独立表,所以 role 用 INSERT 单独写。

运行:  python crawler/scripts/make_seed_user.py
"""
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / 'crawler' / '.env')

PG = dict(
    host=os.getenv('PG_HOST', 'localhost'),
    port=int(os.getenv('PG_PORT', 5432)),
    dbname=os.getenv('PG_DB', 'guide_platform'),
    user=os.getenv('PG_USER', 'postgres'),
    password=os.getenv('PG_PASSWORD', 'postgres'),
)

UPSERT_USER = """
INSERT INTO "user" (id, username, email, password_hash, bio, level, exp, status, created_at, updated_at)
VALUES (1, 'crawler_bot', 'crawler-bot@game-aibot.local',
        '!crawler!', '自动采集账号(由 crawler 模块写入)', 1, 0, 'NORMAL', now(), now())
ON CONFLICT (id) DO UPDATE
SET username = EXCLUDED.username,
    email    = EXCLUDED.email,
    bio      = EXCLUDED.bio,
    status   = EXCLUDED.status;
"""

UPSERT_ROLE = """
INSERT INTO user_role (user_id, role, created_at)
VALUES (1, 'USER', now())
ON CONFLICT (user_id, role) DO NOTHING;
"""

SYNC_SEQUENCE = """
SELECT setval('user_id_seq', coalesce((SELECT max(id) FROM "user"), 1));
"""


def main():
    print(f"→ 连接数据库 {PG['host']}:{PG['port']}/{PG['dbname']}")
    try:
        with psycopg2.connect(
            host=PG['host'],
            port=PG['port'],
            dbname=PG['dbname'],
            user=PG['user'],
            password=PG['password'],
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(UPSERT_USER)
                cur.execute(UPSERT_ROLE)
                cur.execute(SYNC_SEQUENCE)
            conn.commit()
            print("✅ 采集者用户已确保存在 (id=1, username=crawler_bot, role=USER), 自增序列已同步")
    except Exception as e:
        print(f"❌ 失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
