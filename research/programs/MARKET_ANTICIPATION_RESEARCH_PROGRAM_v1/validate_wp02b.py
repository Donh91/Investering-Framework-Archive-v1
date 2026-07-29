#!/usr/bin/env python3
"""Validate MAR-WP02B canonical owner discovery and materialized coverage controls."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def load(name: str):
    with (ROOT / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    checks = 0
    registry = load("WP02B_CANONICAL_OWNER_REGISTRY_v1.json")
    coverage = load("WP02B_MATERIALIZED_COVERAGE_REPORT_v1.json")
    join = load("FORECAST_BASELINE_JOIN_CONTRACT_v1.json")

    owner_ids = [row["owner_id"] for row in registry["owners"]]
    checks += 1
    if len(owner_ids) != len(set(owner_ids)):
        fail("owner IDs must be unique")

    checks += 1
    authority = registry["authority"]
    if any(authority.values()):
        fail("WP02B must retain zero execution, weighting, promotion and portfolio authority")

    by_family = {row["family"]: row for row in registry["owners"]}
    checks += 1
    forecast = by_family.get("forecast_baseline")
    if not forecast or forecast["canonical_path_pattern"] != "03_WEEKLY_OPERATIONS/forecast_ledger/*__official.md":
        fail("forecast ledger canonical path is not bound")

    checks += 1
    if forecast["navigation_pointer"] != "03_WEEKLY_OPERATIONS/forecast_ledger/latest_forecast_ledger.json":
        fail("forecast navigation pointer is not bound")

    checks += 1
    etf = by_family.get("etf_flows")
    if not etf or etf["coverage"]["btc_sessions"] != 651 or etf["coverage"]["eth_sessions"] != 513:
        fail("ETF owner coverage does not match archived validated package")

    checks += 1
    if join["authority"]["backfill_allowed"] is not False:
        fail("forecast backfill must remain forbidden")

    summary = coverage["summary"]
    checks += 1
    if summary["gate_b_result"] != "NO_GO" or summary["ready_for_unrestricted_economic_execution"]:
        fail("Gate B must remain closed with no unrestricted economic-ready families")

    checks += 1
    if coverage["final_holdout_opened"] is not False:
        fail("final holdout must remain sealed")

    unresolved = {row["family"] for row in registry["owners"] if row["status"] == "UNRESOLVED"}
    checks += 1
    if unresolved != {"stablecoin_flows", "defi_bridges"}:
        fail("unresolved owner set changed unexpectedly")

    print(json.dumps({"status": "PASS", "checks": checks, "failures": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        raise