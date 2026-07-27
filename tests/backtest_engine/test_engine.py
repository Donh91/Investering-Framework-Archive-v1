from __future__ import annotations

import hashlib
import json
import math
import tempfile
import unittest
import zipfile
from pathlib import Path

from backtest_engine.models import Authority, DatasetIdentity, MarketType, TemporalPoint
from backtest_engine.package_audit import audit_zip
from backtest_engine.validation import (
    ContinuationPage,
    ContractViolation,
    duplicate_keys,
    validate_backward_continuation,
    validate_composite_key,
    validate_direct_gate_source,
    validate_etf_sessions,
    validate_no_silent_substitution,
    validate_temporal,
)
from backtest_engine.w30_replay import (
    build_daily_utc,
    build_etf_divergence,
    build_etf_trailing,
    build_ethbtc_derived,
    build_hourly_volatility,
)


def make_package(root: Path, *, manifest_defect: bool = False) -> Path:
    package = root / "fixture.zip"
    prefix = "FIXTURE/"
    payloads = {
        prefix + "data.csv": b"asset,timestamp,value\nBTC,1,10\nETH,1,20\n",
        prefix + "README.md": b"fixture\n",
    }
    checksum_lines = [f"{hashlib.sha256(data).hexdigest()}  {name[len(prefix):]}" for name, data in payloads.items()]
    manifest = {
        "file_count": 4,
        "files": [{"path": "manifest.json", "bytes": 1 if manifest_defect else 0, "sha256": "0" * 64 if manifest_defect else None}],
    }
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in payloads.items():
            archive.writestr(name, data)
        archive.writestr(prefix + "CHECKSUMS.sha256", "\n".join(checksum_lines) + "\n")
        archive.writestr(prefix + "manifest.json", json.dumps(manifest))
    return package


def hourly_row(asset: str, hour: int, close: float, *, settled: bool = True) -> dict[str, str]:
    open_value = close - 1.0
    return {
        "asset": asset,
        "timestamp_ms": str(hour * 3_600_000),
        "timestamp_utc": f"2026-07-{20 + hour // 24:02d}T{hour % 24:02d}:00:00Z",
        "open": str(open_value),
        "high": str(close + 2.0),
        "low": str(close - 2.0),
        "close": str(close),
        "volume_contracts": "100",
        "volume_coin": "1",
        "volume_quote_usd": str(close),
        "settled": str(settled),
    }


class PackageAuditTests(unittest.TestCase):
    def test_crc_and_checksums_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            audit = audit_zip(make_package(Path(temp)))
        self.assertEqual(audit.zip_crc_status, "PASS")
        self.assertEqual(audit.checksum_entries, 2)
        self.assertEqual(audit.checksum_mismatches, 0)
        self.assertEqual(audit.missing_checksum_targets, 0)

    def test_manifest_self_reference_defect_is_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            audit = audit_zip(make_package(Path(temp), manifest_defect=True))
        self.assertEqual(audit.status, "PASS_WITH_MANIFEST_SELF_REFERENCE_DEFECT")
        self.assertEqual(audit.checksum_mismatches, 0)


class TemporalTests(unittest.TestCase):
    def test_valid_temporal_order(self) -> None:
        validate_temporal(TemporalPoint(
            knowledge_at_utc="2026-07-27T20:00:00Z",
            decision_at_utc="2026-07-27T20:01:00Z",
            execution_at_utc="2026-07-27T20:05:00Z",
            label_end_utc="2026-08-03T20:00:00Z",
        ))

    def test_lookahead_is_rejected(self) -> None:
        with self.assertRaises(ContractViolation):
            validate_temporal(TemporalPoint(
                knowledge_at_utc="2026-07-27T21:00:00Z",
                decision_at_utc="2026-07-27T20:01:00Z",
                execution_at_utc="2026-07-27T20:05:00Z",
                label_end_utc="2026-08-03T20:00:00Z",
            ))


class AuthorityTests(unittest.TestCase):
    def test_direct_spot_passes(self) -> None:
        validate_direct_gate_source(DatasetIdentity(
            "ETHBTC_DIRECT", "BINANCE", MarketType.SPOT, Authority.DIRECT, "CEST"
        ), "BT04")

    def test_derived_source_is_rejected(self) -> None:
        with self.assertRaises(ContractViolation):
            validate_direct_gate_source(DatasetIdentity(
                "ETHBTC_DERIVED", "OKX", MarketType.PERPETUAL_SWAP, Authority.DERIVED_SAME_VENUE, "UTC"
            ), "BT04")

    def test_silent_market_type_substitution_is_rejected(self) -> None:
        owner = DatasetIdentity("BTC_SPOT", "BINANCE", MarketType.SPOT, Authority.DIRECT, "CEST")
        candidate = DatasetIdentity("BTC_SWAP", "BINANCE", MarketType.PERPETUAL_SWAP, Authority.DIRECT, "CEST")
        with self.assertRaises(ContractViolation):
            validate_no_silent_substitution(owner, candidate)


class CompositeKeyTests(unittest.TestCase):
    def test_timestamp_only_false_positive_is_avoided(self) -> None:
        rows = [
            {"timestamp": "2026-07-27T00:00:00Z", "asset": "BTC", "venue": "OKX"},
            {"timestamp": "2026-07-27T00:00:00Z", "asset": "ETH", "venue": "OKX"},
        ]
        self.assertEqual(duplicate_keys(rows, ["timestamp"]), [("2026-07-27T00:00:00Z",)])
        validate_composite_key(rows, ["timestamp", "asset", "venue"])

    def test_real_composite_duplicate_is_rejected(self) -> None:
        rows = [
            {"timestamp": "2026-07-27T00:00:00Z", "asset": "BTC", "venue": "OKX"},
            {"timestamp": "2026-07-27T00:00:00Z", "asset": "BTC", "venue": "OKX"},
        ]
        with self.assertRaises(ContractViolation):
            validate_composite_key(rows, ["timestamp", "asset", "venue"])


class ETFSessionTests(unittest.TestCase):
    def test_weekday_session_passes(self) -> None:
        validate_etf_sessions([{"date": "2026-07-24", "not_before_session_close_utc": "2026-07-24T20:00:00Z"}])

    def test_weekend_zero_is_rejected(self) -> None:
        with self.assertRaises(ContractViolation):
            validate_etf_sessions([{
                "date": "2026-07-25",
                "not_before_session_close_utc": "2026-07-25T20:00:00Z",
                "synthetic_zero": True,
            }])


class ContinuationTests(unittest.TestCase):
    def test_valid_backward_page(self) -> None:
        validate_backward_continuation(ContinuationPage((500, 400, 300), 300), ContinuationPage((200, 100), 100))

    def test_overlap_is_rejected(self) -> None:
        with self.assertRaises(ContractViolation):
            validate_backward_continuation(ContinuationPage((500, 400, 300), 300), ContinuationPage((300, 200), 200))

    def test_cursor_mismatch_is_rejected(self) -> None:
        with self.assertRaises(ContractViolation):
            validate_backward_continuation(ContinuationPage((500, 400, 300), 400), ContinuationPage((200, 100), 100))


class FeatureBuilderTests(unittest.TestCase):
    def test_hourly_volatility_uses_sample_std_and_settled_flag(self) -> None:
        rows = [hourly_row("BTC", hour, 100.0 + hour) for hour in range(25)]
        result = build_hourly_volatility(rows, "BTC")
        expected_returns = [math.log((101.0 + hour) / (100.0 + hour)) for hour in range(24)]
        expected_mean = sum(expected_returns) / len(expected_returns)
        expected_var = sum((value - expected_mean) ** 2 for value in expected_returns) / (len(expected_returns) - 1)
        expected = math.sqrt(expected_var) * math.sqrt(24 * 365)
        self.assertAlmostEqual(result[-1]["realized_vol_24h_annualized"], expected, places=14)

    def test_daily_aggregation_excludes_unsettled_tail(self) -> None:
        rows = [hourly_row("BTC", hour, 100.0 + hour) for hour in range(24)]
        rows.append(hourly_row("BTC", 24, 999.0, settled=False))
        result = build_daily_utc(rows, "BTC")
        self.assertEqual(result[0]["settled_hour_count"], 24)
        self.assertEqual(result[0]["close"], 123.0)
        self.assertTrue(result[0]["day_complete_24h"])

    def test_derived_ethbtc_bounds_are_cross_divided_and_not_direct(self) -> None:
        btc = [hourly_row("BTC", 0, 100.0)]
        eth = [hourly_row("ETH", 0, 10.0)]
        result = build_ethbtc_derived(btc, eth)[0]
        self.assertEqual(result["derivation_status"], "DERIVED_NOT_DIRECT")
        self.assertEqual(result["high_low_semantics"], "CROSS_DIVIDED_RATIO_BOUNDS_NOT_TRADED_OHLC")
        self.assertAlmostEqual(result["close"], 0.1)

    def test_etf_trailing_features_and_reversal(self) -> None:
        rows = []
        for index, flow in enumerate((10.0, 20.0, 30.0, -5.0, -10.0), start=20):
            rows.append({
                "date": f"2026-07-{index}", "FUND_A": str(flow), "FUND_B": "0",
                "total_usd_millions": str(flow),
                "not_before_session_close_utc": f"2026-07-{index}T20:00:00Z",
                "publication_timestamp_verified": "False", "asset": "BTC",
                "source": "fixture", "method_id": "fixture",
            })
        result = build_etf_trailing(rows, "BTC")
        self.assertEqual(result[2]["rolling_net_flow_3s_usd_millions"], 60.0)
        self.assertTrue(result[3]["reversal_flag"])
        self.assertEqual(result[4]["signed_flow_streak_sessions"], -2)

    def test_etf_divergence_detects_opposite_sign(self) -> None:
        btc = [{"date": "2026-07-24", "total_usd_millions": "10"}]
        eth = [{"date": "2026-07-24", "total_usd_millions": "-5"}]
        result = build_etf_divergence(btc, eth)[0]
        self.assertEqual(result["btc_minus_eth_flow_usd_millions"], 15.0)
        self.assertTrue(result["opposite_sign_divergence"])


if __name__ == "__main__":
    unittest.main()
