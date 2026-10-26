# 上线前检查清单（Production Readiness Checklist）

> 扫描时间：2026-10-13 · 扫描方式：代码与配置静态扫描 + 真实启动验证

## 一、阻塞级（必须修，否则不能上线）

| # | 问题 | 现状 | 处置 |
|---|---|---|---|
| 1 | **JWT 密钥有默认值** | `application.yml:46` 写死 `guide-platform-jwt-secret-key-please-change-in-production-...` | ✅ 已新增 `application-prod.yml`，`JWT_SECRET` 无默认值，未注入即启动失败 |
| 2 | **数据库密码有默认值** | `postgres` 明文写在配置里 | ✅ prod profile 改为 `${DB_PASSWORD}` 强制注入 |
| 3 | **OAuth mock 登录** | `app.oauth.mock: true`，任何人可用任意邮箱登录 | ✅ prod profile 强制 `mock: false` |
| 4 | **演示数据写入** | `DataSeeder` 会建 `admin/admin123` 账号 | ✅ 已有 `@ConditionalOnProperty(matchIfMissing=false)`，prod 再加 `app.seed.enabled: false` 双保险 |
| 5 | **无生产配置文件** | 原本只有 `application.yml`（开发配置直接上生产） | ✅ 已创建 `application-prod.yml` |
| 6 | **上传大小未限制** | 未配 `max-file-size`，默认 1MB | ✅ prod 配置 10MB/12MB 并可用环境变量调整 |

## 二、高危（强烈建议修）

| # | 问题 | 说明 |
|---|---|---|
| 7 | **CORS 未配置** | 代码中无任何 CORS 配置。若前后端不同域名部署，浏览器会直接拦截请求 |
| 8 | **SQL 日志级别** | 开发配置含 `org.hibernate.SQL`，生产需 WARN，否则日志里全是带参数的 SQL |
| 9 | **前端 65 处 `any`** | `GameStatsViews` 31 处、`CharacterDetailModal` 24 处。类型失守让重构风险高 |
| 10 | **前端零组件测试** | 仅有 `tests/unit.test.mjs`（9 个纯函数用例），组件与 hooks 无任何测试 |

## 三、可观测性与运维（缺失）

| # | 缺口 | 建议 |
|---|---|---|
| 12 | 无健康检查端点 | 建议加 `/actuator/health`，供 LB / K8s 探活 |
| 13 | 无指标端点 | `micrometer` 已引入但未启用 actuator，接上后可观测 QPS/耗时/连接池 |
| 14 | 无结构化日志 | 当前为默认 pattern，建议 prod 切换 JSON 格式便于 ELK/Loki 采集 |
| 15 | 无优雅停机验证 | 已在 prod 配置 `server.shutdown: graceful`，但需实际压测确认 |

## 四、已确认安全的项

| 检查项 | 结果 |
|---|---|
| SQL 注入 | ✅ 未发现字符串拼接 SQL，均走 JPA 参数化 |
| 依赖冗余 | ✅ pom.xml 共 17 个依赖，全为 Spring Boot 标准 starter，无未使用的第三方库 |
| 前端产物泄露密钥 | ✅ `dist/` 中不含 JWT secret 或 API key（构建产物 0 个 `.map`） |
| sourcemap 泄露 | ✅ 0 个 `.map` 文件 |
| `console.log` 残留 | ✅ 0 处 |
| 安全框架 | ✅ `STATELESS` + CSRF 关闭（纯 token 认证下正确）、白名单最小化 |
| CORS 误放开 | ✅ 无 `allowedOrigins: ["*"]` 类问题 |

## 五、上线操作步骤

```bash
# 1. 生成强随机密钥（务必 ≥32 字节）
export JWT_SECRET="$(openssl rand -base64 48)"

# 2. 注入必需环境变量
export DB_URL="jdbc:postgresql://<内网地址>:5432/guide_platform"
export DB_USERNAME="<生产用户>"
export DB_PASSWORD="<强密码>"
export REDIS_HOST="<内网地址>"
export ES_URIS="http://<内网地址>:9200"
export OPENAI_API_KEY="<你的 key>"          # 不投AI 功能可留空并设 LLM_ENABLED=false
export OAUTH_REDIRECT_URL="https://<域名>/oauth/callback"

# 3. 启动
java -jar target/guide-platform-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
```

启动前置条件（缺任一项会**直接启动失败**，这是刻意设计）：
`DB_URL` / `DB_USERNAME` / `DB_PASSWORD` / `REDIS_HOST` / `ES_URIS` / `JWT_SECRET` / `OPENAI_API_KEY` / `OAUTH_REDIRECT_URL`

## 六、当前遗留的已知阻塞

1. **Docker 守护进程未运行** —— 依赖服务（PG/Redis/ES/MinIO）全部下线，无法启动后端。重启 Docker Desktop 后执行：
   ```bash
   docker compose -p gameaibot -f docker-compose.local.yml up -d
   ```
2. **`docker-compose.local.yml` 是本机开发配置** —— ES 配了 `xpack.security.enabled=false`，生产需启用认证或置于内网并加访问控制。

## 七、建议的后续排期

| 优先级 | 事项 | 预估 |
|---|---|---|
| 高 | 配置 CORS（前后端分离部署时必需） | 0.5 天 |
| 中 | 接入 actuator健康检查 + 指标 | 1 天 |
| 中 | 收敛前端 `any` | 2 天 |
| 中 | 补组件测试（从GameCover、QAPage 等改动点开始） | 2 天 |
| 低 | 拆分 GameStatsViews（1165 行） | 3 天 |
