#!/usr/bin/env python3
"""Validate MAR-WP02A owner bindings, coverage gate and forecast join controls."""
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
    bindings = load("WP02A_LIQUIDITY_ROUTING_OWNER_BINDINGS_v1.json")
    coverage = load("WP02A_COVERAGE_GATE_v1.json")
    forecast = load("FORECAST_BASELINE_JOIN_CONTRACT_v1.json")

    node_ids = [row["node_id"] for row in bindings["routing_nodes"]]
    checks += 1
    if len(node_ids) != len(set(node_ids)):
        fail("routing node IDs must be unique")

    node_set = set(node_ids)
    checks += 1
    for edge in bindings["routing_edges"]:
        if edge["from"] not in node_set or edge["to"] not in node_set:
            fail(f"routing edge references unknown node: {edge}")

    checks += 1
    authority = bindings["authority"]
    if any(authority.values()):
        fail("WP02A must retain zero economic, predictive, promotion and portfolio authority")

    checks += 1
    if coverage["gate_result"] != "NO_GO_FOR_ECONOMIC_EXECUTION":
        fail("coverage gate must remain closed")

    families = [row["family"] for row in coverage["families"]]
    checks += 1
    if len(families) != len(set(families)) or "forecast_baseline" not in families:
        fail("coverage families must be unique and include forecast baseline")

    checks += 1
    required_forecast = set(forecast["required_forecast_fields"])
    for field in {"forecast_created_at_utc", "knowledge_cutoff_at_utc", "immutable_content_hash"}:
        if field not in required_forecast:
            fail(f"missing anti-leakage forecast field: {field}")

    checks += 1
    if forecast["authority"]["backfill_allowed"] is not False:
        fail("retrospective forecast backfill must remain forbidden")

    checks += 1
    if forecast["time_rules"]["retrospective_forecast_rows_forbidden"] is not True:
        fail("retrospective forecast rows must remain forbidden")

    print(json.dumps({"status": "PASS", "checks": checks, "failures": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        raise
