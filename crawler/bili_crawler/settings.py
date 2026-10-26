# Scrapy settings for bili_crawler
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env(项目根)
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')

BOT_NAME = 'bili_crawler'

# 并发限速:1 req/s
# 遵从 robots.txt(B 站 /robots.txt 允许 / 路径但声明了 UA 与频率约束)。
# 如确需抓取 robots 禁止的路径,应通过环境变量显式放行并在 README 记录理由,
# 不接受"默认关闭"这种静默不合规行为。
ROBOTSTXT_OBEY = os.getenv('ROBOTSTXT_OBEY', 'true').lower() == 'true'
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', 1))
DOWNLOAD_DELAY = float(os.getenv('DOWNLOAD_DELAY', 1.0))
COOKIES_ENABLED = False
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
)
# 声明真实用途,便于站点方在 UA 中识别与联系(robots 礼仪要求)
USER_AGENT = f'{USER_AGENT} (+game-aibot research crawler; contact via repo owner)'

# 版权与内容使用约束:采集内容入库时必须
#  1) 在 content_source.license_note 记录原作者与原链接;
#  2) 保留署名,不做全文转载;
#  3) 仅用于站内检索与摘要,不二次分发原文。
# 由 scripts/import_to_pg.py 与 pipelines.py 共同强制。
ATTRIBUTION_REQUIRED = True
MAX_ITEMS_PER_RUN = int(os.getenv('MAX_ITEMS_PER_RUN', 200))
LOG_LEVEL = 'INFO'

# 限速:单机 B 站 1 req/s,加 jitter
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Pipeline:过滤 + JSON 落盘
ITEM_PIPELINES = {
    'bili_crawler.pipelines.FilterPipeline': 100,
    'bili_crawler.pipelines.JsonExportPipeline': 200,
}

# 关闭 Scrapy 默认的 telnet/cookie
TELNETCONSOLE_ENABLED = False

# 编码
FEED_EXPORT_ENCODING = 'utf-8'

# Scrapy 项目关键配置
SPIDER_MODULES = ['bili_crawler.spiders']
NEWSPIDER_MODULE = 'bili_crawler.spiders'

# Scrapy 整合 Playwright(通过 scrapy-playwright,这里我们直接调 sync_api 更轻)
# 实际在 spider 里同步调 Playwright
