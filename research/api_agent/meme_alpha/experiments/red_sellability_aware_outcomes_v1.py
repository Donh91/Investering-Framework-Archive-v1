from __future__ import annotations

import argparse
import collections
import concurrent.futures
import json
import zipfile
from pathlib import Path
from typing import Any

from red_earliest_first_buy_reconstruction_v1 import (
    PUMP_IDL_ASOF_COMMIT,
    choose_pairs,
    fetch_tx,
    h,
    member_by_basename,
    rows,
    rpc,
    trade_events,
)

QUALIFICATION_LAUNCH_ORDINAL = 3
HORIZON_SECONDS = 24 * 60 * 60
THRESHOLDS = (2.0, 5.0, 10.0)


def fetch_post_signal_history(url: str, mint: str, signal_slot: int, *, page_size: int, max_pages: int):
    infos: list[dict[str, Any]] = []
    statuses: list[str] = []
    cursor = None
    seen: set[str] = set()
    for _ in range(max_pages):
        opts: dict[str, Any] = {"limit": page_size, "commitment": "finalized"}
        if cursor:
            opts["before"] = cursor
        status, result = rpc(url, "getSignaturesForAddress", [mint, opts])
        statuses.append(status)
        if status != "OK" or result is None:
            return infos, False, f"SIGNATURE_HISTORY_{status}", statuses
        page = [x for x in result if isinstance(x, dict) and x.get("signature")]
        if not page:
            return infos, False, "SIGNAL_BOUNDARY_NOT_REACHED_EMPTY", statuses
        new = 0
        crossed = False
        for item in page:
            sig = str(item["signature"])
            if sig in seen:
                continue
            seen.add(sig)
            new += 1
            slot = int(item.get("slot") or 0)
            if slot > signal_slot:
                infos.append(item)
            else:
                crossed = True
        if crossed:
            return infos, True, "CROSSED_SIGNAL_SLOT_BOUNDARY", statuses
        if new == 0:
            return infos, False, "SIGNATURE_HISTORY_CURSOR_STALLED", statuses
        if len(page) < page_size:
            return infos, False, "HISTORY_ENDED_BEFORE_SIGNAL_SLOT", statuses
        cursor = str(page[-1]["signature"])
    return infos, False, "MAX_HISTORY_PAGES_REACHED", statuses


def exact_events(mint: str, sig: str, tx: dict[str, Any]):
    slot = int(tx.get("slot") or 0)
    out = []
    for event in trade_events(tx):
        if event.get("mint") != mint:
            continue
        token = int(event.get("token_amount") or 0)
        quote = int(event.get("quote_amount") or 0)
        if token <= 0 or quote <= 0:
            continue
        out.append({
            "slot": slot,
            "timestamp": int(event.get("timestamp") or 0),
            "signature_sha256": h(sig),
            "is_buy": bool(event.get("is_buy")),
            "quote_mint_sha256": h(str(event.get("quote_mint") or "")),
            "quote_amount_raw": quote,
            "token_amount_raw": token,
            "price_raw_ratio": quote / token,
            "fee_basis_points": int(event.get("fee_basis_points") or 0),
            "fee_raw": int(event.get("fee") or 0),
            "real_quote_reserves_raw": int(event.get("real_quote_reserves") or 0),
            "real_token_reserves_raw": int(event.get("real_token_reserves") or 0),
        })
    return out


def first_unambiguous_buy(events: list[dict[str, Any]], signal_slot: int):
    by_slot: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for event in events:
        if event["slot"] > signal_slot:
            by_slot[event["slot"]].append(event)
    for slot in sorted(by_slot):
        group = by_slot[slot]
        if len(group) == 1 and group[0]["is_buy"]:
            return group[0]
    return None


def threshold_result(entry: dict[str, Any], later: list[dict[str, Any]], threshold: float):
    ep = float(entry["price_raw_ratio"])
    all_hits = [e for e in later if float(e["price_raw_ratio"]) / ep >= threshold]
    sell_hits = [e for e in all_hits if not e["is_buy"]]
    max_capacity = max((e["token_amount_raw"] / entry["token_amount_raw"] for e in sell_hits), default=0.0)
    if max_capacity >= 1.0:
        cls = "SELLABLE_AT_ENTRY_ANCHOR_SIZE"
    elif max_capacity > 0:
        cls = "SELL_ANCHORED_SMALLER_SIZE"
    elif all_hits:
        cls = "THEORETICAL_MFE_ONLY"
    else:
        cls = "NOT_REACHED"
    best_sell = max(sell_hits, key=lambda e: float(e["price_raw_ratio"]) / ep) if sell_hits else None
    return {
        "threshold_multiple": threshold,
        "classification": cls,
        "theoretical_event_threshold_reached": bool(all_hits),
        "sell_anchor_present": bool(sell_hits),
        "max_sell_capacity_vs_entry_anchor_tokens": max_capacity,
        "entry_anchor_size_sellable": max_capacity >= 1.0,
        "best_sell_multiple": (float(best_sell["price_raw_ratio"]) / ep) if best_sell else None,
        "best_sell_token_amount_raw": best_sell["token_amount_raw"] if best_sell else None,
        "best_sell_quote_amount_raw": best_sell["quote_amount_raw"] if best_sell else None,
        "best_sell_slot": best_sell["slot"] if best_sell else None,
        "best_sell_timestamp": best_sell["timestamp"] if best_sell else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--signal-freeze", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rpc-url", default="https://api.mainnet-beta.solana.com")
    ap.add_argument("--pairs", type=int, default=2)
    ap.add_argument("--history-page-size", type=int, default=250)
    ap.add_argument("--max-history-pages", type=int, default=50)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()

    freeze = json.loads(Path(args.signal_freeze).read_text())
    frozen = {(x["pair_identity_sha256"], int(x["launch_ordinal"]), x["mint_sha256"]): x for x in freeze["launches"]}
    with zipfile.ZipFile(args.zip) as zf:
        intra = list(rows(zf, member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")))
    pairs = choose_pairs(intra, args.pairs)

    targets = []
    qualification_rows = 0
    for pair, pair_rows in pairs:
        pair_hash = h("|".join(pair))
        ordered = sorted(pair_rows, key=lambda row: (int(row.get("detected_at") or 0), h(str(row.get("mint", "")))))
        for ordinal, row in enumerate(ordered, start=1):
            if ordinal < QUALIFICATION_LAUNCH_ORDINAL:
                continue
            mint = str(row.get("mint", ""))
            key = (pair_hash, ordinal, h(mint))
            f = frozen.get(key)
            if ordinal == QUALIFICATION_LAUNCH_ORDINAL:
                qualification_rows += 1
                continue
            targets.append({"pair_hash": pair_hash, "mint": mint, "mint_hash": h(mint), "ordinal": ordinal, "freeze": f})

    history_statuses: collections.Counter[str] = collections.Counter()
    histories = {}
    for target in targets:
        f = target["freeze"]
        if not f or not f.get("prediction_eligible"):
            continue
        infos, complete, reason, statuses = fetch_post_signal_history(
            args.rpc_url,
            target["mint"],
            int(f["signal_slot"]),
            page_size=args.history_page_size,
            max_pages=args.max_history_pages,
        )
        history_statuses.update(statuses)
        histories[(target["pair_hash"], target["ordinal"], target["mint_hash"])] = {"infos": infos, "complete": complete, "reason": reason}

    required_sigs: set[str] = set()
    per_target_sigs = {}
    for target in targets:
        key = (target["pair_hash"], target["ordinal"], target["mint_hash"])
        hist = histories.get(key) or {"infos": [], "complete": False, "reason": "FREEZE_JOIN_FAILED"}
        f = target["freeze"]
        end_ts = int(f["signal_timestamp"]) + HORIZON_SECONDS if f else 0
        sigs = {
            str(info["signature"])
            for info in hist["infos"]
            if info.get("err") is None and int(info.get("blockTime") or 0) <= end_ts
        }
        per_target_sigs[key] = sigs
        required_sigs.update(sigs)

    txs: dict[str, dict[str, Any]] = {}
    tx_statuses: collections.Counter[str] = collections.Counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        for sig, status, tx in executor.map(lambda s: fetch_tx(args.rpc_url, s), sorted(required_sigs)):
            tx_statuses[status] += 1
            if tx is not None:
                txs[sig] = tx

    output_rows = []
    for target in targets:
        key = (target["pair_hash"], target["ordinal"], target["mint_hash"])
        f = target["freeze"]
        hist = histories.get(key) or {"infos": [], "complete": False, "reason": "FREEZE_JOIN_FAILED"}
        sigs = per_target_sigs.get(key, set())
        tx_complete = bool(hist["complete"]) and all(sig in txs for sig in sigs)
        events = []
        if tx_complete:
            for sig in sigs:
                tx = txs[sig]
                if (tx.get("meta") or {}).get("err") is None:
                    events.extend(exact_events(target["mint"], sig, tx))
        events.sort(key=lambda e: (e["slot"], e["timestamp"], e["signature_sha256"], e["is_buy"]))
        signal_slot = int(f["signal_slot"]) if f else 0
        signal_ts = int(f["signal_timestamp"]) if f else 0
        end_ts = signal_ts + HORIZON_SECONDS
        events = [e for e in events if e["slot"] > signal_slot and signal_ts <= e["timestamp"] <= end_ts]
        entry = first_unambiguous_buy(events, signal_slot) if tx_complete else None
        later = [e for e in events if entry and e["slot"] > entry["slot"]]
        quote_mints = sorted({e["quote_mint_sha256"] for e in events})
        quote_consistent = len(quote_mints) <= 1 and bool(quote_mints)
        theoretical_mfe = max((e["price_raw_ratio"] / entry["price_raw_ratio"] for e in later), default=None) if entry else None
        theoretical_mae = min((e["price_raw_ratio"] / entry["price_raw_ratio"] for e in later), default=None) if entry else None
        sell_mfe = max((e["price_raw_ratio"] / entry["price_raw_ratio"] for e in later if not e["is_buy"]), default=None) if entry else None
        curve_exhaustion = any(e["real_token_reserves_raw"] == 0 for e in events)
        thresholds = {str(int(t)): threshold_result(entry, later, t) for t in THRESHOLDS} if entry else {}
        row_ready = bool(f) and bool(f.get("prediction_eligible")) and hist["complete"] and tx_complete and entry is not None and quote_consistent
        output_rows.append({
            "pair_identity_sha256": target["pair_hash"],
            "mint_sha256": target["mint_hash"],
            "launch_ordinal": target["ordinal"],
            "prediction_eligible": bool(f and f.get("prediction_eligible")),
            "signal_timestamp": signal_ts if f else None,
            "signal_slot": signal_slot if f else None,
            "same_slot_entry_forbidden": True,
            "history_complete_to_signal_boundary": hist["complete"],
            "history_completion_reason": hist["reason"],
            "successful_24h_transactions_required": len(sigs),
            "successful_24h_transactions_resolved": sum(1 for sig in sigs if sig in txs),
            "exact_pump_trade_events_24h": len(events),
            "quote_mint_consistent": quote_consistent,
            "quote_mint_sha256": quote_mints[0] if len(quote_mints) == 1 else None,
            "entry_anchor_found": entry is not None,
            "entry_anchor_rule": "first post-signal slot containing exactly one exact-mint Pump TradeEvent and that event is BUY; same signal slot is forbidden",
            "entry_anchor": ({k: entry[k] for k in ["slot", "timestamp", "signature_sha256", "quote_amount_raw", "token_amount_raw", "price_raw_ratio", "fee_basis_points", "fee_raw", "real_quote_reserves_raw", "real_token_reserves_raw"]} if entry else None),
            "theoretical_event_mfe_multiple_24h": theoretical_mfe,
            "theoretical_event_mae_multiple_24h": theoretical_mae,
            "sell_anchored_mfe_multiple_24h": sell_mfe,
            "thresholds_24h": thresholds,
            "pump_curve_real_token_reserves_zero_observed_24h": curve_exhaustion,
            "row_ready": row_ready,
            "raw_identifiers_logged": False,
        })

    expected_prediction = sum(1 for x in freeze["launches"] if x.get("prediction_eligible"))
    ready_rows = sum(1 for r in output_rows if r["row_ready"])
    qualification_leaks = sum(1 for x in freeze["launches"] if int(x["launch_ordinal"]) == 3 and x.get("prediction_eligible"))
    full_tx_resolution = len(required_sigs) == len(txs)
    result = {
        "experiment": "CLEAN_G3_RED_SELLABILITY_AWARE_OUTCOMES_v1",
        "source": "RED-COHORT-2026-v1.1.1",
        "historical_protocol_schema": {"pump_idl_commit": PUMP_IDL_ASOF_COMMIT},
        "scope": {
            "horizon_seconds": HORIZON_SECONDS,
            "venue_evidence": "exact historical Pump TradeEvents only",
            "entry": "strictly after the causal recurring-pair signal slot",
            "sellability": "threshold is sell-anchored; capacity is actual SELL token amount divided by observed entry-anchor token amount",
            "important_limit": "Pump-only event reconstruction does not silently claim post-migration AMM coverage; reserve-zero observations are surfaced for follow-up"
        },
        "counts": {
            "selected_pairs": len(pairs),
            "qualification_launches_seen_not_scored": qualification_rows,
            "expected_prediction_launches": expected_prediction,
            "materialized_prediction_launches": len(output_rows),
            "ready_prediction_launches": ready_rows,
            "unique_24h_transactions_required": len(required_sigs),
            "unique_24h_transactions_resolved": len(txs)
        },
        "rpc": {
            "signature_history_status_counts": dict(sorted(history_statuses.items())),
            "transaction_status_counts": dict(sorted(tx_statuses.items()))
        },
        "invariants": {
            "qualification_launch_prediction_eligible_count": qualification_leaks,
            "launch_3_excluded_from_prediction": qualification_leaks == 0,
            "only_launch_4_plus_scored": all(r["launch_ordinal"] > 3 for r in output_rows),
            "same_slot_entry_forbidden": True,
            "all_required_transactions_resolved": full_tx_resolution,
            "raw_identifiers_logged": False
        },
        "rows": output_rows,
        "verdict": {
            "pilot_outcome_reconstruction": "SUPPORTED" if expected_prediction == len(output_rows) == ready_rows and full_tx_resolution and qualification_leaks == 0 else "PARTIAL_OR_BLOCKED",
            "safe_for_g2_vs_clean_g3_ablation": False,
            "reason_ablation_stays_blocked": "pilot contains only four post-qualification launches; first establish sellability path and migration/venue completeness, then scale the frozen cohort before ablation"
        },
        "authority": {
            "research_only": True,
            "automatic_trading": False,
            "portfolio_execution": False,
            "buy_now_promotion": False,
            "live_threshold_change": False
        }
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
