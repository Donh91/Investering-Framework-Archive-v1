#!/usr/bin/env python3
"""One-shot hash/count/time quality checks of existing private exports.

Exports must be from the pinned private tree, using the exact paths in the receipt.
Never prints or publishes price, sentiment, PnL, wallet or execution payloads.
No hypothesis/performance analysis or new collection. Output is metadata only.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import io
import json
import statistics
from datetime import datetime
from pathlib import Path

HASHES = {
    "parents.csv": "532c858ba3d6f0c765419c6869f881bec278aa792108676a6d70933b08f94441",
    "fills.csv": "eed893a6c9307c12d762c9d5b4126c5242ff8d88d3fef44aaf3589bd19f16144",
    "cfgi-events.jsonl.gz": "66a3c2b7266c7d87b31d9e10dd54e5c93837a421839608d1d9dee726b8822a9a",
    "cfgi-block-1.json": "502434bd6bb60026faa79354df933ed7c441deff6f7bfa126570941d27fb156d",
    "cfgi-block-2.json": "0cdc1f67ba021614aa624a8efe9b65045acc55e7e5304e1ec872f3ae595f72c5",
    "cfgi-block-3.json": "a60852e31eea50ab31f40a2c59b880a92785ad9128ce6d3453cdc8d1ad637cf7",
    "bh-reconciliation.json": "b135c287a1564f95196d9fe410215f4272f3a557619c5a5273a185ddb48daf2f",
}
EXPORT_PATHS = {
    "parents.csv": "raw/MAEVE_PUBLIC_LEDGER_RECOVERY_V1/2026/09/09/MAEVE_TRADES_NORMALIZED.csv",
    "fills.csv": "raw/MAEVE_PUBLIC_LEDGER_RECOVERY_V1/2026/09/09/extracted/MAEVE_FILLS_NORMALIZED.csv",
    "cfgi-events.jsonl.gz": "raw/CFGI_HISTORICAL_1H_EVENT_STAGE_V1/2026/08/21/extracted/cfgi_targeted.jsonl.gz",
    "cfgi-block-1.json": "raw/CFGI_PDLT_HISTORICAL_BOOTSTRAP_V1/2026/08/07/extracted/validated_market_4h.json",
    "cfgi-block-2.json": "raw/CFGI_PDLT_HISTORICAL_BOOTSTRAP_V1/2026/08/07/extracted/validated_btc_eth_4h.json",
    "cfgi-block-3.json": "raw/CFGI_PDLT_HISTORICAL_BOOTSTRAP_V1/2026/08/07/extracted/validated_market_btc_eth_1d.json",
    "bh-reconciliation.json": "receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/2026/09/09/2026-09-09__blockhorizon_combo_reconciliation_receipt_v1.json",
}


def parse(s):
    value = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if value.utcoffset() is None:
        raise ValueError("Naive timestamp is not admitted")
    return value


def number(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def csv_rows(raw):
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if any(None in r for r in rows):
        raise ValueError("Malformed CSV row, stop")
    return rows


def inspect(root):
    # Verify all exact exports before reading any values for the checks.
    inputs = {name: (root / name).read_bytes() for name in HASHES}
    for name, raw in inputs.items():
        if hashlib.sha256(raw).hexdigest() != HASHES[name]:
            raise ValueError(f"HASH_MISMATCH:{name}")
    parents, fills = csv_rows(inputs["parents.csv"]), csv_rows(inputs["fills.csv"])
    parent_map = {r["public_trade_id"]: r for r in parents}
    groups = collections.Counter(r["public_parent_id"] for r in fills)
    closed = [r for r in parents if r["status"] == "CLOSED"]
    parent_counts = {
        "rows": len(parents), "unique_parent_ids": len(parent_map),
        "status_counts": dict(collections.Counter(r["status"] for r in parents)),
        "sum_dca_count": sum(int(r["dca_count"]) for r in parents),
        "sum_n_fills": sum(int(r["n_fills"]) for r in parents),
        "closed_positive_capital_records": sum((number(r["total_buy_usd"]) or 0) > 0 for r in closed),
        "closed_usd_weighted_entry_records": sum(number(r["avg_entry_usd_weighted"]) is not None for r in closed),
        "closed_post_entry_analysis_records": sum((number(r["analysis_lag_minutes"]) or 0) > 0 for r in closed),
        "all_post_entry_analysis_records": sum((number(r["analysis_lag_minutes"]) or 0) > 0 for r in parents),
    }
    fill_counts = {
        "rows": len(fills), "unique_fill_ids": len({r["internal_id"] for r in fills}),
        "parent_groups": len(groups), "first_fills": sum(r["fill_index"] == "0" for r in fills),
        "dca_fills": sum(int(r["fill_index"]) > 0 for r in fills),
        "orphan_parent_group_count": len(set(groups) - set(parent_map)),
        "parent_n_fill_mismatch_count": sum(groups[cid] != int(r["n_fills"]) for cid, r in parent_map.items()),
        "duplicate_parent_fill_index_count": len(fills) - len({(r["public_parent_id"], r["fill_index"]) for r in fills}),
    }
    blocks = []
    for i in range(1, 4):
        q = json.loads(inputs[f"cfgi-block-{i}.json"])
        series = collections.defaultdict(list)
        for r in q["rows"]:
            series[r["symbol"]].append(parse(r["timestamp"]))
        rows = []
        for symbol, times in sorted(series.items()):
            unique = sorted(set(times))
            gaps = [(b-a).total_seconds()/60 for a, b in zip(unique, unique[1:])]
            rows.append({"symbol": symbol, "rows": len(times), "duplicate_timestamps": len(times)-len(unique),
                         "start_utc": min(times).isoformat(), "end_utc": max(times).isoformat(),
                         "median_gap_minutes": round(statistics.median(gaps), 3),
                         "gaps_gt_30m": sum(g > 30 for g in gaps)})
        blocks.append({"block": i, "declared_rows": q["row_count"], "actual_rows": len(q["rows"]), "series": rows})
    events = [json.loads(line) for line in gzip.decompress(inputs["cfgi-events.jsonl.gz"]).splitlines()]
    event_counts = {"rows": len(events), "symbol_counts": dict(collections.Counter(r["symbol"] for r in events)),
                    "duplicate_symbol_timestamp_count": len(events)-len({(r["symbol"], r["timestamp"]) for r in events}),
                    "exact_hour_timestamps": sum(parse(r["timestamp"]).minute == 0 and parse(r["timestamp"]).second == 0 for r in events)}
    bh = json.loads(inputs["bh-reconciliation.json"])
    return {
        "private_source_commit": "36bd008d9c08dcaa4219927cddc9f4324f8b7d8b",
        "classification": "PROVIDER_VALUE_FREE_QUALITY_METADATA_ONLY",
        "exact_exports_sha256": HASHES, "all_exact_export_hashes_match": True,
        "export_bindings": {name: {"repository": "Donh91/secrets", "path": EXPORT_PATHS[name],
                                  "bytes": len(inputs[name]), "sha256": HASHES[name]} for name in HASHES},
        "maeve_parent_counts": parent_counts, "maeve_fill_join_counts": fill_counts,
        "cfgi_bootstrap_blocks": blocks, "cfgi_bootstrap_total_rows": sum(b["actual_rows"] for b in blocks),
        "cfgi_selected_event_stage": event_counts,
        "blockhorizon_receipt_readback": {"archive_summary": bh["archive_summary"], "raw_csv_files_independently_rehashed": 0},
        "hypothesis_trials_created": 0, "economic_performance_replay": False,
        "point_in_time_admission": "NOT_ESTABLISHED_BY_HASH_OR_EVENT_TIME",
        "limitations": ["No full altseason gzip rehash/replay", "BH receipt hash verified, not 55 raw CSV hashes",
                        "Closed MAEVE capital coverage is a subset", "Post-entry analysis fields remain look-ahead suspect",
                        "CFGI retrospective API event times are not original availability times", "No net-return, beta, drawdown or sellability claim"],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("private_export_root", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    value = inspect(args.private_export_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"exact_hashes": len(HASHES), "maeve_parents": value["maeve_parent_counts"]["rows"],
                      "maeve_fills": value["maeve_fill_join_counts"]["rows"], "economic_replay": False}))


if __name__ == "__main__":
    main()
