import unittest
from datetime import date, datetime, timezone

from scripts.health.build_daily_machine_throughput import (
    _workflow_metrics,
    day_window,
    flatten_runs,
    is_failure,
    scalar_leaf_count,
)


class DailyMachineThroughputHelperTests(unittest.TestCase):
    def test_scalar_leaf_count_is_structural_and_deterministic(self):
        value = {
            "a": 1,
            "b": [2, {"c": None, "d": True}],
            "e": {"f": "x"},
        }
        self.assertEqual(scalar_leaf_count(value), 5)

    def test_flatten_runs_accepts_gh_api_slurp_shape(self):
        payload = [
            {"workflow_runs": [{"id": 1}, {"id": 2}]},
            {"workflow_runs": [{"id": 3}]},
        ]
        self.assertEqual([row["id"] for row in flatten_runs(payload)], [1, 2, 3])

    def test_failure_semantics_do_not_treat_cancelled_as_failure(self):
        self.assertTrue(is_failure("failure"))
        self.assertTrue(is_failure("timed_out"))
        self.assertFalse(is_failure("success"))
        self.assertFalse(is_failure("cancelled"))

    def test_scheduled_success_rate_counts_only_success_conclusions(self):
        payload = {
            "workflow_runs": [
                {
                    "id": 1,
                    "event": "schedule",
                    "conclusion": "success",
                    "run_started_at": "2026-08-27T10:00:00Z",
                },
                {
                    "id": 2,
                    "event": "schedule",
                    "conclusion": "cancelled",
                    "run_started_at": "2026-08-27T11:00:00Z",
                },
                {
                    "id": 3,
                    "event": "schedule",
                    "conclusion": "failure",
                    "run_started_at": "2026-08-27T12:00:00Z",
                },
            ]
        }
        start = datetime(2026, 8, 27, tzinfo=timezone.utc)
        end = datetime(2026, 8, 28, tzinfo=timezone.utc)
        metrics = _workflow_metrics(payload, start, end)
        self.assertEqual(metrics["scheduled_runs"], 3)
        self.assertEqual(metrics["scheduled_failed_runs"], 1)
        self.assertEqual(metrics["cancelled_runs"], 1)
        self.assertEqual(metrics["scheduled_success_rate_pct"], 33.333)

    def test_copenhagen_window_respects_dst(self):
        summer_start, summer_end = day_window(date(2026, 8, 28), "Europe/Copenhagen")
        winter_start, winter_end = day_window(date(2026, 1, 28), "Europe/Copenhagen")
        self.assertEqual(summer_start.isoformat(), "2026-08-27T22:00:00+00:00")
        self.assertEqual(summer_end.isoformat(), "2026-08-28T22:00:00+00:00")
        self.assertEqual(winter_start.isoformat(), "2026-01-27T23:00:00+00:00")
        self.assertEqual(winter_end.isoformat(), "2026-01-28T23:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
