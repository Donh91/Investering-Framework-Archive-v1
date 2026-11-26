"""Research-only forecast allocation policy probe; no runtime wiring or market scoring."""
from collections import Counter
from dataclasses import dataclass
import json
import unittest

@dataclass(frozen=True)
class Candidate:
    id: str
    kind: str
    eligible: bool


def allocate(candidates, prior_pairs, window, cap):
    """Pure selection over already validated eligibility and PIT forecast identities.

    prior_pairs: unique (candidate ID, causal window ID) allocations, no outcomes.
    Caller must supply complete history available at cutoff and a stable roster.
    No clock authentication, production mutation or admission is performed here.
    """
    if not isinstance(cap, int) or isinstance(cap, bool) or cap < 0 or not window:
        raise ValueError('INVALID_CAP_OR_WINDOW')
    rows = list(candidates)
    if any(not x.id or type(x.eligible) is not bool for x in rows) or len({x.id for x in rows}) != len(rows):
        raise ValueError('INVALID_OR_DUPLICATE_CANDIDATE')
    pairs = set()
    for cid, wid in prior_pairs:
        if not cid or not wid:
            raise ValueError('INVALID_HISTORY_ID')
        pairs.add((cid, wid))  # exact duplicate identities do not inflate exposure
    occupied = {cid for cid, wid in pairs if wid == window}
    if len(occupied) > cap:
        raise ValueError('EXISTING_WINDOW_OVER_CAP')
    count = Counter(cid for cid, wid in pairs if wid != window)
    ranked = sorted((x for x in rows if x.eligible and x.id not in occupied),
                    key=lambda x: (x.kind != 'FORECAST_TEST', count[x.id], x.id))
    return [x.id for x in ranked[:cap-len(occupied)]]


def simulation():
    rows = [Candidate(str(i), 'FORECAST_TEST', True) for i in range(8)]
    fixed, fair = Counter(), set()
    for tick in range(10):
        fixed.update(x.id for x in rows[:5])
        wid = str(tick)
        fair.update((cid, wid) for cid in allocate(rows, fair, wid, 5))
    counts = Counter(cid for cid, _ in fair)
    # Synthetic replay: old invocation cap does not account for prior same-window writes.
    old_first = [x.id for x in rows[:5]]
    old_second = [x.id for x in rows if x.id not in old_first][:5]
    new_first = allocate(rows, [], 'retry', 5)
    new_second = allocate(rows, [(x, 'retry') for x in new_first], 'retry', 5)
    return {'evidence': 'SYNTHETIC_ONLY', 'fixed': [fixed[x.id] for x in rows],
            'least_served': [counts[x.id] for x in rows], 'retry_old_unique': len(old_first+old_second),
            'retry_new_unique': len(new_first+new_second)}


class Tests(unittest.TestCase):
    def setUp(self):
        self.rows = [Candidate(str(i), 'FORECAST_TEST', True) for i in range(8)]
    def test_no_starvation_equal_kind(self):
        r = simulation(); self.assertEqual(r['fixed'], [10]*5+[0]*3); self.assertLessEqual(max(r['least_served'])-min(r['least_served']),1)
    def test_same_window_cap(self):
        r = simulation(); self.assertEqual(r['retry_old_unique'],8); self.assertEqual(r['retry_new_unique'],5)
    def test_partial_resume(self):
        self.assertEqual(allocate(self.rows,[('0','w'),('1','w')],'w',5),['2','3','4'])
    def test_kind_priority(self):
        self.assertEqual(allocate([Candidate('a','SENSOR_COMBINATION',True),Candidate('b','FORECAST_TEST',True)],[('b','old')],'w',1),['b'])
    def test_ineligible(self):
        self.assertEqual(allocate([Candidate('a','FORECAST_TEST',False),Candidate('b','FORECAST_TEST',True)],[],'w',1),['b'])
    def test_history_dedup(self):
        self.assertEqual(allocate(self.rows,[('0','old')]*10+[('1','old'),('1','old2')],'w',8),['2','3','4','5','6','7','0','1'])
    def test_occupied_outside_roster(self):
        self.assertEqual(allocate(self.rows,[('other','w')],'w',2),['0'])
    def test_overcap_fails(self):
        with self.assertRaises(ValueError): allocate(self.rows,[('0','w'),('1','w')],'w',1)
    def test_duplicate_candidates_fail(self):
        with self.assertRaises(ValueError): allocate(self.rows+[self.rows[0]],[],'w',5)
    def test_bad_cap(self):
        for cap in (-1,True,2.5):
            with self.assertRaises(ValueError): allocate(self.rows,[],'w',cap)
    def test_order_invariance(self):
        self.assertEqual(allocate(self.rows,[],'w',5),allocate(list(reversed(self.rows)),[],'w',5))
    def test_zero(self):
        self.assertEqual(allocate(self.rows,[],'w',0),[])
    def test_prior_exposure_not_result(self):
        self.assertEqual(allocate(self.rows,[('0','old'),('1','old')],'w',2),['2','3'])

if __name__ == '__main__':
    print(json.dumps(simulation(),indent=2))
    unittest.main()
