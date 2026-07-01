from dataclasses import dataclass
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jitter_analysis.gui.scan_logic import (
    generate_random_targets,
    generate_values_by_points,
    generate_values_by_step,
    parse_manual_scan_values,
)


@dataclass
class _Knob:
    id: str


def test_parse_manual_scan_values_accepts_commas_semicolons_and_newlines():
    assert parse_manual_scan_values("-0.1, 0; 0.1\n0.2") == [-0.1, 0.0, 0.1, 0.2]


def test_parse_manual_scan_values_rejects_empty_and_non_numeric_values():
    with pytest.raises(ValueError, match="Enter one or more"):
        parse_manual_scan_values(" , ; ")
    with pytest.raises(ValueError, match="must be numeric"):
        parse_manual_scan_values("0.1, bad")


def test_generate_values_by_step_includes_stop_for_ascending_and_descending_ranges():
    assert generate_values_by_step(0.0, 0.5, 0.2) == [0.0, 0.2, 0.4, 0.5]
    assert generate_values_by_step(0.5, 0.0, 0.2) == [0.5, 0.3, 0.09999999999999998, 0.0]


def test_generate_values_by_points_handles_single_and_multiple_points():
    assert generate_values_by_points(1.0, 2.0, 1) == [1.0]
    assert generate_values_by_points(1.0, 2.0, 3) == [1.0, 1.5, 2.0]


def test_generate_random_targets_is_seeded_and_clips_normal_values():
    knob_ranges = [
        {"knob": _Knob("k1"), "low": -1.0, "high": 1.0},
        {"knob": _Knob("k2"), "low": 2.0, "high": 2.0},
    ]

    first = generate_random_targets(knob_ranges, "normal_clipped", 3, 123)
    second = generate_random_targets(knob_ranges, "normal_clipped", 3, 123)

    assert first == second
    assert len(first) == 3
    assert all(-1.0 <= row["k1"] <= 1.0 for row in first)
    assert all(row["k2"] == 2.0 for row in first)


def test_generate_random_targets_rejects_invalid_inputs():
    knob_ranges = [{"knob": _Knob("k1"), "low": 0.0, "high": 1.0}]
    with pytest.raises(ValueError, match="Num points"):
        generate_random_targets(knob_ranges, "uniform", 0, 1)
    with pytest.raises(ValueError, match="Unsupported random distribution"):
        generate_random_targets(knob_ranges, "bad", 1, 1)
