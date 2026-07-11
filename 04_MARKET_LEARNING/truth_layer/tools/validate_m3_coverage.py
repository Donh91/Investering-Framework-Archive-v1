#!/usr/bin/env python3
"""Validate frozen M3 baseline plus prospective forward rows. No outcome scoring."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ALLOWED = {
    "SOURCE_BACKED",
    "PUBLIC_SOURCE_BACKED",
    "OFFLINE_GITHUB_SNAPSHOT_BACKED",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def field(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name)
        if value is not None:
            return str(value).strip()
    return ""


def eligible(row: dict[str, str]) -> bool:
    return field(row, "eligible_for_M3").upper() == "YES"


def exact_iso(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return "T" in value and parsed.tzinfo is not None
    except Exception:
        return False


def validate_row(
    row: dict[str, str],
    row_number: int,
    ledger_kind: str,
    errors: list[dict[str, str]],
) -> None:
    decision_id = field(row, "decision_id")
    if not decision_id:
        errors.append(
            {
                "ledger": ledger_kind,
                "row": str(row_number),
                "decision_id": "",
                "error": "missing decision_id",
            }
        )
    if not eligible(row):
        return

    issued = field(row, "issued_timestamp_utc", "issued_timestamp")
    event_window = field(row, "event_window_id")
    excerpt = field(row, "exact_source_excerpt")
    source_path = field(row, "source_path_or_url", "source_file_or_thread")
    horizon = field(row, "effective_horizon")
    source_status = field(row, "source_status")
    retro = field(row, "retrospective_or_live").upper()

    required = {
        "issued_timestamp": issued,
        "event_window_id": event_window,
        "effective_horizon": horizon,
        "source_path": source_path,
        "exact_source_excerpt": excerpt,
    }
    for name, value in required.items():
        if not value:
            errors.append(
                {
                    "ledger": ledger_kind,
                    "row": str(row_number),
                    "decision_id": decision_id,
                    "error": f"eligible row missing {name}",
                }
            )

    if not exact_iso(issued):
        errors.append(
            {
                "ledger": ledger_kind,
                "row": str(row_number),
                "decision_id": decision_id,
                "error": "eligible row lacks exact timezone-aware timestamp",
            }
        )
    if source_status not in ALLOWED:
        errors.append(
            {
                "ledger": ledger_kind,
                "row": str(row_number),
                "decision_id": decision_id,
                "error": f"ineligible source_status: {source_status}",
            }
        )
    if "RETROSPECT" in retro or "RECONSTRUCT" in retro:
        errors.append(
            {
                "ledger": ledger_kind,
                "row": str(row_number),
                "decision_id": decision_id,
                "error": "retrospective/reconstructed row marked eligible",
            }
        )

    if ledger_kind == "forward":
        supplied_hash = field(row, "source_content_sha256")
        expected_hash = hashlib.sha256(excerpt.encode("utf-8")).hexdigest() if excerpt else ""
        if not supplied_hash:
            errors.append(
                {
                    "ledger": ledger_kind,
                    "row": str(row_number),
                    "decision_id": decision_id,
                    "error": "new eligible row missing source_content_sha256",
                }
            )
        elif expected_hash and supplied_hash != expected_hash:
            errors.append(
                {
                    "ledger": ledger_kind,
                    "row": str(row_number),
                    "decision_id": decision_id,
                    "error": "source excerpt hash mismatch",
                }
            )

        source_type = field(row, "source_type").upper()
        receipt = field(row, "source_commit_receipt", "github_commit_receipt")
        if ("MASTER_MONDAY" in source_type or "FORECAST" in source_type) and not receipt:
            errors.append(
                {
                    "ledger": ledger_kind,
                    "row": str(row_number),
                    "decision_id": decision_id,
                    "error": "new Master Monday/forecast row missing commit receipt",
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--forward", required=True)
    parser.add_argument("--baseline-window-map")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    forward_path = Path(args.forward)
    baseline_rows = read_rows(baseline_path)
    forward_rows = read_rows(forward_path)

    if args.baseline_window_map:
        mapping = {
            field(row, "decision_id"): field(row, "event_window_id")
            for row in read_rows(Path(args.baseline_window_map))
            if field(row, "decision_id") and field(row, "event_window_id")
        }
        for row in baseline_rows:
            if not field(row, "event_window_id") and field(row, "decision_id") in mapping:
                row["event_window_id"] = mapping[field(row, "decision_id")]

    errors: list[dict[str, str]] = []
    ids: dict[str, tuple[str, int]] = {}
    for kind, rows in (("baseline", baseline_rows), ("forward", forward_rows)):
        for row_number, row in enumerate(rows, start=2):
            validate_row(row, row_number, kind, errors)
            decision_id = field(row, "decision_id")
            if not decision_id:
                continue
            if decision_id in ids:
                prior_kind, prior_row = ids[decision_id]
                errors.append(
                    {
                        "ledger": kind,
                        "row": str(row_number),
                        "decision_id": decision_id,
                        "error": f"duplicate decision_id across {prior_kind} row {prior_row}",
                    }
                )
            else:
                ids[decision_id] = (kind, row_number)

    eligible_rows = [row for row in baseline_rows + forward_rows if eligible(row)]
    windows = Counter(
        field(row, "event_window_id")
        for row in eligible_rows
        if field(row, "event_window_id")
    )
    families = Counter(
        field(row, "source_type")
        for row in eligible_rows
        if field(row, "source_type")
    )
    largest = max(windows.values(), default=0)
    concentration = largest / len(eligible_rows) * 100 if eligible_rows else 0.0

    gates = {
        "eligible_rows_30": len(eligible_rows) >= 30,
        "event_windows_3": len(windows) >= 3,
        "source_families_3": len(families) >= 3,
        "max_concentration_50": concentration <= 50.0,
    }
    report = {
        "baseline_ledger": str(baseline_path),
        "forward_ledger": str(forward_path),
        "baseline_rows": len(baseline_rows),
        "forward_rows": len(forward_rows),
        "baseline_eligible_rows": sum(eligible(row) for row in baseline_rows),
        "forward_eligible_rows": sum(eligible(row) for row in forward_rows),
        "eligible_rows_total": len(eligible_rows),
        "independent_event_windows": len(windows),
        "source_families": len(families),
        "largest_window_concentration_pct": round(concentration, 4),
        "coverage_gate": gates,
        "ready_for_governance_review": all(gates.values()) and not errors,
        "errors": errors,
        "validation_pass": not errors,
        "scoring_performed": False,
    }
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
