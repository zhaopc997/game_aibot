#!/usr/bin/env python3
"""
根据 COS 上传结果，生成改写数据库图片字段的 SQL。

为什么不直接连库：
  生产库没有对宿主机暴露端口，也不应为了改几个 URL 去开端口。
  这里只产出 SQL 文件，再用 psql 经 docker exec 执行，零端口暴露、可审阅。

行为：
  · media_urls.json 里有的条目 → 改成 COS/CDN 地址
  · 下载失败（源头 404）的条目 → 置为 NULL
    理由：留着一个必定 404 的外链，浏览器会白白等待并显示破图；
         置 NULL 后前端走占位符，体验更好。
  · 整段放进一个事务，可用 ROLLBACK 撤销

用法：
  python3 update_media_urls.py                  # 生成 SQL
  # 然后在库所在机器上：
 #   docker exec -i <pg> psql -U <user> -d <db> < out/update_media_urls.sql
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MEDIA_DIR = Path("./media_download")

# kind → (表名, 列名)
TARGETS = {
    "characters": ("game_character", "avatar_url"),
    "weapons": ("game_weapon", "icon_url"),
    "artifacts": ("game_artifact_set", "icon_url"),
    "games": ("game", "cover_url"),
}


def esc(s: str) -> str:
    return s.replace("'", "''")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", default=str(MEDIA_DIR / "media_urls.json"))
    ap.add_argument("--items", default="/tmp/media_items.txt",
                    help="原始清单（kind|id|url），用于识别哪些条目需要置空")
    ap.add_argument("--out", default=str(MEDIA_DIR / "update_media_urls.sql"))
    ap.add_argument("--null-missing", action="store_true", default=True,
                    help="下载失败的条目置 NULL（默认开启）")
    args = ap.parse_args()

    urls_path = Path(args.urls)
    if not urls_path.exists():
        sys.exit(f"找不到映射表：{urls_path}（请先运行 upload_media_to_cos.py）")
    mapping: dict[str, dict[str, str]] = json.loads(urls_path.read_text(encoding="utf-8"))

    # 原始清单：确认哪些 (kind,id) 原本有外链
    originals: dict[str, set[int]] = {}
    items_path = Path(args.items)
    if items_path.exists():
        for line in items_path.read_text(encoding="utf-8").splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3 and parts[2].startswith("http"):
                originals.setdefault(parts[0], set()).add(int(parts[1]))

    lines: list[str] = [
        "-- 由 update_media_urls.py 生成：把图片字段从第三方外链改为 COS/CDN 地址",
        "-- 事务包裹，执行后可用 ROLLBACK 撤销",
        "BEGIN;",
        "",
    ]

    stats: dict[str, tuple[int, int]] = {}
    for kind, (table, column) in TARGETS.items():
        m = mapping.get(kind, {})
        if not m:
            continue
        ids = ",".join(sorted(m.keys(), key=lambda x: int(x)))
        cases = "\n".join(
            f"    WHEN {rid} THEN '{esc(url)}'" for rid, url in
            sorted(m.items(), key=lambda kv: int(kv[0]))
        )
        lines.append(f"-- {kind}: {len(m)} 条改为 COS 地址")
        lines.append(
            f"UPDATE {table} SET {column} = CASE id\n{cases}\n"
            f"  ELSE {column} END\nWHERE id IN ({ids});"
        )
        lines.append("")

        null_cnt = 0
        if args.null_missing and kind in originals:
            missing = originals[kind] - {int(k) for k in m}
            if missing:
                mid = ",".join(str(i) for i in sorted(missing))
                lines.append(f"-- {kind}: {len(missing)} 条源头已 404，置空走占位符")
                lines.append(f"UPDATE {table} SET {column} = NULL WHERE id IN ({mid});")
                lines.append("")
                null_cnt = len(missing)
        stats[kind] = (len(m), null_cnt)

    lines += [
        "-- 校验：仍有外链的条目应为 0",
        "SELECT 'characters' AS t, count(*) FROM game_character WHERE avatar_url LIKE 'http%'",
        "  UNION ALL SELECT 'weapons', count(*) FROM game_weapon WHERE icon_url LIKE 'http%'",
        "  UNION ALL SELECT 'artifacts', count(*) FROM game_artifact_set WHERE icon_url LIKE 'http%'",
        "  UNION ALL SELECT 'games', count(*) FROM game WHERE cover_url LIKE 'http%';",
        "",
        "-- 确认无误后提交；如需撤销把 COMMIT 换成 ROLLBACK",
        "COMMIT;",
        "",
    ]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    print("[sql] 生成完成")
    for kind, (upd, nul) in stats.items():
        print(f"        {kind:12} 改 COS {upd:>5} 条    置空 {nul:>4} 条")
    print(f"[sql] 输出 → {out}  ({out.stat().st_size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
