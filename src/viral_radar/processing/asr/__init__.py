"""asr —— 音频转写层（spec AC-5 / INV-2 / BEH-6 / DECISION-1：faster-whisper）。

产物契约：分段文本列表，每段含 start/end（秒级时间戳）与 text。
无时间戳的转写产物在该层即被拒绝（fail-closed），不进入融合阶段（INV-2）。
引擎可注入（测试/离线以 stub 替代；默认引擎惰性加载 faster-whisper）。
"""

from viral_radar.processing.asr.transcriber import WhisperTranscriber

__all__ = ["WhisperTranscriber"]
