#!/usr/bin/env python3
"""Regression tests for direct-ETHBTC persistence lifecycle lineage."""
from __future__ import annotations

import csv
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts/evidence_lifecycle/write_ethbtc_persistence_receipt.py"
VALIDATOR = ROOT / "scripts/evidence_lifecycle/validate_lifecycle_receipt.py"


def write_hourly(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "test.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "ethbtc_close"])
        writer.writeheader()
        writer.writerow({"timestamp_utc": "2026-08-16T09:00:00Z", "ethbtc_close": "0.0298"})
        writer.writerow({"timestamp_utc": "2026-08-16T10:00:00Z", "ethbtc_close": "0.0301"})


def run_adapter(context: dict, hourly: Path, output: Path) -> dict:
    context_path = output.parent / "context.json"
    context_path.write_text(json.dumps(context))
    subprocess.run([
        "python", str(ADAPTER),
        "--context", str(context_path),
        "--hourly-root", str(hourly),
        "--output", str(output),
        "--source-run-id", "test-ethbtc",
        "--repo-head-sha", "test-sha",
    ], check=True, capture_output=True, text=True)
    assert subprocess.run(["python", str(VALIDATOR), str(output)], capture_output=True).returncode == 0
    return json.loads(output.read_text())


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        hourly = root / "hourly"
        write_hourly(hourly)

        ready = {
            "api_intelligence_v2": {
                "cutoff_utc": "2026-08-16T10:30:00Z",
                "ethbtc_0_0300_persistence": {"status": "READY"},
            }
        }
        receipt = run_adapter(ready, hourly, root / "ready.json")
        assert receipt["derivation_status"] == "READY"
        assert receipt["observation_time"] == "2026-08-16T10:00:00Z"
        assert receipt["timestamp_status"]["observation_time"] == "KNOWN"
        assert receipt["normalization_time"] is not None
        assert receipt["retrieval_start_time"] is None
        assert receipt["source_available_time"] is None
        assert receipt["framework_acceptance_time"] is None
        assert receipt["policy_evaluable_time"] is None
        assert receipt["synthetic_ratio_used"] is False
        assert "DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS" in receipt["source_lineage"]

        unavailable = {
            "api_intelligence_v2": {
                "cutoff_utc": "2026-08-16T10:30:00Z",
                "ethbtc_0_0300_persistence": {"status": "UNAVAILABLE", "reason": "TEST_GAP"},
            }
        }
        receipt = run_adapter(unavailable, hourly, root / "unavailable.json")
        assert receipt["derivation_status"] == "UNAVAILABLE"
        assert receipt["derivation_reason"] == "TEST_GAP"
        assert receipt["framework_acceptance_time"] is None
        assert receipt["policy_evaluable_time"] is None

        no_rows_root = root / "empty-hourly"
        no_rows_root.mkdir()
        receipt = run_adapter(ready, no_rows_root, root / "no_rows.json")
        assert receipt["derivation_status"] == "UNAVAILABLE"
        assert receipt["derivation_reason"] == "DIRECT_ETHBTC_HOURLY_ROW_UNAVAILABLE"
        assert receipt["observation_time"] is None

    print("ETHBTC persistence lifecycle tests: PASS")


if __name__ == "__main__":
    main()
