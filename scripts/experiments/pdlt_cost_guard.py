from __future__ import annotations

import argparse
import json
from pathlib import Path


def total_cost(root: Path) -> tuple[float, int]:
    total = 0.0
    receipts = 0
    for path in root.rglob("*.json") if root.exists() else []:
        try:
            value = json.loads(path.read_text())
        except Exception:
            continue
        if value.get("contract") != "PDLT_OPENAI_RECEIPT_v1":
            continue
        cost = value.get("estimated_cost_usd")
        if isinstance(cost, (int, float)):
            total += float(cost)
            receipts += 1
    return total, receipts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt-root", type=Path, required=True)
    ap.add_argument("--hard-cap-usd", type=float, default=10.0)
    ap.add_argument("--reserve-usd", type=float, default=0.50)
    args = ap.parse_args()
    spent, receipts = total_cost(args.receipt_root)
    remaining = args.hard_cap_usd - spent
    status = "PASS" if remaining >= args.reserve_usd else "BLOCKED"
    print(json.dumps({"status":status,"spent_usd":round(spent,8),"remaining_usd":round(remaining,8),"receipt_count":receipts,"reserve_usd":args.reserve_usd}, sort_keys=True))
    if status != "PASS":
        raise SystemExit(78)


if __name__ == "__main__":
    main()
