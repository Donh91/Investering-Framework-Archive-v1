#!/usr/bin/env python3
"""ARP-02 / Risk #1553: source-locked HRE price warning confusion sensitivity.

This computes hypothetical classification-loss identities on the ORIGINAL
overlapping retrospective HRE matrix. It never infers actual investor alerts,
historical provider first-known, financial PnL, independent market crises or
permission to change production warning thresholds.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = "research/historical_reality_engine/CROSS_ERA_NATIVE_RESULTS_20261107.json"
SOURCE_BLOB_SHA1 = "2f46169590ae208f724d783c70a545bfceb228fb"
CONTRACT = "ARP02_HRE_PRICE_WARNING_COST_SENSITIVITY_V1"
ERAS = ("terra_2022", "ftx_2022", "usdc_2023", "aug_2024", "feb_2026")
ASSETS = ("BTCUSDT", "ETHUSDT")
CLASSIFIERS = ("price_baseline", "price_candidate")
FIELDS = ("tp", "fp", "fn", "tn")


def read_source(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    candidate = root / SOURCE_PATH
    if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(root):
        raise ValueError("HRE_SOURCE_PATH_UNVERIFIED")
    raw = candidate.read_bytes()
    blob_hash = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob_hash != SOURCE_BLOB_SHA1:
        raise ValueError("HRE_NATIVE_SOURCE_BLOB_DRIFT")
    return json.loads(raw)


def evaluate(source: dict) -> dict:
    if (source.get("contract") != "HRE_CROSS_ERA_NATIVE_RESULTS_V1"
            or source.get("historical_source_class") !=
            "POSTHOC_PRICE_TRUTH_TAPE_NOT_ORIGINAL_PROVIDER_FIRST_KNOWN"
            or source.get("quote_unit") != "USDT"):
        raise ValueError("HRE_SOURCE_AUTHORITY_OR_QUOTE_MISMATCH")
    episodes = source.get("episodic_results")
    if (not isinstance(episodes, list) or len(episodes) != len(ERAS)
            or tuple(e.get("episode_id") for e in episodes if isinstance(e, dict)) != ERAS):
        raise ValueError("HRE_EPISODE_ROSTER_OR_ORDER_DRIFT")
    totals = {a: {name: {k: 0 for k in FIELDS} for name in CLASSIFIERS} for a in ASSETS}
    per_era = []
    for episode in episodes:
        n = episode.get("utc_daily_cutoffs_per_asset")
        if type(n) is not int or n <= 0:
            raise ValueError("INVALID_ORIGINAL_CUTOFF_COUNT")
        row = {"episode_id": episode["episode_id"], "daily_cutoffs_per_asset": n}
        for asset in ASSETS:
            source_rows = episode.get(asset)
            if not isinstance(source_rows, dict):
                raise ValueError("MISSING_HRE_ASSET")
            row[asset] = {}
            for name in CLASSIFIERS:
                m = source_rows.get(name)
                if (not isinstance(m, dict)
                        or any(type(m.get(k)) is not int or m[k] < 0 for k in FIELDS)
                        or sum(m[k] for k in FIELDS) != n):
                    raise ValueError("INVALID_ORIGINAL_CONFUSION_DENOMINATOR")
                row[asset][name] = {k: m[k] for k in FIELDS}
                for k in FIELDS:
                    totals[asset][name][k] += m[k]
        per_era.append(row)
    out = {}
    for asset in ASSETS:
        baseline = totals[asset]["price_baseline"]
        challenger = totals[asset]["price_candidate"]
        if sum(baseline.values()) != 418 or sum(challenger.values()) != 418:
            raise ValueError("HRE_FIXED_SOURCE_AGGREGATE_DRIFT")
        delta_fp = challenger["fp"] - baseline["fp"]
        delta_fn = challenger["fn"] - baseline["fn"]
        if delta_fp <= 0 or delta_fn >= 0:
            raise ValueError("HRE_ORIGINAL_TRADEOFF_DISAPPEARED")
        out[asset] = {
            "baseline": baseline,
            "challenger": challenger,
            "overlapping_daily_cutoff_count": sum(episode["utc_daily_cutoffs_per_asset"] for episode in episodes),
            "extra_false_alarms": delta_fp,
            "fewer_missed_outcome_windows": -delta_fn,
            "delta_equal_unit_classification_loss": delta_fp + delta_fn,
            "miss_to_false_alarm_cost_ratio_to_break_even": round(delta_fp / -delta_fn, 6),
            "candidate_minus_baseline_loss_at_miss_cost_1": delta_fp + delta_fn,
            "candidate_minus_baseline_loss_at_miss_cost_5": delta_fp + 5 * delta_fn,
        }
    return {
        "contract": CONTRACT,
        "original_owner": "Archive#1553",
        "source_path": SOURCE_PATH,
        "source_blob_sha1": SOURCE_BLOB_SHA1,
        "source_native_run": source.get("native_run_url"),
        "historical_source_class": source["historical_source_class"],
        "unit_loss_is_not_trade_cost": True,
        "overlapping_cutoffs_are_not_independent": True,
        "actual_issued_warning_or_delivery_proven": False,
        "economic_paper_outcome_proven": False,
        "official_threshold_or_model_change_authorized": False,
        "market_event_families_selected_retrospectively": len(ERAS),
        "number_of_independent_market_shocks_certified": None,
        "per_era": per_era,
        "assets": out,
        "scientific_status": "RETROSPECTIVE_DESCRIPTIVE_DIAGNOSTIC_ONLY",
    }


def build(root: Path = ROOT) -> dict:
    return evaluate(read_source(root))


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
