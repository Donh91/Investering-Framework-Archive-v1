"""Independent W45 Thursday self-test outcome ledger, research only.

No prediction is generated here. The source prices and eight forecasts were
locked as GitHub issue comment 6668153478 on 2026-11-05T20:11:38Z. This
scorer never impersonates a Monday Cycle Navigator original issue or
upgrades unauthenticated provider-first-known timestamps.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.research.verify_w45_midweek_shadow_benchmark import parse_utc

UTC = timezone.utc
PACKET = Path("06_RESEARCH_LAB/mission_packets/2026-11-05__W45_THURSDAY_SELFTEST_v1.json")
HOURLY = Path("03_DAILY_CAPTURE_LOGS/hourly")
CONTRACT = "RESEARCH_W45_THURSDAY_SELFTEST_OUTCOMES_v1"
ISSUE = parse_utc("2026-11-05T20:11:38Z")
SOURCE_CUTOFF = parse_utc("2026-11-05T18:00:00Z")
FIRST_FUTURE_HOUR = parse_utc("2026-11-05T21:00:00Z")
EXPECTED = {
    "BTC": ((75573.64, 74143.64, 77417.33),
            (74670.48, 71871.41, 78516.89),
            (74133.78, 71354.82, 77578.57),
            (73813.61, 71046.66, 77020.96)),
    "ETH": ((2244.16, 2186.31, 2315.09),
            (2210.28, 2097.79, 2364.50),
            (2190.20, 2078.73, 2328.80),
            (2178.24, 2067.38, 2307.65)),
}
ANCHOR = {"BTC": (75952.45, 80427.66), "ETH": (2255.41, 2424.85)}
SOURCE_GIT_BLOBS = (
    "b9cdbc7696e1e91c903a694708a21f13c86b2f35",
    "2bfff1294bc7c571be13c703fa85c18ba9d78e2e",
    "3d4b79464daaa8263468b033fc71d4904ca3c0fb",
    "d3821a71aec0faf2181abdc3743b487cc368469e",
)


def stamp(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def valid(x: object) -> bool:
    return type(x) in (int, float) and math.isfinite(x) and x > 0


def verify_freeze(packet: dict) -> None:
    if (packet.get("contract") != "RESEARCH_W45_THURSDAY_SELFTEST_FREEZE_v1"
            or packet.get("forecast_week") != "2026-W45"
            or parse_utc(packet["first_public_issue_utc"]) != ISSUE
            or parse_utc(packet["last_input_source_close_utc"]) != SOURCE_CUTOFF
            or parse_utc(packet["first_wholly_prospective_hour_open_utc"]) != FIRST_FUTURE_HOUR
            or packet.get("original_comment_id") != 6668153478
            or packet.get("correction_comment_id") != 6668328354
            or packet.get("original_monday_W45_daily_issued") != {"BTC": 0, "ETH": 0}
            or packet.get("authority") != "RESEARCH_ONLY_NONCANONICAL_NO_PORTFOLIO_ACTION"
            or any(packet.get(k) is not False for k in (
                "scientific_first_known_verified", "official_scoring_eligible",
                "independent_edge_proven", "portfolio_action"))):
        raise ValueError("FROZEN_SELFTEST_OR_AUTHORITY_CHANGED")
    if tuple(packet.get("input_source_git_blobs", {}).values()) != SOURCE_GIT_BLOBS:
        raise ValueError("FROZEN_INPUT_GIT_BLOBS_CHANGED")
    assets = packet.get("assets")
    if not isinstance(assets, dict) or set(assets) != {"BTC", "ETH"}:
        raise ValueError("SELFTEST_ASSET_SET_CHANGED")
    for asset in ("BTC", "ETH"):
        meta = assets[asset]
        if (meta.get("pair") != asset + "USDT" or meta.get("quote") != "USDT"
                or (meta.get("anchor_close"), meta.get("prior_24h_close")) != ANCHOR[asset]
                or parse_utc(meta["anchor_hour_close_utc"]) != SOURCE_CUTOFF
                or not isinstance(meta.get("forecasts"), list)
                or len(meta["forecasts"]) != 4):
            raise ValueError("FROZEN_SELFTEST_ANCHOR_OR_QUOTE_CHANGED")
        for index, row in enumerate(meta["forecasts"]):
            day = 5 + index
            date = f"2026-11-{day:02d}"
            expected_target = parse_utc(f"2026-11-{day+1:02d}T00:00:00Z")
            if (row.get("day") != 4 + index
                    or row.get("utc_date") != date
                    or parse_utc(row["target_close_at_utc"]) != expected_target
                    or row.get("B0_flat_close") != ANCHOR[asset][0]
                    or (row.get("B1_conditional_close"), row.get("low"), row.get("high"))
                       != EXPECTED[asset][index]
                    or row.get("high_low_scope") != (
                        "THURSDAY_PARTIAL_UNSCORABLE_FULL_6H" if index == 0
                        else "FUTURE_FULL_UTC_DAY")
                    or not row["low"] <= row["B1_conditional_close"] <= row["high"]
                    or expected_target <= ISSUE):
                raise ValueError("FROZEN_SELFTEST_ROW_CHANGED")


def load_source(root: Path, now: datetime) -> dict:
    """No future rows, duplicates, fake OHLC, non-PASS source or silent units."""
    rows = {}
    for day in range(4, 9):
        date = f"2026-11-{day:02d}"
        path = root / HOURLY / "2026" / "11" / (date + ".csv")
        if not path.is_file():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            for line in csv.DictReader(handle):
                opened = parse_utc(line["timestamp_utc"])
                end = opened + timedelta(hours=1)
                captured = parse_utc(line["source_window_end_utc"])
                if (opened.minute or opened.second or opened.microsecond
                        or opened.date().isoformat() != date
                        or opened.tzinfo != UTC
                        or captured < end):
                    raise ValueError("SOURCE_HOUR_OR_CAPTURE_CLOCK_INVALID")
                # Newer source bytes are allowed, but not new observations
                # that were unavailable at the evaluation as-of.
                if end > now or captured > now:
                    continue
                if line.get("spot_status") != "PASS":
                    raise ValueError("SPOT_SOURCE_NOT_PASS")
                prices = {}
                for asset in ("BTC", "ETH"):
                    prefix = asset.lower()
                    try:
                        o, h, l, c = (float(line[prefix + "_" + k])
                                      for k in ("open", "high", "low", "close"))
                    except (KeyError, TypeError, ValueError) as exc:
                        raise ValueError("INVALID_SPOT_SOURCE_PRICE") from exc
                    if not (all(valid(x) for x in (o, h, l, c))
                            and l <= min(o, c) <= max(o, c) <= h):
                        raise ValueError("INVALID_SPOT_OHLC")
                    prices[asset] = {"close": c, "low": l, "high": h}
                if opened in rows:
                    raise ValueError("DUPLICATE_SOURCE_HOUR")
                rows[opened] = prices
    # Verify unchanged at-issue source anchors. 24h lookback exactly.
    for asset in ("BTC", "ETH"):
        for opened, expected in ((parse_utc("2026-11-05T17:00:00Z"), ANCHOR[asset][0]),
                                  (parse_utc("2026-11-04T17:00:00Z"), ANCHOR[asset][1])):
            if opened not in rows or rows[opened][asset]["close"] != expected:
                raise ValueError("ANCHOR_OR_PRIOR24_CHANGED_OR_MISSING")
    return rows


def compile_outcomes(packet: dict, root: Path, now: datetime) -> dict:
    if now.tzinfo is None:
        raise ValueError("UTC_NOW_REQUIRED")
    now = now.astimezone(UTC)
    verify_freeze(packet)
    original_blob_sha256 = hashlib.sha256(
        (root / PACKET).read_bytes()).hexdigest() if (root / PACKET).is_file() else None
    # After issuance only. The score is not an accredited source PIT or edge test.
    if now < ISSUE:
        source, source_state, failure = {}, "ISSUE_NOT_YET_PUBLIC", None
    else:
        try:
            source = load_source(root, now)
            source_state, failure = "PUBLIC_PASS_OHLC_NOT_PROVIDER_FIRST_KNOWN", None
        except (ValueError, KeyError, TypeError, OSError) as exc:
            source, source_state, failure = {}, "UNAVAILABLE_FAIL_CLOSED", str(exc).split(":")[0]
    output_rows = []
    for asset in ("BTC", "ETH"):
        for original in packet["assets"][asset]["forecasts"]:
            day = original["day"]
            target = parse_utc(original["target_close_at_utc"])
            date = original["utc_date"]
            count = 3 if day == 4 else 24
            start = FIRST_FUTURE_HOUR if day == 4 else parse_utc(date + "T00:00:00Z")
            hours = [start + timedelta(hours=i) for i in range(count)]
            wholly_future = all(h >= FIRST_FUTURE_HOUR for h in hours)
            complete = (source_state == "PUBLIC_PASS_OHLC_NOT_PROVIDER_FIRST_KNOWN"
                        and now >= target and wholly_future
                        and all(h in source for h in hours))
            outcome = (source[hours[-1]][asset]["close"] if complete else None)
            observed_low = (min(source[h][asset]["low"] for h in hours) if complete else None)
            observed_high = (max(source[h][asset]["high"] for h in hours) if complete else None)
            if now < target:
                state = "PENDING_UTC_TARGET"
            elif source_state != "PUBLIC_PASS_OHLC_NOT_PROVIDER_FIRST_KNOWN":
                state = "AWAITING_VERIFIED_SOURCE"
            elif not complete:
                state = "AWAITING_COMPLETE_FUTURE_UTC_CANDLES"
            else:
                state = "MATURED_PUBLIC_HOURLY_CAPTURE"
            mature = state == "MATURED_PUBLIC_HOURLY_CAPTURE"
            can_range_score = mature and day != 4
            output_rows.append({
                "asset": asset, "day": day, "utc_date": date,
                "target_close_at_utc": original["target_close_at_utc"],
                "B0_frozen_flat_close_USDT": original["B0_flat_close"],
                "B1_frozen_conditional_close_USDT": original["B1_conditional_close"],
                "original_low_USDT": original["low"], "original_high_USDT": original["high"],
                "original_band_scope": original["high_low_scope"],
                "observed_close_USDT": outcome if mature else None,
                "observed_post_issue_low_USDT": observed_low if mature else None,
                "observed_post_issue_high_USDT": observed_high if mature else None,
                "B0_absolute_pct_error": round(100 * abs(original["B0_flat_close"] / outcome - 1), 5) if mature else None,
                "B1_absolute_pct_error": round(100 * abs(original["B1_conditional_close"] / outcome - 1), 5) if mature else None,
                "range_state": (
                    "PARTIAL_THURSDAY_SIX_HOUR_COVERAGE_UNSCORABLE" if mature and day == 4
                    else ("FULL_UTC_DAY_CONTAINED" if observed_low >= original["low"] and
                          observed_high <= original["high"] else "FULL_UTC_DAY_BREACHED")
                    if can_range_score else "PENDING_SOURCE_OR_TARGET"),
                "width_pct_midpoint": round(200 * (original["high"] - original["low"]) /
                                            (original["high"] + original["low"]), 4),
                "source_hours_required": count,
                "source_hours_complete": sum(h in source for h in hours) if source_state == "PUBLIC_PASS_OHLC_NOT_PROVIDER_FIRST_KNOWN" else 0,
                "outcome_state": state
            })
    mature_rows = [r for r in output_rows if r["outcome_state"] == "MATURED_PUBLIC_HOURLY_CAPTURE"]
    return {
        "contract": CONTRACT, "forecast_week": "2026-W45",
        "created_at_utc": stamp(now), "original_issue_utc": stamp(ISSUE),
        "input_cutoff_utc": stamp(SOURCE_CUTOFF),
        "first_scored_future_hour_open_utc": stamp(FIRST_FUTURE_HOUR),
        "frozen_packet_sha256": original_blob_sha256,
        "source_state": source_state, "source_failure": failure,
        "provider_first_known_verified": False, "scientific_edge_proven": False,
        "official_scoring_eligible": False, "portfolio_action_authority": False,
        "research_only": True,
        "original_monday_daily_issued": {"BTC": 0, "ETH": 0},
        "matured_observations": len(mature_rows), "total_forecast_observations": 8,
        "full_daily_range_scored": sum(r["range_state"].startswith("FULL_UTC_DAY_") for r in mature_rows),
        "rows": output_rows,
    }


def compile_from_repo(root: Path, now: datetime | None = None) -> dict:
    clock = datetime.now(UTC) if now is None else now
    packet = json.loads((root / PACKET).read_text(encoding="utf-8"))
    return compile_outcomes(packet, root, clock)
