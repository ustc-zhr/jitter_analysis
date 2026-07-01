from __future__ import annotations

from pathlib import Path

from ..domain.types import RunMode, RunResult


def run_browser_scope_kind(root_dir: str | Path) -> str:
    root_path = Path(root_dir)
    if not root_path.exists():
        return "root"
    if any((root_path / filename).exists() for filename in ("raw.h5", "metadata.json", "result.json")):
        return "single_run"
    return "root"


def validate_loaded_run_config(result: RunResult, loaded_config) -> tuple[bool, str]:
    if loaded_config is None:
        return False, "No PV library is loaded."

    expected_object_ids = [
        str(item).strip()
        for item in result.details.get("target_object_ids", [])
        if str(item).strip()
    ]
    available_object_ids = {obj.id for obj in loaded_config.objects}
    missing_object_ids = [object_id for object_id in expected_object_ids if object_id not in available_object_ids]

    expected_knob_ids: list[str] = []
    if result.metadata.mode == RunMode.KNOB_SCAN:
        knob_id = str(result.details.get("knob_id", "")).strip()
        if knob_id:
            expected_knob_ids = [knob_id]
    elif result.metadata.mode == RunMode.MULTI_KNOB_RANDOM:
        knob_ranges = result.details.get("knob_ranges", [])
        expected_knob_ids = [
            str(item.get("knob_id", "")).strip()
            for item in knob_ranges
            if isinstance(item, dict) and str(item.get("knob_id", "")).strip()
        ]

    available_knob_ids = {knob.id for knob in loaded_config.knobs}
    missing_knob_ids = [knob_id for knob_id in expected_knob_ids if knob_id not in available_knob_ids]

    if not missing_object_ids and not missing_knob_ids:
        return True, ""

    missing_parts = []
    if missing_object_ids:
        missing_parts.append("read PV IDs: " + ", ".join(missing_object_ids[:8]))
    if missing_knob_ids:
        missing_parts.append("control PV IDs: " + ", ".join(missing_knob_ids[:8]))
    return (
        False,
        "The loaded PV library does not match this saved run.\nMissing "
        + " | ".join(missing_parts),
    )
