"""Positive, negative, and mutation-sensitive controls for BUILD_v1 admission."""
import copy
import json
import unittest

from scripts.api_agent import astra_build_admit_v1 as a


class BuildAdmissionTest(unittest.TestCase):
    def setUp(self):
        self.path = "scripts/learning/runner_v1.py"
        self.created = "tests/learning/test_runner_v1.py"
        self.scope = {
            "contract": a.SCOPE_CONTRACT,
            "mission_id": "ASTRA-KOMPAS-BUILD-M1-20261121",
            "main_sha": "a" * 40,
            "test_command_id": "M1",
            "allowlist": ["scripts/learning/**", "tests/learning/**"],
            "source_files": {self.path: {"sha256": "b" * 64, "mode": "100644"},
                             self.created: None},
            "stage": 1,
            "previous_repair": None,
        }
        self.proposal = {
            "status": "BUILD",
            "files": [{"path": self.created, "action": "create",
                       "content": "def test_one():\n    assert 1 == 1\n"}],
            "test_command_id": "M1",
            "rationale": "Add frozen fixture",
            "risks": ["No live authority"],
        }

    def submit(self, proposal=None, scope=None):
        return a.admit(a.canonical(self.proposal if proposal is None else proposal),
                       self.scope if scope is None else scope)

    def rejects(self, reason, proposal=None, scope=None):
        with self.assertRaisesRegex(a.AdmissionBlocked, reason):
            self.submit(proposal, scope)

    def test_valid_create(self):
        result = self.submit()
        self.assertEqual(result["status"], "ADMITTED_UNTRUSTED_CODE_TEST_REQUIRED")
        self.assertEqual(result["files"][0]["action"], "create")
        self.assertFalse(result["sandbox_executed"])
        self.assertFalse(result["paid_authority"])
        self.assertEqual(result["test_command_id"], "M1")

    def test_valid_modify(self):
        p = copy.deepcopy(self.proposal)
        p["files"] = [{"path": self.path, "action": "modify",
                       "content": "def run():\n    return 1\n"}]
        v = self.submit(p)
        self.assertEqual(v["files"][0]["preimage_sha256"], "b" * 64)

    def test_valid_abstention(self):
        p = copy.deepcopy(self.proposal)
        p["status"] = "ABSTAIN"
        p["files"] = []
        self.assertEqual(self.submit(p)["status"], "ABSTAINED")

    def test_abstention_cannot_create(self):
        p = copy.deepcopy(self.proposal)
        p["status"] = "ABSTAIN"
        self.rejects("ABSTAIN_WITH_FILES", p)

    def test_no_empty_build(self):
        p = copy.deepcopy(self.proposal)
        p["files"] = []
        self.rejects("BUILD_WITHOUT_FILES", p)

    def test_model_cannot_supply_command(self):
        p = copy.deepcopy(self.proposal)
        p["shell_command"] = "curl https://example.org"
        self.rejects("PROPOSAL_SCHEMA", p)

    def test_model_cannot_change_fixed_command(self):
        p = copy.deepcopy(self.proposal)
        p["test_command_id"] = "M3"
        self.rejects("MODEL_SELECTED_DIFFERENT_TEST", p)

    def test_model_cannot_modify_scope(self):
        p = copy.deepcopy(self.proposal)
        p["allowlist"] = [".github/**"]
        self.rejects("PROPOSAL_SCHEMA", p)

    def test_scope_cannot_expand_allowlist(self):
        s = copy.deepcopy(self.scope)
        s["allowlist"].append(".github/**")
        self.rejects("SCOPE_ALLOWLIST", scope=s)

    def test_scope_cannot_add_other_mission_path(self):
        s = copy.deepcopy(self.scope)
        s["source_files"]["scripts/api_agent/check_monthly_cost_guard.py"] = None
        self.rejects("SOURCE_OUTSIDE_SCOPE|PATH_PROTECTED", scope=s)

    def test_protected_paths(self):
        examples = (".github/workflows/x.yml", "00_FMOS/S1/BOOTSTRAP.txt",
                    "AGENTS.md", ".agents/a.md", "vault/x.py",
                    "secrets/x.py", "03_DAILY_CAPTURE_LOGS/x.json",
                    "research/api_agent/outputs/x.json",
                    "foo/private/bar.py", "foo/round_3/x.py",
                    "07/../x.py", "/root/x.py", "foo//x.py",
                    "foo\\x.py", "foo/x.exe")
        for path in examples:
            with self.subTest(path=path), self.assertRaises(a.AdmissionBlocked):
                a.safe_path(path)

    def test_duplicate_file(self):
        p = copy.deepcopy(self.proposal)
        p["files"].append(copy.deepcopy(p["files"][0]))
        self.rejects("FILE_OUT_OF_SCOPE_OR_DUPLICATED", p)

    def test_create_existing_denied(self):
        p = copy.deepcopy(self.proposal)
        p["files"][0]["path"] = self.path
        self.rejects("ACTION_PREIMAGE_MISMATCH", p)

    def test_modify_missing_denied(self):
        p = copy.deepcopy(self.proposal)
        p["files"][0]["action"] = "modify"
        self.rejects("ACTION_PREIMAGE_MISMATCH", p)

    def test_modified_scope_rejects_symlink_mode(self):
        s = copy.deepcopy(self.scope)
        s["source_files"][self.path]["mode"] = "120000"
        self.rejects("SOURCE_PREIMAGE", scope=s)

    def test_missing_original_blob_rejected(self):
        s = copy.deepcopy(self.scope)
        s["source_files"][self.path]["sha256"] = None
        self.rejects("SOURCE_PREIMAGE", scope=s)

    def test_path_traversal_in_file(self):
        p = copy.deepcopy(self.proposal)
        p["files"][0]["path"] = "scripts/learning/../../.github/x.py"
        self.rejects("PATH_TRAVERSAL", p)

    def test_oversized_single_file(self):
        p = copy.deepcopy(self.proposal)
        p["files"][0]["content"] = "x" * (a.MAX_FILE_BYTES + 1)
        self.rejects("FILE_TOO_LARGE", p)

    def test_oversized_bundle(self):
        # 4 separately scoped files, each individually within 120KB.
        p = copy.deepcopy(self.proposal)
        s = copy.deepcopy(self.scope)
        rows = []
        for i in range(4):
            path = f"scripts/learning/new_{i}.py"
            s["source_files"][path] = None
            rows.append({"path": path, "action": "create", "content": "x" * 110_000})
        p["files"] = rows
        self.rejects("BUNDLE_TOO_LARGE", p, s)

    def test_binary_nul_rejected(self):
        p = copy.deepcopy(self.proposal)
        p["files"][0]["content"] = "abc\x00"
        self.rejects("CONTENT_NOT_TEXT", p)

    def test_control_character_rejected(self):
        p = copy.deepcopy(self.proposal)
        p["files"][0]["content"] = "abc\x1b"
        self.rejects("CONTENT_NOT_TEXT", p)

    def test_secret_text_rejected(self):
        p = copy.deepcopy(self.proposal)
        p["files"][0]["content"] = "secret = 'sk-proj-" + "A" * 40 + "'\n"
        self.rejects("CREDENTIAL_PATTERN", p)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(a.AdmissionBlocked):
            a.admit(b'{"status":"BUILD","status":"ABSTAIN"}', self.scope)

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(a.AdmissionBlocked):
            a.admit(b'{"status":NaN}', self.scope)

    def test_non_utf8_json_rejected(self):
        with self.assertRaises(a.AdmissionBlocked):
            a.admit(b"\xff", self.scope)

    def test_overlarge_raw_json_rejected(self):
        with self.assertRaises(a.AdmissionBlocked):
            a.admit(b" " * (a.MAX_RAW_JSON_BYTES + 1), self.scope)

    def test_source_preimage_required(self):
        s = copy.deepcopy(self.scope)
        del s["source_files"][self.created]
        self.rejects("FILE_OUT_OF_SCOPE_OR_DUPLICATED", scope=s)

    def test_repair_requires_native_failed_receipt(self):
        s = copy.deepcopy(self.scope)
        s["stage"] = 2
        self.rejects("REPAIR_EVIDENCE_MISSING", scope=s)
        s["previous_repair"] = {"mission_id": s["mission_id"], "stage": 1,
                                "status": "VERIFIED_SANDBOX_TEST_FAILURE",
                                "test_receipt_sha256": "c" * 64}
        self.assertEqual(self.submit(scope=s)["stage"], 2)
        s["previous_repair"]["status"] = "SUCCESS"
        self.rejects("REPAIR_EVIDENCE_MISSING", scope=s)

    def test_boolean_stage_not_integer(self):
        s = copy.deepcopy(self.scope)
        s["stage"] = True
        self.rejects("SCOPE_STAGE", scope=s)

    def test_untrusted_scope_not_accepted_as_release(self):
        v = self.submit()
        self.assertFalse(v["merged"])
        self.assertFalse(v["sandbox_executed"])
        self.assertNotIn("command", v)


if __name__ == "__main__":
    unittest.main()
