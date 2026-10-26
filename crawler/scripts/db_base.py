#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据库连接与配置管理模块 (crawler/scripts/db_base.py)
自动解析项目根目录与 crawler 目录下的 .env 文件，提供自动检测端口与稳健连接。
"""

import os
import sys
import logging
from pathlib import Path

# 配置通用日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("db_base")

def _load_env_file(path: Path):
    if not path.is_file():
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        logger.warning(f"Failed to read {path}: {e}")

# 自动定位项目根目录与 .env
SCRIPT_DIR = Path(__file__).resolve().parent
CRAWLER_DIR = SCRIPT_DIR.parent
ROOT_DIR = CRAWLER_DIR.parent

_load_env_file(CRAWLER_DIR / ".env")
_load_env_file(ROOT_DIR / ".env")

def get_db_config() -> dict:
    """获取解析后的 PostgreSQL 连接配置"""
    port_str = os.getenv("PG_PORT") or os.getenv("POSTGRES_PORT") or os.getenv("DB_PORT") or "5432"
    try:
        port = int(port_str)
    except ValueError:
        port = 5432

    return {
        "host": os.getenv("PG_HOST") or os.getenv("POSTGRES_HOST") or "localhost",
        "port": port,
        "dbname": os.getenv("PG_DB") or os.getenv("POSTGRES_DB") or "guide_platform",
        "user": os.getenv("PG_USER") or os.getenv("POSTGRES_USER") or "postgres",
        "password": os.getenv("PG_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or "postgres",
        "connect_timeout": 10
    }

def get_db_conn():
    """建立并返回 psycopg2 连接。若默认端口连接失败，尝试备用本地端口 (5433 / 5432)"""
    try:
        import psycopg2
    except ImportError:
        logger.error("psycopg2 is not installed. Please run: pip install psycopg2-binary")
        raise

    cfg = get_db_config()
    try:
        conn = psycopg2.connect(**cfg)
        return conn
    except Exception as e:
        # 如果端口连接被拒绝，尝试 5433 / 5432 自动重试
        fallback_port = 5433 if cfg["port"] == 5432 else 5432
        logger.warning(f"Connection to Postgres on port {cfg['port']} failed ({e}). Retrying fallback port {fallback_port}...")
        try:
            cfg_fallback = dict(cfg)
            cfg_fallback["port"] = fallback_port
            conn = psycopg2.connect(**cfg_fallback)
            logger.info(f"Successfully connected to Postgres on fallback port {fallback_port}")
            return conn
        except Exception:
            # 重新抛出原异常
            raise e
