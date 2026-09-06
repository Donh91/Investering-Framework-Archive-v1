from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/api_agent/augment_director_compounding_learning_context.py"
WORKFLOW = ROOT / ".github/workflows/daily-director-shadow.yml"
spec = importlib.util.spec_from_file_location("augment_director_compounding_learning_context", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def _write_surfaces(tmp_path: Path, *, breach: bool = False) -> tuple[Path, Path, Path, Path]:
    state = tmp_path / "STATE.json"
    proposal = tmp_path / "NEXT_BEST_EXPERIMENT.json"
    backlog = tmp_path / "LEARNING_BACKLOG.json"
    health = tmp_path / "HEALTH.json"

    state.write_text(json.dumps({
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": breach,
        "portfolio_execution": False,
        "automatic_canonical_write": False,
        "automatic_market_rule_change": False,
        "automatic_promotion": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
        "generated_at_utc": "2026-09-05T07:53:55Z",
        "adjudication_generated_at_utc": "2026-09-05T07:53:55Z",
        "checkpoint_packet_count": 2,
        "evidence_fingerprint": "abc",
        "hypothesis_families": [
            {"redundancy_collinearity_warning": True},
            {"redundancy_collinearity_warning": False},
        ],
    }))
    proposal.write_text(json.dumps({
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "automatic_execution": False,
        "automatic_market_rule_change": False,
        "automatic_parameter_search": False,
        "automatic_promotion": False,
        "automatic_threshold_change": False,
        "model_weight_change": False,
        "candidate_test_id": "NBT-1",
        "parent_candidate_id": "EC-1",
        "action": "RUN_INCREMENTAL_VALUE_TEST",
        "test_type": "INCREMENTAL_VALUE_AND_ADVERSARIAL_REPLICATION_TEST",
        "problem_uncertainty": "INCREMENTAL_VALUE_UNRESOLVED",
        "proposed_priority": 1,
        "expected_information_gain": {"score": 91.0},
        "proposal_status": "PROPOSAL_ONLY_ROUTE_THROUGH_EXISTING_RESEARCH_GOVERNANCE_AND_SCIENTIFIC_ADMISSION",
        "requires_scientific_admission": True,
        "new_test_automatically_admitted": False,
        "redundancy_risk": "NORMAL",
        "what_would_change_our_view": "prospective disconfirmation",
        "revisit_condition": "AFTER_NEW_MATURE_EVIDENCE",
    }))
    backlog.write_text(json.dumps({
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "entry_count": 2,
        "entries": [
            {"rank": 1, "status": "SELECTED_NEXT_BEST_TEST", "candidate_test_id": "NBT-1", "test_type": "INCREMENTAL_VALUE", "problem_uncertainty": "A", "score": 91.0, "requires_scientific_admission": True},
            {"rank": 2, "status": "RANKED_NOT_SELECTED", "candidate_test_id": "NBT-2", "test_type": "REGIME_SPECIFICITY", "problem_uncertainty": "B", "score": 88.0, "requires_scientific_admission": True},
        ],
    }))
    health.write_text(json.dumps({
        "contract": "COMPOUNDING_LEARNING_HEALTH_v1",
        "status": "PASS",
        "blockers": [],
        "authority": {"canonical_effect": False, "portfolio_execution": False},
        "summary": {"backlog_entry_count": 2, "run_disposition": "MATERIAL_LEARNING_DELTA"},
    }))
    return state, proposal, backlog, health


def test_compounding_learning_routes_compact_context(tmp_path: Path) -> None:
    state, proposal, backlog, health = _write_surfaces(tmp_path)
    out = module.compounding_learning(state, proposal, backlog, health)
    assert out["status"] == "READY"
    assert out["canonical_effect"] is False
    assert out["portfolio_execution"] is False
    assert out["controller"]["redundancy_collinearity_warning_count"] == 1
    assert out["next_best_test"]["candidate_test_id"] == "NBT-1"
    assert out["next_best_test"]["requires_scientific_admission"] is True
    assert out["backlog"]["entry_count"] == 2
    assert len(out["backlog"]["top_entries"]) == 2
    assert out["closure"] == "COMPOUNDING_LEARNING_ROUTED_TO_FUTURE_DIRECTOR_CONTEXT"


def test_compounding_learning_fails_closed_on_authority_breach(tmp_path: Path) -> None:
    state, proposal, backlog, health = _write_surfaces(tmp_path, breach=True)
    out = module.compounding_learning(state, proposal, backlog, health)
    assert out["status"] == "BLOCKED_AUTHORITY_OR_HEALTH_FIREWALL"
    assert "state" in out["invalid_states"]


def test_compounding_learning_reports_missing_without_invention(tmp_path: Path) -> None:
    out = module.compounding_learning(
        tmp_path / "state",
        tmp_path / "proposal",
        tmp_path / "backlog",
        tmp_path / "health",
    )
    assert out["status"] == "UNAVAILABLE"
    assert out["reason"] == "COMPOUNDING_LEARNING_SURFACE_MISSING"
    assert out["missing"] == ["backlog", "health", "proposal", "state"]


def test_daily_director_workflow_routes_compounding_after_existing_learning_context() -> None:
    text = WORKFLOW.read_text()
    existing = "python scripts/api_agent/augment_director_learning_context.py"
    compounding = "python scripts/api_agent/augment_director_compounding_learning_context.py"
    assert existing in text
    assert compounding in text
    assert text.index(existing) < text.index(compounding)
