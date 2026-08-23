#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SECRET_ENV_RE = re.compile(r"(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)", re.IGNORECASE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8", errors="replace"))


def clean_runtime_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env: dict[str, str] = {}
    allow = {
        "PATH",
        "HOME",
        "TMPDIR",
        "TMP",
        "TEMP",
        "RUNNER_TEMP",
        "GITHUB_ACTIONS",
        "CI",
        "LANG",
        "LC_ALL",
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "PYTHONDONTWRITEBYTECODE",
        "PYTHONPYCACHEPREFIX",
        "NODE_OPTIONS",
    }
    for key, value in os.environ.items():
        if key in allow and not SECRET_ENV_RE.search(key):
            env[key] = value
    if extra:
        env.update(extra)
    return env


def run_cmd(
    argv: list[str],
    *,
    cwd: Path,
    env_extra: dict[str, str] | None = None,
    timeout: int = 120,
) -> tuple[dict[str, Any], str, str]:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            env=clean_runtime_env(env_extra),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        timed_out = False
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        returncode = 124
    duration_ms = round((time.perf_counter() - started) * 1000.0, 3)
    record = {
        "argv_head": Path(argv[0]).name,
        "arg_count": len(argv) - 1,
        "returncode": returncode,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
        "stderr_bytes": len(stderr.encode("utf-8", errors="replace")),
        "stdout_sha256": hash_text(stdout),
        "stderr_sha256": hash_text(stderr),
    }
    return record, stdout, stderr


def git_status(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git status failed")
    return proc.stdout


def snapshot_tree(root: Path) -> dict[str, Any]:
    files = []
    total_bytes = 0
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        files.append(path.relative_to(root).as_posix())
        total_bytes += path.stat().st_size
    return {"file_count": len(files), "bytes": total_bytes}


def copy_arm_fixture(source: Path, arm: str) -> Path:
    dest = source.parent / f"{source.name}_{arm.lower()}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    if git_status(dest) != "":
        raise RuntimeError(f"copied_fixture_not_clean:{arm}")
    return dest


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pin_map(pins: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in pins["pins"]}


def baseline_probe(fixture: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    definitions: set[str] = set()
    edges: set[tuple[str, str]] = set()
    for path in sorted((fixture / "app").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                definitions.add(node.name)
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            edges.add((node.name, child.func.id))
                        elif isinstance(child.func, ast.Attribute):
                            edges.add((node.name, child.func.attr))
    expected_symbols = set(manifest["expected_symbols"])
    expected_edges = {tuple(row) for row in manifest["expected_call_edges"]}
    missing_symbols = sorted(expected_symbols - definitions)
    missing_edges = sorted(expected_edges - edges)
    return {
        "status": "PASS" if not missing_symbols and not missing_edges else "FAIL",
        "definitions_found": sorted(definitions),
        "expected_symbol_count": len(expected_symbols),
        "expected_edge_count": len(expected_edges),
        "missing_symbols": missing_symbols,
        "missing_edges": [list(x) for x in missing_edges],
    }


def version_ok(output: str, expected: str) -> bool:
    return expected in output.strip()


def graft_probe(fixture: Path, expected_version: str) -> dict[str, Any]:
    commands: list[dict[str, Any]] = []
    env = {"CI": "1", "DO_NOT_TRACK": "1", "GRAFT_NO_REFRESH": "1"}
    checks: list[bool] = []

    rec, out, err = run_cmd(["graft", "--version"], cwd=fixture, env_extra=env, timeout=30)
    commands.append(rec)
    checks.append(rec["returncode"] == 0 and version_ok(out + err, expected_version))

    for argv, needle in (
        (["graft", "build", str(fixture)], None),
        (["graft", "grep", "load_customer", str(fixture), "--no-refresh"], "load_customer"),
        (["graft", "callers", "load_customer", str(fixture), "--direction", "out", "--no-refresh"], "fetch_customer"),
        (["graft", "map", str(fixture), "--no-refresh"], "app"),
        (["graft", "check", str(fixture)], None),
    ):
        rec, out, err = run_cmd(argv, cwd=fixture, env_extra=env, timeout=120)
        commands.append(rec)
        checks.append(rec["returncode"] == 0 and (needle is None or needle.lower() in out.lower()))

    return {
        "status": "QUALIFIED_FOR_STAGE_B" if all(checks) else "BLOCK",
        "version_expected": expected_version,
        "checks_passed": sum(1 for value in checks if value),
        "checks_total": len(checks),
        "commands": commands,
        "fixture_after": snapshot_tree(fixture),
    }


def compact_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def cbm_probe(fixture: Path, expected_version: str, cache: Path) -> dict[str, Any]:
    cache.mkdir(parents=True, exist_ok=True)
    env = {
        "CI": "1",
        "CBM_ALLOWED_ROOT": str(fixture),
        "CBM_CACHE_DIR": str(cache),
    }
    commands: list[dict[str, Any]] = []
    checks: list[bool] = []

    rec, out, err = run_cmd(["codebase-memory-mcp", "--version"], cwd=fixture, env_extra=env, timeout=30)
    commands.append(rec)
    checks.append(rec["returncode"] == 0 and version_ok(out + err, expected_version))

    documented_calls = [
        ("index_repository", {"repo_path": str(fixture)}, None, 180),
        ("list_projects", {}, None, 60),
        ("search_graph", {"name_pattern": ".*load_customer.*", "label": "Function"}, "load_customer", 60),
        ("trace_call_path", {"function_name": "load_customer", "direction": "both"}, "load_customer", 60),
        ("get_architecture", {}, None, 60),
    ]
    for tool, payload, needle, timeout in documented_calls:
        rec, out, err = run_cmd(
            ["codebase-memory-mcp", "cli", tool, compact_json(payload)],
            cwd=fixture,
            env_extra=env,
            timeout=timeout,
        )
        commands.append(rec)
        text = (out + "\n" + err).lower()
        checks.append(rec["returncode"] == 0 and (needle is None or needle.lower() in text))

    return {
        "status": "QUALIFIED_FOR_STAGE_B" if all(checks) else "BLOCK",
        "version_expected": expected_version,
        "cli_contract": "DOCUMENTED_JSON_ARGUMENT",
        "checks_passed": sum(1 for value in checks if value),
        "checks_total": len(checks),
        "commands": commands,
        "cache_after": snapshot_tree(cache),
        "fixture_after": snapshot_tree(fixture),
        "runtime_bootstrap_complexity_tax": "NPM_WRAPPER_DOWNLOADS_VERIFIED_NATIVE_RUNTIME_SET",
    }


def inspect_probe(fixture: Path, expected_version: str) -> dict[str, Any]:
    code = """
import importlib.metadata
from inspect_ai import Task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import exact
from inspect_ai.solver import generate
version = importlib.metadata.version('inspect-ai')
task = Task(
    dataset=[Sample(input='round2', target='round2')],
    solver=generate(),
    scorer=exact(),
)
print(version)
print(type(task).__name__)
print(len(task.dataset))
"""
    rec, out, err = run_cmd([sys.executable, "-c", code], cwd=fixture, timeout=60)
    checks = [
        rec["returncode"] == 0,
        version_ok(out, expected_version),
        "Task" in out,
        out.strip().splitlines()[-1:] == ["1"],
    ]
    return {
        "status": "QUALIFIED_FOR_STAGE_B" if all(checks) else "BLOCK",
        "version_expected": expected_version,
        "checks_passed": sum(1 for value in checks if value),
        "checks_total": len(checks),
        "commands": [rec],
        "fixture_after": snapshot_tree(fixture),
    }


def promptfoo_probe(fixture: Path, expected_version: str) -> dict[str, Any]:
    env = {
        "CI": "1",
        "PROMPTFOO_DISABLE_TELEMETRY": "1",
        "PROMPTFOO_DISABLE_UPDATE": "1",
        "PROMPTFOO_DISABLE_REMOTE_GENERATION": "1",
        "PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION": "1",
        "PROMPTFOO_DISABLE_SHARING": "1",
    }
    commands: list[dict[str, Any]] = []
    checks: list[bool] = []

    rec, out, err = run_cmd(["promptfoo", "--version"], cwd=fixture, env_extra=env, timeout=30)
    commands.append(rec)
    checks.append(rec["returncode"] == 0 and version_ok(out + err, expected_version))

    rec, out, err = run_cmd(
        ["promptfoo", "validate", "-c", str(fixture / "promptfooconfig.yaml")],
        cwd=fixture,
        env_extra=env,
        timeout=60,
    )
    commands.append(rec)
    checks.append(rec["returncode"] == 0)

    return {
        "status": "QUALIFIED_FOR_STAGE_B" if all(checks) else "BLOCK",
        "version_expected": expected_version,
        "checks_passed": sum(1 for value in checks if value),
        "checks_total": len(checks),
        "commands": commands,
        "fixture_after": snapshot_tree(fixture),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-root", type=Path, required=True)
    parser.add_argument("--fixture-manifest", type=Path, required=True)
    parser.add_argument("--pins", type=Path, required=True)
    parser.add_argument("--cbm-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    fixture = args.fixture_root.resolve()
    repo = REPO_ROOT.resolve()
    if fixture == repo or repo in fixture.parents:
        raise SystemExit("fixture_must_be_outside_framework_checkout")

    manifest = load_json(args.fixture_manifest)
    pins = pin_map(load_json(args.pins))
    before_status = git_status(repo)
    fixture_before = snapshot_tree(fixture)
    if git_status(fixture) != "":
        raise SystemExit("source_fixture_must_begin_clean")

    graft_fixture = copy_arm_fixture(fixture, "graft")
    cbm_fixture = copy_arm_fixture(fixture, "codebase_memory")
    inspect_fixture = copy_arm_fixture(fixture, "inspect_ai")
    promptfoo_fixture = copy_arm_fixture(fixture, "promptfoo")

    evidence = {
        "contract": "AGENT_TOOL_SHADOW_ROUND2_STAGE_A_EVIDENCE_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "stage_a_auto_promotion_permitted": False,
        "fixture_hash": manifest["fixture_hash"],
        "fixture_before": fixture_before,
        "arm_fixture_isolation": "BYTE_IDENTICAL_INDEPENDENT_COPIES",
        "upstream_pins": {
            key: {
                "repository": value["repository"],
                "version": value["version"],
                "source_main_observed_sha": value["source_main_observed_sha"],
            }
            for key, value in pins.items()
        },
        "candidates": {},
    }

    evidence["candidates"]["BASELINE"] = baseline_probe(fixture, manifest)
    evidence["candidates"]["GRAFT"] = graft_probe(graft_fixture, pins["GRAFT"]["version"])
    evidence["candidates"]["CODEBASE_MEMORY"] = cbm_probe(
        cbm_fixture, pins["CODEBASE_MEMORY"]["version"], args.cbm_cache.resolve()
    )
    evidence["candidates"]["INSPECT_AI"] = inspect_probe(inspect_fixture, pins["INSPECT_AI"]["version"])
    evidence["candidates"]["PROMPTFOO"] = promptfoo_probe(promptfoo_fixture, pins["PROMPTFOO"]["version"])

    after_status = git_status(repo)
    repository_clean = before_status == after_status == ""
    source_fixture_clean = git_status(fixture) == ""
    evidence["framework_checkout_clean"] = repository_clean
    evidence["source_fixture_clean"] = source_fixture_clean
    statuses = {key: row["status"] for key, row in evidence["candidates"].items()}
    all_qualified = (
        repository_clean
        and source_fixture_clean
        and statuses["BASELINE"] == "PASS"
        and all(
            statuses[key] == "QUALIFIED_FOR_STAGE_B"
            for key in ("GRAFT", "CODEBASE_MEMORY", "INSPECT_AI", "PROMPTFOO")
        )
    )
    evidence["status"] = "PASS" if all_qualified else "BLOCK"
    evidence["decision"] = "EVIDENCE_ONLY_NO_PROMOTION"
    evidence["stage_b_authorized"] = all_qualified
    evidence["raw_stdout_stderr_persisted"] = False
    evidence["provider_credentials_available_to_candidate_runtime"] = False

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "candidate_statuses": statuses}, sort_keys=True))
    return 0 if all_qualified else 2


if __name__ == "__main__":
    raise SystemExit(main())
