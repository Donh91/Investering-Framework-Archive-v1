"""All examples synthetic, never original price forecasts or market data."""
import copy
import unittest
from scripts.learning.forward_price_research_oracle import digest, check_issue, inspect_completed_window, inspect_native_usdt_candidate, NATIVE_COMPARISON_CONTRACT, NATIVE_OBSERVATION_CONTRACT


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

    def test_extreme_numeric_inputs_fail_closed_not_overflow_or_inf_output(self):
        issue=sample(); issue['anchor_usd']=10**1000
        issue['freeze_sha256']=digest({k:v for k,v in issue.items() if k!='freeze_sha256'})
        with self.assertRaisesRegex(ValueError,'POSITIVE_FINITE_PRICE_REQUIRED'): check_issue(issue)
        issue=sample(); issue['anchor_usd']=1e-308
        issue['candidates'][0].update(low_usd=1e308,high_usd=1.1e308)
        issue['freeze_sha256']=digest({k:v for k,v in issue.items() if k!='freeze_sha256'})
        with self.assertRaisesRegex(ValueError,'RESEARCH_DIAGNOSTIC_NONFINITE'):
            inspect_completed_window(issue,observations(),observed_as_of_utc='2026-10-26T09:01:00Z')

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


class NativeUsdtMatchedWindowTests(unittest.TestCase):
    def fixture(self,h=30,n=720):
        from datetime import datetime,timedelta
        from scripts.learning.forward_price_shadow import build_native_usdt_shadow
        from tests.learning.test_forward_price_native_usdt_shadow import fixture
        payload=fixture(n=n);candidate=build_native_usdt_shadow(payload)
        issued=datetime.fromisoformat(payload['issued_at_utc'].replace('Z','+00:00'))
        delivery=issued+timedelta(minutes=1)
        start=delivery.replace(hour=0,minute=0,second=0)+timedelta(days=1)
        end=start+timedelta(days=h)
        stamp=lambda x:x.strftime('%Y-%m-%dT%H:%M:%SZ')
        f={'contract':NATIVE_COMPARISON_CONTRACT,'asset':'BTC','quote':'USDT','venue':'BINANCE_SPOT_BTCUSDT',
           'authority':{'research_only':True,'issuer':False,'canonical_score':False,'public_release':False,'portfolio_action':False},
           'horizon_days':h,'candidate_sha256':candidate['candidate_sha256'],
           'source_manifest_sha256':payload['source_manifest_sha256'],'source_rows_sha256':payload['source_rows_sha256'],
           'issued_at_utc':payload['issued_at_utc'],'delivery_clock_claim_utc':stamp(delivery),
           'target_start_utc':stamp(start),'target_end_utc':stamp(end)}
        f['freeze_sha256']=digest(f)
        anchor=candidate['anchor_usdt'];rows=[]
        for i in range(h):
            left=start+timedelta(days=i);right=left+timedelta(days=1)
            rows.append({'start_utc':stamp(left),'end_utc':stamp(right),
                         'first_known_at_utc':stamp(right+timedelta(seconds=1)),
                         'low_usdt':anchor*.99,'high_usdt':anchor*1.01,'close_usdt':anchor})
        o={'contract':NATIVE_OBSERVATION_CONTRACT,'asset':'BTC','quote':'USDT','venue':'BINANCE_SPOT_BTCUSDT',
           'freeze_sha256':f['freeze_sha256'],'source_manifest_sha256':'b'*64,'rows':rows,'rows_sha256':digest(rows)}
        return payload,f,o,stamp(end+timedelta(minutes=1))

    def seal(self,f,o):
        f.pop('freeze_sha256',None);f['freeze_sha256']=digest(f)
        o['freeze_sha256']=f['freeze_sha256'];o['rows_sha256']=digest(o['rows'])

    def test_native_original_builder_to_oracle_all_six_horizons(self):
        for h in (1,7,14,21,30,56):
            with self.subTest(h=h):
                p,f,o,asof=self.fixture(h)
                r=inspect_native_usdt_candidate(p,f,o,observed_as_of_utc=asof)
                self.assertEqual(r['status'],'MATURED_DESCRIPTIVE_ONLY')
                self.assertEqual(r['quote'],'USDT')
                self.assertEqual(r['horizon_days'],h)
                self.assertEqual(r['anchor_to_target_start_hours'],24.)
                self.assertEqual(len(r['candidate_results']),2)
                self.assertTrue(all(v['width_pct']>0 for v in r['candidate_results']))
                self.assertFalse(r['forecast_issued'])
                self.assertFalse(r['first_delivery_verified'])
                self.assertFalse(r['source_custody_verified'])
                self.assertFalse(r['eligible_for_canonical_score'])
                self.assertIsNone(r['coverage_probability'])

    def test_56d_insufficient_training_history_remains_abstain(self):
        p,f,o,asof=self.fixture(56,365)
        r=inspect_native_usdt_candidate(p,f,o,observed_as_of_utc=asof)
        self.assertTrue(all(v['status']=='ABSTAIN' and v['research_loss'] is None for v in r['candidate_results']))

    def test_missing_future_gap_and_partial_outcome_never_score(self):
        p,f,o,asof=self.fixture(14)
        self.assertEqual(inspect_native_usdt_candidate(p,f,o,observed_as_of_utc=f['target_start_utc'])['status'],'PENDING_MATURITY')
        self.assertEqual(inspect_native_usdt_candidate(p,f,None,observed_as_of_utc=asof)['status'],'UNAVAILABLE_NO_COMPLETE_OBSERVATIONS')
        short=copy.deepcopy(o);short['rows'].pop();short['rows_sha256']=digest(short['rows'])
        self.assertEqual(inspect_native_usdt_candidate(p,f,short,observed_as_of_utc=asof)['status'],'INELIGIBLE_INCOMPLETE_WINDOW')
        for field,value in [('start_utc',o['rows'][0]['start_utc']),('first_known_at_utc','2099-01-01T00:00:00Z')]:
            bad=copy.deepcopy(o);bad['rows'][1][field]=value;bad['rows_sha256']=digest(bad['rows'])
            self.assertIsNone(inspect_native_usdt_candidate(p,f,bad,observed_as_of_utc=asof)['candidate_results'])

    def test_resealed_quote_digest_authority_and_target_attacks(self):
        p,f,o,asof=self.fixture(14)
        for key,value in [('quote','USD'),('venue','BINANCE_FUTURES_BTCUSDT'),('horizon_days',True),
                          ('candidate_sha256','0'*64),('source_rows_sha256','0'*64),
                          ('target_start_utc',f['issued_at_utc']),('target_end_utc',f['target_start_utc'])]:
            with self.subTest(key=key):
                a,b=copy.deepcopy(f),copy.deepcopy(o);a[key]=value;self.seal(a,b)
                with self.assertRaises(ValueError):inspect_native_usdt_candidate(p,a,b,observed_as_of_utc=asof)
        a,b=copy.deepcopy(f),copy.deepcopy(o);a['authority']['issuer']=True;self.seal(a,b)
        with self.assertRaises(ValueError):inspect_native_usdt_candidate(p,a,b,observed_as_of_utc=asof)
        for key,value in [('quote','USD'),('venue','BINANCE_FUTURES_BTCUSDT'),('rows_sha256','0'*64),('freeze_sha256','0'*64)]:
            b=copy.deepcopy(o);b[key]=value
            with self.assertRaises(ValueError):inspect_native_usdt_candidate(p,f,b,observed_as_of_utc=asof)
        b=copy.deepcopy(o);b['rows'][0]['close_usdt']=b['rows'][0]['high_usdt']*2;b['rows_sha256']=digest(b['rows'])
        with self.assertRaises(ValueError):inspect_native_usdt_candidate(p,f,b,observed_as_of_utc=asof)
