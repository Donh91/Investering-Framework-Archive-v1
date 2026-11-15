"""Until Metronome has passed ACTIVE production proof, cadence is best-effort."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATHS = (
    "scripts/cycle_navigator/build_public_live_precision.py",
    ".github/workflows/cycle-navigator-pages.yml",
    ".github/workflows/cycle-navigator-public-contract-gate.yml",
    "05_CYCLE_NAVIGATOR/site/validate-v2.mjs",
)


class CadenceTruthTests(unittest.TestCase):
    def test_all_producer_and_gates_match_best_effort(self):
        for path in PATHS:
            with self.subTest(path=path):
                content = (ROOT / path).read_text()
                self.assertIn("BEST_EFFORT_EVENT_CHAIN", content)
                self.assertNotIn("HOURLY_OWNER_CHAIN", content)

    def test_source_never_claims_metronome_without_active_proof(self):
        producer = (ROOT / PATHS[0]).read_text()
        self.assertIn('"refresh_cadence": "BEST_EFFORT_EVENT_CHAIN"', producer)
        self.assertNotIn('"refresh_cadence": "METRONOME_HOURLY_CHAIN"', producer)


if __name__ == "__main__":
    unittest.main()
