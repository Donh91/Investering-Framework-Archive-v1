"""Bounded first accepted Git custody; no supplier/PIT or skill admission.

Pins remote main once per registry. Missing/shallow history fails closed.
Never fetches, deepens, rewrites refs or trusts PR/local-main as authority.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

ALLOWED_ORIGINS = frozenset((
    "https://github.com/Donh91/Investering-Framework-Archive-v1.git",
    "https://github.com/Donh91/Investering-Framework-Archive-v1",
    "git@github.com:Donh91/Investering-Framework-Archive-v1.git",
))


class SourceGitAnchorUnavailable(RuntimeError):
    pass


def _git(root: Path, *args: str) -> bytes:
    try:
        env = dict(os.environ, GIT_NO_REPLACE_OBJECTS="1",
                   GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
        return subprocess.run(
            ("git", "--no-replace-objects", "-C", str(root), *args),
            check=True, capture_output=True, timeout=5, env=env,
        ).stdout
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise SourceGitAnchorUnavailable("CANONICAL_MAIN_HISTORY_UNVERIFIED") from exc


class AcceptedMainSource:
    """Per-build immutable head and bounded path history lookup cache."""

    def __init__(self, repo_root: Path, *, fixture_origin: str | None = None):
        self.root = repo_root.resolve()
        self.fixture_origin = fixture_origin
        self.head: str | None = None
        self.initialized = False
        self.originals: dict[str, tuple[bytes, int]] = {}
        self.lookups = 0
        self.deadline = time.monotonic() + 15

    def _main(self) -> str:
        if not self.initialized:
            self.initialized = True
            if _git(self.root, "rev-parse", "--is-shallow-repository").strip() != b"false":
                raise SourceGitAnchorUnavailable("SHALLOW_HISTORY")
            if _git(self.root, "for-each-ref", "--format=%(refname)", "refs/replace").strip():
                raise SourceGitAnchorUnavailable("REPLACED_HISTORY")
            graft = _git(self.root, "rev-parse", "--git-path", "info/grafts").decode().strip()
            graft_path = Path(graft) if Path(graft).is_absolute() else self.root / graft
            if graft_path.exists():
                raise SourceGitAnchorUnavailable("GRAFTED_HISTORY")
            url = _git(self.root, "remote", "get-url", "origin").decode().strip()
            if url not in ({self.fixture_origin} if self.fixture_origin else ALLOWED_ORIGINS):
                raise SourceGitAnchorUnavailable("WRONG_ORIGIN")
            remote = _git(self.root, "ls-remote", "--exit-code", "origin", "refs/heads/main").decode()
            match = re.fullmatch(r"([0-9a-f]{40})\s+refs/heads/main\s*", remote)
            if match is None:
                raise SourceGitAnchorUnavailable("MAIN_UNAVAILABLE")
            head = match.group(1)
            _git(self.root, "cat-file", "-e", head + "^{commit}")
            self.head = head
        if self.head is None:
            raise SourceGitAnchorUnavailable("MAIN_UNAVAILABLE")
        return self.head

    def matches(self, relative_path: Path, expected_sha256: str, *,
                accepted_before: datetime | None = None,
                accepted_after: datetime | None = None) -> bool:
        try:
            if time.monotonic() > self.deadline or self.lookups >= 128:
                return False
            if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
                return False
            rel = Path(relative_path)
            if rel.is_absolute() or not rel.parts or ".." in rel.parts:
                return False
            path = self.root / rel
            if (path.is_symlink() or not path.is_file() or path.resolve() != path
                    or path.stat().st_size > 10_000_000):
                return False
            head = self._main()
            key = rel.as_posix()
            if key not in self.originals:
                self.lookups += 1
                revisions = _git(self.root, "rev-list", "--reverse", "--first-parent",
                                 head, "--", key).splitlines()
                if not revisions:
                    return False
                first = revisions[0].decode("ascii")
                _git(self.root, "merge-base", "--is-ancestor", first, head)
                entry = _git(self.root, "ls-tree", first, "--", key).decode()
                if not entry.startswith(("100644 blob ", "100755 blob ")):
                    return False
                if int(_git(self.root, "cat-file", "-s", f"{first}:{key}")) > 10_000_000:
                    return False
                original = _git(self.root, "show", f"{first}:{key}")
                stamp = int(_git(self.root, "show", "-s", "--format=%ct", first))
                self.originals[key] = (original, stamp)
            original, stamp = self.originals[key]
            if accepted_before is not None:
                if accepted_before.tzinfo is None or stamp >= accepted_before.timestamp():
                    return False
            if accepted_after is not None:
                if accepted_after.tzinfo is None or stamp < accepted_after.timestamp():
                    return False
            return (path.read_bytes() == original
                    and hashlib.sha256(original).hexdigest() == expected_sha256)
        except (OSError, UnicodeError, ValueError, SourceGitAnchorUnavailable):
            return False


def first_accepted_main_raw(repo_root: Path, relative_raw_path: Path,
                            expected_sha256: str, *, fixture_origin: str | None = None) -> bool:
    """Compatibility helper. fixture_origin is an isolated-test seam only."""
    return AcceptedMainSource(repo_root, fixture_origin=fixture_origin).matches(
        relative_raw_path, expected_sha256)
