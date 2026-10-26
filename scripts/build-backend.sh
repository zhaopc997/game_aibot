#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# 后端快速构建
#
#   ./scripts/build-backend.sh            # 构建 jar + 镜像
#   ./scripts/build-backend.sh --skip-mvn # 只重建镜像（jar 已最新）
#
# 相比 `docker compose build backend`（约 10 分钟），本脚本约 1~2 分钟：
# 依赖下载与编译在宿主机完成（~/.m2 已预热），容器内只做 COPY。
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

export LC_ALL=C
export LANG=C

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SKIP_MVN=0
[[ "${1:-}" == "--skip-mvn" ]] && SKIP_MVN=1

log() { printf "[build] %s\n" "$*"; }
ok()  { printf "[  ok  ] %s\n" "$*"; }
die() { printf "[ fail ] %s\n" "$*" >&2; exit 1; }

command -v docker >/dev/null || die "未找到 docker"
command -v mvn    >/dev/null || die "未找到 mvn"

START=$(date +%s)

if [[ "$SKIP_MVN" -eq 0 ]]; then
  log "1/2 宿主机编译（Maven）…"
  ( cd backend && mvn -q package -DskipTests ) || die "Maven 构建失败，详见上方输出"
  ok "编译完成"
else
  log "跳过 Maven 编译（--skip-mvn）"
fi

JAR=$(ls backend/target/*.jar 2>/dev/null | grep -v '\.original' | head -1 || true)
[[ -n "$JAR" ]] || die "未找到 backend/target/*.jar，请先执行 mvn package"
log "使用产物：$JAR（$(du -h "$JAR" | cut -f1)）"

log "2/2 构建镜像…"
# 本地快路径默认用经典构建器：
# 该 Dockerfile 只做 COPY，没有 BuildKit 专属特性；
# 而部分受限环境（如沙箱）会禁止 BuildKit 写 ~/.docker/buildx，
# 导致 "failed to update builder last activity time" 而失败。
# 需要 BuildKit 时显式传 DOCKER_BUILDKIT=1。
export DOCKER_BUILDKIT="${DOCKER_BUILDKIT:-0}"
docker build -f backend/Dockerfile.fast -t game-platform-backend:latest backend/ \
  || die "镜像构建失败"

END=$(date +%s)
echo ""
ok "镜像已更新：game-platform-backend:latest（耗时 $((END-START)) 秒）"
echo ""
echo "  重启服务使其生效："
echo "    docker compose -p gameaibot -f docker-compose.prod.yml --env-file .env.production up -d backend"