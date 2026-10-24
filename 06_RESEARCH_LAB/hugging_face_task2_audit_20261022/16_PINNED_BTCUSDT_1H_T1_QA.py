"""Pinned research-only QA of one public Binance BTCUSDT 1h Parquet file.

Requires duckdb. No network request, inference, PIT admission, or raw row export.
"""
import argparse
import hashlib
import json
from pathlib import Path

import duckdb


EXPECTED_SHA256 = "712fedb852b6eb26a2864959cf3c6c7cc1ee0ca80565ad12a264b84c0eb12772"


def quality(con, relation):
    query = f"""
    WITH typed AS (
      SELECT open_time, close_time, TRY_CAST(open AS DOUBLE) o,
        TRY_CAST(high AS DOUBLE) h, TRY_CAST(low AS DOUBLE) l,
        TRY_CAST(close AS DOUBLE) c, TRY_CAST(volume AS DOUBLE) v,
        TRY_CAST(quote_volume AS DOUBLE) q, TRY_CAST(taker_buy_volume AS DOUBLE) tb,
        TRY_CAST(taker_buy_quote_volume AS DOUBLE) tq, TRY_CAST(count AS DOUBLE) n
      FROM {relation}
    ), sequenced AS (
      SELECT *, LAG(open_time) OVER (ORDER BY open_time) prev,
        LEAD(open_time) OVER (ORDER BY open_time) nxt FROM typed
    )
    SELECT COUNT(*) total, COUNT(DISTINCT open_time) unique_open,
      COUNT(*) FILTER (WHERE open_time IS NULL OR close_time IS NULL) null_clocks,
      COUNT(*) FILTER (WHERE o IS NULL OR h IS NULL OR l IS NULL OR c IS NULL
        OR v IS NULL OR q IS NULL OR tb IS NULL OR tq IS NULL OR n IS NULL
        OR NOT COALESCE(ISFINITE(o) AND ISFINITE(h) AND ISFINITE(l) AND ISFINITE(c)
          AND ISFINITE(v) AND ISFINITE(q) AND ISFINITE(tb) AND ISFINITE(tq)
          AND ISFINITE(n), FALSE)) bad_numeric,
      COUNT(*) FILTER (WHERE h < GREATEST(o,c,l) OR l > LEAST(o,c,h)
        OR l > h OR LEAST(o,h,l,c) <= 0) invalid_ohlc,
      COUNT(*) FILTER (WHERE v < 0 OR q < 0 OR tb < 0 OR tq < 0 OR tb > v + 0.000001
        OR tq > q + 0.000001 OR n < 0 OR n != FLOOR(n)) invalid_volume,
      COUNT(*) FILTER (WHERE close_time != open_time + INTERVAL '1 hour' - INTERVAL '1 millisecond') partial_or_wrong_close,
      COUNT(*) FILTER (WHERE open_time != DATE_TRUNC('hour',open_time)) unaligned_open,
      COUNT(*) FILTER (WHERE prev IS NOT NULL AND open_time - prev > INTERVAL '1 hour') gap_boundaries,
      SUM(CASE WHEN prev IS NOT NULL AND open_time-prev > INTERVAL '1 hour'
        THEN DATE_DIFF('hour',prev,open_time)-1 ELSE 0 END) missing_hours,
      COUNT(*) FILTER (WHERE close_time != open_time + INTERVAL '1 hour' - INTERVAL '1 millisecond'
        AND nxt-open_time > INTERVAL '1 hour') partial_before_gap,
      MIN(open_time) first_open, MAX(open_time) last_open
    FROM sequenced
    """
    cur = con.execute(query)
    row = cur.fetchone()
    return dict(zip([x[0] for x in cur.description], row))


def hostile_fixtures():
    con = duckdb.connect()
    con.execute("""CREATE TEMP TABLE base (open_time TIMESTAMP, close_time TIMESTAMP,
      open VARCHAR, high VARCHAR, low VARCHAR, close VARCHAR, volume VARCHAR,
      quote_volume VARCHAR, taker_buy_volume VARCHAR, taker_buy_quote_volume VARCHAR,
      count DOUBLE)""")
    base = ("2026-10-12 22:00:00", "2026-10-12 22:59:59.999", "100", "110", "90", "105", "10", "1000", "5", "500", 10.)
    valid_next = ("2026-10-12 23:00:00", "2026-10-12 23:59:59.999", "105", "110", "100", "106", "10", "1000", "5", "500", 10.)
    cases = [
      ("duplicate_open", [base, base], lambda x: x["total"] != x["unique_open"]),
      ("missing_hour", [base, ("2026-10-13 00:00:00", "2026-10-13 00:59:59.999", *valid_next[2:])], lambda x: x["missing_hours"] == 1),
      ("partial_candle", [(base[0], base[0], *base[2:])], lambda x: x["partial_or_wrong_close"] == 1),
      ("impossible_ohlc", [(base[0], base[1], "100", "99", "90", "105", *base[6:])], lambda x: x["invalid_ohlc"] == 1),
      ("negative_volume", [(*base[:6], "-1", *base[7:])], lambda x: x["invalid_volume"] == 1),
      ("nan_price", [(base[0], base[1], "NaN", *base[3:])], lambda x: x["bad_numeric"] == 1),
    ]
    for name, rows, detects in cases:
        con.execute("DELETE FROM base")
        con.executemany("INSERT INTO base VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
        if not detects(quality(con, "base")):
            raise AssertionError(f"hostile fixture escaped: {name}")
    return [name for name, _, _ in cases]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    digest = hashlib.sha256(args.file.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("PINNED_FILE_SHA256_MISMATCH")
    con = duckdb.connect()
    path = str(args.file).replace("'", "''")
    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()
    names = {row[0] for row in schema}
    required = {"open_time", "close_time", "open", "high", "low", "close", "volume",
                "quote_volume", "taker_buy_volume", "taker_buy_quote_volume", "count"}
    if not required <= names:
        raise SystemExit("REQUIRED_PARQUET_SCHEMA_MISSING")
    result = quality(con, f"read_parquet('{path}')")
    result["extra_columns"] = sorted(names - required)
    result["price_and_volume_storage_types"] = {
        row[0]: row[1] for row in schema if row[0] in required - {"open_time", "close_time", "count"}
    }
    result["file_sha256"] = digest
    result["file_bytes"] = args.file.stat().st_size
    result["hostile_fixtures_passed"] = hostile_fixtures()
    print(json.dumps(result, default=str, sort_keys=True))


if __name__ == "__main__":
    main()
