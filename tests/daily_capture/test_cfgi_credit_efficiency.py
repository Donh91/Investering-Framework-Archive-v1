from pathlib import Path
import unittest

from scripts.daily_capture.build_weekly_cfgi_summary import cfgi_from_capture


class CfgiCreditEfficiencyTests(unittest.TestCase):
    def test_daily_tiered_fields(self):
        text = Path('.github/workflows/daily-raw-owner-capture.yml').read_text()
        self.assertIn('CFGI_FIELDS="score"', text)
        self.assertIn('score,whales,orders,technical,volatility', text)
        self.assertIn('11 23 * * *', text)

    def test_weekly_summary_adds_no_api_calls(self):
        workflow = Path('.github/workflows/sunday-market-close-and-cfgi.yml').read_text()
        script = Path('scripts/daily_capture/build_weekly_cfgi_summary.py').read_text()
        self.assertNotIn('CFGI_API_KEY', workflow)
        self.assertIn('api_calls_added', script)
        self.assertIn('DAILY_RAW_CAPTURE_INDEX_v2_OWNER_SUMMARIES', script)

    def test_collector_persists_credit_headers(self):
        text = Path('scripts/data_terminal/cfgi_owner_collector.py').read_text()
        self.assertIn('X-Credits-Used', text)
        self.assertIn('X-Credits-Remaining', text)
        self.assertIn('CFGI_OWNER_RECEIPT_v3', text)

    def test_weekly_reader_accepts_current_live_anchor_cfgi_schema(self):
        packet = {
            'market_metrics': {
                'sentiment': {
                    'cfgi': {
                        'timeframe': '4h',
                        'symbols': {
                            'BTC': {
                                'score': 45,
                                'classification': 'Neutral',
                                'price': 77644.25,
                                'timestamp': '2026-09-03T04:19:02Z',
                                'owner_status': 'PASS',
                                'stale': False,
                            },
                            'MARKET': {
                                'score': 49.5,
                                'classification': 'Neutral',
                                'timestamp': '2026-09-03T04:19:02Z',
                            },
                        },
                    },
                },
            },
            'owners': [],
        }
        rows, billing = cfgi_from_capture(packet)
        self.assertEqual(billing, {})
        self.assertEqual([row['symbol'] for row in rows], ['BTC', 'MARKET'])
        self.assertEqual(rows[0]['score'], 45)
        self.assertEqual(rows[0]['timestamp'], '2026-09-03T04:19:02Z')

    def test_legacy_owner_rows_remain_preferred(self):
        packet = {
            'owners': [{
                'owner_id': 'cfgi_sentiment',
                'files': [{
                    'summary': {
                        'rows': [{'symbol': 'BTC', 'score': 40}],
                        'fields': ['score'],
                        'billing': {'credits_remaining': 100},
                    },
                }],
            }],
            'market_metrics': {
                'sentiment': {
                    'cfgi': {
                        'symbols': {'BTC': {'score': 99}},
                    },
                },
            },
        }
        rows, billing = cfgi_from_capture(packet)
        self.assertEqual(rows, [{'symbol': 'BTC', 'score': 40}])
        self.assertEqual(billing['credits_used'], 1)
        self.assertEqual(billing['usage_source'], 'DERIVED_FROM_FIELDS_X_ROWS')


if __name__ == '__main__':
    unittest.main()
