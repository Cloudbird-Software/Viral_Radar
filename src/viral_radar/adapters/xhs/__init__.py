"""xhs —— 小红书采集适配器（spec AC-4 小红书面 / DECISION-1 自研通道）。

归一化产物字段：content_id / content_type(video|images) / url / published_at / likes /
shares / images / hashtags；图文形态 images 为有序页面清单（封面第 0 位 +
内页图片顺序属性——spec AC-6 顺序面）。transport 注入契约同抖音适配器。
"""

from viral_radar.adapters.xhs.client import XhsAdapter

__all__ = ["XhsAdapter"]
