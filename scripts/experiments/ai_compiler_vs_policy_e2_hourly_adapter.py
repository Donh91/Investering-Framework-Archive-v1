#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_compiler_vs_policy_e2 as base  # noqa: E402

CANONICAL_RAW_COLUMNS = {"timestamp_utc", "btc_close", "eth_close", "spot_status"}
base.RAW_COLUMNS = set(CANONICAL_RAW_COLUMNS)


def load_raw_close_rows(root: Path, cutoff: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Bind the frozen E2 harness to the canonical hourly CSV schema without consuming derived fields."""
    cutoff_dt = base.dt(cutoff)
    rows: dict[str, dict[str, Any]] = {}
    sources: list[dict[str, str]] = []
    for path in sorted(root.glob("20??/??/*.csv")):
        raw_bytes = path.read_bytes()
        used = False
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not CANONICAL_RAW_COLUMNS.issubset(set(reader.fieldnames)):
                continue
            for source in reader:
                ts = str(source.get("timestamp_utc") or "").strip()
                if not ts:
                    continue
                when = base.dt(ts)
                if when > cutoff_dt or str(source.get("spot_status") or "").upper() != "PASS":
                    continue
                try:
                    row = {
                        "timestamp": base.iso(when),
                        "btc_close": float(source["btc_close"]),
                        "eth_close": float(source["eth_close"]),
                        "spot_status": "PASS",
                    }
                except (TypeError, ValueError):
                    continue
                if row["btc_close"] <= 0 or row["eth_close"] <= 0:
                    continue
                existing = rows.get(row["timestamp"])
                if existing is not None and existing != row:
                    raise ValueError(f"conflicting_raw_close_duplicate:{row['timestamp']}")
                rows[row["timestamp"]] = row
                used = True
        if used:
            sources.append({"path": str(path), "sha256": base.sha_bytes(raw_bytes)})
    return sorted(rows.values(), key=lambda item: base.dt(item["timestamp"])), sources


base.load_raw_close_rows = load_raw_close_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    base.run_trial(request, args.repo_root, args.output_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
