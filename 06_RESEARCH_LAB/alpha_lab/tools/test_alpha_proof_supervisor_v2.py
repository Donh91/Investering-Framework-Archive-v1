from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('alpha_proof_supervisor_v2.py')

def freeze_spec(source_sha='abc123'):
    value = {
        'test': 'SHADOW-04-PROSPECTIVE',
        'frozen_at': 100.0,
        'future_start_block': 200,
        'target_launches': 1000,
        'chain_id': '0x1237',
        'factory': '0xfactory',
        'topic0': '0xtopic',
        'providers': ['a', 'b'],
        'source_sha': source_sha,
        'assertions': ['future-only'],
    }
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    value['spec_sha256'] = hashlib.sha256(raw).hexdigest()
    return value

class ProofSupervisorV2Test(unittest.TestCase):
    def run_supervisor(self, state, *, artifact=None, freeze=None, conclusion='success', head='abc123'):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state_path = root / 'state.json'
            state_path.write_text(json.dumps(state))
            args = [sys.executable, str(SCRIPT), '--state', str(state_path), '--upstream-conclusion', conclusion, '--upstream-head-sha', head]
            if artifact is not None:
                artifact_path = root / 'result.json'
                artifact_path.write_text(json.dumps(artifact))
                args += ['--artifact', str(artifact_path)]
            if freeze is not None:
                freeze_path = root / 'freeze.json'
                freeze_path.write_text(json.dumps(freeze))
                args += ['--freeze', str(freeze_path)]
            subprocess.run(args, check=True, capture_output=True, text=True)
            return json.loads(state_path.read_text())

    def seed(self):
        return {'state':'WAIT_SHADOW04','shadow04_attempts':0,'next_action':'WAIT','portfolio_execution':False,'canonical_effect':False}

    def valid_artifact(self, freeze):
        return {
            'test':'SHADOW-04-PROSPECTIVE',
            'spec_sha256':freeze['spec_sha256'],
            'source_sha':freeze['source_sha'],
            'n':1000,
            'future_start_block':freeze['future_start_block'],
            'first_observed_block':freeze['future_start_block'],
            'first_observed_unix':freeze['frozen_at'] + 1,
            'provider_disagreement':0,
            'prospective':True,
            'PASS_COLLECTION':True,
        }

    def test_valid_frozen_future_artifact_passes(self):
        freeze = freeze_spec()
        state = self.run_supervisor(self.seed(), artifact=self.valid_artifact(freeze), freeze=freeze)
        self.assertEqual(state['state'], 'SHADOW04_PASS')
        self.assertEqual(state['next_action'], 'START_SHADOW07')

    def test_tampered_preregistration_hash_halts(self):
        freeze = freeze_spec()
        artifact = self.valid_artifact(freeze)
        freeze['target_launches'] = 999
        state = self.run_supervisor(self.seed(), artifact=artifact, freeze=freeze)
        self.assertEqual(state['state'], 'HALT_CRITICAL')
        self.assertEqual(state['reason'], 'preregistration_hash_mismatch')

    def test_non_main_source_sha_halts(self):
        freeze = freeze_spec('wrong')
        artifact = self.valid_artifact(freeze)
        state = self.run_supervisor(self.seed(), artifact=artifact, freeze=freeze, head='abc123')
        self.assertEqual(state['state'], 'HALT_CRITICAL')
        self.assertEqual(state['reason'], 'unreviewed_or_mismatched_source_sha')

    def test_observation_before_frozen_start_halts(self):
        freeze = freeze_spec()
        artifact = self.valid_artifact(freeze)
        artifact['first_observed_block'] = freeze['future_start_block'] - 1
        state = self.run_supervisor(self.seed(), artifact=artifact, freeze=freeze)
        self.assertEqual(state['state'], 'HALT_CRITICAL')
        self.assertEqual(state['reason'], 'outcome_precedes_frozen_start')

    def test_failed_runs_consume_bounded_retry_budget(self):
        state = self.seed()
        state = self.run_supervisor(state, conclusion='failure')
        self.assertEqual((state['state'], state['shadow04_attempts']), ('WAIT_SHADOW04', 1))
        state = self.run_supervisor(state, conclusion='failure')
        self.assertEqual((state['state'], state['shadow04_attempts']), ('WAIT_SHADOW04', 2))
        state = self.run_supervisor(state, conclusion='failure')
        self.assertEqual(state['state'], 'HALT_CRITICAL')

    def test_terminal_pass_cannot_be_rewritten(self):
        state = self.seed()
        state.update(state='SHADOW04_PASS', next_action='START_SHADOW07', reason='prospective_gate_pass')
        after = self.run_supervisor(state, conclusion='failure')
        self.assertEqual(after, state)

if __name__ == '__main__':
    unittest.main()
