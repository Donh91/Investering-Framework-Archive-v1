#!/usr/bin/env python3
"""Fail-closed structural QA for ETF flow history pack v1.1."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPECTED = {
    "btc": {"rows": 651, "start": "2024-01-11", "end": "2026-07-24", "non_sessions": 16,
            "funds": ["IBIT","FBTC","BITB","ARKB","BTCO","EZBC","BRRR","HODL","BTCW","MSBT","GBTC","BTC"]},
    "eth": {"rows": 513, "start": "2024-07-23", "end": "2026-07-24", "non_sessions": 10,
            "funds": ["ETHA","ETHB","FETH","ETHW","TETH","ETHV","QETH","EZET","ETHE","ETH"]},
}
NYSE_FULL_CLOSURES = {
    "2024-01-15","2024-02-19","2024-03-29","2024-05-27","2024-06-19","2024-07-04","2024-09-02","2024-11-28","2024-12-25",
    "2025-01-01","2025-01-09","2025-01-20","2025-02-17","2025-04-18","2025-05-26","2025-06-19","2025-07-04","2025-09-01",
    "2025-11-27","2025-12-25","2026-01-01","2026-01-19","2026-02-16","2026-04-03","2026-05-25","2026-06-19","2026-07-03",
}

def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")

def load(asset: str):
    rows=[]
    for path in sorted(DATA.glob(f"us_spot_{asset}_etf_flows_daily_*.csv")):
        with path.open(newline="") as h:
            reader=csv.DictReader(h)
            expected_cols=["date",*EXPECTED[asset]["funds"],"Total","session_status"]
            if reader.fieldnames != expected_cols:
                fail(f"{path.name}: schema {reader.fieldnames} != {expected_cols}")
            for row in reader:
                if None in row or any(value is None or value == "" for value in row.values()):
                    fail(f"{path.name}: null/short cell at {row.get('date')}")
                rows.append(row)
    return sorted(rows,key=lambda r:r["date"])

def main() -> None:
    for asset, expected in EXPECTED.items():
        rows=load(asset)
        if len(rows)!=expected["rows"]: fail(f"{asset}: row count {len(rows)} != {expected['rows']}")
        dates=[r["date"] for r in rows]
        if min(dates)!=expected["start"] or max(dates)!=expected["end"]: fail(f"{asset}: coverage mismatch")
        if len(dates)!=len(set(dates)): fail(f"{asset}: duplicate date")
        non_sessions=0
        for row in rows:
            expected_status="NYSE_FULL_CLOSURE" if row["date"] in NYSE_FULL_CLOSURES else "TRADING_SESSION"
            if row["session_status"] != expected_status:
                fail(f"{asset} {row['date']}: session status {row['session_status']} != {expected_status}")
            non_sessions += row["session_status"] == "NYSE_FULL_CLOSURE"
            vals=[float(row[c]) for c in expected["funds"]]
            total=float(row["Total"])
            if abs(round(sum(vals),1)-round(total,1))>0.05:
                fail(f"{asset} {row['date']}: Total reconciliation failure")
        if non_sessions != expected["non_sessions"]:
            fail(f"{asset}: non-session count {non_sessions} != {expected['non_sessions']}")
    print("PASS: ETF flow history v1.1 is structurally valid and session-labelled.")

if __name__ == "__main__":
    main()
