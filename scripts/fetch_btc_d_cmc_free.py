#!/usr/bin/env python3
"""Fetch free daily CoinMarketCap BTC dominance history from the public website endpoint.

No API key. Standard library only.
No interpolation, no current-day backfill, and no TradingView relabelling.
"""

from __future__ import annotations

import csv
import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BASE = "https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/historical"

OUT_FIELDS = [
    "date_utc",
    "btc_d_close",
    "source_symbol",
    "source_provider",
    "source_convention",
    "settled_timezone",
    "source_timestamp",
    "source_verified_timestamp",
    "print_status",
    "revision_delta",
    "data_quality",
    "source_status",
    "notes",
]

START_DATE = date(2023, 1, 1)
USER_AGENT = (
    "Mozilla/5.0 (compatible; Investering-Truth-Layer-Recovery/1.0; "
    "+https://github.com/)"
)

def epoch_start(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())

def fetch_json(start: date, end: date, attempts: int = 4) -> tuple[bytes, Any, str]:
    params = {
        "convertId": "2781",
        "timeStart": str(epoch_start(start)),
        "timeEnd": str(epoch_start(end)),
        "interval": "1d",
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json,text/plain,*/*",
                    "Referer": "https://coinmarketcap.com/charts/bitcoin-dominance/",
                },
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                raw = response.read()
            return raw, json.loads(raw), url
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"CoinMarketCap public web request failed: {last_error}")

def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds > 10_000_000_000:
            seconds /= 1000.0
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    text = str(value).strip()
    if text.isdigit():
        return parse_timestamp(int(text))
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def find_quotes(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("quotes"), list):
            return data["quotes"]
        if isinstance(payload.get("quotes"), list):
            return payload["quotes"]
    raise ValueError("Could not locate data.quotes in CoinMarketCap response")

def dominance_value(row: dict[str, Any]) -> float:
    candidates = (
        "btcDominance",
        "btc_dominance",
        "bitcoinDominance",
        "bitcoin_dominance",
    )
    for key in candidates:
        if key in row and row[key] is not None:
            return float(row[key])
    raise ValueError(f"BTC dominance field missing. Keys: {sorted(row)}")

def anchor_dates(dates: list[date], count: int = 12) -> list[date]:
    if len(dates) <= count:
        return dates
    indexes = sorted({round(i * (len(dates) - 1) / (count - 1)) for i in range(count)})
    return [dates[i] for i in indexes]

def main() -> int:
    out = Path("btc_d_output")
    out.mkdir(parents=True, exist_ok=True)

    verified = datetime.now(timezone.utc).replace(microsecond=0)
    latest_complete = verified.date() - timedelta(days=1)

    raw, payload, request_url = fetch_json(START_DATE, latest_complete)
    (out / "BTC_D_CMC_RAW_SOURCE.json").write_bytes(raw)

    quotes = find_quotes(payload)
    by_date: dict[date, tuple[datetime, float]] = {}
    duplicate_dates: list[str] = []
    parse_errors: list[str] = []
    future_rows = 0

    for index, row in enumerate(quotes):
        try:
            dt = parse_timestamp(row.get("timestamp"))
            value = dominance_value(row)
            if not 0 <= value <= 100:
                raise ValueError(f"dominance outside 0..100: {value}")
        except Exception as exc:
            parse_errors.append(f"quote_index={index}: {exc}")
            continue

        d = dt.date()
        if d < START_DATE:
            continue
        if d > latest_complete:
            future_rows += 1
            continue
        if d in by_date:
            duplicate_dates.append(d.isoformat())
            continue
        by_date[d] = (dt, value)

    dates = sorted(by_date)
    rows = []
    gaps = []
    previous = None
    for d in dates:
        if previous and d > previous + timedelta(days=1):
            gaps.append((previous + timedelta(days=1), d - timedelta(days=1)))
        previous = d
        dt, value = by_date[d]
        rows.append({
            "date_utc": d.isoformat(),
            "btc_d_close": f"{value:.10f}".rstrip("0").rstrip("."),
            "source_symbol": "CMC_GLOBAL_METRICS_BTC_DOMINANCE",
            "source_provider": "CoinMarketCap",
            "source_convention": (
                "CMC_DIRECT_SOURCE_CONVENTION: Bitcoin market cap / "
                "total market cap of cryptoassets tracked by CoinMarketCap * 100"
            ),
            "settled_timezone": "UTC",
            "source_timestamp": dt.isoformat().replace("+00:00", "Z"),
            "source_verified_timestamp": verified.isoformat().replace("+00:00", "Z"),
            "print_status": "SETTLED_COMPLETE_DATE",
            "revision_delta": "NOT_COMPUTABLE",
            "data_quality": "PASS",
            "source_status": "PUBLIC_SOURCE_BACKED",
            "notes": "Direct CMC historical global-metrics BTC dominance; not TradingView top-125 convention.",
        })

    csv_path = out / "BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    anchors = anchor_dates(dates)
    latest_three = dates[-3:] if len(dates) >= 3 else dates

    status = "PASS"
    reasons = []
    if not dates:
        status = "FAIL"
        reasons.append("No usable daily rows")
    else:
        if dates[0] > START_DATE:
            status = "PARTIAL"
            reasons.append(f"First date is {dates[0]}, later than {START_DATE}")
        if dates[-1] < latest_complete:
            status = "PARTIAL"
            reasons.append(f"Last date is {dates[-1]}, earlier than {latest_complete}")
        if len(anchors) < 12:
            status = "PARTIAL"
            reasons.append("Fewer than 12 anchor dates")
        if len(latest_three) < 3:
            status = "PARTIAL"
            reasons.append("Fewer than latest three complete dates")
        if duplicate_dates or parse_errors:
            status = "PARTIAL"
            reasons.append("Duplicate dates or parse errors present")

    raw_hash = hashlib.sha256(raw).hexdigest()
    csv_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    receipt = f"""# BTC.D CoinMarketCap Raw Source Receipt

- Provider: CoinMarketCap public website data endpoint
- Endpoint: `{request_url}`
- Retrieval timestamp: `{verified.isoformat().replace('+00:00', 'Z')}`
- Raw SHA-256: `{raw_hash}`
- Raw bytes: `{len(raw)}`
- Raw quote records: `{len(quotes)}`
- Authentication: none
- Source convention: `CMC_DIRECT_SOURCE_CONVENTION`
- TradingView equivalence: `NO`
"""
    (out / "BTC_D_SOURCE_RECEIPT.md").write_text(receipt, encoding="utf-8")

    report_lines = [
        "# BTC.D Validation Report",
        "",
        f"- Validation status: `{status}`",
        f"- Normalized rows: {len(rows)}",
        f"- First date: {dates[0] if dates else 'DATA_MISSING'}",
        f"- Last date: {dates[-1] if dates else 'DATA_MISSING'}",
        f"- Required latest complete date: {latest_complete}",
        f"- Future/current partial rows excluded: {future_rows}",
        f"- Duplicate dates rejected: {len(duplicate_dates)}",
        f"- Parse errors: {len(parse_errors)}",
        f"- Genuine date-gap ranges: {len(gaps)}",
        f"- Raw SHA-256: `{raw_hash}`",
        f"- Normalized CSV SHA-256: `{csv_hash}`",
        "",
        "## Convention",
        "",
        "`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.",
        "",
        "This is not the TradingView top-125 convention.",
        "",
        "## Twelve dispersed anchor dates",
        "",
    ]
    report_lines.extend(f"- {d}: {by_date[d][1]}" for d in anchors)
    report_lines.extend(["", "## Latest three complete dates", ""])
    report_lines.extend(f"- {d}: {by_date[d][1]}" for d in latest_three)
    report_lines.extend(["", "## Genuine gap ranges", ""])
    report_lines.extend(f"- {a} through {b}" for a, b in gaps[:100])
    if not gaps:
        report_lines.append("- None")
    report_lines.extend(["", "## Issues", ""])
    report_lines.extend(f"- {x}" for x in (reasons + parse_errors + [f"duplicate: {d}" for d in duplicate_dates])[:100])
    if not reasons and not parse_errors and not duplicate_dates:
        report_lines.append("- None")
    report_lines.extend([
        "",
        "## Readiness",
        "",
        "A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.",
        "It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.",
    ])
    (out / "BTC_D_VALIDATION_REPORT.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        "status": status,
        "rows": len(rows),
        "first_date": dates[0].isoformat() if dates else None,
        "last_date": dates[-1].isoformat() if dates else None,
        "raw_sha256": raw_hash,
        "csv_sha256": csv_hash,
        "output_dir": str(out),
    }, indent=2))
    return 0 if rows else 2

if __name__ == "__main__":
    raise SystemExit(main())
