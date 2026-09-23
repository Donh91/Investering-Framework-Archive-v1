"""P1 Project->CA project-memory substrate.

Research-only. Persists/fingerprints pre-token project observations without
granting project->token binding, trading, alert, or production authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

TOKEN_STATES = frozenset({"NO_TOKEN_OBSERVED", "TOKEN_CANDIDATE", "TOKEN_BOUND", "TOKEN_CONFLICT"})


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value.strip()


def stable_project_trial_id(method_version: str, identity_anchor: Mapping[str, Any]) -> str:
    """Derive identity only from authenticated/bounded project lineage.

    Callers must not pass ticker/name/logo/alias as the identity anchor.
    """
    mv = _require_text(method_version, "method_version")
    if not isinstance(identity_anchor, Mapping) or not identity_anchor:
        raise ValueError("identity_anchor must be a non-empty mapping")
    forbidden = {"ticker", "symbol", "name", "logo", "alias", "aliases"}
    if forbidden.intersection(identity_anchor):
        raise ValueError("ticker/name/logo/alias cannot establish project identity")
    return "PCA-" + sha256_json({"method_version": mv, "identity_anchor": identity_anchor})[:24]


def source_observation(*, source_ref: str, observed_at: str, available_at: str | None,
                       content_hash: str, authentication_state: str,
                       conflict_state: str = "NONE") -> dict[str, Any]:
    return {
        "source_ref": _require_text(source_ref, "source_ref"),
        "observed_at": _require_text(observed_at, "observed_at"),
        "available_at": available_at if available_at else None,
        "content_hash": _require_text(content_hash, "content_hash"),
        "authentication_state": _require_text(authentication_state, "authentication_state"),
        "conflict_state": _require_text(conflict_state, "conflict_state"),
    }


def freeze_project_trial(*, method_version: str, frozen_at_utc: str,
                         eligibility_manifest_sha256: str, discovery: Mapping[str, Any],
                         project_identity: Mapping[str, Any],
                         source_observations: Sequence[Mapping[str, Any]],
                         project_memory_before: Mapping[str, Any] | None = None,
                         material_delta: Mapping[str, Any] | None = None,
                         token_state: str = "NO_TOKEN_OBSERVED",
                         ca_candidates: Sequence[Mapping[str, Any]] = (),
                         lineage: Mapping[str, Any] | None = None,
                         authority: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if token_state not in TOKEN_STATES:
        raise ValueError("invalid token_state")
    anchor = project_identity.get("identity_anchor") if isinstance(project_identity, Mapping) else None
    trial_id = stable_project_trial_id(method_version, anchor)
    observations = [dict(x) for x in source_observations]
    if not observations:
        raise ValueError("source_observations must not be empty")
    for obs in observations:
        for key in ("source_ref", "observed_at", "content_hash", "authentication_state", "conflict_state"):
            _require_text(obs.get(key), f"source_observations.{key}")
        obs.setdefault("available_at", None)
    record = {
        "schema": "PROJECT_CA_PROJECT_MEMORY_P1_v1",
        "project_trial_id": trial_id,
        "method_version": _require_text(method_version, "method_version"),
        "frozen_at_utc": _require_text(frozen_at_utc, "frozen_at_utc"),
        "eligibility_manifest_sha256": _require_text(eligibility_manifest_sha256, "eligibility_manifest_sha256"),
        "discovery": dict(discovery),
        "project_identity": dict(project_identity),
        "source_observations": observations,
        "project_memory_before": dict(project_memory_before or {}),
        "material_delta": dict(material_delta or {}),
        "token_state": token_state,
        "ca_candidates": [dict(x) for x in ca_candidates],
        "lineage": dict(lineage or {}),
        "authority": dict(authority or {
            "research_only": True,
            "project_to_ca_binding": False,
            "portfolio_action": False,
            "automatic_trading": False,
            "user_alerts": False,
            "production_activation": False,
        }),
    }
    record["frozen_input_sha256"] = sha256_json(record)
    return record


def append_snapshot(history: Sequence[Mapping[str, Any]], snapshot: Mapping[str, Any],
                    supersedes_sha256: str | None = None) -> list[dict[str, Any]]:
    """Append-only history. Existing entries are never mutated."""
    out = [dict(x) for x in history]
    item = dict(snapshot)
    if supersedes_sha256 is not None:
        item["supersedes_sha256"] = _require_text(supersedes_sha256, "supersedes_sha256")
    item["snapshot_sha256"] = sha256_json(item)
    if any(x.get("snapshot_sha256") == item["snapshot_sha256"] for x in out):
        return out
    out.append(item)
    return out
