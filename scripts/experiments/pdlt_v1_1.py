from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FIELDS = ["score","volatility","volume","impulse","technical","social","dominance","trends","whales","orders"]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def expected_credits(symbols: list[str], fields: list[str], limit: int) -> int:
    return len(symbols) * len(fields) * int(limit)


def validate_config(cfg: dict[str, Any]) -> dict[str, Any]:
    if cfg.get("contract") != "PDLT_CONFIG_v1_1":
        raise ValueError("invalid_contract")
    if cfg.get("status") != "READY_SHADOW_ONLY":
        raise ValueError("not_shadow_ready")
    cfgi = cfg["cfgi"]
    running = 0
    for row in cfgi["historical_plan"]:
        calculated = expected_credits(row["symbols"], row["fields"], row["limit"])
        if calculated != row["expected_credits"]:
            raise ValueError(f"credit_mismatch:{row['name']}:{calculated}:{row['expected_credits']}")
        if row["fields"] != FIELDS:
            raise ValueError(f"field_set_drift:{row['name']}")
        running += calculated
    if running != cfgi["historical_total_credits"]:
        raise ValueError("historical_total_mismatch")
    burst = cfgi["burst"]
    burst_calc = expected_credits(burst["symbols"], FIELDS, burst["limit"])
    if burst_calc != burst["expected_credits"]:
        raise ValueError("burst_credit_mismatch")
    planned = running + burst_calc * int(burst["planned_events"])
    maximum = running + burst_calc * (int(burst["planned_events"]) + int(burst["reserve_events"]))
    if planned != cfgi["planned_cap_credits"]:
        raise ValueError("planned_cap_mismatch")
    if maximum > cfgi["hard_cap_credits"]:
        raise ValueError("hard_cap_exceeded_by_config")
    if cfg["openai"]["planned_cap_usd"] > cfg["openai"]["soft_stop_usd"]:
        raise ValueError("openai_planned_above_soft_stop")
    if cfg["openai"]["soft_stop_usd"] > cfg["openai"]["hard_cap_usd"]:
        raise ValueError("openai_soft_above_hard")
    return {"historical_credits": running, "planned_credits": planned, "maximum_credits": maximum}


def epoch_for(ts: str, boundary: str) -> str:
    when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    edge = datetime.fromisoformat(boundary.replace("Z", "+00:00"))
    return "LEGACY_PRE_20260708" if when < edge else "UPGRADED_POST_20260708"


def validate_cfgi_snapshot(packet: dict[str, Any], cfg: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    if packet.get("contract") != "CFGI_OWNER_SNAPSHOT_v3":
        raise ValueError("unexpected_cfgi_contract")
    if packet.get("symbols") != expected["symbols"]:
        raise ValueError("symbol_mismatch")
    if packet.get("timeframe") != expected["timeframe"]:
        raise ValueError("timeframe_mismatch")
    if packet.get("fields") != expected["fields"]:
        raise ValueError("field_mismatch")
    if int(packet.get("limit", -1)) != int(expected["limit"]):
        raise ValueError("limit_mismatch")
    billing = packet.get("billing", {})
    exp = int(expected["expected_credits"])
    if billing.get("expected_credits") != exp:
        raise ValueError("expected_billing_mismatch")
    used = billing.get("credits_used")
    if used is not None and int(used) != exp:
        raise ValueError("actual_billing_mismatch")
    boundary = cfg["cfgi"]["engine_epoch_boundary_utc"]
    rows = packet.get("rows", [])
    if not rows:
        raise ValueError("empty_rows")
    tagged = []
    for row in rows:
        copy = dict(row)
        timestamp = copy.get("timestamp") or copy.get("time") or copy.get("datetime") or copy.get("created_at")
        if timestamp:
            try:
                copy["pdlt_engine_epoch"] = epoch_for(str(timestamp), boundary)
            except Exception:
                copy["pdlt_engine_epoch"] = "UNKNOWN_TIMESTAMP"
        else:
            copy["pdlt_engine_epoch"] = "UNKNOWN_TIMESTAMP"
        tagged.append(copy)
    return {
        "contract": "PDLT_CFGI_VALIDATED_BLOCK_v1",
        "source_contract": packet.get("contract"),
        "source_sha256": sha(packet),
        "name": expected["name"],
        "expected_credits": exp,
        "row_count": len(rows),
        "rows": tagged,
        "authority": "SHADOW_ONLY"
    }


def make_manifest(cfg: dict[str, Any]) -> dict[str, Any]:
    budget = validate_config(cfg)
    return {
        "contract": "PDLT_PREREGISTRATION_MANIFEST_v1",
        "experiment_id": cfg["experiment_id"],
        "config_sha256": sha(cfg),
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "budget": budget,
        "arms": cfg["arms"],
        "primary_contrasts": cfg["primary_contrasts"],
        "outcomes": cfg["outcomes"],
        "kill_criteria": cfg["kill_criteria"],
        "authority": cfg["authority"]
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--mode", choices=["validate-config", "preregister", "validate-cfgi"], required=True)
    ap.add_argument("--input", type=Path)
    ap.add_argument("--plan-name")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    cfg = load(args.config)
    if args.mode == "validate-config":
        result = {"status": "PASS", **validate_config(cfg), "config_sha256": sha(cfg)}
    elif args.mode == "preregister":
        result = make_manifest(cfg)
    else:
        if not args.input or not args.plan_name:
            raise SystemExit("validate-cfgi_requires_input_and_plan_name")
        expected = next((x for x in cfg["cfgi"]["historical_plan"] if x["name"] == args.plan_name), None)
        if expected is None:
            raise SystemExit("unknown_plan_name")
        result = validate_cfgi_snapshot(load(args.input), cfg, expected)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(result))
    print(json.dumps(result if args.mode != "validate-cfgi" else {k: result[k] for k in ("contract","name","expected_credits","row_count","source_sha256")}, sort_keys=True))


if __name__ == "__main__":
    main()
