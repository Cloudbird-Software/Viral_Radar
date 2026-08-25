"""client.py —— 视频号公开内容采集通道（spec AC-4 视频号面 / BEH-4）。

视频流 + 社交元数据（点赞/转发/收藏）。未注入 transport 拒绝采集（INV-3）。
"""

from datetime import UTC, datetime, timedelta


class VideoChannelAdapter:
    """视频号采集适配器。"""

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
