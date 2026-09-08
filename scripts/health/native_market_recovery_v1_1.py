#!/usr/bin/env python3
"""Native market recovery v1.1: bounded self-repair with repo-relative durable pointers."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "NATIVE_MARKET_RECOVERY_DECISION_v1_1"
STATE_CONTRACT = "NATIVE_MARKET_RECOVERY_STATE_v1_1"
DEFAULT_AUTO_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
DEFAULT_STATE = Path("09_SOURCE_QA/native_market_recovery/STATE.json")
DEFAULT_DECISION_ROOT = Path("09_SOURCE_QA/native_market_recovery/decisions")

POLICY = {
    "hourly_market": {"workflow": "hourly-sequence-capture.yml", "streak": 2, "cooldown_hours": 2},
    "live_anchor": {"workflow": "daily-raw-owner-capture.yml", "streak": 2, "cooldown_hours": 4},
    "breadth": {"workflow": "daily-raw-owner-capture.yml", "streak": 2, "cooldown_hours": 4},
    "stablecoin_liquidity": {"workflow": "daily-stablecoin-liquidity.yml", "streak": 2, "cooldown_hours": 12},
    "sentiment": {"workflow": "daily-raw-owner-capture.yml", "streak": 2, "cooldown_hours": 4},
}
SUPPRESS_RETRY_TOKENS = (
    "QUOTA", "RATE_LIMIT", "USAGE_LIMIT", "TOKEN", "CREDIT", "BUDGET", "INSUFFICIENT_FUNDS",
    "AUTH", "UNAUTHORIZED", "FORBIDDEN", "API_KEY", "401", "403", "429",
)


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.utcoffset() is not None else None


def default_state() -> dict[str, Any]:
    return {"contract": STATE_CONTRACT, "lanes": {}, "authority": {"portfolio_action": False, "market_threshold_change": False}}


def load_auto(repo_root: Path, pointer_path: Path) -> Mapping[str, Any]:
    pointer = json.loads((repo_root / pointer_path).read_text())
    packet_path = pointer.get("packet_path")
    if not isinstance(packet_path, str) or not packet_path:
        raise ValueError("AUTO_MARKET_STATE_POINTER_MISSING_PACKET_PATH")
    packet = json.loads((repo_root / packet_path).read_text())
    if pointer.get("packet_sha256") != packet.get("packet_sha256"):
        raise ValueError("AUTO_MARKET_STATE_POINTER_HASH_MISMATCH")
    return packet


def provider_limited(row: Mapping[str, Any]) -> bool:
    text = f"{row.get('classification','')} {row.get('detail','')}".upper()
    return any(token in text for token in SUPPRESS_RETRY_TOKENS)


def decide(auto: Mapping[str, Any], prior: Mapping[str, Any], now: datetime) -> tuple[dict[str, Any], dict[str, Any]]:
    health = auto.get("source_health") or {}
    prior_lanes = prior.get("lanes") or {}
    state = default_state()
    actions: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []

    for lane, rule in POLICY.items():
        row = health.get(lane) if isinstance(health, Mapping) else None
        row = row if isinstance(row, Mapping) else {"status": "UNAVAILABLE", "classification": "HEALTH_ROW_MISSING"}
        status = str(row.get("status") or "UNKNOWN")
        previous = prior_lanes.get(lane) if isinstance(prior_lanes, Mapping) else None
        previous = previous if isinstance(previous, Mapping) else {}
        streak = 0 if status == "PASS" else int(previous.get("consecutive_nonpass", 0)) + 1
        last_dispatch = parse_utc(previous.get("last_dispatch_utc"))
        cooldown_ok = last_dispatch is None or now - last_dispatch >= timedelta(hours=int(rule["cooldown_hours"]))
        limited = status != "PASS" and provider_limited(row)
        dispatch = status != "PASS" and streak >= int(rule["streak"]) and cooldown_ok and not limited

        if limited:
            suppressed.append({"lane": lane, "reason": "PROVIDER_OR_BUDGET_LIMIT_RETRY_SUPPRESSED", "classification": row.get("classification")})
        if dispatch:
            actions.append({
                "lane": lane,
                "workflow": rule["workflow"],
                "reason": "REPEATED_OPERATIONAL_DEGRADATION",
                "consecutive_nonpass": streak,
                "cooldown_hours": rule["cooldown_hours"],
            })

        state["lanes"][lane] = {
            "status": status,
            "classification": row.get("classification"),
            "consecutive_nonpass": streak,
            "last_dispatch_utc": now.isoformat().replace("+00:00", "Z") if dispatch else previous.get("last_dispatch_utc"),
            "retry_suppressed_provider_limit": limited,
        }

    unique: dict[str, dict[str, Any]] = {}
    for action in actions:
        workflow = action["workflow"]
        if workflow not in unique:
            unique[workflow] = {**action, "lanes": [action["lane"]]}
        else:
            unique[workflow]["lanes"].append(action["lane"])
            unique[workflow]["consecutive_nonpass"] = max(unique[workflow]["consecutive_nonpass"], action["consecutive_nonpass"])

    decision = {
        "contract": CONTRACT,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "source_auto_market_state_sha256": auto.get("packet_sha256"),
        "source_snapshot_commit_sha": (auto.get("source_snapshot") or {}).get("exact_commit_sha") if isinstance(auto.get("source_snapshot"), Mapping) else None,
        "dispatches": list(unique.values()),
        "suppressed_retries": suppressed,
        "manual_market_data_required": False,
        "authority": {"portfolio_action": False, "market_threshold_change": False, "owner_switch": False, "historical_rewrite": False},
    }
    decision["decision_sha256"] = digest(canon({k: v for k, v in decision.items() if k != "decision_sha256"}))
    state["updated_at_utc"] = decision["generated_at_utc"]
    state["last_decision_sha256"] = decision["decision_sha256"]
    return decision, state


def write(repo_root: Path, decision: Mapping[str, Any], state: Mapping[str, Any], state_path: Path, decision_root: Path) -> dict[str, str]:
    state_abs = repo_root / state_path
    state_abs.parent.mkdir(parents=True, exist_ok=True)
    state_abs.write_bytes(canon(state))
    dt = parse_utc(decision["generated_at_utc"])
    assert dt is not None
    rel_path = decision_root / dt.strftime("%Y/%m/%d") / f"{dt:%H%M%S}_{decision['decision_sha256'][:12]}.json"
    abs_path = repo_root / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(canon(decision))
    latest_rel = decision_root.parent / "LATEST.json"
    latest_abs = repo_root / latest_rel
    latest_abs.write_bytes(canon({
        "contract": "NATIVE_MARKET_RECOVERY_LATEST_POINTER_v1_1",
        "decision_path": rel_path.as_posix(),
        "decision_sha256": decision["decision_sha256"],
        "generated_at_utc": decision["generated_at_utc"],
        "dispatch_count": len(decision["dispatches"]),
        "suppressed_retry_count": len(decision["suppressed_retries"]),
        "manual_market_data_required": False,
    }))
    return {"decision_path": rel_path.as_posix(), "latest_path": latest_rel.as_posix(), "state_path": state_path.as_posix()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--auto-pointer", type=Path, default=DEFAULT_AUTO_POINTER)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--decision-root", type=Path, default=DEFAULT_DECISION_ROOT)
    parser.add_argument("--now-utc")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    now = parse_utc(args.now_utc) if args.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None:
        raise ValueError("INVALID_NOW_UTC")
    auto = load_auto(args.repo_root, args.auto_pointer)
    state_abs = args.repo_root / args.state
    prior = json.loads(state_abs.read_text()) if state_abs.exists() else default_state()
    decision, state = decide(auto, prior, now)
    paths = {} if args.no_write else write(args.repo_root, decision, state, args.state, args.decision_root)
    print(json.dumps({**decision, **paths}, sort_keys=True))


if __name__ == "__main__":
    main()
