"""single.py —— 单账号深度报告（spec AC-11 单账号面）。

四节齐备：overview（概览）/ video_details（视频级秒级拆解详情）/ outline（结构化大纲）
/ conclusion（爆款逻辑总结）。全部由 pipeline 产物机械装配，不引入主观判定。
"""

from viral_radar.analysis.summary import AccountSummarizer


class SingleReportBuilder:
    """单账号深度报告装配器。"""

    def build(
        self,
        account_id: str,
        profile: dict,
        docs: list[dict],
        slice_sets: list[list[dict]],
    ) -> dict:
        videos = []
        for doc, slices in zip(docs, slice_sets, strict=True):
            videos.append(
                {
                    "content_id": doc["task_id"],
                    "title": (doc.get("content_meta") or {}).get("title", ""),
                    "slices": [
                        {
                            "time_range": s["time_range"],
                            "intent": s["intent"],
                            "script_text": s["script_text"],
                        }
                        for s in slices
                    ],
                }
            )
        return {
            "overview": {
                "account_id": account_id,
                "name": profile.get("name", ""),
                "followers": profile.get("followers", 0),
                "video_count": len(videos),
                "platform": docs[0]["platform"] if docs else "",
            },
            "video_details": videos,
            "outline": self._outline(videos),
            "conclusion": AccountSummarizer().summarize(account_id, slice_sets),
        }

    def _outline(self, videos: list[dict]) -> dict:
        sections = []
        for video in videos:
            sections.append(
                {
                    "content_id": video["content_id"],
                    "title": video["title"],
                    "beats": [
                        {
                            "time_range": s["time_range"],
                            "hook": s["intent"],
                        }
                        for s in video["slices"]
                    ],
                }
            )
        return {"sections": sections, "note": "大纲由秒级拆解按时间轴机械生成"}
