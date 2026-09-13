#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CONTRACT = "AUTO_TRADING_FACTOR_TEST_ADJUDICATION_REPLAY_v1"
METHOD_VERSION = "POSITIVE_OOS_SIGN_STABILITY_v2"
METHOD_TRIAL_N = 3
MIN_IC_IMPROVEMENT = 0.02
NORMALIZED = ("ROLLING_PERCENTILE", "ZSCORE", "DISTANCE_FROM_EXTREMA")


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and float(value) > 0.0


def adjudicate(source: dict[str, Any]) -> dict[str, Any]:
    metrics = source.get("metrics") or {}
    raw = metrics.get("RAW") or {}
    raw_combined = (raw.get("oos_combined") or {}).get("spearman_ic")
    raw_btc = ((raw.get("oos_by_symbol") or {}).get("BTC") or {}).get("spearman_ic")
    raw_eth = ((raw.get("oos_by_symbol") or {}).get("ETH") or {}).get("spearman_ic")
    checks: dict[str, Any] = {}
    eligible: list[str] = []

    for name in NORMALIZED:
        row = metrics.get(name) or {}
        combined = row.get("oos_combined") or {}
        by_symbol = row.get("oos_by_symbol") or {}
        btc = by_symbol.get("BTC") or {}
        eth = by_symbol.get("ETH") or {}
        ic = combined.get("spearman_ic")
        btc_ic = btc.get("spearman_ic")
        eth_ic = eth.get("spearman_ic")
        spread = combined.get("top_bottom_quartile_spread_pct")
        btc_spread = btc.get("top_bottom_quartile_spread_pct")
        eth_spread = eth.get("top_bottom_quartile_spread_pct")

        rules = {
            "combined_oos_ic_positive": positive(ic),
            "btc_oos_ic_positive": positive(btc_ic),
            "eth_oos_ic_positive": positive(eth_ic),
            "combined_quartile_spread_positive": positive(spread),
            "btc_quartile_spread_positive": positive(btc_spread),
            "eth_quartile_spread_positive": positive(eth_spread),
            "combined_ic_beats_raw_by_min_margin": (
                isinstance(ic, (int, float))
                and isinstance(raw_combined, (int, float))
                and float(ic) >= float(raw_combined) + MIN_IC_IMPROVEMENT
            ),
            "btc_ic_not_worse_than_raw": (
                isinstance(btc_ic, (int, float))
                and isinstance(raw_btc, (int, float))
                and float(btc_ic) >= float(raw_btc)
            ),
            "eth_ic_not_worse_than_raw": (
                isinstance(eth_ic, (int, float))
                and isinstance(raw_eth, (int, float))
                and float(eth_ic) >= float(raw_eth)
            ),
        }
        passed = all(rules.values())
        checks[name] = {"passed": passed, "rules": rules}
        if passed:
            eligible.append(name)

    status = "METHOD_REPLAY_CONDITION_MET_NO_NEW_EVIDENCE" if eligible else "METHOD_REPLAY_NOT_SUPPORTED"
    return {
        "contract": CONTRACT,
        "method_version": METHOD_VERSION,
        "method_trial_n": METHOD_TRIAL_N,
        "source_experiment_id": source.get("experiment_id"),
        "source_theory_id": source.get("theory_id"),
        "source_trial_n": (source.get("trial_accounting") or {}).get("proposal_trial_n"),
        "source_result_sha256": sha(source),
        "evidence_role": "METHOD_CORRECTION_REPLAY_ONLY_SAME_DATASET_AS_TRIAL_2",
        "why_trial_2_adjudication_was_invalid": "Relative improvement over a negative frozen-orientation OOS IC was incorrectly allowed to count as historical support. Positive sign-stable OOS information is now mandatory.",
        "pre_registered_gate_v2": {
            "min_combined_ic_improvement_over_raw": MIN_IC_IMPROVEMENT,
            "combined_oos_ic_must_be_positive": True,
            "btc_oos_ic_must_be_positive": True,
            "eth_oos_ic_must_be_positive": True,
            "combined_quartile_spread_must_be_positive": True,
            "btc_quartile_spread_must_be_positive": True,
            "eth_quartile_spread_must_be_positive": True,
            "cross_symbol_non_degradation_vs_raw": True,
        },
        "transform_checks": checks,
        "eligible_normalized_transforms": eligible,
        "status": status,
        "historical_support_claim_authorized": False,
        "independent_evidence": False,
        "authority": {
            "research_only": True,
            "portfolio_execution": False,
            "automatic_promotion": False,
            "canonical_effect": False,
        },
        "next_evidence_requirement": "Use this corrected gate on a temporally independent dataset not inspected when the rule was repaired.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-result", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    source = json.loads(args.source_result.read_text())
    result = adjudicate(source)
    encoded = canon(result)
    if args.verify:
        if args.verify.read_bytes() != encoded:
            raise SystemExit("ADJUDICATION_REPLAY_MISMATCH")
    if args.output:
        if args.output.exists():
            raise SystemExit(f"immutable_output_exists:{args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(encoded.decode().rstrip())


if __name__ == "__main__":
    main()
