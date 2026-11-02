"""S1 outcome readout counts only candidate receipts, not proved merges."""
import unittest

from scripts.governance.s1_closure_impact_readout_v1 import closure_readout

STAMP = "2026-11-02T10:00:00Z"


def merge():
    return {
        "kind": "MERGE", "observed_at_utc": STAMP,
        "actual_actor": "CHAT_S1", "repo": "Donh91/Investering-Framework-Archive-v1",
        "pr": 1877, "original_head": "a"*40, "merge_sha": "b"*40,
        "old_main_sha": "c"*40, "new_main_sha": "d"*40,
        "main_blob_readback": True,
    }


class ImpactReadoutTests(unittest.TestCase):
    def test_genuine_shape_is_still_unauthenticated(self):
        out = closure_readout([merge()], STAMP)
        self.assertEqual(out["claimed_s1_main_readback_merges"], 1)
        self.assertFalse(out["externally_authenticated"])
        self.assertIsNone(out["verified_production_impact"])
        self.assertIsNone(out["success_rate"])

    def test_comment_does_not_count_as_merge(self):
        out = closure_readout([{"kind": "COMMENT", "observed_at_utc": STAMP}], STAMP)
        self.assertEqual(out["claimed_s1_main_readback_merges"], 0)

    def test_other_actor_does_not_credit_s1(self):
        m = merge()
        m["actual_actor"] = "EXTERNAL"
        out = closure_readout([m], STAMP)
        self.assertEqual(out["claimed_s1_main_readback_merges"], 0)

    def test_duplicate_receipt_deduped(self):
        out = closure_readout([merge(), merge()], STAMP)
        self.assertEqual(out["claimed_s1_main_readback_merges"], 1)

    def test_missing_main_blob_readback(self):
        m = merge()
        m["main_blob_readback"] = False
        self.assertEqual(closure_readout([m], STAMP)["claimed_s1_main_readback_merges"], 0)

    def test_run_is_not_merge(self):
        rows = [{"kind": "S1_RUN", "native_run_id": "task-run-1",
                 "observed_at_utc": STAMP}] * 2
        out = closure_readout(rows, STAMP)
        self.assertEqual(out["claimed_distinct_native_runs"], 1)
        self.assertEqual(out["claimed_s1_main_readback_merges"], 0)

    def test_only_fixed_windows(self):
        with self.assertRaises(ValueError):
            closure_readout([], STAMP, days=9)

    def test_old_event_outside_window(self):
        m = merge()
        m["observed_at_utc"] = "2026-10-01T00:00:00Z"
        self.assertEqual(closure_readout([m], STAMP)["claimed_s1_main_readback_merges"], 0)


if __name__ == "__main__":
    unittest.main()
