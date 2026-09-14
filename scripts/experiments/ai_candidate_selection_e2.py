#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_compiler_reliability_e2 as parent  # noqa: E402

base = parent.base
hourly = parent.hourly
handoff = parent.handoff
AUTHORITY = dict(parent.AUTHORITY)

REQUEST_CONTRACT = "AUTO_TRADING_E2_CANDIDATE_SELECTION_REQUEST_v1"
RESULT_CONTRACT = "AUTO_TRADING_E2_CANDIDATE_SELECTION_RESULT_v1"
EXPERIMENT_ID = "AT-E2-CANDIDATE-SELECTION-v3"
ISSUE = 966
PARENT_EXPERIMENT_ID = "AT-E2-COMPILER-RELIABILITY-v2"
PARENT_RESULT_SHA256 = "9bbd4ff624f4b82cb7fff946fc72c1237683b6fbc31e82aa8710d93c7bbc399c"
CANDIDATE_SET_SHA256 = "defbe64b0cdb02133b1cbfda79010de94f2872db0af0d581e71f42dd193cc731"

FIXED_CANDIDATES: list[dict[str, str]] = [
    {"candidate_id": "C01", "feature": "ret1_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"},
    {"candidate_id": "C02", "feature": "ret1_pct", "long_trigger": "GT_Q50", "short_trigger": "LT_Q50"},
    {"candidate_id": "C03", "feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"},
    {"candidate_id": "C04", "feature": "ret4_pct", "long_trigger": "GT_Q50", "short_trigger": "LT_Q50"},
    {"candidate_id": "C05", "feature": "ret12_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"},
    {"candidate_id": "C06", "feature": "ret12_pct", "long_trigger": "GT_Q50", "short_trigger": "LT_Q50"},
    {"candidate_id": "C07", "feature": "cross_ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"},
    {"candidate_id": "C08", "feature": "cross_ret4_pct", "long_trigger": "GT_Q50", "short_trigger": "LT_Q50"},
    {"candidate_id": "C09", "feature": "vol6_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"},
    {"candidate_id": "C10", "feature": "vol6_pct", "long_trigger": "GT_Q50", "short_trigger": "LT_Q50"},
]


def candidate_map(candidates: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["candidate_id"]: row for row in candidates}


def selection_schema(candidates: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["candidate_id"],
        "properties": {
            "candidate_id": {
                "type": "string",
                "enum": [row["candidate_id"] for row in candidates],
            }
        },
    }


def _rule_only(candidate: dict[str, str]) -> dict[str, str]:
    return {key: candidate[key] for key in ("feature", "long_trigger", "short_trigger")}


def validate_candidates(candidates: Any) -> list[dict[str, str]]:
    if candidates != FIXED_CANDIDATES:
        raise ValueError("candidate_set_differs_from_preregistered_v3")
    if base.sha(candidates) != CANDIDATE_SET_SHA256:
        raise ValueError("candidate_set_hash_mismatch")
    ids: set[str] = set()
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or candidate_id in ids:
            raise ValueError("candidate_id_invalid_or_duplicate")
        ids.add(candidate_id)
        if parent.replayable_rule(_rule_only(candidate)) is None:
            raise ValueError(f"candidate_not_replayable:{candidate_id}")
    if len(candidates) != 10:
        raise ValueError("candidate_count_must_equal_ten")
    return candidates


def validate_request(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("contract") != REQUEST_CONTRACT:
        raise ValueError("invalid_request_contract")
    if raw.get("status") != "APPROVED_RESEARCH_ONLY" or raw.get("issue") != ISSUE:
        raise ValueError("request_not_approved_for_issue_966")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("experiment_id_mismatch")
    if raw.get("parent_experiment_id") != PARENT_EXPERIMENT_ID:
        raise ValueError("parent_experiment_binding_required")
    if raw.get("parent_result_sha256") != PARENT_RESULT_SHA256:
        raise ValueError("parent_result_binding_mismatch")
    if raw.get("model") != "gpt-5.6-luna" or raw.get("reasoning_effort") != "medium":
        raise ValueError("frozen_model_effort_mismatch")
    if raw.get("selection_repeats") != 10:
        raise ValueError("selection_repeats_must_equal_ten")
    if raw.get("selection_max_output_tokens") != 200:
        raise ValueError("selection_token_headroom_must_equal_200")
    if raw.get("consumed_columns") != sorted(hourly.CANONICAL_RAW_COLUMNS):
        raise ValueError("raw_column_firewall_mismatch")
    if raw.get("candidate_set_sha256") != CANDIDATE_SET_SHA256:
        raise ValueError("frozen_candidate_set_hash_required")
    validate_candidates(raw.get("candidate_set"))
    for key in ("design_rows", "evaluation_points", "evaluation_stride_hours"):
        if not isinstance(raw.get(key), int) or int(raw[key]) <= 0:
            raise ValueError(f"invalid_request_field:{key}")
    hard_stop = float(raw.get("hard_cost_stop_usd") or 0.0)
    if hard_stop <= 0 or hard_stop > 0.05:
        raise ValueError("invalid_hard_cost_stop")
    if sorted(raw.get("theory_ids") or []) != ["AT-HYP-0004", "AT-HYP-0008"]:
        raise ValueError("theory_binding_required")
    for key in (
        "evaluation_outcomes_hidden_from_ai",
        "failed_and_abandoned_attempts_remain_counted",
        "no_post_result_prompt_tuning",
        "no_retroactive_rescore",
        "identical_primary_payload_required",
        "modal_candidate_may_only_seed_new_preregistered_successor",
    ):
        if raw.get(key) is not True:
            raise ValueError(f"required_true:{key}")
    if raw.get("economic_scoring_enabled") is not False or raw.get("direct_policy_arm_enabled") is not False:
        raise ValueError("selection_phase_must_exclude_economics_and_direct_policy")
    if raw.get("authority") != AUTHORITY:
        raise ValueError("research_only_authority_required")
    if raw.get("pre_registered_thresholds") != {
        "structured_selection_success_rate": 0.9,
        "candidate_admission_rate": 0.9,
        "modal_candidate_share": 0.7,
    }:
        raise ValueError("preregistered_thresholds_mismatch")
    return raw


def structured_selection(value: Any, candidates: list[dict[str, str]]) -> str | None:
    if not isinstance(value, dict) or set(value) != {"candidate_id"}:
        return None
    candidate_id = value.get("candidate_id")
    if candidate_id not in candidate_map(candidates):
        return None
    return str(candidate_id)


def failure_class(record: dict[str, Any], selected_id: str | None) -> str | None:
    error = str(record.get("error") or "")
    if error.startswith("openai_http_"):
        return "HTTP_API_FAILURE"
    if "missing_output_text" in error:
        return "MISSING_OUTPUT_TEXT"
    if "JSONDecodeError" in error:
        return "MALFORMED_JSON"
    if error:
        return "OUTPUT_OR_API_FAILURE"
    if selected_id is None:
        return "STRICT_SELECTION_SCHEMA_INVALID"
    return None


def fake_live_call(_api_key: str, payload: dict[str, Any], _model: str) -> dict[str, Any]:
    output = {"candidate_id": "C03"}
    return {
        "request_hash": base.sha(payload),
        "response_id": "dry-run",
        "output": output,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "error": None,
        "response_hash": base.sha(output),
    }


def _entropy_bits(counts: Counter[str], total: int) -> float:
    if total <= 0:
        return 0.0
    value = 0.0
    for count in counts.values():
        p = count / total
        value -= p * math.log2(p)
    return round(value, 6)


def evaluate_records(
    records: list[dict[str, Any]],
    *,
    request: dict[str, Any],
    design_summary: dict[str, Any],
    capability: dict[str, Any],
) -> dict[str, Any]:
    repeats = int(request["selection_repeats"])
    if len(records) != repeats:
        raise ValueError("selection_record_count_mismatch")
    candidates = validate_candidates(request["candidate_set"])
    by_id = candidate_map(candidates)

    structured_count = 0
    admitted_count = 0
    taxonomy: Counter[str] = Counter()
    selection_counts: Counter[str] = Counter()
    handoffs: list[dict[str, Any] | None] = []
    enriched: list[dict[str, Any]] = []
    mission_lock = {
        "experiment_id": request["experiment_id"],
        "issue": ISSUE,
        "request_sha256": base.sha(request),
        "phase": "DETERMINISTIC_CANDIDATE_SELECTION_ONLY",
        "candidate_set_sha256": CANDIDATE_SET_SHA256,
    }

    for repeat, record in enumerate(records, start=1):
        selected_id = structured_selection(record.get("output"), candidates)
        structured_count += int(selected_id is not None)
        selected_candidate = by_id.get(selected_id) if selected_id else None
        admitted = selected_candidate is not None and parent.replayable_rule(_rule_only(selected_candidate)) is not None
        admitted_count += int(admitted)
        if admitted and selected_id:
            selection_counts[selected_id] += 1
        contract = None
        if admitted and selected_candidate is not None:
            selected_artifact = {
                "candidate_id": selected_candidate["candidate_id"],
                "rule": _rule_only(selected_candidate),
            }
            contract = handoff.build_contract(
                stage_id=f"E2_V3_SELECTION_RUN_{repeat}",
                mission=mission_lock,
                input_artifact={"design_summary": design_summary, "candidate_set": candidates},
                capability_snapshot=capability,
                output_artifact=selected_artifact,
                repair_scope=f"E2_V3_SELECTION_RUN_{repeat}",
                owner_candidate_id=request["experiment_id"],
                created_at=request["frozen_at_utc"],
            )
            handoff.assert_downstream_input(contract, selected_artifact)
        handoffs.append(contract)
        failure = failure_class(record, selected_id)
        if failure:
            taxonomy[failure] += 1
        enriched.append({
            **record,
            "structured_selection_valid": selected_id is not None,
            "candidate_admitted": admitted,
            "selected_candidate_id": selected_id,
            "selected_candidate": selected_candidate,
            "failure_class": failure,
            "handoff_id": contract.get("handoff_id") if contract else None,
        })

    modal_id, modal_count = selection_counts.most_common(1)[0] if selection_counts else (None, 0)
    modal_candidate = by_id.get(modal_id) if modal_id else None
    request_hashes = [str(record.get("request_hash") or "") for record in records]
    payload_hash_stable = len(set(request_hashes)) == 1 and bool(request_hashes[0])
    capability_snapshot = handoff.normalize_capabilities(capability)
    capability_hashes = [
        contract["capability_snapshot"]["snapshot_sha256"]
        for contract in handoffs
        if contract is not None
    ]
    capability_stable = all(value == capability_snapshot["snapshot_sha256"] for value in capability_hashes)

    structured_rate = structured_count / repeats
    admission_rate = admitted_count / repeats
    modal_share = modal_count / repeats
    thresholds = request["pre_registered_thresholds"]
    gates = {
        "structured_selection_success": structured_rate >= float(thresholds["structured_selection_success_rate"]),
        "candidate_admission": admission_rate >= float(thresholds["candidate_admission_rate"]),
        "modal_candidate_convergence": modal_share >= float(thresholds["modal_candidate_share"]),
        "candidate_set_hash_frozen": base.sha(candidates) == CANDIDATE_SET_SHA256,
        "identical_primary_payload": payload_hash_stable,
        "capability_snapshot_stable": capability_stable,
    }
    supported = all(gates.values())
    return {
        "records": enriched,
        "structured_selection_success_rate": round(structured_rate, 6),
        "candidate_admission_rate": round(admission_rate, 6),
        "modal_candidate_share": round(modal_share, 6),
        "modal_candidate_id": modal_id,
        "modal_candidate": modal_candidate,
        "selection_counts": dict(sorted(selection_counts.items())),
        "selection_entropy_bits": _entropy_bits(selection_counts, admitted_count),
        "failed_call_count": sum(taxonomy.values()),
        "failure_taxonomy": dict(sorted(taxonomy.items())),
        "request_hash": request_hashes[0] if payload_hash_stable else None,
        "capability_snapshot_sha256": capability_snapshot["snapshot_sha256"],
        "candidate_set_sha256": base.sha(candidates),
        "gates": gates,
        "conclusion": (
            "CANDIDATE_SELECTION_CONVERGENCE_SUPPORTED_FOR_ECONOMIC_SUCCESSOR"
            if supported
            else "CANDIDATE_SELECTION_CONVERGENCE_NOT_SUPPORTED"
        ),
        "economic_successor_eligible": supported,
    }


def run_trial(
    request: dict[str, Any],
    repo_root: Path,
    output_dir: Path,
    *,
    dry_run: bool = False,
    call_impl: Callable[[str, dict[str, Any], str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    request = validate_request(request)
    candidates = validate_candidates(request["candidate_set"])
    rows, source_hashes = hourly.load_raw_close_rows(repo_root / request["source_root"], request["cutoff_utc"])
    design_summary, hidden_points = base.build_frozen_sample(rows, request)
    if not hidden_points:
        raise ValueError("frozen_sample_missing_hidden_points")

    schema = selection_schema(candidates)
    envelope = {
        "contract": "AUTO_TRADING_E2_CANDIDATE_SELECTION_BLINDED_INPUT_v1",
        "mode": "DETERMINISTIC_CANDIDATE_SELECTION",
        "mission": "Select exactly one candidate rule best supported by the frozen design evidence. Return only candidate_id. This phase measures selection convergence, not economic performance.",
        "design_summary": design_summary,
        "candidate_set_sha256": CANDIDATE_SET_SHA256,
        "candidate_set": candidates,
        "evaluation_outcomes_hidden": True,
        "economic_scoring_enabled": False,
        "direct_policy_arm_enabled": False,
    }
    if "_evaluation_label" in json.dumps(envelope):
        raise ValueError("evaluation_label_leak")

    payload = base.build_payload(
        request["model"],
        request["reasoning_effort"],
        "e2_candidate_selection_v3",
        schema,
        envelope,
        int(request["selection_max_output_tokens"]),
    )
    capability = {
        "tools": ["openai.responses", "deterministic_candidate_validation", "agent_handoff_contract"],
        "schemas": {
            "selection_output": base.sha(schema),
            "candidate_set": CANDIDATE_SET_SHA256,
        },
        "runtime": "AUTO_TRADING_E2_CANDIDATE_SELECTION_v3",
    }

    if call_impl is None:
        call_impl = fake_live_call if dry_run else base.live_call
    api_key = "dry-run" if dry_run else str(os.environ.get("OPENAI_API_KEY") or "")
    if not dry_run and not api_key:
        raise SystemExit("OPENAI_API_KEY_missing")

    total_cost = 0.0
    records: list[dict[str, Any]] = []
    for repeat in range(1, int(request["selection_repeats"]) + 1):
        record = call_impl(api_key, payload, request["model"])
        total_cost += float(record.get("cost_usd") or 0.0)
        records.append({"arm": "AI_CANDIDATE_SELECTION", "repeat": repeat, **record})
        if total_cost > float(request["hard_cost_stop_usd"]):
            raise RuntimeError(f"e2_v3_cost_hard_stop:{total_cost:.8f}")

    evaluated = evaluate_records(records, request=request, design_summary=design_summary, capability=capability)
    result = {
        "contract": RESULT_CONTRACT,
        "status": "COMPLETE",
        "issue": ISSUE,
        "experiment_id": request["experiment_id"],
        "parent_experiment_id": request["parent_experiment_id"],
        "parent_result_sha256": request["parent_result_sha256"],
        "request_sha256": base.sha(request),
        "candidate_set_sha256": CANDIDATE_SET_SHA256,
        "source_hashes": source_hashes,
        "sample": {
            "design_rows": request["design_rows"],
            "design_window": {
                "first_design_timestamp": design_summary["window"]["first_design_timestamp"],
                "last_design_timestamp": design_summary["window"]["last_design_timestamp"],
            },
            "evaluation_outcomes_hidden_from_ai": True,
        },
        "api": {
            "model": request["model"],
            "reasoning_effort": request["reasoning_effort"],
            "selection_calls": request["selection_repeats"],
            "failed_calls": evaluated["failed_call_count"],
            "total_cost_usd": round(total_cost, 8),
            "hard_cost_stop_usd": request["hard_cost_stop_usd"],
            "selection_max_output_tokens": request["selection_max_output_tokens"],
        },
        "selection": {
            key: evaluated[key]
            for key in (
                "structured_selection_success_rate",
                "candidate_admission_rate",
                "modal_candidate_share",
                "modal_candidate_id",
                "modal_candidate",
                "selection_counts",
                "selection_entropy_bits",
                "failure_taxonomy",
                "request_hash",
                "capability_snapshot_sha256",
                "candidate_set_sha256",
                "gates",
            )
        },
        "conclusion": evaluated["conclusion"],
        "economic_successor_eligible": evaluated["economic_successor_eligible"],
        "economic_scoring_performed": False,
        "direct_policy_arm_performed": False,
        "capital_ready": False,
        "no_post_result_prompt_tuning": True,
        "no_retroactive_rescore": True,
        "authority": dict(AUTHORITY),
    }
    result["result_sha256"] = base.sha(result)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_bytes(base.canon(result))
    (output_dir / "design_summary.json").write_bytes(base.canon(design_summary))
    (output_dir / "candidate_set.json").write_bytes(base.canon(candidates))
    with (output_dir / "calls.jsonl").open("w", encoding="utf-8") as handle:
        for record in evaluated["records"]:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run preregistered E2 v3 deterministic candidate-selection convergence gate.")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    result = run_trial(request, args.repo_root, args.output_dir, dry_run=args.dry_run)
    print(json.dumps({
        "experiment_id": result["experiment_id"],
        "status": result["status"],
        "conclusion": result["conclusion"],
        "structured_selection_success_rate": result["selection"]["structured_selection_success_rate"],
        "candidate_admission_rate": result["selection"]["candidate_admission_rate"],
        "modal_candidate_share": result["selection"]["modal_candidate_share"],
        "modal_candidate_id": result["selection"]["modal_candidate_id"],
        "selection_entropy_bits": result["selection"]["selection_entropy_bits"],
        "total_cost_usd": result["api"]["total_cost_usd"],
        "result_sha256": result["result_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
