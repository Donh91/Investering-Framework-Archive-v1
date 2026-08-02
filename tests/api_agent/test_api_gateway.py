import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.api_gateway import build_request, estimate_cost, load_registry, validate_output

REGISTRY = Path('research/api_agent/API_TASK_REGISTRY_v1.json')


class ApiGatewayTests(unittest.TestCase):
    def test_registry_is_shadow_only(self):
        data = load_registry(REGISTRY)
        self.assertEqual(data['status'], 'ACTIVE_SHADOW_ONLY')
        self.assertFalse(data['authority']['portfolio_action'])
        self.assertFalse(data['authority']['framework_state_change'])

    def test_cost_estimate(self):
        self.assertEqual(estimate_cost('gpt-5.6-luna', 1000000, 1000000), 7.0)
        self.assertEqual(estimate_cost('gpt-5.6-terra', 1000000, 1000000), 17.5)

    def test_valid_output(self):
        validate_output({
            'status': 'READY',
            'summary': 'x',
            'evidence_for': [],
            'evidence_against': [],
            'uncertainties': [],
            'hypotheses': [],
        })

    def test_forbidden_authority_rejected(self):
        with self.assertRaises(ValueError):
            validate_output({
                'status': 'READY',
                'summary': 'x',
                'evidence_for': [],
                'evidence_against': [],
                'uncertainties': [],
                'hypotheses': [],
                'portfolio_action': 'BUY',
            })

    def test_request_is_store_false_and_current_turn(self):
        data = load_registry(REGISTRY)
        cfg = data['tasks']['DAILY_DIRECTOR_SHADOW']
        request = build_request('DAILY_DIRECTOR_SHADOW', cfg, 'test', {'a': 1})
        self.assertFalse(request['store'])
        self.assertEqual(request['reasoning']['context'], 'current_turn')
        self.assertEqual(request['model'], 'gpt-5.6-luna')


if __name__ == '__main__':
    unittest.main()
