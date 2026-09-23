"""Bounded P1 Project -> CA project-memory substrate.

Research/shadow only. This module deliberately has no Project -> CA binding,
market, alert, portfolio, or trading authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

TOKEN_STATES = frozenset({"NO_TOKEN_OBSERVED", "TOKEN_CANDIDATE", "TOKEN_BOUND", "TOKEN_CONFLICT"})
IDENTITY_ROOT_TYPES = frozenset({
    "AUTHENTICATED_PROJECT_ROOT",
    "PROJECT_CONTROLLED_ONCHAIN_ROOT",
    "BOUNDED_ARCHIVE_ROOT",
})


class ProjectMemoryError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectMemoryError(f"{field} is required")
    return value.strip()


def _source_observation(row: Mapping[str, Any]) -> dict[str, Any]:
    source_ref = _require_text(row.get("source_ref"), "source_ref")
    observed_at = _require_text(row.get("observed_at_utc"), "observed_at_utc")
    available_at = row.get("available_at_utc")
    if available_at is not None:
        available_at = _require_text(available_at, "available_at_utc")
    content_hash = _require_text(row.get("content_sha256"), "content_sha256")
    auth = _require_text(row.get("authentication_state"), "authentication_state")
    conflict = _require_text(row.get("conflict_state"), "conflict_state")
    return {
        "source_ref": source_ref,
        "observed_at_utc": observed_at,
        "available_at_utc": available_at,
        "content_sha256": content_hash,
        "authentication_state": auth,
        "conflict_state": conflict,
    }


def _identity(identity: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    roots = []
    for root in identity.get("control_roots", []):
        root_type = _require_text(root.get("root_type"), "root_type")
        root_value = _require_text(root.get("root_value"), "root_value")
        if root_type not in IDENTITY_ROOT_TYPES:
            raise ProjectMemoryError("identity root is not authoritative")
        roots.append({"root_type": root_type, "root_value": root_value})
    if not roots:
        raise ProjectMemoryError("at least one bounded authoritative control root is required")
    roots = sorted(roots, key=lambda x: (x["root_type"], x["root_value"]))
    aliases = sorted({str(x).strip() for x in identity.get("aliases", []) if str(x).strip()})
    normalized = {"control_roots": roots, "aliases": aliases}
    # Aliases are metadata only and MUST NOT affect stable project identity.
    identity_key = _sha256(roots)
    return normalized, identity_key


def build_project_memory(
    *,
    method_version: str,
    frozen_at_utc: str,
    eligibility_manifest_sha256: str,
    discovery: Mapping[str, Any],
    project_identity: Mapping[str, Any],
    source_observations: Sequence[Mapping[str, Any]],
    project_memory_before: Mapping[str, Any] | None = None,
    material_delta: Mapping[str, Any] | None = None,
    token_state: str = "NO_TOKEN_OBSERVED",
    ca_candidates: Sequence[Mapping[str, Any]] = (),
    authority: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one immutable P1 snapshot.

    No outcome field is accepted or required. A token/CA candidate cannot confer
    project identity or binding authority here.
    """
    method_version = _require_text(method_version, "method_version")
    frozen_at_utc = _require_text(frozen_at_utc, "frozen_at_utc")
    eligibility_manifest_sha256 = _require_text(
        eligibility_manifest_sha256, "eligibility_manifest_sha256"
    )
    if token_state not in TOKEN_STATES:
        raise ProjectMemoryError("invalid token_state")

    identity, identity_key = _identity(project_identity)
    sources = [_source_observation(x) for x in source_observations]
    sources = sorted(sources, key=lambda x: (
        x["source_ref"], x["observed_at_utc"], x["content_sha256"]
    ))
    discovery_frozen = json.loads(_canonical(discovery))

    project_trial_id = "PCA-P1-" + identity_key[:20]
    before = json.loads(_canonical(project_memory_before)) if project_memory_before else None
    lineage = {
        "supersedes_snapshot_sha256": before.get("snapshot_sha256") if before else None,
        "append_only": True,
    }
    safe_authority = {
        "shadow_only": True,
        "project_ca_binding": False,
        "portfolio_action": False,
        "automatic_trading": False,
        "user_alerts": False,
        "production_activation": False,
    }
    if authority:
        for key, value in authority.items():
            if key in safe_authority and value is True and safe_authority[key] is False:
                raise ProjectMemoryError(f"P1 cannot grant {key} authority")

    snapshot = {
        "contract": "PROJECT_CA_PROJECT_MEMORY_P1_v1",
        "project_trial_id": project_trial_id,
        "method_version": method_version,
        "frozen_at_utc": frozen_at_utc,
        "eligibility_manifest_sha256": eligibility_manifest_sha256,
        "discovery": discovery_frozen,
        "project_identity": identity,
        "source_observations": sources,
        "project_memory_before": before,
        "material_delta": json.loads(_canonical(material_delta or {"state": "UNKNOWN"})),
        "token_state": token_state,
        "ca_candidates": json.loads(_canonical(list(ca_candidates))),
        "lineage": lineage,
        "authority": safe_authority,
    }
    # Hash the current state only. Embedded prior snapshots remain lineage evidence,
    # but are excluded from the current-state hash to avoid recursive growth semantics.
    hash_view = dict(snapshot)
    hash_view["project_memory_before"] = (
        {"snapshot_sha256": before.get("snapshot_sha256")} if before else None
    )
    snapshot["snapshot_sha256"] = _sha256(hash_view)
    return snapshot


def supersede_project_memory(previous: Mapping[str, Any], **changes: Any) -> dict[str, Any]:
    """Create a new snapshot while preserving the previous snapshot verbatim."""
    required = {
        "method_version": previous["method_version"],
        "eligibility_manifest_sha256": previous["eligibility_manifest_sha256"],
        "discovery": previous["discovery"],
        "project_identity": previous["project_identity"],
        "source_observations": previous["source_observations"],
        "project_memory_before": previous,
        "token_state": previous["token_state"],
        "ca_candidates": previous["ca_candidates"],
    }
    required.update(changes)
    result = build_project_memory(**required)
    if result["project_trial_id"] != previous["project_trial_id"]:
        raise ProjectMemoryError("supersession cannot change project identity lineage")
    return result
