#!/usr/bin/env python3
"""Bound, offline-first skill evaluations. Collect evidence; never release a skill.

Only standard-library dependencies. A command adapter is trusted executable code,
not an OS sandbox. Raw responses and stderr are never included in the report.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import subprocess
import tempfile
import time
from typing import Any, Callable

UNKNOWN = "UNKNOWN"
CALIBRATION_STATES = {"NOT_USED", "UNCALIBRATED_ADVISORY", "CALIBRATED_DEV_ONLY", "CALIBRATED_HELDOUT"}
ASSERTION_KINDS = {"output_contains", "output_excludes", "json_equals", "workspace_unchanged"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def safe_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("UNSAFE_INPUT_PATH")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in {".", "..", ".git"} for part in p.parts) or str(p) != value:
        raise ValueError("UNSAFE_INPUT_PATH")
    return value


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        raise ValueError("IMMUTABLE_GIT_INPUT_UNAVAILABLE")
    return result.stdout


def commit_ref(repo: Path, ref: str) -> str:
    if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError("FULL_COMMIT_SHA_REQUIRED")
    if git(repo, "rev-parse", ref + "^{commit}").decode().strip() != ref:
        raise ValueError("COMMIT_IDENTITY_MISMATCH")
    return ref


def tracked_file(repo: Path, ref: str, path: str) -> bytes:
    safe_path(path)
    tree = git(repo, "ls-tree", ref, "--", path).decode()
    if not tree.startswith(("100644 blob ", "100755 blob ")):
        raise ValueError("REGULAR_TRACKED_FILE_REQUIRED")
    return git(repo, "show", ref + ":" + path)


def bound_json(repo: Path, ref: str, spec: dict) -> tuple[Any, str]:
    data = tracked_file(repo, ref, spec["path"])
    if digest(data) != spec["sha256"]:
        raise ValueError("INPUT_HASH_MISMATCH")
    return json.loads(data), digest(data)


def prepare(repo: Path, plan: dict) -> dict:
    """Resolve all immutable bytes before creating workspaces or calling runners."""
    if plan.get("contract") != "SKILL_QUALITY_RUNTIME_PLAN_v1":
        raise ValueError("PLAN_CONTRACT_INVALID")
    ref = commit_ref(repo, plan["source_ref"])
    name = plan["skill_name"]
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("SKILL_NAME_INVALID")
    repeats = plan["repetitions"]
    if type(repeats) is not int or repeats < 1:
        raise ValueError("REPETITIONS_MUST_BE_POSITIVE_INTEGER")
    cases_doc, cases_hash = bound_json(repo, ref, plan["case_set"])
    assertions, assertions_hash = bound_json(repo, ref, plan["assertions"])
    if cases_doc.get("contract") != "INVESTERING_SKILL_EVAL_CASES_v1":
        raise ValueError("CASE_CONTRACT_INVALID")
    cases = cases_doc["cases"]
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("DUPLICATE_CASE_ID")
    selected = plan["case_ids"]
    if not selected or len(set(selected)) != len(selected):
        raise ValueError("CASE_SELECTION_INVALID")
    by_id = {c["id"]: c for c in cases}
    if any(c not in by_id for c in selected):
        raise ValueError("CASE_ID_UNAVAILABLE")
    selected_cases = [by_id[c] for c in selected]
    for case in selected_cases:
        if case.get("skill") != name or type(case.get("critical")) is not bool or not isinstance(case.get("prompt"), str):
            raise ValueError("CASE_SCOPE_OR_SCHEMA_INVALID")
        checks = assertions.get(case["id"])
        if not isinstance(checks, list) or not checks:
            raise ValueError("DETERMINISTIC_ASSERTIONS_REQUIRED")
        for check in checks:
            if not isinstance(check, dict) or check.get("kind") not in ASSERTION_KINDS:
                raise ValueError("ASSERTION_KIND_INVALID")
            if check["kind"] in {"output_contains", "output_excludes"} and (not isinstance(check.get("value"), str) or not check["value"]):
                raise ValueError("ASSERTION_VALUE_INVALID")
            if check["kind"] == "json_equals" and (not isinstance(check.get("path"), list) or "value" not in check):
                raise ValueError("ASSERTION_VALUE_INVALID")
    conditions = plan["conditions"]
    labels = [c["name"] for c in conditions]
    if len(set(labels)) != len(labels) or set(labels) not in ({"baseline", "candidate"}, {"baseline", "candidate", "no_skill"}):
        raise ValueError("BASELINE_AND_CANDIDATE_REQUIRED")
    frozen_conditions = []
    for condition in conditions:
        if condition["name"] == "no_skill":
            if condition.get("skill") is not None:
                raise ValueError("NO_SKILL_CONDITION_HAS_SKILL")
            frozen_conditions.append({"name": "no_skill", "binding": None, "bytes": None})
            continue
        spec = condition["skill"]
        skill_ref = commit_ref(repo, spec["ref"])
        data = tracked_file(repo, skill_ref, spec["path"])
        blob = git(repo, "rev-parse", skill_ref + ":" + spec["path"]).decode().strip()
        if blob != spec["blob_sha"]:
            raise ValueError("SKILL_BLOB_MISMATCH")
        frozen_conditions.append({"name": condition["name"], "binding": {**spec, "sha256": digest(data)}, "bytes": data})
    context = {}
    for path in plan.get("context_paths", []):
        safe_path(path)
        # Do not accidentally load other skills, user plugins, hooks or credentials.
        if any(part.startswith(".") for part in PurePosixPath(path).parts) or path in context:
            raise ValueError("CONTEXT_PATH_INVALID")
        context[path] = tracked_file(repo, ref, path)
    return {"conditions": frozen_conditions, "cases": selected_cases, "assertions": assertions,
            "context": context, "cases_hash": cases_hash, "assertions_hash": assertions_hash}


def workspace_state(root: Path) -> dict[str, str]:
    """Record bytes without following symlinks or retaining file contents."""
    state = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs[:] + files:
            path = Path(directory) / name
            key = path.relative_to(root).as_posix()
            if path.is_symlink():
                state[key] = "SYMLINK:" + digest(os.readlink(path).encode())
                if name in dirs:
                    dirs.remove(name)
            elif path.is_file():
                state[key] = digest(path.read_bytes())
    return state


def check_output(check: dict, output: str, unchanged: bool) -> bool:
    kind = check["kind"]
    if kind == "workspace_unchanged":
        return unchanged
    if kind == "output_contains":
        return check["value"] in output
    if kind == "output_excludes":
        return check["value"] not in output
    try:
        value = json.loads(output)
        for key in check["path"]:
            value = value[key]
        # JSON true is not interchangeable with numeric 1.
        return canonical(value) == canonical(check["value"])
    except (ValueError, TypeError, KeyError, IndexError):
        return False


class FixtureRunner:
    """Canned response replay exercises the harness, never model behavior."""
    kind = "OFFLINE_FIXTURE"

    def __init__(self, fixture: dict):
        self.fixture = copy.deepcopy(fixture)

    def __call__(self, request: dict, workspace: Path) -> dict:
        response = self.fixture.get(request["case_id"])
        if response is None:
            return {"status": "INCOMPLETE", "output": ""}
        return copy.deepcopy(response)


class CommandRunner:
    """Explicit opt-in adapter: JSON request on stdin, JSON response on stdout.

    Supply a separately authorized, trusted executable. Its own sandbox must
    constrain network and filesystem access; a temporary directory alone cannot.
    """
    kind = "LIVE_ADAPTER"

    def __init__(self, argv: list[str], *, authorized: bool, timeout: float = 60):
        if authorized is not True:
            raise ValueError("LIVE_EXECUTION_NOT_AUTHORIZED")
        if not argv or not all(isinstance(s, str) and s for s in argv):
            raise ValueError("COMMAND_ARGV_INVALID")
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("TIMEOUT_INVALID")
        self.argv, self.timeout = argv[:], timeout

    def __call__(self, request: dict, workspace: Path) -> dict:
        with tempfile.TemporaryDirectory(prefix="skill-eval-home-") as home:
            # Never inherit credentials, user-level Codex config, proxies or hooks.
            env = {"PATH": os.defpath, "HOME": home, "CODEX_HOME": home,
                   "TMPDIR": home, "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
            try:
                proc = subprocess.run(self.argv, input=canonical(request), cwd=workspace,
                                      env=env, capture_output=True, timeout=self.timeout, check=False)
            except subprocess.TimeoutExpired:
                return {"status": "INCOMPLETE", "output": "", "error_code": "ADAPTER_TIMEOUT"}
            if proc.returncode:
                return {"status": "FAILED", "output": "", "error_code": "ADAPTER_NONZERO_EXIT"}
            try:
                return json.loads(proc.stdout)
            except (ValueError, UnicodeDecodeError):
                return {"status": "FAILED", "output": "", "error_code": "ADAPTER_INVALID_JSON"}


def metric(value: Any) -> Any:
    if type(value) in (int, float) and math.isfinite(value) and value >= 0:
        return value
    return UNKNOWN


def evaluate(repo: Path, plan: dict, runner: Callable, *, judge: Callable | None = None) -> dict:
    plan = copy.deepcopy(plan)
    frozen = prepare(repo, plan)
    kind = getattr(runner, "kind", "OFFLINE_FIXTURE")
    if kind not in {"OFFLINE_FIXTURE", "LIVE_ADAPTER"}:
        raise ValueError("RUNNER_KIND_INVALID")
    calibration = plan.get("evaluator_calibration_state", "NOT_USED")
    if calibration not in CALIBRATION_STATES:
        raise ValueError("CALIBRATION_STATE_INVALID")
    report = {"contract": "SKILL_QUALITY_RUNTIME_EVIDENCE_v1", "plan_sha256": digest(canonical(plan)),
              "source_ref": plan["source_ref"], "skill_name": plan["skill_name"],
              "case_set_sha256": frozen["cases_hash"], "assertions_sha256": frozen["assertions_hash"],
              "case_ids": plan["case_ids"], "repetitions": plan["repetitions"], "execution_kind": kind,
              "runtime_model": plan.get("runtime_model", UNKNOWN) if kind == "LIVE_ADAPTER" else UNKNOWN,
              "runtime_effort": plan.get("runtime_effort", UNKNOWN) if kind == "LIVE_ADAPTER" else UNKNOWN,
              "runtime_identity_source": "OPERATOR_DECLARED_NOT_VERIFIED" if kind == "LIVE_ADAPTER" else "NOT_APPLICABLE",
              "live_runtime_status": UNKNOWN, "adapter_attempts": 0,
              "isolation": "FRESH_TEMP_WORKSPACE_PER_RUN_NOT_OS_SECURITY_SANDBOX",
              "context_sha256": {p: digest(b) for p, b in frozen["context"].items()},
              "conditions": [], "runs": [], "release_authority": "NONE",
              "behavioral_superiority": "NOT_ESTABLISHED", "baseline_without_skill_value": "NOT_EVALUATED",
              "calibration_claim": calibration, "calibration_verified": False,
              "judge_release_authority": "NONE", "raw_outputs_retained": False}
    blind_outputs = []
    labels = secrets.SystemRandom().sample(list("ABC"), len(frozen["conditions"]))
    for ordinal, condition in enumerate(frozen["conditions"]):
        label = labels[ordinal]
        report["conditions"].append({"label": label, "name": condition["name"], "skill": condition["binding"]})
        for repetition in range(plan["repetitions"]):
            for case in frozen["cases"]:
                temp = tempfile.TemporaryDirectory(prefix="skill-eval-")
                workspace = Path(temp.name)
                output = ""
                row = {"condition": label, "case_id": case["id"], "repetition": repetition + 1,
                       "critical": case["critical"], "status": "FAILED", "error_code": None,
                       "usage": {"input_tokens": UNKNOWN, "output_tokens": UNKNOWN, "cost_usd": UNKNOWN},
                       "cleanup_status": "UNKNOWN", "deterministic_pass": False,
                       "assertions": [], "side_effects": [], "side_effect_observation": "UNKNOWN",
                       "observed_wall_ms": UNKNOWN, "output_sha256": digest(b"")}
                try:
                    for path, data in frozen["context"].items():
                        target = workspace / path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(data)
                    if condition["bytes"] is not None:
                        target = workspace / ".agents/skills" / plan["skill_name"] / "SKILL.md"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(condition["bytes"])
                    before = workspace_state(workspace)
                    request = {"case_id": case["id"], "prompt": case["prompt"], "repetition": repetition + 1,
                               "instruction": "Complete the task using the provided workspace and any installed skill; preserve project authority."}
                    row["request_sha256"] = digest(canonical(request))
                    started = time.perf_counter()
                    try:
                        if kind == "LIVE_ADAPTER":
                            report["adapter_attempts"] += 1
                        response = runner(copy.deepcopy(request), workspace)
                        if not isinstance(response, dict) or response.get("status") not in {"COMPLETED", "FAILED", "INCOMPLETE"} or not isinstance(response.get("output"), str):
                            raise ValueError("RUNNER_RESPONSE_INVALID")
                        output = response["output"]
                        row["status"] = response["status"]
                        row["error_code"] = response.get("error_code") if response.get("error_code") in {"ADAPTER_TIMEOUT", "ADAPTER_NONZERO_EXIT", "ADAPTER_INVALID_JSON"} else None
                        usage = response.get("usage", {})
                        if kind == "LIVE_ADAPTER" and isinstance(usage, dict):
                            row["usage"] = {k: metric(usage.get(k)) for k in row["usage"]}
                    except Exception:
                        # Exception text may contain secrets. Preserve failure, not text.
                        row["status"], row["error_code"] = "FAILED", "RUNNER_ERROR"
                    row["observed_wall_ms"] = round((time.perf_counter() - started) * 1000, 3)
                    after = workspace_state(workspace)
                    changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
                    row["side_effects"] = [{"path_sha256": digest(p.encode()), "before_sha256": before.get(p), "after_sha256": after.get(p)} for p in changed]
                    row["side_effect_observation"] = "COMPLETE_WITHIN_WORKSPACE"
                    row["assertions"] = [check_output(c, output, not changed) for c in frozen["assertions"][case["id"]]]
                    row["deterministic_pass"] = row["status"] == "COMPLETED" and all(row["assertions"])
                    row["output_sha256"] = digest(output.encode())
                except Exception:
                    row["status"], row["error_code"] = "FAILED", "WORKSPACE_OR_GRADING_ERROR"
                    row["deterministic_pass"] = False
                    row["output_sha256"] = digest(output.encode())
                finally:
                    try:
                        temp.cleanup()
                        row["cleanup_status"] = "PASS" if not workspace.exists() else "FAIL"
                    except OSError:
                        row["cleanup_status"] = "FAIL"
                report["runs"].append(row)
                blind_outputs.append({"label": label, "case_id": case["id"], "repetition": repetition + 1,
                                      "status": row["status"], "deterministic_pass": row["deterministic_pass"], "output": output})
    if kind == "LIVE_ADAPTER":
        report["live_runtime_status"] = ("ADAPTER_ATTEMPTED_MODEL_EXECUTION_UNVERIFIED"
                                         if report["adapter_attempts"] else "NOT_ATTEMPTED")
    # All objective grades are frozen before a subjective observer sees outputs.
    report["judge_status"] = "NOT_USED"
    if judge is not None:
        try:
            # Neither fixed labels nor grouped iteration order reveal conditions.
            shuffled = copy.deepcopy(blind_outputs)
            secrets.SystemRandom().shuffle(shuffled)
            judgment = judge(shuffled)
            report["judge_observation_sha256"] = digest(canonical(judgment))
            report["judge_status"] = "ADVISORY_ONLY"
        except Exception:
            report["judge_status"] = "FAILED_ADVISORY_ONLY"
    report["summary"] = {}
    for condition in report["conditions"]:
        rows = [r for r in report["runs"] if r["condition"] == condition["label"]]
        report["summary"][condition["name"]] = {
            "total": len(rows), "passed": sum(r["deterministic_pass"] for r in rows),
            "failed": sum(r["status"] == "FAILED" for r in rows),
            "incomplete": sum(r["status"] == "INCOMPLETE" for r in rows),
            "critical_failures": sum(r["critical"] and not r["deterministic_pass"] for r in rows)}
    report["deterministic_blockers"] = [{"condition": r["condition"], "case_id": r["case_id"], "repetition": r["repetition"]}
                                        for r in report["runs"] if not r["deterministic_pass"] or r["cleanup_status"] != "PASS"]
    report["evidence_status"] = "BLOCKED_BY_DETERMINISTIC_EVIDENCE" if report["deterministic_blockers"] else "COLLECTED_FOR_REVIEW"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--plan", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", type=Path)
    mode.add_argument("--command-json", help="JSON argv of a separately authorized trusted adapter")
    parser.add_argument("--authorize-live", action="store_true")
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_bytes())
        runner = FixtureRunner(json.loads(args.fixture.read_bytes())) if args.fixture else CommandRunner(json.loads(args.command_json), authorized=args.authorize_live, timeout=args.timeout)
        report = evaluate(args.repo_root.resolve(), plan, runner)
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
        return 1 if report["deterministic_blockers"] else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        error = str(exc)
        code = error if re.fullmatch(r"[A-Z_]{1,80}", error) else "INPUT_OR_RUNTIME_ERROR"
        print(json.dumps({"contract": "SKILL_QUALITY_RUNTIME_EVIDENCE_v1", "evidence_status": "INPUT_OR_RUNTIME_BLOCKED", "error_code": code, "release_authority": "NONE"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
