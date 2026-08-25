"""W2-C1 秒级结构化拆解引擎（pytest 面）：AC-8 / IFACE-2 structure + intent 值域断言。"""

from types import SimpleNamespace

import pytest
from viral_radar.analysis.assets import AnalysisAssets
from viral_radar.analysis.decompose import DecomposeEngine


def _doc() -> dict:
    return {
        "task_id": "t",
        "platform": "Douyin",
        "content_type": "video",
        "author": {"name": "a"},
        "content_meta": {"title": "x"},
        "raw_text": "提问开场",
        "timeline_data": [
            {"time_start": 0, "time_end": 3, "source_type": "ASR", "raw_text": "提问开场"}
        ],
    }


def _gateway(response: str):
    return SimpleNamespace(chat=lambda prompt, **kw: response)


class TestDecomposeEngine:
    def test_valid_slices_roundtrip(self):
        canned = (
            '[{"time_range": "00:00-00:03", "script_text": "提问开场", "intent": "黄金3秒开头"}]'
        )
        out = DecomposeEngine().decompose(_doc(), _gateway(canned))
        assert out == [
            {"time_range": "00:00-00:03", "script_text": "提问开场", "intent": "黄金3秒开头"}
        ]

    def test_intent_enum_enforced(self):
        canned = '[{"time_range": "00:00-00:03", "script_text": "x", "intent": "乱来"}]'
        with pytest.raises(ValueError):
            DecomposeEngine().decompose(_doc(), _gateway(canned))

    def test_missing_field_rejected(self):
        canned = '[{"time_range": "00:00-00:03", "script_text": "x"}]'
        with pytest.raises(ValueError):
            DecomposeEngine().decompose(_doc(), _gateway(canned))

    def test_bad_time_range_rejected(self):
        canned = '[{"time_range": "三点", "script_text": "x", "intent": "干货输出"}]'
        with pytest.raises(ValueError):
            DecomposeEngine().decompose(_doc(), _gateway(canned))

    def test_non_json_llm_output_rejected(self):
        with pytest.raises(ValueError):
            DecomposeEngine().decompose(_doc(), _gateway("抱歉，我无法输出 JSON"))

    def test_intent_values_come_from_versioned_asset(self):
        labels = AnalysisAssets().intent_labels()
        assert labels == ["黄金3秒开头", "痛点引入", "情绪反转", "干货输出", "引导转化"]
