#!/usr/bin/env python3
"""
把本地已下载的媒体上传到腾讯云 COS，并输出可回写的 URL 映射。

前置：先跑 download_media.py 把外链图片落到 ./media_download

设计要点：
  1. **幂等**：已存在且大小一致的 object 跳过，可反复执行。
  2. **并发**：COS 上传是网络 IO，多线程显著提速；线程数可调。
  3. **缓存头**：图片是不可变资源（文件名带 id），设置长缓存，
     让 CDN 和浏览器都能长期缓存，减少回源。
  4. **URL 两种形态**：优先用 CDN 域名（更快），未配置则用 COS 默认域名。
  5. 输出 media_urls.json，供 update_media_urls.py 回写数据库。

用法：
  export COS_SECRET_ID=...
  export COS_SECRET_KEY=...
  export COS_BUCKET=gameguide-1250000000
  export COS_REGION=ap-guangzhou
  export COS_CDN_DOMAIN=https://cdn.example.com   # 可选

  python3 upload_media_to_cos.py
  python3 upload_media_to_cos.py --dry-run        # 只统计，不上传
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client

MEDIA_DIR = Path(os.environ.get("MEDIA_DIR", "./media_download"))
WORKERS = int(os.environ.get("WORKERS", "8"))

CONTENT_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml",
    ".avif": "image/avif",
}

# 图片内容按 id 命名、永不变更 → 可长期缓存
CACHE_CONTROL = "public, max-age=31536000, immutable"


def make_client() -> CosS3Client:
    secret_id = os.environ.get("COS_SECRET_ID")
    secret_key = os.environ.get("COS_SECRET_KEY")
    region = os.environ.get("COS_REGION")
    if not (secret_id and secret_key and region):
        sys.exit("缺少 COS_SECRET_ID / COS_SECRET_KEY / COS_REGION")
    cfg = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key,
                    Scheme="https", Timeout=60)
    return CosS3Client(cfg)


def public_url(key: str) -> str:
    """对外访问 URL：优先 CDN 域名，否则 COS 默认域名。"""
    cdn = os.environ.get("COS_CDN_DOMAIN", "").rstrip("/")
    if cdn:
        return f"{cdn}/{key}"
    bucket = os.environ["COS_BUCKET"]
    region = os.environ["COS_REGION"]
    return f"https://{bucket}.cos.{region}.myqcloud.com/{key}"


def collect_files() -> list[Path]:
    if not MEDIA_DIR.exists():
        sys.exit(f"媒体目录不存在：{MEDIA_DIR}（请先运行 download_media.py）")
    files = [p for p in MEDIA_DIR.rglob("*")
             if p.is_file() and p.suffix.lower() in CONTENT_TYPES
             and "media_download" not in p.name]
    # 排除统计用的 json
    return [p for p in files if p.suffix.lower() != ".json"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prefix", default=os.environ.get("COS_PREFIX", "media"),
                    help="COS 上的路径前缀，默认 media")
    args = ap.parse_args()

    files = collect_files()
    total = len(files)
    total_bytes = sum(f.stat().st_size for f in files)
    print(f"[cos] 待上传 {total} 个文件，共 {total_bytes/1048576:.1f} MB")
    print(f"[cos] 目标：cos://{os.environ.get('COS_BUCKET')} "
          f"({os.environ.get('COS_REGION')})  前缀 {args.prefix}/")
    if args.dry_run:
        from collections import Counter
        c = Counter(f.parent.name for f in files)
        for k, v in c.most_common():
            print(f"        {k}: {v}")
        return 0

    client = make_client()
    bucket = os.environ["COS_BUCKET"]

    # 先列出现有 object，做幂等跳过（避免逐个 HEAD 请求）
    existing: dict[str, int] = {}
    print("[cos] 读取桶内已有对象…", flush=True)
    marker = ""
    while True:
        resp = client.list_objects(Bucket=bucket, Prefix=f"{args.prefix}/",
                                   Marker=marker, MaxKeys=1000)
        for c in resp.get("Contents", []) or []:
            existing[c["Key"]] = int(c["Size"])
        if resp.get("IsTruncated") == "true":
            marker = resp.get("NextMarker", "")
            if not marker:
                break
        else:
            break
    print(f"[cos] 桶内已有 {len(existing)} 个对象")

    ok = skip = fail = 0
    results: list[dict] = []
    failed: list[dict] = []
    t0 = time.time()

    def work(p: Path) -> dict:
        key = f"{args.prefix}/{p.parent.name}/{p.name}"
        size = p.stat().st_size
        if existing.get(key) == size:
            return {"file": str(p), "key": key, "status": "skip"}
        ctype = CONTENT_TYPES.get(p.suffix.lower(), "application/octet-stream")
        try:
            with p.open("rb") as fh:
                # 不传 ContentLength：SDK 会按 Body 自行计算；
                # 手动传 int 会触发 "Header part must be str or bytes" 错误
                client.put_object(
                    Bucket=bucket, Key=key, Body=fh,
                    ContentType=ctype, CacheControl=CACHE_CONTROL,
                )
            return {"file": str(p), "key": key, "status": "ok", "bytes": size}
        except Exception as e:  # noqa: BLE001
            return {"file": str(p), "key": key, "status": "fail",
                    "error": f"{type(e).__name__}: {str(e)[:120]}"}

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(work, f): f for f in files}
        for n, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            if r["status"] == "ok":
                ok += 1
            elif r["status"] == "skip":
                skip += 1
            else:
                fail += 1
                failed.append(r)
            results.append(r)
            if n % 100 == 0 or n == total:
                el = time.time() - t0
                print(f"[cos] {n}/{total}  上传 {ok}  跳过 {skip}  "
                      f"失败 {fail}  {n/max(el,1):.1f} 个/秒", flush=True)

    # 输出映射：kind/id → 公网 URL
    mapping: dict[str, dict[str, str]] = {}
    for r in results:
        if r["status"] == "fail":
            continue
        parts = Path(r["key"]).parts  # media/<kind>/<id>.<ext>
        if len(parts) >= 3:
            kind, filename = parts[-2], parts[-1]
            rid = Path(filename).stem
            mapping.setdefault(kind, {})[rid] = public_url(r["key"])

    out = MEDIA_DIR / "media_urls.json"
    out.write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    (MEDIA_DIR / "upload_failed.json").write_text(
        json.dumps(failed, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n[cos] 完成：上传 {ok} / 跳过 {skip} / 失败 {fail}")
    print(f"[cos] 映射表 → {out}")
    for kind, m in mapping.items():
        print(f"        {kind}: {len(m)} 条")
    if failed:
        print(f"[cos] 失败清单 → {MEDIA_DIR/'upload_failed.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
