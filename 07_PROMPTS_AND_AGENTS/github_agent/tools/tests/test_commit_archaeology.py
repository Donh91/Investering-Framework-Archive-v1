import importlib.util
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("commit_archaeology", ROOT / "commit_archaeology.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_tracked_spec_has_git_facts():
    path = "07_PROMPTS_AND_AGENTS/github_agent/2026-07-19__harvested-agent-patterns-v0-1__implementation-spec.md"
    out = mod.analyze(path)
    assert out["status"] == "OK"
    assert out["introducing_commit"]["evidence_class"] == "FACT_FROM_GIT"
    assert out["introducing_commit"]["sha"]


def test_untracked_path_not_determinable():
    out = mod.analyze("07_PROMPTS_AND_AGENTS/github_agent/tools/tests/nope.md")
    assert out["status"] == "NOT_TRACKED"
    assert out["evidence_class"] == "NOT_DETERMINABLE"


def test_valid_line_range_returns_history():
    path = "07_PROMPTS_AND_AGENTS/github_agent/2026-07-19__harvested-agent-patterns-v0-1__implementation-spec.md"
    out = mod.analyze(path, 1, 2)
    assert out["status"] == "OK"
    assert out["line_range"] == [1, 2]
    assert out["introducing_commit"]["sha"]


@pytest.mark.parametrize("start,end", [(1, None), (0, 1), (3, 2)])
def test_invalid_line_range_is_explicit(start, end):
    path = "07_PROMPTS_AND_AGENTS/github_agent/2026-07-19__harvested-agent-patterns-v0-1__implementation-spec.md"
    out = mod.analyze(path, start, end)
    assert out["status"] == "INVALID_LINE_RANGE"
    assert out["evidence_class"] == "NOT_DETERMINABLE"


def test_git_history_error_is_not_ok(monkeypatch):
    path = "07_PROMPTS_AND_AGENTS/github_agent/2026-07-19__harvested-agent-patterns-v0-1__implementation-spec.md"
    original_git = mod.git

    def fake_git(args):
        if args and args[0] == "ls-files":
            return original_git(args)
        if args and args[0] == "log":
            return 128, "", "synthetic git failure"
        return original_git(args)

    monkeypatch.setattr(mod, "git", fake_git)
    out = mod.analyze(path)
    assert out["status"] == "GIT_HISTORY_ERROR"
    assert out["evidence_class"] == "NOT_DETERMINABLE"


def test_rename_and_co_change_are_reported(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "old.txt").write_text("one\n")
    (tmp_path / "peer.txt").write_text("peer\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=tmp_path, check=True)
    subprocess.run(["git", "mv", "old.txt", "new.txt"], cwd=tmp_path, check=True)
    (tmp_path / "peer.txt").write_text("peer two\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "rename and peer"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)

    out = mod.analyze("new.txt")
    assert out["status"] == "OK"
    assert "old.txt" in out["aliases_or_renames"]["paths"]
    assert out["co_changed_files"]["counts"].get("peer.txt", 0) >= 1
