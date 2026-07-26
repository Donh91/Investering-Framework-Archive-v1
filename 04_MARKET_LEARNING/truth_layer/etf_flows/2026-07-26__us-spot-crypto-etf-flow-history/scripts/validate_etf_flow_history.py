#!/usr/bin/env python3
"""Fail-closed structural QA for yearly ETF flow partitions."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPECTED = {
    "btc": {"rows": 651, "start": "2024-01-11", "end": "2026-07-24"},
    "eth": {"rows": 513, "start": "2024-07-23", "end": "2026-07-24"},
}

def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")

def load(asset: str) -> pd.DataFrame:
    files = sorted(DATA.glob(f"us_spot_{asset}_etf_flows_daily_*.csv"))
    if not files:
        fail(f"{asset}: no partitions")
    return pd.concat([pd.read_csv(path) for path in files], ignore_index=True).sort_values("date")

def main() -> None:
    for asset, expected in EXPECTED.items():
        df = load(asset)
        if len(df) != expected["rows"]:
            fail(f"{asset}: row count {len(df)} != {expected['rows']}")
        if df["date"].min() != expected["start"] or df["date"].max() != expected["end"]:
            fail(f"{asset}: coverage mismatch")
        if df["date"].duplicated().any():
            fail(f"{asset}: duplicate date")
        if df.isna().any().any():
            fail(f"{asset}: null cell")
        funds = [c for c in df.columns if c not in {"date", "Total"}]
        diff = (df[funds].sum(axis=1).round(1) - df["Total"].round(1)).abs()
        if (diff > 0.05).any():
            fail(f"{asset}: daily Total reconciliation failure")
    print("PASS: ETF flow history partitions are structurally valid.")

if __name__ == "__main__":
    main()
