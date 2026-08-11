#!/usr/bin/env python3
"""Select the next executable Deep Research Horizon Queue item from retained providers."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

QUEUE_PATH = Path("research/api_agent/deep_research/DEEP_RESEARCH_QUEUE_v1.json")
STATE_PATH = Path("research/api_agent/deep_research/LATEST_DEEP_RESEARCH_STATE.json")
PROVIDER_SCORECARD = Path("research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json")

USABLE_PROVIDER_STATES = {
    "RESEARCH_ACTIVE_BASELINE",
    "RESEARCH_ACTIVE",
    "CROSSCHECK_ACTIVE",
    "SHADOW_OBSERVATION",
    "CANDIDATE_DISCOVERY_ACTIVE",
    "DIAGNOSTICS_ACTIVE",
}
TERMINAL_ITEM_STATES = {"COMPLETE", "KILLED", "HOLD"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def retained_providers(scorecard: dict[str, Any]) -> set[str]:
    return {
        str(row.get("provider"))
        for row in scorecard.get("providers", [])
        if isinstance(row, dict) and row.get("state") in USABLE_PROVIDER_STATES
    }


def refresh_item_states(queue: dict[str, Any], state: dict[str, Any], available: set[str]) -> dict[str, Any]:
    updated = deepcopy(state)
    current_states = updated.setdefault("item_states", {})
    active = updated.get("active_research_id")

    for item in queue.get("items", []):
        rid = str(item["id"])
        existing = current_states.get(rid, {})
        existing_state = existing.get("state")
        if existing_state in TERMINAL_ITEM_STATES:
            continue
        required = set(item.get("required_providers", []))
        missing = sorted(required - available)
        if rid == active and existing_state in {"ACTIVE_READY_FOR_RESEARCH", "IN_RESEARCH", "RED_TEAM"}:
            current_states[rid] = {"state": existing_state, "missing_required_providers": missing}
        else:
            current_states[rid] = {
                "state": "READY" if not missing else "WAIT_PROVIDER",
                "missing_required_providers": missing,
            }

    updated["available_retained_providers"] = sorted(available)
    updated["generated_at_utc"] = utc_now()
    return updated


def select_next(queue: dict[str, Any], state: dict[str, Any], scorecard: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    available = retained_providers(scorecard)
    updated = refresh_item_states(queue, state, available)

    active = updated.get("active_research_id")
    if active:
        active_state = updated.get("item_states", {}).get(active, {}).get("state")
        if active_state in {"ACTIVE_READY_FOR_RESEARCH", "IN_RESEARCH", "RED_TEAM"}:
            item = next((x for x in queue.get("items", []) if x.get("id") == active), None)
            return updated, item

    priority_order = {name: index for index, name in enumerate(queue.get("priority_order", ["P0", "P1", "P2"]))}
    indexed = list(enumerate(queue.get("items", [])))
    indexed.sort(key=lambda pair: (priority_order.get(pair[1].get("priority"), 99), pair[0]))

    for _, item in indexed:
        rid = str(item["id"])
        row = updated.get("item_states", {}).get(rid, {})
        if row.get("state") == "READY":
            updated["active_research_id"] = rid
            updated["item_states"][rid] = {
                "state": "ACTIVE_READY_FOR_RESEARCH",
                "missing_required_providers": [],
            }
            return updated, item

    updated["active_research_id"] = None
    return updated, None


def build_task_packet(item: dict[str, Any] | None, state: dict[str, Any]) -> dict[str, Any]:
    if item is None:
        return {
            "contract": "DEEP_RESEARCH_TASK_PACKET_v1",
            "status": "NO_EXECUTABLE_RESEARCH",
            "generated_at_utc": utc_now(),
            "available_retained_providers": state.get("available_retained_providers", []),
            "authority": {"framework_state_change": False, "portfolio_action": False, "canonical_promotion": False},
        }

    available = set(state.get("available_retained_providers", []))
    optional_available = sorted(set(item.get("optional_providers", [])) & available)
    return {
        "contract": "DEEP_RESEARCH_TASK_PACKET_v1",
        "status": "READY",
        "generated_at_utc": utc_now(),
        "research_id": item["id"],
        "priority": item["priority"],
        "title": item["title"],
        "horizons": item["horizons"],
        "question": item["question"],
        "primary_goal": item["primary_goal"],
        "hypothesis": item["hypothesis"],
        "baseline": item["baseline"],
        "decision_divergence": item["decision_divergence"],
        "falsifier": item["falsifier"],
        "kill_condition": item["kill_condition"],
        "required_providers": item["required_providers"],
        "optional_retained_providers": optional_available,
        "integration_ceiling": item["integration_ceiling"],
        "canonical_links": item["canonical_links"],
        "output_authority": "RESEARCH_EVIDENCE_ONLY",
        "instructions": [
            "Use only retained provider connections and existing canonical owner evidence.",
            "Separate evidence for risk-on, risk-off, range/chop and transition per horizon.",
            "Preserve horizon conflict instead of forcing one direction.",
            "Preserve provider provenance and missingness.",
            "Do not create a new test, sensor, threshold, weight, market state or portfolio action.",
            "Route any integration proposal through Research Lab Red Team and the existing canonical owner.",
        ],
        "authority": {
            "framework_state_change": False,
            "portfolio_action": False,
            "market_rule_change": False,
            "canonical_promotion": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, default=QUEUE_PATH)
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    parser.add_argument("--provider-scorecard", type=Path, default=PROVIDER_SCORECARD)
    parser.add_argument("--output-state", type=Path)
    parser.add_argument("--output-task", type=Path)
    args = parser.parse_args()

    queue = load_json(args.queue)
    state = load_json(args.state)
    scorecard = load_json(args.provider_scorecard)
    updated, item = select_next(queue, state, scorecard)
    packet = build_task_packet(item, updated)

    if args.output_state:
        args.output_state.parent.mkdir(parents=True, exist_ok=True)
        args.output_state.write_text(json.dumps(updated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.output_task:
        args.output_task.parent.mkdir(parents=True, exist_ok=True)
        args.output_task.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(packet, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
