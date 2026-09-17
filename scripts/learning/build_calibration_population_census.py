from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CONTRACT = "CALIBRATION_POPULATION_CENSUS_v1"
FORECAST_CONTRACT = "FROZEN_FORECAST_v1"
OUTCOME_CONTRACTS = {"MATURED_OUTCOME_v2", "MATURED_OUTCOME_v3"}
REQUIRED_FORECAST_FIELDS = ("model", "task", "horizon_days", "metric_path", "prompt_sha256")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def collect_docs(root: Path, contracts: set[str]) -> tuple[list[tuple[Path, dict]], list[str]]:
    docs: list[tuple[Path, dict]] = []
    errors: list[str] = []
    if not root.exists():
        return docs, errors
    for path in sorted(root.rglob("*.json")):
        try:
            value = load_json(path)
        except Exception as exc:  # diagnostic surface: record, never silently skip
            errors.append(f"{path}:{type(exc).__name__}")
            continue
        if isinstance(value, dict) and value.get("contract") in contracts:
            docs.append((path, value))
    return docs, errors


def evidence_class(repo_root: Path, outcome: dict) -> str:
    raw = outcome.get("evidence_path")
    if not raw:
        return "MISSING"
    path = Path(str(raw))
    if path.is_absolute():
        if str(path).startswith("/tmp/"):
            return "ABSOLUTE_TMP_EPHEMERAL"
        return "ABSOLUTE_OTHER"
    candidate = repo_root / path
    return "REPO_RELATIVE_RESOLVABLE" if candidate.exists() else "REPO_RELATIVE_MISSING"


def summarize_population(
    repo_root: Path,
    population_id: str,
    forecast_root: Path,
    outcome_root: Path,
    replay_root: Path | None = None,
) -> dict:
    forecast_docs, forecast_errors = collect_docs(forecast_root, {FORECAST_CONTRACT})
    outcome_docs, outcome_errors = collect_docs(outcome_root, OUTCOME_CONTRACTS)
    replay_docs: list[tuple[Path, dict]] = []
    replay_errors: list[str] = []
    if replay_root is not None:
        replay_docs, replay_errors = collect_docs(replay_root, OUTCOME_CONTRACTS)

    forecast_ids = [str(v.get("forecast_id")) for _, v in forecast_docs if v.get("forecast_id")]
    outcome_ids = [str(v.get("forecast_id")) for _, v in outcome_docs if v.get("forecast_id")]
    replay_ids = [str(v.get("forecast_id")) for _, v in replay_docs if v.get("forecast_id")]

    forecast_id_counts = Counter(forecast_ids)
    outcome_id_counts = Counter(outcome_ids)
    forecast_id_set = set(forecast_ids)
    outcome_id_set = set(outcome_ids)

    field_completeness = {}
    for field in REQUIRED_FORECAST_FIELDS:
        present = sum(1 for _, value in forecast_docs if value.get(field) not in (None, ""))
        field_completeness[field] = {
            "present": present,
            "missing": len(forecast_docs) - present,
            "coverage": round(present / len(forecast_docs), 6) if forecast_docs else None,
        }

    evidence_counts = Counter(evidence_class(repo_root, value) for _, value in outcome_docs)
    result_counts = Counter(str(value.get("result")) for _, value in outcome_docs)
    status_counts = Counter(str(value.get("status")) for _, value in outcome_docs)
    contract_counts = Counter(str(value.get("contract")) for _, value in outcome_docs)

    score_eligible = sum(1 for _, value in outcome_docs if value.get("scientific_score_eligible") is True)
    matured = sum(1 for _, value in outcome_docs if value.get("status") == "MATURED")

    return {
        "population_id": population_id,
        "forecast_root": str(forecast_root.relative_to(repo_root)),
        "outcome_root": str(outcome_root.relative_to(repo_root)),
        "replay_root": str(replay_root.relative_to(repo_root)) if replay_root is not None else None,
        "forecast_root_exists": forecast_root.exists(),
        "outcome_root_exists": outcome_root.exists(),
        "replay_root_exists": replay_root.exists() if replay_root is not None else None,
        "forecast_file_count": len(forecast_docs),
        "unique_forecast_id_count": len(forecast_id_set),
        "duplicate_forecast_id_count": sum(1 for count in forecast_id_counts.values() if count > 1),
        "outcome_file_count": len(outcome_docs),
        "unique_outcome_forecast_id_count": len(outcome_id_set),
        "duplicate_outcome_forecast_id_count": sum(1 for count in outcome_id_counts.values() if count > 1),
        "matured_outcome_count": matured,
        "scientific_score_eligible_count": score_eligible,
        "outcome_status_counts": dict(sorted(status_counts.items())),
        "outcome_result_counts": dict(sorted(result_counts.items())),
        "outcome_contract_counts": dict(sorted(contract_counts.items())),
        "forecast_field_completeness": field_completeness,
        "joinable_outcome_count": len(outcome_id_set & forecast_id_set),
        "orphan_outcome_forecast_id_count": len(outcome_id_set - forecast_id_set),
        "forecast_without_outcome_count": len(forecast_id_set - outcome_id_set),
        "evidence_path_classes": dict(sorted(evidence_counts.items())),
        "replay_outcome_file_count": len(replay_docs),
        "replay_unique_forecast_id_count": len(set(replay_ids)),
        "replay_overlap_with_primary_outcome_count": len(set(replay_ids) & outcome_id_set),
        "parse_errors": sorted(forecast_errors + outcome_errors + replay_errors),
        "forecast_ids": sorted(forecast_id_set),
        "outcome_forecast_ids": sorted(outcome_id_set),
    }


def build_census(repo_root: Path) -> dict:
    repo_root = repo_root.resolve()
    api = summarize_population(
        repo_root,
        "API_AGENT_RATIFIED_T13",
        repo_root / "research/api_agent/forecast_candidates/FROZEN",
        repo_root / "research/api_agent/forecast_candidates/MATURED",
    )
    memory = summarize_population(
        repo_root,
        "FRAMEWORK_MEMORY_BROAD",
        repo_root / "research/framework_memory/forecast_memory",
        repo_root / "research/framework_memory/outcome_memory",
        repo_root / "research/framework_memory/outcome_replays",
    )

    api_forecasts = set(api.pop("forecast_ids"))
    api_outcomes = set(api.pop("outcome_forecast_ids"))
    memory_forecasts = set(memory.pop("forecast_ids"))
    memory_outcomes = set(memory.pop("outcome_forecast_ids"))
    parse_error_count = len(api["parse_errors"]) + len(memory["parse_errors"])

    return {
        "contract": CONTRACT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authority": {
            "market_state_change": False,
            "model_weight_change": False,
            "portfolio_action": False,
            "calibration_owner_change": False,
            "automatic_path_repoint": False,
        },
        "purpose": "READ_ONLY_DIAGNOSTIC_BEFORE_CALIBRATION_OWNERSHIP_DECISION",
        "status": "WARN_PARSE_ERRORS" if parse_error_count else "PASS",
        "populations": [api, memory],
        "cross_population": {
            "forecast_id_overlap_count": len(api_forecasts & memory_forecasts),
            "outcome_forecast_id_overlap_count": len(api_outcomes & memory_outcomes),
            "api_only_forecast_id_count": len(api_forecasts - memory_forecasts),
            "framework_memory_only_forecast_id_count": len(memory_forecasts - api_forecasts),
        },
        "decision_guardrail": "DO_NOT_REPOINT_CALIBRATION_PATHS_FROM_THIS_CENSUS_ALONE",
        "next_required_decision": "DEFINE_POPULATION_OWNERSHIP_AND_COHORT_SEMANTICS_BEFORE_CANONICAL_LEDGER_CHANGE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    census = build_census(args.repo_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(census, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": census["status"],
        "contract": census["contract"],
        "output": str(args.output),
        "populations": {
            row["population_id"]: {
                "forecasts": row["forecast_file_count"],
                "outcomes": row["outcome_file_count"],
                "score_eligible": row["scientific_score_eligible_count"],
            }
            for row in census["populations"]
        },
        "cross_population": census["cross_population"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
