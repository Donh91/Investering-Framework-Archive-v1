#!/usr/bin/env python3
"""Admit a Sol MAX code-patch CANDIDATE from authentic GET-only evidence.

This validates untrusted structured output and exact public source binding.
It does NOT execute, apply, commit, push, review-approve or merge the patch.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.api_agent import sol_max_elite_transport as t

PATCH_LIMIT = 16000
RESPONSE_LIMIT = 2_000_000
FILE_HEADER = re.compile(r"^diff --git a/([^\s]+) b/([^\s]+)$", re.MULTILINE)
BODY_HEADERS = re.compile(r"^--- (\S+)\n\+\+\+ (\S+)$", re.MULTILINE)
BANNED = ("new file mode ", "deleted file mode ", "old mode ", "new mode ",
          "rename from ", "rename to ", "copy from ", "copy to ",
          "GIT binary patch", "Binary files ", "Submodule ", "\\ No newline")
SCHEMA = frozenset(("status", "unified_diff", "rationale", "tests"))


def load_object(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > RESPONSE_LIMIT:
        raise ValueError("ELITE_PROPOSAL_SOURCE_MISSING_OR_OVERSIZED")
    obj = json.loads(path.read_text())
    if not isinstance(obj, dict):
        raise ValueError("ELITE_PROPOSAL_SOURCE_NOT_OBJECT")
    return obj


def verify_source(source: dict, request: dict) -> dict[str, dict]:
    if (source.get("contract") != "S1_SOL_ELITE_SOURCE_PACKET_v1"
            or source.get("repo") != t.REPO
            or not isinstance(source.get("source_head"), str)
            or t.HEX40.fullmatch(source["source_head"]) is None
            or request != t.checked_request(source)):
        raise ValueError("ELITE_SOURCE_REQUEST_NOT_EXACTLY_BOUND")
    files = source.get("source_files")
    if not isinstance(files, dict) or not files:
        raise ValueError("ELITE_PATCH_SOURCE_FILES_MISSING")
    for path, detail in files.items():
        t.check_safe_relative(path)
        if (not isinstance(detail, dict) or not isinstance(detail.get("content"), str)
                or type(detail.get("bytes")) is not int
                or not isinstance(detail.get("sha256"), str)):
            raise ValueError("ELITE_PATCH_SOURCE_BYTES_INVALID")
        raw = detail["content"].encode("utf-8")
        if len(raw) != detail["bytes"] or t.digest(raw) != detail["sha256"]:
            raise ValueError("ELITE_PATCH_SOURCE_HASH_MISMATCH")
    return files


def extract_structured(response: dict) -> dict[str, Any]:
    if (response.get("status") != "completed"
            or response.get("model") != t.MODEL
            or not isinstance(response.get("id"), str)
            or t.RESPONSE_ID.fullmatch(response["id"]) is None):
        raise ValueError("ELITE_PROVIDER_COMPLETION_OR_MODEL_INVALID")
    blocks = [
        content.get("text")
        for item in response.get("output", [])
        if isinstance(item, dict) and item.get("type") == "message"
        for content in item.get("content", [])
        if isinstance(content, dict) and content.get("type") == "output_text"
    ]
    if len(blocks) != 1 or not isinstance(blocks[0], str) or len(blocks[0]) > 60000:
        raise ValueError("ELITE_PROVIDER_STRUCTURED_TEXT_INVALID")
    obj = json.loads(blocks[0])
    if (not isinstance(obj, dict) or set(obj) != SCHEMA
            or obj.get("status") not in ("PATCH", "ABSTAIN")
            or not isinstance(obj.get("unified_diff"), str)
            or not isinstance(obj.get("rationale"), str)
            or len(obj["rationale"]) > 6000
            or not isinstance(obj.get("tests"), list)
            or len(obj["tests"]) > 24
            or any(not isinstance(x, str) or len(x) > 800 for x in obj["tests"])):
        raise ValueError("ELITE_PROVIDER_PATCH_SCHEMA_INVALID")
    return obj


def patch_paths(diff: str, source_files: dict[str, dict]) -> list[str]:
    if not diff.startswith("diff --git "):
        raise ValueError("ELITE_NOT_UNIFIED_DIFF")
    raw = diff.encode("utf-8")
    if (len(raw) > PATCH_LIMIT or b"\x00" in raw
            or any(re.search(pat, raw) for pat in t.CREDENTIALS)):
        raise ValueError("ELITE_PATCH_OVERSIZED_BINARY_OR_SECRET")
    lines = diff.splitlines()
    if any(line.startswith(BANNED) for line in lines):
        raise ValueError("ELITE_PATCH_MODE_RENAME_BINARY_FORBIDDEN")
    names = FILE_HEADER.findall(diff)
    body = BODY_HEADERS.findall(diff)
    if not names or len(names) != len(body) or len(names) > 8:
        raise ValueError("ELITE_PATCH_HEADER_COVERAGE")
    paths = []
    for (src, dst), (old, new) in zip(names, body):
        t.check_safe_relative(src)
        if (src != dst or src not in source_files
                or old != "a/" + src or new != "b/" + dst
                or src in paths):
            raise ValueError("ELITE_PATCH_PATH_NOT_IN_EXACT_SOURCE_SCOPE")
        paths.append(src)
    if not any(line.startswith("@@ ") for line in lines):
        raise ValueError("ELITE_PATCH_WITHOUT_CHANGE_HUNKS")
    return paths


def admit(source: dict, request: dict, response: dict) -> tuple[dict, dict]:
    files = verify_source(source, request)
    proposal = extract_structured(response)
    if proposal["status"] == "ABSTAIN":
        if proposal["unified_diff"]:
            raise ValueError("ELITE_ABSTAIN_WITH_PATCH")
        changed = []
    else:
        changed = patch_paths(proposal["unified_diff"], files)
    result = {
        "contract": "S1_SOL_ELITE_PATCH_CANDIDATE_v1",
        "status": ("ABSTAIN" if not changed else "UNTRUSTED_PATCH_REQUIRES_REVIEW"),
        "response_id": response["id"],
        "model": response["model"],
        "mission": source.get("mission_id"),
        "owner_issue": source.get("original_owner_issue"),
        "original_pr": source.get("original_pr"),
        "source_head": source["source_head"],
        "source_sha256": t.digest(t.canonical(source)),
        "request_sha256": t.digest(t.canonical(request)),
        "proposal_sha256": t.digest(t.canonical(proposal)),
        "patch_sha256": (t.digest(proposal["unified_diff"].encode()) if changed else None),
        "changed_paths": changed,
        "risk_class": ("HIGH_IMPACT_REVIEW_REQUIRED" if any(
            p.startswith(".github/") or "/governance/" in p
            or "/api_agent/" in p for p in changed)
            else "BOUNDED_SOURCE_REVIEW_REQUIRED"),
        "source_written": False,
        "code_executed": False,
        "github_review_approved": False,
        "merge_authorized": False,
        "next_gate": ("ORIGINAL_HEAD_SANDBOX_GIT_APPLY_CHECK_AND_TEST"
                      if changed else "ABSTAIN_WITH_EVIDENCE"),
    }
    return result, proposal


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--request", type=Path, required=True)
    p.add_argument("--provider-response", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    source, request, response = (load_object(x) for x in (
        args.source, args.request, args.provider_response))
    result, proposal = admit(source, request, response)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for file in ("patch_candidate.json", "proposal.json"):
        if (args.output_dir / file).exists():
            raise ValueError("ELITE_PATCH_OUTPUT_ALREADY_EXISTS")
    (args.output_dir / "patch_candidate.json").write_bytes(t.canonical(result))
    (args.output_dir / "proposal.json").write_bytes(t.canonical(proposal))
    if result["status"] == "UNTRUSTED_PATCH_REQUIRES_REVIEW":
        (args.output_dir / "candidate.patch").write_bytes(
            proposal["unified_diff"].encode("utf-8"))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
