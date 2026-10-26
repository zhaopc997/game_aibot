# 生产部署指南

> 目标：**一条命令**完成部署，且默认安全（缺密钥即拒绝启动）。

## 快速开始

```bash
# 1. 准备配置（仅首次）
cp .env.production.example .env.production
openssl rand -base64 48# 生成 JWT 密钥，填入 .env.production 的 JWT_SECRET
chmod 600 .env.production                # 含密钥，限制为仅所有者可读

# 2. 部署
./scripts/deploy.sh up                   # 构建镜像 + 启动 + 等待健康

# 3. 验证
./scripts/deploy.sh health
```

访问 http://localhost（端口由 `.env.production` 的 `HTTP_PORT` 决定）。

## 架构

```
                    ┌─────────────────────────────┐
   浏览器 ─────────▶│ frontend (nginx:80)         │
                    │  · 托管 dist 静态资源        │
                    │  · SPA history fallback      │
                    │  · /api /ws 反向代理 ────┐│
                    └─────────────────────────┼────┘
                                              ▼
                    ┌─────────────────────────────┐
                    │ backend (Spring Boot:8080)  │
                    │  profile=prod│
                    │  无任何默认密钥              │
                    └──────────┬──┬──┬────────────┘
                               │  │  │
              ┌────────────────┘  │  └──────────────┐
              ▼                   ▼                 ▼
      ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
      │ postgres:16  │   │ redis:7│   │ elasticsearch │
      │  （不暴露端口）  │   │ requirepass │   │   8.13.4     │
      └──────────────┘   └──────────────┘   └──────────────┘
```

**关键设计**：数据层**不映射到宿主机端口**，只在容器网络内可达，
避免数据库/ES 直接暴露到公网。对外只有 Nginx 一个入口。

## 安全设计

| 项 | 做法 |
|---|---|
| 密钥 | `.env.production` 中无默认值，缺任一项**启动即失败** |
| JWT_SECRET | 要求 ≥32 字符，脚本自动校验 |
| 默认密钥 | `application-prod.yml` 中所有敏感项写作 `${VAR}`（无默认值） |
| 演示数据 | `app.seed.enabled: false`，不写入 admin 账号 |
| OAuth | `app.oauth.mock: false`，禁止任意邮箱登录 |
| 错误信息 | `include-stacktrace/message/binding-errors: never` |
| SQL 日志 | `org.hibernate.SQL: WARN` |
| 依赖服务 | 不暴露宿主机端口 |
| 容器用户 | 后端以非 root（`app` 用户）运行 |
| 静态资源 | 带 hash 的资源长缓存 1 年，`index.html` 不缓存 |
| 安全响应头 | CSP / X-Frame-Options / X-Content-Type-Options |

## 部署脚本命令

| 命令 | 说明 |
|---|---|
| `./scripts/deploy.sh up` | 构建 + 启动 + 等待健康（首次部署） |
| `./scripts/deploy.sh up --no-build` | 仅重启（镜像已存在时更快） |
| `./scripts/deploy.sh status` | 查看容器状态与健康 |
| `./scripts/deploy.sh logs [服务]` | 跟踪日志，如 `logs backend` |
| `./scripts/deploy.sh health` | 逐项健康检查（前端/后端/接口/SPA） |
| `./scripts/deploy.sh down` | 停止（**保留数据卷**） |

## 健康检查端点

| 端点 | 用途 |
|---|---|
| `GET /healthz` | Nginx 容器存活 |
| `GET /actuator/health` | 应用整体状态 |
| `GET /actuator/health/liveness` | 存活探针（K8s livenessProbe） |
| `GET /actuator/health/readiness` | 就绪探针（含 db/redis） |

`show-details: never`，不对外暴露依赖细节。暴露面已收敛为
`health,info,metrics` 三项（`/actuator/env`、`/heapdump` 等**未开放**）。

## 数据持久化

| 卷 | 用途 |
|---|---|
| `prod-pgdata` | PostgreSQL 数据 |
| `prod-redisdata` | Redis 持久化（AOF） |
| `prod-esdata` | Elasticsearch 索引 |
| `prod-miniodata` | MinIO 对象存储 |
| `prod-uploads` | 用户上传文件 |
| `prod-logs` | 应用日志 |

> `down` 不会删除卷。彻底清理需手动 `docker volume rm`。

## 首次上线检查表

- [ ] `JWT_SECRET` 已改为随机值（非 CHANGE_ME）
- [ ] 数据库密码、Redis 密码、MinIO 密码已改为强密码
- [ ] `OAUTH_REDIRECT_URL` 改为真实域名
- [ ] `chmod 600 .env.production`
- [ ] `.env.production` 未提交到 Git（`.gitignore` 已配`*.env.production`）
- [ ] 若使用云数据库/Redis，改为外连并**移除**对应本地服务
- [ ] `LLM_ENABLED=true` 时已填入 `OPENAI_API_KEY`
- [ ] 开放了 80/443 端口，防火墙已配置
- [ ] 已配置 HTTPS（生产**必须**，可在 Nginx 前置 TLS 终结）

## 常见问题

**启动失败，提示占位符**
`.env.production` 里有 `CHANGE_ME`。脚本会明确列出哪几项未填。

**后端反复重启**
```bash
./scripts/deploy.sh logs backend | tail -80
```
常见原因：数据库密码不一致、Redis 密码未同步、`JWT_SECRET` 太短。

**前端 502**
后端尚未就绪。`depends_on: service_healthy` 会等待，若仍失败看后端日志。

**SPA 刷新 404**
Nginx 缺 `try_files`。确认 `frontend/nginx.conf` 中`location /` 含该指令。

**数据要回滚**
```bash
./scripts/deploy.sh down
docker compose -p gameaibot -f docker-compose.prod.yml --env-file .env.production \
  down -v   # ⚠️ 删除卷，数据不可恢复
```

## 尚未覆盖（生产加固建议）

- **HTTPS**：当前 Nginx 只监听 80，生产建议前置 TLS 终结（Caddy / 云 LB / certbot）
- **数据库备份**：`prod-pgdata` 无自动备份，建议加定时 `pg_dump` + 对象存储
- **日志集中**：当前输出到 `prod-logs` 卷，建议接Loki / ELK
- **多实例**：当前为单节点，需要水平扩展时把数据层换为托管服务（云 RDS /云 Redis）

## ⚠️ 重要：开发库与生产库是两套独立数据

这是本项目最容易踩的坑。

| 环境 | compose 文件 | 数据卷 | 端口 |
|---|---|---|---|
| 开发 | `docker-compose.local.yml` | `gameaibot_pgdata` | 5432 |
| 生产 | `docker-compose.prod.yml` | `gameaibot_prod-pgdata` | 不暴露 |

**新建生产环境时，生产数据卷是全新的空库**，Flyway 只建表、不插数据，
所以首次上线后页面会是空的（游戏列表、攻略、英雄/武器/装备全部缺失）。

### 解决：迁移数据

```bash
./scripts/migrate-data.sh --dry-run    # 先看两库差异
./scripts/migrate-data.sh              # 确认后迁移（会先清空目标表）
```

脚本会把开发库的数据导入生产库，并跳过 `flyway_schema_history` 的主键冲突
（表结构由迁移脚本管理，不需要复制）。

### 演示数据从哪来

开发库的数据由crawler 下的脚本导入：

```bash
cd crawler
export PG_HOST=localhost PG_PORT=5432 PG_DB=guide_platform PG_USER=postgres PG_PASSWORD=postgres
../.venv-crawler/bin/python scripts/sync_genshin_full_stats.py    # 原神
../.venv-crawler/bin/python scripts/sync_lol_full_stats.py# 英雄联盟
../.venv-crawler/bin/python scripts/sync_starrail_full_stats.py  # 星穹铁道
../.venv-crawler/bin/python scripts/sync_arknights_full_stats.py  # 明日方舟
../.venv-crawler/bin/python scripts/sync_elden_ring_full_stats.py # 艾尔登法环
../.venv-crawler/bin/python scripts/sync_wukong_full_stats.py    # 黑神话
../.venv-crawler/bin/python scripts/sync_zelda_full_stats.py     # 塞尔达
```

游戏列表与攻略等基础内容来自 `DataSeeder`（需 `app.seed.enabled=true`）。

> 注意：crawler 脚本里写死的 game_id 必须与当前数据库一致。
> 已知失效：王者荣耀=24、绝区零=25 在当前库（id 只到 22）中不存在，
> 对应脚本会报错，需先修正 id 再运行。

## HTTPS 接入（生产必须）

当前默认编排只监听 HTTP，**JWT 与登录凭据会明文传输**，公网部署前必须加 TLS。
已提供基于 Caddy 的方案（自动申请并续期 Let's Encrypt 证书，不用手工 certbot + cron）。

### 前置条件

1. 一个已解析到本机公网 IP 的域名（A 记录）
2. 开放 **80**（ACME HTTP-01 质询）与 **443** 端口

### 步骤

```bash
# 1. 补充环境变量
cat >> .env.production <<'EOF'
SITE_DOMAIN=your-domain.com
ACME_EMAIL=you@example.com
# 关键：明文端口只绑回环，公网只能走 443
HTTP_PORT=127.0.0.1:8088
EOF

# 2. 用 TLS 叠加文件启动
docker compose -p gameaibot \
  -f docker-compose.prod.yml -f docker-compose.tls.yml \
  --env-file .env.production up -d

# 3. 验证
curl -I https://your-domain.com
```

### 两个设计说明

**1. 为什么把 `HTTP_PORT` 设为 `127.0.0.1:8088`**

compose 的 `ports` 是**追加**语义，叠加文件无法移除 `prod.yml` 里已声明的映射。
与其依赖 `!reset`（各 compose 版本支持不一致，本项目实测过端口叠加踩坑），
不如让明文端口只绑定回环地址 —— 公网访问只能走 Caddy 的 443，效果等同且更稳。

**2. 证书存储必须持久化**

`prod-caddydata` 卷保存证书与 ACME 账号。**切勿删除**，
否则每次重启都会重新签发，容易触发 Let's Encrypt 速率限制。

### 首次部署建议先用测试环境

Let's Encrypt 正式环境有速率限制（每周同域名 5 次）。
首次调试把 `deploy/caddy/Caddyfile` 里的 `acme_ca` 换成：

```
acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
```

调通后再切回正式地址（staging 签发的证书浏览器不信任，属正常）。

### 若已有云负载均衡 / 网关

也可不在本机做 TLS，改由云 LB 终结：
- 云 LB 监听 443，回源到本机 `8088`（HTTP）
- 此时**不要**把 8088 暴露到公网，安全组只放行 LB 来源 IP
- 后端已支持 `X-Forwarded-Proto`，OAuth 回调地址记得改成 `https://`

## 备份与监控（运维必备）

### 数据库备份

```bash
./scripts/backup-db.sh              # 执行一次备份
./scripts/backup-db.sh --list       # 查看已有备份
./scripts/backup-db.sh --verify backups/xxx.dump   # 校验能否恢复
```

特性：
- `pg_dump -Fc` 自定义格式（压缩 + 支持选择性恢复），实测 30 篇攻略的库约 976K
- **备份后立即用 `pg_restore --list` 校验完整性** —— 未校验的备份等于没有备份
- 默认保留 7 天（`KEEP_DAYS` 可调），自动清理过期文件
- 备份目录默认 `./backups`，可用 `BACKUP_DIR` 指向挂载盘 / 网络存储

**定时执行**（每天 03:30）：

```bash
crontab -e
30 3 * * * cd /path/to/游戏攻略 && ./scripts/backup-db.sh >> /var/log/game-backup.log 2>&1
```

> 重要：备份应放到**与数据库不同的物理设备**（另一块盘 / 对象存储）。
> 同盘备份在磁盘故障时一起丢失，等于没备份。

### 健康巡检

```bash
./scripts/health-check.sh           # 人类可读
./scripts/health-check.sh --quiet   # 仅异常时输出（cron 用）
```

覆盖项（退出码 0=正常 / 1=异常）：

| 类别 | 检查内容 |
|---|---|
| 容器 | 6 个服务的运行状态与 healthcheck |
| 服务 | 前端 /healthz、后端 health/readiness、游戏列表接口 |
| 数据 | 游戏数、攻略数、角色数（防"库空了服务还活着"） |
| **搜索索引** | `guides` 与 `guide_chunks` 的文档数是否与攻略数匹配 |
| **搜索功能** | 实际搜一个关键词，验证命中数 > 0 |

后两项是**本项目最关键的健康指标**。此前曾出现"ES 索引写入全部失败 → 搜索与 AI 助手完全不可用"，
而容器健康检查全绿、日志显示成功、页面无报错，问题潜伏很久才被发现 ——
根因就是没有任何指标覆盖索引条数与搜索命中率。

**定时巡检 + 告警**：

```bash
*/10 * * * * cd /path/to/游戏攻略 && ./scripts/health-check.sh --quiet >> /var/log/game-health.log 2>&1 || echo "游戏平台巡检异常" | mail -s "ALERT" you@example.com
```

### 快速重建后端镜像

```bash
./scripts/build-backend.sh            # 约 1~2 分钟（宿主机编译 + 容器 COPY jar）
./scripts/build-backend.sh --skip-mvn # 仅重建镜像
```

对比 `docker compose build backend`（约 10 分钟）：标准 Dockerfile 在容器内跑 Maven，
`dependency:go-offline` 不完整导致每次重复下载约 500 个依赖。
本脚本改为**宿主机编译**（`~/.m2` 已预热）+ 容器内只 `COPY` jar，
实测可把重建时间压到 1~2 分钟。

> 正式 CI 环境仍建议用标准 `Dockerfile`（构建可复现、不依赖宿主环境），
> 或为 BuildKit 配置 `--mount=type=cache,target=/root/.m2`。
