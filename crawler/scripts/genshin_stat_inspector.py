#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原神数值版本变动定期巡检与差分比对引擎 (Stat Inspection & Diff Engine)
功能：
1. 定期（或在游戏版本发布后）自动扫描官方数值与本地数据库
2. 基于 SHA-256 数据快照实现快速命中校验
3. 对变动的条目执行细粒度字段递归比对（面板/倍率/命座/材料/机制）
4. 结构化写入 stat_version_audit 审计表，并向系统管理员推送 VERSION_OUTDATED 变动告警通知
"""

import argparse
import hashlib
import json
import os
import sys
import time
import psycopg2
from psycopg2.extras import Json

PG_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': int(os.getenv('PG_PORT', 5433)),
    'dbname': os.getenv('PG_DB', 'guide_platform'),
    'user': os.getenv('PG_USER', 'postgres'),
    'password': os.getenv('PG_PASSWORD', 'postgres'),
}

def calc_hash(data: dict) -> str:
    s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def diff_dicts(old_val, new_val, path=""):
    """递归比对两个对象的各个字段并提取差异"""
    diffs = []
    if type(old_val) != type(new_val):
        diffs.append({
            "field": path,
            "type": "TYPE_MISMATCH",
            "old": str(old_val),
            "new": str(new_val)
        })
        return diffs

    if isinstance(old_val, dict):
        all_keys = set(old_val.keys()).union(set(new_val.keys()))
        for k in sorted(all_keys):
            p = f"{path}.{k}" if path else k
            if k not in old_val:
                diffs.append({"field": p, "type": "FIELD_ADDED", "old": None, "new": new_val[k]})
            elif k not in new_val:
                diffs.append({"field": p, "type": "FIELD_REMOVED", "old": old_val[k], "new": None})
            else:
                diffs.extend(diff_dicts(old_val[k], new_val[k], p))
    elif isinstance(old_val, list):
        if len(old_val) != len(new_val):
            diffs.append({
                "field": f"{path}.length",
                "type": "LIST_SIZE_CHANGED",
                "old": len(old_val),
                "new": len(new_val)
            })
        for i in range(min(len(old_val), len(new_val))):
            diffs.extend(diff_dicts(old_val[i], new_val[i], f"{path}[{i}]"))
    else:
        if str(old_val).strip() != str(new_val).strip():
            diffs.append({
                "field": path,
                "type": "VALUE_CHANGED",
                "old": old_val,
                "new": new_val
            })
    return diffs

def inspect_game_stats(game_id=2, trigger_mode="CRON"):
    batch_no = f"INSPECT_{time.strftime('%Y%m%d_%H%M%S')}"
    print(f"=== 启动原神数值巡检任务 [批次号: {batch_no}, 触发源: {trigger_mode}] ===")

    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # 读取数据库中现存角色
    cur.execute("SELECT id, name, data_hash, base_stats, talents, constellations, special_mechanics FROM game_character WHERE game_id = %s", (game_id,))
    db_chars = {r[1]: {"id": r[0], "hash": r[2], "base_stats": r[3], "talents": r[4], "constellations": r[5], "mechanics": r[6]} for r in cur.fetchall()}

    # 从 sync_genshin_full_stats 模块获取最新标准基准源
    from sync_genshin_full_stats import get_characters, get_weapons, get_artifact_sets
    latest_chars = get_characters()

    report = {
        "batch_no": batch_no,
        "total": 0,
        "unchanged": 0,
        "modified": 0,
        "new_added": 0,
        "details": []
    }

    # 1. 巡检角色
    for ch in latest_chars:
        name = ch['name']
        new_h = calc_hash(ch)
        report["total"] += 1

        if name not in db_chars:
            # 新增角色
            report["new_added"] += 1
            summary = f"检测到新实装角色: 【{name}】({ch.get('title', '')})，已纳入数据监控"
            cur.execute("""
                INSERT INTO stat_version_audit (
                    game_id, target_type, target_id, target_name, check_batch_no,
                    status, diff_summary, diff_detail, old_hash, new_hash
                ) VALUES (%s, 'CHARACTER', NULL, %s, %s, 'NEW_ADDED', %s, %s, '', %s)
            """, (game_id, name, batch_no, summary, Json([]), new_h))
            print(f"  [+] 新增角色: {name}")
            report["details"].append({"name": name, "status": "NEW_ADDED", "summary": summary})
        else:
            old_h = db_chars[name]["hash"]
            char_id = db_chars[name]["id"]

            if old_h == new_h:
                report["unchanged"] += 1
                cur.execute("""
                    INSERT INTO stat_version_audit (
                        game_id, target_type, target_id, target_name, check_batch_no,
                        status, diff_summary, diff_detail, old_hash, new_hash
                    ) VALUES (%s, 'CHARACTER', %s, %s, %s, 'UNCHANGED', %s, %s, %s, %s)
                """, (game_id, char_id, name, batch_no, f"角色【{name}】全量数值与基准完全一致", Json([]), old_h, new_h))
                print(f"  [=] 角色一致: {name} (Hash: {new_h[:8]})")
            else:
                report["modified"] += 1
                # 递归提取差异
                old_snap = {
                    "base_stats": db_chars[name]["base_stats"],
                    "talents": db_chars[name]["talents"],
                    "constellations": db_chars[name]["constellations"],
                    "special_mechanics": db_chars[name]["mechanics"]
                }
                new_snap = {
                    "base_stats": ch["base_stats"],
                    "talents": ch["talents"],
                    "constellations": ch["constellations"],
                    "special_mechanics": ch["special_mechanics"]
                }
                diffs = diff_dicts(old_snap, new_snap)
                summary = f"角色【{name}】在最新版本检测到 {len(diffs)} 处数值变动！"
                print(f"  [!] 数值变动: {name} ({len(diffs)} 处差异)")

                cur.execute("""
                    INSERT INTO stat_version_audit (
                        game_id, target_type, target_id, target_name, check_batch_no,
                        status, diff_summary, diff_detail, old_hash, new_hash
                    ) VALUES (%s, 'CHARACTER', %s, %s, %s, 'MODIFIED', %s, %s, %s, %s)
                """, (game_id, char_id, name, batch_no, summary, Json(diffs[:20]), old_h, new_h))

                # 插入系统通知表
                cur.execute("""
                    INSERT INTO notification (
                        user_id, type, title, content, related_type, related_id, is_read
                    ) VALUES (
                        1, 'VERSION_OUTDATED', %s, %s, 'CHARACTER', %s, false
                    )
                """, (
                    f"【数值变动预警】{name} 存在版本数值调整",
                    f"在巡检批次 {batch_no} 中发现角色 {name} 存在 {len(diffs)} 处数值/倍率调整，请核对。",
                    char_id
                ))
                report["details"].append({"name": name, "status": "MODIFIED", "summary": summary, "diffs": diffs})

    # 2. 巡检武器
    cur.execute("SELECT id, name, data_hash FROM game_weapon WHERE game_id = %s", (game_id,))
    db_weapons = {r[1]: {"id": r[0], "hash": r[2]} for r in cur.fetchall()}
    latest_weapons = get_weapons()
    for w in latest_weapons:
        wname = w['name']
        report["total"] += 1
        new_h = calc_hash(w)
        if wname in db_weapons:
            old_h = db_weapons[wname]["hash"]
            if old_h == new_h:
                cur.execute("""
                    INSERT INTO stat_version_audit (
                        game_id, target_type, target_id, target_name, check_batch_no,
                        status, diff_summary, diff_detail, old_hash, new_hash
                    ) VALUES (%s, 'WEAPON', %s, %s, %s, 'UNCHANGED', %s, %s, %s, %s)
                """, (game_id, db_weapons[wname]["id"], wname, batch_no, f"武器【{wname}】数值一致", Json([]), old_h, new_h))
                report["unchanged"] += 1
            else:
                report["modified"] += 1
                cur.execute("""
                    INSERT INTO stat_version_audit (
                        game_id, target_type, target_id, target_name, check_batch_no,
                        status, diff_summary, diff_detail, old_hash, new_hash
                    ) VALUES (%s, 'WEAPON', %s, %s, %s, 'MODIFIED', %s, %s, %s, %s)
                """, (game_id, db_weapons[wname]["id"], wname, batch_no, f"武器【{wname}】数值变动", Json([]), old_h, new_h))
        else:
            report["new_added"] += 1

    # 3. 巡检圣遗物
    cur.execute("SELECT id, name, data_hash FROM game_artifact_set WHERE game_id = %s", (game_id,))
    db_artifacts = {r[1]: {"id": r[0], "hash": r[2]} for r in cur.fetchall()}
    latest_artifacts = get_artifact_sets()
    for art in latest_artifacts:
        aname = art['name']
        report["total"] += 1
        new_h = calc_hash(art)
        if aname in db_artifacts:
            old_h = db_artifacts[aname]["hash"]
            if old_h == new_h:
                cur.execute("""
                    INSERT INTO stat_version_audit (
                        game_id, target_type, target_id, target_name, check_batch_no,
                        status, diff_summary, diff_detail, old_hash, new_hash
                    ) VALUES (%s, 'ARTIFACT', %s, %s, %s, 'UNCHANGED', %s, %s, %s, %s)
                """, (game_id, db_artifacts[aname]["id"], aname, batch_no, f"圣遗物【{aname}】套装规格一致", Json([]), old_h, new_h))
                report["unchanged"] += 1
            else:
                report["modified"] += 1
                cur.execute("""
                    INSERT INTO stat_version_audit (
                        game_id, target_type, target_id, target_name, check_batch_no,
                        status, diff_summary, diff_detail, old_hash, new_hash
                    ) VALUES (%s, 'ARTIFACT', %s, %s, %s, 'MODIFIED', %s, %s, %s, %s)
                """, (game_id, db_artifacts[aname]["id"], aname, batch_no, f"圣遗物【{aname}】套装规格变动", Json([]), old_h, new_h))
        else:
            report["new_added"] += 1

    conn.commit()
    conn.close()

    print("\n=== 巡检报告概要 ===")
    print(f"巡检批次: {batch_no}")
    print(f"总计检测条目: {report['total']}")
    print(f"无变动项 (一致): {report['unchanged']}")
    print(f"检测到变动项: {report['modified']}")
    print(f"新增实装项: {report['new_added']}")
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="原神数值巡检与变动比对引擎")
    parser.add_argument("--game-id", type=int, default=2, help="游戏ID (原神默认为2)")
    parser.add_argument("--trigger", type=str, default="CLI_MANUAL", help="触发来源")
    args = parser.parse_args()

    inspect_game_stats(game_id=args.game_id, trigger_mode=args.trigger)
