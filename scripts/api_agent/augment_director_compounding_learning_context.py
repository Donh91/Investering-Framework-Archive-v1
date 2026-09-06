#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

BASE = Path("00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1")
DEFAULT_STATE = BASE / "STATE.json"
DEFAULT_PROPOSAL = BASE / "NEXT_BEST_EXPERIMENT.json"
DEFAULT_BACKLOG = BASE / "LEARNING_BACKLOG.json"
DEFAULT_HEALTH = Path("research/architecture_health/LATEST_COMPOUNDING_LEARNING_HEALTH.json")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _research_only(value: dict[str, Any]) -> bool:
    if value.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        return False
    for key in (
        "canonical_effect",
        "portfolio_execution",
        "automatic_canonical_write",
        "automatic_execution",
        "automatic_market_rule_change",
        "automatic_parameter_search",
        "automatic_promotion",
        "automatic_threshold_change",
        "automatic_weight_change",
        "model_weight_change",
    ):
        if value.get(key) is True:
            return False
    return True


def _health_safe(value: dict[str, Any]) -> bool:
    authority = value.get("authority") if isinstance(value.get("authority"), dict) else {}
    blockers = value.get("blockers") if isinstance(value.get("blockers"), list) else ["INVALID_BLOCKERS"]
    return (
        value.get("contract") == "COMPOUNDING_LEARNING_HEALTH_v1"
        and value.get("status") == "PASS"
        and not blockers
        and authority.get("canonical_effect") is False
        and authority.get("portfolio_execution") is False
    )


def _compact_backlog(entries: Any, limit: int = 5) -> list[dict[str, Any]]:
    if not isinstance(entries, list):
        return []
    out: list[dict[str, Any]] = []
    allowed = (
        "rank",
        "status",
        "candidate_test_id",
        "test_type",
        "problem_uncertainty",
        "score",
        "requires_scientific_admission",
    )
    for row in entries:
        if not isinstance(row, dict):
            continue
        out.append({key: row.get(key) for key in allowed if key in row})
        if len(out) >= limit:
            break
    return out


def compounding_learning(
    state_path: Path,
    proposal_path: Path,
    backlog_path: Path,
    health_path: Path,
) -> dict[str, Any]:
    paths = {
        "state": state_path,
        "proposal": proposal_path,
        "backlog": backlog_path,
        "health": health_path,
    }
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        return {
            "status": "UNAVAILABLE",
            "reason": "COMPOUNDING_LEARNING_SURFACE_MISSING",
            "missing": sorted(missing),
        }

    try:
        state = load_json(state_path)
        proposal = load_json(proposal_path)
        backlog = load_json(backlog_path)
        health = load_json(health_path)
    except Exception as exc:
        return {
            "status": "BLOCKED_INVALID_STATE",
            "reason": str(exc),
        }

    invalid: list[str] = []
    if not _research_only(state):
        invalid.append("state")
    if not _research_only(proposal):
        invalid.append("proposal")
    if not _research_only(backlog):
        invalid.append("backlog")
    if not _health_safe(health):
        invalid.append("health")
    if proposal.get("requires_scientific_admission") is not True:
        invalid.append("proposal_scientific_admission")
    if proposal.get("new_test_automatically_admitted") is True:
        invalid.append("proposal_auto_admission")

    if invalid:
        return {
            "status": "BLOCKED_AUTHORITY_OR_HEALTH_FIREWALL",
            "invalid_states": sorted(set(invalid)),
            "instruction": "Do not route Compounding Learning into Director reasoning unless research-only authority and health firewalls pass.",
        }

    families = state.get("hypothesis_families") if isinstance(state.get("hypothesis_families"), list) else []
    redundancy_warning_count = sum(
        1 for row in families if isinstance(row, dict) and row.get("redundancy_collinearity_warning") is True
    )
    information_gain = proposal.get("expected_information_gain") if isinstance(proposal.get("expected_information_gain"), dict) else {}
    entries = backlog.get("entries") if isinstance(backlog.get("entries"), list) else []

    return {
        "status": "READY",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "controller": {
            "generated_at_utc": state.get("generated_at_utc"),
            "adjudication_generated_at_utc": state.get("adjudication_generated_at_utc"),
            "checkpoint_packet_count": state.get("checkpoint_packet_count"),
            "hypothesis_family_count": len(families),
            "redundancy_collinearity_warning_count": redundancy_warning_count,
            "evidence_fingerprint": state.get("evidence_fingerprint"),
        },
        "next_best_test": {
            "candidate_test_id": proposal.get("candidate_test_id"),
            "parent_candidate_id": proposal.get("parent_candidate_id"),
            "action": proposal.get("action"),
            "test_type": proposal.get("test_type"),
            "problem_uncertainty": proposal.get("problem_uncertainty"),
            "proposed_priority": proposal.get("proposed_priority"),
            "information_value_score": information_gain.get("score"),
            "proposal_status": proposal.get("proposal_status"),
            "requires_scientific_admission": proposal.get("requires_scientific_admission"),
            "redundancy_risk": proposal.get("redundancy_risk"),
            "what_would_change_our_view": proposal.get("what_would_change_our_view"),
            "revisit_condition": proposal.get("revisit_condition"),
        },
        "backlog": {
            "entry_count": backlog.get("entry_count", len(entries)),
            "top_entries": _compact_backlog(entries),
        },
        "health": {
            "status": health.get("status"),
            "blockers": health.get("blockers"),
            "summary": health.get("summary"),
        },
        "instruction": (
            "Treat Compounding Learning as prior post-adjudication learning and next-test context only. "
            "It may change which hypotheses, uncertainties or prospective tests deserve attention. "
            "It cannot change canonical state, thresholds, weights, market rules or portfolio action, and every new test must re-enter Scientific Admission."
        ),
        "closure": "COMPOUNDING_LEARNING_ROUTED_TO_FUTURE_DIRECTOR_CONTEXT",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--proposal", type=Path, default=DEFAULT_PROPOSAL)
    parser.add_argument("--backlog", type=Path, default=DEFAULT_BACKLOG)
    parser.add_argument("--health", type=Path, default=DEFAULT_HEALTH)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    context = load_json(args.context)
    routed = compounding_learning(args.state, args.proposal, args.backlog, args.health)
    context["compounding_learning"] = routed

    provenance = context.get("learning_context_provenance")
    if not isinstance(provenance, list):
        provenance = []
    for field, path in (
        ("compounding_learning_state", args.state),
        ("compounding_learning_proposal", args.proposal),
        ("compounding_learning_backlog", args.backlog),
        ("compounding_learning_health", args.health),
    ):
        if path.exists():
            provenance.append({"field": field, "path": str(path), "sha256": sha256(path)})
    context["learning_context_provenance"] = provenance

    contract = context.get("context_routing_contract")
    if not isinstance(contract, dict):
        contract = {
            "contract": "DIRECTOR_CONTEXT_ROUTING_v1",
            "principle": "COLLECTED_DATA_IS_NOT_AVAILABLE_TO_AN_AGENT_UNLESS_PRESENT_IN_CONTEXT",
            "required_context_families": [],
            "no_automatic_authority_promotion": True,
        }
    required = contract.get("required_context_families")
    if not isinstance(required, list):
        required = []
    if "compounding_learning" not in required:
        required.append("compounding_learning")
    contract["required_context_families"] = required
    context["context_routing_contract"] = contract

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(context, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"status": routed.get("status"), "closure": routed.get("closure")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
