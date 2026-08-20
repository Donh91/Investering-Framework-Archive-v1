#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

import free_altseason_bootstrap_resilient as resilient

DEFAULT_WORKERS = 12
MAX_WORKERS = 24
ARCHIVE_FIRST_REASON = "BINANCE_REST_BYPASSED_ARCHIVE_FIRST_REPRODUCIBILITY"
AUDIT_PATH = Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/FREE_SOURCE_AUDIT.json")


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
    """Archive-first deterministic Vision transport for the historical laboratory.

    Before 2022, corrected daily archives remain preferred. From 2022 onward, completed monthly
    archives are used when available, with daily fallback when they are not. Bounded concurrency
    changes retrieval order only. Rows are sorted back into timestamp order before emission.
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


def archive_first_load_target():
    """Load the unchanged analytical engine but bypass live REST for this historical archive study."""
    mod = ORIGINAL_LOAD_TARGET()

    def archive_first_marker(symbol: str, start_ms: int, end_ms: int):
        raise RuntimeError(ARCHIVE_FIRST_REASON)
        yield  # pragma: no cover - keeps generator semantics explicit

    mod.fetch_klines = archive_first_marker
    return mod


def annotate_source_audit():
    if not AUDIT_PATH.exists():
        return
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    events = audit.get("source_resolution_events") or []
    for event in events:
        if event.get("source") == "BINANCE_REST_FAILED" and ARCHIVE_FIRST_REASON in str(event.get("error", "")):
            event["source"] = "BINANCE_REST_BYPASSED_ARCHIVE_FIRST"
            event["error"] = None
    audit["historical_transport_policy"] = {
        "contract": "BINANCE_VISION_ARCHIVE_FIRST_TRANSPORT_v1",
        "archive_first": True,
        "pre_2022_resolution": "DAILY_ARCHIVES_PREFERRED",
        "post_2022_resolution": "COMPLETED_MONTHLY_WITH_DAILY_FALLBACK",
        "daily_download_workers": worker_count(),
        "bounded_worker_cap": MAX_WORKERS,
        "deterministic_timestamp_reordering": True,
        "analysis_semantics_changed": False,
        "reason": "Historical reproducibility and archive revision control; avoid geography-sensitive live REST retries.",
    }
    audit.setdefault("limitations", []).append(
        "Historical kline transport is archive-first for reproducibility. Live Binance REST is intentionally bypassed in this laboratory run and this bypass is recorded explicitly."
    )
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")


ORIGINAL_LOAD_TARGET = resilient.load_target


def main():
    resilient.vision_klines = parallel_vision_klines
    resilient.load_target = archive_first_load_target
    rc = resilient.main()
    annotate_source_audit()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
