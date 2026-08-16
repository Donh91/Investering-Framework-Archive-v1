#!/usr/bin/env python3
"""Emit lifecycle evidence for the existing direct-ETHBTC persistence derivation.

This adapter does not fetch market data. It observes the retained direct ETHBTC
hourly rows already consumed by the Director context and records only the
observation/derivation stages that are actually knowable here.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.api_agent.augment_director_context_v2 import load_hourly_rows, parse_ts


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", type=Path, required=True)
    ap.add_argument("--hourly-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-run-id", required=True)
    ap.add_argument("--repo-head-sha", required=True)
    args = ap.parse_args()

    context = json.loads(args.context.read_text())
    api = context.get("api_intelligence_v2") if isinstance(context.get("api_intelligence_v2"), dict) else {}
    persistence = api.get("ethbtc_0_0300_persistence") if isinstance(api.get("ethbtc_0_0300_persistence"), dict) else {}
    cutoff = parse_ts(api.get("cutoff_utc"))

    rows = load_hourly_rows(args.hourly_root, cutoff) if cutoff is not None else []
    direct = [row for row in rows if isinstance(row.get("ethbtc_close"), float)]
    latest = direct[-1] if direct else None
    observation_time = latest["timestamp"].isoformat().replace("+00:00", "Z") if latest else None
    source_path = str(latest.get("source_path") or "") if latest else ""
    derivation_completed = now_utc()

    writer = ROOT / "scripts/evidence_lifecycle/write_lifecycle_receipt.py"
    cmd = [
        sys.executable, str(writer),
        "--output", str(args.output),
        "--source-run-id", args.source_run_id,
        "--evidence-lane", "ETHBTC_PERSISTENCE_DERIVED",
        "--repo-head-sha", args.repo_head_sha,
        "--source-lineage", (
            f"DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS:{source_path}"
            if latest else "DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS:UNAVAILABLE"
        ),
    ]
    if observation_time:
        cmd += ["--timestamp", f"observation_time={observation_time}"]
        # A retained direct row was actually loaded and normalized in this run.
        cmd += ["--timestamp", f"normalization_time={derivation_completed}"]
    subprocess.run(cmd, check=True)

    body = json.loads(args.output.read_text())
    body["derivation_status"] = "READY" if persistence.get("status") == "READY" and latest else "UNAVAILABLE"
    body["derivation_reason"] = None
    if cutoff is None:
        body["derivation_reason"] = "API_INTELLIGENCE_CUTOFF_UNAVAILABLE"
    elif not latest:
        body["derivation_reason"] = "DIRECT_ETHBTC_HOURLY_ROW_UNAVAILABLE"
    elif persistence.get("status") != "READY":
        body["derivation_reason"] = str(persistence.get("reason") or "ETHBTC_PERSISTENCE_NOT_READY")
    body["derivation_checked_at_utc"] = derivation_completed
    body["derivation_contract"] = "API_INTELLIGENCE_SEQUENCE_CONTEXT_v2_2.ethbtc_0_0300_persistence"
    body["synthetic_ratio_used"] = False
    body["policy_evaluable_from_this_receipt"] = False
    args.output.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")

    validator = ROOT / "scripts/evidence_lifecycle/validate_lifecycle_receipt.py"
    subprocess.run([sys.executable, str(validator), str(args.output)], check=True)
    print(json.dumps({
        "status": "PASS",
        "derivation_status": body["derivation_status"],
        "observation_time": observation_time,
        "derivation_checked_at_utc": derivation_completed,
        "source_path": source_path,
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
