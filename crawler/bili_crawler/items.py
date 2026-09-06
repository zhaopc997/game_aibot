"""Scrapy Item — 标准化一条 B 站攻略视频的结构化数据。"""
import scrapy


class GuideItem(scrapy.Item):
    # ─── 来源信息(B 站) ───
    bv_id       = scrapy.Field()   # BVxxxx
    av_id       = scrapy.Field()   # 对应数字 aid
    url         = scrapy.Field()   # https://www.bilibili.com/video/BVxxx
    title       = scrapy.Field()
    description = scrapy.Field()
    cover_url   = scrapy.Field()
    duration    = scrapy.Field()   # 秒
    view_count  = scrapy.Field()   # 播放量
    danmaku_count = scrapy.Field()
    like_count  = scrapy.Field()
    publish_time = scrapy.Field()  # ISO 8601

    # ─── UP 主信息 ───
    up_mid      = scrapy.Field()   # UP 主 uid
    up_name     = scrapy.Field()
    up_face     = scrapy.Field()

    # ─── 分 P ───
    pages = scrapy.Field()  # List[Dict] {cid, title, duration, view}

    # ─── 映射到业务侧 ───
    game_slug   = scrapy.Field()   # 'ys' / 'wzry' / 'lol' / 'dzpd'
    game_id     = scrapy.Field()   # 1 / 4 / 5 / 6
    game_name   = scrapy.Field()   # 中文

    # ─── 内部追踪 ───
    matched_keyword = scrapy.Field()  # 命中的搜索关键词
    crawl_time   = scrapy.Field()      # 采集时间 ISO
