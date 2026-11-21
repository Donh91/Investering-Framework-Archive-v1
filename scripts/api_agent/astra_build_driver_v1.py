"""BUILD_v1 no-secret, no-network, no-write downstream Astra evidence gate.

M1/M2/M3 Stage1 only. Original owner event, one-use claim, provider GET and
cost guard remain in the existing owner-astra-mission workflow. This driver
never calls any provider, dispatches, reviews, writes Git or opens a PR.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
from pathlib import Path

from scripts.api_agent import astra_build_admit_v1 as admit
from scripts.api_agent import astra_build_cost_v1 as budget
from scripts.api_agent import astra_build_receipt_v1 as binding
from scripts.api_agent import astra_build_sandbox_v1 as sandbox
from scripts.research import owner_astra_mission_v1 as owner

CONTRACT = "ASTRA_BUILD_DRIVER_RECEIPT_v1"
MAX_ARTIFACT_BYTES = 800_000
SCOPE_NAME = "BUILD_SCOPE.json"
ALLOWED_STAGE1_IDS = frozenset(f"ASTRA-BUILD-{m}-20261121-S1"
                               for m in budget.PROGRAM_MISSIONS)

class DriverHold(ValueError):
    pass

def require(value, why):
    if not value:
        raise DriverHold(why)

def read_bound(root: Path, rel: str, maximum: int = MAX_ARTIFACT_BYTES) -> bytes:
    require(isinstance(rel, str) and rel and not rel.startswith("/")
            and ".." not in Path(rel).parts and "\\" not in rel,
            "ARTIFACT_PATH")
    actual = root / rel
    require(actual.is_file() and not actual.is_symlink()
            and actual.resolve().is_relative_to(root.resolve())
            and stat.S_ISREG(actual.lstat().st_mode)
            and 0 < actual.stat().st_size <= maximum, "ARTIFACT_UNTRUSTED_FILE")
    return actual.read_bytes()

def load_json(raw: bytes) -> dict:
    result = admit.parse_untrusted(raw)
    require(type(result) is dict, "JSON_SHAPE")
    return result

def trusted_scope(repo: Path, mission_id: str, head: str) -> dict:
    """Load author-reviewed source-only scope from the actual main checkout.

    No self-referential future main SHA is stored in the file; current
    authenticated HEAD is injected, and preimage sha256 is compared to bytes.
    """
    require(mission_id in ALLOWED_STAGE1_IDS, "MISSION_NOT_STAGE1_BUILD")
    scope_path = "06_RESEARCH_LAB/astra_missions/" + mission_id + "/" + SCOPE_NAME
    raw = read_bound(repo, scope_path, 64_000)
    data = load_json(raw)
    require(set(data) == {"contract", "mission_id", "test_command_id",
                          "allowlist", "source_files", "stage", "previous_repair"},
            "SCOPE_MAIN_SCHEMA")
    require(data["mission_id"] == mission_id
            and data["test_command_id"] == mission_id.split("-")[2]
            and data["stage"] == 1 and data["previous_repair"] is None,
            "SCOPE_STAGE_ID")
    scope = dict(data, main_sha=head)
    admit.verify_scope(scope)
    for path, meta in data["source_files"].items():
        entry = repo / path
        require(entry.resolve(strict=False).is_relative_to(repo.resolve()),
                "SOURCE_PATH_ESCAPE")
        if meta is None:
            require(not entry.exists() and not entry.is_symlink(),
                    "SOURCE_CREATE_PATH_ALREADY_EXISTS")
        else:
            require(entry.is_file() and not entry.is_symlink()
                    and stat.S_ISREG(entry.lstat().st_mode)
                    and admit.digest(entry.read_bytes()) == meta["sha256"],
                    "SOURCE_REVIEWED_PREIMAGE_MISMATCH")
    return scope

def verified_head(repo: Path, native: str) -> str:
    require(isinstance(native, str) and admit.HEX40.fullmatch(native),
            "NATIVE_HEAD_SHA")
    try:
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                       timeout=10, text=True,
                                       env={"PATH": "/usr/bin:/bin"}).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise DriverHold("CHECKOUT_MAIN_UNVERIFIED") from exc
    require(head == native, "NATIVE_GITHUB_SHA_DRIFT")
    return head

def verify_original_artifact(repo: Path, input_dir: Path, mission_id: str,
                             native_head: str, run_id: str):
    """Native workflow must download the same run's artifact unprivileged."""
    require(mission_id in ALLOWED_STAGE1_IDS, "MISSION_NOT_STAGE1_BUILD")
    expected_req, expected_raw, meta = owner.build_request(mission_id)
    require(expected_req["model"] == budget.MODEL
            and meta["reasoning_effort"] == budget.EFFORT
            and meta["max_usd"] <= budget.MAX_STAGE_USD
            and meta["request_bytes"] <= budget.MAX_REQUEST_BYTES,
            "BUILD_MODEL_OR_REQUEST_CAP")
    original_manifest_bytes = read_bound(input_dir, "source_manifest.json", 48_000)
    original_receipt_bytes = read_bound(input_dir, "receipt.json", 48_000)
    sr = load_json(original_manifest_bytes)
    paid = load_json(original_receipt_bytes)
    require({k: v for k, v in sr.items()
             if k not in ("trigger_comment_id", "release_main_sha")} == meta,
            "SOURCE_MANIFEST_NOT_EXACT_NATIVE_REQUEST")
    require(sr.get("release_main_sha") == native_head, "SOURCE_MAIN_WRONG")
    require(paid.get("release_main_sha") == native_head, "PAID_MAIN_WRONG")
    require(sr.get("mission_id") == mission_id and paid.get("mission_id") == mission_id
            and paid.get("work_id") == mission_id, "MISSION_WRONG")
    require(str(paid.get("run_id")) == run_id, "PAID_RUN_NOT_CURRENT_NATIVE_RUN")
    require(paid.get("status") == "completed"
            and paid.get("incomplete_details") is None
            and paid.get("no_retry") is True, "PAID_NOT_FINAL")
    prefix = "archive/" + meta["mission_dir"] + "/results/"
    require(read_bound(input_dir, prefix + "receipt.json", 48_000)
            == original_receipt_bytes, "PAID_ARCHIVE_RECEIPT_NOT_MATCHED")
    require(read_bound(input_dir, prefix + "source_manifest.json", 48_000)
            == original_manifest_bytes, "SOURCE_ARCHIVE_MANIFEST_NOT_MATCHED")
    raw = read_bound(input_dir, prefix + "ASTRA_RAW_REPORT.md")
    require(admit.digest(raw) == paid.get("output_sha256")
            and len(raw) == paid.get("bytes"), "RAW_REPORT_DIGEST_MISMATCH")
    require(not owner.CREDENTIAL.search(raw) and not owner.WALLET.search(raw),
            "RAW_REPORT_SENSITIVE_PATTERN")
    # The exact native request is reconstructed, never downloaded and trusted
    # as a possible arbitrary shell command.
    require(admit.digest(expected_raw) == meta["request_sha256"],
            "ORIGINAL_REQUEST_MISMATCH")
    return raw, sr, paid

def run(repo: Path, artifact: Path, mission_id: str, native_head: str,
        native_run_id: str) -> dict:
    head = verified_head(repo, native_head)
    scope = trusted_scope(repo, mission_id, head)
    raw, source, paid = verify_original_artifact(
        repo, artifact, mission_id, head, native_run_id)
    admitted = admit.admit(raw, scope)
    tested = sandbox.run_admitted(raw, scope, repo)
    verdict = binding.bind(raw_report=raw, source_manifest=source,
                           paid_receipt=paid, admitted=admitted, tested=tested,
                           approved_scope=scope,
                           verified_current_run_id=native_run_id)
    require(verdict["paid_authority"] is False
            and verdict["merge_authority"] is False,
            "RELEASE_AUTHORITY_IN_SANDBOX")
    return verdict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--mission", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo.resolve(), args.artifact.resolve(), args.mission,
                 os.environ.get("GITHUB_SHA", ""),
                 os.environ.get("GITHUB_RUN_ID", ""))
    data = admit.canonical(result) + b"\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("xb") as dest:
        dest.write(data)
    print(CONTRACT, result["status"], admit.digest(data))
    return 0 if result["status"] == "TESTED_PASS_REVIEW_REQUIRED" else 3

if __name__ == "__main__":
    raise SystemExit(main())
