"""S1_DIFF_SCAN_V1, source-bound public/private boundary scan. SHADOW ONLY.

This is an advisory text scanner, NOT an authentication oracle or release authority.
An existing S1 operator must independently fetch and authenticate every original
PR file/HEAD/blob and its complete pages. No network, credentials or write side
effects are used by this module. Never output secret text in findings.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

CONTRACT = "S1_DIFF_SCAN_V1"
RULES_VERSION = "S1_DIFF_SCAN_RULES_20261112_V1"
REPO = "Donh91/Investering-Framework-Archive-v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
MAX_FILES = 3000
MAX_TEXT_BYTES = 512 * 1024

# Conservative high-impact/private routes. These are NOT eligible for unattended
# LOW releases even if their textual diff contains no known key or secret string.
BLOCKED_PREFIXES = (
    ".github/", ".agents/", "00_FMOS/", "00_ARCHIVE_CONTROL/",
    "research/api_agent/", "private/", "secrets/", "vault/",
    "config/private/", "data/private/", "08_SOURCE_MATERIAL/private/",
)
BLOCKED_BASENAMES = {"AGENTS.md", ".env", ".npmrc", ".pypirc", "id_rsa", "id_ed25519"}
TEXT_SUFFIXES = (
    ".md", ".mdx", ".rst", ".txt", ".py", ".js", ".mjs", ".cjs",
    ".ts", ".tsx", ".jsx", ".json", ".jsonl", ".css", ".html",
    ".htm", ".yml", ".yaml", ".toml", ".ini", ".sh",
)
KNOWN_SECRET_OR_RESTRICTED_DESIGN = (
    ("PRIVATE_KEY_BLOCK", re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----", re.I)),
    ("API_KEY_LITERAL", re.compile(r"\b(?:ghp_|gho_|github_pat_|sk-proj-|sk-[A-Za-z0-9]{20,})[A-Za-z0-9_-]{12,}", re.I)),
    ("AWS_ACCESS_KEY", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("SIGNED_URL", re.compile(r"\b(?:X-Amz-Signature|X-Goog-Signature|Signature=)[A-Za-z0-9%_-]{8,}", re.I)),
    ("EXPLICIT_PRIVATE_DESIGN", re.compile(
        r"\b(?:PRIVATE[_ -]ALPHA[_ -](?:DESIGN|STRATEGY|ARCHITECTURE|MODEL)"
        r"|INTERNAL[_ -]ONLY|OWNER[_ -]ONLY|NOT[_ -]FOR[_ -]PUBLICATION"
        r"|CONFIDENTIAL[_ -]RESEARCH|PRIVATE[_ -]RESEARCH[_ -]DESIGN)\b", re.I)),
    ("CREDENTIAL_ASSIGNMENT", re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|private[_-]?key)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_+./=-]{18,}")),
    ("MNEMONIC_EXPOSURE", re.compile(r"(?i)\b(?:seed phrase|mnemonic phrase)\s*[:=]\s*\w+(?:\s+\w+){5,}")),
)

def _sha(s: Any) -> bool:
    return type(s) is str and SHA40.fullmatch(s) is not None

def _path(p: Any) -> bool:
    return (type(p) is str and bool(p) and len(p) < 500 and
            p == p.strip() and not p.startswith(("/", "./", "\\")) and
            "\\" not in p and "//" not in p and
            all(part not in ("", ".", "..") for part in p.split("/")))

def _is_text_path(p: str) -> bool:
    return p.lower().endswith(TEXT_SUFFIXES)

def _result(head: Any, value: str, findings: list[dict[str, str]],
            input_sha256: str | None) -> dict[str, Any]:
    return {
        "contract": CONTRACT, "method": CONTRACT, "rules_version": RULES_VERSION,
        "head": head, "result": value, "findings_count": len(findings),
        "findings": findings, "input_sha256": input_sha256,
        "authority": "ADVISORY_ONLY", "externally_authenticated": False,
    }

def scan_pr(record: Any) -> dict[str, Any]:
    """Return NO_RESTRICTED_CONTENT, RESTRICTED_CONTENT or UNKNOWN.

    Native completeness is an INPUT CONTRACT, not a proof created by this function.
    A caller-supplied boolean, timestamp, hash or API URL never authenticates GitHub.
    """
    r = record if type(record) is dict else {}
    head = r.get("head")
    try:
        encoded = json.dumps(r, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("utf-8")
        input_hash = hashlib.sha256(encoded).hexdigest()
    except (TypeError, ValueError, UnicodeError):
        return _result(head, "UNKNOWN", [{"path": "(input)", "reason": "INPUT_NOT_CANONICAL"}], None)

    findings: list[dict[str, str]] = []
    unknown: list[dict[str, str]] = []

    def fail(path: str, reason: str) -> None:
        findings.append({"path": path, "reason": reason})

    def uncertain(path: str, reason: str) -> None:
        unknown.append({"path": path, "reason": reason})

    if (r.get("repo") != REPO or not _sha(head) or
            r.get("pr_head_sha") != head or
            r.get("changed_files_count_head_sha") != head or
            type(r.get("changed_files_count")) is not int or
            not 0 < r["changed_files_count"] <= MAX_FILES or
            r.get("pages_complete") is not True):
        uncertain("(input)", "NATIVE_HEAD_OR_FILE_CENSUS_UNVERIFIED")
    if type(r.get("title")) is not str or type(r.get("body")) is not str:
        uncertain("(conversation)", "PR_TITLE_OR_BODY_UNAVAILABLE")
    files = r.get("files")
    if not isinstance(files, list) or len(files) == 0:
        uncertain("(files)", "FILE_LIST_MISSING")
        files = []
    if type(r.get("changed_files_count")) is int and len(files) != r["changed_files_count"]:
        uncertain("(files)", "FILE_LIST_COUNT_MISMATCH")

    all_paths: set[str] = set()
    for index, item in enumerate(files[:MAX_FILES + 1]):
        prefix = f"(file {index + 1})"
        if type(item) is not dict or not _path(item.get("path")):
            uncertain(prefix, "INVALID_PATH_OR_FILE_RECORD")
            continue
        path = item["path"]
        if path in all_paths:
            uncertain(path, "DUPLICATE_PATH")
            continue
        all_paths.add(path)
        if (path in BLOCKED_BASENAMES or
                any(path.startswith(prefix) for prefix in BLOCKED_PREFIXES) or
                path.lower().endswith((".pem", ".p12", ".pfx", ".key"))):
            fail(path, "HIGH_IMPACT_OR_PRIVATE_PATH")
        if not _is_text_path(path):
            uncertain(path, "FILE_TYPE_NOT_ALLOWLISTED")
        status = item.get("status")
        if status not in ("added", "modified", "changed", "renamed", "copied", "removed", "deleted"):
            uncertain(path, "INVALID_NATIVE_CHANGE_STATUS")
        if item.get("head_sha") != head:
            uncertain(path, "FILE_HEAD_UNVERIFIED")
        if item.get("binary") is not False or item.get("is_symlink") is not False:
            uncertain(path, "BINARY_OR_SYMLINK_UNVERIFIED")
        if item.get("patch_complete") is not True:
            uncertain(path, "PATCH_UNAVAILABLE_OR_TRUNCATED")
        patch = item.get("patch")
        if type(patch) is not str or not patch:
            uncertain(path, "PATCH_MISSING")
            patch = ""
        if status in ("removed", "deleted"):
            if item.get("content") not in (None, ""):
                uncertain(path, "DELETED_FILE_HAS_CURRENT_BODY")
            content = ""
        else:
            content = item.get("content")
            if type(content) is not str or item.get("content_head_sha") != head:
                uncertain(path, "CURRENT_BLOB_TEXT_UNVERIFIED")
                content = ""
        for field, value in (("patch", patch), ("content", content)):
            if len(value.encode("utf-8")) > MAX_TEXT_BYTES:
                uncertain(path, f"{field.upper()}_EXCEEDS_SAFE_SIZE")
                continue
            for reason, pattern in KNOWN_SECRET_OR_RESTRICTED_DESIGN:
                if pattern.search(value):
                    fail(path, reason)
        if status == "renamed":
            if not _path(item.get("previous_filename")) or item["previous_filename"] == path:
                uncertain(path, "RENAME_SOURCE_UNVERIFIED")
        if path.startswith("05_CYCLE_NAVIGATOR/site/"):
            if r.get("generated_site_outputs_complete") is not True:
                uncertain(path, "GENERATED_PUBLIC_OUTPUT_UNVERIFIED")

    for field in ("title", "body"):
        value = r.get(field)
        if type(value) is str:
            if len(value.encode("utf-8")) > MAX_TEXT_BYTES:
                uncertain("(conversation)", "PR_TEXT_OVERSIZE")
                continue
            for reason, pattern in KNOWN_SECRET_OR_RESTRICTED_DESIGN:
                if pattern.search(value):
                    fail("(conversation)", reason)

    # A limited matcher cannot establish semantic safety for arbitrary content.
    # The existing owner must still check provenance, current governance, risk,
    # independent review (staged D2) and all native GitHub gates.
    if findings:
        result = "RESTRICTED_CONTENT"
        evidence = findings + unknown
    elif unknown:
        result = "UNKNOWN"
        evidence = unknown
    else:
        result = "NO_RESTRICTED_CONTENT"
        evidence = []
    # Never include matched sensitive strings, source excerpts or hidden values.
    return _result(head, result, evidence, input_hash)

if __name__ == "__main__":
    import sys
    value = json.load(sys.stdin)
    print(json.dumps(scan_pr(value), indent=2, sort_keys=True))
