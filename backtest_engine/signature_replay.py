from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import canonical_rows_hash, read_csv_path
from .w30_replay import (
    build_daily_utc,
    build_drawdown,
    build_etf_divergence,
    build_etf_trailing,
    build_ethbtc_derived,
    build_hourly_volatility,
)

SIGNATURES: dict[str, dict[str, Any]] = {
    "W30_BTC_VOLATILITY": {"rows": 166, "sha256": "69aa61eb9c04dccc40a618984e36cd07bd8509d9dfb67f1d9c1cfc2566748094"},
    "W30_ETH_VOLATILITY": {"rows": 166, "sha256": "3b1a4d521e943c3d5f0517914fdac7260b02de1b0c9c95b112878cb6bac9b077"},
    "W30_BTC_DRAWDOWN": {"rows": 166, "sha256": "8eee6da65ba585b463fdbd1f16a60e481d2c77a3c71fdc36ae64a37261e112f4"},
    "W30_ETH_DRAWDOWN": {"rows": 166, "sha256": "5922dc9a80dd1479dd6e9b7ee206e224ce52ce8f2ca9dd3e81a0dfcf1deb30c5"},
    "W30_BTC_DAILY_UTC": {"rows": 8, "sha256": "ddfd0f04b7de11690229d7d4ea60b7cfcdf8095043dc6ab256543d2d74a20139"},
    "W30_ETH_DAILY_UTC": {"rows": 8, "sha256": "5ab9d7aa7c680b3ffbfe2837b3a85a95bce6b43f4e8ee573ec77f94f6a80b4ad"},
    "W30_ETHBTC_DERIVED": {"rows": 166, "sha256": "532dbd2931ded3115f1331c288ba8420bcec7e7bb4463db373b4f67ad9d36531"},
    "W30_BTC_ETF_TRAILING": {"rows": 5, "sha256": "75a65fd20a5fe7d270df44b312f99ea5f4b99d91c302c0a03f26c80b70f8e89b"},
    "W30_ETH_ETF_TRAILING": {"rows": 5, "sha256": "7880aea01ca84222c90f3cb1325f4f3dd35883212c6cc5dd3f9e3ef3eea079c9"},
    "W30_ETF_DIVERGENCE": {"rows": 5, "sha256": "667dae32dacf31c7a5874bd340ca7354e99224b6d6cf8054d64cfaff958aa0e0"},
}

COLUMNS = {
    "W30_BTC_VOLATILITY": ["asset", "timestamp_utc", "close", "log_return_1h", "realized_vol_24h_annualized", "realized_vol_72h_annualized", "running_high_close", "drawdown_from_running_high", "settled", "method_id"],
    "W30_ETH_VOLATILITY": ["asset", "timestamp_utc", "close", "log_return_1h", "realized_vol_24h_annualized", "realized_vol_72h_annualized", "running_high_close", "drawdown_from_running_high", "settled", "method_id"],
    "W30_BTC_DRAWDOWN": ["asset", "timestamp_utc", "close", "running_high_close", "drawdown_from_running_high", "method_id"],
    "W30_ETH_DRAWDOWN": ["asset", "timestamp_utc", "close", "running_high_close", "drawdown_from_running_high", "method_id"],
    "W30_BTC_DAILY_UTC": ["instrument", "venue", "interval", "date_utc", "open", "high", "low", "close", "volume_contracts", "volume_asset", "quote_volume_usd", "settled_hour_count", "day_complete_24h", "source", "method_id"],
    "W30_ETH_DAILY_UTC": ["instrument", "venue", "interval", "date_utc", "open", "high", "low", "close", "volume_contracts", "volume_asset", "quote_volume_usd", "settled_hour_count", "day_complete_24h", "source", "method_id"],
    "W30_ETHBTC_DERIVED": ["instrument", "venue", "interval", "open_time_utc", "close_time_utc", "timezone", "open", "high_proxy", "low_proxy", "close", "volume", "quote_volume", "settled", "source_timestamp", "retrieval_timestamp", "method_id", "derivation_status", "high_low_semantics"],
    "W30_BTC_ETF_TRAILING": ["asset", "date", "total_usd_millions", "not_before_session_close_utc", "publication_timestamp_verified", "rolling_net_flow_1s_usd_millions", "rolling_net_flow_3s_usd_millions", "rolling_net_flow_5s_usd_millions", "rolling_net_flow_10s_usd_millions", "rolling_net_flow_20s_usd_millions", "rolling_1s_complete", "rolling_3s_complete", "rolling_5s_complete", "rolling_10s_complete", "rolling_20s_complete", "signed_flow_streak_sessions", "flow_acceleration_1s_usd_millions", "flow_acceleration_3s_usd_millions", "reversal_flag", "issuer_concentration_abs_share", "feature_knowledge_available_at_utc", "feature_method_id"],
    "W30_ETH_ETF_TRAILING": ["asset", "date", "total_usd_millions", "not_before_session_close_utc", "publication_timestamp_verified", "rolling_net_flow_1s_usd_millions", "rolling_net_flow_3s_usd_millions", "rolling_net_flow_5s_usd_millions", "rolling_net_flow_10s_usd_millions", "rolling_net_flow_20s_usd_millions", "rolling_1s_complete", "rolling_3s_complete", "rolling_5s_complete", "rolling_10s_complete", "rolling_20s_complete", "signed_flow_streak_sessions", "flow_acceleration_1s_usd_millions", "flow_acceleration_3s_usd_millions", "reversal_flag", "issuer_concentration_abs_share", "feature_knowledge_available_at_utc", "feature_method_id"],
    "W30_ETF_DIVERGENCE": ["date", "total_usd_millions_btc", "total_usd_millions_eth", "btc_minus_eth_flow_usd_millions", "opposite_sign_divergence", "method_id"],
}


def replay_w30_signatures(root: Path) -> dict[str, Any]:
    inputs = root / "inputs"
    btc_hourly = read_csv_path(inputs / "btc_okx_swap_1h_2026_w30.csv")
    eth_hourly = read_csv_path(inputs / "eth_okx_swap_1h_2026_w30.csv")
    btc_etf = read_csv_path(inputs / "btc_etf_fund_flows_2026_w30.csv")
    eth_etf = read_csv_path(inputs / "eth_etf_fund_flows_2026_w30.csv")
    btc_vol = build_hourly_volatility(btc_hourly, "BTC")
    eth_vol = build_hourly_volatility(eth_hourly, "ETH")
    generated = {
        "W30_BTC_VOLATILITY": btc_vol,
        "W30_ETH_VOLATILITY": eth_vol,
        "W30_BTC_DRAWDOWN": build_drawdown(btc_vol),
        "W30_ETH_DRAWDOWN": build_drawdown(eth_vol),
        "W30_BTC_DAILY_UTC": build_daily_utc(btc_hourly, "BTC"),
        "W30_ETH_DAILY_UTC": build_daily_utc(eth_hourly, "ETH"),
        "W30_ETHBTC_DERIVED": build_ethbtc_derived(btc_hourly, eth_hourly),
        "W30_BTC_ETF_TRAILING": build_etf_trailing(btc_etf, "BTC"),
        "W30_ETH_ETF_TRAILING": build_etf_trailing(eth_etf, "ETH"),
        "W30_ETF_DIVERGENCE": build_etf_divergence(btc_etf, eth_etf),
    }
    checks = []
    for check_id, rows in generated.items():
        actual_hash = canonical_rows_hash(rows, COLUMNS[check_id])
        expected = SIGNATURES[check_id]
        status = "PASS" if len(rows) == expected["rows"] and actual_hash == expected["sha256"] else "FAIL"
        checks.append({
            "check_id": check_id,
            "status": status,
            "rows": len(rows),
            "expected_rows": expected["rows"],
            "sha256": actual_hash,
            "expected_sha256": expected["sha256"],
        })
    return {
        "fixture": "W30_GOLDEN_FIXTURE_COMPACT_SIGNATURES",
        "status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "checks": checks,
        "economic_backtest_executed": False,
    }
