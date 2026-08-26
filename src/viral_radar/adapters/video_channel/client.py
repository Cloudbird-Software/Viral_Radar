"""client.py —— 视频号公开内容采集通道（spec AC-4 视频号面 / BEH-4）。

视频流 + 社交元数据（点赞/转发/收藏）。未注入 transport 拒绝采集（INV-3）。
采集骨架（分页/窗口/INV-3 门禁）复用 adapters.base 公共基座，归一逻辑仍在本文件。
"""

from viral_radar.adapters.base import PlatformAdapter


class VideoChannelAdapter(PlatformAdapter):
    """视频号采集适配器。"""

    def _normalize(self, entry: dict) -> dict:
        base = dict(entry)
        base.pop("video_url", None)
        base.update(
            {
                "content_id": str(entry.get("content_id") or ""),
                "url": entry.get("video_url") or entry.get("url") or "",
                "published_at": entry.get("published_at") or "",
                "likes": int(entry.get("likes") or 0),
                "shares": int(entry.get("shares") or 0),
                "favorites": int(entry.get("favorites") or 0),
            }
        )
        return base
