"""W1-C1 账号录入与平台判定（pytest 面）：AC-1 三平台归位 / 基础信息 / 持久化可查。"""

import json

import pytest
from viral_radar.adapters.registry import (
    PLATFORM_DOUYIN,
    PLATFORM_VIDEO_CHANNEL,
    PLATFORM_XHS,
    AccountRegistry,
)


class TestAccountRegistry:
    def _fetch(self, src: str) -> dict:
        return {"name": f"账号{src[-3:]}", "followers": 1234}

    def test_three_platforms_classified_into_own_channel(self):
        reg = AccountRegistry(fetch_profile=self._fetch)
        assert reg.classify("https://www.douyin.com/user/abc123") == PLATFORM_DOUYIN
        assert reg.classify("https://www.xiaohongshu.com/user/profile/5f3a") == PLATFORM_XHS
        assert reg.classify("finder-abc") == PLATFORM_VIDEO_CHANNEL

    def test_id_shapes_classified(self):
        reg = AccountRegistry(fetch_profile=self._fetch)
        assert reg.classify("123456789") == PLATFORM_DOUYIN
        assert reg.classify("5f3af0000000000000000000") == PLATFORM_XHS

    def test_unknown_input_rejected(self):
        reg = AccountRegistry(fetch_profile=self._fetch)
        try:
            reg.classify("not-a-platform")
            raise AssertionError("非法输入应当被拒绝")
        except ValueError:
            pass

    def test_hostname_boundary_not_spoofable(self):
        reg = AccountRegistry(fetch_profile=self._fetch)
        with pytest.raises(ValueError):
            reg.classify("https://evil.example/douyin.com")
        with pytest.raises(ValueError):
            reg.classify("https://douyin.com.evil.example/u")

    def test_register_pulls_profile(self):
        reg = AccountRegistry(fetch_profile=self._fetch)
        record = reg.register("finder-abc")
        assert record.platform == PLATFORM_VIDEO_CHANNEL
        assert record.profile["followers"] == 1234

    def test_persist_and_query(self, tmp_path):
        reg = AccountRegistry(fetch_profile=self._fetch)
        original = reg.register("https://www.douyin.com/user/abc123")
        path = tmp_path / "registry.json"
        reg.save(path)
        loaded = AccountRegistry.load(path, fetch_profile=self._fetch)
        restored = loaded.get(original.source)
        assert restored.platform == original.platform
        assert restored.profile == original.profile
        assert json.loads(path.read_text(encoding="utf-8"))[0]["platform"] == PLATFORM_DOUYIN
