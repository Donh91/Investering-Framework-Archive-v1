#!/usr/bin/env python3
"""Fail-closed MAR-WP04C4 enumeration scaffold.

This module validates materialization gates only. It intentionally emits no
historical event counts until every required owner dataset is replayable.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REQUIRED_DATASETS = {
    "DTWEXBGS", "DGS2", "DGS10", "VIXCLS",
    "BTC_SPOT_DAILY_CEST_BINANCE", "ETH_SPOT_DAILY_CEST_BINANCE",
    "ETHBTC_SPOT_DAILY_CEST_BINANCE_DIRECT",
    "DERIVATIVES_BINANCE_UM_BTC_ETH_HOURLY",
    "BREADTH_BINANCE_TOP100_PIT",
}


def evaluate(registry: dict) -> dict:
    rows = registry.get("datasets", [])
    replayable = {
        row.get("dataset_id") for row in rows
        if row.get("materialization_status") == "REPLAYABLE_OWNER"
        and row.get("member_sha256_verified") is True
        and row.get("raw_normalized_parity") == "PASS"
    }
    missing = sorted(REQUIRED_DATASETS - replayable)
    if missing:
        return {
            "status": "BLOCKED",
            "enumeration_authorized": False,
            "missing_required_owner_datasets": missing,
            "candidate_event_counts": {"macro": None, "leverage": None, "rotation": None},
            "outcome_access": False,
        }
    return {
        "status": "READY_FOR_ENUMERATION_ONLY",
        "enumeration_authorized": True,
        "missing_required_owner_datasets": [],
        "candidate_event_counts": {"macro": None, "leverage": None, "rotation": None},
        "outcome_access": False,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: wp04c4_enumerate.py MATERIALIZATION_REGISTRY.json", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(data), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
