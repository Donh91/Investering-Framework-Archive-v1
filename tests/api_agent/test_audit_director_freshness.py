from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.api_agent import check_director_freshness as freshness


NOW = datetime(2026, 9, 9, 0, 0, tzinfo=timezone.utc)


def write_context(path: Path, run_id: str = "RUN_NEW", captured_at_utc: object = "2026-09-08T23:00:00Z") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"latest_capture": {"run_id": run_id, "captured_at_utc": captured_at_utc}}))


class DirectorFreshnessAuditTests(unittest.TestCase):
    def test_fresh_valid_unseen_owner_run_is_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context)
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertTrue(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "NEW_OWNER_RUN_FRESH_SOURCE")
            self.assertTrue(result["source_timestamp_valid"])
            self.assertTrue(result["identity_unseen"])

    def test_duplicate_fresh_owner_run_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, "RUN_DUP")
            write_context(root / "outputs" / "old" / "context.json", "RUN_DUP", "2026-09-08T22:00:00Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertFalse(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "OWNER_RUN_ALREADY_ANALYZED")
            self.assertFalse(result["identity_unseen"])

    def test_unseen_ancient_capture_is_not_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, "SYNTHETIC_UNSEEN_OLD", "2026-08-08T14:01:34Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertFalse(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "CURRENT_CAPTURE_SOURCE_STALE")
            self.assertGreater(result["source_age_seconds"], freshness.OWNER_CAPTURE_CADENCE.total_seconds())

    def test_missing_or_naive_source_timestamp_fails_closed(self) -> None:
        for raw_timestamp in (None, "", "2026-09-08T23:00:00", "not-a-time"):
            with self.subTest(raw_timestamp=raw_timestamp), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                context = root / "context.json"
                write_context(context, captured_at_utc=raw_timestamp)
                result = freshness.evaluate(context, root / "outputs", NOW)
                self.assertFalse(result["fresh_ready"])
                self.assertEqual(result["fresh_reason"], "CURRENT_CAPTURE_TIMESTAMP_INVALID_OR_MISSING")
                self.assertFalse(result["source_timestamp_valid"])

    def test_future_source_timestamp_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, captured_at_utc="2026-09-09T00:00:01Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertFalse(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "CURRENT_CAPTURE_TIMESTAMP_FUTURE")

    def test_owner_cadence_boundary_is_not_tightened(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, captured_at_utc="2026-09-08T20:00:00Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertTrue(result["fresh_ready"])
            self.assertEqual(result["source_age_seconds"], 14400.0)


if __name__ == "__main__":
    unittest.main()
