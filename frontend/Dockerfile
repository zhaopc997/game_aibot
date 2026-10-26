# ═══════════════════════════════════════════════════════════════
# 前端生产镜像：构建 → Nginx 托管
# ═══════════════════════════════════════════════════════════════

# ───── 阶段 1：构建静态产物 ─────
FROM node:22-alpine AS build

WORKDIR /build

# 先只拷依赖清单，利用层缓存
COPY package.json package-lock.json* ./
# npm ci 失败时退回 install（无 lock 文件的场景）
RUN npm ci || npm install

COPY . .

# API 基址：生产走同域相对路径（由 Nginx 反代 /api），无需注入后端地址
ENV VITE_API_BASE_URL=/api

RUN npm run build

# ───── 阶段 2：Nginx 托管 ─────
FROM nginx:1.27-alpine

COPY --from=build /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]