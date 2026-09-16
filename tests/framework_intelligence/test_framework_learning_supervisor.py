import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path('scripts/framework_intelligence/framework_learning_supervisor.py')
spec = importlib.util.spec_from_file_location('framework_learning_supervisor', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FrameworkLearningSupervisorTest(unittest.TestCase):
    def compounding_state(self):
        return {
            'contract': 'COMPOUNDING_LEARNING_CONTROLLER_STATE_v1',
            'authority': 'RESEARCH_ONLY_NON_CANONICAL',
            'hypothesis_families': [
                {
                    'semantic_identity': 'range-family',
                    'titles': ['BTC RANGE 3d'],
                    'kinds': ['FORECAST_TEST'],
                    'candidate_ids': ['A', 'B'],
                    'current_evidence_status': 'SUPPORTED_NEEDS_INCREMENTAL_VALUE',
                    'matured_outcome_count_total': 6,
                    'observation_count_total': 12,
                    'supporting_evidence_refs': ['A'],
                    'contradicting_evidence_refs': [],
                    'inconclusive_evidence_refs': [],
                    'known_regime_dependence': ['CONSOLIDATION'],
                    'redundancy_collinearity_warning': True,
                    'confidence_class': 'LOW_TO_MODERATE',
                    'unresolved_uncertainty': 'INCREMENTAL_VALUE_INDEPENDENCE_AND_REPLICATION_REMAIN_UNRESOLVED',
                    'material_evidence': True,
                    'material_evidence_fingerprint': 'fp-range',
                    'evidence_fingerprint': 'e-range',
                },
                {
                    'semantic_identity': 'rotation-family',
                    'titles': ['ETHBTC rotation'],
                    'kinds': ['SEQUENCE_TEST'],
                    'candidate_ids': ['C'],
                    'current_evidence_status': 'NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW',
                    'matured_outcome_count_total': 4,
                    'observation_count_total': 8,
                    'supporting_evidence_refs': [],
                    'contradicting_evidence_refs': ['C'],
                    'inconclusive_evidence_refs': [],
                    'known_regime_dependence': ['UNSPECIFIED'],
                    'redundancy_collinearity_warning': False,
                    'confidence_class': 'LOW_TO_MODERATE',
                    'unresolved_uncertainty': 'GENERAL_FAILURE_VERSUS_REGIME_SPECIFICITY_REMAINS_UNRESOLVED',
                    'material_evidence': True,
                    'material_evidence_fingerprint': 'fp-rotation',
                    'evidence_fingerprint': 'e-rotation',
                },
            ],
        }

    def test_compounding_learning_is_family_owner(self):
        families = mod.normalize_compounding_families(self.compounding_state())
        by_id = {x['semantic_identity']: x for x in families}
        self.assertEqual(by_id['range-family']['family_status'], 'SUPPORTED_NEEDS_INCREMENTAL_VALUE')
        self.assertTrue(by_id['range-family']['redundancy_collinearity_warning'])
        self.assertEqual(by_id['rotation-family']['family_status'], 'NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW')

    def test_rejects_wrong_compounding_authority(self):
        state = self.compounding_state()
        state['authority'] = 'CANONICAL'
        with self.assertRaises(RuntimeError):
            mod.normalize_compounding_families(state)

    def test_negative_learning_routes_failure_review(self):
        families = mod.normalize_compounding_families(self.compounding_state())
        queue = mod.build_queue(families, [], [])
        item = next(x for x in queue if x.get('semantic_identity') == 'rotation-family')
        self.assertEqual(item['state'], 'PROPOSE_EXPERIMENT')
        self.assertEqual(item['specialist'], 'EXPERIMENT_FAMILY_CURATOR')
        self.assertEqual(item['compute_tier'], 'DETERMINISTIC_FIRST')

    def test_supported_range_routes_range_lab(self):
        families = mod.normalize_compounding_families(self.compounding_state())
        queue = mod.build_queue(families, [], [])
        item = next(x for x in queue if x.get('semantic_identity') == 'range-family')
        self.assertEqual(item['state'], 'DELEGATE_DETERMINISTIC')
        self.assertEqual(item['specialist'], 'RANGE_LAB_ANALYST')

    def test_delta_support_is_learning_not_proof(self):
        old = {'family_status': 'WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE', 'matured_outcome_count': 1}
        new = {'family_status': 'SUPPORTED_NEEDS_INCREMENTAL_VALUE', 'matured_outcome_count': 3}
        self.assertEqual(mod.classify_delta(old, new), 'STRENGTHENED')

    def test_architecture_forbids_authority_escalation(self):
        text = Path('00_FMOS/FRAMEWORK_INTELLIGENCE_AND_LEARNING_LOOP_v1.md').read_text()
        self.assertIn('Canonical market authority: NONE', text)
        self.assertIn('Portfolio authority: NONE', text)
        self.assertIn('LEARNING MUST NOT be silently promoted to PROVEN', text)
        self.assertIn('automatic rule change', text)


if __name__ == '__main__':
    unittest.main()
