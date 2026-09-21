import unittest
from datetime import datetime, timezone
from scripts.framework_intelligence.weekly_forensics_replay_v1 import sunday_cutoffs, PATHS

class WeeklyForensicsReplayTests(unittest.TestCase):
    def test_bounded_sources(self):
        self.assertIn("pullback", PATHS); self.assertIn("compounding", PATHS)
    def test_cutoffs_are_weekly_and_bounded(self):
        xs=list(sunday_cutoffs(datetime(2026,9,21,12,tzinfo=timezone.utc),12))
        self.assertEqual(len(xs),12)
        self.assertTrue(all((xs[i]-xs[i+1]).days==7 for i in range(11)))
        self.assertTrue(all(x.weekday()==6 for x in xs))
if __name__=="__main__": unittest.main()
