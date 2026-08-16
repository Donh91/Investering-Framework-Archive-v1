#!/usr/bin/env python3
"""Emit lifecycle evidence for the existing direct-ETHBTC persistence derivation."""
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
    if cutoff is None:
        raise SystemExit("api_intelligence_cutoff_required")
    if persistence.get("status") != "READY":
        raise SystemExit("ethbtc_persistence_not_ready")

    rows = load_hourly_rows(args.hourly_root, cutoff)
    direct = [row for row in rows if isinstance(row.get("ethbtc_close"), float)]
    if not direct:
        raise SystemExit("direct_ethbtc_hourly_row_required")
    latest = direct[-1]
    observation_time = latest["timestamp"].isoformat().replace("+00:00", "Z")
    source_path = str(latest.get("source_path") or "")
    derivation_completed = now_utc()

    writer = ROOT / "scripts/evidence_lifecycle/write_lifecycle_receipt.py"
    cmd = [
        sys.executable, str(writer),
        "--output", str(args.output),
        "--source-run-id", args.source_run_id,
        "--evidence-lane", "ETHBTC_PERSISTENCE_DERIVED",
        "--repo-head-sha", args.repo_head_sha,
        "--source-lineage", f"DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS:{source_path}",
        "--timestamp", f"observation_time={observation_time}",
        "--timestamp", f"normalization_time={derivation_completed}",
    ]
    subprocess.run(cmd, check=True)
    validator = ROOT / "scripts/evidence_lifecycle/validate_lifecycle_receipt.py"
    subprocess.run([sys.executable, str(validator), str(args.output)], check=True)
    print(json.dumps({
        "status": "PASS",
        "observation_time": observation_time,
        "derivation_completed_at_utc": derivation_completed,
        "source_path": source_path,
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
