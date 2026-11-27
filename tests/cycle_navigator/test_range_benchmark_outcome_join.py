import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from scripts.cycle_navigator.range_benchmark_outcome_join import join_diagnostics, _join


class OutcomeJoin(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 30, 12, tzinfo=timezone.utc)
        self.row = {"contract":"CN_FORWARD_RANGE_FREEZE_v2","asset":"BTC","window":"day_3_4",
                    "forecast_week":"2026-W48","generated_unix":1795427178,
                    "public_issue_number":35,"machine_issue_number":36,"status":"FROZEN_PROSPECTIVE",
                    "baseline_status":"FROZEN_RETAINED_SNAPSHOT"}

    def test_no_historical_backfill_or_duplicate(self):
        r = dict(self.row, baseline_status=None)
        with TemporaryDirectory() as tmp, patch("scripts.cycle_navigator.range_benchmark_outcome_join._join") as join:
            out = join_diagnostics(Path(tmp), [r], self.now)
            self.assertEqual(out["excluded"], {"NO_ORIGINAL_FROZEN_BENCHMARK":1})
            out = join_diagnostics(Path(tmp), [self.row,self.row], self.now)
            self.assertEqual(out["excluded"], {"DUPLICATE_FREEZE_IDENTITY":2})
            join.assert_not_called()
            self.assertEqual(out["scientifically_eligible_rows"],0)

    def test_unmatured_late_and_missing_sources(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp)
            with self.assertRaisesRegex(ValueError,"WEEK_NOT_MATURE"):
                _join(p,self.row,datetime(2026,11,27,12,tzinfo=timezone.utc))
            with self.assertRaisesRegex(ValueError,"NOT_FULL_WINDOW_PROSPECTIVE"):
                _join(p,dict(self.row,window="day_1_2"),self.now)
            out=join_diagnostics(p,[self.row],self.now)
            self.assertEqual(out["joined_rows"],0)
            self.assertEqual(out["scientifically_eligible_rows"],0)

    def test_diagnostic_result_never_admits(self):
        with TemporaryDirectory() as tmp, patch("scripts.cycle_navigator.range_benchmark_outcome_join._join",return_value={"CN":100}) as join:
            out=join_diagnostics(Path(tmp),[self.row],self.now)
            join.assert_called_once()
            self.assertEqual(out["joined_rows"],1)
            self.assertEqual(out["scientifically_eligible_rows"],0)
            self.assertFalse(out["independence_attested"])

if __name__=="__main__":
    unittest.main()
