#!/usr/bin/env python3
"""Deterministic research-only EdgeOnchain E2/E3 ledger analysis.

This script analyzes the immutable public Polymarket capture retained under issue #922.
It does not infer hidden model internals, execute trades, or promote a strategy.

Important semantics:
- `curPrice == 1` is used as the selected outcome resolving true.
- `realizedPnl > 0` is account-level realized profitability, not event correctness.
- `avgPrice * totalBought` is an approximate observed cost-basis denominator from the
  Polymarket closed-positions API, not a reconstructed bankroll.
- equal-notional hold ROI uses `y / avgPrice - 1` and is descriptive only.
- cluster bootstrap groups by UTC date of the closed-position timestamp to reduce
  false independence from multiple markets resolving together.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable

CONTRACT = "EDGEONCHAIN_LEDGER_ANALYSIS_v1"
SEED = 922
BOOTSTRAP_DRAWS = 20_000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mean(xs: Iterable[float]) -> float:
    vals = list(xs)
    return sum(vals) / len(vals) if vals else float("nan")


def quantile_sorted(xs: list[float], q: float) -> float:
    if not xs:
        return float("nan")
    if q <= 0:
        return xs[0]
    if q >= 1:
        return xs[-1]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def cluster_bootstrap(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    clusters: dict[str, list[float]] = collections.defaultdict(list)
    for r in rows:
        clusters[r["cluster_date_utc"]].append(float(r[field]))
    keys = sorted(clusters)
    rng = random.Random(SEED)
    draws: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        sampled: list[float] = []
        for _ in keys:
            sampled.extend(clusters[rng.choice(keys)])
        draws.append(mean(sampled))
    draws.sort()
    return {
        "cluster_key": "closed_position_timestamp_utc_date",
        "cluster_count": len(keys),
        "draws": BOOTSTRAP_DRAWS,
        "seed": SEED,
        "mean": mean(float(r[field]) for r in rows),
        "ci95": [quantile_sorted(draws, 0.025), quantile_sorted(draws, 0.975)],
    }


def max_streak(flags: list[bool]) -> int:
    best = 0
    cur = 0
    for flag in flags:
        if flag:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def subset_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0}
    pnl = sum(r["pnl"] for r in rows)
    cost = sum(r["cost_basis_approx"] for r in rows)
    return {
        "n": len(rows),
        "realized_pnl_usdc": pnl,
        "realized_pnl_over_cost_basis_approx": pnl / cost if cost else None,
        "selected_outcome_hit_rate": mean(r["y"] for r in rows),
        "mean_avg_price": mean(r["p"] for r in rows),
        "mean_market_residual_y_minus_p": mean(r["market_residual"] for r in rows),
        "equal_notional_hold_roi_mean": mean(r["equal_notional_hold_roi"] for r in rows),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    evidence = args.evidence_dir
    manifest_path = evidence / "MANIFEST.json"
    activity_path = evidence / "activity.json"
    trades_path = evidence / "trades.json"
    closed_path = evidence / "closed_positions.json"
    identity_path = evidence / "identity.json"

    manifest = json.loads(manifest_path.read_text())
    activity = json.loads(activity_path.read_text())
    trades = json.loads(trades_path.read_text())
    closed = json.loads(closed_path.read_text())
    identity = json.loads(identity_path.read_text())

    expected = manifest["artifacts"]
    local_hashes = {
        "MANIFEST.json": sha256_file(manifest_path),
        "activity.json": sha256_file(activity_path),
        "trades.json": sha256_file(trades_path),
        "closed_positions.json": sha256_file(closed_path),
        "identity.json": sha256_file(identity_path),
    }
    hash_checks = {
        "activity": local_hashes["activity.json"] == expected["activity"]["sha256"],
        "trades": local_hashes["trades.json"] == expected["trades"]["sha256"],
        "closed_positions": local_hashes["closed_positions.json"] == expected["closed_positions"]["sha256"],
        "identity": local_hashes["identity.json"] == expected["identity"]["sha256"],
    }
    if not all(hash_checks.values()):
        raise SystemExit(f"hash mismatch: {hash_checks}")

    proxy_wallet = identity["proxy_wallet"].lower()
    if any(str(x.get("proxyWallet", "")).lower() != proxy_wallet for x in trades + closed):
        raise SystemExit("proxy-wallet mismatch inside ledger")

    trade_conditions = collections.Counter(t["conditionId"] for t in trades)
    closed_conditions = collections.Counter(c["conditionId"] for c in closed)
    if any(v != 1 for v in closed_conditions.values()):
        raise SystemExit("duplicate closed conditionId")

    rows: list[dict[str, Any]] = []
    for c in closed:
        p = float(c["avgPrice"])
        bought = float(c["totalBought"])
        pnl = float(c["realizedPnl"])
        y = 1.0 if float(c["curPrice"]) == 1.0 else 0.0
        timestamp = int(c["timestamp"])
        cluster_date = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).date().isoformat()
        cost = p * bought
        hold_pnl = (y - p) * bought
        hold_roi = (y / p - 1.0) if p > 0 else float("nan")
        eps = 1e-12
        pp = min(max(p, eps), 1.0 - eps)
        brier = (y - p) ** 2
        logloss = -(y * math.log(pp) + (1.0 - y) * math.log(1.0 - pp))
        rows.append(
            {
                "timestamp": timestamp,
                "cluster_date_utc": cluster_date,
                "condition_id": c["conditionId"],
                "p": p,
                "y": y,
                "market_residual": y - p,
                "brier": brier,
                "logloss": logloss,
                "pnl": pnl,
                "cost_basis_approx": cost,
                "hold_pnl": hold_pnl,
                "equal_notional_hold_roi": hold_roi,
                "pnl_positive": pnl > 0,
                "end_date": c.get("endDate"),
            }
        )

    ordered = sorted(rows, key=lambda r: (r["timestamp"], r["condition_id"]))
    n = len(ordered)
    total_pnl = sum(r["pnl"] for r in ordered)
    total_cost = sum(r["cost_basis_approx"] for r in ordered)
    hold_pnl = sum(r["hold_pnl"] for r in ordered)
    correctness = [bool(r["y"]) for r in ordered]
    pnl_wins = [r["pnl_positive"] for r in ordered]

    rolling_39_best = 0
    if n >= 39:
        rolling_39_best = max(sum(1 for x in correctness[i : i + 39] if x) for i in range(n - 38))

    half = n // 2
    first_half = ordered[:half]
    second_half = ordered[half:]

    monthly: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for r in ordered:
        month = dt.datetime.fromtimestamp(r["timestamp"], dt.timezone.utc).strftime("%Y-%m")
        monthly[month].append(r)

    activity_types = collections.Counter(a.get("type", "UNKNOWN") for a in activity)
    deposits = sum(float(a.get("usdcSize") or 0) for a in activity if a.get("type") == "DEPOSIT")
    withdrawals = sum(float(a.get("usdcSize") or 0) for a in activity if a.get("type") == "WITHDRAWAL")

    result = {
        "contract": CONTRACT,
        "authority": {
            "research_only": True,
            "portfolio_execution": False,
            "order_routing": False,
            "automatic_promotion": False,
        },
        "input": {
            "evidence_dir": str(evidence),
            "manifest_contract": manifest.get("contract"),
            "capture_run_id": manifest.get("run_id"),
            "proxy_wallet": proxy_wallet,
            "hash_checks": hash_checks,
            "hashes": local_hashes,
        },
        "ledger_integrity": {
            "activity_rows": len(activity),
            "trade_rows": len(trades),
            "closed_positions": len(closed),
            "unique_trade_conditions": len(trade_conditions),
            "unique_closed_conditions": len(closed_conditions),
            "trade_conditions_not_closed": sorted(set(trade_conditions) - set(closed_conditions)),
            "closed_conditions_without_trade": sorted(set(closed_conditions) - set(trade_conditions)),
            "activity_types": dict(sorted(activity_types.items())),
            "trade_side_counts": dict(sorted(collections.Counter(t["side"] for t in trades).items())),
            "duplicate_exact_trade_rows": len(trades) - len({(t["transactionHash"], t["asset"], t["side"], t["size"], t["price"]) for t in trades}),
        },
        "source_performance_descriptive": {
            "selected_outcome_correct": int(sum(r["y"] for r in ordered)),
            "selected_outcome_hit_rate": mean(r["y"] for r in ordered),
            "mean_avg_price_market_implied_probability": mean(r["p"] for r in ordered),
            "mean_market_residual_y_minus_p": mean(r["market_residual"] for r in ordered),
            "brier_score_market_price": mean(r["brier"] for r in ordered),
            "log_loss_market_price": mean(r["logloss"] for r in ordered),
            "positive_realized_pnl_positions": sum(1 for r in ordered if r["pnl"] > 0),
            "negative_realized_pnl_positions": sum(1 for r in ordered if r["pnl"] < 0),
            "realized_pnl_usdc": total_pnl,
            "cost_basis_approx_usdc": total_cost,
            "realized_pnl_over_cost_basis_approx": total_pnl / total_cost if total_cost else None,
            "hypothetical_hold_to_resolution_pnl_usdc": hold_pnl,
            "hypothetical_hold_weighted_roi": hold_pnl / total_cost if total_cost else None,
            "actual_minus_hold_pnl_usdc": total_pnl - hold_pnl,
            "equal_notional_hold_roi_mean": mean(r["equal_notional_hold_roi"] for r in ordered),
            "cluster_bootstrap_market_residual": cluster_bootstrap(ordered, "market_residual"),
            "cluster_bootstrap_equal_notional_hold_roi": cluster_bootstrap(ordered, "equal_notional_hold_roi"),
            "first_half": subset_metrics(first_half),
            "second_half": subset_metrics(second_half),
            "monthly": {k: subset_metrics(v) for k, v in sorted(monthly.items())},
        },
        "streak_reconciliation": {
            "ordering": "closed_position_timestamp_asc_then_condition_id",
            "max_consecutive_correct_selected_outcomes": max_streak(correctness),
            "max_consecutive_positive_realized_pnl_positions": max_streak(pnl_wins),
            "best_correct_count_in_any_39_consecutive_closed_positions": rolling_39_best,
            "claim_25_consecutive_wins": "NOT_REPRODUCED_UNDER_COMPLETE_WALLET_CLOSED_POSITION_DEFINITION",
            "claim_38_of_39": "NOT_REPRODUCED_UNDER_COMPLETE_WALLET_CLOSED_POSITION_DEFINITION",
            "caveat": "A social claim may refer to a narrower published-pick subset or different ordering. Without a frozen primary claim definition/window it is not admissible to call the claim definitively false.",
        },
        "cash_flow_context": {
            "deposits_usdc_from_activity": deposits,
            "withdrawals_usdc_from_activity": withdrawals,
            "net_deposits_minus_withdrawals_usdc": deposits - withdrawals,
            "interpretation": "Context only. This is not a reconstructed bankroll and cannot validate the third-party follower challenge.",
        },
        "e2_claims": {
            "third_party_1k_to_85k_or_93k": "UNVERIFIED_NOT_RECONCILED_TO_CANONICAL_EDGE_WALLET",
            "25_consecutive_wins": "NOT_REPRODUCED_COMPLETE_WALLET_DEFINITION",
            "38_of_39": "NOT_REPRODUCED_COMPLETE_WALLET_DEFINITION",
            "headline_backtest_roi": "INADMISSIBLE_PENDING_RAW_BACKTEST_AND_CADENCE_RECONCILIATION",
        },
        "e3_adjudication": {
            "status": "NO_VERIFIED_SOURCE_EDGE_FROM_E1_ONLY",
            "why": [
                "The complete closed-position ledger has positive realized PnL, but raw outcome calibration margin versus average market price is small.",
                "Cluster-bootstrap confidence intervals for market residual and equal-notional hold ROI include zero.",
                "Performance is not temporally stable: the early half is positive while the later half is negative.",
                "Observed weighted profitability can be influenced by sizing and execution; maker/taker role is not yet reconstructed.",
                "The contemporaneous eligible opportunity set, true event-time enrichment, and matched controls are not yet frozen.",
            ],
            "not_a_claim_of_no_edge": True,
            "final_source_alpha_gate": "BLOCKED_PENDING_OPPORTUNITY_SET_MICROSTRUCTURE_EVENT_TIME_AND_MATCHED_CONTROLS",
        },
        "next_stage_gate": {
            "e4_copyability": "NOT_ADMISSIBLE_YET",
            "reason": "Do not spend resources on latency-decay until source alpha survives the remaining E3 controls.",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
