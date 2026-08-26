"""W0-C2 统一数据模型 schema v1（pytest 面）：合法样本全过 / 非法样本逐一被拒。

schema 真源 = src/viral_radar/processing/unified/v1/schema.json（IFACE-1 落盘要求）。
"""

import json
import pathlib

from viral_radar.processing.unified import UnifiedValidator

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "src" / "viral_radar" / "processing" / "unified" / "v1" / "schema.json"


def _doc() -> dict:
    return {
        "task_id": "t-1",
        "platform": "Douyin",
        "content_type": "video",
        "author": {"name": "样例作者", "followers": 1024},
        "content_meta": {"title": "爆款样例", "likes": 9999},
        "raw_text": "标题文本",
        "timeline_data": [
            {"time_start": 0, "time_end": 3, "source_type": "ASR", "raw_text": "黄金三秒"},
            {"time_start": 3, "time_end": 9, "source_type": "OCR", "raw_text": "花字"},
        ],
    }


class TestUnifiedSchema:
    def test_schema_asset_exists_and_versioned(self):
        assert SCHEMA_PATH.exists()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        assert schema["schema_version"] == 1

    def test_optional_field_null_allowed(self):
        """真实执行回归：平台数据可选属性（followers）常显式缺失/为 null。"""
        doc = _doc()
        doc["author"]["followers"] = None
        assert UnifiedValidator().validate(doc) == []

    def test_valid_document_passes(self):
        assert UnifiedValidator().validate(_doc()) == []

    def test_missing_required_field_rejected(self):
        bad = _doc()
        del bad["raw_text"]
        errors = UnifiedValidator().validate(bad)
        assert any("raw_text" in e for e in errors)

    def test_bad_source_type_rejected(self):
        bad = _doc()
        bad["timeline_data"][0]["source_type"] = "BAD"
        errors = UnifiedValidator().validate(bad)
        assert any("source_type" in e for e in errors)

    def test_bad_platform_rejected(self):
        bad = _doc()
        bad["platform"] = "Bilibili"
        errors = UnifiedValidator().validate(bad)
        assert any("enum" in e or "platform" in e for e in errors)

    def test_timeline_item_missing_field_rejected(self):
        bad = _doc()
        del bad["timeline_data"][1]["time_end"]
        errors = UnifiedValidator().validate(bad)
        assert any("time_end" in e for e in errors)
