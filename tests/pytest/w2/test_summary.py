"""W2-C3 账号爆款逻辑总结（pytest 面）：AC-10 三要素结构断言 + 机械派生复核。"""

from viral_radar.analysis.summary import AccountSummarizer


class TestAccountSummarizer:
    def _results(self) -> list[list[dict]]:
        return [
            [
                {
                    "time_range": "00:00-00:03",
                    "script_text": "黄金3秒开头 提问开场",
                    "intent": "黄金3秒开头",
                },
                {
                    "time_range": "00:03-00:08",
                    "script_text": "痛点引入 怎么省钱",
                    "intent": "痛点引入",
                },
                {
                    "time_range": "00:08-00:12",
                    "script_text": "情绪反转 万万没想到",
                    "intent": "情绪反转",
                },
            ],
            [
                {
                    "time_range": "00:00-00:03",
                    "script_text": "黄金3秒开头 提问开场",
                    "intent": "黄金3秒开头",
                },
                {
                    "time_range": "00:03-00:08",
                    "script_text": "干货输出 三步法",
                    "intent": "干货输出",
                },
            ],
        ]

    def test_three_elements_explicit(self):
        out = AccountSummarizer().summarize("acct1", self._results())
        assert set(out.keys()) == {"style", "top_words", "patterns"}

    def test_top_words_derived_by_frequency(self):
        out = AccountSummarizer().summarize("acct1", self._results())
        assert "黄金3秒开头" in out["top_words"]
        assert "提问开场" in out["top_words"]

    def test_structure_pattern_recorded(self):
        out = AccountSummarizer().summarize("acct1", self._results())
        top = out["patterns"][0]
        assert top["sequence"] == ["黄金3秒开头", "痛点引入", "情绪反转"]

    def test_style_reflects_hook_heavy_intent(self):
        out = AccountSummarizer().summarize("acct1", self._results())
        assert "黄金3秒" in out["style"]

    def test_empty_input_degrades_explicitly(self):
        out = AccountSummarizer().summarize("acct1", [])
        assert "样本不足" in out["style"]
        assert out["top_words"] == []
        assert out["patterns"] == []
