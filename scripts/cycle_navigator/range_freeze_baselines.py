"""R6 retained-price benchmarks, frozen once by the existing CN issuer.

No network reads, source promotion, outcome use, or historical writes.
Legacy retained BTC/ETH columns are not independent raw quote attestation.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ASSETS = ("BTC", "ETH")
ROOT = Path("03_DAILY_CAPTURE_LOGS")
HISTORY_WEEKS = 9


def _clock(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("noncanonical UTC clock")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _number(value):
    result = Decimal(str(value))
    if not result.is_finite() or result <= 0:
        raise ValueError("invalid price")
    return result


def _bar(values):
    o, h, l, c = map(_number, values)
    if not l <= min(o, c) <= max(o, c) <= h:
        raise ValueError("invalid OHLC")
    return o, h, l, c


def _aggregate(bars):
    return bars[0][0], max(x[1] for x in bars), min(x[2] for x in bars), bars[-1][3]


def _round(value):
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def benchmark(days):
    if len(days) != 63:
        raise ValueError("63 settled days required")
    tr = []
    for i, (_, high, low, close) in enumerate(days):
        tr.append(high - low if i == 0 else max(high - low, abs(high-days[i-1][3]), abs(low-days[i-1][3])))
    atr = sum(tr[:14]) / Decimal(14)
    for value in tr[14:]:
        atr = (13 * atr + value) / 14
    rounded = Decimal(_round(atr))
    anchor = days[-1][3]
    def band(mult):
        lo, hi = _round(anchor - mult*rounded), _round(anchor + mult*rounded)
        if not 0 < lo < hi:
            raise ValueError("unusable ATR band")
        return {"low": lo, "high": hi}
    return {"anchor_close": float(anchor), "atr14_raw": float(atr),
            "atr14_rounded": int(rounded), "DUMB1.5": band(Decimal("1.5")),
            "DUMB2.0": band(Decimal("2.0")),
            "PREVWK": {"low": float(min(x[2] for x in days[-7:])),
                       "high": float(max(x[1] for x in days[-7:]))}}


def _read(repo, rel):
    path = repo / rel
    if path.is_symlink() or path.resolve() != path or not path.is_file():
        raise ValueError("source path unavailable")
    raw = path.read_bytes()
    if len(raw) > 2_000_000:
        raise ValueError("source too large")
    return raw


def freeze_baselines(repo, *, year, week, generated_unix, completed_capture, range_forecast):
    """Freeze only current inputs, with exact retained snapshot digests.

    A later day needs newer settled candles; never silently reuse Sunday.
    Failure abstains without blocking publication or altering the forecast.
    """
    unavailable = {"contract": "CN_RANGE_BENCHMARK_FREEZE_v1",
                   "status": "UNAVAILABLE", "scientific_admission": False,
                   "assets": {}}
    try:
        repo = Path(repo).resolve()
        if type(generated_unix) is not int:
            raise ValueError("invalid freeze clock")
        freeze = datetime.fromtimestamp(generated_unix, timezone.utc)
        monday = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), timezone.utc)
        if not monday <= freeze < monday + timedelta(days=1):
            raise ValueError("settled daily anchor not current")
        if not isinstance(completed_capture, dict) or not isinstance(range_forecast, dict):
            raise ValueError("missing forecast snapshot")
        daily = {a: [] for a in ASSETS}
        sources = []
        legacy = False
        for offset in range(HISTORY_WEEKS, 0, -1):
            start = monday - timedelta(weeks=offset)
            iso = start.date().isocalendar()
            stem = ROOT / "weekly" / str(iso.year) / f"W{iso.week:02d}"
            pack_raw = _read(repo, stem.with_suffix(".json"))
            pack = json.loads(pack_raw)
            seq = pack["hourly_sequence"]
            diag = pack["hourly_gap_diagnostics"]
            if (pack["contract"] != "WEEKLY_RAW_CALIBRATION_PACK_v3"
                    or (pack["iso_year"], pack["iso_week"]) != (iso.year, iso.week)
                    or pack["readiness"] != "READY" or diag["observed_hours"] != 168
                    or diag["missing_hour_count"] != 0 or seq["spot_complete_hours"] != 168
                    or not start + timedelta(days=7) <= _clock(pack["generated_at_utc"]) <= freeze):
                raise ValueError("incomplete or late weekly source")
            if offset == 1 and pack != completed_capture:
                raise ValueError("completed snapshot differs from issuer input")
            csv_path = stem / "WEEKLY_HOURLY_ENRICHED.csv"
            if pack["enriched_hourly_path"] != csv_path.relative_to(ROOT).as_posix():
                raise ValueError("weekly CSV binding mismatch")
            raw = _read(repo, csv_path)
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError("ambiguous CSV fields")
            rows = list(reader)
            if len(rows) != 168:
                raise ValueError("incomplete hourly snapshot")
            for i, row in enumerate(rows):
                at = start + timedelta(hours=i)
                if (None in row or row["spot_status"] != "PASS"
                        or _clock(row["timestamp_utc"]) != at
                        or not at + timedelta(hours=1) <= _clock(row["source_window_end_utc"]) <= freeze):
                    raise ValueError("invalid hourly source")
            for asset in ASSETS:
                quote = (seq.get("spot_flow_readback") or {}).get(asset)
                if quote is None:
                    if offset == 1:
                        raise ValueError("current quote binding missing")
                    legacy = True
                elif quote.get("symbol") != asset+"USDT" or quote.get("quote_unit") != "USDT":
                    raise ValueError("quote mismatch")
                prefix = asset.lower()
                bars = [_bar([r[prefix+"_"+k] for k in ("open", "high", "low", "close")]) for r in rows]
                aggregate = _aggregate(bars)
                summary = seq[prefix]["week_range"]
                if aggregate != _bar([summary[k] for k in ("open", "high", "low", "close")]):
                    raise ValueError("retained OHLC differs from weekly frame")
                daily[asset].extend(_aggregate(bars[j:j+24]) for j in range(0, 168, 24))
            sources.append({"week": f"{iso.year}-W{iso.week:02d}", "pack_sha256": hashlib.sha256(pack_raw).hexdigest(),
                            "hourly_csv_sha256": hashlib.sha256(raw).hexdigest()})
        assets = {a: benchmark(daily[a]) for a in ASSETS}
        for asset in ASSETS:
            if _number(range_forecast["assets"][asset]["anchor_price"]) != daily[asset][-1][3]:
                raise ValueError("benchmark anchor differs from issuer anchor")
        payload = {"contract": "CN_RANGE_BENCHMARK_FREEZE_v1",
                   "status": "FROZEN_RETAINED_SNAPSHOT", "scientific_admission": False,
                   "generated_unix": generated_unix, "quote_unit": "USDT",
                   "quote_provenance": "LEGACY_RETAINED_COLUMNS_UNATTESTED" if legacy else "RETAINED_METADATA_ONLY",
                   "anchor_date": (monday.date()-timedelta(days=1)).isoformat(),
                   "history_days": 63, "atr_method": "WILDER_ATR14_63_SETTLED_DAYS_HALF_UP_QUOTE_UNIT",
                   "sources": sources, "assets": assets}
        payload["snapshot_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        return payload
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ArithmeticError, OverflowError):
        return unavailable


def row_benchmarks(snapshot, asset, generated_unix):
    """Explicit nulls for missing evidence; never recompute old rows."""
    values = {}
    if (isinstance(snapshot, dict) and snapshot.get("status") == "FROZEN_RETAINED_SNAPSHOT"
            and snapshot.get("generated_unix") == generated_unix):
        values = (snapshot.get("assets") or {}).get(asset) or {}
    return {**{key: values.get(key) for key in ("DUMB1.5", "DUMB2.0", "PREVWK")},
            "baseline_status": "FROZEN_RETAINED_SNAPSHOT" if values else "UNAVAILABLE",
            "baseline_snapshot_sha256": snapshot.get("snapshot_sha256") if values else None,
            "baseline_quote_unit": "USDT" if values else None,
            "baseline_scientific_admission": False}
