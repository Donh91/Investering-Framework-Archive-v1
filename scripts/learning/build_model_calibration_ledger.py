from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

UNIT_CONTRACT_VERSION = "FORECAST_TARGET_UNITS_v2"
LINEAGE_CONTRACT = "MODEL_CALIBRATION_DATA_PING_LINEAGE_v1"
ELIGIBILITY_CONTRACT = "MODEL_CALIBRATION_SETTLEMENT_ELIGIBILITY_v1"
ELIGIBILITY_SCOPE = "SETTLEMENT_TIMING_ONLY"
POPULATION_CONTRACT = "CALIBRATION_POPULATION_CONTRACT_v1"
POPULATION_CONTRACT_PATH = "research/api_agent/CALIBRATION_POPULATION_CONTRACT.json"
POPULATION_ID = "API_AGENT_RATIFIED_T13"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def load(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def path_matches_declared_population(actual: Path, declared: str) -> bool:
    declared_path = Path(declared)
    actual_parts = actual.resolve(strict=False).parts
    if declared_path.is_absolute():
        return actual_parts == declared_path.resolve(strict=False).parts
    declared_parts = declared_path.parts
    return len(actual_parts) >= len(declared_parts) and actual_parts[-len(declared_parts) :] == declared_parts


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def required_fields_present(value: dict, required_fields: list[str]) -> bool:
    return all(field in value and value[field] is not None and value[field] != "" for field in required_fields)


def fail_closed(reason: str, **details) -> None:
    print(json.dumps({"status": "BLOCKED", "reason": reason, **details}, sort_keys=True), file=sys.stderr)
    raise SystemExit(2)


def legacy_unit_ambiguous(forecast: dict) -> bool:
    if forecast.get("contract") != "FROZEN_FORECAST_v1":
        return False
    if forecast.get("unit_contract_version") == UNIT_CONTRACT_VERSION:
        return False
    if forecast.get("source_candidate_id") and forecast.get("direction") == "RANGE":
        return False
    return True


def settlement_score_eligible(outcome: dict) -> bool:
    return (
        outcome.get("status") == "MATURED"
        and outcome.get("result") in {"HIT", "MISS"}
        and outcome.get("scientific_score_eligible") is True
    )


def cohort_status(*, frozen_count: int, outcome_count: int, settlement_eligible_count: int) -> str:
    if frozen_count == 0:
        return "NO_FROZEN_RATIFIED_COHORT"
    if outcome_count == 0:
        return "COHORT_PRESENT_AWAITING_OUTCOMES"
    if settlement_eligible_count > 0:
        return "SETTLEMENT_ELIGIBLE_ROWS_PRESENT"
    return "COHORT_PRESENT_NO_SETTLEMENT_ELIGIBLE_OUTCOMES"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--forecast-root", type=Path, required=True)
    parser.add_argument("--outcome-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lineage-output", type=Path)
    parser.add_argument("--eligibility-output", type=Path)
    args = parser.parse_args()

    population_contract = load(REPOSITORY_ROOT / POPULATION_CONTRACT_PATH)
    population = (
        population_contract.get("populations", {}).get(POPULATION_ID)
        if isinstance(population_contract, dict)
        else None
    )
    if not isinstance(population, dict):
        fail_closed("POPULATION_CONTRACT_INVALID", population_id=POPULATION_ID)

    expected_forecast_root = population.get("forecast_root")
    expected_outcome_root = population.get("outcome_root")
    required_forecast_fields = population.get("required_forecast_fields")
    if (
        not isinstance(expected_forecast_root, str)
        or not isinstance(expected_outcome_root, str)
        or not isinstance(required_forecast_fields, list)
        or not all(isinstance(field, str) and field for field in required_forecast_fields)
    ):
        fail_closed("POPULATION_CONTRACT_INVALID", population_id=POPULATION_ID)
    forecast_root_matches = path_matches_declared_population(args.forecast_root, expected_forecast_root)
    outcome_root_matches = path_matches_declared_population(args.outcome_root, expected_outcome_root)
    strict_population_roots = forecast_root_matches and outcome_root_matches
    registered_other_roots = {
        value.get(key)
        for population_id, value in population_contract.get("populations", {}).items()
        if population_id != POPULATION_ID and isinstance(value, dict)
        for key in ("forecast_root", "outcome_root")
        if isinstance(value.get(key), str)
    }
    matches_other_population = any(
        path_matches_declared_population(actual, declared)
        for actual in (args.forecast_root, args.outcome_root)
        for declared in registered_other_roots
    )
    noncanonical_fixture = (
        not matches_other_population
        and not path_is_within(args.forecast_root, REPOSITORY_ROOT)
        and not path_is_within(args.outcome_root, REPOSITORY_ROOT)
        and not path_is_within(args.output, REPOSITORY_ROOT)
    )
    if not strict_population_roots and not noncanonical_fixture:
        fail_closed(
            "POPULATION_ROOT_MISMATCH",
            population_id=POPULATION_ID,
            expected_forecast_root=expected_forecast_root,
            expected_outcome_root=expected_outcome_root,
            supplied_forecast_root=str(args.forecast_root),
            supplied_outcome_root=str(args.outcome_root),
        )

    forecasts = {}
    invalid_frozen_forecast_count = 0
    for path in args.forecast_root.rglob("*.json") if args.forecast_root.exists() else []:
        value = load(path)
        if value and value.get("contract") == "FROZEN_FORECAST_v1":
            if strict_population_roots and not required_fields_present(value, required_forecast_fields):
                invalid_frozen_forecast_count += 1
                continue
            forecasts[value.get("forecast_id")] = value

    rows = []
    lineage_rows = []
    eligibility_rows = []
    quarantined = set()
    orphan_outcome_count = 0

    for path in args.outcome_root.rglob("*.json") if args.outcome_root.exists() else []:
        outcome = load(path)
        if not outcome or outcome.get("contract") not in {"MATURED_OUTCOME_v2", "MATURED_OUTCOME_v3"}:
            continue
        forecast = forecasts.get(outcome.get("forecast_id"))
        if not forecast:
            orphan_outcome_count += 1
            continue
        if legacy_unit_ambiguous(forecast):
            quarantined.add(outcome.get("forecast_id"))
            continue

        rows.append(
            {
                "scored_at_utc": outcome.get("created_at_utc"),
                "model": forecast.get("model"),
                "task": forecast.get("task"),
                "prompt_sha256": forecast.get("prompt_sha256"),
                "forecast_id": outcome.get("forecast_id"),
                "metric_path": forecast.get("metric_path"),
                "horizon_days": forecast.get("horizon_days"),
                "outcome": outcome.get("status"),
                "result": outcome.get("result"),
                "hit": 1 if outcome.get("result") == "HIT" else (0 if outcome.get("result") == "MISS" else ""),
                "return_pct": outcome.get("return_pct"),
                "forecast_sha256": outcome.get("forecast_sha256"),
                "evidence_sha256": outcome.get("evidence_sha256"),
            }
        )

        eligible = settlement_score_eligible(outcome)
        eligibility_rows.append(
            {
                "forecast_id": outcome.get("forecast_id"),
                "outcome_contract": outcome.get("contract"),
                "outcome_status": outcome.get("status"),
                "result": outcome.get("result"),
                "settlement_contract_version": outcome.get("settlement_contract_version") or "UNDECLARED_LEGACY",
                "settlement_target_utc": outcome.get("settlement_target_utc"),
                "settlement_observation_utc": outcome.get("settlement_observation_utc"),
                "settlement_offset_seconds": outcome.get("settlement_offset_seconds"),
                "scientific_score_eligible": eligible,
                "settlement_score_eligible": eligible,
                "eligibility_scope": ELIGIBILITY_SCOPE,
                "scientific_skill_eligible": False,
                "scientific_score_exclusion_reason": None
                if eligible
                else (
                    outcome.get("scientific_score_exclusion_reason")
                    or "LEGACY_OUTCOME_WITHOUT_EXPLICIT_SETTLEMENT_ELIGIBILITY"
                ),
                "forecast_sha256": outcome.get("forecast_sha256"),
                "evidence_sha256": outcome.get("evidence_sha256"),
            }
        )

        lineage = forecast.get("data_ping_lineage") if isinstance(forecast.get("data_ping_lineage"), dict) else None
        if lineage:
            lineage_rows.append(
                {
                    "contract": LINEAGE_CONTRACT,
                    "scored_at_utc": outcome.get("created_at_utc"),
                    "forecast_id": outcome.get("forecast_id"),
                    "forecast_sha256": outcome.get("forecast_sha256"),
                    "accepted_packet_sha256": lineage.get("accepted_packet_sha256"),
                    "accepted_packet_identity": lineage.get("accepted_packet_identity"),
                    "accepted_packet_path": lineage.get("accepted_packet_path"),
                    "action_compass_receipt_id": lineage.get("action_compass_receipt_id"),
                    "action_compass_receipt_sha256": lineage.get("action_compass_receipt_sha256"),
                    "canonical_repository": lineage.get("canonical_repository"),
                    "canonical_commit_sha": lineage.get("canonical_commit_sha"),
                    "owner_contract": lineage.get("owner_contract"),
                    "portfolio_execution": False,
                }
            )

    rows.sort(key=lambda row: (str(row["scored_at_utc"]), str(row["forecast_id"])))
    lineage_rows.sort(key=lambda row: (str(row["scored_at_utc"]), str(row["forecast_id"])))
    eligibility_rows.sort(key=lambda row: str(row["forecast_id"]))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "scored_at_utc",
        "model",
        "task",
        "prompt_sha256",
        "forecast_id",
        "metric_path",
        "horizon_days",
        "outcome",
        "result",
        "hit",
        "return_pct",
        "forecast_sha256",
        "evidence_sha256",
    ]
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lineage_output = args.lineage_output or args.output.with_name(args.output.stem + "_DATA_PING_LINEAGE.jsonl")
    if lineage_rows:
        lineage_output.parent.mkdir(parents=True, exist_ok=True)
        lineage_output.write_text("".join(canon(row) + "\n" for row in lineage_rows))
    elif lineage_output.exists():
        lineage_output.unlink()

    settlement_eligible_count = sum(1 for row in eligibility_rows if row["settlement_score_eligible"] is True)
    matured_unscorable_count = sum(
        1
        for row in eligibility_rows
        if row["outcome_status"] == "MATURED" and row["settlement_score_eligible"] is not True
    )
    pending_root = args.forecast_root.parent / "PENDING"
    candidate_count = sum(1 for _ in pending_root.rglob("*.json")) if pending_root.exists() else 0
    frozen_count = len(forecasts)
    outcome_count = len(eligibility_rows)
    population_state = cohort_status(
        frozen_count=frozen_count,
        outcome_count=outcome_count,
        settlement_eligible_count=settlement_eligible_count,
    )

    eligibility_output = args.eligibility_output or args.output.with_name("MODEL_CALIBRATION_SETTLEMENT_ELIGIBILITY.json")
    eligibility_output.parent.mkdir(parents=True, exist_ok=True)
    eligibility_doc = {
        "contract": ELIGIBILITY_CONTRACT,
        "population_contract": POPULATION_CONTRACT,
        "population_contract_path": POPULATION_CONTRACT_PATH,
        "population_id": POPULATION_ID,
        "cohort_status": population_state,
        "forecast_root": str(args.forecast_root),
        "outcome_root": str(args.outcome_root),
        "forecast_root_exists": args.forecast_root.exists(),
        "outcome_root_exists": args.outcome_root.exists(),
        "candidate_count": candidate_count,
        "frozen_count": frozen_count,
        "outcome_record_count": outcome_count,
        "invalid_frozen_forecast_count": invalid_frozen_forecast_count,
        "orphan_outcome_count": orphan_outcome_count,
        "direct_framework_memory_import_allowed": False,
        "historical_schema_backfill_by_inference_allowed": False,
        "eligibility_scope": ELIGIBILITY_SCOPE,
        "legacy_calibration_csv_path": str(args.output),
        "legacy_calibration_csv_role": "DESCRIPTIVE_BACKWARD_COMPATIBILITY_ONLY",
        "settlement_eligibility_status": population_state,
        "scientific_skill_status": "NOT_ASSESSED_SETTLEMENT_TIMING_ONLY",
        "scientific_skill_authority": False,
        "scientific_scored_count": settlement_eligible_count,
        "settlement_eligible_count": settlement_eligible_count,
        "matured_unscorable_count": matured_unscorable_count,
        "row_count": len(eligibility_rows),
        "rows": eligibility_rows,
        "authority": {
            "model_weight_change": False,
            "portfolio_action": False,
            "automatic_promotion": False,
            "forecast_skill_claim": False,
            "automatic_path_repoint": False,
        },
    }
    eligibility_output.write_text(json.dumps(eligibility_doc, indent=2, sort_keys=True) + "\n")

    scored_count = sum(1 for row in rows if row["outcome"] == "MATURED")
    censored_count = sum(1 for row in rows if row["outcome"] == "CENSORED")
    print(
        json.dumps(
            {
                "status": "PASS",
                "population_id": POPULATION_ID,
                "cohort_status": population_state,
                "scored_count": scored_count,
                "scientific_scored_count": settlement_eligible_count,
                "settlement_eligible_count": settlement_eligible_count,
                "scientific_skill_status": "NOT_ASSESSED_SETTLEMENT_TIMING_ONLY",
                "matured_unscorable_count": matured_unscorable_count,
                "censored_count": censored_count,
                "ledger_row_count": len(rows),
                "settlement_eligibility_output": str(eligibility_output),
                "data_ping_lineage_row_count": len(lineage_rows),
                "data_ping_lineage_output": str(lineage_output) if lineage_rows else None,
                "quarantined_legacy_unit_outcome_count": len(quarantined),
                "candidate_count": candidate_count,
                "frozen_count": frozen_count,
                "outcome_record_count": outcome_count,
                "invalid_frozen_forecast_count": invalid_frozen_forecast_count,
                "orphan_outcome_count": orphan_outcome_count,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
