#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import statistics
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent_handoff_contract as handoff  # noqa: E402

UTC = timezone.utc
CONTRACT = "AUTO_TRADING_E2_RESULT_v1"
REQUEST_CONTRACT = "AUTO_TRADING_E2_REQUEST_v1"
PRICE_PER_MILLION = {"gpt-5.6-luna": {"input": 0.2, "output": 1.2}}
ACTIONS = {"LONG", "SHORT", "FLAT"}
FEATURES = {"ret1_pct", "ret4_pct", "ret12_pct", "vol6_pct", "cross_ret4_pct"}
RAW_COLUMNS = {"timestamp", "btc_close", "eth_close", "spot_status"}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)).astimezone(UTC)


def iso(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def quantile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("empty_quantile")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def validate_request(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("contract") != REQUEST_CONTRACT:
        raise ValueError("invalid_request_contract")
    if raw.get("issue") != 911 or raw.get("status") != "APPROVED_RESEARCH_ONLY":
        raise ValueError("request_not_approved_for_issue_911")
    if raw.get("model") != "gpt-5.6-luna":
        raise ValueError("e2_v1_model_must_be_luna")
    if raw.get("compiler_repeats") != 3 or raw.get("policy_repeats") != 3:
        raise ValueError("e2_v1_repeats_must_equal_three")
    if raw.get("consumed_columns") != sorted(RAW_COLUMNS):
        raise ValueError("raw_column_firewall_mismatch")
    if raw.get("no_post_result_prompt_tuning") is not True:
        raise ValueError("post_result_tuning_must_be_forbidden")
    if raw.get("failed_and_abandoned_attempts_remain_counted") is not True:
        raise ValueError("failed_attempt_accounting_required")
    authority = raw.get("authority")
    if not isinstance(authority, dict) or any(bool(v) for v in authority.values()):
        raise ValueError("research_only_authority_required")
    for key in ("design_rows", "evaluation_points", "evaluation_stride_hours", "round_trip_cost_bps"):
        if not isinstance(raw.get(key), (int, float)) or float(raw[key]) <= 0:
            raise ValueError(f"invalid_request_field:{key}")
    if float(raw.get("hard_cost_stop_usd") or 0) <= 0 or float(raw["hard_cost_stop_usd"]) > 1.5:
        raise ValueError("invalid_hard_cost_stop")
    if sorted(raw.get("theory_ids") or []) != ["AT-HYP-0004", "AT-HYP-0008"]:
        raise ValueError("theory_binding_required")
    return raw


def load_raw_close_rows(root: Path, cutoff: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    cutoff_dt = dt(cutoff)
    rows: dict[str, dict[str, Any]] = {}
    sources: list[dict[str, str]] = []
    for path in sorted(root.glob("20??/??/*.csv")):
        raw_bytes = path.read_bytes()
        used = False
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not RAW_COLUMNS.issubset(set(reader.fieldnames)):
                continue
            for source in reader:
                ts = str(source.get("timestamp") or "").strip()
                if not ts:
                    continue
                when = dt(ts)
                if when > cutoff_dt or str(source.get("spot_status") or "").upper() != "PASS":
                    continue
                try:
                    row = {
                        "timestamp": iso(when),
                        "btc_close": float(source["btc_close"]),
                        "eth_close": float(source["eth_close"]),
                        "spot_status": "PASS",
                    }
                except (TypeError, ValueError):
                    continue
                if row["btc_close"] <= 0 or row["eth_close"] <= 0:
                    continue
                existing = rows.get(row["timestamp"])
                if existing is not None and existing != row:
                    raise ValueError(f"conflicting_raw_close_duplicate:{row['timestamp']}")
                rows[row["timestamp"]] = row
                used = True
        if used:
            sources.append({"path": str(path), "sha256": sha_bytes(raw_bytes)})
    ordered = sorted(rows.values(), key=lambda item: dt(item["timestamp"]))
    return ordered, sources


def latest_contiguous_block(rows: list[dict[str, Any]], minimum: int) -> list[dict[str, Any]]:
    best: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    for row in rows:
        if current and (dt(row["timestamp"]) - dt(current[-1]["timestamp"])).total_seconds() != 3600:
            if len(current) >= minimum:
                best = current
            current = []
        current.append(row)
    if len(current) >= minimum:
        best = current
    if len(best) < minimum:
        raise ValueError(f"insufficient_contiguous_raw_hours:{len(best)}<{minimum}")
    return best[-minimum:]


def pct(a: float, b: float) -> float:
    return (a / b - 1.0) * 100.0


def feature_row(block: list[dict[str, Any]], idx: int, asset: str) -> dict[str, float]:
    key = f"{asset.lower()}_close"
    other = "eth_close" if key == "btc_close" else "btc_close"
    one_hour_returns = [pct(block[j][key], block[j - 1][key]) for j in range(idx - 5, idx + 1)]
    return {
        "ret1_pct": pct(block[idx][key], block[idx - 1][key]),
        "ret4_pct": pct(block[idx][key], block[idx - 4][key]),
        "ret12_pct": pct(block[idx][key], block[idx - 12][key]),
        "vol6_pct": statistics.pstdev(one_hour_returns),
        "cross_ret4_pct": pct(block[idx][other], block[idx - 4][other]),
    }


def build_frozen_sample(rows: list[dict[str, Any]], request: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    warmup = 12
    design_rows = int(request["design_rows"])
    eval_points = int(request["evaluation_points"])
    stride = int(request["evaluation_stride_hours"])
    required = warmup + design_rows + (eval_points - 1) * stride + 2
    block = latest_contiguous_block(rows, required)
    design_indices = list(range(warmup, warmup + design_rows))
    eval_start = warmup + design_rows
    eval_indices = [eval_start + i * stride for i in range(eval_points)]
    design_summary: dict[str, Any] = {"assets": {}, "design_rows": design_rows}
    for asset in ("BTC", "ETH"):
        feature_values: dict[str, list[float]] = {name: [] for name in FEATURES}
        labels: list[float] = []
        by_index: list[dict[str, float]] = []
        key = f"{asset.lower()}_close"
        for idx in design_indices:
            features = feature_row(block, idx, asset)
            label = pct(block[idx + 1][key], block[idx][key])
            labels.append(label)
            by_index.append(features)
            for name, value in features.items():
                feature_values[name].append(value)
        summary_features: dict[str, Any] = {}
        for name, values in sorted(feature_values.items()):
            q25, q50, q75 = quantile(values, 0.25), quantile(values, 0.5), quantile(values, 0.75)
            gt75 = [labels[i] for i, value in enumerate(values) if value > q75]
            lt25 = [labels[i] for i, value in enumerate(values) if value < q25]
            summary_features[name] = {
                "q25": round(q25, 8), "q50": round(q50, 8), "q75": round(q75, 8),
                "mean_next_1h_bps_if_gt_q75": round(statistics.fmean(gt75) * 100.0, 6) if gt75 else None,
                "mean_next_1h_bps_if_lt_q25": round(statistics.fmean(lt25) * 100.0, 6) if lt25 else None,
            }
        design_summary["assets"][asset] = {
            "features": summary_features,
            "mean_next_1h_bps": round(statistics.fmean(labels) * 100.0, 6),
        }
    points: list[dict[str, Any]] = []
    for idx in eval_indices:
        for asset in ("BTC", "ETH"):
            key = f"{asset.lower()}_close"
            points.append({
                "asset": asset,
                "timestamp": block[idx]["timestamp"],
                "features": {k: round(v, 10) for k, v in feature_row(block, idx, asset).items()},
                "_evaluation_label_next_1h_pct": pct(block[idx + 1][key], block[idx][key]),
            })
    design_summary["window"] = {
        "first_design_timestamp": block[design_indices[0]]["timestamp"],
        "last_design_timestamp": block[design_indices[-1]]["timestamp"],
        "first_evaluation_timestamp": block[eval_indices[0]]["timestamp"],
        "last_evaluation_timestamp": block[eval_indices[-1]]["timestamp"],
    }
    return design_summary, points


def compiler_schema() -> dict[str, Any]:
    return {
        "type": "object", "additionalProperties": False,
        "required": ["feature", "long_trigger", "short_trigger", "rationale"],
        "properties": {
            "feature": {"type": "string", "enum": sorted(FEATURES)},
            "long_trigger": {"type": "string", "enum": ["GT_Q75", "GT_Q50", "DISABLED"]},
            "short_trigger": {"type": "string", "enum": ["LT_Q25", "LT_Q50", "DISABLED"]},
            "rationale": {"type": "string", "maxLength": 600},
        },
    }


def policy_schema() -> dict[str, Any]:
    return {
        "type": "object", "additionalProperties": False,
        "required": ["action", "rationale"],
        "properties": {
            "action": {"type": "string", "enum": sorted(ACTIONS)},
            "rationale": {"type": "string", "maxLength": 300},
        },
    }


def build_payload(model: str, effort: str, schema_name: str, schema: dict[str, Any], envelope: dict[str, Any], max_tokens: int) -> dict[str, Any]:
    instructions = (
        "You are participating in a blinded, research-only reproducibility experiment. "
        "The supplied action labels are offline research classes only; never infer live execution authority. "
        "Use only supplied design-period evidence and current point-in-time features. Evaluation outcomes are hidden. "
        "Do not request tools, portfolio actions, order routing, position sizes, credentials, or framework changes. "
        "Return only the strict structured output."
    )
    return {
        "model": model,
        "reasoning": {"effort": effort, "context": "current_turn"},
        "store": False,
        "max_output_tokens": max_tokens,
        "instructions": instructions,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": json.dumps(envelope, sort_keys=True)}]}],
        "text": {"format": {"type": "json_schema", "name": schema_name, "strict": True, "schema": schema}},
    }


def extract_output(response: dict[str, Any]) -> dict[str, Any]:
    text = response.get("output_text")
    if not text:
        chunks: list[str] = []
        for item in response.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    chunks.append(str(content.get("text") or ""))
        text = "".join(chunks)
    if not text:
        raise ValueError("missing_output_text")
    return json.loads(text)


def usage_cost(model: str, response: dict[str, Any]) -> tuple[int, int, float]:
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    i = int(usage.get("input_tokens", 0) or 0)
    o = int(usage.get("output_tokens", 0) or 0)
    price = PRICE_PER_MILLION[model]
    cost = (i * price["input"] + o * price["output"]) / 1_000_000.0
    return i, o, cost


def live_call(api_key: str, payload: dict[str, Any], model: str) -> dict[str, Any]:
    request_hash = sha(payload)
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=canon(payload),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            raw = json.loads(response.read())
        i, o, cost = usage_cost(model, raw)
        try:
            output = extract_output(raw)
            error = None
        except Exception as exc:  # failed output remains a counted trial
            output = None
            error = f"{type(exc).__name__}:{str(exc)[:200]}"
        return {
            "request_hash": request_hash, "response_id": raw.get("id"), "output": output,
            "input_tokens": i, "output_tokens": o, "cost_usd": cost, "error": error,
            "response_hash": sha(raw),
        }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        return {
            "request_hash": request_hash, "response_id": None, "output": None,
            "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
            "error": f"openai_http_{exc.code}:{body[:300]}", "response_hash": None,
        }


def fake_call(payload: dict[str, Any], model: str) -> dict[str, Any]:
    envelope = json.loads(payload["input"][0]["content"][0]["text"])
    if envelope["mode"] == "COMPILER":
        output = {"feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25", "rationale": "dry-run deterministic rule"}
    else:
        value = float(envelope["point"]["features"]["ret4_pct"])
        output = {"action": "LONG" if value > 0 else "SHORT" if value < 0 else "FLAT", "rationale": "dry-run deterministic policy"}
    return {
        "request_hash": sha(payload), "response_id": "dry-run", "output": output,
        "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "error": None,
        "response_hash": sha(output),
    }


def validate_rule(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    feature = value.get("feature")
    long_trigger = value.get("long_trigger")
    short_trigger = value.get("short_trigger")
    if feature not in FEATURES:
        return None
    if long_trigger not in {"GT_Q75", "GT_Q50", "DISABLED"} or short_trigger not in {"LT_Q25", "LT_Q50", "DISABLED"}:
        return None
    if long_trigger == "DISABLED" and short_trigger == "DISABLED":
        return None
    return {"feature": feature, "long_trigger": long_trigger, "short_trigger": short_trigger, "rationale": str(value.get("rationale") or "")}


def threshold(summary: dict[str, Any], asset: str, feature: str, trigger: str) -> float:
    q = {"GT_Q75": "q75", "GT_Q50": "q50", "LT_Q25": "q25", "LT_Q50": "q50"}[trigger]
    return float(summary["assets"][asset]["features"][feature][q])


def apply_rule(rule: dict[str, str], point: dict[str, Any], summary: dict[str, Any]) -> str:
    value = float(point["features"][rule["feature"]])
    if rule["long_trigger"] != "DISABLED" and value > threshold(summary, point["asset"], rule["feature"], rule["long_trigger"]):
        return "LONG"
    if rule["short_trigger"] != "DISABLED" and value < threshold(summary, point["asset"], rule["feature"], rule["short_trigger"]):
        return "SHORT"
    return "FLAT"


def baseline_action(point: dict[str, Any], summary: dict[str, Any]) -> str:
    rule = {"feature": "ret4_pct", "long_trigger": "GT_Q75", "short_trigger": "LT_Q25"}
    return apply_rule(rule, point, summary)


def placebo_action(point: dict[str, Any]) -> str:
    idx = int(hashlib.sha256(f"{point['asset']}|{point['timestamp']}".encode()).hexdigest()[:8], 16) % 3
    return ("LONG", "SHORT", "FLAT")[idx]


def pairwise_agreement(sequences: list[list[str]]) -> float:
    pairs = list(itertools.combinations(sequences, 2))
    if not pairs or not sequences or not sequences[0]:
        return 0.0
    matches = total = 0
    for left, right in pairs:
        if len(left) != len(right):
            raise ValueError("agreement_sequence_length_mismatch")
        for a, b in zip(left, right):
            matches += int(a == b)
            total += 1
    return matches / total if total else 0.0


def economic_metrics(actions: list[str], points: list[dict[str, Any]], round_trip_cost_bps: float) -> dict[str, Any]:
    if len(actions) != len(points):
        raise ValueError("action_point_length_mismatch")
    rows: list[dict[str, Any]] = []
    sign = {"LONG": 1.0, "SHORT": -1.0, "FLAT": 0.0}
    for action, point in zip(actions, points):
        gross = sign[action] * float(point["_evaluation_label_next_1h_pct"]) * 100.0
        cost = round_trip_cost_bps if action != "FLAT" else 0.0
        rows.append({"asset": point["asset"], "action": action, "gross_bps": gross, "net_bps": gross - cost})

    def summarize(subset: list[dict[str, Any]]) -> dict[str, Any]:
        trades = [row for row in subset if row["action"] != "FLAT"]
        return {
            "decisions": len(subset),
            "trades": len(trades),
            "exposure_rate": round(len(trades) / len(subset), 6) if subset else 0.0,
            "mean_net_bps_per_decision": round(statistics.fmean(row["net_bps"] for row in subset), 6) if subset else 0.0,
            "sum_net_bps": round(sum(row["net_bps"] for row in subset), 6),
            "hit_rate_on_trades": round(sum(row["net_bps"] > 0 for row in trades) / len(trades), 6) if trades else None,
        }
    return {
        "pooled": summarize(rows),
        "BTC": summarize([row for row in rows if row["asset"] == "BTC"]),
        "ETH": summarize([row for row in rows if row["asset"] == "ETH"]),
    }


def run_trial(request: dict[str, Any], repo_root: Path, output_dir: Path, dry_run: bool = False) -> dict[str, Any]:
    request = validate_request(request)
    rows, source_hashes = load_raw_close_rows(repo_root / request["source_root"], request["cutoff_utc"])
    design_summary, points = build_frozen_sample(rows, request)
    public_points = [{k: v for k, v in point.items() if not k.startswith("_evaluation_")} for point in points]
    if any("_evaluation_label" in json.dumps(point) for point in public_points):
        raise ValueError("evaluation_label_leak")
    model = request["model"]
    effort = request["reasoning_effort"]
    total_cost = 0.0
    call_records: list[dict[str, Any]] = []
    api_key = os.environ.get("OPENAI_API_KEY") if not dry_run else None
    if not dry_run and not api_key:
        raise SystemExit("OPENAI_API_KEY_missing")

    def call(payload: dict[str, Any], arm: str, repeat: int, point_id: str | None = None) -> dict[str, Any]:
        nonlocal total_cost
        rec = fake_call(payload, model) if dry_run else live_call(str(api_key), payload, model)
        total_cost += float(rec["cost_usd"])
        record = {"arm": arm, "repeat": repeat, "point_id": point_id, **rec}
        call_records.append(record)
        if total_cost > float(request["hard_cost_stop_usd"]):
            raise RuntimeError(f"e2_cost_hard_stop:{total_cost:.8f}")
        return record

    compiler_records: list[dict[str, Any]] = []
    compiler_rules: list[dict[str, str] | None] = []
    compiler_actions: list[list[str]] = []
    compiler_handoffs: list[dict[str, Any] | None] = []
    compiler_envelope = {
        "contract": "AUTO_TRADING_E2_BLINDED_INPUT_v1", "mode": "COMPILER",
        "mission": "Compile one constrained deterministic rule to replay on hidden evaluation outcomes.",
        "design_summary": design_summary,
        "allowed_features": sorted(FEATURES),
        "allowed_rule": {"long": ["GT_Q75", "GT_Q50", "DISABLED"], "short": ["LT_Q25", "LT_Q50", "DISABLED"]},
        "evaluation_outcomes_hidden": True,
    }
    compiler_payload = build_payload(model, effort, "e2_compiler_rule_v1", compiler_schema(), compiler_envelope, int(request["compiler_max_output_tokens"]))
    capability = {
        "tools": ["openai.responses", "deterministic_replay"],
        "schemas": {"compiler_output": sha(compiler_schema()), "policy_output": sha(policy_schema())},
        "runtime": "AUTO_TRADING_E2_v1",
    }
    mission_lock = {"experiment_id": request["experiment_id"], "issue": 911, "request_sha256": sha(request)}
    for repeat in range(1, int(request["compiler_repeats"]) + 1):
        record = call(compiler_payload, "AI_COMPILER", repeat)
        compiler_records.append(record)
        rule = validate_rule(record["output"])
        compiler_rules.append(rule)
        if rule is None:
            compiler_actions.append(["INVALID"] * len(points))
            compiler_handoffs.append(None)
            continue
        contract = handoff.build_contract(
            stage_id=f"E2_COMPILER_RUN_{repeat}", mission=mission_lock, input_artifact=design_summary,
            capability_snapshot=capability, output_artifact=rule, repair_scope=f"E2_COMPILER_RUN_{repeat}",
            owner_candidate_id=request["experiment_id"], created_at=request["frozen_at_utc"],
        )
        handoff.assert_downstream_input(contract, rule)
        compiler_handoffs.append(contract)
        compiler_actions.append([apply_rule(rule, point, design_summary) for point in points])

    policy_sequences: list[list[str]] = [[] for _ in range(int(request["policy_repeats"]))]
    for point_index, point in enumerate(public_points):
        envelope = {
            "contract": "AUTO_TRADING_E2_BLINDED_INPUT_v1", "mode": "DIRECT_POLICY",
            "mission": "Choose one offline research action class for this frozen point-in-time observation.",
            "design_summary": design_summary, "point": point, "evaluation_outcomes_hidden": True,
        }
        payload = build_payload(model, effort, "e2_direct_policy_v1", policy_schema(), envelope, int(request["policy_max_output_tokens"]))
        point_id = f"{point['asset']}@{point['timestamp']}"
        for repeat in range(1, int(request["policy_repeats"]) + 1):
            record = call(payload, "DIRECT_POLICY", repeat, point_id)
            output = record["output"]
            action = output.get("action") if isinstance(output, dict) else None
            policy_sequences[repeat - 1].append(action if action in ACTIONS else "INVALID")

    compiler_repro = pairwise_agreement(compiler_actions)
    direct_repro = pairwise_agreement(policy_sequences)
    valid_rule_hashes = [sha(rule) if rule is not None else "INVALID" for rule in compiler_rules]
    compiler_exact_rule_agreement = max(valid_rule_hashes.count(value) for value in set(valid_rule_hashes)) / len(valid_rule_hashes)

    primary_rule = compiler_rules[0]
    primary_compiler_actions = [apply_rule(primary_rule, point, design_summary) for point in points] if primary_rule else ["FLAT"] * len(points)
    primary_direct_actions = [action if action in ACTIONS else "FLAT" for action in policy_sequences[0]]
    baseline_actions = [baseline_action(point, design_summary) for point in points]
    placebo_actions = [placebo_action(point) for point in points]
    cost_bps = float(request["round_trip_cost_bps"])
    economics = {
        "DETERMINISTIC_BASELINE": economic_metrics(baseline_actions, points, cost_bps),
        "DETERMINISTIC_PLACEBO": economic_metrics(placebo_actions, points, cost_bps),
        "AI_COMPILER_PRIMARY": economic_metrics(primary_compiler_actions, points, cost_bps),
        "DIRECT_POLICY_PRIMARY": economic_metrics(primary_direct_actions, points, cost_bps),
    }
    thresholds = request["pre_registered_thresholds"]
    gap = compiler_repro - direct_repro
    baseline_net = economics["DETERMINISTIC_BASELINE"]["pooled"]["mean_net_bps_per_decision"]
    compiler_net = economics["AI_COMPILER_PRIMARY"]["pooled"]["mean_net_bps_per_decision"]
    noninferior = compiler_net >= baseline_net - float(thresholds["economic_noninferiority_bps_per_decision"])
    if primary_rule is None or compiler_repro < float(thresholds["compiler_min_replay_agreement"]):
        conclusion = "COMPILED_RULE_NOT_SUPPORTED"
    elif direct_repro < float(thresholds["direct_min_action_agreement"]) and gap >= float(thresholds["material_reproducibility_gap"]) and noninferior:
        conclusion = "DIRECT_LLM_NOT_REPRODUCIBLE__COMPILER_ROLE_SUPPORTED_FOR_FURTHER_RESEARCH"
    elif gap >= float(thresholds["material_reproducibility_gap"]) and noninferior:
        conclusion = "AI_COMPILER_ROLE_SUPPORTED_FOR_FURTHER_RESEARCH"
    elif -gap >= float(thresholds["material_reproducibility_gap"]):
        conclusion = "DIRECT_POLICY_MORE_REPRODUCIBLE_IN_THIS_TRIAL"
    else:
        conclusion = "NO_CLEAR_ROLE_ADVANTAGE"

    compiler_cost = sum(float(r["cost_usd"]) for r in call_records if r["arm"] == "AI_COMPILER")
    direct_cost = sum(float(r["cost_usd"]) for r in call_records if r["arm"] == "DIRECT_POLICY")
    result = {
        "contract": CONTRACT,
        "experiment_id": request["experiment_id"],
        "issue": 911,
        "status": "COMPLETE",
        "request_sha256": sha(request),
        "source_hashes": source_hashes,
        "data_firewall": {
            "consumed_columns": sorted(RAW_COLUMNS),
            "quarantined_derived_history_used": False,
            "features_computed_point_in_time_in_harness": True,
            "evaluation_labels_hidden_from_ai": True,
        },
        "sample": {"design": design_summary["window"], "evaluation_decisions": len(points), "assets": ["BTC", "ETH"]},
        "reproducibility": {
            "compiler_replay_pairwise_agreement": round(compiler_repro, 8),
            "compiler_exact_rule_hash_agreement": round(compiler_exact_rule_agreement, 8),
            "direct_policy_pairwise_action_agreement": round(direct_repro, 8),
            "compiler_minus_direct_gap": round(gap, 8),
            "compiler_rule_hashes": valid_rule_hashes,
        },
        "economics": economics,
        "api": {
            "model": model, "reasoning_effort": effort,
            "compiler_calls": int(request["compiler_repeats"]),
            "direct_policy_calls": int(request["policy_repeats"]) * len(points),
            "failed_calls": sum(bool(r["error"]) or r["output"] is None for r in call_records),
            "compiler_cost_usd": round(compiler_cost, 8), "direct_policy_cost_usd": round(direct_cost, 8),
            "total_cost_usd": round(total_cost, 8), "hard_cost_stop_usd": request["hard_cost_stop_usd"],
        },
        "primary_compiler_rule": primary_rule,
        "compiler_handoffs": compiler_handoffs,
        "conclusion": conclusion,
        "economic_noninferiority_to_baseline": noninferior,
        "authority": request["authority"],
        "capital_ready": False,
        "no_retroactive_rescore": True,
        "no_post_result_prompt_tuning": True,
    }
    result["result_sha256"] = sha(result)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_bytes(canon(result))
    (output_dir / "calls.jsonl").write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in call_records), encoding="utf-8")
    (output_dir / "design_summary.json").write_bytes(canon(design_summary))
    print(json.dumps({
        "status": result["status"], "experiment_id": result["experiment_id"], "conclusion": conclusion,
        "compiler_agreement": result["reproducibility"]["compiler_replay_pairwise_agreement"],
        "direct_agreement": result["reproducibility"]["direct_policy_pairwise_action_agreement"],
        "compiler_net_bps": compiler_net, "baseline_net_bps": baseline_net,
        "total_cost_usd": result["api"]["total_cost_usd"], "result_sha256": result["result_sha256"],
    }, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    run_trial(request, args.repo_root, args.output_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
