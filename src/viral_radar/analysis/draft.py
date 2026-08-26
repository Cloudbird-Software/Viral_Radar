"""draft.py —— 脚本草稿仿写生成（spec AC-13 / BEH-14 / IR-6）。

调取账号爆款逻辑特征（summary 三要素）+ 用户主题输入 → 三段结构草稿：
场景描述（scene）/ 口播台词（script）/ 运镜与画面建议（camera）。
特征引用可追溯：based_on 显式记录所引用的叙事风格/高频词汇/固定套路，机械可查。
LLM 调用经注入 gateway；驱动/测试用 mock 供应商（响应 tag 携带 JSON）。
"""

import json

from viral_radar.analysis.json_scan import scan_balanced_json


class ScriptDraftGenerator:
    """三段结构脚本草稿生成器（输出与特征引用可机器复核）。"""

    def generate(self, account_id: str, topic: str, summary: dict, gateway) -> dict:
        feature_brief = {
            "叙事风格": (summary.get("style") or ""),
            "高频词汇": (summary.get("top_words") or [])[:3],
            "固定套路": [p.get("sequence") or [] for p in (summary.get("patterns") or [])][:1],
        }
        prompt = (
            f"为账号 {account_id} 仿写新视频主题「{topic}」的脚本草稿，"
            f"沿用其爆款逻辑特征 {json.dumps(feature_brief, ensure_ascii=False)}。"
            "输出 JSON 对象（scene/script/camera 三键）。"
        )
        response = gateway.chat(prompt)
        parsed = self._parse(response)
        draft = {
            "scene": str(parsed.get("scene") or ""),
            "script": str(parsed.get("script") or ""),
            "camera": str(parsed.get("camera") or ""),
            "based_on": feature_brief,
        }
        return draft

    def _parse(self, response: str) -> dict:
        """取第一个括号配平的完整 JSON 对象（LLM 输出前后常夹带自由文本）。

        括号配平扫描收敛至 analysis.json_scan（与 decompose.py 双份复制合一）；
        json.loads 失败在此保持原样上抛（历史语义：本调用点不做二次包装）。
        """
        fragment = scan_balanced_json(
            response,
            opener="{",
            opens="{",
            closes="}",
            absent_message=f"仿写输出未含 JSON 对象：{response[:120]!r}",
            unclosed_message="仿写输出 JSON 对象未闭合",
        )
        parsed = json.loads(fragment)
        if not isinstance(parsed, dict):
            raise ValueError("仿写输出必须是 JSON 对象")
        missing = [k for k in ("scene", "script", "camera") if k not in parsed]
        if missing:
            raise ValueError(f"仿写草稿缺三段字段 {missing}")
        return parsed
