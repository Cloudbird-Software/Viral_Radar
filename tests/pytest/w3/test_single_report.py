"""W3-C1 单账号深度报告（pytest 面）：AC-11 四节齐备 + 视频级详情 + 大纲对齐。"""

from viral_radar.analysis.report.single import SingleReportBuilder


def _docs():
    return [
        {
            "task_id": "v1",
            "platform": "Douyin",
            "content_meta": {"title": "爆款一"},
            "timeline_data": [
                {"time_start": 0, "time_end": 3, "source_type": "ASR", "raw_text": "a"}
            ],
        }
    ]


def _slices():
    return [[{"time_range": "00:00-00:03", "script_text": "a", "intent": "黄金3秒开头"}]]


class TestSingleReportBuilder:
    def test_four_sections_present(self):
        out = SingleReportBuilder().build("acc1", {"name": "n", "followers": 1}, _docs(), _slices())
        assert set(out.keys()) == {"overview", "video_details", "outline", "conclusion"}

    def test_video_level_details(self):
        out = SingleReportBuilder().build("acc1", {"name": "n", "followers": 1}, _docs(), _slices())
        detail = out["video_details"][0]
        assert detail["content_id"] == "v1"
        assert detail["title"] == "爆款一"
        assert detail["slices"][0]["intent"] == "黄金3秒开头"

    def test_outline_aligned_with_slices(self):
        out = SingleReportBuilder().build("acc1", {"name": "n", "followers": 1}, _docs(), _slices())
        section = out["outline"]["sections"][0]
        assert section["beats"][0]["time_range"] == "00:00-00:03"

    def test_conclusion_has_three_elements(self):
        out = SingleReportBuilder().build("acc1", {"name": "n", "followers": 1}, _docs(), _slices())
        assert set(out["conclusion"].keys()) == {"style", "top_words", "patterns"}
