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

    def test_method_audit_proposes_gpt6_sol_senior_lane(self):
        queue = mod.build_queue([], [], [{
            'method': 'MASTER_MONDAY_INFORMATION_BINDING',
            'status': 'METHOD_AUDIT_DUE',
            'trigger': 'high-value binding defect',
            'automatic_change_allowed': False,
        }])
        self.assertEqual(len(queue), 1)
        item = queue[0]
        self.assertEqual(item['state'], 'REQUEST_METHOD_AUDIT')
        self.assertEqual(item['compute_tier'], 'GPT6_SOL_SENIOR_IF_DETERMINISTIC_REVIEW_INSUFFICIENT')
        self.assertEqual(item['api_task'], 'SENIOR_REPAIR_AUDIT')
        self.assertEqual(item['authority'], 'PROPOSAL_ONLY')

    def test_delta_support_is_learning_not_proof(self):
        old = {'family_status': 'WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE', 'matured_outcome_count': 1}
        new = {'family_status': 'SUPPORTED_NEEDS_INCREMENTAL_VALUE', 'matured_outcome_count': 3}
        self.assertEqual(mod.classify_delta(old, new), 'STRENGTHENED')

    def test_senior_repair_issue_dispatch_is_strictly_owner_gated(self):
        text = Path('.github/workflows/framework-learning-supervisor.yml').read_text()
        self.assertIn('issue_comment:', text)
        self.assertIn("github.event.issue.number == 1156", text)
        self.assertIn("github.event.comment.author_association == 'OWNER'", text)
        self.assertIn("contains(github.event.comment.body, '[SENIOR_REPAIR_AUDIT]')", text)
        self.assertIn('--task SENIOR_REPAIR_AUDIT', text)
        self.assertIn('--cap-usd 10.0', text)
        self.assertIn('--hard-stop-usd 40', text)
        self.assertIn('--reserve-usd 4.0', text)
        self.assertIn('comment-${COMMENT_ID}', text)
        self.assertIn('senior_repair_audit_dispatch.py validate', text)
        self.assertIn("github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'", text)
        self.assertNotIn("if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'", text)

    def test_failed_senior_audit_cost_receipt_is_persisted_before_validation(self):
        text = Path('.github/workflows/framework-learning-supervisor.yml').read_text()
        persist = text.index('Persist immutable senior audit evidence and cost receipt')
        validate = text.index('Validate senior audit receipt and output')
        self.assertLess(persist, validate)
        self.assertIn("if: always() && steps.dedupe.outputs.run_audit == 'true'", text)
        self.assertIn('failure-report', text)
        self.assertIn('senior_audit_no_receipt_to_persist', text)

    def test_senior_dispatch_helper_preserves_read_only_audit_boundary(self):
        text = Path('scripts/api_agent/senior_repair_audit_dispatch.py').read_text()
        self.assertIn('ADVISORY_READ_ONLY', text)
        self.assertIn('forecast_candidates MUST be empty', text)
        self.assertIn('NO_CODE_WRITE_PERFORMED', text)
        self.assertIn('NO_AUTHORITY_CHANGE', text)
        self.assertIn('private_data_included', text)
        self.assertIn('gpt-6.1-sol', text)
    def test_architecture_forbids_authority_escalation(self):
        text = Path('00_FMOS/FRAMEWORK_INTELLIGENCE_AND_LEARNING_LOOP_v1.md').read_text()
        self.assertIn('Canonical market authority: NONE', text)
        self.assertIn('Portfolio authority: NONE', text)
        self.assertIn('LEARNING MUST NOT be silently promoted to PROVEN', text)
        self.assertIn('automatic rule change', text)


    def _current_cross_domain_fixture(self):
        return {
            "contract": "SHADOW_WEEKLY_RELEVANCE_SNAPSHOT_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "portfolio_execution": False,
            "week": "2026-W42",
            "cross_domain_review": {
                "contract": "SHADOW_CROSS_DOMAIN_WEEKLY_REVIEW_v1",
                "week": "2026-W42",
                "authority": "RESEARCH_ONLY_NON_CANONICAL",
                "cost_and_execution": {
                    "external_llm_calls": 0,
                    "incremental_paid_api_usd": 0,
                    "incremental_provider_calls": 0,
                    "new_schedulers": 0,
                    "automatic_execution": False,
                    "automatic_market_rule_change": False,
                    "automatic_model_promotion": False,
                    "wallet_signing": False,
                },
                "lanes": [
                    {"lane_id": "COMPASS", "source_status": "SOURCE_OBSERVED",
                     "scientific_edge": "UNPROVEN", "paper_or_live_trading_authorized": False,
                     "owner": "Official Compass #1530",
                     "review_question": "WAIT_FOR_MATURATION"},
                    {"lane_id": "AUTO_TRADING", "source_status": "SOURCE_OBSERVED",
                     "scientific_edge": "UNPROVEN", "paper_or_live_trading_authorized": False,
                     "owner": "AUTO_TRADING #1557",
                     "review_question": "GLOBAL_N_PENDING"},
                    {"lane_id": "ALPHA_LAB", "source_status": "PRIVATE_REPO_SOURCE_NOT_IMPORTED",
                     "scientific_edge": "UNPROVEN", "paper_or_live_trading_authorized": False,
                     "owner": "MAL #88", "review_question": "SOURCE_PENDING"}
                ],
            },
        }

    def test_weekly_shadow_supervisor_reuses_reviewed_main_only(self):
        x = mod.admit_cross_domain_shadow_weekly(self._current_cross_domain_fixture(), "2026-W42")
        self.assertEqual(x["status"], "WEEKLY_RESEARCH_ADVISORY_ONLY")
        self.assertEqual(len(x["lanes"]), 3)
        self.assertFalse(x["automatic_model_calls"])
        self.assertFalse(x["portfolio_execution"])
        self.assertEqual(x["lanes"][2]["source_status"], "PRIVATE_REPO_SOURCE_NOT_IMPORTED")

    def test_weekly_shadow_old_or_unmerged_candidate_stays_pending(self):
        x = mod.admit_cross_domain_shadow_weekly(self._current_cross_domain_fixture(), "2026-W43")
        self.assertEqual(x["status"], "PENDING_REVIEWED_WEEKLY_SNAPSHOT")
        self.assertEqual(x["reason"], "WEEKLY_REVIEW_NOT_MERGED_OR_STALE")
        snapshot = self._current_cross_domain_fixture()
        snapshot.pop("cross_domain_review")
        y = mod.admit_cross_domain_shadow_weekly(snapshot, "2026-W42")
        self.assertEqual(y["reason"], "CROSS_DOMAIN_REVIEW_NOT_IN_MERGED_SNAPSHOT")

    def test_weekly_shadow_fails_closed_if_model_calls_or_trading_added(self):
        x = self._current_cross_domain_fixture()
        x["cross_domain_review"]["cost_and_execution"]["external_llm_calls"] = 1
        self.assertEqual(
            mod.admit_cross_domain_shadow_weekly(x, "2026-W42")["reason"],
            "INVALID_COST_OR_AUTHORITY_BOUNDARY"
        )
        x = self._current_cross_domain_fixture()
        x["cross_domain_review"]["lanes"][1]["paper_or_live_trading_authorized"] = True
        self.assertEqual(
            mod.admit_cross_domain_shadow_weekly(x, "2026-W42")["reason"],
            "UNAPPROVED_TRADING_OR_EDGE_PROMOTION"
        )

    def test_weekly_shadow_never_promotes_missing_private_evidence(self):
        x = self._current_cross_domain_fixture()
        x["authority"] = "CANONICAL"
        self.assertEqual(
            mod.admit_cross_domain_shadow_weekly(x, "2026-W42")["reason"],
            "INVALID_REGISTRY_AUTHORITY"
        )
        self.assertEqual(
            mod.admit_cross_domain_shadow_weekly({}, "2026-W42")["status"],
            "PENDING_REVIEWED_WEEKLY_SNAPSHOT"
        )


if __name__ == '__main__':
    unittest.main()
