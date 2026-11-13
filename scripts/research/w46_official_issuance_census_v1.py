#!/usr/bin/env python3
"""Research-only, frozen-Git census of W46 original Official Compass issuances.

Every input is fetched by exact Git commit and path, not mutable current main.
Issued_at is a claim in an archived JSON, NOT verified first-known or delivery.
This tool cannot issue forecasts, execute trades, change risk or call models.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PIN = "a4504580273bc4396f20395ac9cd272656dc4454"
FREEZE = "05_CYCLE_NAVIGATOR/weekly/2026/W46/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
PREFIX = "04_MARKET_LEARNING/handlekompas/official/daily/2026/11/"
VALID_DAYS = frozenset({"09", "10", "11", "12", "13"})
FILENAME = re.compile(r"^CMP-202611(09|10|11|12|13)-[a-f0-9]{12}\.json$")

def git_output(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)

def load_frozen(root: Path, ref: str = PIN) -> tuple[list[tuple[str, bytes]], bytes]:
    if not re.fullmatch(r"[a-f0-9]{40}", ref):
        raise ValueError("SOURCE_COMMIT_NOT_40_HEX")
    names = git_output(root, "ls-tree", "-r", "--name-only", ref, "--", PREFIX).decode().splitlines()
    paths = sorted(n for n in names
                   if n.startswith(PREFIX) and n.endswith(".json") and
                   len(n.split("/")) == 9 and
                   n.split("/")[-2] in VALID_DAYS and
                   FILENAME.fullmatch(n.split("/")[-1]))
    # No silently truncated denominator, and no unrelated or later November issuances.
    if len(paths) != 42 or len(set(paths)) != 42:
        raise ValueError(f"FROZEN_ISSUANCE_DENOMINATOR_MISMATCH:{len(paths)}")
    rows = [(p, git_output(root, "show", f"{ref}:{p}")) for p in paths]
    freeze = git_output(root, "show", f"{ref}:{FREEZE}")
    return rows, freeze

def summarize(records: list[tuple[str, bytes]], frozen_forecast: bytes,
              *, exact_count: int = 42) -> tuple[dict, list[dict]]:
    try:
        freeze = json.loads(frozen_forecast)
        floor = float(freeze["btc_range_low"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("FROZEN_BTC_WEEK_LOW_INVALID") from exc
    if not 0 < floor < 1_000_000:
        raise ValueError("FROZEN_WEEK_LOW_OUT_OF_RANGE")
    if len(records) != exact_count or len(set(p for p, _ in records)) != exact_count:
        raise ValueError("SOURCE_ISSUANCE_CENSUS_INCOMPLETE")
    results = []
    ids = set()
    for path, raw in records:
        try:
            j = json.loads(raw)
            at = j["issued_at_utc"]
            dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
                raise ValueError("NOT_UTC")
            p = j["protection_tracker"]["pullback_risk_state"]
            act = j["action_now"]
            stat = j["data_status"]
            btc = float(j["market_reference"]["btc_usdt"])
            compass_id = j["compass_id"]
            d1 = j["horizons"]["NEXT_1_3D"]["expected_direction"]
            d5 = j["horizons"]["NEXT_5_7D"]["expected_direction"]
            d2 = j["horizons"]["NEXT_2_3W"]["expected_direction"]
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("INVALID_ORIGINAL_ISSUANCE:" + path) from exc
        if compass_id in ids:
            raise ValueError("DUPLICATED_ISSUANCE_ID")
        ids.add(compass_id)
        if not (0 < btc < 1_000_000):
            raise ValueError("INVALID_BTC_REFERENCE:" + path)
        if dt.strftime("%Y/11/%d") not in path:
            raise ValueError("ISSUER_DATE_DIRECTORY_MISMATCH")
        results.append({
            "issued_at_utc_claim": at,
            "archive_source_path": path,
            "archive_blob_sha256": hashlib.sha256(raw).hexdigest(),
            "compass_id": compass_id,
            "btc_reference_usdt": btc,
            "btc_frozen_week_low_usdt": floor,
            "below_frozen_week_low_at_issuer_reference": btc < floor,
            "protection_risk": p,
            "data_status": stat,
            "action_now": act,
            "h1_3d": d1,
            "h5_7d": d5,
            "h2_3w": d2,
            "first_known_verification": "UNKNOWN",
            "website_delivery_verification": "UNKNOWN",
        })
    results.sort(key=lambda r: (r["issued_at_utc_claim"], r["archive_source_path"]))
    below = [r for r in results if r["below_frozen_week_low_at_issuer_reference"]]
    counts = lambda k: dict(sorted(Counter(row[k] for row in results).items()))
    first = lambda seq: seq[0]["issued_at_utc_claim"] if seq else None
    summary = {
        "contract": "W46_ORIGINAL_OFFICIAL_ISSUANCE_CENSUS_v1",
        "source_commit": PIN,
        "frozen_forecast_sha256": hashlib.sha256(frozen_forecast).hexdigest(),
        "issuance_rows": len(results),
        "btc_weekly_floor_usdt": floor,
        "risk_counts": counts("protection_risk"),
        "data_status_counts": counts("data_status"),
        "action_counts": counts("action_now"),
        "h1_3d_counts": counts("h1_3d"),
        "h5_7d_counts": counts("h5_7d"),
        "h2_3w_counts": counts("h2_3w"),
        "issuer_reference_below_floor_count": len(below),
        "issuer_reference_below_floor_elevated": sum(r["protection_risk"] == "ELEVATED" for r in below),
        "issuer_reference_below_floor_high": sum(r["protection_risk"] == "HIGH" for r in below),
        "first_issue_claim_utc": first(results),
        "first_below_floor_issue_claim_utc": first(below),
        "original_provider_first_known": "UNKNOWN",
        "first_market_trade_breach": "UNKNOWN",
        "site_delivery": "UNKNOWN",
        "cohort": "W46_EXPOSED_PARTIAL_NOT_HOLDOUT",
        "warning_skill": "NOT_ESTABLISHED",
        "severity_escalation_policy_change": False,
        "paper_action_utility": "NOT_MEASURED",
        "no_trade": True,
    }
    return summary, results

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--ref", default=PIN)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    if args.ref != PIN:
        raise ValueError("CENSUS_SOURCE_PIN_CHANGED")
    rows, freeze = load_frozen(args.repo_root, args.ref)
    report, table = summarize(rows, freeze)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "w46_official_issuance_summary.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    with (args.out_dir / "w46_official_issuance_rows.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    print("W46_FROZEN_CENSUS_PASS", report["issuance_rows"], report["risk_counts"],
          "below_floor", report["issuer_reference_below_floor_count"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
