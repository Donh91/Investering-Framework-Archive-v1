#!/usr/bin/env python3
"""Validate public cross-repository agent-context invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = ROOT / "00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md"
CONTEXT_MAP = ROOT / "00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json"
ROUND3 = ROOT / "06_RESEARCH_LAB/round3_new_information_v1"

REQUIRED_MARKERS = {
    "README.md": ["CROSS_REPO_DATA_BOUNDARY.md", "Donh91/secrets"],
    "AGENTS.md": ["CROSS_REPO_AGENT_CONTEXT_MAP.json", "Donh91/secrets"],
    "00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md": [
        "CROSS_REPO_DATA_BOUNDARY.md",
        "Donh91/secrets",
    ],
    "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md": [
        "CROSS_REPO_AGENT_CONTEXT_MAP.json",
        "Donh91/secrets",
    ],
    "research/codex/README.md": ["CROSS_REPO_DATA_BOUNDARY.md", "restricted"],
    "07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md": [
        "CROSS_REPO_AGENT_CONTEXT_MAP.json",
        "Donh91/secrets",
    ],
    "research/specialists/SPECIALIST_ARCHITECTURE_v1.md": [
        "CROSS_REPO_AGENT_CONTEXT_MAP.json",
        "Donh91/secrets",
    ],
    "00_ARCHIVE_CONTROL/source_recovery_controller_v1/POLICY.json": [
        "IMMUTABLE_POINTER_AND_VALUE_FREE_HEALTH_ONLY",
        "Donh91/secrets",
    ],
    "06_RESEARCH_LAB/round3_new_information_v1/README.md": [
        "PROSPECTIVE_COLLECTION_ONLY",
        "Donh91/secrets",
        "PRIVATE_COLLECTION_HOLD_RECEIPT_2026-08-23.json",
    ],
    ".agents/skills/canonical-context-router/SKILL.md": ["CROSS_REPO_DATA_BOUNDARY.md"],
    ".agents/skills/archive-governance/SKILL.md": ["CROSS_REPO_DATA_BOUNDARY.md"],
    ".agents/skills/prospective-evidence-ledger/SKILL.md": ["CROSS_REPO_DATA_BOUNDARY.md"],
    ".agents/skills/research-lab-red-team/SKILL.md": ["CROSS_REPO_DATA_BOUNDARY.md"],
    ".agents/skills/codex-intake/SKILL.md": ["CROSS_REPO_DATA_BOUNDARY.md"],
    ".agents/skills/developer-source-research/SKILL.md": [
        "CROSS_REPO_DATA_BOUNDARY.md",
        "Donh91/secrets",
    ],
}

ACTIVE_ROUTE_FILES = [
    "README.md",
    "AGENTS.md",
    "00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md",
    "00_FMOS/ARCHITECTURE.md",
    "00_FMOS/WP00_PATH_OWNER_REGISTRY_v1.md",
    "01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md",
    "03_WEEKLY_OPERATIONS/automation_patches/2026-07-11__github-archive-sync-backup-v1-4__canonical.md",
    "03_WEEKLY_OPERATIONS/automation_patches/2026-07-20__repository-preflight-and-data-gate-receipt-repair-v1__operational.md",
    "research/codex/README.md",
    "06_RESEARCH_LAB/round3_new_information_v1/README.md",
]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid or missing JSON {path.relative_to(ROOT)}: {exc}", errors)
        return {}


def main() -> int:
    errors: list[str] = []

    for path in (BOUNDARY, CONTEXT_MAP):
        if not path.is_file():
            fail(f"missing canonical cross-repo file: {path.relative_to(ROOT)}", errors)

    if CONTEXT_MAP.is_file():
        data = load_json(CONTEXT_MAP, errors)
        if data.get("contract") != "CROSS_REPO_AGENT_CONTEXT_MAP_v1":
            fail("unexpected context-map contract", errors)
        if data.get("round3_firewall", {}).get("hypothesis_testing") != "OFF":
            fail("Round 3 hypothesis firewall is not OFF", errors)
        if data.get("round3_firewall", {}).get("outcome_scoring") != "OFF":
            fail("Round 3 outcome-scoring firewall is not OFF", errors)
        routes = data.get("routes", [])
        if not routes:
            fail("context map has no routes", errors)
        for index, route in enumerate(routes):
            for key in (
                "id",
                "kind",
                "required_repositories",
                "required_canonical_files",
                "private_data_authority",
                "forbidden_actions",
            ):
                if not route.get(key):
                    fail(f"route {index} missing {key}", errors)

    for relative, markers in REQUIRED_MARKERS.items():
        path = ROOT / relative
        if not path.is_file():
            fail(f"missing entrypoint: {relative}", errors)
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                fail(f"{relative} missing marker {marker}", errors)

    for relative in ACTIVE_ROUTE_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "Donh91/Cycle-navigator-" in text or "`Cycle-navigator-`" in text:
            fail(f"active route still uses retired repository name: {relative}", errors)

    status = load_json(ROUND3 / "COLLECTION_STATUS.json", errors)
    expected = {
        "collection_mode": "PROSPECTIVE_COLLECTION_ONLY",
        "restricted_private_collection_active": False,
        "hypothesis_testing_active": False,
        "outcome_scoring_active": False,
        "raw_provider_values_public_repo_allowed": False,
        "restricted_analysis_authorized": False,
        "restricted_terms_readiness_status": "PASS_FAIL_CLOSED_HOLD",
        "restricted_reactivation_review_candidates": [],
        "first_post_reactivation_capture_requirement": "SCHEMA_V2_HEALTH_ONLY_BEFORE_ANY_ANALYSIS_LINKAGE",
    }
    for key, value in expected.items():
        if status.get(key) != value:
            fail(f"Round 3 status invariant failed: {key}", errors)

    if status.get("programme_status") != (
        "CONTRACT_FROZEN_V2_MATERIALIZED_PRIVATE_COLLECTION_HOLD_TERMS_AND_PROVENANCE"
    ):
        fail("Round 3 current programme status is not fail-closed", errors)

    hold = load_json(ROUND3 / "PRIVATE_COLLECTION_HOLD_RECEIPT_2026-08-23.json", errors)
    if hold.get("current_collection_active") is not False:
        fail("private hold receipt does not close collection", errors)
    if hold.get("analysis_authorized") is not False:
        fail("private hold receipt authorizes analysis", errors)
    if hold.get("private_health_readback_merge_commit") != status.get(
        "restricted_health_readback_commit"
    ):
        fail("private health readback binding drift", errors)
    if hold.get("dataset_manifest_sha256") != status.get("restricted_dataset_manifest_sha256"):
        fail("private dataset-manifest binding drift", errors)
    if hold.get("legacy_provenance_quarantine_count") != 11:
        fail("unexpected legacy provenance quarantine count", errors)
    if hold.get("schema_v2_capture_count") != 0:
        fail("unexpected schema-v2 capture count before reactivation", errors)

    terms_requirements = load_json(ROUND3 / "PROVIDER_TERMS_EVIDENCE_REQUIREMENTS_v1.json", errors)
    if terms_requirements.get("collection_activation_authorized") is not False:
        fail("provider terms requirements authorize collection", errors)
    if terms_requirements.get("analysis_authorized") is not False:
        fail("provider terms requirements authorize analysis", errors)
    if terms_requirements.get("activation_gate", {}).get(
        "separate_reviewed_reactivation_pull_request_required"
    ) is not True:
        fail("provider terms reactivation review gate is missing", errors)
    if terms_requirements.get("activation_gate", {}).get(
        "health_only_validation_before_any_analysis"
    ) is not True:
        fail("provider terms first-capture health-only gate is missing", errors)
    if terms_requirements.get("activation_gate", {}).get(
        "sc06_requires_separate_runtime_storage_and_paid_infrastructure_authorization"
    ) is not True:
        fail("SC06 separate runtime/storage authorization gate is missing", errors)

    readiness = load_json(ROUND3 / "PRIVATE_PROVIDER_TERMS_READINESS_RECEIPT_2026-08-23.json", errors)
    readiness_expected = {
        "restricted_repository": "Donh91/secrets",
        "restricted_merge_commit": "e5e7a95e70642ac063484375f28fa62ecefbd633",
        "restricted_attestation_path": "GOVERNANCE/PROVIDER_TERMS_ATTESTATION.json",
        "restricted_attestation_contract": "ROUND3_PROVIDER_TERMS_ATTESTATION_v1",
        "restricted_readiness_validator_path": "scripts/validate_provider_terms_readiness.py",
        "restricted_readiness_contract": "ROUND3_PROVIDER_TERMS_READINESS_GATE_v1",
        "restricted_readiness_status": "PASS_FAIL_CLOSED_HOLD",
        "restricted_collection_active": False,
        "restricted_analysis_authorized": False,
        "reactivation_review_candidates": [],
        "sc06_separate_runtime_storage_authorization_required": True,
        "first_post_reactivation_capture_requirement": "SCHEMA_V2_HEALTH_ONLY_BEFORE_ANY_ANALYSIS_LINKAGE",
        "separate_reviewed_reactivation_pull_request_required": True,
        "provider_values_in_public_receipt": False,
        "credentials_in_public_receipt": False,
    }
    for key, value in readiness_expected.items():
        if readiness.get(key) != value:
            fail(f"private terms readiness receipt invariant failed: {key}", errors)

    if status.get("restricted_terms_readiness_merge_commit") != readiness.get("restricted_merge_commit"):
        fail("private terms readiness merge binding drift", errors)
    if status.get("restricted_terms_attestation_path") != readiness.get("restricted_attestation_path"):
        fail("private terms attestation path binding drift", errors)
    if status.get("restricted_terms_readiness_contract") != readiness.get("restricted_readiness_contract"):
        fail("private readiness contract binding drift", errors)
    if status.get("restricted_terms_readiness_status") != readiness.get("restricted_readiness_status"):
        fail("private readiness status binding drift", errors)

    private_binding = terms_requirements.get("private_machine_readiness_binding", {})
    if private_binding.get("restricted_merge_commit") != readiness.get("restricted_merge_commit"):
        fail("terms requirements private merge binding drift", errors)
    if private_binding.get("current_status") != "PASS_FAIL_CLOSED_HOLD":
        fail("terms requirements do not preserve fail-closed hold", errors)

    if errors:
        print("CROSS_REPO_CONTEXT_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CROSS_REPO_CONTEXT_VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
