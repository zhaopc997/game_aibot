# game_crawler — B 站攻略采集器

从 B 站抓取游戏攻略视频元数据,转成结构化 guide,落到 PostgreSQL。

## 项目结构
```
crawler/
├── README.md                 本文件
├── requirements.txt          Python 依赖
├── .env.example              环境变量示例
├── run_crawl.sh              一键启动脚本(激活 venv + 跑)
├── bili_crawler/             Scrapy 项目
│   ├── settings.py
│   ├── items.py
│   ├── pipelines.py
│   └── spiders/
│       └── bili_guide.py
├── scripts/
│   ├── import_to_pg.py       JSON → PostgreSQL 入库
│   └── make_seed_user.py     创建 system bot 用户
├── bv_list.example.txt       手动 BV 号列表(可选)
└── out/                      采集产物(按游戏分子目录)
```

## 快速开始

```bash
# 1. 装依赖(首次)
python3 -m venv .venv-crawler
source .venv-crawler/bin/activate
pip install -r crawler/requirements.txt
playwright install chromium

# 2. 配置环境
cp crawler/.env.example crawler/.env
# 编辑 crawler/.env 填入数据库连接信息

# 3. 创建采集者用户(一次)
python crawler/scripts/make_seed_user.py

# 4. 跑爬虫
bash crawler/run_crawl.sh              # 默认:原神 3 篇
bash crawler/run_crawl.sh --game=ys --limit=3

# 5. 入库
python crawler/scripts/import_to_pg.py crawler/out
```

## 扩展游戏
在 `bili_crawler/spiders/bili_guide.py` 的 `GAME_RULES` 字典里加新游戏:

```python
GAME_RULES = {
    'ys': {  # 原神
        'name': '原神', 'slug': 'ys',
        'search_keywords': ['原神', '原神攻略', 'Genshin'],
        'exclude_keywords': ['抽卡', ...],
        'game_id': 1,  # 对应 guide.game_id
    },
    'wzry': {  # 王者荣耀
        'name': '王者荣耀', 'slug': 'wzry',
        'search_keywords': ['王者荣耀攻略', ...],
        'exclude_keywords': [...],
        'game_id': 4,
    },
    # 加更多...
}
```

## 数据流
```
B 站搜索 API
  ↓
bili_guide.py (Spider) — 抓标题/封面/UP主/简介/分P
  ↓
FilterPipeline — 过滤黑名单 + 最低播放量
  ↓
JsonExportPipeline — 写 out/{game_slug}/{bv_id}.json
  ↓
import_to_pg.py — 读 JSON → 入 PostgreSQL
  ↓
guide + content_source
```

## 注意事项
- 本工具**仅做学习用途**,采集到的攻略请保留原作者署名(B 站 UP 主)
- `content_source.license_note` 会自动写"采集自 B 站 UP:xxx,版权属原作者"
- B 站 API 限速 1 req/s 已内置,频繁运行可能被临时封 IP
- 建议每天最多跑 1-2 次,总产出控制在 20-50 篇/天
