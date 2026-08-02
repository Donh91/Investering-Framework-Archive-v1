from pathlib import Path
import unittest


class WeeklyCloseArchitectureTests(unittest.TestCase):
    def test_weekly_close_script_contract(self):
        text = Path('scripts/daily_capture/build_weekly_market_close_package.py').read_text()
        self.assertIn('WEEKLY_MARKET_CLOSE_PACKAGE_v1', text)
        self.assertIn('BTCUSDT', text)
        self.assertIn('ETHUSDT', text)
        self.assertIn('ETHBTC', text)
        self.assertIn('daily_ranges', text)
        self.assertIn('handoff_targets', text)

    def test_cfgi_owner_is_shadow_only(self):
        text = Path('scripts/data_terminal/cfgi_owner_collector.py').read_text()
        self.assertIn('CFGI_API_KEY', text)
        self.assertIn('CFGI_OWNER_SNAPSHOT_v1', text)
        self.assertIn('SHADOW_OBSERVATION_ONLY', text)
        self.assertIn('portfolio_action', text)

    def test_schedule_precedes_weekly_bridge(self):
        text = Path('.github/workflows/sunday-market-close-and-cfgi.yml').read_text()
        self.assertIn("cron: '35 23 * * 0'", text)
        self.assertIn("timezone: 'Europe/Copenhagen'", text)
        self.assertIn('LATEST_WEEKLY_MARKET_CLOSE', Path('scripts/daily_capture/build_weekly_market_close_package.py').read_text())


if __name__ == '__main__':
    unittest.main()
