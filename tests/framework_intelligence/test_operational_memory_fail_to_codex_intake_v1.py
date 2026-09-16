import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path('scripts/framework_intelligence/operational_memory_fail_to_codex_intake_v1.py')
spec = importlib.util.spec_from_file_location('operational_memory_fail_to_codex_intake_v1', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

VALIDATOR_SCRIPT = Path('scripts/remediation/merge_codex_research_intake.py')
validator_spec = importlib.util.spec_from_file_location('merge_codex_research_intake', VALIDATOR_SCRIPT)
validator = importlib.util.module_from_spec(validator_spec)
validator_spec.loader.exec_module(validator)


def audit_doc(status='FAIL', failures=None, head='a' * 40):
    return {
        'contract': 'OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT_v1',
        'generated_at_utc': '2026-09-15T12:00:00Z',
        'status': status,
        'source_head_sha': head,
        'failures': failures or ['stale_memory_not_quarantined:OE-1'],
        'warnings': [],
    }


class OperationalMemoryFailToCodexIntakeV1Test(unittest.TestCase):
    def write_audit(self, root: Path, doc: dict) -> Path:
        path = root / 'research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc))
        return path

    def test_non_fail_is_noop(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc(status='PASS'))
            out = mod.route(root, audit)
            self.assertFalse(out['created'])
            self.assertEqual(out['reason'], 'AUDIT_NOT_FAIL')

    def test_fail_creates_valid_bounded_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc())
            out = mod.route(root, audit)
            self.assertTrue(out['created'])
            candidate_path = root / out['path']
            candidate = json.loads(candidate_path.read_text())
            self.assertEqual(candidate['contract'], 'CODEX_RESEARCH_CANDIDATE_v1')
            self.assertEqual(candidate['status'], 'SUBMITTED')
            self.assertEqual(candidate['authority_boundary'], 'CODE_REMEDIATION_ONLY')
            self.assertFalse(candidate['requires_framework_owner_authority'])
            self.assertEqual(set(candidate['forbidden_changes']), set(mod.REQUIRED_FORBIDDEN))
            self.assertTrue(candidate['acceptance_tests']['positive'])
            self.assertTrue(candidate['acceptance_tests']['negative'])
            self.assertTrue(candidate['authority']['code_remediation_only'])
            self.assertFalse(candidate['authority']['automatic_merge'])
            self.assertEqual(Path(out['path']).stem, candidate['candidate_id'])
            status, reasons = validator.validate_candidate(candidate_path, candidate)
            self.assertEqual(status, 'VALID', reasons)
            self.assertEqual(reasons, [])

    def test_same_fail_pending_candidate_dedupes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc())
            first = mod.route(root, audit)
            second = mod.route(root, audit)
            self.assertTrue(first['created'])
            self.assertFalse(second['created'])
            self.assertEqual(second['candidate_id'], first['candidate_id'])
            self.assertEqual(second['reason'], 'MATCHING_PENDING_CANDIDATE_EXISTS')

    def test_completed_candidate_allows_one_recurrence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc(head='b' * 40))
            first = mod.route(root, audit)
            completion = root / 'research/codex/completions' / f"{first['candidate_id']}.json"
            completion.parent.mkdir(parents=True, exist_ok=True)
            completion.write_text('{}')
            second = mod.route(root, audit)
            self.assertTrue(second['created'])
            self.assertNotEqual(second['candidate_id'], first['candidate_id'])
            self.assertIn('bbbbbbbbbb', second['candidate_id'])
            third = mod.route(root, audit)
            self.assertFalse(third['created'])
            self.assertEqual(third['candidate_id'], second['candidate_id'])

    def test_failure_fingerprint_is_order_insensitive(self):
        a = audit_doc(failures=['b', 'a', 'a'])
        b = audit_doc(failures=['a', 'b'])
        self.assertEqual(mod.failure_fingerprint(a), mod.failure_fingerprint(b))

    def test_allowed_scope_does_not_broaden_authority(self):
        forbidden_tokens = {'market gates', 'model weights', 'canonical authority', 'portfolio logic', 'api budget', 'new policy semantics'}
        allowed = ' '.join(mod.ALLOWED_SCOPE).lower()
        self.assertFalse(any(token in allowed for token in forbidden_tokens))


if __name__ == '__main__':
    unittest.main()
