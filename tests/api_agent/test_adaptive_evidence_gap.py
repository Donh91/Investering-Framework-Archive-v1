from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def policy():
    return json.loads((ROOT / "research/evidence_gap/EVIDENCE_GAP_FAMILY_POLICY_v1.json").read_text())


def test_gap_key_deduplicates_semantically_same_observation_identity():
    mod = load("gap_registry", "scripts/api_agent/evidence_gap_registry.py")
    base = {
        "metric_name": "ETH/BTC persistence above 0.0300",
        "data_shape": "TIME_SERIES",
        "capability_hint": "HOURLY_SEQUENCE",
        "desired_cadence_minutes": 60,
    }
    changed_rationale = dict(base, decision_relevance="new words")
    assert mod.gap_key(base) == mod.gap_key(changed_rationale)


def test_hourly_metric_wording_maps_to_one_durable_family():
    mod = load("gap_registry_family_hourly", "scripts/api_agent/evidence_gap_registry.py")
    a = {"metric_name": "Validated hourly BTC/ETH/ETH-BTC price sequence", "capability_hint": "HOURLY_SEQUENCE"}
    b = {"metric_name": "Fixed-anchor hourly BTC, ETH, and ETH/BTC price-return sequence", "capability_hint": "HOURLY_SEQUENCE"}
    assert mod.gap_family(a, policy()) == "EG-HOURLY-SEQUENCE"
    assert mod.gap_family(b, policy()) == "EG-HOURLY-SEQUENCE"


def test_market_structure_overrides_misrouted_live_breadth_hint():
    mod = load("gap_registry_market_structure", "scripts/api_agent/evidence_gap_registry.py")
    candidate = {
        "metric_name": "BTC dominance, Total2, Total3, and stablecoin-dominance history",
        "capability_hint": "LIVE_BREADTH",
    }
    assert mod.gap_family(candidate, policy()) == "EG-MARKET-STRUCTURE"


def test_ambiguous_repo_derivations_map_by_work_family():
    mod = load("gap_registry_ambiguous", "scripts/api_agent/evidence_gap_registry.py")
    assert mod.gap_family(
        {"metric_name": "Matured candidate outcome and benchmark score series", "capability_hint": "EXISTING_REPO_DERIVATION"},
        policy(),
    ) == "EG-FORECAST-OUTCOMES"
    assert mod.gap_family(
        {"metric_name": "Timestamped BTC/ETH funding-rate history by venue", "capability_hint": "EXISTING_REPO_DERIVATION"},
        policy(),
    ) == "EG-DERIVATIVES-FORENSICS"
    assert mod.gap_family(
        {"metric_name": "ETHBTC level test and persistence history", "capability_hint": "EXISTING_REPO_DERIVATION"},
        policy(),
    ) == "EG-HOURLY-SEQUENCE"


def test_unknown_source_is_classified_without_creating_metric_specific_owner():
    mod = load("gap_registry_unknown_family", "scripts/api_agent/evidence_gap_registry.py")
    assert mod.gap_family(
        {"metric_name": "CFGI aggregate and component history", "capability_hint": "UNKNOWN_SOURCE"},
        policy(),
    ) == "EG-SENTIMENT"
    assert mod.gap_family(
        {"metric_name": "Market-capitalization and dominance history", "missing_history_problem": "BTC dominance and Total2 missing", "capability_hint": "UNKNOWN_SOURCE"},
        policy(),
    ) == "EG-MARKET-STRUCTURE"


def test_legacy_registry_migration_preserves_rows_and_collapses_families():
    mod = load("gap_registry_migration", "scripts/api_agent/evidence_gap_registry.py")
    reg = {
        "items": {
            "EG-old-a": {
                "metric_name": "Daily settled BTC and ETH ETF net-flow history",
                "capability_hint": "SETTLED_ETF",
                "first_seen_utc": "2026-08-15T00:00:00Z",
                "last_seen_utc": "2026-08-16T00:00:00Z",
                "observation_count": 2,
                "closure_state": "BACKFILL_QUEUED",
                "evidence_reference": "a",
            },
            "EG-old-b": {
                "metric_name": "Settled BTC and ETH ETF flow series",
                "capability_hint": "SETTLED_ETF",
                "first_seen_utc": "2026-08-17T00:00:00Z",
                "last_seen_utc": "2026-08-17T00:00:00Z",
                "observation_count": 1,
                "closure_state": "BACKFILL_QUEUED",
                "evidence_reference": "b",
            },
            "EG-old-c": {
                "metric_name": "Comparable daily macro context history",
                "capability_hint": "FRED_MACRO",
                "first_seen_utc": "2026-08-18T00:00:00Z",
                "last_seen_utc": "2026-08-18T00:00:00Z",
                "observation_count": 1,
                "closure_state": "BACKFILL_QUEUED",
                "evidence_reference": "c",
            },
        }
    }
    migrated = mod.migrate_registry(reg, policy(), "2026-08-28T00:00:00Z")
    assert set(migrated["items"]) == {"EG-ETF-FLOWS", "EG-MACRO-HISTORY"}
    etf = migrated["items"]["EG-ETF-FLOWS"]
    assert etf["observation_count"] == 3
    assert etf["observation_variant_count"] == 2
    assert set(etf["legacy_gap_ids"]) == {"EG-old-a", "EG-old-b"}
    assert len(etf["observations"]) == 2


def test_mixed_family_closure_state_is_fail_closed_to_hardest_active_path():
    mod = load("gap_registry_state", "scripts/api_agent/evidence_gap_registry.py")
    observations = [
        {"closure_state": "BACKFILL_QUEUED"},
        {"closure_state": "PROSPECTIVE_CAPTURE_REQUIRED"},
        {"closure_state": "SOURCE_DISCOVERY_REQUIRED"},
    ]
    assert mod.aggregate_state(observations) == "SOURCE_DISCOVERY_REQUIRED"


def test_backfillable_capability_routes_to_backfill():
    mod = load("gap_registry_backfill", "scripts/api_agent/evidence_gap_registry.py")
    state, _ = mod.route(
        {"capability_hint": "HOURLY_SEQUENCE"},
        {"HOURLY_SEQUENCE": {"historical_backfill": True, "prospective_capture": True, "closure_mode": "BACKFILL_OR_EXISTING_ARCHIVE"}},
    )
    assert state == "BACKFILL_QUEUED"


def test_perishable_capability_routes_to_prospective_capture():
    mod = load("gap_registry_prospective", "scripts/api_agent/evidence_gap_registry.py")
    state, _ = mod.route(
        {"capability_hint": "PULLBACK_FORENSICS"},
        {"PULLBACK_FORENSICS": {"historical_backfill": False, "prospective_capture": True, "closure_mode": "PROSPECTIVE_CAPTURE_ONLY_FOR_PERISHABLE_FIELDS"}},
    )
    assert state == "PROSPECTIVE_CAPTURE_REQUIRED"


def test_unknown_source_never_auto_backfills():
    mod = load("gap_registry_unknown", "scripts/api_agent/evidence_gap_registry.py")
    state, _ = mod.route(
        {"capability_hint": "UNKNOWN_SOURCE"},
        {"UNKNOWN_SOURCE": {"historical_backfill": False, "prospective_capture": False, "closure_mode": "SOURCE_DISCOVERY_REQUIRED"}},
    )
    assert state == "SOURCE_DISCOVERY_REQUIRED"


def test_auditor_schema_forbids_market_semantic_fields():
    mod = load("gap_auditor", "scripts/api_agent/adaptive_evidence_gap_auditor.py")
    candidate = mod.schema()["properties"]["candidates"]["items"]
    props = set(candidate["properties"])
    assert "threshold" not in props
    assert "weight" not in props
    assert "buy" not in props
    assert "sell" not in props
    assert candidate["additionalProperties"] is False
