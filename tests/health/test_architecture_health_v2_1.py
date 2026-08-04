from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path('scripts/health/build_architecture_health.py')
spec = importlib.util.spec_from_file_location('architecture_health', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class ArchitectureHealthV21Tests(unittest.TestCase):
    def test_daily_director_uses_paired_receipt_created_unix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'research/api_agent/outputs/daily/2026/08/04/120000/DAILY_DIRECTOR_OUTPUT.json'
            output.parent.mkdir(parents=True)
            output.write_text(json.dumps({'status': 'READY'}))
            receipt = output.with_name('DAILY_DIRECTOR_RECEIPT.json')
            receipt.write_text(json.dumps({'contract': 'API_AGENT_RECEIPT_v3', 'created_unix': 1785844800, 'status': 'PASS'}))
            path, value, stamp, receipt_path = module.latest_paired_output(root / 'research/api_agent/outputs/daily', 'DAILY_DIRECTOR_OUTPUT.json', 'DAILY_DIRECTOR_RECEIPT.json')
            self.assertEqual(path, output)
            self.assertEqual(receipt_path, receipt)
            self.assertEqual(stamp, datetime.fromtimestamp(1785844800, timezone.utc))
            self.assertEqual(value['status'], 'READY')

    def test_nested_cfgi_billing_is_discovered(self):
        owner = {'files': [{'summary': {'billing': {'credits_remaining': 98765}}}]}
        self.assertEqual(module.find_cfgi_remaining(owner), 98765)


if __name__ == '__main__':
    unittest.main()
