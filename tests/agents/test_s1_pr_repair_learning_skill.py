"""Static, adversarial routing checks for the repository-local S1 skill."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/s1-pr-repair-learning/SKILL.md"
CASES = ROOT / ".agents/skills/s1-pr-repair-learning/references/verified-casebook.json"

class S1RepairLearningSkillTest(unittest.TestCase):
    def test_installed_skill_and_triggers(self):
        body = SKILL.read_text(encoding="utf-8")
        self.assertTrue(body.startswith("---\nname: s1-pr-repair-learning\n"))
        for marker in ("PROCESS_STALLED", "merge base", "adversarial negatives",
                       "native merge", "postmerge", "CANDIDATE_ONLY", "skill-quality-gate",
                       "Sol MAX", "original PR", "AGENTS.md"):
            self.assertIn(marker.lower(), body.lower())
        self.assertNotIn("AUTO_APPROVE", body)
        self.assertNotIn("AUTO_PAID_DISPATCH", body)

    def test_routing_is_discoverable_but_not_new_authority(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        registry = (ROOT / "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/s1-pr-repair-learning/SKILL.md", agents)
        self.assertIn(".agents/skills/s1-pr-repair-learning/SKILL.md", registry)
        self.assertIn("existing", agents.split("### 0.2b S1", 1)[1].split("### 0.3", 1)[0].lower())
        self.assertIn("no new", registry.lower())

    def test_cases_separate_merge_from_production(self):
        packet = json.loads(CASES.read_text(encoding="utf-8"))
        self.assertEqual(packet["contract"], "S1_PR_REPAIR_LEARNING_CASEBOOK_v1")
        self.assertEqual({x["original_pr"] for x in packet["examples"]}, {1879, 1889, 1900})
        self.assertTrue(all(x["merge_confirmed"] for x in packet["examples"]))
        self.assertTrue(all("not" in x["verified_limit"].lower() or
                            "remain" in x["verified_limit"].lower() or
                            "requires" in x["verified_limit"].lower()
                            for x in packet["examples"]))
        self.assertGreaterEqual(len(packet["negative_controls"]), 6)

if __name__ == "__main__":
    unittest.main()
