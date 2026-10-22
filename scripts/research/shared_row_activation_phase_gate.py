"""Shared Row P0 activation phase validator (schema-only, NO activation authority).

This validates the coherence of quarantined and prospective ACTIVE contracts.
Actual source readiness, original first-known availability, activation-review
approval and future-floor selection require separate immutable evidence gates.
"""
from __future__ import annotations

import re
from datetime import datetime

CORE_FAMILIES = {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}
GATE_VERSION = "SHARED_ROW_ACTIVATION_PHASE_GATE_v1_1"
FROZEN_DECISIONS = {
    "C01_ETHBTC": "ETHBTC_PERSISTENCE.permission",
    "C02_BREADTH": "BREADTH_SURVIVAL.permission",
    "C03_BTCD": "BTCD_PATH_RECLAIM.permission",
    "C04_ETHBTC_BREADTH": "C01_ETHBTC AND C02_BREADTH",
    "C05_ETHBTC_BTCD": "C01_ETHBTC AND C03_BTCD",
    "C06_BREADTH_BTCD": "C02_BREADTH AND C03_BTCD",
    "C07_SIMPLE_3": "C01_ETHBTC AND C02_BREADTH AND C03_BTCD",
}
QUARANTINED = "QUARANTINED_PENDING_POST_REPAIR_EVIDENCE"
ACTIVE = "ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION"


def exact_utc(value: object) -> datetime:
    """Reject ambiguous/naive timestamps; never infer decision-time legality."""
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value
    ):
        raise AssertionError("ACTIVATION_TIMESTAMP_MUST_BE_EXACT_UTC")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def validate_activation_phase(contract: dict, freeze: dict, runtime: dict | None = None) -> str:
    """Validate phase consistency only; do not certify external sources/reviews.

    A separately governed activation PR must reproduce the original immutable
    source bundles, prove the future floor, and pass existing research controls.
    """
    activation = contract["prospective_activation"]
    rule = freeze["core_activation_rule"]
    state = activation.get("collection_state")
    assert state in {QUARANTINED, ACTIVE}, "UNRECOGNIZED_COLLECTION_STATE"
    assert rule.get("collection_state") == state, "ACTIVATION_FREEZE_STATE_DRIFT"
    assert isinstance(runtime, dict), "RUNTIME_STATE_REQUIRED"
    assert runtime.get("collection_state") == state, "ACTIVATION_RUNTIME_STATE_DRIFT"
    assert runtime.get("core_prospective_eligibility_status") == contract.get("prospective_eligibility_status"), "RUNTIME_ELIGIBILITY_STATUS_DRIFT"
    assert runtime.get("core_prospective_eligibility_start") == contract.get("prospective_eligibility_start"), "RUNTIME_ELIGIBILITY_FLOOR_DRIFT"
    assert runtime.get("authority") == "RESEARCH_ONLY_NON_CANONICAL", "RUNTIME_AUTHORITY_DRIFT"
    assert runtime.get("canonical_effect") is False, "RUNTIME_CANONICAL_AUTHORITY_FORBIDDEN"
    assert contract.get("no_backdating") is True and rule.get("no_backdating") is True
    assert contract.get("legacy_equivalence") is False
    assert activation.get("readiness_must_be_reproduced_from_actual_bound_sources") is True
    assert freeze.get("retroactive_candidate_decision_backfill") is False
    assert contract.get("candidate_decision_contract", {}).get("complete_core_set_required") is True
    assert rule.get("candidate_decision_contract_version") == contract["candidate_decision_contract"]["version"]
    required_candidates = {
        "C01_ETHBTC", "C02_BREADTH", "C03_BTCD", "C04_ETHBTC_BREADTH",
        "C05_ETHBTC_BTCD", "C06_BREADTH_BTCD", "C07_SIMPLE_3",
    }
    assert set(rule.get("candidates", [])) == required_candidates
    assert set(contract["candidate_decision_contract"]) >= required_candidates
    assert all(
        contract["candidate_decision_contract"].get(name) == expr
        for name, expr in FROZEN_DECISIONS.items()
    ), "FROZEN_CANDIDATE_DECISION_MUTATED"
    assert set(rule.get("start_only_when", [])) == CORE_FAMILIES
    families = {item["family_id"]: item for item in freeze["families"]}
    assert len(families) == len(freeze["families"]), "DUPLICATE_FROZEN_FAMILY_ID"
    assert CORE_FAMILIES <= families.keys(), "CORE_FAMILY_MISSING"
    assert all(
        families[name].get("status") == "READY"
        and families[name].get("candidate_decision_contract_status") == "READY"
        and families[name].get("repair_state") == "P0_REPAIRED_AWAITING_ACTIVATION_OR_ACTIVE"
        for name in CORE_FAMILIES
    ), "CORE_FAMILY_NOT_READY"
    # Optional families remain separately governed; blocked does NOT become core.
    assert all(
        fam.get("prospective_eligibility_start") is None
        for name, fam in families.items()
        if name not in CORE_FAMILIES and fam.get("candidate_decision_contract_status") == "BLOCKED"
    ), "BLOCKED_OPTIONAL_FAMILY_HAS_FLOOR"
    floor = exact_utc(contract.get("prospective_eligibility_start"))
    assert rule.get("prospective_eligibility_start") == contract.get("prospective_eligibility_start")
    assert all(
        fam.get("prospective_eligibility_start") == contract.get("prospective_eligibility_start")
        for name, fam in families.items() if name in CORE_FAMILIES
    ), "CORE_FAMILY_FLOOR_DRIFT"
    implementation_commit = activation.get("implementation_merge_commit")
    assert isinstance(implementation_commit, str) and re.fullmatch(r"[0-9a-f]{40}", implementation_commit)
    assert implementation_commit == freeze.get("p0_implementation_merge_commit")
    implementation_utc = exact_utc(activation.get("implementation_merged_at_utc"))
    assert activation.get("post_repair_source_capture_not_before_utc") == activation.get("implementation_merged_at_utc")
    assert freeze.get("post_repair_source_capture_not_before_utc") == activation.get("implementation_merged_at_utc")

    if state == QUARANTINED:
        assert contract.get("prospective_eligibility_status") == "CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR"
        assert rule.get("containment_floor_sentinel") is True
        assert contract["p0_containment"]["containment_floor_sentinel"] == contract["prospective_eligibility_start"]
        assert floor > implementation_utc
        assert activation.get("activation_pr") is None
        return "QUARANTINED_VALID"

    assert contract.get("prospective_eligibility_status") == "ACTIVE_POST_REPAIR_FLOOR"
    assert rule.get("containment_floor_sentinel") is False
    pr = activation.get("activation_pr")
    assert isinstance(pr, str) and re.fullmatch(
        r"https://github\.com/Donh91/Investering-Framework-Archive-v1/pull/[1-9][0-9]*",
        pr,
    ), "ACTIVATION_PR_REFERENCE_REQUIRED"
    # References below MUST be independently reproduced; formatting proves NO source.
    evidence = activation.get("activation_evidence")
    assert isinstance(evidence, dict), "ACTIVATION_EVIDENCE_REQUIRED"
    sha = evidence.get("source_readiness_commit_sha")
    assert isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha)
    path = evidence.get("source_readiness_path")
    assert isinstance(path, str) and path.startswith("06_RESEARCH_LAB/shared_row_model_tournament_v1/")
    assert ".." not in path and path.endswith(".md"), "SOURCE_READINESS_PATH_INVALID"
    source_ready_utc = exact_utc(evidence.get("latest_source_capture_at_utc"))
    review_utc = exact_utc(evidence.get("activation_reviewed_at_utc"))
    assert implementation_utc < source_ready_utc <= review_utc < floor, "ACTIVATION_CLOCK_ORDER_INVALID"
    assert activation.get("no_backdating", True) is True
    assert evidence.get("validator_repair_version") == GATE_VERSION, "VALIDATOR_REPAIR_VERSION_MISSING"
    adjudication_path = evidence.get("activation_adjudication_path")
    assert isinstance(adjudication_path, str) and adjudication_path.startswith(
        "06_RESEARCH_LAB/shared_row_model_tournament_v1/"
    ) and adjudication_path.endswith(".md") and ".." not in adjudication_path, "ACTIVATION_ADJUDICATION_PATH_REQUIRED"
    source_cutoff_utc = exact_utc(evidence.get("readiness_evidence_cutoff_utc"))
    freeze_utc = exact_utc(evidence.get("activation_freeze_time_utc"))
    assert implementation_utc < source_ready_utc <= source_cutoff_utc <= review_utc <= freeze_utc < floor, (
        "ACTIVATION_SOURCE_REVIEW_FREEZE_CLOCK_ORDER_INVALID"
    )
    return "ACTIVE_SCHEMA_VALID_SOURCE_REVIEW_STILL_REQUIRED"
