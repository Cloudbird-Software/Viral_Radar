"""W3-C2 多账号聚合对比报告（pytest 面）：AC-11 聚合面——量化特征由拆解结果机械派生。"""

from viral_radar.analysis.report.aggregate import AggregateReportBuilder


def _report(account_id, head_intent="黄金3秒开头", head_time="00:00-00:03"):
    return {
        "overview": {"account_id": account_id},
        "video_details": [
            {
                "slices": [
                    {"time_range": head_time, "script_text": "a", "intent": head_intent},
                    {"time_range": "00:03-00:08", "script_text": "b", "intent": "干货输出"},
                ]
            }
        ],
    }


class TestAggregateReportBuilder:
    def test_quantified_hook_share_mechanical(self):
        reports = [
            _report("a1"),
            _report("a2", head_intent="痛点引入", head_time="00:01-00:04"),
            _report("a3"),
        ]
        out = AggregateReportBuilder().build(reports)
        q = out["quantified_common"]
        assert q["hook_opener_share"] == 0.67
        assert q["hook_first_five_count"] == 2  # a1 与 a3 前 5 秒黄金3秒开头

    def test_statement_expresses_share(self):
        out = AggregateReportBuilder().build([_report("a1"), _report("a2")])
        assert "前 5 秒" in out["quantified_common"]["statement"]

    def test_intent_distribution_sums_to_one(self):
        out = AggregateReportBuilder().build([_report("a1")])
        dist = out["quantified_common"]["intent_distribution"]
        assert round(sum(dist.values()), 3) == 1.0

    def test_common_patterns_derived(self):
        out = AggregateReportBuilder().build([_report("a1"), _report("a2", "黄金3秒开头")])
        top = out["quantified_common"]["common_hook_patterns"][0]
        assert top["sequence"] == ["黄金3秒开头", "干货输出"]
