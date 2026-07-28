#!/usr/bin/env python3
"""Validate the Global Liquidity Causal Chain research control package."""
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
    claims = load("CLAIM_FREEZE_v1.json")
    sources = load("SOURCE_REGISTRY_v1.json")
    dag = load("CAUSAL_DAG_v1.json")
    state = load("EXECUTION_STATE_v1.json")
    monitor = load("PROSPECTIVE_MONITORING_CONTRACT_v1.json")

    claim_ids = [row["claim_id"] for row in claims["claims"]]
    checks += 1
    if len(claim_ids) != len(set(claim_ids)) or len(claim_ids) < 6:
        fail("claim IDs must be unique and complete")

    dataset_ids = [row["dataset_id"] for row in sources["datasets"]]
    checks += 1
    if len(dataset_ids) != len(set(dataset_ids)):
        fail("dataset IDs must be unique")

    checks += 1
    if sources["authority"]["economic_execution_allowed"] is not False:
        fail("economic execution must remain locked")

    expected_phases = [
        "P0_CLAIM_FREEZE",
        "P1_SOURCE_ARCHITECTURE",
        "P2_DATA_ACQUISITION_AND_NORMALISATION",
        "P3_STATISTICAL_ENGINE_VALIDATION",
        "P4_GRAPH_ENGINE_VALIDATION",
        "P5_ECONOMIC_TEST_EXECUTION",
        "P6_INDEPENDENT_REPLICATION",
        "P7_PROSPECTIVE_MONITORING",
    ]
    checks += 1
    if [row["phase"] for row in state["phases"]] != expected_phases:
        fail("phase order changed")

    p5 = next(row for row in state["phases"] if row["phase"] == "P5_ECONOMIC_TEST_EXECUTION")
    checks += 1
    if p5["allowed"] is not False or "G20" not in p5["status"]:
        fail("P5 must remain blocked by G20")

    node_ids = {row["id"] for row in dag["nodes"]}
    checks += 1
    for edge in dag["edges"]:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            fail(f"edge references unknown node: {edge}")

    checks += 1
    required_forbidden = {
        "live liquidity trading signal",
        "retrospective forecast row",
        "automatic sensor promotion",
        "automatic gate change",
        "portfolio action",
    }
    if set(monitor["prohibited"]) != required_forbidden:
        fail("monitor prohibition set changed")

    checks += 1
    if any(claims["authority"].values()):
        fail("claim package has forbidden authority")

    print(json.dumps({"status": "PASS", "checks": checks, "failures": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        raise
