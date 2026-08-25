"""reader.py —— 花字/字幕/内嵌文案 OCR（spec AC-6 / BEH-7）。

引擎契约：callable(image_path) -> [{"text": str, "y_ratio": float}]（y_ratio=文字框
纵向中心位置/画面高度 [0..1]）。分类规则：视频形态 y_ratio>=0.78 → 字幕，否则花字；
图文形态一律内嵌。每条输出都带 order（帧序/图片顺序属性，spec AC-6）。
"""

from pathlib import Path

_SUBTITLE_ZONE = 0.78
KIND_CAPTION = "花字"
KIND_SUBTITLE = "字幕"
KIND_EMBEDDED = "内嵌"


class OcrReader:
    """画面文字识别入口（输出含顺序属性的三类文本清单）。"""

    def read(
        self,
        image_path: str | Path,
        order: int = 0,
        mode: str = "video",
        engine=None,
    ) -> list[dict]:
        runner = engine if engine is not None else self._default_engine
        items = []
        for item in runner(str(image_path)):
            y_ratio = float(item.get("y_ratio") or 1.0)
            kind = self._classify(y_ratio, mode)
            items.append(
                {
                    "order": int(order),
                    "kind": kind,
                    "text": str(item.get("text") or ""),
                }
            )
        return items

    def _default_engine(self, image_path: str) -> list[dict]:
        from rapidocr_onnxruntime import RapidOCR  # 惰性：stub 路径零外部依赖

        ocr = RapidOCR()
        result, _elapsed = ocr(image_path)
        if not result:
            return []
        image_height = self._image_height(image_path)
        return [
            {
                "text": str(line[1]),
                "y_ratio": (float(line[0][0][1]) + float(line[0][2][1])) / 2 / image_height,
            }
            for line in result
            if len(line) >= 2
        ]

    def _image_height(self, image_path: str) -> int:
        from PIL import Image  # rapidocr 依赖链内含 Pillow

        with Image.open(image_path) as img:
            return int(img.height)

    def _classify(self, y_ratio: float, mode: str) -> str:
        if mode != "video":
            return KIND_EMBEDDED
        if y_ratio >= _SUBTITLE_ZONE:
            return KIND_SUBTITLE
        return KIND_CAPTION
