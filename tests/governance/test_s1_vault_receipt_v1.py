import copy
import json
import unittest

from scripts.governance.s1_vault_receipt_v1 import ISSUE, VAULT, WORKFLOW, bind_technical_receipt


def fixture():
    key = "2026-11-13-run-90-1"
    ref = "refs/heads/agent/task-20261113-recovery-90-1"
    receipt = {
        "schema": "VAULT_NATIVE_RECEIPT_V1", "id": "90-1", "run_id": "90",
        "run_attempt": "1", "vault_repository": VAULT, "workflow_file": WORKFLOW,
        "run_url": f"https://github.com/{VAULT}/actions/runs/90",
        "job_key": "publish_archive_receipt", "workflow_commit": "a" * 40,
        "source_sha": "b" * 40, "source_tree_sha": "c" * 40, "snapshot_commit": "d" * 40,
        "snapshot_key": key, "snapshot_ref": ref,
        "manifest_identity": f"manifests/{key}__snapshot-manifest.json",
        "inventory_identity": f"manifests/{key}__inventory/",
        "manifest_sha256": "e" * 64, "inventory_sha256": "f" * 64,
        "verified_files": 25, "verified_manifest_shards": 1,
        "remote_readback": "PASS", "restore": "PASS_ALL_FILES_AND_GIT_TREE",
        "verified_at_utc": "2026-11-13T02:00:00+00:00",
        "custody": "CUSTODY_UNATTESTED", "separation": "REQUIRES_INDEPENDENT_OWNER_EVIDENCE",
        "release_permission": False,
    }
    native = {
        "receipt_author_id": 42,
        "source_sha": receipt["source_sha"], "source_tree_sha": receipt["source_tree_sha"],
        "snapshot_ref": ref, "snapshot_head": receipt["snapshot_commit"],
        "run": {"id": "90", "attempt": "1", "repository": VAULT, "workflow_file": WORKFLOW,
                "head_sha": receipt["workflow_commit"], "event": "schedule", "status": "completed",
                "conclusion": "success", "snapshot_job": "success",
                "publish_archive_receipt_job": "success"},
    }
    for key in ("manifest_sha256", "inventory_sha256", "verified_files",
                "verified_manifest_shards", "remote_readback", "restore"):
        native[key] = receipt[key]
    return receipt, native


def comment(receipt, author=42):
    return {"url": ISSUE + "#issuecomment-123", "author_id": author,
            "body": "<!-- VAULT_NATIVE_RECEIPT_V1:90-1 -->\nTechnical receipt.\n\n"
                    + "~~~json\n" + json.dumps(receipt) + "\n~~~\n"}


class VaultReceiptTest(unittest.TestCase):
    def test_maps_technical_fields_only(self):
        receipt, native = fixture()
        result = bind_technical_receipt(comment(receipt), native)
        self.assertEqual(result["reason"], "NATIVE_TECHNICAL_RECOVERY_BOUND")
        recovery = result["recovery"]
        self.assertEqual(recovery["observed_at_utc"], "2026-11-13T02:00:00Z")
        self.assertEqual(recovery["manifest_sha256"], receipt["manifest_sha256"])
        self.assertIs(recovery["native_release_permission"], False)
        self.assertNotIn("independent_custody", recovery)
        self.assertNotIn("separation", recovery)

    def test_native_observations_required(self):
        receipt, native = fixture()
        cases = [
            (("receipt_author_id",), 43, "NATIVE_RECEIPT_ORIGIN_UNVERIFIED"),
            (("run", "attempt"), "2", "NATIVE_RUN_SUCCESS_UNVERIFIED"),
            (("run", "status"), "in_progress", "NATIVE_RUN_SUCCESS_UNVERIFIED"),
            (("run", "publish_archive_receipt_job"), "skipped", "NATIVE_RUN_SUCCESS_UNVERIFIED"),
            (("snapshot_head",), "0" * 40, "NATIVE_SNAPSHOT_BINDING_INVALID"),
            (("source_sha",), "0" * 40, "RECOVERY_SOURCE_STALE"),
            (("source_tree_sha",), "0" * 40, "RECOVERY_SOURCE_STALE"),
            (("manifest_sha256",), "0" * 64, "NATIVE_RESTORE_READBACK_MISMATCH"),
            (("verified_files",), 24, "NATIVE_RESTORE_READBACK_MISMATCH"),
            (("remote_readback",), "FAIL", "NATIVE_RESTORE_READBACK_MISMATCH"),
        ]
        for path, value, reason in cases:
            with self.subTest(path=path):
                changed = copy.deepcopy(native)
                parent = changed if len(path) == 1 else changed[path[0]]
                parent[path[-1]] = value
                self.assertEqual(bind_technical_receipt(comment(receipt), changed), {"reason": reason})

    def test_receipt_tampering_fails_closed(self):
        receipt, native = fixture()
        for field, value in (
            ("release_permission", True), ("verified_files", True),
            ("inventory_sha256", "garbage"), ("custody", "PASS"),
            ("restore", "PASS"), ("snapshot_key", "../90-1"),
        ):
            with self.subTest(field=field):
                self.assertNotIn("recovery", bind_technical_receipt(comment(receipt | {field: value}), native))
        duplicate = comment(receipt)
        duplicate["body"] = duplicate["body"].replace('{"schema"', '{"id":"90-1","schema"')
        self.assertEqual(bind_technical_receipt(duplicate, native), {"reason": "NATIVE_RECEIPT_FORMAT_INVALID"})

    def test_classifier_uses_native_result_and_keeps_custody_separate(self):
        from scripts.governance.s1_release_evidence_classifier_v1 import classify_pr_disposition
        from tests.governance.test_s1_release_evidence_classifier_v1 import decision_fixture

        receipt, native = fixture()
        record = decision_fixture()
        record["native_vault_evidence"] = {"comment": comment(receipt), "native": native}
        record["current"]["source"] = receipt["source_sha"]
        record["evaluated"]["source"] = receipt["source_sha"]
        record["review"]["source"] = receipt["source_sha"]
        record["now_utc"] = "2026-11-13T02:15:00Z"
        record["recovery"] = {"technical_recovery": True, "native_release_permission": True}
        self.assertEqual(classify_pr_disposition(record)["reason"], "CUSTODY_UNATTESTED")
        native["run"]["status"] = "in_progress"
        self.assertEqual(classify_pr_disposition(record)["reason"], "NATIVE_RUN_SUCCESS_UNVERIFIED")
