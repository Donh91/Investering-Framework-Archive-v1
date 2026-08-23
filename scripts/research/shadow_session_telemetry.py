#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_command(command: List[str]) -> Dict[str, Any]:
    if not command:
        raise ValueError("command is required")

    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    completed = subprocess.run(command, capture_output=True, check=False)
    duration = time.perf_counter() - t0
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)

    return {
        "contract": "SHADOW_SESSION_TELEMETRY_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "external_backend": False,
        "raw_output_persisted": False,
        "started_at_utc": started.isoformat(),
        "duration_ms": round(duration * 1000.0, 3),
        "exit_code": completed.returncode,
        "command_executable": Path(command[0]).name,
        "command_arg_count": max(0, len(command) - 1),
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "stdout_sha256": _sha256(completed.stdout),
        "stderr_sha256": _sha256(completed.stderr),
        "max_rss_kb": int(usage.ru_maxrss),
        "pid": os.getpid(),
        "privacy_policy": "RAW_STDOUT_STDERR_NEVER_WRITTEN",
    }


def self_test() -> Dict[str, Any]:
    ok = run_command([sys.executable, "-c", "print('ok')"])
    fail = run_command([sys.executable, "-c", "raise SystemExit(3)"])
    checks = {
        "success_exit_captured": ok["exit_code"] == 0,
        "failure_exit_captured": fail["exit_code"] == 3,
        "raw_output_not_persisted": ok["raw_output_persisted"] is False and fail["raw_output_persisted"] is False,
        "hash_shape": len(ok["stdout_sha256"]) == 64 and len(fail["stderr_sha256"]) == 64,
        "stable_contract": ok["contract"] == fail["contract"] == "SHADOW_SESSION_TELEMETRY_v1",
        "no_external_backend": ok["external_backend"] is False and fail["external_backend"] is False,
    }
    return {
        "contract": "SHADOW_SESSION_TELEMETRY_SELF_TEST_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "success_sample": {k: ok[k] for k in ("duration_ms", "exit_code", "stdout_bytes", "stderr_bytes", "max_rss_kb")},
        "failure_sample": {k: fail[k] for k in ("duration_ms", "exit_code", "stdout_bytes", "stderr_bytes", "max_rss_kb")},
    }


def _write(report: Dict[str, Any], output: str | None) -> None:
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.self_test:
        report = self_test()
        _write(report, args.output)
        return 0 if report["status"] == "PASS" else 1

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("command required after --")

    report = run_command(command)
    _write(report, args.output)
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
