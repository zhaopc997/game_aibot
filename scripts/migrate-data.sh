#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 数据迁移脚本：开发库 → 生产库
#
#   ./scripts/migrate-data.sh              # 交互确认后迁移
#   ./scripts/migrate-data.sh --force      # 跳过确认
#   ./scripts/migrate-data.sh --dry-run    # 只看差异，不改动
#
# 背景：本项目有**两个独立的 PostgreSQL 实例**：
#   - 开发：docker-compose.local.yml  → 卷 gameaibot_pgdata      （端口5432）
#   - 生产：docker-compose.prod.yml→ 卷 gameaibot_prod-pgdata （不暴露端口）
#
# 两者数据卷独立，**新建生产环境时生产库是空的**，
# 必须显式迁移数据，否则页面会显示为"无数据"。
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DEV_VOLUME="${DEV_VOLUME:-gameaibot_pgdata}"
PROD_CONTAINER="${PROD_CONTAINER:-game-prod-postgres}"
ENV_FILE="${ENV_FILE:-.env.production}"

FORCE=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --force)   FORCE=1 ;;
    --dry-run) DRY_RUN=1 ;;
    *) echo "未知参数: $arg"; exit 1 ;;
  esac
done

log()  { printf "[migrate] %s\n" "$*"; }
ok()   { printf "[  ok  ] %s\n" "$*"; }
warn() { printf "[ warn ] %s\n" "$*"; }
die()  { printf "[ fail ] %s\n" "$*" >&2; exit 1; }

docker info >/dev/null 2>&1 || die "Docker 未运行"
# ───── 通过一次性容器读取开发库 ─────
# 注意：postgres 官方镜像挂载已有数据卷时不会自动启动，
# 需以 postgres 用户执行 initdb 校验并手动启动，再执行查询。
dev_psql() {
  local sql="$1"
  docker run --rm \
    -v "$DEV_VOLUME":/var/lib/postgresql/data \
    --user postgres \
    postgres:16-alpine \
    sh -c "pg_ctl -D /var/lib/postgresql/data -o '-c listen_addresses=' -w start >/dev/null 2>&1; \
           trap 'pg_ctl -D /var/lib/postgresql/data -m fast stop >/dev/null 2>&1' EXIT; \
           psql -U postgres -d guide_platform -tAc \"$sql\"" 2>/dev/null | tr -d ' \r'
}

dev_pg_dump() {
  docker run --rm \
    -v "$DEV_VOLUME":/var/lib/postgresql/data \
    --user postgres \
    postgres:16-alpine \
    sh -c "pg_ctl -D /var/lib/postgresql/data -o '-c listen_addresses=' -w start >/dev/null 2>&1; \
           trap 'pg_ctl -D /var/lib/postgresql/data -m fast stop >/dev/null 2>&1' EXIT; \
           pg_dump -U postgres -d guide_platform --data-only --no-owner --no-privileges" 2>/dev/null
}

[[ -f "$ENV_FILE" ]] || die "缺少 $ENV_FILE"
PG_USER=$(grep -E '^DB_USERNAME=' "$ENV_FILE" | cut -d= -f2-)
[[ -n "$PG_USER" ]] || die "$ENV_FILE 中缺少 DB_USERNAME"

# ───── 读取开发库（挂载开发卷的临时容器）─────
count_dev() {
  dev_psql "SELECT count(*) FROM game;"
}

count_prod() {
  docker exec "$PROD_CONTAINER" psql -U "$PG_USER" -d guide_platform -tAc \
    "SELECT count(*) FROM game;" 2>/dev/null | tr -d ' \r'
}

DEV_N=$(count_dev || echo "0")
PROD_N=$(count_prod || echo "0")

log "开发库（卷 $DEV_VOLUME）游戏数: ${DEV_N}"
log "生产库（$PROD_CONTAINER）游戏数: ${PROD_N}"

if [[ "$DEV_N" == "0" ]]; then
  warn "开发库为空，跳过。如需初始化演示数据请先运行 crawler 下的 sync_* 脚本。"
  exit 0
fi

if [[ "$DEV_N" == "$PROD_N" && "$FORCE" -eq 0 ]]; then
  ok "两库数据量一致，无需迁移"
  exit 0
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  log "--dry-run 模式，未做任何改动"
  exit 0
fi

if [[ "$FORCE" -eq 0 ]]; then
  warn "即将用开发库数据**覆盖**生产库（生产库现有 ${PROD_N} 款游戏将被替换为 ${DEV_N} 款）"
  read -r -p "确认继续？输入 yes 继续：" ans
  [[ "$ans" == "yes" ]] || { log "已取消"; exit 0; }
fi

# ───── 导出 → 导入 ─────
TMP_SQL=$(mktemp /tmp/guide_migrate_XXXXXX.sql)
trap 'rm -f "$TMP_SQL"' EXIT

log "1/3 从开发卷导出数据…"
dev_pg_dump > "$TMP_SQL"
SIZE=$(wc -c < "$TMP_SQL" | tr -d ' ')
log "    导出 $(echo "$SIZE" | awk '{printf "%.1f", $1/1048576}') MB"

log "2/3 清空目标表…"
# 先按外键反序清空，避免依赖顺序问题
TABLES=$(docker exec "$PROD_CONTAINER" psql -U "$PG_USER" -d guide_platform -tAc \
  "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename <> 'flyway_schema_history';" \
  2>/dev/null | tr -d ' \r' | tac | tr '\n' ' ')
for t in $TABLES; do
  docker exec "$PROD_CONTAINER" psql -U "$PG_USER" -d guide_platform -tAc \
    "TRUNCATE TABLE \"$t\" RESTART IDENTITY CASCADE;" >/dev/null 2>&1 || true
done
ok "    已清空 ${TABLES% } 等表"

log "3/3 导入数据…"
docker exec -i "$PROD_CONTAINER" psql -U "$PG_USER" -d guide_platform \
  < "$TMP_SQL" > /tmp/migrate_import.log 2>&1 || true
# flyway_schema_history 主键冲突属预期（表结构由迁移脚本管理，不重复导入）
ERRS=$(grep -c "ERROR" /tmp/migrate_import.log 2>/dev/null || echo 0)
NON_FLYWAY=$(grep "ERROR" /tmp/migrate_import.log 2>/dev/null | grep -vc "flyway_schema_history_pk" || echo 0)
if [[ "$NON_FLYWAY" -gt 0 ]]; then
  warn "导入中有 $NON_FLYWAY 个非 flyway 相关错误："
  grep "ERROR" /tmp/migrate_import.log | grep -v "flyway_schema_history_pk" | head -5 | sed 's/^/       /'
else
  ok "    导入完成（仅 flyway 历史记录重复，已忽略）"
fi

# ───── 验证 ─────
log "验证生产库…"
docker exec "$PROD_CONTAINER" psql -U "$PG_USER" -d guide_platform -c "
SELECT 'game' AS 表, count(*) FROM game
UNION ALL SELECT 'guide', count(*) FROM guide
UNION ALL SELECT 'article', count(*) FROM article
UNION ALL SELECT 'game_character', count(*) FROM game_character
UNION ALL SELECT 'game_weapon', count(*) FROM game_weapon
UNION ALL SELECT 'game_artifact_set', count(*) FROM game_artifact_set
UNION ALL SELECT 'game_mechanic_rule', count(*) FROM game_mechanic_rule;" 2>/dev/null

ok "迁移完成"