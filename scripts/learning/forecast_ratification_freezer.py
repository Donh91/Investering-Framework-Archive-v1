from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_ratification_contract import (  # noqa: E402
    DECISION_SLA_MINUTES,
    RATIFICATION_PACKET_V2,
    decision_deadline,
    is_post_cutover_candidate,
    parse_dt,
    validate_packet_shape,
)
from forecast_settlement_contract import (  # noqa: E402
    SETTLEMENT_EXACT_TARGET_TIME_V1,
    supports_exact_price_settlement,
)

UTC = timezone.utc
UNIT_CONTRACT_VERSION = "FORECAST_TARGET_UNITS_v2"
LINEAGE_CONTRACT = "DATA_PING_LEARNING_LINEAGE_v1"


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def at_path(value: Any, path: str) -> Any:
    cur = value
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def metric_value(evidence: dict[str, Any], metric_path: str) -> Any:
    direct = at_path(evidence, metric_path)
    if direct is not None:
        return direct
    market_metrics = evidence.get("market_metrics")
    if isinstance(market_metrics, dict):
        return at_path(market_metrics, metric_path)
    return None


def evidence_timestamp(evidence: dict[str, Any]) -> datetime:
    for key in ("captured_at_utc", "freeze_utc", "snapshot_utc", "created_at_utc"):
        if evidence.get(key):
            return parse_dt(str(evidence[key]))
    raise ValueError("BASELINE_EVIDENCE_TIMESTAMP_MISSING")


def normalize_target(candidate: dict[str, Any], start: float) -> dict[str, Any]:
    direction = candidate.get("direction")
    mode = candidate.get("target_mode")
    if direction in {"UP", "DOWN"}:
        if mode == "PCT_MOVE":
            pct = candidate.get("threshold_pct")
            if not isinstance(pct, (int, float)) or float(pct) <= 0:
                raise ValueError("PCT_THRESHOLD_REQUIRED")
            return {"target_mode": mode, "threshold_pct": float(pct), "target_value": None, "range_lower_pct": None, "range_upper_pct": None}
        if mode == "ABSOLUTE_VALUE":
            target = candidate.get("target_value")
            if not isinstance(target, (int, float)):
                raise ValueError("ABSOLUTE_TARGET_REQUIRED")
            target = float(target)
            if direction == "UP":
                if target <= start:
                    raise ValueError("UP_TARGET_MUST_EXCEED_START")
                pct = (target / start - 1.0) * 100.0
            else:
                if target >= start:
                    raise ValueError("DOWN_TARGET_MUST_BE_BELOW_START")
                pct = (1.0 - target / start) * 100.0
            return {"target_mode": mode, "threshold_pct": pct, "target_value": target, "range_lower_pct": None, "range_upper_pct": None}
        raise ValueError("EXPLICIT_DIRECTIONAL_TARGET_MODE_REQUIRED")
    if direction == "RANGE":
        if mode != "ABSOLUTE_RANGE":
            raise ValueError("ABSOLUTE_RANGE_MODE_REQUIRED")
        low = candidate.get("range_low")
        high = candidate.get("range_high")
        if not isinstance(low, (int, float)) or not isinstance(high, (int, float)) or float(low) >= float(high):
            raise ValueError("VALID_RANGE_BOUNDS_REQUIRED")
        return {
            "target_mode": mode,
            "threshold_pct": None,
            "target_value": None,
            "range_lower_pct": (float(low) / start - 1.0) * 100.0,
            "range_upper_pct": (float(high) / start - 1.0) * 100.0,
            "range_lower_value": float(low),
            "range_upper_value": float(high),
        }
    raise ValueError("INVALID_DIRECTION")


def validate_data_ping_lineage(candidate: dict[str, Any], receipt_path: Path | None) -> dict[str, Any] | None:
    lineage = candidate.get("data_ping_lineage")
    if lineage is None:
        if receipt_path is not None:
            raise ValueError("ORPHAN_ACTION_COMPASS_RECEIPT")
        return None
    if not isinstance(lineage, dict) or lineage.get("contract") != LINEAGE_CONTRACT:
        raise ValueError("INVALID_DATA_PING_LINEAGE")
    if receipt_path is None:
        raise ValueError("ACTION_COMPASS_RECEIPT_REQUIRED")
    receipt = load(receipt_path)
    packet_hash = lineage.get("accepted_packet_sha256")
    if not isinstance(packet_hash, str) or len(packet_hash) != 64 or any(ch not in "0123456789abcdef" for ch in packet_hash):
        raise ValueError("INVALID_ACCEPTED_PACKET_SHA256")
    expected = {
        "accepted_packet_identity": "DPI-" + packet_hash[:24],
        "action_compass_receipt_id": receipt.get("receipt_id"),
        "action_compass_receipt_sha256": digest(receipt),
        "accepted_packet_path": receipt.get("source_reference"),
        "canonical_repository": receipt.get("canonical_repository"),
        "canonical_commit_sha": receipt.get("canonical_commit_sha"),
        "owner_contract": receipt.get("owner_contract"),
    }
    if receipt.get("contract") != "THREE_HORIZON_ACTION_COMPASS_RECEIPT_v1_1":
        raise ValueError("WRONG_ACTION_COMPASS_RECEIPT_CONTRACT")
    if receipt.get("input_binding_status") != "VERIFIED_REPO_FILE":
        raise ValueError("ACTION_COMPASS_INPUT_NOT_VERIFIED_REPO_FILE")
    if receipt.get("input_packet_sha256") != packet_hash:
        raise ValueError("ACTION_COMPASS_PACKET_HASH_MISMATCH")
    if receipt.get("portfolio_execution") is not False:
        raise ValueError("PORTFOLIO_EXECUTION_MUST_REMAIN_FALSE")
    commit = receipt.get("canonical_commit_sha")
    if not isinstance(commit, str) or len(commit) != 40:
        raise ValueError("INVALID_CANONICAL_COMMIT_SHA")
    for key, expected_value in expected.items():
        if lineage.get(key) != expected_value:
            raise ValueError("DATA_PING_LINEAGE_MISMATCH:" + key)
    return dict(lineage)


def validate_ratification(candidate: dict[str, Any], packet: dict[str, Any]) -> datetime:
    validate_packet_shape(packet)
    if candidate.get("contract") != "FORECAST_CANDIDATE_v1" or candidate.get("ratification_status") != "PENDING":
        raise ValueError("CANDIDATE_NOT_PENDING")
    if candidate.get("self_promotion_allowed") is not False:
        raise ValueError("CANDIDATE_SELF_PROMOTION_INVALID")
    if not is_post_cutover_candidate(candidate):
        raise ValueError("LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE")
    if packet.get("decision") != "RATIFY":
        raise ValueError("RATIFY_DECISION_REQUIRED")
    if packet.get("candidate_id") != candidate.get("candidate_id"):
        raise ValueError("CANDIDATE_ID_MISMATCH")
    if packet.get("candidate_sha256") != digest(candidate):
        raise ValueError("CANDIDATE_HASH_MISMATCH")
    created = parse_dt(str(candidate["created_at_utc"]))
    decision_at = parse_dt(str(packet["decision_at_utc"]))
    if decision_at < created:
        raise ValueError("RATIFICATION_PRECEDES_CANDIDATE")
    if decision_at > decision_deadline(str(candidate["created_at_utc"])):
        raise ValueError("RATIFICATION_DECISION_SLA_EXCEEDED")
    return decision_at


def build_frozen(candidate_record: dict[str, Any], packet: dict[str, Any], baseline: dict[str, Any], baseline_path: Path, target: dict[str, Any], lineage: dict[str, Any] | None, decision_at: datetime) -> dict[str, Any]:
    candidate = candidate_record["candidate"]
    horizon = int(candidate["horizon_days"])
    metric = str(candidate["metric_path"])
    start = metric_value(baseline, metric)
    baseline_hash = digest(baseline)
    forecast_id = "ff_" + hashlib.sha256(canon({
        "candidate": candidate_record["candidate_id"],
        "ratification": digest(packet),
        "baseline": baseline_hash,
        "decision_at_utc": iso(decision_at),
    })).hexdigest()[:24]
    frozen: dict[str, Any] = {
        "contract": "FROZEN_FORECAST_v1",
        "unit_contract_version": UNIT_CONTRACT_VERSION,
        "forecast_id": forecast_id,
        "candidate_id": candidate_record["candidate_id"],
        "frozen_at_utc": iso(decision_at),
        "outcome_due_utc": iso(decision_at + timedelta(days=horizon)),
        "horizon_days": horizon,
        "metric_path": metric,
        "direction": candidate["direction"],
        "start_value": float(start),
        "target_mode": target["target_mode"],
        "threshold_pct": target.get("threshold_pct"),
        "target_value": target.get("target_value"),
        "range_lower_pct": target.get("range_lower_pct"),
        "range_upper_pct": target.get("range_upper_pct"),
        "range_lower_value": target.get("range_lower_value"),
        "range_upper_value": target.get("range_upper_value"),
        "rationale": candidate.get("rationale"),
        "model": candidate_record.get("model"),
        "task": candidate_record.get("task"),
        "prompt_sha256": candidate_record.get("prompt_sha256"),
        "context_sha256": candidate_record.get("context_sha256"),
        "source_output_sha256": candidate_record.get("source_output_sha256"),
        "candidate_sha256": digest(candidate_record),
        "ratification_sha256": digest(packet),
        "ratification_contract": RATIFICATION_PACKET_V2,
        "ratification_authority": packet.get("authority"),
        "ratification_decision_at_utc": iso(decision_at),
        "ratification_outcome_blind": True,
        "ratification_decision_sla_minutes": DECISION_SLA_MINUTES,
        "baseline_evidence_path": str(baseline_path),
        "baseline_evidence_sha256": baseline_hash,
        "baseline_evidence_observed_at_utc": iso(evidence_timestamp(baseline)),
        "authority": {"portfolio_action": False, "model_weight_change": False, "canonical_promotion": False, "framework_state_change": False},
    }
    if supports_exact_price_settlement(metric):
        frozen["settlement_contract_version"] = SETTLEMENT_EXACT_TARGET_TIME_V1
        frozen["settlement_activation_semantics"] = "FROZEN_AT_RATIFICATION_DECISION_PROSPECTIVE_ONLY"
    if lineage is not None:
        frozen["data_ping_lineage"] = lineage
    return frozen


def freeze_candidate(candidate_record: dict[str, Any], packet: dict[str, Any], baseline: dict[str, Any], baseline_path: Path, output_root: Path, action_compass_receipt: Path | None = None) -> tuple[str, dict[str, Any], Path]:
    decision_at = validate_ratification(candidate_record, packet)
    baseline_at = evidence_timestamp(baseline)
    if baseline_at > decision_at:
        raise ValueError("BASELINE_EVIDENCE_AFTER_RATIFICATION_DECISION")
    candidate = candidate_record["candidate"]
    metric = str(candidate["metric_path"])
    start = metric_value(baseline, metric)
    if not isinstance(start, (int, float)):
        raise ValueError("BASELINE_METRIC_UNAVAILABLE")
    target = normalize_target(candidate, float(start))
    lineage = validate_data_ping_lineage(candidate_record, action_compass_receipt)
    frozen = build_frozen(candidate_record, packet, baseline, baseline_path, target, lineage, decision_at)
    out = output_root / f"{frozen['forecast_id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        existing = load(out)
        if canon(existing) != canon(frozen):
            raise ValueError("FORECAST_ID_COLLISION")
        return "DUPLICATE_NOOP", existing, out
    out.write_bytes(canon(frozen))
    if out.read_bytes() != canon(frozen):
        raise RuntimeError("FORECAST_FREEZE_READBACK_MISMATCH")
    return "FROZEN", frozen, out
