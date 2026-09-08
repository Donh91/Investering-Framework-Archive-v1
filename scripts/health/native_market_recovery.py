#!/usr/bin/env python3
"""Plan bounded self-repair for repeated GitHub-native market owner degradation."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "NATIVE_MARKET_RECOVERY_DECISION_v1"
STATE_CONTRACT = "NATIVE_MARKET_RECOVERY_STATE_v1"
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


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.utcoffset() is not None else None


def load_auto(repo: Path, pointer_path: Path) -> Mapping[str, Any]:
    pointer = json.loads((repo / pointer_path).read_text())
    packet_path = pointer.get("packet_path")
    if not isinstance(packet_path, str) or not packet_path:
        raise ValueError("AUTO_MARKET_STATE_POINTER_MISSING_PACKET_PATH")
    packet = json.loads((repo / packet_path).read_text())
    if pointer.get("packet_sha256") != packet.get("packet_sha256"):
        raise ValueError("AUTO_MARKET_STATE_POINTER_HASH_MISMATCH")
    return packet


def default_state() -> dict[str, Any]:
    return {"contract": STATE_CONTRACT, "lanes": {}, "authority": {"portfolio_action": False, "market_threshold_change": False}}


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
        last_dispatch = parse(previous.get("last_dispatch_utc"))
        cooldown = timedelta(hours=int(rule["cooldown_hours"]))
        cooldown_ok = last_dispatch is None or now - last_dispatch >= cooldown
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

    # De-duplicate workflows: one live-anchor run can repair live_anchor+breadth+sentiment.
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
        "authority": {
            "portfolio_action": False,
            "market_threshold_change": False,
            "owner_switch": False,
            "historical_rewrite": False,
        },
    }
    decision["decision_sha256"] = sha(canon({k: v for k, v in decision.items() if k != "decision_sha256"}))
    state["updated_at_utc"] = decision["generated_at_utc"]
    state["last_decision_sha256"] = decision["decision_sha256"]
    return decision, state


def write(decision: Mapping[str, Any], state: Mapping[str, Any], state_path: Path, root: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_bytes(canon(state))
    dt = parse(decision["generated_at_utc"])
    assert dt is not None
    out = root / dt.strftime("%Y/%m/%d")
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{dt:%H%M%S}_{decision['decision_sha256'][:12]}.json"
    path.write_bytes(canon(decision))
    latest = root.parent / "LATEST.json"
    latest.write_bytes(canon({
        "contract": "NATIVE_MARKET_RECOVERY_LATEST_POINTER_v1",
        "decision_path": path.as_posix(),
        "decision_sha256": decision["decision_sha256"],
        "generated_at_utc": decision["generated_at_utc"],
        "dispatch_count": len(decision["dispatches"]),
        "suppressed_retry_count": len(decision["suppressed_retries"]),
        "manual_market_data_required": False,
    }))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--auto-pointer", type=Path, default=DEFAULT_AUTO_POINTER)
    p.add_argument("--state", type=Path, default=DEFAULT_STATE)
    p.add_argument("--decision-root", type=Path, default=DEFAULT_DECISION_ROOT)
    p.add_argument("--now-utc")
    p.add_argument("--no-write", action="store_true")
    args = p.parse_args()
    now = parse(args.now_utc) if args.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None:
        raise ValueError("INVALID_NOW_UTC")
    auto = load_auto(args.repo_root, args.auto_pointer)
    state_path = args.repo_root / args.state
    prior = json.loads(state_path.read_text()) if state_path.exists() else default_state()
    decision, state = decide(auto, prior, now)
    if not args.no_write:
        write(decision, state, state_path, args.repo_root / args.decision_root)
    print(json.dumps(decision, sort_keys=True))


if __name__ == "__main__":
    main()
