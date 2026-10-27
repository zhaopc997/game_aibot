#!/usr/bin/env python3
"""
把本地文件（典型是数据库备份）上传到腾讯云 COS。

设计要点：
  1. **失败不阻断备份**：本脚本用于 backup-db.sh 的收尾步骤。
     备份本身成功但上传失败时，应保留本地备份并告警，而不是让整个备份任务报错失败
     —— 本地备份仍有价值，只是少了异地副本。
  2. **按日期分目录**：backup/2026/10/xxx.dump，便于按时间清理与查找。
  3. **对象名带日期时间**：与本地文件名一致，避免歧义。
  4. 上传后做一次 HEAD 校验，确认大小一致 —— 未校验的上传等于没上传。

用法：
  COS_SECRET_ID=... COS_SECRET_KEY=... COS_BUCKET=... COS_REGION=... \\
    python3 upload_backup_to_cos.py <file> [--prefix backup]

退出码：
  0 = 上传成功
  1 = 上传失败（调用方应记录告警，但不必让备份任务整体失败）
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--prefix", default=os.environ.get("COS_BACKUP_PREFIX", "backup"))
    args = ap.parse_args()

    f = Path(args.file)
    if not f.is_file():
        print(f"[cos-backup] 文件不存在：{f}", file=sys.stderr)
        return 1

    sid = os.environ.get("COS_SECRET_ID")
    skey = os.environ.get("COS_SECRET_KEY")
    bucket = os.environ.get("COS_BUCKET")
    region = os.environ.get("COS_REGION")
    missing = [k for k, v in (("COS_SECRET_ID", sid), ("COS_SECRET_KEY", skey),
                              ("COS_BUCKET", bucket), ("COS_REGION", region)) if not v]
    if missing:
        print(f"[cos-backup] 未配置 {', '.join(missing)}，跳过上传", file=sys.stderr)
        return 1

    try:
        from qcloud_cos import CosConfig, CosS3Client
    except ImportError:
        print("[cos-backup] 未安装 cos-python-sdk-v5，跳过上传", file=sys.stderr)
        return 1

    import datetime as dt
    now = dt.datetime.now()
    key = f"{args.prefix}/{now:%Y/%m}/{f.name}"
    size = f.stat().st_size

    cfg = CosConfig(Region=region, SecretId=sid, SecretKey=skey,
                    Scheme="https", Timeout=300)
    client = CosS3Client(cfg)

    try:
        with f.open("rb") as fh:
            # ACL=private 不能省：存储桶本身可能是「公有读」（图片需要），
            # 但备份含用户密码哈希等敏感数据，必须对象级私有，
            # 否则任何人猜到路径就能下载整库备份。
            client.put_object(Bucket=bucket, Key=key, Body=fh,
                              ContentType="application/octet-stream",
                              ACL="private")
        # 校验：对象大小与本地一致
        head = client.head_object(Bucket=bucket, Key=key)
        remote = int(head.get("Content-Length", -1))
        if remote != size:
            print(f"[cos-backup] 大小不一致：本地 {size} / 远端 {remote}", file=sys.stderr)
            return 1
    except Exception as e:  # noqa: BLE001
        print(f"[cos-backup] 上传失败：{type(e).__name__}: {str(e)[:160]}", file=sys.stderr)
        return 1

    scheme = "https"
    print(f"[cos-backup] 已上传 cos://{bucket}/{key}（{size/1048576:.1f} MB）")
    print(f"[cos-backup] 访问地址 {scheme}://{bucket}.cos.{region}.myqcloud.com/{key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
