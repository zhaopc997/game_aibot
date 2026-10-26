# Memory System

> 状态：短期记忆已打通读取链路；长期记忆当前仍是进程内存储，尚未落库。
> 本文以 architecture-v2.md 为准，冲突处以 V2 为准。

## Short Memory（短期记忆）

当前任务上下文，供多轮对话使用。

- Storage：**当前为 `InMemoryMemoryService` 内的 `ConcurrentHashMap`**（进程内，重启即失忆）
- 设计目标：迁 Redis（依赖与配置已就位，`MemoryService` 已声明 Redis-backed 实现方向）
- 窗口：滑动窗口，最近 10 条（`InMemoryMemoryService.SHORT_WINDOW`）
- 读取链路：Agent 每轮 `readShort` 注入 prompt，最多回溯 `MAX_HISTORY_MESSAGES = 12` 条

## Long Memory（长期记忆）

玩家习惯、历史行为（游玩风格、常用角色等）。

- Storage：**当前为进程内 `Map<Long, PlayerPreference>`，不是向量库**
- 设计目标：写 `user_game_profile.preference` JSONB
- 说明：V1 规划的独立向量数据库（`player_memory` 表）**已在 architecture-v2.md §4.7 明确弃用**，
  本项目不引入向量库；此处早期表述已作废
- 现状：读取链路已接通，但**尚无写入方**（缺 `record_player_preference` 一类入口），
  因此 `loadPreference` 仍可能返回空偏好

## Knowledge Memory（知识记忆）

游戏知识库（攻略、百科、游戏数值），由 RAG 模块提供检索，见 `docs/ai-agent/rag-design.md`。