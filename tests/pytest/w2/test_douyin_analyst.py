"""W2-C2 抖音平台差异化分析（pytest 面）：AC-9 三产物独立 / IFACE-4 平台面互不可替换。"""

import pytest
from viral_radar.analysis.platforms.douyin import DouyinAnalyst


def _doc() -> dict:
    return {
        "platform": "Douyin",
        "timeline_data": [
            {"time_start": 0, "time_end": 3, "source_type": "ASR", "raw_text": "a"},
            {"time_start": 3, "time_end": 8, "source_type": "ASR", "raw_text": "b"},
            {"time_start": 8, "time_end": 12, "source_type": "ASR", "raw_text": "c"},
        ],
    }


def _slices() -> list[dict]:
    return [
        {"time_range": "00:00-00:03", "script_text": "a", "intent": "黄金3秒开头"},
        {"time_range": "00:03-00:08", "script_text": "b", "intent": "痛点引入"},
        {"time_range": "00:08-00:12", "script_text": "c", "intent": "引导转化"},
    ]


class TestDouyinAnalyst:
    def test_three_outputs_independent(self):
        out = DouyinAnalyst().analyze(_doc(), _slices())
        assert set(out.keys()) == {"rhythm", "bgm", "golden_three"}
        assert out["rhythm"] != out["bgm"]
        assert out["golden_three"] != out["rhythm"]

    def test_rhythm_mechanically_derived(self):
        out = DouyinAnalyst().analyze(_doc(), _slices())
        assert out["rhythm"]["beats"] == [3.0, 5.0, 4.0]
        assert out["rhythm"]["avg_segment_s"] == 4.0

    def test_golden_three_reports_head_slices(self):
        out = DouyinAnalyst().analyze(_doc(), _slices())
        assert out["golden_three"]["golden_intent_found"] is True
        assert out["golden_three"]["golden_three_slices"] == ["00:00-00:03"]

    def test_platform_isolation_rejects_xhs(self):
        with pytest.raises(ValueError):
            DouyinAnalyst().analyze({"platform": "XHS", "timeline_data": []}, _slices())

    def test_empty_timeline_degrades_gracefully(self):
        out = DouyinAnalyst().analyze({"platform": "Douyin", "timeline_data": []}, [])
        assert out["rhythm"]["avg_segment_s"] == 0.0
