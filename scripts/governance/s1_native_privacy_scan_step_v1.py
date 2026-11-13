"""S1_NATIVE_PRIVACY_SCAN_STEP_V1: native, run-bound producer for S1_DIFF_SCAN_V1.

One step of the existing ``gate`` job in ``.github/workflows/data-architecture-gate.yml``.
It builds the scanner record from the pull_request event payload and the local git
objects of the checked-out PR merge commit, runs the UNCHANGED ``scan_pr`` and exits
non-zero unless the verdict is ``NO_RESTRICTED_CONTENT`` (mode ``enforce``).

What it binds:
* the scanned commit: second parent of the checked-out merge commit must equal
  ``pull_request.head.sha`` from the event payload;
* the scanned text: every scanned file body is hashed as a git blob
  (``sha1("blob <len>\\0" + bytes)``) and must equal the blob id in the head tree;
* the scan code: blob ids of scanner, this step and the workflow file are reported
  for the merge commit and for the base parent.

It never prints file content, patch text, the PR title or body, or raw paths.
It uses no secret and no token of its own; the optional ``git fetch`` reuses the
read-only checkout credential. This step is a producer of evidence, not a release
authority: S1_DIFF_SCAN_V1 stays an advisory pattern scanner.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s1_diff_scan_v1 as scanner  # noqa: E402  (sibling module, logic unchanged)

CONTRACT = "S1_NATIVE_PRIVACY_SCAN_STEP_V1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SCAN_CODE_PATHS = (
    "scripts/governance/s1_diff_scan_v1.py",
    "scripts/governance/s1_native_privacy_scan_step_v1.py",
    ".github/workflows/data-architecture-gate.yml",
)
STATUS = {"A": "added", "M": "modified", "D": "removed", "R": "renamed",
          "C": "copied", "T": "changed"}


class Git:
    def __init__(self, repo: str) -> None:
        self.repo = repo

    def run(self, *args: str, check: bool = True) -> bytes | None:
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C")
        p = subprocess.run(["git", "-C", self.repo, "-c", "core.quotepath=off", *args],
                           capture_output=True, env=env)
        if p.returncode != 0:
            if check:
                raise RuntimeError("git " + args[0] + " failed")
            return None
        return p.stdout

    def rev(self, spec: str) -> str | None:
        out = self.run("rev-parse", "--verify", "--quiet", spec, check=False)
        value = out.decode("ascii", "replace").strip() if out else ""
        return value if SHA40.fullmatch(value) else None


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _path_ref(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8", errors="backslashreplace")).hexdigest()[:16]


def _text_sha(value: Any) -> str | None:
    if type(value) is not str:
        return None
    return hashlib.sha256(value.encode("utf-8", errors="backslashreplace")).hexdigest()


def read_head_blob(git: Git, head: str, path: str) -> bytes | None:
    """Bytes of ``path`` in the tree of ``head`` (no filters, no working-tree read)."""
    return git.run("cat-file", "blob", f"{head}:{path}", check=False)


def ensure_merge_parents(git: Git) -> tuple[str | None, str | None, str | None]:
    """Return (merge, base_parent, head_parent); deepen a depth-1 checkout once."""
    merge = git.rev("HEAD^{commit}")
    if merge is None:
        return None, None, None
    if git.rev("HEAD^1") is None or git.rev("HEAD^2") is None:
        # actions/checkout default is depth 1: the merge commit without its parents.
        git.run("fetch", "--no-tags", "--depth=2", "origin", merge, check=False)
    if git.rev("HEAD^3") is not None:
        return merge, None, None
    return merge, git.rev("HEAD^1"), git.rev("HEAD^2")


def original_pr_base(git: Git, base_parent: str, head: str, merge: str) -> str | None:
    """Three-dot PR ancestor. Never substitute merge-output delta for original diff."""
    def candidate() -> str | None:
        raw = git.run("merge-base", base_parent, head, check=False)
        value = raw.decode("ascii", "replace").strip() if raw else ""
        return value if SHA40.fullmatch(value) else None

    ancestor = candidate()
    if ancestor is None:
        shallow = git.run("rev-parse", "--is-shallow-repository", check=False)
        if shallow is not None and shallow.strip() == b"true":
            # Bounded deepen for checkout@v4 default shallow PR-merge checkout.
            # If ancestry is still unavailable, classify UNKNOWN rather than green.
            git.run("fetch", "--no-tags", "--deepen=64", "origin", merge, check=False)
            ancestor = candidate()
    return ancestor


def changed_entries(git: Git, base: str, merge: str) -> list[tuple[str, str, str | None]]:
    """(status_letter, path, previous_path) from original three-dot PR diff."""
    raw = git.run("diff", "--name-status", "-M", "-z", base, merge) or b""
    parts = raw.split(b"\x00")
    out: list[tuple[str, str, str | None]] = []
    i = 0
    while i < len(parts) and parts[i]:
        letter = parts[i].decode("ascii", "replace")[:1]
        if letter in ("R", "C"):
            old = parts[i + 1].decode("utf-8", "surrogateescape")
            new = parts[i + 2].decode("utf-8", "surrogateescape")
            out.append((letter, new, old))
            i += 3
        else:
            out.append((letter, parts[i + 1].decode("utf-8", "surrogateescape"), None))
            i += 2
    return out


def build_record(git: Git, event: dict[str, Any], repo_name: Any, merge: str, base: str,
                 head: str, reader: Callable[[Git, str, str], bytes | None] = read_head_blob,
                 ) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    """Scanner record, per-file binding rows and wrapper-level fail-closed reasons."""
    pr = event.get("pull_request") if type(event.get("pull_request")) is dict else {}
    reasons: list[str] = []
    files: list[dict[str, Any]] = []
    binding: list[dict[str, Any]] = []
    entries = changed_entries(git, base, merge)
    for letter, path, previous in entries:
        pathspec = ["--", path] if previous is None else ["--", previous, path]
        # Git filename bytes may begin with :(...), which is pathspec magic.
        # Disable pathspec interpretation so deletion patches cannot disappear.
        numstat = git.run("--literal-pathspecs", "diff", "--numstat", "-M", base, merge, *pathspec) or b""
        binary = numstat.startswith(b"-\t-\t")
        patch_bytes = git.run("--literal-pathspecs", "diff", "-M", base, merge, *pathspec) or b""
        try:
            patch, patch_ok = patch_bytes.decode("utf-8"), True
        except UnicodeDecodeError:
            patch, patch_ok = "", False
        row: dict[str, Any] = {
            "path": path, "status": STATUS.get(letter, "unknown"), "head_sha": head,
            "binary": binary, "is_symlink": False, "patch": patch,
            "patch_complete": patch_ok and not binary,
        }
        if previous is not None:
            row["previous_filename"] = previous
        bind: dict[str, Any] = {"path_sha256_16": _path_ref(path), "status": row["status"],
                                "head_blob_sha": None}
        if letter == "D":
            row["content"] = None
        else:
            tree = git.run("--literal-pathspecs", "ls-tree", "-z", head, "--", path, check=False) or b""
            meta = tree.split(b"\t", 1)[0].split()
            mode = meta[0].decode() if len(meta) == 3 else ""
            native_blob = meta[2].decode() if len(meta) == 3 else None
            row["is_symlink"] = mode == "120000"
            data = reader(git, head, path) if mode in ("100644", "100755") else None
            content: str | None = None
            if data is None or native_blob is None:
                reasons.append("HEAD_BLOB_UNAVAILABLE")
            elif git_blob_sha(data) != native_blob:
                reasons.append("SCANNED_TEXT_NOT_BOUND_TO_HEAD_BLOB")
            else:
                bind["head_blob_sha"] = native_blob
                try:
                    content = data.decode("utf-8")
                except UnicodeDecodeError:
                    content = None  # scanner reports CURRENT_BLOB_TEXT_UNVERIFIED
            row["content"] = content
            row["content_head_sha"] = head if content is not None else None
        files.append(row)
        binding.append(bind)
    native_count = pr.get("changed_files")
    if type(native_count) is not int or native_count != len(files):
        reasons.append("FILE_CENSUS_MISMATCH_WITH_EVENT")
    record = {
        "repo": repo_name, "head": head, "pr_head_sha": head,
        "changed_files_count_head_sha": head, "changed_files_count": len(files),
        "pages_complete": True, "title": pr.get("title"),
        "body": pr.get("body") if pr.get("body") is not None else "",
        "files": files,
    }
    return record, binding, sorted(set(reasons))


def scan_code_blobs(git: Git, merge: str, base: str | None) -> dict[str, Any]:
    rows = {p: {"merge_blob_sha": git.rev(f"{merge}:{p}"),
                "base_blob_sha": git.rev(f"{base}:{p}") if base else None}
            for p in SCAN_CODE_PATHS}
    same = all(v["merge_blob_sha"] and v["merge_blob_sha"] == v["base_blob_sha"]
               for v in rows.values())
    return {"files": rows, "identical_to_base_parent": same}


def run_step(repo: str, env: dict[str, str],
             reader: Callable[[Git, str, str], bytes | None] = read_head_blob) -> dict[str, Any]:
    out: dict[str, Any] = {
        "contract": CONTRACT, "scanner_contract": scanner.CONTRACT,
        "scanner_rules_version": scanner.RULES_VERSION,
        "authority": "EVIDENCE_PRODUCER_ONLY_NOT_RELEASE_AUTHORITY",
        "run": {k: env.get(k) for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT",
                                        "GITHUB_WORKFLOW_REF", "GITHUB_JOB", "GITHUB_SHA")},
        "result": "UNKNOWN", "wrapper_reasons": [],
    }
    event: Any = None
    try:
        event = json.loads(Path(env.get("GITHUB_EVENT_PATH", "")).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        event = None
    if env.get("GITHUB_EVENT_NAME") != "pull_request":
        out["result"] = "SKIPPED_NOT_PR"
        return out
    if type(event) is not dict or type(event.get("pull_request")) is not dict:
        out["wrapper_reasons"] = ["PULL_REQUEST_EVENT_PAYLOAD_UNAVAILABLE"]
        return out
    pr = event["pull_request"]
    head_event = (pr.get("head") or {}).get("sha") if type(pr.get("head")) is dict else None
    base_event = (pr.get("base") or {}).get("sha") if type(pr.get("base")) is dict else None
    out.update({"pr_number": pr.get("number") if type(pr.get("number")) is int else None,
                "head_sha": head_event if type(head_event) is str and SHA40.fullmatch(head_event) else None,
                "event_base_sha": base_event if type(base_event) is str and SHA40.fullmatch(base_event) else None,
                "title_sha256": _text_sha(pr.get("title")),
                "body_sha256": _text_sha(pr.get("body") if pr.get("body") is not None else "")})
    if out["head_sha"] is None:
        out["wrapper_reasons"] = ["EVENT_HEAD_SHA_INVALID"]
        return out
    git = Git(repo)
    try:
        merge, base, head = ensure_merge_parents(git)
        out.update({"merge_sha": merge, "merge_base_parent_sha": base})
        if merge is None or base is None or head is None:
            out["wrapper_reasons"] = ["MERGE_PARENTS_UNAVAILABLE"]
            return out
        if head != out["head_sha"]:
            out["wrapper_reasons"] = ["CHECKOUT_IS_NOT_MERGE_OF_EVENT_HEAD"]
            return out
        out["scan_code"] = scan_code_blobs(git, merge, base)
        pr_base = original_pr_base(git, base, head, merge)
        out["original_pr_merge_base_sha"] = pr_base
        if pr_base is None:
            out["wrapper_reasons"] = ["ORIGINAL_PR_MERGE_BASE_UNAVAILABLE"]
            return out
        repo_name = env.get("GITHUB_REPOSITORY")
        record, binding, reasons = build_record(git, event, repo_name, head, pr_base, head, reader)
    except RuntimeError:
        out["wrapper_reasons"] = ["GIT_READ_FAILED"]
        return out
    if not out["scan_code"]["identical_to_base_parent"]:
        reasons.append("SCAN_CODE_CHANGED_BY_PR_OR_ABSENT_ON_BASE")
    scan = scanner.scan_pr(record)
    out["scanner_result"] = {k: scan.get(k) for k in (
        "result", "findings_count", "findings", "input_sha256", "head", "rules_version")}
    out["files"] = binding
    out["files_count"] = len(binding)
    out["files_binding_sha256"] = hashlib.sha256(json.dumps(
        binding, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    out["wrapper_reasons"] = sorted(set(reasons))
    if scan.get("result") == "RESTRICTED_CONTENT":
        out["result"] = "RESTRICTED_CONTENT"
    elif scan.get("result") == "NO_RESTRICTED_CONTENT" and not reasons:
        out["result"] = "NO_RESTRICTED_CONTENT"
    else:
        out["result"] = "UNKNOWN"
    return out


def exit_code(result: str, mode: str) -> int:
    if result in ("NO_RESTRICTED_CONTENT", "SKIPPED_NOT_PR"):
        return 0
    return 0 if mode == "shadow" else 1


def main(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    env = dict(os.environ) if env is None else env
    args = sys.argv[1:] if argv is None else argv
    repo = args[args.index("--repo") + 1] if "--repo" in args else "."
    mode = env.get("S1_PRIVACY_SCAN_MODE", "enforce")
    if mode not in ("enforce", "shadow"):
        mode = "enforce"
    out = run_step(repo, env)
    out["mode"] = mode
    code = exit_code(out["result"], mode)
    out["exit_code"] = code
    text = json.dumps(out, indent=2, sort_keys=True)
    line = f"{CONTRACT} result={out['result']} head={out.get('head_sha')} mode={mode} exit={code}"
    print(text)
    print(line)
    summary = env.get("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(f"### {CONTRACT}\n\n`{line}`\n\n```json\n{text}\n```\n")
        except OSError:
            pass
    return code


if __name__ == "__main__":
    raise SystemExit(main())
