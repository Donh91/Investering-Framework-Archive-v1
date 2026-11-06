#!/usr/bin/env python3
"""Task 2 archive-first descriptive evidence matrix, never an official scorer.

Reuses original M1 sensor audit, Shared Row frozen decisions and native outcome
receipt gate, and historical breadth/ETF/latency research. No API, market
source fetch, experiment admission, weights, positions, or state writes.
The ONLY permissible output is an explicit research-only JSON sidecar.

This is an existing-owner diagnostic within Archive #1596, not an alternative
Shared Row scoring authority. It does NOT authenticate vendor first-publication
or independently re-fetch every Git source blob from original capture commits.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import os
import tempfile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "research"))
import prospective_evidence_controller as original_row_gate
import shared_row_outcome_receipt_gate as original_outcome_gate

CONTRACT = "TASK2_ARCHIVE_FIRST_EDGE_EVIDENCE_MATRIX_v1"
AUTHORITY = "RESEARCH_ONLY_NON_CANONICAL"
M1 = "06_RESEARCH_LAB/audit_summaries/sensor_survival_v1/data/"
SHARED = "06_RESEARCH_LAB/shared_row_model_tournament_v1/"
SOURCES = {
    "m1_placebo": M1 + "M1_FREQUENCY_MATCHED_TIMING_PLACEBO.csv",
    "m1_rule_timing": M1 + "M1_RULE_TIMING_ATLAS.csv",
    "transmission_latency": M1 + "M4_STRATEGY_OPERATIONAL_LATENCY_TEST.csv",
    "shared_rows": SHARED + "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",
    "shared_outcomes": SHARED + "data/OUTCOME_DETAIL_LEDGER.csv",
    "shared_divergences": SHARED + "14_DIVERGENCE_FNP_LEDGER.csv",
    "shared_runtime": SHARED + "RUNTIME_STATUS.json",
    "shared_candidates": SHARED + "03_CANDIDATE_REGISTRY.json",
    "breadth_summary": "06_RESEARCH_LAB/audit_summaries/marginal_decision_breadth_v1/MACHINE_SUMMARY.json",
    "edge_admission": "04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK_1_5_EDGE_ADMISSION_GATE_v1.json",
    "archive_atlas": "research/altseason_atlas/SOURCE_MANIFEST_v1.json",
    "historical_terminal": "06_RESEARCH_LAB/historical_altseason_pullback_v1/ROUND2_TERMINAL_RESEARCH_DECISION.md",
    "etf_adjudication": "06_RESEARCH_LAB/m1_checkpoints/2026-10-05__RL-ETF-TEMPORAL-EDGE-001__FINAL_ADJUDICATION_v1.md",
}
CORE_IDS = (
    "C01_ETHBTC", "C02_BREADTH", "C03_BTCD", "C04_ETHBTC_BREADTH",
    "C05_ETHBTC_BTCD", "C06_BREADTH_BTCD", "C07_SIMPLE_3",
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


def utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("EXPLICIT_UTC_REQUIRED")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo != timezone.utc:
        raise ValueError("NON_UTC_OFFSET")
    return dt


def read_sources(root: Path) -> tuple[dict, dict]:
    content, provenance = {}, {}
    for label, rel in SOURCES.items():
        p = root / rel
        if not p.is_file() or p.is_symlink() or root.resolve() not in p.resolve().parents:
            raise ValueError("MISSING_OR_UNSAFE_PUBLIC_SOURCE:" + rel)
        raw = p.read_bytes()
        if not raw or len(raw) > 5_000_000:
            raise ValueError("UNEXPECTED_PUBLIC_SOURCE_SIZE:" + rel)
        provenance[label] = {
            "path": rel,
            "git_blob_sha1": hashlib.sha1(
                b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
            ).hexdigest(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
        if rel.endswith(".json"):
            content[label] = json.loads(raw)
        elif rel.endswith(".csv"):
            content[label] = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
        else:
            content[label] = raw.decode("utf-8")
    return content, provenance


def audit_e1(archive: dict) -> dict:
    rows = archive["m1_placebo"]
    pairs = {(int(r["window_days"]), r["entity_type"], r["entity"]): r for r in rows}
    table = []
    for days in (14, 21, 30, 45):
        family = pairs[(days, "family", "C")]
        c2 = pairs[(days, "rule", "C2")]
        table.append({
            "window_days": days,
            "c_family": {
                "unique_signal_dates": int(family["n_unique_signal_dates"]),
                "events_one_to_one": int(family["observed_one_to_one_events_hit"]),
                "frequency_matched_random_median": float(family["random_one_to_one_median"]),
                "reported_exploratory_p": float(family["p_random_one_to_one_ge_observed"]),
            },
            "c2_rule": {
                "unique_signal_dates": int(c2["n_unique_signal_dates"]),
                "events_one_to_one": int(c2["observed_one_to_one_events_hit"]),
                "frequency_matched_random_median": float(c2["random_one_to_one_median"]),
                "reported_exploratory_p": float(c2["p_random_one_to_one_ge_observed"]),
            },
        })
    c2_timing = [r for r in archive["m1_rule_timing"] if r["rule"] == "C2"]
    if len(c2_timing) != 1:
        raise ValueError("C2_ORIGINAL_TIMING_ROW_NOT_UNIQUE")
    r = c2_timing[0]
    if table[2]["c_family"]["reported_exploratory_p"] == table[2]["c2_rule"]["reported_exploratory_p"]:
        raise ValueError("FAMILY_RULE_CONFLATION")
    return {
        "status": "HISTORICAL_EXPLORATORY_NOT_NEW_PIT_OR_PROSPECTIVE",
        "role": "LEAN_WARNING_HYPOTHESIS_ONLY",
        "rule": "C2 ratio-5d<=-3%, frozen legacy source, not live threshold",
        "reported_comparison": table,
        "c2_original_unique_signal_dates": int(r["unique_signal_dates"]),
        "c2_original_unique_false_alarm_dates": int(r["unique_false_alarm_dates"]),
        "c2_reported_median_true_pre_lead_days": float(r["median_TRUE_PRE_lead_to_C5_days"]),
        "event_family_n_independent": None,
        "multiple_horizon_and_rule_selection_adjusted": False,
        "provider_publication_clocks_authenticated": False,
        "decision_value_proven": False,
    }


def _truth(value: str) -> bool | None:
    if value == "1":
        return True
    if value == "0":
        return False
    if value == "":
        return None
    raise ValueError("UNEXPECTED_ORIGINAL_BINARY_OUTCOME")


def _count(pred: bool, actual: bool, mat: dict) -> None:
    mat["n"] += 1
    mat["tp" if pred and actual else "fp" if pred else "fn" if actual else "tn"] += 1


def _source_shape(row: dict, floor: datetime) -> dict:
    if row.get("row_integrity_contract") != "SHARED_ROW_P0_BINDING_v1":
        raise ValueError("WRONG_ORIGINAL_ROW_CONTRACT")
    issue = utc(row["information_cutoff_utc"])
    if issue != utc(row["observation_timestamp_utc"]) or issue < floor:
        raise ValueError("INVALID_ORIGINAL_ROW_CLOCK")
    if not SHA40.fullmatch(row.get("source_version_commit") or ""):
        raise ValueError("INVALID_ORIGINAL_SOURCE_COMMIT")
    manifest = json.loads(row["source_binding_manifest"])
    if manifest.get("source_commit") != row["source_version_commit"]:
        raise ValueError("SOURCE_COMMIT_NOT_BOUND")
    if row.get("source_binding_manifest_sha256") != original_row_gate.core.sha_json(manifest):
        raise ValueError("SOURCE_MANIFEST_HASH_NOT_BOUND")
    for family in manifest.get("families", {}).values():
        if utc(family["capture_max_utc"]) > issue:
            raise ValueError("SOURCE_CAPTURE_AFTER_DECISION")
    original_row_gate.verify_frozen_provenance(row)
    decisions = json.loads(row["candidate_decisions"])
    original_row_gate.validate_core_decision_contract(row, decisions, set(CORE_IDS))
    if set(decisions) != set(CORE_IDS):
        raise ValueError("UNEXPECTED_CANDIDATE_SET")
    return decisions


def audit_e2(archive: dict, as_of: datetime) -> dict:
    runtime = archive["shared_runtime"]
    if (
        runtime.get("collection_state") != "ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION"
        or runtime.get("core_prospective_eligibility_status") != "ACTIVE_POST_REPAIR_FLOOR"
    ):
        raise ValueError("PROSPECTIVE_SOURCE_NOT_ACTIVE")
    floor = utc(runtime["core_prospective_eligibility_start"])
    registry = archive["shared_candidates"]
    if set(CORE_IDS) != {r["id"] for r in registry["candidates"] if r["id"] in CORE_IDS}:
        raise ValueError("CORE_REGISTRY_DRIFT")
    rows = archive["shared_rows"]
    if len({r["event_id"] for r in rows}) != len(rows):
        raise ValueError("DUPLICATE_ORIGINAL_EVENT")
    details = original_outcome_gate.detail_index(archive["shared_outcomes"])
    verdicts = {
        key: {"n": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0}
        for key in (*CORE_IDS, "B0_ALWAYS_POSITIVE", "B0_ALWAYS_NEGATIVE")
    }
    admitted, matured, positive, negative, pending = {}, {}, 0, 0, 0
    block_ids = set()
    future_rows = 0
    for row in rows:
        issue = utc(row["information_cutoff_utc"])
        if issue > as_of:
            future_rows += 1
            continue
        decisions = _source_shape(row, floor)
        # Existing original owner enforces full immutable outcome hashes, exact
        # source lineage, target clocks, prices and no synthetic early maturity.
        original_outcome_gate.verify_row_outcomes(row, details)
        admitted[row["event_id"]] = row
        block_ids.add((issue - floor) // timedelta(days=28))
        outcome = _truth(row["outcome_7d"])
        if outcome is not None:
            receipt = details.get((row["event_id"], "7d"), [])
            if len(receipt) != 1:
                raise ValueError("NO_UNIQUE_ORIGINAL_7D_RECEIPT")
            if utc(receipt[0]["matured_at_utc"]) > as_of:
                pending += 1
                continue
            matured[row["event_id"]] = row
            positive += int(outcome)
            negative += int(not outcome)
            for name, prediction in (
                *[(key, decisions[key]) for key in CORE_IDS],
                ("B0_ALWAYS_POSITIVE", True),
                ("B0_ALWAYS_NEGATIVE", False),
            ):
                _count(prediction, outcome, verdicts[name])
        else:
            pending += 1
    if matured and sum((positive, negative)) != len(matured):
        raise ValueError("MATURED_DENOMINATOR_MISMATCH")
    for state in verdicts.values():
        state["accuracy_pct"] = (
            round(100 * (state["tp"] + state["tn"]) / state["n"], 3)
            if state["n"] else None
        )
    # An original divergence record is only supplemental. It must not turn
    # numerous comparisons of one event into independent event families.
    seen_pairs = set()
    c02_c07 = {"disagreement_n_7d": 0, "c02_matches": 0, "c07_matches": 0}
    for div in archive["shared_divergences"]:
        event = div["event_id"]
        if event not in matured:
            continue
        key = (event, div["candidate_a"], div["candidate_b"])
        if key in seen_pairs:
            raise ValueError("DUPLICATE_ORIGINAL_DIVERGENCE")
        seen_pairs.add(key)
        original = matured[event]
        d = json.loads(original["candidate_decisions"])
        if (
            div["observation_timestamp_utc"] != original["observation_timestamp_utc"]
            or div["information_cutoff_utc"] != original["information_cutoff_utc"]
            or div["outcome_7d"] != original["outcome_7d"]
            or d[div["candidate_a"]] == d[div["candidate_b"]]
            or div["decision_a"].lower() != str(d[div["candidate_a"]]).lower()
            or div["decision_b"].lower() != str(d[div["candidate_b"]]).lower()
            or div["provenance_hash"] != hashlib.sha256(
                (original["provenance_hash"] + div["divergence_id"]).encode("utf-8")
            ).hexdigest()
        ):
            raise ValueError("DIVERGENCE_ORIGINAL_SOURCE_MISMATCH")
        if (div["candidate_a"], div["candidate_b"]) == (
            "C02_BREADTH", "C07_SIMPLE_3"
        ):
            c02_c07["disagreement_n_7d"] += 1
            actual = original["outcome_7d"] == "1"
            c02_c07["c02_matches"] += int(d["C02_BREADTH"] == actual)
            c02_c07["c07_matches"] += int(d["C07_SIMPLE_3"] == actual)
    return {
        "status": "DESCRIPTIVE_OWNER_RECEIPT_CHECKED_NO_GIT_ANCESTRY_REPLAY",
        "source_observations_seen": len(rows),
        "observations_through_as_of": len(admitted),
        "future_observations_excluded": future_rows,
        "matured_7d_rows": len(matured),
        "matured_7d_positive": positive,
        "matured_7d_negative": negative,
        "not_due_or_missing_7d": pending,
        "fixed_28d_block_n": len(block_ids),
        "independent_market_event_family_n": None,
        "models": verdicts,
        "c02_vs_c07_disagreements": c02_c07,
        "target": "ETHBTC_7D_FORWARD_RETURN_POSITIVE_NOT_BROAD_ALTSEASON",
        "label_source": "EXISTING_SHARED_ROW_OUTCOME_OWNER_ONLY",
        "provider_first_publication_authenticated_here": False,
        "independent_original_git_source_ancestry_replayed_here": False,
        "price_only_baseline_on_same_event_tested": False,
        "statistical_or_economic_edge_established": False,
        "winner_selected": False,
    }


def audit_e3(archive: dict) -> dict:
    breadth = archive["breadth_summary"]
    if breadth.get("source_truth", {}).get("snapshots_passed") != 184:
        raise ValueError("BREADTH_FROZEN_SOURCE_HAS_CHANGED_REAUDIT")
    if breadth.get("primary_verdicts", {}).get("breadth_predictive_gate") != "NOT_SUPPORTED":
        raise ValueError("BREADTH_NEGATIVE_VERDICT_CHANGED")
    all_latency = archive["transmission_latency"]
    delay = {int(r["extra_operational_delay_days_beyond_existing_1d_lag"]): float(r["total_return_pct"])
             for r in all_latency if r["strategy"] == "DEPLOYMENT_EXPANDING"}
    if 0 not in delay or 1 not in delay:
        raise ValueError("MISSING_TRANSMISSION_LATENCY_PAIR")
    etf = archive["etf_adjudication"]
    terminal = archive["historical_terminal"]
    if "Verdict: REJECTED" not in etf or "zero of 11 reload policies" not in terminal:
        raise ValueError("NEGATIVE_OWNER_RESEARCH_CHANGED")
    return {
        "status": "CONDITIONAL_SEQUENCE_NOT_PAIRED_ON_COMMON_TIMESTAMPS",
        "frozen_breadth_weekly_snapshots": breadth["source_truth"]["snapshots_passed"],
        "frozen_breadth_universe_rows": breadth["source_truth"]["frozen_universe_rows"],
        "breadth_added_mae_deterioration_pp": breadth["breadth_magnitude_mae_delta_pp_vs_price"],
        "breadth_standalone_predictive_gate": "NOT_SUPPORTED",
        "etf_outflow_strong_edge_verdict": "REJECTED_FROM_EXISTING_OWNER_ADJUDICATION",
        "deployment_expanding_historical_strategy_return_pct_0_extra_delay": round(delay[0], 6),
        "deployment_expanding_historical_strategy_return_pct_1_extra_day": round(delay[1], 6),
        "one_day_strategy_sensitivity_pp": round(delay[1] - delay[0], 6),
        "after_cost_investable_joint_sequence_comparator": None,
        "full_2020_2026_source_causal_pit_replay": False,
        "portfolio_edge_or_live_signal": False,
        "new_model_or_sensor_promoted": False,
    }


def build(root: Path, as_of: datetime) -> dict:
    inputs, provenance = read_sources(root)
    atlas = inputs["archive_atlas"]
    gate = inputs["edge_admission"]
    if (
        atlas["contract"] != "ALTSEASON_SOURCE_MANIFEST_v1"
        or atlas["authority"] != "NAVIGATION_ONLY"
        or not atlas["scoped_not_exhaustive"]
        or atlas["totals"]["public_entries"] != len(atlas["entries"])
        or gate["status"] != "BLOCKED_SCIENTIFIC_CLOSURE"
    ):
        raise ValueError("ARCHIVE_DISCOVERY_OR_PIT_GATE_CHANGED")
    if any(entry.get("repo") in {"Donh91/secrets", "Donh91/Meme-Alpha-Lab"}
           for entry in atlas["entries"]):
        raise ValueError("PRIVATE_ENTRY_IN_PUBLIC_ATLAS")
    return {
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "as_of_utc": as_of.isoformat().replace("+00:00", "Z"),
        "scope": "ARCHIVED_M1_SENSOR_AND_SHARED_ROW_BINARY_OUTCOMES_ONLY",
        "external_data_calls": 0,
        "source_manifest": provenance,
        "source_discovery": {
            "indexed_public_paths_not_semantically_reviewed_datasets": atlas["totals"]["public_entries"],
            "frozen_source_tree_count": len(atlas["source_root_tree_sha"]),
            "complete_whole_repo_crawl": False,
            "private_repo_values_imported": False,
        },
        "E1_warning": audit_e1(inputs),
        "E2_rotation": audit_e2(inputs, as_of),
        "E3_hidden_deterioration": audit_e3(inputs),
        "official_compass_original_scientific_gate": gate["status"],
        "round3_analysis_authorized": False,
        "source_first_known_vendor_authentication_added": False,
        "canonical_promotion_allowed": False,
        "automatic_model_weight_change": False,
        "portfolio_execution": False,
        "after_cost_edge_proven": False,
        "scientific_verdict": "INSUFFICIENT_EVIDENCE",
        "next_action": "REUSE_EXISTING_OWNER_PROSPECTIVE_SOURCE_VINTAGE_AND_DUE_OUTCOMES",
    }


ADVISORY_PATH = Path("research/framework_memory/task2_archive_first/LATEST.json")


def persist_advisory_if_changed(root: Path, document: dict) -> str:
    """Existing daily learning writer only. No new independent market owner.

    Suppress routine time-only updates. A malformed/untrusted previous public
    advisory fails closed instead of being silently rewritten or promoted.
    """
    if (
        document.get("contract") != CONTRACT
        or document.get("authority") != AUTHORITY
        or document.get("scientific_verdict") != "INSUFFICIENT_EVIDENCE"
        or document.get("canonical_promotion_allowed") is not False
        or document.get("automatic_model_weight_change") is not False
        or document.get("portfolio_execution") is not False
        or document.get("source_first_known_vendor_authentication_added") is not False
    ):
        raise ValueError("TASK2_PUBLIC_ADVISORY_AUTHORITY_BREACH")
    root = root.resolve()
    target = root / ADVISORY_PATH
    parent = target.parent
    # A public workflow may not follow a symlink to a private or other owner.
    if parent.is_symlink() or target.is_symlink() or (parent.exists() and not parent.is_dir()):
        raise ValueError("TASK2_ADVISORY_PATH_UNSAFE")
    if target.is_file():
        if target.stat().st_size > 2_000_000:
            raise ValueError("TASK2_ADVISORY_OLD_FILE_TOO_LARGE")
        old = json.loads(target.read_text(encoding="utf-8"))
        if old.get("contract") != CONTRACT or old.get("authority") != AUTHORITY:
            raise ValueError("TASK2_ADVISORY_PREVIOUS_CONTRACT_DRIFT")
        # All fields listed here represent upstream evidence, not the current
        # run timestamp. Never commit another copy merely for a new wake.
        stable = (
            "source_manifest", "E1_warning", "E2_rotation",
            "E3_hidden_deterioration", "official_compass_original_scientific_gate",
        )
        if all(old.get(key) == document.get(key) for key in stable):
            return "SOURCE_UNCHANGED_NO_WRITE"
    parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".task2-evidence-", suffix=".json", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, sort_keys=True, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temp, target)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return "SOURCE_CHANGED_ADVISORY_WRITTEN"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=str(REPO))
    p.add_argument("--as-of-utc")
    p.add_argument("--output")
    p.add_argument("--advisory-latest", action="store_true")
    args = p.parse_args()
    at = utc(args.as_of_utc) if args.as_of_utc else datetime.now(timezone.utc)
    result = build(Path(args.root).resolve(), at)
    serialized = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    if args.advisory_latest:
        print("TASK2_ARCHIVE_FIRST_ADVISORY", persist_advisory_if_changed(Path(args.root), result))


if __name__ == "__main__":
    main()
