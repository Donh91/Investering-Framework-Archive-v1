"""No-secret prospective fixed-suite baseline census on a pristine MAIN checkout.

One-time PR-only diagnostic. This does NOT attest untrusted candidate code,
lift any BUILD HOLD, trigger a provider call, or prove a paid mission ready.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from scripts.api_agent import astra_build_admit_v1 as admission
from scripts.api_agent import astra_build_sandbox_v1 as sandbox

IMAGE_ID = re.compile(r"sha256:[0-9a-f]{64}\Z")
TEST_IDS = ("M1", "M3")


def native_pristine_source(path: Path, expected: str) -> str:
    path = path.resolve()
    if not path.is_dir() or not re.fullmatch(r"[0-9a-f]{40}", expected):
        raise ValueError("PRISTINE_SOURCE_INVALID")
    actual = subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True, timeout=10).strip()
    if actual != expected:
        raise ValueError("PRISTINE_SOURCE_SHA_DRIFT")
    sandbox.verify_snapshot(path, expected)
    return actual


def probe(pristine: Path, sha: str, image_id: str) -> dict:
    if not isinstance(image_id, str) or not IMAGE_ID.fullmatch(image_id):
        raise ValueError("IMAGE_ID_UNVERIFIED")
    actual_id = subprocess.check_output(
        ["docker", "image", "inspect", "--format", "{{.Id}}", image_id],
        text=True, timeout=15).strip()
    if actual_id != image_id:
        raise ValueError("IMAGE_ID_LOCAL_MISMATCH")
    verified_sha = native_pristine_source(pristine, sha)
    with tempfile.TemporaryDirectory(prefix="astra-build-pristine-") as folder:
        # The Docker candidate runs as uid 65534; the temporary parent
        # must be searchable without granting write authority.
        Path(folder).chmod(0o755)
        root = Path(folder) / "repo"
        root.mkdir(mode=0o755)
        copied = sandbox._copy_public_tree(pristine.resolve(), root)
        outcomes = []
        for scope in TEST_IDS:
            for ordinal, command in enumerate(admission.TEST_COMMANDS[scope]):
                # A pristine trusted MAIN checkout can run the FULL fixed suite
                # with public Git metadata and historical files mounted read-only.
                # This code executes before and separately from model-supplied
                # file admission; the candidate sandbox still gets only root's
                # narrow, tracked public fixture closure.
                name, argv = sandbox.docker_command(pristine.resolve(), scope, ordinal)
                image_pos = len(argv) - len(command) - 1
                if argv[image_pos] != sandbox.IMAGE:
                    raise ValueError("NATIVE_IMAGE_ARGV_DRIFT")
                argv[image_pos] = image_id
                run = sandbox._run_once(argv, name, trusted_full_baseline=True)
                outcomes.append({
                    "scope": scope,
                    "fixed_command": list(command),
                    "result": run["status"],
                    "exit_code": run["returncode"],
                    "observed_count_untrusted": run["completed_tests_observed"],
                    "log_sha256": run["output_sha256"],
                    "failure_diagnostics_untrusted": run.get("failure_diagnostics_untrusted", []),
                    "last_200_lines_untrusted": run["last_200_lines"][-35:],
                })
    all_look_green = bool(outcomes) and all(
        x["result"] == "EXIT0_WITH_UNTRUSTED_SUMMARY" and x["observed_count_untrusted"] > 0
        for x in outcomes)
    return {
        "contract": "ASTRA_BUILD_PRISTINE_BASELINE_PROBE_v1",
        "pristine_main_sha": verified_sha,
        "baseline_workspace": "TRUSTED_PRISTINE_MAIN_READONLY_NO_MODEL",
        "candidate_workspace": "RESTRICTED_PUBLIC_COPY",
        "toolchain_local_image_id": image_id,
        "source_copy": copied,
        "results": outcomes,
        "probe_result": "CANDIDATE_BASELINES_LOOK_COMPLETE" if all_look_green
                        else "BASELINES_FAIL_OR_INCOMPLETE",
        "candidate_test_completion_attested": False,
        "build_hold_lifted": False,
        "paid_or_merge_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pristine", type=Path, required=True)
    p.add_argument("--sha", required=True)
    p.add_argument("--image-id", required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    try:
        result = probe(args.pristine, args.sha, args.image_id)
    except (OSError, ValueError, subprocess.SubprocessError,
            sandbox.SandboxBlocked) as error:
        result = {
            "contract": "ASTRA_BUILD_PRISTINE_BASELINE_PROBE_v1",
            "probe_result": "PROBE_INFRA_OR_SECURITY_HOLD",
            "error_type": type(error).__name__,
            "error_code": str(error) if re.fullmatch(r"[A-Z][A-Z0-9_]{2,79}", str(error))
                          else "UNCLASSIFIED_DIAGNOSTIC",
            "build_hold_lifted": False,
            "paid_or_merge_authority": False,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(admission.canonical(result) + b"\n")
    print(result["contract"], result["probe_result"],
          result.get("error_code", "NO_ERROR_CODE"))
    return 0 if result["probe_result"] == "CANDIDATE_BASELINES_LOOK_COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
