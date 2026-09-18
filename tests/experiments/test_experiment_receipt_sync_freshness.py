from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.experiments.sync_experiment_receipts import (
    classify_sync_state,
    prior_success_utc,
    sha256,
    sync_receipts,
    unavailable_summary,
)


class ExperimentReceiptSyncFreshnessTests(unittest.TestCase):
    def test_health_states_distinguish_new_no_change_stale_and_failed(self):
        self.assertEqual(
            classify_sync_state(imported=2, hash_mismatches=0, fetch_failures=0, source_age_hours=1, max_source_age_hours=24),
            ("HEALTHY_NEW_DATA", "PASS"),
        )
        self.assertEqual(
            classify_sync_state(imported=0, hash_mismatches=0, fetch_failures=0, source_age_hours=1, max_source_age_hours=24),
            ("HEALTHY_NO_CHANGE", "PASS"),
        )
        self.assertEqual(
            classify_sync_state(imported=3, hash_mismatches=0, fetch_failures=0, source_age_hours=48, max_source_age_hours=24),
            ("STALE", "DEGRADED"),
        )
        self.assertEqual(
            classify_sync_state(imported=0, hash_mismatches=1, fetch_failures=0, source_age_hours=1, max_source_age_hours=24),
            ("FAILED", "FAIL"),
        )

    def test_unavailable_run_writes_current_degraded_state_not_old_pass(self):
        previous = {
            "status": "PASS",
            "generated_at_utc": "2026-09-15T06:23:13Z",
            "source_manifest_sha256": "a" * 64,
        }
        now = datetime(2026, 9, 18, 8, 0, tzinfo=timezone.utc)
        summary = unavailable_summary(now=now, previous=previous, error_class="URLError")
        self.assertEqual(summary["sync_state"], "UNAVAILABLE")
        self.assertEqual(summary["status"], "DEGRADED")
        self.assertFalse(summary["source_reachable"])
        self.assertEqual(summary["generated_at_utc"], "2026-09-18T08:00:00Z")
        self.assertEqual(summary["last_successful_sync_utc"], "2026-09-15T06:23:13Z")
        self.assertNotEqual(summary["status"], previous["status"])

    def test_existing_receipts_are_hash_verified_without_refetch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = {"contract": "EXPERIMENT_EXECUTION_RECEIPT_v1", "receipt_id": "XR-1"}
            (root / "XR-1.json").write_text(json.dumps(receipt))
            calls = []

            def no_fetch(url: str):
                calls.append(url)
                raise AssertionError("existing verified receipt must not be refetched")

            manifest = {
                "receipts": [{
                    "receipt_id": "XR-1",
                    "sha256": sha256(receipt),
                    "raw_url": "https://example.invalid/XR-1.json",
                }]
            }
            imported, mismatches, failures, verified = sync_receipts(manifest, root, fetcher=no_fetch)
            self.assertEqual((imported, mismatches, failures, verified), (0, 0, 0, 1))
            self.assertEqual(calls, [])

    def test_missing_receipt_is_fetched_hash_bound_and_written_once(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt = {"contract": "EXPERIMENT_EXECUTION_RECEIPT_v1", "receipt_id": "XR-NEW"}
            manifest = {
                "receipts": [{
                    "receipt_id": "XR-NEW",
                    "sha256": sha256(receipt),
                    "raw_url": "fixture://XR-NEW",
                }]
            }
            imported, mismatches, failures, verified = sync_receipts(
                manifest,
                root,
                fetcher=lambda _: receipt,
            )
            self.assertEqual((imported, mismatches, failures, verified), (1, 0, 0, 0))
            self.assertEqual(json.loads((root / "XR-NEW.json").read_text()), receipt)

    def test_prior_success_prefers_explicit_last_success(self):
        previous = {
            "status": "DEGRADED",
            "sync_state": "STALE",
            "generated_at_utc": "2026-09-18T08:00:00Z",
            "last_successful_sync_utc": "2026-09-15T06:23:13Z",
        }
        self.assertEqual(prior_success_utc(previous), "2026-09-15T06:23:13Z")


if __name__ == "__main__":
    unittest.main()
