"""Shared helpers for the ETF temporal-integrity lab (research only, no production authority).

Everything here READS existing owner outputs; nothing writes to owner paths.
"""
from __future__ import annotations

import csv
import hashlib
import os
import importlib.util
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(os.environ.get("ETF_LAB_REPO", Path(__file__).resolve().parents[3]))
WORK = Path(os.environ.get("ETF_LAB_WORK", "/tmp/etf_temporal_integrity_lab"))  # outputs + live captures; never inside owner paths
LIVE = WORK / "live"
NY = ZoneInfo("America/New_York")
UTC = timezone.utc
PACK = REPO / "04_MARKET_LEARNING/truth_layer/etf_flows/2026-07-26__us-spot-crypto-etf-flow-history"

NYSE_CLOSED = frozenset({
    "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27", "2024-06-19", "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25",
    "2025-01-01", "2025-01-09", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01",
    "2025-11-27", "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19", "2026-07-03",
    "2026-09-07",
})
# Early closes (13:00 ET) relevant to the window; used only for session-close timestamps.
NYSE_EARLY_CLOSE = frozenset({"2024-07-03", "2024-11-29", "2024-12-24", "2025-07-03", "2025-11-28", "2025-12-24", "2026-11-27", "2026-12-24"})


def owner_module():
    spec = importlib.util.spec_from_file_location("farside_etf_owner_ro", REPO / "scripts/data_terminal/farside_etf_owner.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def session_close_utc(day: str) -> datetime:
    d = date.fromisoformat(day)
    hour = 13 if day in NYSE_EARLY_CLOSE else 16
    return datetime(d.year, d.month, d.day, hour, 0, tzinfo=NY).astimezone(UTC)


def is_session(day: str) -> bool:
    d = date.fromisoformat(day)
    return d.weekday() < 5 and day not in NYSE_CLOSED


def next_session(day: str) -> str:
    d = date.fromisoformat(day) + timedelta(days=1)
    while not is_session(d.isoformat()):
        d += timedelta(days=1)
    return d.isoformat()


def session_open_utc(day: str) -> datetime:
    d = date.fromisoformat(day)
    return datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY).astimezone(UTC)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_json(value) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    from html import unescape
    return re.sub(r"\s+", " ", unescape(value)).strip()


def live_table(asset: str) -> dict:
    """Structural read of the captured live Farside page (no values altered).

    Returns the source ticker header exactly as published plus every row's raw cells.
    """
    raw = (LIVE / f"{asset.lower()}.html").read_bytes()
    html = raw.decode("utf-8", "replace")
    start = html.find('<table class="etf">')
    end = html.find("</table>", start)
    table = html[start:end]
    trs = re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, re.I | re.S)
    header_rows, meta_rows, date_rows = [], [], []
    mod = owner_module()
    for tr in trs:
        th = re.findall(r"<th\b[^>]*>(.*?)</th>", tr, re.I | re.S)
        cells = [clean(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)]
        if not cells:
            continue
        d = mod.parse_date_label(cells[0])
        if d is not None:
            date_rows.append({"date": d.isoformat(), "cells": cells})
        elif th and cells[-1].lower() == "total":
            header_rows.append(cells)
        else:
            meta_rows.append({"label": cells[0], "cells": cells, "is_th": bool(th)})
    footer = [m for m in meta_rows if m["label"].lower() == "total"]
    return {"asset": asset, "raw_sha256": sha256_bytes(raw), "bytes": len(raw), "header_rows": header_rows,
            "meta_rows": meta_rows, "footer_total_rows": footer, "date_rows": date_rows,
            "table_content_sha256": sha256_json([header_rows, [r["cells"] for r in date_rows], [m["cells"] for m in meta_rows]])}


def num(cell: str):
    """Owner number semantics (parse_number), kept identical so ledgers agree with the owner."""
    return owner_module().parse_number(cell)


def pack_rows(asset: str) -> list[dict]:
    rows = []
    for path in sorted((PACK / "data").glob(f"us_spot_{asset.lower()}_etf_flows_daily_*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as h:
            rows.extend(csv.DictReader(h))
    rows.sort(key=lambda r: r["date"])
    return rows


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, sort_keys=False, default=str) + "\n")
