#!/usr/bin/env python3
"""Research-only, offline Tehc-style launchpad/terminal heat reconstruction.

Inputs are user-supplied public JSON snapshots, NEVER fetched by this program.
Historical Tehc rows have unknown first publication times/backfills. Comparing
them with Kraken historical candles is RECONSTRUCTED_RETROSPECTIVE_ONLY, not
prospectively certified PIT, skill, a new Compass owner, or a trade rule.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONTRACT = "S7_TEHC_HEAT_RETROSPECTIVE_V1"
FIELDS = ("pad_volume", "tokens_launched", "bot_volume", "bot_fees")
WEIGHTS = (0.35, 0.20, 0.25, 0.20)
BLEND = (0.60, 0.40)
COOLDOWN = 0.65
MIN_PRIOR = 30
PROVIDER = "tehcscreener.com"


def day(s: Any) -> str:
    if not isinstance(s, str) or len(s) != 10:
        raise ValueError("INVALID_UTC_DAY")
    try:
        d = date.fromisoformat(s)
    except ValueError as e:
        raise ValueError("INVALID_UTC_DAY") from e
    if d.isoformat() != s:
        raise ValueError("INVALID_UTC_DAY")
    return s


def shift(d: str, n: int) -> str:
    return (date.fromisoformat(d) + timedelta(days=n)).isoformat()


def num(v: Any, *, positive: bool = False) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError("NONFINITE_OR_MISSING_METRIC")
    n = float(v)
    if not math.isfinite(n) or n < 0 or (positive and n == 0):
        raise ValueError("NONFINITE_OR_MISSING_METRIC")
    return n


def require_source(doc: Any, kind: str) -> tuple[list[str], list[dict[str, Any]]]:
    if not isinstance(doc, dict) or doc.get("source") != PROVIDER or doc.get("window") != "all":
        raise ValueError("UNVERIFIED_PROVIDER_OR_ALL_WINDOW")
    if kind == "bots" and doc.get("group") != "bot":
        raise ValueError("BOT_GROUP_MUST_BE_BOT")
    days = doc.get("days")
    series = doc.get("series")
    if not isinstance(days, list) or not days or not isinstance(series, list) or not series:
        raise ValueError("SOURCE_DAILY_SERIES_REQUIRED")
    if any(day(x) != x for x in days) or sorted(set(days)) != days:
        raise ValueError("SOURCE_DAYS_UNORDERED_OR_DUPLICATED")
    if any(shift(a, 1) != b for a, b in zip(days, days[1:])):
        raise ValueError("SOURCE_DAILY_GAP")
    if day(doc.get("through")) != days[-1]:
        raise ValueError("SOURCE_THROUGH_MISMATCH")
    metrics = ("volume_usd", "tokens_launched") if kind == "pads" else ("volume_usd", "fees_usd")
    for item in series:
        if not isinstance(item, dict):
            raise ValueError("INVALID_SOURCE_SERIES")
        for metric in metrics:
            values = item.get(metric)
            if not isinstance(values, list) or len(values) != len(days):
                raise ValueError("SOURCE_METRIC_LENGTH_MISMATCH")
            for value in values:
                num(value)
    return days, series


def panel(pads: dict[str, Any], bots: dict[str, Any]) -> list[dict[str, Any]]:
    pad_days, pad_series = require_source(pads, "pads")
    bot_days, bot_series = require_source(bots, "bots")
    # A missing day from either source is a coverage gap, not synthetic zero.
    shared = sorted(set(pad_days) & set(bot_days))
    if not shared or any(shift(a, 1) != b for a, b in zip(shared, shared[1:])):
        raise ValueError("NO_CONTIGUOUS_SOURCE_OVERLAP")
    pi = {d: i for i, d in enumerate(pad_days)}
    bi = {d: i for i, d in enumerate(bot_days)}
    rows: list[dict[str, Any]] = []
    for d in shared:
        p, b = pi[d], bi[d]
        row = {
            "day": d,
            "pad_volume": sum(num(s["volume_usd"][p]) for s in pad_series),
            "tokens_launched": sum(num(s["tokens_launched"][p]) for s in pad_series),
            "bot_volume": sum(num(s["volume_usd"][b]) for s in bot_series),
            "bot_fees": sum(num(s["fees_usd"][b]) for s in bot_series),
        }
        # The vendor only scores days with real observed pad AND bot activity.
        # Never assume an all-zero universe means a valid low-activity sample.
        if row["pad_volume"] == 0 or row["bot_volume"] == 0:
            raise ValueError("INACTIVE_SOURCE_UNIVERSE_NOT_ADMITTED")
        rows.append(row)
    return rows


def percentile(value: float, prior: list[float]) -> float:
    if not prior:
        raise ValueError("NO_PRIOR_HISTORY")
    return 100.0 * sum(x <= value for x in prior) / len(prior)


def heat(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if any(shift(a["day"], 1) != b["day"] for a, b in zip(rows, rows[1:])):
        raise ValueError("HEAT_INPUT_DATE_GAP")
    previous: float | None = None
    out = []
    for i, row in enumerate(rows):
        if i < MIN_PRIOR:
            continue
        prior_90 = rows[max(0, i - 90):i]  # strictly prior days, no current/future
        prior_365 = rows[max(0, i - 365):i]
        components = [
            BLEND[0] * percentile(row[f], [x[f] for x in prior_90])
            + BLEND[1] * percentile(row[f], [x[f] for x in prior_365])
            for f in FIELDS
        ]
        raw = sum(v * w for v, w in zip(components, WEIGHTS))
        cooled = raw if previous is None or raw >= previous else COOLDOWN * previous + (1 - COOLDOWN) * raw
        previous = cooled
        out.append({
            "day": row["day"],
            "heat_raw": raw,
            "heat_cooldown": cooled,
            "heat_equal_weight": sum(components) / len(components),
            "components": dict(zip(FIELDS, components)),
        })
    return out


def vendor_index(doc: dict[str, Any]) -> dict[str, int]:
    if not isinstance(doc, dict) or doc.get("source") != PROVIDER:
        raise ValueError("VENDOR_SOURCE_INVALID")
    method = doc.get("method", {})
    if method.get("window_days") != 90 or method.get("window_days_long") != 365:
        raise ValueError("VENDOR_METHOD_DRIFT")
    for name, weight in zip(FIELDS, WEIGHTS):
        if not math.isclose(method.get("weights", {}).get(name, -1), weight):
            raise ValueError("VENDOR_METHOD_DRIFT")
    for name, weight in (("short", 0.6), ("long", 0.4)):
        if not math.isclose(method.get("blend", {}).get(name, -1), weight):
            raise ValueError("VENDOR_METHOD_DRIFT")
    if not math.isclose(method.get("cooldown", -1), COOLDOWN):
        raise ValueError("VENDOR_METHOD_DRIFT")
    history = doc.get("history")
    if not isinstance(history, list) or not history:
        raise ValueError("VENDOR_HISTORY_REQUIRED")
    out = {}
    for item in history:
        d = day(item["day"])
        n = item["score"]
        if d in out or isinstance(n, bool) or not isinstance(n, int) or not 0 <= n <= 100:
            raise ValueError("VENDOR_SCORE_INVALID")
        out[d] = n
    if doc.get("today", {}).get("day") != max(out):
        raise ValueError("VENDOR_THROUGH_MISMATCH")
    return out


def pearson(values: list[float], targets: list[float]) -> float | None:
    if len(values) < 3 or len(values) != len(targets):
        return None
    mx, my = sum(values) / len(values), sum(targets) / len(targets)
    xx = sum((x - mx) ** 2 for x in values)
    yy = sum((y - my) ** 2 for y in targets)
    if xx == 0 or yy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(values, targets)) / math.sqrt(xx * yy)


def kraken_daily(doc: dict[str, Any], expected_key: str) -> dict[str, float]:
    if not isinstance(doc, dict) or doc.get("error") != [] or not isinstance(doc.get("result"), dict):
        raise ValueError("KRAKEN_RESPONSE_INVALID")
    candles = doc["result"].get(expected_key)
    if not isinstance(candles, list) or len(candles) < 10:
        raise ValueError("KRAKEN_QUOTE_OR_HISTORY_INVALID")
    out: dict[str, float] = {}
    last_t = -1
    # Kraken documents its FINAL candle as in-progress, ALWAYS drop it.
    for candle in candles[:-1]:
        if not isinstance(candle, list) or len(candle) < 5:
            raise ValueError("KRAKEN_CANDLE_INVALID")
        t = candle[0]
        if isinstance(t, bool) or not isinstance(t, int) or t % 86400 or t <= last_t:
            raise ValueError("KRAKEN_CANDLE_TIMESTAMP_INVALID")
        last_t = t
        d = datetime.fromtimestamp(t, timezone.utc).date().isoformat()
        price = float(candle[4])
        if not math.isfinite(price) or price <= 0 or d in out:
            raise ValueError("KRAKEN_CLOSE_INVALID")
        out[d] = price
    return out


def dated_outcomes(heat_rows: list[dict[str, Any]], vendor: dict[str, int],
                   btc: dict[str, float], sol: dict[str, float]) -> list[dict[str, Any]]:
    rows = []
    for r in heat_rows:
        d = r["day"]
        # The day's activity is known no earlier than *after* day d ends.
        # Enter ONLY at the next UTC daily close d+1, outcome at d+4 or d+8.
        entry, at3, at7 = shift(d, 1), shift(d, 4), shift(d, 8)
        if d not in vendor or any(x not in btc or x not in sol for x in (entry, at3, at7)):
            continue
        lookback = [(shift(d, k - 1), shift(d, k)) for k in range(-5, 2)]
        if any(a not in sol or b not in sol for a, b in lookback):
            continue
        v = math.sqrt(sum(math.log(sol[b] / sol[a]) ** 2 for a, b in lookback))
        s3 = math.log(sol[at3] / sol[entry])
        r3 = math.log((sol[at3] / btc[at3]) / (sol[entry] / btc[entry]))
        rows.append({
            "day": d, "vendor": vendor[d], "heat_raw": r["heat_raw"],
            "heat_cooldown": r["heat_cooldown"], "heat_equal_weight": r["heat_equal_weight"],
            "relative_solbtc_3d_log": r3, "abs_sol_3d_log": abs(s3),
            "sol_down_5pct_3d": s3 < math.log(.95),
            "realized_sol_vol_prev_7d": v,
        })
    return rows


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0, "relative_solbtc_mean_pct": None, "sol_down_5pct_rate": None}
    return {
        "n": len(rows),
        "relative_solbtc_mean_pct": round(100 * sum(r["relative_solbtc_3d_log"] for r in rows) / len(rows), 3),
        "sol_down_5pct_rate": round(sum(r["sol_down_5pct_3d"] for r in rows) / len(rows), 5),
        "mean_abs_sol3_pct": round(100 * sum(r["abs_sol_3d_log"] for r in rows) / len(rows), 3),
    }


def correlation(rows: list[dict[str, Any]], x: str, y: str) -> float | None:
    return pearson([r[x] for r in rows], [r[y] for r in rows])


def build(pads: dict[str, Any], bots: dict[str, Any], vendor_doc: dict[str, Any],
          btc_doc: dict[str, Any], sol_doc: dict[str, Any]) -> dict[str, Any]:
    rows = panel(pads, bots)
    h = heat(rows)
    vi = vendor_index(vendor_doc)
    paired = [x | {"vendor": vi[x["day"]]} for x in h if x["day"] in vi]
    if not paired:
        raise ValueError("NO_VENDOR_OVERLAP")
    outcomes = dated_outcomes(
        h, vi, kraken_daily(btc_doc, "XXBTZUSD"), kraken_daily(sol_doc, "SOLUSD")
    )
    years = {}
    for year in ("2025", "2026"):
        g = [r for r in outcomes if r["day"].startswith(year)]
        hv = [r for r in g if r["vendor"] >= 60]
        lv = [r for r in g if r["vendor"] < 40]
        years[year] = {
            "all": summary(g), "cold_vendor_below_40": summary(lv),
            "hot_vendor_at_least_60": summary(hv),
            "correlation_vendor_vs_3d_relative": correlation(g, "vendor", "relative_solbtc_3d_log"),
            "correlation_internal_raw_vs_3d_relative": correlation(g, "heat_raw", "relative_solbtc_3d_log"),
            "correlation_vendor_vs_3d_abs_sol": correlation(g, "vendor", "abs_sol_3d_log"),
            "correlation_price_only_prior_vol7_vs_3d_abs_sol": correlation(
                g, "realized_sol_vol_prev_7d", "abs_sol_3d_log"
            ),
        }
    weekly = [r for r in outcomes if "2026-01-01" <= r["day"] < "2026-11-01"][::7]
    return {
        "contract": CONTRACT, "classification": "RETROSPECTIVE_METHOD_CHECK_ONLY",
        "scientific_pit_admission": False, "prospective_skill": False,
        "market_action_authority": False, "new_forecast_owner": False,
        "source_raw_original_first_known": "UNVERIFIED_BACKFILLED_VENDOR_HISTORY",
        "outcome_provider": "KRAKEN_SPOT_USD_CLOSED_1D",
        "outcome_entry_policy": "DAY_D_PLUS_1_UTC_CLOSE_AFTER_DAILY_VENDOR_OBSERVATION",
        "outcome_horizons": "DAY_D_PLUS_4_AND_D_PLUS_8_CLOSES_AFTER_ENTRY",
        "method": {"percentile_prior_only": True, "short_days": 90, "long_days": 365,
                   "blend": BLEND, "weights": dict(zip(FIELDS, WEIGHTS)),
                   "cooldown": COOLDOWN, "minimum_prior_days": MIN_PRIOR},
        "source_census": {
            "daily_overlap": len(rows), "first": rows[0]["day"], "last": rows[-1]["day"],
            "launchpad_series": len(pads["series"]), "bot_series": len(bots["series"]),
            "vendor_history": len(vi), "vendor_matched": len(paired),
        },
        "vendor_replication": {
            "mae_unsmoothed": sum(abs(x["heat_raw"] - x["vendor"]) for x in paired) / len(paired),
            "mae_cooldown": sum(abs(x["heat_cooldown"] - x["vendor"]) for x in paired) / len(paired),
            "pearson_cooldown": correlation(paired, "heat_cooldown", "vendor"),
            "latest_5": [{"day": x["day"], "vendor": x["vendor"],
                          "internal_cooldown": round(x["heat_cooldown"], 2)}
                         for x in paired[-5:]],
        },
        "market_retrospective": {
            "eligible_days": len(outcomes), "first": outcomes[0]["day"] if outcomes else None,
            "last": outcomes[-1]["day"] if outcomes else None, "by_year": years,
            "year_2026_every_seventh_day": {
                "all": summary(weekly),
                "cold": summary([r for r in weekly if r["vendor"] < 40]),
                "hot": summary([r for r in weekly if r["vendor"] >= 60]),
                "caution": "DETERMINISTIC_NONOVERLAPPING_FORWARD_WINDOWS_NOT_INDEPENDENT_MARKET_REGIMES",
            },
        },
        "limitations": [
            "Historic vendor panels may have post-event restatements/coverage changes",
            "Underlying Allium data and historical publication clocks are not independently attested",
            "No exact vendor calculation replica because component coverage/tie rules and smoothing are partly opaque",
            "No original prospective event denominator, fees, slippage, market regime matching or confidence intervals",
            "Overlapping 3d outcome rows and repeated market regimes bias raw significance",
            "Cross-domain Kompas and token-level Alpha survival edge remain UNPROVEN",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("pads", "bots", "vendor", "btc", "sol"):
        p.add_argument("--" + key, type=Path, required=True,
                       help="Local JSON snapshot: no programmatic download or auto-publication")
    args = p.parse_args()
    docs = {}
    hashes = {}
    for key in ("pads", "bots", "vendor", "btc", "sol"):
        path = getattr(args, key)
        raw = path.read_bytes()
        hashes[key] = hashlib.sha256(raw).hexdigest()
        docs[key] = json.loads(raw)
    out = build(docs["pads"], docs["bots"], docs["vendor"], docs["btc"], docs["sol"])
    out["input_sha256"] = hashes
    print(json.dumps(out, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
