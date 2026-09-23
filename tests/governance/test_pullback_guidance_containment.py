from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.governance.pullback_guidance_containment import (
    REQUIRED_REPRO_FIELDS,
    inspect_text,
    scan_repo,
)


class PullbackGuidanceContainmentTests(unittest.TestCase):
    def test_guidance_only_descriptive_usage_passes(self) -> None:
        text = """
        PULLBACK_POLICY_V0_2_STATUS: GUIDANCE_ONLY
        Pullback Moderate is descriptive context for human review.
        Qualitative label alone MUST NOT trigger REDUCE, rebuy or calibration.
        """
        self.assertEqual(inspect_text(text), [])

    def test_direct_moderate_to_reduce_mapping_fails(self) -> None:
        text = "pullback_label: Moderate\nModerate -> REDUCE"
        findings = inspect_text(text)
        self.assertTrue(findings)
        self.assertTrue(any(row["direct_mapping"] for row in findings))

    def test_label_alone_cannot_unlock_rebuy(self) -> None:
        text = '{"pullback_label":"Large","rebuy_status":"ACTIVE","context":"pullback"}'
        findings = inspect_text(text)
        self.assertTrue(findings)
        self.assertTrue(any(row["structured_mapping"] for row in findings))

    def test_label_alone_cannot_create_recovery_failure(self) -> None:
        text = '{"pullback_label":"Extreme","recovery_failure":"TRUE","context":"pullback"}'
        self.assertTrue(inspect_text(text))

    def test_label_alone_cannot_create_calibration_hit(self) -> None:
        text = '{"pullback_label":"Mild","calibration_outcome":"HIT","context":"pullback"}'
        self.assertTrue(inspect_text(text))

    def test_fully_specified_owner_authorized_future_artifact_passes(self) -> None:
        rows = {field: "source-backed" for field in REQUIRED_REPRO_FIELDS}
        fields = "\n".join(f"{key}: {value}" for key, value in rows.items())
        text = f"""
        context: pullback
        owner_authorized: true
        pullback_label: Moderate
        action: REDUCE
        {fields}
        """
        self.assertEqual(inspect_text(text), [])

    def test_conditional_mapping_fails(self) -> None:
        text = '''
        if pullback_label == "Moderate":
            return {"action": "REDUCE"}
        '''
        self.assertTrue(inspect_text(text))

    def test_current_active_surface_passes(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        result = scan_repo(repo)
        self.assertGreater(result["scanned_path_count"], 0)
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["market_semantic_change"])
        self.assertFalse(result["threshold_change"])
        self.assertFalse(result["portfolio_authority_change"])


if __name__ == "__main__":
    unittest.main()
