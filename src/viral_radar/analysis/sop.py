"""sop.py —— 拍摄 SOP 标准化输出（spec AC-12 / BEH-13）。

爆款逻辑 → 三类可执行条目：必含元素清单（must_have_elements）/ 时长限制
（duration_limit）/ 分镜要求（shot_requirements）。全部由报告数据机械派生：
  元素 = 最高频结构套路各 intent 逐条映射到可执行动作；
  时长 = 各视频时长中位数；
  分镜 = ASR 节拍切点对应的分段要求。
"""

from statistics import median


class SopBuilder:
    """拍摄 SOP 装配器（三类条目结构固定）。"""

    def build(self, report: dict, docs: list[dict]) -> dict:
        conclusion = report.get("conclusion") or {}

        def patterns():
            yield from (p.get("sequence") or [] for p in conclusion.get("patterns") or [])

        elements = []
        for seq in patterns():
            elements.extend(map(self._element_for, seq))
        return {
            "must_have_elements": list(dict.fromkeys(elements)),
            "duration_limit": self._duration(docs),
            "shot_requirements": self._shots(docs),
        }

    def _element_for(self, intent: str) -> str:
        table = {
            "黄金3秒开头": "开场钩子：前 3 秒内抛出提问或悬念（黄金3秒开头）",
            "痛点引入": "痛点锚点：3-8 秒内点名目标人群痛点",
            "情绪反转": "情绪反转：中段设置预期翻转或反差",
            "干货输出": "干货输出：至少一段可操作的具体方法步骤",
            "引导转化": "引导转化：结尾给出明确关注/行动指令",
        }
        return table.get(intent, intent)

    def _duration(self, docs: list[dict]) -> str:
        ends = [
            max((float(e["time_end"]) for e in doc.get("timeline_data", [])), default=0.0)
            for doc in docs
        ]
        seconds = int(median(ends)) if ends else 0
        return f"单条时长建议 {seconds} 秒左右（对标样本中位数，时长限制）"

    def _shots(self, docs: list[dict]) -> list[dict]:
        shots = []
        for doc in docs[:5]:
            asr_entries = [e for e in doc.get("timeline_data", []) if e.get("source_type") == "ASR"]
            shots.append(
                {
                    "content_id": doc["task_id"],
                    "beats": [
                        {"cut_at_s": round(float(e["time_end"]), 1), "note": "BGM 卡点切镜位"}
                        for e in asr_entries
                    ],
                }
            )
        return shots
