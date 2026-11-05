"""Offline controls for the research-only cross-framework OSS intake."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "04_RESEARCH_LAB/external_specialist_dissection/2026-11-05__CROSS_FRAMEWORK_OSS_SOURCE_SNAPSHOT_v1.json"

class FrameworkWideOssIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj = json.loads(PATH.read_text(encoding="utf-8"))

    def test_source_snapshot_is_not_new_agent_or_paid_policy(self):
        o = self.obj
        self.assertEqual(o["status"], "RESEARCH_ONLY_NO_API_OR_AGENT_EXECUTION_AUTHORITY")
        self.assertEqual(o["authority"], "PUBLIC_SAFE_RESEARCH_ONLY")
        self.assertTrue(any("Do not create a separate research queue" in r for r in o["rules"]))

    def test_all_five_existing_archive_domains_registered(self):
        names = {r["repository"] for r in self.obj["repos_in_scope"]}
        self.assertEqual(names, {
            "Donh91/Investering-Framework-Archive-v1",
            "Donh91/Eksperimenter-framework-",
            "Donh91/Meme-Alpha-Lab",
            "Donh91/Investering-AI-Audit-Bridge",
            "Donh91/CycleNavigator-scores",
        })

    def test_no_private_plane_source_is_ingested(self):
        names = {r["repository"] for r in self.obj["repos_in_scope"]}
        self.assertNotIn("Donh91/secrets", names)
        self.assertTrue(any(r["repository"] == "Donh91/secrets" for r in self.obj["out_of_scope"]))

    def test_pinned_oss_sources_unique_and_method_bounded(self):
        entries = self.obj["entries"]
        self.assertEqual(self.obj["candidate_count"], len(entries))
        self.assertGreaterEqual(len(entries), 16)
        ids = [e["id"] for e in entries]
        self.assertEqual(len(ids), len(set(ids)))
        for e in entries:
            self.assertRegex(e["audit_head_sha"], r"^[0-9a-f]{40}$")
            self.assertTrue(e["repository"] and "/" in e["repository"])
            self.assertTrue(e["source_path"] and ".." not in e["source_path"])
            self.assertTrue(e["existing_owner_overlap"])
            self.assertIn(e["github_license"], {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"})

    def test_news_sources_dedup_existing_merged_mission(self):
        news = [e for e in self.obj["entries"] if e["id"] in {
            "AIHOT_EVENT_FAMILY", "HORIZON_SOURCE_COVERAGE", "XNEWS_PROVIDER_ADAPTERS"}]
        self.assertEqual(len(news), 3)
        self.assertTrue(all(e["recommendation"] == "ALREADY_INTAKED_NO_DUPLICATE" for e in news))

    def test_priority_coverage_is_multi_domain_not_news_only(self):
        lanes = {e["lane"] for e in self.obj["entries"]}
        self.assertTrue({"SUPERVISOR_RELIABILITY", "COMPASS_REGIME_M6",
                         "ALPHA_EXECUTION_REALISM", "TASK2_AND_EXPERIMENTS",
                         "DATA_CAPTURE_QUALITY", "ALPHA_CHAIN_INDEXING"}.issubset(lanes))

    def test_research_only_next_action_stages_and_falsification(self):
        stages = self.obj["stages"]
        self.assertEqual(stages[0], "SOURCE_PINNED")
        self.assertIn("PROSPECTIVE_OUTCOME_GRADED", stages)
        self.assertEqual(stages[-1], "RETAINED_OR_FALSIFIED")

if __name__ == "__main__":
    unittest.main()
