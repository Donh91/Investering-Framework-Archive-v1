"""Only a token-bearing runtime audit may publish canonical Automation Health.

build_automation_health.py without --token cannot see any workflow run; every
row becomes WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE and the report is AMBER
with zero RED. Framework Learning Operations used to write that blind report
over research/architecture_health/LATEST_AUTOMATION_HEALTH.json on every
successful run (e.g. 574daaaae, 2026-09-15: RED 7 -> AMBER 0), and remediation
maturation consumed such reports on 2026-08-31 and 2026-09-04.
"""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
CANONICAL = "research/architecture_health/LATEST_AUTOMATION_HEALTH"


def _logical_lines(text: str) -> list[str]:
    """Join shell line continuations so one command is one line (no YAML dependency)."""
    return re.sub(r"\\\s*\n\s*", " ", text).splitlines()


def canonical_automation_health_writers(workflow_root: Path) -> list[tuple[str, str]]:
    """Return (workflow, command) for every command that writes canonical automation health."""
    writers = []
    for path in sorted(workflow_root.glob("*.y*ml")):
        for line in _logical_lines(path.read_text()):
            if "build_automation_health" in line and CANONICAL in line:
                writers.append((path.name, " ".join(line.split())))
    return writers


def is_token_bearing_runtime_audit(command: str) -> bool:
    return "build_automation_health_runtime.py" in command and "--token" in command and "--repo" in command


class CanonicalAutomationHealthWriterTest(unittest.TestCase):
    def test_every_canonical_writer_is_token_bearing_runtime_audit(self):
        writers = canonical_automation_health_writers(WORKFLOWS)
        self.assertTrue(writers, "the canonical owner workflow must still exist")
        offenders = [(name, cmd) for name, cmd in writers if not is_token_bearing_runtime_audit(cmd)]
        self.assertEqual(offenders, [])

    def test_owner_is_automation_production_health(self):
        names = {name for name, _ in canonical_automation_health_writers(WORKFLOWS)}
        self.assertEqual(names, {"automation-production-health.yml"})

    def test_detector_flags_tokenless_canonical_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            (fixture / "bad.yml").write_text(
                "on: {workflow_dispatch: {}}\n"
                "jobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n"
                "      - run: |\n"
                "          python scripts/health/build_automation_health.py \\\n"
                "            --workflow-root .github/workflows \\\n"
                f"            --json-output {CANONICAL}.json \\\n"
                f"            --md-output {CANONICAL}.md\n"
            )
            writers = canonical_automation_health_writers(fixture)
            self.assertEqual(len(writers), 1)
            self.assertFalse(is_token_bearing_runtime_audit(writers[0][1]))


if __name__ == "__main__":
    unittest.main()
