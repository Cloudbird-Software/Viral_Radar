"""W0-C4 LLM 网关与版本化 Prompt 资产（pytest 面）。

覆盖 AC-17 热切换 / INV-5 单一接口 / INV-6 资产可溯源。
"""

import json
import sys

from viral_radar.analysis.assets import AnalysisAssets
from viral_radar.app.llm.gateway import LlmGateway

CANONICAL_LABELS = ["黄金3秒开头", "痛点引入", "情绪反转", "干货输出", "引导转化"]


class TestGateway:
    def _mock_config(self) -> dict:
        return {
            "providers": {
                "a": {"kind": "mock", "tag": "ALPHA"},
                "b": {"kind": "mock", "tag": "BETA"},
            }
        }

    def test_mock_switch_same_interface_no_code_change(self):
        gw = LlmGateway(self._mock_config())
        out_a = gw.chat("hi", provider="a")
        out_b = gw.chat("hi", provider="b")
        assert out_a.startswith("ALPHA")
        assert out_b.startswith("BETA")
        assert out_a != out_b

    def test_default_provider_routing(self):
        gw = LlmGateway(self._mock_config())
        assert gw.chat("hi").startswith("ALPHA")  # 首个 providers 条目为默认

    def test_unknown_provider_raises(self):
        gw = LlmGateway(self._mock_config())
        try:
            gw.chat("hi", provider="nope")
            raise AssertionError("应当拒绝未知供应商")
        except KeyError:
            pass

    def test_litellm_provider_lazy_import(self):
        config = {
            "providers": {
                "mock": {"kind": "mock", "tag": "M"},
                "real": {"kind": "litellm", "model": "openai/not-used"},
            }
        }
        gw = LlmGateway(config)
        assert "litellm" not in sys.modules
        assert gw.chat("hi", provider="mock").startswith("M")
        assert "litellm" not in sys.modules  # mock 路径不触网、不引依赖

    def test_config_file_roundtrip(self, tmp_path):
        path = tmp_path / "providers.json"
        path.write_text(json.dumps(self._mock_config(), ensure_ascii=False), encoding="utf-8")
        gw = LlmGateway.from_config_file(path)
        assert gw.chat("hi", provider="b").startswith("BETA")


class TestAssets:
    def test_intent_labels_canonical_and_enumerable(self):
        assert AnalysisAssets().intent_labels() == CANONICAL_LABELS

    def test_decompose_template_versioned_with_output_contract(self):
        tpl = AnalysisAssets().decompose_template(version=1)
        for keyword in ("time_range", "script_text", "intent"):
            assert keyword in tpl
