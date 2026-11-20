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
PINNED_IMAGE = "python@sha256:1148dbb014615300fa7e713b2f94f550c0d1c69780c0805f84f093ceee34dd0b"
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
        row({"cutoff_utc": "2026-02-30T00:00:00Z"}, "INVALID"),
        row({"witness": {**early, "independent": 1}}, "INVALID"),
        row({"witness": {**early, "observed_at_utc": CUTOFF, "baseline_sha256": "bad"}}, "INVALID"),
        row({"witness": {"independent": True}}, "INVALID"),
        row({"unexpected": True}, "INVALID"),
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
            "--name", name, "--platform", "linux/amd64", "--network", "none", "--read-only",
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
                env = {"PATH": "/usr/bin:/bin", "HOME": "/tmp"}
                subprocess.run(["docker", "rm", "-f", name], shell=False, timeout=5,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
                remaining = subprocess.run(["docker", "ps", "-a", "--filter", "name=^/"+name+"$",
                                            "--format", "{{.Names}}"], shell=False, timeout=5,
                                           capture_output=True, env=env)
                if remaining.returncode or remaining.stdout.strip():
                    raise gate.PilotBlocked("SANDBOX_CLEANUP_UNVERIFIED")
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


def smoke():
    """Real sandbox smoke with a deterministic reference, then a false-success control.

    This is synthetic harness evidence, not model performance or production edge.
    """
    reference = b"""import datetime, json, re, sys
def ts(s):
    if not isinstance(s, str) or not re.fullmatch(r'\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z', s):
        raise ValueError()
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
def digest(s):
    if not isinstance(s, str) or not re.fullmatch(r'[0-9a-f]{64}', s):
        raise ValueError()
    return s
def verdict(r):
    if set(r)!= {'cutoff_utc','baseline_sha256','published_at_utc','witness'}:
        raise ValueError()
    cutoff=ts(r['cutoff_utc'])
    published=ts(r['published_at_utc'])
    baseline=digest(r['baseline_sha256'])
    w=r['witness']
    if w is not None:
        if set(w)!= {'observed_at_utc','baseline_sha256','independent'} or type(w['independent']) is not bool:
            raise ValueError()
        wt=ts(w['observed_at_utc'])
        wd=digest(w['baseline_sha256'])
        good=wt<cutoff and wd==baseline and w['independent']
    else:
        good=False
    return 'ELIGIBLE' if published<cutoff or good else 'UNKNOWN'
try:
    status=verdict(json.load(sys.stdin))
except (ValueError, TypeError, KeyError):
    status='INVALID'
print(json.dumps({'status':status}))
"""
    good = verify_in_disposable_runner(reference, PINNED_IMAGE)
    bad = verify_in_disposable_runner(b"""print('{"status":"ELIGIBLE"}')\n""", PINNED_IMAGE)
    if good["status"] != "PASS" or bad["status"] != "TEST_FAILURE":
        raise gate.PilotBlocked("SANDBOX_SMOKE_OR_MUTANT_FAILED")
    return {"contract": "ASTRA_WORKLIKE_SANDBOX_SMOKE_v1", "status": "PASS",
            "good": good, "negative": bad, "image": PINNED_IMAGE,
            "model_execution_proven": False, "paid_api": False}

def read_artifact(root, rel, maximum):
    path = root / rel
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise gate.PilotBlocked("ARTIFACT_PATH")
    if not 0 < path.stat().st_size <= maximum:
        raise gate.PilotBlocked("ARTIFACT_SIZE")
    return path.read_bytes()

def strict_json(data):
    def pairs(items):
        if len({k for k, _ in items}) != len(items):
            raise gate.PilotBlocked("DUPLICATE_JSON_KEY")
        return dict(items)
    def nonfinite(_):
        raise gate.PilotBlocked("NONFINITE_JSON")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise gate.PilotBlocked("ARTIFACT_JSON") from exc

def admit_collected(root):
    """Bind the paid artifact to the exact current native run and trusted request.

    Must be called only on a same-workflow artifact in the isolated job.
    Does not execute or write any model code.
    """
    from scripts.research import owner_astra_mission_v1 as owner
    root = Path(root)
    mid = owner.WORKLIKE_STAGE1
    _, _, expected = owner.build_request(mid)
    rb = read_artifact(root, "receipt.json", 32000)
    mb = read_artifact(root, "source_manifest.json", 32000)
    receipt, meta = strict_json(rb), strict_json(mb)
    if not isinstance(receipt, dict) or not isinstance(meta, dict):
        raise gate.PilotBlocked("ARTIFACT_SHAPE")
    if any(meta.get(k) != v for k, v in expected.items()):
        raise gate.PilotBlocked("ARTIFACT_REQUEST_MISMATCH")
    current_run = os.environ.get("GITHUB_RUN_ID", "")
    main = owner.git_head()
    native_run = receipt.get("run_id")
    if (not current_run.isdigit() or not isinstance(native_run, str) or not native_run.isdigit()
            or (native_run != current_run and meta.get("recovered_by_run") != current_run)
            or receipt.get("release_main_sha") != main):
        raise gate.PilotBlocked("ARTIFACT_NATIVE_RUN_MISMATCH")
    if (receipt.get("contract") != "ASTRA_MISSION_RECEIPT_V1"
            or receipt.get("mission_id") != mid or receipt.get("work_id") != mid
            or receipt.get("request_sha256") != expected["request_sha256"]
            or receipt.get("bundle_sha256") != expected["bundle_sha256"]
            or receipt.get("status") != "completed" or receipt.get("incomplete_details") is not None
            or receipt.get("model") != gate.MODEL
            or not owner.provider_model(gate.MODEL).fullmatch(str(receipt.get("provider_model")))
            or not owner.RESPONSE_ID.fullmatch(str(receipt.get("response_id")))
            or receipt.get("reasoning_effort") != gate.EFFORT
            or receipt.get("provider_reasoning_effort") != gate.EFFORT
            or receipt.get("no_retry") is not True or receipt.get("research_only") is not True
            or receipt.get("owner_reserved_usd") != gate.STAGE_CAP_MICROUSD / 1_000_000
            or receipt.get("usage_valid") is not True or receipt.get("output_file") != "ASTRA_RAW_REPORT.md"):
        raise gate.PilotBlocked("ARTIFACT_RECEIPT_INVALID")
    usage = receipt.get("usage")
    if not isinstance(usage, dict):
        raise gate.PilotBlocked("ARTIFACT_USAGE_INVALID")
    ni, no = usage.get("input_tokens"), usage.get("output_tokens")
    if (type(ni) is not int or type(no) is not int or ni < 0 or no < 0
            or ni > expected["input_token_upper"] or no > gate.MAX_OUTPUT_TOKENS):
        raise gate.PilotBlocked("ARTIFACT_USAGE_INVALID")
    cost = owner.estimate_cost(gate.MODEL, ni, no)
    if cost != receipt.get("estimated_upper_usd") or cost > receipt["owner_reserved_usd"]:
        raise gate.PilotBlocked("ARTIFACT_COST_MISMATCH")
    prefix = "archive/" + expected["mission_dir"] + "/results/"
    if (read_artifact(root, prefix+"receipt.json", 32000) != rb
            or read_artifact(root, prefix+"source_manifest.json", 32000) != mb):
        raise gate.PilotBlocked("ARTIFACT_ARCHIVE_COPY_MISMATCH")
    raw = read_artifact(root, prefix+"ASTRA_RAW_REPORT.md", 128000)
    if gate.sha(raw) != receipt.get("output_sha256") or len(raw) != receipt.get("bytes"):
        raise gate.PilotBlocked("ARTIFACT_OUTPUT_MISMATCH")
    if owner.CREDENTIAL.search(raw) or owner.WALLET.search(raw):
        raise gate.PilotBlocked("ARTIFACT_RESTRICTED_PATTERN")
    proposal = strict_json(raw)
    preflight = gate.validate_proposal(proposal, dict.fromkeys(gate.PATHS))
    candidate = next(row["content"].encode("utf-8") for row in proposal["files"]
                     if row["path"] == gate.PATHS[0])
    return candidate, {"mission_id": mid, "native_run_id": current_run,
                       "paid_run_id": native_run, "release_main_sha": main,
                       "receipt_sha256": gate.sha(rb), "request_sha256": expected["request_sha256"],
                       "raw_output_sha256": gate.sha(raw), "proposal": preflight}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("smoke", "verify"))
    parser.add_argument("--input", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.action == "smoke":
        result = smoke()
    else:
        if args.input is None:
            raise gate.PilotBlocked("ARTIFACT_INPUT_MISSING")
        candidate, binding = admit_collected(args.input)
        result = verify_in_disposable_runner(candidate, PINNED_IMAGE)
        result.update(binding)
        result["image"] = PINNED_IMAGE
        result["model_output_executed_in_sandbox"] = True
        result["automatic_repair_authorized"] = False
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("xb") as f:
        f.write(gate.canonical(result)+b"\n")
    print(result["contract"], result["status"], gate.sha(args.out.read_bytes()))
    return 0 if result["status"] == "PASS" else 3

if __name__ == "__main__":
    raise SystemExit(main())
