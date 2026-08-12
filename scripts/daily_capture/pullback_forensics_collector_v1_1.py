#!/usr/bin/env python3
"""Identity-safe correction layer for Pullback Forensics v1.

The legacy OKX liquidation REST response identifies a SWAP family at group/query
level and may omit ``instId`` from individual detail rows. v1 incorrectly
required event-level ``instId`` and could therefore normalize zero otherwise
valid events. This version resolves identity from the explicit detail/group
identity when present, otherwise from the exact queried SWAP family plus the
separately verified exact instrument metadata.

All other v1 authority and storage semantics remain unchanged.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from scripts.daily_capture import pullback_forensics_collector as base


# Re-export stable v1 helpers used by tests and downstream code.
normalized_liquidation_notional_usd = base.normalized_liquidation_notional_usd
merge_events_by_day = base.merge_events_by_day
read_gzip_jsonl = base.read_gzip_jsonl
load_events_since = base.load_events_since
aggregate_liquidations = base.aggregate_liquidations
build_moneyness_skew = base.build_moneyness_skew
canonical_bytes = base.canonical_bytes
sha256_bytes = base.sha256_bytes


def event_id(detail: dict[str, Any], meta: dict[str, Any], resolved_inst_id: str | None = None) -> str:
    resolved = resolved_inst_id or detail.get("_resolved_inst_id") or detail.get("instId")
    if not resolved:
        raise ValueError("missing_resolved_inst_id")
    identity = {
        "instId": resolved,
        "posSide": detail.get("posSide"),
        "sz": str(detail.get("sz")),
        "bkPx": str(detail.get("bkPx")),
        "bkLoss": str(detail.get("bkLoss", "")),
        "ts": str(detail.get("ts")),
        "ctVal": str(meta.get("ctVal")),
        "ctMult": str(meta.get("ctMult")),
        "ctType": str(meta.get("ctType")),
    }
    return base.sha256_bytes(base.canonical_bytes(identity))


def flatten_okx_liquidations(
    doc: dict[str, Any], expected_family: str, expected_inst_id: str
) -> list[dict[str, Any]]:
    """Flatten OKX legacy liquidation groups while preserving identity context.

    Detail rows may lack ``instId``. Since the request is bounded to
    ``instType=SWAP`` and one ``uly`` family, the exact SWAP identity may be
    resolved from the query family plus separately verified exact instrument
    metadata. Any explicit conflicting identity fails closed.
    """
    if str(doc.get("code")) != "0":
        raise ValueError("okx_liquidation_source_error")
    events: list[dict[str, Any]] = []
    for group in doc.get("data", []):
        if not isinstance(group, dict):
            raise ValueError("okx_liquidation_group_not_object")
        family = group.get("uly") or group.get("instFamily")
        if family not in (None, "", expected_family):
            raise ValueError(f"okx_liquidation_family_mismatch:{family}")
        group_inst_id = group.get("instId")
        if group_inst_id not in (None, "", expected_inst_id):
            raise ValueError(f"okx_liquidation_group_instrument_mismatch:{group_inst_id}")
        details = group.get("details") or []
        if not isinstance(details, list):
            raise ValueError("okx_liquidation_details_not_list")
        for raw_detail in details:
            if not isinstance(raw_detail, dict):
                raise ValueError("okx_liquidation_detail_not_object")
            detail_inst_id = raw_detail.get("instId")
            if detail_inst_id not in (None, "", expected_inst_id):
                raise ValueError(f"okx_liquidation_detail_instrument_mismatch:{detail_inst_id}")
            if detail_inst_id == expected_inst_id:
                mode = "DETAIL_EXACT_INST_ID"
            elif group_inst_id == expected_inst_id:
                mode = "GROUP_EXACT_INST_ID"
            else:
                mode = "QUERY_FAMILY_PLUS_EXACT_SWAP_METADATA"
            detail = dict(raw_detail)
            detail["_resolved_inst_id"] = expected_inst_id
            detail["_identity_resolution_mode"] = mode
            detail["_source_group_family"] = family
            detail["_source_group_inst_id"] = group_inst_id
            events.append(detail)
    return events


def normalized_liquidation_event(
    detail: dict[str, Any], meta: dict[str, Any], receipt_hash: str
) -> dict[str, Any]:
    resolved_inst_id = detail.get("_resolved_inst_id") or detail.get("instId")
    if not resolved_inst_id:
        raise ValueError("missing_resolved_inst_id")
    if meta.get("instId") != resolved_inst_id:
        raise ValueError(f"resolved_instrument_metadata_mismatch:{resolved_inst_id}:{meta.get('instId')}")
    ts = int(detail["ts"])
    notional = base.normalized_liquidation_notional_usd(detail, meta)
    raw_detail = {key: value for key, value in detail.items() if not key.startswith("_")}
    return {
        "event_id": event_id(detail, meta, str(resolved_inst_id)),
        "event_timestamp_utc": base.iso_utc_from_ms(ts),
        "event_timestamp_ms": ts,
        "inst_id": resolved_inst_id,
        "identity_resolution_mode": detail.get("_identity_resolution_mode"),
        "source_group_family": detail.get("_source_group_family"),
        "source_group_inst_id": detail.get("_source_group_inst_id"),
        "pos_side": detail.get("posSide"),
        "contracts": float(base.d(detail.get("sz"), "sz")),
        "bankruptcy_price": float(base.d(detail.get("bkPx"), "bkPx")),
        "bankruptcy_loss": detail.get("bkLoss"),
        "ct_type": meta.get("ctType"),
        "ct_val": float(base.d(meta.get("ctVal"), "ctVal")),
        "ct_mult": float(base.contract_multiplier(meta)),
        "ct_val_ccy": meta.get("ctValCcy"),
        "settle_ccy": meta.get("settleCcy"),
        "notional_usd": round(float(notional), 8),
        "notional_method": "OKX_CONTRACT_UNIT_NORMALIZATION_v1",
        "source_payload_sha256": receipt_hash,
        "raw_detail": raw_detail,
    }


def collect_liquidation_asset(asset: str, observed_at) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    family = f"{asset}-USDT"
    inst_id = f"{family}-SWAP"
    meta_doc, meta_receipt = base.fetch_json(
        f"{base.OKX}/api/v5/public/instruments?{base.urllib.parse.urlencode({'instType': 'SWAP', 'instId': inst_id})}"
    )
    meta = base.parse_okx_instrument(meta_doc, inst_id)
    liq_doc, liq_receipt = base.fetch_json(
        f"{base.OKX}/api/v5/public/liquidation-orders?{base.urllib.parse.urlencode({'instType': 'SWAP', 'uly': family, 'state': 'filled', 'limit': '100'})}"
    )
    raw_events = flatten_okx_liquidations(liq_doc, family, inst_id)
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    for detail in raw_events:
        try:
            normalized.append(normalized_liquidation_event(detail, meta, liq_receipt["payload_sha256"]))
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:120]}")
    observed_ms = int(observed_at.timestamp() * 1000)
    modes = Counter(str(row.get("identity_resolution_mode")) for row in normalized)
    status = "PASS" if not errors and len(normalized) == len(raw_events) else ("PARTIAL" if normalized else "UNKNOWN")
    summary = {
        "status": status,
        "source_class": "EXECUTED_LIQUIDATIONS",
        "source_stability": "LEGACY_REST_STILL_LIVE_SOURCE_FRAGILE",
        "backfill": "HARD_ROLLING_WINDOW_NO_RELIABLE_BACKFILL",
        "identity_contract": "OKX_LEGACY_DETAIL_IDENTITY_RESOLUTION_v1_1",
        "instrument_metadata": meta,
        "raw_detail_count": len(raw_events),
        "normalized_exact_instrument_count": len(normalized),
        "identity_resolution_modes": dict(sorted(modes.items())),
        "normalization_errors": errors[:20],
        "current_response_aggregates": base.aggregate_liquidations(normalized, observed_ms),
        "source_receipts": {"instrument": meta_receipt, "liquidations": liq_receipt},
    }
    return summary, normalized


def install_corrections() -> None:
    """Install v1.1 identity semantics into the existing v1 storage/runtime shell."""
    base.event_id = event_id
    base.flatten_okx_liquidations = flatten_okx_liquidations
    base.normalized_liquidation_event = normalized_liquidation_event
    base.collect_liquidation_asset = collect_liquidation_asset


def main() -> None:
    install_corrections()
    base.main()


# Ensure imports through this module also use corrected functions before tests or callers execute.
install_corrections()


if __name__ == "__main__":
    main()
