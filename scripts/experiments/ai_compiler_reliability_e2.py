#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent_handoff_contract as handoff  # noqa: E402
import ai_compiler_vs_policy_e2_hourly_adapter as hourly  # noqa: E402

base = hourly.base

REQUEST_CONTRACT = "AUTO_TRADING_E2_COMPILER_RELIABILITY_REQUEST_v1"
RESULT_CONTRACT = "AUTO_TRADING_E2_COMPILER_RELIABILITY_RESULT_v1"
EXPERIMENT_ID = "AT-E2-COMPILER-RELIABILITY-v2"
ISSUE = 962
REQUIRED_OUTPUT_FIELDS = {"feature", "long_trigger", "short_trigger"}
AUTHORITY = {
    "automatic_promotion": False,
    "canonical_effect": False,
    "exchange_signing": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "order_routing": False,
    "portfolio_execution": False,
    "threshold_change": False,
}


def compiler_schema_v2() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(REQUIRED_OUTPUT_FIELDS),
        "properties": {
            "feature": {"type": "string", "enum": sorted(base.FEATURES)},
            "long_trigger": {"type": "string", "enum": ["GT_Q75", "GT_Q50", "DISABLED"]},
            "short_trigger": {"type": "string", "enum": ["LT_Q25", "LT_Q50", "DISABLED"]},
        },
    }


def validate_request(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("contract") != REQUEST_CONTRACT:
        raise ValueError("invalid_request_contract")
    if raw.get("status") != "APPROVED_RESEARCH_ONLY" or raw.get("issue") != ISSUE:
        raise ValueError("request_not_approved_for_issue_962")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("experiment_id_mismatch")
    if raw.get("parent_experiment_id") != "AT-E2-911-v1":
        raise ValueError("parent_experiment_binding_required")
    if raw.get("parent_result_sha256") != "53ad7e6b56a9ed24df2ca2285090c8d0967b3836d85a28f2c9e6779628a24168":
        raise ValueError("parent_result_binding_mismatch")
    if raw.get("model") != "gpt-5.6-luna" or raw.get("reasoning_effort") != "medium":
        raise ValueError("frozen_model_effort_mismatch")
    if raw.get("compiler_repeats") != 10:
        raise ValueError("compiler_repeats_must_equal_ten")
    if raw.get("compiler_max_output_tokens") != 1000:
        raise ValueError("compiler_token_headroom_must_equal_1000")
    if raw.get("consumed_columns") != sorted(hourly.CANONICAL_RAW_COLUMNS):
        raise ValueError("raw_column_firewall_mismatch")
    for key in ("design_rows", "evaluation_points", "evaluation_stride_hours"):
        if not isinstance(raw.get(key), int) or int(raw[key]) <= 0:
            raise ValueError(f"invalid_request_field:{key}")
    hard_stop = float(raw.get("hard_cost_stop_usd") or 0.0)
    if hard_stop <= 0 or hard_stop > 0.25:
        raise ValueError("invalid_hard_cost_stop")
    if sorted(raw.get("theory_ids") or []) != ["AT-HYP-0004", "AT-HYP-0008"]:
        raise ValueError("theory_binding_required")
    for key in (
        "evaluation_outcomes_hidden_from_ai",
        "failed_and_abandoned_attempts_remain_counted",
        "no_post_result_prompt_tuning",
        "no_retroactive_rescore",
        "identical_primary_payload_required",
        "modal_rule_may_only_seed_new_preregistered_successor",
    ):
        if raw.get(key) is not True:
            raise ValueError(f"required_true:{key}")
    if raw.get("economic_scoring_enabled") is not False or raw.get("direct_policy_arm_enabled") is not False:
        raise ValueError("reliability_phase_must_exclude_economics_and_direct_policy")
    authority = raw.get("authority")
    if authority != AUTHORITY:
        raise ValueError("research_only_authority_required")
    thresholds = raw.get("pre_registered_thresholds") or {}
    expected = {
        "structured_output_success_rate": 0.9,
        "replayable_rule_admission_rate": 0.9,
        "modal_normalized_rule_share": 0.7,
    }
    if thresholds != expected:
        raise ValueError("preregistered_thresholds_mismatch")
    return raw


def structured_rule(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict) or set(value) != REQUIRED_OUTPUT_FIELDS:
        return None
    feature = value.get("feature")
    long_trigger = value.get("long_trigger")
    short_trigger = value.get("short_trigger")
    if feature not in base.FEATURES:
        return None
    if long_trigger not in {"GT_Q75", "GT_Q50", "DISABLED"}:
        return None
    if short_trigger not in {"LT_Q25", "LT_Q50", "DISABLED"}:
        return None
    return {
        "feature": str(feature),
        "long_trigger": str(long_trigger),
        "short_trigger": str(short_trigger),
    }


def replayable_rule(value: Any) -> dict[str, str] | None:
    rule = structured_rule(value)
    if rule is None:
        return None
    validated = base.validate_rule({**rule, "rationale": ""})
    if validated is None:
        return None
    return {key: str(validated[key]) for key in ("feature", "long_trigger", "short_trigger")}


def error_class(record: dict[str, Any], structured: dict[str, str] | None, replayable: dict[str, str] | None) -> str | None:
    error = str(record.get("error") or "")
    if error.startswith("openai_http_"):
        return "HTTP_API_FAILURE"
    if "missing_output_text" in error:
        return "MISSING_OUTPUT_TEXT"
    if "JSONDecodeError" in error:
        return "MALFORMED_JSON"
    if error:
        return "OUTPUT_OR_API_FAILURE"
    if structured is None:
        return "STRICT_SCHEMA_INVALID"
    if replayable is None:
        return "SEMANTICALLY_INADMISSIBLE_RULE"
    return None


def fake_live_call(_api_key: str, payload: dict[str, Any], _model: str) -> dict[str, Any]:
    output = {"feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"}
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


def evaluate_records(
    records: list[dict[str, Any]],
    *,
    request: dict[str, Any],
    design_summary: dict[str, Any],
    capability: dict[str, Any],
) -> dict[str, Any]:
    repeats = int(request["compiler_repeats"])
    if len(records) != repeats:
        raise ValueError("compiler_record_count_mismatch")

    structured_count = 0
    admitted_count = 0
    hashes: list[str | None] = []
    handoffs: list[dict[str, Any] | None] = []
    taxonomy: Counter[str] = Counter()
    mission_lock = {
        "experiment_id": request["experiment_id"],
        "issue": ISSUE,
        "request_sha256": base.sha(request),
        "phase": "COMPILER_RELIABILITY_ONLY",
    }

    enriched: list[dict[str, Any]] = []
    for repeat, record in enumerate(records, start=1):
        structured = structured_rule(record.get("output"))
        replayable = replayable_rule(record.get("output"))
        structured_count += int(structured is not None)
        admitted_count += int(replayable is not None)
        rule_hash = base.sha(replayable) if replayable is not None else None
        hashes.append(rule_hash)
        contract = None
        if replayable is not None:
            contract = handoff.build_contract(
                stage_id=f"E2_V2_COMPILER_RUN_{repeat}",
                mission=mission_lock,
                input_artifact=design_summary,
                capability_snapshot=capability,
                output_artifact=replayable,
                repair_scope=f"E2_V2_COMPILER_RUN_{repeat}",
                owner_candidate_id=request["experiment_id"],
                created_at=request["frozen_at_utc"],
            )
            handoff.assert_downstream_input(contract, replayable)
        handoffs.append(contract)
        failure = error_class(record, structured, replayable)
        if failure:
            taxonomy[failure] += 1
        enriched.append({
            **record,
            "structured_output_valid": structured is not None,
            "replayable_rule_admitted": replayable is not None,
            "normalized_rule": replayable,
            "normalized_rule_hash": rule_hash,
            "failure_class": failure,
            "handoff_id": contract.get("handoff_id") if contract else None,
        })

    valid_hashes = [value for value in hashes if value is not None]
    counts = Counter(valid_hashes)
    modal_hash, modal_count = (counts.most_common(1)[0] if counts else (None, 0))
    modal_rule = None
    if modal_hash:
        for row in enriched:
            if row["normalized_rule_hash"] == modal_hash:
                modal_rule = row["normalized_rule"]
                break

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
        "structured_output_success": structured_rate >= float(thresholds["structured_output_success_rate"]),
        "replayable_rule_admission": admission_rate >= float(thresholds["replayable_rule_admission_rate"]),
        "modal_normalized_rule_convergence": modal_share >= float(thresholds["modal_normalized_rule_share"]),
        "identical_primary_payload": payload_hash_stable,
        "capability_snapshot_stable": capability_stable,
    }
    supported = all(gates.values())
    return {
        "records": enriched,
        "structured_output_success_rate": round(structured_rate, 6),
        "replayable_rule_admission_rate": round(admission_rate, 6),
        "modal_normalized_rule_share": round(modal_share, 6),
        "modal_normalized_rule_hash": modal_hash,
        "modal_normalized_rule": modal_rule,
        "normalized_rule_hashes": hashes,
        "failed_call_count": sum(taxonomy.values()),
        "failure_taxonomy": dict(sorted(taxonomy.items())),
        "request_hash": request_hashes[0] if payload_hash_stable else None,
        "capability_snapshot_sha256": capability_snapshot["snapshot_sha256"],
        "gates": gates,
        "conclusion": (
            "COMPILER_RELIABILITY_SUPPORTED_FOR_ECONOMIC_SUCCESSOR"
            if supported
            else "COMPILER_RELIABILITY_NOT_SUPPORTED"
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
    rows, source_hashes = hourly.load_raw_close_rows(repo_root / request["source_root"], request["cutoff_utc"])
    design_summary, hidden_points = base.build_frozen_sample(rows, request)
    if not hidden_points:
        raise ValueError("frozen_sample_missing_hidden_points")

    schema = compiler_schema_v2()
    envelope = {
        "contract": "AUTO_TRADING_E2_COMPILER_RELIABILITY_BLINDED_INPUT_v1",
        "mode": "COMPILER",
        "mission": "Compile exactly one constrained deterministic rule. This phase measures delivery reliability and rule convergence only.",
        "design_summary": design_summary,
        "allowed_features": sorted(base.FEATURES),
        "allowed_rule": {
            "long": ["GT_Q75", "GT_Q50", "DISABLED"],
            "short": ["LT_Q25", "LT_Q50", "DISABLED"],
        },
        "evaluation_outcomes_hidden": True,
        "economic_scoring_enabled": False,
        "direct_policy_arm_enabled": False,
    }
    if "_evaluation_label" in json.dumps(envelope):
        raise ValueError("evaluation_label_leak")

    payload = base.build_payload(
        request["model"],
        request["reasoning_effort"],
        "e2_compiler_reliability_rule_v2",
        schema,
        envelope,
        int(request["compiler_max_output_tokens"]),
    )
    capability = {
        "tools": ["openai.responses", "deterministic_rule_validation", "agent_handoff_contract"],
        "schemas": {"compiler_output": base.sha(schema)},
        "runtime": "AUTO_TRADING_E2_COMPILER_RELIABILITY_v2",
    }

    if call_impl is None:
        call_impl = fake_live_call if dry_run else base.live_call
    api_key = "dry-run" if dry_run else str(os.environ.get("OPENAI_API_KEY") or "")
    if not dry_run and not api_key:
        raise SystemExit("OPENAI_API_KEY_missing")

    total_cost = 0.0
    records: list[dict[str, Any]] = []
    for repeat in range(1, int(request["compiler_repeats"]) + 1):
        record = call_impl(api_key, payload, request["model"])
        total_cost += float(record.get("cost_usd") or 0.0)
        records.append({"arm": "AI_COMPILER_RELIABILITY", "repeat": repeat, **record})
        if total_cost > float(request["hard_cost_stop_usd"]):
            raise RuntimeError(f"e2_v2_cost_hard_stop:{total_cost:.8f}")

    evaluated = evaluate_records(records, request=request, design_summary=design_summary, capability=capability)
    result = {
        "contract": RESULT_CONTRACT,
        "status": "COMPLETE",
        "issue": ISSUE,
        "experiment_id": request["experiment_id"],
        "parent_experiment_id": request["parent_experiment_id"],
        "parent_result_sha256": request["parent_result_sha256"],
        "request_sha256": base.sha(request),
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
            "compiler_calls": request["compiler_repeats"],
            "failed_calls": evaluated["failed_call_count"],
            "total_cost_usd": round(total_cost, 8),
            "hard_cost_stop_usd": request["hard_cost_stop_usd"],
            "compiler_max_output_tokens": request["compiler_max_output_tokens"],
        },
        "reliability": {
            key: evaluated[key]
            for key in (
                "structured_output_success_rate",
                "replayable_rule_admission_rate",
                "modal_normalized_rule_share",
                "modal_normalized_rule_hash",
                "modal_normalized_rule",
                "normalized_rule_hashes",
                "failure_taxonomy",
                "request_hash",
                "capability_snapshot_sha256",
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
    with (output_dir / "calls.jsonl").open("w", encoding="utf-8") as handle:
        for record in evaluated["records"]:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run preregistered E2 v2 compiler reliability gate.")
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
        "structured_output_success_rate": result["reliability"]["structured_output_success_rate"],
        "replayable_rule_admission_rate": result["reliability"]["replayable_rule_admission_rate"],
        "modal_normalized_rule_share": result["reliability"]["modal_normalized_rule_share"],
        "total_cost_usd": result["api"]["total_cost_usd"],
        "result_sha256": result["result_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
