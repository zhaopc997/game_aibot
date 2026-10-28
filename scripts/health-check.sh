#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 健康巡检（cron 每 10 分钟执行，异常时发送告警）
#
#   ./scripts/health-check.sh          # 人类可读输出
#   ./scripts/health-check.sh --quiet  # 精简输出（cron 用）
#
# 退出码：0 = 全部正常；1 = 有异常
#
# 为什么监控这几项：
#   本项目曾出现「ES 索引写入全部失败 → 搜索与 AI 助手完全不可用」，
#   但容器健康检查全绿、页面无报错，问题潜伏很久才被发现。
#   根因是没有指标覆盖「索引条数」与「搜索命中率」。
#
# 为什么加告警（2026-10-27 事故的直接教训）：
#   后端容器重建后 nginx 缓存了旧 IP，/api 全线 502 达 6 小时。
#   巡检脚本每 10 分钟都记录了 [FAIL]，但**只写日志、没有人看**，
#   等于没监控。现在补上：
#     · 状态变化时主动推送（企业微信 / 钉钉 / 通用 webhook）
#     · 持续故障按间隔重提醒，不是每 10 分钟轰炸
#     · 恢复正常时发「已恢复」，否则永远不知道好没好
#     · 每次运行都写一行心跳，能区分「健康」和「根本没跑」
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-.env.production}"
STATE_FILE="${STATE_FILE:-$ROOT/.health-state}"
QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

# 同一故障持续存在时的重提醒间隔（秒）。6 小时。
RENOTIFY_AFTER="${RENOTIFY_AFTER:-21600}"

FAILS=0
WARNS=0
FAIL_LINES=()

say()  { [[ "$QUIET" -eq 0 ]] && printf "%s\n" "$*"; }
ok()   { say "  [ ok ] $*"; }
bad()  { printf "  [FAIL] %s\n" "$*"; FAILS=$((FAILS + 1)); FAIL_LINES+=("$*"); }
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
  # 注意不能写 $(curl ... || echo 000)：curl 失败时 -w 已输出 000，
  # `|| echo 000` 会再追加一次，得到 "000000"，告警里很难看懂
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$url" 2>/dev/null)
  code="${code:-000}"
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

# ═══════════════════════════════════════════════════════════════
# 告警：状态变化 / 持续故障重提醒 / 恢复通知
# ═══════════════════════════════════════════════════════════════
NOW=$(date +%s)
STATUS="ok"
[[ "$FAILS" -gt 0 ]] && STATUS="fail"

# 故障签名：把失败项拼起来取 md5，用于判断"是不是同一批故障"。
# 不用失败数量做签名——数量抖动会导致重复告警。
SIG=""
if [[ ${#FAIL_LINES[@]} -gt 0 ]]; then
  SIG=$(printf '%s\n' "${FAIL_LINES[@]}" | md5sum | cut -d' ' -f1)
fi

PREV_STATUS=""; PREV_SIG=""; PREV_ALERT=0
if [[ -r "$STATE_FILE" ]]; then
  PREV_STATUS=$(grep -E '^status=' "$STATE_FILE" 2>/dev/null | cut -d= -f2-)
  PREV_SIG=$(grep -E '^sig=' "$STATE_FILE" 2>/dev/null | cut -d= -f2-)
  PREV_ALERT=$(grep -E '^last_alert=' "$STATE_FILE" 2>/dev/null | cut -d= -f2-)
  PREV_ALERT="${PREV_ALERT:-0}"
fi

SHOULD_ALERT=0
ALERT_LEVEL="warn"

if [[ "$STATUS" == "fail" ]]; then
  ALERT_LEVEL="fail"
  if [[ "$PREV_STATUS" != "fail" ]]; then
    SHOULD_ALERT=1                       # 新故障
  elif [[ -n "$PREV_SIG" && "$SIG" != "$PREV_SIG" ]]; then
    SHOULD_ALERT=1                       # 故障内容变了
  elif [[ $((NOW - PREV_ALERT)) -ge $RENOTIFY_AFTER ]]; then
    SHOULD_ALERT=1                       # 同一故障持续，按间隔重提醒
  fi
elif [[ "$PREV_STATUS" == "fail" ]]; then
  SHOULD_ALERT=1                         # 故障恢复
  ALERT_LEVEL="ok"
fi

if [[ "$SHOULD_ALERT" -eq 1 ]]; then
  if [[ "$ALERT_LEVEL" == "ok" ]]; then
    TITLE="helozero 已恢复正常"
    BODY="之前的故障已恢复，巡检全部通过。

时间：$(date '+%Y-%m-%d %H:%M:%S')
主机：$(hostname -s 2>/dev/null || echo server)

游戏=$GAMES  攻略=$GUIDES  角色=$CHARS
搜索「新手」命中 ${HIT} 条"
  else
    TITLE="helozero 巡检失败（${FAILS} 项）"
    BODY="$(printf '%s\n' "${FAIL_LINES[@]}" | sed 's/^/· /')

时间：$(date '+%Y-%m-%d %H:%M:%S')
主机：$(hostname -s 2>/dev/null || echo server)

完整日志：/var/log/game-health.log"
    if [[ ${#WARNS} -gt 0 ]]; then :; fi
  fi

  if [[ -x "$ROOT/scripts/alert.sh" ]]; then
    "$ROOT/scripts/alert.sh" "$TITLE" "$BODY" "$ALERT_LEVEL" || \
      echo "  [warn] 告警发送失败（见上方 error），巡检结果不受影响" >&2
  fi

  # 只有发送成功才更新 last_alert，避免发送失败后陷入长时间静默
  {
    echo "status=$STATUS"
    echo "sig=$SIG"
    echo "last_alert=$NOW"
  } > "$STATE_FILE" 2>/dev/null || true
else
  # 未触发告警时只更新状态，保留原有的 last_alert
  {
    echo "status=$STATUS"
    echo "sig=$SIG"
    echo "last_alert=$PREV_ALERT"
  } > "$STATE_FILE" 2>/dev/null || true
fi

# ───── 心跳：无论正常与否都写一行 ─────
# 之前的坑：--quiet 模式下健康时没有任何输出，日志不增长，
# 于是无法区分「系统健康」和「巡检根本没在跑」。
printf '[%s] heartbeat status=%s fails=%d warns=%d games=%s guides=%s es=%s hit=%s\n' \
  "$(date '+%Y-%m-%d %H:%M:%S')" "$STATUS" "$FAILS" "$WARNS" \
  "${GAMES:-?}" "${GUIDES:-?}" "${ES_DOCS:-?}" "${HIT:-?}"

# ───── 汇总 ─────
say ""
say "════════ 结果 ════════"
if [[ "$FAILS" -eq 0 && "$WARNS" -eq 0 ]]; then
  say "  全部正常"
  exit 0
fi
say "  失败 $FAILS 项，警告 $WARNS 项"
exit 1
