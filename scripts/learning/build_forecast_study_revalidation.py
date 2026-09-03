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
    REVALIDATION,
    canon,
    digest,
    iso,
    parse_dt,
    technical_revalidation,
    validate_activation,
    verify_self_hash,
    with_self_hash,
)

UTC = timezone.utc


def read(path: Path):
    return json.loads(path.read_text())


def write_new(path: Path, value: dict) -> bool:
    payload = canon(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise RuntimeError(f"APPEND_ONLY_COLLISION:{path}")
        return False
    path.write_bytes(payload)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forecast-root", type=Path, required=True)
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--endpoint-erratum", type=Path, required=True)
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)

    if not args.activation.exists():
        print(json.dumps({"status": "WAITING_FOR_COHORT_ACTIVATION", "outcome_data_read": False}, sort_keys=True))
        return

    activation = read(args.activation)
    prereg_bytes = args.preregistration.read_bytes()
    erratum_bytes = args.endpoint_erratum.read_bytes()
    validate_activation(activation, prereg_bytes, erratum_bytes)

    forecasts = {}
    if args.forecast_root.exists():
        for path in args.forecast_root.glob("*.json"):
            value = read(path)
            if value.get("forecast_id"):
                forecasts[value["forecast_id"]] = value

    ledger = args.study_root / "STUDY_ADMISSION_LEDGER_v1"
    output_root = args.study_root / "TECHNICAL_REVALIDATION"
    counts = {"created_pass": 0, "created_fail": 0, "future_due": 0, "noop": 0}
    errors = []

    for path in sorted(ledger.glob("*.json")) if ledger.exists() else []:
        admission = read(path)
        if admission.get("status") != "ADMITTED":
            continue
        verify_self_hash(admission, "admission_sha256")
        forecast_id = admission["forecast_id"]
        destination = output_root / f"{forecast_id}.json"
        if destination.exists():
            existing = read(destination)
            verify_self_hash(existing, "revalidation_sha256")
            counts["noop"] += 1
            continue
        if now < parse_dt(str(admission["outcome_due_utc"])):
            counts["future_due"] += 1
            continue

        forecast = forecasts.get(forecast_id)
        try:
            if forecast is None:
                raise ValueError("FROZEN_FORECAST_MISSING")
            revalidation = technical_revalidation(
                admission, forecast, activation, prereg_bytes, erratum_bytes, iso(now)
            )
        except Exception as exc:
            revalidation = {
                "contract": REVALIDATION,
                "forecast_id": forecast_id,
                "admission_id": admission.get("admission_id"),
                "revalidated_at_utc": iso(now),
                "status": "FAIL",
                "checks": {},
                "error": str(exc),
                "outcome_data_read": False,
                "technical_failure_effect": "OUTCOME_UNAVAILABLE",
                "authority": {
                    "forecast_skill_claim": False,
                    "portfolio_action": False,
                    "model_weight_change": False,
                },
            }
            revalidation = with_self_hash(revalidation, "revalidation_sha256")
        try:
            write_new(destination, revalidation)
            counts["created_pass" if revalidation["status"] == "PASS" else "created_fail"] += 1
        except Exception as exc:
            errors.append({"forecast_id": forecast_id, "error": str(exc)})

    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "counts": counts,
                "errors": errors,
                "outcome_data_read": False,
            },
            sort_keys=True,
        )
    )
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
