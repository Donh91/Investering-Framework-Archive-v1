import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path('scripts/framework_intelligence/framework_learning_supervisor.py')
spec = importlib.util.spec_from_file_location('framework_learning_supervisor', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FrameworkLearningSupervisorTest(unittest.TestCase):
    def sample(self):
        registry = {'candidates': [
            {'candidate_id': 'A', 'title': 'BTC RANGE 3d', 'state': 'MATURED_SUPPORTED', 'matured_outcome_count': 6, 'observation_count': 10},
            {'candidate_id': 'B', 'title': 'BTC RANGE 3d duplicate', 'state': 'INCUBATING', 'matured_outcome_count': 0, 'observation_count': 2},
            {'candidate_id': 'C', 'title': 'ETHBTC rotation', 'state': 'MATURED_NOT_SUPPORTED', 'matured_outcome_count': 4, 'observation_count': 8},
        ]}
        admission = {'candidates': [
            {'candidate_id': 'A', 'status': 'QUALIFIED_FOR_FORWARD_TEST', 'semantic_fingerprint': 'range-family'},
            {'candidate_id': 'B', 'status': 'SEMANTIC_DUPLICATE_KEEP_SHADOW', 'semantic_fingerprint': 'range-family'},
            {'candidate_id': 'C', 'status': 'QUALIFIED_FOR_FORWARD_TEST', 'semantic_fingerprint': 'rotation-family'},
        ]}
        adjudication = {'candidate_actions': [
            {'candidate_id': 'A', 'selected_action': 'RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW'},
            {'candidate_id': 'B', 'selected_action': 'ARCHIVE_ONLY_DUPLICATE'},
            {'candidate_id': 'C', 'selected_action': 'RUN_FAILURE_AND_RETIREMENT_REVIEW'},
        ]}
        return registry, admission, adjudication

    def test_semantic_family_deduplication(self):
        families = mod.derive_families(*self.sample())
        by_id = {x['semantic_identity']: x for x in families}
        self.assertEqual(by_id['range-family']['candidate_count'], 2)
        self.assertEqual(by_id['range-family']['semantic_duplicate_count'], 1)
        self.assertEqual(by_id['range-family']['duplicate_adjusted_candidate_count'], 1)
        self.assertEqual(by_id['range-family']['family_status'], 'SUPPORTED_NEEDS_INCREMENTAL_VALUE')

    def test_negative_learning_is_first_class(self):
        families = mod.derive_families(*self.sample())
        rotation = next(x for x in families if x['semantic_identity'] == 'rotation-family')
        self.assertEqual(rotation['family_status'], 'NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW')
        queue = mod.build_queue(families, {}, [], [])
        item = next(x for x in queue if x.get('semantic_identity') == 'rotation-family')
        self.assertEqual(item['state'], 'PROPOSE_EXPERIMENT')
        self.assertEqual(item['specialist'], 'EXPERIMENT_FAMILY_CURATOR')

    def test_supported_range_routes_bounded_specialist(self):
        families = mod.derive_families(*self.sample())
        queue = mod.build_queue(families, {}, [], [])
        item = next(x for x in queue if x.get('semantic_identity') == 'range-family')
        self.assertEqual(item['state'], 'DELEGATE_DETERMINISTIC')
        self.assertEqual(item['specialist'], 'RANGE_LAB_ANALYST')
        self.assertEqual(item['compute_tier'], 'DETERMINISTIC_FIRST')

    def test_architecture_forbids_authority_escalation(self):
        text = Path('00_FMOS/FRAMEWORK_INTELLIGENCE_AND_LEARNING_LOOP_v1.md').read_text()
        self.assertIn('Canonical market authority: NONE', text)
        self.assertIn('Portfolio authority: NONE', text)
        self.assertIn('LEARNING MUST NOT be silently promoted to PROVEN', text)
        self.assertIn('automatic rule change', text)

    def test_delta_does_not_call_support_proven(self):
        old = {'family_status': 'WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE', 'matured_outcome_count': 1}
        new = {'family_status': 'SUPPORTED_NEEDS_INCREMENTAL_VALUE', 'matured_outcome_count': 3}
        self.assertEqual(mod.classify_delta(old, new), 'STRENGTHENED')


if __name__ == '__main__':
    unittest.main()
