"""client.py —— 抖音采集通道（spec AC-4 抖音面 / BEH-4）。

本适配器只做两件事：经注入的 transport 拉取公开内容页，并把平台原始形态归一为
标准化元数据（content_id/url/published_at/likes/shares/top_comments）。近 6 个月
回溯=按 published_at 过滤窗口内条目。去重（BEH-5）归 W1-C4 处理——本卡不做跳重。

transport 契约：callable(page_cursor) -> {"items": [...], "next_cursor": str|None}；
测试注入 mock 数据源（spec 测试要求：契约测试 mock 数据源产出标准化元数据）。
未注入 transport 时 collect 直接拒绝（INV-3：无频控直连路径不存在）。
采集骨架（分页/窗口/INV-3 门禁）由 adapters.base 公共基座提供（PR #39/#53 骨架
与 #42/#43 同构——refactor 收敛为单一实现，归一逻辑仍在本文件）。
"""

from viral_radar.adapters.base import PlatformAdapter


class DouyinAdapter(PlatformAdapter):
    """抖音公开内容采集适配器。"""

    _NO_TRANSPORT_MSG = (
        "采集通道未注入合规传输层——直连采集被禁止（INV-3：仅公开数据 + 频控/代理默认启用）"
    )

    def _normalize(self, entry: dict) -> dict:
        # 标准化六字段覆盖同名原始键；未知扩展字段透传（fixture 内嵌
        # asr_segments/ocr_items/title 等下游提取素材经此进入处理链）。
        base = dict(entry)
        base.pop("video_url", None)
        base.update(
            {
                "content_id": str(entry.get("content_id") or entry.get("aweme_id") or ""),
                "url": entry.get("video_url") or entry.get("url") or "",
                "published_at": entry.get("published_at") or "",
                "likes": int(entry.get("likes") or 0),
                "shares": int(entry.get("shares") or 0),
                "top_comments": [str(c) for c in (entry.get("top_comments") or [])][:10],
            }
        )
        return base
