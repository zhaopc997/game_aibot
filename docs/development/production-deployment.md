# 生产部署记录

> 部署时间：2026-10-26 · 执行人：自动化部署

## 访问信息

| 项 | 值 |
|---|---|
| 站点 | **https://helozero.com** |
| 服务器 | 111.229.224.236（腾讯云 · Ubuntu 24.04 · 4C / 3.7G / 40G） |
| 部署目录 | `/opt/GameGuide` |
| 应用端口 | `127.0.0.1:8088`（仅回环，公网经 Caddy 80/443） |
| 反代 | 系统 Caddy v2.11.4（systemd，自动 HTTPS） |
| 证书 | Let's Encrypt，自动续期，当前有效期至 2027-01-24 |

## 服务构成

| 容器 | 作用 | 内存限制 |
|---|---|---|
| game-prod-frontend | Nginx + 静态资源 | 256M |
| game-prod-backend | Spring Boot 应用 | 1.5G |
| game-prod-postgres | PostgreSQL 16 | 1G |
| game-prod-redis | 缓存 | 768M |
| game-prod-elasticsearch | 搜索 + RAG（堆 384m） | 2G |
| game-prod-minio | 对象存储 | 1G |

全部 `restart: unless-stopped`，Docker 与 Caddy 均 `enabled` 开机自启。

## 数据状态

| 项 | 数量 |
|---|---|
| 游戏 | 31 |
| 攻略 | 52 |
| 角色 | 1093 |
| 问答 | 10 |
| `guides` 索引 | 52（与库一致） |
| `guide_chunks` 索引 | 52（与库一致） |

## 账号

- 管理员：`admin`，密码已轮换为强随机（见交付信息，`admin123` 已验证失效）
- `tester` 演示账号：已禁用
- 所有基础设施凭据（DB / Redis / MinIO / JWT）均为服务器本地生成的强随机值，
  存放于 `/opt/GameGuide/.env.production`（权限 600）

## 运维

### 定时任务 `/etc/cron.d/gameguide`

```
30 3 * * *   备份数据库（保留 7 天，含完整性校验）
*/10 * * * * 健康巡检（索引条数、搜索命中率、容器与服务）
```

日志：`/var/log/game-backup.log`、`/var/log/game-health.log`

### 常用命令

```bash
# 查看服务状态
ssh -i ~/.ssh/helozero_deploy ubuntu@111.229.224.236 \
  'sudo docker ps --filter name=game-prod --format "{{.Names}} {{.Status}}"'

# 健康巡检
sudo bash /opt/GameGuide/scripts/health-check.sh

# 手动备份
sudo bash /opt/GameGuide/scripts/backup-db.sh

# 查看 Caddy 访问日志（走 journald，不是文件）
sudo journalctl -u caddy -f

# 重启应用（改代码后）
cd /opt/GameGuide && sudo docker compose -p gameaibot \
  -f docker-compose.prod.yml --env-file .env.production up -d --build backend
```

## 部署过程中修复/规避的问题

1. **SSH 微信扫码验证**：密码登录被 `up.yd.qcloud.com` 二次验证拦截，
   改用公钥认证可正常通过（横幅仅提示）。密钥 `~/.ssh/helozero_deploy`。
2. **Maven 源过慢**：直连 Central 单 POM 4.18s，阿里云 0.054s。
   已在 `backend/Dockerfile` 加入 `maven-settings.xml` 镜像配置。
3. **Elasticsearch 镜像拉取卡死**：国内加速器不覆盖 `docker.elastic.co`，
   首次 `compose up` 会挂住；单独 `docker pull` 可解决。
4. **Caddy 文件日志无权限**：发行版 unit 带 `ProtectSystem=full`，
   `/var/log` 只读，`ReadWritePaths` 覆盖亦无效 → 改为 journald 输出。

## 待办与建议

| 优先级 | 事项 |
|---|---|
| 中 | **内存偏紧**：可用约 836M，swap 已用 502M。建议升配到 8G（腾讯云在线升配，需重启） |
| 低 | LLM 与向量检索未启用（`LLM_ENABLED=false`、`use-knn=false`），AI 问答走模板拼接 |
| 低 | 服务器另有两套已停止的系统（gewe / ainovel），确认不再需要后可 `compose down -v` 回收磁盘 |
| 低 | 备份目前落在同盘 `/opt/GameGuide/backups`，建议改为异地/对象存储 |
| 低 | 服务器登录密码曾在对话中明文出现，建议更换 |

## 恢复被停止的旧系统（如需）

```bash
# gewe
sudo docker start gewe

# ainovel
cd /opt/Ai-Novel && sudo docker compose start
```

> 注意：两者合计约 760M 内存，恢复后会挤占本应用的余量。

---

## 巡检告警（2026-10-28 新增）

### 为什么加

2026-10-27 发生过一次真实事故：后端容器重建后，前端 nginx 缓存了旧 IP，
`/api` 全线 502 持续约 6 小时。巡检脚本每 10 分钟都记录了 `[FAIL]`，
**但只写日志、没有任何通知渠道**，等于没有监控。

### 组成

| 文件 | 作用 |
|---|---|
| `scripts/health-check.sh` | 巡检 + 告警判定（去重 / 重提醒 / 恢复通知 / 心跳） |
| `scripts/alert.sh` | 多通道发送器（企业微信 / 钉钉 / 通用 webhook） |
| `.alert.env` | 渠道配置（含密钥，600 权限，已 gitignore） |
| `.health-state` | 去重状态（记录上次告警时间与故障签名） |

### 配置（必须做，否则只写日志不发通知）

```bash
ssh ubuntu@111.229.224.236
cd /opt/GameGuide
cp .alert.env.example .alert.env
chmod 600 .alert.env
vi .alert.env      # 填 WECOM_WEBHOOK（企业微信群机器人）
```

企业微信群机器人获取：群聊 → 右上角 → 群机器人 → 添加 → 复制 Webhook 地址。

### 告警策略

不是"每次失败都发"，否则故障持续时每 10 分钟一条，很快就会被忽略：

| 情况 | 行为 |
|---|---|
| 新故障 | 立即告警 |
| 同一批故障再次检出 | **静默**（按故障签名 md5 判重） |
| 故障内容变化（新增失败项） | 告警 |
| 同一故障持续超过 6 小时 | 重提醒一次 |
| 恢复正常 | 发「已恢复」通知 |
| 持续正常 | 不发，只写心跳 |

重提醒间隔可调：`RENOTIFY_AFTER=3600 bash scripts/health-check.sh --quiet`

### 心跳

每次运行都追加一行，即使一切正常：

```
[2026-10-28 09:48:06] heartbeat status=ok fails=0 warns=0 games=31 guides=52 es=52 hit=17
```

这条的价值：能区分「系统健康」和「巡检根本没在跑」。
之前 `--quiet` 模式下健康时零输出，日志不增长，两种状态无法辨别。

### 日志轮转

`/etc/logrotate.d/gameguide`：每周轮转、保留 8 份、压缩、`copytruncate`。

### 手动排查

```bash
sudo tail -20 /var/log/game-health.log      # 最近巡检结果与心跳
sudo cat /opt/GameGuide/.health-state       # 当前状态与上次告警时间
sudo bash /opt/GameGuide/scripts/alert.sh "测试" "内容" fail   # 测试通道
```
