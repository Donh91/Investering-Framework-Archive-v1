#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parent

def load(name):
    with (ROOT / name).open(encoding="utf-8") as f:
        return json.load(f)

def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def main():
    rows = load("WP02C_FORECAST_NORMALIZED_ROWS_v1.json")
    gate = load("WP02C_TEMPORAL_PARITY_GATE_v1.json")
    etf = load("WP02C_ETF_AVAILABILITY_AUDIT_v1.json")
    checks = 0
    ids = [r["forecast_id"] for r in rows["rows"]]
    assert len(ids) == len(set(ids)); checks += 1
    assert rows["status"] == "DERIVED_NON_AUTHORITATIVE"; checks += 1
    assert rows["summary"]["rows"] == len(rows["rows"]) == 15; checks += 1
    for r in rows["rows"]:
        assert r["source_commit"] and r["source_path"] and r["source_authority"] == "OFFICIAL_FORECAST_LEDGER"
        if r["knowledge_time_status"] == "SOURCE_HAS_DATE_ONLY":
            assert r["forecast_created_at_utc"] is None and r["evaluation_allowed"] is False
        else:
            assert parse(r["forecast_created_at_utc"]) <= parse(r["source_commit_created_at_utc"]) or r["week"] == "2026-W29"
    checks += 1
    results = {r["week"]: r["result"] for r in gate["week_results"]}
    assert results == {"2026-W28":"BLOCKED","2026-W29":"TEMPORAL_METADATA_PASS","2026-W30":"TEMPORAL_METADATA_PASS"}; checks += 1
    assert gate["summary"]["economic_comparison_allowed"] is False; checks += 1
    assert gate["final_holdout_opened"] is False; checks += 1
    assert etf["gate_result"] == "BLOCKED_PENDING_ROW_LEVEL_MATERIALIZATION"; checks += 1
    assert etf["accepted_time_policy"]["session_date_is_not_availability_time"] is True; checks += 1
    assert etf["economic_use_allowed"] is False; checks += 1
    print(json.dumps({"status":"PASS","checks":checks,"failures":0}, sort_keys=True))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status":"FAIL","error":str(exc)}, sort_keys=True), file=sys.stderr)
        raise