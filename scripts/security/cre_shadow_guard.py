"""Owner-maintained PR-only CRE scope guard. This is not a merge authorization.

The script is trusted ONLY after protected source, mandatory checks and real
branch rules are configured. Until then it is defense in depth and all CRE
PRs remain owner-reviewed. No network, credentials, or private data access.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

ROOT = "06_RESEARCH_LAB/compass_research_engine_v1/"
TRUSTED_GUARD = "scripts/security/cre_shadow_guard.py"
BOOTSTRAP_FILES = frozenset({
    TRUSTED_GUARD,
    "tests/security/test_cre_shadow_guard.py",
    ".github/workflows/cre-shadow-tests.yml",
    ".github/CODEOWNERS",
})
ALLOWED_SUFFIXES = frozenset({".py", ".json", ".md", ".txt"})
FORBIDDEN_PARTS = frozenset({".github", ".git", "__pycache__", "secrets", "private", "credentials", ".env"})


class GuardError(ValueError):
    pass


def inspect_scope(paths: list[str], *, is_bootstrap: bool) -> str:
    """Fail on mixed-scope CRE changes; special-case initial owner-reviewed bootstrap."""
    changed = set(paths)
    cre = {p for p in changed if p.startswith(ROOT)}
    trusted = changed & BOOTSTRAP_FILES
    if not cre and not trusted:
        return "NOT_CRE_PR"
    for path in cre:
        subpath = path[len(ROOT):]
        if not subpath or any(x in FORBIDDEN_PARTS or x.startswith(".") for x in pathlib.PurePosixPath(subpath).parts):
            raise GuardError("HIDDEN_OR_RESTRICTED_PATH")
        if pathlib.PurePosixPath(path).suffix not in ALLOWED_SUFFIXES:
            raise GuardError("UNSUPPORTED_FILE_TYPE")
        if ".." in pathlib.PurePosixPath(subpath).parts:
            raise GuardError("TRAVERSAL")
    extra = changed - cre
    if is_bootstrap:
        if extra <= BOOTSTRAP_FILES and trusted:
            return "BOOTSTRAP_OWNER_REVIEW_REQUIRED"
        raise GuardError("BOOTSTRAP_SCOPE_VIOLATION")
    if extra:
        raise GuardError("CRE_MIXED_SCOPE_OR_TRUSTED_POLICY_CHANGE")
    return "CRE_SCOPE_ONLY_NOT_MERGE_AUTHORITY"


def git(*args: str, check: bool = True) -> bytes:
    proc = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and proc.returncode:
        raise GuardError("GIT_QUERY_FAILED")
    return proc.stdout if proc.returncode == 0 else b""


def bootstrap_expected(base: str) -> bool:
    # git cat-file -e reports success via EXIT STATUS, never stdout.
    result = subprocess.run(["git", "cat-file", "-e", f"{base}:{TRUSTED_GUARD}"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return result.returncode != 0


def changed_paths(base: str, head: str) -> list[str]:
    merge_base = git("merge-base", base, head).decode("ascii", "strict").strip()
    raw = git("diff", "--name-only", "--no-renames", "-z", "--diff-filter=ACDMRTUXB", merge_base, head)
    return [s.decode("utf-8", "strict") for s in raw.split(b"\0") if s]


def inspect_tree_files(head: str, paths: list[str]) -> None:
    """Refuse symlink/submodule/executable/binary or oversized research blobs."""
    for path in paths:
        if not path.startswith(ROOT):
            continue
        raw = git("ls-tree", head, "--", path).decode("utf-8", "strict")
        if not raw:
            continue  # deletion, still subject to file-scope check
        match = re.fullmatch(r"(\d{6}) blob ([0-9a-f]{40})\t.+\n", raw)
        if not match or match.group(1) != "100644":
            raise GuardError("NONREGULAR_RESEARCH_FILE")
        raw_content = git("show", f"{head}:{path}")
        if len(raw_content) > 250_000 or b"\0" in raw_content:
            raise GuardError("LARGE_OR_BINARY_RESEARCH_FILE")
        try:
            raw_content.decode("utf-8", "strict")
        except UnicodeDecodeError as e:
            raise GuardError("NONUTF8_RESEARCH_FILE") from e


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--head", required=True)
    args = p.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", args.base) or not re.fullmatch(r"[a-f0-9]{40}", args.head):
        raise GuardError("FULL_SHA40_REQUIRED")
    paths = changed_paths(args.base, args.head)
    state = inspect_scope(paths, is_bootstrap=bootstrap_expected(args.base))
    inspect_tree_files(args.head, paths)
    print(state)
    print("AUTONOMOUS_MERGE_AUTHORITY=FALSE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GuardError as exc:
        print(f"CRE_SCOPE_GUARD_FAILED:{exc}")
        raise SystemExit(2)
