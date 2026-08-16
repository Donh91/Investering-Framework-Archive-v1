#!/usr/bin/env python3
"""Validate every committed lifecycle receipt under the evidence store.

The store audit is intentionally semantic-free. It checks receipt integrity and
false-precision guards only. Missing lifecycle stages are allowed and preserved.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("03_DAILY_CAPTURE_LOGS/evidence_lifecycle"))
    args = ap.parse_args()
    validator = Path(__file__).with_name("validate_lifecycle_receipt.py")

    if not args.root.exists():
        print(json.dumps({"status": "PASS", "receipt_count": 0, "reason": "STORE_NOT_YET_PRESENT"}, sort_keys=True))
        return 0

    receipts = sorted(p for p in args.root.rglob("*.json") if p.is_file())
    failures = []
    lane_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}

    for path in receipts:
        try:
            body = json.loads(path.read_text())
        except Exception as exc:
            failures.append({"path": str(path), "error": f"invalid_json:{exc}"})
            continue
        if body.get("contract") != "EVIDENCE_LIFECYCLE_RECEIPT_v0_1":
            failures.append({"path": str(path), "error": "wrong_contract"})
            continue
        proc = subprocess.run([sys.executable, str(validator), str(path)], capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append({"path": str(path), "error": "validator_failed", "stdout": proc.stdout[-2000:]})
            continue
        lane = str(body.get("evidence_lane") or "UNKNOWN")
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
        for status in (body.get("timestamp_status") or {}).values():
            status_counts[str(status)] = status_counts.get(str(status), 0) + 1

    result = {
        "status": "PASS" if not failures else "FAIL",
        "receipt_count": len(receipts),
        "lane_counts": lane_counts,
        "timestamp_status_counts": status_counts,
        "failure_count": len(failures),
        "failures": failures[:50],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
