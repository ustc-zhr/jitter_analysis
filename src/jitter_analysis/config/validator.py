from __future__ import annotations

from typing import Any


REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "machine",
    "defaults",
    "groups",
    "knobs",
    "objects",
    "presets",
}

SUPPORTED_OBJECT_VALUE_REDUCERS = {
    "none",
    "mean",
}

SUPPORTED_OBJECT_CAPTURE_MODES = {
    "scalar",
    "waveform",
}


def validate_config_dict(data: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_TOP_LEVEL_KEYS.difference(data)
    if missing:
        missing_keys = ", ".join(sorted(missing))
        raise ValueError(f"Missing required config keys: {missing_keys}")

    group_ids = {item["id"] for item in data["groups"]}
    for knob in data["knobs"]:
        if knob["group"] not in group_ids:
            raise ValueError(f"Unknown group for knob {knob['id']}: {knob['group']}")
    for obj in data["objects"]:
        if obj["group"] not in group_ids:
            raise ValueError(f"Unknown group for object {obj['id']}: {obj['group']}")
        reducer = str(obj.get("value_reducer", "none")).strip().lower()
        if reducer not in SUPPORTED_OBJECT_VALUE_REDUCERS:
            raise ValueError(
                f"Unsupported value_reducer for object {obj['id']}: {obj.get('value_reducer')}"
            )
        capture_mode = str(obj.get("capture_mode", "scalar")).strip().lower()
        if capture_mode not in SUPPORTED_OBJECT_CAPTURE_MODES:
            raise ValueError(
                f"Unsupported capture_mode for object {obj['id']}: {obj.get('capture_mode')}"
            )
        if capture_mode == "waveform":
            if reducer != "none":
                raise ValueError(
                    f"Waveform object {obj['id']} must use value_reducer 'none', got {obj.get('value_reducer')!r}"
                )
            raw_sample_interval = obj.get("waveform_sample_interval_sec")
            if raw_sample_interval is None:
                raise ValueError(f"Waveform object {obj['id']} requires waveform_sample_interval_sec.")
            try:
                sample_interval = float(raw_sample_interval)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Waveform object {obj['id']} waveform_sample_interval_sec must be numeric."
                ) from exc
            if sample_interval <= 0.0:
                raise ValueError(
                    f"Waveform object {obj['id']} waveform_sample_interval_sec must be positive."
                )

    knob_ids = {item["id"] for item in data["knobs"]}
    object_ids = {item["id"] for item in data["objects"]}
    for preset in data["presets"]:
        target_ids = set(preset.get("targets", []))
        unknown_targets = target_ids.difference(object_ids)
        if unknown_targets:
            raise ValueError(
                f"Unknown preset targets for {preset['id']}: {', '.join(sorted(unknown_targets))}"
            )
        knob_id = preset.get("knob_id")
        if knob_id and knob_id not in knob_ids:
            raise ValueError(f"Unknown preset knob for {preset['id']}: {knob_id}")

    return data
