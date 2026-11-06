"""Shared source-gated Sol MAX model policy, never an arbitrary model fallback.

Owner-authenticated future missions may use one existing Research Lab route from
any conversation. New model availability is read via GET only and the source-
reviewed price table; no GET or policy flag authorizes a paid POST by itself.
"""
from __future__ import annotations
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

POLICY_PATH = Path("research/api_agent/coordination/SOL_MAX_SHARED_MODEL_POLICY_V1.json")
SOL_ID = re.compile(r"gpt-6(?:\.[1-9][0-9]*)?-sol\Z")
MAX_OUTPUT = 128_000
MAX_INPUT_EVIDENCE_BYTES = 180_000
MAX_NEW_REQUEST_USD = 3.0
LEGACY_SOL = "gpt-6.1-sol"


def project_model_available(model: str, api_key: str) -> bool:
    """A strictly read-only provider availability probe for a *verified* model."""
    if not SOL_ID.fullmatch(model) or not api_key:
        return False
    request = urllib.request.Request(
        "https://api.openai.com/v1/models/" + model,
        headers={"Authorization": "Bearer " + api_key},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = json.loads(response.read(10_001))
    except (OSError, ValueError, urllib.error.HTTPError):
        return False
    return isinstance(body, dict) and body.get("id") == model


def validated_models(policy: dict, prices: dict) -> list[dict]:
    """Never trust a model merely because its name appears in a user packet."""
    if (not isinstance(policy, dict)
            or policy.get("contract") != "SOL_MAX_SHARED_MODEL_POLICY_V1"
            or policy.get("max_output_tokens") != MAX_OUTPUT
            or policy.get("public_only") is not True
            or "gpt-6-astra" not in policy.get("forbidden_auto_models", [])
            or policy.get("new_models_not_approved_by_name_alone") is not True):
        raise ValueError("SOL_MAX_MODEL_POLICY_INVALID")
    rows = policy.get("available_verified_sol_models")
    if not isinstance(rows, list) or not rows:
        raise ValueError("SOL_MAX_NO_VERIFIED_SOL_MODELS")
    seen, result = set(), []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("SOL_MAX_MODEL_ROW_INVALID")
        name = row.get("id")
        if (not isinstance(name, str) or not SOL_ID.fullmatch(name)
                or name in seen or row.get("verified_available") is not True
                or not isinstance(row.get("official_model_spec"), str)
                or not row["official_model_spec"].startswith(
                    "https://developers.openai.com/api/docs/models/" + name)
                or type(row.get("max_output_tokens")) is not int
                or not 1 <= row["max_output_tokens"] <= MAX_OUTPUT):
            raise ValueError("SOL_MAX_MODEL_NOT_OFFICIALLY_VERIFIED")
        seen.add(name)
        price = prices.get(name)
        if (not isinstance(price, dict)
                or price.get("input") != row.get("standard_input_usd_per_million")
                or price.get("output") != row.get("standard_output_usd_per_million")):
            raise ValueError("SOL_MAX_MODEL_PRICE_NOT_PINNED")
        result.append(row)
    if LEGACY_SOL not in seen:
        raise ValueError("SOL_MAX_BASELINE_SOL_MISSING")
    return sorted(result, key=lambda x: [int(x["id"].split("-")[1].split(".")[0]),
                                         int(x["id"].split("-")[1].split(".")[1])
                                         if "." in x["id"].split("-")[1] else 0], reverse=True)


def choose_model(policy: dict, prices: dict, *,
                 available: Callable[[str], bool] | None = None) -> dict:
    """Prefer newest approved *and project-available* Sol; 6.1 is safe fallback."""
    rows = validated_models(policy, prices)
    for row in rows:
        if row["id"] == LEGACY_SOL or (available is not None and available(row["id"])):
            return row
    raise ValueError("SOL_MAX_NO_PROJECT_AVAILABLE_SOL")


def quoted_upper_usd(context_bytes: int, output_tokens: int, row: dict) -> float:
    """Conservative short-context quote, never a provider invoice."""
    if (type(context_bytes) is not int or not 0 < context_bytes <= MAX_INPUT_EVIDENCE_BYTES
            or type(output_tokens) is not int
            or not 2048 <= output_tokens <= min(MAX_OUTPUT, row["max_output_tokens"])):
        raise ValueError("SOL_MAX_INPUT_OR_OUTPUT_BOUND_INVALID")
    # Conservative byte-to-token bound for serialized public text, plus
    # 20k-token headroom for instructions and output schema overhead.
    upper_input_tokens = context_bytes + 20_000
    if upper_input_tokens > 272_000:
        raise ValueError("SOL_MAX_LONG_CONTEXT_PRICE_NEEDS_DISTINCT_ADMISSION")
    upper = ((upper_input_tokens * row["standard_input_usd_per_million"])
             + (output_tokens * row["standard_output_usd_per_million"])) / 1_000_000
    if upper > MAX_NEW_REQUEST_USD or upper < 0:
        raise ValueError("SOL_MAX_NEW_REQUEST_PRICE_CAP_EXCEEDED")
    return round(upper, 8)
