"""W1-C3 抖音采集适配器（pytest 面）：契约测试 = mock 数据源产出标准化元数据。"""

from datetime import UTC, datetime, timedelta

import pytest
from viral_radar.adapters.douyin import DouyinAdapter


class TestDouyinAdapter:
    def _transport(self, items, cursors):
        calls = []

        def transport(cursor):
            calls.append(cursor)
            return {
                "items": items if len(calls) == 1 else [],
                "next_cursor": cursors[len(calls) - 1],
            }

        return transport, calls

    def _page(self, days_ago=10, likes=100, shares=20, comments=("好评",)):
        return {
            "content_id": "v1",
            "video_url": "https://cdn.example/v1",
            "published_at": (datetime.now(UTC) - timedelta(days=days_ago)).isoformat(),
            "likes": likes,
            "shares": shares,
            "top_comments": list(comments),
        }

    def test_normalized_metadata_shape(self):
        items_payload = [self._page()]
        transport, _ = self._transport(items_payload, [None])
        items = DouyinAdapter(transport=transport).collect("acct")
        assert items == [
            {
                "content_id": "v1",
                "url": "https://cdn.example/v1",
                "published_at": items_payload[0]["published_at"],
                "likes": 100,
                "shares": 20,
                "top_comments": ["好评"],
            }
        ]

    def test_six_month_window_filters_stale(self):
        fresh = self._page(days_ago=10)
        stale = self._page(days_ago=220)
        transport, _ = self._transport([fresh, stale], [None])
        items = DouyinAdapter(transport=transport).collect("acct")
        assert [i["content_id"] for i in items] == ["v1"]

    def test_pagination_until_exhaustion(self):
        fresh = self._page()
        transport, calls = self._transport([fresh], ["c2", None])
        DouyinAdapter(transport=transport).collect("acct")
        assert len(calls) == 2

    def test_no_transport_rejected(self):
        """未注入合规传输层=直连采集路径，必须拒绝（INV-3）。"""
        with pytest.raises(RuntimeError):
            DouyinAdapter().collect("acct")
