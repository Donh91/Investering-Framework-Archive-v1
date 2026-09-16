from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path

DEFAULT_POINTER = Path("03_DAILY_CAPTURE_LOGS/hourly/LATEST.json")
DEFAULT_ROOT = Path("03_DAILY_CAPTURE_LOGS/hourly")
REQUIRED_SPOT_CLOSE_FIELDS = ("btc_close", "eth_close", "ethbtc_close")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def pointer_has_complete_spot(pointer: dict) -> bool:
    """Return True only when the pointer proves the requested spot window is complete.

    Global ``PARTIAL`` can be caused by an incomplete derivatives lane. Spot-only
    consumers may proceed only when the owner pointer explicitly proves that all
    requested spot hours are present. Missing/invalid counters and FAILED pointers
    remain fail-closed.
    """
    status = pointer.get("status")
    if status == "COMPLETE":
        return True
    if status != "PARTIAL":
        return False
    requested = pointer.get("requested_hours")
    spot_complete = pointer.get("spot_complete_hours")
    if isinstance(requested, bool) or isinstance(spot_complete, bool):
        return False
    if not isinstance(requested, int) or not isinstance(spot_complete, int) or requested <= 0:
        return False
    return spot_complete == requested


def _dates_between(first: date, last: date) -> list[date]:
    days = (last - first).days
    return [first + timedelta(days=i) for i in range(days + 1)]


def read_complete_spot_window(
    pointer_path: Path = DEFAULT_POINTER,
    hourly_root: Path = DEFAULT_ROOT,
    *,
    minimum_rows: int = 1,
) -> tuple[dict, list[tuple[datetime, dict[str, str]]]]:
    """Read the exact completed spot window owned by the hourly pointer.

    The pointer's right boundary is exclusive. The returned rows are exactly the
    requested closed 1h candles and are accepted from a global PARTIAL pointer only
    when explicit owner counters prove the spot lane itself is complete.
    """
    try:
        pointer = json.loads(pointer_path.read_text())
    except Exception as exc:
        raise RuntimeError("hourly sequence pointer missing/unreadable") from exc
    if not pointer_has_complete_spot(pointer):
        raise RuntimeError("hourly sequence pointer missing/incomplete spot coverage")

    raw_end = pointer.get("window_end_utc")
    if not raw_end:
        raise RuntimeError("hourly sequence pointer missing window_end_utc")
    boundary = parse_utc(str(raw_end))
    requested = pointer.get("requested_hours")
    if isinstance(requested, bool) or not isinstance(requested, int) or requested <= 0:
        raise RuntimeError("hourly owner lookback missing/insufficient")

    first_ts = boundary - timedelta(hours=requested)
    rows_by_ts: dict[datetime, dict[str, str]] = {}
    for day in _dates_between(first_ts.date(), (boundary - timedelta(microseconds=1)).date()):
        csv_path = hourly_root / day.strftime("%Y/%m/%Y-%m-%d.csv")
        if not csv_path.exists():
            continue
        with csv_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("spot_status") != "PASS":
                    continue
                raw_ts = row.get("timestamp_utc")
                if not raw_ts:
                    continue
                ts = parse_utc(raw_ts)
                if first_ts <= ts < boundary:
                    rows_by_ts[ts] = row

    expected = {boundary - timedelta(hours=i) for i in range(1, requested + 1)}
    if not expected.issubset(rows_by_ts):
        raise RuntimeError("hourly owner window has missing completed spot candles")
    rows = [(ts, rows_by_ts[ts]) for ts in sorted(expected)]
    if len(rows) < minimum_rows:
        raise RuntimeError("insufficient hourly spot rows")
    for _, row in rows:
        if any(not row.get(field) for field in REQUIRED_SPOT_CLOSE_FIELDS):
            raise RuntimeError("hourly spot window row missing direct spot close")
    return pointer, rows


def read_latest_complete_spot_row(
    pointer_path: Path = DEFAULT_POINTER,
    hourly_root: Path = DEFAULT_ROOT,
):
    """Resolve the final materialized spot row from an hourly sequence pointer.

    This intentionally keeps its narrow latest-row behavior for existing consumers,
    while sharing the same pointer-level spot completeness contract as full-window
    consumers.
    """
    try:
        pointer = json.loads(pointer_path.read_text())
    except Exception as exc:
        raise RuntimeError("hourly sequence pointer missing/unreadable") from exc
    if not pointer_has_complete_spot(pointer):
        raise RuntimeError("hourly sequence pointer missing/incomplete spot coverage")

    raw_end = pointer.get("window_end_utc")
    if not raw_end:
        raise RuntimeError("hourly sequence pointer missing window_end_utc")
    boundary = parse_utc(str(raw_end))
    final_row_day = boundary - timedelta(microseconds=1)
    csv_path = hourly_root / final_row_day.strftime("%Y/%m/%Y-%m-%d.csv")
    if not csv_path.exists():
        raise RuntimeError(f"hourly permanent CSV missing: {csv_path}")

    rows: list[tuple[datetime, dict[str, str]]] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("spot_status") != "PASS":
                continue
            raw_ts = row.get("timestamp_utc")
            if not raw_ts:
                continue
            ts = parse_utc(raw_ts)
            if ts < boundary:
                rows.append((ts, row))

    if not rows:
        raise RuntimeError("no complete hourly row available before exclusive window end")
    ts, row = max(rows, key=lambda item: item[0])
    if any(not row.get(field) for field in REQUIRED_SPOT_CLOSE_FIELDS):
        raise RuntimeError("latest hourly row missing direct spot close")
    return pointer, ts, row
