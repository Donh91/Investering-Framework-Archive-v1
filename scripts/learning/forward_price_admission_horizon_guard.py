"""Read-only evidence diagnosis for existing #1516 BTC priced-horizon research.

This is NOT a source-admission decision, issuer, price model, public projection,
score gate or trading signal. It cannot turn a capture into an eligible forecast.
Real provider prices and source manifests remain in the restricted data plane.
"""
from __future__ import annotations

from typing import Any, Mapping

CONTRACT = "FORWARD_PRICE_ADMISSION_HORIZON_DIAGNOSTIC_v1"
CAPTURE_CONTRACT = "FORWARD_PRICE_SOURCE_CUSTODY_PUBLIC_BINDING_v1"

# Requested forecast endpoints, not target-close probabilities or approved models.
# Only the daily intervals at 1/7/14/21 days have an existing offline builder.
HORIZONS = {
    "12h": ("HOURLY_REQUIRED", "PRICE_MODEL_NOT_IMPLEMENTED"),
    "24h": ("DAILY_OFFLINE_1D", "RESEARCH_ONLY_NOT_ISSUED"),
    "72h": ("HOURLY_REQUIRED", "PRICE_MODEL_NOT_IMPLEMENTED"),
    "7d": ("DAILY_OFFLINE_7D", "RESEARCH_ONLY_NOT_ISSUED"),
    "14d": ("DAILY_OFFLINE_14D", "RESEARCH_ONLY_NOT_ISSUED"),
    "21d": ("DAILY_OFFLINE_21D", "RESEARCH_ONLY_NOT_ISSUED"),
    "30d": ("LONG_HORIZON_SHADOW", "PRICE_MODEL_NOT_IMPLEMENTED"),
    "56d": ("LONG_HORIZON_SHADOW", "PRICE_MODEL_NOT_IMPLEMENTED"),
}


def diagnose_captured_source(binding: Mapping[str, Any], horizon: str) -> dict[str, Any]:
    """Never admit an existing *captured-only* source; explain missing price.

    The result is safe to display as diagnostics, never as market data.
    A future admission flow needs a separate authorized source contract and
    verified independent custody; this function will NEVER implement it.
    """
    if not isinstance(horizon, str) or horizon not in HORIZONS:
        raise ValueError("UNSUPPORTED_PRICED_HORIZON")
    if not isinstance(binding, Mapping):
        raise ValueError("PUBLIC_BINDING_OBJECT_REQUIRED")
    family, model_reason = HORIZONS[horizon]
    identity = {
        "contract": CAPTURE_CONTRACT,
        "asset": "BTC",
        "quote": "USD",
        "provider": "KRAKEN",
        "instrument_id": "XXBTZUSD",
        "private_repository": "Donh91/secrets",
    }
    identity_ok = all(binding.get(k) == v and type(binding.get(k)) is str
                      for k, v in identity.items())
    captured_only = (
        binding.get("status") == "CAPTURED_NOT_ADMITTED"
        and binding.get("source_admitted") is False
        and binding.get("forecast_issued") is False
        and binding.get("historical_replay_allowed") is False
        and binding.get("outcome_scoring_allowed") is False
        and binding.get("original_historical_provider_first_known_verified") is False
        and "collector_commit_sha" in binding
        and binding["collector_commit_sha"] is None
        and binding.get("provider_first_known_proven") is not True
        and binding.get("public_issuance") is not True
    )
    reason_codes = ["SOURCE_NOT_ADMITTED" if identity_ok and captured_only
                    else "SOURCE_BINDING_INVALID_OR_AUTHORITY_CONFLICT"]
    if model_reason not in reason_codes:
        reason_codes.append(model_reason)
    return {
        "contract": CONTRACT,
        "requested_horizon": horizon,
        "required_family": family,
        "status": "UNAVAILABLE",
        "reason_codes": reason_codes,
        "research_only": True,
        "source_admitted": False,
        "forecast_issued": False,
        "eligible_for_canonical_score": False,
        "eligible_for_public_price": False,
        "portfolio_action": False,
        "low_usd": None,
        "high_usd": None,
        "expected_close_usd": None,
        "coverage_probability": None,
    }
