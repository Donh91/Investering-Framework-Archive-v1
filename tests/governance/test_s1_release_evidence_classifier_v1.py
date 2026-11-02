"""Negative controls for staged release evidence classification."""
import copy
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import (
    classify_release_evidence,
)


def fixture():
    head = "a" * 40
    return {
        "original_head": head,
        "required_pr_jobs": [{
            "head": head, "event": "pull_request",
            "status": "completed", "conclusion": "success",
            "executed_test_steps": 2,
        }],
        "merge_sha": "b" * 40,
        "main_sha": "c" * 40,
        "changed_main_blobs": [{
            "path": "scripts/governance/example.py",
            "expected_sha": "d" * 40, "actual_sha": "d" * 40,
        }],
        "natural_consumer": {
            "event": "natural", "run_url": "https://github.com/Donh91/example/actions/runs/1",
            "consumer_url": "https://github.com/Donh91/example",
            "source_id": "real-source", "delivered_source_id": "real-source",
            "clock_eligible": True,
        },
    }


class ReleaseEvidenceTests(unittest.TestCase):
    def stage(self, item):
        return classify_release_evidence(item)["stage"]

    def test_positive_is_still_unverified_without_external_auth(self):
        result = classify_release_evidence(fixture())
        self.assertEqual(result["stage"], "PROD_EVIDENCE_SUPPLIED_NEEDS_AUTHENTICATION")
        self.assertFalse(result["authorized"])
        self.assertFalse(result["externally_authenticated"])

    def test_no_head_fails(self):
        item = fixture()
        item["original_head"] = "a1"
        self.assertEqual(self.stage(item), "INVALID_INPUT")

    def test_green_but_skipped_is_not_ci(self):
        item = fixture()
        item["required_pr_jobs"][0]["executed_test_steps"] = 0
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_manual_only_does_not_count_as_pr_ci(self):
        item = fixture()
        item["required_pr_jobs"][0]["event"] = "workflow_dispatch"
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_old_head_run_not_accepted(self):
        item = fixture()
        item["required_pr_jobs"][0]["head"] = "f" * 40
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_boolean_step_count_not_accepted(self):
        item = fixture()
        item["required_pr_jobs"][0]["executed_test_steps"] = True
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_green_ci_not_merge(self):
        item = fixture()
        del item["merge_sha"]
        self.assertEqual(self.stage(item), "CI_ONLY")

    def test_main_blobs_required(self):
        item = fixture()
        item["changed_main_blobs"] = []
        self.assertEqual(self.stage(item), "MAIN_NOT_PROVEN")

    def test_main_blob_mismatch_fails(self):
        item = fixture()
        item["changed_main_blobs"][0]["actual_sha"] = "e" * 40
        self.assertEqual(self.stage(item), "MAIN_NOT_PROVEN")

    def test_no_natural_cycle_is_main_only(self):
        item = fixture()
        del item["natural_consumer"]
        self.assertEqual(self.stage(item), "MAIN_READBACK_SUPPLIED")

    def test_dispatch_cannot_pose_as_natural_cycle(self):
        item = fixture()
        item["natural_consumer"]["event"] = "workflow_dispatch"
        self.assertEqual(self.stage(item), "PRODUCTION_NOT_PROVEN")

    def test_source_clock_must_match_consumer(self):
        item = fixture()
        item["natural_consumer"]["delivered_source_id"] = "old-source"
        self.assertEqual(self.stage(item), "PRODUCTION_NOT_PROVEN")

    def test_expired_source_cannot_be_prod_verified(self):
        item = fixture()
        item["natural_consumer"]["clock_eligible"] = False
        self.assertEqual(self.stage(item), "PRODUCTION_NOT_PROVEN")


if __name__ == "__main__":
    unittest.main()
