"""W1-C6 OCR 画面识别（pytest 面）：AC-6 三类文本 + 顺序属性 + 分类规则。"""

from viral_radar.processing.ocr import OcrReader


class TestOcrReader:
    def _stub(self, lines):
        return lambda p: lines

    def test_video_subtitle_zone_classification(self):
        stub = self._stub(
            [
                {"text": "底部字幕", "y_ratio": 0.95},
                {"text": "中间花字", "y_ratio": 0.4},
            ]
        )
        items = OcrReader().read("/f.png", order=2, mode="video", engine=stub)
        assert items == [
            {"order": 2, "kind": "字幕", "text": "底部字幕"},
            {"order": 2, "kind": "花字", "text": "中间花字"},
        ]

    def test_image_mode_all_embedded_with_order(self):
        stub = self._stub([{"text": "内页文案", "y_ratio": 0.5}])
        items = OcrReader().read("/p.png", order=1, mode="image", engine=stub)
        assert items == [{"order": 1, "kind": "内嵌", "text": "内页文案"}]

    def test_multi_frame_order_attr_preserved(self):
        stub = self._stub([{"text": "字幕", "y_ratio": 0.9}])
        first = OcrReader().read("/f1.png", order=0, engine=stub)
        second = OcrReader().read("/f2.png", order=5, engine=stub)
        assert first[0]["order"] == 0
        assert second[0]["order"] == 5

    def test_empty_results_allowed(self):
        assert OcrReader().read("/none.png", engine=self._stub([])) == []
