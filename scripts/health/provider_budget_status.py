#!/usr/bin/env python3
"""Materialize provider-credit health from already-paid owner receipts.

No provider/source calls are made here. The primary use is preserving CFGI's
X-Credits-* response headers from the Live Anchor artifact so the user-facing
Handlekompas can warn before/when the provider credit budget is exhausted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "PROVIDER_BUDGET_STATUS_v1"
AUTHORITY = {
    "binding": False,
    "market_interpretation": "NONE",
    "portfolio_execution": False,
    "market_threshold_change": False,
    "provider_retry_authority": False,
    "purpose": "OPERATIONAL_PROVIDER_CREDIT_OBSERVABILITY_ONLY",
}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, Mapping):
        raise ValueError("PROVIDER_RECEIPT_NOT_OBJECT")
    return value


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def cfgi_status(receipt: Mapping[str, Any]) -> dict[str, Any]:
    billing = receipt.get("billing") if isinstance(receipt.get("billing"), Mapping) else {}
    used = integer(billing.get("credits_used"))
    remaining = integer(billing.get("credits_remaining"))
    expected = integer(billing.get("expected_credits"))
    receipt_status = str(receipt.get("status") or "UNKNOWN")

    if remaining is None:
        status = "UNKNOWN_CREDIT_HEADER_ABSENT"
        reason = "CFGI_X_CREDITS_REMAINING_NOT_AVAILABLE"
    elif remaining <= 0:
        status = "EXHAUSTED"
        reason = "CFGI_CREDITS_REMAINING_ZERO"
    elif expected is not None and expected > 0 and remaining < expected:
        status = "LOW_INSUFFICIENT_FOR_NEXT_STANDARD_CALL"
        reason = "CFGI_REMAINING_BELOW_CURRENT_STANDARD_CALL_COST"
    else:
        status = "PASS"
        reason = "CFGI_CREDITS_AVAILABLE"

    return {
        "provider": "CFGI",
        "status": status,
        "reason": reason,
        "owner_receipt_status": receipt_status,
        "retrieved_at_utc": receipt.get("retrieved_at_utc"),
        "credits_used": used,
        "credits_remaining": remaining,
        "current_standard_call_expected_credits": expected,
        "semantics": "PROVIDER_REPORTED_CREDIT_HEADERS_NOT_ACCOUNT_MONTHLY_SPEND",
    }


def build(receipt: Mapping[str, Any], source_run_id: str, now: datetime | None = None) -> dict[str, Any]:
    generated = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    cfgi = cfgi_status(receipt)
    if cfgi["status"] in {"EXHAUSTED", "LOW_INSUFFICIENT_FOR_NEXT_STANDARD_CALL"}:
        overall = "DEGRADED"
    elif cfgi["status"] == "PASS":
        overall = "PASS"
    else:
        overall = "UNKNOWN"
    packet = {
        "contract": CONTRACT,
        "generated_at_utc": generated.isoformat().replace("+00:00", "Z"),
        "status": overall,
        "scope": "PROVIDER_CREDITS_ONLY_NOT_ACCOUNT_MONTHLY_SPEND",
        "source_run_id": source_run_id,
        "providers": {"CFGI": cfgi},
        "exact_monthly_spend_available": False,
        "exact_remaining_monthly_budget_available": False,
        "authority": AUTHORITY,
    }
    packet["status_sha256"] = digest(canon({k: v for k, v in packet.items() if k != "status_sha256"}))
    return packet


def write(packet: Mapping[str, Any], output_root: Path) -> dict[str, Any]:
    dt = datetime.fromisoformat(str(packet["generated_at_utc"]).replace("Z", "+00:00"))
    run_path = output_root / "runs" / dt.strftime("%Y/%m/%d") / f"{dt:%H%M%S}_{packet['status_sha256'][:12]}.json"
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_bytes(canon(packet))
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "LATEST.json").write_bytes(canon(packet))
    return {"path": run_path.as_posix(), "latest": (output_root / "LATEST.json").as_posix(), "sha256": packet["status_sha256"], "status": packet["status"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfgi-receipt", type=Path, required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--output-root", type=Path, default=Path("03_WEEKLY_OPERATIONS/provider_budget"))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    packet = build(read_json(args.cfgi_receipt), args.source_run_id)
    result = packet if args.no_write else write(packet, args.output_root)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
