#!/usr/bin/env python3
from __future__ import annotations

import os
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import free_altseason_bootstrap_resilient as resilient

DEFAULT_WORKERS = 12
MAX_WORKERS = 24


def worker_count() -> int:
    raw = os.environ.get("HISTORICAL_VISION_MAX_WORKERS", str(DEFAULT_WORKERS))
    try:
        value = int(raw)
    except ValueError:
        value = DEFAULT_WORKERS
    return max(1, min(MAX_WORKERS, value))


def fetch_daily(day: datetime, symbol: str):
    try:
        rows = list(resilient._vision_daily(symbol, day))
        return day, rows, None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return day, [], "HTTP_404"
        raise


def parallel_daily_month(symbol: str, first_day: datetime, last_day: datetime):
    days = []
    day = first_day
    while day <= last_day:
        days.append(day)
        day += timedelta(days=1)

    results = {}
    with ThreadPoolExecutor(max_workers=worker_count(), thread_name_prefix="vision-daily") as pool:
        futures = {pool.submit(fetch_daily, day, symbol): day for day in days}
        for future in as_completed(futures):
            day, rows, status = future.result()
            results[day] = (rows, status)

    for day in sorted(results):
        rows, _ = results[day]
        for row in rows:
            yield row


def parallel_vision_klines(symbol: str, start_ms: int, end_ms: int):
    """Scientifically equivalent Vision transport with bounded concurrent daily retrieval before 2022.

    Daily archives remain preferred before 2022. Concurrency changes only retrieval order. Rows are
    re-sorted by calendar day and timestamp before emission, preserving deterministic input semantics.
    """
    start = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
    end = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc)
    month = resilient._month_floor(start)
    current_month = resilient._month_floor(datetime.now(timezone.utc))
    prefer_daily_before = datetime(2022, 1, 1, tzinfo=timezone.utc)
    emitted = set()

    while month <= end:
        month_end = resilient._next_month(month) - timedelta(milliseconds=1)
        use_monthly = month >= prefer_daily_before and month < current_month and month_end <= end
        monthly_ok = False

        if use_monthly:
            try:
                rows = list(resilient._vision_monthly(symbol, month))
                rows.sort(key=lambda row: int(row[0]))
                for row in rows:
                    monthly_ok = True
                    ts = int(row[0])
                    if start_ms <= ts <= end_ms and ts not in emitted:
                        emitted.add(ts)
                        yield row
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise

        if not use_monthly or not monthly_ok:
            first_day = max(start, month)
            first_day = datetime(first_day.year, first_day.month, first_day.day, tzinfo=timezone.utc)
            last_day = min(end, month_end)
            daily_rows = list(parallel_daily_month(symbol, first_day, last_day))
            daily_rows.sort(key=lambda row: int(row[0]))
            for row in daily_rows:
                ts = int(row[0])
                if start_ms <= ts <= end_ms and ts not in emitted:
                    emitted.add(ts)
                    yield row

        month = resilient._next_month(month)


def main():
    resilient.vision_klines = parallel_vision_klines
    return resilient.main()


if __name__ == "__main__":
    raise SystemExit(main())
