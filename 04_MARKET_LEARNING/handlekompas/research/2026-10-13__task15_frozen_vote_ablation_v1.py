#!/usr/bin/env python3
"""Task 1.5 preregistered frozen-vote shadow ablations. Research-only.

Uses immutable original *issued* vote lists + later-retrieved spot outcome
sensitivity from the Task 1.5 ledger. No futures, live trades, model tuning,
retrospective owner rescoring or auto-selection. All known 2026 windows are
EXPOSED DEVELOPMENT, never an untouched holdout.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CANDIDATES = (
    "PRICE_FAMILY_MAJORITY",
    "PRICE_AND_TAKER_CONFIRM",
    "PRICE_TAKER_ETH_CROSS_CONFIRM",
    "INVERT_INCUMBENT_DIAGNOSTIC",
)
PRICE = ("return_1h", "return_4h", "session_vwap", "momentum_acceleration")
TAKER = ("taker_balance", "taker_change")
ETH_CROSS = ("ethbtc_1h", "breadth_balance")
CUTOFF_UTC = "2026-10-13T00:00:00Z"

def majority(votes, allowed, min_votes, min_agree):
    filtered = {}
    for row in votes:
        name = row.get("family")
        if name not in allowed:
            continue
        if name in filtered:
            return None  # One indicator must never earn duplicate votes.
        filtered[name] = row.get("direction")
    values = [filtered[n] for n in allowed if filtered.get(n) in ("UP", "DOWN")]
    if len(values) < min_votes:
        return None
    up, down = values.count("UP"), values.count("DOWN")
    if max(up, down) < min_agree or up == down:
        return None
    return "UP" if up > down else "DOWN"

def frozen_vote_challengers(target, asset, incumbent):
    votes = target.get("votes")
    if not isinstance(votes, list):
        return dict.fromkeys(CANDIDATES)
    price = majority(votes, PRICE, min_votes=4, min_agree=3)
    flow = majority(votes, TAKER, min_votes=2, min_agree=2)
    price_flow = price if price in ("UP", "DOWN") and flow == price else None
    cross = majority(votes, ETH_CROSS, min_votes=2, min_agree=2) if asset == "ETH" else None
    strict = price_flow if asset == "ETH" and price_flow == cross else None
    inv = {"UP": "DOWN", "DOWN": "UP"}.get(incumbent)
    return {
        "PRICE_FAMILY_MAJORITY": price,
        "PRICE_AND_TAKER_CONFIRM": price_flow,
        "PRICE_TAKER_ETH_CROSS_CONFIRM": strict,
        "INVERT_INCUMBENT_DIAGNOSTIC": inv,
    }

def self_test():
    p = [{"family": name, "direction": "UP"} for name in (*PRICE, *TAKER, *ETH_CROSS)]
    ok = frozen_vote_challengers({"votes": p}, "ETH", "UP")
    assert ok["PRICE_FAMILY_MAJORITY"] == "UP"
    assert ok["PRICE_AND_TAKER_CONFIRM"] == "UP"
    assert ok["PRICE_TAKER_ETH_CROSS_CONFIRM"] == "UP"
    assert ok["INVERT_INCUMBENT_DIAGNOSTIC"] == "DOWN"
    conflict = [{"family": name, "direction": "UP"} for name in PRICE]
    conflict += [{"family": name, "direction": "DOWN"} for name in TAKER]
    contradict = frozen_vote_challengers({"votes": conflict}, "BTC", "UP")
    assert contradict["PRICE_FAMILY_MAJORITY"] == "UP"
    assert contradict["PRICE_AND_TAKER_CONFIRM"] is None
    assert contradict["PRICE_TAKER_ETH_CROSS_CONFIRM"] is None
    assert majority(p + [p[0]], PRICE, 4, 3) is None, "Duplicate vote leakage"
    assert majority([{"family": name, "direction": "UP"} for name in PRICE[:2]], PRICE, 4, 3) is None
    assert frozen_vote_challengers({"votes": []}, "BTC", "DOWN")["PRICE_FAMILY_MAJORITY"] is None
    print("TASK15_ABLATION_SYNTHETIC_CONTROLS_PASS: agreeing, opposing, missing, duplicate, no ETH cross")

def load_rows(root: Path, path: Path):
    rows = []
    cached = {}
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if row["research_admission"] not in (
                "RESEARCH_TAPE_SENSITIVITY_ONLY",
                "CENSORED_ORIGINAL_RESEARCH_TAPE_SENSITIVITY_ONLY",
            ) or row["descriptive_hit"] not in ("True", "False"):
                continue
            name, detail = row["prediction_id"].rsplit("#", 1)
            horizon, asset = detail.split(":")
            if horizon not in ("1H", "4H", "24H") or asset not in ("BTC", "ETH"):
                raise ValueError("unexpected source identity")
            if name not in cached:
                f = root / name
                if not f.is_file():
                    raise ValueError("original freeze file missing")
                content = f.read_bytes()
                if hashlib.sha256(content).hexdigest() != row["prediction_sha256"]:
                    raise ValueError("immutable original freeze hash mismatch")
                cached[name] = json.loads(content)
            frozen = cached[name]
            original = frozen["horizons"][horizon]["targets"][asset]
            if original.get("direction") != row["direction"]:
                raise ValueError("original freeze direction mismatch")
            row["frozen_candidates"] = frozen_vote_challengers(
                original, asset, row["direction"]
            )
            rows.append(row)
    return rows, len(cached)

def diagnostics(rows):
    output = {}
    for h in ("1H", "4H", "24H"):
        for asset in ("BTC", "ETH", "ALL"):
            src = [r for r in rows if r["horizon"] == h
                   and (asset == "ALL" or r["asset"] == asset)]
            cell = {}
            for name in CANDIDATES:
                supported = [r for r in src
                             if r["frozen_candidates"][name] in ("UP", "DOWN")]
                compare = [r for r in supported if r["baseline_hit"] in ("True", "False")]
                cell[name] = {
                    "original_issued_directional_n": len(src),
                    "frozen_challenger_available_n": len(supported),
                    "same_clock_paired_n": len(compare),
                    "challenger_hits_on_pairs": sum(
                        r["frozen_candidates"][name] == r["observed_direction"]
                        for r in compare
                    ),
                    "incumbent_hits_on_pairs": sum(
                        r["descriptive_hit"] == "True" for r in compare
                    ),
                    "prior_momentum_hits_on_pairs": sum(
                        r["baseline_hit"] == "True" for r in compare
                    ),
                    "original_censored_in_pairs": sum(
                        r["original_outcome_status"] == "CENSORED" for r in compare
                    ),
                    "coverage_fraction_of_incumbent": (
                        round(len(supported) / len(src), 6) if src else None
                    ),
                }
            output[f"{h}:{asset}"] = cell
    return output

def run(root: Path, ledger: Path, outfile: Path):
    if not ledger.is_file():
        raise ValueError("Task1.5 freeze ledger unavailable")
    rows, unique_issued_files = load_rows(root, ledger)
    cohorts = {
        "ISSUED_SEP15_TO_OCT12_235959": [
            r for r in rows if r["issue_utc"] < CUTOFF_UTC
        ],
        "ISSUED_SEP15_TO_OCT13_055959": rows,
    }
    answer = {
        "contract": "TASK15_FROZEN_VOTE_ABLATION_DEV_v1",
        "status": "EXPOSED_DEVELOPMENT_ONLY_PIT_AND_PROSPECTIVE_HOLDOUT_BLOCKED",
        "source": {
            "original_forecast_freeze_files_hashed": unique_issued_files,
            "task15_input_ledger_sha256": hashlib.sha256(ledger.read_bytes()).hexdigest(),
            "source_semantics": "FROZEN_ORIGINAL_ISSUED_FEATURE_VOTES + EX_POST_TAPE_ONLY",
        },
        "preregistration": {
            "PRICE_FAMILY_MAJORITY": "Require all 4 original frozen price votes present and >=3 of 4 same direction; de-duplicates the correlated family",
            "PRICE_AND_TAKER_CONFIRM": "PRICE_FAMILY_MAJORITY plus both independent-label taker directions agree",
            "PRICE_TAKER_ETH_CROSS_CONFIRM": "ETH-only, previous confirmation plus both frozen ETH/BTC and breadth agree",
            "INVERT_INCUMBENT_DIAGNOSTIC": "Flip eligible original direction only, NONTRADABLE negative-control benchmark, NEVER optimizer candidate",
        },
        "results": {name: diagnostics(value) for name, value in cohorts.items()},
        "legal_conclusions": [
            "These votes were frozen on originally issued forecasts, but provider PIT/independent main-publication validation is separate.",
            "The same public 28d outcomes informed the research agenda; this is EXPOSED DEVELOPMENT, not a clean unseen holdout.",
            "Model, baseline and controls must be compared at the same exact issued clock and due horizon with matched coverage.",
            "More abstentions can mechanically boost hit rate, so reporting coverage and missed opportunities is mandatory.",
            "Cross-horizon and BTC/ETH observations overlap; raw row N is NOT independent shock-family N.",
            "CENSORED canonical outcomes remain censored; ex-post tape uses sensitivity ONLY and no financial action/PnL.",
            "No empirical winner/threshold/SELL/economic alpha or promotion permission follows from this file.",
        ],
        "permission": {
            "read_only": True,
            "new_schedule": False,
            "automatic_model_weight_changes": False,
            "official_or_shadow_v2_authority": False,
            "portfolio_execution": False,
        },
    }
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(answer, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return answer

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--ledger", default="/tmp/task15-evidence/TASK15_R0_FROZEN_FORECAST_TAPE_CENSOR_LEDGER.csv")
    p.add_argument("--out", default="/tmp/task15-evidence/TASK15_FROZEN_VOTE_ABLATION_DEV_v1.json")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    r = run(Path(args.root), Path(args.ledger), Path(args.out))
    print(json.dumps({
        "status": r["status"],
        "source": r["source"],
        "results": r["results"],
        "permission": r["permission"],
    }, sort_keys=True))

if __name__ == "__main__":
    main()
