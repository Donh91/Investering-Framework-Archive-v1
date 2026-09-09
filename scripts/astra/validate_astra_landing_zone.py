#!/usr/bin/env python3
"""Deterministic semantic validator for the Astra Research Intelligence Landing Zone v1.

No model call is required. This validator complements, rather than replaces, JSON Schema.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_REQUIRED = [
    "07_PROMPTS_AND_AGENTS/astra/00_READ_FIRST_ASTRA_LANDING_ZONE_v1.md",
    "07_PROMPTS_AND_AGENTS/astra/ASTRA_LANDING_ZONE_POLICY_v1.json",
    "07_PROMPTS_AND_AGENTS/astra/ASTRA_RESEARCH_RUN_ENVELOPE_v1.schema.json",
    "07_PROMPTS_AND_AGENTS/astra/LATEST_ASTRA_LANDING_ZONE.json",
]

ALLOWED_DUPLICATE_MODES = {"ADVERSARIAL", "REPLICATION"}


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_run(run: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if run.get("contract") != "ASTRA_RESEARCH_RUN_ENVELOPE_v1":
        errors.append("contract must be ASTRA_RESEARCH_RUN_ENVELOPE_v1")

    budget = run.get("budget", {})
    assignments = run.get("assignments", [])
    max_agents = budget.get("max_agents")
    max_parallel = budget.get("max_parallel_agents")
    max_total_tokens = budget.get("max_total_tokens")
    reserve_pct = budget.get("escalation_reserve_pct")

    if not isinstance(max_agents, int) or max_agents < 1:
        errors.append("budget.max_agents must be a positive integer")
    elif len(assignments) > max_agents:
        errors.append("assignment count exceeds budget.max_agents")

    if isinstance(max_parallel, int) and isinstance(max_agents, int) and max_parallel > max_agents:
        errors.append("budget.max_parallel_agents cannot exceed max_agents")

    if isinstance(max_total_tokens, int) and isinstance(reserve_pct, (int, float)):
        assigned_tokens = sum(a.get("token_budget", 0) for a in assignments if isinstance(a, dict))
        spendable = max_total_tokens * (1 - reserve_pct / 100)
        if assigned_tokens > spendable:
            errors.append("assignment token budgets consume the escalation reserve")

    required_capabilities = set(run.get("required_capabilities", []))
    assigned_capabilities = {a.get("capability") for a in assignments if isinstance(a, dict)}
    uncovered = sorted(c for c in required_capabilities if c not in assigned_capabilities)
    if uncovered:
        errors.append(f"required capabilities are not covered by assignments: {', '.join(uncovered)}")

    by_hash: dict[str, list[dict[str, Any]]] = {}
    for assignment in assignments:
        qh = assignment.get("question_hash")
        if qh:
            by_hash.setdefault(qh, []).append(assignment)

    for qh, group in by_hash.items():
        if len(group) > 1:
            modes = {g.get("mode") for g in group}
            if not modes.issubset(ALLOWED_DUPLICATE_MODES):
                errors.append(f"duplicate question_hash {qh} is not explicit adversarial/replication work")

    if run.get("execution_mode") == "BLIND_OPPOSITION":
        if len(assignments) < 2:
            errors.append("BLIND_OPPOSITION requires at least two assignments")
        groups = {a.get("blind_group") for a in assignments}
        if None in groups or len(groups) != 1:
            errors.append("BLIND_OPPOSITION assignments must share one non-null blind_group")
        if any(not a.get("commit_before_reveal_required") for a in assignments):
            errors.append("BLIND_OPPOSITION requires commit_before_reveal_required=true for every assignment")

    escalation_rule = run.get("escalation_rule")
    if not isinstance(escalation_rule, dict):
        errors.append("escalation_rule must be an object")
    else:
        for key in ("load_bearing_disagreement", "material_coverage_gap", "budget_exhaustion"):
            if not escalation_rule.get(key):
                errors.append(f"escalation_rule.{key} is required")

    try:
        decision_at = _dt(run["decision_at"])
    except Exception:
        decision_at = None
        errors.append("decision_at must be a valid ISO-8601 timestamp")

    for evidence in run.get("evidence", []):
        try:
            observable_at = _dt(evidence["observable_at"])
            retrieved_at = _dt(evidence["retrieved_at"])
        except Exception:
            errors.append(f"evidence {evidence.get('evidence_id')} has invalid timestamps")
            continue

        if retrieved_at < observable_at:
            errors.append(f"evidence {evidence.get('evidence_id')} retrieved_at precedes observable_at")

        if evidence.get("used_for_decision"):
            if evidence.get("leakage_status") != "POINT_IN_TIME_VALID":
                errors.append(f"decision evidence {evidence.get('evidence_id')} is not POINT_IN_TIME_VALID")
            if decision_at is not None and observable_at > decision_at:
                errors.append(f"decision evidence {evidence.get('evidence_id')} is look-ahead")

    utility_policy = run.get("utility_policy", {})
    if utility_policy.get("mode") != "SHADOW_LOG_ONLY":
        errors.append("utility_policy.mode must remain SHADOW_LOG_ONLY in v1")
    if utility_policy.get("auto_pruning_enabled") is not False:
        errors.append("auto_pruning_enabled must be false in v1")
    if utility_policy.get("auto_routing_promotion") is not False:
        errors.append("auto_routing_promotion must be false in v1")

    for obs in run.get("utility_observations", []):
        if obs.get("mode") != "SHADOW_LOG_ONLY":
            errors.append("utility observation mode must be SHADOW_LOG_ONLY")
        if not obs.get("evaluation_source"):
            errors.append("utility observation must identify evaluation_source")

    authority = run.get("authority", {})
    if authority.get("research_only") is not True:
        errors.append("authority.research_only must be true")
    for key in ["market_state_change", "portfolio_action", "trade_action", "canonical_self_promotion", "automatic_merge"]:
        if authority.get(key) is not False:
            errors.append(f"authority.{key} must be false")

    disagreement = run.get("disagreement", {})
    if disagreement.get("status") != "SHADOW_ONLY":
        errors.append("disagreement.status must remain SHADOW_ONLY in v1")

    return errors


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in ROOT_REQUIRED:
        if not (root / rel).exists():
            errors.append(f"missing required landing-zone file: {rel}")

    for rel in ROOT_REQUIRED[1:]:
        path = root / rel
        if path.exists() and path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"invalid JSON in {rel}: {exc}")

    policy_path = root / "07_PROMPTS_AND_AGENTS/astra/ASTRA_LANDING_ZONE_POLICY_v1.json"
    if policy_path.exists():
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        if policy.get("status") != "PREPARED_NOT_ACTIVE":
            errors.append("landing-zone policy must remain PREPARED_NOT_ACTIVE in v1")
        utility = policy.get("agent_utility", {})
        if utility.get("auto_pruning_enabled") is not False or utility.get("auto_routing_promotion") is not False:
            errors.append("landing-zone policy must not activate pruning/routing")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--run-envelope")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    errors = validate_repository(root)

    if args.run_envelope:
        run = json.loads(Path(args.run_envelope).read_text(encoding="utf-8"))
        errors.extend(validate_run(run))

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("PASS: ASTRA_LANDING_ZONE_V1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
