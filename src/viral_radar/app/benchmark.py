"""benchmark.py —— 对标组管理与四维筛选（spec AC-2 / BEH-2）。

对标组：账号集合，规模收敛于 5-20（构造与增减均执法，越界即 ValueError）。
四维筛选：垂类关键词（账号 tags 命中）、点赞数、转发数、近期爆款频次——
apply() 产出确定顺序（爆款频次降序、同频按账号 id 升序），结果可复核。
"""

MIN_GROUP_SIZE = 5
MAX_GROUP_SIZE = 20


class BenchmarkGroup:
    """对标组：成员有序、规模受 5-20 约束。"""

    def __init__(self, name: str, members: list[str]) -> None:
        if not MIN_GROUP_SIZE <= len(members) <= MAX_GROUP_SIZE:
            raise ValueError(
                f"对标组成员数必须落在 {MIN_GROUP_SIZE}-{MAX_GROUP_SIZE} 区间"
                f"（实得 {len(members)}）"
            )
        self.name = name
        self._members = list(members)

    def members(self) -> list[str]:
        return list(self._members)


class GroupFilters:
    """四维筛选器；None 维度=不筛。"""

    def __init__(
        self,
        keyword: str | None = None,
        min_likes: int | None = None,
        min_shares: int | None = None,
        min_viral: int | None = None,
    ) -> None:
        self.keyword = keyword
        self.min_likes = min_likes
        self.min_shares = min_shares
        self.min_viral = min_viral

    def apply(self, pool: dict[str, dict]) -> list[str]:
        hits = []
        for account_id, stats in pool.items():
            if self.keyword is not None and self.keyword not in stats.get("tags", []):
                continue
            if self.min_likes is not None and stats.get("likes", 0) < self.min_likes:
                continue
            if self.min_shares is not None and stats.get("shares", 0) < self.min_shares:
                continue
            if self.min_viral is not None and stats.get("recent_viral_count", 0) < self.min_viral:
                continue
            hits.append(account_id)
        return sorted(
            hits,
            key=lambda aid: (-pool[aid].get("recent_viral_count", 0), aid),
        )
