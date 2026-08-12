from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.api_agent.mcp_provider_automation import (
    aggregate_receipts,
    auth_missing_evaluation,
    compact_receipt,
)


def receipt(**overrides):
    value = {
        "official_server_verified": True,
        "auth_secret_present": True,
        "auth_secret_persisted": False,
        "tool_discovery_status": "PASS",
        "discovered_tool_count": 10,
        "allowed_read_only_tool_count": 8,
        "mcp_call_count": 1,
        "successful_mcp_call_count": 1,
        "failed_mcp_call_count": 0,
        "mutating_tool_called": False,
        "provenance_complete": True,
        "research_questions_total": 1,
        "research_questions_answered": 1,
        "unique_value_items": 2,
        "overlap_items": 1,
        "manual_intervention_count": 0,
        "production_dependency": False,
        "canonical_owner_replaced": False,
        "provider_cost_status": "UNKNOWN",
        "hard_blockers": [],
        "openai_estimated_cost_usd": 0.01,
    }
    value.update(overrides)
    return value


def test_provider_aggregate_preserves_provenance_and_sums_only_bounded_receipts():
    rows = [compact_receipt(receipt()), compact_receipt(receipt(unique_value_items=1, overlap_items=0))]
    agg = aggregate_receipts("Dune", "research/api_agent/mcp/DUNE_MCP_RESEARCH_RECOVERY_v1.json", rows)
    assert agg["research_questions_total"] == 2
    assert agg["research_questions_answered"] == 2
    assert agg["mcp_call_count"] == 2
    assert agg["successful_mcp_call_count"] == 2
    assert agg["provenance_complete"] is True
    assert agg["mutating_tool_called"] is False
    assert agg["openai_estimated_cost_usd"] == 0.02
    assert not any(agg["authority"].values())


def test_provider_aggregate_carries_hard_blocker_forward():
    rows = [compact_receipt(receipt()), compact_receipt(receipt(hard_blockers=["MUTATING_TOOL_CALLED"], mutating_tool_called=True))]
    agg = aggregate_receipts("Dune", "x.json", rows)
    assert "MUTATING_TOOL_CALLED" in agg["hard_blockers"]
    assert agg["mutating_tool_called"] is True
    assert agg["status"] == "PARTIAL"


def test_missing_specific_provider_auth_is_data_blocked_not_kill():
    evaluation = auth_missing_evaluation("Dune", Path("receipt.json"), "RESEARCH_ACTIVE")
    assert evaluation["deterministic_verdict"] == "DATA_BLOCKED"
    assert evaluation["ai_red_team_required"] is False
    assert evaluation["hard_blockers"] == ["AUTH_MISSING_EXTERNAL_DEPENDENCY"]
    assert not any(evaluation["authority"].values())


def test_automation_state_has_zero_authority():
    state = json.loads((ROOT / "research/api_agent/coordination/LATEST_RESEARCH_AUTOMATION_STATE.json").read_text())
    assert state["contract"] == "RESEARCH_AUTOMATION_STATE_v1"
    assert state["last_heavy_lane"] is None
    assert not any(state["authority"].values())


def test_high_impact_safepoint_receipt_precedes_workflow_change():
    safety = json.loads((ROOT / "research/repository_safety/2026-08-12__research-automation-wiring-safepoint-receipt.json").read_text())
    assert safety["verification_result"] == "PASS_INTERNAL_SAFEPOINT_VERIFIED"
    assert safety["source_commit_sha"] == safety["safepoint_sha"]
    assert safety["safepoint_branch"].startswith("backup-safepoint/")
    assert safety["external_vault_claimed_complete"] is False
    assert safety["deletions"] == []
    assert safety["force_operations"] is False


def test_workflow_uses_single_writer_lock_budget_guard_and_one_lane_selector():
    text = (ROOT / ".github/workflows/research-execution-coordinator.yml").read_text()
    assert "group: framework-main-writer" in text
    assert "cancel-in-progress: false" in text
    assert "research_execution_coordinator.py" in text
    assert "check_monthly_cost_guard.py" in text
    assert "--hard-stop-usd 20" in text
    assert "--reserve-usd 0.75" in text
    assert "run_deep_research_task.py" in text
    assert "mcp_provider_automation.py" in text
    assert "pull_request:" not in text


def test_workflow_has_no_market_or_portfolio_writer_path():
    text = (ROOT / ".github/workflows/research-execution-coordinator.yml").read_text()
    git_add_block = text.split("git add", 1)[1]
    assert "01_CORE_FRAMEWORK" not in git_add_block
    assert "02_MARKET" not in git_add_block
    assert "Cycle Navigator" not in git_add_block
    assert "portfolio" not in git_add_block.lower()
    assert "research/api_agent" in git_add_block


def test_workflow_specific_provider_secrets_are_runtime_only():
    text = (ROOT / ".github/workflows/research-execution-coordinator.yml").read_text()
    for secret_name in [
        "OPENAI_API_KEY",
        "DUNE_API_KEY",
        "LUNARCRUSH_API_KEY",
        "CMC_MCP_API_KEY",
        "THEGRAPH_GATEWAY_API_KEY",
        "ALTFINS_API_KEY",
    ]:
        assert f"secrets.{secret_name}" in text
    assert "git add .env" not in text
    assert "echo $DUNE_API_KEY" not in text
