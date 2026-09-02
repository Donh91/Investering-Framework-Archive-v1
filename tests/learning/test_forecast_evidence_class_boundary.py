from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from forecast_evidence_class import (  # noqa: E402
    AUTOMATED_EXPERIMENT,
    LEGACY_UNCLASSIFIED,
    OWNER_RATIFIED,
    EvidenceClassError,
    assert_same_evidence_class,
    classify_forecast_evidence,
    scientific_pool_compatibility_key,
)
from audit_forecast_evidence_class_boundary import build_audit  # noqa: E402


def owner_forecast(fid: str = "owner-1"):
    return {
        "contract": "FROZEN_FORECAST_v1",
        "forecast_id": fid,
        "candidate_id": "candidate-1",
        "frozen_at_utc": "2026-09-02T10:20:00Z",
        "ratification_contract": "FORECAST_RATIFICATION_PACKET_v2",
        "ratification_outcome_blind": True,
        "authority": {"portfolio_action": False, "canonical_promotion": False},
    }


def experiment_forecast(fid: str = "exp-1"):
    return {
        "contract": "FROZEN_FORECAST_v1",
        "forecast_id": fid,
        "source_candidate_id": "EC-1",
        "frozen_at_utc": "2026-09-02T10:20:00Z",
        "experimental_only": True,
        "scientific_admission": {
            "contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_v1",
            "status": "QUALIFIED_FOR_FORWARD_TEST",
        },
        "authority": {"portfolio_action": False, "canonical_promotion": False},
    }


class ForecastEvidenceClassBoundaryTests(unittest.TestCase):
    def test_owner_ratified_forecast_has_owner_class(self):
        row = owner_forecast()
        self.assertEqual(classify_forecast_evidence(row), OWNER_RATIFIED)
        self.assertEqual(scientific_pool_compatibility_key(row), OWNER_RATIFIED)

    def test_automated_scientific_experiment_has_separate_class(self):
        row = experiment_forecast()
        self.assertEqual(classify_forecast_evidence(row), AUTOMATED_EXPERIMENT)
        self.assertEqual(scientific_pool_compatibility_key(row), AUTOMATED_EXPERIMENT)

    def test_legacy_record_is_explicitly_non_poolable(self):
        row = {"contract": "FROZEN_FORECAST_v1", "forecast_id": "legacy"}
        self.assertEqual(classify_forecast_evidence(row), LEGACY_UNCLASSIFIED)
        self.assertIsNone(scientific_pool_compatibility_key(row))
        with self.assertRaisesRegex(EvidenceClassError, "LEGACY_OR_UNCLASSIFIED_FORECAST_CANNOT_BE_POOLED"):
            assert_same_evidence_class([row])

    def test_cross_class_pooling_is_forbidden(self):
        with self.assertRaisesRegex(EvidenceClassError, "CROSS_EVIDENCE_CLASS_POOLING_FORBIDDEN"):
            assert_same_evidence_class([owner_forecast(), experiment_forecast()])

    def test_conflicting_provenance_signals_fail_closed(self):
        row = owner_forecast()
        row.update({
            "source_candidate_id": "EC-conflict",
            "experimental_only": True,
            "scientific_admission": {
                "contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_v1",
                "status": "QUALIFIED_FOR_FORWARD_TEST",
            },
        })
        with self.assertRaisesRegex(EvidenceClassError, "FORECAST_EVIDENCE_CLASS_CONFLICT_OWNER_AND_EXPERIMENT"):
            classify_forecast_evidence(row)

    def test_live_root_audit_allows_historical_unclassified_but_rejects_cross_root_class(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            owner_root = root / "owner"
            exp_root = root / "experiment"
            owner_root.mkdir()
            exp_root.mkdir()
            (owner_root / "legacy.json").write_text(json.dumps({"contract": "FROZEN_FORECAST_v1", "forecast_id": "legacy"}))
            (owner_root / "owner.json").write_text(json.dumps(owner_forecast()))
            (exp_root / "exp.json").write_text(json.dumps(experiment_forecast()))
            clean = build_audit(owner_root, exp_root)
            self.assertEqual(clean["status"], "PASS")
            self.assertFalse(clean["cross_evidence_class_pooling_allowed"])
            self.assertEqual(clean["evidence_class_counts"][OWNER_RATIFIED], 1)
            self.assertEqual(clean["evidence_class_counts"][AUTOMATED_EXPERIMENT], 1)
            self.assertEqual(clean["evidence_class_counts"][LEGACY_UNCLASSIFIED], 1)

            (owner_root / "wrong.json").write_text(json.dumps(experiment_forecast("wrong")))
            bad = build_audit(owner_root, exp_root)
            self.assertEqual(bad["status"], "FAIL")
            self.assertTrue(any(row["error"] == "EVIDENCE_CLASS_ROOT_MISMATCH" for row in bad["violations"]))


if __name__ == "__main__":
    unittest.main()
