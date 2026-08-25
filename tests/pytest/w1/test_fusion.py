"""W1-C7 数据融合对齐（pytest 面）：AC-7 产物过 W0-C2 schema / INV-2 无时间戳拒绝。"""

import pytest
from viral_radar.processing.unified import UnifiedValidator
from viral_radar.processing.unified.fusion import FusionEngine


class TestFusionEngine:
    def _fuse_args(self, **overrides):
        args = dict(
            task_id="t1",
            platform="Douyin",
            content_type="video",
            author={"name": "a"},
            content_meta={"title": "x"},
            title="标题文案",
            asr_segments=[{"start": 0.5, "end": 3.0, "text": "口播"}],
            ocr_items=[{"order": 1, "time_sec": 2.0, "text": "花字"}],
        )
        args.update(overrides)
        return args

    def test_output_passes_schema_and_has_three_sources(self):
        doc = FusionEngine().fuse(**self._fuse_args())
        assert UnifiedValidator().validate(doc) == []
        sources = {e["source_type"] for e in doc["timeline_data"]}
        assert sources == {"Title", "ASR", "OCR"}

    def test_title_first_and_sorted(self):
        doc = FusionEngine().fuse(**self._fuse_args())
        starts = [e["time_start"] for e in doc["timeline_data"]]
        assert starts == sorted(starts)
        assert doc["timeline_data"][0]["source_type"] == "Title"

    def test_timestampless_asr_rejected(self):
        with pytest.raises(ValueError):
            FusionEngine().fuse(**self._fuse_args(asr_segments=[{"end": 3.0, "text": "无start"}]))

    def test_images_content_maps_order(self):
        doc = FusionEngine().fuse(
            **self._fuse_args(
                content_type="images",
                asr_segments=[],
                ocr_items=[{"order": 2, "text": "第二页"}, {"order": 0, "text": "封面"}],
            )
        )
        assert UnifiedValidator().validate(doc) == []
        ocr = [e for e in doc["timeline_data"] if e["source_type"] == "OCR"]
        assert ocr[0]["raw_text"] == "封面"  # 按顺序属性映射后保持升序
