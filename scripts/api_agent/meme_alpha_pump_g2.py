from __future__ import annotations

import math
import statistics
from datetime import datetime, timezone
from typing import Any

PUMP_PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
PUMP_AMM_PROGRAM_ID = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
PUMP_PUBLIC_DOCS_IDL_COMMIT = "81091419e4457566469d4e2a27f64ed84d42419c"
SUPPORTED_WINDOW_SECONDS = {60, 300, 900, 1800}
CAPTURE_STATES = {"COMPLETE", "DEGRADED"}


def _utc_from_epoch(seconds: int) -> str:
    return datetime.fromtimestamp(int(seconds), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _require(event: dict[str, Any], keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if event.get(key) in {None, ""}]
    if missing:
        raise ValueError("PUMP_EVENT_MISSING:" + ",".join(sorted(missing)))


def _nonnegative_int(value: Any, field: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"PUMP_EVENT_INVALID_INTEGER:{field}") from exc
    if parsed < 0:
        raise ValueError(f"PUMP_EVENT_NEGATIVE_INTEGER:{field}")
    return parsed


def _source_identity(signature: str, event_index: int) -> str:
    if not signature:
        raise ValueError("PUMP_EVENT_MISSING:signature")
    if int(event_index) < 0:
        raise ValueError("PUMP_EVENT_INVALID:event_index")
    return f"solana:{signature}:anchor_event:{int(event_index)}"


def normalize_pump_create_event(
    event: dict[str, Any],
    *,
    signature: str,
    slot: int,
    event_index: int,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Normalize a decoded Pump createEvent from the pinned official IDL."""

    _require(
        event,
        (
            "mint",
            "bondingCurve",
            "user",
            "creator",
            "timestamp",
            "virtualTokenReserves",
            "virtualSolReserves",
            "realTokenReserves",
            "tokenTotalSupply",
            "tokenProgram",
            "quoteMint",
        ),
    )
    timestamp = _nonnegative_int(event["timestamp"], "timestamp")
    return {
        "contract": "MEME_ALPHA_PUMP_CREATE_EVENT_v1",
        "program_id": PUMP_PROGRAM_ID,
        "idl_commit": PUMP_PUBLIC_DOCS_IDL_COMMIT,
        "source_record_or_event_identity": _source_identity(signature, event_index),
        "signature": signature,
        "slot": _nonnegative_int(slot, "slot"),
        "source_observed_at_utc": str(observed_at_utc),
        "event_timestamp": timestamp,
        "event_timestamp_utc": _utc_from_epoch(timestamp),
        "mint": str(event["mint"]),
        "bonding_curve": str(event["bondingCurve"]),
        "user": str(event["user"]),
        "creator": str(event["creator"]),
        "quote_mint": str(event["quoteMint"]),
        "token_program": str(event["tokenProgram"]),
        "virtual_token_reserves_raw": _nonnegative_int(event["virtualTokenReserves"], "virtualTokenReserves"),
        "virtual_quote_reserves_raw": _nonnegative_int(event["virtualSolReserves"], "virtualSolReserves"),
        "real_token_reserves_raw": _nonnegative_int(event["realTokenReserves"], "realTokenReserves"),
        "token_total_supply_raw": _nonnegative_int(event["tokenTotalSupply"], "tokenTotalSupply"),
        "mayhem_mode": bool(event.get("isMayhemMode", False)),
        "cashback_enabled": bool(event.get("isCashbackEnabled", False)),
        "mutability_class": "IMMUTABLE_EVENT",
    }


def normalize_pump_trade_event(
    event: dict[str, Any],
    *,
    signature: str,
    slot: int,
    event_index: int,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Normalize a decoded Pump tradeEvent from the pinned official IDL.

    Quote amounts are kept in raw quote-asset units.  This layer deliberately
    does not assume SOL, quote decimals, USD conversion or independent entities.
    """

    _require(
        event,
        (
            "mint",
            "tokenAmount",
            "isBuy",
            "user",
            "timestamp",
            "virtualTokenReserves",
            "realTokenReserves",
            "creator",
            "quoteMint",
            "quoteAmount",
            "virtualQuoteReserves",
            "realQuoteReserves",
        ),
    )
    timestamp = _nonnegative_int(event["timestamp"], "timestamp")
    quote_amount = _nonnegative_int(event["quoteAmount"], "quoteAmount")
    token_amount = _nonnegative_int(event["tokenAmount"], "tokenAmount")
    is_buy = bool(event["isBuy"])
    return {
        "contract": "MEME_ALPHA_PUMP_TRADE_EVENT_v1",
        "program_id": PUMP_PROGRAM_ID,
        "idl_commit": PUMP_PUBLIC_DOCS_IDL_COMMIT,
        "source_record_or_event_identity": _source_identity(signature, event_index),
        "signature": signature,
        "slot": _nonnegative_int(slot, "slot"),
        "source_observed_at_utc": str(observed_at_utc),
        "event_timestamp": timestamp,
        "event_timestamp_utc": _utc_from_epoch(timestamp),
        "mint": str(event["mint"]),
        "quote_mint": str(event["quoteMint"]),
        "user": str(event["user"]),
        "creator_at_trade": str(event["creator"]),
        "side": "BUY" if is_buy else "SELL",
        "is_buy": is_buy,
        "quote_amount_raw": quote_amount,
        "signed_trade_quote_amount_raw": quote_amount if is_buy else -quote_amount,
        "token_amount_raw": token_amount,
        "virtual_token_reserves_raw": _nonnegative_int(event["virtualTokenReserves"], "virtualTokenReserves"),
        "real_token_reserves_raw": _nonnegative_int(event["realTokenReserves"], "realTokenReserves"),
        "virtual_quote_reserves_raw": _nonnegative_int(event["virtualQuoteReserves"], "virtualQuoteReserves"),
        "real_quote_reserves_raw": _nonnegative_int(event["realQuoteReserves"], "realQuoteReserves"),
        "fee_raw": _nonnegative_int(event.get("fee", 0), "fee"),
        "creator_fee_raw": _nonnegative_int(event.get("creatorFee", 0), "creatorFee"),
        "cashback_raw": _nonnegative_int(event.get("cashback", 0), "cashback"),
        "buyback_fee_raw": _nonnegative_int(event.get("buybackFee", 0), "buybackFee"),
        "ix_name": str(event.get("ixName", "UNKNOWN")),
        "mayhem_mode": bool(event.get("mayhemMode", False)),
        "mutability_class": "IMMUTABLE_EVENT",
    }


def normalize_pump_complete_event(
    event: dict[str, Any],
    *,
    signature: str,
    slot: int,
    event_index: int,
    observed_at_utc: str,
) -> dict[str, Any]:
    """Normalize the bonding-curve completion event without inferring PnL."""

    _require(event, ("user", "mint", "bondingCurve", "timestamp", "quoteMint"))
    timestamp = _nonnegative_int(event["timestamp"], "timestamp")
    return {
        "contract": "MEME_ALPHA_PUMP_COMPLETE_EVENT_v1",
        "program_id": PUMP_PROGRAM_ID,
        "idl_commit": PUMP_PUBLIC_DOCS_IDL_COMMIT,
        "source_record_or_event_identity": _source_identity(signature, event_index),
        "signature": signature,
        "slot": _nonnegative_int(slot, "slot"),
        "source_observed_at_utc": str(observed_at_utc),
        "event_timestamp": timestamp,
        "event_timestamp_utc": _utc_from_epoch(timestamp),
        "mint": str(event["mint"]),
        "bonding_curve": str(event["bondingCurve"]),
        "quote_mint": str(event["quoteMint"]),
        "user": str(event["user"]),
        "lifecycle_event": "BONDING_CURVE_COMPLETE",
        "profitability_claim": "NONE",
        "mutability_class": "IMMUTABLE_EVENT",
    }


def _raw_price(event: dict[str, Any]) -> float | None:
    token_amount = int(event["token_amount_raw"])
    quote_amount = int(event["quote_amount_raw"])
    if token_amount <= 0 or quote_amount <= 0:
        return None
    return quote_amount / token_amount


def aggregate_pump_g2_window(
    create_event: dict[str, Any],
    trade_events: list[dict[str, Any]],
    *,
    cutoff_seconds: int,
    capture_state: str = "COMPLETE",
) -> dict[str, Any]:
    """Aggregate address-level early Pump microstructure from immutable events.

    The output intentionally calls buyers *addresses*, not independent economic
    entities.  Entity-adjusted breadth belongs to the later entity-resolution
    layer and remains UNKNOWN here.
    """

    if int(cutoff_seconds) not in SUPPORTED_WINDOW_SECONDS:
        raise ValueError("UNSUPPORTED_PUMP_G2_WINDOW")
    if capture_state not in CAPTURE_STATES:
        raise ValueError("INVALID_CAPTURE_STATE")
    if create_event.get("contract") != "MEME_ALPHA_PUMP_CREATE_EVENT_v1":
        raise ValueError("INVALID_PUMP_CREATE_EVENT")

    origin = int(create_event["event_timestamp"])
    cutoff_ts = origin + int(cutoff_seconds)
    mint = str(create_event["mint"])
    quote_mint = str(create_event["quote_mint"])

    by_identity: dict[str, dict[str, Any]] = {}
    for event in trade_events:
        if event.get("contract") != "MEME_ALPHA_PUMP_TRADE_EVENT_v1":
            raise ValueError("INVALID_PUMP_TRADE_EVENT")
        if str(event.get("mint")) != mint:
            raise ValueError("PUMP_G2_MINT_MISMATCH")
        if str(event.get("quote_mint")) != quote_mint:
            raise ValueError("PUMP_G2_QUOTE_MINT_MISMATCH")
        identity = str(event["source_record_or_event_identity"])
        by_identity[identity] = event

    window = [
        event
        for event in by_identity.values()
        if origin <= int(event["event_timestamp"]) <= cutoff_ts
    ]
    window.sort(key=lambda event: (int(event["event_timestamp"]), int(event["slot"]), str(event["source_record_or_event_identity"])))

    buys = [event for event in window if bool(event["is_buy"])]
    sells = [event for event in window if not bool(event["is_buy"])]
    buyers = [str(event["user"]) for event in buys]
    sellers = [str(event["user"]) for event in sells]
    unique_buyers = set(buyers)
    unique_sellers = set(sellers)
    buyer_counts = {buyer: buyers.count(buyer) for buyer in unique_buyers}
    repeat_buyers = sum(1 for count in buyer_counts.values() if count > 1)

    buy_sizes = [int(event["quote_amount_raw"]) for event in buys]
    sell_sizes = [int(event["quote_amount_raw"]) for event in sells]
    gross_buy = sum(buy_sizes)
    gross_sell = sum(sell_sizes)
    net_flow = gross_buy - gross_sell
    buy_mean = statistics.fmean(buy_sizes) if buy_sizes else None
    buy_std = statistics.pstdev(buy_sizes) if len(buy_sizes) >= 2 else 0.0 if buy_sizes else None
    buy_cv = (buy_std / buy_mean) if buy_mean not in {None, 0.0} and buy_std is not None else None

    first_sell_latency = None
    if sells:
        first_sell_latency = int(sells[0]["event_timestamp"]) - origin

    raw_prices = [price for price in (_raw_price(event) for event in window) if price is not None and price > 0]
    raw_price_ratio = None
    log_price_pstdev = None
    if len(raw_prices) >= 2:
        raw_price_ratio = raw_prices[-1] / raw_prices[0]
        log_price_pstdev = statistics.pstdev([math.log(price) for price in raw_prices])

    first_reserve = int(window[0]["real_quote_reserves_raw"]) if window else None
    last_reserve = int(window[-1]["real_quote_reserves_raw"]) if window else None
    reserve_delta = (last_reserve - first_reserve) if first_reserve is not None and last_reserve is not None else None
    creator_addresses = sorted({str(event["creator_at_trade"]) for event in window})
    latest_observed_at = max((str(event["source_observed_at_utc"]) for event in window), default=str(create_event["source_observed_at_utc"]))

    return {
        "contract": "MEME_ALPHA_PUMP_G2_WINDOW_v1",
        "idl_commit": PUMP_PUBLIC_DOCS_IDL_COMMIT,
        "mint": mint,
        "quote_mint": quote_mint,
        "token_origin_utc": str(create_event["event_timestamp_utc"]),
        "cutoff_seconds": int(cutoff_seconds),
        "cutoff_utc": _utc_from_epoch(cutoff_ts),
        "capture_state": capture_state,
        "eligible_for_training": capture_state == "COMPLETE",
        "trade_count": len(window),
        "buy_count": len(buys),
        "sell_count": len(sells),
        "address_level_unique_buyers": len(unique_buyers),
        "address_level_unique_sellers": len(unique_sellers),
        "entity_adjusted_unique_buyers": "UNKNOWN",
        "entity_adjusted_unique_sellers": "UNKNOWN",
        "repeat_buyer_fraction": round(repeat_buyers / len(unique_buyers), 6) if unique_buyers else None,
        "gross_buy_quote_raw": gross_buy,
        "gross_sell_quote_raw": gross_sell,
        "net_trade_quote_flow_raw": net_flow,
        "net_trade_quote_flow_raw_per_second": round(net_flow / int(cutoff_seconds), 6),
        "net_trade_quote_flow_raw_per_address_level_buyer": round(net_flow / len(unique_buyers), 6) if unique_buyers else None,
        "trade_velocity_per_minute": round(len(window) / (int(cutoff_seconds) / 60.0), 6),
        "address_level_buyer_velocity_per_minute": round(len(unique_buyers) / (int(cutoff_seconds) / 60.0), 6),
        "first_sell_seen": bool(sells),
        "first_sell_latency_seconds": first_sell_latency,
        "buy_sell_count_ratio": round(len(buys) / len(sells), 6) if sells else None,
        "buy_sell_quote_ratio": round(gross_buy / gross_sell, 6) if gross_sell else None,
        "buy_quote_mean_raw": round(buy_mean, 6) if buy_mean is not None else None,
        "buy_quote_pstdev_raw": round(buy_std, 6) if buy_std is not None else None,
        "buy_quote_coefficient_of_variation": round(buy_cv, 6) if buy_cv is not None else None,
        "raw_price_ratio_last_to_first": round(raw_price_ratio, 9) if raw_price_ratio is not None else None,
        "log_raw_price_pstdev": round(log_price_pstdev, 9) if log_price_pstdev is not None else None,
        "first_real_quote_reserves_raw": first_reserve,
        "last_real_quote_reserves_raw": last_reserve,
        "real_quote_reserve_delta_raw": reserve_delta,
        "creator_addresses_at_trade": creator_addresses,
        "creator_changed_within_window": len(creator_addresses) > 1,
        "mayhem_mode_seen": any(bool(event.get("mayhem_mode")) for event in window),
        "deduped_event_count": len(window),
        "source_observed_at_utc": latest_observed_at,
        "source_event_identities": [str(event["source_record_or_event_identity"]) for event in window],
        "semantic_warnings": [
            "quote amounts are raw quote-asset units, not USD",
            "address-level buyer breadth is not independent economic-entity breadth",
            "graduation/completion is not a profitability label",
        ],
        "authority": {
            "automatic_trading": False,
            "portfolio_action": False,
            "position_size_output": False,
            "live_alert_change": False,
        },
    }


def pump_g2_shadow_features(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert a Pump G2 window into point-in-time feature envelopes.

    Only source-neutral, directly derived metrics are emitted. Entity-adjusted
    and wallet-quality features are intentionally left to later owners.
    """

    if summary.get("contract") != "MEME_ALPHA_PUMP_G2_WINDOW_v1":
        raise ValueError("INVALID_PUMP_G2_SUMMARY")
    feature_names = (
        "trade_count",
        "buy_count",
        "sell_count",
        "address_level_unique_buyers",
        "address_level_unique_sellers",
        "repeat_buyer_fraction",
        "gross_buy_quote_raw",
        "gross_sell_quote_raw",
        "net_trade_quote_flow_raw",
        "net_trade_quote_flow_raw_per_second",
        "net_trade_quote_flow_raw_per_address_level_buyer",
        "trade_velocity_per_minute",
        "address_level_buyer_velocity_per_minute",
        "first_sell_seen",
        "first_sell_latency_seconds",
        "buy_sell_count_ratio",
        "buy_sell_quote_ratio",
        "buy_quote_coefficient_of_variation",
        "raw_price_ratio_last_to_first",
        "log_raw_price_pstdev",
        "real_quote_reserve_delta_raw",
        "creator_changed_within_window",
        "mayhem_mode_seen",
    )
    event_ids = list(summary.get("source_event_identities", []))
    source_identity = "pump-events:" + (event_ids[0] if event_ids else f"{summary['mint']}:empty-window")
    return [
        {
            "feature_name": name,
            "feature_value_at_cutoff": summary.get(name),
            "feature_effective_at_utc": str(summary["cutoff_utc"]),
            "source_observed_at_utc": str(summary["source_observed_at_utc"]),
            "source_or_schema_version": f"pump-public-docs@{PUMP_PUBLIC_DOCS_IDL_COMMIT}",
            "source_record_or_event_identity": source_identity + f":{name}",
            "mutability_class": "DERIVED_FROM_PINNED_EVENTS",
        }
        for name in feature_names
    ]
