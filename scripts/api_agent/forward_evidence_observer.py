from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TEST_ID = "GATE_BTC_PARTIAL_FT_1"
HORIZON_HOURS = {"24H": 24, "72H": 72, "7D": 168}
COVERAGE_STATUSES = {"CHECKED_NO_DIVERGENCE", "DIVERGENCE_CAPTURED", "NOT_EVALUABLE_DATA_BLOCKED"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp_required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone_aware_timestamp_required")
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _blocked_receipt(source: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    return {
        "contract": "BTC_PARTIAL_WAIT_COVERAGE_RECEIPT_v1",
        "test_id": TEST_ID,
        "check_id": source.get("check_id"),
        "timestamp_utc": source.get("timestamp_utc"),
        "status": "NOT_EVALUABLE_DATA_BLOCKED",
        "reasons": sorted(set(reasons)),
        "source_run_id": source.get("source_run_id"),
        "source_hash": source.get("source_hash"),
        "counts_as_outcome_row": False,
        "divergence_source_row": None,
        "authority": _zero_authority(),
    }


def _zero_authority() -> dict[str, bool]:
    return {
        "framework_state_change": False,
        "portfolio_action": False,
        "market_rule_change": False,
        "threshold_change": False,
        "weight_change": False,
        "canonical_promotion": False,
    }


def observe(source: dict[str, Any]) -> dict[str, Any]:
    if source.get("test_id") != TEST_ID:
        raise ValueError("wrong_registered_test_id")
    required_identity = ["check_id", "timestamp_utc", "source_run_id", "source_hash"]
    missing = [name for name in required_identity if not source.get(name)]
    declared_missing = source.get("missing_fields") or []
    if not isinstance(declared_missing, list):
        raise ValueError("missing_fields_must_be_list")
    if source.get("eligible_check") is not True:
        return _blocked_receipt(source, missing + declared_missing + ["CHECK_NOT_ELIGIBLE"])
    if missing or declared_missing:
        return _blocked_receipt(source, missing + declared_missing)

    timestamp = parse_utc(source["timestamp_utc"])
    assertion = source.get("actual_decision_divergence")
    wait_action = source.get("benchmark_action_WAIT")
    partial_action = source.get("experimental_action_BTC_PARTIAL")

    if not isinstance(assertion, bool):
        return _blocked_receipt(source, ["ACTUAL_DECISION_DIVERGENCE_NOT_EXPLICIT"])
    if wait_action is None or partial_action is None:
        return _blocked_receipt(source, ["ACTION_FIELDS_MISSING"])
    actions_differ = wait_action != partial_action
    if assertion != actions_differ:
        return _blocked_receipt(source, ["ACTION_DIVERGENCE_CONTRADICTS_EXPLICIT_ASSERTION"])

    base = {
        "contract": "BTC_PARTIAL_WAIT_COVERAGE_RECEIPT_v1",
        "test_id": TEST_ID,
        "check_id": source["check_id"],
        "timestamp_utc": iso_z(timestamp),
        "source_run_id": source["source_run_id"],
        "source_hash": source["source_hash"],
        "counts_as_outcome_row": False,
        "authority": _zero_authority(),
    }
    if not assertion:
        base.update({
            "status": "CHECKED_NO_DIVERGENCE",
            "reasons": [],
            "divergence_source_row": None,
        })
        return base

    entry = source.get("entry_reference_price")
    if not isinstance(entry, (int, float)) or isinstance(entry, bool) or entry <= 0:
        return _blocked_receipt(source, ["VALID_ENTRY_REFERENCE_PRICE_REQUIRED_FOR_DIVERGENCE"])

    horizons = {name: iso_z(timestamp + timedelta(hours=hours)) for name, hours in HORIZON_HOURS.items()}
    frozen = {
        "row_id": source.get("row_id") or f"{TEST_ID}:{source['check_id']}",
        "timestamp_utc": iso_z(timestamp),
        "source_run_id": source["source_run_id"],
        "framework_state": source.get("framework_state"),
        "asset_tier": source.get("asset_tier", "BTC"),
        "benchmark_action_WAIT": wait_action,
        "experimental_action_BTC_PARTIAL": partial_action,
        "experimental_action_GRADUATED": source.get("experimental_action_GRADUATED", "DATA_BLOCKED_UNLESS_OWNER_FIELDS_COMPLETE"),
        "decision_divergence": True,
        "permission_reason": source.get("permission_reason"),
        "blocking_reason": source.get("blocking_reason"),
        "required_data_complete": source.get("required_data_complete"),
        "entry_reference_price": float(entry),
        "position_fraction_assumed": source.get("position_fraction_assumed"),
        "frozen_horizon_24h": horizons["24H"],
        "frozen_horizon_72h": horizons["72H"],
        "frozen_horizon_7d": horizons["7D"],
        "max_favorable_excursion_pct": None,
        "max_adverse_excursion_pct": None,
        "return_at_horizon_pct": None,
        "benchmark_return_pct": None,
        "drawdown_pct": None,
        "opportunity_cost_pct": None,
        "false_permission_cost_pct": None,
        "correct_restraint_value_pct": None,
        "final_classification": None,
        "source_lineage": {
            "source_hash": source["source_hash"],
            "source_run_id": source["source_run_id"],
        },
        "framework_acceptance": "PENDING_OUTCOME_MATURITY",
    }
    frozen["frozen_input_sha256"] = canonical_hash({
        key: frozen[key]
        for key in [
            "row_id", "timestamp_utc", "source_run_id", "framework_state", "asset_tier",
            "benchmark_action_WAIT", "experimental_action_BTC_PARTIAL", "decision_divergence",
            "entry_reference_price", "position_fraction_assumed", "frozen_horizon_24h",
            "frozen_horizon_72h", "frozen_horizon_7d", "source_lineage",
        ]
    })
    base.update({
        "status": "DIVERGENCE_CAPTURED",
        "reasons": [],
        "divergence_source_row": frozen,
    })
    return base


def mature(receipt: dict[str, Any], observations: list[dict[str, Any]], as_of_utc: str) -> dict[str, Any]:
    if receipt.get("status") != "DIVERGENCE_CAPTURED":
        raise ValueError("divergence_receipt_required")
    row = receipt.get("divergence_source_row")
    if not isinstance(row, dict):
        raise ValueError("divergence_source_row_required")
    expected_hash = row.get("frozen_input_sha256")
    frozen_subset = {
        key: row.get(key)
        for key in [
            "row_id", "timestamp_utc", "source_run_id", "framework_state", "asset_tier",
            "benchmark_action_WAIT", "experimental_action_BTC_PARTIAL", "decision_divergence",
            "entry_reference_price", "position_fraction_assumed", "frozen_horizon_24h",
            "frozen_horizon_72h", "frozen_horizon_7d", "source_lineage",
        ]
    }
    if expected_hash != canonical_hash(frozen_subset):
        raise ValueError("frozen_input_mutation_detected")

    as_of = parse_utc(as_of_utc)
    by_horizon: dict[str, dict[str, Any]] = {}
    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("observation_object_required")
        horizon = observation.get("horizon")
        if horizon not in HORIZON_HOURS:
            raise ValueError("invalid_horizon")
        if horizon in by_horizon:
            raise ValueError("duplicate_horizon_observation")
        observed_at = parse_utc(observation.get("observed_at_utc"))
        due = parse_utc(row[{"24H": "frozen_horizon_24h", "72H": "frozen_horizon_72h", "7D": "frozen_horizon_7d"}[horizon]])
        if observed_at < due:
            raise ValueError(f"partial_window_forbidden:{horizon}")
        if not observation.get("source_hash"):
            raise ValueError(f"source_hash_required:{horizon}")
        by_horizon[horizon] = observation

    matured: dict[str, Any] = {}
    pending: list[str] = []
    missing_due: list[str] = []
    for horizon, field in [("24H", "frozen_horizon_24h"), ("72H", "frozen_horizon_72h"), ("7D", "frozen_horizon_7d")]:
        due = parse_utc(row[field])
        if as_of < due:
            pending.append(horizon)
            continue
        observation = by_horizon.get(horizon)
        if observation is None:
            missing_due.append(horizon)
            continue
        matured[horizon] = {
            "due_utc": iso_z(due),
            "observed_at_utc": iso_z(parse_utc(observation["observed_at_utc"])),
            "return_pct": observation.get("return_pct"),
            "max_favorable_excursion_pct": observation.get("max_favorable_excursion_pct"),
            "max_adverse_excursion_pct": observation.get("max_adverse_excursion_pct"),
            "benchmark_return_pct": observation.get("benchmark_return_pct"),
            "source_hash": observation["source_hash"],
            "source_provider": observation.get("source_provider"),
            "data_quality": observation.get("data_quality"),
        }
    return {
        "contract": "BTC_PARTIAL_WAIT_MATURITY_RECEIPT_v1",
        "test_id": TEST_ID,
        "row_id": row.get("row_id"),
        "frozen_input_sha256": expected_hash,
        "as_of_utc": iso_z(as_of),
        "matured_horizons": matured,
        "pending_horizons": pending,
        "missing_due_horizons": missing_due,
        "maturity_complete": not pending and not missing_due and set(matured) == set(HORIZON_HOURS),
        "counts_as_outcome_row": False,
        "owner_attach_required_before_outcome_row_count": True,
        "authority": _zero_authority(),
    }


def coverage_health(expected_check_ids: list[str], receipts: list[dict[str, Any]], matured_owner_row_ids: list[str] | None = None) -> dict[str, Any]:
    expected = [str(value) for value in expected_check_ids]
    seen: dict[str, dict[str, Any]] = {}
    invalid: list[str] = []
    for receipt in receipts:
        if not isinstance(receipt, dict) or receipt.get("status") not in COVERAGE_STATUSES:
            invalid.append(str(receipt.get("check_id") if isinstance(receipt, dict) else "UNKNOWN"))
            continue
        check_id = str(receipt.get("check_id"))
        if check_id in seen:
            raise ValueError(f"duplicate_coverage_receipt:{check_id}")
        seen[check_id] = receipt
    gaps = [check_id for check_id in expected if check_id not in seen]
    no_div = sum(1 for item in seen.values() if item.get("status") == "CHECKED_NO_DIVERGENCE")
    divergences = [item for item in seen.values() if item.get("status") == "DIVERGENCE_CAPTURED"]
    blocked = sum(1 for item in seen.values() if item.get("status") == "NOT_EVALUABLE_DATA_BLOCKED")
    matured_ids = set(matured_owner_row_ids or [])
    divergence_row_ids = {
        str(item.get("divergence_source_row", {}).get("row_id"))
        for item in divergences
        if isinstance(item.get("divergence_source_row"), dict)
    }
    matured_count = len(divergence_row_ids & matured_ids)
    return {
        "contract": "BTC_PARTIAL_WAIT_COVERAGE_HEALTH_v1",
        "test_id": TEST_ID,
        "checks_total": len(seen),
        "expected_checks_total": len(expected),
        "no_divergence_checks": no_div,
        "divergence_source_rows": len(divergences),
        "matured_outcome_rows": matured_count,
        "data_blocked_checks": blocked,
        "coverage_gaps": len(gaps),
        "coverage_gap_ids": gaps,
        "invalid_receipt_ids": invalid,
        "coverage_status": "GAP" if gaps or invalid else "COMPLETE_FOR_EXPECTED_CHECK_SET",
        "coverage_receipts_are_outcome_evidence": False,
        "authority": _zero_authority(),
    }


def write_or_print(value: Any, path: Path | None) -> None:
    text = json.dumps(value, sort_keys=True, indent=2) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    else:
        print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="Observe BTC Partial vs WAIT checks without converting non-divergence or blocked checks into outcome rows.")
    sub = parser.add_subparsers(dest="command", required=True)

    observe_parser = sub.add_parser("observe")
    observe_parser.add_argument("--input", required=True, type=Path)
    observe_parser.add_argument("--output", type=Path)

    mature_parser = sub.add_parser("mature")
    mature_parser.add_argument("--receipt", required=True, type=Path)
    mature_parser.add_argument("--observations", required=True, type=Path)
    mature_parser.add_argument("--as-of-utc", required=True)
    mature_parser.add_argument("--output", type=Path)

    health_parser = sub.add_parser("coverage-health")
    health_parser.add_argument("--expected-checks", required=True, type=Path)
    health_parser.add_argument("--receipts", required=True, type=Path)
    health_parser.add_argument("--matured-owner-row-ids", type=Path)
    health_parser.add_argument("--output", type=Path)

    args = parser.parse_args()
    if args.command == "observe":
        value = observe(load_json(args.input))
    elif args.command == "mature":
        observations = load_json(args.observations)
        if not isinstance(observations, list):
            raise ValueError("observations_list_required")
        value = mature(load_json(args.receipt), observations, args.as_of_utc)
    else:
        expected = load_json(args.expected_checks)
        receipts = load_json(args.receipts)
        matured_ids = load_json(args.matured_owner_row_ids) if args.matured_owner_row_ids else []
        if not isinstance(expected, list) or not isinstance(receipts, list) or not isinstance(matured_ids, list):
            raise ValueError("coverage_inputs_must_be_lists")
        value = coverage_health(expected, receipts, matured_ids)
    write_or_print(value, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
