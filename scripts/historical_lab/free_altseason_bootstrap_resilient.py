#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import importlib.util
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
TARGET = BASE / "free_altseason_bootstrap.py"
VISION = "https://data.binance.vision/data/spot"
UA = {"User-Agent": "Investering-Historical-Altseason-Lab/1.1", "Accept": "*/*"}


def _norm_ts(value: str | int) -> int:
    x = int(value)
    # Binance Vision spot archives use microsecond timestamps in newer files.
    if x > 10**15:
        x //= 1000
    return x


def _download_zip(url: str, retries: int = 4) -> bytes:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 404:
                raise
        except Exception as exc:
            last = exc
        time.sleep(min(8, 0.8 * (2 ** attempt)))
    raise RuntimeError(f"vision_fetch_failed:{url}:{last}")


def _rows_from_zip(blob: bytes):
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith('.csv')]
        if not names:
            return
        with zf.open(names[0]) as fh:
            text = io.TextIOWrapper(fh, encoding='utf-8')
            for row in csv.reader(text):
                if not row or not row[0].strip().isdigit():
                    continue
                if len(row) < 11:
                    continue
                out = list(row)
                out[0] = _norm_ts(out[0])
                if len(out) > 6 and str(out[6]).strip().isdigit():
                    out[6] = _norm_ts(out[6])
                yield out


def _month_floor(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)


def _next_month(dt: datetime) -> datetime:
    if dt.month == 12:
        return datetime(dt.year + 1, 1, 1, tzinfo=timezone.utc)
    return datetime(dt.year, dt.month + 1, 1, tzinfo=timezone.utc)


def _vision_monthly(symbol: str, month: datetime):
    ym = month.strftime('%Y-%m')
    url = f"{VISION}/monthly/klines/{symbol}/1h/{symbol}-1h-{ym}.zip"
    return _rows_from_zip(_download_zip(url))


def _vision_daily(symbol: str, day: datetime):
    ds = day.strftime('%Y-%m-%d')
    url = f"{VISION}/daily/klines/{symbol}/1h/{symbol}-1h-{ds}.zip"
    return _rows_from_zip(_download_zip(url))


def vision_klines(symbol: str, start_ms: int, end_ms: int):
    start = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
    end = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc)
    current_month = _month_floor(datetime.now(timezone.utc))
    month = _month_floor(start)
    emitted = set()

    while month <= end:
        month_end = _next_month(month) - timedelta(milliseconds=1)
        use_monthly = month < current_month and month >= _month_floor(start) and month_end <= end
        rows = None
        if use_monthly:
            try:
                rows = _vision_monthly(symbol, month)
                for row in rows:
                    ts = int(row[0])
                    if start_ms <= ts <= end_ms and ts not in emitted:
                        emitted.add(ts)
                        yield row
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
                rows = None

        if not use_monthly or rows is None:
            day = max(start, month)
            day = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            last_day = min(end, month_end)
            while day <= last_day:
                try:
                    for row in _vision_daily(symbol, day):
                        ts = int(row[0])
                        if start_ms <= ts <= end_ms and ts not in emitted:
                            emitted.add(ts)
                            yield row
                except urllib.error.HTTPError as exc:
                    if exc.code != 404:
                        raise
                    # Missing archive is expected for symbols not yet listed or delisted.
                day += timedelta(days=1)
        month = _next_month(month)


def load_target():
    spec = importlib.util.spec_from_file_location("free_altseason_bootstrap_base", TARGET)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot_load_base_bootstrap")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    mod = load_target()
    original = mod.fetch_klines

    def resilient_fetch_klines(symbol: str, start_ms: int, end_ms: int):
        try:
            yielded = False
            for row in original(symbol, start_ms, end_ms):
                yielded = True
                yield row
            if yielded:
                return
        except Exception as exc:
            print(f"REST_KLINES_FALLBACK {symbol}: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"VISION_KLINES {symbol} {mod.ms_to_iso(start_ms)} -> {mod.ms_to_iso(end_ms)}", file=sys.stderr)
        yield from vision_klines(symbol, start_ms, end_ms)

    mod.fetch_klines = resilient_fetch_klines
    if not hasattr(mod, 'main'):
        raise RuntimeError('base_bootstrap_missing_main')
    return mod.main()


if __name__ == '__main__':
    raise SystemExit(main())
