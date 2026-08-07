from __future__ import annotations

import argparse
import json
from pathlib import Path


def receipt_costs(roots: list[Path]) -> tuple[float, int]:
    total = 0.0
    receipts = 0
    seen: set[str] = set()
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            try:
                value = json.loads(path.read_text())
            except Exception:
                continue
            if value.get("contract") != "PDLT_OPENAI_RECEIPT_v1":
                continue
            identity = str(value.get("response_id") or value.get("forecast_sha256") or path.resolve())
            if identity in seen:
                continue
            seen.add(identity)
            cost = value.get("estimated_cost_usd")
            if isinstance(cost, (int, float)):
                total += float(cost)
                receipts += 1
    return total, receipts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt-root", type=Path, action="append", required=True)
    ap.add_argument("--hard-cap-usd", type=float, default=10.0)
    ap.add_argument("--reserve-usd", type=float, default=0.50)
    ap.add_argument("--pending-reserve-usd", type=float, default=0.0)
    args = ap.parse_args()
    spent, receipts = receipt_costs(args.receipt_root)
    remaining = args.hard_cap_usd - spent
    required = args.reserve_usd + args.pending_reserve_usd
    status = "PASS" if remaining >= required else "BLOCKED"
    print(json.dumps({
        "status": status,
        "spent_usd": round(spent, 8),
        "remaining_usd": round(remaining, 8),
        "receipt_count": receipts,
        "reserve_usd": args.reserve_usd,
        "pending_reserve_usd": args.pending_reserve_usd,
        "required_remaining_usd": round(required, 8),
    }, sort_keys=True))
    if status != "PASS":
        raise SystemExit(78)


if __name__ == "__main__":
    main()
