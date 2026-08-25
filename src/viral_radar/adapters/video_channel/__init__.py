"""video_channel —— 视频号采集适配器（spec AC-4 视频号面 / DECISION-1 自研通道）。

归一化产物字段：content_id / url / published_at / likes / shares / favorites（社交元数据）。
transport 注入契约同抖音适配器；无 transport 拒绝采集（INV-3）。
"""

from viral_radar.adapters.video_channel.client import VideoChannelAdapter

__all__ = ["VideoChannelAdapter"]
