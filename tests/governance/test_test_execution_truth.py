"""Guard the native pytest execution receipt, not only test collection."""
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from scripts.governance.check_test_execution_truth import (
    EXECUTE_COMMAND,
    WORKFLOW_STEP,
    executed_test_files,
    verify,
    workflow_executes_tests,
)


def sample_workflow(command=EXECUTE_COMMAND, *, enabled=True):
    marker = "        if: github.event_name == 'pull_request'\n" if enabled else ""
    return ("      " + WORKFLOW_STEP + "\n" + marker +
            "        timeout-minutes: 18\n        run: |\n          " + command + "\n"
            "      - name: Next step\n        run: echo done\n")


def test_real_execution_step_required_not_collect_only():
    assert workflow_executes_tests(sample_workflow())
    for bad in (
        sample_workflow("python -m pytest --collect-only -q tests"),
        sample_workflow(EXECUTE_COMMAND + " || true"),
        sample_workflow(EXECUTE_COMMAND.replace(" tests", " -k smoke tests")),
        sample_workflow(EXECUTE_COMMAND.replace("--junitxml=/tmp/full-repository-tests.xml ", "")),
        sample_workflow(enabled=False),
        sample_workflow().replace("timeout-minutes: 18", "continue-on-error: true"),
        sample_workflow().replace(WORKFLOW_STEP, "- name: Only collect test names"),
    ):
        assert not workflow_executes_tests(bad)


def test_junit_tracks_actual_cases_and_not_only_collected(tmp_path: Path):
    expected = ["tests/governance/test_a.py", "tests/api_agent/test_b.py"]
    xml = tmp_path / "report.xml"
    xml.write_text('<testsuites><testsuite tests="2"><testcase classname="tests.governance.test_a" name="test_ok"/>'
                   '<testcase classname="tests.api_agent.test_b" name="test_skip"><skipped/></testcase>'
                   '</testsuite></testsuites>')
    executed, total, skipped = executed_test_files(xml, expected)
    assert executed == {"tests/governance/test_a.py"}
    assert total == 2 and skipped == 1
    root = tmp_path
    for file in expected:
        p = root / file
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("def test_ok(): pass\n")
    wf = root / "workflow.yml"
    wf.write_text(sample_workflow())
    with pytest.raises(ValueError, match="UNEXECUTED_TEST_FILES:tests/api_agent/test_b.py"):
        verify(root, wf, xml, ["tests"])
    xml.write_text('<testsuites><testsuite tests="2">'
                   '<testcase classname="tests.governance.test_a" name="test_ok"/>'
                   '<testcase classname="tests.api_agent.test_b.TestSuite" name="test_b"/>'
                   '</testsuite></testsuites>')
    result = verify(root, wf, xml, ["tests"])
    assert result["status"] == "PASS" and result["test_files"] == 2


def test_missing_or_corrupt_xml_fails_closed(tmp_path: Path):
    with pytest.raises(ValueError, match="JUNIT_XML_MISSING"):
        executed_test_files(tmp_path / "missing.xml", ["tests/test_a.py"])
    xml = tmp_path / "bad.xml"
    xml.write_text("<testsuites><testsuite>")
    with pytest.raises(ET.ParseError):
        executed_test_files(xml, ["tests/test_a.py"])
    xml.write_text("<testsuites></testsuites>")
    with pytest.raises(ValueError, match="NO_EXECUTED_TESTCASES"):
        executed_test_files(xml, ["tests/test_a.py"])


def test_actual_workflow_has_real_runner():
    wf = Path(".github/workflows/automation-production-health-gate.yml").read_text(encoding="utf-8")
    assert workflow_executes_tests(wf)
