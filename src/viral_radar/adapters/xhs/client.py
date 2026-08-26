"""client.py —— 小红书公开内容采集通道（spec AC-4 小红书面 / BEH-4）。

图文形态重点：封面图、内页图、文末 Hashtag——images 字段为有序清单（封面第 0 位，
顺序属性即数组下标），hashtags 为文末话题标签。未注入 transport 拒绝采集（INV-3）。
采集骨架（分页/窗口/INV-3 门禁）复用 adapters.base 公共基座，归一逻辑仍在本文件。
"""

from viral_radar.adapters.base import PlatformAdapter


class XhsAdapter(PlatformAdapter):
    """小红书采集适配器（短视频流 + 图文图片集双形态）。"""

    def _normalize(self, entry: dict) -> dict:
        base = dict(entry)
        for raw_key in ("note_id", "cover_url", "images_urls"):
            base.pop(raw_key, None)
        inner = [str(u) for u in (entry.get("images_urls") or [])]
        cover = entry.get("cover_url") or ""
        images = ([cover] if cover else []) + inner
        declared = entry.get("content_type")
        base.update(
            {
                "content_id": str(entry.get("content_id") or entry.get("note_id") or ""),
                "content_type": declared
                if declared in ("video", "images")
                else ("images" if images and not entry.get("video_url") else "video"),
                "url": entry.get("video_url") or entry.get("url") or "",
                "published_at": entry.get("published_at") or "",
                "likes": int(entry.get("likes") or 0),
                "shares": int(entry.get("shares") or 0),
                "images": images,
                "hashtags": [str(t) for t in (entry.get("hashtags") or [])],
            }
        )
        return base
