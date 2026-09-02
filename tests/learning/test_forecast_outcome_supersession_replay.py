from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "replay_superseded_forecast_outcomes.py"
_spec = importlib.util.spec_from_file_location("replay_superseded_forecast_outcomes", SCRIPT)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)


class ForecastOutcomeSupersessionReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.forecasts = self.repo / "research/framework_memory/forecast_memory"
        self.original_outcomes = self.repo / "research/framework_memory/outcome_memory"
        self.evidence = self.repo / "research/framework_memory/outcome_replay_evidence"
        self.raw = self.repo / "research/framework_memory/outcome_replay_raw"
        self.replay_outcomes = self.repo / "research/framework_memory/outcome_replays"
        self.overlays = self.repo / "research/framework_memory/outcome_supersession"
        self.fixtures = self.repo / "fixtures"
        for path in (self.forecasts, self.original_outcomes, self.fixtures):
            path.mkdir(parents=True, exist_ok=True)
        self.addCleanup(self.tmp.cleanup)

    def forecast(self, forecast_id: str = "legacy-btc") -> dict:
        return {
            "contract": "FROZEN_FORECAST_v1",
            "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
            "forecast_id": forecast_id,
            "source_candidate_id": "EC-test",
            "frozen_at_utc": "2026-08-14T14:01:34Z",
            "outcome_due_utc": "2026-08-15T14:01:34Z",
            "metric_path": "spot.BTCUSDT.close",
            "direction": "UP",
            "start_value": 100.0,
            "target_mode": "PCT_MOVE",
            "threshold_pct": 1.0,
            "range_lower_pct": None,
            "range_upper_pct": None,
            "authority": {
                "portfolio_action": False,
                "framework_state_change": False,
                "model_weight_change": False,
                "canonical_promotion": False,
            },
        }

    def write_pair(self, forecast: dict, original_status: str = "CENSORED", original_result=None):
        forecast_path = self.forecasts / f"{forecast['forecast_id']}.json"
        forecast_path.write_bytes(_module.canon(forecast))
        outcome = {
            "contract": "MATURED_OUTCOME_v3",
            "forecast_id": forecast["forecast_id"],
            "forecast_sha256": _module.digest(forecast),
            "status": original_status,
            "authority": {"model_weight_change": False, "portfolio_action": False},
        }
        if original_status == "CENSORED":
            outcome["reason"] = "METRIC_UNAVAILABLE"
        else:
            outcome["result"] = original_result
            outcome["start_value"] = 100.0
            outcome["end_value"] = 98.0 if original_result == "MISS" else 102.0
        outcome_path = self.original_outcomes / f"{forecast['forecast_id']}.json"
        outcome_path.write_bytes(_module.canon(outcome))
        return forecast_path, outcome_path, outcome

    def write_binance_fixture(self):
        target = datetime(2026, 8, 15, 14, 1, 34, tzinfo=timezone.utc)
        open_dt = target.replace(second=0, microsecond=0).replace(minute=0)
        open_ms = int(open_dt.timestamp() * 1000)
        row = [[open_ms, "100", "103", "99", "102", "10", open_ms + 59_999]]
        (self.fixtures / "BINANCE_SPOT_1M__BTCUSDT.json").write_text(json.dumps(row))

    def test_population_selection_is_outcome_blind(self):
        forecast = self.forecast()
        _, _, censored = self.write_pair(forecast, "CENSORED")
        eligible_censored, _ = _module.replay_population_eligible(forecast, censored)
        hit = dict(censored)
        hit.pop("reason", None)
        hit["status"] = "MATURED"
        hit["result"] = "HIT"
        eligible_hit, _ = _module.replay_population_eligible(forecast, hit)
        self.assertTrue(eligible_censored)
        self.assertTrue(eligible_hit)

    def test_original_forecast_hash_mismatch_fails_closed(self):
        forecast = self.forecast()
        _, _, outcome = self.write_pair(forecast)
        outcome["forecast_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "ORIGINAL_OUTCOME_FORECAST_HASH_MISMATCH"):
            _module.replay_population_eligible(forecast, outcome)

    def test_replay_envelope_does_not_mutate_original(self):
        forecast = self.forecast()
        before = _module.canon(forecast)
        envelope = _module.replay_envelope(forecast)
        self.assertEqual(_module.canon(forecast), before)
        self.assertEqual(envelope["settlement_contract_version"], "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1")
        self.assertEqual(envelope["replay_envelope"]["source_forecast_sha256"], _module.digest(forecast))
        self.assertTrue(envelope["replay_envelope"]["supersedes_without_mutating"])

    def test_censored_original_replays_to_hit_and_writes_append_only_overlay(self):
        forecast = self.forecast()
        forecast_path, outcome_path, _ = self.write_pair(forecast, "CENSORED")
        original_forecast_bytes = forecast_path.read_bytes()
        original_outcome_bytes = outcome_path.read_bytes()
        self.write_binance_fixture()
        now = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)

        status = _module.run_replay(
            forecast_path,
            outcome_path,
            self.evidence,
            self.raw,
            self.replay_outcomes,
            self.overlays,
            self.repo,
            now,
            self.fixtures,
        )
        self.assertEqual(status, "CREATED_SUPERSESSION_OVERLAY")
        self.assertEqual(forecast_path.read_bytes(), original_forecast_bytes)
        self.assertEqual(outcome_path.read_bytes(), original_outcome_bytes)

        replay = json.loads((self.replay_outcomes / "legacy-btc.json").read_text())
        overlay = json.loads((self.overlays / "legacy-btc.json").read_text())
        self.assertEqual(replay["status"], "MATURED")
        self.assertEqual(replay["result"], "HIT")
        self.assertTrue(overlay["comparison"]["verdict_changed"])
        self.assertEqual(overlay["original"]["verdict"]["status"], "CENSORED")
        self.assertEqual(overlay["replay"]["verdict"]["result"], "HIT")
        self.assertTrue(overlay["supersedes_without_mutating"])
        self.assertFalse(overlay["selection_uses_original_verdict"])
        self.assertFalse(overlay["authority"]["scientific_skill_authority"])
        self.assertFalse(overlay["authority"]["historical_outcome_rewrite"])

        again = _module.run_replay(
            forecast_path,
            outcome_path,
            self.evidence,
            self.raw,
            self.replay_outcomes,
            self.overlays,
            self.repo,
            now,
            self.fixtures,
        )
        self.assertEqual(again, "DUPLICATE_NOOP")

    def test_exact_forecast_is_not_historical_replay_population(self):
        forecast = self.forecast()
        forecast["settlement_contract_version"] = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
        outcome = {
            "contract": "MATURED_OUTCOME_v3",
            "forecast_id": forecast["forecast_id"],
            "forecast_sha256": _module.digest(forecast),
            "status": "MATURED",
            "result": "HIT",
        }
        eligible, reason = _module.replay_population_eligible(forecast, outcome)
        self.assertFalse(eligible)
        self.assertEqual(reason, "ALREADY_EXACT_SETTLEMENT")


if __name__ == "__main__":
    unittest.main()
