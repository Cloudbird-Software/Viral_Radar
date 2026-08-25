"""client.py —— 小红书公开内容采集通道（spec AC-4 小红书面 / BEH-4）。

图文形态重点：封面图、内页图、文末 Hashtag——images 字段为有序清单（封面第 0 位，
顺序属性即数组下标），hashtags 为文末话题标签。未注入 transport 拒绝采集（INV-3）。
"""

from datetime import UTC, datetime, timedelta


class XhsAdapter:
    """小红书采集适配器（短视频流 + 图文图片集双形态）。"""

    def __init__(self, transport=None) -> None:
        self._transport = transport

    def collect(self, account: str, months: int = 6) -> list[dict]:
        if self._transport is None:
            raise RuntimeError("采集通道未注入合规传输层——直连采集被禁止（INV-3）")
        cutoff = datetime.now(UTC) - timedelta(days=30 * months + 3)
        items = []
        cursor = None
        while True:
            page = self._transport(cursor)
            raw = page.get("items") or []
            for entry in raw:
                if self._within_window(entry, cutoff):
                    items.append(self._normalize(entry))
            cursor = page.get("next_cursor")
            if not cursor or not raw:
                break
        return items

    def _within_window(self, entry: dict, cutoff: datetime) -> bool:
        published = entry.get("published_at")
        if not published:
            return True
        return datetime.fromisoformat(str(published).replace("Z", "+00:00")) >= cutoff

    def _normalize(self, entry: dict) -> dict:
        base = dict(entry)
        for raw_key in ("note_id", "cover_url", "images_urls"):
            base.pop(raw_key, None)
        inner = [str(u) for u in (entry.get("images_urls") or [])]
        cover = entry.get("cover_url") or ""
        images = ([cover] if cover else []) + inner
        base.update(
            {
                "content_id": str(entry.get("content_id") or entry.get("note_id") or ""),
                "content_type": entry.get("content_type")
                if entry.get("content_type") in ("video", "images")
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
