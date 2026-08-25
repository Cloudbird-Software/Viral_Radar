"""registry.py —— 账号录入与平台判定（spec AC-1 / BEH-1）。

入口面：录入三平台账号链接或 ID，自动判定平台（三通道归位），拉取账号基础信息
（名称/粉丝数等，经注入的 fetcher——离线与测试注入 mock 数据源，真实拉取仅触碰
公开可浏览数据）；判定结果可持久化（JSON 文件）并可按原始输入查询。
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

PLATFORM_DOUYIN = "Douyin"
PLATFORM_XHS = "XHS"
PLATFORM_VIDEO_CHANNEL = "VideoChannel"

_FETCHER = Callable[[str], dict]


@dataclass
class AccountRecord:
    """一次录入的判定结果：平台归位 + 基础信息 + 原始输入。"""

    source: str
    platform: str
    profile: dict


class AccountRegistry:
    """账号注册表：判定、归位、持久化、查询的单一入口。"""

    def __init__(self, fetch_profile: _FETCHER | None = None) -> None:
        self._fetch = fetch_profile if fetch_profile is not None else (lambda src: {})
        self._records: dict[str, AccountRecord] = {}

    def classify(self, source: str) -> str:
        """平台判定：链接形态（主机名域边界匹配）与 ID 形态双口径。"""
        host = self._host_of(source)
        if host and (host == "douyin.com" or host.endswith(".douyin.com")):
            return PLATFORM_DOUYIN
        if host and (
            host == "xiaohongshu.com"
            or host.endswith(".xiaohongshu.com")
            or host == "xhslink.com"
            or host.endswith(".xhslink.com")
        ):
            return PLATFORM_XHS
        if host and host.endswith(".channels.weixin.qq.com"):
            return PLATFORM_VIDEO_CHANNEL
        if host:
            raise ValueError(f"无法判定平台：{source!r}（主机 {host} 不在已知平台域内）")
        text = source.lower()
        if text.startswith(("v.douyin.com/", "iesdouyin.com/")):
            return PLATFORM_DOUYIN
        if source.startswith("finder-"):
            return PLATFORM_VIDEO_CHANNEL
        # 小红书 ID 形态：24 位十六进制串（5f…/63… 前缀簇）
        if len(source) == 24 and all(c in "0123456789abcdef" for c in source):
            return PLATFORM_XHS
        if source.isdigit():
            return PLATFORM_DOUYIN
        raise ValueError(f"无法判定平台：{source!r}")

    @staticmethod
    def _host_of(source: str) -> str:
        return (urlsplit(source).hostname or "").lower()

    def register(self, source: str) -> AccountRecord:
        record = AccountRecord(
            source=source,
            platform=self.classify(source),
            profile=self._fetch(source),
        )
        self._records[source] = record
        return record

    def get(self, source: str) -> AccountRecord:
        return self._records[source]

    def save(self, path: str | Path) -> None:
        payload = [
            {"source": r.source, "platform": r.platform, "profile": r.profile}
            for r in self._records.values()
        ]
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path, fetch_profile: _FETCHER | None = None) -> "AccountRegistry":
        registry = cls(fetch_profile=fetch_profile)
        for item in json.loads(Path(path).read_text(encoding="utf-8")):
            registry._records[item["source"]] = AccountRecord(
                source=item["source"],
                platform=item["platform"],
                profile=item["profile"],
            )
        return registry
