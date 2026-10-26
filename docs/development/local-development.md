# Local Development

## 环境要求

| 依赖 | 版本 | 说明 |
|---|---|---|
| JDK | 17+ | pom 声明 `java.version=17`；Lombok 需 ≥ 1.18.48 才能在较新 JDK 上编译 |
| Maven | 3.9+ | |
| Node.js | 18+ | 前端构建 |
| Docker / Docker Compose | 任意近期版本 | 用于起 PG / Redis / ES / MinIO |

## 端口约定

`backend/src/main/resources/application.yml` 的默认值已与 `docker-compose.yml` 对齐：

| 服务 | 宿主机端口 | 环境变量覆盖 |
|---|---|---|
| PostgreSQL | 5432 | `DB_URL` / `DB_USERNAME` / `DB_PASSWORD` |
| Redis | 6379 | `REDIS_HOST` / `REDIS_PORT` |
| Elasticsearch | 9200 | `ES_URIS` |
| MinIO | 9000（控制台 9001） | — |
| 后端 | 8080 | — |
| 前端 (Vite) | 5180 | `npm run dev -- --port` |

> 改宿主机端口时，请同步修改 compose 映射或通过上述环境变量覆盖，
> 否则会出现"compose 起来了但应用连不上"的情况。

## 启动步骤

### 1. 启动依赖服务

```bash
docker compose up -d
docker compose ps   # 等待 postgres/redis/elasticsearch 健康
```

> 若不想用 Docker，需自行准备 PostgreSQL 16、Redis 7、Elasticsearch 8.13，
> 并用环境变量把 `application.yml` 中的默认地址指向你的实例。

### 2. 初始化数据库

**无需手工执行 SQL**：Flyway 会在后端启动时自动按版本执行
`backend/src/main/resources/db/migration/` 下的 V1 → V2 → V3。

> `sql/schema.sql` 已废弃（内容等同 V1 但缺 V2/V3 六张表），请勿手工执行。

### 3. 配置 LLM（可选）

```bash
export OPENAI_API_KEY=<你的 SiliconFlow/OpenAI key>
```

未配置时 RAG 走纯 BM25，AI 攻略生成走 Mock 实现，其余功能不受影响。

### 4. 启动后端

```bash
cd backend
mvn spring-boot:run
```

健康检查：`curl http://localhost:8080/api/v1/games`

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5180`。Vite 已配置 `/api` 与 `/ws` 代理到后端 8080。

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 编译报 `TypeTag::UNKNOWN` | Lombok 版本过旧 / 未 fork 外部 javac | pom 已锁定 Lombok ≥1.18.48 且开启 `fork`，确认本地 `~/.m2` 中有对应 jar |
| 启动报缺表 | 用了 `sql/schema.sql` 建库 | 删库重建，交给 Flyway 初始化 |
| ES 查询报连不上 | `ES_URIS` 与实际端口不一致 | 用 `curl http://localhost:9200` 核对 |

## 本机端口占用与本地 compose（2026-10 补充）

本机 6379 / 9200 / 9000 已被其他项目占用：

| 端口 | 占用者 |
|---|---|
| 6379 | `mishop-redis` |
| 9200 | `mishop-elasticsearch` |
| 9000 / 9001 | `ti-smart-agent-deep-minio` |

因此新增 `docker-compose.local.yml`（**独立文件，不是 override**），用独立端口 + 独立容器名 + 独立数据卷，
不触碰既有容器：

| 服务 | 本地端口 |
|---|---|
| PostgreSQL | 5432 |
| Redis | 6380 |
| Elasticsearch | 9201（容器内 9200） |
| MinIO | 9100 / 9101 |

> 注意：compose 的 `ports` 是**追加而非替换**语义。
> 用 `-f docker-compose.yml -f docker-compose.local.yml` 叠加会产生重复映射且不生效，
> 必须单独使用 `-f docker-compose.local.yml`。

### 启动命令

```bash
# 1. 依赖服务（中文目录名必须显式指定 project name）
docker compose -p gameaibot -f docker-compose.local.yml up -d

# 2. 后端（显式指定端口与依赖地址）
cd backend
REDIS_PORT=6380 ES_URIS=http://localhost:9201 SERVER_PORT=8080 mvn spring-boot:run

# 3. 前端
cd frontend && npm run dev
```

访问 http://localhost:5180

### 未配置项（可预期行为）

- 未设 `OPENAI_API_KEY` 时，AI 相关接口返回 `LLM API 401 Token is invalid`，不影响其他功能
- 此时 RAG 自动降级为纯 BM25（未启用向量检索）
- MinIO 已启动但后端文件上传走 `LocalStorageService`，暂未使用 MinIO

### 演示账号

`admin / admin123`（由 `DataSeeder` 创建，生产环境请置 `app.seed.enabled=false`）

### 前端端口为何是 5180

`5173` 与本机另一个项目（拼豆乐园）冲突：同一端口上 IPv4/IPv6 被不同进程分别绑定，
浏览器访问 `localhost` 时命中哪个取决于解析顺序，表现为「有时能打开、有时打开的是别的项目」。

已改为 `5180` 并开启 `strictPort: true`——端口再被占用时 vite 会直接报错，
而不是静默漂移到随机端口导致你不知道实际跑在哪。

改端口只需改 `frontend/vite.config.ts` 的 `server.port`；
后端代理指向的是 `127.0.0.1:8080`（后端端口），**不受前端端口变化影响，无需同步修改**。
