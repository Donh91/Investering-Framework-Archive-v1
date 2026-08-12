from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

READY_PROVIDER_STATES = {
    "READY_FOR_TOOL_DISCOVERY",
    "DOCS_VERIFIED_READY_FOR_TOOL_DISCOVERY",
    "READY_FOR_LIVE_SMOKE",
    "READY_FOR_RESEARCH_CHALLENGE",
    "AWAITING_AI_RED_TEAM",
}
READY_DEEP_RESEARCH_STATES = {"ACTIVE_READY_FOR_RESEARCH", "READY"}
HEAVY_LANES = {"provider_evaluation", "deep_research"}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def provider_ready(scorecard: dict[str, Any]) -> tuple[bool, str | None, str | None]:
    active = scorecard.get("active_provider")
    if not active:
        return False, None, None
    for item in scorecard.get("providers", []):
        if isinstance(item, dict) and item.get("provider") == active:
            state = item.get("state")
            return state in READY_PROVIDER_STATES, str(active), str(state) if state is not None else None
    return False, str(active), None


def deep_research_ready(state: dict[str, Any]) -> tuple[bool, str | None, str | None]:
    active = state.get("active_research_id")
    if not active:
        return False, None, None
    item = state.get("item_states", {}).get(active, {})
    item_state = item.get("state") if isinstance(item, dict) else None
    return item_state in READY_DEEP_RESEARCH_STATES, str(active), str(item_state) if item_state is not None else None


def choose_heavy_lane(*, provider_is_ready: bool, deep_is_ready: bool, last_heavy_lane: str | None, active_heavy_lane: str | None) -> str | None:
    if active_heavy_lane:
        if active_heavy_lane not in HEAVY_LANES:
            raise ValueError("invalid_active_heavy_lane")
        return None
    if provider_is_ready and deep_is_ready:
        if last_heavy_lane == "deep_research":
            return "provider_evaluation"
        if last_heavy_lane == "provider_evaluation":
            return "deep_research"
        return "deep_research"
    if provider_is_ready:
        return "provider_evaluation"
    if deep_is_ready:
        return "deep_research"
    return None


def build_plan(scorecard: dict[str, Any], deep_state: dict[str, Any], *, last_heavy_lane: str | None = None, active_heavy_lane: str | None = None) -> dict[str, Any]:
    p_ready, provider, provider_state = provider_ready(scorecard)
    d_ready, research_id, research_state = deep_research_ready(deep_state)
    selected = choose_heavy_lane(
        provider_is_ready=p_ready,
        deep_is_ready=d_ready,
        last_heavy_lane=last_heavy_lane,
        active_heavy_lane=active_heavy_lane,
    )
    return {
        "contract": "RESEARCH_EXECUTION_PLAN_v1",
        "passive_forward_evidence": {
            "allowed": True,
            "consumes_heavy_slot": False,
            "owner_test_id": "GATE_BTC_PARTIAL_FT_1",
        },
        "heavy_execution": {
            "max_active_total": 1,
            "active_lane": active_heavy_lane,
            "selected_next_lane": selected,
            "selection_reason": (
                "HEAVY_SLOT_ALREADY_OCCUPIED" if active_heavy_lane else
                "BOTH_READY_FAIRNESS" if p_ready and d_ready else
                "PROVIDER_ONLY_READY" if p_ready else
                "DEEP_RESEARCH_ONLY_READY" if d_ready else
                "NO_HEAVY_LANE_READY"
            ),
        },
        "provider_evaluation": {
            "ready": p_ready,
            "provider": provider,
            "state": provider_state,
            "max_active_provider_trials": 1,
        },
        "deep_research": {
            "ready": d_ready,
            "research_id": research_id,
            "state": research_state,
            "max_active_research_items": 1,
        },
        "authority": {
            "framework_state_change": False,
            "portfolio_action": False,
            "market_rule_change": False,
            "canonical_promotion": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministically coordinate provider and Deep Research heavy execution while leaving passive evidence independent.")
    parser.add_argument("--provider-scorecard", required=True, type=Path)
    parser.add_argument("--deep-research-state", required=True, type=Path)
    parser.add_argument("--last-heavy-lane", choices=sorted(HEAVY_LANES))
    parser.add_argument("--active-heavy-lane", choices=sorted(HEAVY_LANES))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    plan = build_plan(
        load_json(args.provider_scorecard),
        load_json(args.deep_research_state),
        last_heavy_lane=args.last_heavy_lane,
        active_heavy_lane=args.active_heavy_lane,
    )
    text = json.dumps(plan, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
