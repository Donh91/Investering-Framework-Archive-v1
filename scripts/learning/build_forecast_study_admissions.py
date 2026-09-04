#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from forecast_b1_source_owner import fetch_daily_history  # noqa: E402
from forecast_evidence_class import OWNER_RATIFIED, classify_forecast_evidence  # noqa: E402
from forecast_study_v1_3_2 import (  # noqa: E402
    ADMISSION,
    EXACT_SETTLEMENT,
    STUDY_ID,
    admission_for,
    b1_climatology,
    canon,
    digest,
    digest_bytes,
    iso,
    parse_dt,
    validate_activation,
    validate_candidate_cohort_eligibility,
    validate_source_candidate_binding,
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


def not_admitted(forecast, reason, activation, prereg_bytes, erratum_bytes, now):
    row = {
        "contract": ADMISSION,
        "status": "NOT_ADMITTED",
        "study_id": STUDY_ID,
        "forecast_id": forecast.get("forecast_id"),
        "forecast_sha256": digest(forecast),
        "reason": reason,
        "decision_recorded_at_utc": iso(now),
        "outcome_data_read": False,
        "preregistration_sha256": digest_bytes(prereg_bytes),
        "endpoint_erratum_sha256": digest_bytes(erratum_bytes),
        "activation_receipt_sha256": digest(activation),
        "authority": {
            "forecast_skill_claim": False,
            "portfolio_action": False,
            "model_weight_change": False,
        },
    }
    return with_self_hash(row, "admission_sha256")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forecast-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--endpoint-erratum", type=Path, required=True)
    parser.add_argument("--now-utc")
    parser.add_argument("--fixture-root", type=Path)
    args = parser.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)

    if not args.activation.exists():
        print(json.dumps({"status": "WAITING_FOR_COHORT_ACTIVATION", "admitted": 0, "outcome_data_read": False}, sort_keys=True))
        return

    activation = read(args.activation)
    prereg_bytes = args.preregistration.read_bytes()
    erratum_bytes = args.endpoint_erratum.read_bytes()
    start, end = validate_activation(activation, prereg_bytes, erratum_bytes)

    ledger = args.study_root / "STUDY_ADMISSION_LEDGER_v1"
    b1_root = args.study_root / "B1_CLIMATOLOGY"
    source_root = args.study_root / "B1_SOURCE_RECEIPTS"
    failure_root = args.study_root / "ADMISSION_FAILURES"
    counts = {"admitted": 0, "noop": 0, "outside_cohort": 0, "non_primary": 0, "not_admitted_technical": 0}
    errors = []

    candidate_index = {}
    if args.candidate_root.exists():
        for candidate_path in sorted(args.candidate_root.rglob("*.json")):
            try:
                candidate_record = read(candidate_path)
            except Exception:
                continue
            cid = str(candidate_record.get("candidate_id") or "")
            if cid:
                candidate_index.setdefault(cid, []).append((candidate_path, candidate_record))

    for forecast_path in sorted(args.forecast_root.glob("*.json")) if args.forecast_root.exists() else []:
        try:
            forecast = read(forecast_path)
            if forecast.get("contract") != "FROZEN_FORECAST_v1":
                continue
            forecast_id = str(forecast.get("forecast_id") or "")
            admission_path = ledger / f"{forecast_id}.json"
            failure_path = failure_root / f"{forecast_id}.json"
            if admission_path.exists():
                existing = read(admission_path)
                verify_self_hash(existing, "admission_sha256")
                if existing.get("forecast_sha256") != digest(forecast):
                    raise RuntimeError("EXISTING_ADMISSION_FORECAST_HASH_DRIFT")
                counts["noop"] += 1
                continue
            if failure_path.exists():
                existing = read(failure_path)
                verify_self_hash(existing, "admission_sha256")
                counts["noop"] += 1
                continue

            frozen = parse_dt(str(forecast["frozen_at_utc"]))
            if not (start <= frozen < end):
                counts["outside_cohort"] += 1
                continue

            try:
                evidence_class = classify_forecast_evidence(forecast)
            except Exception as exc:
                write_new(failure_path, not_admitted(forecast, f"EVIDENCE_CLASS_ERROR:{exc}", activation, prereg_bytes, erratum_bytes, now))
                counts["not_admitted_technical"] += 1
                continue

            if evidence_class != OWNER_RATIFIED or forecast.get("direction") not in {"UP", "DOWN"} or forecast.get("settlement_contract_version") != EXACT_SETTLEMENT:
                counts["non_primary"] += 1
                continue

            candidates = candidate_index.get(str(forecast.get("candidate_id") or ""), [])
            if len(candidates) != 1:
                write_new(failure_path, not_admitted(forecast, "SOURCE_CANDIDATE_UNIQUE_BINDING_REQUIRED", activation, prereg_bytes, erratum_bytes, now))
                counts["not_admitted_technical"] += 1
                continue
            candidate_path, candidate_record = candidates[0]
            try:
                source_provenance = validate_source_candidate_binding(candidate_record, forecast)
                candidate_created_at = validate_candidate_cohort_eligibility(candidate_record, start, end)
            except Exception as exc:
                write_new(failure_path, not_admitted(forecast, f"SOURCE_TEMPORAL_PROVENANCE_FAILURE:{exc}", activation, prereg_bytes, erratum_bytes, now))
                counts["not_admitted_technical"] += 1
                continue

            source_path = source_root / f"{forecast_id}.json"
            b1_path = b1_root / f"{forecast_id}.json"
            if source_path.exists() or b1_path.exists():
                if not (source_path.exists() and b1_path.exists()):
                    raise RuntimeError("PARTIAL_B1_FREEZE_STATE")
                source_doc = read(source_path)
                b1_doc = read(b1_path)
                if source_doc.get("forecast_sha256") != digest(forecast) or b1_doc.get("forecast_sha256") != digest(forecast):
                    raise RuntimeError("B1_FREEZE_FORECAST_BINDING_DRIFT")
            else:
                fixture = None
                if args.fixture_root:
                    fixture_path = args.fixture_root / f"{forecast_id}.json"
                    if fixture_path.exists():
                        fixture = read(fixture_path)
                try:
                    bars, source_doc = fetch_daily_history(str(forecast["metric_path"]), str(forecast["frozen_at_utc"]), fixture=fixture, min_bars=190)
                    source_doc.update({"forecast_id": forecast_id, "forecast_sha256": digest(forecast), "retrieved_at_utc": iso(now)})
                    b1_core = b1_climatology(bars, str(forecast["frozen_at_utc"]), int(forecast["horizon_days"]), str(forecast["direction"]), float(forecast["threshold_pct"]))
                    b1_doc = {
                        "contract": "B1_CLIMATOLOGY_FREEZE_RECORD_v1",
                        "forecast_id": forecast_id,
                        "forecast_sha256": digest(forecast),
                        "source_receipt_sha256": digest(source_doc),
                        "source_receipt_path": source_path.as_posix(),
                        "climatology": b1_core,
                        "outcome_data_read": False,
                        "authority": {"forecast_skill_claim": False, "portfolio_action": False, "model_weight_change": False},
                    }
                    write_new(source_path, source_doc)
                    write_new(b1_path, b1_doc)
                except Exception as exc:
                    write_new(failure_path, not_admitted(forecast, f"B1_PRE_OUTCOME_TECHNICAL_FAILURE:{exc}", activation, prereg_bytes, erratum_bytes, now))
                    counts["not_admitted_technical"] += 1
                    continue

            row = admission_for(forecast, evidence_class, activation, prereg_bytes, erratum_bytes, b1_doc["climatology"], iso(now))
            row.update({
                "b1_source_receipt_path": source_path.as_posix(),
                "b1_source_receipt_sha256": digest(source_doc),
                "b1_climatology_path": b1_path.as_posix(),
                "b1_climatology_record_sha256": digest(b1_doc),
                "source_candidate_path": candidate_path.as_posix(),
                "source_candidate_created_at_utc": iso(candidate_created_at),
                **source_provenance,
            })
            row.pop("admission_sha256", None)
            row = with_self_hash(row, "admission_sha256")
            write_new(admission_path, row)
            counts["admitted"] += 1
        except Exception as exc:
            errors.append({"path": str(forecast_path), "error": str(exc)})

    result = {"status": "PASS" if not errors else "FAIL", "counts": counts, "errors": errors, "outcome_data_read": False}
    print(json.dumps(result, sort_keys=True))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
