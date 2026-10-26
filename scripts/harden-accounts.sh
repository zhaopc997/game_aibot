#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 账号安全加固：清除默认弱密码
#
#   ./scripts/harden-accounts.sh              # 交互确认后执行
#   ./scripts/harden-accounts.sh --force      # 跳过确认
#   ./scripts/harden-accounts.sh --dry-run    # 只检查现状
#
# 背景：DataSeeder 创建的演示账号（admin/admin123、tester/...）
# 会随数据迁移进入生产库，而生产环境一旦存在已知弱口令，
# 等于后台完全敞开。本脚本：
#   1. 检测是否存在仍使用默认密码的账号
#   2. 为保留的账号重置为强随机密码
#   3. 禁用无用的演示账号
#
# 实现要点：数据库里存的是 BCrypt 哈希，本机通常没有 bcrypt 工具，
# 因此通过应用自身的 /auth/register 接口生成哈希（保证与
# BCryptPasswordEncoder 完全兼容），再回写到目标账号。
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-.env.production}"
KEEP_USER="${KEEP_USER:-admin}"          # 保留并重置密码的账号
DISABLE_USERS="${DISABLE_USERS:-tester}" # 需要禁用的演示账号（空格分隔）
DEFAULT_PASSWORDS="${DEFAULT_PASSWORDS:-admin123 password 123456}"

FORCE=0; DRY_RUN=0
for a in "$@"; do
  case "$a" in
    --force) FORCE=1 ;;
    --dry-run) DRY_RUN=1 ;;
    *) echo "未知参数: $a"; exit 1 ;;
  esac
done

log()  { printf "[harden] %s\n" "$*"; }
ok()   { printf "[  ok  ] %s\n" "$*"; }
warn() { printf "[ warn ] %s\n" "$*"; }
die()  { printf "[ fail ] %s\n" "$*" >&2; exit 1; }

[[ -f "$ENV_FILE" ]] || die "缺少 $ENV_FILE"
PG_USER=$(grep -E '^DB_USERNAME=' "$ENV_FILE" | cut -d= -f2-)
PG_DB=$(grep -E '^DB_NAME=' "$ENV_FILE" | cut -d= -f2-); PG_DB="${PG_DB:-guide_platform}"
HTTP_PORT=$(grep -E '^HTTP_PORT=' "$ENV_FILE" | cut -d= -f2-); HTTP_PORT="${HTTP_PORT:-80}"
BASE="http://127.0.0.1:${HTTP_PORT}"

psql_q() { docker exec "$(docker compose -p gameaibot -f docker-compose.prod.yml --env-file "$ENV_FILE" ps -q postgres)" psql -U "$PG_USER" -d "$PG_DB" -tAc "$1" 2>/dev/null; }

# ───── 1. 检测弱密码 ─────
log "巡检现有账号是否仍使用默认密码…"
VULNERABLE=()
for u in $(psql_q 'SELECT username FROM "user" WHERE deleted_at IS NULL;' | tr -d '\r'); do
  for p in $DEFAULT_PASSWORDS; do
    code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/api/v1/auth/login" \
             -H 'Content-Type: application/json' \
             -d "{\"username\":\"$u\",\"password\":\"$p\"}" 2>/dev/null || echo 000)
    if [[ "$code" == "200" ]]; then
      VULNERABLE+=("$u:$p")
      warn "账号 $u 可被默认密码 '$p' 登录"
      break
    fi
  done
done

if [[ ${#VULNERABLE[@]} -eq 0 ]]; then
  ok "未发现使用默认密码的账号"
  [[ "$DRY_RUN" -eq 1 ]] && exit 0
else
  log "共发现 ${#VULNERABLE[@]} 个弱口令账号"
  [[ "$DRY_RUN" -eq 1 ]] && { log "--dry-run 结束"; exit 0; }
fi

[[ "$FORCE" -eq 1 ]] || {
  warn "即将：重置 $KEEP_USER 的密码为强随机值；禁用账号：$DISABLE_USERS"
  read -r -p "确认继续？输入 yes：" ans
  [[ "$ans" == "yes" ]] || { log "已取消"; exit 0; }
}

# ───── 2. 用应用接口生成 BCrypt 哈希 ─────
# 先注册一个临时账号，取其密码哈希；用完立即删除。
STRONG_PW="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-24)"
TMP_USER="__pwgen_$(date +%s)"
log "通过 /auth/register 生成密码哈希（临时账号 $TMP_USER）…"
code=$(curl -s -o /tmp/harden_reg.json -w '%{http_code}' -X POST "$BASE/api/v1/auth/register" \
         -H 'Content-Type: application/json' \
         -d "{\"username\":\"$TMP_USER\",\"email\":\"$TMP_USER@local.invalid\",\"password\":\"$STRONG_PW\"}" 2>/dev/null || echo 000)
[[ "$code" == "200" ]] || die "注册临时账号失败（HTTP $code）：$(head -c 200 /tmp/harden_reg.json)"

HASH=$(psql_q "SELECT password_hash FROM \"user\" WHERE username='$TMP_USER';" | tr -d '\r')
[[ -n "$HASH" ]] || die "未能取到密码哈希"
ok "已生成 BCrypt 哈希（长度 ${#HASH}）"

# ───── 3. 重置目标账号 + 清理临时账号 ─────
log "为 $KEEP_USER 重置密码…"
psql_q "UPDATE \"user\" SET password_hash='$HASH', updated_at=now() WHERE username='$KEEP_USER';" >/dev/null
ok "$KEEP_USER 密码已重置"

log "删除临时账号 $TMP_USER…"
psql_q "DELETE FROM user_role WHERE user_id IN (SELECT id FROM \"user\" WHERE username='$TMP_USER');" >/dev/null
psql_q "DELETE FROM \"user\" WHERE username='$TMP_USER';" >/dev/null
ok "临时账号已清理"

# ───── 4. 禁用演示账号 ─────
for u in $DISABLE_USERS; do
  exists=$(psql_q "SELECT 1 FROM \"user\" WHERE username='$u' AND deleted_at IS NULL;" | tr -d '\r')
  [[ -n "$exists" ]] || continue
  psql_q "UPDATE \"user\" SET status='DISABLED', updated_at=now() WHERE username='$u';" >/dev/null
  ok "已禁用演示账号 $u"
done

# ───── 5. 验证 ─────
log "验证加固效果…"
new_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/api/v1/auth/login" \
             -H 'Content-Type: application/json' \
             -d "{\"username\":\"$KEEP_USER\",\"password\":\"$STRONG_PW\"}" 2>/dev/null || echo 000)
old_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/api/v1/auth/login" \
             -H 'Content-Type: application/json' \
             -d "{\"username\":\"$KEEP_USER\",\"password\":\"admin123\"}" 2>/dev/null || echo 000)

echo ""
echo "════════════ 加固结果 ════════════"
printf "  %-28s → HTTP %s %s\n" "$KEEP_USER / <新密码>" "$new_code" "$([[ "$new_code" == "200" ]] && echo '✓ 可登录' || echo '✗ 异常')"
printf "  %-28s → HTTP %s %s\n" "$KEEP_USER / admin123" "$old_code" "$([[ "$old_code" != "200" ]] && echo '✓ 已失效' || echo '⚠ 仍可登录')"
echo ""
echo "  新的 $KEEP_USER 账号密码（请立即保存到密码管理器）："
echo "      用户名: $KEEP_USER"
echo "      密  码: $STRONG_PW"
echo ""
warn "该密码仅在本输出中显示一次，请立即保存。"
[[ "$new_code" == "200" && "$old_code" != "200" ]] || die "加固后验证未通过，请人工检查"