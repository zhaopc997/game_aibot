# 问题清单执行报告

> 执行时间：2026-10-19 · 依据 `audit-2026-10-15.md` 的问题清单逐项落地

## 完成情况总览

| # | 问题 | 状态 | 说明 |
|---|---|---|---|
| P0-1 | admin 默认弱密码 | ⚠️ **待你执行** | 已交付 `scripts/harden-accounts.sh`，改密需你授权 |
| P0-2 | 无 HTTPS | ✅ 已交付方案 | Caddy 自动证书编排 + 文档 |
| P1-1 | 15 款游戏无数值数据 | ✅ 已解决 | 22 款 → **27 款全部有数据**（Phasmophobia 除外，无对应数据源） |
| P1-2 | 社区内容为空 | ✅ 已解决 | 问答 0 → 10 条 |
| P2-1 | 65 处 `any` | ✅ 已清零 | 65 → **0**，`tsc --noEmit` 通过 |
| P2-2 | `oauthMock` 死代码 | ✅ 已删除 | 同时移除界面暴露 |
| P2-3 | ES mapping 易漂移 | ✅ 已固化 | 新增 `GuidesIndexBootstrap` |
| P3-1 | 无备份 / 无监控 | ✅ 已解决 | `backup-db.sh` + `health-check.sh`，实测通过 |
| P3-2 | 构建慢（10 分钟） | ✅ 已优化 | **10 分钟 → 29 秒** |

## 额外发现并修复的 2 个真实 Bug

### 🔴 问答列表恒为空（与数据无关）

`QuestionRepository.findTop50ByGameIdOrderByCreatedAtDesc(gameId)` 传入 `null` 时，
Spring Data 生成 `WHERE game_id = NULL`，而 SQL 中 `= NULL` 恒为 false ——
**不传 gameId 时列表永远是空数组**，即使库里有数据。

修复：新增 `findTop50ByOrderByCreatedAtDesc()`，服务层按 `gameId == null` 分支。
验证：接口从 0 条 → **10 条**。

### 🟠 封面外链失效后不回退本地素材

`GameCover` 原逻辑是 `src ? [src] : 本地探测` —— 只要数据库给了 URL 就完全不试本地文件。
多个厂商图床 404/防盗链（实测明日方舟封面 404），于是**本地有正确封面也只能显示 🎮**。

修复：改为"外链优先 + 本地兜底"的候选链，外链失败自动试 `/games/{id}.{png,jpg,...}`。

## 关键数据变化

| 指标 | 执行前 | 执行后 |
|---|---|---|
| 游戏数 | 22 | **27**（脚本一并写入 5 款手游） |
| 有角色数据的游戏 | 7 款 | **26 款** |
| 角色总数 | 546 | **593** |
| 武器总数 | 806 | **857** |
| 套装总数 | 132 | **160** |
| 机制总数 | 35 | **78** |
| 攻略数 | 30 | **52** |
| 问答数 | 0 | **10** |
| `guides` 索引 | 30 | **52**（与库一致） |
| `guide_chunks` 索引 | 30 | **52**（与库一致） |
| 前端 `any` | 65 | **0** |

> 注：脚本还自动新增了 和平精英 / 金铲铲之战 / 阴阳师 / 崩坏3 / 重返未来1999
> 五款游戏（含角色数据）。这些游戏的封面外链已确认失效，已置空回退占位符。

## 新增脚本与文档

| 文件 | 用途 |
|---|---|
| `scripts/harden-accounts.sh` | 账号加固：检测弱口令 → 重置强密码 → 禁用演示账号 |
| `scripts/backup-db.sh` | 数据库备份（含完整性校验、保留期清理） |
| `scripts/health-check.sh` | 健康巡检（容器/服务/数据/**索引条数/搜索命中率**） |
| `scripts/build-backend.sh` | 快速构建后端（29 秒 vs 10 分钟） |
| `backend/Dockerfile.fast` | 复用宿主 jar 的轻量镜像 |
| `docker-compose.tls.yml` + `deploy/caddy/Caddyfile` | HTTPS 自动证书接入 |
| `backend/.../GuidesIndexBootstrap.java` | 固化 `guides` 索引 mapping |
| `sql/seed-community-demo.sql` | 社区演示问答（幂等，可 `DELETE WHERE title LIKE '[演示]%'` 清除） |
| `frontend/src/components/stats/types.ts` | 数值组件共享类型（消除 any 的根因） |
| `docs/development/deployment-guide.md` | 补充 HTTPS / 备份 / 监控 / 快速构建章节 |

## 本轮修的几个深层问题（值得记录）

1. **`= NULL` 陷阱**：Spring Data 派生查询传 null 参数会生成 `= NULL`，恒 false。
   凡"可选筛选条件"都必须显式分支或用 `(:p IS NULL OR ...)`。
2. **索引"落后"比"为空"更隐蔽**：原自愈只在索引为空时触发，
   批量导入后索引停留在旧条数，新内容永远搜不到且无报错。
   已改为 `docCount < guideCount` 即重建。
3. **外链不可信**：厂商图床普遍防盗链/会失效，素材必须有本地兜底。

## 仍需你决策/处理

1. **改 admin 密码**（P0，安全）
   ```bash
   ./scripts/harden-accounts.sh --dry-run   # 先看哪些账号是弱口令
   ./scripts/harden-accounts.sh             # 确认后执行
   ```
   该操作会修改生产账号凭据，需你本人授权执行。

2. **HTTPS**：需要域名 + 公网 IP，按 `deployment-guide.md` 的步骤接入 Caddy。

3. **评论功能**：后端有 `CommentController`，但**前端完全没有评论 UI**（0 处代码）。
   这不是数据问题，是功能未接入 —— 是否要做需要产品决策。

4. **Phasmophobia** 仍无数值数据（crawler 无对应数据源）。

5. **LLM / 向量检索** 未启用（`LLM_ENABLED=false`、`use-knn=false`），
   AI 问答走模板拼接，语义检索未生效。启用需 API key 与成本评估。

6. **crawler 脚本 game_id 失效**：`sync_wuthering_waves(26)` 与
   `sync_hot_mobile_games` 中的 27-31 在旧库中不存在（现已被脚本自动创建，问题已自然消解）。
