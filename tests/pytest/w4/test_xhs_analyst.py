"""W4-C2 小红书平台差异化分析（pytest 面）。"""

import pytest
from viral_radar.analysis.platforms.xhs import XhsAnalyst


def _xhs_doc():
    return {
        "platform": "XHS",
        "content_meta": {"title": "5 秒判断美妆干货？"},
        "timeline_data": [
            {"time_start": 0, "time_end": 1, "source_type": "OCR", "raw_text": "封面"},
            {"time_start": 1, "time_end": 2, "source_type": "OCR", "raw_text": "内页"},
        ],
    }


class TestXhsAnalyst:
    def test_three_outputs_independent(self):
        slices = [
            {"time_range": "00:00-00:03", "script_text": "x", "intent": "干货输出"},
            {"time_range": "00:03-00:06", "script_text": "x", "intent": "引导转化"},
        ]
        out = XhsAnalyst().analyze(_xhs_doc(), slices)
        assert set(out.keys()) == {"cover_appeal", "seeding_path", "layout_logic"}
        assert out["seeding_path"]["has_seed_conversion"] is True

    def test_platform_isolation(self):
        with pytest.raises(ValueError):
            XhsAnalyst().analyze({"platform": "Douyin"}, [])
