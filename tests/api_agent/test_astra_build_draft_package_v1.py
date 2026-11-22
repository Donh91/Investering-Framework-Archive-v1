"""No-secret draft staging, original full-file content and deny-on-drift."""
import copy
import json
import unittest

from scripts.api_agent import astra_build_admit_v1 as admit
from scripts.api_agent import astra_build_draft_package_v1 as draft


class DraftPackageTest(unittest.TestCase):
    def setUp(self):
        self.scope = {
            "contract": admit.SCOPE_CONTRACT,
            "mission_id": "ASTRA-BUILD-M1-20261121-S1",
            "main_sha": "b"*40,
            "test_command_id": "M1",
            "allowlist": ["scripts/learning/**", "tests/learning/**"],
            "source_files": {
                "scripts/learning/model.py": {"sha256": "f"*64, "mode": "100644"},
                "tests/learning/test_new_model.py": None
            },
            "stage": 1, "previous_repair": None
        }
        self.content = {
            "status": "BUILD", "test_command_id": "M1",
            "rationale": "Synthetic model full file", "risks": [],
            "files": [{"path": "tests/learning/test_new_model.py",
                       "action": "create", "content": "def test_new():\n    assert True\n"}]
        }
        self.raw = admit.canonical(self.content)
        admission = admit.admit(self.raw, self.scope)
        self.verdict = {
            "contract": "ASTRA_BUILD_EVIDENCE_BINDING_v1",
            "status": draft.ELIGIBLE,
            "mission_id": self.scope["mission_id"],
            "release_main_sha": self.scope["main_sha"],
            "fixed_test_id": "M1",
            "raw_model_response_sha256": admit.digest(self.raw),
            "admission_sha256": admit.digest(admit.canonical(admission)),
            "paid_authority": False,
            "merge_authority": False,
            "review_required": True,
            "independent_native_pr_ci_pending": True,
            "output_eligibility": "ONE_DRAFT_PR_NO_AUTOMERGE",
        }

    def invoke(self, verdict=None, raw=None):
        return draft.build(raw=self.raw if raw is None else raw,
                           scope=self.scope,
                           verdict=self.verdict if verdict is None else verdict)

    def test_full_file_is_in_package_with_exact_bound_preimage(self):
        data = self.invoke()
        obj = json.loads(data)
        self.assertEqual(obj["status"], "STAGED_FOR_ONE_DRAFT_PR")
        self.assertEqual(obj["mission_id"], self.scope["mission_id"])
        self.assertEqual(obj["main_sha"], self.scope["main_sha"])
        self.assertEqual(len(obj["files"]), 1)
        self.assertEqual(obj["files"][0]["utf8_full_file"],
                         self.content["files"][0]["content"])
        self.assertEqual(obj["files"][0]["sha256"],
                         admit.digest(obj["files"][0]["utf8_full_file"].encode()))
        self.assertIsNone(obj["files"][0]["preimage_sha256"])
        self.assertFalse(obj["permissions"]["git_write_performed"])
        self.assertFalse(obj["permissions"]["merge_performed"])
        self.assertEqual(obj["review"]["pr_mode"], "DRAFT_ONLY")
        self.assertEqual(obj["review"]["native_ci"], "MUST_RUN_ON_EXACT_OUTPUT_PR_HEAD")

    def test_noneligible_or_forged_native_ci_is_blocked(self):
        for k, value in [("status", "TEST_COMPLETION_HOLD"),
                         ("merge_authority", True), ("paid_authority", True),
                         ("independent_native_pr_ci_pending", False),
                         ("review_required", False),
                         ("output_eligibility", "AUTOMERGE")]:
            with self.subTest(k=k):
                v = copy.deepcopy(self.verdict)
                v[k] = value
                with self.assertRaises(draft.DraftPackageBlocked):
                    self.invoke(v)

    def test_changed_model_report_without_receipt_is_blocked(self):
        model = copy.deepcopy(self.content)
        model["files"][0]["content"] = "def changed():\n    return False\n"
        with self.assertRaisesRegex(draft.DraftPackageBlocked, "DRAFT_REPORT_SHA_DRIFT"):
            self.invoke(raw=admit.canonical(model))

    def test_mismatch_mission_and_main_denied(self):
        for key,value in (("mission_id","ASTRA-BUILD-M2-20261121-S1"),
                          ("release_main_sha","c"*40),
                          ("fixed_test_id","M3")):
            v=copy.deepcopy(self.verdict)
            v[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(
                    draft.DraftPackageBlocked,"DRAFT_MISSION_OR_MAIN_DRIFT"):
                self.invoke(v)

    def test_no_files_abstention_cannot_produce_a_draft(self):
        abstain = admit.canonical({"status":"ABSTAIN","files":[],
                                  "test_command_id":"M1",
                                  "rationale":"Abstain", "risks":[]})
        v=dict(self.verdict,raw_model_response_sha256=admit.digest(abstain))
        with self.assertRaises(draft.DraftPackageBlocked):
            self.invoke(v,abstain)


if __name__=="__main__":
    unittest.main()
