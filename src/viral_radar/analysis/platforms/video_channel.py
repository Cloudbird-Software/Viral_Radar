"""video_channel.py —— 视频号平台差异化分析面（spec AC-9 视频号面 / IFACE-4 / BEH-10）。

两产物独立存在且互不可替换：社交货币属性分析（social_currency）、情绪共鸣点提取
（emotional_resonance）。只接受 platform=VideoChannel 输入。
"""

from collections import Counter

from viral_radar.analysis.assets import AnalysisAssets

_PLATFORM = "VideoChannel"


class VideoChannelAnalyst:
    """视频号差异化分析：两产物结构固定，机械派生。"""

    def analyze(self, doc: dict, decompose_slices: list[dict]) -> dict:
        if doc.get("platform") != _PLATFORM:
            raise ValueError(f"视频号分析面只接受 platform={_PLATFORM}（IFACE-4）")
        labels = AnalysisAssets().intent_labels()
        intents = Counter(s["intent"] for s in decompose_slices)
        shareable = [i for i in (labels[0], labels[2]) if intents.get(i)]
        return {
            "social_currency": {
                "shareable_intents": shareable,
                "suggestion": (
                    "社交货币强：含转发动机钩子（黄金3秒/情绪反转）"
                    if shareable
                    else "社交货币弱：建议强化可转发的情绪/身份表达"
                ),
            },
            "emotional_resonance": self._resonance(doc, intents),
        }

    def _resonance(self, doc: dict, intents: Counter) -> dict:
        words = " ".join(str(e.get("raw_text") or "") for e in doc.get("timeline_data") or [])
        emotive = [w for w in ("感动", "治愈", "破防", "共鸣", "焦虑", "骄傲") if w in words]
        return {
            "emotive_words_found": emotive,
            "pain_point_present": intents.get("痛点引入", 0) > 0,
            "suggestion": "情绪共鸣点明确" if emotive else "建议显式植入情绪触点词",
        }
