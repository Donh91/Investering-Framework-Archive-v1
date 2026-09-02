from __future__ import annotations

SETTLEMENT_EXACT_TARGET_TIME_V1 = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
SETTLEMENT_EVIDENCE_V1 = "FORECAST_SETTLEMENT_EVIDENCE_v1"
SETTLEMENT_PRICE_OWNER_V1 = "FORECAST_SETTLEMENT_PRICE_OWNER_v1"
SETTLEMENT_OUTCOME_BINDING_V1 = "FORECAST_SETTLEMENT_OUTCOME_BINDING_v1"

_MARKET_METRICS_PREFIX = "market_metrics."

SUPPORTED_PRICE_METRICS = frozenset({
    "spot.BTCUSDT.close",
    "spot.ETHUSDT.close",
    "spot.ETHBTC.close",
    "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
    "derivatives.ETH-USDT-SWAP.mark_price.mark_price",
})


def normalize_metric_path(path: str) -> str:
    value = str(path or "")
    return value[len(_MARKET_METRICS_PREFIX):] if value.startswith(_MARKET_METRICS_PREFIX) else value


def supports_exact_price_settlement(path: str) -> bool:
    return normalize_metric_path(path) in SUPPORTED_PRICE_METRICS


def settlement_contract_for_metric(path: str) -> str | None:
    return SETTLEMENT_EXACT_TARGET_TIME_V1 if supports_exact_price_settlement(path) else None
