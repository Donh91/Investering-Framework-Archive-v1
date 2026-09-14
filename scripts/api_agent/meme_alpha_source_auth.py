from __future__ import annotations

import json
from typing import Any

SOURCE_AUTH_STATES = {
    "NOT_APPLICABLE",
    "UNASSESSED",
    "CANDIDATE",
    "AUTHENTICATED_FIRST_PARTY",
    "INVALIDATED_FIRST_PARTY",
    "CONFLICTED",
}

SOURCE_AUTH_SCOPES = {
    "NONE",
    "PROJECT_SOURCE",
    "TOKEN_SOURCE",
    "TOKEN_CA_BINDING",
    "CTO_COMMUNITY",
}

ANCHOR_CATEGORIES = {
    "OFFICIAL_WEBSITE",
    "OFFICIAL_DOCS",
    "OFFICIAL_SOCIAL",
    "DOMAIN_CONTROL",
    "ORGANIZATION_ANCESTRY",
    "ONCHAIN_PROJECT_CONTROL",
    "SIGNED_RELEASE",
    "OTHER_EXTERNAL",
}

FIRST_PARTY_TASK_TERMS = (
    "official",
    "first-party",
    "first party",
    "github",
    "repository",
    "repo",
    "provenance",
    "developer",
    "dev team",
    "owned by",
    "mascot",
    "easter egg",
    "canonical",
)

FIRST_PARTY_FINDING_TERMS = (
    "official",
    "first-party",
    "first party",
    "project-owned",
    "project controlled",
    "canonical mascot",
    "official mascot",
    "official token",
)


def source_authentication_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "scope",
            "state",
            "claimed_entity",
            "subject",
            "first_party_claim_allowed",
            "external_trust_anchors",
            "repository_forensics",
            "onchain_bindings",
            "red_team_findings",
            "gate_reasons",
        ],
        "properties": {
            "scope": {"type": "string", "enum": sorted(SOURCE_AUTH_SCOPES)},
            "state": {"type": "string", "enum": sorted(SOURCE_AUTH_STATES)},
            "claimed_entity": {"type": "string"},
            "subject": {"type": "string"},
            "first_party_claim_allowed": {"type": "boolean"},
            "external_trust_anchors": {
                "type": "array",
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "category",
                        "locator",
                        "evidence",
                        "external_to_subject",
                        "source_controlled",
                        "independent",
                    ],
                    "properties": {
                        "category": {"type": "string", "enum": sorted(ANCHOR_CATEGORIES)},
                        "locator": {"type": "string"},
                        "evidence": {"type": "string"},
                        "external_to_subject": {"type": "boolean"},
                        "source_controlled": {"type": "boolean"},
                        "independent": {"type": "boolean"},
                    },
                },
            },
            "repository_forensics": {
                "type": "array",
                "maxItems": 10,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["signal", "severity", "evidence"],
                    "properties": {
                        "signal": {"type": "string"},
                        "severity": {"type": "string", "enum": ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]},
                        "evidence": {"type": "string"},
                    },
                },
            },
            "onchain_bindings": {
                "type": "array",
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["relation", "confidence", "evidence"],
                    "properties": {
                        "relation": {"type": "string"},
                        "confidence": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                        "evidence": {"type": "string"},
                    },
                },
            },
            "red_team_findings": {
                "type": "array",
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["hypothesis", "status", "evidence"],
                    "properties": {
                        "hypothesis": {"type": "string"},
                        "status": {"type": "string", "enum": ["CLEAR", "UNRESOLVED", "BLOCKER"]},
                        "evidence": {"type": "string"},
                    },
                },
            },
            "gate_reasons": {"type": "array", "items": {"type": "string"}},
        },
    }


def default_source_authentication() -> dict[str, Any]:
    return {
        "scope": "NONE",
        "state": "NOT_APPLICABLE",
        "claimed_entity": "",
        "subject": "",
        "first_party_claim_allowed": False,
        "external_trust_anchors": [],
        "repository_forensics": [],
        "onchain_bindings": [],
        "red_team_findings": [],
        "gate_reasons": [],
    }


def task_requires_source_authentication(task: dict[str, Any]) -> bool:
    # Hydrated private context is supporting evidence, not task intent. Ignoring it
    # prevents an unrelated wallet task from becoming provenance-gated simply
    # because an attached file happens to mention GitHub or an official account.
    intent = {key: value for key, value in task.items() if key != "runtime_hydration"}
    text = json.dumps(intent, sort_keys=True).lower()
    return any(term in text for term in FIRST_PARTY_TASK_TERMS)


def _valid_external_anchors(packet: dict[str, Any]) -> list[dict[str, Any]]:
    anchors = packet.get("external_trust_anchors")
    if not isinstance(anchors, list):
        return []
    valid: list[dict[str, Any]] = []
    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        if anchor.get("category") not in ANCHOR_CATEGORIES:
            continue
        if not anchor.get("external_to_subject"):
            continue
        if not anchor.get("source_controlled"):
            continue
        if not anchor.get("independent"):
            continue
        valid.append(anchor)
    return valid


def _has_blocking_red_team(packet: dict[str, Any]) -> bool:
    rows = packet.get("red_team_findings")
    if not isinstance(rows, list):
        return False
    return any(isinstance(row, dict) and row.get("status") in {"UNRESOLVED", "BLOCKER"} for row in rows)


def _has_blocking_repo_forensics(packet: dict[str, Any]) -> bool:
    rows = packet.get("repository_forensics")
    if not isinstance(rows, list):
        return False
    return any(isinstance(row, dict) and row.get("severity") == "BLOCKER" for row in rows)


def _has_high_onchain_binding(packet: dict[str, Any]) -> bool:
    rows = packet.get("onchain_bindings")
    if not isinstance(rows, list):
        return False
    return any(isinstance(row, dict) and row.get("confidence") == "HIGH" and str(row.get("evidence") or "").strip() for row in rows)


def apply_source_authentication_gate(
    output: dict[str, Any],
    task: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    cfg = policy.get("source_authentication") if isinstance(policy.get("source_authentication"), dict) else {}
    packet = output.get("source_authentication")
    if not isinstance(packet, dict):
        packet = default_source_authentication()
        output["source_authentication"] = packet

    required = task_requires_source_authentication(task)
    minimum_anchors = int(cfg.get("minimum_external_trust_anchors", 2))
    minimum_categories = int(cfg.get("minimum_independent_anchor_categories", 2))
    require_onchain_for_token = bool(cfg.get("require_high_confidence_onchain_binding_for_token_ca_claim", True))
    block_on_red_team = bool(cfg.get("block_on_unresolved_red_team", True))
    block_on_repo_forensics = bool(cfg.get("block_on_repo_forensics_blocker", True))

    reasons: list[str] = []
    valid_anchors = _valid_external_anchors(packet)
    categories = {str(anchor.get("category")) for anchor in valid_anchors}
    state = str(packet.get("state") or "UNASSESSED")
    scope = str(packet.get("scope") or "NONE")

    allowed = True
    if not required and scope in {"NONE", "CTO_COMMUNITY"}:
        allowed = False
        if scope == "NONE":
            state = "NOT_APPLICABLE"
    else:
        if state != "AUTHENTICATED_FIRST_PARTY":
            allowed = False
            reasons.append("STATE_NOT_AUTHENTICATED_FIRST_PARTY")
        if len(valid_anchors) < minimum_anchors:
            allowed = False
            reasons.append("INSUFFICIENT_EXTERNAL_TRUST_ANCHORS")
        if len(categories) < minimum_categories:
            allowed = False
            reasons.append("INSUFFICIENT_INDEPENDENT_ANCHOR_CATEGORIES")
        if scope == "TOKEN_CA_BINDING" and require_onchain_for_token and not _has_high_onchain_binding(packet):
            allowed = False
            reasons.append("HIGH_CONFIDENCE_ONCHAIN_BINDING_REQUIRED")
        if block_on_red_team and _has_blocking_red_team(packet):
            allowed = False
            reasons.append("RED_TEAM_UNRESOLVED_OR_BLOCKING")
        if block_on_repo_forensics and _has_blocking_repo_forensics(packet):
            allowed = False
            reasons.append("REPOSITORY_FORENSICS_BLOCKER")
        if state in {"INVALIDATED_FIRST_PARTY", "CONFLICTED"}:
            allowed = False
            reasons.append("SOURCE_STATE_BLOCKS_FIRST_PARTY")

    packet["first_party_claim_allowed"] = allowed
    packet["gate_reasons"] = sorted(set(reasons))
    if required and not allowed and state == "AUTHENTICATED_FIRST_PARTY":
        packet["state"] = "CANDIDATE"
    elif required and scope == "NONE":
        packet["scope"] = "PROJECT_SOURCE"
        packet["state"] = "CANDIDATE"
        packet["gate_reasons"] = sorted(set(packet["gate_reasons"] + ["SOURCE_AUTH_SCOPE_REQUIRED"]))

    if required and not packet["first_party_claim_allowed"]:
        if output.get("status") == "READY":
            output["status"] = "DEGRADED"
        uncertainty = "SOURCE_AUTHENTICATION_GATE_BLOCKED_FIRST_PARTY_CLAIM"
        if uncertainty not in output.setdefault("uncertainties", []):
            output["uncertainties"].append(uncertainty)
        if bool(cfg.get("sanitize_unauthenticated_first_party_findings", True)):
            kept: list[str] = []
            moved: list[str] = []
            for item in output.get("verified_findings", []):
                if not isinstance(item, str):
                    kept.append(item)
                    continue
                lower = item.lower()
                if any(term in lower for term in FIRST_PARTY_FINDING_TERMS):
                    moved.append(item)
                else:
                    kept.append(item)
            if moved:
                output["verified_findings"] = kept
                for item in moved:
                    output["uncertainties"].append("AUTH_GATED_UNVERIFIED_FIRST_PARTY_CLAIM: " + item)

    return output


def source_authentication_instruction(policy: dict[str, Any]) -> str:
    cfg = policy.get("source_authentication") if isinstance(policy.get("source_authentication"), dict) else {}
    minimum_anchors = int(cfg.get("minimum_external_trust_anchors", 2))
    minimum_categories = int(cfg.get("minimum_independent_anchor_categories", 2))
    return (
        "Treat discovery and source authentication as separate stages. Repository branding, internal README claims, realistic code, "
        "commit chronology, exact contract addresses, GitHub Verified signatures and self-asserted official status do not prove first-party ownership. "
        f"For any official/first-party/project-owned claim require at least {minimum_anchors} independent project-controlled anchors across at least "
        f"{minimum_categories} external categories, and actively red-team look-alike repositories, disposable authors, copied code, account age, alternate repos, "
        "domain/social mismatches and chronology. For TOKEN_CA_BINDING claims require a HIGH-confidence on-chain binding. "
        "If these conditions are not met, keep the source CANDIDATE/CONFLICTED/INVALIDATED and set first_party_claim_allowed false. "
        "A community CTO may still be real even when the original first-party provenance is false; score those theses separately."
    )
