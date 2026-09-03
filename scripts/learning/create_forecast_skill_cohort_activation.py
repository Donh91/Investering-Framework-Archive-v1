#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--endpoint-erratum", type=Path, required=True)
    parser.add_argument("--implementation-main-sha", required=True)
    parser.add_argument("--implementation-readback-at-utc", required=True)
    parser.add_argument("--recorded-at-utc")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if len(args.implementation_main_sha) != 40:
        raise SystemExit("IMPLEMENTATION_MAIN_SHA_INVALID")
    prereg_bytes = args.preregistration.read_bytes()
    erratum_bytes = args.endpoint_erratum.read_bytes()
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
    print(json.dumps({"status": "CREATED", "cohort_start_utc": activation["cohort_start_utc"], "cohort_end_utc_exclusive": activation["cohort_end_utc_exclusive"], "outcome_data_read": False}, sort_keys=True))


if __name__ == "__main__":
    main()
