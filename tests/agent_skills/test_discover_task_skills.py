"""Regression tests for advisory-only skill discovery, no model or API calls."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "scripts/agent_skills/discover_task_skills.py"
SPEC = importlib.util.spec_from_file_location("discover_task_skills", PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def skill(name, triggers, *, implicit=False, maturity="PILOT_ACTIVE",
          exclusions=None):
    return {
        "name": name,
        "skill_path": ".agents/skills/" + name + "/SKILL.md",
        "maturity": maturity,
        "triggers": triggers,
        "do_not_use_for": exclusions or [],
        "allow_implicit_invocation": implicit,
    }


def fixture():
    return {
        "status": "DERIVED_ROUTING_ONLY",
        "authority": "NONE_BY_ITSELF",
        "canonical_owner": "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
        "skills": [
            skill("canonical-context-router", ["framework", "current version"],
                  implicit=True),
            skill("research-lab-red-team", ["audit", "red team"], implicit=False),
            skill("archive-governance", ["archive", "save"], implicit=False,
                  exclusions=["portfolio actions"]),
            skill("conclusion-challenge-loop", ["high value conclusion", "self correction"],
                  implicit=False, maturity="PILOT_CANDIDATE_READ_ONLY_V1"),
            skill("prospective-evidence-ledger", ["M3", "prospective row"],
                  implicit=False),
        ],
    }


class DiscoveryTests(unittest.TestCase):
    def test_routine_has_no_candidates_or_invocation(self):
        for task in ("Tak", "Status?", "PR status #2090", "godnat", "ok"):
            with self.subTest(task=task):
                r = MODULE.discover(fixture(), task)
                self.assertEqual(r["status"], "SKIPPED_ROUTINE")
                self.assertEqual(r["recommendations"], [])
                self.assertFalse(r["auto_invocation_authorized"])

    def test_task_first_order_and_explicit_gate(self):
        r = MODULE.discover(fixture(), "audit framework", max_results=3)
        self.assertEqual(r["status"], "SHORTLIST")
        names = [x["name"] for x in r["recommendations"]]
        self.assertEqual(names, ["canonical-context-router", "research-lab-red-team"])
        self.assertEqual(r["recommendations"][1]["invocation_status"], "EXPLICIT_ADMISSION_REQUIRED")
        self.assertFalse(r["skill_instruction_loaded"])

    def test_specific_phrase_outranks_generic_keyword(self):
        r = MODULE.discover(fixture(), "Review current version of framework")
        self.assertEqual(r["recommendations"][0]["matched_triggers"], ["current version"])

    def test_pilot_excluded_unless_explicitly_inspected(self):
        r = MODULE.discover(fixture(), "high value conclusion")
        self.assertEqual(r["status"], "NO_MATCH")
        pilot = MODULE.discover(fixture(), "high value conclusion", include_pilot=True)
        self.assertEqual(pilot["recommendations"][0]["name"], "conclusion-challenge-loop")
        self.assertEqual(pilot["recommendations"][0]["invocation_status"], "PILOT_REVIEW_ONLY")
        self.assertFalse(pilot["auto_invocation_authorized"])

    def test_negative_trigger_blocks_not_overrides_others(self):
        r = MODULE.discover(fixture(), "save portfolio actions")
        self.assertEqual(r["status"], "NO_MATCH")

    def test_token_boundary_prevents_identifier_false_positive(self):
        self.assertEqual(MODULE.discover(fixture(), "read XM30")["status"], "NO_MATCH")
        self.assertEqual(MODULE.discover(fixture(), "review M3")["recommendations"][0]["name"],
                         "prospective-evidence-ledger")

    def test_bad_metadata_blocks_without_partial_recommendations(self):
        for field, val in (
            ("authority", "GLOBAL_EXECUTION"),
            ("status", "CANONICAL"),
            ("canonical_owner", "new_registry.md"),
            ("skills", "not a list"),
        ):
            data = fixture()
            data[field] = val
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    MODULE.discover(data, "audit")

    def test_duplicate_skill_names_are_invalid(self):
        data = fixture()
        data["skills"].append(data["skills"][0].copy())
        with self.assertRaises(ValueError):
            MODULE.discover(data, "audit")

    def test_unsafe_skill_path_rejected(self):
        data = fixture()
        data["skills"][0]["skill_path"] = "../../secrets/SKILL.md"
        with self.assertRaises(ValueError):
            MODULE.discover(data, "framework")

    def test_result_is_bounded(self):
        r = MODULE.discover(fixture(), "audit framework archive prospective row",
                            max_results=2)
        self.assertLessEqual(len(r["recommendations"]), 2)
        with self.assertRaises(ValueError):
            MODULE.discover(fixture(), "audit", max_results=20)
        with self.assertRaises(ValueError):
            MODULE.discover(fixture(), "audit", max_results=0)

    def test_result_never_contains_task_or_private_strings(self):
        task = "audit framework private marker 5533-supersecret"
        r = MODULE.discover(fixture(), task)
        self.assertNotIn("5533-supersecret", json.dumps(r))

    def test_negative_control_no_keyword_spam(self):
        r = MODULE.discover(fixture(), "Please calculate two plus two")
        self.assertEqual(r["status"], "NO_MATCH")

    def test_live_index_is_readable_and_nonauthoritative(self):
        path = ROOT / "00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json"
        if not path.exists():
            self.skipTest("repo index not present in isolated test checkout")
        index = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(index["skills"])
        self.assertFalse(MODULE.discover(index, "audit framework")["auto_invocation_authorized"])
        self.assertNotIn("conclusion-challenge-loop",
                         [x["name"] for x in MODULE.discover(index, "high value conclusion")["recommendations"]])


if __name__ == "__main__":
    unittest.main()
