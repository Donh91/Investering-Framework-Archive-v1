"""Bounded first accepted Git custody; no supplier/PIT or skill admission.

Pins remote main once per registry. Missing/shallow history fails closed.
Never fetches, deepens, rewrites refs or trusts PR/local-main as authority.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import URLError

ALLOWED_ORIGINS = frozenset((
    "https://github.com/Donh91/Investering-Framework-Archive-v1.git",
    "https://github.com/Donh91/Investering-Framework-Archive-v1",
    "git@github.com:Donh91/Investering-Framework-Archive-v1.git",
))



ARCHIVE_REPOSITORY = "Donh91/Investering-Framework-Archive-v1"
ARCHIVE_REPOSITORY_ID = 1289482022


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _native_push_runs(first_commit):
    """Direct GitHub HTTPS GET only; no redirect, paid service or new credential."""
    if not isinstance(first_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", first_commit):
        return None
    url = (f"https://api.github.com/repos/{ARCHIVE_REPOSITORY}/actions/runs"
           f"?event=push&branch=main&head_sha={first_commit}&per_page=100")
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "Archive-source-anchor-v1"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with build_opener(_NoRedirect()).open(Request(url, headers=headers), timeout=5) as response:
            if response.status != 200 or response.geturl() != url:
                return None
            data = response.read(2_000_001)
        if len(data) > 2_000_000:
            return None
        return json.loads(data)
    except (OSError, URLError, ValueError, TypeError):
        return None


def _push_upper_bound(intro, response):
    """Derive a conservative inclusion upper bound, NEVER a lower bound.

    Called only on a freshly retrieved native API response in production.
    The pure function is separately testable; supplied JSON is not an
    authenticated receipt and must not be accepted from stored artifacts.
    """
    if not isinstance(intro, dict) or not isinstance(response, dict):
        return None
    if (intro.get("contract") != "EXPERIMENT_FIRST_MAIN_INTRODUCTION_v1"
            or intro.get("repository") != ARCHIVE_REPOSITORY
            or intro.get("ref") != "refs/heads/main"):
        return None
    sha_keys = ("first_commit", "first_parent", "main_head", "git_blob_sha")
    if any(not isinstance(intro.get(k), str) or not re.fullmatch(r"[0-9a-f]{40}", intro[k]) for k in sha_keys):
        return None
    if (not isinstance(intro.get("content_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", intro["content_sha256"])
            or not isinstance(intro.get("path"), str)
            or not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", intro["path"])):
        return None
    rows = response.get("workflow_runs")
    total = response.get("total_count")
    if (not isinstance(rows, list) or type(total) is not int
            or total != len(rows) or not 1 <= total <= 100):
        return None
    clocks = []
    ids = set()
    for row in rows:
        if not isinstance(row, dict):
            return None
        repositories = (row.get("repository"), row.get("head_repository"))
        if (row.get("event") != "push" or row.get("head_branch") != "main"
                or row.get("head_sha") != intro["first_commit"]
                or any(not isinstance(r, dict) or r.get("id") != ARCHIVE_REPOSITORY_ID
                       or r.get("full_name") != ARCHIVE_REPOSITORY for r in repositories)
                or type(row.get("id")) is not int or row["id"] <= 0 or row["id"] in ids):
            return None
        ids.add(row["id"])
        clock = row.get("created_at")
        if not isinstance(clock, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", clock):
            return None
        try:
            at = datetime.fromisoformat(clock[:-1]+"+00:00")
            if at > datetime.now(timezone.utc):
                return None
            # GitHub returns second precision. Do not round a cutoff down.
            clocks.append((at + timedelta(seconds=1), row["id"]))
        except (ValueError, OverflowError):
            return None
    at, run_id = min(clocks)
    return {**intro, "server_acceptance_clock_verified": False,
            "server_upper_witness_verified": True,
            "acceptance_state": "UPPER_BOUND_ONLY_UNADMITTED",
            "present_by_utc": at.isoformat().replace("+00:00", "Z"),
            "absent_through_utc": None, "witness_run_id": run_id,
            "witness_kind": "GITHUB_NATIVE_PUSH_RUN_CREATION",
            "scientifically_admitted": False}


class SourceGitAnchorUnavailable(RuntimeError):
    pass


class SourceGitAnchorBudgetExceeded(SourceGitAnchorUnavailable):
    """The whole registry build must stop; partial source coverage is unsafe."""


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

    def _check_budget(self) -> None:
        # Subprocess timeout is per Git invocation; aggregate calls must also
        # have a checked build-level deadline even on an early False return.
        if time.monotonic() > self.deadline or self.lookups > 128:
            raise SourceGitAnchorBudgetExceeded("SOURCE_ANCHOR_LOOKUP_BUDGET_EXCEEDED")

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
        # No authenticated server-side acceptance clock exists in this owner.
        # A time-bounded scientific claim is therefore deterministically
        # UNADMITTED regardless of Git history, which has forgeable clocks.
        # Refuse BEFORE launching potentially hundreds of pointless Git calls.
        # A later trusted timing receipt needs a separately governed extension.
        if accepted_before is not None or accepted_after is not None:
            return False
        try:
            if self.lookups >= 128:
                raise SourceGitAnchorBudgetExceeded("SOURCE_ANCHOR_LOOKUP_BUDGET_EXCEEDED")
            self._check_budget()
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
            self._check_budget()
            key = rel.as_posix()
            if key not in self.originals:
                self.lookups += 1
                revisions = _git(self.root, "rev-list", "--reverse", "--first-parent",
                                 head, "--", key).splitlines()
                self._check_budget()
                if not revisions:
                    return False
                first = revisions[0].decode("ascii")
                _git(self.root, "merge-base", "--is-ancestor", first, head)
                self._check_budget()
                entry = _git(self.root, "ls-tree", first, "--", key).decode()
                self._check_budget()
                if not entry.startswith(("100644 blob ", "100755 blob ")):
                    return False
                size = int(_git(self.root, "cat-file", "-s", f"{first}:{key}"))
                self._check_budget()
                if size > 10_000_000:
                    return False
                original = _git(self.root, "show", f"{first}:{key}")
                self._check_budget()
                self.originals[key] = (original, 0)
            original, _untrusted_commit_clock = self.originals[key]
            self._check_budget()
            # Untimed object custody is allowed; it is not temporal admission.
            current = path.read_bytes()
            self._check_budget()
            return (current == original
                    and hashlib.sha256(original).hexdigest() == expected_sha256)
        except SourceGitAnchorBudgetExceeded:
            raise
        except (OSError, UnicodeError, ValueError, SourceGitAnchorUnavailable):
            return False


    def first_introduction(self, relative_path: Path, expected_sha256: str) -> dict | None:
        """Immutable single-parent path introduction, NOT a server clock."""
        try:
            rel = Path(relative_path)
            key = rel.as_posix()
            if (rel.is_absolute() or not rel.parts or ".." in rel.parts
                    or not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", key)):
                return None
            if not self.matches(rel, expected_sha256):
                return None
            self._check_budget()
            if self.lookups >= 128:
                raise SourceGitAnchorBudgetExceeded("SOURCE_ANCHOR_LOOKUP_BUDGET_EXCEEDED")
            self.lookups += 1
            head = self._main()

            def checked(*args: str) -> bytes:
                self._check_budget()
                result = _git(self.root, *args)
                self._check_budget()
                return result

            revisions = checked("--literal-pathspecs", "rev-list", "--full-history",
                                "--first-parent", head, "--", key).splitlines()
            # Refuse replacements and delete/re-add, even with identical bytes.
            if len(revisions) != 1:
                return None
            first = revisions[0].decode("ascii")
            parents = checked("rev-list", "--parents", "-n", "1", first).decode("ascii").split()
            if (len(parents) != 2 or parents[0] != first
                    or not all(re.fullmatch(r"[0-9a-f]{40}", x) for x in parents)):
                return None
            parent = parents[1]
            checked("merge-base", "--is-ancestor", first, head)
            if checked("--literal-pathspecs", "ls-tree", "-z", parent, "--", key):
                return None
            entry = checked("--literal-pathspecs", "ls-tree", "-z", first, "--", key)
            match = re.fullmatch(rb"100(?:644|755) blob ([0-9a-f]{40})\t"
                                 + re.escape(key.encode("ascii")) + rb"\x00", entry)
            if match is None:
                return None
            if checked("--literal-pathspecs", "ls-tree", "-z", head, "--", key) != entry:
                return None
            original = self.originals[key][0]
            blob = hashlib.sha1(b"blob " + str(len(original)).encode("ascii") + b"\0" + original).hexdigest()
            if blob != match.group(1).decode("ascii"):
                return None
            self._check_budget()
            return {
                "contract": "EXPERIMENT_FIRST_MAIN_INTRODUCTION_v1",
                "repository": "Donh91/Investering-Framework-Archive-v1" if self.fixture_origin is None else None,
                "ref": "refs/heads/main", "main_head": head, "path": key,
                "first_commit": first, "first_parent": parent,
                "git_blob_sha": blob, "content_sha256": expected_sha256,
                "server_acceptance_clock_verified": False,
                "absent_through_utc": None, "present_by_utc": None,
                "scientifically_admitted": False,
            }
        except SourceGitAnchorBudgetExceeded:
            raise
        except (OSError, UnicodeError, ValueError, SourceGitAnchorUnavailable):
            return None

    def native_upper_witness(self, relative_path: Path, expected_sha256: str) -> dict | None:
        """Opt-in diagnostic. No timed matches caller is enabled by this method."""
        if self.fixture_origin is not None:
            return None
        intro = self.first_introduction(relative_path, expected_sha256)
        if intro is None:
            return None
        self._check_budget()
        response = _native_push_runs(intro["first_commit"])
        self._check_budget()
        return _push_upper_bound(intro, response)


def first_accepted_main_raw(repo_root: Path, relative_raw_path: Path,
                            expected_sha256: str, *, fixture_origin: str | None = None) -> bool:
    """Compatibility helper. fixture_origin is an isolated-test seam only."""
    return AcceptedMainSource(repo_root, fixture_origin=fixture_origin).matches(
        relative_raw_path, expected_sha256)
