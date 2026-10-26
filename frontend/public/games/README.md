# 游戏封面素材接入指南

> 面向 22 款游戏的封面/Logo 素材。**所有素材必须来自开发商官方授权渠道**，
> 禁止直接抓取官网/第三方站点图片（版权风险 + 防盗链失效）。

## 一、命名约定

素材统一放在 `frontend/public/games/`，文件名必须为游戏 id：

```
frontend/public/games/<gameId>.png     # 推荐，宽幅 460x215 或 1200x562
frontend/public/games/<gameId>.jpg     # 备选
frontend/public/games/<gameId>.webp    # 备选，体积最小
```

读取优先级（前端已实现）：

1. 数据库 `game.cover_url` 非空 → 用它（支持 CDN 外链）
2. 否则探测 `/games/{id}.png` → `.jpg` → `.webp`
3. 都没有 → 渲染 🎮 emoji 占位

>换素材只需替换同名文件，无需改代码。建议统一用 `.png`。

## 二、当前素材状态（2026-10-10 实测）

数据库 `game.cover_url` **22 款全部为 NULL**，因此前端全靠本地文件兜底。

| id | 游戏 | 本地文件 | 状态 |
|---|---|---|---|
| 1 | 艾尔登法环 | 1.jpg | ✅ 正确 |
| 2 | 原神 | 2.png | ❌ **错位**（卡通头像） |
| 3 | 塞尔达传说：王国之泪 | 3.jpg | ✅ 正确（竖版官方封面） |
| 4 | 黑神话：悟空 | 4.jpg | ✅ 正确 |
| 5 | DOTA 2 | 5.jpg | ✅ 正确 |
| 6 | 英雄联盟 | 6.png | ❌ **错位**（吃播头像） |
| 7 | CS2 | 7.jpg | ✅ 正确 |
| 8 | 崩坏：星穹铁道 | 8.png | ❌ **错位**（表情包） |
| 9 | 明日方舟 | 9.jpg | ✅ 正确（官方 logo） |
| 10 | 暗黑破坏神4 | 10.jpg | ✅ 正确 |
| 11 | 博德之门3 | 11.jpg | ✅ 正确 |
| 12 | 赛博朋克2077 | 12.jpg | ✅ 正确 |
| 13 | 荒野大镖客2 | 13.jpg | ✅ 正确 |
| 14 | 空洞骑士 | 14.jpg | ✅ 正确 |
| 15 | 以撒的结合：忏悔 | 15.jpg | ✅ 正确 |
| 16 | Apex 英雄 | 16.jpg | ✅ 正确 |
| 17 | Valorant | 17.png | ❌ **错位**（二战照片） |
| 18 | 炉石传说 | 18.jpg | ✅ 正确 |
| 19 | 云顶之弈 | 19.png | ✅ 正确（官方图标） |
| 20 | 永劫无间 | 20.jpg | ✅ 正确 |
| 21 | 幻塔 | 21.jpg | ✅ 正确 |
| 22 | Phasmophobia | 22.jpg | ✅ 正确 |

**结论：19 款可用，4 款需替换**（id = 2 / 6 / 8 / 17）。

## 三、需替换素材的官方申请渠道

以下 4 款需要重新获取官方授权素材。可用的官方渠道：

### 2. 原神（米哈游 / HoYoverse）
- 官网品牌页：https://www.hoyoverse.com/
- 媒体中心：https://www.hoyoverse.com/en-us/news
- 说明：米哈游对外提供品牌素材需通过商务合作申请；社区页可下载 Logo 但仅限非商业用途

### 6. 英雄联盟（腾讯游戏 / Riot Games）
- Riot 品牌中心：https://www.riotgames.com/en/branding
- 说明：Riot 有公开的 Brand Portal，提供各游戏 Logo 与品牌规范

### 8. 崩坏：星穹铁道（米哈游 / HoYoverse）
- 同原神渠道：https://www.hoyoverse.com/

### 17. Valorant（Riot Games）
- 同 Riot 品牌中心：https://www.riotgames.com/en/branding

## 四、获取后的操作

```bash
# 1. 把授权素材放到对应路径（覆盖错位的旧文件）
cp 原神官方封面.jpg     frontend/public/games/2.jpg
cp 英雄联盟官方封面.jpg   frontend/public/games/6.jpg
cp 崩坏星穹铁道官方封面.jpg frontend/public/games/8.jpg
cp Valorant官方封面.jpg  frontend/public/games/17.jpg

# 2. 校验尺寸是否合理（脚本会列出所有素材状态）
node frontend/scripts/check-game-covers.mjs
```

前端是 HMR 的，替换后刷新页面即可生效。

## 五、可选：改用数据库字段

若素材放在 CDN 上，可写入数据库（优先级高于本地文件）：

```sql
UPDATE game SET cover_url = 'https://cdn.example.com/games/2.png' WHERE id = 2;
```

## 六、已知问题：扩展名必须与内容一致

排查中发现 **17 个 `.png` 文件的实际内容是 JPEG**（爬虫抓取时未按内容重命名）。
Vite 按扩展名发 `Content-Type: image/png`，浏览器严格模式会拒绝解码 → 图片加载失败。
已统一按真实格式重命名为 `.jpg`。

**放置新素材时请注意**：`file xxx.png` 若输出 `JPEG image data`，说明扩展名错了，
浏览器会加载失败。命名要么与内容一致，要么在提交前执行：

```bash
cd frontend/public/games && for f in *.png; do file -b "$f" | grep -q JPEG && echo "$f 实为 JPEG"; done
```

## 七、素材使用合规要求

- 必须来自开发商官方授权渠道，保留来源与授权证明
- 不得抓取官网/百科/社区的图片（含防盗链绕过）
- 不得用于与授权范围不符的用途（如需商用需另行取得许可）
- 版权信息建议记录在项目文档中