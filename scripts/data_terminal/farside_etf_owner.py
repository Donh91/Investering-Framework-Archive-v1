from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import date, datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

URLS = {"BTC": "https://farside.co.uk/btc/", "ETH": "https://farside.co.uk/eth/"}


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def parse_number(value: str) -> float | None:
    value = value.strip().replace(",", "").replace("$", "").replace("(", "-").replace(")", "")
    if value in {"", "-", "–", "—", "N/A"}:
        return None
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*([KMB]?)", value, re.I)
    if not match:
        return None
    scale = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[match.group(2).upper()]
    return float(match.group(1)) * scale


def parse_date_label(value: str) -> date | None:
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    return None


def parse_table(html: str, asset: str, today_utc: date) -> tuple[list[dict[str, Any]], list[str]]:
    table_rows = re.findall(r"<tr\b[^>]*>(.*?)</tr>", html, re.I | re.S)
    headers: list[str] | None = None
    parsed: list[dict[str, Any]] = []
    for tr in table_rows:
        th = [clean(cell) for cell in re.findall(r"<th\b[^>]*>(.*?)</th>", tr, re.I | re.S)]
        if th and any("date" in cell.lower() for cell in th):
            headers = th
            continue
        cells = [clean(cell) for cell in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)]
        if len(cells) < 3:
            continue
        parsed_date = parse_date_label(cells[0])
        if parsed_date is None:
            continue
        values = [parse_number(cell) for cell in cells[1:]]
        if not any(value is not None for value in values):
            continue
        parsed.append({"asset": asset, "date": parsed_date.isoformat(), "date_label": cells[0], "values": values, "raw_cells": cells})
    if not headers or len(headers) < 3:
        raise ValueError("HEADER_NOT_FOUND")
    normalized = [re.sub(r"[^a-z0-9]+", "", header.lower()) for header in headers]
    if normalized[0] != "date" or "total" not in normalized[-1]:
        raise ValueError("HEADER_CONTRACT_DRIFT")
    final_rows = [row for row in parsed if date.fromisoformat(row["date"]) < today_utc]
    return final_rows, headers


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--fixture-dir", type=Path)
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00")) if args.now_utc else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    output_rows: list[dict[str, Any]] = []
    source_hashes: dict[str, str] = {}
    errors: list[dict[str, str]] = []
    parity_failed = False

    for asset, url in URLS.items():
        try:
            if args.fixture_dir:
                raw = (args.fixture_dir / f"{asset.lower()}.html").read_bytes()
            else:
                request = urllib.request.Request(url, headers={"User-Agent": "InvesteringFramework/2.0 (+verified ETF owner capture)"})
                with urllib.request.urlopen(request, timeout=30) as response:
                    raw = response.read()
            source_hashes[asset] = hashlib.sha256(raw).hexdigest()
            rows, headers = parse_table(raw.decode("utf-8", "replace"), asset, now.date())
            if not rows:
                raise ValueError("NO_FINALIZED_ROWS")
            latest = max(rows, key=lambda row: row["date"])
            values = latest.pop("values")
            expected_columns = len(headers) - 1
            if len(values) != expected_columns:
                raise ValueError("COLUMN_COUNT_DRIFT")
            latest["headers"] = headers
            latest["fund_headers"] = headers[1:-1]
            latest["fund_values"] = values[:-1]
            latest["reported_total"] = values[-1]
            latest["session_final"] = True
            calculated = sum(value for value in latest["fund_values"] if value is not None)
            parity = None if latest["reported_total"] is None else abs(calculated - latest["reported_total"]) <= max(0.2, abs(latest["reported_total"]) * 0.01)
            latest["calculated_total"] = calculated
            latest["total_parity"] = parity
            if parity is False:
                parity_failed = True
            output_rows.append(latest)
        except Exception as exc:
            errors.append({"asset": asset, "error": str(exc)})

    if not output_rows:
        status = "SOURCE_UNAVAILABLE"
    elif len(output_rows) != 2 or errors or parity_failed:
        status = "DEGRADED"
    else:
        status = "PASS"

    snapshot = {
        "contract": "FARSIDE_ETF_OWNER_SNAPSHOT_v2",
        "retrieved_at_utc": now.isoformat().replace("+00:00", "Z"),
        "status": status,
        "rows": output_rows,
        "errors": errors,
        "source_hashes": source_hashes,
        "authority": "SHADOW_ONLY",
    }
    raw_snapshot = (json.dumps(snapshot, sort_keys=True, separators=(",", ":")) + "\n").encode()
    snapshot_sha = hashlib.sha256(raw_snapshot).hexdigest()
    (args.output_dir / "owner_snapshot.json").write_bytes(raw_snapshot)
    receipt = {
        "contract": "FARSIDE_ETF_OWNER_RECEIPT_v2",
        "status": status,
        "snapshot_sha256": snapshot_sha,
        "row_count": len(output_rows),
        "parity_failed": parity_failed,
        "source_type": "WEB_TABLE",
        "portfolio_action": False,
    }
    (args.output_dir / "receipt.json").write_text(json.dumps(receipt, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    if status == "SOURCE_UNAVAILABLE":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
