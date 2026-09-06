from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

from tests.api_agent.test_weekly_director_intraday_sequence import WeeklyDirectorIntradaySequenceTests  # noqa: F401


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/api_agent/augment_director_learning_context.py"
spec = importlib.util.spec_from_file_location("augment_director_learning_context", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_experiment_learning_prioritizes_supported_and_not_supported(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({
        "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION",
        "candidate_count": 3,
        "candidates": [
            {"candidate_id": "i", "state": "MATURED_INCONCLUSIVE", "title": "i"},
            {"candidate_id": "n", "state": "MATURED_NOT_SUPPORTED", "title": "n"},
            {"candidate_id": "s", "state": "MATURED_SUPPORTED", "title": "s"},
        ],
    }))
    out = module.experiment_learning(path)
    assert out["state_counts"]["MATURED_SUPPORTED"] == 1
    assert [row["state"] for row in out["decision_relevant_matured_examples"]] == [
        "MATURED_SUPPORTED", "MATURED_NOT_SUPPORTED", "MATURED_INCONCLUSIVE"
    ]
    assert "INCONCLUSIVE is never support" in out["instruction"]


def test_btc_dominance_uses_latest_direct_row(tmp_path: Path) -> None:
    path = tmp_path / "btcd.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "btc_dominance"])
        writer.writeheader()
        writer.writerow({"date": "2026-08-26", "btc_dominance": "55.1"})
        writer.writerow({"date": "2026-08-27", "btc_dominance": "54.9"})
    out = module.btc_dominance(path)
    assert out["row_count"] == 2
    assert out["latest"]["date"] == "2026-08-27"
    assert out["latest"]["btc_dominance"] == "54.9"
    assert "NO_PORTFOLIO_AUTHORITY" in out["authority"]


def test_exit_warning_calibration_preserves_valid_report(tmp_path: Path) -> None:
    path = tmp_path / "calibration.json"
    expected = {"contract": "ACTION_COMPASS_EXIT_WARNING_CALIBRATION_v1", "status": "PASS", "rows": []}
    path.write_text(json.dumps(expected))
    assert module.exit_warning_calibration(path) == expected


def test_exit_warning_calibration_marks_missing_and_invalid_without_fabrication(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert module.exit_warning_calibration(missing) == {"status": "UNAVAILABLE_NO_MATERIALIZED_REPORT"}
    invalid = tmp_path / "invalid.json"
    invalid.write_text("not-json")
    assert module.exit_warning_calibration(invalid) == {"status": "UNAVAILABLE_INVALID"}


def _write_research_states(tmp_path: Path, *, bad_authority: bool = False) -> tuple[Path, Path, Path]:
    authority = "CANONICAL" if bad_authority else "RESEARCH_ONLY_NON_CANONICAL"
    common = {
        "authority": authority,
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
        "external_provider_calls_authorized": False,
    }
    meta = tmp_path / "meta.json"
    memory = tmp_path / "memory.json"
    voi = tmp_path / "voi.json"
    meta.write_text(json.dumps({
        **common,
        "primary_action": "QUEUE_BOUNDED_RESEARCH",
        "primary_source": "SHADOW_REGISTRY",
        "primary_target": "CYCLE_NAVIGATOR_RESEARCH_FAMILY",
        "primary_execution_mode": "AUTO_LOCAL_RESEARCH",
        "reason": "recover evaluator",
        "sentinel_verdict": "PASS",
        "binding_integrity": "PRIMARY_COMPLETE",
        "active_heavy_workstreams": [{
            "orchestrator_action": "QUEUE_BOUNDED_RESEARCH",
            "source": "SHADOW_REGISTRY",
            "target": "CYCLE_NAVIGATOR_RESEARCH_FAMILY",
            "impact_tier": "MEDIUM",
        }],
        "queue": [],
    }))
    memory.write_text(json.dumps({
        **common,
        "selected_verdict": "DUPLICATE_EXACT",
        "selected_source": "SHADOW_REGISTRY",
        "selected_action": "RUN_INCREMENTAL_VALUE_TEST",
        "selected_target": "SENSOR_X",
        "reason": "already tested",
        "proposal_n": 1,
    }))
    voi.write_text(json.dumps({
        **common,
        "selected_source": "SHADOW_REGISTRY",
        "selected_action": "RECOVER_EVALUATOR",
        "selected_target": "CYCLE_NAVIGATOR_RESEARCH_FAMILY",
        "selected_impact_tier": "MEDIUM",
        "selected_decision_surface": "SENSOR_PORTFOLIO_QUALITY",
        "reason": "recover evaluator",
        "queue": [],
    }))
    return meta, memory, voi


def test_research_governance_learning_routes_bounded_prior_learning(tmp_path: Path) -> None:
    meta, memory, voi = _write_research_states(tmp_path)
    out = module.research_governance_learning(meta, memory, voi)
    assert out["status"] == "READY"
    assert out["authority"] == "RESEARCH_ONLY_NON_CANONICAL"
    assert out["canonical_effect"] is False
    assert out["portfolio_execution"] is False
    assert out["meta_orchestrator"]["primary_action"] == "QUEUE_BOUNDED_RESEARCH"
    assert out["memory_novelty"]["selected_verdict"] == "DUPLICATE_EXACT"
    assert out["decision_impact"]["selected_impact_tier"] == "MEDIUM"
    assert out["closure"] == "ROUTED_TO_FUTURE_DIRECTOR_CONTEXT"
    assert "no automatic canonical" in out["instruction"]


def test_research_governance_learning_fails_closed_on_authority_breach(tmp_path: Path) -> None:
    meta, memory, voi = _write_research_states(tmp_path, bad_authority=True)
    out = module.research_governance_learning(meta, memory, voi)
    assert out["status"] == "BLOCKED_AUTHORITY_FIREWALL"
    assert "meta" in out["invalid_states"]
    assert "memory" in out["invalid_states"]
    assert "decision_impact" in out["invalid_states"]


def test_research_governance_learning_reports_missing_without_invention(tmp_path: Path) -> None:
    out = module.research_governance_learning(tmp_path / "meta", tmp_path / "memory", tmp_path / "voi")
    assert out["status"] == "UNAVAILABLE"
    assert out["reason"] == "RESEARCH_GOVERNANCE_STATE_MISSING"
    assert out["missing"] == ["decision_impact", "memory", "meta"]
