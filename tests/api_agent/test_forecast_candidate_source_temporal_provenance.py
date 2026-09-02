from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "api_agent"))
sys.path.insert(0, str(ROOT / "scripts" / "learning"))
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from build_forecast_ratification_queue import build_queue  # noqa: E402
from materialize_forecast_candidates import materialize_forecast_candidates  # noqa: E402
from forecast_ratification_contract import SOURCE_FRESHNESS_CONTRACT_V1, SOURCE_OUTPUT_MAX_AGE_MINUTES  # noqa: E402

UTC = timezone.utc


def forecast():
    return {
        "metric_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
        "direction": "UP",
        "target_mode": "PCT_MOVE",
        "threshold_pct": 1.0,
        "target_value": None,
        "range_low": None,
        "range_high": None,
        "horizon_days": 1,
        "rationale": "fresh prospective source fixture",
    }


def receipt(created_unix: int):
    return {
        "contract": "API_AGENT_RECEIPT_v3",
        "task": "DAILY_DIRECTOR_SHADOW",
        "model": "gpt-5.6-luna",
        "prompt_hash": "a" * 64,
        "context_hash": "b" * 64,
        "output_hash": "c" * 64,
        "created_unix": created_unix,
    }


class ForecastCandidateSourceTemporalProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pending = self.root / "PENDING"
        self.terminal = self.root / "TERMINAL"
        self.pending.mkdir(parents=True)
        self.terminal.mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def test_fresh_director_output_materializes_and_is_owner_visible(self):
        now = datetime(2026, 9, 2, 21, 45, tzinfo=UTC)
        source = datetime(2026, 9, 2, 21, 30, tzinfo=UTC)
        result = materialize_forecast_candidates({"forecast_candidates": [forecast()]}, receipt(int(source.timestamp())), self.pending, now)
        self.assertEqual(result["created_count"], 1)
        self.assertEqual(result["source_temporal_censored_count"], 0)
        candidate = json.loads(next(self.pending.rglob("*.json")).read_text())
        self.assertEqual(candidate["source_freshness_contract"], SOURCE_FRESHNESS_CONTRACT_V1)
        self.assertEqual(candidate["source_output_created_at_utc"], "2026-09-02T21:30:00Z")
        self.assertEqual(candidate["source_output_age_at_materialization_seconds"], 900.0)
        self.assertEqual(candidate["source_output_max_age_minutes"], SOURCE_OUTPUT_MAX_AGE_MINUTES)
        self.assertEqual(len(candidate["source_receipt_sha256"]), 64)
        queue = build_queue(self.pending, self.terminal, datetime(2026, 9, 2, 21, 50, tzinfo=UTC))
        self.assertEqual(queue["counts"]["decision_required"], 1)
        self.assertEqual(queue["counts"]["source_temporal_quarantine_ids"], 0)
        self.assertEqual(queue["candidates"][0]["source_output_created_at_utc"], "2026-09-02T21:30:00Z")
        self.assertFalse(queue["outcome_data_included"])

    def test_hours_old_director_output_is_censored_not_reborn_as_new_forecast(self):
        now = datetime(2026, 9, 2, 21, 45, tzinfo=UTC)
        source = datetime(2026, 9, 2, 11, 27, tzinfo=UTC)
        result = materialize_forecast_candidates({"forecast_candidates": [forecast()]}, receipt(int(source.timestamp())), self.pending, now)
        self.assertEqual(result["created_count"], 0)
        self.assertEqual(result["source_temporal_censored_count"], 1)
        self.assertEqual(result["source_temporal_censored"][0]["reason"], "SOURCE_OUTPUT_STALE_AT_CANDIDATE_MATERIALIZATION")
        self.assertEqual(list(self.pending.rglob("*.json")), [])

    def test_missing_receipt_timestamp_is_censored_without_batch_failure(self):
        now = datetime(2026, 9, 2, 21, 45, tzinfo=UTC)
        bad_receipt = receipt(int(now.timestamp()))
        bad_receipt.pop("created_unix")
        result = materialize_forecast_candidates({"forecast_candidates": [forecast()]}, bad_receipt, self.pending, now)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["created_count"], 0)
        self.assertEqual(result["source_temporal_censored_count"], 1)
        self.assertEqual(result["source_temporal_censored"][0]["reason"], "SOURCE_RECEIPT_CREATED_UNIX_REQUIRED")

    def test_owner_queue_fail_closes_new_candidate_without_source_provenance(self):
        candidate = {
            "contract": "FORECAST_CANDIDATE_v1",
            "authority": "UNRATIFIED_RESEARCH_ONLY",
            "candidate_id": "manual-missing-source",
            "created_at_utc": "2026-09-02T21:45:00Z",
            "model": "gpt-5.6-luna",
            "task": "DAILY_DIRECTOR_SHADOW",
            "prompt_sha256": "a" * 64,
            "context_sha256": "b" * 64,
            "source_output_sha256": "c" * 64,
            "candidate": forecast(),
            "ratification_status": "PENDING",
            "self_promotion_allowed": False,
        }
        path = self.pending / "2026/09/02/manual-missing-source.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(candidate, sort_keys=True, separators=(",", ":")) + "\n")
        queue = build_queue(self.pending, self.terminal, datetime(2026, 9, 2, 21, 50, tzinfo=UTC))
        self.assertEqual(queue["counts"]["decision_required"], 0)
        self.assertEqual(queue["counts"]["source_temporal_quarantine_ids"], 1)
        self.assertIn("SOURCE_TEMPORAL_PROVENANCE_CONTRACT_REQUIRED", queue["quarantines"][0]["error"])
        self.assertFalse(queue["quarantines"][0]["owner_decision_allowed"])

    def test_owner_queue_rejects_tampered_age_binding(self):
        now = datetime(2026, 9, 2, 21, 45, tzinfo=UTC)
        source = datetime(2026, 9, 2, 21, 30, tzinfo=UTC)
        materialize_forecast_candidates({"forecast_candidates": [forecast()]}, receipt(int(source.timestamp())), self.pending, now)
        path = next(self.pending.rglob("*.json"))
        candidate = json.loads(path.read_text())
        candidate["source_output_age_at_materialization_seconds"] = 0
        path.write_text(json.dumps(candidate, sort_keys=True, separators=(",", ":")) + "\n")
        queue = build_queue(self.pending, self.terminal, datetime(2026, 9, 2, 21, 50, tzinfo=UTC))
        self.assertEqual(queue["counts"]["decision_required"], 0)
        self.assertEqual(queue["counts"]["source_temporal_quarantine_ids"], 1)
        self.assertIn("SOURCE_OUTPUT_AGE_BINDING_MISMATCH", queue["quarantines"][0]["error"])


if __name__ == "__main__":
    unittest.main()
