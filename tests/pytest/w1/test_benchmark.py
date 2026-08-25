"""W1-C2 对标组管理与四维筛选（pytest 面）：AC-2 边界 5/20 收敛 + 四维筛选可复核。"""

from viral_radar.app.benchmark import BenchmarkGroup, GroupFilters


class TestBenchmark:
    def _pool(self) -> dict:
        return {
            "a1": {"tags": ["美妆"], "likes": 100, "shares": 50, "recent_viral_count": 3},
            "a2": {"tags": ["美食"], "likes": 200, "shares": 10, "recent_viral_count": 1},
            "a3": {"tags": ["美妆"], "likes": 300, "shares": 60, "recent_viral_count": 5},
            "a4": {"tags": ["知识"], "likes": 50, "shares": 5, "recent_viral_count": 0},
            "a5": {"tags": ["美妆"], "likes": 80, "shares": 20, "recent_viral_count": 2},
        }

    def _names(self, n: int) -> list[str]:
        return [f"x{i}" for i in range(n)]

    def test_size_bounds_5_20(self):
        BenchmarkGroup("ok-min", self._names(5))
        BenchmarkGroup("ok-max", self._names(20))
        for bad in (4, 21):
            try:
                BenchmarkGroup("bad", self._names(bad))
                raise AssertionError(f"{bad} 人组应当被拒绝")
            except ValueError:
                pass

    def test_four_dim_filter_combined(self):
        pool = self._pool()
        f = GroupFilters(keyword="美妆", min_likes=150, min_shares=55, min_viral=4)
        assert f.apply(pool) == ["a3"]

    def test_each_dimension_independent(self):
        pool = self._pool()
        assert GroupFilters(keyword="美妆").apply(pool) == ["a3", "a1", "a5"]
        assert GroupFilters(min_likes=200).apply(pool) == ["a3", "a2"]
        assert GroupFilters(min_shares=50).apply(pool) == ["a3", "a1"]
        assert GroupFilters(min_viral=3).apply(pool) == ["a3", "a1"]

    def test_deterministic_order_for_review(self):
        pool = self._pool()
        reordered = {k: pool[k] for k in reversed(list(pool))}
        f = GroupFilters(keyword="美妆")
        assert f.apply(pool) == f.apply(reordered)
        assert f.apply(pool) == ["a3", "a1", "a5"]
