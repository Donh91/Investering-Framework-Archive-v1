import copy
import hashlib
import unittest
from pathlib import Path
from scripts.cycle_navigator.weekly_shadow_analysis_v1 import build_weekly_analysis, ordered_sequence
ROOT=Path(__file__).resolve().parents[2]

class RealWeek(unittest.TestCase):
    def setUp(self):
        self.raw=(ROOT/'03_DAILY_CAPTURE_LOGS/weekly/2026/W47.json').read_bytes()
        self.sha=hashlib.sha256(self.raw).hexdigest()
    def test_source_grounded_partial_analysis(self):
        a=build_weekly_analysis(self.raw,self.sha,'2026-11-23T09:46:18Z',2026,47)
        self.assertEqual(a['settled_week']['btc']['direction'],'DOWN')
        self.assertEqual(a['settled_week']['eth']['direction'],'DOWN')
        self.assertEqual(a['settled_week']['ethbtc']['direction'],'UP')
        self.assertFalse(a['operational_translation']['portfolio_action'])
        self.assertFalse(a['independent_first_known_verified'])
    def test_hash_and_clock_and_week_rejected(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_DIGEST_MISMATCH'):build_weekly_analysis(self.raw,'0'*64,'2026-11-23T09:46:18Z',2026,47)
        with self.assertRaisesRegex(ValueError,'SOURCE_NOT_AVAILABLE_AT_FREEZE'):build_weekly_analysis(self.raw,self.sha,'2026-11-23T09:00:00Z',2026,47)
        with self.assertRaisesRegex(ValueError,'SOURCE_WEEK_OR_CONTRACT_MISMATCH'):build_weekly_analysis(self.raw,self.sha,'2026-11-23T09:46:18Z',2026,46)

class Sequence(unittest.TestCase):
    def events(self):
        return [dict(family=family,admission='ADMITTED',state=True,source_sha256=hashlib.sha256(b'fixture').hexdigest(),observed_at_utc=f'2026-11-23T0{i}:00:00Z',available_at_utc=f'2026-11-23T0{i}:01:00Z') for i,family in enumerate(('ethbtc','btc_dominance','breadth'),1)]
    def test_order_and_timing(self):
        events=self.events();freeze='2026-11-23T04:00:00Z'; sources={hashlib.sha256(b'fixture').hexdigest():b'fixture'}
        self.assertEqual(ordered_sequence('leadership_transmission',events,freeze,sources)['status'],'ORDERED_CLAIMS_ONLY')
        for mutation in ('late','equal','unknown','unverified'):
            e=copy.deepcopy(events)
            if mutation=='late': e[2]['available_at_utc']='2026-11-23T05:00:00Z'
            if mutation=='equal': e[2]['observed_at_utc']=e[1]['observed_at_utc']
            if mutation=='unknown': e[2]['state']=None
            if mutation=='unverified': e[2]['source_sha256']='0'*64
            self.assertEqual(ordered_sequence('leadership_transmission',e,freeze,sources)['status'],'UNKNOWN',mutation)
