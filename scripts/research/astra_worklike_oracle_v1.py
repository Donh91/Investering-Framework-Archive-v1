"""Independent L04 clock pilot sandbox, never a production forecast admission.

Host must be a dedicated disposable no-secret/no-write runner, trusted code
from reviewed main, with an independently approved pinned image already
present. Do not run this from a privileged job or source candidate checkout.
"""
from __future__ import annotations

import json
import os
import re
import selectors
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from scripts.research import astra_worklike_pilot_v1 as gate

IMAGE = re.compile(r"python@sha256:[0-9a-f]{64}\Z")
NAME = re.compile(r"astra-pilot-[0-9a-f]{32}\Z")
MAX_OUTPUT_BYTES = 8192
WALL_SECONDS = 15
# Cases are a trusted oracle, not supplied to the model or mounted into its sandbox.
CUTOFF = "2026-11-23T00:00:00Z"
DIGEST = "a" * 64

def cases():
    base = {"cutoff_utc": CUTOFF, "baseline_sha256": DIGEST,
            "published_at_utc": "2026-11-23T08:35:56Z",
            "witness": None}
    early = {"observed_at_utc": "2026-11-22T23:59:59Z",
             "baseline_sha256": DIGEST, "independent": True}
    def row(changes, expected):
        return ({**base, **changes}, expected)
    return [
        row({}, "UNKNOWN"),
        row({"published_at_utc": "2026-11-22T23:59:59Z"}, "ELIGIBLE"),
        row({"published_at_utc": CUTOFF}, "UNKNOWN"),
        row({"witness": early}, "ELIGIBLE"),
        row({"witness": {**early, "baseline_sha256": "b"*64}}, "UNKNOWN"),
        row({"witness": {**early, "independent": False}}, "UNKNOWN"),
        row({"witness": {**early, "observed_at_utc": CUTOFF}}, "UNKNOWN"),
        row({"published_at_utc": "2026-11-22T23:59:59"}, "INVALID"),
        row({"published_at_utc": "not-a-date"}, "INVALID"),
        row({"baseline_sha256": "not-a-digest"}, "INVALID"),
        row({"witness": {**early, "observed_at_utc": "2026-11-22T23:59:59"}}, "INVALID"),
    ]

def docker_command(image, name, scratch):
    if not isinstance(image, str) or not IMAGE.fullmatch(image):
        raise gate.PilotBlocked("IMAGE_NOT_PINNED")
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise gate.PilotBlocked("CONTAINER_NAME")
    path = Path(scratch)
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise gate.PilotBlocked("SCRATCH_PATH")
    if "," in str(path) or "\n" in str(path):
        raise gate.PilotBlocked("SCRATCH_PATH")
    return ["docker", "run", "--rm", "--interactive", "--pull", "never",
            "--name", name, "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--user", "65534:65534", "--memory", "256m", "--memory-swap", "256m",
            "--cpus", "0.5", "--pids-limit", "32", "--log-driver", "none",
            "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=16m",
            "--mount", "type=bind,src="+str(path)+",dst=/candidate,readonly",
            "--workdir", "/candidate", image, "python", "-I", "-B", "/candidate/candidate.py"]

def parse_answer(data):
    if not isinstance(data, bytes) or len(data) > MAX_OUTPUT_BYTES:
        raise gate.PilotBlocked("OUTPUT_LIMIT")
    def pairs(items):
        if len({k for k, _ in items}) != len(items):
            raise gate.PilotBlocked("DUPLICATE_JSON_KEY")
        return dict(items)
    try:
        obj = json.loads(data.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise gate.PilotBlocked("OUTPUT_JSON") from exc
    if (not isinstance(obj, dict) or set(obj) != {"status"} or
            obj["status"] not in ("ELIGIBLE", "UNKNOWN", "INVALID")):
        raise gate.PilotBlocked("OUTPUT_CONTRACT")
    return obj["status"]

def run_case(image, scratch, fixture):
    """One candidate process per case, bounded stdout/stderr, no shell interpolation."""
    name = "astra-pilot-" + uuid.uuid4().hex
    cmd = docker_command(image, name, scratch)
    payload = gate.canonical(fixture) + b"\n"
    if len(payload) > 4096:
        raise gate.PilotBlocked("FIXTURE_BYTES")
    deadline = time.monotonic() + WALL_SECONDS
    proc = None
    sel = selectors.DefaultSelector()
    stdout = bytearray()
    stderr = bytearray()
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=False, env={
                                    "PATH": "/usr/bin:/bin",
                                    "HOME": "/tmp",
                                })
        proc.stdin.write(payload)
        proc.stdin.close()
        sel.register(proc.stdout, selectors.EVENT_READ, stdout)
        sel.register(proc.stderr, selectors.EVENT_READ, stderr)
        while sel.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise gate.PilotBlocked("SANDBOX_TIMEOUT")
            for key, _ in sel.select(remaining):
                chunk = os.read(key.fileobj.fileno(), 4096)
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                key.data.extend(chunk)
                if len(stdout)+len(stderr) > MAX_OUTPUT_BYTES:
                    raise gate.PilotBlocked("SANDBOX_OUTPUT_LIMIT")
        code = proc.wait(timeout=max(0.01, deadline-time.monotonic()))
        if code != 0:
            raise gate.PilotBlocked("SANDBOX_NONZERO:"+str(code))
        return bytes(stdout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise gate.PilotBlocked("SANDBOX_INFRA_OR_TIMEOUT") from exc
    finally:
        sel.close()
        if proc is not None:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
            # Remove only our own generated container, including on CLI timeout.
            try:
                subprocess.run(["docker", "rm", "-f", name], shell=False, timeout=5,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               env={"PATH": "/usr/bin:/bin", "HOME": "/tmp"})
            except (OSError, subprocess.TimeoutExpired):
                raise gate.PilotBlocked("SANDBOX_CLEANUP_UNVERIFIED")
            for stream in (proc.stdout, proc.stderr):
                stream.close()

def compare(candidate, *, run):
    """Independent expectations, exactly one result per hidden case.

    'run' must be a trusted native sandbox adapter. Mock runs are tests only.
    Exceptions, timeouts and invalid JSON HOLD rather than justify paid repair.
    """
    rows = []
    for fixture, expected in cases():
        data = run(candidate, fixture)
        actual = parse_answer(data)
        rows.append({"fixture_sha256": gate.sha(gate.canonical(fixture)),
                     "expected": expected, "actual": actual,
                     "output_sha256": gate.sha(data), "pass": actual == expected})
    return {"contract": "ASTRA_WORKLIKE_ORACLE_RESULT_v1",
            "status": "PASS" if all(r["pass"] for r in rows) else "TEST_FAILURE",
            "cases": rows, "candidate_sha256": gate.sha(candidate),
            "release_authority": False, "native_attestation_required": True}

def verify_in_disposable_runner(candidate, image):
    """No Git checkout mounted. Only the candidate module, read-only.

    Caller must prove runner isolation and reviewed image availability before
    invoking. This function does not submit a model request or write GitHub.
    """
    if not isinstance(candidate, bytes) or not 0 < len(candidate) <= gate.MAX_FILE_BYTES:
        raise gate.PilotBlocked("CANDIDATE_BYTES")
    if not isinstance(image, str) or not IMAGE.fullmatch(image):
        raise gate.PilotBlocked("IMAGE_NOT_PINNED")
    with tempfile.TemporaryDirectory(prefix="astra-public-pilot-") as name:
        scratch = Path(name)
        scratch.chmod(0o755)
        file = scratch / "candidate.py"
        file.write_bytes(candidate)
        file.chmod(0o444)
        return compare(candidate, run=lambda _, fixture: run_case(image, scratch, fixture))
