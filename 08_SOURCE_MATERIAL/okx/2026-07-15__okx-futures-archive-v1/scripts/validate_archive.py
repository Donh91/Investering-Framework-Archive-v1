#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

HOUR_MS = 3_600_000

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def validate_hourly(path: Path) -> dict:
    rows = read_csv(path)
    timestamps = [int(row["timestamp_ms"]) for row in rows]
    unique = sorted(set(timestamps))
    gaps = []
    for left, right in zip(unique, unique[1:]):
        if right - left != HOUR_MS:
            gaps.append({"left": left, "right": right, "delta_ms": right-left})
    return {
        "path": str(path),
        "records": len(rows),
        "duplicates": len(rows) - len(unique),
        "gaps": len(gaps),
        "oldest": unique[0] if unique else None,
        "newest": unique[-1] if unique else None,
        "pass": bool(rows) and len(rows) == len(unique) and not gaps,
    }

def verify_checksums(root: Path) -> dict:
    checksum_path = root / "checksums.sha256"
    failures = []
    checked = 0
    if not checksum_path.exists():
        return {"checked": 0, "failures": ["checksums.sha256 missing"], "pass": False}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        path = root / rel
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        checked += 1
        if actual != expected:
            failures.append({"path": rel, "expected": expected, "actual": actual})
    return {"checked": checked, "failures": failures, "pass": not failures}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    root = Path(args.archive)
    reports = []
    for path in sorted(root.glob("normalized/*/*_1h.csv")):
        reports.append(validate_hourly(path))
    result = {
        "hourly_files": reports,
        "checksums": verify_checksums(root),
        "pass": all(r["pass"] for r in reports) and verify_checksums(root)["pass"],
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
