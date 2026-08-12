from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.api_agent.deep_research_executor import (
    authority_is_zero,
    coverage_gate_passes,
    prepare_provider_contract,
    select_followup,
    zero_authority,
)
from scripts.api_agent.mcp_transport_normalizer import normalize_mcp_contract, resolve_mcp_server_url
from scripts.api_agent.run_deep_research_task import evidence_bundle_valid


def scorecard():
    return {
        "providers": [
            {"provider": "CoinGecko", "state": "RESEARCH_ACTIVE_BASELINE"},
            {"provider": "Dune", "state": "READY_FOR_TOOL_DISCOVERY"},
        ]
    }


def queue():
    def item(rid, priority="P2", required=None):
        return {
            "id": rid,
            "priority": priority,
            "title": rid,
            "horizons": ["1_3D"],
            "question": rid,
            "primary_goal": rid,
            "hypothesis": rid,
            "baseline": rid,
            "decision_divergence": rid,
            "falsifier": rid,
            "kill_condition": rid,
            "required_providers": required or ["CoinGecko"],
            "optional_providers": [],
            "integration_ceiling": "RESEARCH_CONTEXT_ONLY",
            "canonical_links": {"open_questions": [], "active_tests": []},
        }
    return {
        "priority_order": ["P0", "P1", "P2"],
        "items": [
            item("DRQ-001", "P0"),
            item("DRQ-006", "P1"),
            item("DRQ-016", "P2"),
            item("DRQ-018", "P2"),
        ],
    }


def state():
    return {
        "active_research_id": "DRQ-001",
        "available_retained_providers": ["CoinGecko"],
        "item_states": {
            "DRQ-001": {"state": "ACTIVE_READY_FOR_RESEARCH", "missing_required_providers": []},
            "DRQ-006": {"state": "READY", "missing_required_providers": []},
            "DRQ-016": {"state": "READY", "missing_required_providers": []},
            "DRQ-018": {"state": "READY", "missing_required_providers": []},
        },
        "completed_research_ids": [],
        "held_research_ids": [],
    }


def policy():
    return {
        "event_priority": {
            "source_research_id": "DRQ-001",
            "condition_field": "horizon_conflict",
            "condition_value": True,
            "priority_target": "DRQ-016",
        },
        "coverage_gate": {
            "target_research_id": "DRQ-018",
            "required_coverage_contract": "BTC_PARTIAL_WAIT_COVERAGE_HEALTH_v1",
            "required_coverage_status": "COMPLETE_FOR_EXPECTED_CHECK_SET",
            "minimum_checks_total": 1,
        },
    }


def supplemental():
    return {
        "contract": "DEEP_RESEARCH_TASK_PACKET_v1",
        "status": "PREREGISTERED_SUPPLEMENTAL_RESEARCH",
        "research_id": "DRQ-CUAU-001",
        "priority": "P1_HIGH",
        "title": "Copper Gold",
        "horizons": ["WEEKLY"],
        "question": "decompose",
        "primary_goal": "decompose",
        "hypothesis": "horizon dependent",
        "baseline": "unchanged",
        "decision_divergence": "scope only",
        "falsifier": "not reproduced",
        "kill_condition": "explanatory only",
        "required_providers": [],
        "optional_retained_providers": [],
        "integration_ceiling": "RESEARCH_CONTEXT_ONLY",
        "canonical_links": {"active_tests": []},
        "authority": zero_authority(),
    }


def current_task():
    return {
        "research_id": "DRQ-001",
        "status": "READY",
        "authority": zero_authority(),
    }


def test_coingecko_endpoint_only_is_normalized_to_server_url():
    contract = {
        "provider": "CoinGecko",
        "transport": {"endpoint": "https://mcp.api.coingecko.com/mcp"},
    }
    normalized = normalize_mcp_contract(contract)
    assert normalized["transport"]["server_url"] == "https://mcp.api.coingecko.com/mcp"
    assert contract["transport"].get("server_url") is None


def test_matching_endpoint_and_server_url_are_accepted():
    url = "https://example.com/mcp"
    assert resolve_mcp_server_url({"transport": {"endpoint": url, "server_url": url}}) == url


def test_mismatched_endpoint_and_server_url_fail_closed():
    with pytest.raises(ValueError, match="mcp_transport_url_conflict"):
        resolve_mcp_server_url({
            "transport": {
                "endpoint": "https://one.example/mcp",
                "server_url": "https://two.example/mcp",
            }
        })


def test_non_https_transport_is_rejected():
    with pytest.raises(ValueError, match="verified_https_mcp_server_required"):
        resolve_mcp_server_url({"transport": {"endpoint": "http://example.com/mcp"}})


def test_prepared_provider_contract_adds_universal_mutation_denials():
    contract = {
        "provider": "CoinGecko",
        "transport": {"endpoint": "https://mcp.api.coingecko.com/mcp"},
        "forbidden_tool_name_fragments": ["custom_mutation"],
    }
    prepared = prepare_provider_contract(contract)
    forbidden = set(prepared["forbidden_tool_name_fragments"])
    assert {"trade", "order", "portfolio", "account", "create", "delete", "custom_mutation"} <= forbidden


def test_copper_gold_requires_independent_evidence_bundle():
    task = {"research_id": "DRQ-CUAU-001"}
    ok, reasons = evidence_bundle_valid(task, None)
    assert ok is False
    assert reasons == ["INDEPENDENT_EVIDENCE_BUNDLE_MISSING"]


def test_copper_gold_bundle_requires_both_series_hashes_and_provenance():
    task = {"research_id": "DRQ-CUAU-001"}
    incomplete = {
        "evidence_bundle_id": "bundle-1",
        "captured_at_utc": "2026-08-12T06:00:00Z",
        "source_series": {"copper": [1, 2], "gold": [3, 4]},
        "source_provenance": {"copper": "source-a"},
        "source_hashes": {"copper": "a" * 64},
    }
    ok, reasons = evidence_bundle_valid(task, incomplete)
    assert ok is False
    assert "COPPER_AND_GOLD_SOURCE_HASHES_REQUIRED" in reasons or "COPPER_AND_GOLD_PROVENANCE_REQUIRED" in reasons


def test_copper_gold_complete_independent_bundle_passes_preflight():
    task = {"research_id": "DRQ-CUAU-001"}
    bundle = {
        "evidence_bundle_id": "bundle-1",
        "captured_at_utc": "2026-08-12T06:00:00Z",
        "source_series": {"copper": [1, 2], "gold": [3, 4]},
        "source_provenance": {"copper": "source-a", "gold": "source-b"},
        "source_hashes": {"copper": "a" * 64, "gold": "b" * 64},
    }
    ok, reasons = evidence_bundle_valid(task, bundle)
    assert ok is True
    assert reasons == []


def test_drq018_coverage_gate_requires_observed_complete_checks():
    p = policy()
    assert coverage_gate_passes(None, p) is False
    assert coverage_gate_passes({
        "contract": "BTC_PARTIAL_WAIT_COVERAGE_HEALTH_v1",
        "coverage_status": "COMPLETE_FOR_EXPECTED_CHECK_SET",
        "checks_total": 0,
    }, p) is False
    assert coverage_gate_passes({
        "contract": "BTC_PARTIAL_WAIT_COVERAGE_HEALTH_v1",
        "coverage_status": "COMPLETE_FOR_EXPECTED_CHECK_SET",
        "checks_total": 1,
    }, p) is True


def test_drq001_horizon_conflict_prioritizes_drq016_before_cuau():
    updated, task = select_followup(
        queue(), state(), scorecard(), policy(), current_task(),
        {"horizon_conflict": True}, supplemental(), None, "COMPLETE",
    )
    assert updated["active_research_id"] == "DRQ-016"
    assert task["research_id"] == "DRQ-016"


def test_drq001_without_conflict_runs_preregistered_cuau_before_normal_p1():
    updated, task = select_followup(
        queue(), state(), scorecard(), policy(), current_task(),
        {"horizon_conflict": False}, supplemental(), None, "COMPLETE",
    )
    assert updated["active_research_id"] == "DRQ-CUAU-001"
    assert task["research_id"] == "DRQ-CUAU-001"
    assert task["status"] == "READY"


def test_after_supplemental_completion_base_queue_resumes_and_drq018_waits_for_coverage():
    s = state()
    s["active_research_id"] = "DRQ-CUAU-001"
    s["completed_research_ids"] = ["DRQ-001"]
    s["item_states"]["DRQ-001"] = {"state": "COMPLETE", "missing_required_providers": []}
    task = supplemental()
    task["status"] = "READY"
    updated, next_task = select_followup(
        queue(), s, scorecard(), policy(), task,
        {"horizon_conflict": False}, supplemental(), None, "COMPLETE",
    )
    assert updated["item_states"]["DRQ-018"]["state"] == "WAIT_PROSPECTIVE_COVERAGE"
    assert next_task["research_id"] == "DRQ-006"


def test_completion_authority_shape_is_zero():
    assert authority_is_zero({"authority": zero_authority()}) is True
    bad = zero_authority()
    bad["portfolio_action"] = True
    assert authority_is_zero({"authority": bad}) is False
