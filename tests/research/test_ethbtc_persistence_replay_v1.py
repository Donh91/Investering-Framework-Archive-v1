import unittest
from datetime import datetime, timedelta, timezone
from scripts.research.ethbtc_persistence_replay_v1 import replay, verify_window_inputs, METHOD, sequence_census

START = datetime(2026, 11, 1, tzinfo=timezone.utc)
H = timedelta(hours=1)
CUTOFF = START+169*H


def window(n=7, side=0.031):
    return [{"ts": START+i*H, "available": START+(i+1)*H,
             "ethbtc": side if i >= 168-n else 0.029} for i in range(168)]


def inputs(w):
    r = replay(w, CUTOFF)
    return dict(lookback_rows=168, sample_count=168, continuous_hours=168,
                window_start_utc=r['window_start_utc'], window_end_utc=r['window_end_utc'],
                consecutive_same_side=r['consecutive_same_side'], method=METHOD)


class ReplayTests(unittest.TestCase):
    def test_seven_hours_and_crossing(self):
        r = replay(window(), CUTOFF)
        self.assertEqual(r['consecutive_same_side'], 7)
        self.assertEqual(r['first_above_bar_utc'], (START+161*H).isoformat().replace('+00:00','Z'))
        self.assertFalse(r['left_censored'])
    def test_same_latest_different_persistence(self):
        self.assertNotEqual(replay(window(7), CUTOFF)['consecutive_same_side'], replay(window(11), CUTOFF)['consecutive_same_side'])
    def test_censored(self):
        r = replay(window(168), CUTOFF)
        self.assertTrue(r['left_censored'])
        self.assertIsNone(r['first_above_bar_utc'])
        self.assertEqual(r['consecutive_same_side'],168)
    def test_below_and_equal(self):
        self.assertEqual(replay(window(168,0.029), CUTOFF)['side'],'BELOW')
        self.assertEqual(replay(window(7,0.03), CUTOFF)['side'],'AT')
    def test_no_authority_or_invented_confirmation(self):
        r = replay(window(), CUTOFF)
        self.assertIsNone(r['stable_confirmation_utc'])
        self.assertIsNone(r['independent_first_known_utc'])
        self.assertFalse(r['scientific_pit_eligible'])
        self.assertFalse(r['forecast_authority'])
    def test_source_clock_not_bar_clock(self):
        w = window()
        w[-7]['available'] += H
        r = replay(w,CUTOFF)
        self.assertNotEqual(r['first_above_source_window_end_utc'],r['first_above_bar_utc'])
    def test_missing_duplicate_and_disordered(self):
        w = window()
        for invalid in [w[:-1], w[:5]+[w[4]]+w[6:], w[:5]+[w[6],w[5]]+w[7:]]:
            with self.subTest(invalid=len(invalid)), self.assertRaises(ValueError):
                replay(invalid,CUTOFF)
    def test_future_or_unsettled_source(self):
        for a in [CUTOFF+H, window()[-1]['ts']]:
            w=window(); w[-1]['available']=a
            with self.assertRaises(ValueError): replay(w,CUTOFF)
    def test_nonfinite_and_nonpositive(self):
        for value in [float('nan'),float('inf'),0,-1,True,'0.031']:
            w=window(); w[0]['ethbtc']=value
            with self.subTest(value=value), self.assertRaises(ValueError): replay(w,CUTOFF)
    def test_forged_duration(self):
        w=window(); p=inputs(w); p['consecutive_same_side']=168
        with self.assertRaisesRegex(ValueError,'consecutive_same_side'): verify_window_inputs(w,CUTOFF,p)
    def test_forged_type(self):
        w=window(1); p=inputs(w); p['consecutive_same_side']=True
        with self.assertRaisesRegex(ValueError,'consecutive_same_side'): verify_window_inputs(w,CUTOFF,p)
    def test_missing_and_mutated_metadata(self):
        w=window()
        for key in inputs(w):
            p=inputs(w); p.pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError): verify_window_inputs(w,CUTOFF,p)
    def test_valid(self):
        w=window(); self.assertEqual(verify_window_inputs(w,CUTOFF,inputs(w))['consecutive_same_side'],7)


class SequenceCensusTests(unittest.TestCase):
    def observation(self, i, btcd="MIXED_PATH", breadth="NON_BROAD_MAJORITY",
                    day=4, run=None, episode="2026-11-04T15:00:00Z", side="ABOVE"):
        return {"observation_utc": f"2026-11-05T{i:02d}:00:00Z",
                "persistence": {"side": side, "first_above_bar_utc": episode,
                                "consecutive_same_side": 8+i},
                "btcd_state": btcd, "btcd_settled_dates": [f"2026-11-{day:02d}"],
                "breadth_state": breadth, "breadth_run_id": run or str(i),
                "breadth_capture_utc": f"2026-11-05T{i:02d}:00:00Z"}

    def test_repeated_observations_not_independent_episodes(self):
        r = sequence_census([self.observation(1), self.observation(2)])
        self.assertEqual(r["above_observation_n"], 2)
        self.assertEqual(r["observed_episode_n"], 1)
        self.assertEqual(r["ordered_proxy_episode_n"], 0)
        self.assertIsNone(r["episodes"][0]["stable_confirmation_utc"])

    def test_ordered_proxy_requires_distinct_nonoverlapping_transitions(self):
        rows = [self.observation(1), self.observation(2, "FALLING_PATH", day=5),
                self.observation(3, "FALLING_PATH", "BROAD_MAJORITY", day=5)]
        r = sequence_census(rows)
        self.assertEqual(r["ordered_proxy_episode_n"], 1)
        self.assertEqual(r, sequence_census(list(reversed(rows))))
        self.assertFalse(r["original_sequence_equivalence"])
        self.assertFalse(r["scientific_pit_eligible"])
        self.assertFalse(r["forecast_authority"])
        self.assertEqual(r["sequence_2"]["status"], "BLOCKED_MISSING_SOURCE")
        self.assertEqual(r["sequence_3"]["status"], "BLOCKED_MISSING_SOURCE")

    def test_simultaneous_change_not_ordered(self):
        r = sequence_census([self.observation(1),
            self.observation(2, "FALLING_PATH", "BROAD_MAJORITY", day=5)])
        self.assertEqual(r["ordered_proxy_episode_n"], 0)

    def test_censored_start_no_episode(self):
        r = sequence_census([self.observation(1, episode=None)])
        self.assertEqual(r["unidentified_censored_above_n"], 1)
        self.assertEqual(r["observed_episode_n"], 0)

    def test_conflicting_same_source_and_duplicate_clock_fail_closed(self):
        a = self.observation(1)
        for rows in ([a, a], [a, self.observation(2, "FALLING_PATH")],
                     [a, self.observation(2, breadth="BROAD_MAJORITY", run="1")]):
            with self.assertRaises(ValueError):
                sequence_census(rows)

    def test_path_loss_resets_downstream_proxy(self):
        rows = [self.observation(1), self.observation(2, "FALLING_PATH", day=5),
                self.observation(3, "FALLING_PATH", "BROAD_MAJORITY", day=5),
                self.observation(4, "RISING_RECLAIM", "BROAD_MAJORITY", day=6)]
        result = sequence_census(rows)
        self.assertEqual(result["ordered_proxy_episode_n"], 0)
        self.assertEqual(result["ever_ordered_proxy_episode_n"], 1)
        self.assertEqual(result["active_ordered_proxy_episode_n"], 0)
        self.assertEqual(result["episodes"][0]["first_ordered_proxy_observation_utc"], rows[2]["observation_utc"])

    def test_closed_episode_is_not_active_and_history_is_preserved(self):
        rows = [self.observation(1), self.observation(2, "FALLING_PATH", day=5),
                self.observation(3, "FALLING_PATH", "BROAD_MAJORITY", day=5),
                self.observation(4, "FALLING_PATH", "BROAD_MAJORITY", day=5, episode=None, side="BELOW")]
        result = sequence_census(rows)
        self.assertEqual(result["ever_ordered_proxy_episode_n"], 1)
        self.assertEqual(result["active_ordered_proxy_episode_n"], 0)
        self.assertFalse(result["episodes"][0]["active"])
        self.assertEqual(result["episodes"][0]["end_observation_utc"], rows[-1]["observation_utc"])

if __name__=='__main__': unittest.main()
