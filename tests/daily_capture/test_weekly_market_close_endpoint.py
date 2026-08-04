from __future__ import annotations

import importlib.util
import json
import unittest
from unittest.mock import patch
from pathlib import Path

MODULE_PATH = Path('scripts/daily_capture/build_weekly_market_close_package.py')
spec = importlib.util.spec_from_file_location('weekly_close', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def read(self):
        return self.payload


class WeeklyMarketCloseEndpointTests(unittest.TestCase):
    def test_market_data_only_endpoint_is_canonical(self):
        self.assertEqual(module.BINANCE_MARKET_DATA_BASE, 'https://data-api.binance.vision')

    def test_fetch_uses_market_data_only_domain(self):
        captured = {}
        def fake_urlopen(request, timeout):
            captured['url'] = request.full_url
            captured['timeout'] = timeout
            return Response([[1, '1', '2', '0.5', '1.5', '10', 2]])
        with patch.object(module.urllib.request, 'urlopen', fake_urlopen):
            rows = module.fetch_klines('BTCUSDT', 1, 3)
        self.assertTrue(captured['url'].startswith('https://data-api.binance.vision/api/v3/klines?'))
        self.assertEqual(captured['timeout'], 60)
        self.assertEqual(len(rows), 1)


if __name__ == '__main__':
    unittest.main()
