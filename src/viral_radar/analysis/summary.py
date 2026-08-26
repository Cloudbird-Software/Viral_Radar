"""summary.py —— 账号爆款逻辑总结（spec AC-10 / BEH-11）。

单账号多条视频的拆解结果 → 三要素自然语言总结：
  - 叙事风格（style）：由意图分布机械定调（高频黄金3秒开头+情绪反转 → 强钩子叙事等）；
  - 高频词汇（top_words）：跨视频 script_text 词频统计（机械派生）；
  - 固定结构套路（patterns）：相邻 intent 序列频次最高的套路模板。
输出 dict 三键齐备、结构断言可机器复核。
"""

import re
from collections import Counter

from viral_radar.analysis.assets import AnalysisAssets

_TOKEN = re.compile(r"[一-鿿0-9]{2,}|[A-Za-z]{3,}")


class AccountSummarizer:
    """账号爆款逻辑总结器（机械派生，不引入主观判定）。"""

    def summarize(self, account_id: str, decompose_results: list[list[dict]]) -> dict:
        intents = [item["intent"] for slices in decompose_results for item in slices]
        words: Counter = Counter()
        for slices in decompose_results:
            for item in slices:
                words.update(_TOKEN.findall(str(item.get("script_text") or "")))
        return {
            "style": self._style(intents),
            "top_words": [word for word, _count in words.most_common(5)],
            "patterns": self._patterns(decompose_results),
        }

    def _style(self, intents: list[str]) -> str:
        if not intents:
            return "样本不足：暂无法归纳叙事风格"
        labels = AnalysisAssets().intent_labels()
        counts = Counter(intents)
        total = len(intents)
        golden = counts.get(labels[0], 0) / total  # 黄金3秒开头占比
        reversal = counts.get(labels[2], 0) / total  # 情绪反转占比
        if golden >= 0.4 and reversal >= 0.2:
            return "强钩子+情绪反转型叙事：黄金3秒提问/悬念开场，中段情绪翻转后收口"
        if golden >= 0.4:
            return "强钩子叙事：高频黄金3秒开场钩住留存，中段干货或痛点推进"
        return "平铺推进型叙事：以干货输出为主体节奏，缺少统一开场套路"

    def _patterns(self, decompose_results: list[list[dict]]) -> list[dict]:
        sequences = [tuple(item["intent"] for item in slices) for slices in decompose_results]
        if not sequences:
            return []
        return [
            {"sequence": list(seq), "count": count}
            for seq, count in Counter(sequences).most_common(3)
        ]
