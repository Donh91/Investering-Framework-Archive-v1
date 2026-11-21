"""S1_SITE_PUBLIC_READBACK_V1: readback of the GENERATED public Cycle Navigator bundle at one exact PR head.

Why it exists. ``s1_diff_scan_v1`` scans the added lines and head blobs of a PR. The public site is not those bytes:
``.github/workflows/cycle-navigator-pages.yml`` runs a build (node and python build scripts, ``npm ci`` and a vite
build) and uploads the generated directory ``05_CYCLE_NAVIGATOR/site/dist``. A build can copy data from anywhere in
the repository into that directory, so the diff scanner never calls a changed path under ``05_CYCLE_NAVIGATOR/site/``
green on its own (``GENERATED_PUBLIC_OUTPUT_NEEDS_SEPARATE_READBACK``). This module is that separate readback.

Two halves, in two different jobs of ``.github/workflows/data-architecture-gate.yml``:

* ``build`` (job ``site-public-build``, UNTRUSTED). It runs the steps of the Pages workflow itself, read from the
  workflow file of the checked-out tree: every ``run`` step before the ``actions/upload-pages-artifact`` step, in
  order, each as ``bash -e`` like the Actions runner does. The steps are PR-controlled code, so this half runs in a
  job of its own that has no secret, a read-only token that is not persisted, and nothing else worth stealing. It
  stages the published file set and a build receipt, and the job uploads both as one artifact. Any failing step,
  time-out, change to a tracked file, output outside the publish root (``node_modules`` and ``__pycache__`` aside),
  symlink or special file is a failed build: nothing is staged and the exit code is non-zero.
* ``readback`` (job ``privacy-scan``, the isolated gate job). It executes NO PR-controlled code. It reads the
  downloaded artifact as bytes only: EVERY published file (not only the changed ones, not only diff lines) is hashed
  and scanned with the content rules of ``s1_diff_scan_v1`` (the rule table is imported, never copied). The privacy
  step calls ``readback()`` in-process and accepts changed site paths only for ``PUBLIC_OUTPUT_CLEAN`` at its own head.

Why the build is not run inside the privacy job: AGENTS.md section 0.2e treats the gate as isolated because its
evidence does not come from a job that runs PR-controlled code. A build process in the same job could write to the
job log or to the step summary and so forge the one result line. A job boundary (another virtual machine) is the
only isolation this module relies on; the artifact crosses it as data.

Published set. ``actions/upload-pages-artifact@v4`` archives the ``path`` directory, leaves out every entry whose
name starts with a dot, and follows symlinks. The readback is stricter than that: a hidden entry, a symlink, a
special file or a path that leaves the publish root is UNKNOWN, never silently skipped or followed.

File classes (fail closed):
* text: the suffix is on ``PUBLISHED_TEXT_SUFFIXES`` and the bytes are strict UTF-8 without NUL. Scanned by every rule;
* binary (anything else): cannot be scanned for private data, so it is accepted ONLY when its sha256 is pinned in
  ``PINNED_BINARY_SHA256`` below for that exact published path. A new or changed image is UNKNOWN until an
  owner-gated change of this file pins it (this file is scan code: a PR that edits it is never lane evidence);
* a text-suffixed file that does not decode, a file over ``MAX_FILE_BYTES``, more than ``MAX_FILES`` files, a total
  over ``MAX_TOTAL_BYTES`` or an empty bundle: UNKNOWN.

Limits, stated plainly. The build is time- and data-dependent, so the manifest digest identifies THIS build, not the
bytes Pages later deploys from main. A build script that behaves differently when it detects a pull request can show
clean bytes here and other bytes on main: this readback finds accidental leaks, the independent review finds hostile
build code. It prints no file content and no matched text. It is evidence, not a release authority.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s1_diff_scan_v1 as scanner  # noqa: E402  (sibling module: the one rule table)

CONTRACT = "S1_SITE_PUBLIC_READBACK_V1"
BUILD_CONTRACT = "S1_SITE_PUBLIC_BUILD_V1"
RECEIPT_CONTRACT = "S1_SITE_PUBLIC_BUILD_RECEIPT_V1"
PAGES_WORKFLOW = ".github/workflows/cycle-navigator-pages.yml"
UPLOAD_ACTION = "actions/upload-pages-artifact@v4"
# Steps of the Pages job that set up the runner and write nothing into the bundle.
SETUP_ACTIONS = ("actions/checkout@v6", "actions/setup-node@v4", "actions/configure-pages@v5")
STAGED_DIST = "dist"
RECEIPT_NAME = "S1_SITE_PUBLIC_BUILD_RECEIPT.json"
RESULTS = ("PUBLIC_OUTPUT_CLEAN", "RESTRICTED_CONTENT", "UNKNOWN")
MAX_FILES = scanner.MAX_FILES
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_RECEIPT_BYTES = 64 * 1024
STEP_TIMEOUT_SECONDS = 900
PUBLISHED_TEXT_SUFFIXES = scanner.TEXT_SUFFIXES + (".svg", ".webmanifest")
# Published binary files, by path inside the bundle: the brand icon (a tracked file, copied as it is) and the social
# card (generated from tracked base64 parts; the build itself checks the same digest). Both were viewed when pinned
# (2026-11-17): a logo and a title card, no data. Changing or adding one means changing this table in an owner-gated PR.
PINNED_BINARY_SHA256: dict[str, frozenset[str]] = {
    "apple-touch-icon.png": frozenset({"b05b7657644917974e5e75f85956c506b77e1c046776713054ee59034d9f448b"}),
    "social-card.png": frozenset({"131b7096f3a144333e977a236d0b1bae2a0c6aaff7df3a83e1715aeb70bf9f86"}),
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
_KEY = re.compile(r"([A-Za-z][A-Za-z0-9_-]*):(?: (.*))?")
_IF_FAILED = re.compile(r"steps\.([A-Za-z_][A-Za-z0-9_-]*)\.outcome == 'failure'")
_STEP_KEYS = frozenset({"name", "uses", "with", "id", "if", "continue-on-error", "run"})
_BUILD_LEFTOVER_PARTS = frozenset({"node_modules", "__pycache__"})


class RecipeError(Exception):
    """The Pages workflow is not in the shape this module reproduces. Callers fail closed."""


class BuildError(Exception):
    """The build did not produce a publishable bundle. Callers fail closed."""


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _path_ref(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8", errors="backslashreplace")).hexdigest()[:16]


# --------------------------------------------------------------------------------------------------------------
# The publication recipe: read from the Pages workflow, never kept as a second list
# --------------------------------------------------------------------------------------------------------------

def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _parse_step(block: list[str]) -> dict[str, Any]:
    step: dict[str, Any] = {}
    i = 0
    while i < len(block):
        line = block[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = _KEY.fullmatch(line)
        if not m or m.group(1) in step:
            raise RecipeError("STEP_LINE_NOT_UNDERSTOOD")
        key, value = m.group(1), (m.group(2) or "").strip()
        i += 1
        nested: list[str] = []
        while i < len(block) and (block[i].startswith("  ") or not block[i].strip()):
            nested.append(block[i][2:])
            i += 1
        while nested and not nested[-1].strip():
            nested.pop()
        if key == "run":
            if value == "|" and nested:
                step[key] = "\n".join(nested) + "\n"
            elif value and value[0] not in "|>" and not nested:
                step[key] = _unquote(value) + "\n"
            else:
                raise RecipeError("RUN_FORM_NOT_UNDERSTOOD")
        elif key == "with":
            fields: dict[str, str] = {}
            if value:
                if nested or not (value.startswith("{") and value.endswith("}")):
                    raise RecipeError("WITH_FORM_NOT_UNDERSTOOD")
                nested = [part.strip() for part in value[1:-1].split(",") if part.strip()]
            for item in nested:
                fm = _KEY.fullmatch(item)
                if not fm or fm.group(1) in fields:
                    raise RecipeError("WITH_FORM_NOT_UNDERSTOOD")
                fields[fm.group(1)] = _unquote(fm.group(2) or "")
            step[key] = fields
        elif nested:
            raise RecipeError("NESTED_VALUE_NOT_UNDERSTOOD")
        else:
            step[key] = _unquote(value)
    return step


def parse_pages_recipe(text: Any) -> dict[str, Any]:
    """The build steps and the published directory of the Pages workflow.

    Line-based on purpose (standard library only, runs under ``python -I``). It understands exactly the constructs
    the workflow uses before its upload step and raises RecipeError on anything else: an unknown step key, an
    ``env``, ``shell`` or ``working-directory``, a ``${{ }}`` expression in a command, an ``if`` other than
    ``steps.<id>.outcome == 'failure'``, an action that is not a known set-up action, a second job or upload step."""
    if type(text) is not str:
        raise RecipeError("WORKFLOW_TEXT_UNAVAILABLE")
    lines = text.splitlines()
    if any("\t" in line for line in lines):
        raise RecipeError("TAB_IN_WORKFLOW")
    job_ids: list[str] = []
    if "jobs:" in lines:
        job_ids = [l for l in lines[lines.index("jobs:") + 1:] if re.fullmatch(r"  [A-Za-z0-9_-]+:", l)]
    if lines.count("jobs:") != 1 or len(job_ids) != 1 or lines.count("    steps:") != 1:
        raise RecipeError("EXPECTED_ONE_JOB_WITH_ONE_STEP_LIST")
    blocks: list[list[str]] = []
    for line in lines[lines.index("    steps:") + 1:]:
        if line.startswith("      - "):
            blocks.append([line[8:]])
        elif blocks and (line.startswith("        ") or not line.strip()):
            blocks[-1].append(line[8:])
        else:
            raise RecipeError("LINE_OUTSIDE_STEP_LIST")
    steps: list[dict[str, Any]] = []
    ids: set[str] = set()
    publish_root: str | None = None
    for index, block in enumerate(blocks):
        step = _parse_step(block)
        uses = step.get("uses")
        if uses == UPLOAD_ACTION:
            if set(step) - {"name", "uses", "with"} or set(step.get("with") or {}) != {"path"}:
                raise RecipeError("UPLOAD_STEP_HAS_OPTIONS_THAT_CHANGE_THE_PUBLISHED_SET")
            publish_root = step["with"]["path"].rstrip("/")
            if any("upload-pages-artifact" in line for b in blocks[index + 1:] for line in b):
                raise RecipeError("SECOND_UPLOAD_STEP")
            break
        if set(step) - _STEP_KEYS:
            raise RecipeError("STEP_KEY_NOT_REPRODUCED")
        if uses is not None:
            if uses not in SETUP_ACTIONS or "run" in step or "if" in step:
                raise RecipeError("ACTION_BEFORE_UPLOAD_NOT_KNOWN")
            continue
        if "run" not in step or "with" in step:
            raise RecipeError("STEP_IS_NEITHER_RUN_NOR_ACTION")
        if "${{" in step["run"]:
            raise RecipeError("EXPRESSION_IN_RUN_NOT_REPRODUCED")
        row: dict[str, Any] = {"name": step.get("name", ""), "run": step["run"], "id": None,
                               "continue_on_error": False, "only_if_failed": None}
        if "id" in step:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", step["id"]) or step["id"] in ids:
                raise RecipeError("STEP_ID_NOT_UNDERSTOOD")
            row["id"] = step["id"]
            ids.add(step["id"])
        if "continue-on-error" in step:
            if step["continue-on-error"] != "true" or row["id"] is None:
                raise RecipeError("CONTINUE_ON_ERROR_FORM_NOT_REPRODUCED")
            row["continue_on_error"] = True
        if "if" in step:
            m = _IF_FAILED.fullmatch(step["if"])
            if not m or m.group(1) not in ids or m.group(1) == row["id"]:
                raise RecipeError("IF_FORM_NOT_REPRODUCED")
            row["only_if_failed"] = m.group(1)
        steps.append(row)
    if publish_root is None or not steps:
        raise RecipeError("NO_UPLOAD_STEP_OR_NO_BUILD_STEP")
    if not scanner._path(publish_root) or scanner._blocked_path(publish_root):
        raise RecipeError("PUBLISH_ROOT_NOT_A_SAFE_REPOSITORY_PATH")
    return {"publish_root": publish_root, "steps": steps}


def read_recipe(repo: str | os.PathLike[str]) -> tuple[dict[str, Any], str]:
    """(recipe, git blob id of the workflow file) for the tree checked out at ``repo``."""
    path = Path(repo) / PAGES_WORKFLOW
    try:
        if path.is_symlink() or not path.is_file():
            raise RecipeError("WORKFLOW_FILE_UNAVAILABLE")
        data = path.read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        raise RecipeError("WORKFLOW_FILE_UNAVAILABLE") from None
    return parse_pages_recipe(text), git_blob_sha(data)


# --------------------------------------------------------------------------------------------------------------
# Enumeration of one directory tree as a published file set
# --------------------------------------------------------------------------------------------------------------

def enumerate_tree(root: str | os.PathLike[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """(regular files as sorted relative POSIX paths, problems as (path, reason)). Never follows a symlink."""
    base = os.path.realpath(root)
    files: list[str] = []
    problems: list[tuple[str, str]] = []
    if os.path.islink(root) or not os.path.isdir(base):
        return files, [("(publish-root)", "PUBLISH_ROOT_NOT_A_DIRECTORY")]
    stack = [""]
    while stack:
        rel_dir = stack.pop()
        with os.scandir(os.path.join(base, rel_dir) if rel_dir else base) as it:
            entries = sorted(it, key=lambda e: e.name)
        for entry in entries:
            rel = f"{rel_dir}/{entry.name}" if rel_dir else entry.name
            if len(files) + len(problems) > MAX_FILES:
                return files, problems + [("(publish-root)", "TOO_MANY_FILES")]
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                problems.append((rel, "SYMLINK_IN_PUBLIC_OUTPUT"))
            elif entry.name.startswith("."):
                problems.append((rel, "HIDDEN_ENTRY_NOT_IN_PAGES_SET"))
            elif not scanner._path(rel):
                problems.append((rel, "INVALID_PATH"))
            elif os.path.commonpath([base, os.path.realpath(os.path.join(base, rel))]) != base:
                problems.append((rel, "PATH_ESCAPES_PUBLISH_ROOT"))
            elif stat.S_ISDIR(mode):
                stack.append(rel)
            elif stat.S_ISREG(mode):
                files.append(rel)
            else:
                problems.append((rel, "UNEXPECTED_FILE_TYPE"))
    return sorted(files), problems


def manifest_sha256(rows: list[tuple[str, str]]) -> str:
    """sha256 over ``<sha256>  <path>\\n`` for every published file, sorted by path."""
    digest = hashlib.sha256()
    for path, sha in sorted(rows):
        digest.update(f"{sha}  {path}\n".encode("utf-8", errors="backslashreplace"))
    return digest.hexdigest()


def is_text_name(path: str) -> bool:
    return path.lower().endswith(PUBLISHED_TEXT_SUFFIXES)


# --------------------------------------------------------------------------------------------------------------
# Trusted half: readback of a staged bundle. Executes nothing.
# --------------------------------------------------------------------------------------------------------------

def _load_receipt(staged: str) -> dict[str, Any] | None:
    path = os.path.join(staged, RECEIPT_NAME)
    try:
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_RECEIPT_BYTES:
            return None
        with open(path, "rb") as fh:
            value = json.loads(fh.read().decode("utf-8"))
    except (OSError, ValueError):
        return None
    return value if type(value) is dict else None


def readback(staged_dir: Any, head: Any, *, repo: str | os.PathLike[str], run_id: Any = None,
             run_attempt: Any = None, merge_sha: Any = None,
             pinned: dict[str, frozenset[str]] | None = None) -> dict[str, Any]:
    """Scan every byte of the staged public bundle for ``head``. Returns the result document; never raises.

    ``PUBLIC_OUTPUT_CLEAN`` needs all of: a receipt of this contract for exactly ``head``, from this workflow run and
    attempt, for the publish root and the workflow blob the checked-out tree names, for ``merge_sha`` when given; a
    staged directory that holds only the receipt and the bundle; no enumeration problem; every file scanned or
    pinned; no rule match in any file body or file name."""
    pins = PINNED_BINARY_SHA256 if pinned is None else pinned
    findings: list[dict[str, str]] = []
    unknown: list[dict[str, str]] = []
    out: dict[str, Any] = {
        "contract": CONTRACT, "scanner_contract": scanner.CONTRACT, "rules_version": scanner.RULES_VERSION,
        "head": head if type(head) is str and SHA40.fullmatch(head) else None,
        "publish_root": None, "pages_workflow_blob_sha": None, "file_count": 0, "total_bytes": 0,
        "text_files_scanned": 0, "binary_files_pinned": 0, "manifest_sha256": None, "build_receipt": None,
        "authority": "EVIDENCE_PRODUCER_ONLY_NOT_RELEASE_AUTHORITY", "executes_pr_code": False,
    }

    def finish() -> dict[str, Any]:
        rows = sorted(({"path_sha256_16": _path_ref(f["path"]), "reason": f["reason"]} for f in findings + unknown),
                      key=lambda r: (r["reason"], r["path_sha256_16"]))
        by_rule: dict[str, int] = {}
        for row in rows:
            by_rule[row["reason"]] = by_rule.get(row["reason"], 0) + 1
        out["result"] = "RESTRICTED_CONTENT" if findings else "UNKNOWN" if unknown else "PUBLIC_OUTPUT_CLEAN"
        out["findings_count"] = len(rows)
        out["findings_by_rule"] = dict(sorted(by_rule.items()))
        out["findings"] = rows
        return out

    def uncertain(path: str, reason: str) -> None:
        unknown.append({"path": path, "reason": reason})

    try:
        if out["head"] is None:
            uncertain("(input)", "HEAD_SHA_INVALID")
            return finish()
        if type(staged_dir) is not str or not staged_dir or os.path.islink(staged_dir) or not os.path.isdir(staged_dir):
            uncertain("(input)", "READBACK_INPUT_ABSENT")
            return finish()
        try:
            recipe, workflow_blob = read_recipe(repo)
        except RecipeError as exc:
            uncertain("(recipe)", "PUBLISH_RECIPE_NOT_REPRODUCIBLE_" + str(exc))
            return finish()
        out["publish_root"], out["pages_workflow_blob_sha"] = recipe["publish_root"], workflow_blob
        receipt = _load_receipt(staged_dir)
        if receipt is None or receipt.get("contract") != RECEIPT_CONTRACT or receipt.get("status") != "BUILT":
            uncertain("(receipt)", "BUILD_RECEIPT_MISSING_OR_UNPARSABLE")
            return finish()
        out["build_receipt"] = {k: receipt.get(k) if type(receipt.get(k)) in (str, int) else None for k in (
            "head_sha", "merge_sha", "run_id", "run_attempt", "publish_root", "pages_workflow_blob_sha", "file_count")}
        if receipt.get("head_sha") != out["head"]:
            uncertain("(receipt)", "BUILD_RECEIPT_FOR_ANOTHER_HEAD")
        if (type(run_id) is not str or not run_id or type(run_attempt) is not str or not run_attempt
                or receipt.get("run_id") != run_id or receipt.get("run_attempt") != run_attempt):
            uncertain("(receipt)", "BUILD_RECEIPT_NOT_FROM_THIS_RUN")
        if merge_sha is not None and receipt.get("merge_sha") != merge_sha:
            uncertain("(receipt)", "BUILD_RECEIPT_FOR_ANOTHER_CHECKOUT")
        if receipt.get("publish_root") != recipe["publish_root"] or receipt.get("pages_workflow_blob_sha") != workflow_blob:
            uncertain("(receipt)", "BUILD_RECEIPT_FOR_ANOTHER_RECIPE")
        if unknown:
            return finish()
        with os.scandir(staged_dir) as it:
            top = sorted(e.name for e in it)
        if top != sorted([STAGED_DIST, RECEIPT_NAME]):
            uncertain("(staged)", "UNEXPECTED_STAGED_ENTRY")
            return finish()
        root = os.path.join(staged_dir, STAGED_DIST)
        files, problems = enumerate_tree(root)
        for path, reason in problems:
            uncertain(path, reason)
        if not files:
            uncertain("(publish-root)", "EMPTY_PUBLIC_OUTPUT")
        if receipt.get("file_count") != len(files):
            uncertain("(publish-root)", "FILE_COUNT_MISMATCH_WITH_RECEIPT")
        rows: list[tuple[str, str]] = []
        total = 0
        out["file_count"] = len(files)
        for rel in files:
            for reason, pattern in scanner.KNOWN_SECRET_OR_RESTRICTED_DESIGN:
                if pattern.search(rel):
                    findings.append({"path": rel, "reason": reason + "_IN_FILENAME"})
            full = os.path.join(root, rel)
            size = os.lstat(full).st_size
            total += size
            if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                uncertain(rel, "PUBLISHED_FILE_EXCEEDS_SAFE_SIZE" if size > MAX_FILE_BYTES else "PUBLIC_OUTPUT_EXCEEDS_SAFE_SIZE")
                if total > MAX_TOTAL_BYTES:
                    break
                continue
            with open(full, "rb") as fh:
                data = fh.read(MAX_FILE_BYTES + 1)
            if len(data) != size:
                uncertain(rel, "PUBLISHED_FILE_CHANGED_DURING_READBACK")
                continue
            sha = hashlib.sha256(data).hexdigest()
            rows.append((rel, sha))
            text: str | None = None
            if is_text_name(rel) and b"\x00" not in data:
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = None
            if text is None:
                if is_text_name(rel):
                    uncertain(rel, "PUBLISHED_TEXT_NOT_UTF8")
                elif sha in pins.get(rel, frozenset()):
                    out["binary_files_pinned"] += 1
                else:
                    uncertain(rel, "BINARY_PUBLISHED_FILE_NOT_PINNED")
                continue
            out["text_files_scanned"] += 1
            for reason, pattern in scanner.KNOWN_SECRET_OR_RESTRICTED_DESIGN:
                if pattern.search(text):
                    findings.append({"path": rel, "reason": reason})
        out["total_bytes"] = total
        if len(rows) == len(files):
            out["manifest_sha256"] = manifest_sha256(rows)
    except (OSError, ValueError, RecursionError):
        uncertain("(publish-root)", "ENUMERATION_ERROR")
    return finish()


# --------------------------------------------------------------------------------------------------------------
# Untrusted half: run the Pages build steps and stage the bundle. Runs PR-controlled code.
# --------------------------------------------------------------------------------------------------------------

def _git(repo: str, *args: str) -> bytes | None:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C")
    p = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *args], capture_output=True, env=env)
    return p.stdout if p.returncode == 0 else None


def _rev(repo: str, spec: str) -> str | None:
    raw = _git(repo, "rev-parse", "--verify", "--quiet", spec)
    value = raw.decode("ascii", "replace").strip() if raw else ""
    return value if SHA40.fullmatch(value) else None


def site_changed_in_merge(repo: str) -> bool | None:
    """Does the checked-out merge commit differ from its base parent under the site prefix? None when unknown."""
    if _rev(repo, "HEAD^1") is None:
        return None
    raw = _git(repo, "--literal-pathspecs", "diff", "--name-only", "-z", "HEAD^1", "HEAD", "--", scanner.SITE_PUBLIC_PREFIX)
    return None if raw is None else bool(raw.strip(b"\x00"))


def _bash(script: str, cwd: str, timeout: int) -> int:
    """One workflow step, the way the Actions runner starts a ``run`` step without a ``shell`` key."""
    try:
        return subprocess.run(["bash", "--noprofile", "--norc", "-e", "-c", script], cwd=cwd, timeout=timeout,
                              stdin=subprocess.DEVNULL).returncode
    except subprocess.TimeoutExpired:
        return 124


def _only_build_leftovers(repo: str, allowed_prefix: str | None, reason: str) -> None:
    """Fail unless the work tree equals HEAD apart from untracked files under ``allowed_prefix`` and the caches a
    build leaves behind (``node_modules``, ``__pycache__``; this script's own import writes the latter)."""
    raw = _git(repo, "status", "--porcelain", "-z", "--untracked-files=all")
    if raw is None:
        raise BuildError("GIT_STATE_UNAVAILABLE")
    for entry in raw.split(b"\x00"):
        if not entry:
            continue
        status, path = entry[:2], entry[3:].decode("utf-8", "surrogateescape")
        if status != b"??":
            raise BuildError("BUILD_CHANGED_A_TRACKED_FILE" if allowed_prefix else reason)
        if not (allowed_prefix and path.startswith(allowed_prefix)) and not _BUILD_LEFTOVER_PARTS & set(path.split("/")):
            raise BuildError(reason)


def run_build(repo: str, out_dir: str, head: Any, env: dict[str, str],
              run_step: Callable[[str, str, int], int] = _bash) -> dict[str, Any]:
    """Run the Pages build steps in ``repo`` and stage the published set in ``out_dir``. Raises BuildError."""
    if type(head) is not str or not SHA40.fullmatch(head):
        raise BuildError("HEAD_SHA_INVALID")
    try:
        recipe, workflow_blob = read_recipe(repo)
    except RecipeError as exc:
        raise BuildError("PUBLISH_RECIPE_NOT_REPRODUCIBLE_" + str(exc)) from None
    publish = os.path.join(repo, recipe["publish_root"])
    if os.path.lexists(publish):
        raise BuildError("PUBLISH_ROOT_EXISTS_BEFORE_BUILD")
    if os.path.lexists(out_dir) and (os.path.islink(out_dir) or not os.path.isdir(out_dir) or os.listdir(out_dir)):
        raise BuildError("OUTPUT_DIRECTORY_NOT_EMPTY")
    if os.path.commonpath([os.path.realpath(repo), os.path.realpath(out_dir)]) == os.path.realpath(repo):
        raise BuildError("OUTPUT_DIRECTORY_INSIDE_REPOSITORY")
    merge = _rev(repo, "HEAD^{commit}")
    if merge is None:
        raise BuildError("GIT_STATE_UNAVAILABLE")
    _only_build_leftovers(repo, None, "CHECKOUT_NOT_CLEAN_BEFORE_BUILD")
    outcome: dict[str, str] = {}
    for number, step in enumerate(recipe["steps"], 1):
        if step["only_if_failed"] is not None and outcome.get(step["only_if_failed"]) != "failure":
            continue
        print(f"{BUILD_CONTRACT} step={number}/{len(recipe['steps'])}", flush=True)
        code = run_step(step["run"], repo, STEP_TIMEOUT_SECONDS)
        if step["id"] is not None:
            outcome[step["id"]] = "success" if code == 0 else "failure"
        if code != 0 and not step["continue_on_error"]:
            raise BuildError(f"BUILD_STEP_{number}_FAILED")
    if _rev(repo, "HEAD^{commit}") != merge:
        raise BuildError("GIT_STATE_UNAVAILABLE")
    _only_build_leftovers(repo, recipe["publish_root"] + "/", "BUILD_OUTPUT_OUTSIDE_PUBLISH_ROOT")
    files, problems = enumerate_tree(publish)
    hidden = [p for p, reason in problems if reason == "HIDDEN_ENTRY_NOT_IN_PAGES_SET"]
    if len(hidden) != len(problems):
        raise BuildError("PUBLISH_ROOT_" + sorted(r for _, r in problems if r != "HIDDEN_ENTRY_NOT_IN_PAGES_SET")[0])
    if not files:
        raise BuildError("EMPTY_PUBLIC_OUTPUT")
    staged = os.path.join(out_dir, STAGED_DIST)
    rows: list[tuple[str, str]] = []
    total = 0
    for rel in files:
        target = os.path.join(staged, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(os.path.join(publish, rel), target, follow_symlinks=False)
        with open(target, "rb") as fh:
            data = fh.read()
        total += len(data)
        rows.append((rel, hashlib.sha256(data).hexdigest()))
    receipt = {
        "contract": RECEIPT_CONTRACT, "status": "BUILT", "head_sha": head, "merge_sha": merge,
        "run_id": env.get("GITHUB_RUN_ID"), "run_attempt": env.get("GITHUB_RUN_ATTEMPT"),
        "publish_root": recipe["publish_root"], "pages_workflow_blob_sha": workflow_blob,
        "file_count": len(files), "total_bytes": total, "manifest_sha256": manifest_sha256(rows),
        "hidden_entries_left_out_like_pages": len(hidden), "steps_run": len(recipe["steps"]),
        "step_outcomes": dict(sorted(outcome.items())),
        "authority": "UNTRUSTED_BUILD_OUTPUT_NOT_EVIDENCE_UNTIL_READ_BACK",
    }
    with open(os.path.join(out_dir, RECEIPT_NAME), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    env = dict(os.environ) if env is None else env
    args = list(sys.argv[1:] if argv is None else argv)

    def option(name: str, default: str | None = None) -> str | None:
        return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default

    command = args[0] if args else ""
    repo = option("--repo", ".") or "."
    head = option("--head")
    if command == "build":
        out_dir = option("--out")
        status, detail = "FAILED", "USAGE"
        try:
            if out_dir:
                if "--skip-unless-site-changed" in args and site_changed_in_merge(repo) is False:
                    status, detail = "SKIPPED", "NO_SITE_PATH_IN_MERGE_DELTA"
                else:
                    receipt = run_build(repo, out_dir, head, env)
                    status, detail = "BUILT", f"files={receipt['file_count']} manifest_sha256={receipt['manifest_sha256']}"
        except BuildError as exc:
            detail = str(exc)
        except (OSError, ValueError) as exc:
            detail = "BUILD_ERROR_" + type(exc).__name__
        if status == "FAILED" and out_dir and os.path.isdir(out_dir) and not os.path.islink(out_dir):
            shutil.rmtree(out_dir, ignore_errors=True)  # never leave a half-staged bundle for the upload step
        print(f"{BUILD_CONTRACT} status={status} head={head} {detail}")
        return 0 if status in ("BUILT", "SKIPPED") else 1
    if command == "scan":
        out = readback(option("--staged"), head, repo=repo, run_id=env.get("GITHUB_RUN_ID"),
                       run_attempt=env.get("GITHUB_RUN_ATTEMPT"), merge_sha=option("--merge"))
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["result"] == "PUBLIC_OUTPUT_CLEAN" else 1
    print(json.dumps({"contract": CONTRACT, "result": "UNKNOWN", "reason": "USAGE: build|scan"}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
