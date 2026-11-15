#!/usr/bin/env python3
"""Fail closed when CI merely collects tests or leaves Python test files unexecuted.

This is a PR-side runtime receipt validator, not a new scheduler or a green badge based
on workflow source alone. Collection is checked separately by the existing guard.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

# A direct 'python scripts/governance/...' CLI starts with scripts/governance
# on sys.path, unlike 'python -m pytest'. Support both without a second parser.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))
from scripts.governance.check_test_collection_truth import test_files

WORKFLOW_STEP = "- name: Execute full repository tests (no collect-only)"
EXECUTE_COMMAND = "python -m pytest -q --import-mode=importlib -p no:cacheprovider --junitxml=/tmp/full-repository-tests.xml tests"


def workflow_executes_tests(source: str) -> bool:
    """Strictly require a real nonoptional PR test step with an exact all-tests command."""
    if source.count(WORKFLOW_STEP) != 1:
        return False
    block = source.split(WORKFLOW_STEP, 1)[1].split("\n      - ", 1)[0]
    lines = [line.strip() for line in block.splitlines()]
    if "if: github.event_name == 'pull_request'" not in lines:
        return False
    if "continue-on-error: true" in lines or "timeout-minutes: 18" not in lines:
        return False
    if EXECUTE_COMMAND not in lines:
        return False
    cmd = lines[lines.index(EXECUTE_COMMAND)]
    if any(x in cmd for x in ("--collect-only", "--ignore", "|| true", " -k ", "--deselect", "; true")):
        return False
    # `python -m pytest` is module invocation, NOT a pytest `-m marker` filter.
    if " -m " in cmd.split("pytest", 1)[1]:
        return False
    return True


def executed_test_files(junit_xml: Path, expected: list[str]) -> tuple[set[str], int, int]:
    """Map actual JUnit testcase classnames to exact test files, excluding skipped-only files."""
    if not junit_xml.exists():
        raise ValueError("JUNIT_XML_MISSING")
    parsed = ET.parse(junit_xml)
    cases = list(parsed.getroot().iter("testcase"))
    if not cases:
        raise ValueError("NO_EXECUTED_TESTCASES")
    prefixes = sorted(
        ((file.removesuffix(".py").replace("/", "."), file) for file in expected),
        key=lambda item: len(item[0]), reverse=True,
    )
    found: set[str] = set()
    skipped = 0
    for case in cases:
        if case.find("skipped") is not None:
            skipped += 1
            continue
        classname = (case.get("classname") or "").strip()
        matches = [
            file for module, file in prefixes
            if classname == module or classname.startswith(module + ".")
        ]
        if matches:
            found.add(matches[0])
    return found, len(cases), skipped


def verify(repo_root: Path, workflow: Path, xml: Path, roots: list[str]) -> dict:
    source = workflow.read_text(encoding="utf-8")
    if not workflow_executes_tests(source):
        raise ValueError("FULL_SUITE_EXECUTION_STEP_MISSING_OR_UNSAFE")
    expected = test_files(repo_root, roots)
    if not expected:
        raise ValueError("NO_TEST_FILES")
    actual, case_count, skipped = executed_test_files(xml, expected)
    missing = sorted(set(expected) - actual)
    if missing:
        raise ValueError("UNEXECUTED_TEST_FILES:" + ",".join(missing))
    return {
        "contract": "TEST_EXECUTION_TRUTH_v1",
        "status": "PASS",
        "test_files": len(expected),
        "files_with_executed_case": len(actual),
        "testcases_reported": case_count,
        "skipped_testcases": skipped,
        "source": "REAL_JUNIT_NATIVE_HOSTED_PYTEST_RUN",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--junit-xml", type=Path, required=True)
    parser.add_argument("--root", action="append", dest="roots", required=True)
    args = parser.parse_args()
    try:
        result = verify(args.repo_root, args.workflow, args.junit_xml, args.roots)
    except (ValueError, ET.ParseError, OSError) as exc:
        print(f"TEST_EXECUTION_TRUTH_FAIL:{exc}")
        return 1
    print("TEST_EXECUTION_TRUTH_PASS " + " ".join(f"{k}={v}" for k, v in result.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
