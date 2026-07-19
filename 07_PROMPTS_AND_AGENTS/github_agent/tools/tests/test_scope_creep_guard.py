import argparse
import importlib.util
import io
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scope_creep_guard", ROOT / "scope_creep_guard.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_in_scope_fixture_keeps():
    diff = (ROOT / "tests/fixtures/in_scope.diff").read_text()
    out = mod.analyze("Wave A github_agent tools only", diff)
    assert out["status"] == "KEEP"
    assert out["changed_paths"] == [
        "07_PROMPTS_AND_AGENTS/github_agent/tools/scope_creep_guard.py"
    ]


def test_workflow_dependency_and_deletion_block():
    diff = (
        (ROOT / "tests/fixtures/block_workflow.diff").read_text()
        + "\ndiff --git a/requirements.txt b/requirements.txt\n+x\n"
        + "\ndiff --git a/old.md b/old.md\ndeleted file mode 100644\n"
    )
    out = mod.analyze("Wave A github_agent tools only", diff)
    codes = {finding["code"] for finding in out["findings"]}
    assert out["status"] == "BLOCK_REVIEW"
    assert {
        "WORKFLOW_OR_SCHEDULE_CHANGE",
        "DEPENDENCY_MANIFEST_CHANGE",
        "DESTRUCTIVE_OR_MOVE_SIGNAL",
    } <= codes


def test_invalid_base_never_returns_keep(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)
    ns = argparse.Namespace(staged=False, base="definitely-missing-ref", diff=None)
    with pytest.raises(mod.DiffSourceError):
        mod.read_diff(ns)


def test_stdin_diff_is_read(monkeypatch):
    expected = (ROOT / "tests/fixtures/in_scope.diff").read_text()
    monkeypatch.setattr(mod.sys, "stdin", io.StringIO(expected))
    ns = argparse.Namespace(staged=False, base=None, diff="-")
    assert mod.read_diff(ns) == expected


def test_clean_staged_diff_is_deterministic(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)
    ns = argparse.Namespace(staged=True, base=None, diff=None)
    assert mod.read_diff(ns) == ""
    assert mod.analyze("Wave A github_agent tools only", "")["status"] == "KEEP"
