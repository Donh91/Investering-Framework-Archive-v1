#!/usr/bin/env python3
"""Source-pinned, no-network, no-push Sol MAX patch sandbox.

Creates a disposable Git worktree for a received advisory patch. It checks
actual patch application, source bytes and Python syntax. It deliberately
does NOT execute modified code, run model-supplied commands or merge anything.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import tempfile
from pathlib import Path

from scripts.api_agent import sol_max_elite_transport as t
from scripts.api_agent import sol_max_elite_patch_admit as a


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> str:
    # Git receives no GitHub token or OpenAI key. All paths are fixed by owner
    # code and source allowlists, never constructed from an LLM shell command.
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith(("GITHUB_", "GH_", "OPENAI_", "AWS_"))
                   or k in ("GIT_ASKPASS", "SSH_ASKPASS", "SSH_AUTH_SOCK"))}
    env["GIT_TERMINAL_PROMPT"] = "0"
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], input=input_bytes,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        timeout=45, check=False,
    )
    if proc.returncode:
        raise ValueError("ELITE_SANDBOX_GIT_VERIFICATION_FAILED")
    return proc.stdout.decode("utf-8", errors="strict").strip()


def verify_binding(source: dict, candidate: dict, receipt: dict, patch: bytes) -> list[str]:
    if (not isinstance(source, dict) or not isinstance(candidate, dict)
            or not isinstance(receipt, dict)
            or source.get("contract") != "S1_SOL_ELITE_SOURCE_PACKET_v1"
            or candidate.get("contract") != "S1_SOL_ELITE_PATCH_CANDIDATE_v1"
            or candidate.get("status") != "UNTRUSTED_PATCH_REQUIRES_REVIEW"
            or candidate.get("source_head") != source.get("source_head")
            or t.HEX40.fullmatch(str(source.get("source_head"))) is None
            or candidate.get("source_sha256") != t.digest(t.canonical(source))
            or candidate.get("patch_sha256") != t.digest(patch)
            or candidate.get("response_id") != receipt.get("response_id")
            or receipt.get("contract") != "S1_SOL_ELITE_GET_RECEIPT_v1"
            or receipt.get("status") != "COMPLETED"
            or type(receipt.get("http_status")) is not int
            or receipt.get("http_status") != 200
            or receipt.get("mission") != source.get("mission_id")
            or receipt.get("source_head") != source.get("source_head")
            or receipt.get("context_sha256") != t.digest(t.canonical(source))
            or receipt.get("new_paid_post") is not False
            or receipt.get("source_applied") is not False
            or receipt.get("merge_authorized") is not False
            or candidate.get("source_written") is not False
            or candidate.get("code_executed") is not False
            or candidate.get("merge_authorized") is not False):
        raise ValueError("ELITE_SANDBOX_UNBOUND_ARTIFACT")
    files = source.get("source_files")
    if not isinstance(files, dict) or not files:
        raise ValueError("ELITE_SANDBOX_MISSING_SOURCE")
    diff = patch.decode("utf-8", errors="strict")
    paths = a.patch_paths(diff, files)
    if paths != candidate.get("changed_paths"):
        raise ValueError("ELITE_SANDBOX_CHANGED_PATH_DRIFT")
    for path, entry in files.items():
        t.check_safe_relative(path)
        if (not isinstance(entry, dict)
                or not isinstance(entry.get("content"), str)
                or type(entry.get("bytes")) is not int
                or not isinstance(entry.get("sha256"), str)):
            raise ValueError("ELITE_SANDBOX_INVALID_SOURCE_ENTRY")
        raw = entry["content"].encode("utf-8")
        if len(raw) != entry["bytes"] or t.digest(raw) != entry["sha256"]:
            raise ValueError("ELITE_SANDBOX_SOURCE_HASH_INVALID")
    return paths


def verify_in_sandbox(repo: Path, source: dict, candidate: dict,
                      receipt: dict, patch: bytes) -> dict:
    paths = verify_binding(source, candidate, receipt, patch)
    repo = repo.resolve(strict=True)
    if not (repo / ".git").exists():
        raise ValueError("ELITE_SANDBOX_REPO_NOT_GIT")
    head = source["source_head"]
    # No network fetch and no arbitrary ref: only an already-local exact SHA.
    if git(repo, "cat-file", "-t", head) != "commit":
        raise ValueError("ELITE_SANDBOX_SOURCE_HEAD_NOT_COMMIT")
    changed = {}
    with tempfile.TemporaryDirectory(prefix="s1-sol-elite-sandbox-") as tmp:
        worktree = Path(tmp) / "isolated"
        git(repo, "worktree", "add", "--detach", str(worktree), head)
        try:
            if git(worktree, "rev-parse", "HEAD") != head:
                raise ValueError("ELITE_SANDBOX_HEAD_DRIFT")
            for path, detail in source["source_files"].items():
                obj = worktree / path
                if obj.is_symlink() or not obj.is_file():
                    raise ValueError("ELITE_SANDBOX_SOURCE_NOT_REGULAR")
                actual = obj.read_bytes()
                if actual != detail["content"].encode("utf-8"):
                    raise ValueError("ELITE_SANDBOX_SOURCE_BYTES_DRIFT")
            git(worktree, "apply", "--check", "--whitespace=error", "-", input_bytes=patch)
            git(worktree, "apply", "--whitespace=error", "-", input_bytes=patch)
            git(worktree, "diff", "--check")
            actual_paths = git(worktree, "diff", "--name-only", "--no-renames").splitlines()
            if sorted(actual_paths) != sorted(paths):
                raise ValueError("ELITE_SANDBOX_CHANGED_FILES_MISMATCH")
            for path in paths:
                obj = worktree / path
                if obj.is_symlink() or not obj.is_file():
                    raise ValueError("ELITE_SANDBOX_PATCH_CREATED_SYMLINK")
                raw = obj.read_bytes()
                if any(__import__("re").search(pattern, raw) for pattern in t.CREDENTIALS):
                    raise ValueError("ELITE_SANDBOX_PATCH_INTRODUCED_SECRET")
                if path.endswith(".py"):
                    try:
                        ast.parse(raw.decode("utf-8"), filename=path)
                    except (UnicodeError, SyntaxError) as exc:
                        raise ValueError("ELITE_SANDBOX_PYTHON_SYNTAX_INVALID") from exc
                changed[path] = t.digest(raw)
        finally:
            git(repo, "worktree", "remove", "--force", str(worktree))
    return {
        "contract": "S1_SOL_ELITE_SANDBOX_RECEIPT_v1",
        "status": "PATCH_APPLIES_AND_PYTHON_SYNTAX_VALID",
        "original_source_head": head,
        "source_sha256": t.digest(t.canonical(source)),
        "response_id": candidate["response_id"],
        "patch_sha256": t.digest(patch),
        "changed_paths": paths,
        "patched_sha256_by_path": changed,
        "model_code_executed": False,
        "domain_regressions_executed": False,
        "source_committed": False,
        "source_pushed": False,
        "merge_authorized": False,
        "next_gate": "EXISTING_ORIGINAL_OWNER_INDEPENDENT_REVIEW_AND_REAL_TESTS",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--patch-candidate", type=Path, required=True)
    p.add_argument("--get-receipt", type=Path, required=True)
    p.add_argument("--patch", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    source = a.load_object(args.source)
    candidate = a.load_object(args.patch_candidate)
    receipt = a.load_object(args.get_receipt)
    if args.patch.stat().st_size > a.PATCH_LIMIT:
        raise ValueError("ELITE_SANDBOX_PATCH_OVERSIZED")
    result = verify_in_sandbox(args.repo_root, source, candidate,
                               receipt, args.patch.read_bytes())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / "sandbox_receipt.json"
    if out.exists():
        raise ValueError("ELITE_SANDBOX_RECEIPT_ALREADY_EXISTS")
    out.write_bytes(t.canonical(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
