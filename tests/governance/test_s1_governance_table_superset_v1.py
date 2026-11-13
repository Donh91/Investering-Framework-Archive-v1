"""Grok R5RT-F3 (Bridge PR #183): the manifest governance table must be at least as strict
as the release classifier's `_release_sensitive_path` and the privacy scanner's blocked
prefixes. A path any of those treats as sensitive must be governance per the manifest."""
import json
import unittest
from pathlib import Path

from scripts.governance.s1_release_evidence_classifier_v1 import _release_sensitive_path
from scripts.governance.s1_standing_policy_v1 import is_governance_path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json").read_text())

try:  # present once #2091 is on main
    from scripts.governance.s1_diff_scan_v1 import BLOCKED_PREFIXES as SCANNER_PREFIXES
except Exception:  # pragma: no cover - mirror of #2091 @ b8769682
    SCANNER_PREFIXES = (".github/", ".agents/", "00_FMOS/", "00_ARCHIVE_CONTROL/",
                        "research/api_agent/", "private/", "secrets/", "vault/",
                        "config/private/", "data/private/", "08_SOURCE_MATERIAL/private/")

PROBES = [
    "AGENTS.md", "CLAUDE.md", ".github/workflows/x.yml", ".agents/skills/x/SKILL.md",
    "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json", "00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md",
    "01_CORE_FRAMEWORK/governance/guard.md", "scripts/governance/check_codex_review_finality.py",
    "scripts/governance/s1_release_evidence_classifier_v1.py", "tests/governance/test_s1_x.py",
    "research/api_agent/budget.json", "private/x.md", "secrets/x.json", "vault/x",
    "config/private/x.yml", "data/private/x.csv", "08_SOURCE_MATERIAL/private/x.md",
]


class GovernanceTableSupersetTests(unittest.TestCase):
    def test_classifier_sensitive_implies_manifest_governance(self):
        for path in PROBES:
            if _release_sensitive_path(path):
                with self.subTest(path=path):
                    self.assertTrue(is_governance_path(path, MANIFEST))

    def test_scanner_blocked_prefix_implies_manifest_governance(self):
        for prefix in SCANNER_PREFIXES:
            with self.subTest(prefix=prefix):
                self.assertTrue(is_governance_path(prefix + "probe.md", MANIFEST))

    def test_ordinary_docs_path_is_not_governance(self):
        self.assertFalse(is_governance_path("docs/public-notes.md", MANIFEST))


if __name__ == "__main__":
    unittest.main()
