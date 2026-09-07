#!/usr/bin/env python3
"""Bounded adaptive cadence gate for Native OTA.

The gate reads only existing GitHub-owned artifacts. It may adapt research-attention
weights and decide whether the single weekly adaptive candidate should become a
FULL Native OTA readback. It has no authority to change market rules, thresholds,
canonical state, portfolio execution, experiment promotion, or market-model weights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import native_ota_readback as ota

UTC = timezone.utc
CONTRACT = "NATIVE_OTA_ADAPTIVE_GATE_v1"
POLICY_PATH = Path("research/ota_native/ADAPTIVE_OTA_POLICY_v1.json")
STATE_PATH = Path("04_MARKET_LEARNING/ota_native/adaptive/STATE.json")


def utcnow() -> datetime:
    return datetime.now(UTC)


def parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def safe_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text())
        return payload if isinstance(payload, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def safe_float(value: Any) -> float | None:
    try:
        out = float(value)
        return out if math.isfinite(out) else None
    except (TypeError, ValueError):
        return None


def digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def load_policy(root: Path) -> dict[str, Any]:
    policy = safe_json(root / POLICY_PATH)
    if not policy or policy.get("contract") != "NATIVE_OTA_ADAPTIVE_POLICY_v1":
        raise RuntimeError("adaptive OTA policy missing or invalid")
    guards = policy.get("immutable_guards") or {}
    required_false = (
        "canonical_state_change", "market_rule_change", "threshold_change",
        "portfolio_execution", "experiment_promotion",
        "automatic_weight_change_to_market_model", "new_market_source_calls",
    )
    if any(guards.get(key) is not False for key in required_false):
        raise RuntimeError("adaptive OTA immutable guard breach")
    if policy.get("source_policy") != "READ_EXISTING_GITHUB_OWNERS_ONLY_NO_NEW_MARKET_SOURCE_CALLS":
        raise RuntimeError("adaptive OTA source policy breach")
    return policy


def latest_breadth(root: Path) -> float | None:
    payload = safe_json(root / "03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
    if not payload:
        return None
    aggregate = payload.get("aggregate") if isinstance(payload.get("aggregate"), dict) else payload
    value = safe_float(aggregate.get("advance_ratio"))
    if value is None:
        pct = safe_float(aggregate.get("advancer_pct"))
        value = None if pct is None else pct / 100.0
    return value


def research_primary_action(root: Path) -> str | None:
    payload = safe_json(root / "00_ARCHIVE_CONTROL/research_governance_v1/meta_orchestrator_v1/STATE.json")
    if not payload:
        return None
    value = payload.get("primary_action")
    return str(value) if value else None


def full_reports_this_iso_week(root: Path, now: datetime) -> tuple[int, datetime | None]:
    report_root = root / "04_MARKET_LEARNING/ota_native"
    iso_year, iso_week, _ = now.isocalendar()
    count = 0
    latest: datetime | None = None
    for path in report_root.glob("*/*/*/*_NATIVE_OTA_READBACK.json"):
        payload = safe_json(path)
        if not payload or payload.get("mode") == "TRIGGER_ONLY":
            continue
        ts = parse_dt(payload.get("generated_at_utc"))
        if ts is None:
            continue
        y, w, _ = ts.isocalendar()
        if (y, w) != (iso_year, iso_week):
            continue
        count += 1
        if latest is None or ts > latest:
            latest = ts
    return count, latest


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def evaluate(root: Path, now: datetime | None = None) -> dict[str, Any]:
    now = now or utcnow()
    policy = load_policy(root)
    cfg = policy["adaptive_gate"]
    previous = safe_json(root / STATE_PATH) or {}

    preview, early = ota.build_report(root, "ADAPTIVE_GATE_PREVIEW", False)
    counts = preview.get("classification_counts") or {}
    new_information = int(counts.get("NEW_INFORMATION") or 0)
    evidential = int(counts.get("EVIDENTIAL") or 0)
    gaps = len((preview.get("gap_accounting") or {}).get("framework_data_gaps") or [])

    breadth = latest_breadth(root)
    previous_breadth = safe_float(previous.get("latest_breadth_advance_ratio"))
    breadth_reference = float(cfg["breadth_support_reference_read_only"])
    breadth_delta_limit = float(cfg["breadth_material_delta_abs"])
    breadth_regime_change = bool(
        breadth is not None and previous_breadth is not None
        and ((breadth >= breadth_reference) != (previous_breadth >= breadth_reference))
    )
    breadth_material_delta = bool(
        breadth is not None and previous_breadth is not None
        and abs(breadth - previous_breadth) >= breadth_delta_limit
    )

    primary_action = research_primary_action(root)
    prior_action = previous.get("research_primary_action")
    research_novelty = bool(primary_action and prior_action and primary_action != prior_action)

    active = {
        "settled_transition": bool(early),
        "classified_new_information": new_information > 0,
        "classified_evidential": evidential > 0,
        "breadth_regime_change": breadth_regime_change,
        "breadth_material_delta": breadth_material_delta,
        "research_novelty": research_novelty,
        "framework_data_gap": gaps > 0,
    }

    initial = {k: float(v) for k, v in cfg["initial_attention_weights"].items()}
    prior_weights = previous.get("attention_weights") if isinstance(previous.get("attention_weights"), dict) else {}
    weights = {k: safe_float(prior_weights.get(k)) or initial[k] for k in initial}

    strengths = {
        "settled_transition": 2.5,
        "classified_new_information": min(new_information, 2) * 1.0,
        "classified_evidential": min(evidential, 2) * 0.75,
        "breadth_regime_change": 1.5,
        "breadth_material_delta": 1.0,
        "research_novelty": 1.0,
        "framework_data_gap": 0.5,
    }
    contributions = {
        key: (strengths[key] * weights[key] if active[key] else 0.0)
        for key in active
    }
    score = sum(contributions.values())

    signature = sorted(key for key, enabled in active.items() if enabled)
    prior_signature = previous.get("active_signal_signature") or []
    repeated = bool(signature and signature == prior_signature)
    bounds = [float(x) for x in cfg["attention_weight_bounds"]]
    step = float(cfg["repeated_signal_step"] if repeated else cfg["novel_signal_step"])
    next_weights = dict(weights)
    for key in signature:
        next_weights[key] = clamp(weights[key] + step, bounds[0], bounds[1])

    full_count, latest_full = full_reports_this_iso_week(root, now)
    max_full = int(policy["cadence"]["max_full_runs_per_iso_week"])
    min_hours = float(policy["cadence"]["minimum_hours_between_full_runs"])
    hours_since_full = None if latest_full is None else (now - latest_full).total_seconds() / 3600.0
    cap_blocked = full_count >= max_full
    cooldown_blocked = hours_since_full is not None and hours_since_full < min_hours
    threshold = float(cfg["run_score_threshold"])
    run_full = bool(score >= threshold and not cap_blocked and not cooldown_blocked)

    reasons = [key for key in signature]
    blockers = []
    if score < threshold:
        blockers.append("ADAPTIVE_SCORE_BELOW_THRESHOLD")
    if cap_blocked:
        blockers.append("WEEKLY_FULL_RUN_CAP_REACHED")
    if cooldown_blocked:
        blockers.append("MINIMUM_FULL_RUN_COOLDOWN_ACTIVE")

    result: dict[str, Any] = {
        "contract": CONTRACT,
        "schema_version": 1,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "source_policy": policy["source_policy"],
        "authority": dict(policy["immutable_guards"]),
        "decision": "RUN_ADAPTIVE_FULL_OTA" if run_full else "NO_ADAPTIVE_FULL_OTA",
        "run_full_ota": run_full,
        "adaptive_score": round(score, 6),
        "adaptive_score_threshold": threshold,
        "active_signal_signature": signature,
        "signal_contributions": {k: round(v, 6) for k, v in contributions.items()},
        "attention_weights_used": {k: round(v, 6) for k, v in weights.items()},
        "attention_weights_next": {k: round(v, 6) for k, v in next_weights.items()},
        "learning_update": "DAMP_REPEATED_SIGNATURE" if repeated else "BOOST_NOVEL_ACTIVE_SIGNALS",
        "self_development_scope": policy["self_development_scope"],
        "reasons": reasons,
        "blockers": blockers,
        "latest_breadth_advance_ratio": breadth,
        "previous_adaptive_breadth_advance_ratio": previous_breadth,
        "classified_delta_counts": {
            "NEW_INFORMATION": new_information,
            "EVIDENTIAL": evidential,
            "CONTEXT_ONLY": int(counts.get("CONTEXT_ONLY") or 0),
        },
        "framework_data_gap_count": gaps,
        "research_primary_action": primary_action,
        "full_ota_runs_this_iso_week_before_decision": full_count,
        "latest_full_ota_utc": None if latest_full is None else latest_full.isoformat().replace("+00:00", "Z"),
        "hours_since_latest_full_ota": None if hours_since_full is None else round(hours_since_full, 3),
        "market_semantics_changed": False,
        "thresholds_changed": False,
        "portfolio_rules_changed": False,
        "canonical_effect": False
    }
    result["decision_hash_sha256"] = digest(result)
    return result


def persist(root: Path, result: dict[str, Any]) -> Path:
    generated = parse_dt(result["generated_at_utc"]) or utcnow()
    base = root / "04_MARKET_LEARNING/ota_native/adaptive"
    run_dir = base / generated.strftime("%Y/%m/%d")
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / (generated.strftime("%H%M%S") + "_ADAPTIVE_GATE.json")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    state = dict(result)
    state["attention_weights"] = state.pop("attention_weights_next")
    state.pop("attention_weights_used", None)
    state["state_hash_sha256"] = digest(state)
    (root / STATE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / STATE_PATH).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-status")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    result = evaluate(root)
    path = persist(root, result)
    status = {
        "contract": "NATIVE_OTA_ADAPTIVE_EXECUTION_STATUS_v1",
        "run_full_ota": result["run_full_ota"],
        "decision": result["decision"],
        "adaptive_score": result["adaptive_score"],
        "decision_hash_sha256": result["decision_hash_sha256"],
        "output_path": str(path.relative_to(root)),
        "state_path": str(STATE_PATH),
    }
    if args.output_status:
        out = root / args.output_status
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print(json.dumps(status, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
