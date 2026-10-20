from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUTCOME_CONTRACT = "OFFICIAL_DAILY_COMPASS_OUTCOME_v1"
FREEZE_CONTRACT = "OFFICIAL_DAILY_COMPASS_v1"
PROTECTION_CONTRACT = "COMPASS_PROTECTION_TRACKER_v1"
REPORT_CONTRACT = "ACTION_COMPASS_PROTECTION_CALIBRATION_v2"
ELIGIBLE_DECISION_POLICIES = {
    "2026-09-25_DECISION_INTEGRITY_V3_2",
    "2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0",
}
ELIGIBLE_PROJECTION_SOURCE = "MACHINE_PACKAGE"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def frozen_compass_digest(freeze: dict[str, Any]) -> str | None:
    """Recompute the producer's frozen digest, excluding its self-hash.

    Mirrors native_handlekompas.py: json.dumps(sorted, compact,
    ensure_ascii=False, allow_nan=False) plus one trailing newline.
    Invalid/noncanonical data fails closed instead of entering calibration.
    """
    try:
        payload = {key: value for key, value in freeze.items() if key != "compass_sha256"}
        canonical = (json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError):
        return None
    return hashlib.sha256(canonical).hexdigest()


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def median(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(statistics.median(values)), 10)


def iso_now(value: str | None) -> str:
    if value:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("generated_at_utc_timezone_required")
        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_repo_path(repo_root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative or relative.startswith("/"):
        return None
    root = repo_root.resolve()
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        return None
    return path


def eligible_typed_protection(freeze: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    if freeze.get("contract") != FREEZE_CONTRACT:
        return None, "FREEZE_CONTRACT_INVALID"
    schema = freeze.get("schema_version")
    if isinstance(schema, bool) or not isinstance(schema, (int, float)) or int(schema) < 3:
        return None, "PRE_DECISION_INTEGRITY_SCHEMA"
    policy = str(freeze.get("decision_policy_version") or "")
    if policy not in ELIGIBLE_DECISION_POLICIES:
        return None, "UNREGISTERED_DECISION_POLICY"

    cn = ((freeze.get("source_bindings") or {}).get("cycle_navigator") or {})
    if cn.get("decision_projection_source") != ELIGIBLE_PROJECTION_SOURCE:
        return None, "PROJECTION_NOT_PROSPECTIVE_MACHINE_PACKAGE"

    tracker = freeze.get("protection_tracker")
    if not isinstance(tracker, dict) or tracker.get("contract") != PROTECTION_CONTRACT:
        return None, "PROTECTION_TRACKER_MISSING"
    if tracker.get("data_quality") != "OK":
        return None, "PROTECTION_DATA_QUALITY_NOT_OK"
    if tracker.get("pullback_risk_state") in {None, "", "UNAVAILABLE"}:
        return None, "PROTECTION_STATE_UNAVAILABLE"
    if not isinstance(tracker.get("invalidation"), str) or not tracker.get("invalidation", "").strip():
        return None, "PROTECTION_INVALIDATION_MISSING"
    return tracker, None


def full_exit_reference(terminal_return_pct: float | None) -> tuple[float | None, float | None]:
    if terminal_return_pct is None:
        return None, None
    return max(0.0, -terminal_return_pct), max(0.0, terminal_return_pct)


def collect_rows(repo_root: Path, outcome_root: Path) -> tuple[list[dict[str, Any]], int, Counter[str]]:
    rows: list[dict[str, Any]] = []
    outcome_count = 0
    excluded: Counter[str] = Counter()
    if not outcome_root.exists():
        return rows, outcome_count, excluded

    for path in sorted(outcome_root.rglob("*.json")):
        try:
            outcome = read_json(path)
        except Exception:
            excluded["OUTCOME_INVALID_JSON"] += 1
            continue
        if outcome.get("contract") != OUTCOME_CONTRACT:
            continue
        outcome_count += 1

        freeze_path = safe_repo_path(repo_root, outcome.get("forecast_path"))
        if freeze_path is None or not freeze_path.exists():
            excluded["FORECAST_BINDING_UNAVAILABLE"] += 1
            continue
        try:
            freeze = read_json(freeze_path)
        except Exception:
            excluded["FORECAST_INVALID_JSON"] += 1
            continue
        if freeze.get("compass_id") != outcome.get("compass_id") or freeze.get("compass_sha256") != outcome.get("compass_sha256"):
            excluded["FORECAST_BINDING_MISMATCH"] += 1
            continue
        # Matching declared identifiers are insufficient: historical freeze bytes
        # might have changed while their copied claimed digests stayed identical.
        computed_digest = frozen_compass_digest(freeze)
        if computed_digest is None or computed_digest != freeze.get("compass_sha256"):
            excluded["FORECAST_PAYLOAD_HASH_MISMATCH"] += 1
            continue

        tracker, reason = eligible_typed_protection(freeze)
        if tracker is None:
            excluded[reason or "PROTECTION_INELIGIBLE"] += 1
            continue

        realized = outcome.get("realized")
        if not isinstance(realized, dict):
            excluded["REALIZED_OUTCOME_MISSING"] += 1
            continue

        horizon = str(outcome.get("horizon") or "UNKNOWN")
        common = {
            "horizon": horizon,
            "pullback_risk_state": str(tracker.get("pullback_risk_state") or "UNAVAILABLE"),
            "pullback_class": str(tracker.get("pullback_class") or "UNKNOWN"),
            "distribution_risk": str(tracker.get("distribution_risk") or "UNKNOWN"),
            "confidence_quality": str(tracker.get("confidence_quality") or "LOW"),
            "eta_window": str(tracker.get("eta_window") or "UNKNOWN"),
            "reentry_state": str(tracker.get("reentry_state") or "UNAVAILABLE"),
            "drivers": tuple(str(x) for x in (tracker.get("decisive_public_drivers") or [])[:4]),
            "invalidation": str(tracker.get("invalidation") or ""),
            "compass_id": str(outcome.get("compass_id") or ""),
        }
        for asset, prefix in (("BTC_USDT_MARK_PRICE", "btc"), ("ETH_USDT_MARK_PRICE", "eth")):
            terminal = finite_number(realized.get(f"{prefix}_return_pct"))
            upside = finite_number(realized.get(f"{prefix}_mfe_pct"))
            drawdown = finite_number(realized.get(f"{prefix}_mae_pct"))
            if terminal is None and upside is None and drawdown is None:
                continue
            preserved, foregone = full_exit_reference(terminal)
            rows.append({
                **common,
                "series_id": asset,
                "terminal_return_pct": terminal,
                "max_upside_after_signal_pct": upside,
                "max_drawdown_after_signal_pct": drawdown,
                "full_exit_capital_preserved_reference_pct": preserved,
                "full_exit_terminal_upside_foregone_reference_pct": foregone,
            })
    return rows, outcome_count, excluded


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            row["horizon"],
            row["pullback_risk_state"],
            row["pullback_class"],
            row["distribution_risk"],
            row["confidence_quality"],
            row["series_id"],
        )
        groups.setdefault(key, []).append(row)

    output: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]

        def numbers(field: str) -> list[float]:
            return [float(row[field]) for row in group if row.get(field) is not None]

        driver_sets = sorted({row["drivers"] for row in group})
        output.append({
            "horizon": key[0],
            "pullback_risk_state": key[1],
            "pullback_class": key[2],
            "distribution_risk": key[3],
            "confidence_quality": key[4],
            "series_id": key[5],
            "observation_count": len(group),
            "eta_windows_observed": sorted({row["eta_window"] for row in group}),
            "reentry_states_observed": sorted({row["reentry_state"] for row in group}),
            "decisive_driver_sets_observed": [list(x) for x in driver_sets[:10]],
            "invalidation_texts_observed": sorted({row["invalidation"] for row in group})[:10],
            "median_terminal_return_pct": median(numbers("terminal_return_pct")),
            "median_max_upside_after_signal_pct": median(numbers("max_upside_after_signal_pct")),
            "median_max_drawdown_after_signal_pct": median(numbers("max_drawdown_after_signal_pct")),
            "median_full_exit_capital_preserved_reference_pct": median(numbers("full_exit_capital_preserved_reference_pct")),
            "median_full_exit_terminal_upside_foregone_reference_pct": median(numbers("full_exit_terminal_upside_foregone_reference_pct")),
        })
    return output


def nonwarning_downside_context(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Observe downside while no typed protection warning was issued.

    Descriptive only. Overlapping freezes and horizon windows are not
    independent adverse-event families; neither a minimum MAE nor a return
    constitutes a retrospective alert, missed warning or sell permission.
    """
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        if row["distribution_risk"] in {"WARNING", "CONFIRMED"}:
            continue
        if row["pullback_risk_state"] in {"ELEVATED", "HIGH", "CONFIRMED"}:
            continue
        groups.setdefault((row["horizon"], row["series_id"]), []).append(row)

    context: list[dict[str, Any]] = []
    for (horizon, series), group in sorted(groups.items()):
        downside = [
            value for row in group
            if (value := finite_number(row.get("max_drawdown_after_signal_pct"))) is not None
        ]
        context.append({
            "horizon": horizon,
            "series_id": series,
            "series_row_count": len(group),
            "distinct_compass_freeze_count": len({row["compass_id"] for row in group}),
            "mae_observed_row_count": len(downside),
            "mae_missing_row_count": len(group) - len(downside),
            "median_observed_mae_pct": median(downside),
            "worst_observed_mae_pct": round(min(downside), 10) if downside else None,
            "warning_classification": "NO_TYPED_WARNING_IN_FROZEN_COMPASS",
            "independent_adverse_event_count": None,
        })
    return context


def build_report(repo_root: Path, outcome_root: Path, generated_at_utc: str | None) -> dict[str, Any]:
    rows, outcome_count, excluded = collect_rows(repo_root, outcome_root)
    cohorts = summarize(rows)
    warning_rows = [
        row for row in rows
        if row["distribution_risk"] in {"WARNING", "CONFIRMED"}
        or row["pullback_risk_state"] in {"ELEVATED", "HIGH", "CONFIRMED"}
    ]
    evidence_state = "HAS_MATURED_TYPED_ROWS" if rows else "COLLECTING_PROSPECTIVE_TYPED_ROWS"
    blockers: list[str] = []
    if not rows:
        blockers.append("NO_ELIGIBLE_PROSPECTIVE_TYPED_PROTECTION_OUTCOMES")
    if rows and not warning_rows:
        blockers.append("NO_MATURED_TYPED_WARNING_OUTCOMES")

    return {
        "contract": REPORT_CONTRACT,
        "generated_at_utc": iso_now(generated_at_utc),
        "status": "PASS" if rows else "NO_ELIGIBLE_MATURED_ROWS",
        "source_contract": OUTCOME_CONTRACT,
        "source_outcome_count": outcome_count,
        "eligible_series_row_count": len(rows),
        "warning_series_row_count": len(warning_rows),
        "nonwarning_downside_context": nonwarning_downside_context(rows),
        "excluded_outcome_counts": dict(sorted(excluded.items())),
        "cohorts": cohorts,
        "prospective_source_gate": {
            "minimum_compass_schema_version": 3,
            "registered_decision_policies": sorted(ELIGIBLE_DECISION_POLICIES),
            "required_decision_projection_source": ELIGIBLE_PROJECTION_SOURCE,
            "required_protection_contract": PROTECTION_CONTRACT,
            "historical_prose_backfill": False,
        },
        "evidence_state": evidence_state,
        "promotion_readiness": {
            "status": "NOT_PROMOTION_AUTHORITY",
            "blockers": blockers,
            "automatic_promotion": False,
            "minimum_sample_threshold_invented": False,
            "note": (
                "This report makes typed protection states prospectively outcome-accountable. "
                "It cannot define or promote pullback, distribution, exit, re-entry or ETA rules."
            ),
        },
        "interpretation_boundary": {
            "descriptive_only": True,
            "hit_miss_labels": False,
            "nonwarning_downside_context_is_descriptive": True,
            "overlapping_freezes_are_not_independent_events": True,
            "new_thresholds": False,
            "market_rule_change": False,
            "portfolio_action": False,
            "automatic_promotion": False,
            "note": (
                "Measures post-protection-state upside, drawdown and full-exit reference opportunity cost "
                "from Official Daily Compass outcomes without defining when to reduce, exit or re-enter."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--outcome-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at-utc")
    args = parser.parse_args()
    report = build_report(args.repo_root, args.outcome_root, args.generated_at_utc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "cohort_count": len(report["cohorts"]),
        "row_count": report["eligible_series_row_count"],
        "source_outcome_count": report["source_outcome_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
