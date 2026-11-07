#!/usr/bin/env python3
"""Historical Reality Engine: bounded, source-hash-verified research pilot.

Retrospective source truth only, not an original 2020-2025 Kompas forecast.
Uses Binance publicly published monthly SPOT 1h archives with .CHECKSUM.
This is deliberately NOT a trading signal or official Cycle Navigator producer.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import re
import statistics
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

BASE = "https://data.binance.vision/data/spot/monthly/klines"
MAX_ARCHIVE_BYTES = 3_000_000
MAX_CSV_BYTES = 12_000_000
TZ = dt.timezone.utc
SOURCE_CLASS = "POSTHOC_PRICE_TRUTH_TAPE_NOT_ORIGINAL_PROVIDER_FIRST_KNOWN"
INFERENCE_CLASS = "RETROSPECTIVE_BASELINE_EXPERIMENT_NOT_OFFICIAL_KOMPAS"
KNOWN_SYMBOLS = {"BTCUSDT", "ETHUSDT"}
KNOWN_MONTHS = {
    "source": ["2020-02", "2020-03", "2025-09", "2025-10"],
    "crisis": ["2020-02", "2020-03", "2020-04", "2025-09", "2025-10"],
    "weekly": ["2021-02", "2021-03", "2021-04", "2021-05"],
}
FIXED_CRISIS_RULES = {
    "label": "forward_72h_low_from_closed_price_le_-8pct",
    "baseline_signal": "past_24h_close_return_le_-5pct",
    "challenger_signal": "past_24h_close_return_le_-3pct_AND_past_72h_high_to_low_drawdown_ge_8pct",
    "sample": "daily_UTC_at_00h_non_independent_72h_labels",
    "purpose": "diagnostic_only_no_preregistered_prospective_edge",
}
FIXED_WEEKLY_RULES = {
    "forecast_issue": "monday_00h_UTC_after_previous_Sunday_daily_close",
    "expected_close": "last_closed_daily_close_all_7_days",
    "range_baseline": "last_close_times_(1_plus_minus_2pct_times_sqrt(day_index))",
    "range_challenger": "last_close_times_(1_plus_minus_1.5_times_median_abs_prior_28_daily_return_times_sqrt(day_index))",
    "training_window": "28_complete_prior_UTC_days",
    "purpose": "historical_naive_control_only_NOT_CN_original_forecast",
}


@dataclass(frozen=True)
class Candle:
    open_ms: int
    close_ms: int  # nominal completed UTC hour boundary minus 1ms
    provider_last_trade_ms: int  # original source close-time field, may be intrabar
    o: float
    h: float
    l: float
    c: float
    volume: float


def _month_from_date(day: dt.datetime) -> str:
    return f"{day.year:04d}-{day.month:02d}"


def _decode_epoch(raw: str) -> int:
    n = int(raw)
    if n > 100_000_000_000_000:  # Binance spot from Jan 2025: microseconds
        # Provider close-time may be a LAST-TRADE timestamp with arbitrary microseconds.
        # Opening time is checked separately for exact hour alignment.
        return n // 1000
    if n < 1_500_000_000_000:
        raise ValueError("invalid epoch milliseconds")
    return n


def _limited_get(url: str, limit: int, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "HRE-source-qa/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("source payload exceeds byte budget")
    return data


def parse_binance_hourly(blob: bytes, expected_name: str, expected_month: str) -> list[Candle]:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = z.infolist()
        if len(names) != 1 or names[0].filename != expected_name:
            raise ValueError("unexpected ZIP member or archive path")
        member = names[0]
        if member.file_size > MAX_CSV_BYTES or member.compress_size > MAX_ARCHIVE_BYTES:
            raise ValueError("ZIP decompression budget exceeded")
        if member.is_dir() or (member.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError("archive contains forbidden entry type")
        contents = z.read(member)
        if len(contents) > MAX_CSV_BYTES:
            raise ValueError("uncompressed input exceeds budget")
    reader = csv.reader(io.StringIO(contents.decode("utf-8-sig")))
    candles: list[Candle] = []
    seen = set()
    gaps = []
    for row in reader:
        if not row:
            continue
        if row[0] in ("open_time", "Open time"):
            continue
        if len(row) < 7:
            raise ValueError("missing required Binance OHLC fields")
        opened = _decode_epoch(row[0])
        closed = _decode_epoch(row[6])
        vals = [float(v) for v in row[1:6]]
        if not all(math.isfinite(v) for v in vals) or vals[4] < 0:
            raise ValueError("nonfinite or negative volume")
        o, h, l, c, vol = vals
        if o <= 0 or l <= 0 or h < max(o, c) or l > min(o, c):
            raise ValueError("invalid OHLC candle")
        if opened in seen or opened % 3_600_000 or not 0 <= closed - opened < 3_600_000:
            raise ValueError(
                f"duplicate/bad hour or source close time, month={expected_month}, "
                f"raw_open={row[0]}, raw_close={row[6]}, open_ms={opened}, provider_close_ms={closed}, "
                f"delta_ms={closed-opened}, mod_hour_ms={opened%3_600_000}, duplicate={opened in seen}"
            )
        if _month_from_date(dt.datetime.fromtimestamp(opened / 1000, tz=TZ)) != expected_month:
            raise ValueError("candle outside filename month")
        if candles and opened <= candles[-1].open_ms:
            raise ValueError("unordered candles")
        if candles and opened - candles[-1].open_ms != 3_600_000:
            gaps.append((candles[-1].open_ms, opened))
        seen.add(opened)
        # A last trade at minute 35 does not make a one-hour candle complete.
        # The earliest research availability is AFTER the nominal UTC hour end.
        candles.append(Candle(opened, opened + 3_600_000 - 1, closed, o, h, l, c, vol))
    if len(candles) < 24 * 27 or gaps:
        raise ValueError(f"incomplete hourly month: candles={len(candles)}, gaps={len(gaps)}")
    return candles


def load_month(symbol: str, month: str, fetch=_limited_get):
    if symbol not in KNOWN_SYMBOLS or not re.fullmatch(r"20[0-2][0-9]-(0[1-9]|1[0-2])", month):
        raise ValueError("symbol/date not allowlisted")
    name = f"{symbol}-1h-{month}.zip"
    prefix = f"{BASE}/{symbol}/1h/{name}"
    raw = fetch(prefix, MAX_ARCHIVE_BYTES)
    digest = hashlib.sha256(raw).hexdigest()
    raw_checksum = fetch(prefix + ".CHECKSUM", 4096).decode("ascii", errors="strict")
    expected = re.match(r"^\s*([0-9a-fA-F]{64})\s+\*?(\S+)\s*$", raw_checksum.strip())
    if not expected or expected.group(2) != name or digest != expected.group(1).lower():
        raise ValueError("upstream source SHA256 CHECKSUM mismatch")
    data = parse_binance_hourly(raw, name.replace(".zip", ".csv"), month)
    return data, {
        "provider": "Binance Public Data",
        "provider_documentation": "https://github.com/binance/binance-public-data",
        "symbol": symbol, "instrument": "SPOT", "quote": "USDT",
        "interval": "1h", "month": month, "url": prefix,
        "sha256": digest, "zip_bytes": len(raw),
        "expected_sha256": expected.group(1).lower(),
        "observations": len(data),
        "provider_close_pre_nominal_bucket_end_count": sum(c.provider_last_trade_ms < c.close_ms for c in data),
        "completion_time_policy": "NOMINAL_HOUR_END_NOT_PROVIDER_LAST_TRADE_TIME",
        "first_open_utc": dt.datetime.fromtimestamp(data[0].open_ms/1000, TZ).isoformat(),
        "last_close_utc": dt.datetime.fromtimestamp((data[-1].close_ms+1)/1000, TZ).isoformat(),
        "source_first_known_at_original_market_time": None,
        "historical_data_class": SOURCE_CLASS
    }


def load_dataset(symbols: list[str], months: list[str], fetch=_limited_get):
    series = {}
    evidence = []
    for symbol in symbols:
        data = []
        for month in months:
            entries, item = load_month(symbol, month, fetch=fetch)
            data += entries
            evidence.append(item)
        data.sort(key=lambda x: x.open_ms)
        if len({c.open_ms for c in data}) != len(data):
            raise ValueError("duplicate candles across months")
        for prev, cur in zip(data, data[1:]):
            if cur.open_ms - prev.open_ms != 3_600_000:
                raise ValueError("cross-month gap")
        series[symbol] = data
    return series, evidence


def closed_as_of(rows: list[Candle], ref_ms: int) -> list[Candle]:
    # No current/incomplete candle is visible at decision timestamp.
    return [c for c in rows if c.close_ms < ref_ms]


def score_crisis(rows: list[Candle]):
    positives = {"baseline": {"tp": 0, "fp": 0, "fn": 0, "tn": 0},
                 "challenger": {"tp": 0, "fp": 0, "fn": 0, "tn": 0}}
    daily = []
    for i in range(72, len(rows) - 72):
        ref = rows[i]
        # Decisions are made after this entire completed hour. Use daily midnight
        # UTC settlement, never hourly overlapping labels as independent events.
        decision_ms = ref.close_ms + 1
        if decision_ms % 86_400_000:
            continue
        last24 = rows[i - 24]
        past72 = rows[i - 71:i + 1]
        future72 = rows[i + 1:i + 73]
        r24 = ref.c / last24.c - 1.0
        past_drawdown = min(c.l for c in past72) / max(c.h for c in past72) - 1.0
        future_worst = min(c.l for c in future72) / ref.c - 1.0
        severe = future_worst <= -0.08
        b = r24 <= -0.05
        challenger = r24 <= -0.03 and past_drawdown <= -0.08
        for key, alarm in [("baseline", b), ("challenger", challenger)]:
            positives[key][("tp" if severe else "fp") if alarm else ("fn" if severe else "tn")] += 1
        daily.append({"cutoff_utc": dt.datetime.fromtimestamp(decision_ms / 1000, TZ).isoformat(),
                      "past_24h_return": round(r24, 6),
                      "past_72h_high_to_low": round(past_drawdown, 6),
                      "forward_72h_worst_from_ref": round(future_worst, 6),
                      "severe_next_72h": severe,
                      "price_baseline_warning": b,
                      "price_challenger_warning": challenger})
    return {"rules": FIXED_CRISIS_RULES, "daily_cutoffs": len(daily),
            "overlap_warning": "Rolling 72h labels overlap: daily rows are not independent events.",
            "confusion_descriptive": positives, "sample_first": daily[:3],
            "worst_future_event": min(daily, key=lambda x:x["forward_72h_worst_from_ref"], default=None),
            "not_original_framework_warning": True}


def daily_candles(rows: list[Candle]):
    groups = {}
    for c in rows:
        day = dt.datetime.fromtimestamp(c.open_ms / 1000, TZ).date()
        groups.setdefault(day, []).append(c)
    result = {}
    for day, candles in sorted(groups.items()):
        if len(candles) != 24:
            continue
        if candles[0].open_ms != int(dt.datetime.combine(day, dt.time(), TZ).timestamp() * 1000):
            continue
        result[day] = {"o": candles[0].o, "h": max(c.h for c in candles),
                       "l": min(c.l for c in candles), "c": candles[-1].c}
    return result


def frozen_week_forecast(ordered_days: list[tuple], idx: int):
    if idx < 29 or idx + 7 > len(ordered_days):
        raise ValueError("insufficient 28-day past and 7-day outcome")
    day, _ = ordered_days[idx]
    if day.weekday() != 0:
        raise ValueError("not a Monday")
    training = ordered_days[idx-29:idx]
    if any((training[j+1][0] - training[j][0]).days != 1 for j in range(len(training)-1)):
        raise ValueError("training day gap")
    for k in range(1,8):
        if (ordered_days[idx+k-1][0] - day).days != k-1:
            raise ValueError("forecast horizon contains missing day")
    previous = [training[j][1]["c"] for j in range(len(training))]
    abs_returns = [abs(previous[j] / previous[j-1] - 1) for j in range(1,len(previous))]
    med_abs = statistics.median(abs_returns)
    reference = previous[-1]
    predicted = []
    for d in range(1, 8):
        day_out, actual = ordered_days[idx+d-1]
        naive_radius = min(.95, .02 * math.sqrt(d))
        challenger_radius = min(.95, med_abs * 1.5 * math.sqrt(d))
        naive_low, naive_high = reference * (1-naive_radius), reference * (1+naive_radius)
        alt_low, alt_high = reference * (1-challenger_radius), reference * (1+challenger_radius)
        predicted.append({
            "day": d, "utc_date": day_out.isoformat(),
            "frozen_expected_close": round(reference, 5),
            "naive_low": round(naive_low, 5), "naive_high": round(naive_high, 5),
            "alternative_low": round(alt_low, 5), "alternative_high": round(alt_high, 5),
            "actual_close": round(actual["c"], 5), "actual_low": round(actual["l"], 5),
            "actual_high": round(actual["h"], 5),
            "naive_full_range_covered": actual["l"] >= naive_low and actual["h"] <= naive_high,
            "alternative_full_range_covered": actual["l"] >= alt_low and actual["h"] <= alt_high,
        })
    return {"freeze_utc": day.isoformat() + "T00:00:00Z",
            "source_cutoff": ordered_days[idx-1][0].isoformat() + "T23:59:59.999Z",
            "reference_closed_price": round(reference, 5),
            "prior_28d_abs_return_median": round(med_abs, 7),
            "days": predicted}


def score_weekly(rows: list[Candle]):
    days = list(daily_candles(rows).items())
    forecasts = []
    for i, (date, _) in enumerate(days):
        if date.weekday() == 0 and i >= 29 and i + 7 <= len(days):
            forecasts.append(frozen_week_forecast(days, i))
    if not forecasts:
        raise ValueError("not enough complete historical Mondays")
    all_d = [d for w in forecasts for d in w["days"]]
    return {
        "rules": FIXED_WEEKLY_RULES,
        "weekly_freezes": len(forecasts),
        "daily_points": len(all_d),
        "naive_full_range_coverage": sum(d["naive_full_range_covered"] for d in all_d)/len(all_d),
        "alternative_full_range_coverage": sum(d["alternative_full_range_covered"] for d in all_d)/len(all_d),
        "naive_mean_relative_interval_width": statistics.mean((d["naive_high"]-d["naive_low"])/d["frozen_expected_close"] for d in all_d),
        "alternative_mean_relative_interval_width": statistics.mean((d["alternative_high"]-d["alternative_low"])/d["frozen_expected_close"] for d in all_d),
        "mean_abs_expected_close_error_pct": statistics.mean(abs(d["actual_close"]/d["frozen_expected_close"]-1)*100 for d in all_d),
        "first_week": forecasts[0],
        "last_week": forecasts[-1],
        "note": "RETROSPECTIVE PRICE-ONLY BENCHMARK, not any originally issued CN forecast, incomplete 2026 W45 unchanged."
    }


def run(lane: str) -> dict:
    if lane not in KNOWN_MONTHS:
        raise ValueError("unsupported lane")
    months = KNOWN_MONTHS[lane]
    symbols = ["BTCUSDT", "ETHUSDT"]
    output = {"contract": "HRE_NATIVE_RESEARCH_PILOT_V1", "lane": lane,
              "source_class": SOURCE_CLASS, "scientific_class": INFERENCE_CLASS,
              "issuance": "NONE", "original_2020_2025_kompas_forecasts": 0,
              "scientific_edge_admitted": False, "live_authority": False,
              "source_historical_revision_after_outcome": True,
              "months": months, "assets": symbols,
              "verified_file_receipts": [], "results": {}, "execution_state": "SUCCESS_WITH_RETROSPECTIVE_LIMITS"}
    # Two historical periods are independent sequences, never bridge a 2020
    # candle directly to a 2025 candle as if missing hours were a quiet market.
    groups = {}
    for month in months:
        groups.setdefault(month[:4], []).append(month)
    for year, group_months in sorted(groups.items()):
        data, receipts = load_dataset(symbols, group_months)
        output["verified_file_receipts"].extend(receipts)
        for symbol, series in data.items():
            key = f"{symbol}_{year}"
            if lane == "source":
                output["results"][key] = {
                    "hourly_candles": len(series),
                    "min_low": min(c.l for c in series),
                    "max_high": max(c.h for c in series),
                    "closed_candle_at_reference_test": len(closed_as_of(series, series[72].open_ms)),
                    "source_admission": "POSTHOC_PUBLIC_PRICE_SOURCE_QA_ONLY"
                }
            elif lane == "crisis":
                output["results"][key] = score_crisis(series)
            else:
                output["results"][key] = score_weekly(series)
    return output


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lane", choices=sorted(KNOWN_MONTHS), required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    result = run(a.lane)
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    result["receipt_sha256_without_self_digest"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"HRE_NATIVE_LANE_COMPLETE lane={a.lane} source_files={len(result['verified_file_receipts'])} output={path}")
    for key, row in result["results"].items():
        if a.lane == "crisis":
            print(f"HRE_DESCRIPTIVE_CRISIS {key} cutoffs={row['daily_cutoffs']} price_baseline={row['confusion_descriptive']['baseline']} candidate={row['confusion_descriptive']['challenger']}")
        elif a.lane == "weekly":
            print(f"HRE_DESCRIPTIVE_WEEKLY {key} freezes={row['weekly_freezes']} daily_points={row['daily_points']} naive_coverage={row['naive_full_range_coverage']:.4f} alternative_coverage={row['alternative_full_range_coverage']:.4f} close_mae_pct={row['mean_abs_expected_close_error_pct']:.4f}")
        else:
            print(f"HRE_SOURCE_QA {key} observations={row['hourly_candles']} admission={row['source_admission']}")
    print("SCIENCE_GATE: RETROSPECTIVE_ONLY_NOT_ORIGINAL_FORECAST_NOT_PROVEN_EDGE")


if __name__ == "__main__":
    main()
