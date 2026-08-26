"""W3-C4 报告在线阅读与导出（pytest 面）：AC-14 在线阅读四节齐备 + PDF 与在线一致。"""

import io

from pypdf import PdfReader

from viral_radar.app.report_web import ReportExporter


def _report() -> dict:
    return {
        "overview": {
            "account_id": "a1",
            "name": "账号",
            "followers": 1,
            "video_count": 1,
            "platform": "Douyin",
        },
        "video_details": [
            {
                "content_id": "v1",
                "title": "爆款",
                "slices": [
                    {
                        "time_range": "00:00-00:03",
                        "intent": "黄金3秒开头",
                        "script_text": "提问开场",
                    }
                ],
            }
        ],
        "outline": {
            "sections": [
                {
                    "content_id": "v1",
                    "title": "爆款",
                    "beats": [{"time_range": "00:00-00:03", "hook": "黄金3秒开头"}],
                }
            ]
        },
        "conclusion": {
            "style": "强钩子",
            "top_words": ["提问开场"],
            "patterns": [{"sequence": ["黄金3秒开头", "痛点引入"], "count": 1}],
        },
    }


class TestReportExporter:
    def _pdf_text(self) -> str:
        data = ReportExporter().export_pdf(_report())
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def test_online_html_four_sections(self):
        html = ReportExporter().render_html(_report())
        for title in ("概览", "视频级拆解详情", "结构化大纲", "爆款逻辑总结"):
            assert title in html

    def test_html_escapes_content(self):
        nasty = _report()
        nasty["video_details"][0]["slices"][0]["script_text"] = "<script>alert(1)</script>"
        html = ReportExporter().render_html(nasty)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_pdf_is_pdf(self):
        assert ReportExporter().export_pdf(_report()).startswith(b"%PDF")

    def test_pdf_content_matches_online_version(self):
        text = self._pdf_text()
        for expected in ("账号：a1", "黄金3秒开头", "强钩子", "提问开场"):
            assert expected in text

    def test_word_export_postponed_surface_not_present(self):
        assert not hasattr(ReportExporter(), "export_word")
