"""
Master Crawler Orchestrator
Executes all specialized crawlers and outputs a comprehensive database report.
"""

import sys
import psycopg2
from .common.db import get_connection
from .modules.tft_crawler import crawl_and_sync_tft
from .modules.valorant_crawler import crawl_and_sync_valorant
from .modules.peace_elite_crawler import crawl_and_sync_peace_elite
from .modules.cs2_crawler import crawl_and_sync_cs2
from .modules.wuthering_waves_crawler import crawl_and_sync_wuthering_waves
from .modules.onmyoji_crawler import crawl_and_sync_onmyoji
from .modules.wukong_crawler import crawl_and_sync_wukong
from .modules.reverse1999_crawler import crawl_and_sync_reverse1999
from .modules.naraka_crawler import crawl_and_sync_naraka
from .modules.apex_crawler import crawl_and_sync_apex
from .modules.honkai3_crawler import crawl_and_sync_honkai3
from .modules.dota2_crawler import crawl_and_sync_dota2
from .modules.bg3_crawler import crawl_and_sync_bg3
from .modules.diablo4_crawler import crawl_and_sync_diablo4


def print_database_census():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
            SELECT 
                g.id,
                g.name,
                g.category,
                COALESCE(c.char_count, 0) AS characters,
                COALESCE(w.weap_count, 0) AS weapons,
                COALESCE(a.art_count, 0) AS artifacts,
                COALESCE(m.mech_count, 0) AS mechanics,
                (COALESCE(c.char_count, 0) + COALESCE(w.weap_count, 0) + COALESCE(a.art_count, 0) + COALESCE(m.mech_count, 0)) AS total
            FROM game g
            LEFT JOIN (SELECT game_id, COUNT(*) AS char_count FROM game_character GROUP BY game_id) c ON g.id = c.game_id
            LEFT JOIN (SELECT game_id, COUNT(*) AS weap_count FROM game_weapon GROUP BY game_id) w ON g.id = w.game_id
            LEFT JOIN (SELECT game_id, COUNT(*) AS art_count FROM game_artifact_set GROUP BY game_id) a ON g.id = a.game_id
            LEFT JOIN (SELECT game_id, COUNT(*) AS mech_count FROM game_mechanic_rule GROUP BY game_id) m ON g.id = m.game_id
            ORDER BY g.id;
            """
            cur.execute(sql)
            rows = cur.fetchall()

            print('\n' + '=' * 88)
            print(f'{"ID":<4} | {"游戏名称":<14} | {"分类":<10} | {"角色/英雄":<8} | {"装备/武器":<8} | {"套装/羁绊":<8} | {"机制规则":<8} | {"总数据条数":<8}')
            print('-' * 88)
            for r in rows:
                print(f'{r[0]:<4} | {r[1]:<14} | {r[2]:<10} | {r[3]:<8} | {r[4]:<8} | {r[5]:<8} | {r[6]:<8} | {r[7]:<8}')
            print('=' * 88 + '\n')
    finally:
        conn.close()


def run():
    print('Starting full game crawler & data synchronization pipeline...\n')

    tasks = [
        ('TFT & Golden Spatula (金铲铲之战 ID 28, 云顶之弈 ID 19)', lambda: crawl_and_sync_tft([28, 19])),
        ('Valorant (无畏契约 ID 17)', lambda: crawl_and_sync_valorant(17)),
        ('Peace Elite (和平精英 ID 27)', lambda: crawl_and_sync_peace_elite(27)),
        ('Counter-Strike 2 (CS2 ID 7)', lambda: crawl_and_sync_cs2(7)),
        ('Wuthering Waves (鸣潮 ID 26)', lambda: crawl_and_sync_wuthering_waves(26)),
        ('Onmyoji Mitama (阴阳师 ID 29)', lambda: crawl_and_sync_onmyoji(29)),
        ('Black Myth: Wukong (黑神话：悟空 ID 4)', lambda: crawl_and_sync_wukong(4)),
        ('Reverse: 1999 (重返未来：1999 ID 31)', lambda: crawl_and_sync_reverse1999(31)),
        ('Naraka: Bladepoint (永劫无间 ID 20)', lambda: crawl_and_sync_naraka(20)),
        ('Apex Legends (Apex 英雄 ID 16)', lambda: crawl_and_sync_apex(16)),
        ('Honkai Impact 3rd (崩坏3 ID 30)', lambda: crawl_and_sync_honkai3(30)),
        ('DOTA 2 (刀塔2 ID 5)', lambda: crawl_and_sync_dota2(5)),
        ('Baldur\'s Gate 3 (博德之门3 ID 11)', lambda: crawl_and_sync_bg3(11)),
        ('Diablo IV (暗黑破坏神4 ID 10)', lambda: crawl_and_sync_diablo4(10))
    ]

    for idx, (desc, func) in enumerate(tasks, 1):
        try:
            print(f'\n>>> [{idx}/{len(tasks)}] Crawling {desc} ...')
            func()
        except Exception as e:
            print(f'Warning: {desc} encountered an issue: {e}')

    print('\nAll crawlers finished! Generating database status report...')
    print_database_census()


if __name__ == '__main__':
    run()
