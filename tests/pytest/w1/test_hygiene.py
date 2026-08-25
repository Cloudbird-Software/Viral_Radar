"""W1-C4 采集去重与频控代理（pytest 面）：AC-15 频控触发 + 去重幂等 + INV-3 边界。"""

import time

import pytest
from viral_radar.adapters.hygiene import CompliantTransport, DedupeStore, HostGuard, RateLimiter


class TestDedupeStore:
    def test_idempotent_skip(self):
        store = DedupeStore()
        assert store.seen("v1") is False
        assert store.seen("v1") is True
        assert store.seen("v1") is True


class TestRateLimiter:
    def test_pacing_below_threshold(self):
        limiter = RateLimiter(min_interval_s=0.05)
        limiter.before_request()
        start = time.monotonic()
        limiter.before_request()
        assert time.monotonic() - start >= 0.045

    def test_proxy_rotation_round_robin(self):
        limiter = RateLimiter(proxies=["p1", "p2"], min_interval_s=0)
        seen = [limiter.before_request() for _ in range(4)]
        assert seen == ["p1", "p2", "p1", "p2"]

    def test_no_pool_is_slowdown_mode(self):
        limiter = RateLimiter(min_interval_s=0)
        assert limiter.before_request() is None


class TestHostGuard:
    def test_allowlisted_host_passes(self):
        HostGuard(["douyin.example"]).check("https://douyin.example/feed")

    def test_unknown_host_rejected(self):
        with pytest.raises(ValueError):
            HostGuard(["douyin.example"]).check("https://evil.example/x")

    def test_credential_paths_rejected(self):
        guard = HostGuard(["douyin.example"])
        for path in ("/passport/login", "/user/login", "/oauth", "/captcha"):
            with pytest.raises(ValueError):
                guard.check(f"https://douyin.example{path}")


class TestCompliantTransport:
    def test_guard_then_fetch_pipeline(self):
        calls = []

        def fetch(url, **kwargs):
            calls.append(url)
            return {"ok": 1}

        transport = CompliantTransport(
            fetch,
            HostGuard(["douyin.example"]),
            RateLimiter(min_interval_s=0),
        )
        assert transport.fetch("https://douyin.example/feed") == {"ok": 1}
        assert calls == ["https://douyin.example/feed"]

    def test_only_public_data_enforced(self):
        transport = CompliantTransport(
            lambda url: None,
            HostGuard(["douyin.example"]),
            RateLimiter(min_interval_s=0),
        )
        with pytest.raises(ValueError):
            transport.fetch("https://douyin.example/passport/session")
