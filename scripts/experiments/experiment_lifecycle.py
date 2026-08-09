#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
KINDS = {"SENSOR_COMBINATION", "FORECAST_TEST", "SEQUENCE_TEST", "DATA_QUALITY_TEST"}
OPS = {"GT", "LT", "DELTA_PCT_GT", "DELTA_PCT_LT", "POSITIVE", "NEGATIVE", "AVAILABLE", "CHANGED"}
UNIT_CONTRACT_VERSION = "FORECAST_TARGET_UNITS_v2"


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def dt(value: Any) -> datetime:
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return (result if result.tzinfo else result.replace(tzinfo=UTC)).astimezone(UTC)


def iso(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def at(value: Any, path: str) -> Any:
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def rel(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def write_new(path: Path, value: dict[str, Any]) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canon(value))
    return True


def component(raw: dict[str, Any]) -> dict[str, Any]:
    path = str(raw.get("metric_path") or "").strip()
    operator = str(raw.get("operator") or "").upper()
    threshold = raw.get("threshold")
    if not path or operator not in OPS:
        raise ValueError("invalid_component")
    if operator in {"GT", "LT", "DELTA_PCT_GT", "DELTA_PCT_LT"} and not isinstance(threshold, (int, float)):
        raise ValueError("threshold_required")
    return {"metric_path": path, "operator": operator, "threshold": float(threshold) if isinstance(threshold, (int, float)) else None}


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    kind = str(raw.get("kind") or "SENSOR_COMBINATION").upper()
    direction = str(raw.get("target_direction") or "NONE").upper()
    if kind not in KINDS or direction not in {"UP", "DOWN", "RANGE", "NONE"}:
        raise ValueError("invalid_kind_or_direction")
    title = str(raw.get("title") or "").strip()
    hypothesis = str(raw.get("hypothesis") or "").strip()
    falsifier = str(raw.get("falsifier") or "").strip()
    horizon_days = int(raw.get("horizon_days") or 0)
    if not title or not hypothesis or not falsifier or not 1 <= horizon_days <= 365:
        raise ValueError("invalid_identity_or_horizon")
    target = str(raw.get("target_metric_path") or "").strip() or None
    threshold_pct = raw.get("target_threshold_pct")
    range_lower_pct = raw.get("target_range_lower_pct")
    range_upper_pct = raw.get("target_range_upper_pct")
    if direction in {"UP", "DOWN"} and (not target or not isinstance(threshold_pct, (int, float)) or float(threshold_pct) <= 0):
        raise ValueError("invalid_directional_target")
    if direction == "RANGE" and (not target or not isinstance(range_lower_pct, (int, float)) or not isinstance(range_upper_pct, (int, float)) or float(range_lower_pct) >= float(range_upper_pct)):
        raise ValueError("invalid_range_target")
    if direction == "NONE":
        target = threshold_pct = range_lower_pct = range_upper_pct = None
    return {
        "kind": kind,
        "title": title,
        "hypothesis": hypothesis,
        "falsifier": falsifier,
        "horizon_days": horizon_days,
        "components": [component(item) for item in raw.get("components", []) if isinstance(item, dict)],
        "target_metric_path": target,
        "target_direction": direction,
        "target_threshold_pct": float(threshold_pct) if isinstance(threshold_pct, (int, float)) else None,
        "target_range_lower_pct": float(range_lower_pct) if isinstance(range_lower_pct, (int, float)) else None,
        "target_range_upper_pct": float(range_upper_pct) if isinstance(range_upper_pct, (int, float)) else None,
        "target_unit_contract_version": raw.get("target_unit_contract_version"),
        "regime_dependency": str(raw.get("regime_dependency") or "REGIME_AGNOSTIC"),
        "novelty_reason": str(raw.get("novelty_reason") or "UNSPECIFIED"),
        "revisit_conditions": [str(item) for item in raw.get("revisit_conditions", [])],
        "evidence_basis": [str(item) for item in raw.get("evidence_basis", [])],
    }


def identity_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {key: spec[key] for key in ("kind", "title", "hypothesis", "falsifier", "horizon_days", "components", "target_metric_path", "target_direction", "target_threshold_pct", "target_range_lower_pct", "target_range_upper_pct", "target_unit_contract_version", "regime_dependency")}


def placebo(event_window_id: str) -> str:
    return ("UP", "DOWN", "RANGE")[int(event_window_id[0], 16) % 3]


def from_forecast(raw: dict[str, Any], latest: dict[str, Any]) -> dict[str, Any] | None:
    direction = str(raw.get("direction") or "").upper()
    path = str(raw.get("metric_path") or "")
    horizon_days = raw.get("horizon_days")
    start = at(latest, path)
    if direction not in {"UP", "DOWN", "RANGE"} or not path or not isinstance(horizon_days, int):
        return None
    out = {
        "kind": "FORECAST_TEST", "title": f"Prospective {path} {direction}",
        "hypothesis": str(raw.get("rationale") or "Prospective forecast candidate"),
        "falsifier": "The fixed target is not satisfied at the fixed horizon.",
        "horizon_days": horizon_days, "components": [], "target_metric_path": path,
        "target_direction": direction, "target_threshold_pct": None, "target_range_lower_pct": None,
        "target_range_upper_pct": None, "target_unit_contract_version": UNIT_CONTRACT_VERSION,
        "regime_dependency": "CURRENT_OBSERVED_REGIME", "novelty_reason": "DAILY_DIRECTOR_FORECAST",
        "revisit_conditions": [], "evidence_basis": [str(raw.get("rationale") or "")],
    }
    mode = raw.get("target_mode")
    if direction in {"UP", "DOWN"}:
        if mode == "PCT_MOVE":
            threshold_pct = raw.get("threshold_pct")
            if not isinstance(threshold_pct, (int, float)) or float(threshold_pct) <= 0:
                return None
            out["target_threshold_pct"] = float(threshold_pct)
            return out
        if mode == "ABSOLUTE_VALUE":
            target_value = raw.get("target_value")
            if not isinstance(start, (int, float)) or not isinstance(target_value, (int, float)) or float(start) == 0:
                return None
            start_value = float(start); target_value = float(target_value)
            if direction == "UP":
                if target_value <= start_value: return None
                out["target_threshold_pct"] = (target_value / start_value - 1.0) * 100.0
            else:
                if target_value >= start_value: return None
                out["target_threshold_pct"] = (1.0 - target_value / start_value) * 100.0
            return out
        return None
    if mode != "ABSOLUTE_RANGE": return None
    low = raw.get("range_low"); high = raw.get("range_high")
    if not isinstance(start, (int, float)) or float(start) == 0 or not isinstance(low, (int, float)) or not isinstance(high, (int, float)) or float(low) >= float(high):
        return None
    out["target_range_lower_pct"] = (float(low) / float(start) - 1.0) * 100.0
    out["target_range_upper_pct"] = (float(high) / float(start) - 1.0) * 100.0
    return out


def emergent_pairs(context: dict[str, Any], latest: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    rows = []
    for item in context.get("metric_deltas", []):
        if not isinstance(item, dict) or not isinstance(item.get("percentage_change"), (int, float)): continue
        path = str(item.get("metric") or ""); change = float(item["percentage_change"])
        if not path or abs(change) < 0.05 or any(key in path.lower() for key in ("timestamp", "time_ms", "retrieval")): continue
        rows.append((abs(change), path, change))
    rows = sorted(rows, reverse=True)[:6]
    target = "spot.BTCUSDT.close" if isinstance(at(latest, "spot.BTCUSDT.close"), (int, float)) else None
    output = []
    if not target: return output
    for (_, first, first_delta), (_, second, second_delta) in itertools.combinations(rows, 2):
        same = first_delta * second_delta > 0; direction = "UP" if same and first_delta > 0 else "DOWN" if same else "RANGE"
        output.append({"kind": "SENSOR_COMBINATION", "title": f"Emergent pair: {first} + {second}", "hypothesis": f"The coincident direction of {first} and {second} may contain forward information for BTC over seven days.", "falsifier": "The pair fails to beat its fixed directional or range target across prospective independent windows.", "horizon_days": 7, "components": [{"metric_path": first, "operator": "DELTA_PCT_GT" if first_delta > 0 else "DELTA_PCT_LT", "threshold": 0.0}, {"metric_path": second, "operator": "DELTA_PCT_GT" if second_delta > 0 else "DELTA_PCT_LT", "threshold": 0.0}], "target_metric_path": target, "target_direction": direction, "target_threshold_pct": 1.0 if direction in {"UP", "DOWN"} else None, "target_range_lower_pct": -1.5 if direction == "RANGE" else None, "target_range_upper_pct": 1.5 if direction == "RANGE" else None, "target_unit_contract_version": UNIT_CONTRACT_VERSION, "regime_dependency": "DISCOVERED_IN_CURRENT_DELTA_REGIME", "novelty_reason": "AUTOMATIC_COINCIDENCE_DISCOVERY", "revisit_conditions": ["Re-evaluate whenever both metrics are comparable."], "evidence_basis": [f"{first} delta={first_delta:.8f}%", f"{second} delta={second_delta:.8f}%"]})
        if len(output) >= limit: break
    return output


def legacy(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists(): return []
    value = read(path); output = []
    for pair in value.get("pairs", []):
        first = str(pair.get("sensor_a") or "UNKNOWN"); second = str(pair.get("sensor_b") or "UNKNOWN"); pair_id = str(pair.get("pair_id") or "UNKNOWN")
        output.append({"kind": "SENSOR_COMBINATION", "title": f"Legacy sensor pair {pair_id}: {first} + {second}", "hypothesis": f"The frozen combination {first} and {second} may add marginal value when machine-mappable.", "falsifier": "After prospective mapping and sufficient independent windows, the pair fails to beat the best single-sensor control.", "horizon_days": 7, "components": [], "target_metric_path": None, "target_direction": "NONE", "target_threshold_pct": None, "target_range_lower_pct": None, "target_range_upper_pct": None, "target_unit_contract_version": None, "regime_dependency": "WAITING_FOR_MACHINE_SENSOR_MAPPING", "novelty_reason": f"PRESERVE_FROZEN_SENSOR_PAIR_{pair_id}", "revisit_conditions": [f"Map {first} to source-backed metrics", f"Map {second} to source-backed metrics", "Create a new linked measurable candidate without rewriting this concept"], "evidence_basis": [f"legacy_test_id={value.get('test_id')}", f"pair_id={pair_id}"]})
    return output


def delta(latest: Any, previous: Any) -> float | None:
    if not isinstance(latest, (int, float)) or not isinstance(previous, (int, float)) or previous == 0: return None
    return (float(latest) / float(previous) - 1.0) * 100.0


def evaluate(spec: dict[str, Any], latest: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    latest_value = at(latest, spec["metric_path"]); previous_value = at(previous, spec["metric_path"]); change = delta(latest_value, previous_value); operator = spec["operator"]; threshold = spec.get("threshold")
    if latest_value is None or (operator.startswith("DELTA_") and change is None): matched = None
    elif operator == "AVAILABLE": matched = True
    elif operator == "GT": matched = isinstance(latest_value, (int, float)) and float(latest_value) > float(threshold)
    elif operator == "LT": matched = isinstance(latest_value, (int, float)) and float(latest_value) < float(threshold)
    elif operator == "DELTA_PCT_GT": matched = change is not None and change > float(threshold)
    elif operator == "DELTA_PCT_LT": matched = change is not None and change < float(threshold)
    elif operator == "POSITIVE": matched = isinstance(latest_value, (int, float)) and float(latest_value) > 0
    elif operator == "NEGATIVE": matched = isinstance(latest_value, (int, float)) and float(latest_value) < 0
    else: matched = previous_value is not None and latest_value != previous_value
    return {**spec, "latest": latest_value, "previous": previous_value, "delta_pct": round(change, 8) if change is not None else None, "matched": matched}


def jsons(root: Path, contract: str) -> list[tuple[Path, dict[str, Any]]]:
    output = []
    for path in root.rglob("*.json") if root.exists() else []:
        try: value = read(path)
        except Exception: continue
        if value.get("contract") == contract: output.append((path, value))
    return output


def registry(candidate_root: Path, observation_root: Path, forecast_root: Path, outcome_root: Path, receipt_root: Path, now: str) -> dict[str, Any]:
    candidates = [value for _, value in jsons(candidate_root, "EXPERIMENT_CANDIDATE_v1")]; observations = {}; candidate_forecasts = {}; outcomes = {}; receipts = {}
    for _, value in jsons(observation_root, "EXPERIMENT_OBSERVATION_v1"): observations.setdefault(value["candidate_id"], []).append(value)
    for _, value in jsons(forecast_root, "FROZEN_FORECAST_v1"):
        candidate_id = value.get("source_candidate_id"); forecast_id = value.get("forecast_id")
        if candidate_id and forecast_id: candidate_forecasts.setdefault(candidate_id, []).append(forecast_id)
    for path in outcome_root.rglob("*.json") if outcome_root.exists() else []:
        try: value = read(path)
        except Exception: continue
        if value.get("forecast_id"): outcomes[value["forecast_id"]] = value
    for _, value in jsons(receipt_root, "EXPERIMENT_EXECUTION_RECEIPT_v1"): receipts.setdefault(value.get("candidate_id"), []).append(value.get("replication_status"))
    rows = []; counts = {}
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]; candidate_observations = sorted(observations.get(candidate_id, []), key=lambda item: item.get("observed_at_utc", "")); last = candidate_observations[-1] if candidate_observations else None; forecast_ids = candidate_forecasts.get(candidate_id, []); matured = [outcomes[item] for item in forecast_ids if item in outcomes]
        if candidate.get("spec", {}).get("kind") == "FORECAST_TEST" and candidate.get("spec", {}).get("target_unit_contract_version") != UNIT_CONTRACT_VERSION: state = "TARGET_UNIT_QUARANTINED"
        elif any(item.get("status") == "MATURED" and item.get("result") == "HIT" for item in matured): state = "MATURED_SUPPORTED"
        elif any(item.get("status") == "MATURED" and item.get("result") == "MISS" for item in matured): state = "MATURED_NOT_SUPPORTED"
        elif matured: state = "MATURED_INCONCLUSIVE"
        elif forecast_ids: state = "WAITING_FOR_MATURITY"
        elif last and last.get("evaluation_status") == "WAITING_FOR_MAPPING": state = "WAITING_FOR_MAPPING"
        elif last and last.get("evaluation_status") == "WAITING_FOR_DATA": state = "WAITING_FOR_DATA"
        elif last and last.get("evaluation_status") == "FIRED_NO_TARGET": state = "FIRED_NO_TARGET"
        elif candidate_observations: state = "INCUBATING"
        else: state = "PROPOSED"
        counts[state] = counts.get(state, 0) + 1
        rows.append({"candidate_id": candidate_id, "title": candidate["spec"]["title"], "kind": candidate["spec"]["kind"], "state": state, "created_at_utc": candidate["created_at_utc"], "observation_count": len(candidate_observations), "forecast_ids": forecast_ids, "matured_outcome_count": len(matured), "replication_receipts": sorted(set(item for item in receipts.get(candidate_id, []) if item)), "automatic_age_expiry": False})
    return {"contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1", "generated_at_utc": now, "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION", "candidate_count": len(rows), "state_counts": counts, "candidates": rows, "rules": {"idea_bank_capacity": "UNBOUNDED_WITH_SEMANTIC_DEDUPLICATION", "automatic_age_expiry": False, "max_new_forecasts_per_run_default": 5, "promotion_requires_governance_review": True}}


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("repo-root", "daily-output", "daily-context", "daily-receipt", "candidate-root", "observation-root", "dispatch-root", "forecast-root", "outcome-root", "receipt-root", "registry-output", "manifest-output"): parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--legacy-sensor-catalog", type=Path); parser.add_argument("--repository", default="Donh91/Investering-Framework-Archive-v1"); parser.add_argument("--branch", default="main"); parser.add_argument("--max-new-forecasts", type=int, default=5); args = parser.parse_args()
    root = args.repo_root.resolve(); output = read(args.daily_output); context = read(args.daily_context); receipt = read(args.daily_receipt); latest = ((context.get("latest_capture") or {}).get("market_metrics") or {}); previous = ((context.get("previous_capture") or {}).get("market_metrics") or {}); captured = (context.get("latest_capture") or {}).get("captured_at_utc") or iso(datetime.now(UTC)); when = dt(captured); now = iso(datetime.now(UTC)); source = {"daily_output_sha256": sha(output), "daily_context_sha256": sha(context), "daily_receipt_sha256": sha(receipt), "source_run_id": (context.get("latest_capture") or {}).get("run_id")}
    raw = [item for item in output.get("experiment_candidates", []) if isinstance(item, dict)] + legacy(args.legacy_sensor_catalog) + emergent_pairs(context, latest); rejected = []
    for item in output.get("forecast_candidates", []):
        if not isinstance(item, dict): continue
        mapped = from_forecast(item, latest)
        if mapped: raw.append(mapped)
        else: rejected.append({"title": f"Prospective {item.get('metric_path')}", "error": "explicit_target_unit_contract_required"})
    new_ids = set()
    for item in raw:
        try:
            spec = normalize(item); candidate_id = "EC-" + sha(identity_spec(spec))[:20]; value = {"contract": "EXPERIMENT_CANDIDATE_v1", "candidate_id": candidate_id, "created_at_utc": captured, "registered_at_utc": now, "target_unit_contract_version": spec.get("target_unit_contract_version"), "spec": spec, "source": {**source, "daily_output_path": rel(root, args.daily_output), "daily_context_path": rel(root, args.daily_context), "daily_receipt_path": rel(root, args.daily_receipt)}, "dormancy_policy": {"automatic_age_expiry": False, "retain_until": "FALSIFIED_OR_GOVERNANCE_CLOSED"}, "authority": {"canonical_promotion": False, "framework_state_change": False, "model_weight_change": False, "portfolio_action": False}}
            if write_new(args.candidate_root / when.strftime("%Y/%m") / f"{candidate_id}.json", value): new_ids.add(candidate_id)
        except Exception as exc: rejected.append({"title": str(item.get("title") or "UNKNOWN"), "error": str(exc)})
    new_forecasts = 0; dispatch = 0; candidate_rows = jsons(args.candidate_root, "EXPERIMENT_CANDIDATE_v1"); candidate_rows.sort(key=lambda item: (0 if item[1].get("spec", {}).get("kind") == "FORECAST_TEST" else 1, str(item[1].get("candidate_id") or "")))
    for spec_path, candidate in candidate_rows:
        spec = candidate["spec"]; legacy_forecast_unit_ambiguous = spec.get("kind") == "FORECAST_TEST" and spec.get("target_unit_contract_version") != UNIT_CONTRACT_VERSION; results = [evaluate(item, latest, previous) for item in spec["components"]]; mapping = not spec["components"] and spec["kind"] != "FORECAST_TEST"; missing = any(item["matched"] is None for item in results); fired = not legacy_forecast_unit_ambiguous and not mapping and ((not spec["components"] and spec["kind"] == "FORECAST_TEST") or (results and not missing and all(item["matched"] for item in results)))
        status = "TARGET_UNIT_QUARANTINED" if legacy_forecast_unit_ambiguous else "WAITING_FOR_MAPPING" if mapping else "WAITING_FOR_DATA" if missing else "FIRED_NO_TARGET" if fired and spec["target_direction"] == "NONE" else "FIRED" if fired else "OBSERVED_NOT_FIRED"
        observation_id = "EO-" + sha({"candidate_id": candidate["candidate_id"], "captured": captured, "source": source})[:20]; observation = {"contract": "EXPERIMENT_OBSERVATION_v1", "observation_id": observation_id, "candidate_id": candidate["candidate_id"], "observed_at_utc": captured, "evaluation_status": status, "component_results": results, "source": source, "authority": "SHADOW_ONLY"}; observation_path = args.observation_root / candidate["candidate_id"] / f"{observation_id}.json"; is_new = False if mapping and candidate["candidate_id"] not in new_ids else write_new(observation_path, observation)
        forecast_id = None; start = at(latest, spec.get("target_metric_path") or "") if spec.get("target_metric_path") else None
        if fired and spec["target_direction"] != "NONE" and isinstance(start, (int, float)) and new_forecasts < args.max_new_forecasts:
            window = sha({"run": source["source_run_id"], "captured": captured})[:20]; forecast_id = "EXP-FC-" + sha({"candidate_id": candidate["candidate_id"], "window": window})[:20]; frozen = {"contract": "FROZEN_FORECAST_v1", "unit_contract_version": UNIT_CONTRACT_VERSION, "forecast_id": forecast_id, "source_candidate_id": candidate["candidate_id"], "source_observation_id": observation_id, "frozen_at_utc": captured, "outcome_due_utc": iso(when + timedelta(days=spec["horizon_days"])), "metric_path": spec["target_metric_path"], "direction": spec["target_direction"], "start_value": float(start), "target_mode": "PCT_MOVE" if spec["target_direction"] in {"UP", "DOWN"} else "PCT_RANGE", "threshold_pct": spec["target_threshold_pct"], "range_lower_pct": spec["target_range_lower_pct"], "range_upper_pct": spec["target_range_upper_pct"], "causal_event_window_id": window, "experimental_only": True, "controls": {"always_wait": "ALWAYS_WAIT", "single_component_specs": spec["components"], "deterministic_placebo_direction": placebo(window), "control_freeze_time_utc": captured}, "authority": {"portfolio_action": False, "framework_state_change": False, "model_weight_change": False, "canonical_promotion": False}}
            if write_new(args.forecast_root / when.strftime("%Y/%m") / f"{forecast_id}.json", frozen): new_forecasts += 1
        if is_new and (candidate["candidate_id"] in new_ids or fired):
            request_id = "ER-" + sha({"candidate_id": candidate["candidate_id"], "observation_id": observation_id})[:20]; request = {"contract": "EXPERIMENT_REQUEST_v1", "request_id": request_id, "candidate_id": candidate["candidate_id"], "created_at_utc": now, "request_type": "SENSOR_FIRE_REPLICATION" if fired else "SPEC_REGISTRATION", "spec": spec, "embedded_observation": observation, "local_frozen_forecast_id": forecast_id, "source_spec_path": rel(root, spec_path), "source_spec_sha256": sha(candidate), "authority": {"automatic_trade": False, "canonical_promotion": False, "portfolio_action": False}}
            dispatch += int(write_new(args.dispatch_root / when.strftime("%Y/%m/%d") / f"{request_id}.json", request))
    reg = registry(args.candidate_root, args.observation_root, args.forecast_root, args.outcome_root, args.receipt_root, now); args.registry_output.parent.mkdir(parents=True, exist_ok=True); args.registry_output.write_bytes(canon(reg)); requests = []
    for path, value in jsons(args.dispatch_root, "EXPERIMENT_REQUEST_v1"):
        relative_path = rel(root, path); requests.append({"request_id": value["request_id"], "candidate_id": value["candidate_id"], "path": relative_path, "sha256": sha(value), "raw_url": f"https://raw.githubusercontent.com/{args.repository}/{args.branch}/{relative_path}"})
    manifest = {"contract": "EXPERIMENT_DISPATCH_MANIFEST_v1", "generated_at_utc": now, "source_repository": args.repository, "source_branch": args.branch, "request_count": len(requests), "requests": sorted(requests, key=lambda item: item["request_id"]), "authority": "SHADOW_ONLY_CROSS_REPO_DISPATCH"}; args.manifest_output.parent.mkdir(parents=True, exist_ok=True); args.manifest_output.write_bytes(canon(manifest)); print(json.dumps({"candidate_count": reg["candidate_count"], "new_candidate_count": len(new_ids), "new_forecasts": new_forecasts, "dispatch_created": dispatch, "rejected": rejected}, sort_keys=True))


if __name__ == "__main__": main()
