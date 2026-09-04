from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "create_forecast_skill_cohort_activation.py"


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


class ForecastSkillActivationGovernanceT13Tests(unittest.TestCase):
    def fixture(self, root: Path):
        prereg = b'{"contract":"FORECAST_SKILL_PREREGISTRATION_v1_3_1"}\n'
        erratum = b'{"contract":"FORECAST_SKILL_PREREGISTRATION_v1_3_2_ERRATUM"}\n'
        prereg_path = root / "prereg.json"
        erratum_path = root / "erratum.json"
        acceptance_path = root / "acceptance.json"
        active_path = root / "active.json"
        output = root / "activation.json"
        prereg_path.write_bytes(prereg)
        erratum_path.write_bytes(erratum)
        acceptance = {
            "contract": "FORECAST_SKILL_PREREGISTRATION_ACCEPTANCE_v1",
            "status": "ACCEPTED_MERGED_READBACK_VERIFIED",
            "study_id": "FORECAST_SKILL_CONFIRMATORY_V1_3_1",
            "preregistration": {"git_blob_sha1": git_blob_sha1(prereg)},
            "endpoint_erratum": {"git_blob_sha1": git_blob_sha1(erratum)},
            "implementation_merge_sha": "1" * 40,
            "implementation_ancestor_of_readback": True,
            "pre_activation_rows_allowed": False,
            "historical_replay_allowed": False,
            "outcome_data_read": False,
            "authority": {
                "forecast_skill_claim": False,
                "portfolio_action": False,
                "model_weight_change": False,
                "automatic_promotion": False,
            },
        }
        active = {
            "contract": "FORECAST_SKILL_ACTIVE_TEST_REGISTRATION_v1_3_2",
            "status": "REGISTERED_PRE_ACTIVATION",
            "test_id": "FORECAST_SKILL_CONFIRMATORY_V1_3_1",
            "preregistration_acceptance_contract": "FORECAST_SKILL_PREREGISTRATION_ACCEPTANCE_v1",
            "preregistration_git_blob_sha1": git_blob_sha1(prereg),
            "endpoint_erratum_git_blob_sha1": git_blob_sha1(erratum),
            "implementation_merge_sha": "1" * 40,
            "primary_population": {
                "pre_activation_rows_allowed": False,
                "historical_replay_allowed": False,
                "automated_scientific_experiment_pooling_allowed": False,
            },
            "outcome_data_read": False,
            "activation_allowed_only_after_registration_merge_readback": True,
            "authority": {
                "forecast_skill_claim": False,
                "portfolio_action": False,
                "model_weight_change": False,
                "automatic_promotion": False,
            },
        }
        acceptance_path.write_text(json.dumps(acceptance))
        active_path.write_text(json.dumps(active))
        return prereg_path, erratum_path, acceptance_path, active_path, output, acceptance, active

    def run_script(self, prereg, erratum, acceptance, active, output):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--preregistration", str(prereg),
                "--endpoint-erratum", str(erratum),
                "--preregistration-acceptance", str(acceptance),
                "--active-test-registration", str(active),
                "--implementation-main-sha", "1" * 40,
                "--implementation-readback-at-utc", "2026-09-03T20:55:00Z",
                "--recorded-at-utc", "2026-09-03T21:00:00Z",
                "--output", str(output),
            ],
            capture_output=True,
            text=True,
        )

    def test_valid_governance_bindings_create_prospective_activation(self):
        with tempfile.TemporaryDirectory() as td:
            values = self.fixture(Path(td))
            proc = self.run_script(*values[:5])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            activation = json.loads(values[4].read_text())
            self.assertTrue(activation["governance_prerequisites_verified"])
            self.assertEqual(activation["cohort_start_utc"], "2026-09-04T00:00:00Z")
            self.assertEqual(activation["cohort_end_utc_exclusive"], "2027-05-02T00:00:00Z")
            self.assertFalse(activation["outcome_data_read"])

    def test_active_test_implementation_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            values = self.fixture(Path(td))
            active = values[6]
            active["implementation_merge_sha"] = "2" * 40
            values[3].write_text(json.dumps(active))
            proc = self.run_script(*values[:5])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("ACTIVE_TEST_IMPLEMENTATION_SHA_MISMATCH", proc.stderr + proc.stdout)

    def test_authority_leak_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            values = self.fixture(Path(td))
            active = values[6]
            active["authority"]["forecast_skill_claim"] = True
            values[3].write_text(json.dumps(active))
            proc = self.run_script(*values[:5])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("ACTIVE_TEST_REGISTRATION_AUTHORITY_LEAK:forecast_skill_claim", proc.stderr + proc.stdout)

    def test_preregistration_blob_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            values = self.fixture(Path(td))
            values[0].write_text('{"contract":"FORECAST_SKILL_PREREGISTRATION_v1_3_1","drift":true}\n')
            proc = self.run_script(*values[:5])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("PREREGISTRATION_ACCEPTANCE_BLOB_MISMATCH", proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
