#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment_lifecycle as base  # noqa: E402
import experiment_lifecycle_scientific_admission as scientific  # noqa: E402

UTC = timezone.utc
FACTOR_KIND = "FACTOR_TEST"
CANDIDATE_CONTRACT = "EXPERIMENT_CANDIDATE_v1"
ADMISSION_CONTRACT = scientific.ADMISSION_CONTRACT
QUALIFIED = scientific.QUALIFIED
EXTENSION_CONTRACT = "FACTOR_TEST_ADMISSION_EXTENSION_v1"
ALLOWED_TRANSFORMS = {"RAW", "ROLLING_PERCENTILE", "ZSCORE", "DISTANCE_FROM_EXTREMA"}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def require_string(value: Any, error: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(error)
    return text


def normalize_factor_design(raw: dict[str, Any]) -> dict[str, Any]:
    theory_id = require_string(raw.get("theory_id"), "factor_theory_id_required")
    feature_field = require_string(raw.get("feature_field"), "factor_feature_field_required")
    label_field = require_string(raw.get("label_field"), "factor_label_field_required")
    source_repository = require_string(raw.get("source_repository"), "factor_source_repository_required")
    source_path = require_string(raw.get("source_path"), "factor_source_path_required")
    source_commit = require_string(raw.get("source_commit"), "factor_source_commit_required")
    source_sha256 = require_string(raw.get("source_sha256"), "factor_source_sha256_required")
    transforms = [str(item).upper() for item in raw.get("transforms", [])]
    if not transforms or set(transforms) - ALLOWED_TRANSFORMS or "RAW" not in transforms:
        raise ValueError("invalid_factor_transforms")
    if len(transforms) != len(set(transforms)):
        raise ValueError("duplicate_factor_transforms")
    rolling_window_hours = int(raw.get("rolling_window_hours") or 0)
    forward_horizon_hours = int(raw.get("forward_horizon_hours") or 0)
    if not 1 <= rolling_window_hours <= 24 * 365:
        raise ValueError("invalid_rolling_window_hours")
    if not 1 <= forward_horizon_hours <= 24 * 365:
        raise ValueError("invalid_forward_horizon_hours")
    trial_n = int(raw.get("proposal_trial_n") or 0)
    if trial_n < 1:
        raise ValueError("proposal_trial_n_required")
    primary_metric = require_string(raw.get("primary_metric"), "primary_metric_required")
    support_rule = raw.get("support_rule")
    if not isinstance(support_rule, dict) or not support_rule:
        raise ValueError("support_rule_required")
    return {
        "theory_id": theory_id,
        "feature_field": feature_field,
        "label_field": label_field,
        "source_repository": source_repository,
        "source_path": source_path,
        "source_commit": source_commit,
        "source_sha256": source_sha256,
        "rolling_window_hours": rolling_window_hours,
        "forward_horizon_hours": forward_horizon_hours,
        "transforms": transforms,
        "primary_metric": primary_metric,
        "support_rule": support_rule,
        "proposal_trial_n": trial_n,
        "monotonic_trial_n_required": bool(raw.get("monotonic_trial_n_required", True)),
        "failed_and_abandoned_attempts_remain_counted": bool(raw.get("failed_and_abandoned_attempts_remain_counted", True)),
        "point_in_time_required": bool(raw.get("point_in_time_required", True)),
        "independent_evidence_required_for_promotion": bool(raw.get("independent_evidence_required_for_promotion", True)),
    }


def normalize_spec(raw: dict[str, Any]) -> dict[str, Any]:
    previous_kinds = set(base.KINDS)
    try:
        base.KINDS.add(FACTOR_KIND)
        base_spec = base.normalize({**raw, "kind": FACTOR_KIND, "components": [], "target_direction": "NONE"})
    finally:
        base.KINDS.clear()
        base.KINDS.update(previous_kinds)
    factor_design = normalize_factor_design(raw.get("factor_design") or {})
    base_spec["factor_design"] = factor_design
    return base_spec


def identity_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_identity": base.identity_spec(spec),
        "factor_design": spec["factor_design"],
        "extension_contract": EXTENSION_CONTRACT,
    }


def semantic_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "base_semantic_spec": scientific.semantic_spec(spec),
        "factor_design": spec["factor_design"],
        "extension_contract": EXTENSION_CONTRACT,
    }


def factor_plan(spec: dict[str, Any]) -> dict[str, Any]:
    design = spec["factor_design"]
    return {
        "problem_to_solve": "Determine whether a frozen deterministic factor transformation adds stable point-in-time out-of-sample information beyond the raw feature baseline.",
        "existing_capability_overlap": ["experiment_lifecycle", "scientific_admission", "E1_temporal_integrity"],
        "baseline": ["RAW_FEATURE_LEVEL", "DETERMINISTIC_PLACEBO", "NO_FACTOR_CONTROL"],
        "incremental_value_claim": "At least one pre-registered normalized transform adds positive sign-stable OOS information beyond RAW without cross-symbol degradation.",
        "success_criteria": [
            "E1 temporal leakage validation remains PASS",
            "all transforms pass right-truncation invariance",
            "pre-registered support rule is satisfied on independent evidence",
            "result remains worthwhile after multiplicity and complexity controls",
        ],
        "failure_criteria": [
            "normalized transforms fail the frozen support rule",
            "train-to-OOS sign instability invalidates support",
            "temporal leakage or timestamp ambiguity is detected",
            "independent evidence does not reproduce the claimed information",
        ],
        "kill_criteria": [
            "point-in-time lineage cannot be proven",
            "trial accounting is incomplete or retroactively rewritten",
            "support depends on raw-data leakage or post-outcome parameter changes",
            "complexity exceeds measured incremental value",
        ],
        "negative_controls": ["RAW_FEATURE_LEVEL", "DETERMINISTIC_PLACEBO", "TIME_SHIFTED_CONTROL"],
        "adversarial_checks": ["RIGHT_TRUNCATION", "WARMUP_CONVERGENCE", "SIGN_STABILITY", "CROSS_SYMBOL_REPLICATION", "MULTIPLE_TESTING_SEARCH_BIAS"],
        "factor_design": design,
        "authority_ceiling": "RESEARCH_ONLY_NON_CANONICAL",
        "prospective_evidence_required": True,
    }


def build_records(raw_spec: dict[str, Any], e1_result: dict[str, Any], created_at: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if e1_result.get("verdict") != "PASS" or not (e1_result.get("gate") or {}).get("e3_may_begin_only_if_verdict_pass"):
        raise ValueError("E1_PASS_REQUIRED")
    spec = normalize_spec(raw_spec)
    candidate_id = "EC-" + base.sha(identity_spec(spec))[:20]
    candidate = {
        "contract": CANDIDATE_CONTRACT,
        "candidate_id": candidate_id,
        "created_at_utc": created_at,
        "registered_at_utc": created_at,
        "target_unit_contract_version": None,
        "spec": spec,
        "source": {
            "mission_issue": 885,
            "theory_id": spec["factor_design"]["theory_id"],
            "admission_extension": EXTENSION_CONTRACT,
            "e1_experiment_id": e1_result.get("experiment_id"),
            "e1_reference_sha256": base.sha(e1_result),
        },
        "dormancy_policy": {"automatic_age_expiry": False, "retain_until": "FALSIFIED_OR_GOVERNANCE_CLOSED"},
        "authority": {"canonical_promotion": False, "framework_state_change": False, "model_weight_change": False, "portfolio_action": False},
    }
    semantic = semantic_spec(spec)
    admission = {
        "contract": ADMISSION_CONTRACT,
        "candidate_id": candidate_id,
        "candidate_created_at_utc": created_at,
        "admission_frozen_at_utc": created_at,
        "historical_candidate_requalification": False,
        "no_retroactive_rescore": True,
        "semantic_fingerprint": scientific.digest(semantic),
        "semantic_spec": semantic,
        "status": QUALIFIED,
        "status_reasons": ["E1_TEMPORAL_INTEGRITY_PASS", "EXPLICIT_FACTOR_DESIGN", "TRIAL_ACCOUNTING_BOUND"],
        "plan": factor_plan(spec),
        "method_reference": "GitHub issue #885 / FACTOR_TEST admission extension",
        "admission_rule_reference": EXTENSION_CONTRACT,
        "authority": {"canonical_effect": False, "portfolio_execution": False, "framework_state_change": False, "threshold_change": False, "weight_change": False, "automatic_promotion": False},
    }
    return candidate, admission


def write_records(candidate_root: Path, admission_root: Path, candidate: dict[str, Any], admission: dict[str, Any]) -> tuple[Path, Path]:
    when = base.dt(candidate["created_at_utc"])
    candidate_path = candidate_root / when.strftime("%Y/%m") / f"{candidate['candidate_id']}.json"
    admission_path = admission_root / when.strftime("%Y/%m") / f"{candidate['candidate_id']}.json"
    if not base.write_new(candidate_path, candidate):
        raise FileExistsError(f"immutable_candidate_exists:{candidate_path}")
    if not base.write_new(admission_path, admission):
        raise FileExistsError(f"immutable_admission_exists:{admission_path}")
    return candidate_path, admission_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--e1-result", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--admission-root", type=Path, required=True)
    parser.add_argument("--created-at", default=None)
    args = parser.parse_args()
    created_at = args.created_at or now_iso()
    candidate, admission = build_records(json.loads(args.spec.read_text()), json.loads(args.e1_result.read_text()), created_at)
    candidate_path, admission_path = write_records(args.candidate_root, args.admission_root, candidate, admission)
    print(json.dumps({
        "candidate_id": candidate["candidate_id"],
        "candidate_path": str(candidate_path),
        "admission_path": str(admission_path),
        "admission_status": admission["status"],
        "kind": candidate["spec"]["kind"],
        "parallel_engine_created": False,
        "authority": admission["authority"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
