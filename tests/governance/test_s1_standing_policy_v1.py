"""Standing S1 policy: decisions as main blobs (A2), required-job closure (B2),
science-gated prefixes (B3) and review reuse across main drift (G3/D3).

Every test reads the repository it runs in, so the manifest, AGENTS.md and the
workflow files cannot drift apart without a red native test.
"""
import copy
import json
import re
import unittest
from pathlib import Path

from scripts.governance import s1_standing_policy_v1 as sp

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_BYTES = (ROOT / sp.MANIFEST_PATH).read_bytes()
MANIFEST = json.loads(MANIFEST_BYTES.decode("utf-8"))
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
A, B = "a" * 40, "b" * 40


def manifest(**changes):
    out = copy.deepcopy(MANIFEST)
    out.update(changes)
    return out


class StandingDecisionsAreMainBlobs(unittest.TestCase):
    def test_manifest_on_this_tree_is_shadow_with_no_optional_review(self):
        self.assertEqual(MANIFEST["lane_state"], "SHADOW")
        self.assertEqual(MANIFEST["review_optional_classes"], [])
        self.assertEqual(sp.lane_state(MANIFEST), "SHADOW")
        for cls in sp.CLASSES:
            self.assertFalse(sp.unattended_class_enabled(MANIFEST, cls))
            self.assertFalse(sp.review_optional(MANIFEST, cls))

    def test_manifest_no_longer_names_a_ui_approval_or_a_permanent_inactive_status(self):
        text = MANIFEST_BYTES.decode("utf-8")
        self.assertNotIn("OWNER_UI_APPROVAL", text)
        self.assertNotIn("PROPOSED_INACTIVE", text)
        self.assertIn("OWNER_PRESENT_INTERACTIVE_DECISION", MANIFEST["activation_gate"])
        self.assertIn("Only this blob as reachable from current main", MANIFEST["standing_decision_rule"])

    def test_agents_states_the_rule_and_points_at_the_same_fields(self):
        self.assertIn("Only blobs on main carry standing decisions", AGENTS)
        for field in ("`lane_state`", "`review_optional_classes`"):
            self.assertIn(field, AGENTS)
        self.assertNotIn("Until that final owner comment", AGENTS)

    def test_unknown_missing_or_malformed_lane_state_reads_shadow(self):
        for bad in (None, "", "docs_only", "LOW", "ACTIVE", 1, ["DOCS_ONLY"], {"x": 1}):
            with self.subTest(bad=bad):
                self.assertEqual(sp.lane_state(manifest(lane_state=bad)), "SHADOW")
        broken = manifest(); del broken["lane_state"]
        self.assertEqual(sp.lane_state(broken), "SHADOW")
        for not_a_manifest in (None, [], "SHADOW", {"lane_state": "LOW_CODE"}):
            self.assertEqual(sp.lane_state(not_a_manifest), "SHADOW")

    def test_lane_stages_open_classes_in_order(self):
        docs = manifest(lane_state="DOCS_ONLY")
        self.assertTrue(sp.unattended_class_enabled(docs, "DOCS_ONLY"))
        self.assertFalse(sp.unattended_class_enabled(docs, "LOW_CODE"))
        low = manifest(lane_state="LOW_CODE")
        self.assertTrue(sp.unattended_class_enabled(low, "DOCS_ONLY"))
        self.assertTrue(sp.unattended_class_enabled(low, "LOW_CODE"))
        for cls in ("HIGH_IMPACT", "GOVERNANCE_WORKFLOW", "", None):
            self.assertFalse(sp.unattended_class_enabled(low, cls))

    def test_review_optional_needs_both_the_list_and_an_open_lane(self):
        self.assertFalse(sp.review_optional(manifest(review_optional_classes=["DOCS_ONLY"]), "DOCS_ONLY"))  # SHADOW
        open_docs = manifest(lane_state="DOCS_ONLY", review_optional_classes=["DOCS_ONLY"])
        self.assertTrue(sp.review_optional(open_docs, "DOCS_ONLY"))
        self.assertFalse(sp.review_optional(open_docs, "LOW_CODE"))
        self.assertFalse(sp.review_optional(manifest(lane_state="DOCS_ONLY", review_optional_classes=["LOW_CODE"]), "LOW_CODE"))
        for bad in ("DOCS_ONLY", None, ["DOCS_ONLY", "EVERYTHING"], [["DOCS_ONLY"]]):
            with self.subTest(bad=bad):
                self.assertFalse(sp.review_optional(manifest(lane_state="LOW_CODE", review_optional_classes=bad), "DOCS_ONLY"))

    def test_standing_decisions_only_from_a_matching_main_blob(self):
        blob = sp.git_blob_sha(MANIFEST_BYTES)
        ok = sp.standing_decisions(MANIFEST_BYTES, blob_sha=blob, source_ref=sp.MAIN_REF)
        self.assertEqual((ok["reason"], ok["lane_state"], ok["source"], ok["manifest_blob_sha"]),
                         ("OK", "SHADOW", "MAIN_BLOB", blob))
        opened = json.dumps(manifest(lane_state="DOCS_ONLY", review_optional_classes=["DOCS_ONLY"])).encode()
        for ref in ("refs/pull/2089/head", "refs/heads/agent/x", "main", None, ""):
            with self.subTest(ref=ref):
                got = sp.standing_decisions(opened, blob_sha=sp.git_blob_sha(opened), source_ref=ref)
                self.assertEqual((got["reason"], got["lane_state"], got["review_optional_classes"]),
                                 ("NOT_FROM_MAIN", "SHADOW", []))
        got = sp.standing_decisions(opened, blob_sha=blob, source_ref=sp.MAIN_REF)  # bytes are not that blob
        self.assertEqual((got["reason"], got["lane_state"]), ("MANIFEST_BLOB_MISMATCH", "SHADOW"))
        got = sp.standing_decisions(opened, blob_sha=sp.git_blob_sha(opened), source_ref=sp.MAIN_REF)
        self.assertEqual((got["lane_state"], got["review_optional_classes"]), ("DOCS_ONLY", ["DOCS_ONLY"]))
        for junk in (b"{", b"[]", b"\xff\xfe", b'{"contract":"OTHER","lane_state":"LOW_CODE"}'):
            with self.subTest(junk=junk):
                got = sp.standing_decisions(junk, blob_sha=sp.git_blob_sha(junk), source_ref=sp.MAIN_REF)
                self.assertEqual(got["lane_state"], "SHADOW")
                self.assertNotEqual(got["reason"], "OK")
        self.assertEqual(sp.standing_decisions("text", blob_sha=blob, source_ref=sp.MAIN_REF)["reason"],
                         "MANIFEST_BLOB_MISMATCH")

    def test_git_blob_sha_matches_git(self):
        self.assertEqual(sp.git_blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
        self.assertEqual(sp.git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")


class RequiredJobClosureIsGovernance(unittest.TestCase):
    def test_manifest_list_equals_the_derivation_from_the_workflow_files(self):
        derived = sp.derive_required_job_executed_paths(ROOT, MANIFEST)
        self.assertEqual(MANIFEST["required_job_executed_paths"], derived,
                         "stale: run scripts/governance/s1_standing_policy_v1.py --derive and update the manifest")
        self.assertEqual(derived, sorted(set(derived)))
        self.assertGreaterEqual(len(derived), 21)
        self.assertEqual(sp.main(["--root", str(ROOT), "--check"]), 0)

    def test_every_listed_file_exists_and_known_members_are_present(self):
        listed = MANIFEST["required_job_executed_paths"]
        for path in listed:
            self.assertTrue((ROOT / path).is_file(), path)
        for path in ("scripts/data_governance/storage_health_gate.py",          # run by storage-health
                     "tests/data_governance/test_storage_health_gate.py",
                     "scripts/data_storage/durable_promotion_controller.py",    # loaded by file path from a test
                     "scripts/data_storage/storage_telemetry.py",
                     "tests/learning/test_kompas_pro_internal_horizon_v2.py"):
            self.assertIn(path, listed)

    def test_every_run_line_file_token_of_the_required_workflows_is_listed(self):
        """Independent of the module's own tokenizer: a plain regex over the workflow text."""
        listed = set(MANIFEST["required_job_executed_paths"])
        for workflow in sp.required_workflow_paths(MANIFEST):
            text = (ROOT / workflow).read_text(encoding="utf-8")
            for token in re.findall(r"[\w./-]+\.(?:py|mjs|js|sh)\b", text):
                if (ROOT / token).is_file():
                    self.assertIn(token, listed, f"{workflow} runs {token}")
            for dotted in re.findall(r"\b(?:tests|scripts)(?:\.\w+)+", text):
                candidate = dotted.replace(".", "/") + ".py"
                if (ROOT / candidate).is_file():
                    self.assertIn(candidate, listed, f"{workflow} runs {dotted}")

    def test_derivation_follows_a_new_step_import_and_literal_path(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".github/workflows").mkdir(parents=True)
            (root / "scripts/x").mkdir(parents=True); (root / "tests/x").mkdir(parents=True); (root / "lib").mkdir()
            (root / ".github/workflows/w.yml").write_text(
                "on:\n  pull_request:\njobs:\n  gate:\n    steps:\n"
                "      - run: python -m unittest tests.x.test_a -v\n"
                "      - run: node lib/run.test.mjs && python scripts/x/tool.py --root .\n", encoding="utf-8")
            (root / "tests/x/test_a.py").write_text(
                "import pathlib\nfrom scripts.x import helper\nP = pathlib.Path('scripts/x/by_path.py')\n", encoding="utf-8")
            (root / "scripts/x/helper.py").write_text("from . import deep\n", encoding="utf-8")
            (root / "scripts/x/deep.py").write_text("X = 1\n", encoding="utf-8")
            (root / "scripts/x/by_path.py").write_text("X = 1\n", encoding="utf-8")
            (root / "scripts/x/tool.py").write_text("import json\n", encoding="utf-8")
            (root / "scripts/x/unrelated.py").write_text("X = 1\n", encoding="utf-8")
            (root / "lib/run.test.mjs").write_text("import x from './dep.mjs';\n", encoding="utf-8")
            (root / "lib/dep.mjs").write_text("export default 1;\n", encoding="utf-8")
            m = {"classes": {"DOCS_ONLY": [{"workflow_path": ".github/workflows/w.yml", "job_id": "gate"}]}}
            self.assertEqual(sp.derive_required_job_executed_paths(root, m), [
                "lib/dep.mjs", "lib/run.test.mjs", "scripts/x/by_path.py", "scripts/x/deep.py",
                "scripts/x/helper.py", "scripts/x/tool.py", "tests/x/test_a.py"])

    def test_closure_workflows_and_policy_paths_are_governance(self):
        for path in MANIFEST["required_job_executed_paths"] + sp.required_workflow_paths(MANIFEST) + [
                "AGENTS.md", "CLAUDE.md", sp.MANIFEST_PATH, "00_FMOS/anything.md", ".agents/skills/x/SKILL.md",
                ".github/workflows/new.yml", "schemas/S1_CLOSURE_ASSURANCE_V1.schema.json",
                "scripts/governance/s1_release_evidence_classifier_v1.py",
                "scripts/governance/s1_standing_policy_v1.py", "tests/governance/test_s1_standing_policy_v1.py"]:
            with self.subTest(path=path):
                self.assertTrue(sp.is_governance_path(path, MANIFEST))

    def test_ordinary_paths_are_not_governance_and_unusable_input_is(self):
        for path in ("README.md", "docs/guide.md", "scripts/health/build_automation_health.py",
                     "02_DATA_PING/2026/x.json"):
            self.assertFalse(sp.is_governance_path(path, MANIFEST), path)
        for bad in ("", None, "/etc/passwd", "a/../AGENTS.md", "./AGENTS.md", " AGENTS.md", "a\\b"):
            self.assertTrue(sp.is_governance_path(bad, MANIFEST), repr(bad))
        broken = manifest(); del broken["required_job_executed_paths"]
        self.assertTrue(sp.is_governance_path("README.md", broken))
        self.assertTrue(sp.is_governance_path("README.md", None))

    def test_agents_names_the_executed_file_rule(self):
        self.assertIn("every file that a required job of `00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json` executes", AGENTS)
        self.assertIn("`required_job_executed_paths`", AGENTS)


class ScienceGatedPrefixes(unittest.TestCase):
    def test_d5_sentence_in_agents_lists_exactly_the_manifest_prefixes(self):
        match = re.search(r"research/market/forecast publications under (.*?) \(the manifest's `science_gated_prefixes`\)", AGENTS)
        self.assertIsNotNone(match)
        self.assertEqual(sorted(re.findall(r"`([^`]+)`", match.group(1))), sorted(MANIFEST["science_gated_prefixes"]))

    def test_both_research_trees_are_gated_and_exist(self):
        for prefix in ("04_RESEARCH_LAB/", "research/", "06_RESEARCH_LAB/", "04_MARKET_LEARNING/", "05_CYCLE_NAVIGATOR/"):
            self.assertIn(prefix, MANIFEST["science_gated_prefixes"])
            self.assertTrue((ROOT / prefix).is_dir(), prefix)
        for path in ("04_RESEARCH_LAB/auto_trading/x.md", "research/api_agent/note.md", "06_RESEARCH_LAB/audit_summaries/x.md"):
            self.assertTrue(sp.is_science_gated_path(path, MANIFEST), path)
        for path in ("docs/x.md", "README.md", "researchers.md", "tools/research/x.md"):
            self.assertFalse(sp.is_science_gated_path(path, MANIFEST), path)
        self.assertTrue(sp.is_science_gated_path("docs/x.md", manifest(science_gated_prefixes=[])))  # fail closed


class ReviewReuseAcrossMainDrift(unittest.TestCase):
    def blobs(self, **changes):
        out = {path: A for path in sp.policy_blob_paths(MANIFEST)}
        out["scripts/governance/s1_diff_scan_v1.py"] = sp.ABSENT
        out.update(changes)
        return out

    def decide(self, **changes):
        args = dict(release_class="DOCS_ONLY", pr_paths=["docs/guide.md"], pr_rename_sources=[],
                    drift_paths=["02_DATA_PING/2026/11/x.json", "scripts/data_ping/compass_event_refresh.py",
                                 "some/unclassified/thing.bin"],
                    drift_census_complete=True, policy_blobs_at_review_main=self.blobs(),
                    policy_blobs_at_current_main=self.blobs(), manifest=MANIFEST)
        args.update(changes)
        return sp.review_reuse_decision(**args)

    def test_unrelated_drift_of_any_class_allows_docs_only_reuse(self):
        got = self.decide()
        self.assertEqual((got["reuse"], got["reason"]), (True, "DISJOINT_AND_POLICY_UNCHANGED"))
        self.assertEqual(self.decide(drift_paths=[])["reuse"], True)

    def test_low_code_and_other_classes_never_reuse(self):
        self.assertEqual(self.decide(release_class="LOW_CODE")["reason"], "LOW_CODE_REQUIRES_REREVIEW")
        for cls in ("HIGH_IMPACT", "GOVERNANCE_WORKFLOW", None, ""):
            self.assertEqual(self.decide(release_class=cls)["reason"], "CLASS_NOT_ELIGIBLE")

    def test_pr_path_or_rename_source_in_drift_blocks(self):
        self.assertEqual(self.decide(drift_paths=["docs/guide.md"])["reason"], "PR_PATH_IN_DRIFT")
        got = self.decide(pr_rename_sources=["docs/old.md"], drift_paths=["docs/old.md"])
        self.assertEqual((got["reason"], got["paths"]), ("PR_PATH_IN_DRIFT", ["docs/old.md"]))

    def test_incomplete_census_or_bad_lists_block(self):
        for flag in (False, None, "true", 1):
            self.assertEqual(self.decide(drift_census_complete=flag)["reason"], "DRIFT_CENSUS_INCOMPLETE")
        for key, bad in (("pr_paths", []), ("pr_paths", None), ("pr_paths", ["../x"]), ("drift_paths", None),
                         ("drift_paths", ["/abs"]), ("pr_rename_sources", "docs/old.md"), ("drift_paths", [1])):
            with self.subTest(key=key, bad=bad):
                self.assertEqual(self.decide(**{key: bad})["reason"], "PATH_LIST_UNUSABLE")

    def test_every_policy_file_in_drift_blocks(self):
        for path in sp.policy_blob_paths(MANIFEST):
            with self.subTest(path=path):
                got = self.decide(drift_paths=["02_DATA_PING/x.json", path])
                self.assertEqual((got["reuse"], got["reason"]), (False, "POLICY_PATH_IN_DRIFT"))

    def test_policy_set_covers_agents_recipe_manifest_classifier_scanner_workflows_and_closure(self):
        policy = set(sp.policy_blob_paths(MANIFEST))
        for path in ["AGENTS.md", "00_FMOS/S1_NATIVE_RULE_CENSUS_AND_RELEASE_RECIPE_V1.md", sp.MANIFEST_PATH,
                     "scripts/governance/s1_release_evidence_classifier_v1.py", "scripts/governance/s1_diff_scan_v1.py",
                     "scripts/governance/s1_standing_policy_v1.py", ".github/workflows/data-architecture-gate.yml",
                     ".github/workflows/storage-health-gate.yml"] + MANIFEST["required_job_executed_paths"]:
            self.assertIn(path, policy)

    def test_changed_or_unproven_policy_blob_blocks_even_when_not_listed_in_drift(self):
        for path in sp.policy_blob_paths(MANIFEST):
            with self.subTest(path=path):
                self.assertEqual(self.decide(policy_blobs_at_current_main=self.blobs(**{path: B}))["reason"],
                                 "POLICY_BLOB_CHANGED")
        missing = self.blobs(); del missing["AGENTS.md"]
        self.assertEqual(self.decide(policy_blobs_at_current_main=missing)["reason"], "POLICY_BLOB_UNPROVEN")
        self.assertEqual(self.decide(policy_blobs_at_review_main=missing)["reason"], "POLICY_BLOB_UNPROVEN")
        for bad in ("abc", "", None, A.upper(), 1):
            self.assertEqual(self.decide(policy_blobs_at_review_main=self.blobs(**{"AGENTS.md": bad}),
                                         policy_blobs_at_current_main=self.blobs(**{"AGENTS.md": bad}))["reason"],
                             "POLICY_BLOB_UNPROVEN")
        self.assertEqual(self.decide(policy_blobs_at_current_main=None)["reason"], "POLICY_BLOB_UNPROVEN")
        # a scanner that appears between the two mains is a change
        self.assertEqual(self.decide(policy_blobs_at_current_main=self.blobs(
            **{"scripts/governance/s1_diff_scan_v1.py": B}))["reason"], "POLICY_BLOB_CHANGED")

    def test_unusable_manifest_blocks(self):
        self.assertEqual(self.decide(manifest=None)["reason"], "MANIFEST_UNUSABLE")
        self.assertEqual(self.decide(manifest={"contract": "OTHER"})["reason"], "MANIFEST_UNUSABLE")

    def test_agents_d3_states_the_same_rule(self):
        self.assertIn("The class of the unrelated drift paths is NOT tested", AGENTS)
        self.assertIn("LOW_CODE never reuses", AGENTS)
        self.assertNotIn("drift paths are exclusively LOW/public data or documentation", AGENTS)
        self.assertEqual(MANIFEST["review_reuse"]["classes"], ["DOCS_ONLY"])


if __name__ == "__main__":
    unittest.main()
