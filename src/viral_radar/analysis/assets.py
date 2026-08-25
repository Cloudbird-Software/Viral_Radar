"""assets.py —— 版本化 Prompt 资产装载（spec INV-6 / IFACE-2 / IFACE-3）。

意图标签集与拆解 Prompt 模板以版本化文件落仓于 assets/v<version>/（仓库内可溯源），
禁止散落于代码或自由文本（INV-6）。本类只装载与交付，不含任何判定逻辑。
"""

import json
from pathlib import Path

_ROOT = Path(__file__).parent / "assets"


class AnalysisAssets:
    """版本化分析资产装载器（intent 标签集 / 拆解 Prompt 模板）。"""

    def intent_labels(self, version: int = 1) -> list[str]:
        """意图标签集（可枚举配置资产，IFACE-2）——资产内顺序即规范顺序。"""
        raw = (_ROOT / f"v{version}" / "intents.json").read_text(encoding="utf-8")
        return json.loads(raw)

    def decompose_template(self, version: int = 1) -> str:
        """秒级拆解 Prompt 模板（版本化字符串，IFACE-3）。"""
        return (_ROOT / f"v{version}" / "decompose.md").read_text(encoding="utf-8")
