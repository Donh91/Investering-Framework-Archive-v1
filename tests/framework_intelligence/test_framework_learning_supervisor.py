import importlib.util
import json
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
        self.assertIn("github.event_name == 'schedule'", text)
        self.assertIn("(github.event_name == 'workflow_dispatch' && inputs.sol_collect_run_id == '')", text)
        self.assertIn("inputs.sol_collect_run_id != ''", text)
        self.assertIn("sol-max-collect:", text)
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
        # Match the current canonical task binding. Legacy Sol is no
        # longer the hard-coded senior model after owner-authorized upgrades.
        task = json.loads(Path('research/api_agent/API_TASK_REGISTRY_v1.json').read_text())['tasks']['SENIOR_REPAIR_AUDIT']
        self.assertIn(task['model'], text)
        self.assertIn(f"MODEL_USED={task['model']}", text)
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


    def test_elite_sol_batch_is_advisory_existing_queue_only(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rel = Path("research/api_agent/coordination/S1_SOL_MAX_ELITE_BOUNDED_BATCH_20261104.json")
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            original = json.loads((Path(".") / rel).read_text())
            dest.write_text(json.dumps(original))
            rows = mod.read_elite_sol_batch_queue(root)
            self.assertEqual(len(rows), 5)
            self.assertEqual(rows[0]["semantic_identity"], "S1-ELITE-EXECUTOR-20261104")
            self.assertEqual(rows[1]["next_gate"], "UNBLOCK_API_TRANSPORT_AND_UNKNOWN_BILLING")
            self.assertTrue(all(x["paid_dispatch_allowed"] is False for x in rows))
            self.assertTrue(all(x["automatic_merge_allowed"] is False for x in rows))
            self.assertEqual(rows[2]["original_pr"], 1879)
            self.assertEqual(rows[2]["original_owner_issue"], 1516)
            original["dispatch_enabled"] = True
            dest.write_text(json.dumps(original))
            self.assertEqual(mod.read_elite_sol_batch_queue(root), [])
            original["dispatch_enabled"] = False
            original["payment_policy"]["no_auto_paid_trigger_until_reconciled"] = False
            dest.write_text(json.dumps(original))
            self.assertEqual(mod.read_elite_sol_batch_queue(root), [])
            original["payment_policy"]["no_auto_paid_trigger_until_reconciled"] = True
            original["definitions"][0]["depends_on"] = [{"not": "a dependency"}]
            dest.write_text(json.dumps(original))
            self.assertEqual(mod.read_elite_sol_batch_queue(root), [])
            dest.write_text("{invalid-json")
            self.assertEqual(mod.read_elite_sol_batch_queue(root), [])
            dest.write_text("[]")
            self.assertEqual(mod.read_elite_sol_batch_queue(root), [])
            dest.unlink()
            self.assertEqual(mod.read_elite_sol_batch_queue(root), [])




class WeeklySkillCalibrationTest(unittest.TestCase):
    """Exercises the real Monday-only code path used by existing S1-independent FMOS."""

    def setUp(self):
        import tempfile
        from datetime import datetime, timezone
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.monday = datetime(2026, 11, 16, 8, 35, tzinfo=timezone.utc)
        spec = importlib.util.spec_from_file_location(
            "weekly_skill_calibration_v1",
            Path("scripts/framework_intelligence/weekly_skill_calibration_v1.py"),
        )
        self.impl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.impl)
        self.put("research/framework_learning/weekly_forensics/LATEST.json", {
            "contract": "WEEKLY_FORENSICS_PACK_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "mode": "FINAL", "iso_year": 2026, "iso_week": 46,
            "generated_at_utc": "2026-11-16T08:00:00Z",
        })
        self.put("00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json", {
            "status": "DERIVED_ROUTING_ONLY", "authority": "NONE_BY_ITSELF",
            "canonical_owner": "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
            "skills": [{
                "name": "canonical-context-router",
                "maturity": "PILOT_ACTIVE",
                "skill_path": ".agents/skills/canonical-context-router/SKILL.md",
                "allow_implicit_invocation": True,
            }, {
                "name": "conclusion-challenge-loop",
                "maturity": "PILOT_CANDIDATE_READ_ONLY_V1",
                "skill_path": ".agents/skills/conclusion-challenge-loop/SKILL.md",
                "allow_implicit_invocation": False,
            }],
        })
        for skill in ("canonical-context-router", "conclusion-challenge-loop"):
            path = self.root / ".agents/skills" / skill / "SKILL.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# " + skill + "\n")

    def put(self, rel, obj):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, sort_keys=True) + "\n")
        return p

    def report(self):
        return self.impl.build(self.root, self.monday)

    def observation(self, *, skill="canonical-context-router",
                    phase="PROCEDURE_APPLIED", invocation="run-20261112-a"):
        original = self.put("research/framework_learning/operational_memory/native-original.json", {
            "contract": "EXISTING_ORIGINAL_OWNER_EVIDENCE", "run": invocation
        })
        skill_file = self.root / ".agents/skills" / skill / "SKILL.md"
        item = {
            "contract": "SKILL_USE_OBSERVATION_v1", "authority": "ADVISORY_SELF_REPORT_ONLY",
            "automatic_skill_activation": False, "week": "2026-W46",
            "observed_at_utc": "2026-11-12T12:45:00Z",
            "invocation_id": invocation, "skill_name": skill, "use_phase": phase,
            "execution_receipt_path": original.relative_to(self.root).as_posix(),
            "execution_receipt_sha256": self.impl.digest(original.read_bytes()),
            "skill_sha256": self.impl.digest(skill_file.read_bytes()),
        }
        return self.put(f"research/framework_learning/skill_usage/observations/2026-W46/{invocation}.json", item)

    def test_only_monday_targets_completed_week(self):
        from datetime import timedelta
        self.assertIsNone(self.impl.build(self.root, self.monday - timedelta(days=1)))
        x = self.report()
        self.assertEqual(x["evaluated_week"], "2026-W46")
        self.assertEqual(x["status"], "BASELINE_ONLY_NATIVE_USAGE_UNKNOWN")
        self.assertIsNone(x["verified_native_skill_usage_count"])
        self.assertIsNone(x["metrics"]["observations"]["reported"])
        self.assertFalse(x["auto_skill_activation"])
        self.assertEqual(x["action"]["code"], "INSTRUMENT_NATIVE_SKILL_USAGE")

    def test_source_not_final_or_mismatched_week_is_not_calibration(self):
        final = self.root / "research/framework_learning/weekly_forensics/LATEST.json"
        item = json.loads(final.read_text())
        item["mode"] = "PRELIMINARY"
        final.write_text(json.dumps(item))
        self.assertEqual(self.report()["status"], "WAIT_FOR_FINAL_WEEKLY_SOURCE")
        item["mode"] = "FINAL"
        item["iso_week"] = 45
        final.write_text(json.dumps(item))
        self.assertEqual(self.report()["status"], "WAIT_FOR_FINAL_WEEKLY_SOURCE")
        item["iso_week"] = 46
        item["generated_at_utc"] = "2026-11-12T00:00:00Z"
        final.write_text(json.dumps(item))
        self.assertEqual(self.report()["status"], "WAIT_FOR_FINAL_WEEKLY_SOURCE")

    def test_source_bound_report_is_not_native_or_value_proof(self):
        self.observation()
        report = self.report()
        self.assertEqual(report["status"], "SOURCE_BOUND_REPORTS_ADVISORY_ONLY")
        self.assertEqual(report["metrics"]["observations"]["reported"], 1)
        self.assertEqual(report["metrics"]["observations"]["by_phase"]["PROCEDURE_APPLIED"], 1)
        self.assertIsNone(report["metrics"]["false_positive_rate"])
        self.assertIsNone(report["independent_skill_effect_rate"])
        self.assertEqual(report["action"]["code"], "INDEPENDENT_SKILL_QUALITY_COMPARISON")
        self.assertFalse(report["scientific_or_performance_promotion"])

    def test_nonstring_phase_in_optional_receipt_does_not_abort_supervisor(self):
        p = self.observation()
        for bad in ({"unexpected": "object"}, ["PROCEDURE_APPLIED"]):
            with self.subTest(phase_type=type(bad).__name__):
                r = json.loads(p.read_text())
                r["use_phase"] = bad
                p.write_text(json.dumps(r))
                score = self.report()
                self.assertEqual(score["metrics"]["observations"]["invalid"], 1)
                self.assertEqual(score["metrics"]["observations"]["reported"], 0)
                self.assertEqual(score["action"]["code"], "REPAIR_SKILL_RECEIPT_INTEGRITY")

    def test_conflicting_phases_never_hide_pilot_use_alert(self):
        first = self.observation(skill="conclusion-challenge-loop",
                                 phase="SUGGESTED_ONLY")
        applied = json.loads(first.read_text())
        applied["use_phase"] = "PROCEDURE_APPLIED"
        extra = self.root / "research/framework_learning/skill_usage/observations/2026-W46/z.json"
        extra.write_text(json.dumps(applied))
        r = self.report()
        observation = r["metrics"]["observations"]
        self.assertEqual(observation["reported"], 1)
        self.assertEqual(observation["phase_conflicts"], 1)
        self.assertEqual(observation["pilots_reported_applied"], 1)
        self.assertEqual(observation["by_phase"]["PROCEDURE_APPLIED"], 0)
        self.assertEqual(r["action"]["code"], "INVESTIGATE_UNAUTHORIZED_PILOT_USE")

    def test_tampered_original_source_fails_closed(self):
        self.observation()
        original = self.root / "research/framework_learning/operational_memory/native-original.json"
        original.write_text('{"changed":true}')
        score = self.report()
        self.assertEqual(score["metrics"]["observations"]["reported"], 0)
        self.assertEqual(score["metrics"]["observations"]["invalid"], 1)
        self.assertEqual(score["action"]["code"], "REPAIR_SKILL_RECEIPT_INTEGRITY")

    def test_pilot_claim_requires_review_not_autonomous_activation(self):
        self.observation(skill="conclusion-challenge-loop")
        r = self.report()
        self.assertEqual(r["metrics"]["catalog"]["pilot_count"], 1)
        self.assertEqual(r["metrics"]["observations"]["pilots_reported_applied"], 1)
        self.assertEqual(r["action"]["priority"], "P0")
        self.assertEqual(r["action"]["code"], "INVESTIGATE_UNAUTHORIZED_PILOT_USE")
        self.assertFalse(r["action"]["auto_execute"])
        self.assertIsNone(r["verified_native_skill_usage_count"])

    def test_duplicate_source_bound_invocation_is_not_independent_n(self):
        original = self.observation()
        other = self.root / "research/framework_learning/skill_usage/observations/2026-W46/b.json"
        other.write_bytes(original.read_bytes())
        r = self.report()
        self.assertEqual(r["metrics"]["observations"]["reported"], 1)
        self.assertEqual(r["metrics"]["observations"]["duplicate"], 1)

    def test_catalog_implicit_pilot_violation_blocked(self):
        p = self.root / "00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json"
        index = json.loads(p.read_text())
        index["skills"][1]["allow_implicit_invocation"] = True
        p.write_text(json.dumps(index))
        r = self.report()
        self.assertEqual(r["status"], "CATALOG_BLOCKED")
        self.assertIsNone(r["metrics"])

    def test_frozen_week_carries_through_daily_supervisor_and_master_packet(self):
        """A real Monday build persists a W46 receipt, Tuesday reuses same bytes."""
        from unittest.mock import patch
        import sys
        import hashlib
        out = self.root / "research/framework_learning"
        args = ["supervisor", "--repo-root", str(self.root), "--as-of-utc", "2026-11-16T08:35:00Z"]
        with patch.object(sys, "argv", args):
            mod.main()
        frozen = out / "skill_calibration/weeks/2026-W46.json"
        self.assertTrue(frozen.is_file())
        first = frozen.read_bytes()
        scorecard = json.loads(first)
        self.assertEqual(scorecard["evaluated_week"], "2026-W46")
        packet = json.loads((out / "LATEST_MASTER_MONDAY_LEARNING_PACKET.json").read_text())
        advisory = packet["skill_calibration_advisory"]
        self.assertEqual(advisory["source_scorecard_sha256"], hashlib.sha256(first).hexdigest())
        self.assertEqual(advisory["output_path"],
                         "research/framework_learning/skill_calibration/weeks/2026-W46.json")
        with patch.object(sys, "argv", ["supervisor", "--repo-root", str(self.root),
                                        "--as-of-utc", "2026-11-17T08:35:00Z"]):
            mod.main()
        self.assertEqual(frozen.read_bytes(), first)
        latest = json.loads((out / "LATEST_SKILL_CALIBRATION.json").read_text())
        self.assertEqual(latest["evaluated_week"], "2026-W46")
        tuesday_packet = json.loads((out / "LATEST_MASTER_MONDAY_LEARNING_PACKET.json").read_text())
        self.assertEqual(tuesday_packet["skill_calibration_advisory"]["source_scorecard_sha256"],
                         advisory["source_scorecard_sha256"])
        self.assertFalse(tuesday_packet["live_consumption_allowed"])
        tuesday_state = json.loads((out / "LATEST_SUPERVISOR_STATE.json").read_text())
        self.assertFalse(tuesday_state["master_monday_live_influence"])
        self.assertEqual(tuesday_state["skill_calibration"]["evaluated_week"], "2026-W46")

    def test_frozen_wrong_week_or_future_timestamp_not_reused(self):
        self.observation()
        self.put("research/framework_learning/skill_calibration/weeks/2026-W46.json", {
            **self.report(), "calibrated_at_utc": "2099-11-16T08:35:00Z",
        })
        self.assertIsNone(self.impl.load_frozen_last_completed_week(
            self.root / "research/framework_learning", self.monday
        ))
        path = self.root / "research/framework_learning/skill_calibration/weeks/2026-W46.json"
        data = json.loads(path.read_text())
        data["calibrated_at_utc"] = "2026-11-16T08:35:00Z"
        data["auto_skill_activation"] = True
        path.write_text(json.dumps(data))
        self.assertIsNone(self.impl.load_frozen_last_completed_week(
            self.root / "research/framework_learning", self.monday
        ))

    def test_weekly_comparison_is_not_benefit_claim(self):
        prev = self.impl._previous(self.root, "2026-W46")
        self.assertIsNone(prev)
        self.put("research/framework_learning/skill_calibration/weeks/2026-W45.json", {
            "contract": self.impl.CONTRACT, "evaluated_week": "2026-W45",
            "metrics": {"catalog": {"catalog_total": 1}}
        })
        r = self.report()
        self.assertEqual(r["prior_comparison_status"], "PREVIOUS_WEEK_PRESENT")
        self.assertEqual(r["metrics"]["catalog_change_vs_prior_week"], 1)
        self.assertIsNone(r["independent_skill_effect_rate"])



if __name__ == '__main__':
    unittest.main()
