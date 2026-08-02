from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-root", type=Path, required=True)
    parser.add_argument("--hard-stop-usd", type=float, required=True)
    parser.add_argument("--reserve-usd", type=float, default=0.25)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    total = 0.0
    receipts = 0
    for path in args.receipt_root.rglob("*RECEIPT*.json") if args.receipt_root.exists() else []:
        try:
            value = json.loads(path.read_text())
        except Exception:
            continue
        created = value.get("created_unix")
        if not isinstance(created, (int, float)):
            continue
        dt = datetime.fromtimestamp(created, timezone.utc)
        if (dt.year, dt.month) != (now.year, now.month):
            continue
        total += float(value.get("estimated_cost_usd", 0.0))
        receipts += 1

    remaining = args.hard_stop_usd - total
    status = "PASS" if remaining > args.reserve_usd else "BLOCKED"
    print(json.dumps({"status": status, "month": now.strftime("%Y-%m"), "receipts": receipts, "spent_usd": round(total, 8), "remaining_usd": round(remaining, 8), "reserve_usd": args.reserve_usd}, sort_keys=True))
    if status != "PASS":
        raise SystemExit("monthly_api_cost_guard_blocked")


if __name__ == "__main__":
    main()
