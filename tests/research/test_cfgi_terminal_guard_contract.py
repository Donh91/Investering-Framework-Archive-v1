from __future__ import annotations

from pathlib import Path
import unittest

from tests.research.cfgi_terminal_guard_contract import (
    FORBIDDEN_PAID_RETRY_MARKERS,
    REQUIRED_TERMINAL_MARKERS,
    validate_terminal_guard_contract,
)


ROOT = Path(__file__).parents[2]
LAUNCHER = ROOT / ".github" / "workflows" / "cfgi-recovery-launch-once.yml"
LAB_GATE = ROOT / ".github" / "workflows" / "historical-altseason-lab-gate.yml"


class TerminalGuardContractTests(unittest.TestCase):
    def test_current_launcher_is_terminal_and_zero_paid_retry(self) -> None:
        validate_terminal_guard_contract(LAUNCHER.read_text())

    def test_rejects_any_reintroduced_paid_retry_capability(self) -> None:
        for unsafe_marker in FORBIDDEN_PAID_RETRY_MARKERS:
            with self.subTest(unsafe_marker=unsafe_marker):
                with self.assertRaisesRegex(AssertionError, "paid retry capability present"):
                    validate_terminal_guard_contract(f"{LAUNCHER.read_text()}\n{unsafe_marker}\n")

    def test_rejects_missing_terminal_guard_evidence(self) -> None:
        for required_marker in REQUIRED_TERMINAL_MARKERS:
            with self.subTest(required_marker=required_marker):
                source = LAUNCHER.read_text().replace(required_marker, "")
                with self.assertRaisesRegex(AssertionError, "missing terminal guard marker"):
                    validate_terminal_guard_contract(source)

    def test_lab_gate_uses_terminal_contract_instead_of_retired_cron(self) -> None:
        gate = LAB_GATE.read_text()
        self.assertIn("validate_terminal_guard_contract(launch)", gate)
        self.assertNotIn('assert "cron: \'*/5 * * * *\'" in launch', gate)


if __name__ == "__main__":
    unittest.main()
