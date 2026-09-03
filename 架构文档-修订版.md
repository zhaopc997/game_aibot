# 游戏攻略平台架构文档（修订版）

> 本文档基于原版架构文档修订，主要修订点：
> 1. 技术栈按阶段精简（MVP 采用 PG + Redis + MinIO 三件套，ES/MQ 延后引入）
> 2. 修正 iOS 悬浮窗不可行问题，补充替代方案
> 3. 补充权限/角色、通知、内容审核等数据模型
> 4. 明确定义攻略状态机
> 5. 补充 AI 任务幂等/降级、版本通知防轰炸等工程细节
> 6. 明确模块化单体 → 微服务的演进触发条件
> 7. 完善 API 规范（统一响应、分页、上传、限流）
> 8. 补充 SLO 监控与告警

---

## 1. 项目概述

本平台旨在为玩家提供结构化、可信、实时、个性化的游戏攻略服务，解决当前攻略信息碎片化、过时、可信度低等问题。核心特色包括：AI 智能攻略聚合、攻略版本管理、互动式攻略、个性化推荐、游戏内悬浮窗（桌面端）等。

**目标用户**：游戏玩家（硬核/休闲）、攻略创作者、游戏厂商合作方。

**核心价值**：让玩家快速找到适配自己游戏进度和版本的攻略，让创作者高效产出结构化内容。

**设计原则**：
- **快速验证**：MVP 阶段控制技术复杂度，优先验证核心痛点（攻略查找与时效性）。
- **渐进演进**：从模块化单体起步，按量化标准决定是否拆分为微服务。
- **成熟优先**：优先采用成熟稳定的开源方案，降低团队上手成本。

---

## 2. 技术选型

### 2.1 技术栈总览

| 层次 | 技术 | 说明 |
|------|------|------|
| 前端（Web） | React 18 + TypeScript + Vite | 响应式设计，支持 PC/移动端浏览器 |
| 前端（移动 App） | Flutter 3.x | 跨平台，一套代码打包 iOS/Android |
| 桌面悬浮窗 | Electron (Windows/macOS) | 仅桌面端实现游戏内悬浮层，需系统级窗口置顶和透明 |
| 后端服务 | Java 17 + Spring Boot 3.x（模块化单体优先） | 成熟生态，便于快速开发，后期可拆分微服务 |
| 数据库（关系型） | PostgreSQL 16 | 存储用户、攻略、评论等核心关系数据 |
| 缓存 | Redis 7 | 热点数据缓存、会话存储 |
| 对象存储 | MinIO（初期）/ 阿里云 OSS（生产可选） | 图片、视频、附件存储 |
| AI 服务 | 调用大模型 API（GPT-4o / Claude / 文心一言等） | 用于 AI 聚合解析、问答助手、内容生成 |
| 推荐系统 | 初期：规则 + Redis 行为缓存 + 定时任务 | 后期可引入 Spark/Flink 或现成推荐引擎 |
| 容器化 | Docker + Kubernetes | 部署与扩展 |
| CI/CD | GitHub Actions（初期）/ GitLab CI（可选） | 自动化构建部署 |

### 2.2 按阶段的中间件引入策略

**为避免 MVP 阶段基础设施过重，按阶段引入中间件：**

| 阶段 | 引入组件 | 说明 |
|------|----------|------|
| MVP（2-3个月） | PostgreSQL + Redis + MinIO | 三件套支撑全部核心功能 |
| 第二阶段（3-6个月） | RabbitMQ | 异步处理（AI 任务、通知、审核） |
| 第二阶段 | Elasticsearch 8 | 全文搜索、标签筛选（由 PG tsvector 迁移） |
| 第三阶段（6-12个月） | Kafka（可选） | 仅当日志流处理/大规模事件驱动需求出现时引入 |

**阶段迁移说明**：
- **搜索**：MVP 阶段用 PG 内置 `tsvector` 全文检索 + 标签过滤，验证搜索需求；第二阶段数据量增长后迁移 ES。
- **异步**：MVP 阶段用 Spring Event + 线程池 + 定时任务补偿；第二阶段引入 RabbitMQ。
- **消息队列定案**：**首选 RabbitMQ**（功能全、运维简单、生态成熟），Kafka 仅留待日志流/实时计算场景，二者不同时启用。

---

## 3. 系统架构

### 3.1 总体架构

采用**模块化单体**架构，核心业务按领域模块划分，便于初期快速开发，后期可平滑拆分为微服务。

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│  Web前端 (React)  移动App (Flutter)  桌面悬浮窗 (Electron)   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                      接入层（分阶段）                        │
│  MVP：Nginx（反代/限流/SSL）                                 │
│  微服务化后：Spring Cloud Gateway + Nginx                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      应用服务层（模块化单体）                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ 用户服务    │  │ 内容服务    │  │ 社区服务    │          │
│  │ (认证/资料) │  │ (攻略/资讯) │  │ (评论/问答) │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ AI服务      │  │ 推荐服务    │  │ 工具服务    │          │
│  │ (聚合/问答) │  │ (个性化)    │  │ (模拟器)    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ 版本服务    │  │ 通知服务    │  │ 审核服务    │          │
│  │ (版本管理)  │  │ (推送/邮件) │  │ (内容安全)  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                        数据层                                │
│  PostgreSQL  Redis  MinIO                                   │
│  （第二阶段：+ RabbitMQ  Elasticsearch）                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 模块说明

- **用户服务**：注册登录、OAuth2（Steam/PSN/微信等）、个人资料、等级积分、角色权限。
- **内容服务**：攻略、资讯、百科的 CRUD，版本关联，结构化内容存储。
- **社区服务**：评论、点赞、收藏、问答、论坛。
- **AI 服务**：AI 聚合解析、攻略问答机器人、内容生成辅助。
- **推荐服务**：基于用户画像和行为日志的个性化推荐。
- **工具服务**：互动地图、Build 模拟器、抽卡分析等小工具。
- **版本服务**：游戏版本库、攻略版本时间线、过期提醒。
- **通知服务**：站内信、邮件、推送。
- **审核服务**：文本/图像审核、人工复审队列。

### 3.3 模块化单体 → 微服务演进

**拆分触发条件（满足任意一条即考虑拆分）：**
1. 某模块团队规模达到 2 个以上独立小组。
2. 某模块需要独立扩缩容（如 AI 服务 CPU 密集，峰值与其他接口差异大）。
3. 单模块故障持续影响其他模块，需要独立隔离。
4. 部署/发布节奏冲突（模块 A 高频发布、模块 B 低频稳定）。

**拆分顺序建议**：
1. **AI 服务最先拆**（CPU 密集、需独立扩缩容、与核心链路异步解耦）。
2. **通知服务**次之（纯异步、易独立部署）。
3. **内容服务**视流量情况（读写比例高、缓存复杂）。

**拆分注意事项**：拆分前先通过接口防腐层（对外只暴露领域接口）、事件驱动（Spring Event → RabbitMQ）完成逻辑解耦，避免"物理拆分、逻辑不拆"。

---

## 4. 数据库设计（核心表）

### 4.0 公共约定

- 所有表使用 `bigint` 自增主键（或雪花 ID），统一 `created_at` / `updated_at` 时间戳。
- 软删除统一使用 `deleted_at` 字段（NULL 表示未删除）。
- 文本内容默认 UTF-8，长文本用 `text` 类型。

### 4.1 用户相关

- `user` (id, username, email, password_hash, avatar, bio, level, exp, status, created_at, updated_at)
  - `status`：`NORMAL` / `DISABLED` / `PENDING_VERIFY`
- `user_game_profile` (id, user_id, game_id, role_info JSON, progress JSON, updated_at)  -- 玩家游戏档案
- `follow` (follower_id, followee_id, created_at)
- `user_points_log` (id, user_id, action, points, created_at)
- `user_role` (id, user_id, role, created_at)  -- 角色：`USER` / `CREATOR` / `MODERATOR` / `ADMIN`（新增）

### 4.2 内容相关

- `game` (id, name, alias, platform, category, cover_url, description, current_version)
- `game_version` (id, game_id, version_number, release_date, patch_notes)
- `guide` (id, game_id, version_id, title, author_id, type, difficulty, tags, summary, content JSON, status, like_count, useful_count, verify_count, created_at, updated_at)
  - `content` 采用 JSON 存储结构化步骤节点：
    ```json
    {
      "steps": [
        {
          "step_id": 1,
          "title": "准备阶段",
          "description": "...",
          "images": ["url1"],
          "video": "url",
          "conditions": ["角色A等级>80"],
          "tools": ["地图标记"]
        }
      ]
    }
    ```
  - `status` 状态机（详见 4.6）：
    `DRAFT → PENDING_REVIEW → PUBLISHED ⇄ PENDING_VERIFICATION → OUTDATED / ARCHIVED`
- `guide_version_history` (id, guide_id, version_id, content_snapshot, updated_by, updated_at)  -- **关联游戏版本**的完整内容快照，用于版本差分对比
- `guide_revision` (id, guide_id, revision_number, changes_summary, created_at)  -- **作者编辑修订记录**，用于审计（与上表职责区分）
- `article` (id, game_id, title, author_id, category, content, published_at, status) -- 资讯/专栏
- `wiki_entry` (id, game_id, title, content, last_updated, version_id)

### 4.3 社区相关

- `comment` (id, target_type, target_id, parent_id, user_id, content, like_count, created_at, status)
- `like` (id, target_type, target_id, user_id, created_at)
- `favorite` (id, target_type, target_id, user_id, created_at)
- `question` (id, game_id, user_id, title, description, bounty_points, status, accepted_answer_id, created_at)
- `answer` (id, question_id, user_id, content, like_count, created_at)
- `report` (id, reporter_id, target_type, target_id, reason, status, handled_by, created_at)

### 4.4 AI 与推荐相关

- `ai_parse_task` (id, source_url, source_type, source_hash, status, result_guide_id, error_msg, created_at)
  - `source_hash` 唯一约束，防止重复提交（新增，保证幂等）
- `ai_qa_log` (id, user_id, question, answer, source_guides, created_at)
- `user_behavior_log` (id, user_id, action_type, target_type, target_id, context JSON, created_at) -- 用于推荐
- `behavior_batch` (id, batch_no, status, processed_at)  -- 行为日志批处理任务表（新增，用于定时聚合）

### 4.5 工具相关

- `interactive_map` (id, game_id, name, map_image_url, markers JSON)
- `build_simulator` (id, game_id, name, config JSON)  -- 模拟器配置
- `tool_usage_log` (id, tool_type, tool_id, user_id, created_at)

### 4.6 新增：权限、通知与审核

```sql
-- 内容审核表：机器审核 + 人工复审队列
content_review (
  id, target_type, target_id,            -- 攻略/评论/资讯等
  reviewer_id,                           -- 人工审核员（可为空）
  status,                                -- PENDING / PASSED / REJECTED / NEED_HUMAN
  reason,                                -- 审核结果或拒绝原因
  risk_level,                            -- LOW / MEDIUM / HIGH（机器初判）
  reviewed_at, created_at
)

-- 审计日志：敏感操作留痕
audit_log (
  id, operator_id, action,
  target_type, target_id,
  before_json, after_json,
  created_at
)

-- 通知表：支撑 5.8 节通知接口
notification (
  id, user_id, type,                     -- GUIDE_UPDATE / VERSION_OUTDATED / AI_TASK_DONE / SYSTEM
  title, content,
  related_type, related_id,
  is_read, created_at
)

-- 内容版权声明（攻略引用的外部来源）
content_source (
  id, guide_id, source_type,             -- BILI_VIDEO / WEB_POST / IMAGE / VIDEO
  source_url, source_title, license_note,
  created_at
)
```

**攻略状态机（`guide.status`）**：

```
DRAFT ──提交──▶ PENDING_REVIEW ──审核通过──▶ PUBLISHED
                  │                          │
                  │ 审核拒绝                  │ 游戏版本更新（宽限期后）
                  ▼                          ▼
              REJECTED                 PENDING_VERIFICATION
                                          │ 作者更新/声明兼容
                                          ▼
                                      PUBLISHED
                                          │ 长时间未更新
                                          ▼
                                      OUTDATED → ARCHIVED
```

各状态触发方：
- 作者：DRAFT、提交审核、编辑更新、声明兼容
- 审核员：REJECTED、PENDING_REVIEW→PUBLISHED
- 系统：游戏版本更新事件 → PENDING_VERIFICATION、OUTDATED、ARCHIVED

---

## 5. API 设计

### 5.0 通用规范

- **路径**：RESTful，版本前缀 `/api/v1`。
- **鉴权**：JWT（Access Token + Refresh Token），Access Token 有效期 30 分钟，Refresh Token 7 天。
- **统一响应格式**：
  ```json
  {
    "code": 0,
    "message": "success",
    "data": { }
  }
  ```
  - `code=0` 成功，非 0 为业务错误码（1001 参数错误、1002 未认证、1003 无权限、2001 资源不存在、3001 频率限制等）。
- **分页规范**：列表接口统一使用游标分页（防深翻页）：
  - 请求：`?cursor=<opaque>&limit=20`
  - 响应：`data` 含 `items` 与 `next_cursor`，`next_cursor` 为空表示无更多数据。
- **限流**：接入层按用户/IP 限流，默认 60 次/分钟/用户，AI 类接口 10 次/分钟。
- **上传接口**：图片/视频使用预签名 URL 直传对象存储，接口返回 `PUT url`，上传完成后回调确认。

### 5.1 用户模块

- `POST /auth/register` 注册
- `POST /auth/login` 登录
- `POST /auth/refresh` 刷新令牌（新增）
- `POST /auth/oauth/{provider}` 第三方登录
- `GET /users/me` 获取当前用户信息
- `PUT /users/me` 更新个人资料
- `GET /users/{id}/guides` 获取用户攻略列表
- `POST /users/me/game-profiles` 创建/更新游戏档案
- `GET /users/me/game-profiles/{gameId}` 获取指定游戏档案
- `POST /behaviors` 批量上报行为埋点（新增）

### 5.2 内容模块

- `GET /games` 游戏列表（支持筛选）
- `GET /games/{id}` 游戏详情
- `GET /games/{id}/guides?version=&type=&sort=` 获取攻略列表
- `POST /guides` 创建攻略（需登录）
- `GET /guides/{id}` 获取攻略详情（含结构化内容）
- `PUT /guides/{id}` 更新攻略
- `DELETE /guides/{id}` 删除攻略
- `POST /guides/{id}/submit-review` 提交审核（新增）
- `POST /guides/{id}/verify` 标记攻略有效/无效（验证机制）
- `GET /guides/{id}/versions` 获取攻略版本历史
- `GET /guides/{id}/diff?from=1.0&to=1.1` 获取版本差分
- `POST /guides/{id}/clone` 克隆攻略用于新版本
- `POST /uploads` 获取上传预签名 URL（新增）
- `GET /articles` 资讯列表
- `GET /wiki/{gameId}` 百科页面

### 5.3 社区模块

- `GET /comments?target_type=guide&target_id=123` 获取评论
- `POST /comments` 发表评论
- `POST /likes` 点赞/取消点赞
- `POST /favorites` 收藏
- `GET /questions?game_id=` 获取问答列表
- `POST /questions` 发布问题
- `POST /questions/{id}/answers` 回答问题
- `POST /questions/{id}/accept-answer` 采纳回答

### 5.4 AI 模块

- `POST /ai/parse` 提交 AI 聚合解析任务（输入 URL 或上传视频，服务端按 `source_hash` 幂等去重）
- `GET /ai/parse/{taskId}` 查询解析任务状态
- `POST /ai/qa` 向 AI 提问（返回结构化答案及来源攻略）
- `POST /ai/generate-draft` 根据录像/笔记生成攻略草稿（需登录，结果进入 DRAFT 状态）

### 5.5 推荐模块

- `GET /recommendations/feed` 个性化首页信息流
- `GET /recommendations/guides?game_id=` 基于用户档案的攻略推荐

### 5.6 工具模块

- `GET /tools/maps/{id}` 获取互动地图数据
- `POST /tools/maps/{id}/markers` 添加个人标记
- `GET /tools/simulators/{id}` 获取模拟器配置
- `POST /tools/simulators/{id}/calculate` 执行计算

### 5.7 版本模块

- `GET /games/{id}/versions` 获取游戏版本列表
- `POST /games/{id}/versions` 添加新版本（管理员/爬虫）
- `GET /guides/{id}/compatibility` 获取攻略兼容性状态
- `POST /guides/{id}/mark-outdated` 标记过期（用户反馈触发）

### 5.8 通知模块

- `GET /notifications` 获取通知列表
- `POST /notifications/read` 标记已读
- `WebSocket /ws/notifications` 实时通知推送（需心跳/断线重连/消息去重）

---

## 6. 关键功能实现方案

### 6.1 AI 智能攻略聚合

**流程**：
1. 用户提交来源（B 站视频链接、NGA 帖子 URL、截图等）。
2. 后端按 `source_hash` 去重（唯一约束），已存在则直接返回原任务，实现幂等。
3. 创建 `ai_parse_task` 并异步处理（MVP 用 Spring Event + 线程池，第二阶段切 RabbitMQ）。
4. AI 服务调用多模态大模型：
   - 视频：抽帧 + ASR 语音转文字 → 总结关键步骤。
   - 帖子：HTML 解析 → 提取文本 + 图片 → 理解内容。
5. 输出结构化 JSON（步骤节点、装备、条件等），**先落入 `guide.status=DRAFT` 草稿态**，不直接发布。
6. 大模型输出经过 JSON Schema 校验；**校验失败时降级为模板匹配**，不直接判失败。
7. 通知用户查看草稿，可人工编辑后提交审核。

**可靠性措施**：
- 任务幂等：`source_hash` 唯一约束 + 状态检查。
- 失败重试：自动重试 2 次（指数退避），仍失败进入人工队列。
- 内容合规：AI 生成内容标记来源（`content_source` 表），符合深度合成管理规定。

### 6.2 攻略版本管理与时效性

- 每篇攻略关联 `game_version_id`。
- 当 `game.current_version` 更新时，触发 Spring Event：
  1. **宽限期**：更新后 X 天内（建议 7 天）不触发过期标记，避免通知轰炸。
  2. 宽限期后，将该游戏下攻略标记为 `PENDING_VERIFICATION`，**支持作者批量"声明兼容"**。
  3. 通过通知服务提醒作者更新（可合并推送，不逐条轰炸）。
- 作者更新攻略时，系统自动创建版本快照（`guide_version_history`），提供差分对比视图。
- 用户搜索或浏览时，默认按当前版本筛选，也可手动切换历史版本。
- 列表和详情页展示"版本可能过期"提示。

**实现**：使用数据库触发器或 Spring Event 监听版本更新。

### 6.3 个性化推荐

**数据来源**：
- 用户游戏库（手动添加或 OAuth 同步 Steam/PSN）。
- 行为日志（客户端 `POST /behaviors` 批量上报）→ `user_behavior_log` → 定时聚合到 Redis。
- 用户游戏档案（角色进度）。

**推荐策略**：
- 协同过滤：基于相似用户的行为推荐（后期）。
- 内容过滤：基于攻略标签、难度、版本匹配度。
- 实时规则：用户最近正在玩的游戏 → 优先推荐该游戏最新攻略。

**技术实现**：
- 初期：Redis 存用户近期行为，定时任务（Spring Scheduler）计算推荐结果缓存到 Redis，`behavior_batch` 表记录批次进度。
- 后期：引入 Spark MLlib 或 Flink 进行离线/实时推荐。

### 6.4 互动式攻略

- **互动地图**：在地图图片上叠加标记点，前端使用 Canvas/SVG 渲染，标记数据存 JSON。
- **Build 模拟器**：后端提供游戏数据 API（角色、装备属性），前端实现拖拽和计算，也可后端计算返回。
- **进度追踪**：用户可标记任务/收集品完成状态，存储于 `user_game_profile` 的 JSON 字段，前端展示 Checklist。

### 6.5 悬浮窗功能

**可行性说明（重要修正）**：
- **桌面端**：Electron 开发独立窗口，设置 `alwaysOnTop`、`transparent`、`skipTaskbar` 等属性，实现悬浮于游戏之上。**可行**。
- **移动端 Android**：利用 `SYSTEM_ALERT_WINDOW` 权限（悬浮窗）。**可行，但需用户手动授权**。
- **移动端 iOS**：**不开放第三方悬浮窗权限**（PiP 仅限原生视频内容，API 受限），游戏内悬浮窗**不可行**。

**移动端替代方案**：
- iOS：提供**快捷栏小组件**（Widget）展示攻略步骤、**通知中心提醒**、或一键跳转主 App。
- Android：悬浮窗 + 主 App 联动。

**内容同步**：悬浮窗通过 WebSocket 与主应用保持实时通信，获取当前正在查看的攻略步骤，支持点击"下一步"切换。

**限制提示**：需注意游戏反作弊系统可能对第三方窗口的检测，建议仅提供浏览器模式或用户手动开启；首次使用需明确告知风险。

---

## 7. 非功能性需求与性能优化

### 7.1 性能目标与 SLO

| 指标 | 目标 |
|------|------|
| API 响应时间 | P95 < 300ms（普通接口），搜索 < 500ms |
| 攻略详情页首屏 | < 1s（配合 CDN 和缓存） |
| 并发支撑 | 峰值 1 万 QPS（利用缓存和水平扩展） |
| 可用性 | ≥ 99.9% |

### 7.2 缓存策略

- 热点攻略详情缓存到 Redis，过期时间 10 分钟，更新时主动失效。
- 游戏列表、版本信息等基础数据缓存 1 小时。
- 用户资料缓存 30 分钟。

**防击穿/防雪崩措施（新增）**：
- **缓存穿透**：对不存在的 ID 缓存空值（短 TTL 30s）；可选引入布隆过滤器拦截非法 ID。
- **缓存雪崩**：过期时间加随机抖动（±20%），避免同时失效；热点攻略加本地二级缓存（Caffeine，短 TTL）。
- **缓存击穿**：热点 key 用互斥锁（Redisson）重建，防止高并发同时回源。

### 7.3 搜索优化

- 索引攻略标题、内容摘要、标签、作者等字段（MVP 用 PG tsvector，第二阶段迁移 ES）。
- 支持错别字纠正（ES fuzzy 查询或同义词库）。
- 搜索结果排序权重公式：
  ```
  score = 0.4 × 文本相关度 + 0.3 × (useful_count / views) + 0.2 × 版本匹配 + 0.1 × 时间衰减
  ```
- PG→ES 同步：第二阶段采用 binlog/Canal 双写或定时增量同步。

### 7.4 内容安全

- 文本审核：接入第三方 API（如阿里云内容安全）或自训练模型，敏感词过滤。
- 图片审核：使用 AI 鉴黄/暴恐识别。
- 审核流程：机器初判 → 低风险自动通过，高风险（`risk_level=HIGH`）转入人工队列（`content_review` 表）。
- 机器审核通过后仍可被用户举报，人工复审。

### 7.5 监控与日志

**监控告警（新增 SLO 告警指标）**：
- API 可用率 < 99.9%（5 分钟窗口）→ 告警
- P95 延迟 > 300ms → 告警
- RabbitMQ 积压量 > 阈值 → 告警
- AI 任务成功率 < 95% → 告警
- ES 索引延迟 > 2s → 告警

**工具栈**：
- 指标：Prometheus + Grafana。
- 日志：ELK（Elasticsearch, Logstash, Kibana）或 Loki。
- 链路追踪：SkyWalking 或 Zipkin（模块化单体阶段可延后）。

---

## 8. 部署方案

- **环境划分**：开发、测试、预发布、生产。
- **容器化**：每个服务打包 Docker 镜像，Kubernetes 编排，支持滚动更新和自动扩缩容（HPA）。
- **数据库**：PostgreSQL 使用云数据库或主从复制，Redis 使用集群模式。
- **CDN**：静态资源（图片、视频）使用 CDN 加速，对象存储作为源站。
- **CI/CD 流水线**：
  1. 提交代码触发自动构建。
  2. 单元测试、代码扫描。
  3. 构建 Docker 镜像并推送仓库。
  4. 部署到测试环境，运行集成测试。
  5. 手动审批后部署到生产。

---

## 9. 开发阶段规划

### 第一阶段（MVP，2-3个月）

**技术栈**：PG + Redis + MinIO（不引入 ES/MQ）。

- 用户注册/登录、个人中心、角色权限基础。
- 攻略 CRUD、分步编辑器（基础版）、**攻略状态机**。
- 游戏库基础数据（手动录入/爬虫）。
- 攻略列表、详情、搜索（PG tsvector）。
- 评论、点赞、收藏基础互动。
- 简单版本字段（作者手动选择）。
- 统一响应格式、分页、上传（预签名 URL）。
- 后台管理基础功能（含审核队列初版）。

### 第二阶段（3-6个月）

**技术栈**：+ RabbitMQ、+ Elasticsearch。

- 攻略版本管理与时间线、版本差分对比。
- 有用/无用反馈与可靠度评分（排序权重公式落地）。
- AI 聚合解析（支持 B 站视频和网页，含幂等与降级）。
- 个性化推荐初版（基于标签和浏览历史）。
- 问答系统。
- 互动式地图（1-2 款热门游戏）。
- 创作者中心与激励体系。
- 内容安全（机器审核 + 人工复审队列）。

### 第三阶段（6-12个月）

- 游戏内悬浮窗（**仅桌面端 + Android**，iOS 用替代方案）。
- AI 问答助手。
- Build 模拟器。
- 用户游戏档案与进度追踪。
- 攻略悬赏功能。
- 深度个性化推荐（协同过滤）。
- 多平台同步（移动 App 发布）。
- 若触发拆分条件，开始微服务化（AI 服务优先）。

---

## 10. 总结

本架构设计以模块化单体起步，**按阶段控制技术复杂度**（MVP 三件套起步，ES/MQ 延后），兼顾快速迭代与未来扩展。核心差异化功能（AI 聚合、版本管理、互动式攻略）均通过独立服务模块实现，降低耦合。技术选型偏向成熟稳定的开源方案，确保团队可快速上手。

**本版相对原版的修订要点**：
1. **技术栈分阶段**：MVP 精简为 PG+Redis+MinIO，明确 ES/RabbitMQ/Kafka 引入时机。
2. **修正 iOS 悬浮窗**：明确不可行，给出小组件/通知中心替代方案。
3. **补齐数据模型**：角色、通知、内容审核、内容来源、行为批处理等表。
4. **明确攻略状态机**：定义完整状态流转与触发方。
5. **工程可靠性**：AI 任务幂等/降级、版本通知宽限期与批量声明、缓存防击穿。
6. **演进路径**：明确拆分触发条件、拆分顺序、防腐层要求。
7. **API 规范化**：统一响应、游标分页、预签名上传、限流。
8. **可观测性**：补充 SLO 告警指标。
