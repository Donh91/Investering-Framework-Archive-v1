#!/usr/bin/env python3
"""Cycle Navigator public release receipt. SOURCE -> rendered hourly data, no new collector.

Read-only checks of canonical PUBLIC hourly PASS/OK rows and the frozen
issue-bound Pages bundle. Never promotes shadow prices, never fills gaps,
never calls an external provider. Runs inside the EXISTING Pages job.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.cycle_navigator.build_public_live_precision import (
    load_hourly_rows, public_hourly_price_path, parse_utc,
)


class PublicationLineageError(ValueError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise PublicationLineageError(code)


def validate_projection(expected: dict, actual: dict) -> None:
    require(isinstance(actual, dict), "PUBLIC_HOURLY_MISSING")
    require(actual.get("contract") == "CN_PUBLIC_HOURLY_PRICE_PATH_v1", "PUBLIC_HOURLY_CONTRACT")
    for key in ("forecast_week", "public_issue_number", "source", "semantics", "observed_through_utc"):
        require(actual.get(key) == expected.get(key), "PUBLIC_HOURLY_BINDING_" + key.upper())
    for asset in ("BTC", "ETH"):
        require(isinstance(actual.get(asset), list), "PUBLIC_HOURLY_ASSET_MISSING_" + asset)
        require(actual[asset] == expected[asset], "PUBLIC_HOURLY_PRICE_DIVERGENCE_" + asset)
        dates = [x.get("observed_at_utc") for x in actual[asset]]
        require(len(dates) == len(set(dates)), "PUBLIC_HOURLY_DUPLICATE_" + asset)
        require(all(set(x) == {"observed_at_utc", "close"} for x in actual[asset]),
                "PUBLIC_HOURLY_EXTRA_FIELDS_" + asset)
        require(all(isinstance(x["close"], (int, float)) and
                    x["close"] > 0 and x["close"] < 100000000
                    for x in actual[asset]), "PUBLIC_HOURLY_PRICE_INVALID_" + asset)


def receipt_for(root: Path, snapshot: dict, current: datetime) -> dict:
    precision = snapshot.get("public_live_precision") or {}
    require(precision.get("contract") == "CN_PUBLIC_LIVE_PRICE_PRECISION_v1",
            "PUBLIC_LIVE_PRECISION_NOT_BOUND")
    week = precision.get("forecast_week")
    issue = precision.get("public_issue_number")
    require(isinstance(week, str) and len(week) == 8 and "-W" in week,
            "PUBLIC_ISSUE_WEEK_INVALID")
    try:
        year, w = (int(x) for x in week.split("-W", 1))
    except ValueError as exc:
        raise PublicationLineageError("PUBLIC_ISSUE_WEEK_INVALID") from exc
    require(isinstance(issue, int) and issue > 0 and 1 <= w <= 53,
            "PUBLIC_ISSUE_INVALID")
    series = snapshot.get("public_series") or {}
    original = series.get("current_public_projection") or {}
    require(original.get("forecast_week") == week and
            original.get("public_issue_number") == issue,
            "PUBLIC_FROZEN_ISSUE_MISMATCH")

    actual = precision.get("hourly_price_path")
    cutoff = parse_utc(actual["observed_through_utc"]) if isinstance(actual, dict) and actual.get("observed_through_utc") else None
    hourly = load_hourly_rows(root, year, w)
    # The public producer's original cutoff is derived exclusively from first-known
    # PASS/OK hourly evidence. A source re-capture cannot silently widen that cutoff.
    expected_cutoff = parse_utc(hourly[-1]["timestamp_utc"]) + timedelta(hours=1) if hourly else None
    require(cutoff == expected_cutoff, "PUBLIC_HOURLY_OBSERVATION_CUTOFF_MISMATCH")
    expected = public_hourly_price_path(hourly, year, w, issue, cutoff, now=current)
    validate_projection(expected, actual)

    published = [x["observed_at_utc"] for a in ("BTC", "ETH") for x in actual[a]]
    last_published = max(published) if published else None
    last_at = parse_utc(last_published) if last_published else None
    lag = round((current - last_at).total_seconds() / 60, 2) if last_at else None
    require(lag is None or lag >= -1, "PUBLIC_HOURLY_FUTURE_OBSERVATION")
    sla = precision.get("freshness_sla_minutes")
    require(isinstance(sla, int) and sla > 0, "PUBLIC_FRESHNESS_SLA_INVALID")
    state = "NO_VERIFIED_OBSERVATIONS" if lag is None else (
        "WITHIN_SLA_AT_BUNDLE_TIME" if lag <= sla else "STALE_AT_BUNDLE_TIME"
    )
    return {
        "contract": "CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1",
        "semantics": "PUBLIC_BUNDLE_BUILD_TIME_EVIDENCE_NOT_LIVE_CLIENT_FRESHNESS",
        "authority": "READ_ONLY_RECONCILIATION_NO_FORECAST_OR_TRADING_AUTHORITY",
        "forecast_week": week,
        "public_issue_number": issue,
        "observed_through_utc": actual.get("observed_through_utc"),
        "last_observed_close_utc": last_published,
        "source_eligible_hourly_rows": len(hourly),
        "published_points": {"BTC": len(actual["BTC"]), "ETH": len(actual["ETH"])},
        "source_to_public_equality": "PASS",
        "release_freshness_state": state,
        "release_age_minutes": lag,
        "freshness_sla_minutes": sla,
        "checked_at_utc": current.isoformat().replace("+00:00", "Z"),
        "prospective_forecast_points_created": 0,
    }


def self_test() -> None:
    row = {
        "timestamp_utc": "2026-10-19T00:00:00Z", "spot_status": "PASS",
        "btc_low": "81000", "btc_high": "82500", "btc_close": "82000",
        "eth_low": "2200", "eth_high": "2300", "eth_close": "2250"
    }
    cutoff = datetime(2026, 10, 19, 1, tzinfo=timezone.utc)
    first = public_hourly_price_path([row], 2026, 43, 30, cutoff, now=cutoff)
    validate_projection(first, first)
    assert len(first["BTC"]) == len(first["ETH"]) == 1
    for changed, code in [
        ({**first, "forecast_week": "2026-W42"}, "PUBLIC_HOURLY_BINDING_FORECAST_WEEK"),
        ({**first, "BTC": []}, "PUBLIC_HOURLY_PRICE_DIVERGENCE_BTC"),
        ({**first, "BTC": first["BTC"] * 2}, "PUBLIC_HOURLY_PRICE_DIVERGENCE_BTC"),
        ({**first, "ETH": [{**first["ETH"][0], "expected_close": 2300}]},
         "PUBLIC_HOURLY_PRICE_DIVERGENCE_ETH"),
        ({**first, "observed_through_utc": "2026-10-20T02:00:00Z"},
         "PUBLIC_HOURLY_BINDING_OBSERVED_THROUGH_UTC"),
    ]:
        try:
            validate_projection(first, changed)
        except PublicationLineageError as exc:
            assert str(exc) == code, (code, str(exc))
        else:
            raise AssertionError("Negative guard did not reject " + code)
    assert public_hourly_price_path([{**row, "spot_status": "FAIL"}], 2026, 43, 30, cutoff, now=cutoff)["BTC"] == []
    assert public_hourly_price_path([{**row, "btc_close": "999999"}], 2026, 43, 30, cutoff, now=cutoff)["BTC"] == []
    print("PASS publication lineage positive, source gap, rejected status, privacy and five negative mutation guards")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    snapshot_path = args.root / "05_CYCLE_NAVIGATOR/site/dist/data/latest.json"
    require(snapshot_path.is_file(), "PUBLIC_BUNDLE_MISSING")
    snapshot = json.loads(snapshot_path.read_text())
    result = receipt_for(args.root, snapshot, datetime.now(timezone.utc))
    out = args.root / "05_CYCLE_NAVIGATOR/site/dist/data/publication-lineage.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
