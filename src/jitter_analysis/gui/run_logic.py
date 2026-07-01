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


def resolve_loaded_run_selection(
    details: dict[str, object],
    mode: RunMode | None,
    available_object_ids,
    record_pv_ids=(),
    series_pv_ids=(),
) -> dict[str, object]:
    selected_object_ids = list(details.get("target_object_ids", []))
    if not selected_object_ids:
        known_object_ids = set(available_object_ids)
        seen = []
        for pv_id in record_pv_ids:
            if pv_id in known_object_ids and pv_id not in seen:
                seen.append(pv_id)
        if not seen:
            for pv_id in series_pv_ids:
                if pv_id in known_object_ids and pv_id not in seen:
                    seen.append(pv_id)
        selected_object_ids = seen

    selected_knob_ids: list[str] = []
    active_knob_id = None
    if mode == RunMode.KNOB_SCAN:
        knob_id = str(details.get("knob_id", "")).strip()
        if knob_id:
            selected_knob_ids = [knob_id]
            active_knob_id = knob_id
    elif mode == RunMode.MULTI_KNOB_RANDOM:
        knob_ranges = details.get("knob_ranges", [])
        selected_knob_ids = [
            str(item.get("knob_id"))
            for item in knob_ranges
            if isinstance(item, dict) and str(item.get("knob_id", "")).strip()
        ]
        active_knob_id = selected_knob_ids[0] if selected_knob_ids else None

    return {
        "selected_object_ids": selected_object_ids,
        "selected_knob_ids": selected_knob_ids,
        "active_knob_id": active_knob_id,
    }


def loaded_run_object_count_hint(
    details: dict[str, object],
    selected_object_ids=(),
    record_pv_ids=(),
) -> int:
    target_object_ids = [
        str(item).strip()
        for item in details.get("target_object_ids", [])
        if str(item).strip()
    ]
    if target_object_ids:
        return len(target_object_ids)
    selected = list(selected_object_ids)
    if selected:
        return len(selected)
    seen_ids = []
    for pv_id in record_pv_ids:
        if pv_id not in seen_ids:
            seen_ids.append(pv_id)
    return len(seen_ids)
