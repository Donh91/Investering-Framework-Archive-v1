"""All examples synthetic, never original price forecasts or market data."""
import copy
import unittest
from scripts.learning.forward_price_research_oracle import digest, check_issue, inspect_completed_window


def sample():
    d = {'contract': 'FORWARD_PRICE_RANGE_RESEARCH_ORACLE_v0_1',
         'forecast_id': 'SYNTHETIC-20261026-BTC-24H', 'asset': 'BTC', 'quote': 'USD',
         'venue': 'SYNTHETIC', 'issued_at_utc': '2026-10-26T06:00:00Z',
         'published_at_utc': '2026-10-26T06:01:00Z',
         'source_as_of_utc': '2026-10-26T05:00:00Z',
         'source_manifest_sha256': 'a'*64,
         'source_authority': 'NOT_INDEPENDENTLY_ADMITTED',
         'target_start_utc': '2026-10-26T07:00:00Z',
         'target_end_utc': '2026-10-26T09:00:00Z', 'anchor_usd': 100.0,
         'authority': {'research_only': True, 'issuer': False, 'canonical_score': False,
                       'public_release': False, 'portfolio_action': False},
         'candidates': [
             {'method': 'Q10_Q90', 'status': 'CANDIDATE', 'low_usd': 90., 'high_usd': 112., 'reason': None},
             {'method': 'ATR_CONTROL', 'status': 'CANDIDATE', 'low_usd': 99., 'high_usd': 101., 'reason': None},
             {'method': 'NO_EDGE', 'status': 'ABSTAIN', 'low_usd': None, 'high_usd': None, 'reason': 'NO_ELIGIBLE_SOURCE'}]}
    d['freeze_sha256'] = digest(d)
    return d


def observations():
    return [{'start_utc': '2026-10-26T07:00:00Z', 'end_utc': '2026-10-26T08:00:00Z',
             'first_known_at_utc': '2026-10-26T08:00:01Z', 'low_usd': 95., 'high_usd': 103.},
            {'start_utc': '2026-10-26T08:00:00Z', 'end_utc': '2026-10-26T09:00:00Z',
             'first_known_at_utc': '2026-10-26T09:00:01Z', 'low_usd': 94., 'high_usd': 107.}]


class ForwardPriceResearchOracleTests(unittest.TestCase):
    def test_positive_reference_oracle_joint_coverage_and_width(self):
        issue=sample(); before=copy.deepcopy(issue); bars=observations()
        result=inspect_completed_window(issue,bars,observed_as_of_utc='2026-10-26T09:01:00Z')
        self.assertEqual(result['status'],'MATURED_DESCRIPTIVE_ONLY')
        self.assertEqual(issue,before)
        self.assertFalse(result['eligible_for_canonical_score'])
        self.assertEqual(result['effective_independent_n'],0)
        q,atr,abstain=result['candidate_results']
        self.assertTrue(q['joint_contained'])
        self.assertEqual(q['width_pct'],22.)
        self.assertEqual(q['research_loss'],22.)
        self.assertFalse(atr['joint_contained'])
        self.assertEqual(atr['breach_pct'],11.)
        self.assertEqual(atr['research_loss'],24.)
        self.assertIsNone(abstain['joint_contained'])

    def test_same_freeze_detects_posthoc_tampering(self):
        issue=sample(); issue['candidates'][0]['high_usd']=115.
        with self.assertRaisesRegex(ValueError,'ORIGINAL_FREEZE_MUTATED'): check_issue(issue)

    def test_issue_target_source_clock_cannot_start_before_publication(self):
        for key,value in [('source_as_of_utc','2026-10-26T07:00:00Z'),
                          ('published_at_utc','2026-10-26T07:01:00Z'),
                          ('issued_at_utc','2026-10-26T07:30:00Z'),
                          ('target_end_utc','2026-10-26T06:00:00Z')]:
            with self.subTest(key=key):
                row=sample(); row[key]=value; row['freeze_sha256']=digest({k:v for k,v in row.items() if k!='freeze_sha256'})
                with self.assertRaisesRegex(ValueError,'CLOCK_INVALID'): check_issue(row)

    def test_reject_future_source_and_wrong_quote_even_with_rehash(self):
        for key,value in [('quote','USDT'),('source_authority','ADMITTED'),('asset','DOGE')]:
            with self.subTest(key=key):
                row=sample(); row[key]=value; row['freeze_sha256']=digest({k:v for k,v in row.items() if k!='freeze_sha256'})
                with self.assertRaises(ValueError): check_issue(row)

    def test_no_forged_public_issuer_portfolio_authority(self):
        for field in ('issuer','canonical_score','portfolio_action','public_release'):
            row=sample(); row['authority'][field]=True
            row['freeze_sha256']=digest({k:v for k,v in row.items() if k!='freeze_sha256'})
            with self.assertRaisesRegex(ValueError,'RESEARCH_ONLY_AUTHORITY_REQUIRED'): check_issue(row)

    def test_missing_and_immature_outcomes_are_not_hits(self):
        issue=sample()
        for observed_asof,rows,expected in [
            ('2026-10-26T08:00:01Z',observations(),'PENDING_MATURITY'),
            ('2026-10-26T09:01:00Z',[],'UNAVAILABLE_NO_COMPLETE_OBSERVATIONS'),
            ('2026-10-26T09:01:00Z',observations()[:1],'INELIGIBLE_INCOMPLETE_WINDOW')]:
            with self.subTest(expected=expected):
                actual=inspect_completed_window(issue,rows,observed_as_of_utc=observed_asof)
                self.assertEqual(actual['status'],expected)
                self.assertIsNone(actual['candidate_results'])

    def test_gap_duplicate_and_posttarget_bar_do_not_score(self):
        for mod in ('gap','duplicate','posttarget','futureknown'):
            with self.subTest(mod=mod):
                rows=observations()
                if mod=='gap': rows[1]['start_utc']='2026-10-26T08:01:00Z'
                if mod=='duplicate': rows[1]['start_utc']='2026-10-26T07:00:00Z'
                if mod=='posttarget': rows[1]['end_utc']='2026-10-26T10:00:00Z'
                if mod=='futureknown': rows[1]['first_known_at_utc']='2026-10-26T09:30:00Z'
                result=inspect_completed_window(sample(),rows,observed_as_of_utc='2026-10-26T09:01:00Z')
                self.assertEqual(result['status'],'INELIGIBLE_GAPPED_PARTIAL_OR_FUTURE_WINDOW')
                self.assertIsNone(result['candidate_results'])

    def test_straddling_issue_candle_rejected(self):
        rows=observations(); rows[0]['start_utc']='2026-10-26T06:00:00Z'
        result=inspect_completed_window(sample(),rows,observed_as_of_utc='2026-10-26T09:01:00Z')
        self.assertEqual(result['status'],'INELIGIBLE_GAPPED_PARTIAL_OR_FUTURE_WINDOW')

    def test_duplicate_methods_and_spoofed_expected_close_rejected(self):
        row=sample(); row['candidates'][1]['method']='Q10_Q90'
        row['freeze_sha256']=digest({k:v for k,v in row.items() if k!='freeze_sha256'})
        with self.assertRaisesRegex(ValueError,'DUPLICATE_OR_BLANK_METHOD'): check_issue(row)
        row=sample(); row['candidates'][0]['expected_close']=100.
        row['freeze_sha256']=digest({k:v for k,v in row.items() if k!='freeze_sha256'})
        with self.assertRaisesRegex(ValueError,'CANDIDATE_SCHEMA_INVALID'): check_issue(row)

    def test_abstaining_method_cannot_smuggle_prices(self):
        row=sample(); row['candidates'][-1]['low_usd']=95.
        row['freeze_sha256']=digest({k:v for k,v in row.items() if k!='freeze_sha256'})
        with self.assertRaisesRegex(ValueError,'ABSTENTION_MUST_HAVE_NULL_PRICES'): check_issue(row)

    def test_invalid_observation_values_rejected(self):
        for val in (float('nan'),float('inf'),-1, True):
            with self.subTest(val=val):
                rows=observations(); rows[0]['low_usd']=val
                with self.assertRaises(ValueError):
                    inspect_completed_window(sample(), rows, observed_as_of_utc='2026-10-26T09:01:00Z')

    def test_malformed_extra_outcome_or_method_id_rejected(self):
        row=sample(); row['candidates'][0]['method']=''
        row['freeze_sha256']=digest({k:v for k,v in row.items() if k!='freeze_sha256'})
        with self.assertRaises(ValueError): check_issue(row)
        rows=observations(); rows[0]['future_close_usd']=100.
        with self.assertRaisesRegex(ValueError,'OBSERVATION_SCHEMA_INVALID'):
            inspect_completed_window(sample(), rows, observed_as_of_utc='2026-10-26T09:01:00Z')

    def test_guard_removal_mutation_is_caught_by_freeze_test(self):
        from unittest.mock import patch
        from scripts.learning import forward_price_research_oracle as mod
        original=mod.digest
        with patch.object(mod, 'digest', return_value='a'*64):
            with self.assertRaisesRegex(ValueError,'ORIGINAL_FREEZE_MUTATED'):
                check_issue(sample())
        self.assertEqual(mod.digest,original)

if __name__=='__main__': unittest.main()
