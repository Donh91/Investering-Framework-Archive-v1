from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


class AnalysisToActionTranslationContractTests(unittest.TestCase):
    def test_contract_validator_passes(self) -> None:
        root = Path(__file__).resolve().parents[2]
        script = root / "research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/analysis_to_action_translation_audit_v1/validate_aata.py"
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["rows"], 4)
        self.assertEqual(payload["new_economic_scores"], 0)
        self.assertFalse(payload["final_holdout_opened"])


if __name__ == "__main__":
    unittest.main()
