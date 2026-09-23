"""Bounded P2 exact Project -> CA binding state machine.

Research/shadow only. Consumes a P1-frozen project trial and bounded evidence.
It grants no market, alert, portfolio, production, or trading authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

BINDING_STATES = frozenset({
    "UNBOUND", "CANDIDATE_BINDING", "BOUND_HIGH", "CONFLICTED",
    "SUPERSEDED_WITH_PROOF", "REVOKED",
})
RELATIONSHIP_TYPES = frozenset({
    "FIRST_PARTY_EXPLICIT_CA",
    "PROJECT_CONTROLLED_ONCHAIN_RELATION",
    "FACTORY_LAUNCH_CANDIDATE_ONLY",
    "SOCIAL_CANDIDATE_ONLY",
    "MIGRATION_WITH_CONTINUITY_PROOF",
    "RELAUNCH_WITH_CONTINUITY_PROOF",
    "UNKNOWN",
})
HIGH_RELATIONSHIPS = frozenset({
    "FIRST_PARTY_EXPLICIT_CA",
    "PROJECT_CONTROLLED_ONCHAIN_RELATION",
    "MIGRATION_WITH_CONTINUITY_PROOF",
    "RELAUNCH_WITH_CONTINUITY_PROOF",
})
CONTINUITY_RELATIONSHIPS = frozenset({
    "MIGRATION_WITH_CONTINUITY_PROOF",
    "RELAUNCH_WITH_CONTINUITY_PROOF",
})


class ProjectCABindingError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectCABindingError(f"{field} is required")
    return value.strip()


def _token_key(chain_id: Any, token_ca: Any) -> tuple[str, str]:
    chain = _text(str(chain_id) if chain_id is not None else None, "chain_id")
    ca = _text(token_ca, "token_ca").lower()
    return chain, ca


def _evidence(row: Mapping[str, Any]) -> dict[str, Any]:
    observed = _text(row.get("observed_at_utc"), "observed_at_utc")
    available = row.get("available_at_utc")
    if available is not None:
        available = _text(available, "available_at_utc")
    return {
        "evidence_ref": _text(row.get("evidence_ref"), "evidence_ref"),
        "observed_at_utc": observed,
        "available_at_utc": available,
        "evidence_sha256": _text(row.get("evidence_sha256"), "evidence_sha256"),
        "authentication_state": _text(row.get("authentication_state"), "authentication_state"),
        "conflict_state": _text(row.get("conflict_state"), "conflict_state"),
    }


def build_binding(
    *,
    project_memory: Mapping[str, Any],
    chain_id: Any,
    token_ca: str,
    relationship_type: str,
    binding_provenance: Sequence[Mapping[str, Any]],
    first_candidate_at_utc: str,
    onchain_verification: Mapping[str, Any],
    project_control_binding: Mapping[str, Any],
    conflicts: Sequence[Mapping[str, Any]] = (),
    continuity_proof: Mapping[str, Any] | None = None,
    supersedes_binding: Mapping[str, Any] | None = None,
    explicit_revocation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate one exact chain+CA binding without scores or outcome data."""
    if project_memory.get("contract") != "PROJECT_CA_PROJECT_MEMORY_P1_v1":
        raise ProjectCABindingError("P2 requires a P1-frozen project memory")
    project_trial_id = _text(project_memory.get("project_trial_id"), "project_trial_id")
    _text(project_memory.get("snapshot_sha256"), "project_memory.snapshot_sha256")
    p1_authority = project_memory.get("authority")
    if p1_authority is not None:
        if p1_authority.get("project_ca_binding") is True or p1_authority.get("project_to_ca_binding") is True:
            raise ProjectCABindingError("P1 input must not already grant Project-to-CA binding authority")
    chain, ca = _token_key(chain_id, token_ca)
    relationship_type = _text(relationship_type, "relationship_type")
    if relationship_type not in RELATIONSHIP_TYPES:
        raise ProjectCABindingError("invalid relationship_type")
    first_candidate_at_utc = _text(first_candidate_at_utc, "first_candidate_at_utc")
    evidence = [_evidence(x) for x in binding_provenance]
    evidence = sorted(evidence, key=lambda x: (
        x["evidence_ref"], x["observed_at_utc"], x["evidence_sha256"]
    ))
    conflict_rows = json.loads(_canonical(list(conflicts)))
    unresolved = [
        x for x in conflict_rows
        if str(x.get("state", "UNRESOLVED")).upper() not in {"RESOLVED", "SUPERSEDED_WITH_PROOF"}
    ]

    onchain_ok = (
        onchain_verification.get("verified") is True
        and str(onchain_verification.get("chain_id")) == chain
        and str(onchain_verification.get("token_ca", "")).lower() == ca
        and bool(onchain_verification.get("evidence_sha256"))
    )
    first_party_source_ok = any(
        x["authentication_state"] == "AUTHENTICATED_FIRST_PARTY"
        and x["conflict_state"] in {"NONE", "RESOLVED"}
        for x in evidence
    )
    project_control_ok = (
        project_control_binding.get("authenticated") is True
        and bool(project_control_binding.get("evidence_sha256"))
    )
    authenticated_relation_ok = (
        first_party_source_ok
        if relationship_type == "FIRST_PARTY_EXPLICIT_CA"
        else project_control_ok
    )
    if relationship_type in CONTINUITY_RELATIONSHIPS:
        authenticated_relation_ok = first_party_source_ok or project_control_ok
    timestamps_and_hashes_ok = bool(evidence) and all(
        x["available_at_utc"] is not None and x["evidence_sha256"] for x in evidence
    )
    relationship_supports_high = relationship_type in HIGH_RELATIONSHIPS
    continuity_required = relationship_type in CONTINUITY_RELATIONSHIPS
    continuity_ok = (
        not continuity_required
        or (
            continuity_proof is not None
            and continuity_proof.get("explicit") is True
            and bool(continuity_proof.get("evidence_sha256"))
        )
    )

    if explicit_revocation is not None:
        if explicit_revocation.get("explicit") is not True or not explicit_revocation.get("evidence_sha256"):
            raise ProjectCABindingError("revocation requires explicit hashed evidence")
        state = "REVOKED"
    elif unresolved:
        state = "CONFLICTED"
    elif (
        onchain_ok
        and authenticated_relation_ok
        and timestamps_and_hashes_ok
        and relationship_supports_high
        and continuity_ok
    ):
        state = "BOUND_HIGH"
    else:
        state = "CANDIDATE_BINDING"

    supersedes_id = None
    superseded_prior = None
    if supersedes_binding is not None:
        supersedes_id = _text(supersedes_binding.get("binding_id"), "supersedes_binding_id")
        if state == "BOUND_HIGH":
            if not continuity_required or not continuity_ok:
                raise ProjectCABindingError("supersession requires explicit continuity proof")
            superseded_prior = {
                "binding_id": supersedes_id,
                "prior_state": supersedes_binding.get("binding_state"),
                "lineage_state": "SUPERSEDED_WITH_PROOF",
                "prior_chain_id": supersedes_binding.get("chain_id"),
                "prior_token_ca": supersedes_binding.get("token_ca"),
            }

    identity = {
        "project_trial_id": project_trial_id,
        "chain_id": chain,
        "token_ca": ca,
        "relationship_type": relationship_type,
        "first_candidate_at_utc": first_candidate_at_utc,
    }
    binding_id = "PCA-P2-" + _sha256(identity)[:20]
    bound_at = None
    if state == "BOUND_HIGH":
        bound_at = max(x["observed_at_utc"] for x in evidence)

    return {
        "contract": "PROJECT_CA_EXACT_BINDING_P2_v1",
        "binding_id": binding_id,
        "project_trial_id": project_trial_id,
        "chain_id": chain,
        "token_ca": ca,
        "relationship_type": relationship_type,
        "binding_state": state,
        "binding_provenance": evidence,
        "first_candidate_at_utc": first_candidate_at_utc,
        "bound_high_at_utc_or_null": bound_at,
        "conflict_ids": [x.get("conflict_id") for x in conflict_rows if x.get("conflict_id")],
        "onchain_verification": json.loads(_canonical(onchain_verification)),
        "project_control_binding": json.loads(_canonical(project_control_binding)),
        "continuity_proof": json.loads(_canonical(continuity_proof)) if continuity_proof else None,
        "supersedes_binding_id_or_null": supersedes_id,
        "superseded_prior_binding": superseded_prior,
        "authority": {
            "shadow_only": True,
            "portfolio_action": False,
            "automatic_trading": False,
            "user_alerts": False,
            "production_activation": False,
        },
        "receipt_sha256": "",
    } | {"receipt_sha256": _sha256({
        "identity": identity,
        "state": state,
        "evidence": evidence,
        "conflicts": conflict_rows,
        "onchain": onchain_verification,
        "project_control": project_control_binding,
        "continuity": continuity_proof,
        "supersedes": supersedes_id,
        "revocation": explicit_revocation,
    })}
