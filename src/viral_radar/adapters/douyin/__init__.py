"""douyin —— 抖音采集适配器（spec DECISION-1：自研通道，MediaCrawler 参考不依赖）。

归一化产物字段：content_id / url / published_at / likes / shares / top_comments。
频控/合规边界由注入的 transport 负责——未注入 transport 的适配器拒绝采集
（INV-3：禁止存在无频控的直连采集路径）。
"""

from viral_radar.adapters.douyin.client import DouyinAdapter

__all__ = ["DouyinAdapter"]
