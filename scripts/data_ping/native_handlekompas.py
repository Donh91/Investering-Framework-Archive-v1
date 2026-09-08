#!/usr/bin/env python3
"""Native, source-call-free Handlekompas built from pinned Auto Market State.

This is a concise non-binding readback layer. It cannot execute trades, mutate
thresholds, promote proxy evidence, switch owners, or rewrite canonical state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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
    "owner_switch": False,
    "purpose": "CONCISE_NATIVE_MARKET_STATE_READBACK",
}

LIMIT_TOKENS = ("QUOTA", "RATE_LIMIT", "USAGE_LIMIT", "429")
BUDGET_TOKENS = ("TOKEN", "CREDIT", "BUDGET", "INSUFFICIENT_FUNDS")
AUTH_TOKENS = ("AUTH", "UNAUTHORIZED", "FORBIDDEN", "401", "403", "API_KEY")


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value: bytes) -> str:
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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_auto_state(repo_root: Path, pointer_path: Path) -> Mapping[str, Any]:
    pointer = read_json(repo_root / pointer_path)
    packet_path = pointer.get("packet_path")
    if not isinstance(packet_path, str) or not packet_path:
        raise ValueError("AUTO_MARKET_STATE_POINTER_MISSING_PACKET_PATH")
    packet = read_json(repo_root / packet_path)
    if pointer.get("packet_sha256") != packet.get("packet_sha256"):
        raise ValueError("AUTO_MARKET_STATE_POINTER_HASH_MISMATCH")
    return packet


def classify_provider_health(auto_state: Mapping[str, Any]) -> dict[str, Any]:
    health = auto_state.get("source_health") or {}
    issues: list[dict[str, Any]] = []
    for lane, row in sorted(health.items() if isinstance(health, Mapping) else []):
        if not isinstance(row, Mapping):
            continue
        status = str(row.get("status") or "UNKNOWN")
        if status == "PASS":
            continue
        classification = str(row.get("classification") or "UNKNOWN")
        text = f"{classification} {row.get('detail','')}".upper()
        if any(token in text for token in LIMIT_TOKENS):
            issue_class = "QUOTA_OR_RATE_LIMIT"
        elif any(token in text for token in BUDGET_TOKENS):
            issue_class = "TOKEN_OR_BUDGET_EXHAUSTION"
        elif any(token in text for token in AUTH_TOKENS):
            issue_class = "AUTHENTICATION_OR_PERMISSION"
        else:
            issue_class = "SOURCE_OR_RUNTIME_DEGRADATION"
        issues.append({"lane": lane, "status": status, "classification": classification, "issue_class": issue_class})
    cfgi = next((row for row in issues if row["lane"] == "sentiment"), None)
    return {
        "status": "DEGRADED" if issues else "PASS",
        "cfgi": cfgi or {"status": "PASS_OR_NOT_EXPLICITLY_DEGRADED", "issue_class": None},
        "issues": issues,
    }


def budget_health(auto_state: Mapping[str, Any], external_budget: Mapping[str, Any] | None = None) -> dict[str, Any]:
    provider = classify_provider_health(auto_state)
    exhaustion = [row for row in provider["issues"] if row["issue_class"] in {"QUOTA_OR_RATE_LIMIT", "TOKEN_OR_BUDGET_EXHAUSTION"}]
    if isinstance(external_budget, Mapping):
        status = external_budget.get("status") or external_budget.get("budget_status")
        remaining = external_budget.get("remaining_monthly_budget")
        spent = external_budget.get("month_to_date_spend")
        if status or remaining is not None or spent is not None:
            return {
                "status": str(status or "AVAILABLE"),
                "exact_monthly_spend_available": spent is not None,
                "exact_remaining_budget_available": remaining is not None,
                "month_to_date_spend": spent,
                "remaining_monthly_budget": remaining,
                "source": "BOUND_EXTERNAL_BUDGET_STATUS",
                "provider_signals": exhaustion,
            }
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


def action_context(auto_state: Mapping[str, Any]) -> dict[str, Any]:
    ns = auto_state.get("normalized_state") or {}
    live = ns.get("live_market") or {}
    breadth = nested(ns, "breadth", "aggregate") or {}
    entry = ns.get("entry_signal_reference") or {}
    ratio = finite(live.get("ethbtc"))
    advance = finite(breadth.get("advance_ratio"))
    blockers = list(auto_state.get("blockers") or [])
    validation = str(auto_state.get("validation_status") or "UNKNOWN")
    decision_health = str(auto_state.get("decision_context_status") or "UNKNOWN")
    entry_state = entry.get("state") if isinstance(entry, Mapping) else None

    healthy = validation != "FAIL" and decision_health == "PASS" and not blockers
    if healthy and entry_state == "GRADUATED_ALTCOIN_TOPUP_ACTIVE":
        now = "GRADUATED_TOPUP_ACTIVE"
    elif advance is not None and advance < 0.40:
        now = "HOLD_DEFENSIVE_WAIT"
    elif not healthy:
        now = "HOLD_WAIT_DATA_DEGRADED"
    elif ratio is not None and ratio > 0.03 and advance is not None and advance >= 0.50:
        now = "PREPARE"
    else:
        now = "HOLD_WAIT"

    why: list[str] = []
    if ratio is not None:
        why.append(f"ETHBTC={ratio:.6f}")
    if advance is not None:
        why.append(f"TOP100_BREADTH={advance:.2f}")
    if entry_state:
        why.append(f"ENTRY_SIGNAL={entry_state}")
    if blockers:
        why.append("BLOCKERS=" + ",".join(blockers))

    return {
        "NOW": now,
        "PREPARE": "ETHBTC_STRENGTH_PLUS_BREADTH_GTE_0_50_PLUS_HEALTHY_NATIVE_STATE",
        "TOPUP_GATE": "ONLY_EXISTING_ENTRY_SIGNAL_OR_REGISTERED_CANONICAL_CONFIRMATION_CAN_ACTIVATE_TOPUP; PROXY_BREADTH_NEVER_SELF_PROMOTES",
        "RISK_DOWN": "BREADTH_LT_0_40_OR_ETHBTC_WEAKENS_OR_NATIVE_HEALTH_DEGRADES_MATERIALLY",
        "WHY": why,
    }


def build(auto_state: Mapping[str, Any], *, external_budget: Mapping[str, Any] | None = None, now: datetime | None = None) -> dict[str, Any]:
    generated = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    provider = classify_provider_health(auto_state)
    packet = {
        "contract": CONTRACT,
        "generated_at_utc": generated.isoformat().replace("+00:00", "Z"),
        "source": {
            "contract": auto_state.get("contract"),
            "packet_generated_at_utc": auto_state.get("packet_generated_at_utc"),
            "packet_sha256": auto_state.get("packet_sha256"),
            "source_snapshot_commit_sha": nested(auto_state, "source_snapshot", "exact_commit_sha"),
            "validation_status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
        },
        "action": action_context(auto_state),
        "DATA_HEALTH": {
            "status": auto_state.get("validation_status"),
            "decision_context_status": auto_state.get("decision_context_status"),
            "blockers": list(auto_state.get("blockers") or []),
            "optional_degraded_lanes": list(auto_state.get("optional_degraded_lanes") or []),
            "provider_health": provider,
        },
        "BUDGET_HEALTH": budget_health(auto_state, external_budget),
        "manual_market_data_required": False,
        "authority": AUTHORITY,
    }
    packet["handlekompas_sha256"] = digest(canon({k: v for k, v in packet.items() if k != "handlekompas_sha256"}))
    return packet


def write(packet: Mapping[str, Any], output_root: Path) -> dict[str, Any]:
    dt = datetime.fromisoformat(str(packet["generated_at_utc"]).replace("Z", "+00:00"))
    path = output_root / "runs" / dt.strftime("%Y/%m/%d") / f"{dt:%H%M%S}_{packet['handlekompas_sha256'][:12]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canon(packet))
    output_root.mkdir(parents=True, exist_ok=True)
    pointer = {
        "contract": POINTER,
        "handlekompas_path": path.as_posix(),
        "handlekompas_sha256": packet["handlekompas_sha256"],
        "generated_at_utc": packet["generated_at_utc"],
        "source_packet_sha256": nested(packet, "source", "packet_sha256"),
        "NOW": nested(packet, "action", "NOW"),
        "data_health": nested(packet, "DATA_HEALTH", "status"),
        "budget_health": nested(packet, "BUDGET_HEALTH", "status"),
        "manual_market_data_required": False,
        "authority": AUTHORITY,
    }
    (output_root / "LATEST.json").write_bytes(canon(pointer))
    return {"path": path.as_posix(), "pointer": (output_root / "LATEST.json").as_posix(), "sha256": packet["handlekompas_sha256"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--auto-state-pointer", type=Path, default=DEFAULT_AUTO_STATE_POINTER)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--budget-status", type=Path)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    auto_state = load_auto_state(args.repo_root, args.auto_state_pointer)
    external_budget = None
    if args.budget_status:
        p = args.repo_root / args.budget_status
        if p.exists():
            external_budget = read_json(p)
    packet = build(auto_state, external_budget=external_budget)
    result = packet if args.no_write else {**write(packet, args.output_root), "NOW": packet["action"]["NOW"], "DATA_HEALTH": packet["DATA_HEALTH"]["status"], "BUDGET_HEALTH": packet["BUDGET_HEALTH"]["status"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
