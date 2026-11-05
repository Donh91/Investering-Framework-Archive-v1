"""Adversarial tests for read-only replay and non-authority guarantees."""
import copy
import unittest

from scripts.orchestration.s1_shadow_native_replay_v1 import classify_snapshot, replay


def fixture():
    h = "a" * 40
    return {"repo": "Donh91/Investering-Framework-Archive-v1", "original_pr": 1931,
            "head_sha": h, "state": "closed", "draft": False, "merged": True,
            "merge_sha": "b" * 40,
            "required_pr_jobs": [{"head": h, "event": "pull_request", "status": "completed",
                                  "conclusion": "success", "executed_test_steps": 2}],
            "changed_main_blobs": [{"path": "research/example.txt", "expected_sha": "c" * 40,
                                    "actual_sha": "c" * 40}],
            "natural_consumer": {"event": "natural", "clock_eligible": True,
                                 "source_id": "s1", "delivered_source_id": "s1",
                                 "run_url": "https://github.com/Donh91/run",
                                 "consumer_url": "https://github.com/Donh91/site"}}


class ShadowReplayTests(unittest.TestCase):
    def stage(self, row):
        out = classify_snapshot(row)
        self.assertFalse(out["release_authorized"])
        self.assertFalse(out["source_authenticated"])
        self.assertFalse(out["s1_merge_credit"])
        self.assertFalse(out["production_verified"])
        self.assertFalse(out["side_effects"])
        return out["stage"]

    def test_happy_path_remains_unverified(self):
        self.assertEqual(self.stage(fixture()), "NATIVE_AUTHENTICATION_REQUIRED")

    def test_forged_true_flags_do_not_authorize(self):
        r = fixture()
        r.update(source_authenticated=True, release_authorized=True,
                 consumer_verified=True, native_main_contains_merge=True)
        self.assertEqual(self.stage(r), "NATIVE_AUTHENTICATION_REQUIRED")

    def test_missing_header(self):
        r = fixture()
        r["head_sha"] = "bad"
        self.assertEqual(self.stage(r), "MISSING_HEAD")

    def test_open_draft(self):
        r = fixture()
        r.update(state="open", merged=False, draft=True)
        self.assertEqual(self.stage(r), "BLOCKED_DRAFT")

    def test_open_nonmergeable(self):
        r = fixture()
        r.update(state="open", merged=False, draft=False, mergeable=False)
        self.assertEqual(self.stage(r), "BLOCKED_MERGEABILITY")

    def test_open_ready_not_merge_permission(self):
        r = fixture()
        r.update(state="open", merged=False, draft=False, mergeable=True)
        self.assertEqual(self.stage(r), "OPEN_NEEDS_NATIVE_GATES")

    def test_inconsistent(self):
        r = fixture()
        r.update(state="open", merged=True)
        self.assertEqual(self.stage(r), "INCONSISTENT")

    def test_closed_not_merged(self):
        r = fixture()
        r.update(merged=False)
        self.assertEqual(self.stage(r), "CLOSED_NOT_MERGED")

    def test_missing_merge_sha(self):
        r = fixture()
        r["merge_sha"] = None
        self.assertEqual(self.stage(r), "MERGED_MISSING_SHA")

    def test_missing_pr_ci(self):
        r = fixture()
        r["required_pr_jobs"] = []
        self.assertEqual(self.stage(r), "MERGED_CI_NOT_PROVEN")

    def test_dispatch_only_not_pr_ci(self):
        r = fixture()
        r["required_pr_jobs"][0]["event"] = "workflow_dispatch"
        self.assertEqual(self.stage(r), "MERGED_CI_NOT_PROVEN")

    def test_zero_steps_not_ci(self):
        r = fixture()
        r["required_pr_jobs"][0]["executed_test_steps"] = 0
        self.assertEqual(self.stage(r), "MERGED_CI_NOT_PROVEN")

    def test_boolean_steps_not_ci(self):
        r = fixture()
        r["required_pr_jobs"][0]["executed_test_steps"] = True
        self.assertEqual(self.stage(r), "MERGED_CI_NOT_PROVEN")

    def test_stale_test_head(self):
        r = fixture()
        r["required_pr_jobs"][0]["head"] = "d" * 40
        self.assertEqual(self.stage(r), "MERGED_CI_NOT_PROVEN")

    def test_main_blob_mismatch(self):
        r = fixture()
        r["changed_main_blobs"][0]["actual_sha"] = "d" * 40
        self.assertEqual(self.stage(r), "MERGED_MAIN_NOT_PROVEN")

    def test_no_main_blobs(self):
        r = fixture()
        r["changed_main_blobs"] = []
        self.assertEqual(self.stage(r), "MERGED_MAIN_NOT_PROVEN")

    def test_no_natural_consumer(self):
        r = fixture()
        del r["natural_consumer"]
        self.assertEqual(self.stage(r), "POST_FIX_OBSERVATION_CANDIDATE")

    def test_fabricated_delivery_does_not_pass(self):
        r = fixture()
        r["natural_consumer"]["delivered_source_id"] = "s2"
        self.assertEqual(self.stage(r), "PRODUCTION_EVIDENCE_MISMATCH")

    def test_manual_dispatch_not_natural(self):
        r = fixture()
        r["natural_consumer"]["event"] = "workflow_dispatch"
        self.assertEqual(self.stage(r), "PRODUCTION_EVIDENCE_MISMATCH")

    def test_bad_source_clock(self):
        r = fixture()
        r["natural_consumer"]["clock_eligible"] = False
        self.assertEqual(self.stage(r), "PRODUCTION_EVIDENCE_MISMATCH")

    def test_replay_dedup(self):
        a = fixture()
        b = copy.deepcopy(a)
        b["head_sha"] = "c" * 40
        report = replay([a, b])
        self.assertEqual(report["distinct_originals"], 1)
        self.assertEqual(len(report["duplicate_originals"]), 1)
        self.assertEqual(report["s1_verified_closures"], 0)

    def test_replay_20_synthetic_unverified(self):
        base = fixture()
        rows = []
        for n in range(1910, 1930):
            r = copy.deepcopy(base)
            r["original_pr"] = n
            rows.append(r)
        o = replay(rows)
        self.assertEqual(o["input_count"], 20)
        self.assertEqual(o["s1_automatic_merge_credit"], 0)
        self.assertEqual(o["stage_counts"], {"NATIVE_AUTHENTICATION_REQUIRED": 20})

    def test_non_object_rejected(self):
        self.assertEqual(self.stage(None), "INVALID_INPUT")

    def test_boolean_pr_rejected(self):
        r = fixture()
        r["original_pr"] = True
        self.assertEqual(self.stage(r), "INVALID_INPUT")

    def test_nonfinite_rejected(self):
        r = fixture()
        r["natural_consumer"]["run_url"] = float("nan")
        self.assertEqual(self.stage(r), "INVALID_INPUT")

    def test_max_batch(self):
        with self.assertRaisesRegex(ValueError, "BOUNDED_REPLAY"):
            replay([fixture()] * 201)

    def test_fingerprint_changes_on_external_release_gate(self):
        base = fixture()
        a = classify_snapshot(base)["fingerprint"]
        for key, value in (("mergeable", True), ("review_state", "APPROVED"),
                           ("rule_census", ["binding_review"]),
                           ("source_binding", "changed_source"),
                           ("active_editor_lease", "other_writer")):
            with self.subTest(key=key):
                changed = copy.deepcopy(base)
                changed[key] = value
                self.assertNotEqual(classify_snapshot(changed)["fingerprint"], a)

    def test_fingerprint_stable_and_changed_on_head(self):
        a = fixture()
        b = copy.deepcopy(a)
        self.assertEqual(classify_snapshot(a)["fingerprint"], classify_snapshot(b)["fingerprint"])
        b["head_sha"] = "c" * 40
        self.assertNotEqual(classify_snapshot(a)["fingerprint"], classify_snapshot(b)["fingerprint"])


if __name__ == "__main__":
    unittest.main()
