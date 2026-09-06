# Architecture v2 — Game AI Copilot

> **版本**:v2.0  · **状态**:设计中  · **作者**:架构组  · **更新日期**:2026-09
>
> 本文档**取代**以下两份占位文件:
> - `docs/architecture/system-architecture.md`(原 28 行骨架)
> - `docs/architecture/ai-agent-architecture.md`(原 23 行骨架)
>
> 本文档**不取代**根目录 `架构文档-修订版.md`,而是其 V2 增量;该修订版中以下章节在 V2 已**显式弃用**:
>
> | 修订版章节 | V2 处置 | 原因 |
> |-----------|--------|------|
> | 6.5 悬浮窗功能(桌面端+Android+iOS) | **整章弃用** | 战略转为 Web 闭环,不做移动 App |
> | 2.1 Flutter 3.x 移动 App | **弃用** | 同上 |
> | 第三阶段(移动端) | **弃用** | 同上 |
> | 2.2 ES 仅第二阶段引入 | **提前到 V2 即用** | AI Copilot 的 RAG 离不开向量检索 |
> | 2.2 RabbitMQ 第二阶段引入 | **继续延后** | 流量未起,MVP 仍用 Spring `ApplicationEvent` |
>
> 阅读路径:第 1 章先看 **战略与原则** → 第 2 章看 **技术选型变更** → 第 3 章看 **模块划分** → 第 4 章看 **AI Copilot 内部架构** → 第 5 章起为工程细节。

---

## 1. 项目战略与设计原则

### 1.1 战略定位

`game_aibot` 从 V1 的"AI 游戏攻略平台"**升级为 Game AI Copilot**:

- **V1(已完成)**:玩家问答 + 攻略知识库(纯 RAG 形态,无 Agent 能力)
- **V2(本文档)**:玩家问答 + 攻略知识库 + **Agent 任务规划 + 工具调用 + 玩家长期记忆**
- **V3(未来)**:从"助手"升级为"Autonomous Game Agent",能主动根据游戏状态(背包/任务/角色等级)做决策,接入游戏环境(读屏/ADB 自动化)

V2 关键差异化:**"能动手的攻略助手"**——不仅告诉你怎么做,还能代你查版本、查装备、记录偏好,跨多轮对话保持玩家画像。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **AI Copilot 优先** | 所有模块设计都让 Agent 可调用、可观测、可中断;不允许有"AI 看不到的暗箱" |
| **模块边界清晰** | 按业务域划 module,模块间只通过 `ApplicationEvent` 或 `Tool` 通信,杜绝直接跨模块 `Service` 调用 |
| **可演进性** | MVP 阶段不用 MQ、不用独立 AI 服务,但**接口防腐层必须预留**(见 §3.3) |
| **成熟优先** | Java 17 + Spring Boot 3.3 + Postgres + Redis + MinIO + ES 8,无冷门依赖 |
| **可观测** | 每条 AI 调用、每次 Tool 调用、每条 Plan Step 都进审计日志,出问题能回放 |
| **Web 闭环** | 只做 Web 前端,**不规划** Flutter / Electron / 悬浮窗,减少分支注意力 |

### 1.3 非目标(Non-Goals)

V2 明确**不**做:

- 移动 App(iOS / Android)
- 桌面端悬浮窗
- 离线本地模型部署(嵌入模型可本地,LLM 必须云端)
- 多语言(只做简体中文;LLM 输出可中英混合)
- 多租户 SaaS(单实例,内部使用)

---

## 2. 技术选型

### 2.1 技术栈总览(V2)

| 层次 | 技术 | 备注 |
|------|------|------|
| 前端 | React 18 + TypeScript + Vite | **不变**,已在 `frontend/` 跑通 |
| 后端 | Java 17 + Spring Boot 3.3.5 | **不变** |
| ORM | Spring Data JPA + Flyway | **不变** |
| 关系库 | PostgreSQL 16 | **不变** |
| 缓存 | Redis 7 | **不变** |
| 对象存储 | MinIO | **不变** |
| **搜索引擎** | **Elasticsearch 8.13+ HNSW** | **从第二阶段提前到 V2 即用**;混用 BM25 + dense 检索 |
| **Agent 框架** | **LangChain4j 0.36+**(主) / Spring AI(备) | 新增;纯 Java,不引副进程 |
| **图编排** | **LangGraph4j 0.5+** | 新增;Plan-and-Execute 状态图 |
| **LLM 客户端** | OpenAI Java Client + DeepSeek 兼容适配 | GPT-4o-mini 主,DeepSeek 备 |
| **嵌入模型** | bge-m3(本地 Ollama) / text-embedding-3-small(云) | 可切换;默认本地 |
| **Reranker** | bge-reranker-base(本地 HTTP) | 显著提升 Top-10 准确率 |
| 鉴权 | JJWT 0.12.6 + Spring Security | **不变** |
| 实时推送 | Spring WebSocket(STOMP) | **不变** |
| 监控 | Prometheus + Grafana + Loki | **ELK 暂缓**;Loki 更轻量 |
| CI/CD | GitHub Actions | **不变** |
| 容器化 | Docker + Docker Compose(开发) / Kubernetes(生产) | **不变** |

### 2.2 pom.xml 增量

`backend/pom.xml` 已在 V1 引入 `spring-boot-starter-data-elasticsearch`;V2 需新增:

```xml
<!-- LangChain4j 核心 -->
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-spring-boot-starter</artifactId>
  <version>0.36.2</version>
</dependency>
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-open-ai</artifactId>
  <version>0.36.2</version>
</dependency>
<!-- LangGraph4j 状态图 -->
<dependency>
  <groupId>org.bsc.langgraph4j</groupId>
  <artifactId>langgraph4j-core</artifactId>
  <version>0.5.0</version>
</dependency>
<!-- BGE 本地嵌入(走 HTTP,不引 ONNX,降低构建复杂度) -->
<!-- 实际通过 WebClient 调本地 bge-m3 服务,无需 SDK -->
<!-- 监控:Loki 不需要 SDK,直接 stdout JSON 即可 -->
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

### 2.3 暂不引入(V2 明确不引)

| 组件 | 何时引入 | 备注 |
|------|----------|------|
| RabbitMQ / Kafka | 触发条件:任一 module 独立扩缩容 或 Spring Event 出现明显延迟堆积 | 通过 `EventBus` 接口防腐层预留,实现可平替 |
| Spring Cloud Gateway | 模块化单体阶段不上;上线 K8s 后用 Nginx 即可 | |
| SkyWalking / Zipkin | 触发条件:调用链超过 5 跳 或出现跨服务调用 | 当前单体内调用链短,日志足够 |
| ELK | 触发条件:日志量 > 10GB/天 或需要复杂全文搜索 | Loki 足够 |
| Kubernetes | 触发条件:单实例无法扛峰值 或需要蓝绿发布 | Docker Compose 已能满足 V2 全量 |
| 独立 AI 微服务 | 触发条件:AI 调用 QPS > 50 或 LLM Token 成本超过业务 SLA | V2 仍是单体内部 module;按 §3.3 拆分 |

---

## 3. 模块划分

### 3.1 模块全景

`com.gametips.platform` 下的 11 个 module,4 新 + 7 已有扩展:

```
com.gametips.platform
├── common/         通用:统一响应/异常/分页/审计/上下文
├── user/           用户/认证/角色/玩家游戏档案
├── oauth/          第三方登录(Steam/PSN/微信,独立保留)
├── content/        攻略/资讯/百科/游戏/版本(含状态机)
├── community/      [从 content 拆出] 评论/点赞/收藏/问答
├── search/         [升级] 升级为 Hybrid Search(BM25 + 向量 + rerank)
├── recommend/      [改造] 召回 + 排序 + 重排 Pipeline
├── notification/   站内信 + WebSocket 推送
├── admin/          后台 + 审核队列
│
│   ──  以下 4 个是 AI Copilot 核心,V2 全新 ──
│
├── agent/          Agent Core 编排门面(Plan-and-Execute)
├── rag/            检索增强(切块/嵌入/检索/重排)
├── tool/           工具注册中心(SPI 加载 + @Tool 注解)
└── memory/         短期 + 长期 + 玩家偏好抽取
```

### 3.2 各 module 职责与依赖关系

| Module | 职责 | 可调用 | 不可调用 |
|--------|------|--------|----------|
| `common` | `ApiResponse<T>`、`BizException`、`PageCursor`、`TraceIdFilter`、`@AuditLog` | 无 | 所有 |
| `user` | 注册/登录/资料/角色/玩家游戏档案 | `common` | `agent`/`rag`/`tool`/`memory` |
| `oauth` | 第三方 OAuth2 绑定 | `user`/`common` | 同上 |
| `content` | 攻略/资讯/百科 CRUD + 状态机 + 版本差分 | `common`/`user`(读) | `community`/`agent` |
| `community` | 评论/点赞/收藏/问答 | `common`/`user`/`content`(读) | `agent` |
| `search` | Hybrid 检索服务(ES BM25 + HNSW + rerank) | `common`/`content`(读元数据) | `agent` |
| `recommend` | 召回-排序-重排 pipeline,基于规则 + 行为 + 协同(后期) | `common`/`content`/`user`(读) | `agent` |
| `notification` | 站内信 + WebSocket | `common`/`user` | `agent` |
| `admin` | 后台 + 审核 + 数据统计 | `common` + 读其他所有 | `agent` |
| **`agent`** | AgentOrchestrator、Planner、ReAct fallback、Agent HTTP API | **所有** | 无(根) |
| **`rag`** | 切块、嵌入、检索、rerank、prompt 模板 | `common`/`content` | `agent` |
| **`tool`** | `@Tool` 注解、ToolRegistry(SPI)、具体工具实现 | `common`/`content`/`user`/`community`/`search` | `agent` |
| **`memory`** | Redis 会话窗口、PG 玩家档案、行为抽取 | `common`/`user` | `agent` |

**关键约束**:

- **`agent` 是唯一编排者**:其他 module 不允许主动调用 `agent` 的能力
- **`tool` 是 agent 与业务 module 的唯一桥梁**:业务 module 不直接被 agent 注入,必须经 `tool` 包一层(避免 AI 把领域逻辑污染)
- **`community` / `notification` 走事件**:模块内产生业务事件(`GuidePublishedEvent` 等)→ `ApplicationEvent` → 监听方处理;agent 不直接落库

### 3.3 模块化单体 → 微服务演进(修订版 §3.3 的 V2 化)

**拆分触发条件**(任一满足):

1. 某 module 的独立团队规模 ≥ 2 个
2. 某 module 需要独立扩缩容(典型:AI 调用 CPU 密集,峰值与主接口差 5x+)
3. 单 module 故障持续影响其他 module
4. 部署/发布节奏冲突

**演进路径**:
1. 接口防腐层先行:`EventBus` 接口定义在 `common`,默认实现 `SpringEventBus`,MQ 化时换 `RabbitMqEventBus` 即可
2. AI 服务最先拆(`agent` + `rag` + `tool` + `memory` 整体拆)
3. `notification` 次之(纯异步,易独立)
4. `content` 视流量(读写比高、缓存复杂)

### 3.4 包结构约定(每个 module 内部)

```
module/<name>/
  domain/         # 实体 + 值对象 + 领域事件
  repository/     # Spring-Data-JPA Repository
  service/        # 业务逻辑(纯 POJO,不依赖 Web)
  web/            # @RestController + DTO
  dto/            # 入参/出参(独立于 domain 实体,避免泄漏)
  config/         # Spring @Configuration(只在本 module 范围内)
  event/          # 本 module 发出的 ApplicationEvent + 监听器
```

`agent` / `rag` / `tool` / `memory` 这 4 个新 module 因为更偏能力,不强制上面的分层,但**必须有 dto**(入参出参)和**service**(纯逻辑)。

---

## 4. AI Copilot 内部架构

### 4.1 总体架构图

```
                ┌─────────────────────────────────────────────┐
                │  Web (React)  →  POST /api/v1/agent/chat   │
                └─────────────────────┬───────────────────────┘
                                      │  {conversationId, message, userId}
                                      │
                ┌─────────────────────▼───────────────────────┐
                │   AgentController (in module/agent/web)     │
                └─────────────────────┬───────────────────────┘
                                      │
                ┌─────────────────────▼───────────────────────┐
                │           AgentOrchestrator                 │
                │   (LangGraph4j StateGraph,plan-and-execute)│
                │                                            │
                │   ┌─ plan ──┐  ┌─ execute ─┐  ┌─ reflect ┐ │
                │   │ Planner │→ │ Executor  │→ │ Reflect  │─┘
                │   └─────────┘  └─────┬─────┘  └──────────┘
                │                       │
                └──────┬──────┬─────────┴───────────┬────────┘
                       │      │                     │
              ┌────────▼─┐ ┌──▼────────┐ ┌──────────▼──────────┐
              │ Memory   │ │  Tool     │ │       RAG           │
              │ short+   │ │  Registry │ │  ES BM25 + HNSW     │
              │ long     │ │  (SPI)    │ │  + BGE reranker     │
              └──────────┘ └─────┬─────┘ └──────────┬──────────┘
                                 │                  │
                                 └────────┬─────────┘
                                          │
                                 ┌────────▼─────────┐
                                 │   LLM Client     │
                                 │ GPT-4o-mini 主   │
                                 │ DeepSeek 备      │
                                 └──────────────────┘
                                          │
                                 ┌────────▼─────────┐
                                 │   External       │
                                 │ - OpenAI API     │
                                 │ - DeepSeek API   │
                                 │ - 本地 bge-m3    │
                                 │ - 本地 reranker  │
                                 └──────────────────┘
```

### 4.2 Plan-and-Execute(区别于裸 ReAct)

```java
// 概念性代码,实际用 LangGraph4j 写
StateGraph<AgentState> graph = new StateGraph<>(AgentState::init)
    .addNode("plan",      this::plan)       // 1 次 LLM 调用,生成 Plan
    .addNode("execute",   this::execute)    // 串行执行 Step[0..n]
    .addNode("reflect",   this::reflect)    // 每步后判断:继续 / 重试 / 完成
    .addEdge(START, "plan")
    .addEdge("plan", "execute")
    .addConditionalEdges("execute",
        state -> state.hasNextStep() ? "execute" : "reflect")
    .addConditionalEdges("reflect",
        state -> state.isDone() ? END : "plan");
```

**Planner 输出 JSON Schema**:

```json
{
  "goal": "回答用户问题并保证答案匹配当前游戏版本",
  "steps": [
    {
      "step_id": 1,
      "tool": "search_guides",
      "input": {"query": "钟离圣遗物", "game_id": "yuanshen", "version_id": "v4.2"},
      "expected_output": "Top-5 攻略片段,含标题/作者/版本",
      "fallback": "若无可用攻略,改用通用 wiki 数据"
    },
    {
      "step_id": 2,
      "tool": "check_compatibility",
      "input": {"guide_ids": "<上一步结果>", "version_id": "v4.2"},
      "expected_output": "每篇攻略的版本兼容状态"
    },
    {
      "step_id": 3,
      "tool": "synthesize_answer",
      "input": {"question": "<原 question>", "context": "<前两步结果>"},
      "expected_output": "自然语言回答 + 来源链接 + 版本声明"
    }
  ]
}
```

**关键工程细节**:

- Plan 状态持久化到 `agent_plan` 表(`conversation_id` + `step_index` + `state_json`),崩溃可恢复
- 单步失败:自动重试 2 次(指数退避 2s/8s)→ 仍败则回 Planner 重新规划(限定 2 次)→ 还败则降级为"无 Tool 直答 LLM"
- 整轮超时:60s,LLM 调用 30s/次,Tool 调用 10s/次
- Human-in-the-loop:留 `interrupt` API,允许前端按 `step_id` 暂停、修改 plan、继续(V2.1 实现)

### 4.3 Tool 注册中心

```java
@Tool("搜索攻略,返回匹配的攻略片段列表")
public List<GuideChunk> searchGuides(
    @P("用户问题") String query,
    @P("游戏 ID") String gameId,
    @P("版本 ID,可选") String versionId
) { ... }

@Tool("检查攻略是否兼容指定游戏版本")
public CompatibilityResult checkCompatibility(
    @P("攻略 ID 列表") List<Long> guideIds,
    @P("目标版本 ID") String versionId
) { ... }
```

**Tool 注册机制**:Spring Boot 启动时扫描所有 `@Component` 中带 `@Tool` 注解的方法 → 写入 `ToolRegistry` → LangChain4j 读 Registry → 自动生成 LLM 的 function-calling schema。

**V2 内置 6 个 Tool**(按交付优先级排):

| # | Tool 名称 | 说明 | 依赖 module |
|---|----------|------|-------------|
| 1 | `search_guides` | 走 RAG 检索攻略片段 | `rag` |
| 2 | `check_compatibility` | 调 content 状态机接口 | `content` |
| 3 | `get_game_version_info` | 取游戏当前版本/历史版本 | `content` |
| 4 | `record_player_preference` | 写玩家长期记忆 | `memory` |
| 5 | `ask_clarification` | 反问用户(V2 留位,前端可渲染为选项) | `agent` |
| 6 | `report_outdated_guide` | 用户反馈攻略过期,触发审核流 | `content` + `notification` |

**Tool 安全约束**:

- 每个 Tool 必须声明 `riskLevel`(`READ_ONLY` / `WRITE` / `DESTRUCTIVE`),`WRITE` 以上的 Tool 需要 LLM 先在 Plan 中显式声明 + 用户确认
- 敏感 Tool(将来如"消耗积分"等)走独立的 `SensitiveToolGuard` 拦截

### 4.4 RAG Pipeline

```
Guide 文档
  ↓ [Chunker,500 字 + 50 字 overlap,按攻略 step 切]
Chunk(原文 + metadata)
  ↓ [Embedding, bge-m3 本地]
Vector (768 维)
  ↓ [Index, ES HNSW + 同步 BM25 索引]
ES Index: guide_chunks
  ↓ [Query]
Hybrid Retriever
  ├─ BM25 召回 Top-50
  └─ KNN 召回 Top-50
  ↓ [RRF 融合]
Top-100
  ↓ [BGE Reranker]
Top-10
  ↓ [Context Window 拼接,带来源标注]
LLM 上下文
```

**关键设计**:

- **Chunk 粒度按"攻略 step"切**而不是按字符,保证每段是完整语义单元;附加 metadata:`game_id`/`version_id`/`guide_id`/`step_id`/`author_id`
- **ES 索引按 `game_id` 路由**,便于单游戏数据规模大时独立 shard
- **检索时强制 filter**:`{ game_id: X, version_id: [current, ±1] }`,避免过期攻略污染
- **嵌入模型可切**:通过 `EmbeddingClient` 接口 + `@ConditionalOnProperty` 切换 bge-m3(text-embedding-3-small)
- **离线索引**:新增/更新攻略时,`content` module 发 `GuideChangedEvent` → `rag` 监听 → 异步重建该篇 chunk 的 ES 文档

### 4.5 Memory 系统

| 层级 | 存储 | TTL/容量 | 内容 |
|------|------|----------|------|
| 短期(对话上下文) | Redis | 滑动窗口最近 10 轮,30 分钟无活动过期 | 原始对话消息 |
| 长期(玩家档案) | PG `user_game_profile.preference JSONB` | 永久 | 玩家偏好:常玩游戏/角色/版本/难度/语言风格 |
| 知识(攻略内容) | ES + PG `guide` | 与内容一致 | 攻略原文(由 RAG 处理,不归 Memory) |

**短期记忆**:Redis key=`agent:conv:{conversationId}`,value=List<Message>。每轮追加,超过 10 轮截断最早。

**长期记忆**:
- 写入路径:`record_player_preference` Tool → `MemoryService.savePreference()` → 写 JSONB
- 抽取路径:每轮对话结束后,后台任务用 LLM 抽"用户偏好"(小模型 GPT-4o-mini,一次性 prompt)→ 合并到 JSONB
- 读取路径:Planner 决策时,从 `user_game_profile` 读 preference → 拼到 system prompt

**V2 简化**:**不引独立向量数据库**(原 V1 规划 `player_memory` 向量库,**弃用**),玩家偏好用结构化 JSONB 足够;真正需要向量化的是攻略知识,已在 RAG 处理。

### 4.6 LLM 客户端

```yaml
# application.yml
agent:
  llm:
    primary:
      provider: openai
      model: gpt-4o-mini
      base-url: ${OPENAI_BASE_URL}        # 走 SiliconFlow 中转
      api-key: ${OPENAI_API_KEY}
      timeout: 30s
      temperature: 0.3
    fallback:
      provider: openai-compatible
      model: deepseek-chat
      base-url: https://api.deepseek.com/v1
      api-key: ${DEEPSEEK_API_KEY}
      timeout: 30s
  embedding:
    provider: bge-local
    base-url: http://localhost:8081      # 本地 bge-m3 服务
  reranker:
    provider: bge-local
    base-url: http://localhost:8082      # 本地 bge-reranker 服务
```

**主备切换**:LangChain4j 支持 `FallbackModel`,主 LLM 连续失败 3 次自动切备;切回人工触发或定时探活。

---

## 5. API 设计(V2 增量)

完整规范继承修订版 §5.0;**以下仅 V2 新增/变更**:

### 5.1 Agent 模块 API

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/api/v1/agent/chat` | 发起对话,支持流式(SSE)和一次性返回 |
| `POST` | `/api/v1/agent/chat/stream` | SSE 流式,逐 token 推送 |
| `GET` | `/api/v1/agent/conversations` | 当前用户的历史对话列表(分页) |
| `GET` | `/api/v1/agent/conversations/{id}` | 单个对话详情(完整 Plan + 消息) |
| `DELETE` | `/api/v1/agent/conversations/{id}` | 删除对话 |
| `POST` | `/api/v1/agent/conversations/{id}/interrupt` | 中断当前正在执行的 Plan |
| `POST` | `/api/v1/agent/conversations/{id}/resume` | 继续被中断的 Plan(可附带修改后的步骤) |

**Request/Response 示例**:

```jsonc
// POST /api/v1/agent/chat
Request:
{
  "conversation_id": "uuid(可选,空则新建)",
  "message": "原神 4.2 钟离圣遗物怎么刷?",
  "stream": false
}

Response:
{
  "code": 0,
  "data": {
    "conversation_id": "abc-123",
    "message_id": "msg-456",
    "answer": "根据当前 4.2 版本,推荐:...",
    "plan": [
      {"step_id": 1, "tool": "search_guides", "status": "SUCCESS", "duration_ms": 312},
      {"step_id": 2, "tool": "check_compatibility", "status": "SUCCESS", "duration_ms": 89},
      {"step_id": 3, "tool": "synthesize_answer", "status": "SUCCESS", "duration_ms": 1240}
    ],
    "sources": [
      {"guide_id": 1001, "title": "钟离圣遗物毕业指南", "version": "4.2", "url": "/guides/1001"}
    ],
    "version_check": "all_sources_current_version"
  }
}
```

### 5.2 Tool 元数据 API(供前端调试面板用)

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/api/v1/agent/tools` | 列出所有可用 Tool(名称/描述/参数 schema) |
| `GET` | `/api/v1/agent/llm/status` | 主备 LLM 健康状态 |

### 5.3 限流调整

- Agent chat 接口:10 次/分钟/用户(LLM 成本高)
- Tool 调用(内部):无额外限流(已在 chat 内整体限流)
- 嵌入/Rerank 接口(内部):无(预签名 URL 模式)

---

## 6. 数据库设计(V2 增量)

继承修订版 §4 全部表;**仅列 V2 新增表**。

### 6.1 新增 AI 相关表

```sql
-- Agent 对话
agent_conversation (
  id              UUID PK,
  user_id         BIGINT NOT NULL,
  title           VARCHAR(200),         -- LLM 起的标题,可空
  status          VARCHAR(20) NOT NULL, -- ACTIVE / ARCHIVED
  created_at      TIMESTAMP,
  updated_at      TIMESTAMP
)

-- 单条消息(用户/系统/AI/Tool)
agent_message (
  id              UUID PK,
  conversation_id UUID NOT NULL,
  role            VARCHAR(20) NOT NULL, -- USER / ASSISTANT / SYSTEM / TOOL_RESULT
  content         TEXT NOT NULL,
  tool_calls      JSONB,                -- role=ASSISTANT 时,LLM 调用的 Tool 列表
  tool_call_id    UUID,                 -- role=TOOL_RESULT 时,对应 Tool 调用 ID
  token_count     INT,                  -- 计量
  created_at      TIMESTAMP
)

-- 计划/步骤状态(用于可观测 + 中断恢复)
agent_plan (
  id              UUID PK,
  conversation_id UUID NOT NULL,
  message_id      UUID NOT NULL,        -- 关联 assistant 消息
  plan_json       JSONB NOT NULL,       -- Planner 输出的完整 plan
  current_step    INT DEFAULT 0,
  status          VARCHAR(20) NOT NULL, -- PLANNING / EXECUTING / REFLECTING / DONE / FAILED / INTERRUPTED
  error_msg       TEXT,
  total_tokens    INT DEFAULT 0,
  created_at      TIMESTAMP,
  updated_at      TIMESTAMP
)

-- 计划步骤执行历史(每步一条)
agent_plan_step (
  id              BIGSERIAL PK,
  plan_id         UUID NOT NULL,
  step_index      INT NOT NULL,
  tool_name       VARCHAR(100),
  input_json      JSONB,
  output_json     JSONB,
  status          VARCHAR(20) NOT NULL, -- PENDING / RUNNING / SUCCESS / FAILED / SKIPPED
  duration_ms     INT,
  retry_count     INT DEFAULT 0,
  error_msg       TEXT,
  created_at      TIMESTAMP,
  updated_at      TIMESTAMP
)

-- 工具调用审计
agent_tool_audit (
  id              BIGSERIAL PK,
  user_id         BIGINT NOT NULL,
  conversation_id UUID,
  plan_step_id    BIGINT,
  tool_name       VARCHAR(100) NOT NULL,
  risk_level      VARCHAR(20) NOT NULL, -- READ_ONLY / WRITE / DESTRUCTIVE
  approved        BOOLEAN DEFAULT FALSE,-- WRITE 级别需要用户在 Plan 中显式确认
  input_hash      VARCHAR(64),          -- 便于去重审计
  created_at      TIMESTAMP
)
```

### 6.2 `user_game_profile` 扩展

```sql
ALTER TABLE user_game_profile
  ADD COLUMN preference JSONB DEFAULT '{}'::jsonb;
-- preference 结构示例:
-- {
--   "favorite_games": ["yuanshen", "starrail"],
--   "play_style": "casual",
--   "language_pref": "zh-CN",
--   "detail_level": "concise",       -- concise | detailed
--   "interest_tags": ["build", "lore"]
-- }
```

### 6.3 `guide` 表增量(为 RAG 服务)

```sql
ALTER TABLE guide
  ADD COLUMN embedding_status VARCHAR(20) DEFAULT 'PENDING';
  -- PENDING / INDEXED / FAILED
ALTER TABLE guide
  ADD COLUMN indexed_at TIMESTAMP;
-- 由 rag 模块的 GuideChangedEvent 监听器更新
```

### 6.4 原 V1 `docs/database/database-design-v2.md` 处置

V1 占位文件提到的 `agent_instance` / `agent_task` / `agent_action` / `game_state` / `player_memory` 五张表,V2 重新定义如下:

| V1 占位表 | V2 处置 |
|----------|---------|
| `agent_instance` | **删除**;改用 `agent_conversation`(实例 ≈ 一次会话) |
| `agent_task` | **删除**;改用 `agent_plan` + `agent_plan_step`(任务树扁平化为 Step 列表) |
| `agent_action` | **删除**;改用 `agent_tool_audit` |
| `game_state` | **V2 暂不建**;V3 接入游戏环境时再建;当前玩家游戏档案够用 |
| `player_memory` | **删除**;长期记忆落到 `user_game_profile.preference` JSONB,不用独立表 + 向量库 |

---

## 7. 可靠性与可观测性

### 7.1 LLM 调用可靠性

- **超时**:LLM 30s/次,Tool 10s/次,整轮 60s
- **重试**:LLM 失败 → 指数退避 2s/8s,最多 2 次 → 切备模型 → 还败降级为"无 Tool 直答"
- **幂等**:`POST /agent/chat` 接受 `client_request_id`,服务端去重 5 分钟
- **成本控制**:每用户每分钟最多 10 次 chat,每会话总 token 上限 8000(超出截断,提示用户开新对话)

### 7.2 Plan 持久化与恢复

- 每步执行完,`agent_plan_step` 写库(状态 + 输出)
- 服务崩溃重启:扫描 `status=EXECUTING` 的 plan → 标记为 `INTERRUPTED` → 用户可见、可手动 `resume`

### 7.3 监控指标(Prometheus)

```
# Agent
agent_chat_total{status}              # counter
agent_chat_duration_seconds{status}   # histogram
agent_plan_steps_total                # counter
agent_tool_call_total{tool,status}    # counter
agent_tool_call_duration_seconds{tool}# histogram
agent_llm_token_total{model,direction}# counter (prompt/completion)
agent_llm_failure_total{provider}     # counter
agent_active_plans                    # gauge

# RAG
rag_indexing_total{status}            # counter
rag_indexing_lag_seconds              # gauge (now - guide.updated_at)
rag_retrieval_duration_seconds        # histogram
rag_retrieval_top_k                   # histogram

# Memory
memory_redis_hit_rate                 # gauge
memory_long_write_total               # counter
```

**告警规则**(继承修订版 §7.5 全部;V2 新增):

- `agent_llm_failure_total{provider="primary"}` 5 分钟内 > 10 → 切备告警
- `agent_chat_duration_seconds` P95 > 8s → 慢响应告警
- `rag_indexing_lag_seconds` > 300 → 索引积压告警
- LLM 月度 token 成本超过预算 80% → 财务告警(走 PromQL → Alertmanager → 邮件)

### 7.4 审计日志

- 所有 `WRITE`/`DESTRUCTIVE` 级别 Tool 调用 → `agent_tool_audit` 表
- Agent 对话全过程 → `agent_conversation` + `agent_message` + `agent_plan` + `agent_plan_step`(自然形成审计链)
- 保留期:1 年(V2),到期归档到 MinIO

---

## 8. 安全

### 8.1 注入防护

- Tool 入参严格 JSON Schema 校验(LangChain4j 自动生成)
- LLM 输出再过一遍正则/白名单(关键 Tool 必走)
- RAG 检索结果注入到 Prompt 时,显式标记 `=== 检索内容开始/结束 ===`,降低 prompt injection 风险

### 8.2 越权防护

- 每个 Tool 强制传 `userId`(从 JWT 取,LLM 不可注入)
- Tool 内所有数据访问必须按 `userId` 过滤,业务 module 的 Service 层用 `@PreAuthorize` 兜底
- 攻略可见性:默认公开,带 `PRIVATE` 标记的攻略只能在 Tool 中按 `author_id = userId` 过滤

### 8.3 成本防护

- 每用户 chat QPS 限流
- LLM 响应长度上限 2000 token
- 嵌入/Rerank 走内部服务,无对外入口,无公网访问

---

## 9. 部署与开发

### 9.1 docker-compose 调整(V2)

`docker-compose.yml` V1 已包含 Postgres/Redis/ES/MinIO;V2 增量:

```yaml
services:
  bge-embed:                    # 新增:本地 bge-m3 嵌入服务
    image: ghcr.io/your-org/bge-m3-server:latest
    container_name: bge-embed
    ports: ["8081:8081"]
  bge-rerank:                   # 新增:本地 reranker 服务
    image: ghcr.io/your-org/bge-reranker-server:latest
    container_name: bge-rerank
    ports: ["8082:8082"]
  agent-platform:               # 后端单体容器
    build: ./backend
    container_name: agent-platform
    ports: ["8080:8080"]
    depends_on: [postgres, redis, elasticsearch, minio, bge-embed, bge-rerank]
    environment:
      OPENAI_BASE_URL: ${OPENAI_BASE_URL}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
  web:                          # 前端
    build: ./frontend
    container_name: agent-web
    ports: ["5173:80"]
    depends_on: [agent-platform]
```

**ES 在 V2 必须就绪**——V1 `架构文档-修订版.md` 写"ES 延后到第二阶段",**V2 不再延后**;但 PG `tsvector` 也保留,作为降级方案(ES 故障时 search 模块切 PG)。

### 9.2 本地开发启动步骤(V2)

```bash
# 1. 启动基础设施
docker compose up -d postgres redis elasticsearch minio bge-embed bge-rerank

# 2. 启动后端
cd backend
./mvnw spring-boot:run
# 健康检查:curl http://localhost:8080/actuator/health
# 看到 "rag":"UP" 表示 RAG 模块就绪

# 3. 启动前端
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173

# 4. (可选)导入种子数据
psql -h localhost -U postgres -d guide_platform < sql/seed.sql
# 触发 RAG 索引:POST /api/v1/admin/rag/reindex
```

### 9.3 配置(环境变量)

```bash
# 必填
OPENAI_BASE_URL=https://api.siliconflow.cn/v1   # 或 OpenAI 官方
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...

# 嵌入/Rerank(本地)
EMBEDDING_BASE_URL=http://localhost:8081
RERANKER_BASE_URL=http://localhost:8082

# 数据库/缓存(由 docker-compose 自动注入)
SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/guide_platform
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=postgres
SPRING_DATA_REDIS_HOST=redis
SPRING_DATA_REDIS_PORT=6379
SPRING_ELASTICSEARCH_URIS=http://elasticsearch:9200

# MinIO
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

---

## 10. 验收(MVP Definition of Done)

V2 验收看以下 5 个 case 全部通过:

| Case | 输入 | 期望 |
|------|------|------|
| **C1 攻略问答** | "原神 4.2 钟离圣遗物怎么刷?" | agent 调 search_guides + check_compatibility + synthesize_answer,返回结构化答案 + 来源链接 + 版本号;`rag` 命中 ≥ 1 篇 4.2 攻略 |
| **C2 版本过期** | "现在还能用 3.x 版本那篇钟离攻略吗?" | agent 调 check_compatibility,识别攻略为 OUTDATED,主动告知"4.x 已出,3.x 数据可能不准",并推荐最新 |
| **C3 偏好记忆** | 用户先说"我喜欢打辅助",再问"钟离怎么配队" | 第二次回答的 prompt 含 "user prefers support role",LLM 输出偏辅助向 |
| **C4 Tool 失败降级** | 故意把 bge-embed 容器停掉,再问问题 | agent 检索失败 → 降级走 PG tsvector → 仍能返回结果,响应中有 `degraded: true` 标记 |
| **C5 限流** | 同用户 1 分钟内 12 次 chat | 前 10 次正常,第 11、12 次返回 `code=3001`(限流) |

每个 Case 的执行结果(Plan/Step/Token/Duration)写到 `agent_plan` + `agent_plan_step`,便于复盘。

---

## 11. 与 V1 文档的关系

| 文档 | 关系 |
|------|------|
| `架构文档-修订版.md`(根目录) | V2 基线;**仅 §6.5 悬浮窗 / §2.1 Flutter / §第三阶段 / §2.2 ES 阶段** 显式弃用,其余章节作为 V2 基础 |
| `docs/architecture/system-architecture.md` | **本文件取代** |
| `docs/architecture/ai-agent-architecture.md` | **本文件取代**(本文 §4) |
| `docs/ai-agent/{planner,rag,memory-system,tool-calling}.md` | 各自 10-20 行的占位 → **本文 §4.2/4.4/4.5/4.3 详尽展开**;占位文件可删除或改为 "see architecture-v2.md §4.x" |
| `docs/roadmap/game-aibot-v2-roadmap.md` | V1 写"Phase 1 Assistant → Phase 2 Copilot → Phase 3 Agent" → V2 决定**直接做 Copilot**,此 roadmap 与 V2 矛盾,需要重写为 V2.1/V2.2/V2.3 子阶段 |
| `docs/database/database-design-v2.md` | 占位提到 5 张 AI 表,本文 §6.4 给出 V2 重定义,占位文件应改为指向本文 |
| `docs/database/entity-model.md` | 8 行的实体名清单 → 本文 §3.1 模块划分 + §4 AI 内部架构已涵盖,占位文件应删 |
| `docs/development/{api-design,local-development}.md` | 占位文件;本文 §5 + §9.2 已涵盖 |
| `docs/deployment/production-deployment.md` | "推荐 Docker + PG + Redis + Nginx" → V2 加 ES + bge 双服务,本文 §9.1 给出完整 compose |

**清理建议(文档维护)**:
- 删 `docs/database/entity-model.md`(本文 §3.1+§4 已覆盖)
- 删 `docs/development/api-design.md`(本文 §5 已覆盖,完整规范见 `架构文档-修订版.md` §5.0)
- 改 `docs/ai-agent/*.md` 4 份为各 3 行 "see architecture-v2.md §4.x"
- 改 `docs/roadmap/game-aibot-v2-roadmap.md` 重新规划 V2.1/V2.2/V2.3
- 改 `docs/database/database-design-v2.md` 改为指向本文 §6.4
- 改 `docs/deployment/production-deployment.md` 加 ES + bge 服务
- 改 `docs/development/local-development.md` 按本文 §9.2 重写

---

## 12. 后续待办(按优先级)

1. ☐ 搭建 `agent` / `rag` / `tool` / `memory` 4 个空 module + `common` 基础包,跑通 `agent/chat` Hello World(不接真 LLM,先 mock)
2. ☐ 接入 bge-m3 + ES,完成 RAG 检索 Pipeline 单元测试
3. ☐ 接入 GPT-4o-mini(SiliconFlow 中转),完成 1 个端到端 Case(C1 攻略问答)
4. ☐ 落地 §10 的 5 个验收 Case
5. ☐ 按 §11 清理占位文档
6. ☐ 补监控告警(§7.3)+ 审计日志(§7.4)
7. ☐ V2.1:Human-in-the-loop(`interrupt`/`resume` API)
8. ☐ V2.2:Web 前端 Agent 调试面板(可视化 Plan/Step)
9. ☐ V3 预研:游戏环境接入(ADB/读屏,先做 1 款手游 POC)

---

> 本文档的同步对象:`README.md` 中的 Architecture 章节应改为指向本文;`架构文档-修订版.md` 头部加 "V2 增量见 `docs/architecture/architecture-v2.md`" 链接。
