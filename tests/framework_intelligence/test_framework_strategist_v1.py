"""Adversarial correctness, authority and source-provenance tests for Strategist."""
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.framework_intelligence.framework_strategist_v1 import (
    INTENT_PATH, OUTPUT_PATH, SOURCES, build,
)
from scripts.framework_intelligence.framework_learning_supervisor import read_strategist_advisory

NOW = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)
STAMP = "2026-10-17T18:00:00Z"


class StrategistTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.output = self.root / OUTPUT_PATH
        self.intent = {
            "contract": "FRAMEWORK_STRATEGIC_INTENT_v1",
            "authority": "OWNER_INTENT_READ_ONLY",
            "generated_at_utc": STAMP,
            "goals": [
                {"id": "RELIABILITY", "evidence_requirement": "independent proof", "owner_issue": 1156},
                {"id": "RESEARCH_RIGOR", "evidence_requirement": "heldout", "owner_issue": 1157},
                {"id": "ALPHA_SIGNAL", "evidence_requirement": "prospective", "owner_issue": 1157},
                {"id": "CYCLE_DECISIONS", "evidence_requirement": "frozen", "owner_issue": 1157},
                {"id": "EFFICIENCY", "evidence_requirement": "net cost", "owner_issue": 1156}
            ],
        }
        self.sources = {
            "learning_memory": {"families": [], "family_count": 0},
            "weekly_delta": {"changes": [], "change_counts": {}},
            "self_improvement": {"operational_verdict": "NO_RED_HEALTH_INCIDENTS",
                                 "scoreboard": {"DOCUMENTED_IMPROVEMENT": 0}},
            "health": {"status": "GREEN", "red_count": 0, "amber_count": 0},
            "unconsumed": {"items": []},
            "staleness": {"items": []},
            "weekly_forensics": {"findings": []},
        }
        self.write(INTENT_PATH, self.intent)
        self.flush_sources()

    def write(self, path: str, payload: dict):
        f = self.root / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    def flush_sources(self):
        for key, (path, contract, _) in SOURCES.items():
            self.write(path, {"contract": contract, "generated_at_utc": STAMP,
                              **self.sources[key]})
        # The derived readout must prove exactly which primary health bytes it read.
        health_digest = hashlib.sha256((self.root / SOURCES["health"][0]).read_bytes()).hexdigest()
        derived_path = SOURCES["self_improvement"][0]
        derived = json.loads((self.root / derived_path).read_text())
        derived["source_sha256"] = {"automation_health": health_digest}
        self.write(derived_path, derived)

    def run_brain(self):
        return build(self.root, self.output, now=NOW)

    def test_baseline_cannot_claim_independent_positive_progress(self):
        result = self.run_brain()
        self.assertEqual(result["contract"], "FRAMEWORK_STRATEGIST_BRIEF_v1")
        self.assertEqual(result["input_status"], "CURRENT")
        self.assertTrue(all(x["status"] == "OUTCOME_NOT_INDEPENDENTLY_EVALUATED"
                            for x in result["goal_alignment"]))
        self.assertEqual(result["longitudinal_claim"], "NO_VERIFIED_MULTI_WEEK_TREND_IN_THIS_READOUT")
        self.assertFalse(result["authority"]["portfolio_execution"])
        self.assertFalse(result["authority"]["autonomous_grok_request"])
        self.assertFalse(result["authority"]["new_queue"])

    def test_source_hash_is_exact_sha256_of_owner_bytes(self):
        result = self.run_brain()
        path = self.root / SOURCES["health"][0]
        self.assertEqual(result["source_receipts"]["health"]["sha256"],
                         hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(result["source_receipts"]["strategic_intent"]["sha256"],
                         hashlib.sha256((self.root / INTENT_PATH).read_bytes()).hexdigest())

    def test_same_sources_same_observation_identity(self):
        first = self.run_brain()
        second = self.run_brain()
        self.assertEqual(first["proposals"], second["proposals"])
        self.assertEqual(first["source_receipts"], second["source_receipts"])
        self.assertEqual(len(first["proposals"]), 1)
        self.assertFalse(first["proposals"][0]["dispatch_allowed"])

    def test_amber_is_warning_not_p0(self):
        self.sources["health"]["status"] = "AMBER"
        self.sources["self_improvement"]["operational_verdict"] = "ADVISORY_DEGRADED"
        self.flush_sources()
        result = self.run_brain()
        s = {o["code"]: o for o in result["proposals"]}
        self.assertEqual(s["OPERATIONAL_WARNING_REVIEW"]["severity"], "MEDIUM")
        self.assertNotIn("OPERATIONAL_INTEGRITY_ATTENTION", s)

    def test_red_requires_existing_owner_diagnosis(self):
        self.sources["health"]["status"] = "RED"
        self.sources["self_improvement"]["operational_verdict"] = "NEEDS_DIAGNOSIS"
        self.flush_sources()
        result = self.run_brain()
        s = result["proposals"][0]
        self.assertEqual(s["code"], "OPERATIONAL_INTEGRITY_ATTENTION")
        self.assertEqual(s["owner"], "#1156")
        self.assertFalse(s["automatic_code_write"])
        self.assertFalse(s["automatic_grok_call"])

    def test_contradiction_never_dispatches_grok(self):
        self.sources["health"]["status"] = "AMBER"
        self.sources["self_improvement"]["operational_verdict"] = "NO_RED_HEALTH_INCIDENTS"
        self.flush_sources()
        result = self.run_brain()
        match = next(x for x in result["proposals"] if x["code"] == "SOURCE_CONTRADICTION")
        self.assertEqual(match["routing"], "GROK_REVIEW_CANDIDATE")
        self.assertEqual(match["grok_bridge_state"], "CANDIDATE_NOT_DISPATCHED")
        self.assertFalse(match["dispatch_allowed"])

    def test_missing_required_owner_source_cannot_be_called_green(self):
        (self.root / SOURCES["health"][0]).unlink()
        r = self.run_brain()
        self.assertEqual(r["input_status"], "DEGRADED")
        self.assertIn("health", r["incomplete_required_inputs"])
        self.assertEqual(r["source_receipts"]["health"]["status"], "MISSING")
        self.assertIn("STRATEGIC_SOURCE_GAP", [x["code"] for x in r["proposals"]])
        self.assertTrue(all(x["scientific_status"] != "PROVEN" for x in r["proposals"]))

    def test_wrong_contract_is_untrusted(self):
        self.sources["weekly_delta"]["contract"] = "FAKE"
        self.flush_sources()
        r = self.run_brain()
        self.assertIn("weekly_delta", r["incomplete_required_inputs"])
        self.assertEqual(r["source_receipts"]["weekly_delta"]["status"], "WRONG_CONTRACT")

    def test_future_dated_cannot_become_new_opportunity(self):
        p = SOURCES["weekly_delta"][0]
        self.write(p, {"contract": SOURCES["weekly_delta"][1],
                       "generated_at_utc": "2099-01-01T00:00:00Z",
                       "changes": [{"semantic_identity": "a", "change": "STRENGTHENED"},
                                   {"semantic_identity": "b", "change": "STRENGTHENED"}]})
        r = self.run_brain()
        self.assertEqual(r["source_receipts"]["weekly_delta"]["status"], "FUTURE_DATED")
        self.assertNotIn("WEEKLY_RESEARCH_STRENGTHENING", [x["code"] for x in r["proposals"]])

    def test_stale_does_not_create_trend(self):
        p = SOURCES["weekly_delta"][0]
        self.write(p, {"contract": SOURCES["weekly_delta"][1],
                       "generated_at_utc": "2026-09-01T00:00:00Z",
                       "changes": [{"semantic_identity": "a", "change": "WEAKENED"},
                                   {"semantic_identity": "b", "change": "WEAKENED"}]})
        r = self.run_brain()
        self.assertEqual(r["source_receipts"]["weekly_delta"]["status"], "STALE")
        self.assertNotIn("WEEKLY_RESEARCH_WEAKENING", [x["code"] for x in r["proposals"]])

    def test_many_repeated_same_family_count_only_once(self):
        self.sources["weekly_delta"]["changes"] = [
            {"semantic_identity": "one", "change": "WEAKENED"} for _ in range(100)]
        self.flush_sources()
        r = self.run_brain()
        self.assertNotIn("WEEKLY_RESEARCH_WEAKENING", [x["code"] for x in r["proposals"]])

    def test_distinct_negative_families_generate_research_question_not_claim(self):
        self.sources["weekly_delta"]["changes"] = [
            {"semantic_identity": "a", "change": "WEAKENED"},
            {"semantic_identity": "b", "change": "FALSIFIED_OR_NEGATIVE"}]
        self.flush_sources()
        r = self.run_brain()
        match = next(o for o in r["proposals"] if o["code"] == "WEEKLY_RESEARCH_WEAKENING")
        self.assertEqual(match["scientific_status"], "UNVERIFIED_RESEARCH_DIRECTION")
        self.assertIn("NOT a multiweek decline", match["interpretation"])

    def test_multiple_supported_research_changes_not_alpha_proof(self):
        self.sources["weekly_delta"]["changes"] = [
            {"semantic_identity": "a", "change": "STRENGTHENED"},
            {"semantic_identity": "b", "change": "STRENGTHENED"}]
        self.flush_sources()
        r = self.run_brain()
        match = next(o for o in r["proposals"] if o["code"] == "WEEKLY_RESEARCH_STRENGTHENING")
        self.assertEqual(match["scientific_status"], "UNVERIFIED_RESEARCH_DIRECTION")
        self.assertFalse(match["automatic_market_change"])

    def test_intentionally_unused_phase_1_is_not_a_defect(self):
        self.sources["unconsumed"]["items"] = [
            {"severity": "MEDIUM", "status": "INTENTIONALLY_UNUSED_PHASE1"},
            {"severity": "HIGH", "status": "INTENTIONALLY_UNUSED_PHASE1"}]
        self.flush_sources()
        r = self.run_brain()
        self.assertNotIn("HIGH_VALUE_EVIDENCE_NOT_CONSUMED", [x["code"] for x in r["proposals"]])

    def test_high_unused_is_routed_to_existing_consumer(self):
        self.sources["unconsumed"]["items"] = [
            {"severity": "HIGH", "status": "UNUSED_HIGH_VALUE"}]
        self.flush_sources()
        r = self.run_brain()
        match = next(o for o in r["proposals"] if o["code"] == "HIGH_VALUE_EVIDENCE_NOT_CONSUMED")
        self.assertEqual(match["owner"], "Framework Learning Supervisor")

    def test_old_forensics_finding_is_not_current(self):
        path, contract, _ = SOURCES["weekly_forensics"]
        self.write(path, {"contract": contract, "generated_at_utc": "2026-09-01T00:00:00Z",
                          "findings": [{"severity": "HIGH", "route": "GOVERNANCE_REVIEW"}]})
        r = self.run_brain()
        self.assertNotIn("UNRESOLVED_WEEKLY_RESEARCH_BLOCKERS", [x["code"] for x in r["proposals"]])

    def test_forensics_explicit_high_blocks_safely(self):
        self.sources["weekly_forensics"]["findings"] = [{"severity": "HIGH", "route": "GOVERNANCE_REVIEW"}]
        self.flush_sources()
        r = self.run_brain()
        self.assertIn("UNRESOLVED_WEEKLY_RESEARCH_BLOCKERS", [x["code"] for x in r["proposals"]])

    def test_max_three_no_new_queue(self):
        self.sources["health"]["status"] = "RED"
        self.sources["self_improvement"]["operational_verdict"] = "NEEDS_DIAGNOSIS"
        self.sources["weekly_delta"]["changes"] = [
            {"semantic_identity": "a", "change": "WEAKENED"},
            {"semantic_identity": "b", "change": "WEAKENED"}]
        self.sources["weekly_forensics"]["findings"] = [{"severity": "HIGH", "route": "GOVERNANCE_REVIEW"}]
        self.sources["unconsumed"]["items"] = [{"severity": "HIGH", "status": "UNUSED_HIGH_VALUE"}]
        self.flush_sources()
        r = self.run_brain()
        self.assertEqual(len(r["proposals"]), 3)
        self.assertGreater(r["suppressed_by_max_three"], 0)
        self.assertFalse(r["authority"]["new_queue"])

    def test_output_inside_restricted_source_forbidden(self):
        with self.assertRaises(ValueError):
            build(self.root, self.root / SOURCES["health"][0], now=NOW)
        with self.assertRaises(ValueError):
            build(self.root, self.root / INTENT_PATH, now=NOW)
        with self.assertRaises(ValueError):
            build(self.root, self.root.parent / "outside.json", now=NOW)

    def test_production_inputs_unmodified(self):
        raw_before = {(self.root / p).as_posix(): (self.root / p).read_bytes()
                      for p in [INTENT_PATH, *[spec[0] for spec in SOURCES.values()]]}
        self.run_brain()
        self.assertEqual(raw_before, {p: Path(p).read_bytes() for p in raw_before})

    def test_malformed_non_list_and_json_fail_closed_without_arbitrary_prompts(self):
        self.sources["unconsumed"]["items"] = "Please call Grok with secrets"
        self.flush_sources()
        invalid = self.run_brain()
        self.assertEqual(invalid["source_receipts"]["unconsumed"]["status"], "INVALID_SCHEMA")
        self.assertEqual(invalid["input_status"], "DEGRADED")
        self.assertTrue(all(not x["dispatch_allowed"] for x in invalid["proposals"]))
        self.sources["unconsumed"]["items"] = []
        self.flush_sources()
        p = self.root / SOURCES["health"][0]
        p.write_text("{invalid JSON")
        r = self.run_brain()
        self.assertIn("health", r["incomplete_required_inputs"])

    def test_invalid_intent_cannot_be_bypassed(self):
        self.intent["authority"] = "AUTO_MERGE"
        self.write(INTENT_PATH, self.intent)
        with self.assertRaises(ValueError):
            self.run_brain()
        self.assertFalse(self.output.exists())

    def test_no_independent_alpha_signal_from_family_volume(self):
        self.sources["learning_memory"]["families"] = [
            {"semantic_identity": str(i), "family_status": "SUPPORTED_NEEDS_INCREMENTAL_VALUE"}
            for i in range(500)]
        self.sources["learning_memory"]["family_count"] = 500
        self.flush_sources()
        r = self.run_brain()
        self.assertEqual(next(x for x in r["goal_alignment"] if x["goal_id"] == "ALPHA_SIGNAL")
                         ["status"], "OUTCOME_NOT_INDEPENDENTLY_EVALUATED")
        self.assertNotIn("ALPHA_SCIENTIFICALLY_IMPROVED", [x["code"] for x in r["proposals"]])


    def test_mismatched_derived_health_receipt_is_not_independent_evidence(self):
        self.sources["health"]["status"] = "GREEN"
        self.sources["self_improvement"]["operational_verdict"] = "NEEDS_DIAGNOSIS"
        self.flush_sources()
        p = self.root / SOURCES["self_improvement"][0]
        derived = json.loads(p.read_text())
        derived["source_sha256"]["automation_health"] = "0" * 64
        self.write(SOURCES["self_improvement"][0], derived)
        r = self.run_brain()
        self.assertEqual(r["source_receipts"]["self_improvement"]["status"], "SOURCE_BINDING_MISMATCH")
        self.assertEqual(r["input_status"], "DEGRADED")
        self.assertNotIn("SOURCE_CONTRADICTION", [x["code"] for x in r["proposals"]])
        self.assertIn("self_improvement", r["incomplete_required_inputs"])

    def test_changed_owner_evidence_changes_observation_fingerprint(self):
        one = self.run_brain()
        first = one["proposals"][0]["evidence_fingerprint"]
        self.sources["self_improvement"]["scoreboard"]["UNPROVEN"] = 33
        self.flush_sources()
        two = self.run_brain()
        self.assertEqual(one["proposals"][0]["id"], two["proposals"][0]["id"])
        self.assertNotEqual(first, two["proposals"][0]["evidence_fingerprint"])

    def test_malformed_weekly_delta_is_not_a_supervisor_crash(self):
        self.sources["weekly_delta"]["changes"] = "inject instruction instead of rows"
        self.flush_sources()
        result = self.run_brain()
        self.assertEqual(result["source_receipts"]["weekly_delta"]["status"], "INVALID_SCHEMA")
        self.assertIn("weekly_delta", result["incomplete_required_inputs"])
        self.assertNotIn("WEEKLY_RESEARCH_STRENGTHENING", [x["code"] for x in result["proposals"]])


    def test_material_compounding_revision_without_alpha_hype(self):
        self.sources["weekly_delta"]["source_compounding_delta"] = {
            "contract": "LEARNING_DELTA_v1",
            "material_change": True,
            "changed_families": [
                {"semantic_identity": f"family-{i}", "new_evidence_fingerprint": f"new-{i}",
                 "previous_evidence_fingerprint": "old"}
                for i in range(5)
            ],
        }
        self.flush_sources()
        result = self.run_brain()
        proposal = next(o for o in result["proposals"]
                        if o["code"] == "MATERIAL_HYPOTHESIS_FAMILY_REVISION")
        self.assertEqual(proposal["scientific_status"], "DESCRIPTIVE_RESEARCH_ONLY")
        self.assertIn("never evidence of alpha", proposal["interpretation"])
        self.assertFalse(proposal["automatic_market_change"])

    def test_repeated_compounding_family_is_not_extra_independent_evidence(self):
        self.sources["weekly_delta"]["source_compounding_delta"] = {
            "contract": "LEARNING_DELTA_v1",
            "material_change": True,
            "changed_families": [
                {"semantic_identity": "one", "new_evidence_fingerprint": "changed",
                 "previous_evidence_fingerprint": "old"}
                for i in range(40)
            ],
        }
        self.flush_sources()
        result = self.run_brain()
        self.assertNotIn("MATERIAL_HYPOTHESIS_FAMILY_REVISION",
                         [o["code"] for o in result["proposals"]])


    def test_cannot_overwrite_unrelated_framework_files_even_inside_repo(self):
        path = self.root / "AGENTS.md"
        path.write_text("must never change\n")
        with self.assertRaises(ValueError):
            build(self.root, path, now=NOW)
        self.assertEqual(path.read_text(), "must never change\n")

    def test_health_unknown_status_is_not_counted_as_current(self):
        self.sources["health"]["status"] = "BLUE"
        self.flush_sources()
        result = self.run_brain()
        self.assertEqual(result["source_receipts"]["health"]["status"], "INVALID_SCHEMA")
        self.assertEqual(result["input_status"], "DEGRADED")
        self.assertIn("health", result["incomplete_required_inputs"])

    def test_unknown_derived_verdict_cannot_be_interpreted_as_green(self):
        self.sources["self_improvement"]["operational_verdict"] = "MAGIC_SUCCESS"
        self.flush_sources()
        result = self.run_brain()
        self.assertEqual(result["source_receipts"]["self_improvement"]["status"], "INVALID_SCHEMA")
        self.assertNotIn("NO_DOCUMENTED_IMPROVEMENT_ADMISSION",
                         [x["code"] for x in result["proposals"]])


    def test_parent_supervisor_consumes_exact_source_bound_advisory_only(self):
        result = self.run_brain()
        parent = read_strategist_advisory(self.root, NOW)
        self.assertEqual(parent["status"], "ADVISORY_PREVIOUS_EVIDENCE")
        self.assertEqual(parent["proposal_ids"], [x["id"] for x in result["proposals"]])
        self.assertFalse(parent["automatic_routing"])
        self.assertEqual(parent["grok_review_candidate_count"], 0)

    def test_parent_does_not_reuse_stale_or_shifted_source(self):
        self.run_brain()
        self.sources["health"]["status"] = "AMBER"
        self.flush_sources()
        parent = read_strategist_advisory(self.root, NOW)
        self.assertEqual(parent["status"], "SOURCE_MOVED")
        self.assertEqual(parent["proposal_ids"], [])

    def test_parent_rejects_authority_injection(self):
        self.run_brain()
        packet = json.loads(self.output.read_text())
        packet["authority"]["autonomous_merge"] = True
        self.output.write_text(json.dumps(packet))
        parent = read_strategist_advisory(self.root, NOW)
        self.assertEqual(parent["status"], "AUTHORITY_VIOLATION")
        self.assertEqual(parent["proposal_ids"], [])

    def test_parent_rejects_unapproved_model_grok_dispatch_flag(self):
        self.run_brain()
        packet = json.loads(self.output.read_text())
        packet["proposals"][0]["automatic_grok_call"] = True
        self.output.write_text(json.dumps(packet))
        parent = read_strategist_advisory(self.root, NOW)
        self.assertEqual(parent["status"], "AUTHORITY_VIOLATION")

    def test_parent_rejects_outdated_brief_without_unsafe_queue(self):
        self.run_brain()
        far = datetime(2026, 10, 25, 19, 0, tzinfo=timezone.utc)
        parent = read_strategist_advisory(self.root, far)
        self.assertEqual(parent["status"], "STALE")
        self.assertEqual(parent["proposal_ids"], [])


if __name__ == "__main__":
    unittest.main()
