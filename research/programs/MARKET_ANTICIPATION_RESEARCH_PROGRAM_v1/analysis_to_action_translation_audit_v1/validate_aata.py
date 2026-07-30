#!/usr/bin/env python3
"""Validate the Analysis-to-Action Translation Audit control package."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    checks = 0
    owner = load("OWNER_BINDING_AND_PROPOSITION_v1.json")
    schema = load("TRANSLATION_ROW_SCHEMA_v1.json")
    rows = load("SOURCE_ROWS_W28_W31_v1.json")
    capture = load("PROSPECTIVE_CAPTURE_CONTRACT_v1.json")

    checks += 1
    if owner["new_active_test"] or owner["new_engine"] or owner["new_score"]:
        fail("AATA must not create an active test, engine or score")

    checks += 1
    if owner["economic_execution_allowed"] or owner["final_holdout_opened"]:
        fail("Economic execution and final holdout must remain locked")

    checks += 1
    row_ids = [row["row_id"] for row in rows["rows"]]
    if len(row_ids) != len(set(row_ids)) or len(row_ids) != 4:
        fail("Expected four unique W28-W31 source rows")

    checks += 1
    weeks = [row["week"] for row in rows["rows"]]
    if weeks != ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]:
        fail("Week order or coverage changed")

    checks += 1
    for row in rows["rows"]:
        required = set(schema["required"])
        if not required.issubset(row):
            fail(f"Missing schema fields in {row['row_id']}")
        if row["temporal_status"].startswith("BLOCKED") and row["outcome"]["status"] != "HISTORICAL_CONTEXT_ONLY":
            fail(f"Blocked row counted beyond context: {row['row_id']}")
        if any(row["authority"].values()):
            fail(f"Forbidden authority in {row['row_id']}")
        for key in ("master_monday_path", "forecast_ledger_path"):
            path = row["source"].get(key)
            if path and not (REPO / path).exists():
                fail(f"Referenced owner path missing: {path}")

    checks += 1
    w30 = next(row for row in rows["rows"] if row["week"] == "2026-W30")
    if w30["outcome"]["status"] != "OWNER_AUDIT_IMPORTED_ECONOMIC_RESCORING_LOCKED":
        fail("W30 owner audit boundary changed")
    if w30["outcome"]["existing_owner_audit"]["leadership"] != "MISS":
        fail("W30 leadership miss must remain separate from range precision")

    checks += 1
    w31 = next(row for row in rows["rows"] if row["week"] == "2026-W31")
    if w31["outcome"]["status"] != "PENDING_HORIZON_MATURITY_AND_OWNER_JOIN":
        fail("W31 must remain pending")

    checks += 1
    required_blocks = set(capture["required_separation"])
    if required_blocks != {"analysis_block", "operational_translation_block"}:
        fail("Analysis and operational translation blocks must remain separate")

    checks += 1
    if any(capture["authority"].values()):
        fail("Capture contract has forbidden authority")

    checks += 1
    if rows["summary"]["new_economic_scores"] != 0:
        fail("No new economic scores allowed")

    result = {
        "status": "PASS",
        "checks": checks,
        "rows": len(rows["rows"]),
        "new_economic_scores": 0,
        "final_holdout_opened": False
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        raise
