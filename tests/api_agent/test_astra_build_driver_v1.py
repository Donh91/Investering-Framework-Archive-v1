"""No-secret BUILD handoff: original native receipt, source and fixed scope."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.api_agent import astra_build_admit_v1 as a
from scripts.api_agent import astra_build_driver_v1 as d


class TestBuildDriver(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.artifact = self.root / "artifact"
        self.artifact.mkdir()
        self.mid = "ASTRA-BUILD-M1-20261121-S1"
        self.main = "a" * 40
        self.src_path = "scripts/learning/matched.py"
        self.src_raw = b"def matched():\n    return True\n"
        original = self.repo / self.src_path
        original.parent.mkdir(parents=True)
        original.write_bytes(self.src_raw)
        self.spec = {
            "contract": a.SCOPE_CONTRACT,
            "mission_id": self.mid,
            "test_command_id": "M1",
            "allowlist": ["scripts/learning/**", "tests/learning/**"],
            "source_files": {
                self.src_path: {"sha256": hashlib.sha256(self.src_raw).hexdigest(),
                                "mode": "100644"},
                "tests/learning/test_candidate.py": None,
            }, "stage": 1, "previous_repair": None,
        }
        self.spec_path = self.repo / "06_RESEARCH_LAB/astra_missions" / self.mid / d.SCOPE_NAME
        self.spec_path.parent.mkdir(parents=True)
        self.spec_path.write_bytes(a.canonical(self.spec) + b"\n")
        self.bundle_path = self.spec_path.parent / "BUNDLE.md"
        self.bundle_path.write_bytes(
            b"Reviewed source manifest (model-visible)\n" +
            b"<!-- ASTRA_BUILD_SOURCE_MANIFEST_V1\n" +
            a.canonical(self.spec["source_files"]) +
            b"\nEND_ASTRA_BUILD_SOURCE_MANIFEST_V1 -->\n")
        self.native_request = b"fixed_request_bytes"
        self.raw_report = a.canonical({"status": "ABSTAIN", "files": [],
                                       "test_command_id": "M1",
                                       "rationale": "No qualified output", "risks": []})
        self.meta = {
            "contract": "ASTRA_MISSION_REQUEST_V1",
            "mission_id": self.mid, "work_id": self.mid,
            "mission_dir": "06_RESEARCH_LAB/astra_missions/" + self.mid,
            "model": "gpt-6.2-astra", "reasoning_effort": "max", "max_usd": 5.0,
            "request_bytes": len(self.native_request), "request_sha256": a.digest(self.native_request),
            "bundle_sha256": "b" * 64,
        }
        self.source = dict(self.meta, release_main_sha=self.main,
                           trigger_comment_id=123)
        self.paid = {
            "contract": "ASTRA_MISSION_RECEIPT_V1",
            "mission_id": self.mid, "work_id": self.mid,
            "release_main_sha": self.main, "run_id": "25",
            "status": "completed", "incomplete_details": None,
            "no_retry": True, "output_sha256": a.digest(self.raw_report),
            "bytes": len(self.raw_report),
        }
        self.archive = (self.artifact / "archive" / self.meta["mission_dir"] /
                        "results")
        self.archive.mkdir(parents=True)
        self.seed()

    def tearDown(self):
        self.tmp.cleanup()

    def seed(self):
        for base in (self.artifact, self.archive):
            (base / "receipt.json").write_bytes(a.canonical(self.paid) + b"\n")
            (base / "source_manifest.json").write_bytes(a.canonical(self.source) + b"\n")
        (self.archive / "ASTRA_RAW_REPORT.md").write_bytes(self.raw_report)

    def call_verify(self):
        with mock.patch.object(d.owner, "build_request",
                               return_value=({"model": "gpt-6.2-astra"},
                                             self.native_request, self.meta)):
            return d.verify_original_artifact(self.repo, self.artifact,
                                              self.mid, self.main, "25")

    def test_native_event_reverified_independent_of_workflow_if(self):
        request = {"model": "gpt-6.2-astra"}
        body = {"comment": {"id": 1245}}
        with mock.patch.object(d.owner, "owner_event",
                               return_value=(body, self.mid, "b"*64)), \
             mock.patch.object(d.owner, "build_request",
                               return_value=(request, self.native_request,
                                             self.meta)):
            proof = d.verified_native_owner_event(self.mid)
            self.assertEqual(proof["comment_id"], 1245)
            self.assertEqual(proof["mission_id"], self.mid)
        with mock.patch.object(d.owner, "owner_event",
                               return_value=(body, "ASTRA-BUILD-M2-20261121-S1", "b"*64)):
            with self.assertRaisesRegex(d.DriverHold, "OWNER_EVENT_MISSION_DRIFT"):
                d.verified_native_owner_event(self.mid)
        with mock.patch.object(d.owner, "owner_event",
                               return_value=(body, self.mid, "c"*64)), \
             mock.patch.object(d.owner, "build_request",
                               return_value=(request, self.native_request,
                                             self.meta)):
            with self.assertRaisesRegex(d.DriverHold, "OWNER_EVENT_BUNDLE_DRIFT"):
                d.verified_native_owner_event(self.mid)

    def test_model_bundle_must_show_the_exact_reviewed_source_manifest(self):
        first = d.trusted_scope(self.repo, self.mid, self.main)
        self.assertEqual(first["source_files"], self.spec["source_files"])
        self.bundle_path.write_bytes(
            b"<!-- ASTRA_BUILD_SOURCE_MANIFEST_V1\n" +
            a.canonical({"scripts/learning/other.py": None}) +
            b"\nEND_ASTRA_BUILD_SOURCE_MANIFEST_V1 -->\n")
        with self.assertRaisesRegex(d.DriverHold, "BUNDLE_SOURCE_PREIMAGES_DRIFT"):
            d.trusted_scope(self.repo, self.mid, self.main)
        self.bundle_path.write_text("unversioned text\n", encoding="utf-8")
        with self.assertRaisesRegex(d.DriverHold, "BUNDLE_SOURCE_MANIFEST_MISSING"):
            d.trusted_scope(self.repo, self.mid, self.main)

    def test_verified_source_scope_has_real_sha(self):
        result = d.trusted_scope(self.repo, self.mid, self.main)
        self.assertEqual(result["main_sha"], self.main)
        self.assertEqual(result["stage"], 1)
        self.assertEqual(result["test_command_id"], "M1")
        self.assertEqual(len(result["source_files"]), 2)

    def test_source_preimage_drift_rejected(self):
        (self.repo / self.src_path).write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(d.DriverHold, "PREIMAGE_MISMATCH"):
            d.trusted_scope(self.repo, self.mid, self.main)

    def test_scope_cannot_borrow_other_mission(self):
        with self.assertRaisesRegex(d.DriverHold, "MISSION_NOT_STAGE1_BUILD"):
            d.trusted_scope(self.repo, "ASTRA-BUILD-M9-20261121-S1", self.main)

    def test_verified_native_artifact_byte_binding(self):
        raw, source, paid = self.call_verify()
        self.assertEqual(raw, self.raw_report)
        self.assertEqual(source, self.source)
        self.assertEqual(paid, self.paid)

    def test_changed_archived_receipt_is_denied(self):
        (self.archive / "receipt.json").write_bytes(b"{}\n")
        with self.assertRaisesRegex(d.DriverHold, "ARCHIVE_RECEIPT"):
            self.call_verify()

    def test_cross_run_artifact_is_denied(self):
        self.paid["run_id"] = "24"
        self.seed()
        with self.assertRaisesRegex(d.DriverHold, "PAID_RUN_NOT_CURRENT"):
            self.call_verify()

    def test_incomplete_paid_result_denied(self):
        self.paid["status"] = "incomplete"
        self.seed()
        with self.assertRaisesRegex(d.DriverHold, "PAID_NOT_FINAL"):
            self.call_verify()

    def test_raw_digest_bond_enforced(self):
        (self.archive / "ASTRA_RAW_REPORT.md").write_bytes(self.raw_report + b"x")
        with self.assertRaisesRegex(d.DriverHold, "RAW_REPORT_DIGEST_MISMATCH"):
            self.call_verify()

    def test_symlinked_artifact_denied(self):
        (self.archive / "ASTRA_RAW_REPORT.md").unlink()
        (self.archive / "ASTRA_RAW_REPORT.md").symlink_to(self.artifact / "receipt.json")
        with self.assertRaisesRegex(d.DriverHold, "ARTIFACT_UNTRUSTED_FILE"):
            self.call_verify()

    def test_out_of_scope_main_file_refused(self):
        fake = copy.deepcopy(self.spec)
        fake["source_files"][".github/workflows/owner-astra-mission.yml"] = None
        self.spec_path.write_bytes(a.canonical(fake))
        with self.assertRaises(a.AdmissionBlocked):
            d.trusted_scope(self.repo, self.mid, self.main)

    def test_same_job_toolchain_is_revalidated_not_taken_from_model(self):
        image = "sha256:" + "a"*64
        with mock.patch.dict(d.os.environ, {"ASTRA_BUILD_IMAGE_ID": image}), \
             mock.patch.object(d.subprocess, "check_output", return_value=image+"\\n"):
            self.assertEqual(d.verified_same_job_toolchain_image(), image)
        with mock.patch.dict(d.os.environ, {"ASTRA_BUILD_IMAGE_ID": "python:latest"}):
            with self.assertRaisesRegex(d.DriverHold, "TRUSTED_TOOLCHAIN_IMAGE_ID_MISSING"):
                d.verified_same_job_toolchain_image()
        with mock.patch.dict(d.os.environ, {"ASTRA_BUILD_IMAGE_ID": image}), \
             mock.patch.object(d.subprocess, "check_output",
                               return_value="sha256:"+"b"*64+"\\n"):
            with self.assertRaisesRegex(d.DriverHold, "TRUSTED_TOOLCHAIN_IMAGE_DRIFT"):
                d.verified_same_job_toolchain_image()

    def test_runner_never_claims_merge_from_sandbox(self):
        result = {"paid_authority": False,
                  "merge_authority": False,
                  "status": "TESTED_PASS_REVIEW_REQUIRED"}
        with mock.patch.object(d, "verified_head", return_value=self.main), \
             mock.patch.object(d, "trusted_scope", return_value=dict(self.spec, main_sha=self.main)), \
             mock.patch.object(d, "verify_original_artifact",
                               return_value=(self.raw_report, self.source, self.paid)), \
             mock.patch.object(d.admit, "admit", return_value={}), \
             mock.patch.object(d.sandbox, "run_admitted", return_value={}), \
             mock.patch.object(d.binding, "bind", return_value=result):
            self.assertIs(d.run(self.repo, self.artifact, self.mid,
                                self.main, "25"), result)

if __name__ == "__main__":
    unittest.main()
