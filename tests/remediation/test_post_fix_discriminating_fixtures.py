"""Discriminating fixture checks for #2352; not an observation/completion engine.

The pre-fix controls are archived evidence where available, otherwise explicit
reconstructions of the documented failure mode. The post-fix side calls the
original owner implementation or uses its dated capture. Natural-run and
consumer joins are deliberately NOT inferred from these local tests.
"""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def owner_test_module(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_2142_archived_false_pass_vs_recomputed_health():
    from scripts.data_ping.auto_market_state import sentiment_source_health
    owner = owner_test_module(
        "tests/data_ping/test_auto_market_state_sentiment_completeness.py", "sentiment_owner_fixture")
    for path, expected in [(owner.NEGATIVE, "UNAVAILABLE"), (owner.POSITIVE, "PASS")]:
        before = path.read_bytes()
        packet = json.loads(before)
        old = packet["source_health"]["sentiment"]["status"]
        if expected == "UNAVAILABLE":
            assert old != expected  # archived pre-fix false PASS
        else:
            assert old == expected  # positive control must stay valid
        assert sentiment_source_health(packet["normalized_state"]["sentiment"])["status"] == expected
        assert path.read_bytes() == before


def test_1675_censored_and_physical_maturity_do_not_create_scientific_score(tmp_path):
    owner = owner_test_module("tests/experiments/test_experiment_lifecycle.py", "lifecycle_owner_fixture")
    case = owner.CensoredOutcomeIntegrityTests()
    outcomes = [
        case.outcome("EXP-FC-1", result="HIT"),
        case.outcome("EXP-FC-2", status="CENSORED", result=None, score=False),
    ]
    try:
        actual = case.sample_registry(tmp_path, outcomes)["candidates"][0]
    finally:
        case.doCleanups()
    expected = {"outcome_record_count": 2, "matured_outcome_count": 1,
                "censored_outcome_count": 1, "scientific_score_eligible_outcome_count": 0}
    # Reconstructed false admission: trusting the row's self-claimed score flag.
    pre = {**expected, "scientific_score_eligible_outcome_count": 1}
    def reconciles(row):
        return all(row.get(key) == value for key, value in expected.items())
    assert not reconciles(pre)
    assert reconciles(actual)


def test_927_same_week_overwrite_vs_original_owner_persistence(tmp_path, monkeypatch):
    from scripts.research import shadow_registry_weekly as runtime
    owner = owner_test_module("tests/research/test_shadow_registry_runtime_integrity.py", "shadow_owner_fixture")
    monkeypatch.setattr(runtime, "OUTDIR", tmp_path / "weekly")
    monkeypatch.setattr(runtime, "LATEST", tmp_path / "LATEST.json")
    first = owner.weekly_fixture()
    second = {**first, "generated_at_utc": "2026-09-01T01:00:00Z"}
    assert runtime.persist_snapshot(first) == "CREATED"
    history = runtime.OUTDIR / "2026-W36.json"
    original = history.read_bytes()
    # Reconstructed old overwrite bug, confined to temporary files.
    history.write_text(json.dumps(second))
    assert history.read_bytes() != original
    history.write_bytes(original)
    assert runtime.persist_snapshot(second) == "PRESERVED_EXISTING"
    assert history.read_bytes() == original
    assert json.loads(runtime.LATEST.read_text()) == second


def test_843_aggregate_only_vs_exact_immutable_reason_census(tmp_path):
    from scripts.learning.outcome_censor_reason_summary import build_summary
    rows = [
        {"status": "CENSORED", "reason": "LEGACY_V1_TARGET_UNIT_AMBIGUOUS"},
        {"status": "CENSORED", "reason": "NO_EVIDENCE_WITHIN_MAX_LAG"},
        {"status": "CENSORED", "reason": "NEW_UNRECOGNIZED_REASON"},
        {"status": "CENSORED"},
        {"status": "MATURED", "result": "HIT"},
    ]
    for i, row in enumerate(rows):
        (tmp_path / f"{i}.json").write_text(json.dumps({"contract": "MATURED_OUTCOME_v3", **row}))
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    expected = {"LEGACY_V1_TARGET_UNIT_AMBIGUOUS": 1, "NO_EVIDENCE_WITHIN_MAX_LAG": 1,
                "NEW_UNRECOGNIZED_REASON": 1, "MISSING_REASON": 1}
    def reconciles(row):
        return (row.get("total_outcomes") == len(rows)
                and row.get("censored_outcomes") == sum(expected.values())
                and row.get("reason_counts") == expected
                and row.get("reason_class_counts", {}).get("UNCLASSIFIED_FAIL_CLOSED") == 2)
    assert not reconciles({"total_outcomes": 5, "censored_outcomes": 4})
    assert reconciles(build_summary(tmp_path))
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


def test_713_original_leakage_vs_dated_exact_taxonomy_capture():
    owner = owner_test_module("tests/remediation/test_post_fix_breadth_capture_census.py", "breadth_owner_fixture")
    snapshot, receipt = owner.load_capture()
    pre = copy.deepcopy(snapshot)
    for row, leaked in zip(pre["constituents"], ("usd1", "usdg", "rlusd", "gho")):
        row["symbol"] = leaked
    with pytest.raises(AssertionError):
        owner.check_census(pre, receipt)
    owner.check_census(snapshot, receipt)


def test_no_new_completion_specs_without_same_run_owner_proof():
    spec = json.loads((ROOT / "research/codex/post_fix_verification_specs_v1.json").read_text())
    assert {row["candidate_id"] for row in spec["candidates"]} == {
        "codex-research-completion-reconciliation-v1",
        "codex-operational-observability-pointer-truth-v1",
        "codex-automation-health-workflow-pagination-v1",
        "codex-automation-health-cadence-aware-staleness-v1",
        "codex-research-alpha-adversarial-runtime-wiring-v1",
        "codex-research-adversarial-operator-qualification-enrichment-v1",
        "codex-situation-room-daily-static-root-cause-v1",
    }
