#!/usr/bin/env python3
"""Build a concise non-binding Handlekompas from GitHub-native market state.

The output is intentionally operational and fail-closed. It never executes trades,
changes thresholds, or promotes proxy evidence to canonical status.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "NATIVE_HANDLEKOMPAS_v1"
POINTER = "NATIVE_HANDLEKOMPAS_LATEST_POINTER_v1"
DEFAULT_AUTO_STATE_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
DEFAULT_ROOT = Path("04_MARKET_LEARNING/handlekompas")

AUTHORITY = {
    "binding": False,
    "portfolio_execution": False,
    "canonical_state_change": False,
    "market_threshold_change": False,
    "model_weight_change": False,
    "purpose": "CONCISE_NATIVE_MARKET_STATE_READBACK",
}


def _canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def _classify_provider_health(auto_state: Mapping[str, Any]) -> dict[str, Any]:
    health = auto_state.get("source_health") or {}
    provider_rows: list[dict[str, Any]] = []
    for lane, lane_health in sorted(health.items()):
        if not isinstance(lane_health, Mapping):
            continue
        status = str(lane_health.get("status") or "UNKNOWN")
        classification = str(lane_health.get("classification") or "UNKNOWN")
        text = f"{classification} {lane_health.get('detail','')}".upper()
        provider_issue = None
        if any(token in text for token in ("QUOTA", "RATE_LIMIT", "429", "USAGE_LIMIT")):
            provider_issue = "QUOTA_OR_RATE_LIMIT"
        elif any(token in text for token in ("TOKEN", "CREDIT", "BUDGET", "INSUFFICIENT_FUNDS")):
            provider_issue = "TOKEN_OR_BUDGET_EXHAUSTION"
        elif any(token in text for token in ("AUTH", "UNAUTHORIZED", "FORBIDDEN", "401", "403", "API_KEY")):
            provider_issue = "AUTHENTICATION_OR_PERMISSION"
        elif status not in {"PASS", "AVAILABLE"}:
            provider_issue = "SOURCE_OR_RUNTIME_DEGRADATION"
        if provider_issue:
            provider_rows.append({
                "lane": lane,
                "status": status,
                "classification": classification,
                "issue_class": provider_issue,
            })

    cfgi = next((row for row in provider_rows if row["lane"] == "sentiment"), None)
    return {
        "status": "DEGRADED" if provider_rows else "PASS",
        "cfgi": cfgi or {"status": "PASS_OR_NOT_EXPLICITLY_DEGRADED", "issue_class": None},
        "issues": provider_rows,
    }


def _budget_health(auto_state: Mapping[str, Any]) -> dict[str, Any]:
    # Exact account spend is intentionally not invented. This contract exposes
    # provider exhaustion signals when observable and otherwise says UNKNOWN.
    provider = _classify_provider_health(auto_state)
    exhaustion = [row for row in provider["issues"] if row["issue_class"] in {"QUOTA_OR_RATE_LIMIT", "TOKEN_OR_BUDGET_EXHAUSTION"}]
    if exhaustion:
        return {
            "status": "DEGRADED",
            "exact_monthly_spend_available": False,
            "exact_remaining_budget_available": False,
            "reason": "OBSERVED_PROVIDER_QUOTA_TOKEN_OR_BUDGET_SIGNAL",
            "provider_signals": exhaustion,
        }
    return {
        "status": "UNKNOWN_EXACT_SPEND_NO_EXHAUSTION_SIGNAL",
        "exact_monthly_spend_available": False,
        "exact_remaining_budget_available": False,
        "reason": "NO_ACCOUNT_LEVEL_COST_LEDGER_BOUND_TO_THIS_PACKET",
        "provider_signals": [],
    }


def _build_action(auto_state: Mapping[str, Any]) -> dict[str, Any]:
    ns = auto_state.get("normalized_state") or {}
    breadth = _nested(ns, "breadth", "aggregate") or {}
    live = ns.get("live_market") or {}
    health = auto_state.get("source_health") or {}

    ratio = live.get("ethbtc")
    breadth_ratio = breadth.get("advance_ratio")
    ethbtc_positive = isinstance(ratio, (int, float)) and ratio > 0.03
    breadth_supportive = isinstance(breadth_ratio, (int, float)) and breadth_ratio >= 0.50
    breadth_weak = isinstance(breadth_ratio, (int, float)) and breadth_ratio < 0.40

    decision_status = auto_state.get("decision_context_status")
    blockers = list(auto_state.get("blockers") or [])
    no_blockers = decision_status == "PASS" and not blockers

    if no_blockers and ethbtc_positive and breadth_supportive:
        now = "PREPARE"
    elif breadth_weak:
        now = "HOLD_DEFENSIVE_WAIT"
    else:
        now = "HOLD_WAIT"

    prepare = "ETHBTC_STRENGTH_PLUS_BREADTH_GTE_0_50_AND_HEALTHY_NATIVE_STATE"
    topup_gate = "REQUIRES_EXISTING_ENTRY_SIGNAL_OR_CANONICAL_REGISTERED_CONFIRMATION; HANDLEKOMPAS_NEVER_SELF_PROMOTES_PROXY_BREADTH"
    risk_down = "BREADTH_LT_0_40_OR_ETHBTC_WEAKENING_OR_NATIVE_HEALTH_DEGRADES_MATERIALLY"

    why = []
    if isinstance(ratio, (int, float)):
        why.append(f"ETHBTC={ratio:.6f}")
    if isinstance(breadth_ratio, (int, float)):
        why.append(f"TOP100_BREADTH={breadth_ratio:.2f}")
    if blockers:
        why.append("BLOCKERS=" + ",".join(blockers))
    degraded = [lane for lane, row in health.items() if isinstance(row, Mapping) and row.get("status") != "PASS"]
    if degraded:
        why.append("DEGRADED_LANES=" + ",".join(sorted(degraded)))

    return {
        "NOW": now,
        "PREPARE": prepare,
        "TOPUP_GATE": topup_gate,
        "RISK_DOWN": risk_down,
        "WHY": why,
    }


def build(auto_state: Mapping[str, Any]) -> dict[str, Any]:
    generated = datetime.now(timezone.utc).replace(microsecond=0)
    provider = _classify_provider_health(auto_state)
    budget = _budget_health(auto_state)
    packet = {
        "contract": CONTRACT,
        "generated_at_utc": generated.isoformat().replace("+00:00", "Z"),
        "source": {
            "contract": auto_state.get("contract"),
            "packet_generated_at_utc": auto_state.get("packet_generated_at_utc"),
            "packet_sha256": auto_state.get("packet_sha256"),
            "source_snapshot_commit_sha": _nested(auto_state, "source_snapshot", "exact_commit_sha"),
            "validation_status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
        },
        "action": _build_action(auto_state),
        "DATA_HEALTH": {
            "status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
            "blockers": list(auto_state.get("blockers") or []),
            "optional_degraded_lanes": list(auto_state.get("optional_degraded_lanes") or []),
            "provider_health": provider,
        },
        "BUDGET_HEALTH": budget,
        "authority": AUTHORITY,
    }
    packet["handlekompas_sha256"] = _sha(_canon({k: v for k, v in packet.items() if k != "handlekompas_sha256"}))
    return packet


def write(packet: Mapping[str, Any], root: Path) -> dict[str, Any]:
    generated = datetime.fromisoformat(str(packet["generated_at_utc"]).replace("Z", "+00:00"))
    run_root = root / "runs" / generated.strftime("%Y/%m/%d")
    run_root.mkdir(parents=True, exist_ok=True)
    path = run_root / f"{generated:%H%M%S}_{packet['handlekompas_sha256'][:12]}.json"
    path.write_bytes(_canon(packet))
    pointer = {
        "contract": POINTER,
        "handlekompas_path": path.as_posix(),
        "handlekompas_sha256": packet["handlekompas_sha256"],
        "generated_at_utc": packet["generated_at_utc"],
        "source_packet_sha256": _nested(packet, "source", "packet_sha256"),
        "NOW": _nested(packet, "action", "NOW"),
        "data_health": _nested(packet, "DATA_HEALTH", "status"),
        "budget_health": _nested(packet, "BUDGET_HEALTH", "status"),
        "authority": AUTHORITY,
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "LATEST.json").write_bytes(_canon(pointer))
    return {"path": path.as_posix(), "pointer": (root / "LATEST.json").as_posix(), "sha256": packet["handlekompas_sha256"]}


def load_auto_state(repo_root: Path, pointer_path: Path) -> Mapping[str, Any]:
    pointer = _read_json(repo_root / pointer_path)
    packet_path = pointer.get("packet_path")
    if not isinstance(packet_path, str) or not packet_path:
        raise ValueError("AUTO_MARKET_STATE_POINTER_MISSING_PACKET_PATH")
    packet = _read_json(repo_root / packet_path)
    expected = pointer.get("packet_sha256")
    actual = packet.get("packet_sha256")
    if not expected or expected != actual:
        raise ValueError("AUTO_MARKET_STATE_POINTER_HASH_MISMATCH")
    return packet


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--auto-state-pointer", type=Path, default=DEFAULT_AUTO_STATE_POINTER)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    auto_state = load_auto_state(args.repo_root, args.auto_state_pointer)
    packet = build(auto_state)
    output = packet if args.no_write else {**write(packet, args.output_root), "NOW": packet["action"]["NOW"], "DATA_HEALTH": packet["DATA_HEALTH"]["status"], "BUDGET_HEALTH": packet["BUDGET_HEALTH"]["status"]}
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
