"""Verify HRE clock lessons are reusable without silently auto-promoting new skills."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ACTIVE = ROOT / ".agents/skills/research-parallel-lanes/SKILL.md"
REF = ROOT / ".agents/skills/research-parallel-lanes/references/HRE_REPLAY_SOURCE_CLOCK_FAILSAFE.md"
CANDIDATE = ROOT / "07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/hre/historical-replay-clock-integrity/SKILL.md"
REGISTRY = ROOT / "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md"
ROUTING = ROOT / "00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json"

class HistoricalClockReferenceTests(unittest.TestCase):
    def test_active_research_parallel_lanes_routes_reference(self):
        self.assertIn("references/HRE_REPLAY_SOURCE_CLOCK_FAILSAFE.md", ACTIVE.read_text())
        self.assertIn("completed-bar clock", ACTIVE.read_text())

    def test_reproducible_clock_trap_is_cited(self):
        ref=REF.read_text()
        for s in ["1582112132286", "Nominal", "72h", "UNKNOWN", "SOURCE", "2025", "USDT", "PR #2010"]:
            self.assertIn(s.lower(), ref.lower())

    def test_proposed_standalone_skill_is_unregistered(self):
        candidate=CANDIDATE.read_text()
        self.assertTrue(candidate.startswith("---\n"))
        self.assertIn("CANDIDATE_ONLY",candidate)
        self.assertIn("NO_AUTOMATIC_INVOCATION",candidate)
        self.assertIn("NOT_RUN",candidate)
        self.assertNotIn("historical-replay-clock-integrity",REGISTRY.read_text())
        self.assertNotIn('"name": "historical-replay-clock-integrity"',ROUTING.read_text())

    def test_candidate_explicit_negative_triggers_and_authority(self):
        c=CANDIDATE.read_text()
        for s in ("Negative:", "baseline", "without", "paid", "original", "source", "missing"):
            self.assertIn(s.lower(),c.lower())
        self.assertIn("no new", REF.read_text().lower())

    def test_reference_relative_link_points_to_real_research(self):
        path = (REF.parent / "../../../../research/historical_reality_engine/README.md").resolve()
        self.assertEqual(path,ROOT/"research/historical_reality_engine/README.md")
        self.assertTrue(path.exists())

if __name__=="__main__":
    unittest.main()
