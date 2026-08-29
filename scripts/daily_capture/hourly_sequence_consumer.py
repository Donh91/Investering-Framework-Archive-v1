from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_POINTER = Path("03_DAILY_CAPTURE_LOGS/hourly/LATEST.json")
DEFAULT_ROOT = Path("03_DAILY_CAPTURE_LOGS/hourly")
REQUIRED_SPOT_CLOSE_FIELDS = ("btc_close", "eth_close", "ethbtc_close")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def read_latest_complete_spot_row(
    pointer_path: Path = DEFAULT_POINTER,
    hourly_root: Path = DEFAULT_ROOT,
):
    """Resolve the final materialized spot row from an hourly sequence pointer.

    ``window_end_utc`` in ``HOURLY_SEQUENCE_LATEST_POINTER_v2_2`` is an
    exclusive right boundary.  A pointer ending at 00:00Z therefore owns a
    final 23:00Z row in the previous UTC day's permanent CSV.  Consumers must
    never interpret the boundary itself as a materialized observation.
    """

    try:
        pointer = json.loads(pointer_path.read_text())
    except Exception as exc:
        raise RuntimeError("hourly sequence pointer missing/unreadable") from exc
    if pointer.get("status") != "COMPLETE":
        raise RuntimeError("hourly sequence pointer missing/incomplete")

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
