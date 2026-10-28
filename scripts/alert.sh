#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 告警发送器（供 health-check.sh 调用，也可单独用）
#
#   ./scripts/alert.sh "标题" "正文" [ok|warn|fail]
#
# 配置：在工作目录放 .alert.env（600 权限），可只配其中一个渠道。
#
#   # 企业微信群机器人（最省事：群设置 → 群机器人 → 添加）
#   WECOM_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
#
#   # 钉钉群机器人
#   DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
#
#   # 通用 Webhook：POST JSON {"title","content","level"}
#   # 适配 Server酱 / PushDeer / Slack 中转 / 自建接收端
#   ALERT_WEBHOOK=https://example.com/hook
#
# 设计原则：
#   · 多通道可同时配置，任一通道失败不影响其他通道；
#   · 全部通道都失败时返回非 0，但**不抛异常**——告警发不出去
#     不能反过来把巡检搞崩（否则用户既收不到告警，也看不到日志）；
#   · 正文超过渠道长度限制时截断，避免因超长被整条丢弃。
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ALERT_ENV:-$ROOT/.alert.env}"

TITLE="${1:-告警}"
BODY="${2:-}"
LEVEL="${3:-warn}"

# 未配置任何渠道：直接退出 0，不打扰巡检
if [[ ! -f "$ENV_FILE" ]]; then
  echo "[alert] 未配置 $ENV_FILE，跳过发送" >&2
  exit 0
fi
# shellcheck disable=SC1090
set -a; . "$ENV_FILE"; set +a

# 单条消息正文上限（企业微信 markdown 上限 4096 字节，留出标题/时间余量）
MAX_BODY=3500
if [[ ${#BODY} -gt $MAX_BODY ]]; then
  BODY="${BODY:0:$MAX_BODY}"$'\n\n…（内容过长已截断，完整信息见服务器 /var/log/game-health.log）'
fi

TS="$(date '+%Y-%m-%d %H:%M:%S')"
HOST="$(hostname -s 2>/dev/null || echo server)"

case "$LEVEL" in
  ok)   EMOJI="✅" ;;
  fail) EMOJI="🔴" ;;
  *)    EMOJI="⚠️" ;;
esac

SENT=0
FAILED_CH=()

# ───── 企业微信群机器人 ─────
if [[ -n "${WECOM_WEBHOOK:-}" ]]; then
  payload=$(jq -n --arg t "$EMOJI $TITLE" --arg b "$BODY" --arg ts "$TS" --arg h "$HOST" \
    '{msgtype:"markdown", markdown:{content:("### " + $t + "\n> 主机：" + $h + "\n> 时间：" + $ts + "\n\n" + $b)}}')
  if curl -sS --max-time 10 -H 'Content-Type: application/json' \
       -d "$payload" "$WECOM_WEBHOOK" 2>/dev/null | grep -q '"errcode":0'; then
    SENT=$((SENT + 1))
  else
    FAILED_CH+=("wecom")
  fi
fi

# ───── 钉钉群机器人 ─────
if [[ -n "${DINGTALK_WEBHOOK:-}" ]]; then
  payload=$(jq -n --arg t "$EMOJI $TITLE" --arg b "$BODY" --arg ts "$TS" --arg h "$HOST" \
    '{msgtype:"markdown", markdown:{title:$t, text:("### " + $t + "\n\n> 主机：" + $h + "  \n> 时间：" + $ts + "\n\n" + $b)}}')
  if curl -sS --max-time 10 -H 'Content-Type: application/json' \
       -d "$payload" "$DINGTALK_WEBHOOK" 2>/dev/null | grep -q '"errcode":0'; then
    SENT=$((SENT + 1))
  else
    FAILED_CH+=("dingtalk")
  fi
fi

# ───── 通用 Webhook ─────
if [[ -n "${ALERT_WEBHOOK:-}" ]]; then
  payload=$(jq -n --arg t "$TITLE" --arg b "$BODY" --arg l "$LEVEL" --arg ts "$TS" --arg h "$HOST" \
    '{title:$t, content:$b, level:$l, host:$h, time:$ts}')
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 \
         -H 'Content-Type: application/json' -d "$payload" "$ALERT_WEBHOOK" 2>/dev/null || echo 000)
  if [[ "$code" =~ ^2 ]]; then
    SENT=$((SENT + 1))
  else
    FAILED_CH+=("webhook(HTTP $code)")
  fi
fi

if [[ ${#FAILED_CH[@]} -gt 0 ]]; then
  echo "[alert] 以下通道发送失败：${FAILED_CH[*]}" >&2
fi
if [[ "$SENT" -eq 0 ]]; then
  echo "[alert] 没有任何通道成功发送（已配置通道数：$(( ${#FAILED_CH[@]} ))）" >&2
  exit 1
fi
echo "[alert] 已通过 $SENT 个通道发送：$TITLE" >&2
exit 0
