"""Fail-closed declaration preflight for Shared Row research activation.

This is NOT activation authority: external receipt hashes, provider first-known,
approval, source readiness and future outcome evidence remain separate gates.
"""
from __future__ import annotations
import re
from datetime import datetime

QUARANTINE = "QUARANTINED_PENDING_POST_REPAIR_EVIDENCE"
ACTIVE = "ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION"
CORE = {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}

def require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)

def instant(value: object, code: str) -> datetime:
    require(isinstance(value,str) and bool(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z",value)),code)
    try:
        result = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(code) from exc
    return result

def validate_phase(contract: dict, freeze: dict, runtime: dict | None = None) -> str:
    """Only declaration coherence. Neither historical PIT nor actual sources certified."""
    activation = contract["prospective_activation"]
    rule = freeze["core_activation_rule"]
    status = contract.get("prospective_eligibility_status")
    state = activation.get("collection_state")
    require(contract.get("no_backdating") is True and rule.get("no_backdating") is True,
            "BACKDATING_POLICY_MISSING")
    require(activation.get("implementation_merge_commit") == freeze.get("p0_implementation_merge_commit"),
            "IMPLEMENTATION_BOUNDARY_DIVERGENCE")
    boundary = instant(activation.get("post_repair_source_capture_not_before_utc"),"BOUNDARY_CLOCK_INVALID")
    require(status in {"CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR","ACTIVE_POST_REPAIR_FLOOR"},
            "UNKNOWN_ACTIVATION_PHASE")
    floor_text = contract.get("prospective_eligibility_start")
    require(floor_text == rule.get("prospective_eligibility_start"),
            "ACTIVATION_FLOOR_DIVERGENCE")
    core = [i for i in freeze.get("families",[]) if i.get("family_id") in CORE]
    require({i.get("family_id") for i in core} == CORE and len(core) == 3,
            "CORE_FAMILY_MISSING_OR_DUPLICATE")
    require(all(i.get("prospective_eligibility_start") == floor_text for i in core),
            "CORE_FAMILY_FLOOR_DIVERGENCE")
    require(all(i.get("status") == "READY" and i.get("candidate_decision_contract_status") == "READY" for i in core),
            "CORE_FAMILY_NOT_READY")
    if status == "CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR":
        require(state == QUARANTINE and rule.get("collection_state") == QUARANTINE,
                "QUARANTINE_STATE_MISMATCH")
        require(rule.get("containment_floor_sentinel") is True,"QUARANTINE_SENTINEL_MISSING")
        require(activation.get("activation_pr") is None,"QUARANTINE_HAS_ACTIVATION_AUTHORITY")
        require(floor_text == contract["p0_containment"]["containment_floor_sentinel"],
                "QUARANTINE_FLOOR_CHANGED")
        if runtime is not None:
            require(runtime.get("collection_state") == QUARANTINE and runtime.get("eligible_prospective_rows") == 0,
                    "RUNTIME_QUARANTINE_MISMATCH")
        return "QUARANTINED_VALIDATED_NO_COLLECTION"
    require(state == ACTIVE and rule.get("collection_state") == ACTIVE,"ACTIVE_STATE_MISMATCH")
    require(rule.get("containment_floor_sentinel") is False,"ACTIVE_STILL_SENTINEL")
    require(bool(re.fullmatch(r"#[1-9][0-9]*",str(activation.get("activation_pr")))),
            "ACTIVATION_PR_MISSING")
    require(bool(re.fullmatch(r"[0-9a-f]{64}",str(activation.get("source_readiness_manifest_sha256")))),
            "SOURCE_READINESS_DIGEST_MISSING")
    receipt=activation.get("source_readiness_receipt_path")
    require(isinstance(receipt,str) and receipt.startswith("06_RESEARCH_LAB/shared_row_model_tournament_v1/")
            and ".." not in receipt,"SOURCE_READINESS_RECEIPT_UNBOUND")
    ready=instant(activation.get("source_readiness_complete_at_utc"),"READINESS_CLOCK_INVALID")
    approved=instant(activation.get("activation_recorded_at_utc"),"ACTIVATION_CLOCK_INVALID")
    floor=instant(floor_text,"ACTIVE_FLOOR_INVALID")
    require(boundary < ready <= approved < floor,"BACKDATED_OR_PRE_READINESS_ACTIVATION")
    if runtime is not None:
        require(runtime.get("collection_state") == ACTIVE and
                runtime.get("core_prospective_eligibility_status") == status and
                runtime.get("core_prospective_eligibility_start") == floor_text,
                "RUNTIME_ACTIVE_MISMATCH")
    return "ACTIVE_DECLARATIONS_COHERENT_EXTERNAL_WITNESSES_UNVERIFIED"
