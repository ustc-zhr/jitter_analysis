from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jitter_analysis.domain.types import RunMetadata, RunMode, RunResult, RunStatus
from jitter_analysis.gui.run_logic import run_browser_scope_kind, validate_loaded_run_config


def _config(object_ids=(), knob_ids=()):
    return SimpleNamespace(
        objects=[SimpleNamespace(id=item) for item in object_ids],
        knobs=[SimpleNamespace(id=item) for item in knob_ids],
    )


def _result(mode: RunMode, details: dict[str, object]) -> RunResult:
    return RunResult(
        metadata=RunMetadata(
            run_id="run",
            mode=mode,
            created_at=datetime(2026, 7, 1, 12, 0, 0),
        ),
        status=RunStatus.COMPLETED,
        details=details,
    )


def test_run_browser_scope_kind_detects_root_and_single_run_dirs(tmp_path):
    assert run_browser_scope_kind(tmp_path / "missing") == "root"
    assert run_browser_scope_kind(tmp_path) == "root"

    (tmp_path / "metadata.json").write_text("{}", encoding="utf-8")

    assert run_browser_scope_kind(tmp_path) == "single_run"


def test_validate_loaded_run_config_rejects_missing_config():
    result = _result(RunMode.TIMED_ACQUISITION, {})

    assert validate_loaded_run_config(result, None) == (False, "No PV library is loaded.")


def test_validate_loaded_run_config_accepts_matching_timed_run():
    result = _result(
        RunMode.TIMED_ACQUISITION,
        {"target_object_ids": [" bpm_x ", "scope_a", ""]},
    )

    assert validate_loaded_run_config(result, _config(object_ids=["bpm_x", "scope_a"])) == (True, "")


def test_validate_loaded_run_config_reports_missing_read_and_single_knob_ids():
    result = _result(
        RunMode.KNOB_SCAN,
        {"target_object_ids": ["bpm_x", "missing_read"], "knob_id": "missing_knob"},
    )

    ok, message = validate_loaded_run_config(result, _config(object_ids=["bpm_x"], knob_ids=["k1"]))

    assert ok is False
    assert "read PV IDs: missing_read" in message
    assert "control PV IDs: missing_knob" in message


def test_validate_loaded_run_config_reports_missing_multi_knob_ids():
    result = _result(
        RunMode.MULTI_KNOB_RANDOM,
        {
            "target_object_ids": ["bpm_x"],
            "knob_ranges": [
                {"knob_id": "k1"},
                {"knob_id": "missing_knob"},
                {"knob_id": ""},
                "bad",
            ],
        },
    )

    ok, message = validate_loaded_run_config(result, _config(object_ids=["bpm_x"], knob_ids=["k1"]))

    assert ok is False
    assert "control PV IDs: missing_knob" in message
