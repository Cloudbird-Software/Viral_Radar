"""W3-C3 拍摄 SOP 标准化输出（pytest 面）：AC-12 三类可执行条目结构断言。"""

from viral_radar.analysis.sop import SopBuilder


def _report():
    return {
        "conclusion": {
            "style": "strong",
            "top_words": ["黄金3秒开头"],
            "patterns": [{"sequence": ["黄金3秒开头", "痛点引入"], "count": 2}],
        }
    }


def _docs():
    return [
        {
            "task_id": "v1",
            "timeline_data": [
                {"time_start": 0, "time_end": 3, "source_type": "ASR", "raw_text": "a"},
                {"time_start": 3, "time_end": 9, "source_type": "ASR", "raw_text": "b"},
            ],
        }
    ]


class TestSopBuilder:
    def test_three_executable_sections(self):
        out = SopBuilder().build(_report(), _docs())
        assert set(out.keys()) == {"must_have_elements", "duration_limit", "shot_requirements"}

    def test_must_have_elements_from_patterns(self):
        out = SopBuilder().build(_report(), _docs())
        assert any("黄金3秒" in e for e in out["must_have_elements"])
        assert any("痛点" in e for e in out["must_have_elements"])

    def test_duration_limit_reflects_samples(self):
        out = SopBuilder().build(_report(), _docs())
        assert "9 秒左右" in out["duration_limit"]

    def test_shot_requirements_include_beats(self):
        out = SopBuilder().build(_report(), _docs())
        shots = out["shot_requirements"][0]
        assert shots["content_id"] == "v1"
        assert shots["beats"][0]["cut_at_s"] == 3.0
