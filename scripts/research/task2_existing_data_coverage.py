#!/usr/bin/env python3
"""Task 2 available-data-first inventory; never score or disclose forecast outcomes.

Reads the immutable v2 original R1 admission *metadata* and emits only aggregate
feature/time coverage. It never claims external publication or actionability.
No API calls, provider payloads, forecasts or new execution authority.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

DEFAULT_SOURCE = Path(
    "04_MARKET_LEARNING/handlekompas/research/"
    "2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json"
)
CONTRACT = "TASK2_AVAILABLE_DATA_EXPLORATORY_COVERAGE_v1"
SOURCE_CONTRACT = "TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2"
STATES = {
    "RETRIEVAL_CLOCK_UNKNOWN",
    "ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN",
    "SETTLEMENT_IS_NOT_QUOTE_OBSERVATION",
}
# Owner classes are hypotheses about suitable matched ablations, not rankings.
FAMILY = {
    "HOURLY_SEQUENCE": "PRICE_BASELINE",
    "AUTO_MARKET_STATE_DELTA": "PRICE_BASELINE",
    "LIVE_ANCHOR_BREADTH_REFERENCE": "PARTICIPATION",
    "RICH_BREADTH_OWNER": "PARTICIPATION",
    "COINMARKETCAP_BTC_D": "ROTATION",
    "FARSIDE_SETTLED_ETF": "CAPITAL_FLOW",
    "DEFILLAMA_STABLECOINS": "CAPITAL_FLOW",
    "OKX_HOURLY_DERIVATIVES": "DERIVATIVES",
    "OKX_LIVE_SWAP": "DERIVATIVES",
    "CFGI": "SENTIMENT_COMPOSITE",
    "BLOCKCHAINCENTER": "ROTATION",
    "ENTRY_SIGNAL_LEDGER": "PREEXISTING_SIGNAL",
}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("INVALID_CLOCK")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("CLOCK_MISSING_TIMEZONE")
    return d.astimezone(timezone.utc)


def audit(document: dict, source_blob_sha: str) -> dict:
    if not isinstance(document, dict) or document.get("contract") != SOURCE_CONTRACT:
        raise ValueError("SOURCE_CONTRACT_INVALID")
    if document.get("status") != "RESEARCH_ONLY_NOT_ADMITTED":
        raise ValueError("SCIENTIFIC_GATE_UNEXPECTED")
    rows = document.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("ORIGINAL_ATTEMPT_UNIVERSE_MISSING")
    declared = document.get("cohort")
    if not isinstance(declared, dict) or declared.get("original_attempts") != len(rows):
        raise ValueError("ORIGINAL_ATTEMPT_DENOMINATOR_CONFLICT")
    original_outcome_counts = Counter()
    clock_counts = Counter()
    by_family = defaultdict(lambda: {"features": set(), "feature_observations": 0,
                                     "explicit_retrieval_clocks": 0,
                                     "independent_vendor_publications": 0,
                                     "observation_states": Counter()})
    ids = set()
    capture_refs = set()
    packet_refs = set()
    delivery_count = actionable_count = admitted_count = families_count = 0
    seen_features = None
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("FORECAST_ROW_INVALID")
        forecast_id = row.get("forecast_id")
        if not isinstance(forecast_id, str) or not forecast_id or forecast_id in ids:
            raise ValueError("ORIGINAL_FORECAST_ID_DUPLICATE_OR_INVALID")
        ids.add(forecast_id)
        issued = _time(row.get("issued_at_utc"))
        if row.get("admissibility") != "NOT_ADMITTED":
            raise ValueError("NO_IMPLICIT_SCIENTIFIC_PROMOTION")
        admitted_count += row["admissibility"] == "ADMITTED"
        delivery_count += row.get("first_user_delivery_at_utc") is not None
        actionable_count += row.get("first_actionable_at_utc") is not None
        families_count += row.get("independent_market_event_family") is not None
        outcome = row.get("original_outcome_status")
        if outcome not in ("PRESENT", "ABSENT_AT_ORIGINAL_SNAPSHOT"):
            raise ValueError("ORIGINAL_OUTCOME_STATUS_UNEXPECTED")
        original_outcome_counts[outcome] += 1
        c = row.get("raw_capture") or {}
        p = row.get("source_packet") or {}
        if not isinstance(c.get("git_blob_sha"), str) or not isinstance(p.get("git_blob_sha"), str):
            raise ValueError("ORIGINAL_SOURCE_IDENTITY_MISSING")
        capture_refs.add(c["git_blob_sha"])
        packet_refs.add(p["git_blob_sha"])
        features = row.get("selected_feature_clocks")
        if not isinstance(features, list) or len(features) != 24:
            raise ValueError("FROZEN_FEATURE_DENOMINATOR_CHANGED")
        per_row = set()
        for feature in features:
            fid, owner = feature.get("feature_id"), feature.get("source_owner")
            state = feature.get("observation_clock_status")
            if (not isinstance(fid, str) or not isinstance(owner, str)
                    or not fid or fid in per_row or owner not in FAMILY or state not in STATES):
                raise ValueError("FEATURE_CLOCK_SCHEMA_OR_ID_INVALID")
            per_row.add(fid)
            if feature.get("vendor_first_publication_at") is not None:
                raise ValueError("UNVERIFIED_VENDOR_CLOCK_CANNOT_BE_PROMOTED")
            recorded = feature.get("declared_retrieved_at")
            if recorded is not None:
                if _time(recorded) > issued:
                    raise ValueError("FEATURE_RETRIEVAL_AFTER_ORIGINAL_ISSUE")
                if state != "ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN":
                    raise ValueError("FEATURE_RETRIEVAL_SEMANTICS_CONFLICT")
            if state == "ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN" and recorded is None:
                raise ValueError("RETRIEVAL_CLOCK_MISSING_DESPITE_LABEL")
            clock_counts[state] += 1
            group = by_family[FAMILY[owner]]
            group["features"].add(fid)
            group["feature_observations"] += 1
            group["explicit_retrieval_clocks"] += recorded is not None
            group["observation_states"][state] += 1
        if seen_features is None:
            seen_features = per_row
        elif per_row != seen_features:
            raise ValueError("FEATURE_UNIVERSE_DRIFT_WITHIN_FROZEN_COHORT")

    if (original_outcome_counts.get("PRESENT", 0) != declared.get("original_outcomes_present")
            or original_outcome_counts.get("ABSENT_AT_ORIGINAL_SNAPSHOT", 0) != declared.get("original_outcomes_absent")
            or len(packet_refs) != declared.get("unique_source_blobs")
            or len(capture_refs) != declared.get("unique_raw_capture_blobs")
            or declared.get("admitted") != 0):
        raise ValueError("ORIGINAL_COHORT_DENOMINATOR_CHANGED")
    groups = [{
        "family": k,
        "feature_ids": sorted(v["features"]),
        "feature_observations": v["feature_observations"],
        "explicit_local_retrieval_clocks": v["explicit_retrieval_clocks"],
        "independently_verified_vendor_publication_clocks": 0,
        "clock_status_counts": dict(sorted(v["observation_states"].items())),
        "information_lift_vs_matched_price_only": None,
    } for k, v in sorted(by_family.items())]
    return {
        "contract": CONTRACT,
        "status": "EXPLORATORY_RESEARCH_ONLY_NOT_AN_EDGE_ESTIMATE",
        "input_contract": SOURCE_CONTRACT,
        "input_original_git_blob_sha": source_blob_sha,
        "original_forecast_attempts": len(rows),
        "original_12h_outcomes_at_pinned_snapshot": dict(sorted(original_outcome_counts.items())),
        "source_packet_dependency_groups": len(packet_refs),
        "raw_capture_dependency_groups": len(capture_refs),
        "unique_feature_ids": len(seen_features),
        "feature_observations": sum(clock_counts.values()),
        "clock_states": dict(sorted(clock_counts.items())),
        "explicit_local_retrieval_clocks": clock_counts[
            "ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN"],
        "independently_verified_vendor_publication_clocks": 0,
        "original_user_delivery_clocks": delivery_count,
        "original_actionable_clocks": actionable_count,
        "certified_independent_event_family_assignments": families_count,
        "scientifically_admitted_forecasts": admitted_count,
        "families": groups,
        "analysis_lanes": {
            "AVAILABLE_NOW": [
                "DESCRIPTIVE_MISSINGNESS_AND_SOURCE_DEPENDENCE",
                "HISTORICAL_RECONSTRUCTION_LABELED_EX_POST",
                "MATCHED_SOURCE_COVERAGE_AND_EXPLORATORY_ASSOCIATION_WHEN_RAW_VALUES_AUTHORIZED",
                "NEGATIVE_CONTROL_AND_BASELINE_CODE_TESTS_WITHOUT_SKILL_CLAIMS",
            ],
            "PROSPECTIVE_ON_EXISTING_CAPTURE_ONLY": [
                "AS_OF_KNOWN_PROSPECTIVE_FEATURE_GROUP_ABLATIONS",
                "FULL_NO_SIGNAL_AND_CENSORED_ATTEMPT_DENOMINATORS",
                "TIME_FROZEN_OUTCOME_AND_SAME_HORIZON_BASELINE",
            ],
            "BLOCKED_UNTIL_ORIGINAL_PROOF": [
                "CERTIFIED_NO_HINDSIGHT_HISTORICAL_R2",
                "PUBLISHED_FORECAST_SKILL_CLAIM",
                "INVESTOR_AFTER_COST_ACTION_LIFT",
            ],
        },
        "proposed_data_value_tests_not_results": [
            {"test": "PRICE_ONLY_VS_PRICE_PLUS_PARTICIPATION",
             "missing_to_verify": "BREADTH_AS_OF_UNIVERSE_AND_PUBLICATION_VINTAGE"},
            {"test": "PRICE_ONLY_VS_PRICE_PLUS_DERIVATIVES",
             "missing_to_verify": "OI_RETRIEVAL_END_AND_FUNDING_QUOTE_VS_SETTLEMENT_CLOCK"},
            {"test": "PRICE_ONLY_VS_PRICE_PLUS_SENTIMENT",
             "missing_to_verify": "CFGI_FIRST_PUBLICATION_AND_MODEL_ENGINE_ERA"},
            {"test": "PRICE_ONLY_VS_PRICE_PLUS_CAPITAL_FLOW",
             "missing_to_verify": "ETF_SETTLEMENT_RELEASE_TIME_AND_STABLECOIN_SOURCE_VINTAGE"},
            {"test": "PRICE_ONLY_VS_PRICE_PLUS_ROTATION",
             "missing_to_verify": "DOMINANCE_AND_ALTSEASON_AS_OF_UNIVERSE"},
        ],
        "unanswered_value_question": "NO_FEATURE_FAMILY_LIFT_MEASURED",
        "provider_backfill_semantics": "RETRIEVED_LATER_IS_RECONSTRUCTED_NOT_ORIGINAL_FIRST_KNOWN",
        "release": {"R1_admitted": False, "R2_certified": False,
                    "source_or_outcome_bytes_rewritten": False,
                    "paid_api_call": False, "portfolio_action": False},
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected-git-blob", default="")
    args = p.parse_args()
    raw = args.source.read_bytes()
    sha = git_blob_sha(raw)
    if args.expected_git_blob and sha != args.expected_git_blob:
        raise SystemExit("EXACT_FROZEN_SOURCE_BLOB_MISMATCH")
    result = audit(json.loads(raw), sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
