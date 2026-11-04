"""Read-only replay of the 5 Nov W45 shadow forecast candidate.

Not a CN publisher, site source, calibrated probability or portfolio signal.
PIT scientific admission remains unavailable until upstream provider first-known
and independent comparative controls are established.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


CONTRACT = "RESEARCH_W45_MIDWEEK_FORWARD_BENCHMARK_v1"


def parse_utc(s: str) -> datetime:
    if not isinstance(s, str) or not s.endswith("Z"):
        raise ValueError("UTC_SOURCE_CLOCK_REQUIRED")
    at = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if at.utcoffset() != timedelta():
        raise ValueError("UTC_SOURCE_CLOCK_REQUIRED")
    return at


def money(x: float) -> float:
    if not math.isfinite(x) or x <= 0:
        raise ValueError("INVALID_POSITIVE_PRICE")
    return math.floor(x * 100 + 0.5) / 100


def recompute(packet: dict) -> dict:
    if packet.get("contract") != CONTRACT or packet.get("forecast_week") != "2026-W45":
        raise ValueError("RESEARCH_IDENTITY_MISMATCH")
    if packet.get("category") != "SHADOW_RESEARCH_ONLY_NOT_ORIGINAL_CN_ISSUANCE":
        raise ValueError("FALSE_FORECAST_AUTHORITY")
    source = packet["source"]
    if (source.get("completed_prior_week_hours") != 168 or
            source.get("current_week_observed_hours") != 70 or
            source.get("provider_first_known_verified") is not False):
        raise ValueError("FALSE_SOURCE_PROVENANCE")
    if source.get("assets_quote") != "USDT" or len(source.get("file_blobs", [])) != 10:
        raise ValueError("UNVERIFIED_SOURCE_QUOTE_OR_FILES")
    original = packet.get("original_W45_daily_price_path_status") or {}
    if original != {"BTC": "UNAVAILABLE", "ETH": "UNAVAILABLE"}:
        raise ValueError("ORIGINAL_FORECAST_MISREPRESENTED")
    forecast = packet["forecast"]
    for forbidden in ("source_admitted_for_official_CN", "site_blue_original_forecast_eligible",
                      "official_scoring_eligible", "portfolio_action_authority"):
        if forecast.get(forbidden) is not False:
            raise ValueError("RESEARCH_AUTHORITY_LEAK")
    origin = parse_utc(packet["generated_at_utc"])
    if parse_utc(forecast["origin_utc"]) != origin:
        raise ValueError("ISSUANCE_CLOCK_MISMATCH")
    rows = packet["observations"]
    if not isinstance(rows, list) or len(rows) != 238:
        raise ValueError("SOURCE_SAMPLE_COUNT_INVALID")
    prev = None
    for row in rows:
        at = parse_utc(row["candle_close_at_utc"])
        known_by = parse_utc(row["source_window_end_utc"])
        if known_by < at or known_by > origin:
            raise ValueError("CAPTURE_TIME_BEFORE_CANDLE_OR_AFTER_ISSUE")
        if prev is not None and at - prev != timedelta(hours=1):
            raise ValueError("MISSING_DUPLICATE_OR_UNSORTED_HOUR")
        for asset in ("BTC", "ETH"):
            p = row[asset + "_USDT"]
            if type(p) not in (float, int) or not math.isfinite(p) or p <= 0:
                raise ValueError("BAD_OBSERVED_SOURCE_PRICE")
        prev = at
    if (parse_utc(rows[167]["candle_close_at_utc"]) !=
            parse_utc("2026-11-02T00:00:00Z") or
            parse_utc(rows[-1]["candle_close_at_utc"]) !=
            parse_utc("2026-11-04T22:00:00Z") or
            source["observed_as_of_utc"] != rows[-1]["candle_close_at_utc"] or
            origin <= prev or origin >= parse_utc("2026-11-06T00:00:00Z")):
        raise ValueError("W45_RESEARCH_PIT_BOUNDARY_INVALID")

    out = {}
    for asset in ("BTC", "ETH"):
        key = asset + "_USDT"
        anchor, old = rows[-1][key], rows[-25][key]
        recent_log = math.log(anchor / old)
        lr = [math.log(rows[i][key] / rows[i-1][key])
              for i in range(1, len(rows))]
        mean = sum(lr) / len(lr)
        sigma = math.sqrt(sum((x-mean)**2 for x in lr) / (len(lr)-1))
        projected = []
        for i in range(4):
            growth = sum(max(-0.02, min(0.02, .35 * recent_log * .6**j))
                         for j in range(i+1))
            widen = math.exp(1.5 * sigma * math.sqrt(24*(i+1)))
            day = 4+i
            projected.append({
                "day": day,
                "utc_date": f"2026-11-{5+i:02d}",
                "target_close_at_utc": f"2026-11-{6+i:02d}T00:00:00Z",
                "B0_persistence_expected_close": money(anchor),
                "B1_decay_momentum_expected_close": money(anchor * math.exp(growth)),
                "heuristic_terminal_close_low": money(anchor / widen),
                "heuristic_terminal_close_high": money(anchor * widen),
            })
        out[asset] = projected
    return out


def verify(packet: dict) -> dict:
    computed = recompute(packet)
    supplied = packet["forecast"]["assets"]
    for asset in ("BTC", "ETH"):
        if supplied[asset]["forecast"] != computed[asset]:
            raise ValueError("RESEARCH_FORECAST_SOURCE_RECOMPUTATION_MISMATCH")
    return {"status": "PASS_RESEARCH_ONLY", "rows": 238, "forecast_points": 8,
            "official_cn_issued_points": 0, "assets": ["BTC", "ETH"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    result = verify(json.loads(args.packet.read_text()))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
