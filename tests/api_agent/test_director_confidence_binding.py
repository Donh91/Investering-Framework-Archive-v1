import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.materialize_director_confidence_binding import (
    CONTRACT,
    build_binding,
    materialize,
    parse_header,
)


class DirectorConfidenceBindingTests(unittest.TestCase):
    def test_valid_header_binds_exact_direct_forecast_candidate(self):
        output = {
            "summary": "CYCLE_HEADER | PHASE=UNCLEAR | WARNING=EXIT_WARNING | DIRECTION=DISTRIBUTION_RISK_RISING | CONFIDENCE=LOW\nbody",
            "forecast_candidates": [
                {
                    "metric_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
                    "direction": "DOWN",
                    "target_mode": "PCT_MOVE",
                    "threshold_pct": 1.0,
                    "target_value": None,
                    "range_low": None,
                    "range_high": None,
                    "horizon_days": 1,
                    "rationale": "fixture",
                }
            ],
        }
        context = {
            "latest_capture": {
                "captured_at_utc": "2026-09-10T12:00:00Z",
                "run_id": "fixture-run",
                "market_metrics": {"derivatives": {"BTC-USDT-SWAP": {"mark_price": {"mark_price": 100.0}}}},
            }
        }
        receipt = {"contract": "API_AGENT_RECEIPT_v3", "task": "DAILY_DIRECTOR_SHADOW"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding = build_binding(
                output,
                context,
                receipt,
                output_path="daily/output.json",
                context_path="daily/context.json",
                receipt_path="daily/receipt.json",
                forecast_root=root / "forecasts",
            )
            self.assertIsNotNone(binding)
            assert binding is not None
            self.assertEqual(binding["contract"], CONTRACT)
            self.assertEqual(binding["cycle_header"]["confidence"], "LOW")
            self.assertEqual(len(binding["emitted_candidate_ids"]), 1)
            self.assertTrue(binding["emitted_candidate_ids"][0].startswith("EC-"))
            self.assertEqual(binding["emitted_forecast_ids"], [])
            self.assertFalse(binding["calibration_boundary"]["historical_prose_backfill"])

    def test_malformed_or_prose_only_header_fails_closed(self):
        self.assertIsNone(parse_header("Confidence looks HIGH from the rationale."))
        self.assertIsNone(parse_header("CYCLE_HEADER | PHASE=X | WARNING=Y | DIRECTION=Z | CONFIDENCE=VERY_HIGH"))
        binding = build_binding(
            {"summary": "Confidence looks HIGH from the rationale.", "forecast_candidates": []},
            {"latest_capture": {"captured_at_utc": "2026-09-10T12:00:00Z", "market_metrics": {}}},
            {},
            output_path="o",
            context_path="c",
            receipt_path="r",
            forecast_root=Path("does-not-exist"),
        )
        self.assertIsNone(binding)

    def test_linked_forecast_is_causal_and_immutable_replay_is_noop(self):
        output = {
            "summary": "CYCLE_HEADER | PHASE=UNCLEAR | WARNING=NONE | DIRECTION=RANGE | CONFIDENCE=MEDIUM",
            "forecast_candidates": [
                {
                    "metric_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
                    "direction": "DOWN",
                    "target_mode": "PCT_MOVE",
                    "threshold_pct": 1.0,
                    "horizon_days": 1,
                    "rationale": "fixture",
                }
            ],
        }
        context = {
            "latest_capture": {
                "captured_at_utc": "2026-09-10T12:00:00Z",
                "run_id": "fixture-run",
                "market_metrics": {"derivatives": {"BTC-USDT-SWAP": {"mark_price": {"mark_price": 100.0}}}},
            }
        }
        receipt = {"contract": "API_AGENT_RECEIPT_v3"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = build_binding(output, context, receipt, output_path="o", context_path="c", receipt_path="r", forecast_root=root / "forecasts")
            assert first is not None
            candidate_id = first["emitted_candidate_ids"][0]
            forecast_dir = root / "forecasts" / "2026" / "09"
            forecast_dir.mkdir(parents=True)
            (forecast_dir / "EXP-FC-fixture.json").write_text(
                json.dumps({
                    "contract": "FROZEN_FORECAST_v1",
                    "forecast_id": "EXP-FC-fixture",
                    "source_candidate_id": candidate_id,
                    "frozen_at_utc": "2026-09-10T12:00:00Z",
                })
            )
            second = build_binding(output, context, receipt, output_path="o", context_path="c", receipt_path="r", forecast_root=root / "forecasts")
            assert second is not None
            self.assertEqual(second["emitted_forecast_ids"], ["EXP-FC-fixture"])
            path = materialize(root / "bindings", second)
            self.assertEqual(path, materialize(root / "bindings", second))
            changed = dict(second)
            changed["status"] = "CHANGED"
            with self.assertRaisesRegex(ValueError, "IMMUTABLE_BINDING_CONFLICT"):
                materialize(root / "bindings", changed)


if __name__ == "__main__":
    unittest.main()
