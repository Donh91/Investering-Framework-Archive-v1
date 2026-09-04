#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_study_v1_3_2 import (  # noqa: E402
    ADMISSION,
    digest,
    digest_bytes,
    iso,
    parse_dt,
    validate_activation,
    validate_candidate_cohort_eligibility,
    validate_source_candidate_binding,
    verify_self_hash,
)


def read(path: Path):
    return json.loads(path.read_text())


def repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def git_first_add(repo_root: Path, path: Path) -> tuple[str, str, bytes]:
    rel = repo_relative(repo_root, path)
    proc = subprocess.run(["git", "log", "--diff-filter=A", "--follow", "--reverse", "--format=%H%x09%cI", "--", rel], cwd=repo_root, check=True, capture_output=True, text=True)
    rows = [row for row in proc.stdout.splitlines() if row.strip()]
    if not rows:
        raise ValueError(f"ADMISSION_NOT_GIT_RECORDED:{rel}")
    commit_sha, commit_time = rows[0].split("\t", 1)
    blob = subprocess.run(["git", "show", f"{commit_sha}:{rel}"], cwd=repo_root, check=True, capture_output=True).stdout
    return commit_sha, commit_time, blob


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forecast-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--endpoint-erratum", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    if not args.activation.exists():
        print(json.dumps({"status": "WAITING_FOR_COHORT_ACTIVATION", "validated": 0, "outcome_data_read": False}, sort_keys=True))
        return

    activation = read(args.activation)
    prereg_bytes = args.preregistration.read_bytes()
    erratum_bytes = args.endpoint_erratum.read_bytes()
    start, end = validate_activation(activation, prereg_bytes, erratum_bytes)

    forecasts = {}
    if args.forecast_root.exists():
        for path in args.forecast_root.glob("*.json"):
            value = read(path)
            if value.get("forecast_id"):
                forecasts[value["forecast_id"]] = value
    candidates = {}
    if args.candidate_root.exists():
        for path in sorted(args.candidate_root.rglob("*.json")):
            try:
                value = read(path)
            except Exception:
                continue
            cid = str(value.get("candidate_id") or "")
            if cid:
                candidates.setdefault(cid, []).append((path, value))

    ledger = args.study_root / "STUDY_ADMISSION_LEDGER_v1"
    errors = []
    validated = 0
    for path in sorted(ledger.glob("*.json")) if ledger.exists() else []:
        admission = read(path)
        if admission.get("status") != "ADMITTED":
            continue
        validated += 1
        try:
            verify_self_hash(admission, "admission_sha256")
            forecast = forecasts.get(admission.get("forecast_id"))
            if not forecast:
                raise ValueError("FROZEN_FORECAST_MISSING")
            if admission.get("contract") != ADMISSION:
                raise ValueError("ADMISSION_CONTRACT_MISMATCH")
            if admission.get("forecast_sha256") != digest(forecast):
                raise ValueError("FORECAST_HASH_BINDING_FAILURE")
            if admission.get("preregistration_sha256") != digest_bytes(prereg_bytes):
                raise ValueError("PREREGISTRATION_HASH_BINDING_FAILURE")
            if admission.get("endpoint_erratum_sha256") != digest_bytes(erratum_bytes):
                raise ValueError("ERRATUM_HASH_BINDING_FAILURE")
            if admission.get("activation_receipt_sha256") != digest(activation):
                raise ValueError("ACTIVATION_HASH_BINDING_FAILURE")
            if admission.get("outcome_data_read") is not False:
                raise ValueError("ADMISSION_OUTCOME_DATA_READ")
            candidate_rows = candidates.get(str(forecast.get("candidate_id") or ""), [])
            if len(candidate_rows) != 1:
                raise ValueError("SOURCE_CANDIDATE_UNIQUE_BINDING_REQUIRED")
            candidate_path, candidate_record = candidate_rows[0]
            provenance = validate_source_candidate_binding(candidate_record, forecast)
            candidate_created_at = validate_candidate_cohort_eligibility(candidate_record, start, end)
            if admission.get("source_candidate_path") != candidate_path.as_posix():
                raise ValueError("SOURCE_CANDIDATE_PATH_BINDING_FAILURE")
            if admission.get("source_candidate_created_at_utc") != iso(candidate_created_at):
                raise ValueError("SOURCE_CANDIDATE_COHORT_BINDING_FAILURE")
            for key, expected in provenance.items():
                if admission.get(key) != expected:
                    raise ValueError("SOURCE_TEMPORAL_PROVENANCE_BINDING_FAILURE:" + key)
            frozen = parse_dt(str(forecast["frozen_at_utc"]))
            due = parse_dt(str(forecast["outcome_due_utc"]))
            if not (start <= frozen < end):
                raise ValueError("FORECAST_OUTSIDE_COHORT")

            for field in ("b1_source_receipt_path", "b1_climatology_path"):
                bound = Path(str(admission.get(field) or ""))
                if not bound.is_absolute():
                    bound = args.repo_root / bound
                if not bound.is_file():
                    raise ValueError(f"{field.upper()}_MISSING")
            source_path = args.repo_root / str(admission["b1_source_receipt_path"])
            b1_path = args.repo_root / str(admission["b1_climatology_path"])
            source = read(source_path)
            b1 = read(b1_path)
            if digest(source) != admission.get("b1_source_receipt_sha256"):
                raise ValueError("B1_SOURCE_HASH_BINDING_FAILURE")
            if digest(b1) != admission.get("b1_climatology_record_sha256"):
                raise ValueError("B1_CLIMATOLOGY_HASH_BINDING_FAILURE")
            if source.get("outcome_data_read") is not False or b1.get("outcome_data_read") is not False:
                raise ValueError("B1_OUTCOME_DATA_READ")

            _, commit_time, first_blob = git_first_add(args.repo_root, path)
            if first_blob != path.read_bytes():
                raise ValueError("ADMISSION_CONTENT_CHANGED_AFTER_FIRST_ADD")
            if parse_dt(commit_time) >= due:
                raise ValueError("ADMISSION_GIT_FIRST_ADD_NOT_BEFORE_OUTCOME_DUE")
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})

    revalidations_validated = 0
    revalidation_root = args.study_root / "TECHNICAL_REVALIDATION"
    for path in sorted(revalidation_root.glob("*.json")) if revalidation_root.exists() else []:
        try:
            row = read(path)
            verify_self_hash(row, "revalidation_sha256")
            if row.get("outcome_data_read") is not False:
                raise ValueError("REVALIDATION_OUTCOME_DATA_READ")
            fid = str(row.get("forecast_id") or "")
            admission_path = ledger / f"{fid}.json"
            if not admission_path.exists():
                raise ValueError("REVALIDATION_WITHOUT_ADMISSION")
            admission = read(admission_path)
            verify_self_hash(admission, "admission_sha256")
            if row.get("admission_id") != admission.get("admission_id"):
                raise ValueError("REVALIDATION_ADMISSION_BINDING_FAILURE")
            if parse_dt(str(row.get("revalidated_at_utc"))) < parse_dt(str(admission.get("outcome_due_utc"))):
                raise ValueError("REVALIDATION_BEFORE_DUE")
            _, _commit_time, first_blob = git_first_add(args.repo_root, path)
            if first_blob != path.read_bytes():
                raise ValueError("REVALIDATION_CONTENT_CHANGED_AFTER_FIRST_ADD")
            revalidations_validated += 1
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})

    result = {
        "status": "PASS" if not errors else "FAIL",
        "validated": validated,
        "revalidations_validated": revalidations_validated,
        "errors": errors,
        "outcome_data_read": False,
        "append_only_first_add_binding_verified": not errors,
        "durable_revalidation_barrier_verified": not errors,
    }
    print(json.dumps(result, sort_keys=True))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
