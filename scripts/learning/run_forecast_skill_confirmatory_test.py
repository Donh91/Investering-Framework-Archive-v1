#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_study_v1_3_2 import (  # noqa: E402
    canon,
    confirmatory,
    confirmatory_readiness,
    digest,
    parse_dt,
    validate_activation,
    verify_self_hash,
    with_self_hash,
)

UTC = timezone.utc


def read(path: Path):
    return json.loads(path.read_text())


def write_replace(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canon(value))


def write_final(path: Path, value: dict) -> bool:
    payload = canon(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise RuntimeError("FINAL_RESULT_COLLISION")
        return False
    path.write_bytes(payload)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--outcome-root", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--endpoint-erratum", type=Path, required=True)
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)

    latest = args.study_root / "LATEST_STUDY_STATUS.json"
    final = args.study_root / "FINAL_CONFIRMATORY_RESULT_v1_3_2.json"
    if final.exists():
        frozen = read(final)
        verify_self_hash(frozen, "result_sha256")
        print(json.dumps({"status": "FINAL_ALREADY_FROZEN", "result": frozen}, sort_keys=True))
        return

    if not args.activation.exists():
        status = {
            "contract": "FORECAST_SKILL_STUDY_STATUS_v1",
            "status": "NOT_STARTED_SCIENTIFIC_FIREWALL",
            "forecast_skill_status": "UNPROVEN",
            "outcome_data_read": False,
        }
        write_replace(latest, status)
        print(json.dumps(status, sort_keys=True))
        return

    activation = read(args.activation)
    prereg_bytes = args.preregistration.read_bytes()
    erratum_bytes = args.endpoint_erratum.read_bytes()
    validate_activation(activation, prereg_bytes, erratum_bytes)

    ledger = args.study_root / "STUDY_ADMISSION_LEDGER_v1"
    revalidation_root = args.study_root / "TECHNICAL_REVALIDATION"
    admissions = []
    if ledger.exists():
        for path in sorted(ledger.glob("*.json")):
            value = read(path)
            if value.get("status") == "ADMITTED":
                verify_self_hash(value, "admission_sha256")
                admissions.append(value)
    revalidations = {}
    if revalidation_root.exists():
        for path in revalidation_root.glob("*.json"):
            value = read(path)
            verify_self_hash(value, "revalidation_sha256")
            revalidations[value["forecast_id"]] = value

    readiness = confirmatory_readiness(admissions, revalidations, activation, now.isoformat())
    if readiness["status"] != "READY_FOR_SINGLE_OUTCOME_READ":
        status = {
            "contract": "FORECAST_SKILL_STUDY_STATUS_v1",
            "forecast_skill_status": "UNPROVEN",
            **readiness,
        }
        write_replace(latest, status)
        if readiness["status"] == "INSUFFICIENT_PROSPECTIVE_EVIDENCE":
            terminal = with_self_hash(
                {**status, "terminal": True, "confirmatory_test_executed": False},
                "result_sha256",
            )
            write_final(final, terminal)
        print(json.dumps(status, sort_keys=True))
        return

    outcomes = {}
    if args.outcome_root.exists():
        for path in args.outcome_root.glob("*.json"):
            value = read(path)
            if value.get("forecast_id"):
                outcomes[value["forecast_id"]] = value
    result = confirmatory(admissions, revalidations, outcomes, activation, now.isoformat())
    result["terminal"] = True
    if "result_sha256" not in result:
        result = with_self_hash(result, "result_sha256")
    write_final(final, result)
    write_replace(
        latest,
        {
            "contract": "FORECAST_SKILL_STUDY_STATUS_v1",
            "forecast_skill_status": "UNPROVEN",
            "status": "TERMINAL_RESULT_FROZEN",
            "final_result_sha256": digest(result),
            "outcome_data_read": result.get("outcome_data_read", False),
        },
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
