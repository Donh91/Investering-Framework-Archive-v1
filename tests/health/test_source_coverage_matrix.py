"""Offline guard tests for the advisory multi-cadence source coverage observer."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

PATH = Path(__file__).parents[2] / "scripts" / "health" / "build_operations_dashboard.py"
spec = importlib.util.spec_from_file_location("dashboard_coverage", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NOW = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)


class SourceCoverageObserverTests(unittest.TestCase):
    def write(self, root, path, value):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def sample(self, root, health=None):
        return module.source_coverage_snapshot(root, NOW, health or {})

    def by_lane(self, result, lane):
        return next(row for row in result["rows"] if row["lane"] == lane)

    def test_missing_sources_do_not_look_green(self):
        with tempfile.TemporaryDirectory() as td:
            snap = self.sample(Path(td))
            self.assertGreaterEqual(snap["source_count"], 9)
            self.assertTrue(all(x["source_state"] == "MISSING_OR_DEGRADED" for x in snap["rows"]))
            self.assertTrue(all(x["consumer_delivery"].startswith("NOT_ATTESTED") for x in snap["rows"]))

    def test_successful_schedule_does_not_certify_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            snap = self.sample(Path(td), {"workflows": [{"workflow": "hourly-sequence-capture.yml",
                "live": {"latest_scheduled_run": {"event": "schedule", "conclusion": "success"}}}]})
            row = self.by_lane(snap, "hourly")
            self.assertEqual(row["last_native_schedule_state"], "LAST_SCHEDULE_SUCCESS_NOT_COVERAGE")
            self.assertEqual(row["source_state"], "MISSING_OR_DEGRADED")

    def test_26_hour_complete_but_stale_is_delayed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json", dict(
                contract="HOURLY_SEQUENCE_LATEST_POINTER_v2_2", status="COMPLETE",
                window_end_utc="2026-11-07T06:00:00Z", requested_hours=26,
                spot_complete_hours=26, spot_flow_complete_hours=26,
                long_short_complete_hours=26, derivatives_oi_complete_hours=26))
            self.assertEqual(self.by_lane(self.sample(root), "hourly")["source_state"], "DELAYED_SOURCE")

    def test_partial_hourly_is_never_healthy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json", dict(
                contract="HOURLY_SEQUENCE_LATEST_POINTER_v2_2", status="COMPLETE",
                window_end_utc="2026-11-07T11:00:00Z", requested_hours=26,
                spot_complete_hours=26, spot_flow_complete_hours=25,
                long_short_complete_hours=26, derivatives_oi_complete_hours=26))
            row = self.by_lane(self.sample(root), "hourly")
            self.assertEqual(row["source_state"], "MISSING_OR_DEGRADED")

    def test_news_fetch_cannot_verify_unverified_discovery(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/2026/11/2026-11-07.json"
            self.write(root, "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json", {
                "contract": "SITUATION_ROOM_DAILY_OWNER_LATEST_POINTER_v1",
                "run_id": "SRDO-1", "path": path})
            self.write(root, path, {
                "run_id": "SRDO-1", "run_status": "DEGRADED",
                "daily_result": "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY",
                "detection_time_utc": "2026-11-07T11:00:00Z",
                "source_coverage": {"primary_pass": 6, "primary_total": 6}})
            row = self.by_lane(self.sample(root), "news_intelligence")
            self.assertEqual(row["source_state"], "MISSING_OR_DEGRADED")
            self.assertEqual(row["reason"], "NEWS_DISCOVERY_NOT_VERIFIED")

    def test_news_pointer_traversal_is_not_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json", {
                "contract": "SITUATION_ROOM_DAILY_OWNER_LATEST_POINTER_v1",
                "run_id": "SRDO-1",
                "path": "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/../../secrets.json"})
            row = self.by_lane(self.sample(root), "news_intelligence")
            self.assertEqual(row["reason"], "NEWS_OWNER_DATED_PATH_INVALID")

    def test_future_source_clock_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, "03_DAILY_CAPTURE_LOGS/etf/LATEST.json", {
                "contract": "DAILY_SETTLED_ETF_LATEST_POINTER_v2", "status": "PASS",
                "retrieved_at_utc": "2026-11-08T12:00:00Z"})
            self.assertEqual(self.by_lane(self.sample(root), "settled_etf")["reason"], "SOURCE_CLOCK_IN_FUTURE")

    def test_research_observed_is_not_economic_edge(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json", {
                "contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1",
                "generated_at_utc": "2026-11-07T11:00:00Z", "candidate_count": 705,
                "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION"})
            row = self.by_lane(self.sample(root), "edge_research")
            self.assertEqual(row["source_state"], "OBSERVED_SOURCE")
            self.assertEqual(row["science_or_edge_admission"], "NOT_ATTESTED_BY_THIS_SNAPSHOT")


if __name__ == "__main__":
    unittest.main()
