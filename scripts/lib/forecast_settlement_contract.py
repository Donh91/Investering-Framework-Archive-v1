from __future__ import annotations

SETTLEMENT_EXACT_TARGET_TIME_V1 = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
SETTLEMENT_EVIDENCE_V1 = "FORECAST_SETTLEMENT_EVIDENCE_v1"
SETTLEMENT_PRICE_OWNER_V1 = "FORECAST_SETTLEMENT_PRICE_OWNER_v1"
SETTLEMENT_OUTCOME_BINDING_V1 = "FORECAST_SETTLEMENT_OUTCOME_BINDING_v1"

SUPPORTED_PRICE_METRICS = frozenset({
    "spot.BTCUSDT.close",
    "spot.ETHUSDT.close",
    "spot.ETHBTC.close",
    "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
    "derivatives.ETH-USDT-SWAP.mark_price.mark_price",
})

# Historical/model-authored prefixes observed in API-agent output. Longest
# prefixes are tested first so nested aliases collapse to one canonical leaf.
_PRICE_PATH_PREFIXES = (
    "api_intelligence_v2.latest_capture.market_metrics.",
    "api_intelligence_v2.latest_capture.",
    "latest_capture.market_metrics.",
    "latest_capture.",
    "market_metrics.",
    "market.",
)


def normalize_metric_path(path: str) -> str:
    value = str(path or "").strip()
    if not value or ";" in value:
        return value
    if value in SUPPORTED_PRICE_METRICS:
        return value
    for prefix in _PRICE_PATH_PREFIXES:
        if value.startswith(prefix):
            candidate = value[len(prefix):]
            if candidate in SUPPORTED_PRICE_METRICS:
                return candidate
    return value


def canonical_price_metric_or_original(path: str) -> str:
    normalized = normalize_metric_path(path)
    return normalized if normalized in SUPPORTED_PRICE_METRICS else str(path or "").strip()


def supports_exact_price_settlement(path: str) -> bool:
    return normalize_metric_path(path) in SUPPORTED_PRICE_METRICS


def settlement_contract_for_metric(path: str) -> str | None:
    return SETTLEMENT_EXACT_TARGET_TIME_V1 if supports_exact_price_settlement(path) else None
