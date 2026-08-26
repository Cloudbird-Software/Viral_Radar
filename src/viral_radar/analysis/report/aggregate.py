"""aggregate.py —— 多账号聚合对比报告（spec AC-11 聚合面 / BEH-12）。

跨账号共性特征的量化表述全部由各账号秒级拆解结果机械派生（不得引入主观判定）：
爆款开头手法占比（前 5 秒黄金3秒开头比例）、意图分布占比、跨账号常现开头套路。
"""

from collections import Counter

from viral_radar.analysis.assets import AnalysisAssets

_FIRST_FIVE = ("00:00", "00:01", "00:02", "00:03", "00:04", "00:05")


class AggregateReportBuilder:
    """聚合报告装配器（量化特征可逐项溯源回拆解结果）。"""

    def build(self, reports: list[dict]) -> dict:
        slice_sets = [
            video["slices"] for report in reports for video in report.get("video_details", [])
        ]
        intents = Counter(s["intent"] for slices in slice_sets for s in slices)
        total_slices = sum(intents.values()) or 1

        hook_openers = 0
        hook_first_five = 0
        for slices in slice_sets:
            if not slices:
                continue
            head = slices[0]
            if head["intent"] == AnalysisAssets().intent_labels()[0]:
                hook_openers += 1
                if str(head["time_range"]).startswith(_FIRST_FIVE):
                    hook_first_five += 1
        account_count = len(reports) or 1

        return {
            "accounts": [r["overview"]["account_id"] for r in reports],
            "quantified_common": {
                "hook_opener_share": round(hook_openers / account_count, 2),
                "hook_first_five_count": hook_first_five,
                "statement": (
                    f"{round(hook_first_five / account_count * 100)}% 的爆款都在前 5 秒"
                    "使用了（黄金3秒开头）"
                ),
                "intent_distribution": {
                    k: round(intents.get(k, 0) / total_slices, 3)
                    for k in AnalysisAssets().intent_labels()
                },
                "common_hook_patterns": self._patterns(slice_sets),
            },
        }

    def _patterns(self, slice_sets: list[list[dict]]) -> list[dict]:
        heads = [
            tuple(s["intent"] for s in slices[:2]) for slices in slice_sets if len(slices) >= 2
        ]
        return [
            {"sequence": list(seq), "count": count} for seq, count in Counter(heads).most_common(3)
        ]
