"""fusion.py —— 数据融合对齐（spec AC-7 / BEH-8）：把标题 + ASR + OCR 融合为
统一数据模型 JSON（IFACE-1），产物必须通过 W0-C2 UnifiedValidator。

融合规则：
  - Title 段始终作为 timeline_data 首条（source_type=Title，占据 0..首个 ASR 起点或 0..0）；
  - ASR 分段照搬（source_type=ASR）；无时间戳段在此被拒绝（INV-2 fail-closed）；
  - OCR 条目按顺序属性映射为时间位置（视频形态取 time_sec，图文形态按序号占位），source_type=OCR；
  - 全量按 time_start 排序后通过 schema 校验器，不过即 ValueError。
"""

from viral_radar.processing.unified import UnifiedValidator


class FusionEngine:
    """统一数据模型的唯一装配点。"""

    def fuse(
        self,
        *,
        task_id: str,
        platform: str,
        content_type: str,
        author: dict,
        content_meta: dict,
        title: str,
        asr_segments: list[dict],
        ocr_items: list[dict],
    ) -> dict:
        asr_entries = [self._asr_segment(seg) for seg in asr_segments]
        timeline = [self._title_segment(title, asr_entries)]
        timeline.extend(asr_entries)
        for item in ocr_items:
            timeline.append(self._ocr_segment(item, content_type))
        timeline.sort(key=lambda entry: (entry["time_start"], entry["time_end"]))
        doc = {
            "task_id": task_id,
            "platform": platform,
            "content_type": content_type,
            "author": author,
            "content_meta": content_meta,
            "raw_text": "\n".join(e["raw_text"] for e in timeline),
            "timeline_data": timeline,
        }
        errors = UnifiedValidator().validate(doc)
        if errors:
            raise ValueError(f"融合产物未通过统一数据模型校验：{errors}")
        return doc

    def _title_segment(self, title: str, asr_entries: list[dict]) -> dict:
        if asr_entries:
            end = min(float(e["time_start"]) for e in asr_entries)
        else:
            end = 0.0
        return {"time_start": 0.0, "time_end": end, "source_type": "Title", "raw_text": title}

    def _asr_segment(self, seg: dict) -> dict:
        for key in ("start", "end"):
            if key not in seg or not isinstance(seg[key], (int, float)):
                raise ValueError(f"ASR 段缺时间戳字段 {key}——拒绝进入融合（INV-2）")
        return {
            "time_start": float(seg["start"]),
            "time_end": float(seg["end"]),
            "source_type": "ASR",
            "raw_text": str(seg.get("text") or ""),
        }

    def _ocr_segment(self, item: dict, content_type: str) -> dict:
        if content_type == "images":
            pos = float(item.get("order") or 0)
        else:
            pos = float(item.get("time_sec", item.get("order") or 0))
        return {
            "time_start": pos,
            "time_end": pos + 0.001,
            "source_type": "OCR",
            "raw_text": str(item.get("text") or ""),
        }
