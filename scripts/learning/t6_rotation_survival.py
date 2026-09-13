#!/usr/bin/env python3
"""Prospective, non-binding T6 rotation-survival instrumentation.

This module never creates market authority. It only freezes a first ETHBTC cross
against the already-registered read-only level carried by Adaptive Rotation Cadence,
then appends source-bound observations. Missing axes remain explicitly unavailable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "ROTATION_SURVIVAL_FORWARD_v1"
OBS_CONTRACT = "ROTATION_SURVIVAL_OBSERVATION_v1"
STATE_CONTRACT = "ROTATION_SURVIVAL_STATE_v1"
AUTHORITY = {
    "binding": False,
    "market_interpretation": "NONE",
    "canonical_acceptance": False,
    "state_change": False,
    "portfolio_action": False,
    "market_threshold_change": False,
    "model_weight_change": False,
    "research_only": True,
}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.utcoffset() is None:
        raise ValueError("timezone_required")
    return dt.astimezone(timezone.utc)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def scalar(packet: dict[str, Any], key: str) -> Any:
    return ((packet.get("normalized_state") or {}).get("scalar_values") or {}).get(key)


def axis(value: Any, source_field: str) -> dict[str, Any]:
    return {
        "available": value is not None,
        "value": value,
        "source_field": source_field,
        "inferred": False,
    }


def packet_timestamp(packet: dict[str, Any]) -> str:
    for key in ("generated_at_utc", "packet_generated_at_utc", "snapshot_utc"):
        if packet.get(key):
            parse_time(str(packet[key]))
            return str(packet[key])
    raise ValueError("packet_timestamp_required")


def registered_level(cadence: dict[str, Any]) -> float:
    if cadence.get("cadence_contract") != "ADAPTIVE_ROTATION_CADENCE_v1":
        raise ValueError("cadence_contract_required")
    if cadence.get("authority") != "OPERATIONAL_SAMPLING_ONLY_NON_BINDING":
        raise ValueError("cadence_authority_mismatch")
    level = cadence.get("registered_ethbtc_level_read_only")
    if isinstance(level, bool) or not isinstance(level, (int, float)) or level <= 0:
        raise ValueError("registered_level_required")
    return float(level)


def prior_ethbtc(packet: dict[str, Any], current: float) -> float | None:
    row = (packet.get("deltas_since_prior_auto_packet") or {}).get("ethbtc") or {}
    absolute = row.get("absolute")
    if isinstance(absolute, bool) or not isinstance(absolute, (int, float)):
        return None
    return current - float(absolute)


def snapshot_axes(packet: dict[str, Any]) -> dict[str, Any]:
    state = packet.get("normalized_state") or {}
    return {
        "ETHBTC": axis(scalar(packet, "ethbtc"), "normalized_state.scalar_values.ethbtc"),
        "breadth": axis(scalar(packet, "breadth_advance_ratio"), "normalized_state.scalar_values.breadth_advance_ratio"),
        "BTC_D": axis(scalar(packet, "btc_dominance_pct"), "normalized_state.scalar_values.btc_dominance_pct"),
        "deployment": axis((state.get("entry_signal_reference") or {}).get("state"), "normalized_state.entry_signal_reference.state"),
        "flow": axis({"btc_etf_musd": scalar(packet, "btc_etf_musd"), "eth_etf_musd": scalar(packet, "eth_etf_musd")} if scalar(packet, "btc_etf_musd") is not None or scalar(packet, "eth_etf_musd") is not None else None, "normalized_state.scalar_values.{btc_etf_musd,eth_etf_musd}"),
    }


def sequence_id(packet_hash: str, observed_at: str) -> str:
    return "T6-" + hashlib.sha256(f"{packet_hash}|{observed_at}".encode()).hexdigest()[:16]


def write_immutable(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canon(value)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"immutable_conflict:{path}")
        return
    path.write_bytes(data)


def operate(packet: dict[str, Any], cadence: dict[str, Any], root: Path) -> dict[str, Any]:
    if packet.get("contract") != "AUTO_MARKET_STATE_PACKET_v1":
        raise ValueError("auto_market_state_contract_required")
    observed_at = packet_timestamp(packet)
    current = scalar(packet, "ethbtc")
    if isinstance(current, bool) or not isinstance(current, (int, float)):
        raise ValueError("ethbtc_required")
    current = float(current)
    level = registered_level(cadence)
    prior = prior_ethbtc(packet, current)
    packet_hash = sha(packet)
    state_path = root / "STATE.json"
    state = read_json(state_path) if state_path.exists() else {"contract": STATE_CONTRACT, "active_sequence_id": None}
    active = state.get("active_sequence_id")
    crossed = prior is not None and prior < level <= current
    observation: dict[str, Any] = {
        "contract": OBS_CONTRACT,
        "authority": AUTHORITY,
        "observed_at_utc": observed_at,
        "source_packet_sha256": packet_hash,
        "registered_ethbtc_level_read_only": level,
        "current_ethbtc": current,
        "prior_ethbtc": prior,
        "first_cross_detected": crossed,
        "active_sequence_id_before": active,
        "axes": snapshot_axes(packet),
        "missing_axes": [name for name, row in snapshot_axes(packet).items() if not row["available"]],
        "retrospective_creation": False,
    }
    if active is None and crossed:
        active = sequence_id(packet_hash, observed_at)
        baseline = {
            "contract": CONTRACT,
            "authority": AUTHORITY,
            "sequence_id": active,
            "sequence_start_utc": observed_at,
            "benchmark": "FIRST_ETHBTC_CROSS",
            "registered_ethbtc_level_read_only": level,
            "source_packet_sha256": packet_hash,
            "first_cross": {"prior_ethbtc": prior, "cross_ethbtc": current},
            "axes_at_freeze": snapshot_axes(packet),
            "right_censored": True,
            "relationship_classification": None,
            "incremental_value_vs_first_cross": None,
            "delay_cost": None,
            "failure_outcome": None,
            "exit_side_outcome": None,
            "missingness_policy": "MISSING_REMAINS_UNKNOWN_NEVER_INFERRED",
        }
        write_immutable(root / "sequences" / active / "BASELINE.json", baseline)
        state = {"contract": STATE_CONTRACT, "active_sequence_id": active, "sequence_start_utc": observed_at, "source_packet_sha256": packet_hash}
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_bytes(canon(state))
        observation["event"] = "FIRST_CROSS_FROZEN"
    elif active is not None:
        start = parse_time(str(state["sequence_start_utc"]))
        now = parse_time(observed_at)
        observation["sequence_id"] = active
        observation["time_in_state_days"] = max(0.0, (now - start).total_seconds() / 86400.0)
        observation["event"] = "ACTIVE_SEQUENCE_OBSERVATION" if current >= level else "ETHBTC_REVERSAL_OBSERVED"
        if current < level:
            observation["right_censored"] = False
            state = {"contract": STATE_CONTRACT, "active_sequence_id": None, "last_closed_sequence_id": active, "closed_at_utc": observed_at, "closure_reason": "ETHBTC_REVERSED_BELOW_REGISTERED_FIRST_CROSS_LEVEL", "source_packet_sha256": packet_hash}
            state_path.write_bytes(canon(state))
        else:
            observation["right_censored"] = True
    else:
        observation["event"] = "NO_ELIGIBLE_FIRST_CROSS"
        observation["right_censored"] = True

    obs_id = hashlib.sha256(f"{packet_hash}|{observed_at}".encode()).hexdigest()[:20]
    write_immutable(root / "observations" / f"{observed_at[:10]}_{obs_id}.json", observation)
    latest = {"contract": "ROTATION_SURVIVAL_LATEST_v1", "observed_at_utc": observed_at, "observation_path": str((root / "observations" / f"{observed_at[:10]}_{obs_id}.json").as_posix()), "observation_sha256": sha(observation), "event": observation["event"], "active_sequence_id": state.get("active_sequence_id"), "authority": AUTHORITY}
    (root / "LATEST.json").write_bytes(canon(latest))
    return latest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--cadence", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("research/framework_memory/rotation_survival_forward_rows"))
    args = parser.parse_args()
    print(json.dumps(operate(read_json(args.packet), read_json(args.cadence), args.output_root), sort_keys=True))


if __name__ == "__main__":
    main()
