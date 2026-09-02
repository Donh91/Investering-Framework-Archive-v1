#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from forecast_settlement_contract import (  # noqa: E402
    SETTLEMENT_EXACT_TARGET_TIME_V1,
    supports_exact_price_settlement,
)
import forecast_settlement_price_owner as price_owner  # noqa: E402
import mature_exact_settlement_forecasts as exact_maturation  # noqa: E402

UTC = timezone.utc
OVERLAY_CONTRACT = "FORECAST_OUTCOME_SUPERSESSION_v1"
REPLAY_ENVELOPE_CONTRACT = "FORECAST_REPLAY_ENVELOPE_v1"
REPLAY_ROLE = "HISTORICAL_SETTLEMENT_DIAGNOSTIC_NOT_FORWARD_EVIDENCE"
UNIT_CONTRACT_VERSION = "FORECAST_TARGET_UNITS_v2"

AUTHORITY = {
    "portfolio_action": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "canonical_promotion": False,
    "scientific_skill_authority": False,
    "historical_outcome_rewrite": False,
}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def replay_population_eligible(forecast: dict[str, Any], original_outcome: dict[str, Any] | None) -> tuple[bool, str]:
    if forecast.get("contract") != "FROZEN_FORECAST_v1":
        return False, "NOT_FROZEN_FORECAST"
    if original_outcome is None:
        return False, "NO_ORIGINAL_OUTCOME"
    if original_outcome.get("contract") != "MATURED_OUTCOME_v3":
        return False, "UNSUPPORTED_ORIGINAL_OUTCOME_CONTRACT"
    if original_outcome.get("forecast_id") != forecast.get("forecast_id"):
        raise ValueError("ORIGINAL_OUTCOME_ID_MISMATCH")
    declared_forecast_hash = original_outcome.get("forecast_sha256")
    if declared_forecast_hash is not None and declared_forecast_hash != digest(forecast):
        raise ValueError("ORIGINAL_OUTCOME_FORECAST_HASH_MISMATCH")
    if forecast.get("settlement_contract_version") == SETTLEMENT_EXACT_TARGET_TIME_V1:
        return False, "ALREADY_EXACT_SETTLEMENT"
    if not supports_exact_price_settlement(str(forecast.get("metric_path") or "")):
        return False, "UNSUPPORTED_PRICE_FAMILY"
    if forecast.get("unit_contract_version") not in (None, UNIT_CONTRACT_VERSION):
        return False, "UNSUPPORTED_TARGET_UNIT_CONTRACT"
    return True, "ELIGIBLE_LEGACY_PRICE_OUTCOME"


def replay_envelope(original: dict[str, Any]) -> dict[str, Any]:
    envelope = dict(original)
    envelope["settlement_contract_version"] = SETTLEMENT_EXACT_TARGET_TIME_V1
    envelope["settlement_activation_semantics"] = "REPLAY_ONLY_NO_CANONICAL_FORECAST_MUTATION"
    envelope["replay_envelope"] = {
        "contract": REPLAY_ENVELOPE_CONTRACT,
        "source_forecast_sha256": digest(original),
        "source_forecast_id": original.get("forecast_id"),
        "role": REPLAY_ROLE,
        "supersedes_without_mutating": True,
    }
    return envelope


def verdict(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": value.get("status"),
        "result": value.get("result"),
        "reason": value.get("reason"),
        "start_value": value.get("start_value"),
        "end_value": value.get("end_value"),
        "return_pct": value.get("return_pct"),
        "resolver_version": value.get("resolver_version"),
        "settlement_contract_version": value.get("settlement_contract_version"),
        "settlement_target_utc": value.get("settlement_target_utc"),
        "settlement_observation_utc": value.get("settlement_observation_utc"),
        "settlement_offset_seconds": value.get("settlement_offset_seconds"),
        "evidence_lag_hours": value.get("evidence_lag_hours"),
    }


def verdict_changed(original: dict[str, Any], replay: dict[str, Any]) -> bool:
    return (
        original.get("status"),
        original.get("result"),
        original.get("reason"),
    ) != (
        replay.get("status"),
        replay.get("result"),
        replay.get("reason"),
    )


def build_overlay(
    original_forecast: dict[str, Any], original_forecast_path: Path,
    original_outcome: dict[str, Any], original_outcome_path: Path,
    envelope: dict[str, Any], evidence: dict[str, Any], evidence_path: Path,
    replay_outcome: dict[str, Any], replay_outcome_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    overlay = {
        "contract": OVERLAY_CONTRACT,
        "forecast_id": original_forecast["forecast_id"],
        "role": REPLAY_ROLE,
        "population_rule": "ALL_EXISTING_OUTCOME_BEARING_LEGACY_FORECASTS_IN_SUPPORTED_EXACT_PRICE_FAMILIES",
        "selection_uses_original_verdict": False,
        "supersedes_without_mutating": True,
        "original": {
            "forecast_path": relative_or_absolute(original_forecast_path, repo_root),
            "forecast_sha256": digest(original_forecast),
            "outcome_path": relative_or_absolute(original_outcome_path, repo_root),
            "outcome_sha256": digest(original_outcome),
            "verdict": verdict(original_outcome),
        },
        "replay": {
            "envelope_contract": REPLAY_ENVELOPE_CONTRACT,
            "envelope_sha256": digest(envelope),
            "settlement_contract_version": SETTLEMENT_EXACT_TARGET_TIME_V1,
            "evidence_path": relative_or_absolute(evidence_path, repo_root),
            "evidence_sha256": digest(evidence),
            "outcome_path": relative_or_absolute(replay_outcome_path, repo_root),
            "outcome_sha256": digest(replay_outcome),
            "verdict": verdict(replay_outcome),
        },
        "comparison": {
            "verdict_changed": verdict_changed(original_outcome, replay_outcome),
            "original_status": original_outcome.get("status"),
            "original_result": original_outcome.get("result"),
            "replay_status": replay_outcome.get("status"),
            "replay_result": replay_outcome.get("result"),
        },
        "authority": AUTHORITY,
    }
    overlay["overlay_sha256"] = digest(overlay)
    return overlay


def validate_existing_replay_outcome(envelope: dict[str, Any], replay_outcome: dict[str, Any]) -> None:
    if replay_outcome.get("forecast_id") != envelope.get("forecast_id"):
        raise ValueError("REPLAY_OUTCOME_FORECAST_ID_MISMATCH")
    if replay_outcome.get("forecast_sha256") != digest(envelope):
        raise ValueError("REPLAY_OUTCOME_ENVELOPE_HASH_MISMATCH")


def run_replay(
    forecast_path: Path,
    original_outcome_path: Path,
    evidence_root: Path,
    raw_root: Path,
    replay_outcome_root: Path,
    overlay_root: Path,
    repo_root: Path,
    now: datetime,
    fixture_dir: Path | None = None,
) -> str:
    original_forecast = read(forecast_path)
    original_outcome = read(original_outcome_path)
    eligible, reason = replay_population_eligible(original_forecast, original_outcome)
    if not eligible:
        return reason

    forecast_id = str(original_forecast["forecast_id"])
    overlay_path = overlay_root / f"{forecast_id}.json"
    if overlay_path.exists():
        existing = read(overlay_path)
        if existing.get("contract") != OVERLAY_CONTRACT or existing.get("original", {}).get("forecast_sha256") != digest(original_forecast):
            raise RuntimeError(f"SUPERSESSION_OVERLAY_COLLISION:{forecast_id}")
        return "DUPLICATE_NOOP"

    envelope = replay_envelope(original_forecast)
    with tempfile.TemporaryDirectory() as td:
        envelope_path = Path(td) / f"{forecast_id}.json"
        envelope_path.write_bytes(canon(envelope))
        owner_status = price_owner.run_one(envelope_path, evidence_root, raw_root, now, fixture_dir)
        if owner_status not in {"CREATED", "DUPLICATE_NOOP"}:
            raise RuntimeError(f"UNEXPECTED_REPLAY_OWNER_STATUS:{owner_status}")

    evidence_path = evidence_root / f"{forecast_id}.json"
    evidence = read(evidence_path)
    exact_maturation.validate_evidence(envelope, evidence, repo_root)

    replay_outcome_root.mkdir(parents=True, exist_ok=True)
    replay_outcome_path = replay_outcome_root / f"{forecast_id}.json"
    if not replay_outcome_path.exists():
        summary = exact_maturation.mature_one(envelope, evidence, replay_outcome_root, repo_root, now, 24.0)
        if int(summary.get("matured", 0)) + int(summary.get("censored", 0)) != 1:
            raise RuntimeError(f"REPLAY_NOT_TERMINAL:{forecast_id}:{summary}")
    replay_outcome = read(replay_outcome_path)
    validate_existing_replay_outcome(envelope, replay_outcome)

    overlay = build_overlay(
        original_forecast,
        forecast_path,
        original_outcome,
        original_outcome_path,
        envelope,
        evidence,
        evidence_path,
        replay_outcome,
        replay_outcome_path,
        repo_root,
    )
    overlay_root.mkdir(parents=True, exist_ok=True)
    overlay_path.write_bytes(canon(overlay))
    return "CREATED_SUPERSESSION_OVERLAY"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--original-outcome-root", type=Path, required=True)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--replay-outcome-root", type=Path, required=True)
    ap.add_argument("--overlay-root", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--fixture-dir", type=Path, help="Tests only; production workflows must omit this argument.")
    ap.add_argument("--max-new-replays", type=int, default=10)
    ap.add_argument("--now-utc")
    args = ap.parse_args()

    if args.max_new_replays < 1 or args.max_new_replays > 50:
        raise SystemExit("MAX_NEW_REPLAYS_OUT_OF_BOUNDS")
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)
    repo_root = args.repo_root.resolve()

    counts: dict[str, int] = {}
    errors: list[dict[str, str]] = []
    created = 0
    attempted = 0
    for forecast_path in sorted(args.forecast_root.rglob("*.json")) if args.forecast_root.exists() else []:
        try:
            forecast = read(forecast_path)
            forecast_id = forecast.get("forecast_id")
            if not forecast_id:
                continue
            original_outcome_path = args.original_outcome_root / f"{forecast_id}.json"
            original_outcome = read(original_outcome_path) if original_outcome_path.exists() else None
            eligible, reason = replay_population_eligible(forecast, original_outcome)
            if not eligible:
                counts[reason] = counts.get(reason, 0) + 1
                continue
            if (args.overlay_root / f"{forecast_id}.json").exists():
                counts["DUPLICATE_NOOP"] = counts.get("DUPLICATE_NOOP", 0) + 1
                continue
            if attempted >= args.max_new_replays:
                counts["DEFERRED_BATCH_LIMIT"] = counts.get("DEFERRED_BATCH_LIMIT", 0) + 1
                continue
            attempted += 1
            status = run_replay(
                forecast_path,
                original_outcome_path,
                args.evidence_root,
                args.raw_root,
                args.replay_outcome_root,
                args.overlay_root,
                repo_root,
                now,
                args.fixture_dir,
            )
            counts[status] = counts.get(status, 0) + 1
            if status == "CREATED_SUPERSESSION_OVERLAY":
                created += 1
        except Exception as exc:
            errors.append({"path": str(forecast_path), "error": str(exc)})

    result = {
        "contract": "FORECAST_OUTCOME_SUPERSESSION_REPLAY_RUN_v1",
        "status": "FAIL" if errors else "PASS",
        "population_rule": "ALL_EXISTING_OUTCOME_BEARING_LEGACY_FORECASTS_IN_SUPPORTED_EXACT_PRICE_FAMILIES",
        "selection_uses_original_verdict": False,
        "max_replay_attempts": args.max_new_replays,
        "attempted_replays": attempted,
        "created_overlays": created,
        "counts": counts,
        "errors": errors,
        "fixture_mode": args.fixture_dir is not None,
        "authority": AUTHORITY,
    }
    print(json.dumps(result, sort_keys=True))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
