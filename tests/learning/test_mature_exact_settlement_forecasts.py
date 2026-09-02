from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "scripts" / "learning" / "mature_exact_settlement_forecasts.py"


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def forecast():
    return {
        "contract": "FROZEN_FORECAST_v1",
        "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
        "forecast_id": "EXP-FC-exact-settlement-test",
        "source_candidate_id": "EC-test",
        "frozen_at_utc": "2026-08-14T14:01:34Z",
        "outcome_due_utc": "2026-08-15T14:01:34Z",
        "metric_path": "spot.BTCUSDT.close",
        "direction": "UP",
        "threshold_pct": 1.0,
        "start_value": 100.0,
        "settlement_contract_version": "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
    }


class ExactSettlementMaturationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.forecasts = self.root / "forecasts"
        self.evidence = self.root / "evidence"
        self.outcomes = self.root / "outcomes"
        self.bindings = self.root / "bindings"
        self.raw = self.root / "raw" / "EXP-FC-exact-settlement-test"
        self.forecasts.mkdir(parents=True)
        self.evidence.mkdir(parents=True)
        self.raw.mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def write_valid_fixture(self):
        fc = forecast()
        (self.forecasts / "forecast.json").write_bytes(canon(fc))
        payload = b"fixture-source-payload"
        raw_path = self.raw / "source.json"
        raw_path.write_bytes(payload)
        ev = {
            "contract": "FORECAST_SETTLEMENT_EVIDENCE_v1",
            "owner_contract": "FORECAST_SETTLEMENT_PRICE_OWNER_v1",
            "forecast_id": fc["forecast_id"],
            "forecast_sha256": digest(fc),
            "settlement_contract_version": fc["settlement_contract_version"],
            "metric_path": fc["metric_path"],
            "normalized_metric_path": fc["metric_path"],
            "settlement_target_utc": fc["outcome_due_utc"],
            "captured_at_utc": fc["outcome_due_utc"],
            "captured_at_semantics": "ADJUDICATION_TARGET_TIME_NOT_SOURCE_OBSERVATION",
            "source_candle_open_utc": "2026-08-15T14:00:00Z",
            "source_candle_close_utc": "2026-08-15T14:00:59.999000Z",
            "source_candle_offset_seconds": -34.001,
            "source_candle_confirmed": True,
            "source_retrieved_at_utc": "2026-08-15T14:03:00Z",
            "source_publication_lag_seconds": 86.0,
            "source_id": "BINANCE_SPOT_MARKET_DATA_ONLY_KLINES",
            "source_instrument": "BTCUSDT",
            "source_request_url": "fixture://BTCUSDT",
            "source_raw_path": str(raw_path),
            "source_raw_sha256": digest_bytes(payload),
            "source_raw_bytes": len(payload),
            "market_metrics": {"spot": {"BTCUSDT": {"close": 102.0}}},
            "authority": {
                "portfolio_action": False,
                "framework_state_change": False,
                "model_weight_change": False,
                "canonical_promotion": False,
                "scientific_skill_authority": False,
            },
        }
        ev["evidence_sha256"] = digest(ev)
        (self.evidence / f"{fc['forecast_id']}.json").write_bytes(canon(ev))
        return fc, ev, raw_path

    def run_wrapper(self, now="2026-08-15T14:05:00Z"):
        return subprocess.run(
            [
                sys.executable,
                str(WRAPPER),
                "--forecast-root", str(self.forecasts),
                "--settlement-evidence-root", str(self.evidence),
                "--output-root", str(self.outcomes),
                "--binding-root", str(self.bindings),
                "--repo-root", str(self.root),
                "--now-utc", now,
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

    def test_valid_exact_evidence_matures_through_canonical_engine_and_binds_source_clock(self):
        fc, ev, _ = self.write_valid_fixture()
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        outcome = json.loads((self.outcomes / f"{fc['forecast_id']}.json").read_text())
        self.assertEqual(outcome["status"], "MATURED")
        self.assertEqual(outcome["result"], "HIT")
        self.assertEqual(outcome["end_value"], 102.0)
        self.assertTrue(outcome["scientific_score_eligible"])
        binding = json.loads((self.bindings / f"{fc['forecast_id']}.json").read_text())
        self.assertEqual(binding["contract"], "FORECAST_SETTLEMENT_OUTCOME_BINDING_v1")
        self.assertEqual(binding["source_candle_close_utc"], ev["source_candle_close_utc"])
        self.assertFalse(binding["authority"]["scientific_skill_authority"])

    def test_tampered_raw_payload_fails_closed_before_maturation(self):
        fc, _, raw_path = self.write_valid_fixture()
        raw_path.write_bytes(b"tampered")
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 2)
        self.assertIn("SETTLEMENT_RAW_PAYLOAD_HASH_MISMATCH", result.stdout)
        self.assertFalse((self.outcomes / f"{fc['forecast_id']}.json").exists())

    def test_missing_evidence_inside_original_grace_stays_pending(self):
        fc = forecast()
        (self.forecasts / "forecast.json").write_bytes(canon(fc))
        result = self.run_wrapper(now="2026-08-15T15:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["engine"]["pending"], 1)
        self.assertFalse((self.outcomes / f"{fc['forecast_id']}.json").exists())


if __name__ == "__main__":
    unittest.main()
