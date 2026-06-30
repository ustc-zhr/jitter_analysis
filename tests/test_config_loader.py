from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from jitter_analysis.config.loader import load_config
from jitter_analysis.config.models import ObjectSpec


def test_load_example_config():
    config = load_config(ROOT / "configs" / "irfel_pvlist_v2.example.json")
    assert config.schema_version == "2.0"
    assert len(config.knobs) >= 1
    assert len(config.objects) >= 1


def test_load_object_value_reducer_from_config(tmp_path):
    config_path = tmp_path / "pvlist.json"
    config_path.write_text(
        """
{
  "schema_version": "2.0",
  "machine": {
    "name": "Test",
    "facility": "Lab",
    "description": "Reducer test"
  },
  "defaults": {
    "acquisition": {
      "shot_interval_sec": 0.2,
      "sample_count": 10,
      "timeout_sec": 1.0,
      "mode": "poll"
    },
    "scan": {
      "settle_mode": "fixed_delay",
      "settle_delay_sec": 0.5,
      "sample_count_per_step": 3,
      "restore_initial_value": true,
      "max_wait_sec": 3.0
    },
    "storage": {
      "format": "hdf5",
      "save_raw_data": true,
      "save_analysis_summary": true
    },
    "safety": {
      "confirm_before_write": true,
      "abort_on_disconnection": true
    }
  },
  "groups": [
    {
      "id": "diag",
      "label": "Diag",
      "kind": "object",
      "color": "#123456",
      "order": 1
    }
  ],
  "knobs": [],
  "objects": [
    {
      "id": "wave_mean",
      "name": "Wave Mean",
      "group": "diag",
      "read_pv": "PV:WAVE",
      "unit": "arb",
      "precision": 3,
      "kind": "waveform",
      "access": "ro",
      "value_reducer": "mean",
      "analysis": {
        "jitter": true,
        "correlation": true,
        "spectrum": true
      }
    }
  ],
  "presets": []
}
        """.strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert len(config.objects) == 1
    obj = config.objects[0]
    assert isinstance(obj, ObjectSpec)
    assert obj.value_reducer == "mean"


def test_load_waveform_capture_fields_from_config(tmp_path):
    config_path = tmp_path / "pvlist_waveform.json"
    config_path.write_text(
        """
{
  "schema_version": "2.0",
  "machine": {
    "name": "Test",
    "facility": "Lab",
    "description": "Waveform capture"
  },
  "defaults": {
    "acquisition": {
      "shot_interval_sec": 0.2,
      "sample_count": 10,
      "timeout_sec": 1.0,
      "mode": "poll"
    },
    "scan": {
      "settle_mode": "fixed_delay",
      "settle_delay_sec": 0.5,
      "sample_count_per_step": 3,
      "restore_initial_value": true,
      "max_wait_sec": 3.0
    },
    "storage": {
      "format": "hdf5",
      "save_raw_data": true,
      "save_analysis_summary": true
    },
    "safety": {
      "confirm_before_write": true,
      "abort_on_disconnection": true
    }
  },
  "groups": [
    {
      "id": "diag",
      "label": "Diag",
      "kind": "object",
      "color": "#123456",
      "order": 1
    }
  ],
  "knobs": [],
  "objects": [
    {
      "id": "wave_raw",
      "name": "Wave Raw",
      "group": "diag",
      "read_pv": "PV:WAVE",
      "unit": "arb",
      "precision": 3,
      "kind": "waveform",
      "access": "ro",
      "capture_mode": "waveform",
      "waveform_sample_interval_sec": 2.5e-9,
      "value_reducer": "none",
      "analysis": {
        "jitter": true,
        "correlation": true,
        "spectrum": true
      }
    }
  ],
  "presets": []
}
        """.strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert len(config.objects) == 1
    obj = config.objects[0]
    assert obj.capture_mode == "waveform"
    assert obj.waveform_sample_interval_sec == 2.5e-9


def test_load_config_snapshot_accepts_legacy_interval_field_names_when_enabled(tmp_path):
    config_path = tmp_path / "legacy_snapshot.json"
    config_path.write_text(
        """
{
  "schema_version": "2.0",
  "machine": {
    "name": "Test",
    "facility": "Lab",
    "description": "Legacy snapshot"
  },
  "defaults": {
    "acquisition": {
      "sample_interval_sec": 0.2,
      "sample_count": 10,
      "timeout_sec": 1.0,
      "mode": "poll"
    },
    "scan": {
      "settle_mode": "fixed_delay",
      "settle_delay_sec": 0.5,
      "sample_count_per_step": 3,
      "restore_initial_value": true,
      "max_wait_sec": 3.0
    },
    "storage": {
      "format": "hdf5",
      "save_raw_data": true,
      "save_analysis_summary": true
    },
    "safety": {
      "confirm_before_write": true,
      "abort_on_disconnection": true
    }
  },
  "groups": [
    {
      "id": "diag",
      "label": "Diag",
      "kind": "object",
      "color": "#123456",
      "order": 1
    }
  ],
  "knobs": [],
  "objects": [
    {
      "id": "wave_raw",
      "name": "Wave Raw",
      "group": "diag",
      "read_pv": "PV:WAVE",
      "unit": "arb",
      "precision": 3,
      "kind": "waveform",
      "access": "ro",
      "capture_mode": "waveform",
      "sample_interval_sec": 2.5e-9,
      "value_reducer": "none",
      "analysis": {
        "jitter": true,
        "correlation": true,
        "spectrum": true
      }
    }
  ],
  "presets": [
    {
      "id": "legacy_monitor",
      "name": "Legacy Monitor",
      "mode": "timed_acquisition",
      "targets": ["wave_raw"],
      "sample_interval_sec": 0.1,
      "sample_count": 5
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    config = load_config(config_path, allow_legacy_field_names=True)

    assert config.defaults.acquisition.shot_interval_sec == 0.2
    assert config.objects[0].waveform_sample_interval_sec == 2.5e-9
    assert config.presets[0].shot_interval_sec == 0.1
