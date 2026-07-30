from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
PROGRAM = ROOT / "04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/research/global_liquidity_causal_chain_v1"


class GlobalLiquidityProgramContractTests(unittest.TestCase):
    def test_control_package_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PROGRAM / "validate_program.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload, {"checks": 19, "failures": 0, "status": "PASS"})

    def test_economic_execution_remains_locked(self) -> None:
        state = json.loads((PROGRAM / "EXECUTION_STATE_v1.json").read_text(encoding="utf-8"))
        p5 = next(row for row in state["phases"] if row["phase"] == "P5_ECONOMIC_TEST_EXECUTION")
        self.assertFalse(p5["allowed"])
        self.assertEqual(p5["status"], "BLOCKED_G20_NO")

    def test_public_claims_have_zero_authority(self) -> None:
        claims = json.loads((PROGRAM / "CLAIM_FREEZE_v1.json").read_text(encoding="utf-8"))
        self.assertTrue(all(value is False for value in claims["authority"].values()))


if __name__ == "__main__":
    unittest.main()
