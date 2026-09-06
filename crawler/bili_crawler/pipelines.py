"""Pipeline:过滤 + JSON 落盘。"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

# 全局输出目录
ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'out'


class FilterPipeline:
    """
    过滤掉:
      - 黑名单关键词(直播/抽卡/MAD/混剪…)
      - 播放量 < 1 万
      - 时长 < 3 分钟 或 > 30 分钟
      - 标题/简介/UP 主名命中黑名单
    """
    GLOBAL_EXCLUDE = re.compile(
        r'角色演示|直播|抽卡|氪金|开箱|测评|同人|MAD|混剪|reaction|翻唱|'
        r'搞笑|段子|广告|推广|打赏|签约|'
        r'cosplay|cos\s|漫展|联名|'
        r'主播|签约|恭喜|中奖|'
        r'声优|主题曲|OP\s|ED\s|'
        r'路线|速刷|速通'  # B 站热门的"X 分钟路线"通常内容稀薄
    )

    MIN_VIEW_COUNT = 10_000
    MIN_DURATION   = 120   # 2 min:再短就基本不是攻略了
    MAX_DURATION   = 3600  # 60 min:允许长攻略 / 系列

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        title = a.get('title', '') or ''
        up_name = a.get('up_name', '') or ''
        desc = a.get('description', '') or ''

        # 1. 关键词黑名单
        for field, text in [('title', title), ('up_name', up_name), ('description', desc)]:
            if self.GLOBAL_EXCLUDE.search(text):
                raise DropItem(f"黑名单关键词命中 ({field}): {title!r}")

        # 2. 播放量
        view = a.get('view_count', 0) or 0
        if view < self.MIN_VIEW_COUNT:
            raise DropItem(f"播放量过低 ({view}): {title!r}")

        # 3. 时长
        dur = a.get('duration', 0) or 0
        if dur < self.MIN_DURATION or dur > self.MAX_DURATION:
            raise DropItem(f"时长不达标 ({dur}s): {title!r}")

        # 4. 必须命中目标游戏关键词(已在 spider 过滤,这里再校验一次)
        if not a.get('game_slug'):
            raise DropItem("未关联到目标游戏")

        return item


class JsonExportPipeline:
    """每条 item 落一份 JSON 到 out/{game_slug}/{bv_id}.json。"""

    def process_item(self, item, spider):
        a = ItemAdapter(item).asdict()
        # 序列化 datetime
        for k, v in a.items():
            if isinstance(v, datetime):
                a[k] = v.isoformat()
        slug = a.get('game_slug', 'unknown')
        bv = a.get('bv_id', 'unknown')
        out_dir = OUT_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f'{bv}.json'
        path.write_text(json.dumps(a, ensure_ascii=False, indent=2), encoding='utf-8')
        spider.logger.info(f"✅ 落盘: {path.relative_to(ROOT)}")
        return item
