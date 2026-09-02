from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / "scripts" / "learning" / "forecast_settlement_price_owner.py"
SPEC = importlib.util.spec_from_file_location("forecast_settlement_price_owner", OWNER)
owner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(owner)


class SettlementOwnerTests(unittest.TestCase):
    def test_last_closed_minute_never_uses_in_progress_bar(self):
        target = datetime.fromisoformat("2026-08-15T14:01:34+00:00")
        self.assertEqual(owner.iso(owner.last_closed_minute_open(target)), "2026-08-15T14:00:00Z")
        exact = datetime.fromisoformat("2026-08-15T14:01:00+00:00")
        self.assertEqual(owner.iso(owner.last_closed_minute_open(exact)), "2026-08-15T14:00:00Z")

    def test_binance_requires_exact_expected_completed_bar(self):
        target = owner.parse_dt("2026-08-15T14:01:34Z")
        open_dt = owner.last_closed_minute_open(target)
        ot = owner.unix_ms(open_dt)
        ct = ot + 59_999
        payload = json.dumps([[ot, "100", "103", "99", "102", "1", ct, "0", 1, "0", "0", "0"]]).encode()
        row = owner.parse_binance(payload, "BTCUSDT", target, open_dt)
        self.assertEqual(row["close"], 102.0)
        self.assertTrue(row["confirmed"])
        bad = json.dumps([[ot + 60_000, "100", "103", "99", "102", "1", ct + 60_000, "0", 1, "0", "0", "0"]]).encode()
        with self.assertRaises(owner.SettlementSourceError):
            owner.parse_binance(bad, "BTCUSDT", target, open_dt)

    def test_okx_requires_confirmed_exact_expected_bar(self):
        target = owner.parse_dt("2026-08-17T09:01:38Z")
        open_dt = owner.last_closed_minute_open(target)
        ts = owner.unix_ms(open_dt)
        payload = json.dumps({"code": "0", "msg": "", "data": [[str(ts), "1870", "1885", "1860", "1880.2", "1"]]}).encode()
        row = owner.parse_okx(payload, "ETH-USDT-SWAP", target, open_dt)
        self.assertEqual(row["close"], 1880.2)
        self.assertEqual(row["candle_close_utc"], "2026-08-17T09:01:00Z")
        unconfirmed = json.dumps({"code": "0", "data": [[str(ts), "1", "2", "1", "1.5", "0"]]}).encode()
        with self.assertRaises(owner.SettlementSourceError):
            owner.parse_okx(unconfirmed, "ETH-USDT-SWAP", target, open_dt)

    def test_evidence_binds_forecast_raw_and_source_clock(self):
        forecast = {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": "fc1",
            "settlement_contract_version": owner.SETTLEMENT_CONTRACT,
            "metric_path": "spot.BTCUSDT.close",
            "outcome_due_utc": "2026-08-15T14:01:34Z",
        }
        target = owner.parse_dt(forecast["outcome_due_utc"])
        raw = b"[]"
        raw_path = Path("raw/fc1/source.json")
        obs = {
            "source": "BINANCE_SPOT_MARKET_DATA_ONLY_KLINES",
            "instrument": "BTCUSDT",
            "candle_open_utc": "2026-08-15T14:00:00Z",
            "candle_close_utc": "2026-08-15T14:00:59.999000Z",
            "close": 102.0,
            "confirmed": True,
        }
        evidence = owner.build_evidence(
            forecast,
            "spot.BTCUSDT.close",
            owner.SUPPORTED["spot.BTCUSDT.close"],
            target,
            raw_path,
            raw,
            "fixture://BTCUSDT",
            obs,
            owner.parse_dt("2026-08-15T14:03:00Z"),
        )
        self.assertEqual(evidence["forecast_sha256"], owner.digest(forecast))
        self.assertEqual(evidence["source_raw_sha256"], owner.digest_bytes(raw))
        self.assertEqual(evidence["source_candle_offset_seconds"], -34.001)
        self.assertEqual(evidence["captured_at_semantics"], "ADJUDICATION_TARGET_TIME_NOT_SOURCE_OBSERVATION")
        self.assertEqual(evidence["market_metrics"]["spot"]["BTCUSDT"]["close"], 102.0)
        self.assertFalse(evidence["authority"]["scientific_skill_authority"])

    def test_batch_fixture_is_idempotent_and_future_safe(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            froot, out, raw, fixtures = root / "f", root / "out", root / "raw", root / "fixtures"
            froot.mkdir()
            fixtures.mkdir()
            due = "2026-08-15T14:01:34Z"
            forecast = {
                "contract": "FROZEN_FORECAST_v1",
                "forecast_id": "fc1",
                "settlement_contract_version": owner.SETTLEMENT_CONTRACT,
                "metric_path": "spot.BTCUSDT.close",
                "outcome_due_utc": due,
            }
            (froot / "fc1.json").write_text(json.dumps(forecast))
            target = owner.parse_dt(due)
            ot = owner.unix_ms(owner.last_closed_minute_open(target))
            ct = ot + 59_999
            (fixtures / "BINANCE_SPOT_1M__BTCUSDT.json").write_text(
                json.dumps([[ot, "100", "103", "99", "102", "1", ct, "0", 1, "0", "0", "0"]])
            )
            status = owner.run_one(froot / "fc1.json", out, raw, owner.parse_dt("2026-08-15T14:03:00Z"), fixtures)
            self.assertEqual(status, "CREATED")
            self.assertEqual(
                owner.run_one(froot / "fc1.json", out, raw, owner.parse_dt("2026-08-15T14:04:00Z"), fixtures),
                "DUPLICATE_NOOP",
            )
            future = dict(forecast, forecast_id="fc2", outcome_due_utc="2026-08-16T14:01:34Z")
            (froot / "fc2.json").write_text(json.dumps(future))
            self.assertEqual(
                owner.run_one(froot / "fc2.json", out, raw, owner.parse_dt("2026-08-15T14:04:00Z"), fixtures),
                "PENDING_FUTURE_DUE",
            )

    def test_unsupported_metric_fails_closed(self):
        forecast = {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": "x",
            "settlement_contract_version": owner.SETTLEMENT_CONTRACT,
            "metric_path": "macro.VIXCLS.value",
            "outcome_due_utc": "2026-08-15T00:00:00Z",
        }
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_SETTLEMENT_METRIC"):
            owner.validate_forecast(forecast)


if __name__ == "__main__":
    unittest.main()
