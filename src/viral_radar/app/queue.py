"""queue.py —— 手动触发的异步任务队列与容错（spec AC-3 / AC-16 / BUDGET-2 / INV-4）。

语义：
  - 任务按需 submit（手动触发，本模块不含任何定时/巡检机制——AC-3）；
  - 批次内单条处理失败：记录状态与错误、按 BUDGET-2 重试上限（2 次重试，
    即最多 3 次执行）重试，超限标记 failed 并跳过，同批次其余任务继续（INV-4 / BEH-17）；
  - 任务标识经 submit 返回值与 get() 可查询（AC-3 查询面）。
"""

from dataclasses import dataclass


class TaskState:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Task:
    """单条处理单元：状态、尝试次数与失败留痕。"""

    task_id: str
    state: str = TaskState.PENDING
    attempts: int = 0
    error: str | None = None


class TaskQueue:
    """内存任务注册表 + 批次执行器（含重试与跳过语义）。"""

    MAX_RETRIES = 2

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def submit(self, task_id: str) -> str:
        task = Task(task_id=task_id)
        self._tasks[task_id] = task
        return task_id

    def get(self, task_id: str) -> Task:
        return self._tasks[task_id]

    def run_batch(self, task_ids: list[str], handler) -> None:
        """逐条执行批次；单条失败不阻塞其余任务。

        handler(task_id) -> None，抛异常视为本次执行失败。
        """
        for task_id in task_ids:
            self._run_one(self._task(task_id), handler)

    def _task(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            self._tasks[task_id] = Task(task_id=task_id)
        return self._tasks[task_id]

    def _run_one(self, task: Task, handler) -> None:
        while True:
            task.state = TaskState.RUNNING
            try:
                handler(task)
                task.state = TaskState.DONE
                return
            except Exception as exc:  # 失败面未知统一折叠（BLE001 经 pyproject 豁免）
                task.attempts += 1
                task.error = str(exc)
                if task.attempts > self.MAX_RETRIES:
                    task.state = TaskState.FAILED
                    return
