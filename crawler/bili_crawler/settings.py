# Scrapy settings for bili_crawler
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env(项目根)
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')

BOT_NAME = 'bili_crawler'

# 并发限速:1 req/s
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', 1))
DOWNLOAD_DELAY = float(os.getenv('DOWNLOAD_DELAY', 1.0))
COOKIES_ENABLED = False
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
)
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
