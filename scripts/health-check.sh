#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 健康巡检（可接 cron / 告警）
#
#   ./scripts/health-check.sh          # 人类可读输出
#   ./scripts/health-check.sh --quiet  # 只在异常时输出（cron 用）
#
# 退出码：0 = 全部正常；1 = 有异常（便于 cron + 告警系统判断）
#
# 为什么要监控这几项：
#   本项目曾出现「ES 索引写入全部失败 → 搜索与 AI 助手完全不可用」，
#   但容器健康检查全绿、日志显示成功、页面无报错，问题潜伏很久才被发现。
#   根因是没有任何指标覆盖「索引条数」与「搜索命中率」。
#   本脚本正是为补上这个盲区。
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-.env.production}"
QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

FAILS=0
WARNS=0

say()  { [[ "$QUIET" -eq 0 ]] && printf "%s\n" "$*"; }
ok()   { say "  [ ok ] $*"; }
bad()  { printf "  [FAIL] %s\n" "$*"; FAILS=$((FAILS + 1)); }
warn() { printf "  [warn] %s\n" "$*"; WARNS=$((WARNS + 1)); }

[[ -f "$ENV_FILE" ]] || { echo "缺少 $ENV_FILE"; exit 1; }
HTTP_PORT=$(grep -E '^HTTP_PORT=' "$ENV_FILE" | cut -d= -f2- | sed 's/.*://')
HTTP_PORT="${HTTP_PORT:-80}"
BASE="http://127.0.0.1:${HTTP_PORT}"
PG_USER=$(grep -E '^DB_USERNAME=' "$ENV_FILE" | cut -d= -f2-)
PG_DB=$(grep -E '^DB_NAME=' "$ENV_FILE" | cut -d= -f2-); PG_DB="${PG_DB:-guide_platform}"

say "════════ 健康巡检 $(date '+%Y-%m-%d %H:%M:%S') ════════"

# ───── 1. 容器状态 ─────
say ""
say "【容器】"
while read -r name state health; do
  [[ -z "$name" ]] && continue
  if [[ "$state" != "running" ]]; then
    bad "$name 状态=$state"
  elif [[ "$health" == "unhealthy" ]]; then
    bad "$name 不健康"
  else
    ok "$name${health:+（$health）}"
  fi
done < <(docker ps -a --filter "name=game-prod" --format '{{.Names}} {{.State}} {{.Status}}' 2>/dev/null | awk '{print $1, $2, ($0 ~ /unhealthy/ ? "unhealthy" : ($0 ~ /healthy/ ? "healthy" : "-"))}')

# ───── 2. 服务可用性 ─────
say ""
say "【服务】"
check_http() {
  local label="$1" url="$2" expect="${3:-200}"
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$url" 2>/dev/null || echo 000)
  if [[ "$code" == "$expect" ]]; then ok "$label → $code"; else bad "$label → $code（期望 $expect）"; fi
}
check_http "前端 /healthz"                "$BASE/healthz"
check_http "后端 /actuator/health"        "$BASE/actuator/health"
check_http "后端 readiness"               "$BASE/actuator/health/readiness"
check_http "游戏列表 /api/v1/games"        "$BASE/api/v1/games"

# ───── 3. 数据量（防"库空了但服务还活着"）─────
say ""
say "【数据】"
pgval() {
  local cid
  cid=$(docker compose -p gameaibot -f docker-compose.prod.yml --env-file "$ENV_FILE" ps -q postgres 2>/dev/null || true)
  [[ -n "$cid" ]] || { echo "0"; return; }
  docker exec "$cid" psql -U "$PG_USER" -d "$PG_DB" -tAc "$1" 2>/dev/null | tr -d ' \r' || echo "0"
}
GAMES=$(pgval "SELECT count(*) FROM game;")
GUIDES=$(pgval "SELECT count(*) FROM guide;")
CHARS=$(pgval "SELECT count(*) FROM game_character;")
say "  游戏=$GAMES  攻略=$GUIDES  角色=$CHARS"
[[ "${GAMES:-0}" -gt 0 ]]  || bad "游戏表为空"
[[ "${GUIDES:-0}" -gt 0 ]] || bad "攻略表为空（搜索与 AI 将无内容）"

# ───── 4. 搜索索引（本项目最关键的健康指标）─────
say ""
say "【搜索索引】"
ES_DOCS=$(docker exec game-prod-es sh -c "curl -s 'http://localhost:9200/guides/_count'" 2>/dev/null | grep -o '"count":[0-9]*' | cut -d: -f2)
CHUNK_DOCS=$(docker exec game-prod-es sh -c "curl -s 'http://localhost:9200/guide_chunks/_count'" 2>/dev/null | grep -o '"count":[0-9]*' | cut -d: -f2)
ES_DOCS="${ES_DOCS:-0}"; CHUNK_DOCS="${CHUNK_DOCS:-0}"
say "  guides=$ES_DOCS  guide_chunks=$CHUNK_DOCS"

if [[ "$ES_DOCS" -eq 0 && "${GUIDES:-0}" -gt 0 ]]; then
  bad "guides 索引为 0 但有 $GUIDES 篇攻略 → 搜索不可用"
elif [[ "$ES_DOCS" -lt $((GUIDES * 8 / 10)) ]]; then
  warn "guides 索引条数($ES_DOCS) 明显少于攻略数($GUIDES)，索引可能不完整"
else
  ok "guides 索引与攻略数匹配"
fi

if [[ "$CHUNK_DOCS" -eq 0 && "${GUIDES:-0}" -gt 0 ]]; then
  bad "guide_chunks 索引为 0 → AI 检索不可用"
else
  ok "RAG 索引已就绪"
fi

# ───── 5. 搜索命中率（端到端验证，能发现 term 大小写这类隐蔽问题）─────
say ""
say "【搜索功能】"
# 用 python 精确解析条目数（grep 计数会把嵌套字段也算进去）
RESP=$(curl -s --max-time 10 "$BASE/api/v1/guides/search?keyword=%E6%96%B0%E6%89%8B" 2>/dev/null)
HIT=$(printf '%s' "$RESP" | python3 -c "
import sys, json
try:
    print(len(json.load(sys.stdin)['data']['items']))
except Exception:
    print(-1)
" 2>/dev/null)
if [[ "${HIT:-0}" -gt 0 ]]; then
  ok "关键词「新手」命中 $HIT 条"
elif [[ "${HIT:-0}" -eq 0 ]]; then
  bad "关键词「新手」命中 0 条 → 搜索链路异常（索引为空或查询条件不匹配）"
else
  bad "搜索接口返回异常，无法解析"
fi

# ───── 汇总 ─────
say ""
say "════════ 结果 ════════"
if [[ "$FAILS" -eq 0 && "$WARNS" -eq 0 ]]; then
  say "  全部正常"
  exit 0
fi
say "  失败 $FAILS 项，警告 $WARNS 项"
exit 1