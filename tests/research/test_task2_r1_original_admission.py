import json
import unittest

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

    def test_full_cohort_fails_closed_and_separates_later_outcomes(self):
        d = build()
        self.assertEqual(d["cohort"], {"original_attempts": 11, "original_outcomes_present": 9, "original_outcomes_absent": 2, "unique_source_blobs": 10, "unique_raw_capture_blobs": 7, "admitted": 0, "independent_market_event_families_certified": 0})
        self.assertEqual(sum(len(r["selected_feature_clocks"]) for r in d["rows"]), 264)
        self.assertEqual(sum(r["current_main_outcome_status"] == "PRESENT_ON_CURRENT_MAIN" for r in d["rows"]), 11)
        self.assertTrue(all(r["nominal_reference_to_target_seconds"] == 43200 for r in d["rows"] if r["original_outcome_status"] == "PRESENT"))
        self.assertTrue(all(r["admissibility"] == "NOT_ADMITTED" and r["first_user_delivery_at_utc"] is None for r in d["rows"]))
        self.assertTrue(all(r["collector_clocks"]["selected_CFGI_scores_match_capture"] and r["collector_clocks"]["selected_OKX_funding_quotes_match_capture"] for r in d["rows"]))
        serialized = json.dumps(d)
        self.assertNotIn('"value":', serialized)
        self.assertNotIn('"funding_rate":', serialized)
        self.assertNotIn('"price":', serialized)


if __name__ == "__main__":
    unittest.main()
