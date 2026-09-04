#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_study_v1_3_2 import (  # noqa: E402
    ACTIVATION,
    STUDY_ID,
    canon,
    digest_bytes,
    iso,
    parse_dt,
    validate_activation,
    with_self_hash,
)

UTC = timezone.utc


def next_midnight_strictly_after(value: datetime) -> datetime:
    day = datetime(value.year, value.month, value.day, tzinfo=UTC)
    return day + timedelta(days=1)


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise SystemExit(f"GOVERNANCE_DOCUMENT_NOT_OBJECT:{path}")
    return value


def require_no_authority(value: dict, prefix: str) -> None:
    authority = value.get("authority")
    if not isinstance(authority, dict):
        raise SystemExit(f"{prefix}_AUTHORITY_MISSING")
    for key in ("forecast_skill_claim", "portfolio_action", "model_weight_change", "automatic_promotion"):
        if authority.get(key) is not False:
            raise SystemExit(f"{prefix}_AUTHORITY_LEAK:{key}")


def verify_governance_prerequisites(
    prereg_bytes: bytes,
    erratum_bytes: bytes,
    implementation_main_sha: str,
    acceptance: dict,
    active_test: dict,
) -> None:
    prereg_blob = git_blob_sha1(prereg_bytes)
    erratum_blob = git_blob_sha1(erratum_bytes)

    if acceptance.get("contract") != "FORECAST_SKILL_PREREGISTRATION_ACCEPTANCE_v1":
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_CONTRACT_INVALID")
    if acceptance.get("status") != "ACCEPTED_MERGED_READBACK_VERIFIED":
        raise SystemExit("PREREGISTRATION_NOT_ACCEPTED_READBACK_VERIFIED")
    if acceptance.get("study_id") != STUDY_ID:
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_STUDY_ID_MISMATCH")
    prereg_binding = acceptance.get("preregistration") or {}
    erratum_binding = acceptance.get("endpoint_erratum") or {}
    if prereg_binding.get("git_blob_sha1") != prereg_blob:
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_BLOB_MISMATCH")
    if erratum_binding.get("git_blob_sha1") != erratum_blob:
        raise SystemExit("ERRATUM_ACCEPTANCE_BLOB_MISMATCH")
    if acceptance.get("implementation_merge_sha") != implementation_main_sha:
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_IMPLEMENTATION_SHA_MISMATCH")
    if acceptance.get("implementation_ancestor_of_readback") is not True:
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_IMPLEMENTATION_ANCESTRY_UNVERIFIED")
    if acceptance.get("pre_activation_rows_allowed") is not False:
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_PREACTIVATION_ROWS_ALLOWED")
    if acceptance.get("historical_replay_allowed") is not False:
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_HISTORICAL_REPLAY_ALLOWED")
    if acceptance.get("outcome_data_read") is not False:
        raise SystemExit("PREREGISTRATION_ACCEPTANCE_OUTCOME_READ")
    require_no_authority(acceptance, "PREREGISTRATION_ACCEPTANCE")

    if active_test.get("contract") != "FORECAST_SKILL_ACTIVE_TEST_REGISTRATION_v1_3_2":
        raise SystemExit("ACTIVE_TEST_REGISTRATION_CONTRACT_INVALID")
    if active_test.get("status") != "REGISTERED_PRE_ACTIVATION":
        raise SystemExit("ACTIVE_TEST_REGISTRATION_STATUS_INVALID")
    if active_test.get("test_id") != STUDY_ID:
        raise SystemExit("ACTIVE_TEST_REGISTRATION_STUDY_ID_MISMATCH")
    if active_test.get("preregistration_acceptance_contract") != acceptance.get("contract"):
        raise SystemExit("ACTIVE_TEST_ACCEPTANCE_BINDING_MISMATCH")
    if active_test.get("preregistration_git_blob_sha1") != prereg_blob:
        raise SystemExit("ACTIVE_TEST_PREREGISTRATION_BLOB_MISMATCH")
    if active_test.get("endpoint_erratum_git_blob_sha1") != erratum_blob:
        raise SystemExit("ACTIVE_TEST_ERRATUM_BLOB_MISMATCH")
    if active_test.get("implementation_merge_sha") != implementation_main_sha:
        raise SystemExit("ACTIVE_TEST_IMPLEMENTATION_SHA_MISMATCH")
    population = active_test.get("primary_population") or {}
    if population.get("pre_activation_rows_allowed") is not False:
        raise SystemExit("ACTIVE_TEST_PREACTIVATION_ROWS_ALLOWED")
    if population.get("historical_replay_allowed") is not False:
        raise SystemExit("ACTIVE_TEST_HISTORICAL_REPLAY_ALLOWED")
    if population.get("automated_scientific_experiment_pooling_allowed") is not False:
        raise SystemExit("ACTIVE_TEST_EXPERIMENT_POOLING_ALLOWED")
    if active_test.get("outcome_data_read") is not False:
        raise SystemExit("ACTIVE_TEST_OUTCOME_READ")
    if active_test.get("activation_allowed_only_after_registration_merge_readback") is not True:
        raise SystemExit("ACTIVE_TEST_MERGE_READBACK_GATE_MISSING")
    require_no_authority(active_test, "ACTIVE_TEST_REGISTRATION")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--endpoint-erratum", type=Path, required=True)
    parser.add_argument("--preregistration-acceptance", type=Path, required=True)
    parser.add_argument("--active-test-registration", type=Path, required=True)
    parser.add_argument("--implementation-main-sha", required=True)
    parser.add_argument("--implementation-readback-at-utc", required=True)
    parser.add_argument("--recorded-at-utc")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if len(args.implementation_main_sha) != 40:
        raise SystemExit("IMPLEMENTATION_MAIN_SHA_INVALID")
    prereg_bytes = args.preregistration.read_bytes()
    erratum_bytes = args.endpoint_erratum.read_bytes()
    acceptance_bytes = args.preregistration_acceptance.read_bytes()
    active_test_bytes = args.active_test_registration.read_bytes()
    acceptance = read_json(args.preregistration_acceptance)
    active_test = read_json(args.active_test_registration)
    verify_governance_prerequisites(
        prereg_bytes,
        erratum_bytes,
        args.implementation_main_sha,
        acceptance,
        active_test,
    )

    readback = parse_dt(args.implementation_readback_at_utc)
    recorded = parse_dt(args.recorded_at_utc) if args.recorded_at_utc else datetime.now(UTC)
    if recorded < readback:
        raise SystemExit("ACTIVATION_RECORD_PRECEDES_IMPLEMENTATION_READBACK")
    start = next_midnight_strictly_after(recorded)
    end = start + timedelta(days=240)

    activation = {
        "contract": ACTIVATION,
        "status": "ACTIVE",
        "study_id": STUDY_ID,
        "activation_recorded_at_utc": iso(recorded),
        "implementation_main_sha": args.implementation_main_sha,
        "implementation_readback_at_utc": iso(readback),
        "cohort_start_utc": iso(start),
        "cohort_end_utc_exclusive": iso(end),
        "window_axis": "FREEZE_ACCRUAL_UTC_CALENDAR",
        "freeze_accrual_window_days": 240,
        "preregistration_sha256": digest_bytes(prereg_bytes),
        "endpoint_erratum_sha256": digest_bytes(erratum_bytes),
        "preregistration_acceptance_sha256": digest_bytes(acceptance_bytes),
        "active_test_registration_sha256": digest_bytes(active_test_bytes),
        "governance_prerequisites_verified": True,
        "activation_semantics": "FIRST_UTC_MIDNIGHT_STRICTLY_AFTER_ACTIVATION_RECORDING_AND_IMPLEMENTATION_READBACK",
        "pre_activation_rows_allowed": False,
        "rolling_extension_allowed": False,
        "outcome_data_read": False,
        "forecast_skill_status": "UNPROVEN",
        "authority": {
            "forecast_skill_claim": False,
            "portfolio_action": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        },
    }
    activation = with_self_hash(activation, "activation_payload_sha256")
    validate_activation(activation, prereg_bytes, erratum_bytes)
    payload = canon(activation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        if args.output.read_bytes() != payload:
            raise SystemExit("ACTIVATION_RECEIPT_COLLISION")
        print(json.dumps({"status": "DUPLICATE_NOOP", "cohort_start_utc": activation["cohort_start_utc"]}, sort_keys=True))
        return
    args.output.write_bytes(payload)
    print(json.dumps({"status": "CREATED", "cohort_start_utc": activation["cohort_start_utc"], "cohort_end_utc_exclusive": activation["cohort_end_utc_exclusive"], "outcome_data_read": False, "governance_prerequisites_verified": True}, sort_keys=True))


if __name__ == "__main__":
    main()
