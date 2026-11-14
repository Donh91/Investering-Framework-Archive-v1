#!/usr/bin/env python3
"""Recover the existing Rich Breadth owner when its last main receipt is stale."""
import datetime as dt
import json
import subprocess
import sys

MAX_AGE = dt.timedelta(hours=5)
ACTIVE = {"queued", "in_progress", "pending", "waiting", "requested"}


def decision(timestamp, now, statuses):
    if not isinstance(timestamp, str):
        raise ValueError("BREADTH_TIMESTAMP_MISSING")
    try:
        value = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("BREADTH_TIMESTAMP_INVALID") from exc
    if value.tzinfo is None or now.tzinfo is None or value > now:
        raise ValueError("BREADTH_TIMESTAMP_UNTRUSTED")
    if now - value <= MAX_AGE:
        return "FRESH"
    if not isinstance(statuses, list) or any(s not in ACTIVE | {"completed"} for s in statuses):
        raise ValueError("BREADTH_RUN_CENSUS_INVALID")
    if any(s in ACTIVE for s in statuses):
        return "ACTIVE"
    return "DISPATCH"


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=30).stdout


def main():
    run(["git", "fetch", "origin", "main"])
    payload = json.loads(run(["git", "show", "origin/main:03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json"]))
    stamp = payload.get("retrieved_at_utc")
    now = dt.datetime.now(dt.timezone.utc)
    # Check freshness first, then query native GitHub runs only if stale.
    if decision(stamp, now, []) == "FRESH":
        print("BREADTH_WATCHDOG_FRESH")
        return
    runs = json.loads(run(["gh", "run", "list", "--workflow", "rich-breadth-checkpoint.yml", "--limit", "100", "--json", "status"]))
    if not isinstance(runs, list) or any(not isinstance(r, dict) or "status" not in r for r in runs):
        raise ValueError("BREADTH_RUN_CENSUS_INVALID")
    result = decision(stamp, now, [r["status"] for r in runs])
    if result == "ACTIVE":
        print("BREADTH_WATCHDOG_ACTIVE")
        return
    run(["gh", "workflow", "run", "rich-breadth-checkpoint.yml", "--ref", "main"])
    print("BREADTH_WATCHDOG_DISPATCHED_NO_INPUTS")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"BREADTH_WATCHDOG_UNAVAILABLE: {type(exc).__name__}", file=sys.stderr)
        sys.exit(1)
