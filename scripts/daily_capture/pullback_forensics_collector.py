#!/usr/bin/env python3
"""Passive Pullback Forensics capture.

Collects only perishable, zero-cost research evidence:
- OKX executed liquidation events with contract-unit-correct USD notional.
- Deribit current option-chain moneyness skew (explicitly NOT 25-delta skew).

SHADOW/RESEARCH ONLY. No framework state or portfolio authority.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

OKX = "https://www.okx.com"
DERIBIT = "https://www.deribit.com/api/v2"
UA = {"User-Agent": "Investering-Pullback-Forensics/1.0", "Accept": "application/json"}
AUTHORITY = {
    "evidence_class": "SHADOW_RESEARCH_ONLY",
    "can_affect_canonical_state": False,
    "can_affect_portfolio_action": False,
    "can_change_market_rules": False,
    "can_create_outcome_rows": False,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def iso_utc_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, dt.UTC).isoformat().replace("+00:00", "Z")


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def fetch_json(url: str, timeout: int = 20) -> tuple[dict[str, Any], dict[str, Any]]:
    started = now_utc()
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        status = response.status
    value = json.loads(raw)
    receipt = {
        "url": url,
        "http_status": status,
        "retrieved_at_utc": started.isoformat().replace("+00:00", "Z"),
        "payload_sha256": sha256_bytes(raw),
        "payload_bytes": len(raw),
    }
    return value, receipt


def d(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"invalid_numeric_{field}") from exc


def contract_multiplier(meta: dict[str, Any]) -> Decimal:
    raw = meta.get("ctMult")
    if raw in (None, ""):
        raise ValueError("missing_ctMult")
    return d(raw, "ctMult")


def normalized_liquidation_notional_usd(detail: dict[str, Any], meta: dict[str, Any]) -> Decimal:
    """Normalize an OKX liquidation size to USD using documented contract value.

    For the exact BTC-USDT-SWAP / ETH-USDT-SWAP pilot instruments, OKX reports
    ``sz`` in contracts and ``ctVal`` as the face value of one contract. The
    current instruments also report ``ctMult=1``. Fail closed if that multiplier
    changes rather than silently extending the unit semantics.

    Pilot notional rule:
      linear  = sz contracts * ctVal base-ccy/contract * bankruptcy price
      inverse = sz contracts * ctVal quote-ccy/contract
    """
    size = d(detail.get("sz"), "sz")
    ct_val = d(meta.get("ctVal"), "ctVal")
    mult = contract_multiplier(meta)
    ct_type = str(meta.get("ctType") or "").lower()
    if size < 0 or ct_val <= 0 or mult <= 0:
        raise ValueError("invalid_contract_units")
    if mult != Decimal("1"):
        raise ValueError("unsupported_ctMult_requires_semantic_review")
    if ct_type == "linear":
        price = d(detail.get("bkPx"), "bkPx")
        if price <= 0:
            raise ValueError("invalid_bankruptcy_price")
        return size * ct_val * price
    if ct_type == "inverse":
        return size * ct_val
    raise ValueError(f"unsupported_ctType:{ct_type or 'missing'}")


def event_id(detail: dict[str, Any], meta: dict[str, Any]) -> str:
    identity = {
        "instId": detail.get("instId"),
        "posSide": detail.get("posSide"),
        "sz": str(detail.get("sz")),
        "bkPx": str(detail.get("bkPx")),
        "bkLoss": str(detail.get("bkLoss", "")),
        "ts": str(detail.get("ts")),
        "ctVal": str(meta.get("ctVal")),
        "ctMult": str(meta.get("ctMult")),
        "ctType": str(meta.get("ctType")),
    }
    return sha256_bytes(canonical_bytes(identity))


def normalized_liquidation_event(detail: dict[str, Any], meta: dict[str, Any], receipt_hash: str) -> dict[str, Any]:
    ts = int(detail["ts"])
    notional = normalized_liquidation_notional_usd(detail, meta)
    return {
        "event_id": event_id(detail, meta),
        "event_timestamp_utc": iso_utc_from_ms(ts),
        "event_timestamp_ms": ts,
        "inst_id": detail.get("instId"),
        "pos_side": detail.get("posSide"),
        "contracts": float(d(detail.get("sz"), "sz")),
        "bankruptcy_price": float(d(detail.get("bkPx"), "bkPx")),
        "bankruptcy_loss": detail.get("bkLoss"),
        "ct_type": meta.get("ctType"),
        "ct_val": float(d(meta.get("ctVal"), "ctVal")),
        "ct_mult": float(contract_multiplier(meta)),
        "ct_val_ccy": meta.get("ctValCcy"),
        "settle_ccy": meta.get("settleCcy"),
        "notional_usd": round(float(notional), 8),
        "notional_method": "OKX_CONTRACT_UNIT_NORMALIZATION_v1",
        "source_payload_sha256": receipt_hash,
        "raw_detail": detail,
    }


def parse_okx_instrument(doc: dict[str, Any], inst_id: str) -> dict[str, Any]:
    if str(doc.get("code")) != "0":
        raise ValueError("okx_instrument_source_error")
    rows = [row for row in doc.get("data", []) if row.get("instId") == inst_id]
    if len(rows) != 1:
        raise ValueError(f"okx_instrument_identity_mismatch:{inst_id}:{len(rows)}")
    row = rows[0]
    for field in ("ctType", "ctVal", "ctMult", "ctValCcy", "settleCcy"):
        if row.get(field) in (None, ""):
            raise ValueError(f"okx_instrument_missing_{field}")
    return {
        key: row.get(key)
        for key in ("instId", "instFamily", "uly", "ctType", "ctVal", "ctMult", "ctValCcy", "settleCcy", "state")
    }


def flatten_okx_liquidations(doc: dict[str, Any], expected_family: str) -> list[dict[str, Any]]:
    if str(doc.get("code")) != "0":
        raise ValueError("okx_liquidation_source_error")
    events: list[dict[str, Any]] = []
    for group in doc.get("data", []):
        family = group.get("uly") or group.get("instFamily")
        if family not in (None, "", expected_family):
            raise ValueError(f"okx_liquidation_family_mismatch:{family}")
        details = group.get("details") or []
        if not isinstance(details, list):
            raise ValueError("okx_liquidation_details_not_list")
        events.extend(details)
    return events


def write_deterministic_gzip_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = b"".join(canonical_bytes(row) + b"\n" for row in rows)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(body)


def read_gzip_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def merge_events_by_day(root: Path, events: list[dict[str, Any]]) -> dict[str, int]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in events:
        day = str(row["event_timestamp_utc"])[:10]
        groups.setdefault(day, []).append(row)
    added_total = 0
    for day, new_rows in groups.items():
        y, m, d_ = day.split("-")
        path = root / "liquidations" / y / m / f"{d_}.jsonl.gz"
        existing = read_gzip_jsonl(path)
        merged = {row["event_id"]: row for row in existing}
        before = len(merged)
        for row in new_rows:
            merged[row["event_id"]] = row
        rows = sorted(merged.values(), key=lambda row: (row["event_timestamp_ms"], row["event_id"]))
        write_deterministic_gzip_jsonl(path, rows)
        added_total += len(merged) - before
    return {"observed_events": len(events), "new_unique_events": added_total, "days_touched": len(groups)}


def load_events_since(root: Path, observed_at: dt.datetime, hours: int = 24) -> list[dict[str, Any]]:
    """Load deduplicated persisted liquidation events from the trailing window."""
    cutoff_ms = int((observed_at - dt.timedelta(hours=hours)).timestamp() * 1000)
    end_ms = int(observed_at.timestamp() * 1000)
    first_day = (observed_at - dt.timedelta(hours=hours)).date()
    last_day = observed_at.date()
    cursor = first_day
    merged: dict[str, dict[str, Any]] = {}
    while cursor <= last_day:
        path = root / "liquidations" / f"{cursor:%Y}" / f"{cursor:%m}" / f"{cursor:%d}.jsonl.gz"
        for row in read_gzip_jsonl(path):
            ts = int(row.get("event_timestamp_ms", -1))
            if cutoff_ms <= ts <= end_ms:
                merged[str(row["event_id"])] = row
        cursor += dt.timedelta(days=1)
    return sorted(merged.values(), key=lambda row: (int(row["event_timestamp_ms"]), str(row["event_id"])))


def aggregate_liquidations(events: list[dict[str, Any]], observed_at_ms: int) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for hours in (1, 6, 24):
        cutoff = observed_at_ms - hours * 3_600_000
        sub = [row for row in events if int(row["event_timestamp_ms"]) >= cutoff]
        result[f"long_liq_usd_{hours}h"] = round(
            sum(float(row["notional_usd"]) for row in sub if row["pos_side"] == "long"), 2
        )
        result[f"short_liq_usd_{hours}h"] = round(
            sum(float(row["notional_usd"]) for row in sub if row["pos_side"] == "short"), 2
        )
        result[f"event_count_{hours}h"] = len(sub)
    six_total = result["long_liq_usd_6h"] + result["short_liq_usd_6h"]
    one_total = result["long_liq_usd_1h"] + result["short_liq_usd_1h"]
    result["liq_acceleration_1h_vs_6h"] = round(one_total / (six_total / 6), 4) if six_total > 0 else None
    result["source_completeness"] = "UNVERIFIED_LEGACY_REST_WINDOW"
    result["page_truncated"] = "UNKNOWN"
    result["aggregates_are_lower_bound"] = True
    return result


def collect_liquidation_asset(asset: str, observed_at: dt.datetime) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    family = f"{asset}-USDT"
    inst_id = f"{family}-SWAP"
    meta_doc, meta_receipt = fetch_json(
        f"{OKX}/api/v5/public/instruments?{urllib.parse.urlencode({'instType': 'SWAP', 'instId': inst_id})}"
    )
    meta = parse_okx_instrument(meta_doc, inst_id)
    liq_doc, liq_receipt = fetch_json(
        f"{OKX}/api/v5/public/liquidation-orders?{urllib.parse.urlencode({'instType': 'SWAP', 'uly': family, 'state': 'filled', 'limit': '100'})}"
    )
    raw_events = flatten_okx_liquidations(liq_doc, family)
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    for detail in raw_events:
        try:
            if detail.get("instId") != inst_id:
                continue
            normalized.append(normalized_liquidation_event(detail, meta, liq_receipt["payload_sha256"]))
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:120]}")
    observed_ms = int(observed_at.timestamp() * 1000)
    summary = {
        "status": "PASS" if normalized and not errors else ("PARTIAL" if normalized else "UNKNOWN"),
        "source_class": "EXECUTED_LIQUIDATIONS",
        "source_stability": "LEGACY_REST_STILL_LIVE_SOURCE_FRAGILE",
        "backfill": "HARD_ROLLING_WINDOW_NO_RELIABLE_BACKFILL",
        "instrument_metadata": meta,
        "raw_detail_count": len(raw_events),
        "normalized_exact_instrument_count": len(normalized),
        "normalization_errors": errors[:20],
        "current_response_aggregates": aggregate_liquidations(normalized, observed_ms),
        "source_receipts": {"instrument": meta_receipt, "liquidations": liq_receipt},
    }
    return summary, normalized


def parse_deribit_instruments(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = doc.get("result")
    if not isinstance(rows, list):
        raise ValueError("deribit_instruments_schema")
    return {
        row["instrument_name"]: row
        for row in rows
        if row.get("kind") == "option" and row.get("instrument_name") and row.get("expiration_timestamp")
    }


def build_moneyness_skew(
    summary_doc: dict[str, Any], instrument_doc: dict[str, Any], observed_at: dt.datetime
) -> dict[str, Any]:
    summaries = summary_doc.get("result")
    if not isinstance(summaries, list):
        raise ValueError("deribit_summary_schema")
    instruments = parse_deribit_instruments(instrument_doc)
    buckets: dict[int, list[dict[str, Any]]] = {}
    for row in summaries:
        name = row.get("instrument_name")
        inst = instruments.get(name)
        if not inst:
            continue
        iv = row.get("mark_iv")
        underlying = row.get("underlying_price")
        strike = inst.get("strike")
        opt = inst.get("option_type")
        expiry = inst.get("expiration_timestamp")
        if iv is None or not underlying or strike is None or opt not in ("call", "put"):
            continue
        moneyness = float(strike) / float(underlying)
        buckets.setdefault(int(expiry), []).append(
            {
                "instrument_name": name,
                "moneyness": moneyness,
                "mark_iv": float(iv),
                "option_type": opt,
                "open_interest": row.get("open_interest"),
                "underlying_price": float(underlying),
            }
        )

    def nearest(rows: list[dict[str, Any]], target: float, option_type: str) -> dict[str, Any] | None:
        candidates = [row for row in rows if row["option_type"] == option_type]
        return min(candidates, key=lambda row: abs(row["moneyness"] - target)) if candidates else None

    now_ms = int(observed_at.timestamp() * 1000)
    output = []
    for expiry in sorted(buckets):
        dte = (expiry - now_ms) / 86_400_000
        if dte < 1 or dte > 60:
            continue
        put = nearest(buckets[expiry], 0.90, "put")
        call = nearest(buckets[expiry], 1.10, "call")
        atm_call = nearest(buckets[expiry], 1.00, "call")
        if not put or not call:
            continue
        output.append(
            {
                "expiration_timestamp_utc": iso_utc_from_ms(expiry),
                "days_to_expiry": round(dte, 4),
                "put_90m_instrument": put["instrument_name"],
                "put_90m_actual_moneyness": round(put["moneyness"], 6),
                "put_90m_mark_iv": put["mark_iv"],
                "call_110m_instrument": call["instrument_name"],
                "call_110m_actual_moneyness": round(call["moneyness"], 6),
                "call_110m_mark_iv": call["mark_iv"],
                "atm_call_mark_iv": None if not atm_call else atm_call["mark_iv"],
                "moneyness_skew_points": round(put["mark_iv"] - call["mark_iv"], 6),
            }
        )
    return {
        "status": "PASS" if output else "PARTIAL",
        "source_class": "EXCHANGE_NATIVE_OPTION_CHAIN",
        "method": "MONEYNESS_BUCKET_SKEW_NOT_25_DELTA",
        "method_warning": "This is NOT 25-delta skew and must never be labelled as 25-delta skew.",
        "backfill": "CURRENT_CHAIN_ONLY_NO_EQUIVALENT_HISTORICAL_SNAPSHOT",
        "expiries_1_to_60d": output,
    }


def collect_skew_asset(asset: str, observed_at: dt.datetime) -> dict[str, Any]:
    summary_doc, summary_receipt = fetch_json(
        f"{DERIBIT}/public/get_book_summary_by_currency?{urllib.parse.urlencode({'currency': asset, 'kind': 'option'})}"
    )
    instrument_doc, instrument_receipt = fetch_json(
        f"{DERIBIT}/public/get_instruments?{urllib.parse.urlencode({'currency': asset, 'kind': 'option', 'expired': 'false'})}"
    )
    result = build_moneyness_skew(summary_doc, instrument_doc, observed_at)
    result["source_receipts"] = {"summary": summary_receipt, "instruments": instrument_receipt}
    return result


def write_metadata_snapshot(root: Path, asset: str, summary: dict[str, Any], run_id: str, observed_at: dt.datetime) -> None:
    y, m, d_ = observed_at.strftime("%Y %m %d").split()
    path = root / "instrument_metadata" / y / m / f"{d_}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(path.read_text()) if path.exists() else {"contract": "PFR_INSTRUMENT_METADATA_DAILY_v1", "snapshots": {}}
    meta = summary.get("instrument_metadata")
    if meta:
        data["snapshots"][asset] = {
            "run_id": run_id,
            "observed_at_utc": observed_at.isoformat().replace("+00:00", "Z"),
            **meta,
        }
    path.write_bytes(canonical_bytes(data) + b"\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    observed_at = now_utc()
    args.output_root.mkdir(parents=True, exist_ok=True)
    output: dict[str, Any] = {
        "contract": "PULLBACK_FORENSICS_PASSIVE_CAPTURE_v1",
        "run_id": args.run_id,
        "observed_at_utc": observed_at.isoformat().replace("+00:00", "Z"),
        "authority": AUTHORITY,
        "topology_class": "PASSIVE_EVIDENCE_CAPTURE",
        "counts_against_experiment_execution_slot": False,
        "lane1_liquidations": {},
        "lane2b_moneyness_skew": {},
        "lane3_orderbook": {"status": "DEFERRED_ARCHITECTURE_CADENCE_MISMATCH"},
        "lane2a_dvol": {"status": "DEFERRED_FULLY_BACKFILLABLE"},
        "lane4_catalyst": {"status": "EXTERNAL_PROSPECTIVE_TAGGING_PROTOCOL", "automatic_classification": False},
    }
    all_events: list[dict[str, Any]] = []
    errors: list[str] = []

    for asset in ("BTC", "ETH"):
        try:
            summary, events = collect_liquidation_asset(asset, observed_at)
            output["lane1_liquidations"][asset] = summary
            all_events.extend(events)
            write_metadata_snapshot(args.output_root, asset, summary, args.run_id, observed_at)
        except Exception as exc:
            output["lane1_liquidations"][asset] = {
                "status": "UNKNOWN",
                "error": f"{type(exc).__name__}:{str(exc)[:200]}",
            }
            errors.append(f"L1_{asset}:{type(exc).__name__}:{str(exc)[:200]}")

    output["liquidation_event_persistence"] = merge_events_by_day(args.output_root, all_events)
    persisted_24h = load_events_since(args.output_root, observed_at, 24)
    for asset in ("BTC", "ETH"):
        lane = output["lane1_liquidations"].get(asset)
        if not isinstance(lane, dict) or lane.get("status") == "UNKNOWN":
            continue
        asset_events = [row for row in persisted_24h if row.get("inst_id") == f"{asset}-USDT-SWAP"]
        lane["persisted_rolling_aggregates"] = aggregate_liquidations(
            asset_events, int(observed_at.timestamp() * 1000)
        )
        lane["persisted_rolling_aggregates"]["basis"] = "DEDUPED_PERSISTED_EVENTS_FROM_ALL_PILOT_CAPTURES"
        lane["persisted_rolling_aggregates"]["captured_event_count_24h"] = len(asset_events)

    for asset in ("BTC", "ETH"):
        try:
            output["lane2b_moneyness_skew"][asset] = collect_skew_asset(asset, observed_at)
        except Exception as exc:
            output["lane2b_moneyness_skew"][asset] = {
                "status": "UNKNOWN",
                "error": f"{type(exc).__name__}:{str(exc)[:200]}",
            }
            errors.append(f"L2B_{asset}:{type(exc).__name__}:{str(exc)[:200]}")

    output["errors"] = errors
    output["status"] = "PASS" if not errors else ("PARTIAL" if all_events else "UNKNOWN")
    payload_hash = sha256_bytes(canonical_bytes(output))
    output["payload_sha256"] = payload_hash

    y, m, d_ = observed_at.strftime("%Y %m %d").split()
    run_dir = args.output_root / "runs" / y / m / d_ / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "PULLBACK_FORENSICS.json").write_bytes(canonical_bytes(output) + b"\n")
    (args.output_root / "LATEST.json").write_bytes(canonical_bytes(output) + b"\n")
    print(
        json.dumps(
            {
                "status": output["status"],
                "run_id": args.run_id,
                "new_unique_events": output["liquidation_event_persistence"]["new_unique_events"],
                "payload_sha256": payload_hash,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
