"""P1 Project Memory substrate for the Project -> CA bridge.

Research-only. This module persists/folds project observations before token existence.
It deliberately implements no Project -> CA binding semantics (P2+) and grants no
market, alert, portfolio, or trading authority.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from typing import Any, Iterable

CONTRACT = "PROJECT_CA_PROJECT_MEMORY_P1_v1"
METHOD_VERSION = "project-ca-bridge-p1-v1"
TOKEN_STATES = {"NO_TOKEN_OBSERVED", "TOKEN_CANDIDATE", "TOKEN_BOUND", "TOKEN_CONFLICT"}
SOURCE_STATES = {
    "UNASSESSED", "CANDIDATE", "AUTHENTICATED_FIRST_PARTY",
    "INVALIDATED_FIRST_PARTY", "CONFLICTED", "BOUNDED"
}

def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _require_utc(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an explicit UTC timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid UTC timestamp") from exc

def _identity_anchor(project_identity: dict[str, Any]) -> dict[str, Any]:
    """Return only bounded identity anchors. Names/tickers/logos/aliases are excluded."""
    anchors = project_identity.get("control_roots") or []
    normalized = []
    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        kind = anchor.get("kind")
        value = anchor.get("value")
        if kind and value:
            normalized.append({"kind": str(kind), "value": str(value).strip().lower()})
    normalized.sort(key=lambda x: (x["kind"], x["value"]))
    if not normalized:
        raise ValueError("project_identity requires at least one bounded control_root; aliases/name/ticker/logo are not identity proof")
    return {"control_roots": normalized}

def derive_project_trial_id(project_identity: dict[str, Any]) -> str:
    return "PCA-" + _sha(_identity_anchor(project_identity))[:20]

def _normalize_source_observation(obs: dict[str, Any]) -> dict[str, Any]:
    required = ("source_family", "source_ref", "observed_at_utc", "content_sha256", "authentication_state")
    for key in required:
        if not obs.get(key):
            raise ValueError(f"source observation missing {key}")
    _require_utc(obs["observed_at_utc"], "observed_at_utc")
    if obs.get("available_at_utc") is not None:
        _require_utc(obs["available_at_utc"], "available_at_utc")
    if obs["authentication_state"] not in SOURCE_STATES:
        raise ValueError("invalid authentication_state")
    out = {
        "source_family": obs["source_family"],
        "source_ref": obs["source_ref"],
        "observed_at_utc": obs["observed_at_utc"],
        "available_at_utc": obs.get("available_at_utc"),
        "content_sha256": obs["content_sha256"],
        "authentication_state": obs["authentication_state"],
        "source_health": obs.get("source_health", "UNKNOWN"),
        "claims": copy.deepcopy(obs.get("claims", {})),
    }
    out["observation_sha256"] = _sha(out)
    return out

def freeze_project_trial(*, frozen_at_utc: str, eligibility_manifest_sha256: str,
                         discovery: dict[str, Any], project_identity: dict[str, Any],
                         source_observations: Iterable[dict[str, Any]],
                         project_memory_before: dict[str, Any] | None = None,
                         material_delta: dict[str, Any] | None = None,
                         token_state: str = "NO_TOKEN_OBSERVED",
                         ca_candidates: Iterable[dict[str, Any]] = (),
                         lineage: dict[str, Any] | None = None) -> dict[str, Any]:
    _require_utc(frozen_at_utc, "frozen_at_utc")
    if not eligibility_manifest_sha256:
        raise ValueError("eligibility_manifest_sha256 is required and must be frozen before outcome")
    if token_state not in TOKEN_STATES:
        raise ValueError("invalid token_state")
    sources = [_normalize_source_observation(x) for x in source_observations]
    sources.sort(key=lambda x: (x["observed_at_utc"], x["source_family"], x["source_ref"], x["observation_sha256"]))
    identity_anchor = _identity_anchor(project_identity)
    trial_id = derive_project_trial_id(project_identity)
    trial = {
        "contract": CONTRACT,
        "project_trial_id": trial_id,
        "method_version": METHOD_VERSION,
        "frozen_at_utc": frozen_at_utc,
        "eligibility_manifest_sha256": eligibility_manifest_sha256,
        "discovery": copy.deepcopy(discovery),
        "project_identity": {
            "identity_anchor": identity_anchor,
            "display_name": project_identity.get("display_name"),
            "aliases": sorted(set(project_identity.get("aliases") or [])),
            "ticker": project_identity.get("ticker"),
            "logo_ref": project_identity.get("logo_ref"),
            "identity_rule": "ALIASES_NAME_TICKER_LOGO_ARE_NONAUTHORITATIVE",
        },
        "source_observations": sources,
        "project_memory_before": copy.deepcopy(project_memory_before),
        "material_delta": copy.deepcopy(material_delta),
        "token_state": token_state,
        "ca_candidates": copy.deepcopy(list(ca_candidates)),
        "lineage": copy.deepcopy(lineage or {"supersedes_snapshot_sha256": None, "reason": "INITIAL_FREEZE"}),
        "authority": {
            "research_only": True, "project_to_ca_binding": False, "buy_sell": False,
            "portfolio_action": False, "automatic_trading": False, "user_alert": False,
            "production_promotion": False,
        },
    }
    # Outcome is intentionally absent: P1 must be creatable before any outcome exists.
    trial["snapshot_sha256"] = _sha(trial)
    return trial

def append_observation(previous: dict[str, Any], *, frozen_at_utc: str,
                       source_observations: Iterable[dict[str, Any]],
                       token_state: str | None = None,
                       ca_candidates: Iterable[dict[str, Any]] | None = None,
                       material_delta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a new snapshot. The prior snapshot is never mutated or silently rewritten."""
    before = copy.deepcopy(previous)
    new_sources = list(previous.get("source_observations", []))
    new_sources.extend(source_observations)
    identity = {
        "control_roots": previous["project_identity"]["identity_anchor"]["control_roots"],
        "display_name": previous["project_identity"].get("display_name"),
        "aliases": previous["project_identity"].get("aliases", []),
        "ticker": previous["project_identity"].get("ticker"),
        "logo_ref": previous["project_identity"].get("logo_ref"),
    }
    nxt = freeze_project_trial(
        frozen_at_utc=frozen_at_utc,
        eligibility_manifest_sha256=previous["eligibility_manifest_sha256"],
        discovery=previous["discovery"],
        project_identity=identity,
        source_observations=new_sources,
        project_memory_before={"snapshot_sha256": previous["snapshot_sha256"]},
        material_delta=material_delta,
        token_state=token_state or previous["token_state"],
        ca_candidates=previous.get("ca_candidates", []) if ca_candidates is None else ca_candidates,
        lineage={"supersedes_snapshot_sha256": previous["snapshot_sha256"], "reason": "APPEND_ONLY_OBSERVATION"},
    )
    if nxt["project_trial_id"] != previous["project_trial_id"]:
        raise ValueError("append changed project trial identity")
    assert previous == before, "append_observation mutated historical evidence"
    return nxt
