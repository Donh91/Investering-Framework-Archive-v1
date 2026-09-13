#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment_lifecycle as base  # noqa: E402

UTC = timezone.utc
CONTRACT = "AGENT_HANDOFF_CONTRACT_v1"
OWNER = "EXPERIMENT_LIFECYCLE_v1"
AUTHORITY = {
    "canonical_effect": False,
    "portfolio_execution": False,
    "framework_state_change": False,
    "threshold_change": False,
    "weight_change": False,
    "automatic_promotion": False,
}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def require_string(value: Any, error: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(error)
    return text


def freeze(value: Any) -> dict[str, Any]:
    """Return a canonical hash envelope without retaining mutable payload bytes."""
    if value is None:
        raise ValueError("artifact_required")
    return {"sha256": base.sha(value), "canonical_bytes": len(base.canon(value))}


def normalize_capabilities(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or not raw:
        raise ValueError("capability_snapshot_required")
    tools = raw.get("tools")
    schemas = raw.get("schemas")
    if not isinstance(tools, list) or not tools or not all(str(item).strip() for item in tools):
        raise ValueError("capability_tools_required")
    if not isinstance(schemas, dict) or not schemas:
        raise ValueError("capability_schemas_required")
    normalized = {
        "tools": sorted({str(item).strip() for item in tools}),
        "schemas": {str(key): str(value) for key, value in sorted(schemas.items())},
        "runtime": str(raw.get("runtime") or "UNSPECIFIED"),
    }
    normalized["snapshot_sha256"] = base.sha(normalized)
    return normalized


def build_contract(
    *,
    stage_id: str,
    mission: Any,
    input_artifact: Any,
    capability_snapshot: dict[str, Any],
    output_artifact: Any,
    repair_scope: str,
    owner_candidate_id: str | None = None,
    previous_handoff_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    stage = require_string(stage_id, "stage_id_required")
    scope = require_string(repair_scope, "repair_scope_required")
    if scope != stage:
        raise ValueError("repair_scope_must_equal_stage")
    capabilities = normalize_capabilities(capability_snapshot)
    locks = {
        "mission_lock": freeze(mission),
        "input_artifact_lock": freeze(input_artifact),
        "capability_lock": {"sha256": capabilities["snapshot_sha256"]},
        "output_artifact_lock": freeze(output_artifact),
    }
    identity = {
        "contract": CONTRACT,
        "owner": OWNER,
        "stage_id": stage,
        "owner_candidate_id": str(owner_candidate_id or "UNBOUND"),
        "previous_handoff_id": str(previous_handoff_id or "ROOT"),
        "locks": locks,
        "repair_scope": scope,
    }
    return {
        **identity,
        "handoff_id": "AHC-" + base.sha(identity)[:20],
        "created_at_utc": created_at or now_iso(),
        "capability_snapshot": capabilities,
        "rules": {
            "downstream_requires_exact_output_hash": True,
            "local_repair_only": True,
            "capability_drift_fails_closed": True,
            "silent_fallback_forbidden": True,
            "upstream_mutation_requires_new_handoff_chain": True,
        },
        "authority": dict(AUTHORITY),
    }


def verify_contract(
    contract: dict[str, Any],
    *,
    mission: Any,
    input_artifact: Any,
    capability_snapshot: dict[str, Any],
    output_artifact: Any,
) -> bool:
    if contract.get("contract") != CONTRACT or contract.get("owner") != OWNER:
        raise ValueError("invalid_handoff_contract")
    capabilities = normalize_capabilities(capability_snapshot)
    expected = {
        "mission_lock": freeze(mission)["sha256"],
        "input_artifact_lock": freeze(input_artifact)["sha256"],
        "capability_lock": capabilities["snapshot_sha256"],
        "output_artifact_lock": freeze(output_artifact)["sha256"],
    }
    locks = contract.get("locks") or {}
    for name, digest in expected.items():
        actual = (locks.get(name) or {}).get("sha256")
        if actual != digest:
            raise ValueError(f"handoff_lock_mismatch:{name}")
    return True


def assert_downstream_input(upstream_contract: dict[str, Any], downstream_input: Any) -> bool:
    expected = ((upstream_contract.get("locks") or {}).get("output_artifact_lock") or {}).get("sha256")
    if not expected:
        raise ValueError("upstream_output_lock_missing")
    if freeze(downstream_input)["sha256"] != expected:
        raise ValueError("downstream_input_not_pinned_to_upstream_output")
    return True


def validate_local_repair(previous: dict[str, Any], replacement: dict[str, Any]) -> bool:
    if previous.get("stage_id") != replacement.get("stage_id"):
        raise ValueError("repair_stage_changed")
    if previous.get("repair_scope") != previous.get("stage_id") or replacement.get("repair_scope") != replacement.get("stage_id"):
        raise ValueError("repair_scope_invalid")
    previous_locks = previous.get("locks") or {}
    replacement_locks = replacement.get("locks") or {}
    for name in ("mission_lock", "input_artifact_lock", "capability_lock"):
        if (previous_locks.get(name) or {}).get("sha256") != (replacement_locks.get(name) or {}).get("sha256"):
            raise ValueError(f"upstream_mutation_forbidden:{name}")
    return True


def write_contract(root: Path, contract: dict[str, Any]) -> Path:
    when = base.dt(contract["created_at_utc"])
    path = root / when.strftime("%Y/%m") / f"{contract['handoff_id']}.json"
    if not base.write_new(path, contract):
        raise FileExistsError(f"immutable_handoff_exists:{path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze an immutable experiment-agent handoff contract.")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.spec.read_text())
    contract = build_contract(
        stage_id=raw["stage_id"],
        mission=raw["mission"],
        input_artifact=raw["input_artifact"],
        capability_snapshot=raw["capability_snapshot"],
        output_artifact=raw["output_artifact"],
        repair_scope=raw["repair_scope"],
        owner_candidate_id=raw.get("owner_candidate_id"),
        previous_handoff_id=raw.get("previous_handoff_id"),
        created_at=raw.get("created_at_utc"),
    )
    path = write_contract(args.output_root, contract)
    print(json.dumps({
        "handoff_id": contract["handoff_id"],
        "path": str(path),
        "owner": contract["owner"],
        "authority": contract["authority"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
