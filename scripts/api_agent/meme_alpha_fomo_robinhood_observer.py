from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "FOMO_ROBINHOOD_OBSERVER_RECEIPT_v1"
REJECT_KINDS = {"dust", "direct", "gift", "seed", "seeded", "airdrop", "passive_transfer"}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def iso_exact(value: Any) -> str | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat().replace("+00:00", "Z")
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def address(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.lower()
    if len(value) != 42 or not value.startswith("0x"):
        return None
    if any(ch not in "0123456789abcdef" for ch in value[2:]):
        return None
    return value


def load_cohort(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text())
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get("members", []):
        addr = address(row.get("evm_address"))
        if addr:
            out[addr] = row
    return out


def classify(row: dict[str, Any]) -> str:
    kind = str(row.get("kind") or "").strip().lower()
    side = str(row.get("side") or "").strip().lower()
    if kind in REJECT_KINDS:
        return "PROVENANCE_REJECT"
    if side != "buy":
        return "RAW_ACTIVITY"
    if not bool(row.get("self_initiated")):
        return "PROVENANCE_PENDING"
    if not str(row.get("economic_entity_id") or "").strip():
        return "ENTITY_PENDING"
    if row.get("liquidity_usd") is None:
        return "MARKET_HEALTH_PENDING"
    if row.get("sellable") is not True:
        return "SELLABILITY_PENDING"
    return "PROVENANCE_PASS"


def build_receipt(row: dict[str, Any], member: dict[str, Any], *, retrieved_at: str) -> dict[str, Any]:
    observed = iso_exact(row.get("observed_at_utc") or row.get("observed_at_unix"))
    event_ts = iso_exact(row.get("source_event_timestamp_utc") or row.get("source_event_timestamp_unix"))
    state = classify(row)
    token = address(row.get("contract") or row.get("token_ca"))
    wallet = address(row.get("wallet_address"))
    identity = {
        "wallet_address": wallet,
        "token_ca": token,
        "observed_at_utc_exact": observed,
        "source_event_timestamp_utc": event_ts,
        "source_tx": row.get("transaction_hash"),
        "source_log_index": row.get("log_index"),
    }
    receipt = {
        "contract": CONTRACT,
        "observation_id": "FOMO-RH-" + hashlib.sha256(canon(identity)).hexdigest()[:20],
        "observed_at_utc_exact": observed,
        "retrieved_at_utc_exact": retrieved_at,
        "source_event_timestamp_or_UNKNOWN": event_ts or "UNKNOWN",
        "source": row.get("source") or "UNKNOWN",
        "source_health": row.get("source_health") or "UNKNOWN",
        "chain": row.get("chain") or "robinhood",
        "chain_id": row.get("chain_id") or 4663,
        "token_ca": token,
        "wallet_address": wallet,
        "wallet_handle": member.get("handle"),
        "wallet_membership_version": "FOMO_ROBINHOOD_PROSPECTIVE_WALLET_COHORT_v0",
        "provenance_class": state,
        "provenance_evidence_refs": row.get("provenance_evidence_refs") or [],
        "provenance_independently_reproduced": bool(row.get("provenance_independently_reproduced")),
        "economic_entity_id_or_PENDING": row.get("economic_entity_id") or "PENDING",
        "independence_state": row.get("independence_state") or "PENDING",
        "market_cap_semantics_or_UNKNOWN": row.get("market_cap_semantics") or "UNKNOWN",
        "market_cap_usd": row.get("market_cap_usd"),
        "liquidity_or_UNKNOWN": row.get("liquidity_usd") if row.get("liquidity_usd") is not None else "UNKNOWN",
        "sellability_state": "PASS" if row.get("sellable") is True else "FAIL" if row.get("sellable") is False else "UNKNOWN",
        "champion_first_seen_at_or_UNKNOWN": iso_exact(row.get("champion_first_seen_at")) or "UNKNOWN",
        "challenger_first_seen_at": observed or "UNKNOWN",
        "lead_time_minutes_or_NOT_COMPARABLE": "NOT_COMPARABLE",
        "state": state,
        "promotion_counter_eligible": False,
        "authority": {"buy": False, "sell": False, "copy_trade": False, "portfolio_action": False},
    }
    champion = receipt["champion_first_seen_at_or_UNKNOWN"]
    if observed and champion != "UNKNOWN":
        a = datetime.fromisoformat(observed.replace("Z", "+00:00"))
        b = datetime.fromisoformat(str(champion).replace("Z", "+00:00"))
        receipt["lead_time_minutes_or_NOT_COMPARABLE"] = round((b - a).total_seconds() / 60.0, 3)
    return receipt


def run(activity_path: Path, cohort_path: Path, output_path: Path, *, retrieved_at: str | None = None) -> dict[str, Any]:
    cohort = load_cohort(cohort_path)
    raw = json.loads(activity_path.read_text())
    rows = raw.get("rows", raw.get("events", raw)) if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError("activity_rows_must_be_list")
    retrieved = iso_exact(retrieved_at) if retrieved_at else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if not retrieved:
        raise ValueError("retrieved_at_must_be_offset_aware")
    receipts = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        wallet = address(row.get("wallet_address"))
        if wallet not in cohort:
            continue
        receipt = build_receipt(row, cohort[wallet], retrieved_at=retrieved)
        if receipt["observed_at_utc_exact"] is None:
            receipt["state"] = "TIMESTAMP_MISSING"
        receipts.append(receipt)
    payload = {
        "contract": "FOMO_ROBINHOOD_OBSERVER_BATCH_v1",
        "retrieved_at_utc_exact": retrieved,
        "cohort_contract": "FOMO_ROBINHOOD_PROSPECTIVE_WALLET_COHORT_v0",
        "receipts": receipts,
        "promotion_counter_increment": 0,
        "authority": {"buy": False, "sell": False, "copy_trade": False, "portfolio_action": False},
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(canon(payload))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed FOMO/RH prospective observer normalizer.")
    parser.add_argument("--activity", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at")
    args = parser.parse_args()
    result = run(args.activity, args.cohort, args.output, retrieved_at=args.retrieved_at)
    print(json.dumps({"receipts": len(result["receipts"]), "promotion_counter_increment": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
