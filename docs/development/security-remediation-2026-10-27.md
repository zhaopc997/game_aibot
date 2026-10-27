# 渗透测试问题整改报告

> 对应《helozero.com 安全测试报告》（2026-10-26）· 整改完成时间：2026-10-27

## 一、核对结论：10 项发现全部属实

逐项对照代码与线上实际行为后确认，报告中 **10 项发现全部真实存在**，无一项误报。
报告中第 12 节主动纠正的两处初判（"搜索接口 SQL 注入"、"登录接口 500"）
判断正确 —— 前者是分词检索的 OR 语义而非注入，后者是测试传错字段名。

| 编号 | 问题 | 核实结果 | 证据 |
|---|---|---|---|
| F-01 | 认证接口无限流与失败锁定 | ✅ 属实 | `RateLimitInterceptor` 原为统一 1000 次/分钟，对登录形同虚设；无失败计数 |
| F-02 | Refresh Token 无轮换、可无限复用 | ✅ 属实 | `AuthService.refresh()` 仅验签后签发新令牌，服务端零状态 |
| F-03 | `/api` 跳转使用明文 http | ✅ 属实 | 实测 `Location: http://helozero.com/api/` |
| F-04 | 主页面缺 CSP 等安全头 | ✅ 属实 | 实测首页仅 4 个头，无 CSP / Permissions-Policy |
| F-05 | 用户枚举 | ✅ 属实 | 注册分别返回「用户名已存在」「邮箱已注册」；登录对不存在用户直接抛异常（时序差） |
| F-06 | 密码策略过弱 | ✅ 属实 | `@Size(min = 6, max = 128)`，`12345678` 可注册 |
| F-07 | 令牌存 localStorage | ✅ 属实 | 前端 `localStorage.getItem('guide_access_token')` |
| F-08 | 未实现端点返回 500 | ✅ 属实 | 兜底 `Exception` 处理器把 `NoResourceFoundException` 也归为 500 |
| F-09 | 参数类型错误返回 500 | ✅ 属实 | 同上，`MethodArgumentTypeMismatchException` 未单独处理 |
| F-10 | 服务端未做输入净化 | ✅ 属实 | `createQuestion` 无 `@Valid`，HTML 原样入库 |

---

## 二、逐项修复方案与实施

### F-03 · `/api` 明文跳转 ✅ 已修复

**根因**：`/api` 未匹配到任何控制器，请求落到后端由 Spring 做尾部斜杠规范化，
生成的 `Location` 使用 `http://` + 内部地址（实测 `http://127.0.0.1/api/`）。
转发头（`X-Forwarded-Proto/Host`、`Forwarded`）实测均无法影响它。

**修复**：在 Caddy 层拦截，显式指定 scheme。`redir` 在 Caddy 指令顺序中先于
`reverse_proxy`，因此请求不会再落到后端产生错误跳转。

```caddy
@apiBare path /api
redir @apiBare https://helozero.com/api/ 301
```

**验证**：`curl -I https://helozero.com/api` → `301 location: https://helozero.com/api/` ✓

---

### F-04 · 缺失安全响应头 ✅ 已修复

**修复**：在 Caddy 统一补齐。落在边缘而非应用，可覆盖静态页与 API 全部响应。

| 头 | 值 | 作用 |
|---|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; ...` | 限制 XSS 后果 |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), ...` | 禁用不需要的强能力 |
| `Cross-Origin-Opener-Policy` | `same-origin` | 防 window.opener 滥用 / Spectre |
| `X-Permitted-Cross-Domain-Policies` | `none` | 禁止跨域策略文件 |

两个放开的点，都是必要的：
- `img-src ... https:` —— 图片托管在 COS，必须允许
- `style-src 'unsafe-inline'` —— Vite 注入样式所需，不涉及脚本执行

已确认构建产物 `index.html` **只有一个外链 module script、无内联脚本**，
因此 `script-src 'self'` 可以收紧到位。

**验证**：首页响应已带上全部 4 个头，站点资源均 200 ✓

---

### F-01 · 登录/注册限流与失败锁定 ✅ 已修复

**原状**：统一 1000 次/分钟，且无失败锁定 —— 攻击者每分钟可试 1000 个密码。

**修复分两层，因为单一手段都有缺口**：

| 层 | 手段 | 挡住的攻击 |
|---|---|---|
| 边缘（IP 维度） | 登录 10 次/分、注册 10 次/时、刷新 30 次/分 | 单点暴力破解、批量注册 |
| 应用（账号维度） | 同账号连续失败 10 次 → 锁 15 分钟；同 IP 失败 30 次 → 锁 15 分钟 | 分布式撞库（换 IP 也绕不过账号维度）、慢速爆破（每分钟 1 次不触发限流） |

计数存 Redis 带 TTL，自动解锁；Redis 不可用时 **fail-open**（可用性优先），
仍有 IP 限流兜底。加 `Retry-After` 头减少客户端盲目重试。

> **注册限制取 10 次/小时而非报告建议的 5 次**：同一出口 IP（学校/公司 NAT）
> 可能有多个真实用户，5 次会误伤；有账号维度锁定兜底，防刷效果不受影响。

**实施中揪出的一个真问题**：初版限流用 `X-Real-IP` 取客户端 IP，
实测打出来的 key 是 `auth:fail:ip:172.19.0.1`（Docker 网关地址）。
原因是链路为 `浏览器 → Caddy → 前端 nginx(8088) → 后端`，
而 nginx 里 `proxy_set_header X-Real-IP $remote_addr` 把真实 IP **覆盖成了网关地址**。

**若按网关地址计数，全站用户会共用一个配额 —— 一个人触发限流就会把所有人挡在门外，
比不限流更糟。** 已抽出 `ClientIpResolver` 统一解析：优先取
`X-Forwarded-For` 首跳（Caddy 会整体替换该头，可信），并跳过内网/回环地址。
修复后 key 为真实公网 IP。

**验证**：连续失败第 10 次 → `429「请求过于频繁」`；Redis 中
`auth:fail:user:*` 与 `auth:fail:ip:<真实IP>` 均正常计数 ✓

---

### F-02 · Refresh Token 轮换与复用检测 ✅ 已修复

**原状**：`refresh()` 只验签就发新令牌，服务端零状态 ——
令牌泄露后 7 天内可无限续期，用户也无法"登出"。

**修复**：新增 `refresh_token` 表（`V4__refresh_token.sql`），只存 **SHA-256 摘要**
（库泄露也无法反推可用令牌），实现三件事：

1. **轮换**：每次刷新把旧记录置 `revoked_at` 并写入 `replaced_by`，旧令牌立即失效；
2. **复用检测**：已吊销的令牌再次出现 → 判定被复制 → **吊销该用户全部令牌**
   （正常客户端换到新令牌后不会再用旧的）；
3. **主动吊销**：登出 / 封号时立即失效（JWT 无状态，本做不到）。

另加每日 04:30 清理 30 天前过期记录，避免表无限增长。

**验证**：
- 首次刷新 → 200 且签发新令牌（已轮换）✓
- 用**旧**令牌再刷 → `401`（复用检测生效）✓
- 登出后旧令牌 → `401` ✓

---

### F-08 · 未实现端点返回 500 ✅ 已修复

**根因**：`@ExceptionHandler(Exception.class)` 兜底把 `NoResourceFoundException`
也归入 500。**这会让监控被伪 500 淹没，真实故障反而看不见。**

**修复**：按 HTTP 语义逐一归类。

| 情形 | 修复前 | 修复后 |
|---|---|---|
| 路径不存在 `NoResourceFoundException` | 500 | **404** |
| 方法不支持 | 500 | **405** + `Allow` 头 |
| 请求体格式错 | 500 | **400** |
| Content-Type 不支持 | 500 | **415** |
| 真正的未预期异常 | 500 | 500（保留） |

同时**实现 `/api/v1/auth/logout`**（原为 500）—— 这是 F-02 的前置依赖，
也是用户"无法主动登出"的直接解法。

**验证**：`/api/v1/qa` → 404；`/api/v1/favorites` → 405（只支持 POST，语义正确）；
`/api/v1/admin/ops` → 404；`/users/me` → 200；`/auth/logout` → 200 ✓

---

### F-05 · 用户枚举 ✅ 已修复

**修复**：
1. 注册冲突统一文案「用户名或邮箱已被占用，请更换后重试」，不再区分是哪个冲突；
2. 登录时**用户不存在也执行一次 BCrypt 比对**（对一个构造期算好的假哈希），
   消除「不存在几毫秒返回 / 存在要等 BCrypt 几十毫秒」的时序侧信道；
3. 登录错误文案本来就统一（报告这点判断有误，实际已是「用户名或密码错误」）。

**验证**：用户名冲突与邮箱冲突返回完全一致的文案 ✓

---

### F-06 · 密码策略 ✅ 已修复

**修复**：新增 `@StrongPassword` 校验器：

- 长度 8–128（原 6 起）；
- 必须同时含字母与数字；
- 常见弱口令黑名单（`12345678`、`password`、`qwerty123`、`woaini1314` 等）；
- 拒绝全相同字符（`11111111`）与连续序列（`12345678`、`abcdefgh`）。

**不强制特殊字符**：研究表明强制符号会诱导用户使用 `Password1!` 这类高预测性模式，
长度 + 弱口令黑名单的实际收益更高（参考 OWASP 建议）。

**验证**：`12345678` → `400「密码至少 8 位，且需同时包含字母和数字」`；
强密码可正常注册 ✓

---

### F-09 · 参数类型错误返回 400 ✅ 已修复

见 F-08 的异常归类表。**验证**：`/guides/abc`、`/guides?size=abc` 均 → 400 ✓

---

### F-10 · 服务端输入净化 ✅ 已修复（限纯文本字段）

**修复**：新增 `@NoHtml` 校验器，拒绝包含 HTML 标签或脚本伪协议的输入。
`Question.title / description` 已加约束，`createQuestion` 补 `@Valid` 使其生效。

**选择「拒收」而非「清洗」**：静默剥标签会让用户以为提交成功、实际内容被改得面目全非；
直接报错更清晰。

**范围说明**：仅应用于**本就应为纯文本**的字段（问答、评论）。
文章正文如果设计上允许富文本，需要的是「HTML 白名单净化」（如 OWASP Java HTML Sanitizer），
不能简单拒收 —— 这部分未动，见"未做项"。

**验证**：含 `<img src=x onerror=...>` 的提问 → `400` ✓

---

### F-07 · 令牌存 localStorage ⏸ 未在本轮改动

**原因**：这不是配置问题，是**前后端认证架构的整体改造** ——
需改为 HttpOnly + Secure + SameSite Cookie，并配套 CSRF 防护、刷新流程重写、
前端拦截器重构。改动面大、回归风险高，不适合与其余 9 项混在一次发布里。

**当前风险可控的原因**：
- 实测未发现可利用的 XSS（React JSX 自动转义，应用层未用 `dangerouslySetInnerHTML`）；
- F-04 的 CSP 已上线，进一步压缩 XSS 注入面；
- F-02 的轮换 + 吊销已上线，令牌泄露的影响窗口从「7 天无限续期」缩短为「最多 30 分钟」；
- F-10 已阻止 HTML 入库，切断了存储型 XSS 的存量来源。

**建议**：作为独立迭代排期，与 CSRF 配套一起做。

---

### F-14 · 测试残留数据 ✅ 已清理

删除 23 个测试账号（`sectest*`、`probe1-20`、`pw_*`）及 6 条测试内容
（含 XSS payload 的提问、`正常标题测试`、回答 `hax`）。
脚本 `sql/cleanup-pentest-data.sql` 事务包裹、逐表按外键顺序删除、执行前后各打统计。

> 过程中发现自己的一个 SQL bug：`username LIKE 'pw[_]%'` 在 PostgreSQL 里
> **不是**字符类语法（`[` 是字面量），导致 `pw23cdc185` 漏删。
> 已改为 `'pw\_%' ESCAPE '\'`。

清理后：用户 2 个（admin、tester[已禁用]）、提问 10 条（均为演示内容）。

---

## 三、验证汇总

`scripts/verify-security-fixes.sh` 可重复执行，覆盖全部可自动化验证的项：

| 项 | 结果 |
|---|---|
| F-06 弱密码被拒 | ✓ 400 |
| F-06b 强密码可注册 | ✓ 200 |
| F-05 冲突文案统一 | ✓ 一致 |
| F-09 参数错误 → 400 | ✓ |
| F-08 未实现端点 → 404 | ✓ |
| F-10 HTML 输入被拒 | ✓ 400 |
| F-02 轮换生效 | ✓ 新令牌 ≠ 旧令牌 |
| F-02 复用检测 | ✓ 旧令牌 401 |
| F-08b logout 可用 | ✓ 200 |
| F-08b 登出后令牌失效 | ✓ 401 |
| F-01 失败限流 | ✓ 第 10 次 429 |
| F-03 跳转协议 | ✓ https |
| F-04 安全头 | ✓ 4 个头全部存在 |

**待人工确认**：F-07（架构改造，未做）。

---

## 四、附带发现并修复的问题

### 真实 IP 解析错误（严重，会导致全站误伤）

详见 F-01。若按 Docker 网关地址限流，一个人触发就会挡住所有用户。
已用 `ClientIpResolver` 统一解析，限流与登录记录都走它。

### nginx 覆盖 `X-Real-IP`（同类根因）

`frontend/nginx.conf` 中 `proxy_set_header X-Real-IP $remote_addr;`
把 Caddy 传来的真实 IP 覆盖为网关地址。后端已不依赖该头
（优先取 `X-Forwarded-For` 首跳），但 nginx 这处仍应在下次前端构建时改为
透传 `$http_x_real_ip`，避免误导后来者。

---

## 五、后续建议

| 优先级 | 事项 | 说明 |
|---|---|---|
| P1 | F-07 令牌迁移 HttpOnly Cookie + CSRF | 需独立迭代与完整回归 |
| P1 | 文章正文的 HTML 白名单净化 | 若允许富文本，需 OWASP Java HTML Sanitizer |
| P2 | 登录设备管理 / 一键下线 | `refresh_token` 表已存 `client_ip`/`user_agent`，基础具备 |
| P2 | 密码强度黑名单接入完整字典 | 当前为内置常见弱口令，可换 rockyou 前 10 万条 |
| P2 | 令牌复用触发告警 | 目前只记 WARN 日志，可接邮件/Webhook |
| P3 | 接入真实 LLM 后重测提示注入 | 当前为模板降级模式，接入后攻击面变化 |
