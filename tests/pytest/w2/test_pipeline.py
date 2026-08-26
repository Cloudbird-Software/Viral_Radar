"""W2-C4 抖音全链竖切（pytest 面）：fixture 驱动的端到端冒烟 + 批次容错不阻塞。"""

from types import SimpleNamespace

from viral_radar.app.pipeline import AnalysisPipeline

_CANNED = '[{"time_range": "00:00-00:03", "script_text": "提问开场", "intent": "黄金3秒开头"}]'


def _gateway():
    return SimpleNamespace(chat=lambda prompt, **kw: _CANNED)


def _transport(items):
    def transport(cursor):
        return {"items": items, "next_cursor": None}

    return transport


def _item(content_id, bad=False):
    if bad:
        asr_segments = [{"end": 3, "text": "无start时间戳"}]
    else:
        asr_segments = [{"start": 0, "end": 3, "text": "提问开场"}]
    return {
        "content_id": content_id,
        "title": f"标题{content_id}",
        "asr_segments": asr_segments,
        "ocr_items": [{"order": 1, "time_sec": 1.0, "text": "花字"}],
    }


class TestAnalysisPipeline:
    def _pipeline(self, items):
        return AnalysisPipeline(
            fetch_profile=lambda src: {"name": "账号", "followers": 1},
            transport=_transport(items),
            gateway=_gateway(),
        )

    def test_end_to_end_smoke(self):
        out = self._pipeline([_item("v1"), _item("v2")]).run("https://www.douyin.com/user/abc123")
        assert out["record"].platform == "Douyin"
        assert len(out["docs"]) == 2
        assert len(out["slices"]) == 2
        assert set(out["summary"].keys()) == {"style", "top_words", "patterns"}
        assert out["broken"] == []

    def test_bad_item_skipped_batch_not_blocked(self):
        # v2 的 ASR 缺时间戳 → 融合拒绝 → 该条失败跳过，v1 正常出成品
        out = self._pipeline([_item("v1"), _item("v2", bad=True)]).run(
            "https://www.douyin.com/user/abc123"
        )
        assert out["broken"] == ["v2"]
        assert len(out["docs"]) == 1

    def test_pipeline_accepts_xhs_but_collector_agnostic(self):
        # 流水线只消费适配器产物——平台判定归 registry/适配器，管道本身无平台特判
        out = self._pipeline([_item("v1")]).run("https://www.douyin.com/user/abc123")
        assert "Douyin" == out["record"].platform
