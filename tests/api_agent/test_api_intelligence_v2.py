from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

AUGMENT_PATH = Path('scripts/api_agent/augment_director_context_v2.py')
RETRY_PATH = Path('scripts/api_agent/deep_research_retry_v2.py')
FRESH_PATH = Path('scripts/api_agent/check_director_freshness.py')


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


augment = load_module('augment_v2', AUGMENT_PATH)
retry = load_module('retry_v2', RETRY_PATH)
freshness = load_module('freshness_v2', FRESH_PATH)


class ApiIntelligenceV2Tests(unittest.TestCase):
    def test_multi_horizon_is_deterministic_and_preserves_missingness(self) -> None:
        cutoff = datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc)
        rows = []
        for hour in range(0, 11):
            rows.append({
                'timestamp': datetime(2026, 8, 15, hour, 0, tzinfo=timezone.utc),
                'btc_close': 100.0 + hour,
                'eth_close': 10.0 + hour / 10,
                'ethbtc_close': 0.1,
                'btc_open_interest': 1000.0 + hour,
                'eth_open_interest': 500.0 + hour,
                'btc_long_short_ratio': 2.0,
                'eth_long_short_ratio': 2.0,
                'btc_taker_buy_quote_share': 0.5,
                'eth_taker_buy_quote_share': 0.5,
                'btc_high': 101.0 + hour,
                'btc_low': 99.0 + hour,
                'eth_high': 11.0 + hour / 10,
                'eth_low': 9.0 + hour / 10,
            })
        h4 = augment.build_horizon(rows, cutoff, 4)
        self.assertEqual(h4['status'], 'READY')
        self.assertEqual(h4['sample_count'], 5)
        self.assertAlmostEqual(h4['btc_return_pct'], (110 / 106 - 1) * 100, places=5)
        h72 = augment.build_horizon(rows, cutoff, 72)
        self.assertEqual(h72['status'], 'UNAVAILABLE')

    def test_freshness_extracts_owner_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'context.json'
            path.write_text(json.dumps({'latest_capture': {'run_id': 'fresh-run'}}))
            self.assertEqual(freshness.run_id_from_context(path), 'fresh-run')

    def test_retry_expands_second_attempt_and_requests_concision(self) -> None:
        payloads = []
        class FakeMcp:
            @staticmethod
            def call_openai(api_key, payload):
                payloads.append(payload)
                if len(payloads) == 1:
                    return {'text': '{"status":"READY"', 'n': 1}
                return {'text': '{"status":"READY"}', 'n': 2}
            @staticmethod
            def usage_cost(response):
                return 1, 1, 0.01
            @staticmethod
            def extract_output_text(response):
                return response['text']
        fake = SimpleNamespace(mcp=FakeMcp())
        retry.install(fake)
        value, cost, attempts = fake.call_structured_with_one_retry('key', {
            'max_output_tokens': 2600,
            'instructions': 'base',
        })
        self.assertEqual(value['status'], 'READY')
        self.assertEqual(attempts, 2)
        self.assertEqual(cost, 0.02)
        self.assertGreaterEqual(payloads[1]['max_output_tokens'], 4200)
        self.assertIn('Be concise', payloads[1]['instructions'])

    def test_policy_and_registry_keep_zero_authority(self) -> None:
        policy = json.loads(Path('research/api_agent/API_INTELLIGENCE_POLICY_v2.json').read_text())
        registry = json.loads(Path('research/api_agent/API_TASK_REGISTRY_v1.json').read_text())
        self.assertEqual(policy['monthly_hard_stop_usd'], 20.0)
        self.assertTrue(all(value is False for value in policy['authority'].values()))
        self.assertEqual(registry['tasks']['WEEKLY_ADVERSARIAL_REVIEW']['model'], 'gpt-5.6-sol')
        self.assertFalse(registry['tasks']['WEEKLY_ADVERSARIAL_REVIEW']['manual_only'])
        self.assertFalse(registry['authority']['portfolio_action'])
        self.assertFalse(registry['authority']['framework_state_change'])


if __name__ == '__main__':
    unittest.main()
