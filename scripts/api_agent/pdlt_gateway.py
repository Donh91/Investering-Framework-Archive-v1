from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PRICES_PER_MILLION = {
    "gpt-5.6-terra": {"input": 2.5, "output": 15.0},
    "gpt-5.6-sol": {"input": 5.0, "output": 30.0},
}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def estimate_cost(model: str, inp: int, out: int) -> float:
    p = PRICES_PER_MILLION[model]
    return round((inp * p["input"] + out * p["output"]) / 1_000_000, 8)


def schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "prediction_valid", "p_pullback_72h", "p_heavy_pullback_7d",
            "p_persistent_distribution_14d", "expected_lead_time_hours",
            "exit_risk_0_100", "top_3_evidence_fields", "falsifier", "abstain_reason"
        ],
        "properties": {
            "prediction_valid": {"type": "boolean"},
            "p_pullback_72h": {"type": "number", "minimum": 0, "maximum": 1},
            "p_heavy_pullback_7d": {"type": "number", "minimum": 0, "maximum": 1},
            "p_persistent_distribution_14d": {"type": "number", "minimum": 0, "maximum": 1},
            "expected_lead_time_hours": {"type": "number", "minimum": 0, "maximum": 336},
            "exit_risk_0_100": {"type": "number", "minimum": 0, "maximum": 100},
            "top_3_evidence_fields": {"type": "array", "maxItems": 3, "items": {"type": "string"}},
            "falsifier": {"type": "string"},
            "abstain_reason": {"type": ["string", "null"]}
        }
    }


def build_payload(model: str, effort: str, context: dict[str, Any], arm: str) -> dict[str, Any]:
    instruction = (
        "You are the frozen forward forecaster for the shadow-only PDLT experiment. "
        "Use only the supplied timestamp-safe context. Do not infer missing values. Do not use future data. "
        "Do not recommend trades or portfolio actions. Return calibrated probabilities, not certainty. "
        "If evidence is stale, materially incomplete, or internally conflicting, set prediction_valid=false. "
        "Arm C never receives CFGI. Arm D may use CFGI only when present in the supplied context."
    )
    prompt = {
        "experiment": "PDLT-v1.1-RUN",
        "arm": arm,
        "task": "Estimate prospective deterioration risk before the registered outcome windows mature.",
        "context": context
    }
    return {
        "model": model,
        "reasoning": {"effort": effort, "context": "current_turn"},
        "store": False,
        "max_output_tokens": 900,
        "instructions": instruction,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": json.dumps(prompt, sort_keys=True)}]}],
        "text": {"format": {"type": "json_schema", "name": "pdlt_forward_forecast", "strict": True, "schema": schema()}}
    }


def call(payload: dict[str, Any]) -> dict[str, Any]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY_missing")
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=canonical(payload),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"openai_http_{exc.code}:{body[:500]}") from exc


def output_text(response: dict[str, Any]) -> str:
    if response.get("output_text"):
        return str(response["output_text"])
    parts: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(str(content.get("text", "")))
    if not parts:
        raise ValueError("missing_output_text")
    return "".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--context", type=Path, required=True)
    ap.add_argument("--arm", choices=["C", "D"], required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text())
    context = json.loads(args.context.read_text())
    model = cfg["openai"]["forward_model"]
    effort = cfg["openai"]["forward_reasoning_effort"]
    if args.arm == "C" and "cfgi" in context:
        raise SystemExit("arm_c_context_contains_cfgi")
    payload = build_payload(model, effort, context, args.arm)
    request_bytes = canonical(payload)
    if args.dry_run:
        forecast = {
            "prediction_valid": False,
            "p_pullback_72h": 0.0,
            "p_heavy_pullback_7d": 0.0,
            "p_persistent_distribution_14d": 0.0,
            "expected_lead_time_hours": 0.0,
            "exit_risk_0_100": 0.0,
            "top_3_evidence_fields": [],
            "falsifier": "DRY_RUN_ONLY",
            "abstain_reason": "NO_API_CALL"
        }
        response = {"id": "dry-run", "usage": {"input_tokens": 0, "output_tokens": 0}}
    else:
        response = call(payload)
        forecast = json.loads(output_text(response))
    usage = response.get("usage", {})
    inp = int(usage.get("input_tokens", 0))
    out = int(usage.get("output_tokens", 0))
    cost = estimate_cost(model, inp, out)
    if cost > float(cfg["openai"]["soft_stop_usd"]):
        raise SystemExit(f"pdlt_single_call_soft_stop_exceeded:{cost}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    forecast_bytes = canonical(forecast)
    (args.output_dir / f"arm_{args.arm}_forecast.json").write_bytes(forecast_bytes)
    receipt = {
        "contract": "PDLT_OPENAI_RECEIPT_v1",
        "experiment_id": cfg["experiment_id"],
        "arm": args.arm,
        "model": model,
        "reasoning_effort": effort,
        "request_sha256": sha(request_bytes),
        "context_sha256": sha(canonical(context)),
        "schema_sha256": sha(canonical(schema())),
        "forecast_sha256": sha(forecast_bytes),
        "response_id": response.get("id"),
        "input_tokens": inp,
        "output_tokens": out,
        "estimated_cost_usd": cost,
        "created_unix": int(time.time()),
        "authority": "SHADOW_ONLY_NO_PORTFOLIO_AUTHORITY"
    }
    (args.output_dir / f"arm_{args.arm}_receipt.json").write_bytes(canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
