"""W1-C5 ASR 音轨转写（pytest 面）：AC-5 时间戳转写 + INV-2 无时间戳拒绝（fail-closed）。"""

import pytest
from viral_radar.processing.asr import WhisperTranscriber


class TestWhisperTranscriber:
    def test_valid_segments_preserved_with_timestamps(self):
        good = [
            {"start": 0.0, "end": 2.5, "text": "黄金三秒"},
            {"start": 2.5, "end": 5.0, "text": "痛点引入"},
        ]
        out = WhisperTranscriber().transcribe("/fake.wav", engine=lambda a: good)
        assert out == good

    def test_missing_start_rejected(self):
        with pytest.raises(ValueError):
            WhisperTranscriber().transcribe(
                "/fake.wav", engine=lambda a: [{"end": 2.0, "text": "x"}]
            )

    def test_missing_end_rejected(self):
        with pytest.raises(ValueError):
            WhisperTranscriber().transcribe(
                "/fake.wav", engine=lambda a: [{"start": 0.0, "text": "x"}]
            )

    def test_non_numeric_timestamp_rejected(self):
        with pytest.raises(ValueError):
            WhisperTranscriber().transcribe(
                "/fake.wav", engine=lambda a: [{"start": "0秒", "end": 2.0, "text": "x"}]
            )

    def test_reversed_bounds_rejected(self):
        with pytest.raises(ValueError):
            WhisperTranscriber().transcribe(
                "/fake.wav", engine=lambda a: [{"start": 5.0, "end": 2.0, "text": "x"}]
            )

    def test_empty_segments_pass(self):
        assert WhisperTranscriber().transcribe("/fake.wav", engine=lambda a: []) == []
