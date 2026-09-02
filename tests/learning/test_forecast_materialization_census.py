from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from materialize_forecast_candidates_batch import run_batch  # noqa: E402

UTC = timezone.utc


def forecast(direction: str = "DOWN") -> dict:
    return {
        "metric_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
        "direction": direction,
        "target_mode": "PCT_MOVE",
        "threshold_pct": 1.0,
        "target_value": None,
        "range_low": None,
        "range_high": None,
        "horizon_days": 1,
        "rationale": "census fixture",
    }


def write_source(root: Path, name: str, created_unix: int | None, candidates: list[dict], *, receipt: bool = True) -> None:
    run = root / name
    run.mkdir(parents=True, exist_ok=True)
    output = {"forecast_candidates": candidates}
    (run / "DAILY_DIRECTOR_OUTPUT.json").write_text(json.dumps(output, sort_keys=True))
    if receipt:
        value = {
            "contract": "API_AGENT_RECEIPT_v3",
            "task": "DAILY_DIRECTOR_SHADOW",
            "model": "gpt-5.6-luna",
            "prompt_hash": "a" * 64,
            "context_hash": "b" * 64,
            "output_hash": (name.encode().hex() + "0" * 64)[:64],
        }
        if created_unix is not None:
            value["created_unix"] = created_unix
        (run / "DAILY_DIRECTOR_RECEIPT.json").write_text(json.dumps(value, sort_keys=True))


class ForecastMaterializationCensusTests(unittest.TestCase):
    def test_census_records_created_stale_and_missing_receipt_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            pending = root / "PENDING"
            census_path = root / "LATEST_FORECAST_MATERIALIZATION_CENSUS.json"
            now = datetime(2026, 9, 2, 21, 45, tzinfo=UTC)

            write_source(outputs, "fresh", int(datetime(2026, 9, 2, 21, 30, tzinfo=UTC).timestamp()), [forecast()])
            write_source(outputs, "stale", int(datetime(2026, 9, 2, 13, 26, tzinfo=UTC).timestamp()), [forecast(), forecast("UP")])
            write_source(outputs, "missing", None, [forecast()], receipt=False)

            census = run_batch(outputs, pending, census_path, now=now)
            self.assertEqual(census["contract"], "FORECAST_MATERIALIZATION_CENSUS_v1")
            self.assertFalse(census["outcome_data_read"])
            self.assertFalse(census["authority"]["forecast_skill_authority"])
            self.assertFalse(census["authority"]["portfolio_action"])
            self.assertEqual(census["totals"]["source_output_count"], 3)
            self.assertEqual(census["totals"]["paired_source_count"], 2)
            self.assertEqual(census["totals"]["missing_receipt_count"], 1)
            self.assertEqual(census["totals"]["created_candidate_count"], 1)
            self.assertEqual(census["totals"]["source_temporal_censored_candidate_count"], 2)
            self.assertEqual(len(list(pending.rglob("*.json"))), 1)
            self.assertEqual(len(census["census_sha256"]), 64)

            rows = {Path(row["output_path"]).parent.name: row for row in census["sources"]}
            self.assertEqual(rows["fresh"]["created_count"], 1)
            self.assertEqual(rows["stale"]["source_temporal_censored_count"], 2)
            self.assertEqual(
                rows["stale"]["source_temporal_censored_reason_counts"],
                {"SOURCE_OUTPUT_STALE_AT_CANDIDATE_MATERIALIZATION": 2},
            )
            self.assertEqual(rows["missing"]["materialization_status"], "SOURCE_RECEIPT_MISSING")
            self.assertEqual(json.loads(census_path.read_text())["census_sha256"], census["census_sha256"])

    def test_second_run_reports_existing_candidate_without_duplication(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = root / "outputs"
            pending = root / "PENDING"
            census_path = root / "LATEST_FORECAST_MATERIALIZATION_CENSUS.json"
            now = datetime(2026, 9, 2, 21, 45, tzinfo=UTC)
            source = int(datetime(2026, 9, 2, 21, 30, tzinfo=UTC).timestamp())
            write_source(outputs, "fresh", source, [forecast()])

            first = run_batch(outputs, pending, census_path, now=now)
            second = run_batch(outputs, pending, census_path, now=now)
            self.assertEqual(first["totals"]["created_candidate_count"], 1)
            self.assertEqual(second["totals"]["created_candidate_count"], 0)
            self.assertEqual(second["totals"]["existing_candidate_count"], 1)
            self.assertEqual(len(list(pending.rglob("*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
