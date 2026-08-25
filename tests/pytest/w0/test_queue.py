"""W0-C3 任务队列与容错（pytest 面）：AC-3 查询面 / AC-16 跳过语义 / BUDGET-2 重试上限。"""

import pathlib

from viral_radar.app.queue import TaskQueue, TaskState

ROOT = pathlib.Path(__file__).resolve().parents[3]


class TestTaskQueue:
    def test_submit_returns_queryable_id(self):
        q = TaskQueue()
        q.submit("a1")
        task = q.get("a1")
        assert task.task_id == "a1"
        assert task.state == TaskState.PENDING

    def test_batch_continues_after_single_failure(self):
        q = TaskQueue()

        def handler(task):
            if task.task_id == "bad":
                raise RuntimeError("boom")

        q.run_batch(["good", "bad", "good2"], handler)
        assert q.get("good").state == TaskState.DONE
        assert q.get("good2").state == TaskState.DONE
        assert q.get("bad").state == TaskState.FAILED

    def test_retry_limit_is_two(self):
        q = TaskQueue()
        calls = []

        def handler(task):
            calls.append(task.task_id)
            raise ValueError("nope")

        q.run_batch(["x"], handler)
        task = q.get("x")
        assert len(calls) == 3  # 首执 + 2 次重试（BUDGET-2）
        assert task.attempts == 3
        assert task.state == TaskState.FAILED
        assert "nope" in task.error

    def test_error_recorded_then_skipped(self):
        q = TaskQueue()

        def handler(task):
            raise RuntimeError("die")

        q.run_batch(["x", "y"], handler)
        assert q.get("x").state == TaskState.FAILED
        assert "die" in q.get("x").error
        assert q.get("y").state == TaskState.FAILED  # 同批次他人照常处理

    def test_no_scheduled_scan_in_module(self):
        source = (ROOT / "src" / "viral_radar" / "app" / "queue.py").read_text(encoding="utf-8")
        assert "Timer" not in source and "sched" not in source
