#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 生产部署脚本
#
#   ./scripts/deploy.sh up          首次部署（构建 + 启动）
#   ./scripts/deploy.sh up --no-build   仅重启（镜像已存在）
#   ./scripts/deploy.sh status      查看状态
#   ./scripts/deploy.sh logs        跟踪日志
#   ./scripts/deploy.sh health      健康检查
#   ./scripts/deploy.sh down        停止（保留数据）
#   ./scripts/deploy.sh rollback    回滚到上一个镜像标签
#
# 设计要点：
#   1. 启动前强制校验 .env.production 中的必填项，绝不带着 CHANGE_ME 上线
#   2. 关键环境变量不写入日志，避免密钥泄露
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

# macOS 自带bash 3.2 在 UTF-8 locale 下解析中文标点（如「。」「：」）时，
# 会把紧邻中文的 $VAR 误判为变量名的一部分，导致 `unbound variable`。
# 固定为C locale 可规避（脚本内的中文提示在 C locale 下仍能正确输出字节）。
export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT=gameaibot
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
ENV_EXAMPLE=".env.production.example"

# ───── 颜色输出 ─────
if [[ -t 1 ]]; then
  RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[0;33m'; CYA='\033[0;36m'; RST='\033[0m'
else
  RED=''; GRN=''; YLW=''; CYA=''; RST=''
fi

log()  { printf "${CYA}[deploy]${RST} %s\n" "$*"; }
ok()   { printf "${GRN}[ ok ]${RST} %s\n" "$*"; }
warn() { printf "${YLW}[warn]${RST} %s\n" "$*"; }
die()  { printf "${RED}[fail]${RST} %s\n" "$*" >&2; exit 1; }

compose() {
  docker compose -p "$PROJECT" -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
}

# 从 .env.production 读取配置到当前 shell。
# compose 的 --env-file 只对 docker 命令生效，
# 脚本自身用到的 HTTP_PORT 等变量必须单独加载，否则会误用默认值。
load_env() {
  [[ -f "$ENV_FILE" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
}

# ───── 前置校验 ─────
preflight() {
  command -v docker >/dev/null 2>&1 || die "未找到 docker，请先安装 Docker"

  docker info >/dev/null 2>&1 || die "Docker 守护进程未运行，请先启动 Docker"

  [[ -f "$ENV_FILE" ]] || die "缺少 $ENV_FILE。请先执行：cp $ENV_EXAMPLE $ENV_FILE 并填入真实配置"

  # 权限检查：含密钥的文件不应全局可读
  local perm
  perm=$(stat -f '%Lp' "$ENV_FILE" 2>/dev/null || stat -c '%a' "$ENV_FILE" 2>/dev/null || echo "")
  if [[ -n "$perm" && "$perm" != "600" && "$perm" != "400" ]]; then
    warn "$ENV_FILE 权限为 $perm，建议执行 chmod 600 $ENV_FILE"
  fi

  # 必填项校验：绝不允许 CHANGE_ME 占位符上线
  local required=(
    DB_USERNAME DB_PASSWORD REDIS_PASSWORD MINIO_USER MINIO_PASSWORD
    JWT_SECRET OAUTH_REDIRECT_URL
  )
  local missing=()
  local val
  for key in "${required[@]}"; do
    val=$(grep -E "^${key}=" "$ENV_FILE" | head -1 | cut -d= -f2- || true)
    if [[ -z "$val" || "$val" == CHANGE_ME* ]]; then
      missing+=("$key")
    fi
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    die "${ENV_FILE} 中以下必填项未设置或仍是占位符：${missing[*]} —— 请编辑该文件填入真实值（JWT_SECRET 可用 openssl rand -base64 48 生成）"
  fi

  # JWT 强度检查
  local jwt
  jwt=$(grep -E '^JWT_SECRET=' "$ENV_FILE" | cut -d= -f2-)
  if [[ ${#jwt} -lt 32 ]]; then
    die "JWT_SECRET 长度不足 32 字符（当前 ${#jwt}），请用 openssl rand -base64 48 重新生成"
  fi

  ok "前置校验通过（${#required[@]} 项必填配置已就绪）"
}

# ───── 健康检查 ─────
health_check() {
  load_env
  local port="${HTTP_PORT:-80}"
  log "等待服务就绪（最多 180 秒）..."

  local deadline=$((SECONDS + 180))
  while (( SECONDS < deadline )); do
    # 1) 前端
    local fe
    fe=$(curl -fsS -o /dev/null -w '%{http_code}' "http://localhost:${port}/healthz" 2>/dev/null || echo 000)
    # 2) 后端就绪探针（经Nginx 反代）
    local be
    be=$(curl -fsS -o /dev/null -w '%{http_code}' "http://localhost:${port}/actuator/health/readiness" 2>/dev/null || echo 000)

    if [[ "$fe" == "200" && "$be" == "200" ]]; then
      ok "服务已就绪 → http://localhost:${port}"
      return 0
    fi
    printf "  等待中… 前端=%s 后端=%s\n" "$fe" "$be"
    sleep 5
  done

  warn "健康检查超时，请查看日志：./scripts/deploy.sh logs"
  return 1
}

# ───── 命令分发 ────
cmd="${1:-up}"
BUILD_FLAG=""

case "$cmd" in
  up)
    shift || true
    [[ "${1:-}" == "--no-build" ]] && BUILD_FLAG="--no-build"

    preflight
    load_env
    log "构建并启动生产服务…"
    if [[ -n "$BUILD_FLAG" ]]; then
      compose up -d
    else
      compose up -d --build
    fi

    if health_check; then
      compose ps
      echo ""

      # 新建的环境数据卷是空的，这里主动检查并提示，
      # 避免出现"页面能开但没有数据"的情况（本项目踩过）。
      local games
      games=$(compose exec -T postgres psql -U "$DB_USERNAME" -d "${DB_NAME:-guide_platform}" \
              -tAc "SELECT count(*) FROM game;" 2>/dev/null | tr -d ' \r')
      if [[ -n "$games" && "$games" == "0" ]]; then
        warn "数据库为空（游戏表 0 条），页面将没有数据。"
        warn "请执行数据迁移：./scripts/migrate-data.sh"
      else
        ok "数据库已有 $games 款游戏"
      fi
      echo ""
      ok "部署完成。访问：http://localhost:${HTTP_PORT:-80}"
    else
      echo ""
      warn "部署未完全就绪，最近日志："
      compose logs --tail=60 backend
      exit 1
    fi
    ;;

  status)
    compose ps
    ;;

  logs)
    shift || true
    if [[ -n "${1:-}" ]]; then
      compose logs -f "$1"
    else
      compose logs -f
    fi
    ;;

  health)
    load_env
    port="${HTTP_PORT:-80}"
    printf "前端 /healthz                   → %s\n" \
      "$(curl -fsS -o /dev/null -w '%{http_code}' "http://localhost:${port}/healthz" 2>/dev/null || echo 不可达)"
    printf "后端 /actuator/health           → %s\n" \
      "$(curl -fsS -o /dev/null -w '%{http_code}' "http://localhost:${port}/actuator/health" 2>/dev/null || echo 不可达)"
    printf "后端 /actuator/health/readiness → %s\n" \
      "$(curl -fsS -o /dev/null -w '%{http_code}' "http://localhost:${port}/actuator/health/readiness" 2>/dev/null || echo 不可达)"
    printf "接口  /api/v1/games→ %s\n" \
      "$(curl -fsS -o /dev/null -w '%{http_code}' "http://localhost:${port}/api/v1/games" 2>/dev/null || echo 不可达)"
    printf "SPA    /games                → %s\n" \
      "$(curl -fsS -o /dev/null -w '%{http_code}' "http://localhost:${port}/games" 2>/dev/null || echo 不可达)"
    ;;

  down)
    log "停止服务（数据卷保留）…"
    compose down
    ok "已停止"
    ;;

  rollback)
    warn "回滚需手动指定上一个镜像标签，示例："
    echo "  docker compose -p $PROJECT -f $COMPOSE_FILE --env-file $ENV_FILE up -d backend:<上一个标签>"
    ;;

  *)
    echo "用法: $0 {up [--no-build]|status|logs [服务名]|health|down|rollback}"
    exit 1
    ;;
esac