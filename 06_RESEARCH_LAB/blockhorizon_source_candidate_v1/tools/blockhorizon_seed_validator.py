#!/usr/bin/env python3
"""Provider-value-free validator for BlockHorizon manual CSV export bundles.

It records hashes, shape, timestamp range, duplicate state, cadence and blank-cell
metadata. It never emits source metric values. If an OHLC file and per-metric
`Price [USD]` columns are present, it verifies equality and emits only counts.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib
import statistics
from collections import defaultdict


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iso_date(ms: int | None):
    if ms is None:
        return None
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date().isoformat()


def inspect_csv(path: pathlib.Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0] if rows else []
    tsidx = header.index("timestamp") if "timestamp" in header else None
    ts = []
    blanks = 0
    cells = 0
    for row in rows[1:]:
        if tsidx is not None and tsidx < len(row) and row[tsidx].strip():
            try:
                ts.append(int(float(row[tsidx])))
            except ValueError:
                pass
        for i, value in enumerate(row):
            if i == tsidx:
                continue
            cells += 1
            if not value.strip() or value.strip().lower() == "null":
                blanks += 1
    diffs = [b - a for a, b in zip(ts, ts[1:]) if b > a]
    med = (statistics.median(diffs) / 86400000) if diffs else None
    cadence = (
        "DAILY"
        if med and abs(med - 1) < 0.01
        else ("WEEKLY" if med and abs(med - 7) < 0.01 else "IRREGULAR_OR_UNKNOWN")
    )
    return {
        "original_filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "row_count": max(0, len(rows) - 1),
        "column_count": len(header),
        "columns": header,
        "timestamp_start": iso_date(min(ts) if ts else None),
        "timestamp_end": iso_date(max(ts) if ts else None),
        "median_cadence": cadence,
        "duplicate_timestamp_count": len(ts) - len(set(ts)),
        "strictly_increasing_timestamps": all(a < b for a, b in zip(ts, ts[1:])),
        "blank_cell_count_ex_timestamp": blanks,
        "non_timestamp_cell_count": cells,
        "blank_cell_pct_ex_timestamp": round(blanks / cells * 100, 6) if cells else None,
        "has_reference_price_column": "Price [USD]" in header,
    }


def price_crosscheck(paths, unique_records, tolerance=0.011):
    ohlc = next((p for p in paths if p.name.startswith("price_ohlc_")), None)
    if not ohlc:
        return {"status": "NOT_AVAILABLE", "mismatch_count": None, "overlapping_row_comparisons": 0}
    with ohlc.open("r", encoding="utf-8-sig", newline="") as f:
        px = {
            int(row["timestamp"]): float(row["Close"])
            for row in csv.DictReader(f)
            if row.get("timestamp") and row.get("Close")
        }
    comparisons = 0
    mismatches = 0
    files_checked = 0
    byname = {p.name: p for p in paths}
    for rec in unique_records:
        if rec["original_filename"] == ohlc.name or not rec["has_reference_price_column"]:
            continue
        path = byname[rec["original_filename"]]
        files_checked += 1
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                ts = row.get("timestamp")
                value = row.get("Price [USD]")
                if not ts or not value:
                    continue
                try:
                    ts = int(float(ts))
                    value = float(value)
                except ValueError:
                    continue
                if ts in px:
                    comparisons += 1
                    if abs(value - px[ts]) > tolerance:
                        mismatches += 1
    return {
        "status": "PASS" if mismatches == 0 else "FAIL",
        "files_checked": files_checked,
        "overlapping_row_comparisons": comparisons,
        "mismatch_count": mismatches,
        "tolerance_usd": tolerance,
    }


def representative_key(rec):
    """Prefer stable export names over browser/UI copy suffixes like `(1)`."""
    name = rec["original_filename"]
    return ("(" in name, len(name), name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    paths = sorted(pathlib.Path(args.input_dir).glob("*.csv"))
    records = [inspect_csv(path) for path in paths]

    duplicate_groups = defaultdict(list)
    records_by_hash = defaultdict(list)
    for rec in records:
        duplicate_groups[rec["sha256"]].append(rec["original_filename"])
        records_by_hash[rec["sha256"]].append(rec)

    unique = []
    for group in records_by_hash.values():
        representative = min(group, key=representative_key)
        representative["content_duplicate_of"] = None
        unique.append(representative)
    unique.sort(key=lambda rec: rec["original_filename"])

    out = {
        "schema": "BLOCKHORIZON_PROVIDER_VALUE_FREE_INVENTORY_v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "raw_values_in_manifest": False,
        "input_csv_count": len(records),
        "unique_content_count": len(unique),
        "exact_content_duplicate_groups": [
            group for group in duplicate_groups.values() if len(group) > 1
        ],
        "validation_summary": {
            "all_timestamp_series_strictly_increasing": all(
                rec["strictly_increasing_timestamps"] for rec in unique if rec["timestamp_start"]
            ),
            "total_duplicate_timestamps": sum(rec["duplicate_timestamp_count"] for rec in unique),
            "reference_price_crosscheck": price_crosscheck(paths, unique),
            "blank_cells_interpretation": "UNASSESSED_FAMILY_AWARE_DO_NOT_IMPUTE",
        },
        "datasets": unique,
    }
    pathlib.Path(args.output).write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
