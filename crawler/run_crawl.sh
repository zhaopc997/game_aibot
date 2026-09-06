#!/usr/bin/env bash
# 一键启动爬虫
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
VENV="$ROOT_DIR/.venv-crawler"

if [ ! -d "$VENV" ]; then
  echo "❌ venv 不存在,先跑: python3 -m venv .venv-crawler && source .venv-crawler/bin/activate && pip install -r crawler/requirements.txt && playwright install chromium"
  exit 1
fi

source "$VENV/bin/activate"
cd "$ROOT_DIR"

# 默认参数:--game=ys --limit=3(原神 3 篇),可改
python -m scrapy crawl bili_guide "$@"
