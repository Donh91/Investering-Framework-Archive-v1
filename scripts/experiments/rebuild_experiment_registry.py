#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from experiment_lifecycle import canon, registry


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-root", type=Path, required=True)
    ap.add_argument("--observation-root", type=Path, required=True)
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--outcome-root", type=Path, required=True)
    ap.add_argument("--receipt-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    value = registry(
        args.candidate_root,
        args.observation_root,
        args.forecast_root,
        args.outcome_root,
        args.receipt_root,
        now,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(value))
    print(canon({"status": "PASS", "candidate_count": value["candidate_count"], "state_counts": value["state_counts"]}).decode().strip())


if __name__ == "__main__":
    main()
