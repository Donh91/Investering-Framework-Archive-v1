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
import re
import subprocess
from pathlib import Path
from typing import Iterable

CONTRACT = "TASK2_CHALLENGER_A_SQRT_T_VOL_BAND_v1"
FORMULA_VERSION = "A1"
DECISION = {
    "first_week": "2026-W47",
    "confirmatory_valid_weeks": 8,
    "one_sided_alpha": 0.05,
    "min_paired_rows_per_week": 8,
    "sign_test": "ONE_SIDED_EXACT_SIGN_TEST",
    "validity": "AT_LEAST_8_PAIRED_ASSET_DAYS_AND_A_OR_CN_WEEK_WINNER",
    "incomplete_tied_missing": "SKIP_AND_USE_NEXT_VALID_WEEK",
    "duplicate": "INCONCLUSIVE_DUPLICATE_WEEK",
    "promotion_allowed": False
}
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
ISSUANCE_PATH = "06_RESEARCH_LAB/task2_challenger_a/issued/{year}/W{week:02d}/CHALLENGER_A_FROZEN_ISSUANCE.json"
SCORE_PATH = "06_RESEARCH_LAB/task2_challenger_a/scored/{year}/W{week:02d}/CHALLENGER_A_FIRST_MATURE_SCORE.json"
SCORE_FIRST_MATURITY_GRACE = dt.timedelta(hours=48)  # source availability bound, not a hypothesis look
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
    seen: set = set()
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
                    if t.minute or t.second or t.microsecond:
                        raise ValueError(f"off-grid hourly source timestamp {iso(t)}; expected UTC HH:00:00")
                    if t in seen:
                        raise ValueError(f"duplicate hourly source timestamp {iso(t)}; do not silently overwrite excursions")
                    seen.add(t)
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
    last_expected = (t0 - HOUR).replace(minute=0, second=0, microsecond=0)
    if (len(times) != n + 1 or times[-1] != last_expected or times[-1] - times[0] != n * HOUR
            or any(t != last_expected - (n - i) * HOUR for i, t in enumerate(times))):
        raise ValueError(f"{asset}: need {n + 1} exact UTC hourly slots through last expected closed hour {iso(last_expected)} before {iso(t0)}")
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
    expected = int((end - start).total_seconds() / 3600)
    if (start.minute or start.second or start.microsecond or end.minute or end.second or end.microsecond
            or expected < PARAMS["min_scored_bars_per_day"] or len(rows) != expected
            or any(t != start + i * HOUR for i, (t, _) in enumerate(rows))):
        return None  # missing ANY expected hour invalidates range and close; no partial-day coverage
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


def issue(bars: dict, year: int, week: int, t0: dt.datetime, provenance: dict | None = None) -> dict:
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
        prior = past.get(monday - HOUR, {}).get(asset)
        # Frozen before T0, never reconstructed from post-outcome bars during scoring.
        assets[asset] = {"P0": p0, "P0_bar_open_utc": p0_bar, "sigma_hourly": round(sd, 8),
                         "prior_week_close": prior[0] if prior else None,
                         "prior_week_close_bar_open_utc": iso(monday - HOUR) if prior else None,
                         "days": days}
    body = {"contract": CONTRACT, "formula_version": FORMULA_VERSION, "week": f"{year}-W{week:02d}",
            "issue_clock_utc": iso(t0), "calibration": cal, "assets": assets,
            "source": provenance if provenance is not None else {"clock_class": "FIXTURE_NOT_MAIN_ATTESTED"},
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


def score(issuance: dict, bars: dict, freeze: dict | None = None, *, issuance_first_main_utc: str | None = None) -> dict:
    """Score matured days for A (all quantiles) and, when given, CN on the same rows."""
    alpha, q = PARAMS["alpha_primary"], str(PARAMS["primary_quantile"])
    rows = []
    abstentions = []
    available = utc(issuance_first_main_utc) if issuance_first_main_utc is not None else None
    for asset, a in issuance["assets"].items():
        cn = cn_bands(freeze, asset) if freeze else {}
        for d in a["days"]:
            # Availability is a real first-main clock, never the earlier CN freeze clock.
            # If the issued band reached main during a UTC day, abstain for that
            # entire asset-day, never score its already-observed early hours.
            if available is not None and utc(d["scored_from_utc"]) < available:
                abstentions.append({"asset": asset, "day": d["day"], "status": "ABSTAIN_PRE_ISSUANCE"})
                continue
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
                row["CN_close_covered"] = int(lo <= r["close"] <= hi)
                prior_close = a.get("prior_week_close")
                if isinstance(prior_close, (int, float)) and math.isfinite(prior_close) and prior_close > 0:
                    width = hi - lo
                    control_lo, control_hi = prior_close - width / 2, prior_close + width / 2
                    if control_lo > 0:
                        row["EQW_PRIOR_interval_score"] = interval_score(control_lo, control_hi, r["close"], alpha) / p0
                        row["EQW_PRIOR_width"] = width / p0
                        row["EQW_PRIOR_range_covered"] = int(control_lo <= r["low"] and r["high"] <= control_hi)
                        row["EQW_PRIOR_close_covered"] = int(control_lo <= r["close"] <= control_hi)
            rows.append(row)
    def aggregate(items):
        result = {}
        if items:
            keys = sorted({k for r in items for k in r if k.endswith(("_covered", "_score", "_width"))})
            for k in keys:
                vals = [r[k] for r in items if k in r]
                result[k] = {"n": len(vals), "mean": round(sum(vals) / len(vals), 6)}
        return result
    both = [r for r in rows if "CN_interval_score" in r]
    # Critical: A and CN PRIMARY means must use exactly the SAME paired asset-days.
    paired = aggregate(both)
    challenger_all = aggregate([{k:v for k,v in r.items() if k.startswith("A_")} for r in rows])
    week_winner = None
    if len(both) >= DECISION["min_paired_rows_per_week"]:
        a_m = sum(r["A_interval_score"] for r in both) / len(both)
        c_m = sum(r["CN_interval_score"] for r in both) / len(both)
        week_winner = "A" if a_m < c_m else ("CN" if c_m < a_m else "TIE")
    else:
        week_winner = "MISSING"
    return {"contract": CONTRACT + "_SCORE", "week": issuance["week"], "issuance_sha256": issuance["issuance_sha256"],
            "matured_rows": len(rows), "rows": rows, "abstentions": abstentions,
            "issuance_first_main_utc": issuance_first_main_utc, "aggregate": paired,
            "aggregate_primary_paired": paired, "aggregate_challenger_all": challenger_all,
            "paired_rows": len(both), "week_winner_interval_score": week_winner,
            "comparison_caveat": "CN is a source-issued daily RANGE interval evaluated against the daily CLOSE, not an independently calibrated close interval. EQW_PRIOR is equal-width prior-week close control; compare like-for-like and never claim edge from range coverage alone.",
            "note": "Research score. First eight valid week clusters from W47 only; minimum eight paired asset-days; no automatic promotion."}


def sign_test_one_sided_p(wins: int, losses: int) -> float:
    """Exact one-sided sign test, pre-registered only after 8 valid weekly clusters."""
    n = wins + losses
    return 1.0 if n == 0 else sum(math.comb(n, i) for i in range(wins, n + 1)) / 2 ** n


def _git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args],
                       capture_output=True, text=True, check=True)
    return p.stdout.strip()


def first_in_main(root: Path, path: str) -> dict:
    """First commit on LOCAL main first-parent carrying a path, never PR HEAD.

    Git committer time is a history clock, NOT independently verified first
    HTTP delivery. Caller must fetch complete main history; a shallow
    checkout is rejected instead of silently inventing provenance.
    """
    if not path or path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("unsafe source path")
    try:
        _git(root, "rev-parse", "--verify", "refs/heads/main")
        if _git(root, "rev-parse", "--is-shallow-repository") != "false":
            raise ValueError("shallow main history cannot establish first-in-main")
        _git(root, "cat-file", "-e", "refs/heads/main:" + path)
        commits = _git(root, "log", "--first-parent", "--reverse",
                       "--format=%H", "refs/heads/main", "--", path).splitlines()
        first = next(sha for sha in commits if subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", sha + ":" + path],
            capture_output=True).returncode == 0)
        # Immutable first-main issue and original CN freeze cannot be edited,
        # even when later restored to their original bytes after outcomes.
        if len(commits) != 1:
            raise ValueError("original main source path was changed after first issue")
        blob = _git(root, "rev-parse", first + ":" + path)
        current_blob = _git(root, "rev-parse", "refs/heads/main:" + path)
        clock = utc(_git(root, "show", "-s", "--format=%cI", first))
        # No pretend first-known from stale PR branch / date of author commit.
        return {"path": path, "first_main_commit": first,
                "first_main_blob_sha": blob, "current_main_blob_sha": current_blob,
                "first_main_utc": iso(clock),
                "clock_class": "MAIN_FIRST_PARENT_COMMITTER_CLOCK_NOT_HTTP_DELIVERY"}
    except (subprocess.CalledProcessError, StopIteration) as e:
        raise ValueError("main source missing, or complete main history unavailable: " + path) from e


def t0_from_git(root: Path, year: int, week: int) -> dt.datetime:
    """CN freeze's first introduction on main, not an unmerged branch."""
    return utc(first_in_main(root, FREEZE_PATH.format(year=year, week=week))["first_main_utc"])


def verify_issuance_digest(issuance: dict) -> None:
    if not isinstance(issuance, dict) or issuance.get("contract") != CONTRACT or issuance.get("formula_version") != FORMULA_VERSION:
        raise ValueError("invalid issuance contract/version")
    content = {k: v for k, v in issuance.items() if k != "issuance_sha256"}
    if issuance.get("issuance_sha256") != _digest(content):
        raise ValueError("original issuance digest mismatch")


def read_frozen_main_issuance(root: Path, year: int, week: int) -> tuple[dict, dict]:
    """Load source-verified frozen issuance. No recalculation from modern CSV."""
    path = ISSUANCE_PATH.format(year=year, week=week)
    proof = first_in_main(root, path)
    current_path = root / path
    try:
        raw = current_path.read_bytes()
        original = subprocess.run(["git", "-C", str(root), "show",
                                   proof["first_main_commit"] + ":" + path],
                                  capture_output=True, check=True).stdout
        current_sha = _git(root, "rev-parse", "refs/heads/main:" + path)
    except (OSError, subprocess.CalledProcessError) as e:
        raise ValueError("cannot verify immutable original issuance bytes") from e
    if raw != original or current_sha != proof["first_main_blob_sha"]:
        raise ValueError("issuance altered after first-main: refuse retrospective reforecast")
    doc = json.loads(original)
    verify_issuance_digest(doc)
    if doc.get("week") != f"{year}-W{week:02d}" or doc.get("source", {}).get("clock_class") != "MAIN_FIRST_PARENT_COMMITTER_CLOCK_NOT_HTTP_DELIVERY":
        raise ValueError("unattested issue week/source; fixture is never scoreable")
    freeze = first_in_main(root, FREEZE_PATH.format(year=year, week=week))
    if (freeze["current_main_blob_sha"] != freeze["first_main_blob_sha"]
            or doc["source"].get("freeze_first_main_commit") != freeze["first_main_commit"]
            or doc["source"].get("freeze_blob_sha") != freeze["first_main_blob_sha"]
            or doc["source"].get("freeze_first_main_utc") != freeze["first_main_utc"]):
        raise ValueError("original CN freeze mutated or issuance ancestry differs")
    original_freeze = subprocess.run(["git", "-C", str(root), "show",
        freeze["first_main_commit"] + ":" + freeze["path"]], capture_output=True, check=True).stdout
    if (root / freeze["path"]).read_bytes() != original_freeze:
        raise ValueError("working copy of original CN freeze differs from main")
    if utc(doc["issue_clock_utc"]) != utc(freeze["first_main_utc"]):
        raise ValueError("issuance clock not identical to frozen CN first-main clock")
    # Late first-main availability is not an integrity failure. Score must
    # abstain for every asset-day that had already started at that clock.
    proof["issuance_first_main_utc"] = proof["first_main_utc"]
    return doc, proof



def no_issuance_missing_score(root: Path, year: int, week: int,
                              *, as_of_utc: dt.datetime | None = None) -> dict:
    """Freeze an explicitly absent A issue as MISSING, never as a retrospective loss.

    Only the canonical score command calls this with the real UTC clock.
    The optional clock is solely for deterministic synthetic-Git tests.
    """
    maturity = week_monday(year, week) + 7 * DAY
    now = as_of_utc if as_of_utc is not None else dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None or not maturity <= now <= maturity + SCORE_FIRST_MATURITY_GRACE:
        raise ValueError("no-issuance MISSING requires the first 48h after full week maturity")
    rel = ISSUANCE_PATH.format(year=year, week=week)
    _git(root, "rev-parse", "--verify", "refs/heads/main")
    if _git(root, "rev-parse", "--is-shallow-repository") != "false":
        raise ValueError("no-issuance MISSING cannot trust shallow main history")
    # A removed or renamed first-main issuance MUST NOT turn into 'never issued'.
    additions = _git(root, "log", "--first-parent", "-m", "--diff-filter=A",
                     "--name-only", "--format=", "refs/heads/main", "--", rel)
    current = subprocess.run(["git", "-C", str(root), "cat-file", "-e",
                              "refs/heads/main:" + rel], capture_output=True)
    if rel in additions.splitlines() or current.returncode == 0:
        raise ValueError("historical or current A issuance exists; no-issuance certificate refused")
    main_sha = _git(root, "rev-parse", "refs/heads/main")
    return {
        "contract": CONTRACT + "_SCORE", "week": f"{year}-W{week:02d}",
        "issuance_sha256": None, "issuance_first_main_utc": None,
        "first_main_issuance": None, "matured_rows": 0, "paired_rows": 0,
        "rows": [], "abstentions": [], "aggregate": {}, "aggregate_primary_paired": {},
        "aggregate_challenger_all": {}, "week_winner_interval_score": "MISSING",
        "missing_reason": "NO_ORIGINAL_ISSUANCE_AT_FIRST_MATURITY",
        "no_issuance_provenance": {
            "contract": "TASK2_A_FIRST_MATURITY_NO_ISSUANCE_v1",
            "canonical_path": rel, "checked_main_sha": main_sha,
            "checked_at_utc": iso(now), "first_parent_historical_additions": 0},
        "first_http_delivery": "UNKNOWN", "decision_status": "SHADOW_ONLY_NO_PROMOTION",
        "note": "Immutable no-issuance denominator. Not a win, not a forecast, no promotion."
    }


def verify_no_issuance_first_main(root: Path, row: dict, proof: dict,
                                  year: int, week: int) -> None:
    """Prove the first committed MISSING row predated any original A issue."""
    maturity = week_monday(year, week) + 7 * DAY
    first_clock = utc(proof["first_main_utc"])
    certificate = row.get("no_issuance_provenance")
    rel = ISSUANCE_PATH.format(year=year, week=week)
    if (row.get("missing_reason") != "NO_ORIGINAL_ISSUANCE_AT_FIRST_MATURITY"
            or row.get("issuance_sha256") is not None
            or row.get("issuance_first_main_utc") is not None
            or row.get("first_main_issuance") is not None
            or row.get("paired_rows") != 0
            or row.get("matured_rows") != 0
            or row.get("rows") != []
            or row.get("week_winner_interval_score") != "MISSING"
            or not isinstance(certificate, dict)
            or certificate.get("contract") != "TASK2_A_FIRST_MATURITY_NO_ISSUANCE_v1"
            or certificate.get("canonical_path") != rel
            or certificate.get("first_parent_historical_additions") != 0):
        raise ValueError("invalid no-issuance MISSING certificate")
    checked = utc(certificate.get("checked_at_utc"))
    if not maturity <= checked <= first_clock <= maturity + SCORE_FIRST_MATURITY_GRACE:
        raise ValueError("no-issuance first-maturity clock out of bounds")
    pin = certificate.get("checked_main_sha")
    if not isinstance(pin, str) or len(pin) != 40 or any(c not in "0123456789abcdef" for c in pin):
        raise ValueError("invalid no-issuance main ancestry pin")
    subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                    pin, proof["first_main_commit"]], check=True, capture_output=True)
    # Audit all history up to the first score commit, not just current main:
    # a genuine early issue cannot be deleted and recast as absent.
    introductions = _git(root, "log", "--first-parent", "-m", "--diff-filter=A",
                         "--name-only", "--format=", proof["first_main_commit"], "--", rel)
    exists = subprocess.run(["git", "-C", str(root), "cat-file", "-e",
                             proof["first_main_commit"] + ":" + rel], capture_output=True)
    if rel in introductions.splitlines() or exists.returncode == 0:
        raise ValueError("issued A source was present before first MISSING score")



def read_first_main_weekly_score(root: Path, year: int, week: int) -> tuple[dict, dict]:
    """Read ONLY the first committed weekly score on full main first-parent history.

    Re-scored/revised working files, an edit-then-restore history, missing
    first-main lineage or post-grace publication cannot produce a valid win.
    Git committer time is an availability proxy, never HTTP first-known proof.
    """
    rel = SCORE_PATH.format(year=year, week=week)
    proof = first_in_main(root, rel)
    path = root / rel
    try:
        first_bytes = subprocess.run(
            ["git", "-C", str(root), "show", proof["first_main_commit"] + ":" + rel],
            capture_output=True, check=True).stdout
        now_bytes = path.read_bytes()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("first-main score inaccessible") from exc
    if now_bytes != first_bytes or proof["current_main_blob_sha"] != proof["first_main_blob_sha"]:
        raise ValueError("first-main score mutated: later backfill cannot rewrite confirmatory evidence")
    try:
        row = json.loads(first_bytes)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("invalid immutable score JSON") from exc
    expected_week = f"{year}-W{week:02d}"
    if (row.get("contract") != CONTRACT + "_SCORE" or row.get("week") != expected_week
            or row.get("decision_status") != "SHADOW_ONLY_NO_PROMOTION"
            or row.get("first_http_delivery") != "UNKNOWN"):
        raise ValueError("score lacks canonical research-only provenance")
    if row.get("missing_reason") == "NO_ORIGINAL_ISSUANCE_AT_FIRST_MATURITY":
        verify_no_issuance_first_main(root, row, proof, year, week)
        proof["no_issuance_verified"] = True
    else:
        issued, issue_proof = read_frozen_main_issuance(root, year, week)
        if (row.get("issuance_sha256") != issued["issuance_sha256"]
                or row.get("issuance_first_main_utc") != issue_proof["issuance_first_main_utc"]):
            raise ValueError("score does not bind the original first-main issuance")
        attested = row.get("first_main_issuance")
        if not isinstance(attested, dict) or any(
            attested.get(key) != issue_proof[key] for key in
            ("first_main_commit", "first_main_blob_sha", "issuance_first_main_utc")
        ):
            raise ValueError("score's issuance proof was replaced or omitted")
    paired = row.get("paired_rows")
    winner = row.get("week_winner_interval_score")
    if (type(paired) is not int or not 0 <= paired <= 14
            or winner not in ("A", "CN", "TIE", "MISSING")):
        raise ValueError("unusable first-main score result")
    maturity = week_monday(year, week) + 7 * DAY
    first_clock = utc(proof["first_main_utc"])
    if first_clock < maturity:
        raise ValueError("score was committed before complete ISO week matured")
    # A first-published score after the frozen 48h opportunity cannot be
    # admitted as a retrospectively backfilled valid week. Keep its provenance
    # but force this week to MISSING regardless of later CSV improvements.
    accepted = first_clock <= maturity + SCORE_FIRST_MATURITY_GRACE
    result = dict(row)
    if not accepted:
        result["paired_rows"] = 0
        result["week_winner_interval_score"] = "MISSING"
    proof["eligible_first_maturity"] = accepted
    proof["first_maturity_deadline_utc"] = iso(maturity + SCORE_FIRST_MATURITY_GRACE)
    return result, proof


def confirmatory_decision_from_main(root: Path, through_week: str) -> dict:
    """Only first-main weekly scores may enter the pre-registered sign test.

    Every intervening week must carry an immutable first-maturity score,
    including explicit MISSING results. Absence is not silently skipped, since
    a later backfill could otherwise insert a prior week into the first eight.
    """
    through_y, through_w = _parse_week(through_week)
    start_y, start_w = _parse_week(DECISION["first_week"])
    monday = week_monday(start_y, start_w)
    through = week_monday(through_y, through_w)
    if through < monday:
        return {"status": "PENDING", "valid_weeks": 0, "promotion_allowed": False}
    if (through - monday).days > 7 * 260:
        raise ValueError("unbounded confirmatory score census")
    records, source_proofs = [], []
    while monday <= through:
        week_string = f"{monday.isocalendar().year}-W{monday.isocalendar().week:02d}"
        try:
            row, proof = read_first_main_weekly_score(
                root, monday.isocalendar().year, monday.isocalendar().week)
        except ValueError as exc:
            # A missing or corrupt historical original must not be skipped.
            return {"status": "INCONCLUSIVE_FIRST_SCORE_SOURCE",
                    "first_unverified_week": week_string,
                    "source_error": str(exc),
                    "verified_weeks_before_gap": len(records),
                    "promotion_allowed": False}
        records.append(row)
        source_proofs.append({"week": week_string,
                              "first_main_commit": proof["first_main_commit"],
                              "first_main_blob_sha": proof["first_main_blob_sha"],
                              "first_main_utc": proof["first_main_utc"],
                              "eligible_first_maturity": proof["eligible_first_maturity"]})
        # The pre-registered look is over the FIRST eight valid weeks only.
        # A later missing/corrupt score must never revoke a completed look.
        decision = confirmatory_decision(records)
        if decision["status"] in ("A_PASSES_SHADOW_CONFIRMATORY", "A_NOT_PROVEN"):
            break
        monday += 7 * DAY
    decision = confirmatory_decision(records)
    decision["source_class"] = "IMMUTABLE_FIRST_MAIN_WEEKLY_SCORES_ONLY"
    decision["first_main_score_census"] = source_proofs
    return decision


def confirmatory_decision(weekly: list[dict]) -> dict:
    """One pre-registered look at the FIRST 8 VALID ISO weeks from W47.

    A valid week has >=8 paired asset-days and an untied A/CN comparison.
    Missing/untied weeks are skipped, but no later result may replace one of
    the first eight valid weeks. Duplicate week input invalidates the look.
    """
    if any(not isinstance(r, dict) or not isinstance(r.get("week"), str) for r in weekly):
        return {"status": "INCONCLUSIVE_INVALID_WEEK", "promotion_allowed": False}
    try:
        for r in weekly:
            _parse_week(r["week"])
    except ValueError:
        return {"status": "INCONCLUSIVE_INVALID_WEEK", "promotion_allowed": False}
    weeks = [r["week"] for r in weekly]
    if len(weeks) != len(set(weeks)):
        return {"status": "INCONCLUSIVE_DUPLICATE_WEEK", "promotion_allowed": False}
    valid = [r for r in sorted(weekly, key=lambda r: r.get("week") or "")
             if isinstance(r.get("week"), str)
             and r["week"] >= DECISION["first_week"]
             and r.get("paired_rows", 0) >= DECISION["min_paired_rows_per_week"]
             and r.get("week_winner_interval_score") in ("A", "CN")]
    if len(valid) < DECISION["confirmatory_valid_weeks"]:
        return {"status": "PENDING", "valid_weeks": len(valid),
                "needed_valid_weeks": DECISION["confirmatory_valid_weeks"], "promotion_allowed": False}
    first = valid[:DECISION["confirmatory_valid_weeks"]]
    wins = sum(r["week_winner_interval_score"] == "A" for r in first)
    losses = len(first) - wins
    p = sign_test_one_sided_p(wins, losses)
    return {"status": "A_PASSES_SHADOW_CONFIRMATORY" if p < DECISION["one_sided_alpha"] else "A_NOT_PROVEN",
            "weeks": [r["week"] for r in first], "wins_A": wins, "wins_CN": losses,
            "one_sided_p": p, "decision_horizon": "ONE_LOOK_FIRST_EIGHT_VALID_WEEKS",
            "promotion_allowed": False}


def _parse_week(s: str) -> tuple[int, int]:
    if not isinstance(s, str) or re.fullmatch(r"[0-9]{4}-W[0-9]{2}", s) is None:
        raise ValueError("ISO week must be canonical YYYY-Www")
    y, w = int(s[:4]), int(s[6:])
    try:
        monday = week_monday(y, w)
    except ValueError as exc:
        raise ValueError("invalid ISO week") from exc
    if f"{monday.isocalendar().year}-W{monday.isocalendar().week:02d}" != s:
        raise ValueError("noncanonical ISO week")
    return y, w


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["issue", "score", "decide"])
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--week", required=True, help="ISO week, e.g. 2026-W47")
    ap.add_argument("--t0", help="fixture clock only, never accepted as main-origin evidence")
    ap.add_argument("--synthetic-fixture-clock", action="store_true")
    ap.add_argument("--output", required=True)
    a = ap.parse_args(list(argv) if argv is not None else None)
    root = Path(a.repo_root)
    year, week = _parse_week(a.week)
    monday = week_monday(year, week)
    output = Path(a.output)
    if a.command == "decide":
        if a.t0 or a.synthetic_fixture_clock:
            raise ValueError("confirmatory decision requires immutable main sources")
        result = confirmatory_decision_from_main(root, a.week)
    elif a.command == "issue":
        expected_output = (root / ISSUANCE_PATH.format(year=year, week=week)).resolve()
        if not a.synthetic_fixture_clock and output.resolve() != expected_output:
            raise ValueError("canonical issue must only write the dedicated research issuance path")
        if a.t0 and not a.synthetic_fixture_clock:
            raise ValueError("manual issue clock cannot claim first-in-main")
        if a.synthetic_fixture_clock and not a.t0:
            raise ValueError("fixture mode requires an explicit test clock")
        t0 = utc(a.t0) if a.synthetic_fixture_clock else t0_from_git(root, year, week)
        source = {"clock_class": "SYNTHETIC_FIXTURE_ONLY"} if a.synthetic_fixture_clock else None
        if source is None:
            proof = first_in_main(root, FREEZE_PATH.format(year=year, week=week))
            source = {"clock_class": proof["clock_class"],
                      "freeze_first_main_commit": proof["first_main_commit"],
                      "freeze_blob_sha": proof["first_main_blob_sha"],
                      "freeze_first_main_utc": proof["first_main_utc"],
                      "first_http_delivery": "UNKNOWN"}
        bars = load_hourly(root, monday - 70 * DAY, monday + 7 * DAY)
        result = issue(bars, year, week, t0, source)
    else:
        if a.t0 or a.synthetic_fixture_clock:
            raise ValueError("score forbids fixture clocks and post-hoc rebuilding")
        if output.resolve() == (root / ISSUANCE_PATH.format(year=year, week=week)).resolve():
            raise ValueError("score must not overwrite the original frozen issuance")
        canonical_score = (root / SCORE_PATH.format(year=year, week=week)).resolve()
        if output.resolve() == canonical_score and canonical_score.is_file():
            raise ValueError("first-maturity canonical score already exists; no in-place re-score")
        try:
            issuance, original = read_frozen_main_issuance(root, year, week)
        except ValueError:
            # This is NOT a generic fallback for malformed/altered sources:
            # the helper proves that no original issuance ever reached main.
            # It also refuses backfilled missing scores after first maturity.
            if output.resolve() != canonical_score:
                raise ValueError("no-issuance MISSING must be committed to the canonical first score path")
            result = no_issuance_missing_score(root, year, week)
        else:
            bars = load_hourly(root, monday, monday + 7 * DAY)
            freeze_path = root / FREEZE_PATH.format(year=year, week=week)
            freeze = json.loads(freeze_path.read_text(encoding="utf-8")) if freeze_path.is_file() else None
            result = score(issuance, bars, freeze, issuance_first_main_utc=original["issuance_first_main_utc"])
            result["first_main_issuance"] = original
            result["first_http_delivery"] = "UNKNOWN"
            result["decision_status"] = "SHADOW_ONLY_NO_PROMOTION"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"contract": result.get("contract", "TASK2_CHALLENGER_A_IMMUTABLE_DECISION_v1"),
                      "week": result.get("week", a.week), "status": result.get("status", "WRITTEN")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
