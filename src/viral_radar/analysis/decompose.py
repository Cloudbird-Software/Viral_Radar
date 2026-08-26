"""decompose.py —— 秒级/段级结构化拆解引擎（spec AC-8 / IFACE-2 / BEH-9 / INV-6）。

输入 = 统一数据模型 JSON（W0-C2 schema 产物）；输出 = [{time_range, script_text, intent}]。
intent 值域必须来自版本化意图标签集（AnalysisAssets.intent_labels()），枚举外取值
fail-closed（ValueError）。Prompt 模板版本化资产（AnalysisAssets.decompose_template）。
LLM 调用一律经注入的 gateway（统一接口 chat），本模块不直连供应商 SDK。
"""

import json
import re

from viral_radar.analysis.assets import AnalysisAssets
from viral_radar.analysis.json_scan import scan_balanced_json

_TIME_RANGE = re.compile(r"^\d{1,2}:\d{2}(?:\.\d+)?-\d{1,2}:\d{2}(?:\.\d+)?$")


class DecomposeEngine:
    """统一数据模型 → 秒级拆解切片（结构 + 值域双重校验）。"""

    def decompose(self, doc: dict, gateway, **kwargs) -> list[dict]:
        assets = AnalysisAssets()
        prompt = (
            assets.decompose_template() + "\n\n输入 JSON：\n" + json.dumps(doc, ensure_ascii=False)
        )
        response = gateway.chat(prompt, **kwargs)
        slices = self._parse(response)
        return [self._validate(item) for item in slices]

    def _parse(self, response: str) -> list[dict]:
        """取第一个括号配平的完整 JSON 数组（LLM 输出前后常夹带自由文本）。

        括号配平扫描收敛至 analysis.json_scan（与 draft.py 双份复制合一）。
        """
        fragment = scan_balanced_json(
            response,
            opener="[",
            opens="[{",
            closes="]}",
            absent_message=f"拆解输出未含 JSON 数组（不可机器解析）：{response[:120]!r}",
            unclosed_message="拆解输出 JSON 数组未闭合",
        )
        try:
            parsed = json.loads(fragment)
        except ValueError as exc:
            raise ValueError(f"拆解输出 JSON 解析失败：{exc}") from exc
        if not isinstance(parsed, list):
            raise ValueError("拆解输出必须是 JSON 数组")
        return parsed

    def _validate(self, item) -> dict:
        if not isinstance(item, dict):
            raise ValueError(f"切片必须为对象：{item!r}")
        missing = [k for k in ("time_range", "script_text", "intent") if k not in item]
        if missing:
            raise ValueError(f"切片缺字段 {missing}（IFACE-2：time_range/script_text/intent）")
        time_range = str(item["time_range"])
        if not _TIME_RANGE.match(time_range):
            raise ValueError(f"time_range 格式非法：{time_range!r}（如 00:00-00:03）")
        intent = str(item["intent"])
        labels = AnalysisAssets().intent_labels()
        if intent not in labels:
            raise ValueError(f"intent 取值 {intent!r} 不在版本化意图标签集内 {labels}")
        return {
            "time_range": time_range,
            "script_text": str(item["script_text"]),
            "intent": intent,
        }
