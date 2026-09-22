from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "FOMO_ROBINHOOD_OBSERVER_RECEIPT_v1"
COHORT_CONTRACT = "FOMO_ROBINHOOD_PROSPECTIVE_WALLET_COHORT_v0"
REJECT_KINDS = {"dust", "direct", "gift", "seed", "seeded", "airdrop", "passive_transfer"}


def authority() -> dict[str, bool]:
    return {"buy": False, "sell": False, "copy_trade": False, "portfolio_action": False}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def iso_exact(value: Any) -> str | None:
    if isinstance(value, bool):
        return None
    try:
        if isinstance(value, (int, float)):
            if not math.isfinite(value):
                return None
            dt = datetime.fromtimestamp(float(value), tz=timezone.utc)
        elif isinstance(value, str) and value.strip() and value not in {"UNKNOWN", "PENDING"}:
            dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        else:
            return None
    except (ValueError, OverflowError, OSError):
        return None
    if dt.tzinfo is None or dt.utcoffset() is None:
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


def evidence_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value.strip().upper() not in {"UNKNOWN", "PENDING"}
    )


def evidence_refs(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(evidence_text(ref) for ref in value)


def finite_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def market_owner_pass(state: Any, refs: Any) -> bool:
    return state == "PASS" and evidence_refs(refs)


def prospective_owner_pass(state: Any, ref: Any) -> bool:
    return state == "PASS" and evidence_text(ref)


def valid_locator(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    tx = value.get("transaction_hash")
    return (
        value.get("type") == "EVM_LOG"
        and type(value.get("chain_id")) is int
        and value.get("chain_id") == 4663
        and isinstance(tx, str)
        and len(tx) == 66
        and tx.startswith("0x")
        and all(ch in "0123456789abcdefABCDEF" for ch in tx[2:])
        and type(value.get("log_index")) is int
        and value.get("log_index") >= 0
    )


def observation_identity(receipt: dict[str, Any]) -> dict[str, Any]:
    """Legacy-compatible observation identity rebuilt from retained lineage."""
    locator = receipt.get("source_locator")
    tx = locator.get("transaction_hash") if isinstance(locator, dict) else None
    log_index = locator.get("log_index") if isinstance(locator, dict) else None
    return {
        "wallet_address": receipt.get("wallet_address"),
        "token_ca": receipt.get("token_ca"),
        "observed_at_utc_exact": receipt.get("observed_at_utc_exact"),
        "source_event_timestamp_utc": receipt.get("source_event_timestamp_or_UNKNOWN"),
        "source_tx": tx,
        "source_log_index": log_index,
    }


def observation_id(receipt: dict[str, Any]) -> str:
    return "FOMO-RH-" + hashlib.sha256(canon(observation_identity(receipt))).hexdigest()[:20]


def classify(row: dict[str, Any]) -> str:
    kind = str(row.get("kind") or "").strip().lower()
    side = str(row.get("side") or "").strip().lower()
    if kind in REJECT_KINDS:
        return "PROVENANCE_REJECT"
    if side != "buy":
        return "RAW_ACTIVITY"
    if (
        row.get("self_initiated") is not True
        or row.get("provenance_independently_reproduced") is not True
        or not evidence_refs(row.get("provenance_evidence_refs"))
    ):
        return "PROVENANCE_PENDING"
    if (
        row.get("independence_state") != "CONFIRMED"
        or not evidence_text(row.get("economic_entity_id"))
    ):
        return "ENTITY_PENDING"
    if row.get("source_health") != "PASS" or not evidence_text(row.get("source")):
        return "DEGRADED"
    if (
        not market_owner_pass(row.get("market_data_health"), row.get("market_data_health_evidence_refs"))
        or not finite_number(row.get("liquidity_usd"))
    ):
        return "MARKET_HEALTH_PENDING"
    if row.get("sellable") is not True:
        return "SELLABILITY_PENDING"
    return "PROVENANCE_PASS"


def receipt_state(row: dict[str, Any]) -> str:
    raw = {
        "kind": row.get("trade_kind"),
        "side": row.get("trade_side"),
        "self_initiated": row.get("self_initiated"),
        "provenance_independently_reproduced": row.get("provenance_independently_reproduced"),
        "provenance_evidence_refs": row.get("provenance_evidence_refs"),
        "independence_state": row.get("independence_state"),
        "economic_entity_id": row.get("economic_entity_id_or_PENDING"),
        "source": row.get("source"),
        "source_health": row.get("source_health"),
        "market_data_health": row.get("market_data_health"),
        "market_data_health_evidence_refs": row.get("market_data_health_evidence_refs"),
        "liquidity_usd": row.get("liquidity_or_UNKNOWN"),
        "sellable": row.get("sellability_state") == "PASS",
    }
    state = classify(raw)
    if state != "PROVENANCE_PASS":
        return state

    for key in ("observed_at_utc_exact", "retrieved_at_utc_exact", "source_event_timestamp_or_UNKNOWN"):
        if not isinstance(row.get(key), str) or iso_exact(row.get(key)) is None:
            return "TIMESTAMP_MISSING"

    if (
        row.get("contract") != CONTRACT
        or row.get("chain") != "robinhood"
        or type(row.get("chain_id")) is not int
        or row.get("chain_id") != 4663
        or not valid_locator(row.get("source_locator"))
        or address(row.get("token_ca")) is None
        or address(row.get("wallet_address")) is None
        or row.get("wallet_membership_version") != COHORT_CONTRACT
        or row.get("observation_id") != observation_id(row)
    ):
        return "PROVENANCE_PENDING"

    if not prospective_owner_pass(row.get("prospective_admission_state"), row.get("prospective_admission_evidence_ref")):
        return "PROVENANCE_PENDING"
    return "PROVENANCE_PASS"


def load_cohort(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text())
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get("members", []):
        addr = address(row.get("evm_address"))
        if addr:
            out[addr] = row
    return out


def raw_timestamp(row: dict[str, Any], text_key: str, unix_key: str) -> str | None:
    if text_key in row:
        return iso_exact(row[text_key])
    return iso_exact(row.get(unix_key))


def build_receipt(row: dict[str, Any], member: dict[str, Any], *, retrieved_at: str) -> dict[str, Any]:
    observed = raw_timestamp(row, "observed_at_utc", "observed_at_unix")
    event_ts = raw_timestamp(row, "source_event_timestamp_utc", "source_event_timestamp_unix")
    retrieved = iso_exact(retrieved_at)
    locator = row.get("source_locator") if "source_locator" in row else {
        "type": "EVM_LOG",
        "chain_id": row.get("chain_id"),
        "transaction_hash": row.get("transaction_hash"),
        "log_index": row.get("log_index"),
    }
    raw_state = classify(row)
    receipt = {
        "contract": CONTRACT,
        "observed_at_utc_exact": observed,
        "retrieved_at_utc_exact": retrieved,
        "source_event_timestamp_or_UNKNOWN": event_ts or "UNKNOWN",
        "source": row.get("source") or "UNKNOWN",
        "source_health": row.get("source_health", "UNKNOWN"),
        "source_locator": locator,
        "chain": row.get("chain") or "robinhood",
        "chain_id": row.get("chain_id") if row.get("chain_id") is not None else 4663,
        "token_ca": address(row.get("contract") or row.get("token_ca")),
        "wallet_address": address(row.get("wallet_address")),
        "wallet_handle": member.get("handle"),
        "wallet_membership_version": COHORT_CONTRACT,
        "trade_kind": str(row.get("kind") or "").strip().lower(),
        "trade_side": str(row.get("side") or "").strip().lower(),
        "self_initiated": row.get("self_initiated") is True,
        "provenance_class": raw_state,
        "provenance_evidence_refs": row.get("provenance_evidence_refs", []),
        "provenance_independently_reproduced": row.get("provenance_independently_reproduced") is True,
        "economic_entity_id_or_PENDING": row.get("economic_entity_id", "PENDING"),
        "independence_state": row.get("independence_state", "PENDING"),
        "market_cap_semantics_or_UNKNOWN": row.get("market_cap_semantics") or "UNKNOWN",
        "market_cap_usd": row.get("market_cap_usd"),
        "liquidity_or_UNKNOWN": row.get("liquidity_usd") if row.get("liquidity_usd") is not None else "UNKNOWN",
        "market_data_health": row.get("market_data_health", "UNKNOWN"),
        "market_data_health_evidence_refs": row.get("market_data_health_evidence_refs", []),
        "sellability_state": "PASS" if row.get("sellable") is True else "FAIL" if row.get("sellable") is False else "UNKNOWN",
        "prospective_admission_state": row.get("prospective_admission_state", "UNKNOWN"),
        "prospective_admission_evidence_ref": row.get("prospective_admission_evidence_ref"),
        "champion_first_seen_at_or_UNKNOWN": iso_exact(row.get("champion_first_seen_at")) or "UNKNOWN",
        "challenger_first_seen_at": observed or "UNKNOWN",
        "lead_time_minutes_or_NOT_COMPARABLE": "NOT_COMPARABLE",
        "promotion_counter_eligible": False,
        "authority": authority(),
    }
    receipt["observation_id"] = observation_id(receipt)
    state = receipt_state(receipt)
    receipt["state"] = state
    if state == "PROVENANCE_PENDING" and raw_state == "PROVENANCE_PASS":
        receipt["provenance_class"] = "PROVENANCE_PENDING"

    champion = receipt["champion_first_seen_at_or_UNKNOWN"]
    if state == "PROVENANCE_PASS" and observed and champion != "UNKNOWN":
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
    retrieved = iso_exact(retrieved_at) if retrieved_at is not None else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if not retrieved:
        raise ValueError("retrieved_at_must_be_exact_and_offset_aware")
    receipts = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        wallet = address(row.get("wallet_address"))
        if wallet in cohort:
            receipts.append(build_receipt(row, cohort[wallet], retrieved_at=retrieved))
    payload = {
        "contract": "FOMO_ROBINHOOD_OBSERVER_BATCH_v1",
        "retrieved_at_utc_exact": retrieved,
        "cohort_contract": COHORT_CONTRACT,
        "receipts": receipts,
        "promotion_counter_increment": 0,
        "authority": authority(),
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
