#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from scripts.experiments import ai_candidate_selection_e2 as v3

base = v3.base
hourly = v3.hourly
AUTHORITY = dict(v3.AUTHORITY)

REQUEST_CONTRACT = v3.REQUEST_CONTRACT
RESULT_CONTRACT = v3.RESULT_CONTRACT
EXPERIMENT_ID = "AT-E2-CANDIDATE-SELECTION-v4"
ISSUE = 972
PARENT_EXPERIMENT_ID = "AT-E2-CANDIDATE-SELECTION-v3"
PARENT_RESULT_SHA256 = "925522e6766218b54ce4112e5e233dcc0738a32c8771416a15e0e92064b477ca"
CANDIDATE_SET_SHA256 = v3.CANDIDATE_SET_SHA256
V3_PRIMARY_REQUEST_HASH = "5dbda5b90c5f18977c002ef55546299bae3c9a421340ade78f9b8a622d52b61a"
V3_MAX_OUTPUT_TOKENS = 200
V4_MAX_OUTPUT_TOKENS = 1000
V3_REQUEST_REL = Path("research/experiment_lifecycle/e2/requests/AT-E2-CANDIDATE-SELECTION-v3.json")

INVARIANT_FIELDS = (
    "theory_ids",
    "source_root",
    "cutoff_utc",
    "consumed_columns",
    "design_rows",
    "evaluation_points",
    "evaluation_stride_hours",
    "model",
    "reasoning_effort",
    "selection_repeats",
    "hard_cost_stop_usd",
    "candidate_set_sha256",
    "candidate_set",
    "pre_registered_thresholds",
    "economic_scoring_enabled",
    "direct_policy_arm_enabled",
    "evaluation_outcomes_hidden_from_ai",
    "failed_and_abandoned_attempts_remain_counted",
    "no_post_result_prompt_tuning",
    "no_retroactive_rescore",
    "identical_primary_payload_required",
    "modal_candidate_may_only_seed_new_preregistered_successor",
    "authority",
)


def validate_request(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("contract") != REQUEST_CONTRACT:
        raise ValueError("invalid_request_contract")
    if raw.get("status") != "APPROVED_RESEARCH_ONLY" or raw.get("issue") != ISSUE:
        raise ValueError("request_not_approved_for_issue_972")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("experiment_id_mismatch")
    if raw.get("parent_experiment_id") != PARENT_EXPERIMENT_ID:
        raise ValueError("parent_experiment_binding_required")
    if raw.get("parent_result_sha256") != PARENT_RESULT_SHA256:
        raise ValueError("parent_result_binding_mismatch")
    if raw.get("model") != "gpt-5.6-luna" or raw.get("reasoning_effort") != "medium":
        raise ValueError("frozen_model_effort_mismatch")
    if raw.get("selection_repeats") != 10 or raw.get("selection_max_output_tokens") != V4_MAX_OUTPUT_TOKENS:
        raise ValueError("frozen_v4_transport_runtime_mismatch")
    if raw.get("consumed_columns") != sorted(hourly.CANONICAL_RAW_COLUMNS):
        raise ValueError("raw_column_firewall_mismatch")
    if raw.get("candidate_set_sha256") != CANDIDATE_SET_SHA256:
        raise ValueError("frozen_candidate_set_hash_required")
    v3.validate_candidates(raw.get("candidate_set"))
    if sorted(raw.get("theory_ids") or []) != ["AT-HYP-0004", "AT-HYP-0008"]:
        raise ValueError("theory_binding_required")
    if float(raw.get("hard_cost_stop_usd") or 0.0) <= 0 or float(raw["hard_cost_stop_usd"]) > 0.05:
        raise ValueError("invalid_hard_cost_stop")
    for key in ("design_rows", "evaluation_points", "evaluation_stride_hours"):
        if not isinstance(raw.get(key), int) or int(raw[key]) <= 0:
            raise ValueError(f"invalid_request_field:{key}")
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


def assert_v3_control(request: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    v3_request = json.loads((repo_root / V3_REQUEST_REL).read_text(encoding="utf-8"))
    v3.validate_request(v3_request)
    for key in INVARIANT_FIELDS:
        if request.get(key) != v3_request.get(key):
            raise ValueError(f"v4_drift_beyond_transport_control:{key}")
    if v3_request.get("selection_max_output_tokens") != V3_MAX_OUTPUT_TOKENS:
        raise ValueError("v3_baseline_headroom_mismatch")
    if request.get("selection_max_output_tokens") != V4_MAX_OUTPUT_TOKENS:
        raise ValueError("v4_headroom_mismatch")
    return v3_request


def _guarded_call(
    inner: Callable[[str, dict[str, Any], str], dict[str, Any]],
) -> Callable[[str, dict[str, Any], str], dict[str, Any]]:
    def call(api_key: str, payload: dict[str, Any], model: str) -> dict[str, Any]:
        if payload.get("max_output_tokens") != V4_MAX_OUTPUT_TOKENS:
            raise ValueError("v4_live_payload_headroom_mismatch")
        normalized = deepcopy(payload)
        normalized["max_output_tokens"] = V3_MAX_OUTPUT_TOKENS
        normalized_hash = base.sha(normalized)
        if normalized_hash != V3_PRIMARY_REQUEST_HASH:
            raise ValueError("model_payload_drift_beyond_headroom")
        return inner(api_key, payload, model)

    return call


def run_trial(
    request: dict[str, Any],
    repo_root: Path,
    output_dir: Path,
    *,
    dry_run: bool = False,
    call_impl: Callable[[str, dict[str, Any], str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    request = validate_request(request)
    assert_v3_control(request, repo_root)
    inner = call_impl or (v3.fake_live_call if dry_run else base.live_call)

    old_validate = v3.validate_request
    old_issue = v3.ISSUE
    try:
        v3.validate_request = validate_request
        v3.ISSUE = ISSUE
        result = v3.run_trial(
            request,
            repo_root,
            output_dir,
            dry_run=dry_run,
            call_impl=_guarded_call(inner),
        )
    finally:
        v3.validate_request = old_validate
        v3.ISSUE = old_issue

    result.pop("result_sha256", None)
    result["transport_control"] = {
        "baseline_experiment_id": PARENT_EXPERIMENT_ID,
        "baseline_result_sha256": PARENT_RESULT_SHA256,
        "baseline_primary_request_hash": V3_PRIMARY_REQUEST_HASH,
        "baseline_max_output_tokens": V3_MAX_OUTPUT_TOKENS,
        "v4_max_output_tokens": V4_MAX_OUTPUT_TOKENS,
        "candidate_set_sha256": CANDIDATE_SET_SHA256,
        "model_facing_change": "MAX_OUTPUT_TOKENS_ONLY",
        "response_format_name_preserved_from_v3": True,
        "blinded_mission_envelope_preserved_from_v3": True,
    }
    result["result_sha256"] = base.sha(result)
    (output_dir / "result.json").write_bytes(base.canon(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run preregistered E2 v4 candidate-selection transport-control gate.")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run_trial(
        json.loads(args.request.read_text(encoding="utf-8")),
        args.repo_root,
        args.output_dir,
        dry_run=args.dry_run,
    )
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
