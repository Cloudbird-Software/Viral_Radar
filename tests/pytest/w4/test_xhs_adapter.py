"""W4-C1 小红书采集适配器（pytest 面）：契约测试——图文形态产出含图片顺序属性。"""

from datetime import UTC, datetime, timedelta

import pytest
from viral_radar.adapters.xhs import XhsAdapter


class TestXhsAdapter:
    def _note_entry(self, days_ago=5):
        return {
            "note_id": "n1",
            "content_type": "images",
            "cover_url": "https://cdn/cover",
            "images_urls": ["https://cdn/p1", "https://cdn/p2", "https://cdn/p3"],
            "hashtags": ["#美妆", "#平价好物"],
            "published_at": (datetime.now(UTC) - timedelta(days=days_ago)).isoformat(),
            "likes": 100,
            "shares": 5,
        }

    def _transport(self, items):
        return lambda cursor: {"items": items, "next_cursor": None}

    def test_images_form_keeps_order_attribute(self):
        entry = self._note_entry()
        items = XhsAdapter(transport=self._transport([entry])).collect("acct")
        assert items[0]["images"] == [
            "https://cdn/cover",
            "https://cdn/p1",
            "https://cdn/p2",
            "https://cdn/p3",
        ]
        assert items[0]["images"][0] == "https://cdn/cover"  # 封面第 0 位

    def test_hashtags_preserved(self):
        entry = self._note_entry()
        items = XhsAdapter(transport=self._transport([entry])).collect("acct")
        assert items[0]["hashtags"] == ["#美妆", "#平价好物"]

    def test_video_form_classified(self):
        entry = dict(
            self._note_entry(), note_id="v2", content_type="video", video_url="https://cdn/v"
        )
        items = XhsAdapter(transport=self._transport([entry])).collect("acct")
        assert items[0]["content_type"] == "video"
        assert items[0]["url"] == "https://cdn/v"

    def test_no_transport_rejected(self):
        with pytest.raises(RuntimeError):
            XhsAdapter().collect("acct")
