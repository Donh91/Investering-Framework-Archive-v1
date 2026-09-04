#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from typing import Any

from compounding_learning_utils import (
    ALLOWED_ACTIONS, ALLOWED_VERDICTS, admission_map, adjudication_map, as_int,
    candidate_age_days, classify, crossed_keys, digest, iso, monthly_claim_map,
    profile_for, validate_policy,
)


def normalized_source_fingerprint(
    registry: dict[str, Any], admissions: dict[str, Any], adjudication: dict[str, Any], monthly: dict[str, Any]
) -> str:
    lifecycle = [
        {
            "candidate_id": row.get("candidate_id"),
            "state": row.get("state"),
            "created_at_utc": row.get("created_at_utc"),
            "kind": row.get("kind"),
            "horizon_days": row.get("horizon_days"),
            "observation_count": row.get("observation_count"),
            "matured_outcome_count": row.get("matured_outcome_count"),
            "replication_receipts": row.get("replication_receipts", []),
        }
        for row in registry.get("candidates", [])
        if isinstance(row, dict)
    ]
    adm = [
        {"candidate_id": row.get("candidate_id"), "status": row.get("status"), "semantic_fingerprint": row.get("semantic_fingerprint")}
        for row in admissions.get("candidates", [])
        if isinstance(row, dict)
    ]
    adj = [
        {"candidate_id": row.get("candidate_id"), "selected_action": row.get("selected_action"), "lifecycle_state": row.get("lifecycle_state")}
        for row in adjudication.get("candidate_actions", [])
        if isinstance(row, dict)
    ]
    claims = [
        {"candidate_id": row.get("candidate_id"), "state": row.get("state"), "matured_outcome_count": row.get("matured_outcome_count")}
        for row in monthly.get("learning_claims", [])
        if isinstance(row, dict)
    ]
    return digest({"lifecycle": lifecycle, "admission": adm, "adjudication": adj, "monthly_claims": claims})


def build_child_proposal(item: dict[str, Any]) -> dict[str, Any]:
    proposal_kind = item["proposal_kind"]
    base = {
        "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "proposal_status": "PROPOSAL_ONLY",
        "parent_candidate_id": item["candidate_id"],
        "parent_preserved_immutable": True,
        "proposal_kind": proposal_kind,
        "action": item["recommended_action"],
        "learning_verdict": item["learning_verdict"],
        "reason": item["reason"],
        "automatic_candidate_registration": False,
        "automatic_scientific_admission": False,
        "automatic_promotion": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "market_rule_change": False,
        "threshold_change": False,
        "weight_change": False,
        "required_route": [
            "RESEARCH_MEMORY_NOVELTY_GATE",
            "DECISION_IMPACT_VOI",
            "SCIENTIFIC_ADMISSION_OR_EXISTING_OWNER",
            "PROSPECTIVE_FREEZE_IF_AUTHORIZED",
            "EXPERIMENT_EXECUTION_PLANE_IF_APPLICABLE",
        ],
    }
    if proposal_kind == "INCREMENTAL_VALUE_CHILD":
        base["child_question_template"] = (
            "Does the frozen parent candidate add incremental value beyond the explicit baseline and controls already bound by its scientific-admission record on new prospective evidence?"
        )
        base["inheritance_rule"] = "INHERIT_REFERENCES_ONLY_NEVER_COPY_OR_MUTATE_FROZEN_PARENT_FIELDS"
    elif proposal_kind == "EVIDENCE_REPAIR":
        base["child_question_template"] = "Can the exact missing mapping/evidence path be repaired without changing the frozen parent hypothesis?"
        base["inheritance_rule"] = "REPAIR_EVIDENCE_PATH_ONLY_PARENT_HYPOTHESIS_UNCHANGED"
    elif proposal_kind == "FAILURE_REVIEW":
        base["child_question_template"] = "Which preregistered failure mode explains the negative prospective result, and is any bounded challenger justified?"
        base["inheritance_rule"] = "NO_CHALLENGER_UNLESS_FAILURE_REVIEW_IDENTIFIES_A_NEW_FALSIFIABLE_UNCERTAINTY"
    return base


def priority_key(item: dict[str, Any]) -> tuple[int, int, int, str]:
    action_rank = {
        "RECOVER_EVIDENCE_PATH": 0,
        "RUN_INCREMENTAL_VALUE_TEST": 1,
        "RUN_REDUNDANCY_CONFIRMATION": 2,
        "DEPRIORITIZE": 3,
        "CONTINUE_OBSERVING": 4,
        "FREEZE_NEW_CHALLENGER": 5,
        "OPEN_PROSPECTIVE_FORWARD_TEST": 6,
    }
    verdict_rank = {
        "DATA_DEFECT": 0,
        "PROMISING": 1,
        "REPLICATION_REQUIRED": 2,
        "FAILED": 3,
        "REDUNDANT": 4,
        "INSUFFICIENT_EVIDENCE": 5,
    }
    return (
        action_rank.get(item["recommended_action"], 99),
        verdict_rank.get(item["learning_verdict"], 99),
        -as_int(item.get("matured_outcome_count"), 0),
        str(item.get("candidate_id") or ""),
    )


def build_state(
    registry: dict[str, Any],
    admissions: dict[str, Any],
    adjudication: dict[str, Any],
    monthly: dict[str, Any],
    policy: dict[str, Any],
    previous: dict[str, Any],
    as_of: datetime,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    validate_policy(policy)
    if registry.get("contract") != "EXPERIMENT_LIFECYCLE_REGISTRY_v1":
        raise ValueError("invalid experiment lifecycle registry")
    if admissions.get("contract") != "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1":
        raise ValueError("invalid scientific admission registry")
    if adjudication and adjudication.get("contract") != "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1":
        raise ValueError("invalid unified adjudication input")

    source_fp = normalized_source_fingerprint(registry, admissions, adjudication, monthly)
    amap = admission_map(admissions)
    jmap = adjudication_map(adjudication)
    mmap = monthly_claim_map(monthly)
    candidates = [row for row in registry.get("candidates", []) if isinstance(row, dict) and row.get("candidate_id")]

    previous_active = previous.get("contract") == "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1" and previous.get("activation_at_utc")
    prior_keys = set(previous.get("checkpoint_keys_seen", [])) if previous_active else set()

    all_crossed: set[str] = set()
    due_items: list[dict[str, Any]] = []
    for candidate in candidates:
        profile = profile_for(candidate, policy)
        crossed = crossed_keys(candidate, profile, policy, as_of)
        all_crossed.update(row["key"] for row in crossed)
        if not previous_active:
            continue
        new_crossings = [row for row in crossed if row["key"] not in prior_keys]
        if not new_crossings:
            continue
        cid = str(candidate["candidate_id"])
        verdict, action, proposal_kind, reason = classify(candidate, amap.get(cid, {}), jmap.get(cid, {}), mmap.get(cid, {}))
        if verdict not in ALLOWED_VERDICTS or action not in ALLOWED_ACTIONS:
            raise ValueError("controller emitted unsupported verdict/action")
        if profile == "CONFIRMATORY":
            verdict = "INSUFFICIENT_EVIDENCE"
            action = "CONTINUE_OBSERVING"
            proposal_kind = "NO_CHILD"
            reason = "confirmatory profile checkpoint is operational/coverage-only; interim performance inference is forbidden"
        due_items.append({
            "candidate_id": cid,
            "parent_candidate_id": cid,
            "title": candidate.get("title"),
            "kind": candidate.get("kind"),
            "horizon_days": candidate.get("horizon_days"),
            "learning_profile": profile,
            "candidate_state": candidate.get("state"),
            "scientific_admission_status": (amap.get(cid, {}).get("status") or candidate.get("scientific_admission_status") or "UNAVAILABLE"),
            "unified_adjudication_action": jmap.get(cid, {}).get("selected_action"),
            "age_days": candidate_age_days(candidate, as_of),
            "observation_count": as_int(candidate.get("observation_count"), 0),
            "matured_outcome_count": as_int(candidate.get("matured_outcome_count"), 0),
            "checkpoint_crossings": sorted(new_crossings, key=lambda row: (row["axis"], row["threshold"])),
            "learning_verdict": verdict,
            "recommended_action": action,
            "proposal_kind": proposal_kind,
            "reason": reason,
            "canonical_effect": False,
            "portfolio_execution": False,
            "automatic_promotion": False,
        })

    if not previous_active:
        state = {
            "contract": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1",
            "status": "ACTIVE_BOOTSTRAPPED_NO_RETROACTIVE_CHECKPOINTS",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "activation_at_utc": iso(as_of),
            "generated_at_utc": iso(as_of),
            "learning_loop": "OBSERVE_FREEZE_TEST_MATURE_LEARN_CHALLENGE_RETEST_IMPROVE",
            "activation_floor_rule": "ALL_PRE_ACTIVATION_CHECKPOINTS_BASELINED_NOT_REPLAYED",
            "source_fingerprint": source_fp,
            "registry_candidate_count": len(candidates),
            "checkpoint_keys_seen": sorted(all_crossed),
            "new_checkpoint_candidate_count": 0,
            "checkpoint_queue": [],
            "primary_action": "CONTINUE_OBSERVING",
            "target": "EXPERIMENT_LIFECYCLE",
            "reason": "controller activation baseline captured without retroactive learning claims",
            "next_best_experiment": {
                "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
                "authority": "RESEARCH_ONLY_NON_CANONICAL",
                "proposal_status": "BOOTSTRAP_NO_RETROACTIVE_PROPOSAL",
                "canonical_effect": False,
                "portfolio_execution": False,
            },
            "confirmatory_firewall": {
                "generic_interim_performance_inference_allowed": False,
                "confirmatory_candidate_ids": list(policy.get("confirmatory_candidate_ids", [])),
                "t13_owner_path": "research/api_agent/forecast_skill",
                "t13_read_or_mutated_by_controller": False,
                "note": "T13 remains owned by its sealed preregistration and confirmatory runtime; this controller neither reads its outcomes nor changes its method.",
            },
            "canonical_effect": False,
            "portfolio_execution": False,
            "automatic_promotion": False,
            "automatic_canonical_write": False,
            "automatic_market_rule_change": False,
            "automatic_threshold_change": False,
            "automatic_weight_change": False,
        }
        state["evidence_fingerprint"] = digest({"source": source_fp, "activation": state["activation_at_utc"], "keys": state["checkpoint_keys_seen"]})
        return state, state["next_best_experiment"], True

    due_items.sort(key=priority_key)
    limit = max(1, as_int(policy.get("max_checkpoint_candidates_per_run"), 25))
    selected = due_items[:limit]
    seen = sorted(prior_keys | all_crossed)

    if selected:
        primary = selected[0]
        if primary["proposal_kind"] == "NO_CHILD":
            next_best = {
                "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
                "authority": "RESEARCH_ONLY_NON_CANONICAL",
                "proposal_status": "NO_CHILD_REQUIRED",
                "parent_candidate_id": primary["candidate_id"],
                "action": primary["recommended_action"],
                "learning_verdict": primary["learning_verdict"],
                "reason": primary["reason"],
                "canonical_effect": False,
                "portfolio_execution": False,
                "automatic_promotion": False,
            }
        else:
            next_best = build_child_proposal(primary)
        primary_action = primary["recommended_action"]
        target = primary["candidate_id"]
        reason = primary["reason"]
    else:
        next_best = previous.get("next_best_experiment") or {
            "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "proposal_status": "NO_NEW_CHECKPOINT_DUE",
            "canonical_effect": False,
            "portfolio_execution": False,
        }
        primary_action = "CONTINUE_OBSERVING"
        target = "EXPERIMENT_LIFECYCLE"
        reason = "no new post-activation time-or-evidence checkpoint crossed"

    state = {
        "contract": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1",
        "status": "ACTIVE",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "activation_at_utc": previous["activation_at_utc"],
        "generated_at_utc": iso(as_of),
        "learning_loop": "OBSERVE_FREEZE_TEST_MATURE_LEARN_CHALLENGE_RETEST_IMPROVE",
        "activation_floor_rule": "ALL_PRE_ACTIVATION_CHECKPOINTS_BASELINED_NOT_REPLAYED",
        "source_fingerprint": source_fp,
        "registry_candidate_count": len(candidates),
        "checkpoint_keys_seen": seen,
        "new_checkpoint_candidate_count": len(selected),
        "checkpoint_queue": selected,
        "primary_action": primary_action,
        "target": target,
        "reason": reason,
        "next_best_experiment": next_best,
        "confirmatory_firewall": {
            "generic_interim_performance_inference_allowed": False,
            "confirmatory_candidate_ids": list(policy.get("confirmatory_candidate_ids", [])),
            "t13_owner_path": "research/api_agent/forecast_skill",
            "t13_read_or_mutated_by_controller": False,
            "note": "T13 remains owned by its sealed preregistration and confirmatory runtime; this controller neither reads its outcomes nor changes its method.",
        },
        "canonical_effect": False,
        "portfolio_execution": False,
        "automatic_promotion": False,
        "automatic_canonical_write": False,
        "automatic_market_rule_change": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
    }
    state["evidence_fingerprint"] = digest({"source": source_fp, "selected": selected, "seen": seen, "next": next_best})

    unchanged = source_fp == previous.get("source_fingerprint") and not selected
    if unchanged:
        return previous, previous.get("next_best_experiment", next_best), False
    return state, next_best, True
