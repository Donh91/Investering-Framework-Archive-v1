#!/usr/bin/env python3
"""Task2 Challenger A: horizon-scaled volatility band, recalibrated weekly.

Pre-registered challenger to the frozen Cycle Navigator (CN) daily bands
(Task2 #1596, track 1 "Forecast Intelligence"). Research only: it issues no
official forecast, grants no trading, release or promotion authority, and
reads only public hourly Binance closes already committed to this repository.

Model (frozen by CHALLENGER_A_SQRT_T_VOL_BAND_PREREG_v1.json):
  P0     last hourly close fully closed at or before the issue clock T0
  sigma  sample std of the last 168 hourly log returns ending at P0
  h_k    hours from T0 to the end of UTC day k (k = 1..7 of the ISO week)
  band   P0 * exp(+-z_q * sigma * sqrt(h_k)), separately for the day's
         full range (low/high) and for the day's close
  z_q    q-quantile of the "needed z" of every completed asset-day in the
         4 ISO weeks before the issue week (proxy issue clock Monday 08:00Z),
         at least 40 rows, else 8 weeks, else the registered seed.

The weekly recalibration is the "learns week by week" rule. It uses only
days completed before T0, so every issuance is point-in-time by construction.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Iterable

CONTRACT = "TASK2_CHALLENGER_A_SQRT_T_VOL_BAND_v1"
FORMULA_VERSION = "A1"
PARAMS = {
    "sigma_window_hours": 168,
    "calibration_weeks": 4,
    "fallback_calibration_weeks": 8,
    "calibration_min_rows": 40,
    "calibration_issue_proxy_utc": "Monday 08:00",
    "quantiles": [0.5, 0.8, 0.95],
    "primary_quantile": 0.8,
    "alpha_primary": 0.2,
    "min_scored_bars_per_day": 6,
    "assets": ["BTC", "ETH"],
}
# Registered seed, used only when fewer than 40 calibration rows exist.
# Derived with this module from ISO weeks 2026-W42..W45 (see the pre-registration).
SEED_Z = {
    "range": {"0.5": 0.966374, "0.8": 1.506929, "0.95": 2.168776},
    "close": {"0.5": 0.639317, "0.8": 1.062982, "0.95": 1.572239},
}
HOURLY_DIR = "03_DAILY_CAPTURE_LOGS/hourly"
FREEZE_PATH = "05_CYCLE_NAVIGATOR/weekly/{year}/W{week:02d}/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
HOUR = dt.timedelta(hours=1)
DAY = dt.timedelta(days=1)
COLS = {"BTC": ("btc_close", "btc_high", "btc_low"), "ETH": ("eth_close", "eth_high", "eth_low")}


def utc(value: str) -> dt.datetime:
    t = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timestamp must carry a timezone")
    return t.astimezone(dt.timezone.utc)


def iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def week_monday(year: int, week: int) -> dt.datetime:
    return dt.datetime.fromisocalendar(year, week, 1).replace(tzinfo=dt.timezone.utc)


def _positive(value) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return x if math.isfinite(x) and x > 0 else None


def load_hourly(root: Path, start: dt.datetime, end: dt.datetime) -> dict:
    """{open_time: {asset: (close, high, low)}} for bars with start <= open < end."""
    bars: dict = {}
    day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    while day < end:
        path = root / HOURLY_DIR / f"{day:%Y}" / f"{day:%m}" / f"{day:%Y-%m-%d}.csv"
        if path.is_file():
            with path.open(newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    try:
                        t = utc(row["timestamp_utc"])
                    except (KeyError, ValueError):
                        continue
                    if not start <= t < end:
                        continue
                    rec = {}
                    for asset, (c, h, l) in COLS.items():
                        vals = (_positive(row.get(c)), _positive(row.get(h)), _positive(row.get(l)))
                        if None not in vals and vals[2] <= vals[0] <= vals[1]:
                            rec[asset] = vals
                    if rec:
                        bars[t] = rec
        day += DAY
    return bars


def sigma_at(bars: dict, asset: str, t0: dt.datetime) -> tuple[float, float, str]:
    """(sigma, P0, P0 bar open time) from bars fully closed at or before t0."""
    n = PARAMS["sigma_window_hours"]
    times = sorted(t for t, r in bars.items() if t + HOUR <= t0 and asset in r)
    times = times[-(n + 1):]
    if len(times) != n + 1 or times[-1] - times[0] != n * HOUR:
        raise ValueError(f"{asset}: need {n + 1} consecutive closed hourly bars before {iso(t0)}")
    closes = [bars[t][asset][0] for t in times]
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    mean = sum(rets) / len(rets)
    sd = math.sqrt(sum((r - mean) ** 2 for r in rets) / (len(rets) - 1))
    if not sd > 0:
        raise ValueError(f"{asset}: zero volatility window")
    return sd, closes[-1], iso(times[-1])


def day_windows(monday: dt.datetime, t0: dt.datetime) -> list[tuple[int, dt.datetime, dt.datetime, float]]:
    """(k, scored_from, day_end, h_k). Day k is scored only on bars opening at or after T0."""
    first = t0.replace(minute=0, second=0, microsecond=0)
    if first < t0:
        first += HOUR
    out = []
    for k in range(1, 8):
        start, end = monday + (k - 1) * DAY, monday + k * DAY
        if end <= t0:
            continue
        out.append((k, max(start, first), end, (end - t0).total_seconds() / 3600))
    return out


def realized(bars: dict, asset: str, start: dt.datetime, end: dt.datetime):
    rows = [(t, bars[t][asset]) for t in sorted(bars) if start <= t < end and asset in bars[t]]
    if len(rows) < PARAMS["min_scored_bars_per_day"] or rows[-1][0] + HOUR != end:
        return None  # immature or incomplete day: never scored, never used for calibration
    return {"low": min(r[2] for _, r in rows), "high": max(r[1] for _, r in rows), "close": rows[-1][1][0], "bars": len(rows)}


def needed_z_rows(bars: dict, year: int, week: int) -> list[dict]:
    """Calibration rows for one past week, with the registered proxy issue clock."""
    monday = week_monday(year, week)
    t0 = monday + dt.timedelta(hours=8)
    rows = []
    for asset in PARAMS["assets"]:
        try:
            sd, p0, _ = sigma_at(bars, asset, t0)
        except ValueError:
            continue
        for k, start, end, h in day_windows(monday, t0):
            r = realized(bars, asset, start, end)
            if r is None:
                continue
            s = sd * math.sqrt(h)
            rows.append({"week": f"{year}-W{week:02d}", "asset": asset, "day": k,
                         "z_range": max(math.log(p0 / r["low"]), math.log(r["high"] / p0)) / s,
                         "z_close": abs(math.log(r["close"] / p0)) / s})
    return rows


def quantile(values: list[float], q: float) -> float:
    xs = sorted(values)
    return xs[min(len(xs) - 1, max(0, math.ceil(q * len(xs)) - 1))]


def calibrate(bars: dict, year: int, week: int) -> dict:
    """z per family and quantile from completed weeks strictly before the issue week."""
    monday = week_monday(year, week)
    for n_weeks in (PARAMS["calibration_weeks"], PARAMS["fallback_calibration_weeks"]):
        rows = []
        for back in range(n_weeks, 0, -1):
            y, w, _ = (monday - back * 7 * DAY).isocalendar()
            rows += needed_z_rows(bars, y, w)
        if len(rows) >= PARAMS["calibration_min_rows"]:
            z = {fam: {str(q): round(quantile([r["z_" + fam] for r in rows], q), 6) for q in PARAMS["quantiles"]}
                 for fam in ("range", "close")}
            return {"source": f"ROLLING_{n_weeks}W", "rows": len(rows), "z": z}
    if any(v is None for fam in SEED_Z.values() for v in fam.values()):
        raise ValueError("insufficient calibration rows and no registered seed")
    return {"source": "REGISTERED_SEED", "rows": 0, "z": SEED_Z}


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def issue(bars: dict, year: int, week: int, t0: dt.datetime) -> dict:
    """Frozen weekly issuance. Uses only bars closed by T0 and days completed before the week."""
    monday = week_monday(year, week)
    if not monday <= t0 < monday + 7 * DAY:
        raise ValueError("issue clock must fall inside the target ISO week")
    past = {t: r for t, r in bars.items() if t + HOUR <= t0}
    cal = calibrate(past, year, week)
    assets = {}
    for asset in PARAMS["assets"]:
        sd, p0, p0_bar = sigma_at(past, asset, t0)
        days = []
        for k, start, end, h in day_windows(monday, t0):
            s = sd * math.sqrt(h)
            band = {fam: {q: [round(p0 * math.exp(-z * s), 2), round(p0 * math.exp(z * s), 2)]
                          for q, z in cal["z"][fam].items()} for fam in ("range", "close")}
            days.append({"day": k, "scored_from_utc": iso(start), "end_utc": iso(end), "h": round(h, 4), "band": band})
        assets[asset] = {"P0": p0, "P0_bar_open_utc": p0_bar, "sigma_hourly": round(sd, 8), "days": days}
    body = {"contract": CONTRACT, "formula_version": FORMULA_VERSION, "week": f"{year}-W{week:02d}",
            "issue_clock_utc": iso(t0), "calibration": cal, "assets": assets,
            "authority": {"research_only": True, "official_forecast": False, "trading": False, "promotion": False}}
    body["issuance_sha256"] = _digest(body)
    return body


def interval_score(low: float, high: float, x: float, alpha: float) -> float:
    if not 0 < alpha < 1 or not 0 < low <= high:
        raise ValueError("invalid interval")
    return (high - low) + (2 / alpha) * (max(0.0, low - x) + max(0.0, x - high))


def cn_bands(freeze: dict, asset: str) -> dict:
    pts = (((freeze.get("daily_range_plan") or {}).get(asset) or {}).get("points")) or []
    out = {}
    for p in pts:
        lo, hi = _positive(p.get("low")), _positive(p.get("high"))
        if isinstance(p.get("day"), int) and lo and hi and lo < hi:
            out[p["day"]] = (lo, hi)
    return out


def score(issuance: dict, bars: dict, freeze: dict | None = None) -> dict:
    """Score matured days for A (all quantiles) and, when given, CN on the same rows."""
    alpha, q = PARAMS["alpha_primary"], str(PARAMS["primary_quantile"])
    rows = []
    for asset, a in issuance["assets"].items():
        cn = cn_bands(freeze, asset) if freeze else {}
        for d in a["days"]:
            r = realized(bars, asset, utc(d["scored_from_utc"]), utc(d["end_utc"]))
            if r is None:
                continue
            p0 = a["P0"]
            row = {"asset": asset, "day": d["day"], "bars": r["bars"]}
            for fam in ("range", "close"):
                for qq, (lo, hi) in d["band"][fam].items():
                    ok = (lo <= r["low"] and r["high"] <= hi) if fam == "range" else (lo <= r["close"] <= hi)
                    row[f"A_{fam}_{qq}_covered"] = int(ok)
            lo, hi = d["band"]["close"][q]
            row["A_interval_score"] = interval_score(lo, hi, r["close"], alpha) / p0
            row["A_width"] = (hi - lo) / p0
            lo, hi = d["band"]["range"][q]
            row["A_range_covered"] = int(lo <= r["low"] and r["high"] <= hi)
            if d["day"] in cn:
                lo, hi = cn[d["day"]]
                row["CN_interval_score"] = interval_score(lo, hi, r["close"], alpha) / p0
                row["CN_width"] = (hi - lo) / p0
                row["CN_range_covered"] = int(lo <= r["low"] and r["high"] <= hi)
            rows.append(row)
    agg = {}
    if rows:
        keys = sorted({k for r in rows for k in r if k.endswith(("_covered", "_score", "_width"))})
        for k in keys:
            vals = [r[k] for r in rows if k in r]
            agg[k] = {"n": len(vals), "mean": round(sum(vals) / len(vals), 6)}
    both = [r for r in rows if "CN_interval_score" in r]
    week_winner = None
    if both:
        a_m = sum(r["A_interval_score"] for r in both) / len(both)
        c_m = sum(r["CN_interval_score"] for r in both) / len(both)
        week_winner = "A" if a_m < c_m else ("CN" if c_m < a_m else "TIE")
    return {"contract": CONTRACT + "_SCORE", "week": issuance["week"], "issuance_sha256": issuance["issuance_sha256"],
            "matured_rows": len(rows), "rows": rows, "aggregate": agg,
            "paired_rows": len(both), "week_winner_interval_score": week_winner,
            "note": "Research score. One week is one cluster; no promotion before the registered decision rule."}


def sign_test_p(wins: int, losses: int) -> float:
    """Two-sided exact sign test over week clusters; ties excluded."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def t0_from_git(root: Path, year: int, week: int) -> dt.datetime:
    """First-in-main time of the CN week freeze; requires full git history."""
    path = FREEZE_PATH.format(year=year, week=week)
    out = subprocess.run(["git", "-C", str(root), "log", "--diff-filter=A", "--format=%cI", "--", path],
                         capture_output=True, text=True, check=True).stdout.split()
    if not out:
        raise ValueError(f"no git history for {path}")
    return min(utc(x) for x in out)


def _parse_week(s: str) -> tuple[int, int]:
    y, w = s.split("-W")
    return int(y), int(w)


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["issue", "score"])
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--week", required=True, help="ISO week, e.g. 2026-W47")
    ap.add_argument("--t0", help="issue clock (ISO-8601 UTC); default: CN freeze first-in-main")
    ap.add_argument("--output", required=True)
    a = ap.parse_args(list(argv) if argv is not None else None)
    root = Path(a.repo_root)
    year, week = _parse_week(a.week)
    t0 = utc(a.t0) if a.t0 else t0_from_git(root, year, week)
    monday = week_monday(year, week)
    bars = load_hourly(root, monday - 70 * DAY, monday + 7 * DAY)
    result = issue(bars, year, week, t0)
    if a.command == "score":
        fp = root / FREEZE_PATH.format(year=year, week=week)
        freeze = json.loads(fp.read_text(encoding="utf-8")) if fp.is_file() else None
        result = score(result, bars, freeze)
    Path(a.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"contract": result["contract"], "week": result["week"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
