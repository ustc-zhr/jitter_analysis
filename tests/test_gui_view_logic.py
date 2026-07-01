from datetime import datetime, timedelta
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jitter_analysis.domain.types import RunMode, RunStatus, ScanStepRecord
from jitter_analysis.gui.view_logic import (
    estimate_series_sample_interval,
    estimate_series_sample_interval_from_sample_indices,
    mode_key_from_run_mode,
    progress_tone,
    run_status_tone,
    single_knob_axis_name,
    single_knob_axis_summary_text,
    single_knob_step_axis_value,
)


def test_mode_and_tone_helpers():
    assert mode_key_from_run_mode(RunMode.KNOB_SCAN) == "single_knob_scan"
    assert mode_key_from_run_mode(None) == "timed_acquisition"
    assert progress_tone(0, 10) == "subtle"
    assert progress_tone(5, 10) == "info"
    assert progress_tone(10, 10) == "success"
    assert run_status_tone(RunStatus.COMPLETED) == "success"
    assert run_status_tone(RunStatus.FAILED) == "danger"


def test_single_knob_axis_helpers():
    step = ScanStepRecord(
        step_index=0,
        target_value=1.5,
        readback_value=None,
        started_at=datetime.now(),
    )

    assert single_knob_axis_name("target", "K1") == "K1 Target"
    assert single_knob_axis_name("readback", "K1") == "K1 Readback"
    assert "target" in single_knob_axis_summary_text("target")
    assert single_knob_step_axis_value("target", step) == 1.5
    assert single_knob_step_axis_value("readback", step) == 1.5
    step.readback_value = 1.45
    assert single_knob_step_axis_value("readback", step) == 1.45


def test_estimate_series_sample_interval_uses_median_positive_delta():
    start = datetime.fromisoformat("2026-05-20T10:00:00")
    timestamps = [
        start,
        start + timedelta(seconds=0.2),
        start + timedelta(seconds=0.4),
        start + timedelta(seconds=2.0),
    ]

    assert estimate_series_sample_interval(timestamps) == 0.2


def test_estimate_series_sample_interval_from_sample_indices_filters_missing_timestamps():
    start = datetime.fromisoformat("2026-05-20T10:00:00")
    sample_timestamps = [
        start,
        None,
        start + timedelta(seconds=0.2),
        start + timedelta(seconds=0.4),
    ]

    assert estimate_series_sample_interval_from_sample_indices([0, 1, 2, 3], sample_timestamps) == 0.2


def test_estimate_series_sample_interval_rejects_missing_positive_deltas():
    timestamp = datetime.fromisoformat("2026-05-20T10:00:00")

    with pytest.raises(ValueError, match="positive timestamp deltas"):
        estimate_series_sample_interval([timestamp, timestamp])
