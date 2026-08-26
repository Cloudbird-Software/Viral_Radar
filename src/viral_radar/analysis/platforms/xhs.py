"""xhs.py —— 小红书平台差异化分析面（spec AC-9 小红书面 / IFACE-4 / BEH-10）。

三产物独立存在且互不可替换：封面吸引力分析（cover_appeal）、种草转化路径拆解
（seeding_path）、图文排版逻辑总结（layout_logic）。只接受 platform=XHS 输入。
"""

from viral_radar.analysis.assets import AnalysisAssets

_PLATFORM = "XHS"


class XhsAnalyst:
    """小红书差异化分析：三产物结构固定，机械派生。"""

    def analyze(self, doc: dict, decompose_slices: list[dict]) -> dict:
        if doc.get("platform") != _PLATFORM:
            raise ValueError(f"小红书分析面只接受 platform={_PLATFORM}（IFACE-4）")
        cover = (doc.get("content_meta") or {}).get("title", "")
        return {
            "cover_appeal": self._cover_appeal(cover),
            "seeding_path": self._seeding_path(decompose_slices),
            "layout_logic": self._layout_logic(doc),
        }

    def _cover_appeal(self, title: str) -> dict:
        hooks = ("？", "?", "!", "秒", "干货", "避坑")
        hit = [h for h in hooks if h in title]
        return {
            "title": title,
            "hook_markers_found": sorted(hit),
            "suggestion": (
                "封面标题含悬念/数字钩子，吸引力强"
                if hit
                else "封面标题缺钩子元素，建议加入数字或悬念词"
            ),
        }

    def _seeding_path(self, slices: list[dict]) -> dict:
        labels = AnalysisAssets().intent_labels()
        sequence = [s["intent"] for s in slices]
        return {
            "steps": sequence,
            "has_seed_conversion": labels[3] in sequence and labels[4] in sequence,
            "suggestion": "种草转化链完整：干货铺垫 → 转化引导" if sequence else "样本不足",
        }

    def _layout_logic(self, doc: dict) -> dict:
        entries = doc.get("timeline_data") or []
        ocr_orders = sorted(
            {int(e["time_start"]) for e in entries if e.get("source_type") == "OCR"}
        )
        return {
            "image_slots": ocr_orders,
            "suggestion": (
                f"图文按 {len(ocr_orders)} 个版面位推进：封面引爆点 + 内页渐进种草"
                if ocr_orders
                else "无 OCR 版面数据"
            ),
        }
