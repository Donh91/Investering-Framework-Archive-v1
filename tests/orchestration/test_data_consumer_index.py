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


def test_existing_changed_bytes_fail_closed_instead_of_current_binding(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text('{"value":1}')
    original_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json"
    _write(manifest, {
        "contract": "FRAMEWORK_HANDOFF_MANIFEST_v2",
        "generated_at_utc": "2026-11-14T11:00:00Z",
        "evidence": {"ORIGINAL": {"path": "source.json", "sha256": original_digest}},
        "consumers": {"READER": ["ORIGINAL"]},
    })
    good = build_index(tmp_path, manifest)
    assert good["rows"][0]["freshness_use_state"] == "CURRENT_BINDING"
    assert good["rows"][0]["binding_state"] == "MATCH"
    assert good["rows"][0]["use_state"] == "CONSUMED"
    assert good["source_manifest_sha256"] == hashlib.sha256(manifest.read_bytes()).hexdigest()

    # Producer writes a newer payload, but this manifest remains frozen.
    source.write_text('{"value":2}')
    stale = build_index(tmp_path, manifest)
    row = stale["rows"][0]
    assert row["producer_state"] == "PRESENT"
    assert row["use_state"] == "CONSUMED"  # legacy route labels are unchanged
    assert row["freshness_use_state"] == "STALE_OR_MISSING_POINTER"
    assert row["binding_state"] == "DIGEST_MISMATCH"
    assert row["sha256"] == original_digest
    assert row["observed_sha256"] != original_digest
    assert stale["summary"]["stale_or_missing_pointer"] == 1


def test_absent_or_invalid_digest_never_claims_current_binding(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text('{"value":1}')
    manifest = tmp_path / "research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json"
    for declared in (None, "", "0" * 64, "Z" * 64):
        _write(manifest, {
            "contract": "FRAMEWORK_HANDOFF_MANIFEST_v2",
            "generated_at_utc": "2026-11-14T11:00:00Z",
            "evidence": {"ORIGINAL": {"path": "source.json", "sha256": declared}},
            "consumers": {"READER": ["ORIGINAL"]},
        })
        result = build_index(tmp_path, manifest)
        row = result["rows"][0]
        assert row["producer_state"] == "PRESENT"
        assert row["freshness_use_state"] == "STALE_OR_MISSING_POINTER"
        assert row["binding_state"] in {"INVALID_DECLARED_DIGEST", "DIGEST_MISMATCH"}
