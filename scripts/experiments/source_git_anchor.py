"""Source-history anchor for Task 2 exact raw settlement, SHADOW/RESEARCH ONLY.

This verifies *first Git publication* on the GitHub origin/main first-parent
history against immutable bytes, not exchange-origin authenticity. A writable
PR branch, a mutable outcome/binding hash and a changed local main ref do not
establish original evidence. Incomplete/shallow history => fail closed.

Integration into outcome eligibility requires separate tests/review. This
module alone does NOT confer scientific_score_eligible status.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
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
        p = subprocess.run(
            ("git", "-C", str(root), *args), check=True,
            capture_output=True, timeout=20,
        )
        return p.stdout
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise SourceGitAnchorUnavailable("CANONICAL_MAIN_HISTORY_UNVERIFIED") from exc


def first_accepted_main_raw(
    repo_root: Path,
    relative_raw_path: Path,
    expected_sha256: str,
    *,
    fixture_origin: str | None = None,
) -> bool:
    """Verify first accepted raw bytes with remote-main authority, not local refs.

    fixture_origin is ONLY for isolated tests with a freshly created bare origin.
    Never accept it from forecast/outcome/evidence files or production callers.
    This path does not update refs, mutate raw bytes, or call market providers.
    """
    try:
        root = repo_root.resolve(strict=True)
        if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            return False
        rel = Path(relative_raw_path)
        if rel.is_absolute() or not rel.parts or any(p in ("..", "") for p in rel.parts):
            return False
        path = root / rel
        if path.is_symlink() or not path.is_file() or path.resolve(strict=True) != path:
            return False
        remote_url = _git(root, "remote", "get-url", "origin").decode().strip()
        if remote_url not in ({fixture_origin} if fixture_origin else ALLOWED_ORIGINS):
            return False
        remote = _git(root, "ls-remote", "--exit-code", "origin", "refs/heads/main").decode()
        match = re.fullmatch(r"([0-9a-f]{40})\s+refs/heads/main\s*", remote)
        if match is None:
            return False
        head = match.group(1)
        # Deepening on-demand without source authority would be too expensive
        # and may silently turn incomplete evidence into a speculative pass.
        if _git(root, "rev-parse", "--is-shallow-repository").strip() != b"false":
            return False
        try:
            _git(root, "cat-file", "-e", head + "^{commit}")
        except SourceGitAnchorUnavailable:
            _git(root, "fetch", "--quiet", "--no-tags", "--no-write-fetch-head", "origin", head)
            _git(root, "cat-file", "-e", head + "^{commit}")
        key = rel.as_posix()
        revisions = _git(root, "rev-list", "--reverse", "--first-parent", head, "--", key).splitlines()
        if not revisions:
            return False
        first = revisions[0].decode("ascii")
        _git(root, "merge-base", "--is-ancestor", first, head)
        original = _git(root, "show", f"{first}:{key}")
        return (path.read_bytes() == original and
                hashlib.sha256(original).hexdigest() == expected_sha256)
    except (OSError, UnicodeError, ValueError, SourceGitAnchorUnavailable):
        return False
