"""Financial failure controls; no provider calls or GitHub writes."""
import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.framework_intelligence.strategist_budget_claim_v1 import (
    canonical, claim_month, max_liability, prepare_payload,
    verified_http_ledger, verify_claim_response,
)


class MonthlyLiabilityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runtime = self.root / 'runtime'
        self.runtime.mkdir()
        self.month = datetime.now(timezone.utc).strftime('%Y-%m')
        for rel in ('research/api_agent/API_TASK_REGISTRY_v1.json',
                    'research/api_agent/API_INTELLIGENCE_POLICY_v2.json'):
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(Path(rel).read_bytes())
        (self.runtime / 'prompt.txt').write_text('Bounded advice only.')
        (self.runtime / 'context.json').write_text('{}')
        (self.runtime / 'plan.json').write_text(json.dumps({
            'run_allowed': True, 'max_api_calls': 1, 'material_fingerprint': 'a'*64}))

    def claim(self, ledger=None, fp='a'*64, amount=0.15):
        return claim_month(ledger or {}, month=self.month,
                           fingerprint=fp, run_id='12345', liability_usd=amount)

    def remote(self, ledger):
        raw = canonical(ledger)
        return {'sha': hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                'content': base64.b64encode(raw).decode()}

    def payload(self, remote=None):
        return prepare_payload(self.root, self.runtime, remote or {},
                               month=self.month, run_id='12345')

    def test_failed_or_unknown_calls_keep_full_liability_until_cap(self):
        ledger = {}
        for n in range(4):
            ledger = self.claim(ledger, fp=f'{n:064x}')
        with self.assertRaisesRegex(ValueError, 'worst_case'):
            self.claim(ledger, fp='f'*64)
        with self.assertRaisesRegex(ValueError, 'second_payment'):
            self.claim(ledger, fp=f'{0:064x}')

    def test_different_fingerprints_contend_on_same_remote_sha(self):
        remote = self.remote(self.claim())
        (self.runtime / 'plan.json').write_text(json.dumps({
            'run_allowed': True, 'max_api_calls': 1, 'material_fingerprint': 'b'*64}))
        a = self.payload(remote)
        (self.runtime / 'plan.json').write_text(json.dumps({
            'run_allowed': True, 'max_api_calls': 1, 'material_fingerprint': 'c'*64}))
        b = self.payload(remote)
        self.assertEqual(a['path'], b['path'])
        self.assertEqual(a['request']['sha'], b['request']['sha'])
        self.assertNotEqual(a['request']['content'], b['request']['content'])

    def test_tampered_remote_ledger_cannot_restore_budget(self):
        remote = self.remote(self.claim())
        remote['content'] = base64.b64encode(b'{}').decode()
        with self.assertRaisesRegex(ValueError, 'sha_mismatch'):
            self.payload(remote)

    def test_only_authoritative_http404_is_absent(self):
        self.assertEqual(verified_http_ledger('HTTP/2.0 404 Not Found\r\nX: y\r\n\r\n{"message":"Not Found"}'), {})
        for raw in ('', '{}', 'HTTP/2.0 403 Forbidden\n\n{"message":"Forbidden"}',
                    'HTTP/2.0 500 Error\n\n{}', 'HTTP/2.0 200 OK\n\n{}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                verified_http_ledger(raw)

    def test_wrong_or_lost_put_receipt_cannot_authorize_payment(self):
        row = self.payload()
        raw = base64.b64decode(row['request']['content'])
        response = {'content': {'path': row['path'], 'sha':
                    hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()},
                    'commit': {'sha': 'a'*40}}
        verify_claim_response(row, response)
        response['content']['sha'] = '0'*40
        with self.assertRaisesRegex(ValueError, 'not_durable'):
            verify_claim_response(row, response)
        with self.assertRaises(ValueError):
            verify_claim_response(row, {})

    def test_policy_drift_unbounded_input_and_nonfinite_claim_rejected(self):
        self.assertLess(max_liability(self.root, self.runtime), 0.15)
        (self.runtime / 'prompt.txt').write_text('x'*10001)
        with self.assertRaisesRegex(ValueError, 'unbounded'):
            self.payload()
        for value in (float('nan'), float('inf'), -0.1, 0.16):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.claim(amount=value)
        (self.runtime / 'prompt.txt').write_text('bounded')
        p = self.root / 'research/api_agent/API_INTELLIGENCE_POLICY_v2.json'
        value = json.loads(p.read_text())
        value['monthly_hard_stop_usd'] = 50
        p.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'policy_or_pricing_drift'):
            self.payload()

    def test_real_cli_fails_closed_on_missing_http_status(self):
        remote = self.runtime / 'remote.http'
        remote.write_text('{}')
        script = Path('scripts/framework_intelligence/strategist_budget_claim_v1.py').resolve()
        result = subprocess.run([sys.executable, str(script), '--repo-root', str(self.root),
            '--runtime-dir', str(self.runtime), '--remote-get', str(remote), '--http-response',
            '--month', self.month, '--run-id', '12345'], cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing_authoritative_http_status', result.stderr)
        self.assertNotIn('ModuleNotFoundError', result.stderr)

    def test_existing_workflow_requires_monthly_cas_before_gateway(self):
        text = Path('.github/workflows/framework-learning-supervisor.yml').read_text()
        step = text.split('      - name: Governed zero-retry', 1)[1].split('      - name:', 1)[0]
        shell = '\n'.join(line[10:] for line in step.split('        run: |\n', 1)[1].splitlines())
        self.assertLess(shell.index('Monthly claim verification failed'), shell.index('python scripts/api_agent/api_gateway.py'))
        self.assertIn('Monthly budget CAS lost or rejected; no payment.', shell)
        self.assertNotIn('--retry', shell)
        self.assertEqual(subprocess.run(['bash', '-n'], input=shell, text=True, capture_output=True).returncode, 0)


from scripts.framework_intelligence.strategist_budget_claim_v1 import CAP_USD, CONTRACT, MODEL, TASK
MONTH = datetime.now(timezone.utc).strftime("%Y-%m")

class BudgetClaimTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.runtime = self.root / "runtime"
        self.runtime.mkdir()
        def save(path, payload):
            fp = self.root / path
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(json.dumps(payload))
        save("research/api_agent/API_TASK_REGISTRY_v1.json", {"tasks": {
            TASK: {"model": MODEL, "max_attempts": 1, "max_output_tokens": 5400,
                   "governed_instruction": "Bounded"}}})
        save("research/api_agent/API_INTELLIGENCE_POLICY_v2.json", {
            "monthly_hard_stop_usd": 40, "global_reserve_usd": 4,
            "lane_caps_usd": {TASK: CAP_USD}})
        (self.runtime / "prompt.txt").write_text("Read-only.")
        (self.runtime / "context.json").write_text('{"source":[]}')
        (self.runtime / "plan.json").write_text(json.dumps({
            "run_allowed": True, "max_api_calls": 1, "material_fingerprint": "b"*64}))

    def test_worst_case_includes_output_tokens(self):
        amount = max_liability(self.root, self.runtime)
        self.assertGreaterEqual(amount, 0.054)
        self.assertLessEqual(amount, 0.15)
        (self.runtime / "context.json").write_text("x"*12002)
        with self.assertRaisesRegex(ValueError, "unbounded"):
            max_liability(self.root, self.runtime)

    def test_new_questions_consume_same_monthly_cap(self):
        month = {}
        for n, digit in enumerate("abcdef", 1):
            month = claim_month(month, month=MONTH, fingerprint=digit*64,
                                run_id=str(n), liability_usd=0.11)
        self.assertEqual(len(month["entries"]), 6)
        with self.assertRaisesRegex(ValueError, "insufficient"):
            claim_month(month, month=MONTH, fingerprint="0"*64,
                        run_id="7", liability_usd=0.11)
        with self.assertRaisesRegex(ValueError, "already_claimed"):
            claim_month(month, month=MONTH, fingerprint="a"*64,
                        run_id="8", liability_usd=0.11)

    def test_existing_ledger_requires_expected_blob_sha(self):
        original = claim_month({}, month=MONTH, fingerprint="a"*64,
                               run_id="1", liability_usd=0.11)
        raw = canonical(original)
        blob_sha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        remote = {"sha": blob_sha, "content": base64.b64encode(raw).decode()}
        claim = prepare_payload(self.root, self.runtime, remote, month=MONTH, run_id="2")
        self.assertEqual(claim["request"]["sha"], blob_sha)
        self.assertIn("b"*64, json.loads(base64.b64decode(claim["request"]["content"]))["entries"])
        remote["sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "sha_mismatch"):
            prepare_payload(self.root, self.runtime, remote, month=MONTH, run_id="3")

    def test_untrusted_ledger_and_budget_policy_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "untrusted_existing"):
            claim_month({"contract": CONTRACT, "month": MONTH}, month=MONTH,
                        fingerprint="c"*64, run_id="4", liability_usd=0.1)
        path = self.root/"research/api_agent/API_TASK_REGISTRY_v1.json"
        cfg = json.loads(path.read_text())
        cfg["tasks"][TASK]["max_attempts"] = 2
        path.write_text(json.dumps(cfg))
        with self.assertRaisesRegex(ValueError, "budget_policy"):
            max_liability(self.root, self.runtime)
