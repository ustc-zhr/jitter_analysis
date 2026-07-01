from __future__ import annotations

from datetime import datetime
from typing import Iterable

from ..domain.types import RunMode, RunStatus, ScanStepRecord


def mode_key_from_run_mode(mode: RunMode | None) -> str:
    mapping = {
        RunMode.TIMED_ACQUISITION: "timed_acquisition",
        RunMode.KNOB_SCAN: "single_knob_scan",
        RunMode.MULTI_KNOB_RANDOM: "multi_knob_random",
    }
    return mapping.get(mode, "timed_acquisition")


def progress_tone(completed: int, total: int) -> str:
    if total <= 0 or completed <= 0:
        return "subtle"
    if completed >= total:
        return "success"
    return "info"


def run_status_tone(status: RunStatus) -> str:
    if status == RunStatus.COMPLETED:
        return "success"
    if status == RunStatus.STOPPED:
        return "warning"
    if status == RunStatus.FAILED:
        return "danger"
    if status == RunStatus.RUNNING:
        return "info"
    return "subtle"


def single_knob_axis_name(axis_source: str, knob_name: str = "") -> str:
    base_name = knob_name.strip() or "Knob Value"
    if axis_source == "target":
        return f"{base_name} Target"
    return f"{base_name} Readback"


def single_knob_axis_summary_text(axis_source: str) -> str:
    if axis_source == "target":
        return "Sensitivity uses target knob values on the x-axis."
    return "Sensitivity uses knob readback on the x-axis, with target fallback if readback is unavailable."


def single_knob_step_axis_value(axis_source: str, step: ScanStepRecord) -> float | None:
    if axis_source == "target":
        return step.target_value
    return step.readback_value if step.readback_value is not None else step.target_value


def estimate_series_sample_interval(timestamps: Iterable[datetime]) -> float:
    rows = list(timestamps)
    if len(rows) < 2:
        raise ValueError("At least two timestamps are required.")
    deltas = []
    for left, right in zip(rows, rows[1:]):
        delta = (right - left).total_seconds()
        if delta > 0.0:
            deltas.append(delta)
    if not deltas:
        raise ValueError("No positive timestamp deltas are available.")
    deltas.sort()
    mid = len(deltas) // 2
    if len(deltas) % 2 == 1:
        return float(deltas[mid])
    return float((deltas[mid - 1] + deltas[mid]) / 2.0)


def estimate_series_sample_interval_from_sample_indices(
    sample_indices,
    sample_timestamps: list[datetime | None],
) -> float:
    timestamps = []
    for sample_index in sample_indices:
        if sample_index is None:
            continue
        index = int(sample_index)
        if 0 <= index < len(sample_timestamps):
            timestamp = sample_timestamps[index]
            if timestamp is not None:
                timestamps.append(timestamp)
    return estimate_series_sample_interval(timestamps)
