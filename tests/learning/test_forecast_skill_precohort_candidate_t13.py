from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_study_v1_3_2 import validate_candidate_cohort_eligibility

UTC = timezone.utc


class T13PreCohortCandidateEligibilityTest(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 9, 5, tzinfo=UTC)
        self.end = datetime(2027, 5, 3, tzinfo=UTC)

    def test_precohort_candidate_rejected(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_CANDIDATE_OUTSIDE_COHORT"):
            validate_candidate_cohort_eligibility({"created_at_utc": "2026-09-04T23:59:59Z"}, self.start, self.end)

    def test_candidate_at_cohort_start_allowed(self):
        created = validate_candidate_cohort_eligibility({"created_at_utc": "2026-09-05T00:00:00Z"}, self.start, self.end)
        self.assertEqual(created, self.start)

    def test_candidate_at_cohort_end_rejected(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_CANDIDATE_OUTSIDE_COHORT"):
            validate_candidate_cohort_eligibility({"created_at_utc": "2027-05-03T00:00:00Z"}, self.start, self.end)


if __name__ == "__main__":
    unittest.main()
