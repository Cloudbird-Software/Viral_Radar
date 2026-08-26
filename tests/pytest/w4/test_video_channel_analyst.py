"""W4-C4 视频号平台差异化分析（pytest 面）。"""

import pytest
from viral_radar.analysis.platforms.video_channel import VideoChannelAnalyst


class TestVideoChannelAnalyst:
    def test_two_outputs_independent(self):
        doc = {
            "platform": "VideoChannel",
            "timeline_data": [
                {"time_start": 0, "time_end": 2, "source_type": "ASR", "raw_text": "治愈共鸣"}
            ],
        }
        slices = [{"time_range": "00:00-00:02", "script_text": "治愈共鸣", "intent": "情绪反转"}]
        out = VideoChannelAnalyst().analyze(doc, slices)
        assert set(out.keys()) == {"social_currency", "emotional_resonance"}
        assert out["emotional_resonance"]["emotive_words_found"] == ["治愈", "共鸣"]

    def test_platform_isolation(self):
        with pytest.raises(ValueError):
            VideoChannelAnalyst().analyze({"platform": "XHS"}, [])
