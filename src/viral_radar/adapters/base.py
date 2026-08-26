"""base.py —— 三平台采集适配器公共基座（spec AC-4 / BEH-4 / INV-3）。

抖音 / 小红书 / 视频号三适配器（PR #39/#42/#43）的采集骨架完全同构：
transport 分页拉取 → 近 N 个月回溯窗口过滤 → 平台形态归一。本模块把骨架
收敛为单一实现，各平台只保留差异化的 ``_normalize`` 归一逻辑与 INV-3 文案。

回溯窗口口径：months 按 30 天折算 + 3 天宽限（即历史实现的 30*months+3 天）；
无 published_at 的条目保守保留（窗口过滤只对带时间戳的条目生效）。
"""

from datetime import UTC, datetime, timedelta

DEFAULT_MONTHS = 6

_DAYS_PER_MONTH = 30
_WINDOW_SLACK_DAYS = 3


class PlatformAdapter:
    """带合规传输层门禁的采集适配器基类（无 transport 直接拒绝，INV-3）。"""

    # 默认拒绝文案；平台差异化补充说明由子类覆盖（语义不变，仅提示面差异）。
    _NO_TRANSPORT_MSG = "采集通道未注入合规传输层——直连采集被禁止（INV-3）"

    def __init__(self, transport=None) -> None:
        self._transport = transport

    def collect(self, account: str, months: int = DEFAULT_MONTHS) -> list[dict]:
        if self._transport is None:
            raise RuntimeError(self._NO_TRANSPORT_MSG)
        cutoff = datetime.now(UTC) - timedelta(days=_DAYS_PER_MONTH * months + _WINDOW_SLACK_DAYS)
        items = []
        cursor = None
        while True:
            page = self._transport(cursor)
            raw = page.get("items") or []
            for entry in raw:
                if self._within_window(entry, cutoff):
                    items.append(self._normalize(entry))
            cursor = page.get("next_cursor")
            if not cursor or not raw:
                break
        return items

    def _normalize(self, entry: dict) -> dict:
        raise NotImplementedError

    @staticmethod
    def _within_window(entry: dict, cutoff: datetime) -> bool:
        published = entry.get("published_at")
        if not published:
            return True  # 无时间戳不可判——保守保留（窗口过滤只对有时间的条目生效）
        return datetime.fromisoformat(str(published).replace("Z", "+00:00")) >= cutoff
