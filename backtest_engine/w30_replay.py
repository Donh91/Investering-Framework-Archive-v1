from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import stdev
from typing import Any

from .utils import canonical_rows_hash, read_csv_path
from .validation import validate_composite_key, validate_etf_sessions

FLOAT_TOLERANCE = 1e-12


@dataclass(frozen=True)
class ReplayCheck:
    check_id: str
    status: str
    rows: int
    max_abs_error: float
    generated_hash: str
    expected_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"true", "1", "yes"}


def _normalise_timestamp(value: str) -> str:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()


def _rolling_sample_std(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return stdev(values[-window:])


def build_hourly_volatility(rows: list[dict[str, str]], asset: str) -> list[dict[str, Any]]:
    closes: list[float] = []
    log_returns: list[float] = []
    output: list[dict[str, Any]] = []
    running_high = -math.inf
    annualization = math.sqrt(24 * 365)
    for row in rows:
        close = float(row["close"])
        previous = closes[-1] if closes else None
        log_return = math.log(close / previous) if previous is not None else None
        closes.append(close)
        if log_return is not None:
            log_returns.append(log_return)
        running_high = max(running_high, close)
        rv24 = _rolling_sample_std(log_returns, 24)
        rv72 = _rolling_sample_std(log_returns, 72)
        output.append({
            "asset": asset,
            "timestamp_utc": _normalise_timestamp(row["timestamp_utc"]),
            "close": close,
            "log_return_1h": log_return,
            "realized_vol_24h_annualized": rv24 * annualization if rv24 is not None else None,
            "realized_vol_72h_annualized": rv72 * annualization if rv72 is not None else None,
            "running_high_close": running_high,
            "drawdown_from_running_high": close / running_high - 1.0,
            "settled": _bool(row["settled"]),
            "method_id": "OKX_SWAP_HOURLY_RETURNS_RV_DRAWDOWN_v1",
        })
    return output


def build_drawdown(volatility_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "asset": row["asset"],
            "timestamp_utc": row["timestamp_utc"],
            "close": row["close"],
            "running_high_close": row["running_high_close"],
            "drawdown_from_running_high": row["drawdown_from_running_high"],
            "method_id": row["method_id"],
        }
        for row in volatility_rows
    ]


def build_daily_utc(rows: list[dict[str, str]], asset: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        if not _bool(row["settled"]):
            continue
        date_utc = datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00")).date().isoformat()
        groups.setdefault(date_utc, []).append(row)
    output: list[dict[str, Any]] = []
    for date_utc in sorted(groups):
        group = groups[date_utc]
        output.append({
            "instrument": f"{asset}-USDT-SWAP",
            "venue": "OKX",
            "interval": "1d_aggregated_from_1h",
            "date_utc": date_utc,
            "open": float(group[0]["open"]),
            "high": max(float(row["high"]) for row in group),
            "low": min(float(row["low"]) for row in group),
            "close": float(group[-1]["close"]),
            "volume_contracts": sum(float(row["volume_contracts"]) for row in group),
            "volume_asset": sum(float(row["volume_coin"]) for row in group),
            "quote_volume_usd": sum(float(row["volume_quote_usd"]) for row in group),
            "settled_hour_count": len(group),
            "day_complete_24h": len(group) == 24,
            "source": "OKX_SWAP_1H_ARCHIVED_AGGREGATION",
            "method_id": "OKX_SWAP_1H_TO_1D_v1",
        })
    return output


def build_ethbtc_derived(btc_rows: list[dict[str, str]], eth_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    btc_by_time = {row["timestamp_utc"]: row for row in btc_rows}
    eth_by_time = {row["timestamp_utc"]: row for row in eth_rows}
    output: list[dict[str, Any]] = []
    for timestamp in sorted(set(btc_by_time).intersection(eth_by_time)):
        btc = btc_by_time[timestamp]
        eth = eth_by_time[timestamp]
        open_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        close_dt = datetime.fromtimestamp(open_dt.timestamp() + 3600, tz=open_dt.tzinfo)
        output.append({
            "instrument": "ETH/BTC",
            "venue": "LOCAL_DERIVATION_FROM_OKX_SWAPS",
            "interval": "1h",
            "open_time_utc": timestamp,
            "close_time_utc": close_dt.isoformat(sep=" "),
            "timezone": "UTC",
            "open": float(eth["open"]) / float(btc["open"]),
            "high_proxy": float(eth["high"]) / float(btc["low"]),
            "low_proxy": float(eth["low"]) / float(btc["high"]),
            "close": float(eth["close"]) / float(btc["close"]),
            "volume": None,
            "quote_volume": None,
            "settled": _bool(btc["settled"]) and _bool(eth["settled"]),
            "source_timestamp": timestamp,
            "retrieval_timestamp": "2026-07-26T19:41:38Z",
            "method_id": "DERIVED_ETHBTC_FROM_OKX_SWAP_1H_v1",
            "derivation_status": "DERIVED_NOT_DIRECT",
            "high_low_semantics": "CROSS_DIVIDED_RATIO_BOUNDS_NOT_TRADED_OHLC",
        })
    return output


def _sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def build_etf_trailing(rows: list[dict[str, str]], asset: str) -> list[dict[str, Any]]:
    validate_etf_sessions(rows)
    flows: list[float] = []
    streak = 0
    output: list[dict[str, Any]] = []
    metadata_fields = {
        "date", "total_usd_millions", "not_before_session_close_utc",
        "publication_timestamp_verified", "asset", "source", "method_id",
    }
    fund_columns = [column for column in rows[0] if column not in metadata_fields]
    for index, row in enumerate(rows):
        flow = float(row["total_usd_millions"])
        flows.append(flow)
        sign = _sign(flow)
        if sign == 0:
            streak = 0
        elif index == 0 or _sign(flows[index - 1]) != sign:
            streak = sign
        else:
            streak += sign
        rolling = {window: sum(flows[-window:]) if len(flows) >= window else None for window in (1, 3, 5, 10, 20)}
        previous_3 = sum(flows[-4:-1]) if len(flows) >= 4 else None
        acceleration_3 = rolling[3] - previous_3 if rolling[3] is not None and previous_3 is not None else None
        acceleration_1 = flow - flows[-2] if len(flows) >= 2 else None
        previous_sign = _sign(flows[-2]) if len(flows) >= 2 else 0
        fund_abs = [abs(float(row[column])) for column in fund_columns if row[column] not in (None, "")]
        concentration = max(fund_abs) / sum(fund_abs) if fund_abs and sum(fund_abs) else None
        output.append({
            "asset": asset,
            "date": row["date"],
            "total_usd_millions": flow,
            "not_before_session_close_utc": row["not_before_session_close_utc"],
            "publication_timestamp_verified": _bool(row["publication_timestamp_verified"]),
            "rolling_net_flow_1s_usd_millions": rolling[1],
            "rolling_net_flow_3s_usd_millions": rolling[3],
            "rolling_net_flow_5s_usd_millions": rolling[5],
            "rolling_net_flow_10s_usd_millions": rolling[10],
            "rolling_net_flow_20s_usd_millions": rolling[20],
            "rolling_1s_complete": rolling[1] is not None,
            "rolling_3s_complete": rolling[3] is not None,
            "rolling_5s_complete": rolling[5] is not None,
            "rolling_10s_complete": rolling[10] is not None,
            "rolling_20s_complete": rolling[20] is not None,
            "signed_flow_streak_sessions": streak,
            "flow_acceleration_1s_usd_millions": acceleration_1,
            "flow_acceleration_3s_usd_millions": acceleration_3,
            "reversal_flag": sign != 0 and previous_sign != 0 and sign != previous_sign,
            "issuer_concentration_abs_share": concentration,
            "feature_knowledge_available_at_utc": row["not_before_session_close_utc"],
            "feature_method_id": "ETF_TRAILING_ONLY_FEATURES_v1",
        })
    return output


def build_etf_divergence(btc_rows: list[dict[str, str]], eth_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    btc = {row["date"]: float(row["total_usd_millions"]) for row in btc_rows}
    eth = {row["date"]: float(row["total_usd_millions"]) for row in eth_rows}
    output: list[dict[str, Any]] = []
    for date in sorted(set(btc).intersection(eth)):
        btc_flow = btc[date]
        eth_flow = eth[date]
        output.append({
            "date": date,
            "total_usd_millions_btc": btc_flow,
            "total_usd_millions_eth": eth_flow,
            "btc_minus_eth_flow_usd_millions": btc_flow - eth_flow,
            "opposite_sign_divergence": _sign(btc_flow) * _sign(eth_flow) == -1,
            "method_id": "BTC_ETH_ETF_FLOW_DIVERGENCE_TRAILING_v1",
        })
    return output


def _expected_value(value: str) -> Any:
    if value == "":
        return None
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return float(value)
    except ValueError:
        if "T" in value or "+00:00" in value:
            try:
                return _normalise_timestamp(value)
            except ValueError:
                pass
        return value


def compare_rows(check_id: str, generated: list[dict[str, Any]], expected_path: Path) -> ReplayCheck:
    expected_raw = read_csv_path(expected_path)
    if len(generated) != len(expected_raw):
        return ReplayCheck(check_id, "FAIL_ROW_COUNT", len(generated), math.inf, "", "")
    columns = list(expected_raw[0]) if expected_raw else []
    max_error = 0.0
    for row_index, (actual, expected_row) in enumerate(zip(generated, expected_raw), start=1):
        for column in columns:
            expected = _expected_value(expected_row[column])
            actual_value = actual.get(column)
            if isinstance(expected, float):
                if actual_value is None or not math.isclose(float(actual_value), expected, rel_tol=1e-11, abs_tol=FLOAT_TOLERANCE):
                    raise AssertionError(f"{check_id} row {row_index} column {column}: actual={actual_value!r}, expected={expected!r}")
                max_error = max(max_error, abs(float(actual_value) - expected))
            elif expected is None:
                if actual_value not in (None, ""):
                    raise AssertionError(f"{check_id} row {row_index} column {column}: expected null")
            else:
                if isinstance(expected, str) and ("T" in expected or "+00:00" in expected):
                    try:
                        actual_value = _normalise_timestamp(str(actual_value))
                    except ValueError:
                        pass
                if actual_value != expected:
                    raise AssertionError(f"{check_id} row {row_index} column {column}: actual={actual_value!r}, expected={expected!r}")
    expected_rows = [{column: _expected_value(row[column]) for column in columns} for row in expected_raw]
    return ReplayCheck(
        check_id, "PASS", len(generated), max_error,
        canonical_rows_hash(generated, columns), canonical_rows_hash(expected_rows, columns),
    )


def replay_w30(root: Path) -> dict[str, Any]:
    inputs = root / "inputs"
    expected = root / "expected"
    btc_hourly = read_csv_path(inputs / "btc_okx_swap_1h_2026_w30.csv")
    eth_hourly = read_csv_path(inputs / "eth_okx_swap_1h_2026_w30.csv")
    btc_etf = read_csv_path(inputs / "btc_etf_fund_flows_2026_w30.csv")
    eth_etf = read_csv_path(inputs / "eth_etf_fund_flows_2026_w30.csv")
    validate_composite_key(btc_hourly, ["asset", "timestamp_ms"])
    validate_composite_key(eth_hourly, ["asset", "timestamp_ms"])
    validate_composite_key(btc_etf, ["asset", "date"])
    validate_composite_key(eth_etf, ["asset", "date"])
    btc_vol = build_hourly_volatility(btc_hourly, "BTC")
    eth_vol = build_hourly_volatility(eth_hourly, "ETH")
    checks = [
        compare_rows("W30_BTC_VOLATILITY", btc_vol, expected / "btc_okx_hourly_volatility_2026_w30.csv"),
        compare_rows("W30_ETH_VOLATILITY", eth_vol, expected / "eth_okx_hourly_volatility_2026_w30.csv"),
        compare_rows("W30_BTC_DRAWDOWN", build_drawdown(btc_vol), expected / "btc_okx_hourly_drawdown_2026_w30.csv"),
        compare_rows("W30_ETH_DRAWDOWN", build_drawdown(eth_vol), expected / "eth_okx_hourly_drawdown_2026_w30.csv"),
        compare_rows("W30_BTC_DAILY_UTC", build_daily_utc(btc_hourly, "BTC"), expected / "btc_okx_swap_1d_aggregated_2026_w30.csv"),
        compare_rows("W30_ETH_DAILY_UTC", build_daily_utc(eth_hourly, "ETH"), expected / "eth_okx_swap_1d_aggregated_2026_w30.csv"),
        compare_rows("W30_ETHBTC_DERIVED", build_ethbtc_derived(btc_hourly, eth_hourly), expected / "ethbtc_derived_okx_swap_1h_2026_w30.csv"),
        compare_rows("W30_BTC_ETF_TRAILING", build_etf_trailing(btc_etf, "BTC"), expected / "btc_etf_trailing_features_2026_w30.csv"),
        compare_rows("W30_ETH_ETF_TRAILING", build_etf_trailing(eth_etf, "ETH"), expected / "eth_etf_trailing_features_2026_w30.csv"),
        compare_rows("W30_ETF_DIVERGENCE", build_etf_divergence(btc_etf, eth_etf), expected / "btc_eth_etf_flow_divergence_2026_w30.csv"),
    ]
    return {
        "fixture": "W30_GOLDEN_FIXTURE",
        "status": "PASS" if all(check.status == "PASS" for check in checks) else "FAIL",
        "checks": [check.to_dict() for check in checks],
        "economic_backtest_executed": False,
    }
