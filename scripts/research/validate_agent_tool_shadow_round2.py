#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUND = ROOT / "06_RESEARCH_LAB" / "agent_tool_shadow_round2_v1"
WORKFLOW = ROOT / ".github" / "workflows" / "agent-tool-shadow-round2.yml"
SHA40 = re.compile(r"^[0-9a-f]{40}$")

EXPECTED_CANDIDATES = {
    "ATR2-C1-CODEBASE-CONTEXT-BAKEOFF",
    "ATR2-C2-INSPECT-EVAL-HARNESS",
    "ATR2-C3-PROMPTFOO-REDTEAM",
}
EXPECTED_PINS = {
    "GRAFT": ("@nanonets/graft", "0.10.1"),
    "CODEBASE_MEMORY": ("codebase-memory-mcp", "0.8.1"),
    "INSPECT_AI": ("inspect-ai", "0.3.258"),
    "PROMPTFOO": ("promptfoo", "0.122.0"),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> int:
    candidates = load(ROUND / "ROUND2_CANDIDATES.json")
    pins_doc = load(ROUND / "UPSTREAM_PINS.json")
    contract = (ROUND / "ROUND_CONTRACT.md").read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    lower = workflow.lower()

    if candidates.get("contract") != "AGENT_TOOL_SHADOW_ROUND2_v1":
        fail("candidate_contract_invalid")
    if candidates.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        fail("candidate_authority_invalid")
    if candidates.get("canonical_effect") is not False or candidates.get("portfolio_execution") is not False:
        fail("candidate_effect_invalid")
    if candidates.get("stage_a_auto_promotion_permitted") is not False:
        fail("stage_a_auto_promotion_must_be_false")
    if candidates.get("authority_ceiling") != "OPERATIONAL_HELPER":
        fail("authority_ceiling_invalid")

    rows = candidates.get("candidates")
    if not isinstance(rows, list) or {row.get("id") for row in rows} != EXPECTED_CANDIDATES:
        fail("candidate_set_invalid")
    for row in rows:
        if row.get("classification") != "SHADOW_TESTING":
            fail(f"candidate_not_shadow:{row.get('id')}")
        if not row.get("stage_a_success_criteria") or not row.get("stage_a_failure_criteria"):
            fail(f"candidate_missing_stage_a_contract:{row.get('id')}")
        if not str(row.get("stage_b_promotion_gate") or "").strip():
            fail(f"candidate_missing_stage_b_gate:{row.get('id')}")
        if not row.get("rollback_criteria") or not row.get("complexity_tax"):
            fail(f"candidate_missing_rollback_or_complexity:{row.get('id')}")
    bakeoff = next(row for row in rows if row["id"] == "ATR2-C1-CODEBASE-CONTEXT-BAKEOFF")
    if bakeoff.get("external_winner_limit") != 1:
        fail("context_bakeoff_must_allow_only_one_external_winner")
    if set(bakeoff.get("arms", [])) != {"BASELINE", "GRAFT", "CODEBASE_MEMORY"}:
        fail("context_bakeoff_arms_invalid")

    if pins_doc.get("contract") != "AGENT_TOOL_SHADOW_ROUND2_UPSTREAM_PINS_v1":
        fail("pins_contract_invalid")
    pins = {row.get("id"): row for row in pins_doc.get("pins", [])}
    if set(pins) != set(EXPECTED_PINS):
        fail("pin_set_invalid")
    for pin_id, (package, version) in EXPECTED_PINS.items():
        row = pins[pin_id]
        if row.get("package") != package or row.get("version") != version:
            fail(f"pin_mismatch:{pin_id}")
        if not SHA40.match(str(row.get("source_main_observed_sha") or "")):
            fail(f"source_sha_invalid:{pin_id}")
        if "latest" in str(row.get("version", "")).lower():
            fail(f"floating_version_forbidden:{pin_id}")

    if "Stage A can only produce" not in contract or "It cannot promote anything." not in contract:
        fail("round_contract_missing_nonpromotion_rule")
    if "no OpenAI key" not in contract:
        fail("round_contract_missing_no_openai_key_rule")

    required_workflow_tokens = [
        "pull_request:",
        "workflow_dispatch:",
        "contents: read",
        "node-version: '24'",
        "PYTHONDONTWRITEBYTECODE=1",
        "DO_NOT_TRACK=1",
        "PROMPTFOO_DISABLE_TELEMETRY=1",
        "PROMPTFOO_DISABLE_UPDATE=1",
        "PROMPTFOO_DISABLE_REMOTE_GENERATION=1",
        "PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=1",
        "PROMPTFOO_DISABLE_SHARING=1",
        "@nanonets/graft@0.10.1",
        "promptfoo@0.122.0",
        "inspect-ai==0.3.258",
        "codebase-memory-mcp==0.8.1",
        "shadow_round2_fixture.py",
        "shadow_round2_qualification.py",
        "shadow_guardrail_probe.py",
    ]
    for token in required_workflow_tokens:
        if token not in workflow:
            fail(f"workflow_missing_required_token:{token}")

    forbidden_workflow_tokens = [
        "schedule:",
        "contents: write",
        "secrets.",
        "openai_api_key",
        "graft init",
        "build --deep",
        "codebase-memory-mcp install",
        "codebase-memory-mcp update",
        "codebase-memory-mcp uninstall",
        "promptfoo eval",
        "promptfoo redteam run",
        "validate target",
        "@latest",
    ]
    for token in forbidden_workflow_tokens:
        if token in lower:
            fail(f"workflow_contains_forbidden_token:{token}")

    result = {
        "contract": "AGENT_TOOL_SHADOW_ROUND2_STATIC_VALIDATION_v1",
        "status": "PASS",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "candidate_count": len(rows),
        "pin_count": len(pins),
        "stage_a_auto_promotion_permitted": False,
        "market_decision_authority_permitted": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
