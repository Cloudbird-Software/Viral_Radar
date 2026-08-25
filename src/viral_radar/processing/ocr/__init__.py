"""ocr —— 画面 OCR 层（spec AC-6 / BEH-7 / DECISION-1：RapidOCR）。

产物契约：每条识别带 order（帧/图片顺序属性）、kind（花字/字幕/内嵌文案）、text。
kind 分类：视频画面按文字纵向位置（底部区域=字幕，其余=花字）、图文形态=内嵌。
引擎可注入；默认引擎惰性加载 RapidOCR（模型文件随运行时首次下载，测试不入网）。
"""

from viral_radar.processing.ocr.reader import OcrReader

__all__ = ["OcrReader"]
