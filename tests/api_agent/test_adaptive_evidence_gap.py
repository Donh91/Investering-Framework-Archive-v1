from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_gap_key_deduplicates_semantically_same_identity():
    mod = load("gap_registry", "scripts/api_agent/evidence_gap_registry.py")
    base = {
        "metric_name": "ETH/BTC persistence above 0.0300",
        "data_shape": "TIME_SERIES",
        "capability_hint": "HOURLY_SEQUENCE",
        "desired_cadence_minutes": 60,
    }
    changed_rationale = dict(base, decision_relevance="new words")
    assert mod.gap_key(base) == mod.gap_key(changed_rationale)


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
