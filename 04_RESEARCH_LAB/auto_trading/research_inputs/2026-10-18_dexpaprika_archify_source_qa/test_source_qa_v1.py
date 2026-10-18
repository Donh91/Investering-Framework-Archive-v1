"""Synthetic negative controls; no private or live market data in tests."""
import copy
import random
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('source_qa_v1', Path(__file__).with_name('source_qa_v1.py'))
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)

SOL = 'So11111111111111111111111111111111111111112'
USDC = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
POOL = 'Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE'
T = '2026-10-18T03:38:30Z'


def sources():
    dp = {'chain': 'solana', 'id': POOL, 'base_token_id': SOL, 'quote_token_id': USDC,
          'liquidity_usd': 10000, 'volume_usd_24h': 5000,
          'created_at': '2023-06-30T06:20:58Z', 'price_time': '2026-10-18T03:38:20Z'}
    ds = {'pair': {'chainId': 'solana', 'pairAddress': POOL,
                   'baseToken': {'address': SOL}, 'quoteToken': {'address': USDC},
                   'liquidity': {'usd': 10003}, 'volume': {'h24': 4999},
                   'pairCreatedAt': 1688106058000}}
    gt = {'data': {'id': 'solana_' + POOL,
                   'attributes': {'address': POOL, 'reserve_in_usd': '10002.9',
                                  'volume_usd': {'h24': '5010'},
                                  'pool_created_at': '2023-06-30T06:20:58Z'},
                   'relationships': {'base_token': {'data': {'id': 'solana_' + SOL}},
                                     'quote_token': {'data': {'id': 'solana_' + USDC}}}}}
    return [{'provider': 'DEXPAPRIKA', 'captured_at_utc': T, 'payload': dp},
            {'provider': 'DEXSCREENER', 'captured_at_utc': T, 'payload': ds},
            {'provider': 'GECKOTERMINAL', 'captured_at_utc': T, 'payload': gt}]


def run(s):
    return qa.evaluate_case({'case_id': 'SYNTHETIC_SOL', 'observations': s})


class Tests(unittest.TestCase):
    def test_positive_three_sources(self):
        x = run(sources())
        self.assertEqual(x['source_qa_state'], 'COMPARABLE_AS_AGGREGATORS_ONLY')
        self.assertFalse(x['independent_onchain_validation'])
        self.assertFalse(x['sellability_proven'])
        self.assertIsNone(x['trade_signal'])
        self.assertNotIn('POOL_OR_TOKEN_IDENTITY_CONFLICT', x['comparison_flags'])

    def test_missing_liquidity_not_zero(self):
        s = sources()
        s[1]['payload']['pair'].pop('liquidity')
        v = run(s)
        self.assertIn('LIQUIDITY_UNKNOWN', v['provider_observations'][1]['flags'])
        self.assertNotIn('LIQUIDITY_ZERO', v['provider_observations'][1]['flags'])

    def test_explicit_zero_distinct(self):
        s = sources()
        s[0]['payload']['liquidity_usd'] = 0
        v = run(s)
        self.assertIn('LIQUIDITY_ZERO', v['provider_observations'][0]['flags'])
        self.assertFalse(v['sellability_proven'])

    def test_nan_negative_bool_quarantine(self):
        for invalid in [float('nan'), -4, True, 'NaN', 'bad']:
            with self.subTest(invalid=invalid):
                s = sources()
                s[0]['payload']['liquidity_usd'] = invalid
                v = run(s)
                self.assertEqual(v['source_qa_state'], 'INVALID')
                self.assertIn('LIQUIDITY_INVALID', v['provider_observations'][0]['flags'])

    def test_reversed_tokens_conflict(self):
        s = sources()
        pair = s[1]['payload']['pair']
        pair['baseToken']['address'], pair['quoteToken']['address'] = USDC, SOL
        self.assertIn('POOL_OR_TOKEN_IDENTITY_CONFLICT', run(s)['comparison_flags'])

    def test_solana_case_sensitive_identity(self):
        s = sources()
        s[1]['payload']['pair']['baseToken']['address'] = SOL.lower()
        self.assertIn('POOL_OR_TOKEN_IDENTITY_CONFLICT', run(s)['comparison_flags'])

    def test_pool_birth_disagreement(self):
        s = sources()
        s[2]['payload']['data']['attributes']['pool_created_at'] = '2023-07-05T14:34:02Z'
        x = run(s)
        self.assertIn('POOL_CREATION_CLAIM_CONFLICT', x['comparison_flags'])
        self.assertEqual(x['source_qa_state'], 'CONFLICT')

    def test_unavailable_does_not_become_agreement(self):
        s = sources()
        s[1]['http_status'] = 429
        x = run(s)
        self.assertIn('SOURCE_COVERAGE_PARTIAL', x['comparison_flags'])
        self.assertEqual(x['source_qa_state'], 'INCOMPLETE')

    def test_stale_provider_time(self):
        s = sources()
        s[0]['payload']['price_time'] = '2026-10-18T03:00:00Z'
        v = run(s)
        self.assertEqual(v['source_qa_state'], 'STALE')
        self.assertIn('SOURCE_STALE', v['provider_observations'][0]['flags'])
        self.assertIn('SOURCE_FRESHNESS_UNKNOWN', v['provider_observations'][1]['flags'])

    def test_future_time(self):
        s = sources()
        s[0]['payload']['price_time'] = '2026-10-19T03:00:00Z'
        self.assertEqual(run(s)['source_qa_state'], 'INVALID')

    def test_empty_or_ambiguous_failure(self):
        s = sources()
        s[1]['payload'] = {'pairs': [{}, {}]}
        self.assertIn('SOURCE_COVERAGE_PARTIAL', run(s)['comparison_flags'])

    def test_same_hash_key_order(self):
        data = sources()[0]['payload']
        self.assertEqual(qa._digest(data), qa._digest(dict(reversed(list(data.items())))))

    def test_no_provider_numeric_leak(self):
        x = run(sources())
        txt = str(x)
        self.assertNotIn(POOL, txt)
        self.assertNotIn(SOL, txt)
        self.assertNotIn('10000', txt)

    def test_unknown_provider_rejected(self):
        s = sources()
        s[0]['provider'] = 'FAKE'
        self.assertRaises(ValueError, run, s)

    def test_duplicate_provider_rejected(self):
        s = sources()
        s.append(copy.deepcopy(s[0]))
        self.assertRaises(ValueError, run, s)

    def test_invalid_capture_time(self):
        s = sources()
        s[0]['captured_at_utc'] = '2026-10-18T03:38:30'
        self.assertIn('CAPTURE_TIME_UNKNOWN', run(s)['provider_observations'][0]['flags'])

    def test_partial_without_second_source(self):
        x = run(sources()[:1])
        self.assertIn('NO_MULTI_SOURCE_COMPARISON', x['comparison_flags'])
        self.assertEqual(x['source_qa_state'], 'INCOMPLETE')

    def test_chain_case_mismatch(self):
        s = sources()
        s[1]['payload']['pair']['chainId'] = 'ethereum'
        self.assertEqual(run(s)['source_qa_state'], 'CONFLICT')

    def test_empty_token_identity(self):
        s = sources()
        s[0]['payload']['base_token_id'] = ''
        x = run(s)
        self.assertIn('IDENTITY_INCOMPLETE', x['provider_observations'][0]['flags'])
        self.assertEqual(x['source_qa_state'], 'INCOMPLETE')

    def test_unsupported_market_data_never_means_can_sell(self):
        x = run(sources())
        self.assertFalse(x['sellability_proven'])
        self.assertEqual(x['outcome_evidence'], 'NOT_EVALUATED')

    def test_different_capture_windows_not_comparable(self):
        s = sources()
        s[1]['captured_at_utc'] = '2026-10-18T03:41:00Z'
        x = run(s)
        self.assertIn('CAPTURE_WINDOW_MISMATCH', x['comparison_flags'])
        self.assertEqual(x['source_qa_state'], 'INCOMPLETE')

    def test_case_id_rejects_value_leak(self):
        bad = {'case_id': '0x' + 'a' * 80, 'observations': sources()}
        self.assertRaises(ValueError, qa.evaluate_case, bad)

    def test_gecko_malformed_structure(self):
        s = sources()
        s[2]['payload'] = {'data': {'id': 'solana_' + POOL, 'attributes': []}}
        x = run(s)
        self.assertEqual(x['source_qa_state'], 'INCOMPLETE')
        self.assertIn('PARSE_UNAVAILABLE', x['provider_observations'][2]['flags'])

    def test_case_reference_is_hashed(self):
        x = qa.evaluate_case({'case_id': 'CONFIDENTIAL_CASE', 'observations': sources()})
        self.assertNotIn('case_id', x)
        self.assertNotIn('CONFIDENTIAL_CASE', str(x))
        self.assertEqual(len(x['case_ref_sha256']), 64)

    def test_parser_never_echoes_provider_error(self):
        s = sources()
        s[2]['payload'] = {'data': 'PRIVATE_PROVIDER_VALUE'}
        x = run(s)
        self.assertIn('PARSE_UNAVAILABLE', x['provider_observations'][2]['flags'])
        self.assertNotIn('PRIVATE_PROVIDER_VALUE', str(x))

    def test_robinhood_v4_64hex_pool_identity(self):
        items = sources()
        pool = '0x' + 'a1' * 32
        base = '0x' + 'c' * 40
        quote = '0x' + 'd' * 40
        dp = items[0]['payload']
        dp.update({'chain': 'robinhood', 'id': pool.upper().replace('0X', '0x'),
                   'base_token_id': base.upper().replace('0X', '0x'),
                   'quote_token_id': quote})
        ds = items[1]['payload']['pair']
        ds.update({'chainId': 'robinhood', 'pairAddress': pool,
                   'baseToken': {'address': base},
                   'quoteToken': {'address': quote}})
        gt = items[2]['payload']['data']
        gt.update({'id': 'robinhood_' + pool,
                   'relationships': {
                       'base_token': {'data': {'id': 'robinhood_' + base}},
                       'quote_token': {'data': {'id': 'robinhood_' + quote}}
                   }})
        gt['attributes']['address'] = pool
        x = run(items)
        self.assertEqual(x['source_qa_state'], 'COMPARABLE_AS_AGGREGATORS_ONLY')
        self.assertFalse(x['independent_onchain_validation'])

    def test_robinhood_v4_zero_vs_absent_liquidity(self):
        items = sources()
        items[0]['payload']['liquidity_usd'] = 0
        items[1]['payload']['pair'].pop('liquidity')
        x = run(items)
        self.assertIn('LIQUIDITY_ZERO', x['provider_observations'][0]['flags'])
        self.assertIn('LIQUIDITY_UNKNOWN', x['provider_observations'][1]['flags'])
        self.assertNotIn('LIQUIDITY_ZERO', x['provider_observations'][1]['flags'])
        self.assertFalse(x['sellability_proven'])

    def test_deterministic_malformed_provider_fuzz(self):
        rng = random.Random(20261018)
        choices = [None, True, False, 0, -1, 1e308, 'NaN', '', {}, [], {'unexpected': 'payload'}]
        for n in range(1200):
            rows = sources()
            for _ in range(rng.randrange(1, 5)):
                obs = rng.choice(rows)
                op = rng.randrange(5)
                if op == 0:
                    obs['captured_at_utc'] = rng.choice(choices)
                elif op == 1:
                    obs['http_status'] = rng.choice([200, 401, 402, 429, 500, None, True])
                elif op == 2:
                    obs['payload'] = rng.choice(choices)
                elif op == 3 and isinstance(obs['payload'], dict):
                    if obs['provider'] == 'DEXPAPRIKA':
                        obs['payload']['liquidity_usd'] = rng.choice(choices)
                    elif obs['provider'] == 'DEXSCREENER' and isinstance(obs['payload'].get('pair'), dict):
                        obs['payload']['pair']['liquidity'] = rng.choice(choices)
                elif op == 4 and obs['provider'] == 'GECKOTERMINAL' and isinstance(obs['payload'], dict):
                    if isinstance(obs['payload'].get('data'), dict):
                        obs['payload']['data']['attributes'] = rng.choice(choices)
            output = qa.evaluate_case({'case_id': 'FUZZ' + str(n), 'observations': rows})
            self.assertNotIn('case_id', output)
            self.assertFalse(output['sellability_proven'])
            self.assertIsNone(output['trade_signal'])
            self.assertIn(output['source_qa_state'],
                          {'INCOMPLETE', 'INVALID', 'CONFLICT', 'STALE', 'COMPARABLE_AS_AGGREGATORS_ONLY'})

    def test_source_time_unknown_not_claimed_fresh(self):
        x = run(sources())
        self.assertIn('SOURCE_FRESHNESS_UNKNOWN', x['provider_observations'][2]['flags'])
        self.assertTrue(x['rea_evidence_class'].startswith('OBSERVED_'))


if __name__ == '__main__':
    unittest.main()
