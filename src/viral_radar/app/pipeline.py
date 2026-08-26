"""pipeline.py —— 抖音全链竖切流水线（spec W2-C4：录入→采集→提取→融合→拆解→总结）。

本卡把 W0+W1+W2 各模块组装为可注入的统一入口（fixture 驱动，不依赖外网）：
  - 录入/判定：AccountRegistry（fetch_profile 注入）；
  - 采集：DouyinAdapter（transport 注入——fixture 条目内嵌 asr_segments/ocr_items）；
  - 提取+融合：FusionEngine（每条目出一条统一数据模型 JSON）；
  - 拆解：DecomposeEngine（gateway 注入，mock 供应商可离线）；
  - 总结：AccountSummarizer；
  - 批次容错：TaskQueue 贯穿逐条目处理——单条失败按 BUDGET-2 重试后标记跳过，
    不阻塞整批（INV-4）。
"""

from viral_radar.adapters.douyin import DouyinAdapter
from viral_radar.adapters.registry import AccountRegistry
from viral_radar.analysis.decompose import DecomposeEngine
from viral_radar.analysis.summary import AccountSummarizer
from viral_radar.app.queue import TaskQueue, TaskState
from viral_radar.processing.unified.fusion import FusionEngine


class AnalysisPipeline:
    """开箱组装的全链入口（全部依赖可注入）。"""

    def __init__(self, fetch_profile=None, transport=None, gateway=None) -> None:
        self._registry = AccountRegistry(fetch_profile=fetch_profile)
        self._adapter = DouyinAdapter(transport=transport)
        self._fusion = FusionEngine()
        self._decompose = DecomposeEngine()
        self._summary = AccountSummarizer()
        self._queue = TaskQueue()
        self._gateway = gateway

    def run(self, account_source: str) -> dict:
        record = self._registry.register(account_source)
        items = self._adapter.collect(account_source)
        results: dict[str, tuple[dict, list[dict]]] = {}

        def handle(task):
            item = next(i for i in items if i["content_id"] == task.task_id)
            results[task.task_id] = self._process_one(item, record)

        item_ids = [item["content_id"] for item in items]
        for content_id in item_ids:
            self._queue.submit(content_id)
        self._queue.run_batch(item_ids, handle)

        docs = [results[cid][0] for cid in item_ids if cid in results]
        slice_sets = [results[cid][1] for cid in item_ids if cid in results]
        broken = [cid for cid in item_ids if self._queue.get(cid).state == TaskState.FAILED]
        return {
            "record": record,
            "docs": docs,
            "slices": slice_sets,
            "summary": self._summary.summarize(record.source, slice_sets),
            "broken": broken,
        }

    def _process_one(self, item: dict, record) -> tuple[dict, list[dict]]:
        doc = self._fusion.fuse(
            task_id=item["content_id"],
            platform=record.platform,
            content_type="video",
            author=record.profile,
            content_meta={"title": item.get("title") or item["content_id"]},
            title=item.get("title") or "",
            asr_segments=item.get("asr_segments") or [],
            ocr_items=item.get("ocr_items") or [],
        )
        slices = self._decompose.decompose(doc, self._gateway)
        return doc, slices
