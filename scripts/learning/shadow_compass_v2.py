#!/usr/bin/env python3
"""Forward-only GPT-6.1 Sol shadow reasoner for Compass v2.

This lane is deliberately non-binding. It consumes only hash-bound existing
market owners plus Cycle Navigator structural context, emits a prospective
forecast, and never grants portfolio execution or rewrites Official Compass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

# Support both module import and direct `python scripts/learning/...py` execution in CI/runtime.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.data_ping.native_handlekompas import (
    DEFAULT_CN_POINTER,
    load_auto_state_bundle,
    load_cn_context,
)

AUTO_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
OUTPUT_ROOT = Path("04_MARKET_LEARNING/handlekompas/shadow_v2")
MODEL_DEFAULT = "gpt-6.1-sol"
REASONER_VERSION = "SHADOW_COMPASS_V2_2026-09-30_A"
INPUT_CONTRACT = "SHADOW_COMPASS_V2_INPUT_v1"
MODEL_OUTPUT_CONTRACT = "SHADOW_COMPASS_V2_MODEL_OUTPUT_v1"
FORECAST_CONTRACT = "SHADOW_COMPASS_V2_FORECAST_v1"
POINTER_CONTRACT = "SHADOW_COMPASS_V2_LATEST_POINTER_v1"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    out = float(value)
    return out if math.isfinite(out) else None


def _trim_microstructure(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    symbols = value.get("symbols") if isinstance(value.get("symbols"), Mapping) else {}
    out: dict[str, Any] = {
        "retrieval_timestamp": value.get("retrieval_timestamp"),
        "source": value.get("source"),
        "symbols": {},
    }
    for symbol in ("BTCUSDT", "ETHUSDT"):
        row = symbols.get(symbol)
        if not isinstance(row, Mapping):
            continue
        out["symbols"][symbol] = {
            "midpoint": finite(row.get("midpoint")),
            "vwap": finite(row.get("vwap")),
            "spread_bps": finite(row.get("spread_bps")),
            "depth20_quote_notional_imbalance": finite(row.get("depth20_quote_notional_imbalance")),
            "taker_quote_imbalance": finite(row.get("taker_quote_imbalance")),
            "trade_count": row.get("trade_count"),
        }
    return out


def _trim_macro(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    out: dict[str, Any] = {}
    for key in ("DGS10", "DGS2", "DTWEXBGS", "VIXCLS"):
        row = value.get(key)
        if isinstance(row, Mapping):
            out[key] = {
                "value": finite(row.get("value")),
                "date": row.get("date"),
                "status": row.get("status"),
                "source_timestamp": row.get("source_timestamp"),
            }
    return out or None


def _trim_sentiment(value: Any) -> dict[str, Any] | None:
    cfgi = nested(value, "cfgi")
    if not isinstance(cfgi, Mapping):
        return None
    symbols = cfgi.get("symbols") if isinstance(cfgi.get("symbols"), Mapping) else {}
    out: dict[str, Any] = {"retrieved_at_utc": cfgi.get("retrieved_at_utc"), "symbols": {}}
    for key in ("BTC", "ETH", "MARKET"):
        row = symbols.get(key)
        if isinstance(row, Mapping):
            out["symbols"][key] = {
                "score": finite(row.get("score")),
                "classification": row.get("classification"),
                "timestamp": row.get("timestamp"),
            }
    return out


def _trim_altseason(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    bc = value.get("blockchaincenter_altcoin_season")
    cmc = value.get("coinmarketcap_altcoin_season")
    out: dict[str, Any] = {}
    if isinstance(bc, Mapping):
        horizons = bc.get("horizons") if isinstance(bc.get("horizons"), Mapping) else {}
        out["blockchaincenter"] = {
            "observation_date_utc": bc.get("observation_date_utc"),
            "30d": horizons.get("30"),
            "90d": horizons.get("90"),
            "365d": horizons.get("365"),
        }
    if isinstance(cmc, Mapping):
        out["coinmarketcap"] = {
            "published_score": cmc.get("published_score"),
            "horizon_days": cmc.get("horizon_days"),
            "observation_date_utc": cmc.get("observation_date_utc"),
        }
    return out or None


def build_input(
    auto_state: Mapping[str, Any],
    *,
    auto_pointer: Mapping[str, Any],
    auto_packet_path: Path,
    cn_package: Mapping[str, Any] | None,
    cn_binding: Mapping[str, Any],
    issued_at: datetime,
) -> dict[str, Any]:
    ns = auto_state.get("normalized_state") if isinstance(auto_state.get("normalized_state"), Mapping) else {}
    ns = ns or {}
    derivatives = ns.get("derivatives") if isinstance(ns.get("derivatives"), Mapping) else {}
    derivatives = derivatives or {}
    projection = cn_package.get("decision_projection") if isinstance(cn_package, Mapping) and isinstance(cn_package.get("decision_projection"), Mapping) else None

    input_value = {
        "contract": INPUT_CONTRACT,
        "issued_at_utc": issued_at.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "reasoner_version": REASONER_VERSION,
        "source_bindings": {
            "auto_market_state": {
                "packet_path": auto_packet_path.as_posix(),
                "packet_sha256": auto_state.get("packet_sha256"),
                "packet_generated_at_utc": auto_state.get("packet_generated_at_utc"),
                "source_snapshot_commit_sha": nested(auto_state, "source_snapshot", "exact_commit_sha"),
                "pointer_sha256": sha256(canonical(auto_pointer)),
            },
            "cycle_navigator": {
                "status": cn_binding.get("status"),
                "issue_number": cn_binding.get("issue_number"),
                "iso_week": cn_binding.get("iso_week"),
                "iso_year": cn_binding.get("iso_year"),
                "decision_projection_source": cn_binding.get("decision_projection_source"),
                "machine_package_sha256": nested(cn_binding, "machine_package", "content_sha256"),
            },
        },
        "data_health": {
            "validation_status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
            "blockers": list(auto_state.get("blockers") or []),
            "optional_degraded_lanes": list(auto_state.get("optional_degraded_lanes") or []),
            "source_health": auto_state.get("source_health"),
            "missingness_policy": auto_state.get("missingness_policy"),
        },
        "market": {
            "live_market": ns.get("live_market"),
            "spot_hourly": ns.get("spot_hourly"),
            "microstructure": _trim_microstructure(ns.get("microstructure")),
            "derivatives_hourly": derivatives.get("hourly"),
            "derivatives_live_anchor": derivatives.get("live_anchor"),
            "current_breadth": ns.get("current_breadth"),
            "rich_breadth_aggregate": nested(ns, "breadth", "aggregate"),
            "btc_dominance": ns.get("btc_dominance"),
            "settled_etf": ns.get("settled_etf"),
            "stablecoin_liquidity": ns.get("stablecoin_liquidity"),
            "macro": _trim_macro(ns.get("macro_risk")),
            "sentiment": _trim_sentiment(ns.get("sentiment")),
            "altseason": _trim_altseason(ns.get("altseason_context")),
            "entry_signal_reference": ns.get("entry_signal_reference"),
            "deltas_since_prior_packet": auto_state.get("deltas_since_prior_auto_packet"),
        },
        "structural_prior": {
            "authority": "CYCLE_NAVIGATOR_CONTEXT_NOT_ANSWER_KEY",
            "decision_projection": projection,
            "base_case_this_week": cn_package.get("base_case_this_week") if isinstance(cn_package, Mapping) else None,
            "base_case_2_3_weeks": cn_package.get("base_case_2_3_weeks") if isinstance(cn_package, Mapping) else None,
        },
        "rules": [
            "This is a shadow forecast only and has no portfolio execution authority.",
            "Infer direction from supplied evidence; do not copy the Cycle Navigator direction merely because it is present.",
            "Cycle Navigator is a structural prior, not an answer key.",
            "Preserve conflicts and missingness.",
            "Stabilization is not continuation; absorption is not recovery.",
            "BTC health is not altcoin transmission.",
            "A bullish direction does not grant BUY permission and a bearish direction does not grant SELL permission.",
            "Use NO_EDGE when evidence is insufficient or materially contradictory.",
            "Do not invent prices, ranges, probabilities, thresholds or sources.",
        ],
    }
    input_value["input_sha256"] = sha256(canonical({k: v for k, v in input_value.items() if k != "input_sha256"}))
    return input_value


def model_schema() -> dict[str, Any]:
    row = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "direction", "expected_path", "supporting_evidence", "contradicting_evidence",
            "missing_evidence", "pullback_risk", "transmission_state", "confidence",
            "falsification_conditions",
        ],
        "properties": {
            "direction": {"type": "string", "enum": ["UP", "DOWN", "SIDEWAYS", "MIXED", "NO_EDGE"]},
            "expected_path": {"type": "string"},
            "supporting_evidence": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
            "contradicting_evidence": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
            "missing_evidence": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
            "pullback_risk": {"type": "string", "enum": ["NORMAL", "BUILDING", "ELEVATED", "HIGH", "UNAVAILABLE"]},
            "transmission_state": {"type": "string", "enum": ["NONE", "WEAK", "BUILDING", "CONFIRMED", "DETERIORATING", "UNAVAILABLE"]},
            "confidence": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
            "falsification_conditions": {"type": "array", "minItems": 1, "maxItems": 5, "items": {"type": "string"}},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["contract", "horizons", "cross_horizon_summary", "global_missing_evidence"],
        "properties": {
            "contract": {"type": "string", "const": MODEL_OUTPUT_CONTRACT},
            "horizons": {
                "type": "object",
                "additionalProperties": False,
                "required": ["12h", "72h", "168h"],
                "properties": {"12h": row, "72h": row, "168h": row},
            },
            "cross_horizon_summary": {"type": "string"},
            "global_missing_evidence": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
        },
    }


def _response_text(raw: Mapping[str, Any]) -> str:
    direct = raw.get("output_text")
    if isinstance(direct, str) and direct:
        return direct
    parts: list[str] = []
    for item in raw.get("output", []) if isinstance(raw.get("output"), list) else []:
        if not isinstance(item, Mapping):
            continue
        for block in item.get("content", []) if isinstance(item.get("content"), list) else []:
            if isinstance(block, Mapping) and block.get("type") == "output_text":
                parts.append(str(block.get("text") or ""))
    return "".join(parts)


def call_model(input_value: Mapping[str, Any], *, model: str, max_output_tokens: int = 4500) -> tuple[dict[str, Any], dict[str, Any]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY_missing")
    instructions = (
        "You are the non-binding Shadow Compass v2 market reasoner inside an audited investment framework. "
        "Analyze only the supplied evidence. Produce prospective 12h, 72h and 168h market-direction forecasts. "
        "Separate descriptive direction from action authority. Explicitly represent supporting evidence, counterevidence, "
        "missingness and falsification. Do not manufacture precision. A structural Cycle Navigator prior is context, not an "
        "answer key. Stabilization is not continuation; absorption is not recovery; BTC resilience is not altcoin transmission. "
        "Never give portfolio sizing, BUY/SELL execution, or change framework thresholds/weights. Use NO_EDGE when appropriate."
    )
    payload = {
        "model": model,
        "reasoning": {"effort": "high"},
        "store": False,
        "max_output_tokens": max_output_tokens,
        "instructions": instructions,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": json.dumps(input_value, sort_keys=True)}]}],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "shadow_compass_v2_analysis",
                "strict": True,
                "schema": model_schema(),
            }
        },
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=canonical(payload),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            raw = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"openai_http_{exc.code}:{body[:800]}") from exc
    except (TimeoutError, urllib.error.URLError) as exc:
        raise RuntimeError(f"openai_transport:{type(exc).__name__}") from exc

    if raw.get("status") == "incomplete":
        reason = nested(raw, "incomplete_details", "reason") or "unknown"
        raise RuntimeError(f"openai_incomplete:{reason}")
    text = _response_text(raw)
    if not text:
        raise RuntimeError("openai_missing_output_text")
    value = json.loads(text)
    validate_model_output(value)
    return value, raw


def validate_model_output(value: Mapping[str, Any]) -> None:
    if value.get("contract") != MODEL_OUTPUT_CONTRACT:
        raise ValueError("shadow_model_contract_mismatch")
    horizons = value.get("horizons")
    if not isinstance(horizons, Mapping) or set(horizons) != {"12h", "72h", "168h"}:
        raise ValueError("shadow_model_horizons_invalid")
    for key, row in horizons.items():
        if not isinstance(row, Mapping):
            raise ValueError(f"shadow_model_{key}_invalid")
        if row.get("direction") not in {"UP", "DOWN", "SIDEWAYS", "MIXED", "NO_EDGE"}:
            raise ValueError(f"shadow_model_{key}_direction_invalid")
        if row.get("confidence") not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError(f"shadow_model_{key}_confidence_invalid")
        if not row.get("falsification_conditions"):
            raise ValueError(f"shadow_model_{key}_falsification_missing")


def build_forecast(
    input_value: Mapping[str, Any],
    model_output: Mapping[str, Any],
    raw_response: Mapping[str, Any],
    *,
    model: str,
) -> dict[str, Any]:
    validate_model_output(model_output)
    issued = input_value["issued_at_utc"]
    source_fingerprint = sha256(canonical({
        "auto_market_state": nested(input_value, "source_bindings", "auto_market_state", "packet_sha256"),
        "cycle_navigator": nested(input_value, "source_bindings", "cycle_navigator", "machine_package_sha256"),
        "model": model,
        "reasoner_version": REASONER_VERSION,
    }))
    stamp = issued.replace("-", "").replace(":", "").replace("T", "-").replace("Z", "")
    forecast_id = f"SCV2-{stamp}-{source_fingerprint[:12]}"
    usage = raw_response.get("usage") if isinstance(raw_response.get("usage"), Mapping) else {}
    value = {
        "contract": FORECAST_CONTRACT,
        "forecast_id": forecast_id,
        "issued_at_utc": issued,
        "model_id": model,
        "reasoner_version": REASONER_VERSION,
        "source_fingerprint": source_fingerprint,
        "input_sha256": input_value.get("input_sha256"),
        "source_bindings": input_value.get("source_bindings"),
        "model_output": model_output,
        "usage": {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
        },
        "authority": {
            "classification": "SHADOW_PROSPECTIVE_FORECAST_ONLY",
            "portfolio_execution": False,
            "official_compass_override": False,
            "source_override": False,
            "market_threshold_change": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        },
    }
    value["forecast_sha256"] = sha256(canonical({k: v for k, v in value.items() if k != "forecast_sha256"}))
    return value


def write_forecast(repo: Path, forecast: Mapping[str, Any]) -> dict[str, Any]:
    issued = datetime.fromisoformat(str(forecast["issued_at_utc"]).replace("Z", "+00:00"))
    rel = OUTPUT_ROOT / "forecasts" / issued.strftime("%Y/%m/%d") / f"{forecast['forecast_id']}.json"
    path = repo / rel
    payload = canonical(forecast)
    if path.exists() and path.read_bytes() != payload:
        raise ValueError(f"IMMUTABLE_SHADOW_FORECAST_REWRITE_BLOCKED:{rel.as_posix()}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    pointer = {
        "contract": POINTER_CONTRACT,
        "forecast_id": forecast["forecast_id"],
        "forecast_path": rel.as_posix(),
        "forecast_sha256": forecast["forecast_sha256"],
        "source_fingerprint": forecast["source_fingerprint"],
        "issued_at_utc": forecast["issued_at_utc"],
        "model_id": forecast["model_id"],
        "authority": forecast["authority"],
    }
    pointer_path = repo / OUTPUT_ROOT / "LATEST.json"
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_bytes(canonical(pointer))
    return {"status": "CREATED", **pointer}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--model", default=MODEL_DEFAULT)
    ap.add_argument("--call-api", action="store_true")
    ap.add_argument("--input-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--now-utc")
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    issued = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00")) if args.now_utc else datetime.now(timezone.utc)
    if issued.utcoffset() is None:
        issued = issued.replace(tzinfo=timezone.utc)
    issued = issued.astimezone(timezone.utc).replace(microsecond=0)

    auto_pointer, auto_state, auto_path = load_auto_state_bundle(repo, AUTO_POINTER)
    cn_package, cn_binding = load_cn_context(repo, DEFAULT_CN_POINTER)
    input_value = build_input(
        auto_state,
        auto_pointer=auto_pointer,
        auto_packet_path=auto_path,
        cn_package=cn_package,
        cn_binding=cn_binding,
        issued_at=issued,
    )

    if args.input_only or not args.call_api:
        print(json.dumps(input_value, sort_keys=True))
        return

    fingerprint = sha256(canonical({
        "auto_market_state": nested(input_value, "source_bindings", "auto_market_state", "packet_sha256"),
        "cycle_navigator": nested(input_value, "source_bindings", "cycle_navigator", "machine_package_sha256"),
        "model": args.model,
        "reasoner_version": REASONER_VERSION,
    }))
    latest_path = repo / OUTPUT_ROOT / "LATEST.json"
    if latest_path.exists() and not args.force:
        latest = json.loads(latest_path.read_text())
        if latest.get("source_fingerprint") == fingerprint:
            print(json.dumps({"status": "NOOP_SAME_SOURCES", "forecast_id": latest.get("forecast_id"), "source_fingerprint": fingerprint}, sort_keys=True))
            return

    model_output, raw = call_model(input_value, model=args.model)
    forecast = build_forecast(input_value, model_output, raw, model=args.model)
    print(json.dumps(write_forecast(repo, forecast), sort_keys=True))


if __name__ == "__main__":
    main()
