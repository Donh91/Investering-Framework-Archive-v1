from __future__ import annotations

from datetime import datetime, timedelta, timezone

from scripts.intraday_execution.intraday_execution_research import asset_features


def test_asset_features_accepts_hourly_rows_as_timestamp_row_tuples():
    start = datetime(2026, 8, 24, 0, 0, tzinfo=timezone.utc)
    pairs = []
    for index in range(6):
        row = {
            "btc_close": str(100 + index),
            "btc_high": str(101 + index),
            "btc_low": str(99 + index),
            "btc_quote_volume": "200" if index == 5 else "100",
            "btc_volume": "1",
            "btc_return_1h_pct": "1.0",
            "btc_taker_buy_quote_share": "0.55",
            "btc_oi_change_1h_pct": "0.2",
            "btc_funding_event_rate": "0.0001",
        }
        pairs.append((start + timedelta(hours=index), row))

    features = asset_features("btc", pairs)

    assert features["close"] == 105.0
    assert features["rolling_relative_quote_volume"] == 2.0
    assert features["return_4h_pct"] == (105.0 / 101.0 - 1.0) * 100.0
