from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from scripts.orchestration.build_data_consumer_index import build_index


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def test_index_exposes_consumed_unconsumed_and_missing(tmp_path: Path) -> None:
    a = tmp_path / "a.json"
    a.write_text("{}")
    manifest = tmp_path / "research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json"
    _write(manifest, {
        "contract": "FRAMEWORK_HANDOFF_MANIFEST_v2",
        "generated_at_utc": "2026-09-18T00:00:00Z",
        "evidence": {
            "A": {"path": "a.json", "sha256": hashlib.sha256(a.read_bytes()).hexdigest()},
            "B": {"path": "missing.json", "sha256": "0" * 64},
            "C": {"path": "a.json", "sha256": hashlib.sha256(a.read_bytes()).hexdigest()},
        },
        "consumers": {"READER": ["A", "B"]},
    })
    result = build_index(tmp_path, manifest)
    rows = {row["artifact"]: row for row in result["rows"]}
    assert rows["A"]["use_state"] == "CONSUMED"
    assert rows["A"]["freshness_use_state"] == "CURRENT_BINDING"
    assert rows["B"]["freshness_use_state"] == "STALE_OR_MISSING_POINTER"
    assert rows["C"]["use_state"] == "NO_REGISTERED_CONSUMER"
    assert result["authority"]["automatic_suppression"] is False


def test_cli_direct_script_execution_resolves_repo_package(tmp_path: Path) -> None:
    manifest = tmp_path / "research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json"
    _write(manifest, {
        "contract": "FRAMEWORK_HANDOFF_MANIFEST_v2",
        "generated_at_utc": "2026-09-23T00:00:00Z",
        "evidence": {},
        "consumers": {},
    })
    output = tmp_path / "out.json"
    script = Path("scripts/orchestration/build_data_consumer_index.py").resolve()
    result = subprocess.run([
        sys.executable, str(script), "--repo-root", str(tmp_path),
        "--manifest", str(manifest), "--output", str(output)
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text())["contract"] == "DATA_CONSUMER_INDEX_v1"
