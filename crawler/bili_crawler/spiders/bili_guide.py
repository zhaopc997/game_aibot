"""B 站攻略爬虫 — Playwright 渲染 + 公开 API 解析。

V1 流程(本期):
  1. 读 GAME_RULES[--game] 配置(默认 'ys')
  2. 遍历 search_keywords,在 B 站搜索 API 找视频
  3. 过滤:每个 (keyword, page) 拉 ~ 30 个候选
  4. 对每个候选调用 view API + page list API 拿详情
  5. 校验通过 → yield GuideItem

命令行:
  scrapy crawl bili_guide -a game=ys -a limit=3
"""
import json
import re
import time
from datetime import datetime
from urllib.parse import quote

import scrapy
from playwright.sync_api import sync_playwright

from bili_crawler.items import GuideItem


# ───── 目标游戏规则(可扩展) ─────
# game_id 对应数据库 guide_platform.game 表 id(与原神/黑神话/英雄联盟等一一对应)
GAME_RULES = {
    'ys': {  # 原神
        'name': '原神',
        'game_id': 2,
        'search_keywords': ['原神 攻略', '原神 圣遗物', '原神 配队', '原神 深渊', '原神 任务', '原神 活动', 'Genshin Impact 攻略'],
        'must_keywords': ['原神', 'Genshin'],
    },
    'wukong': {  # 黑神话：悟空
        'name': '黑神话：悟空',
        'game_id': 4,
        'search_keywords': ['黑神话悟空 攻略', '黑神话悟空 Boss', '黑神话 天命人', '黑神话 全成就', '黑神话 装备', '黑神话 剧情'],
        'must_keywords': ['黑神话', '悟空'],
    },
    'lol': {  # 英雄联盟
        'name': '英雄联盟',
        'game_id': 6,
        'search_keywords': ['英雄联盟 攻略', 'LOL 上分', '英雄联盟 对线', '英雄联盟 打野', 'LOL 教学', '英雄联盟 版本'],
        'must_keywords': ['英雄联盟', 'LOL'],
    },
    'starrail': {  # 崩坏：星穹铁道
        'name': '崩坏：星穹铁道',
        'game_id': 8,
        'search_keywords': ['崩坏星穹铁道 攻略', '星穹铁道 配队', '星穹铁道 遗器', '星穹铁道 任务', '星穹铁道 活动', '星穹铁道 模拟宇宙'],
        'must_keywords': ['星穹铁道', '星铁'],
    },
    'arknights': {  # 明日方舟
        'name': '明日方舟',
        'game_id': 9,
        'search_keywords': ['明日方舟 攻略', '明日方舟 关卡', '明日方舟 基建', '明日方舟 活动', '明日方舟 干员', '明日方舟 危机合约'],
        'must_keywords': ['明日方舟', '方舟'],
    },
}

# 搜索 API(用 search/all/v2 通用接口,然后自己过滤 result_type='video')
SEARCH_URL = (
    'https://api.bilibili.com/x/web-interface/search/all/v2'
    '?keyword={kw}&page={page}&page_size=30&order=click'
)
VIEW_URL = 'https://api.bilibili.com/x/web-interface/view?bvid={bv}'
PAGES_URL = 'https://api.bilibili.com/x/player/pagelist?bvid={bv}&jsonp=jsonp'


class BiliGuideSpider(scrapy.Spider):
    name = 'bili_guide'
    allowed_domains = ['bilibili.com', 'api.bilibili.com']

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
    }

    def __init__(self, game='ys', limit=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_key = game
        self.limit = int(limit)
        if game not in GAME_RULES:
            raise ValueError(f"未知 game={game},可选:{list(GAME_RULES)}")
        self.rule = GAME_RULES[game]
        self.playwright_ctx = None
        self.playwright_page = None
        # 记录已 yield 的 BV,避免重复
        self._yielded_bvs = set()

    def open_spider(self, spider):
        # 启动 Playwright(B 站 API 反爬,先开 headless chromium 拿真实 cookie)
        self.logger.info("🚀 启动 Playwright(用于初始 cookie 采集)…")
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)
        self.playwright_ctx = browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
            )
        )
        self.playwright_page = self.playwright_ctx.new_page()
        # 访问首页拿 wbi / cookie
        self.playwright_page.goto('https://www.bilibili.com', timeout=30_000)
        time.sleep(2)

    def close_spider(self, spider):
        if self.playwright_ctx:
            self.playwright_ctx.close()
            self.playwright_page = None

    def start_requests(self):
        """入口:对每个关键词拉多页搜索结果,扩大候选池,触发详情页抓取。"""
        for kw in self.rule['search_keywords']:
            # 每个关键词拉 3 页(共约 90 个候选),覆盖更多不同的攻略视频
            for page in (1, 2, 3):
                yield scrapy.Request(
                    SEARCH_URL.format(kw=quote(kw), page=page),
                    callback=self.parse_search,
                    meta={'keyword': kw, 'page': page},
                    dont_filter=True,
                )

    def parse_search(self, response):
        """解析搜索 API,过滤出候选 BV,逐个抓详情。

        search/all/v2 返回结构(2025 实际格式):
          data.result = [
            {"result_type":"tips",   "data":[]},
            {"result_type":"brand_ad","data":[]},
            {"result_type":"video",   "data":[{bvid, title, ...}, ...]},
            {"result_type":"bili_user","data":[...]},
            ...
          ]
        旧版 search/all 有时是平铺 list,所以两种都容错。
        """
        kw = response.meta['keyword']
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.warning(f"搜索响应不是 JSON: {response.text[:200]}")
            return

        result_block = (data.get('data') or {}).get('result') or []

        videos = []
        if isinstance(result_block, list) and result_block and isinstance(result_block[0], dict) and 'data' in result_block[0] and 'result_type' in result_block[0]:
            # 新格式:按 type 分组
            for group in result_block:
                if not isinstance(group, dict):
                    continue
                if group.get('result_type') == 'video' and isinstance(group.get('data'), list):
                    videos.extend(group['data'])
        elif isinstance(result_block, list):
            # 旧格式:平铺 list
            videos = [x for x in result_block if isinstance(x, dict) and 'bvid' in x]
        elif isinstance(result_block, dict):
            # 另一种旧格式:{video: {data: [...]}}
            v = result_block.get('video') or {}
            if isinstance(v, dict) and isinstance(v.get('data'), list):
                videos = v['data']
            elif isinstance(v, list):
                videos = v

        self.logger.info(f"🔍 [{kw}] 命中 {len(videos)} 条视频候选")

        for r in videos:
            bv = r.get('bvid')
            raw_title = r.get('title') or ''
            # 新版 highlight 标签是 <em class="keyword">..</em>,也兼容旧版
            clean_title = re.sub(r'<[^>]+>', '', raw_title)

            if not bv or bv in self._yielded_bvs:
                continue
            if len(self._yielded_bvs) >= self.limit:
                self.logger.info(f"🎯 已达 limit={self.limit},停止 yield")
                return

            # 必须命中游戏关键词(在标题里)
            if not any(mk in clean_title for mk in self.rule['must_keywords']):
                continue

            self._yielded_bvs.add(bv)
            yield scrapy.Request(
                VIEW_URL.format(bv=bv),
                callback=self.parse_view,
                meta={'bv': bv, 'title': clean_title, 'keyword': kw},
                dont_filter=True,
            )

    def parse_view(self, response):
        """B 站 view API 拿视频详情 + UP 主 + 数据。"""
        bv = response.meta['bv']
        title = response.meta['title']
        kw = response.meta['keyword']
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.warning(f"view 响应非 JSON: {response.text[:200]}")
            return

        d = (data.get('data') or {})
        if not d or data.get('code') != 0:
            self.logger.warning(f"view API 错误 [{bv}]: {data.get('message')}")
            return

        # 再请求 pagelist(分 P 列表)
        yield scrapy.Request(
            PAGES_URL.format(bv=bv),
            callback=self.parse_pages,
            meta={
                'bv': bv, 'title': title, 'keyword': kw,
                'view_data': d,
            },
            dont_filter=True,
        )

    def parse_pages(self, response):
        """汇总 view + pagelist → yield GuideItem。"""
        meta = response.meta
        bv = meta['bv']
        d = meta['view_data']
        try:
            pages_raw = json.loads(response.text)
        except json.JSONDecodeError:
            pages_raw = []

        data = (pages_raw or {}).get('data') if isinstance(pages_raw, dict) else None
        # data 可能是 list[dict] / list[str] / None
        pages = []
        if isinstance(data, list):
            for i, p in enumerate(data):
                if not isinstance(p, dict):
                    # 有些分 P 的"part"是字符串(全标题在父视频),跳过
                    continue
                title = p.get('part') or ''
                # B 站 vupload 单分 P 的 part 是数字字符串,过滤掉
                if not title or title.isdigit():
                    title = f'P{i+1}'
                pages.append({
                    'part_index': p.get('page') or (i + 1),
                    'cid': p.get('cid'),
                    'title': title.strip(),
                    'duration': p.get('duration', 0),
                })

        # 命中游戏关键词的强化判定
        full_text = (
            (d.get('title', '') or '')
            + ' '
            + (d.get('desc', '') or '')
        )
        if not any(mk in full_text for mk in self.rule['must_keywords']):
            self.logger.info(f"⏭️  详情不含游戏关键词,跳过 [{bv}]: {title!r}")
            return

        # 解析发布时间(UNIX ts)
        pub_ts = d.get('pubdate', 0)
        publish_time = (
            datetime.fromtimestamp(pub_ts).isoformat() if pub_ts else None
        )

        # 简介清洗(去掉 HTML 标签)
        desc = re.sub(r'<[^>]+>', '', d.get('desc', '') or '').strip()

        # 封面(动态协议)
        cover = d.get('pic', '')

        # UP 主
        owner = d.get('owner') or {}
        stat  = d.get('stat') or {}

        item = GuideItem(
            bv_id          = bv,
            av_id          = d.get('aid'),
            url            = f'https://www.bilibili.com/video/{bv}',
            title          = (d.get('title') or '').strip(),
            description    = desc[:500],  # 截断
            cover_url      = cover,
            duration       = d.get('duration', 0),
            view_count     = stat.get('view', 0),
            danmaku_count  = stat.get('danmaku', 0),
            like_count     = stat.get('like', 0),
            publish_time   = publish_time,
            up_mid         = owner.get('mid'),
            up_name        = owner.get('name'),
            up_face        = owner.get('face'),
            pages          = pages,
            game_slug      = self.game_key,
            game_id        = self.rule['game_id'],
            game_name      = self.rule['name'],
            matched_keyword= meta['keyword'],
            crawl_time     = datetime.now().isoformat(),
        )
        self.logger.info(
            f"📦 yield [{bv}] {title!r} | UP:{owner.get('name')} "
            f"| 👁 {stat.get('view', 0)} | P{len(pages)}"
        )
        yield item
