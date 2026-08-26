"""transcriber.py —— 带时间戳的 ASR 转写（spec AC-5 / INV-2 / BEH-6）。

默认引擎 = faster-whisper（本卡 DECISION-1 选型，MIT），模型文件在首次转写时
惰性加载；engine 注入缝供测试与离线契约：callable(audio) -> [{start,end,text}]。
时间戳校验 fail-closed：任一段缺 start/end 或类型非法 → ValueError（拒绝进入融合）。
"""

from pathlib import Path


class WhisperTranscriber:
    """ASR 转写入口（输出恒为含秒级时间戳的分段列表）。"""

    def transcribe(self, audio: str | Path, engine=None) -> list[dict]:
        runner = engine if engine is not None else self._default_engine
        segments = runner(str(audio))
        self._validate(segments)
        return [self._normalize(seg) for seg in segments]

    def _default_engine(self, audio: str) -> list[dict]:
        from faster_whisper import WhisperModel  # 惰性：mock/stub 路径零外部依赖

        model = WhisperModel("small", device="cpu", compute_type="int8")
        raw, _info = model.transcribe(audio)
        return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in raw]

    def _validate(self, segments) -> None:
        for i, seg in enumerate(segments):
            start = seg.get("start")
            end = seg.get("end")
            missing = [k for k in ("start", "end") if k not in seg]
            if missing:
                raise ValueError(f"无时间戳的转写产物被拒绝（INV-2）：第 {i} 段缺 {missing}")
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                raise ValueError(f"时间戳必须为数值秒：第 {i} 段 start={start!r} end={end!r}")
            if end < start:
                raise ValueError(f"时间戳区间非法：第 {i} 段 start={start} end={end}")

    def _normalize(self, seg: dict) -> dict:
        return {
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": str(seg.get("text") or ""),
        }
