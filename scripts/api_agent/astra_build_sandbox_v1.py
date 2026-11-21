"""No-secret, no-network full-file BUILD_v1 sandbox adapter.

This module does not dispatch, reserve, write GitHub, or open PRs.
The caller must run it in a separate no-secret job and supply an independently
authenticated exact-main checkout. All model text is untrusted data.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import selectors
import shutil
import stat
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from scripts.api_agent import astra_build_admit_v1 as admit

IMAGE = "python@sha256:1148dbb014615300fa7e713b2f94f550c0d1c69780c0805f84f093ceee34dd0b"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
MAX_LOG_BYTES = 256_000
WALL_SECONDS = 180
MAX_SNAPSHOT_BYTES = 400_000_000
MAX_SNAPSHOT_FILES = 85_000
# Public code and fixed-test dependencies only. Never copy the giant mutable
# market-data/receipt tree into a model-code sandbox. Missing dependencies
# fail the native fixed test, not a permission to read from private sources.
SOURCE_ROOTS = ("scripts", "tests", "05_CYCLE_NAVIGATOR/site",
                "04_MARKET_LEARNING/handlekompas/contracts", ".github",
                "00_FMOS", "01_CORE_FRAMEWORK/governance", "07_PROMPTS_AND_AGENTS",
                "schemas")
# Narrow, reviewed public fixtures actually read by the fixed M3 governance
# tests. Never bulk-copy 00_ARCHIVE_CONTROL (which includes Vault registries).
SOURCE_FILES = ("pytest.ini", "pyproject.toml", "setup.cfg", "requirements.txt",
                "AGENTS.md", "CLAUDE.md",
                "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md",
                "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
                "00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md")
REQUIRED_PUBLIC_FIXTURES = ("AGENTS.md", "schemas/S1_CLOSURE_ASSURANCE_V1.schema.json",
                            "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md")

class SandboxBlocked(admit.AdmissionBlocked):
    pass

def stop(reason: str):
    raise SandboxBlocked(reason)

def require(cond: bool, reason: str):
    if not cond:
        stop(reason)

def docker_command(workspace: Path, test_command_id: str, ordinal: int, image: str = IMAGE):
    """No shell interpolation; a reviewed static command is chosen by ID."""
    require(image == IMAGE, "IMAGE_NOT_VERIFIED")
    require(test_command_id in admit.TEST_COMMANDS, "TEST_COMMAND_ID")
    commands = admit.TEST_COMMANDS[test_command_id]
    require(type(ordinal) is int and 0 <= ordinal < len(commands), "TEST_INDEX")
    require(isinstance(workspace, Path) and workspace.is_absolute()
            and workspace.is_dir() and not workspace.is_symlink(), "WORKSPACE_INVALID")
    require("," not in str(workspace) and "\n" not in str(workspace), "WORKSPACE_INVALID")
    name = "astra-build-" + uuid.uuid4().hex
    argv = commands[ordinal]
    # The current pinned Python-only image cannot supply Node or pytest.
    # When absent, that fixed test fails closed; never silently skip it or
    # run the model's substitute command. A reviewed pinned test image
    # with dependencies is required for a production BUILD release.
    return name, ["docker", "run", "--rm", "--interactive", "--pull", "never",
                  "--name", name, "--platform", "linux/amd64",
                  "--network", "none", "--read-only", "--cap-drop", "ALL",
                  "--security-opt", "no-new-privileges",
                  "--user", "65534:65534", "--memory", "256m",
                  "--memory-swap", "256m", "--cpus", "0.5", "--pids-limit", "32",
                  "--log-driver", "none",
                  "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=32m",
                  "--mount", "type=bind,src="+str(workspace)+",dst=/work,readonly",
                  "--workdir", "/work", "--env", "PYTHONDONTWRITEBYTECODE=1",
                  "--env", "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
                  image, *argv]

def verify_snapshot(repo_root: Path, expected_sha: str):
    """Verify exact-main identity; no clone/fetch, no credentials."""
    require(isinstance(repo_root, Path) and repo_root.is_dir()
            and not repo_root.is_symlink(), "SOURCE_REPO_INVALID")
    require(isinstance(expected_sha, str) and HEX40.fullmatch(expected_sha),
            "SOURCE_SHA")
    try:
        # Literal argv roots are required by the existing privileged-closure
        # static derivation. Never accept executable names from model output.
        actual = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
                                         env={"PATH": "/usr/bin:/bin"},
                                         text=True, timeout=8).strip()
        dirty = subprocess.check_output(["git", "-C", str(repo_root), "status",
                                         "--porcelain", "--untracked-files=all"],
                                        env={"PATH": "/usr/bin:/bin"},
                                        text=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as exc:
        raise SandboxBlocked("SOURCE_ATTESTATION_UNAVAILABLE") from exc
    require(actual == expected_sha and dirty == "", "SOURCE_MAIN_OR_DIRTY")
    return actual

def _copy_public_tree(source: Path, target: Path):
    """Copy a pinned, public checkout into disposable scope, excluding .git.

    Reject symlinks/special files everywhere, including a parent of a model
    output. This is conservative and may HOLD on oversized repos.
    """
    # Only Git-indexed public files may enter the model-code workspace.
    # A clean working-tree check alone misses .gitignored injected files.
    try:
        tracked_raw = subprocess.check_output(
            ["git", "-C", str(source), "ls-files", "--cached", "-z"],
            timeout=30, env={"PATH": "/usr/bin:/bin"})
        tracked = set(x.decode("utf-8") for x in tracked_raw.split(b"\x00") if x)
    except (OSError, UnicodeError, subprocess.SubprocessError) as exc:
        raise SandboxBlocked("SOURCE_INDEX_UNVERIFIED") from exc
    require(bool(tracked), "SOURCE_INDEX_EMPTY")
    size, count = 0, 0
    excluded = {".git", "secrets", "vault", "private", "__pycache__", ".pytest_cache"}
    for relative in SOURCE_ROOTS:
        subtree = source / relative
        if not subtree.exists():
            continue
        require(subtree.is_dir() and not subtree.is_symlink(), "SOURCE_TREE_ROOT")
        for root, dirs, files in os.walk(subtree, followlinks=False):
            here = Path(root)
            require(not here.is_symlink(), "SOURCE_SYMLINK")
            dirs[:] = [x for x in dirs if x not in excluded]
            for name in dirs:
                require(not (here / name).is_symlink(), "SOURCE_SYMLINK")
            dest = target / here.relative_to(source)
            dest.mkdir(parents=True, exist_ok=True)
            for name in files:
                src = here / name
                require(src.relative_to(source).as_posix() in tracked,
                        "SOURCE_UNTRACKED_OR_IGNORED")
                mode = src.lstat().st_mode
                require(stat.S_ISREG(mode), "SOURCE_SPECIAL_OR_SYMLINK")
                count += 1
                size += src.stat().st_size
                require(count <= MAX_SNAPSHOT_FILES and size <= MAX_SNAPSHOT_BYTES,
                        "SOURCE_SNAPSHOT_TOO_LARGE")
                shutil.copyfile(src, dest / name)
                (dest / name).chmod(0o444)
    for relative in SOURCE_FILES:
        src = source / relative
        if not src.exists():
            continue
        require(relative in tracked, "SOURCE_UNTRACKED_OR_IGNORED")
        require(src.is_file() and not src.is_symlink()
                and stat.S_ISREG(src.lstat().st_mode)
                and all(not parent.is_symlink() for parent in list(src.parents)[:-1]
                        if parent.is_relative_to(source)), "SOURCE_FILE_SPECIAL")
        size += src.stat().st_size
        count += 1
        require(count <= MAX_SNAPSHOT_FILES and size <= MAX_SNAPSHOT_BYTES,
                "SOURCE_SNAPSHOT_TOO_LARGE")
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, destination)
        destination.chmod(0o444)
    for relative in REQUIRED_PUBLIC_FIXTURES:
        require((target / relative).is_file() and not (target / relative).is_symlink(),
                "REQUIRED_FIXED_TEST_FIXTURE_MISSING")
    return {"files": count, "bytes": size, "public_fixture_count": len(REQUIRED_PUBLIC_FIXTURES)}

def _write_admitted(root: Path, proposal: dict, scope: dict, receipt: dict):
    original = {r["path"]: r for r in receipt["files"]}
    for row in proposal["files"]:
        path = admit.safe_path(row["path"])
        meta = original[path]
        target = root / path
        require(target.resolve(strict=False).is_relative_to(root.resolve()),
                "TARGET_PATH_ESCAPE")
        parent = root
        for part in path.split("/")[:-1]:
            parent = parent / part
            require(not parent.is_symlink(), "TARGET_PARENT_SYMLINK")
        if row["action"] == "create":
            require(not target.exists() and not target.is_symlink(),
                    "CREATE_TARGET_EXISTS")
        else:
            require(target.is_file() and not target.is_symlink()
                    and stat.S_ISREG(target.lstat().st_mode), "MODIFY_TARGET_NOT_FILE")
            require(admit.digest(target.read_bytes()) == meta["preimage_sha256"],
                    "MODIFY_PREIMAGE_DRIFT")
        data = row["content"].encode("utf-8")
        require(admit.digest(data) == meta["sha256"], "STAGED_FILE_HASH_DRIFT")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.chmod(0o644)
        with target.open("wb") as dst:
            dst.write(data)
        target.chmod(0o444)
    return {"manifest_sha256": admit.digest(admit.canonical(receipt["files"])),
            "written_files": len(original)}

def observed_test_count(command: list[str], output: bytes) -> int:
    """Native CLI completion summary observed OUTSIDE the candidate process.

    This catches exit(0) before the runner reports completion, but stdout can
    be forged by untrusted code. Therefore this is NOT independent proof and
    can NEVER, on its own, authorize a BUILD PASS or paid release.
    """
    text = output.decode("utf-8", errors="replace")
    if "pytest" in command:
        # Only accept the ordinary end-of-session summary, not collection.
        match = re.search(r"(?m)^(?:=+\s*)?(\d+) passed(?:,[^\n]*)? in [0-9.]+s(?:\s*=+)?\s*$", text)
        return int(match.group(1)) if match else 0
    if "node" in command and "--test" in command:
        def field(name):
            m = re.search(r"(?m)^# " + re.escape(name) + r" (\d+)\s*$", text)
            return int(m.group(1)) if m else None
        n, passed, failed = field("tests"), field("pass"), field("fail")
        return n if n is not None and n > 0 and passed == n and failed == 0 else 0
    if "unittest" in command:
        m = re.search(r"(?m)^Ran (\d+) tests? in [0-9.]+s\s*$", text)
        return int(m.group(1)) if m and re.search(r"(?m)^OK\s*$", text) else 0
    return 0


def _run_once(command: list[str], name: str) -> dict:
    """Bound output, wall time, orphan cleanup; host environment has NO secrets."""
    require(command[:2] == ["docker", "run"] and "--network" in command
            and command[command.index("--network")+1] == "none", "DOCKER_NETWORK")
    env = {"PATH": "/usr/bin:/bin", "HOME": "/tmp"}
    out = bytearray()
    proc = None
    selector = selectors.DefaultSelector()
    try:
        require(command[0] == "docker", "DOCKER_BINARY_MISMATCH")
        proc = subprocess.Popen(["docker", *command[1:]], stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=False, env=env)
        selector.register(proc.stdout, selectors.EVENT_READ)
        end = time.monotonic() + WALL_SECONDS
        while selector.get_map():
            remaining = end - time.monotonic()
            if remaining <= 0:
                stop("TEST_TIMEOUT")
            for key, _ in selector.select(remaining):
                chunk = os.read(key.fileobj.fileno(), 8192)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                out.extend(chunk)
                require(len(out) <= MAX_LOG_BYTES, "TEST_LOG_LIMIT")
        rc = proc.wait(timeout=max(.01, end-time.monotonic()))
        completed = observed_test_count(command, bytes(out)) if rc == 0 else 0
        tail = out.decode("utf-8", errors="replace").splitlines()[-200:]
        return {"returncode": rc, "output_sha256": admit.digest(bytes(out)),
                "output_bytes": len(out), "last_200_lines": tail,
                "completed_tests_observed": completed,
                "completion_evidence": "UNTRUSTED_STDOUT_ONLY",
                "status": "PASS" if rc == 0 and completed > 0 else "TEST_FAILURE"}
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SandboxBlocked("DOCKER_INFRA_OR_TIMEOUT") from exc
    finally:
        selector.close()
        if proc is not None:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
            try:
                subprocess.run(["docker", "rm", "-f", name], shell=False,
                               timeout=5, env=env, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                check = subprocess.run(["docker", "ps", "-a", "--filter",
                                        "name=^/"+name+"$", "--format", "{{.Names}}"],
                                       shell=False, capture_output=True,
                                       timeout=5, env=env)
                require(check.returncode == 0 and not check.stdout.strip(),
                        "DOCKER_CLEANUP_NOT_PROVEN")
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise SandboxBlocked("DOCKER_CLEANUP_NOT_PROVEN") from exc
            proc.stdout.close()

def run_admitted(raw: bytes, scope: dict, exact_main_repo: Path):
    """One isolated job. Never run in a paid/provider credential-bearing job."""
    receipt = admit.admit(raw, scope)
    require(receipt["status"] == "ADMITTED_UNTRUSTED_CODE_TEST_REQUIRED",
            "NO_FILES_TO_TEST")
    proposal = admit.parse_untrusted(raw)
    verified_main = verify_snapshot(exact_main_repo, scope["main_sha"])
    with tempfile.TemporaryDirectory(prefix="astra-build-") as tmp:
        # Docker executes as uid 65534. The disposable parent must be
        # traversable, even though the bind mount itself stays read-only.
        Path(tmp).chmod(0o755)
        root = Path(tmp) / "repo"
        root.mkdir(mode=0o755)
        source = _copy_public_tree(exact_main_repo, root)
        # The original, unmodified fixed suites MUST be capable of completing
        # inside the copied environment before model-created code is staged.
        # This is also a source-fixture/toolchain readiness check.
        baseline = []
        for ordinal, _ in enumerate(admit.TEST_COMMANDS[scope["test_command_id"]]):
            name, argv = docker_command(root, scope["test_command_id"], ordinal)
            baseline.append(_run_once(argv, name))
        require(bool(baseline) and all(x.get("status") == "PASS" and
                x.get("completed_tests_observed", 0) > 0 for x in baseline),
                "FIXED_SUITE_BASELINE_NOT_PROVEN")
        staged = _write_admitted(root, proposal, scope, receipt)
        tests = []
        for ordinal, _ in enumerate(admit.TEST_COMMANDS[scope["test_command_id"]]):
            name, argv = docker_command(root, scope["test_command_id"], ordinal)
            tests.append(_run_once(argv, name))
        observed = all(x.get("status") == "PASS" and
                       x.get("completed_tests_observed", 0) >= base["completed_tests_observed"]
                       for x, base in zip(tests, baseline))
        # Candidate stdout can be forged. A count and exit 0 are NOT
        # independently attestable proof of completion. Explicitly HOLD
        # rather than assert a completed, merge-eligible BUILD test.
        # A separately reviewed, digest-pinned trusted attestor is needed.
        result = {"contract": "ASTRA_BUILD_SANDBOX_RECEIPT_v1",
                  "status": "TEST_COMPLETION_UNATTESTED" if observed else "TEST_FAILURE",
                  "independent_completion_attested": False,
                  "native_suite_baseline": baseline,
                  "mission_id": receipt["mission_id"], "stage": receipt["stage"],
                  "main_sha": verified_main,
                  "proposal_sha256": receipt["proposal_sha256"],
                  "admission_sha256": admit.digest(admit.canonical(receipt)),
                  "source_tree_copy": source, "staging": staged,
                  "test_command_id": scope["test_command_id"],
                  "tests": tests, "image": IMAGE, "network": "none",
                  "secrets": False, "paid_authority": False,
                  "merge_authority": False}
        result["result_sha256"] = admit.digest(admit.canonical(result))
        return result


def smoke() -> dict:
    """Three real Docker executions: network denial, assertion failure, early exit.

    This is the ONLY purpose of TEST_COMMANDS['SMOKE']. No production source,
    no model response, no provider API, no secret, no GitHub write.
    """
    benign = """import socket
import unittest

class SandboxSmoke(unittest.TestCase):
    def test_language_runtime(self):
        self.assertEqual(1 + 1, 2)

    def test_real_network_attempt_fails(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            rc = sock.connect_ex(("1.1.1.1", 443))
        self.assertNotEqual(rc, 0, "Outbound socket surprisingly reachable")
        try:
            with open("/proc/net/route", encoding="ascii") as fd:
                routes = [line.split() for line in fd.read().splitlines()[1:]]
        except OSError:
            routes = []
        self.assertFalse(any(len(r) > 1 and r[0] != "lo" and
                             r[1] == "00000000" for r in routes),
                         "Non-loopback default route exposes network")
"""
    mutant = """import unittest

class SandboxMutant(unittest.TestCase):
    def test_must_fail(self):
        self.fail("Intentional mutant, cannot claim PASS")
"""
    early_exit = """import os
import unittest

class ForcedEarlyExit(unittest.TestCase):
    def test_abort_without_completion(self):
        os._exit(0)
"""
    with tempfile.TemporaryDirectory(prefix="astra-build-smoke-") as temporary:
        parent = Path(temporary)
        parent.chmod(0o755)
        workspace = parent / "repo"
        tests = workspace / "tests" / "smoke"
        tests.mkdir(parents=True, mode=0o755)
        file = tests / "test_smoke.py"
        file.write_text(benign, encoding="utf-8")
        file.chmod(0o444)
        name, command = docker_command(workspace, "SMOKE", 0)
        good = _run_once(command, name)
        require(good["status"] == "PASS" and good["returncode"] == 0,
                "ISOLATED_POSITIVE_OR_NETWORK_DENIAL_FAILED")
        file.chmod(0o644)
        file.write_text(mutant, encoding="utf-8")
        file.chmod(0o444)
        name, command = docker_command(workspace, "SMOKE", 0)
        bad = _run_once(command, name)
        require(bad["status"] == "TEST_FAILURE" and bad["returncode"] != 0,
                "ISOLATED_MUTATION_NOT_DETECTED")
        file.chmod(0o644)
        file.write_text(early_exit, encoding="utf-8")
        file.chmod(0o444)
        name, command = docker_command(workspace, "SMOKE", 0)
        escaped = _run_once(command, name)
        require(escaped["returncode"] == 0 and escaped["status"] == "TEST_FAILURE"
                and escaped["completed_tests_observed"] == 0,
                "EXIT_ZERO_WITHOUT_SUITE_END_FALSE_PASS")
        return {"contract": "ASTRA_BUILD_SANDBOX_SMOKE_v1",
                "status": "PASS", "positive": good,
                "negative": bad, "early_exit_zero": escaped,
                "network_attempt_executed": True,
                "network_denied": True,
                "synthetic_only": True, "image": IMAGE,
                "paid_api": False, "live_task_changed": False}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("smoke",))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    receipt = smoke()
    raw = admit.canonical(receipt) + b"\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("xb") as f:
        f.write(raw)
    print(receipt["contract"], receipt["status"], admit.digest(raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
