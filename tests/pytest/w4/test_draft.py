"""W4-C5 脚本草稿仿写生成（pytest 面）：三段结构断言 + 特征引用可追溯。"""

from types import SimpleNamespace

import pytest
from viral_radar.analysis.draft import ScriptDraftGenerator


class TestScriptDraftGenerator:
    def _gateway(self, response):
        return SimpleNamespace(chat=lambda p, **kw: response)

    def _summary(self):
        return {
            "style": "强钩子",
            "top_words": ["美妆", "三步"],
            "patterns": [{"sequence": ["黄金3秒开头", "干货输出"], "count": 1}],
        }

    def test_three_section_draft_with_traceable_features(self):
        canned = '{"scene": "居家场景", "script": "口播台词：三步美妆法", "camera": "特写+慢推"}'
        out = ScriptDraftGenerator().generate(
            "a1", "新手美妆", self._summary(), self._gateway(canned)
        )
        assert set(out.keys()) == {"scene", "script", "camera", "based_on"}
        assert out["based_on"]["叙事风格"] == "强钩子"
        assert out["based_on"]["高频词汇"] == ["美妆", "三步"]

    def test_segments_nonempty(self):
        canned = '{"scene": "s", "script": "x", "camera": "c"}'
        out = ScriptDraftGenerator().generate("a1", "t", self._summary(), self._gateway(canned))
        assert out["scene"] == "s" and out["script"] == "x" and out["camera"] == "c"

    def test_missing_section_rejected(self):
        with pytest.raises(ValueError):
            ScriptDraftGenerator().generate(
                "a1", "t", self._summary(), self._gateway('{"scene": "x", "script": "y"}')
            )
