"""hygiene.py —— 采集去重与频控代理（spec AC-4 去重面 / AC-15 / INV-3 / BEH-5 / BEH-16）。

三件套：
  - DedupeStore：内容指纹幂等跳重（同一内容再入采集范围 → 识别并跳过，BEH-5）；
  - RateLimiter：频控阈值 + 代理 IP 池轮换（达到阈值 → 降频或轮换后继续，BEH-16）；
  - HostGuard：公开数据边界——主机白名单 + 凭据/登录路径拦截（仅公开可浏览数据，
    无账号密码代登录路径，INV-3）；
  - CompliantTransport：把三者编织成唯一出站通道（guard → limiter → fetch）。
"""

import time
from urllib.parse import urlsplit

_CREDENTIAL_PATHS = ("/passport/", "login", "session", "oauth", "captcha")


class DedupeStore:
    """内容去重：同一 content_id 首次放行、再次跳过（幂等）。"""

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def seen(self, content_id: str) -> bool:
        if content_id in self._seen:
            return True
        self._seen.add(content_id)
        return False


class RateLimiter:
    """频控：每次出站请求前保证最小间隔；代理池按序轮换（无池=降频模式）。"""

    def __init__(self, proxies: list[str] | None = None, min_interval_s: float = 1.0) -> None:
        self._proxies = list(proxies or [])
        self._min_interval = min_interval_s
        self._last_ts = 0.0
        self._cursor = 0

    def before_request(self) -> str | None:
        elapsed = time.monotonic() - self._last_ts
        wait = self._min_interval - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_ts = time.monotonic()
        if not self._proxies:
            return None  # 降频模式
        proxy = self._proxies[self._cursor % len(self._proxies)]
        self._cursor += 1
        return proxy


class HostGuard:
    """公开数据边界：白名单主机 + 凭据路径拦截（fail-closed）。"""

    def __init__(self, allowed_hosts: list[str]) -> None:
        self._hosts = [h.lower() for h in allowed_hosts]

    def check(self, url: str) -> None:
        host = (urlsplit(url).hostname or "").lower()
        if host not in self._hosts:
            raise ValueError(f"主机不在公开采集白名单：{host or url!r}")
        path = urlsplit(url).path.lower()
        for marker in _CREDENTIAL_PATHS:
            if marker in path:
                raise ValueError(f"凭据/登录路径禁止采集：{path!r}（INV-3）")


class CompliantTransport:
    """唯一出站通道：guard 合规检查 → limiter 频控/轮换 → fetch 真实拉取。"""

    def __init__(self, fetch, guard: HostGuard, limiter: RateLimiter) -> None:
        self._fetch = fetch
        self._guard = guard
        self._limiter = limiter

    def fetch(self, url: str, *args, **kwargs):
        self._guard.check(url)
        self._limiter.before_request()
        return self._fetch(url, *args, **kwargs)
