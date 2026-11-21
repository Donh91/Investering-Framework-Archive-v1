"""Bind an Archive #1593 technical receipt to separately observed GitHub facts.

The caller must authenticate the native comment, run, snapshot, and source
observations independently. Neither this adapter nor the producer comment
authenticates custody or authorizes release.
"""

import json
import re
from datetime import datetime

ARCHIVE = "Donh91/Investering-Framework-Archive-v1"
VAULT = "Donh91/Investering-Framework-Vault"
WORKFLOW = ".github/workflows/vault-canonical-recovery.yml"
ISSUE = f"https://github.com/{ARCHIVE}/issues/1593"
SCHEMA = "VAULT_NATIVE_RECEIPT_V1"
COMMENT_URL = re.compile(re.escape(ISSUE) + r"#issuecomment-[1-9][0-9]*")
SHA40 = re.compile(r"[0-9a-f]{40}")
SHA64 = re.compile(r"[0-9a-f]{64}")
ID = re.compile(r"[1-9][0-9]*")


def _matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def bind_technical_receipt(comment, native):
    """Return only technical evidence in the existing S1 classifier's format."""
    if not isinstance(comment, dict) or not isinstance(native, dict):
        return {"reason": "NATIVE_RECOVERY_INPUT_MISSING"}
    body = comment.get("body")
    url = comment.get("url")
    author_id = comment.get("author_id")
    if (not isinstance(body, str) or len(body) > 65536
            or not _matches(COMMENT_URL, url)
            or type(author_id) is not int or author_id < 1
            or type(native.get("receipt_author_id")) is not int
            or author_id != native.get("receipt_author_id")):
        return {"reason": "NATIVE_RECEIPT_ORIGIN_UNVERIFIED"}

    marker = re.match(r"<!-- VAULT_NATIVE_RECEIPT_V1:([1-9][0-9]*-[1-9][0-9]*) -->\n", body)
    payloads = re.findall(r"^~~~json\n(.*?)\n~~~$", body, flags=re.MULTILINE | re.DOTALL)
    if not marker or len(payloads) != 1:
        return {"reason": "NATIVE_RECEIPT_FORMAT_INVALID"}
    try:
        receipt = json.loads(payloads[0], object_pairs_hook=_unique_object)
    except (ValueError, RecursionError):
        return {"reason": "NATIVE_RECEIPT_FORMAT_INVALID"}
    if not isinstance(receipt, dict):
        return {"reason": "NATIVE_RECEIPT_FORMAT_INVALID"}

    run, attempt = receipt.get("run_id"), receipt.get("run_attempt")
    if not _matches(ID, run) or not _matches(ID, attempt):
        return {"reason": "NATIVE_RUN_BINDING_INVALID"}
    identifier = f"{run}-{attempt}"
    run_url = f"https://github.com/{VAULT}/actions/runs/{run}"
    if (marker[1] != identifier or receipt.get("id") != identifier
            or receipt.get("schema") != SCHEMA or receipt.get("run_url") != run_url
            or receipt.get("vault_repository") != VAULT
            or receipt.get("workflow_file") != WORKFLOW
            or receipt.get("job_key") != "publish_archive_receipt"):
        return {"reason": "NATIVE_RUN_BINDING_INVALID"}
    observed_run = native.get("run")
    if not isinstance(observed_run, dict) or any(observed_run.get(k) != v for k, v in {
        "id": run, "attempt": attempt, "repository": VAULT, "workflow_file": WORKFLOW,
        "status": "completed", "conclusion": "success", "snapshot_job": "success",
        "publish_archive_receipt_job": "success",
        "head_sha": receipt.get("workflow_commit"),
    }.items()) or observed_run.get("event") not in ("schedule", "workflow_dispatch"):
        return {"reason": "NATIVE_RUN_SUCCESS_UNVERIFIED"}

    key = receipt.get("snapshot_key")
    if not _matches(re.compile(r"\d{4}-\d{2}-\d{2}-run-" + identifier), key):
        return {"reason": "NATIVE_SNAPSHOT_BINDING_INVALID"}
    snapshot_ref = f"refs/heads/agent/task-{key[:10].replace('-', '')}-recovery-{identifier}"
    if (receipt.get("snapshot_ref") != snapshot_ref
            or receipt.get("manifest_identity") != f"manifests/{key}__snapshot-manifest.json"
            or receipt.get("inventory_identity") != f"manifests/{key}__inventory/"
            or native.get("snapshot_ref") != snapshot_ref
            or native.get("snapshot_head") != receipt.get("snapshot_commit")):
        return {"reason": "NATIVE_SNAPSHOT_BINDING_INVALID"}
    if (any(not _matches(SHA40, receipt.get(k)) for k in
            ("source_sha", "source_tree_sha", "snapshot_commit", "workflow_commit"))
            or any(not _matches(SHA64, receipt.get(k)) for k in
                   ("manifest_sha256", "inventory_sha256"))
            or any(type(receipt.get(k)) is not int or receipt[k] < 1
                   for k in ("verified_files", "verified_manifest_shards"))
            or receipt.get("remote_readback") != "PASS"
            or receipt.get("restore") != "PASS_ALL_FILES_AND_GIT_TREE"
            or receipt.get("custody") != "CUSTODY_UNATTESTED"
            or receipt.get("separation") != "REQUIRES_INDEPENDENT_OWNER_EVIDENCE"
            or receipt.get("release_permission") is not False):
        return {"reason": "NATIVE_TECHNICAL_RECOVERY_INVALID"}
    if (native.get("source_sha") != receipt["source_sha"]
            or native.get("source_tree_sha") != receipt["source_tree_sha"]):
        return {"reason": "RECOVERY_SOURCE_STALE"}
    for field in ("manifest_sha256", "inventory_sha256", "verified_files",
                  "verified_manifest_shards", "remote_readback", "restore"):
        if type(native.get(field)) is not type(receipt[field]) or native[field] != receipt[field]:
            return {"reason": "NATIVE_RESTORE_READBACK_MISMATCH"}

    timestamp = receipt.get("verified_at_utc")
    if not _matches(re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)"), timestamp):
        return {"reason": "NATIVE_RECOVERY_TIMESTAMP_INVALID"}
    timestamp = timestamp.removesuffix("+00:00").removesuffix("Z") + "Z"
    try:
        datetime.fromisoformat(timestamp[:-1] + "+00:00")
    except ValueError:
        return {"reason": "NATIVE_RECOVERY_TIMESTAMP_INVALID"}
    return {
        "reason": "NATIVE_TECHNICAL_RECOVERY_BOUND",
        "recovery": {
            "technical_recovery": True,
            "source": receipt["source_sha"],
            "snapshot": receipt["snapshot_commit"],
            "tree": receipt["source_tree_sha"],
            "workflow": receipt["workflow_commit"],
            "manifest_sha256": receipt["manifest_sha256"],
            "receipt_url": url,
            "observed_at_utc": timestamp,
            "native_release_permission": False,
        },
    }


if __name__ == "__main__":
    import sys

    record = json.load(sys.stdin)
    if not isinstance(record, dict):
        record = {}
    result = bind_technical_receipt(record.get("comment"), record.get("native"))
    print(json.dumps(result, sort_keys=True))
    sys.exit(0 if "recovery" in result else 1)
