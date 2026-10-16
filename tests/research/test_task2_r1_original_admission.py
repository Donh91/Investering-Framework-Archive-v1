import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.research.task2_r1_original_admission as admission
from scripts.research.task2_r1_original_admission import build, clock_status, original


class OriginalAdmissionTests(unittest.TestCase):
    def test_illegal_clocks_and_settlement_are_not_admitted(self):
        issue = "2026-10-13T12:00:00Z"
        self.assertEqual(clock_status("2026-10-13T11:00:00Z", "2026-10-13T12:00:01Z", issue), "NOT_ADMITTED_RETRIEVED_AFTER_ISSUE")
        self.assertEqual(clock_status("2026-10-13T12:00:01Z", None, issue), "NOT_ADMITTED_OBSERVATION_AFTER_ISSUE")
        self.assertEqual(clock_status(1791849600000, None, issue, funding=True), "SETTLEMENT_IS_NOT_QUOTE_OBSERVATION")
        self.assertEqual(clock_status("2026-10-13T11:00:00Z", None, issue), "RETRIEVAL_CLOCK_UNKNOWN")

    def test_wrong_original_git_blob_fails(self):
        with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
            original("098c50d36b222c4c8ffa179a5879d36a74194bc4", "04_MARKET_LEARNING/handlekompas/official/daily/2026/10/12/CMP-20261012-468da783e9d8.json", "0" * 40)

    def _run_with_tampered_frozen_census(self, modify):
        frozen = json.loads((admission.ROOT / admission.FORECAST_CENSUS).read_text())
        modify(frozen)
        with tempfile.TemporaryDirectory() as td:
            tampered_path = Path(td) / "tampered_frozen_forecast_census.json"
            tampered_path.write_text(json.dumps(frozen))
            with mock.patch.object(admission, "FORECAST_CENSUS", tampered_path):
                return build()

    def test_original_forecast_git_blob_must_match_separately_frozen_census(self):
        def modify(frozen):
            f = next(x for x in frozen["forecast_rows"]
                     if x["original_scoring_contract"] == "OFFICIAL_DAILY_COMPASS_SCORING_v3")
            f["forecast_git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
            self._run_with_tampered_frozen_census(modify)

    def test_original_outcome_presence_must_agree_across_two_censuses(self):
        def modify(frozen):
            f = next(x for x in frozen["forecast_rows"]
                     if x["original_scoring_contract"] == "OFFICIAL_DAILY_COMPASS_SCORING_v3"
                     and x["outcome_12h_presence_at_pinned_commit"] == "PRESENT")
            f["outcome_12h_presence_at_pinned_commit"] = "ABSENT_AT_SNAPSHOT"
        with self.assertRaisesRegex(ValueError, "Original outcome snapshot census mismatch"):
            self._run_with_tampered_frozen_census(modify)

    def test_original_forecast_roster_cannot_be_silently_shrunk(self):
        def modify(frozen):
            f = next(x for x in frozen["forecast_rows"]
                     if x["original_scoring_contract"] == "OFFICIAL_DAILY_COMPASS_SCORING_v3")
            frozen["forecast_rows"].remove(f)
        with self.assertRaisesRegex(ValueError, "Original forecast census or attempt roster mismatch"):
            self._run_with_tampered_frozen_census(modify)

    def test_frozen_parent_commit_must_equal_raw_source_era(self):
        def modify(frozen):
            frozen["pinned_public_main_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Original forecast census uses a different pinned Git revision"):
            self._run_with_tampered_frozen_census(modify)

    def test_original_git_object_reads_disable_local_replace_objects(self):
        with mock.patch.object(admission.subprocess, "run") as run:
            run.return_value.stdout = b"frozen"
            admission.git("show", "0123456789012345678901234567890123456789:some.json")
            self.assertEqual(run.call_args.args[0][:3], ["git", "--no-replace-objects", "show"])

    def test_info_edge_and_action_edge_have_distinct_nonpromoting_clocks(self):
        d = build()
        self.assertEqual(len(d["rows"]), 11)
        for row in d["rows"]:
            info = row["information_edge_gate"]
            action = row["investor_action_edge_gate"]
            self.assertEqual(info["status"], "NOT_ADMITTED")
            self.assertEqual(action["status"], "NOT_ADMITTED")
            self.assertFalse(info["user_delivery_required"])
            self.assertTrue(action["user_delivery_required"])
            self.assertNotIn("FIRST_USER_DELIVERY_UNVERIFIED", info["missing"])
            self.assertIn("FIRST_USER_DELIVERY_UNVERIFIED", action["missing"])
            self.assertIn("PROVIDER_FIRST_PUBLICATION_UNVERIFIED", info["missing"])
            self.assertIn("PROVIDER_FIRST_PUBLICATION_UNVERIFIED", action["missing"])
            self.assertFalse(action["portfolio_execution_authorized"])
            self.assertEqual(
                "ORIGINAL_OUTCOME_ABSENT_AT_FROZEN_SNAPSHOT" in info["missing"],
                row["original_outcome_status"] != "PRESENT",
            )
        self.assertEqual(sum(r["information_edge_gate"]["status"] == "ADMITTED" for r in d["rows"]), 0)
        self.assertEqual(sum(r["investor_action_edge_gate"]["status"] == "ADMITTED" for r in d["rows"]), 0)

    def _create_disposable_git_outcome(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "nested").mkdir()
        (root / "nested" / "outcome.json").write_text('{"status":"PRESENT"}')
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "frozen test fixture"], cwd=root, check=True)
        return root

    def test_original_missing_path_is_absent_only_after_successful_tree_traversal(self):
        root = self._create_disposable_git_outcome()
        with mock.patch.object(admission, "ROOT", root):
            self.assertEqual(admission.optional_original("HEAD", "nested/never.json"), (None, None))
            actual, blob = admission.optional_original("HEAD", "nested/outcome.json")
            self.assertEqual(actual["status"], "PRESENT")
            self.assertEqual(len(blob), 40)

    def test_missing_original_blob_is_operational_error_never_absence(self):
        root = self._create_disposable_git_outcome()
        blob = subprocess.check_output(["git", "rev-parse", "HEAD:nested/outcome.json"], cwd=root).decode().strip()
        (root / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
        with mock.patch.object(admission, "ROOT", root):
            with self.assertRaises(subprocess.CalledProcessError):
                admission.optional_original("HEAD", "nested/outcome.json")

    def test_missing_original_nested_tree_is_operational_error_never_absence(self):
        root = self._create_disposable_git_outcome()
        tree = subprocess.check_output(["git", "rev-parse", "HEAD:nested"], cwd=root).decode().strip()
        (root / ".git" / "objects" / tree[:2] / tree[2:]).unlink()
        with mock.patch.object(admission, "ROOT", root):
            with self.assertRaises(subprocess.CalledProcessError):
                admission.optional_original("HEAD", "nested/outcome.json")

    def test_failed_git_tree_lookup_must_propagate_not_become_missing(self):
        with mock.patch.object(admission, "git", side_effect=subprocess.CalledProcessError(128, ["git", "ls-tree"])):
            with self.assertRaises(subprocess.CalledProcessError):
                admission.optional_original("HEAD", "nested/outcome.json")

    def test_checkout_head_is_not_labeled_as_verified_main(self):
        rows = build()
        self.assertIn("generated_from_checkout_head_sha", rows)
        self.assertNotIn("generated_from_main_sha", rows)
        self.assertEqual(rows["checkout_ref_semantics"], "MAY_BE_PR_TEST_MERGE_NOT_VERIFIED_CURRENT_MAIN")
        self.assertTrue(all(
            x["checkout_outcome_status"] == "PRESENT_ON_CHECKOUT_HEAD" for x in rows["rows"]
        ))
        self.assertTrue(all("current_main_outcome_status" not in x for x in rows["rows"]))

    def test_original_forecast_packet_identity_must_be_consistent_across_all_bindings(self):
        # Simulate post-decode corruption after an exact Git blob check. Both
        # source *identity* and hash must be cross-checked against the
        # independent frozen packet, not trusted from the forecast alone.
        real_original = admission.original
        forecast_suffix = "/CMP-20261012-468da783e9d8.json"
        mutations = (
            ("universe_path", lambda f: f["evidence_snapshot"]["full_feature_universe_reference"].__setitem__("packet_path", "wrong.json")),
            ("universe_hash", lambda f: f["evidence_snapshot"]["full_feature_universe_reference"].__setitem__("packet_sha256", "0" * 64)),
            ("binding_path", lambda f: f["source_bindings"]["auto_market_state"].__setitem__("packet_path", "wrong.json")),
            ("binding_hash", lambda f: f["source_bindings"]["auto_market_state"].__setitem__("packet_sha256", "0" * 64)),
            ("selected_path", lambda f: f["evidence_snapshot"]["selected_features"][0].__setitem__("source_path", "wrong.json")),
        )
        for label, change in mutations:
            def forged_original(ref, path, expected_blob=None):
                obj, blob = real_original(ref, path, expected_blob)
                if path.endswith(forecast_suffix):
                    obj = json.loads(json.dumps(obj))
                    change(obj)
                return obj, blob
            with self.subTest(label=label):
                with mock.patch.object(admission, "original", side_effect=forged_original):
                    with self.assertRaisesRegex(ValueError, "packet binding mismatch|Selected feature packet path mismatch"):
                        build()

    def test_full_cohort_fails_closed_and_separates_later_outcomes(self):
        d = build()
        self.assertEqual(d["cohort"], {"original_attempts": 11, "original_outcomes_present": 9, "original_outcomes_absent": 2, "unique_source_blobs": 10, "unique_raw_capture_blobs": 7, "admitted": 0, "independent_market_event_families_certified": 0})
        self.assertEqual(sum(len(r["selected_feature_clocks"]) for r in d["rows"]), 264)
        self.assertEqual(sum(r["checkout_outcome_status"] == "PRESENT_ON_CHECKOUT_HEAD" for r in d["rows"]), 11)
        self.assertTrue(all(r["nominal_reference_to_target_seconds"] == 43200 for r in d["rows"] if r["original_outcome_status"] == "PRESENT"))
        self.assertTrue(all(r["admissibility"] == "NOT_ADMITTED" and r["first_user_delivery_at_utc"] is None for r in d["rows"]))
        self.assertTrue(all(r["collector_clocks"]["selected_CFGI_scores_match_capture"] and r["collector_clocks"]["selected_OKX_funding_quotes_match_capture"] for r in d["rows"]))
        serialized = json.dumps(d)
        self.assertNotIn('"value":', serialized)
        self.assertNotIn('"funding_rate":', serialized)
        self.assertNotIn('"price":', serialized)


if __name__ == "__main__":
    unittest.main()
