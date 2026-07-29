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
    recovery = load("BACKTEST_MASTER_RECOVERY_MANIFEST_v1.json")
    contracts = load("SOURCE_CONTRACTS_v1.json")
    acquisition = load("ACQUISITION_RECEIPT_v1.json")

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

    checks += 1
    exact_final = recovery["expected_exact_final"]
    if exact_final["present_in_upload_set"] is not False or exact_final["byte_integrity_status"] != "BLOCKED_NOT_PRESENT":
        fail("exact final binary must remain explicitly blocked until byte-visible")

    checks += 1
    base = recovery["base_build"]
    if base["sha256"] != "303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f":
        fail("recovered base hash changed")
    if base["contains_master_daily_panel"] is not True:
        fail("recovered base must contain master panel")

    checks += 1
    if any(row["internal_checksums"].endswith("FAIL") for row in recovery["packages"]):
        fail("recovery manifest contains a checksum failure")
    if len(recovery["packages"]) != 10:
        fail("upload-set package count changed")

    checks += 1
    if contracts["rules"]["economic_execution_allowed"] is not False:
        fail("source contracts must not permit economic execution")
    if contracts["rules"]["final_holdout_access_allowed"] is not False:
        fail("source contracts must keep final holdout sealed")
    priorities = {row["priority"] for row in contracts["contracts"]}
    if not {1, 2, 3, 4, 5, 6}.issubset(priorities):
        fail("mandatory WP01 source priorities are incomplete")

    checks += 1
    if acquisition["zip_crc_fail"] != 0:
        fail("uploaded ZIP CRC failure recorded")
    if acquisition["data_ping_internal_checksum_failures"] != 0:
        fail("DATA PING checksum failure recorded")
    if acquisition["tdbc_checksum_failures"] != 0:
        fail("TDBC checksum failure recorded")
    if acquisition["exact_final"]["found"] is not False:
        fail("acquisition receipt must not claim exact final was found")

    checks += 1
    if state["recovery"]["exact_final_present"] is not False:
        fail("execution state must not promote recovered base to exact final")
    if state["execution_rules"]["recovered_base_treated_as_exact_final"] is not False:
        fail("recovered base cannot be treated as exact final")

    print(json.dumps({"status": "PASS", "checks": checks, "failures": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        raise
