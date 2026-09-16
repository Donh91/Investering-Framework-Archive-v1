import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path('scripts/framework_intelligence').resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

SCRIPT = SCRIPT_DIR / 'operational_memory_post_production_audit_v1.py'
spec = importlib.util.spec_from_file_location('operational_memory_post_production_audit_v1', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def base_docs(head: str):
    rows = []
    for i in range(6):
        rows.append(
            {
                'episode_id': f'OE-{i}',
                'source_commit_sha': str(i) * 40,
                'source_timestamp': f'2026-09-1{i}T00:00:00Z',
                'task_class': 'CYCLE_NAVIGATOR',
                'operation_type': 'FIX',
                'task_summary': 'fix cycle navigator binding',
                'failure_signature': 'cycle-navigator-binding',
                'changed_paths': ['05_CYCLE_NAVIGATOR/a.txt'],
                'dominant_path_prefix': '05_CYCLE_NAVIGATOR',
                'compatibility': {'status': 'EXACT'},
                'retrieval_tier': 'WARM',
                'newer_related_episode': None,
                'episode_path': f'episodes/2026/09/OE-{i}.json',
            }
        )
    authority = {
        'canonical_effect': False,
        'portfolio_execution': False,
        'automatic_promotion': False,
        'automatic_skill_activation': False,
        'automatic_repository_write': False,
    }
    state = {
        'contract': 'OPERATIONAL_MEMORY_AND_RETRIEVAL_v1',
        'status': 'PASS',
        'source_head_sha': head,
        'new_episode_count': 6,
        'episode_count': 6,
        'procedural_candidate_count': 1,
        'authority': authority,
    }
    index = {
        'contract': 'OPERATIONAL_MEMORY_INDEX_v1',
        'source_head_sha': head,
        'episode_count': 6,
        'rows': rows,
        'authority': authority,
    }
    health = {
        'contract': 'OPERATIONAL_MEMORY_HEALTH_v1',
        'status': 'PASS',
        'episode_count': 6,
        'authority': authority,
    }
    candidates = {
        'contract': 'OPERATIONAL_PROCEDURAL_CANDIDATES_v1',
        'candidate_count': 1,
        'candidates': [
            {
                'candidate_id': 'PC-1',
                'task_class': 'CYCLE_NAVIGATOR',
                'operation_family': 'REMEDIATION',
                'dominant_path_prefix': '05_CYCLE_NAVIGATOR',
                'independent_commit_count': 3,
                'currently_compatible_count': 3,
                'supporting_episode_ids': ['OE-0', 'OE-1', 'OE-2'],
                'status': 'CANDIDATE_ONLY',
                'automatic_skill_activation': False,
                'promotion_allowed': False,
            }
        ],
        'authority': authority,
    }
    return state, index, health, candidates


class OperationalMemoryPostProductionAuditV1Test(unittest.TestCase):
    def make_repo(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        subprocess.run(['git', 'init', str(root)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(root), 'config', 'user.email', 'test@example.com'], check=True)
        subprocess.run(['git', '-C', str(root), 'config', 'user.name', 'Test'], check=True)
        (root / 'README.md').write_text('x')
        subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(root), 'commit', '-m', 'initial'], check=True, capture_output=True)
        head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        op_root = root / 'research/framework_learning/operational_memory'
        op_root.mkdir(parents=True)
        docs = base_docs(head)
        for name, doc in zip(mod.EXPECTED_CONTRACTS, docs):
            (op_root / name).write_text(json.dumps(doc))
        return td, root, op_root

    def test_happy_path_passes(self):
        td, root, op_root = self.make_repo()
        try:
            out = mod.audit(root, op_root)
            self.assertEqual(out['status'], 'PASS')
            self.assertTrue(out['memory_reuse_allowed'])
            self.assertFalse(out['automatic_escalation_required'])
            self.assertGreaterEqual(out['retrieval_probe']['top_task_class_precision'], 0.8)
        finally:
            td.cleanup()

    def test_stale_memory_must_be_quarantined(self):
        td, root, op_root = self.make_repo()
        try:
            index_path = op_root / 'LATEST_OPERATIONAL_MEMORY_INDEX.json'
            index = json.loads(index_path.read_text())
            index['rows'][0]['compatibility'] = {'status': 'REMOVED'}
            index['rows'][0]['retrieval_tier'] = 'WARM'
            index_path.write_text(json.dumps(index))
            out = mod.audit(root, op_root)
            self.assertEqual(out['status'], 'FAIL')
            self.assertFalse(out['memory_reuse_allowed'])
            self.assertTrue(any(x.startswith('stale_memory_not_quarantined:') for x in out['failures']))
        finally:
            td.cleanup()

    def test_unsafe_candidate_fails(self):
        td, root, op_root = self.make_repo()
        try:
            path = op_root / 'LATEST_PROCEDURAL_CANDIDATES.json'
            doc = json.loads(path.read_text())
            doc['candidates'][0]['automatic_skill_activation'] = True
            path.write_text(json.dumps(doc))
            out = mod.audit(root, op_root)
            self.assertEqual(out['status'], 'FAIL')
            self.assertTrue(any(x.startswith('unsafe_procedural_candidate:') for x in out['failures']))
        finally:
            td.cleanup()

    def test_head_mismatch_fails_closed_for_memory_reuse(self):
        td, root, op_root = self.make_repo()
        try:
            index_path = op_root / 'LATEST_OPERATIONAL_MEMORY_INDEX.json'
            index = json.loads(index_path.read_text())
            index['source_head_sha'] = '0' * 40
            index_path.write_text(json.dumps(index))
            out = mod.audit(root, op_root)
            self.assertEqual(out['status'], 'FAIL')
            self.assertIn('index_not_bound_to_current_head', out['failures'])
        finally:
            td.cleanup()

    def test_zero_compatible_candidate_warns_not_fails(self):
        td, root, op_root = self.make_repo()
        try:
            path = op_root / 'LATEST_PROCEDURAL_CANDIDATES.json'
            doc = json.loads(path.read_text())
            doc['candidates'][0]['currently_compatible_count'] = 0
            path.write_text(json.dumps(doc))
            out = mod.audit(root, op_root)
            self.assertEqual(out['status'], 'WARN')
            self.assertTrue(out['memory_reuse_allowed'])
            self.assertFalse(out['automatic_escalation_required'])
        finally:
            td.cleanup()


if __name__ == '__main__':
    unittest.main()
