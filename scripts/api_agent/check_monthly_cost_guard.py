from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_created(value: dict) -> datetime | None:
    created_unix = value.get("created_unix")
    if isinstance(created_unix, (int, float)):
        return datetime.fromtimestamp(created_unix, timezone.utc)
    for key in ("created_at_utc", "generated_at_utc", "retrieved_at_utc"):
        raw = value.get(key)
        if isinstance(raw, str):
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-root", type=Path, required=True)
    parser.add_argument("--hard-stop-usd", type=float, required=True)
    parser.add_argument("--reserve-usd", type=float, default=0.25)
    parser.add_argument("--pending-ledger-root", type=Path)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    total = 0.0
    receipts = 0
    malformed: list[str] = []
    roots = [args.receipt_root]
    if args.pending_ledger_root:
        roots.append(args.pending_ledger_root)

    seen: set[str] = set()
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            try:
                value = json.loads(path.read_text())
            except Exception:
                malformed.append(str(path))
                continue
            if not isinstance(value, dict) or "estimated_cost_usd" not in value:
                continue
            identity = str(value.get("response_id") or value.get("request_sha256") or path)
            if identity in seen:
                continue
            seen.add(identity)
            created = parse_created(value)
            if created is None:
                malformed.append(str(path))
                continue
            if (created.year, created.month) != (now.year, now.month):
                continue
            try:
                cost = float(value["estimated_cost_usd"])
            except Exception:
                malformed.append(str(path))
                continue
            if cost < 0:
                malformed.append(str(path))
                continue
            total += cost
            receipts += 1

    remaining = args.hard_stop_usd - total
    status = "BLOCKED" if malformed or remaining <= args.reserve_usd else "PASS"
    result = {
        "status": status,
        "month": now.strftime("%Y-%m"),
        "receipts": receipts,
        "spent_usd": round(total, 8),
        "remaining_usd": round(remaining, 8),
        "reserve_usd": args.reserve_usd,
        "malformed_cost_receipts": malformed,
        "fail_closed": True,
    }
    print(json.dumps(result, sort_keys=True))
    if status != "PASS":
        raise SystemExit("monthly_api_cost_guard_blocked")


if __name__ == "__main__":
    main()
