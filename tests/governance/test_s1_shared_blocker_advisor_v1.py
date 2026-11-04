"""Shared-defect diagnosis must never infer implementation authority."""
import unittest
from scripts.governance.s1_shared_blocker_advisor_v1 import cluster_blockers

BASE = "https://github.com/Donh91/Investering-Framework-Archive-v1"
UPSTREAM = BASE + "/issues/1156"


def case(n, blocker="same-failure-123"):
    return {"original_url": BASE + "/pull/" + str(n),
            "original_owner": "existing owner", "blocker_owner_url": UPSTREAM,
            "blocker_fingerprint": blocker}


class SharedBlockerTests(unittest.TestCase):
    def test_two_dependents_share_one_repair_candidate(self):
        proposed = cluster_blockers([case(1877), case(1878)])
        self.assertEqual(len(proposed), 1)
        self.assertEqual(proposed[0]["affected_original_count"], 2)
        self.assertFalse(proposed[0]["autoroute_or_merge_allowed"])
        self.assertFalse(proposed[0]["source_gates_verified"])

    def test_one_case_is_not_a_shared_root(self):
        self.assertEqual(cluster_blockers([case(1877)]), [])

    def test_distinct_fingerprints_not_conflated(self):
        self.assertEqual(cluster_blockers([case(1877), case(1878, "different-failure-987")]), [])

    def test_duplicate_url_does_not_inflate_scope(self):
        one = case(1877)
        two = {**one, "original_url": one["original_url"] + "?from=bridge"}
        self.assertEqual(cluster_blockers([one, two]), [])

    def test_injected_url_rejected(self):
        bad = {**case(1877), "blocker_owner_url": "https://github.com.evil/Donh91/issues/1156"}
        self.assertEqual(cluster_blockers([bad, case(1878)]), [])

    def test_missing_or_short_evidence_ignored(self):
        self.assertEqual(cluster_blockers([case(1877, "123"), case(1878, "123")]), [])

    def test_resolved_blocker_not_reopened(self):
        done = {**case(1877), "blocker_resolved": True}
        self.assertEqual(cluster_blockers([done, case(1878)]), [])

    def test_bounded_maximum(self):
        with self.assertRaises(ValueError):
            cluster_blockers([], limit=4)


if __name__ == "__main__":
    unittest.main()
