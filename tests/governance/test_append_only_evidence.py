from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.governance.check_append_only_evidence import check, check_cached


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, text=True, capture_output=True).stdout.strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", ".")
    git(root, "commit", "-m", message)
    return git(root, "rev-parse", "HEAD")


def setup_repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path
    git(root, "init")
    git(root, "config", "user.name", "test")
    git(root, "config", "user.email", "test@example.com")
    path = root / "research/codex/transitions/abc.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"v":1}\n')
    base = commit(root, "base")
    return root, base


def test_new_append_only_file_is_allowed(tmp_path):
    root, base = setup_repo(tmp_path)
    path = root / "research/codex/completions/new.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"v":1}\n')
    commit(root, "append")
    assert check(root, base, "HEAD") == []


def test_modifying_existing_receipt_is_rejected(tmp_path):
    root, base = setup_repo(tmp_path)
    (root / "research/codex/transitions/abc.json").write_text('{"v":2}\n')
    commit(root, "mutate")
    assert check(root, base, "HEAD")


def test_deleting_existing_receipt_is_rejected(tmp_path):
    root, base = setup_repo(tmp_path)
    (root / "research/codex/transitions/abc.json").unlink()
    commit(root, "delete")
    assert check(root, base, "HEAD")


def test_modifying_existing_convergence_receipt_is_rejected(tmp_path):
    root, base = setup_repo(tmp_path)
    path = root / "research/codex/convergence/example.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"v":1}\\n')
    base = commit(root, "add convergence")
    path.write_text('{"v":2}\\n')
    commit(root, "mutate convergence")
    assert check(root, base, "HEAD")


def test_unrelated_file_change_is_allowed(tmp_path):
    root, base = setup_repo(tmp_path)
    path = root / "README.md"
    path.write_text("ok\n")
    commit(root, "docs")
    assert check(root, base, "HEAD") == []


def test_cached_new_receipt_is_allowed_but_cached_mutation_is_rejected(tmp_path):
    root, _ = setup_repo(tmp_path)
    new_path = root / "research/codex/completions/new.json"
    new_path.parent.mkdir(parents=True)
    new_path.write_text('{"v":1}\n')
    git(root, "add", str(new_path.relative_to(root)))
    assert check_cached(root) == []
    git(root, "reset")
    (root / "research/codex/transitions/abc.json").write_text('{"v":2}\n')
    git(root, "add", "research/codex/transitions/abc.json")
    assert check_cached(root)


def test_direct_main_writers_enforce_cached_append_only_guard():
    root = Path(__file__).parents[2]
    for rel in (
        ".github/workflows/remediation-maturation.yml",
        ".github/workflows/automation-production-health.yml",
    ):
        text = (root / rel).read_text(encoding="utf-8")
        assert "check_append_only_evidence.py --repo-root . --cached" in text
