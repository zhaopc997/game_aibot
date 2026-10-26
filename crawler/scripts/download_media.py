#!/usr/bin/env python3
"""
把数据库里的外链图片下载到本地，为迁往 COS 做准备。

为什么需要：
  角色头像 1093 / 武器图标 856 / 套装图标 160 全部指向第三方图床
  （gtimg、mihoyo、netease、wikia.nocookie、raw.githubusercontent 等）。
  国内访问其中若干域名极慢或直接不可用，且部分站点有防盗链，
  导致页面图片加载慢、大面积不显示。

策略：
  1. 按业务语义命名落盘：characters/{id}.jpg、weapons/{id}.png …
     便于后续排查，也让 COS 上的路径可读。
  2. 每个域名用对应的 Referer 伪装（多数图床只校验 Referer 是否存在）。
  3. 失败重试 + 记录失败清单，最后输出映射表 mapping.json。
  4. 并发下载但限制并发数，避免被目标站点限流。

用法：
  python3 download_media.py                # 全量下载
  python3 download_media.py --limit 20     # 只处理 20 条（试跑）
  python3 download_media.py --retry-failed # 只重试上次失败的
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ───── 配置 ─────
OUT_DIR = Path(os.environ.get("MEDIA_DIR", "./media_download"))
WORKERS = int(os.environ.get("WORKERS", "8"))
TIMEOUT = int(os.environ.get("TIMEOUT", "25"))

# 部分图床需要「来自本站」的 Referer 才放行；按域名给出
REFERERS = {
    "game.gtimg.cn": "https://game.qq.com/",
    "upload-os-bbs.mihoyo.com": "https://bbs.mihoyo.com/",
    "act-webstatic.hoyoverse.com": "https://www.hoyolab.com/",
    "act-upload.mihoyo.com": "https://www.hoyolab.com/",
    "yys.res.netease.com": "https://yys.163.com/",
    "patchwiki.biligame.com": "https://wiki.biligame.com/",
    "static.wikia.nocookie.net": "https://www.fandom.com/",
    "raw.githubusercontent.com": "https://github.com/",
    "eldenring.wiki.fextralife.com": "https://eldenring.wiki.fextralife.com/",
    "image.gcores.com": "https://www.gcores.com/",
}
DEFAULT_REFERER = "https://helozero.com/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# 扩展名归一化：有些 CDN 返回 image/jpeg 但路径无扩展名
EXT_BY_TYPE = {
    "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png",
    "image/webp": ".webp", "image/gif": ".gif", "image/svg+xml": ".svg",
    "image/avif": ".avif",
}


def db():
    return psycopg2.connect(
        host=os.environ.get("PG_HOST", "127.0.0.1"),
        port=int(os.environ.get("PG_PORT", "5432")),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
    )


def build_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=2, backoff_factor=0.6,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(["GET"]))
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_maxsize=WORKERS * 2))
    s.mount("http://", HTTPAdapter(max_retries=retry, pool_maxsize=WORKERS * 2))
    return s


def target_path(kind: str, row_id: int, url: str, content_type: str = "") -> Path:
    """按业务语义决定落盘路径与扩展名。"""
    ext = EXT_BY_TYPE.get((content_type or "").split(";")[0].lower(), "")
    if not ext:
        # 从 URL 路径猜扩展名
        p = urlparse(url).path
        ext = os.path.splitext(p)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"):
            ext = ".jpg"
    if ext == ".jpeg":
        ext = ".jpg"
    return OUT_DIR / kind / f"{row_id}{ext}"


def fetch(session: requests.Session, url: str, referer: str) -> tuple[bytes | None, str, str]:
    """返回 (内容, content_type, 错误信息)。"""
    try:
        r = session.get(url, timeout=TIMEOUT, headers={
            "User-Agent": UA,
            "Referer": referer,
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }, allow_redirects=True, verify=False)  # 部分老图床证书链不全
        if r.status_code != 200:
            return None, "", f"HTTP {r.status_code}"
        ctype = r.headers.get("content-type", "")
        if not ctype.startswith("image/"):
            return None, "", f"非图片类型 {ctype}"
        if len(r.content) < 256:
            return None, "", f"内容过小 {len(r.content)}B"
        return r.content, ctype, ""
    except Exception as e:  # noqa: BLE001 — 单张失败不应中断整批
        return None, "", f"{type(e).__name__}: {str(e)[:80]}"


def collect_items(conn, retry_failed: bool) -> list[dict]:
    items: list[dict] = []
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 'characters' AS kind, id, avatar_url AS url FROM game_character
             WHERE avatar_url LIKE 'http%'
            UNION ALL
            SELECT 'weapons', id, icon_url FROM game_weapon WHERE icon_url LIKE 'http%'
            UNION ALL
            SELECT 'artifacts', id, icon_url FROM game_artifact_set WHERE icon_url LIKE 'http%'
        """)
        for kind, rid, url in cur.fetchall():
            items.append({"kind": kind, "id": rid, "url": url})

    # 游戏封面（既是外链又有本地文件的情况跳过）
    with conn.cursor() as cur:
        cur.execute("SELECT id, cover_url FROM game WHERE cover_url LIKE 'http%'")
        for rid, url in cur.fetchall():
            items.append({"kind": "games", "id": rid, "url": url})

    if retry_failed:
        fp = OUT_DIR / "failed.json"
        if fp.exists():
            failed = json.loads(fp.read_text(encoding="utf-8"))
            keys = {(f["kind"], f["id"]) for f in failed}
            items = [i for i in items if (i["kind"], i["id"]) in keys]
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--input", help="从管道分隔的清单文件读取（kind|id|url），免连数据库")
    args = ap.parse_args()

    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if args.input:
        items = []
        for line in Path(args.input).read_text(encoding="utf-8").splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3 and parts[2].startswith("http"):
                items.append({"kind": parts[0], "id": int(parts[1]), "url": parts[2]})
    else:
        conn = db()
        items = collect_items(conn, args.retry_failed)
    if args.limit:
        items = items[: args.limit]
    total = len(items)
    print(f"[media] 待处理 {total} 张", flush=True)
    if not total:
        return 0

    for kind in ("characters", "weapons", "artifacts", "games"):
        (OUT_DIR / kind).mkdir(parents=True, exist_ok=True)

    ok_cnt = skip_cnt = fail_cnt = 0
    failed: list[dict] = []
    mapping: list[dict] = []
    session = build_session()
    t0 = time.time()

    def work(it: dict) -> dict:
        host = urlparse(it["url"]).netloc
        referer = REFERERS.get(host, DEFAULT_REFERER)
        # 已存在则跳过（支持断点续跑）
        for ext in (".jpg", ".png", ".webp", ".gif", ".svg", ".avif"):
            p = OUT_DIR / it["kind"] / f"{it['id']}{ext}"
            if p.exists() and p.stat().st_size > 256:
                return {**it, "status": "skip", "path": str(p)}
        data, ctype, err = fetch(session, it["url"], referer)
        if data is None:
            return {**it, "status": "fail", "error": err}
        p = target_path(it["kind"], it["id"], it["url"], ctype)
        p.write_bytes(data)
        return {**it, "status": "ok", "path": str(p), "bytes": len(data), "ctype": ctype}

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(work, it): it for it in items}
        for n, fut in enumerate(as_completed(futures), 1):
            res = fut.result()
            st = res["status"]
            if st == "ok":
                ok_cnt += 1
                mapping.append({"kind": res["kind"], "id": res["id"],
                                "url": res["url"], "path": res["path"],
                                "bytes": res.get("bytes")})
            elif st == "skip":
                skip_cnt += 1
                mapping.append({"kind": res["kind"], "id": res["id"],
                                "url": res["url"], "path": res["path"]})
            else:
                fail_cnt += 1
                failed.append({"kind": res["kind"], "id": res["id"],
                               "url": res["url"], "error": res["error"]})
            if n % 50 == 0 or n == total:
                el = time.time() - t0
                print(f"[media] {n}/{total}  成功 {ok_cnt}  跳过 {skip_cnt} "
                      f"失败 {fail_cnt}  {n/max(el,1):.1f} 张/秒", flush=True)

    (OUT_DIR / "mapping.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT_DIR / "failed.json").write_text(
        json.dumps(failed, ensure_ascii=False, indent=1), encoding="utf-8")

    size = sum(f.stat().st_size for f in OUT_DIR.rglob("*") if f.is_file())
    print(f"\n[media] 完成：成功 {ok_cnt} / 跳过 {skip_cnt} / 失败 {fail_cnt}")
    print(f"[media] 本地占用 {size/1048576:.1f} MB → {OUT_DIR}")
    if failed:
        from collections import Counter
        c = Counter(urlparse(f["url"]).netloc for f in failed)
        print("[media] 失败域名分布：")
        for host, n in c.most_common(8):
            print(f"        {host}: {n}")
        print("[media] 可稍后执行 --retry-failed 重试")
    return 0


if __name__ == "__main__":
    sys.exit(main())
