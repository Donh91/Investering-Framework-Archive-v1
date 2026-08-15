from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_created(value: dict) -> datetime | None:
    created_unix = value.get("created_unix")
    if isinstance(created_unix, (int, float)):
        return datetime.fromtimestamp(created_unix, timezone.utc)
    for key in ("created_at_utc", "generated_at_utc"):
        raw = value.get(key)
        if isinstance(raw, str):
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
            except Exception:
                pass
    return None


def task_of(value: dict) -> str | None:
    task = value.get("task")
    if task:
        return str(task)
    if value.get("contract") == "RESEARCH_AUTOMATION_COST_RECEIPT_v1":
        return "RESEARCH_AUTOMATION"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-root", type=Path, required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--reserve-usd", type=float, default=0.1)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    spent = 0.0
    receipts = 0
    seen: set[str] = set()
    if args.receipt_root.exists():
        for path in args.receipt_root.rglob("*.json"):
            try:
                value = json.loads(path.read_text())
            except Exception:
                continue
            if task_of(value) != args.task or "estimated_cost_usd" not in value:
                continue
            created = parse_created(value)
            if created is None or (created.year, created.month) != (now.year, now.month):
                continue
            identity = str(value.get("response_id") or value.get("request_hash") or value.get("request_sha256") or path)
            if identity in seen:
                continue
            seen.add(identity)
            spent += float(value.get("estimated_cost_usd", 0.0) or 0.0)
            receipts += 1
    remaining = args.cap_usd - spent
    status = "PASS" if remaining > args.reserve_usd else "BLOCKED"
    print(json.dumps({
        "status": status,
        "task": args.task,
        "month": now.strftime("%Y-%m"),
        "receipts": receipts,
        "spent_usd": round(spent, 8),
        "cap_usd": args.cap_usd,
        "remaining_usd": round(remaining, 8),
        "reserve_usd": args.reserve_usd,
    }, sort_keys=True))
    if status != "PASS":
        raise SystemExit("api_lane_budget_blocked")


if __name__ == "__main__":
    main()
