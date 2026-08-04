from pathlib import Path
import tempfile
import unittest

from scripts.learning.validate_legacy_knowledge_bootstrap import validate

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "04_MARKET_LEARNING/legacy_framework_knowledge_bootstrap_v1"


class LegacyKnowledgeBootstrapTests(unittest.TestCase):
    def test_repository_package_passes(self):
        result = validate(PACKAGE)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertGreaterEqual(result["hypothesis_count"], 5)
        self.assertGreaterEqual(result["queue_count"], 5)

    def test_legacy_rows_never_gain_authority(self):
        result = validate(PACKAGE)
        self.assertEqual(
            result["authority"],
            {
                "portfolio_action": False,
                "framework_state_change": False,
                "model_weight_change": False,
                "canonical_promotion": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
