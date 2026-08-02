from pathlib import Path
import unittest


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


if __name__ == '__main__':
    unittest.main()
