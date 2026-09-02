#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "scripts" / "learning" / "outcome_maturation_engine.py"
SETTLEMENT_CONTRACT = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
EVIDENCE_CONTRACT = "FORECAST_SETTLEMENT_EVIDENCE_v1"
BINDING_CONTRACT = "FORECAST_SETTLEMENT_OUTCOME_BINDING_v1"

AUTHORITY = {
    "portfolio_action": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "canonical_promotion": False,
    "scientific_skill_authority": False,
}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def validate_evidence(forecast: dict[str, Any], evidence: dict[str, Any], repo_root: Path) -> None:
    if evidence.get("contract") != EVIDENCE_CONTRACT:
        raise ValueError("WRONG_SETTLEMENT_EVIDENCE_CONTRACT")
    if evidence.get("forecast_id") != forecast.get("forecast_id"):
        raise ValueError("SETTLEMENT_FORECAST_ID_MISMATCH")
    if evidence.get("forecast_sha256") != digest(forecast):
        raise ValueError("SETTLEMENT_FORECAST_HASH_MISMATCH")
    if evidence.get("settlement_contract_version") != SETTLEMENT_CONTRACT:
        raise ValueError("SETTLEMENT_CONTRACT_MISMATCH")
    if evidence.get("metric_path") != forecast.get("metric_path"):
        raise ValueError("SETTLEMENT_METRIC_PATH_MISMATCH")
    due = parse_dt(forecast["outcome_due_utc"])
    if parse_dt(evidence["settlement_target_utc"]) != due:
        raise ValueError("SETTLEMENT_TARGET_TIME_MISMATCH")
    if parse_dt(evidence["captured_at_utc"]) != due:
        raise ValueError("ADJUDICATION_TARGET_TIMESTAMP_MISMATCH")
    if evidence.get("captured_at_semantics") != "ADJUDICATION_TARGET_TIME_NOT_SOURCE_OBSERVATION":
        raise ValueError("ADJUDICATION_TIMESTAMP_SEMANTICS_MISSING")
    if evidence.get("source_candle_confirmed") is not True:
        raise ValueError("SOURCE_CANDLE_NOT_CONFIRMED")
    source_close = parse_dt(evidence["source_candle_close_utc"])
    gap = (source_close - due).total_seconds()
    if gap > 0 or gap < -60.001:
        raise ValueError("SOURCE_CANDLE_OUTSIDE_LAST_CLOSED_MINUTE_WINDOW")
    declared_offset = evidence.get("source_candle_offset_seconds")
    if not isinstance(declared_offset, (int, float)) or abs(float(declared_offset) - gap) > 1e-6:
        raise ValueError("SOURCE_CANDLE_OFFSET_MISMATCH")
    raw_path = Path(str(evidence.get("source_raw_path") or ""))
    if not raw_path.is_absolute():
        raw_path = repo_root / raw_path
    if not raw_path.is_file():
        raise ValueError("SETTLEMENT_RAW_PAYLOAD_MISSING")
    payload = raw_path.read_bytes()
    if len(payload) != evidence.get("source_raw_bytes") or digest_bytes(payload) != evidence.get("source_raw_sha256"):
        raise ValueError("SETTLEMENT_RAW_PAYLOAD_HASH_MISMATCH")
    authority = evidence.get("authority") or {}
    if any(authority.get(key) is not False for key in AUTHORITY):
        raise ValueError("SETTLEMENT_EVIDENCE_AUTHORITY_INVALID")


def binding_for(forecast: dict[str, Any], evidence_path: Path, evidence: dict[str, Any], outcome_path: Path, outcome: dict[str, Any]) -> dict[str, Any]:
    binding = {
        "contract": BINDING_CONTRACT,
        "forecast_id": forecast["forecast_id"],
        "forecast_sha256": digest(forecast),
        "outcome_path": outcome_path.as_posix(),
        "outcome_sha256": digest(outcome),
        "evidence_path": evidence_path.as_posix(),
        "evidence_sha256": digest(evidence),
        "settlement_target_utc": evidence["settlement_target_utc"],
        "source_candle_open_utc": evidence["source_candle_open_utc"],
        "source_candle_close_utc": evidence["source_candle_close_utc"],
        "source_candle_offset_seconds": evidence["source_candle_offset_seconds"],
        "source_retrieved_at_utc": evidence["source_retrieved_at_utc"],
        "source_publication_lag_seconds": evidence["source_publication_lag_seconds"],
        "source_id": evidence["source_id"],
        "source_instrument": evidence["source_instrument"],
        "authority": AUTHORITY,
    }
    binding["binding_sha256"] = digest(binding)
    return binding


def merge_engine_summary(total: dict[str, Any], row: dict[str, Any]) -> None:
    for key in ("matured", "censored", "pending", "quarantined", "scientific_score_eligible", "scientific_score_excluded"):
        total[key] = int(total.get(key, 0)) + int(row.get(key, 0))
    total.setdefault("errors", []).extend(row.get("errors", []))


def mature_one(
    forecast: dict[str, Any], evidence: dict[str, Any] | None, output_root: Path,
    repo_root: Path, now: datetime, max_evidence_lag_hours: float,
) -> dict[str, Any]:
    """Run the canonical engine with exactly one forecast and its own evidence.

    Forecast-bound settlement evidence must never compete with another forecast's
    evidence merely because the two horizons share the same target timestamp.
    """
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        forecast_root = temp / "forecasts"
        evidence_root = temp / "evidence"
        forecast_root.mkdir()
        evidence_root.mkdir()
        (forecast_root / f"{forecast['forecast_id']}.json").write_bytes(canon(forecast))
        if evidence is not None:
            (evidence_root / f"{forecast['forecast_id']}.json").write_bytes(canon(evidence))
        command = [
            sys.executable,
            str(ENGINE),
            "--forecast-root", str(forecast_root),
            "--evidence-root", str(evidence_root),
            "--output-root", str(output_root),
            "--now-utc", now.isoformat().replace("+00:00", "Z"),
            "--max-evidence-lag-hours", str(max_evidence_lag_hours),
        ]
        proc = subprocess.run(command, cwd=repo_root, capture_output=True, text=True)
        if proc.returncode:
            print(proc.stdout, end="")
            print(proc.stderr, file=sys.stderr, end="")
            raise RuntimeError(f"CANONICAL_MATURATION_FAILED:{forecast['forecast_id']}")
        return json.loads(proc.stdout)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--settlement-evidence-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--binding-root", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--now-utc")
    ap.add_argument("--max-evidence-lag-hours", type=float, default=24.0)
    args = ap.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)
    repo_root = args.repo_root.resolve()
    rows: list[tuple[Path, dict[str, Any], Path, dict[str, Any] | None, bool]] = []
    pre_pending = 0
    errors: list[dict[str, str]] = []

    for path in sorted(args.forecast_root.rglob("*.json")) if args.forecast_root.exists() else []:
        try:
            forecast = read(path)
            if forecast.get("contract") != "FROZEN_FORECAST_v1" or forecast.get("settlement_contract_version") != SETTLEMENT_CONTRACT:
                continue
            due = parse_dt(forecast["outcome_due_utc"])
            if now < due:
                pre_pending += 1
                continue
            outcome_path = args.output_root / f"{forecast['forecast_id']}.json"
            evidence_path = args.settlement_evidence_root / f"{forecast['forecast_id']}.json"
            evidence: dict[str, Any] | None = None
            if evidence_path.exists():
                evidence = read(evidence_path)
                validate_evidence(forecast, evidence, repo_root)
            elif now <= due + timedelta(hours=args.max_evidence_lag_hours):
                pre_pending += 1
                continue
            rows.append((path, forecast, evidence_path, evidence, outcome_path.exists()))
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})

    if errors:
        print(json.dumps({"status": "FAIL", "pending": pre_pending, "errors": errors}, sort_keys=True))
        raise SystemExit(2)

    engine_summary: dict[str, Any] = {
        "matured": 0,
        "censored": 0,
        "pending": pre_pending,
        "quarantined": 0,
        "scientific_score_eligible": 0,
        "scientific_score_excluded": 0,
        "errors": [],
    }
    for _, forecast, _, evidence, outcome_exists in rows:
        if outcome_exists:
            continue
        try:
            merge_engine_summary(
                engine_summary,
                mature_one(forecast, evidence, args.output_root, repo_root, now, args.max_evidence_lag_hours),
            )
        except Exception as exc:
            errors.append({"forecast_id": str(forecast.get("forecast_id")), "error": str(exc)})

    if errors:
        print(json.dumps({"status": "FAIL", "engine": engine_summary, "errors": errors}, sort_keys=True))
        raise SystemExit(2)

    bindings_created = 0
    args.binding_root.mkdir(parents=True, exist_ok=True)
    for _, forecast, evidence_path, evidence, _ in rows:
        outcome_path = args.output_root / f"{forecast['forecast_id']}.json"
        if not outcome_path.exists() or evidence is None:
            continue
        outcome = read(outcome_path)
        binding = binding_for(forecast, evidence_path, evidence, outcome_path, outcome)
        binding_path = args.binding_root / f"{forecast['forecast_id']}.json"
        if binding_path.exists():
            existing = read(binding_path)
            if canon(existing) != canon(binding):
                raise SystemExit(f"SETTLEMENT_BINDING_COLLISION:{forecast['forecast_id']}")
            continue
        binding_path.write_bytes(canon(binding))
        bindings_created += 1

    print(json.dumps({
        "status": "PASS",
        "engine": engine_summary,
        "bindings_created": bindings_created,
        "forecast_bound_single_evidence_maturation": True,
        "authority": AUTHORITY,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
