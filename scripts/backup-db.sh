#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# PostgreSQL 自动备份
#
#   ./scripts/backup-db.sh                 # 执行一次备份
#   ./scripts/backup-db.sh --list          # 列出已有备份
#   ./scripts/backup-db.sh --verify <file> # 校验某个备份能否恢复
#
# 定时任务（每天 03:30）：
#   crontab -e
#   30 3 * * * cd /path/to/游戏攻略 && ./scripts/backup-db.sh >> /var/log/game-backup.log 2>&1
#
# 关键设计：
#   1. 用 pg_dump 自定义格式（-Fc），支持并行恢复与压缩
#   2. 备份完立即用 pg_restore --list 校验完整性 —— 未校验的备份等于没有备份
#   3. 保留天数可配（默认 7 天），自动清理过期文件
#   4. 备份目录可用环境变量指向挂载盘/网络存储
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-.env.production}"
BACKUP_DIR="${BACKUP_DIR:-$ROOT/backups}"
KEEP_DAYS="${KEEP_DAYS:-7}"
COMPOSE_ARGS=(-p gameaibot -f docker-compose.prod.yml --env-file "$ENV_FILE")

log() { printf "[backup] %s\n" "$*"; }
ok()  { printf "[  ok  ] %s\n" "$*"; }
warn() { printf "[ warn ] %s\n" "$*"; }
die() { printf "[ fail ] %s\n" "$*" >&2; exit 1; }

# ───── 子命令 ─────
case "${1:-}" in
  --list)
    [[ -d "$BACKUP_DIR" ]] || { echo "尚无备份目录"; exit 0; }
    echo "备份目录：$BACKUP_DIR"
    ls -lh "$BACKUP_DIR"/*.dump 2>/dev/null | awk '{printf "  %-52s %s\n", $9, $5}' || echo "  无备份文件"
    exit 0
    ;;
  --verify)
    F="${2:-}"
    [[ -f "$F" ]] || die "文件不存在：$F"
    log "校验 $F …"
    docker run --rm -v "$(cd "$(dirname "$F")" && pwd)":/b postgres:16-alpine \
      pg_restore --list "/b/$(basename "$F")" > /tmp/restore_list.txt 2>/tmp/restore_err.txt \
      || die "校验失败：$(head -3 /tmp/restore_err.txt)"
    N=$(grep -c "TABLE DATA" /tmp/restore_list.txt || true)
    ok "校验通过，含 $N 张表的数据"
    exit 0
    ;;
esac

# ───── 前置检查 ─────
[[ -f "$ENV_FILE" ]] || die "缺少 $ENV_FILE"
docker info >/dev/null 2>&1 || die "Docker 未运行"

PG_USER=$(grep -E '^DB_USERNAME=' "$ENV_FILE" | cut -d= -f2-)
PG_DB=$(grep -E '^DB_NAME=' "$ENV_FILE" | cut -d= -f2-); PG_DB="${PG_DB:-guide_platform}"
[[ -n "$PG_USER" ]] || die "$ENV_FILE 缺少 DB_USERNAME"

CID=$(docker compose "${COMPOSE_ARGS[@]}" ps -q postgres 2>/dev/null || true)
[[ -n "$CID" ]] || die "postgres 容器未运行"

mkdir -p "$BACKUP_DIR"

TS=$(date +%Y%m%d_%H%M%S)
OUT="$BACKUP_DIR/${PG_DB}_${TS}.dump"

log "1/4 导出数据库 $PG_DB …"
# -Fc 自定义格式：压缩 + 支持 pg_restore 选择性恢复；-Z6 兼顾速度与体积
docker exec "$CID" pg_dump -U "$PG_USER" -d "$PG_DB" -Fc -Z6 > "$OUT" 2>/tmp/dump_err.txt \
  || die "pg_dump 失败：$(head -3 /tmp/dump_err.txt)"

SIZE=$(du -h "$OUT" | cut -f1)
ok "已生成 $OUT（$SIZE）"

# ───── 完整性校验 ─────
log "2/4 校验备份完整性 …"
docker run --rm -v "$BACKUP_DIR":/b postgres:16-alpine \
  pg_restore --list "/b/$(basename "$OUT")" > /tmp/restore_list.txt 2>/dev/null \
  || die "备份文件损坏：pg_restore --list 失败"
TABLE_N=$(grep -c "TABLE DATA" /tmp/restore_list.txt || true)
ok "校验通过，含 $TABLE_N 张表的数据"

# ───── 清理过期备份 ─────
log "3/4 清理超过 ${KEEP_DAYS} 天的备份 …"
DELETED=0
while IFS= read -r f; do
  rm -f "$f" && DELETED=$((DELETED + 1))
done < <(find "$BACKUP_DIR" -name '*.dump' -type f -mtime +"$KEEP_DAYS" 2>/dev/null || true)
ok "已清理 $DELETED 个过期备份"

# ───── 上传到 COS（可选，失败不影响本地备份）─────
if [[ -f "$ROOT/.cos.env" ]]; then
  log "4/4 上传到 COS …"
  # shellcheck disable=SC1091
  set -a; . "$ROOT/.cos.env"; set +a
  PYTHONPATH="${COS_PY_PATH:-/opt/cos-tools/lib}" \
    python3 "$ROOT/scripts/upload-backup-to-cos.py" "$OUT" \
    && ok "已上传 COS（异地副本）" \
    || warn "COS 上传失败，本地备份已保留（不影响恢复）"
fi

echo ""
ok "备份完成：$OUT（$SIZE，$TABLE_N 张表）"
echo "  恢复命令："
echo "    docker exec -i \$CID pg_restore -U $PG_USER -d $PG_DB --clean --if-exists < $OUT"