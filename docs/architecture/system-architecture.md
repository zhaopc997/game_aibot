# System Architecture

## Overview

game_aibot V2 使用 AI Native 架构。

```
User
 |
API Gateway
 |
AI Agent Layer
 |
Planner
Memory
Reasoning
Executor
 |
Knowledge Layer
 |
Game Adapter
```

核心模块：
- Agent Layer
- Knowledge Layer
- Game State Layer
- Tool Layer
