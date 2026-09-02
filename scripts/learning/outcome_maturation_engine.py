from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from metric_resolver import (  # noqa: E402  (path is prepared immediately above)
    RESOLVER_VERSION,
    resolve,
    resolve_for_forecast,
)

UNIT_CONTRACT_VERSION = "FORECAST_TARGET_UNITS_v2"
SETTLEMENT_EXACT_TARGET_TIME_V1 = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
SETTLEMENT_LEGACY_FIRST_CAPTURE_V0 = "LEGACY_FIRST_CAPTURE_AFTER_DUE_v0"
SUPPORTED_SETTLEMENT_CONTRACTS = {
    SETTLEMENT_EXACT_TARGET_TIME_V1,
    SETTLEMENT_LEGACY_FIRST_CAPTURE_V0,
}

# Mutable pointer files are not immutable scientific evidence and must never be
# selected as the evidence anchor for a matured outcome (TASK3 R3-17 item 5).
EXCLUDED_EVIDENCE_FILENAMES = frozenset({"LATEST.json"})


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def parse_dt(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def legacy_unit_ambiguous(forecast: dict[str, Any]) -> bool:
    if forecast.get("contract") != "FROZEN_FORECAST_v1":
        return False
    if forecast.get("unit_contract_version") == UNIT_CONTRACT_VERSION:
        return False
    # Automatic experiment RANGE rows converted absolute bounds to percentage bounds before freeze.
    if forecast.get("source_candidate_id") and forecast.get("direction") == "RANGE":
        return False
    # Legacy automatic directional rows and legacy ratified rows lack enough metadata
    # to distinguish absolute targets from percentages without hindsight/guesswork.
    return True


def settlement_contract(forecast: dict[str, Any]) -> str:
    """Return the frozen settlement-time contract for this forecast.

    Historical forecasts did not declare a settlement-time contract. They keep
    their original first-capture-after-due behavior for archive compatibility,
    but that behavior is explicitly legacy and is never scientific-score
    eligible. New forecasts may opt into the exact-target-time contract only
    when their owner can later supply evidence whose observation timestamp is
    exactly the frozen outcome_due_utc. Publication grace is operational wait
    time only; it never moves the market observation being scored.
    """
    declared = forecast.get("settlement_contract_version")
    contract = str(declared) if declared else SETTLEMENT_LEGACY_FIRST_CAPTURE_V0
    if contract not in SUPPORTED_SETTLEMENT_CONTRACTS:
        raise ValueError(f"unsupported_settlement_contract:{contract}")
    return contract


def validate_forecast(forecast: dict[str, Any]) -> None:
    frozen = parse_dt(forecast["frozen_at_utc"])
    due = parse_dt(forecast["outcome_due_utc"])
    if frozen >= due:
        raise ValueError("invalid_horizon")
    settlement_contract(forecast)
    direction = forecast.get("direction")
    if direction not in {"UP", "DOWN", "RANGE"}:
        raise ValueError("invalid_direction")
    if legacy_unit_ambiguous(forecast):
        return
    if direction in {"UP", "DOWN"}:
        threshold = forecast.get("threshold_pct")
        if not isinstance(threshold, (int, float)) or float(threshold) <= 0:
            raise ValueError("threshold_must_be_positive")
    else:
        lower = forecast.get("range_lower_pct")
        upper = forecast.get("range_upper_pct")
        if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)) or float(lower) >= float(upper):
            raise ValueError("explicit_range_bounds_required")
    if not isinstance(forecast.get("start_value"), (int, float)):
        raise ValueError("start_value_required")
    if not forecast.get("metric_path"):
        raise ValueError("metric_path_required")


def classify(forecast: dict[str, Any], start: float, end: float) -> str:
    if legacy_unit_ambiguous(forecast):
        raise ValueError("legacy_v1_unit_ambiguous")
    move = (end / start - 1.0) * 100 if start else 0.0
    direction = forecast["direction"]
    if direction == "UP":
        hit = move >= float(forecast["threshold_pct"])
    elif direction == "DOWN":
        hit = move <= -float(forecast["threshold_pct"])
    else:
        hit = float(forecast["range_lower_pct"]) <= move <= float(forecast["range_upper_pct"])
    return "HIT" if hit else "MISS"


def settlement_fields(
    contract: str,
    due: datetime,
    evidence_timestamp: datetime | None,
    *,
    score_eligible: bool,
    exclusion_reason: str | None,
) -> dict[str, Any]:
    offset = None
    if evidence_timestamp is not None:
        offset = round((evidence_timestamp - due).total_seconds(), 6)
    return {
        "settlement_contract_version": contract,
        "settlement_target_utc": iso(due),
        "settlement_observation_utc": iso(evidence_timestamp) if evidence_timestamp is not None else None,
        "settlement_offset_seconds": offset,
        "scientific_score_eligible": score_eligible,
        "scientific_score_exclusion_reason": exclusion_reason,
    }


def select_evidence(
    evidence: list[tuple[datetime, Path, dict[str, Any]]],
    due: datetime,
    contract: str,
    max_ts: datetime,
) -> tuple[datetime, Path, dict[str, Any]] | None:
    if contract == SETTLEMENT_EXACT_TARGET_TIME_V1:
        # The publication grace controls how long the system waits for an exact
        # due-time observation to appear. It must never shift the scored market
        # observation forward in time.
        return next((row for row in evidence if row[0] == due), None)
    return next((row for row in evidence if due <= row[0] <= max_ts), None)


def write_outcome(path: Path, outcome: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canon(outcome))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--now-utc")
    ap.add_argument("--max-evidence-lag-hours", type=float, default=24.0)
    args = ap.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(timezone.utc)

    evidence: list[tuple[datetime, Path, dict[str, Any]]] = []
    for path in args.evidence_root.rglob("*.json") if args.evidence_root.exists() else []:
        if path.name in EXCLUDED_EVIDENCE_FILENAMES:
            continue
        try:
            value = read(path)
            timestamp = value.get("captured_at_utc") or value.get("freeze_utc") or value.get("created_at_utc") or value.get("snapshot_utc")
            if timestamp:
                evidence.append((parse_dt(timestamp), path, value))
        except Exception:
            continue
    evidence.sort(key=lambda row: row[0])

    matured = pending = censored = quarantined = score_eligible = score_excluded = 0
    errors: list[dict[str, str]] = []
    for path in args.forecast_root.rglob("*.json") if args.forecast_root.exists() else []:
        try:
            forecast = read(path)
            if forecast.get("contract") != "FROZEN_FORECAST_v1":
                continue
            validate_forecast(forecast)
            forecast_id = forecast["forecast_id"]
            due = parse_dt(forecast["outcome_due_utc"])
            contract = settlement_contract(forecast)
            if now < due:
                pending += 1
                continue
            destination = args.output_root / f"{forecast_id}.json"
            if destination.exists():
                continue

            if legacy_unit_ambiguous(forecast):
                outcome = {
                    "contract": "MATURED_OUTCOME_v3",
                    "forecast_id": forecast_id,
                    "status": "CENSORED",
                    "reason": "LEGACY_V1_TARGET_UNIT_AMBIGUOUS",
                    "forecast_sha256": sha(forecast),
                    "created_at_utc": iso(now),
                    "resolver_version": RESOLVER_VERSION,
                    "metric_path_root_applied": None,
                    **settlement_fields(
                        contract,
                        due,
                        None,
                        score_eligible=False,
                        exclusion_reason="LEGACY_V1_TARGET_UNIT_AMBIGUOUS",
                    ),
                    "authority": {"model_weight_change": False, "portfolio_action": False},
                }
                write_outcome(destination, outcome)
                censored += 1
                quarantined += 1
                score_excluded += 1
                continue

            max_ts = due + timedelta(hours=args.max_evidence_lag_hours)
            selected = select_evidence(evidence, due, contract, max_ts)
            if selected is None:
                if now <= max_ts:
                    # Wait for the original evidence/publication window to close.
                    # Under exact-time settlement this grace is publication delay
                    # only and never changes the target observation time.
                    pending += 1
                    continue
                reason = (
                    "NO_EXACT_TARGET_TIME_EVIDENCE_WITHIN_PUBLICATION_GRACE"
                    if contract == SETTLEMENT_EXACT_TARGET_TIME_V1
                    else "NO_EVIDENCE_WITHIN_MAX_LAG"
                )
                outcome = {
                    "contract": "MATURED_OUTCOME_v3",
                    "forecast_id": forecast_id,
                    "status": "CENSORED",
                    "reason": reason,
                    "forecast_sha256": sha(forecast),
                    "created_at_utc": iso(now),
                    "resolver_version": RESOLVER_VERSION,
                    "metric_path_root_applied": None,
                    **settlement_fields(
                        contract,
                        due,
                        None,
                        score_eligible=False,
                        exclusion_reason=reason,
                    ),
                    "authority": {"model_weight_change": False, "portfolio_action": False},
                }
                write_outcome(destination, outcome)
                censored += 1
                score_excluded += 1
                continue

            evidence_timestamp, evidence_path, evidence_value = selected
            metric_path = forecast["metric_path"]
            resolution = resolve_for_forecast(evidence_value, forecast, metric_path)
            start_value = float(forecast["start_value"])

            baseline_path = forecast.get("baseline_evidence_path")
            baseline_hash = forecast.get("baseline_evidence_sha256")
            if baseline_path and baseline_hash:
                baseline_file = Path(baseline_path)
                if not baseline_file.exists():
                    raise ValueError("baseline_evidence_missing")
                baseline_value = read(baseline_file)
                if sha(baseline_value) != baseline_hash:
                    raise ValueError("baseline_evidence_hash_mismatch")
                baseline_resolution = (
                    resolve(baseline_value, metric_path, resolution.root_contract)
                    if resolution.root_contract
                    else resolve_for_forecast(baseline_value, forecast, metric_path)
                )
                if not baseline_resolution.ok or abs(float(baseline_resolution.value) - start_value) > max(1e-9, abs(start_value) * 1e-8):
                    raise ValueError("start_value_baseline_mismatch")

            exact_observation = contract == SETTLEMENT_EXACT_TARGET_TIME_V1 and evidence_timestamp == due
            if not resolution.ok:
                outcome = {
                    "contract": "MATURED_OUTCOME_v3",
                    "forecast_id": forecast_id,
                    "status": "CENSORED",
                    "reason": resolution.status,
                    "forecast_sha256": sha(forecast),
                    "evidence_path": str(evidence_path),
                    "evidence_sha256": sha(evidence_value),
                    "created_at_utc": iso(now),
                    "resolver_version": RESOLVER_VERSION,
                    "metric_path_root_applied": resolution.root_contract,
                    **settlement_fields(
                        contract,
                        due,
                        evidence_timestamp,
                        score_eligible=False,
                        exclusion_reason=resolution.status,
                    ),
                    "authority": {"model_weight_change": False, "portfolio_action": False},
                }
                censored += 1
                score_excluded += 1
            else:
                end_value = resolution.value
                exclusion = None if exact_observation else "LEGACY_POST_DUE_CAPTURE_SETTLEMENT"
                outcome = {
                    "contract": "MATURED_OUTCOME_v3",
                    "forecast_id": forecast_id,
                    "status": "MATURED",
                    "result": classify(forecast, start_value, float(end_value)),
                    "start_value": start_value,
                    "end_value": end_value,
                    "return_pct": round((float(end_value) / start_value - 1) * 100, 8) if start_value else None,
                    "forecast_sha256": sha(forecast),
                    "evidence_path": str(evidence_path),
                    "evidence_sha256": sha(evidence_value),
                    "evidence_lag_hours": round((evidence_timestamp - due).total_seconds() / 3600, 6),
                    "created_at_utc": iso(now),
                    "resolver_version": RESOLVER_VERSION,
                    "metric_path_root_applied": resolution.root_contract,
                    **settlement_fields(
                        contract,
                        due,
                        evidence_timestamp,
                        score_eligible=exact_observation,
                        exclusion_reason=exclusion,
                    ),
                    "authority": {"model_weight_change": False, "portfolio_action": False},
                }
                matured += 1
                if exact_observation:
                    score_eligible += 1
                else:
                    score_excluded += 1
            write_outcome(destination, outcome)
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})

    print(json.dumps({
        "matured": matured,
        "censored": censored,
        "pending": pending,
        "quarantined": quarantined,
        "scientific_score_eligible": score_eligible,
        "scientific_score_excluded": score_excluded,
        "errors": errors,
    }, sort_keys=True))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
