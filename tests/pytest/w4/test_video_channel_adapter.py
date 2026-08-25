"""W4-C3 视频号采集适配器（pytest 面）：契约测试——视频流 + 社交元数据。"""

from datetime import UTC, datetime, timedelta

import pytest
from viral_radar.adapters.video_channel import VideoChannelAdapter


class TestVideoChannelAdapter:
    def _entry(self, content_id="c1", days_ago=5):
        return {
            "content_id": content_id,
            "video_url": "https://finder/c1",
            "published_at": (datetime.now(UTC) - timedelta(days=days_ago)).isoformat(),
            "likes": 200,
            "shares": 50,
            "favorites": 30,
        }

    def _transport(self, items):
        return lambda cursor: {"items": items, "next_cursor": None}

    def test_social_meta_normalized(self):
        entry = self._entry()
        items = VideoChannelAdapter(transport=self._transport([entry])).collect("acct")
        assert items[0] == {
            "content_id": "c1",
            "url": "https://finder/c1",
            "published_at": entry["published_at"],
            "likes": 200,
            "shares": 50,
            "favorites": 30,
        }

    def test_window_filter(self):
        items = VideoChannelAdapter(
            transport=self._transport([self._entry("new", 3), self._entry("old", 230)])
        ).collect("acct")
        assert [i["content_id"] for i in items] == ["new"]

    def test_no_transport_rejected(self):
        with pytest.raises(RuntimeError):
            VideoChannelAdapter().collect("acct")
