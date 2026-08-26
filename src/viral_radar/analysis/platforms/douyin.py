"""douyin.py —— 抖音平台差异化分析面（spec AC-9 抖音面 / IFACE-4 / BEH-10）。

三产物独立存在且互不可替换：节奏分析（rhythm）、BGM 卡点建议（bgm）、黄金 3 秒
留存分析（golden_three）。全部由拆解结果与时间轴机械派生——不做主观判定。
只接受 platform=Douyin 的统一数据模型输入（平台分析面互不可替换：IFACE-4）。
"""

from viral_radar.analysis.assets import AnalysisAssets

_PLATFORM = "Douyin"

# BGM 卡点分档阈值（秒）：按 ASR 平均分段时长机械定档（密集 <2 ≤ 中速 <5 ≤ 慢速）。
_BGM_DENSE_MAX_S = 2.0
_BGM_MID_MAX_S = 5.0


class DouyinAnalyst:
    """抖音差异化分析：三产物结构固定的 dict。"""

    def analyze(self, doc: dict, decompose_slices: list[dict]) -> dict:
        if doc.get("platform") != _PLATFORM:
            raise ValueError(
                f"抖音分析面只接受 platform={_PLATFORM}，实得 {doc.get('platform')!r}（IFACE-4）"
            )
        entries = doc.get("timeline_data") or []
        rhythm = self._rhythm(entries)
        return {
            "rhythm": rhythm,
            "bgm": self._bgm(rhythm),
            "golden_three": self._golden_three(decompose_slices),
        }

    def _rhythm(self, entries: list[dict]) -> dict:
        durations = [
            float(e["time_end"]) - float(e["time_start"])
            for e in entries
            if e.get("source_type") == "ASR"
        ]
        if not durations:
            return {"avg_segment_s": 0.0, "beats": []}
        return {
            "avg_segment_s": round(sum(durations) / len(durations), 2),
            "beats": [round(d, 2) for d in durations],
        }

    def _bgm(self, rhythm: dict) -> str:
        beats = rhythm.get("beats") or []
        if not beats:
            return "无 ASR 节拍数据，BGM 卡点建议不适用"
        mean = rhythm["avg_segment_s"]
        if mean < _BGM_DENSE_MAX_S:
            return "密集切镜节奏：建议 BGM 卡点间隔 ≤2s，鼓点对齐每段 ASR 分界"
        if mean < _BGM_MID_MAX_S:
            return "中速叙事节奏：建议 BGM 在段间停顿处换拍，卡点间隔 2-5s"
        return "慢叙事节奏：建议 BGM 低频推进，卡点与情绪反转段对齐"

    def _golden_three(self, slices: list[dict]) -> dict:
        head = [s for s in slices if s.get("intent") == AnalysisAssets().intent_labels()[0]]
        return {
            "golden_intent_found": bool(head),
            "golden_three_slices": [
                s["time_range"] for s in head if str(s["time_range"]).startswith("00:0")
            ],
        }
