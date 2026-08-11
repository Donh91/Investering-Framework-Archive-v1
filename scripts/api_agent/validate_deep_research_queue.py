#!/usr/bin/env python3
"""Validate the bounded Deep Research Horizon Queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

QUEUE_PATH = Path("research/api_agent/deep_research/DEEP_RESEARCH_QUEUE_v1.json")
STATE_PATH = Path("research/api_agent/deep_research/LATEST_DEEP_RESEARCH_STATE.json")
METHOD_PATH = Path("research/api_agent/deep_research/DEEP_RESEARCH_METHOD_v1.md")
PROVIDER_SCORECARD = Path("research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json")

EXPECTED_HORIZONS = {"1_3D", "5_7D", "2_3W", "CROSS_HORIZON"}
EXPECTED_PROVIDERS = {"CoinGecko", "Dune", "LunarCrush", "CoinMarketCap", "TheGraph", "altFINS", "Binance"}
REQUIRED_P0 = {"DRQ-001", "DRQ-002", "DRQ-003", "DRQ-004"}
ALLOWED_INTEGRATION_CEILINGS = {
    "RESEARCH_CONTEXT_ONLY",
    "EXISTING_TEST_SUPPORT_ONLY",
    "SHADOW_OBSERVATION_ONLY",
    "CROSSCHECK_ONLY",
    "CANDIDATE_DISCOVERY_CONTEXT_ONLY",
    "RESEARCH_INFRASTRUCTURE_ONLY",
}
FORBIDDEN_OUTPUTS = {
    "BUY",
    "SELL",
    "POSITION_SIZE",
    "CANONICAL_MARKET_STATE_CHANGE",
    "NEW_THRESHOLD",
    "NEW_WEIGHT",
    "NEW_POLICY_SEMANTICS",
    "AUTOMATIC_SENSOR_PROMOTION",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_queue(root: Path = Path(".")) -> List[str]:
    root = root.resolve()
    errors: List[str] = []
    qpath = root / QUEUE_PATH
    spath = root / STATE_PATH
    mpath = root / METHOD_PATH
    ppath = root / PROVIDER_SCORECARD

    for path, label in ((qpath, "queue"), (spath, "state"), (mpath, "method"), (ppath, "provider_scorecard")):
        if not path.is_file():
            errors.append(f"missing_{label}:{path.relative_to(root)}")
    if errors:
        return errors

    try:
        queue = load_json(qpath)
        state = load_json(spath)
        provider_scorecard = load_json(ppath)
    except Exception as exc:
        return [f"invalid_json:{type(exc).__name__}:{exc}"]

    if queue.get("contract") != "DEEP_RESEARCH_HORIZON_QUEUE_v1":
        errors.append("queue_contract_mismatch")
    if queue.get("status") != "OPERATIONAL_RESEARCH_QUEUE":
        errors.append("queue_status_mismatch")
    if queue.get("research_kind") != "RESEARCH_QUESTION_NOT_FORWARD_TEST":
        errors.append("research_kind_mismatch")

    canonical = queue.get("canonical_boundaries", {})
    for key in ("does_not_replace_open_questions_register", "does_not_create_new_active_test", "does_not_create_outcome_rows"):
        if canonical.get(key) is not True:
            errors.append(f"canonical_boundary_not_true:{key}")

    execution = queue.get("execution", {})
    if execution.get("sequential") is not True:
        errors.append("queue_not_sequential")
    if execution.get("max_active_research_items") != 1:
        errors.append("max_active_research_items_must_equal_1")
    for key in ("automatic_framework_integration", "automatic_market_semantics_change", "automatic_portfolio_action"):
        if execution.get(key) is not False:
            errors.append(f"unsafe_execution_flag:{key}")

    horizons = set(queue.get("horizons", {}))
    if horizons != EXPECTED_HORIZONS:
        errors.append("horizon_set_mismatch:" + ",".join(sorted(horizons)))

    gate = queue.get("provider_gate", {})
    if execution.get("provider_must_be_retained_before_use") is not True:
        errors.append("provider_retention_gate_disabled")
    if gate.get("provider_ceiling_remains_binding") is not True:
        errors.append("provider_ceiling_not_binding")
    if gate.get("provider_conflict_rule") != "PRESERVE_CONFLICT_CANONICAL_OWNER_WINS":
        errors.append("provider_conflict_rule_mismatch")

    output = queue.get("output_contract", {})
    forbidden = set(output.get("forbidden_outputs", []))
    missing_forbidden = FORBIDDEN_OUTPUTS - forbidden
    if missing_forbidden:
        errors.append("missing_forbidden_outputs:" + ",".join(sorted(missing_forbidden)))
    if output.get("authority_class") != "RESEARCH_EVIDENCE_ONLY":
        errors.append("output_authority_not_research_only")

    authority = queue.get("authority", {})
    if not authority:
        errors.append("authority_missing")
    else:
        enabled = sorted(k for k, v in authority.items() if v is not False)
        if enabled:
            errors.append("nonzero_authority:" + ",".join(enabled))

    items = queue.get("items", [])
    if not isinstance(items, list) or not items:
        errors.append("research_items_missing")
        return errors

    ids = [item.get("id") for item in items if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_research_id")
    missing_p0 = REQUIRED_P0 - set(ids)
    if missing_p0:
        errors.append("missing_required_p0:" + ",".join(sorted(missing_p0)))

    covered_horizons: set[str] = set()
    for item in items:
        rid = str(item.get("id") or "UNKNOWN")
        if item.get("priority") not in {"P0", "P1", "P2"}:
            errors.append(f"invalid_priority:{rid}")
        ih = set(item.get("horizons", []))
        if not ih or not ih <= EXPECTED_HORIZONS:
            errors.append(f"invalid_horizons:{rid}")
        covered_horizons |= ih

        required = set(item.get("required_providers", []))
        optional = set(item.get("optional_providers", []))
        unknown = (required | optional) - EXPECTED_PROVIDERS
        if unknown:
            errors.append(f"unknown_provider:{rid}:{','.join(sorted(unknown))}")
        if required & optional:
            errors.append(f"provider_required_optional_overlap:{rid}")

        for key in ("question", "primary_goal", "hypothesis", "baseline", "decision_divergence", "falsifier", "kill_condition"):
            if not str(item.get(key) or "").strip():
                errors.append(f"missing_{key}:{rid}")

        if item.get("integration_ceiling") not in ALLOWED_INTEGRATION_CEILINGS:
            errors.append(f"invalid_integration_ceiling:{rid}")

        links = item.get("canonical_links")
        if not isinstance(links, dict) or not isinstance(links.get("open_questions"), list) or not isinstance(links.get("active_tests"), list):
            errors.append(f"invalid_canonical_links:{rid}")

    if covered_horizons != EXPECTED_HORIZONS:
        errors.append("queue_does_not_cover_all_horizons")

    if state.get("contract") != "DEEP_RESEARCH_QUEUE_STATE_v1":
        errors.append("state_contract_mismatch")
    if state.get("max_active_research_items") != 1:
        errors.append("state_max_active_mismatch")
    active = state.get("active_research_id")
    if active not in set(ids):
        errors.append("state_active_id_unknown")
    state_authority = state.get("authority", {})
    if any(v is not False for v in state_authority.values()):
        errors.append("state_nonzero_authority")

    known_provider_rows = {row.get("provider") for row in provider_scorecard.get("providers", []) if isinstance(row, dict)}
    if not EXPECTED_PROVIDERS <= known_provider_rows:
        errors.append("provider_scorecard_missing_known_provider")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate_queue(args.root)
    if errors:
        print("DEEP_RESEARCH_QUEUE_FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DEEP_RESEARCH_QUEUE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
