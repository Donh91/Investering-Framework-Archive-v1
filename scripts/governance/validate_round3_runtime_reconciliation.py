#!/usr/bin/env python3
"""Fail closed when public Round 3 runtime/readback semantics drift."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R3 = ROOT / "06_RESEARCH_LAB/round3_new_information_v1"


def load(name: str) -> dict:
    return json.loads((R3 / name).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    frozen = load("COLLECTION_STATUS.json")
    runtime = load("PRIVATE_RUNTIME_STATE.json")
    freshness = load("CROSS_REPO_FRESHNESS_POLICY_v1.json")

    def require(cond: bool, message: str) -> None:
        if not cond:
            errors.append(message)

    require(
        frozen.get("status_scope") == "FROZEN_PRE_REACTIVATION_SNAPSHOT_DO_NOT_USE_FOR_LIVE_PRIVATE_RUNTIME",
        "frozen COLLECTION_STATUS is not explicitly scoped as historical/pre-reactivation",
    )
    require(
        frozen.get("live_runtime_authority") == "06_RESEARCH_LAB/round3_new_information_v1/PRIVATE_RUNTIME_STATE.json",
        "frozen status does not point to live runtime authority",
    )
    require(
        frozen.get("cross_repo_freshness_policy") == "06_RESEARCH_LAB/round3_new_information_v1/CROSS_REPO_FRESHNESS_POLICY_v1.json",
        "frozen status does not point to freshness policy",
    )

    require(runtime.get("contract") == "ROUND3_PUBLIC_PRIVATE_RUNTIME_STATE_v1", "unexpected runtime contract")
    require(runtime.get("snapshot_semantics") == "POINT_IN_TIME_NOT_LIVE_CURRENT", "runtime snapshot must be point-in-time")
    require(runtime.get("live_current_claim_forbidden") is True, "live-current claim must be forbidden")
    require(runtime.get("private_governance_change_requires_public_reconciliation") is True, "governance reconciliation invariant missing")
    require(runtime.get("append_only_private_data_head_may_advance_without_invalidating_governance_binding") is True, "append-only data-head semantics missing")
    require(runtime.get("collection_mode") == "PROSPECTIVE_COLLECTION_ONLY", "unexpected collection mode")
    require(runtime.get("restricted_private_collection_active") is True, "restricted prospective collection should be active")
    require(runtime.get("public_framework_collection_active") is False, "public provider collection must remain off")
    require(runtime.get("hypothesis_testing_active") is False, "hypothesis testing must remain off")
    require(runtime.get("outcome_scoring_active") is False, "outcome scoring must remain off")
    require(runtime.get("restricted_analysis_authorized") is False, "restricted analysis must remain unauthorized")
    require(runtime.get("active_sources") == [
        "SC01_OKX_ETH_OI_HOURLY_V1",
        "SC03_OKX_ETH_REALIZED_FUNDING_V1",
        "SC14_DERIBIT_ETH_TRUE_25D_SKEW_V1",
    ], "unexpected active-source set")
    require(set(runtime.get("blocked_sources", {})) == {"SC06_BINANCE_ETH_BOOK_DEPTH_V1"}, "SC06 must remain the only blocked source")
    require(runtime.get("terms_attestation_status") == "PASSED_APPLICABLE_REGION_AND_OWNER_USE_ATTESTATION", "terms attestation state mismatch")
    require(runtime.get("first_post_reactivation_health_gate_status") == "PASS_COLLECTION_HEALTH_ONLY_ANALYSIS_NOT_AUTHORIZED", "first schema-v2 health gate not recorded as health-only pass")

    health = runtime.get("health_snapshot", {})
    require(health.get("contract") == "ROUND3_PRIVATE_DATA_HEALTH_v2", "unexpected private health contract")
    require(health.get("raw_file_count", 0) >= 15, "runtime snapshot regressed below reconciled raw-file floor")
    require(health.get("valid_file_count") == health.get("raw_file_count"), "not all snapshotted captures are integrity-valid")
    require(health.get("invalid_or_orphan_count") == 0, "invalid/orphan captures present")
    require(health.get("duplicate_payload_capture_count") == 0, "duplicate payload captures present")
    require(health.get("legacy_provenance_quarantine_count") == 11, "legacy quarantine count drift")
    require(health.get("post_floor_schema_v2_provenance_complete_count", 0) >= 4, "schema-v2 provenance-complete capture floor regressed")
    require(health.get("failures_present") is False, "private health failures present")

    firewall = runtime.get("scientific_firewall", {})
    require(firewall.get("round1_round2_evidence_status") == "CLOSED", "closed-evidence firewall drift")
    require(firewall.get("analysis_linkage_allowed") is False, "analysis linkage opened prematurely")
    require(firewall.get("auc_pvalue_effect_policy_pnl_allowed") is False, "performance inspection opened prematurely")
    require(firewall.get("threshold_window_direction_retuning_allowed") is False, "retuning opened prematurely")
    require(runtime.get("provider_values_in_public_state") is False, "provider values cannot enter public runtime state")
    require(runtime.get("credentials_in_public_state") is False, "credentials cannot enter public runtime state")

    require(freshness.get("contract") == "ROUND3_CROSS_REPO_FRESHNESS_POLICY_v1", "unexpected freshness contract")
    require(freshness.get("governance_binding", {}).get("drift_classification") == "PUBLIC_CONTROL_PLANE_STALE", "missing stale-state classification")
    require(freshness.get("governance_binding", {}).get("silent_inference_from_older_public_state_forbidden") is True, "silent stale inference must be forbidden")
    require(freshness.get("data_head_binding", {}).get("append_only_capture_head_may_advance_after_snapshot") is True, "append-only head advancement rule missing")
    require(freshness.get("data_head_binding", {}).get("public_state_must_not_claim_live_current") is True, "public live-current claim prohibition missing")

    if errors:
        print("ROUND3_RUNTIME_RECONCILIATION_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ROUND3_RUNTIME_RECONCILIATION_PASS")
    print("PRIVATE_GOVERNANCE_AUTHORITY", runtime["private_governance_authority_commit"])
    print("PRIVATE_HEALTH_SNAPSHOT", runtime["private_health_snapshot_commit"])
    print("RAW_FILE_COUNT", health["raw_file_count"])
    print("SCHEMA_V2_POST_FLOOR", health["post_floor_schema_v2_provenance_complete_count"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
