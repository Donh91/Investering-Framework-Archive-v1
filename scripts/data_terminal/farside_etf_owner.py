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

URLS = {
    "BTC": "https://farside.co.uk/bitcoin-etf-flow-all-data/",
    "ETH": "https://farside.co.uk/ethereum-etf-flow-all-data/",
}

CANONICAL_FUND_HEADERS = {
    "BTC": ["IBIT", "FBTC", "BITB", "ARKB", "BTCO", "EZBC", "BRRR", "HODL", "BTCW", "MSBT", "GBTC", "BTC"],
    "ETH": ["ETHA", "ETHB", "FETH", "ETHW", "TETH", "ETHV", "QETH", "EZET", "ETHE", "ETH"],
}


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


def normalized_header(cells: list[str]) -> list[str]:
    return [re.sub(r"[^a-z0-9]+", "", cell.lower()) for cell in cells]


def looks_like_header(cells: list[str]) -> bool:
    if len(cells) < 3:
        return False
    normalized = normalized_header(cells)
    return normalized[0] == "date" and normalized[-1] == "total"


def two_row_header_candidate(rows: list[list[str]], asset: str) -> list[str] | None:
    expected = CANONICAL_FUND_HEADERS[asset]
    expected_norm = [value.lower() for value in expected]
    # Ethereum's current Farside table uses one issuer-name row ending in Total
    # followed by a ticker row with blank edge cells. Reconstruct only the schema,
    # never values, and only when the ticker sequence exactly matches the frozen
    # source schema.
    for index, cells in enumerate(rows[:-1]):
        normalized = normalized_header(cells)
        if not normalized or normalized[-1] != "total":
            continue
        next_cells = rows[index + 1]
        next_norm = normalized_header(next_cells)
        tickers = [value for value in next_norm if value]
        if tickers == expected_norm:
            return ["Date", *expected, "Total"]
    return None


def parse_table(html: str, asset: str, today_utc: date) -> tuple[list[dict[str, Any]], list[str], str]:
    table_rows = re.findall(r"<tr\b[^>]*>(.*?)</tr>", html, re.I | re.S)
    headers: list[str] | None = None
    header_mode = "DIRECT_DATE_TOTAL"
    parsed: list[dict[str, Any]] = []
    non_date_rows: list[list[str]] = []
    for tr in table_rows:
        th = [clean(cell) for cell in re.findall(r"<th\b[^>]*>(.*?)</th>", tr, re.I | re.S)]
        cells = [clean(cell) for cell in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)]
        if looks_like_header(cells):
            headers = cells
            continue
        if looks_like_header(th):
            headers = th
            continue
        if len(cells) < 3:
            continue
        parsed_date = parse_date_label(cells[0])
        if parsed_date is None:
            non_date_rows.append(cells)
            continue
        values = [parse_number(cell) for cell in cells[1:]]
        if not any(value is not None for value in values):
            continue
        parsed.append({
            "asset": asset,
            "date": parsed_date.isoformat(),
            "date_label": cells[0],
            "values": values,
            "raw_cells": cells,
        })

    if not headers:
        headers = two_row_header_candidate(non_date_rows, asset)
        if headers:
            header_mode = "SOURCE_TWO_ROW_TICKER_HEADER"

    if not headers and parsed:
        expected = ["Date", *CANONICAL_FUND_HEADERS[asset], "Total"]
        expected_values = len(expected) - 1
        if all(len(row["values"]) == expected_values for row in parsed):
            # Last-resort schema binding only: the asset-specific column order is
            # frozen above and accepted solely when every parsed source row has the
            # exact expected width. No numeric value is filled or transformed.
            headers = expected
            header_mode = "CANONICAL_ASSET_SCHEMA_EXACT_WIDTH_FALLBACK"

    if not headers or len(headers) < 3:
        raise ValueError("HEADER_NOT_FOUND")
    if not looks_like_header(headers):
        raise ValueError("HEADER_CONTRACT_DRIFT")
    expected_headers = ["Date", *CANONICAL_FUND_HEADERS[asset], "Total"]
    if normalized_header(headers) != normalized_header(expected_headers):
        raise ValueError("HEADER_SCHEMA_MISMATCH")
    final_rows = [row for row in parsed if date.fromisoformat(row["date"]) < today_utc]
    return final_rows, headers, header_mode


def decorate(row: dict[str, Any], headers: list[str], header_mode: str) -> dict[str, Any]:
    item = dict(row)
    values = item.pop("values")
    expected_columns = len(headers) - 1
    if len(values) != expected_columns:
        raise ValueError("COLUMN_COUNT_DRIFT")
    item["headers"] = headers
    item["header_mode"] = header_mode
    item["fund_headers"] = headers[1:-1]
    item["fund_values"] = values[:-1]
    item["reported_total"] = values[-1]
    item["session_final"] = True
    calculated = sum(value for value in item["fund_values"] if value is not None)
    tolerance = None if item["reported_total"] is None else max(0.2, abs(item["reported_total"]) * 0.01)
    parity = None if item["reported_total"] is None else abs(calculated - item["reported_total"]) <= tolerance
    raw_fund_cells = item["raw_cells"][1:-1]
    unknown_cells = [
        {"fund": item["fund_headers"][index], "raw": raw_fund_cells[index]}
        for index, value in enumerate(item["fund_values"])
        if value is None
    ]
    item["calculated_total"] = calculated
    item["total_parity"] = parity
    item["unknown_fund_cells"] = unknown_cells
    item["unknown_fund_cell_count"] = len(unknown_cells)
    item["unknown_cells_fully_accounted_by_reported_total"] = bool(parity is True)
    return item


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--fixture-dir", type=Path)
    ap.add_argument("--now-utc")
    ap.add_argument("--history-limit", type=int, default=10)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00")) if args.now_utc else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    output_rows: list[dict[str, Any]] = []
    history_rows: dict[str, list[dict[str, Any]]] = {}
    source_hashes: dict[str, str] = {}
    errors: list[dict[str, str]] = []
    parity_failed = False

    for asset, url in URLS.items():
        try:
            if args.fixture_dir:
                raw = (args.fixture_dir / f"{asset.lower()}.html").read_bytes()
            else:
                request = urllib.request.Request(url, headers={"User-Agent": "InvesteringFramework/2.2 (+verified ETF owner capture)"})
                with urllib.request.urlopen(request, timeout=30) as response:
                    raw = response.read()
            source_hashes[asset] = hashlib.sha256(raw).hexdigest()
            rows, headers, header_mode = parse_table(raw.decode("utf-8", "replace"), asset, now.date())
            if not rows:
                raise ValueError("NO_FINALIZED_ROWS")
            decorated = [decorate(row, headers, header_mode) for row in rows]
            decorated.sort(key=lambda row: row["date"])
            recent = decorated[-max(1, args.history_limit):]
            history_rows[asset] = recent
            latest = recent[-1]
            if latest["total_parity"] is False:
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
        "contract": "FARSIDE_ETF_OWNER_SNAPSHOT_v4",
        "retrieved_at_utc": now.isoformat().replace("+00:00", "Z"),
        "status": status,
        "rows": output_rows,
        "history_rows": history_rows,
        "history_limit": args.history_limit,
        "errors": errors,
        "source_hashes": source_hashes,
        "authority": "SHADOW_ONLY",
        "unknown_cells_are_not_imputed": True,
    }
    raw_snapshot = (json.dumps(snapshot, sort_keys=True, separators=(",", ":")) + "\n").encode()
    snapshot_sha = hashlib.sha256(raw_snapshot).hexdigest()
    (args.output_dir / "owner_snapshot.json").write_bytes(raw_snapshot)
    receipt = {
        "contract": "FARSIDE_ETF_OWNER_RECEIPT_v4",
        "status": status,
        "snapshot_sha256": snapshot_sha,
        "row_count": len(output_rows),
        "history_row_count": sum(len(rows) for rows in history_rows.values()),
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
