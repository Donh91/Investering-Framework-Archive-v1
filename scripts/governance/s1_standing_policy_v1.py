#!/usr/bin/env python3
"""S1 standing policy reader v1: read-only and advisory. It grants nothing.

Standing owner decisions for the bounded S1 LOW lane exist only as fields of the
manifest blob ``00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json`` reachable from
current ``main``. This module reads them fail-closed and derives three things
mechanically so that prose cannot drift from what CI executes:

* ``derive_required_job_executed_paths``: every repository file the manifest's
  required jobs execute (workflow text tokens plus the local import closure).
  Those files are GOVERNANCE, never unattended LOW.
* ``is_governance_path`` / ``is_science_gated_path``: one table for callers.
* ``review_reuse_decision``: the D3 rule for reusing an exact-head independent
  review across main drift.

No network, no git, no write outside ``--output``. A result from this module is
never a release permission; AGENTS.md section 0.2c on current main is.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

CONTRACT = "S1_STANDING_POLICY_V1"
MANIFEST_PATH = "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json"
MAIN_REF = "refs/heads/main"
LANE_STATES = ("SHADOW", "DOCS_ONLY", "LOW_CODE")
CLASSES = ("DOCS_ONLY", "LOW_CODE")
ABSENT = "ABSENT"

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_TOKEN = re.compile(r"[A-Za-z0-9_./-]+")
_CODE_SUFFIXES = (".py", ".mjs", ".js", ".cjs", ".sh")
_JS_IMPORT = re.compile(r"""(?:from|import|require\()\s*['"](\.{1,2}/[^'"]+)['"]""")


def git_blob_sha(data: bytes) -> str:
    """The git blob id of ``data`` (what the GitHub contents API reports as ``sha``)."""
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _clean_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return None
    if value.startswith("/") or "\\" in value or "\x00" in value:
        return None
    parts = PurePosixPath(value).parts
    if any(part in ("..", ".") for part in parts) or "/".join(parts) != value:
        return None
    return value


def _clean_paths(values: Any) -> list[str] | None:
    if not isinstance(values, (list, tuple)):
        return None
    cleaned = [_clean_path(value) for value in values]
    if any(item is None for item in cleaned):
        return None
    return cleaned  # type: ignore[return-value]


# --------------------------------------------------------------------------
# A2: standing decisions are blobs on main
# --------------------------------------------------------------------------

def lane_state(manifest: Any) -> str:
    """SHADOW unless the manifest names a known later stage. SHADOW means no merges."""
    if not isinstance(manifest, Mapping) or manifest.get("contract") != "S1_REQUIRED_PR_JOBS_POLICY_V1":
        return "SHADOW"
    value = manifest.get("lane_state")
    return value if isinstance(value, str) and value in LANE_STATES else "SHADOW"


def unattended_class_enabled(manifest: Any, release_class: str) -> bool:
    state = lane_state(manifest)
    if release_class == "DOCS_ONLY":
        return state in ("DOCS_ONLY", "LOW_CODE")
    if release_class == "LOW_CODE":
        return state == "LOW_CODE"
    return False


def review_optional(manifest: Any, release_class: str) -> bool:
    """True only when main's manifest lists the class AND the lane is open for it."""
    if not unattended_class_enabled(manifest, release_class):
        return False
    listed = manifest.get("review_optional_classes")
    if not isinstance(listed, list) or any(item not in CLASSES for item in listed):
        return False
    return release_class in listed


def standing_decisions(manifest_bytes: Any, *, blob_sha: Any, source_ref: Any) -> dict[str, Any]:
    """Read the standing decisions from one manifest blob.

    The caller states where the bytes came from. Anything other than the main
    ref, a blob id that does not match the bytes, or unparsable JSON yields the
    closed state. The caller's ``source_ref`` is not authenticated here.
    """
    closed = {"contract": CONTRACT, "lane_state": "SHADOW", "review_optional_classes": [],
              "manifest_blob_sha": None, "source": "UNPROVEN"}
    if source_ref != MAIN_REF:
        return {**closed, "reason": "NOT_FROM_MAIN"}
    if not isinstance(manifest_bytes, (bytes, bytearray)) or not isinstance(blob_sha, str) \
            or not _SHA40.match(blob_sha) or git_blob_sha(bytes(manifest_bytes)) != blob_sha:
        return {**closed, "reason": "MANIFEST_BLOB_MISMATCH"}
    try:
        manifest = json.loads(bytes(manifest_bytes).decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {**closed, "reason": "MANIFEST_UNPARSABLE"}
    if not isinstance(manifest, Mapping) or manifest.get("contract") != "S1_REQUIRED_PR_JOBS_POLICY_V1":
        return {**closed, "reason": "MANIFEST_CONTRACT_MISMATCH"}
    raw_state = manifest.get("lane_state")
    if raw_state not in LANE_STATES:
        return {**closed, "reason": "LANE_STATE_MISSING_OR_UNKNOWN", "manifest_blob_sha": blob_sha}
    return {"contract": CONTRACT, "lane_state": raw_state,
            "review_optional_classes": [c for c in CLASSES if review_optional(manifest, c)],
            "manifest_blob_sha": blob_sha, "source": "MAIN_BLOB", "reason": "OK"}


# --------------------------------------------------------------------------
# B2: what the required jobs execute
# --------------------------------------------------------------------------

def required_workflow_paths(manifest: Mapping[str, Any]) -> list[str]:
    paths = set()
    for jobs in (manifest.get("classes") or {}).values():
        for job in jobs:
            paths.add(job["workflow_path"])
    return sorted(paths)


def _files_under(root: Path, rel: str) -> list[str]:
    base = root / rel
    return sorted(p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file())


def _workflow_seed(root: Path, text: str) -> set[str]:
    found: set[str] = set()
    for token in _TOKEN.findall(text):
        token = token.rstrip(".")
        if not token or token.startswith(("/", "-")) or ".." in token.split("/"):
            continue
        candidate = root / token
        if "/" in token and candidate.is_file():
            found.add(PurePosixPath(token).as_posix())
        elif "/" in token and candidate.is_dir() and not token.startswith(".github"):
            found.update(_files_under(root, PurePosixPath(token).as_posix()))
        elif "." in token and "/" not in token:  # dotted module, e.g. tests.x.test_y
            dotted = token.replace(".", "/")
            if (root / (dotted + ".py")).is_file():
                found.add(dotted + ".py")
    return found


def _module_candidates(root: Path, importer: str, module: str, level: int, names: Iterable[str]) -> set[str]:
    found: set[str] = set()
    bases: list[PurePosixPath] = []
    importer_dir = PurePosixPath(importer).parent
    if level:
        anchor = importer_dir
        for _ in range(level - 1):
            anchor = anchor.parent
        bases.append(anchor)
    else:
        bases.extend([PurePosixPath(""), importer_dir])  # repo root and script directory
    for base in bases:
        target = base.joinpath(*module.split(".")) if module else base
        options = [target] + [target / name for name in names]
        for option in options:
            rel = option.as_posix()
            if rel in ("", "."):
                continue
            if (root / (rel + ".py")).is_file():
                found.add(rel + ".py")
            if (root / rel / "__init__.py").is_file():
                found.add(rel + "/__init__.py")
    return found


def _literal_paths(root: Path, text: str) -> set[str]:
    """Repo-relative CODE file paths written out in a source text (e.g. spec_from_file_location targets).

    Data files a test reads are deliberately not followed: producer-written files change on
    every data commit and are not LOW paths anyway."""
    found: set[str] = set()
    for token in _TOKEN.findall(text):
        token = token.rstrip(".")
        if "/" not in token or token.startswith(("/", "-", ".github")) or ".." in token.split("/"):
            continue
        if token.endswith(_CODE_SUFFIXES) and (root / token).is_file():
            found.add(PurePosixPath(token).as_posix())
    return found


def _local_imports(root: Path, rel: str) -> set[str]:
    path = root / rel
    found: set[str] = set()
    if rel.endswith(_CODE_SUFFIXES):
        try:
            found |= _literal_paths(root, path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            pass
    if rel.endswith(".py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            return found
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found |= _module_candidates(root, rel, alias.name, 0, ())
            elif isinstance(node, ast.ImportFrom):
                found |= _module_candidates(root, rel, node.module or "", node.level,
                                            [alias.name for alias in node.names])
    elif rel.endswith((".mjs", ".js", ".cjs")):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return found
        for spec in _JS_IMPORT.findall(text):
            parts: list[str] = []
            for part in (PurePosixPath(rel).parent / spec).parts:
                if part == "..":
                    if not parts:
                        break
                    parts.pop()
                elif part != ".":
                    parts.append(part)
            else:
                target = "/".join(parts)
                if target and (root / target).is_file():
                    found.add(target)
    return found


def derive_required_job_executed_paths(root: Path | str, manifest: Mapping[str, Any]) -> list[str]:
    """Files the manifest's required workflow files execute, to a fixed point.

    Three sources: path and dotted-module tokens in the workflow text, local
    imports, and repo-relative code file paths written out in an executed source.
    A lower bound: files reached through computed paths are not seen. The
    workflow files themselves are excluded (``.github/`` is already governance).
    """
    root = Path(root)
    closure: set[str] = set()
    for workflow in required_workflow_paths(manifest):
        closure |= _workflow_seed(root, (root / workflow).read_text(encoding="utf-8"))
    frontier = set(closure)
    while frontier:
        new: set[str] = set()
        for rel in frontier:
            new |= _local_imports(root, rel) - closure
        closure |= new
        frontier = new
    return sorted(path for path in closure if not path.startswith(".github/"))


def is_governance_path(path: str, manifest: Mapping[str, Any]) -> bool:
    """GOVERNANCE per the manifest: listed prefixes, exact files, required workflows, executed files.

    Unusable input is governance (fail closed)."""
    cleaned = _clean_path(path)
    if cleaned is None or not isinstance(manifest, Mapping):
        return True
    executed = manifest.get("required_job_executed_paths")
    prefixes = manifest.get("governance_prefixes")
    exact = manifest.get("governance_exact_paths")
    if not all(isinstance(item, list) for item in (executed, prefixes, exact)):
        return True
    if cleaned in executed or cleaned in exact or cleaned in required_workflow_paths(manifest):
        return True
    return any(isinstance(prefix, str) and prefix and cleaned.startswith(prefix) for prefix in prefixes)


def is_science_gated_path(path: str, manifest: Mapping[str, Any]) -> bool:
    """D5: publications under these prefixes need the source/science owner gate, whatever the suffix."""
    cleaned = _clean_path(path)
    prefixes = manifest.get("science_gated_prefixes") if isinstance(manifest, Mapping) else None
    if cleaned is None or not isinstance(prefixes, list) or not prefixes:
        return True
    return any(isinstance(prefix, str) and prefix and cleaned.startswith(prefix) for prefix in prefixes)


# --------------------------------------------------------------------------
# G3 / D3: review reuse across main drift
# --------------------------------------------------------------------------

def policy_blob_paths(manifest: Mapping[str, Any]) -> list[str]:
    """Every file whose change between review-time main and current main voids reuse."""
    reuse = manifest.get("review_reuse") or {}
    paths = set(reuse.get("policy_blob_paths") or [])
    paths.add(MANIFEST_PATH)
    paths.update(required_workflow_paths(manifest))
    paths.update(manifest.get("required_job_executed_paths") or [])
    return sorted(paths)


def review_reuse_decision(*, release_class: Any, pr_paths: Any, pr_rename_sources: Any,
                          drift_paths: Any, drift_census_complete: Any,
                          policy_blobs_at_review_main: Any, policy_blobs_at_current_main: Any,
                          manifest: Any) -> dict[str, Any]:
    """May an exact-head independent review made at an older main be reused now?

    Reuse iff (a) the complete drift census is disjoint from every PR path and
    rename source, (b) no policy file is in the drift, and (c) every policy
    blob is proven identical at both mains. The class of the drift paths is not
    tested. DOCS_ONLY only; LOW_CODE is always re-reviewed.
    """
    def no(reason: str, **extra: Any) -> dict[str, Any]:
        return {"contract": CONTRACT, "reuse": False, "reason": reason, **extra}

    if not isinstance(manifest, Mapping) or manifest.get("contract") != "S1_REQUIRED_PR_JOBS_POLICY_V1":
        return no("MANIFEST_UNUSABLE")
    if release_class == "LOW_CODE":
        return no("LOW_CODE_REQUIRES_REREVIEW")
    if release_class != "DOCS_ONLY":
        return no("CLASS_NOT_ELIGIBLE")
    pr = _clean_paths(pr_paths)
    renames = _clean_paths(pr_rename_sources)
    drift = _clean_paths(drift_paths)
    if not pr or renames is None or drift is None:
        return no("PATH_LIST_UNUSABLE")
    if drift_census_complete is not True:
        return no("DRIFT_CENSUS_INCOMPLETE")
    overlap = sorted((set(pr) | set(renames)) & set(drift))
    if overlap:
        return no("PR_PATH_IN_DRIFT", paths=overlap)
    policy = policy_blob_paths(manifest)
    touched = sorted(set(policy) & set(drift))
    if touched:
        return no("POLICY_PATH_IN_DRIFT", paths=touched)
    if not isinstance(policy_blobs_at_review_main, Mapping) or not isinstance(policy_blobs_at_current_main, Mapping):
        return no("POLICY_BLOB_UNPROVEN")
    for path in policy:
        before = policy_blobs_at_review_main.get(path)
        after = policy_blobs_at_current_main.get(path)
        for value in (before, after):
            if not isinstance(value, str) or not (value == ABSENT or _SHA40.match(value)):
                return no("POLICY_BLOB_UNPROVEN", paths=[path])
        if before != after:
            return no("POLICY_BLOB_CHANGED", paths=[path])
    return {"contract": CONTRACT, "reuse": True, "reason": "DISJOINT_AND_POLICY_UNCHANGED",
            "policy_paths_checked": len(policy)}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--derive", action="store_true", help="print the derived executed-path list as JSON")
    group.add_argument("--check", action="store_true", help="exit 1 unless the manifest list equals the derived list")
    args = parser.parse_args(argv)
    root = Path(args.root)
    manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
    derived = derive_required_job_executed_paths(root, manifest)
    if args.derive:
        print(json.dumps(derived, indent=2))
        return 0
    listed = manifest.get("required_job_executed_paths")
    if listed == derived:
        print(f"OK {len(derived)} required-job executed paths match the manifest")
        return 0
    missing = sorted(set(derived) - set(listed or []))
    extra = sorted(set(listed or []) - set(derived))
    print(json.dumps({"status": "STALE", "missing_from_manifest": missing, "not_derived": extra}, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
