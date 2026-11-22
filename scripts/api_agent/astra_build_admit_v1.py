"""Pure, fail-closed admission for full-file Astra BUILD_v1 proposals.

No subprocess, network, write, credential, spend, branch, or merge authority.
Source states/allowlists MUST originate from independently reviewed mission
metadata at an authenticated pinned main. An LLM response is never metadata.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from typing import Any

CONTRACT = "ASTRA_BUILD_v1"
SCOPE_CONTRACT = "ASTRA_BUILD_MISSION_SCOPE_v1"
RECEIPT_CONTRACT = "ASTRA_BUILD_ADMISSION_v1"
MAX_FILE_BYTES = 120_000
MAX_TOTAL_BYTES = 400_000
MAX_RAW_JSON_BYTES = 800_000
MAX_FILES = 24
MAX_RATIONALE = 6_000
MAX_RISKS = 16
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MISSION_ID = re.compile(r"ASTRA-[A-Z0-9]+(?:-[A-Z0-9]+){2,11}\Z")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*\Z")
KEY_OR_SECRET = re.compile(
    r"(?:sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{24,}|"
    r"github_pat_[A-Za-z0-9_]{25,}|gh[pousr]_[A-Za-z0-9]{30,}|"
    r"xox[abposr]-[A-Za-z0-9-]{10,}|AKIA[A-Z0-9]{16}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----)"
)
TEXT_SUFFIXES = (".py", ".json", ".jsonl", ".md", ".txt", ".js", ".mjs", ".ts",
                 ".tsx", ".jsx", ".html", ".css", ".yml", ".yaml")
DENY_PREFIXES = (".github/", ".agents/", "00_FMOS/", "00_ARCHIVE_CONTROL/",
                 "research/api_agent/", "03_DAILY_CAPTURE_LOGS/", "secrets/",
                 "vault/", "private/", "config/private/", "data/private/",
                 "08_SOURCE_MATERIAL/private/", "06_RESEARCH_LAB/astra_missions/",
                 "06_RESEARCH_LAB/astra_program_20261116/results/")
DENY_EXACT = frozenset(("AGENTS.md", "CLAUDE.md", ".env", ".npmrc", ".pypirc",
                       "scripts/governance/s1_runtime_contract_v1.py",
                       "scripts/research/owner_astra_mission_v1.py"))
DENY_SEGMENTS = frozenset((".github", ".agents", "secrets", "private", "vault", "round3",
                          "round_3", "credentials", "__pycache__", ".git", "data"))
DENY_FILENAMES = frozenset((
    "agents.md", "claude.md", ".env", ".npmrc", ".pypirc",
    "conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini",
    "sitecustomize.py", "usercustomize.py", "package.json", "package-lock.json",
    "requirements.txt", "requirements-dev.txt"))
DENY_PATH_SUBSTRINGS = ("round3", "round_3", "vault", "secret", "credential")
SCOPE_ALLOW = {
    "M1": (
        "scripts/learning/**", "scripts/cycle_navigator/**",
        "05_CYCLE_NAVIGATOR/site/**", "tests/learning/**",
        "tests/cycle_navigator/**",
    ),
    "M2": (
        "scripts/learning/**", "04_MARKET_LEARNING/handlekompas/contracts/**",
        "scripts/data_ping/public_regime_feed_v1.py",
        "tests/learning/**", "tests/data_ping/**",
    ),
    "M3": (
        "scripts/governance/s1_tick_brief_v1.py",
        "scripts/governance/s1_closure_*.py",
        "tests/governance/**",
        "scripts/api_agent/astra_build_pr_factory_v1.py",
    ),
}
# No string supplied by the model is ever evaluated as a command.
# Each exact command is reviewed source, passed as an argv tuple (no shell).
TEST_COMMANDS = {
    # Dedicated offline/native security smoke. Not in SCOPE_ALLOW and cannot
    # appear in any paid mission or model-admitted BUILD proposal.
    "SMOKE": (("python", "-m", "unittest", "discover", "-s", "tests/smoke", "-v"),),
    # M1 no-secret sandbox is a PREFILTER, never full site/browser proof.
    # Generated dist/Chrome integration is mandatory in output PR native CI,
    # on separate trusted infrastructure with no model-selected commands.
    "M1": (("python", "-m", "pytest", "-q", "tests/learning", "tests/cycle_navigator"),
           ("node", "--test",
             "05_CYCLE_NAVIGATOR/site/tests/browser-startup-negative.test.mjs",
             "05_CYCLE_NAVIGATOR/site/tests/cn-v2-design-data-boundary.test.mjs",
             "05_CYCLE_NAVIGATOR/site/tests/official-compass-freshness.test.mjs",
             "05_CYCLE_NAVIGATOR/site/tests/pullback-pages-run-block.test.mjs",
             "05_CYCLE_NAVIGATOR/site/tests/pullback-research-readback.test.mjs")),
    "M2": (("python", "-m", "pytest", "-q", "tests/learning", "tests/data_ping",
            "-k", "regime_feed or rotation or recovery"),),
    "M3": (("python", "-m", "pytest", "-q", "tests/governance"),),
}

class AdmissionBlocked(ValueError):
    """A non-admitted untrusted proposal. Never recover by widening scope."""

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise AdmissionBlocked(reason)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")

def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    require(len({x for x, _ in pairs}) == len(pairs), "DUPLICATE_JSON_KEY")
    return dict(pairs)

def parse_untrusted(raw: bytes) -> dict:
    require(isinstance(raw, bytes) and len(raw) <= MAX_RAW_JSON_BYTES,
            "PROPOSAL_RAW_BYTES")
    def nonfinite(_: str) -> None:
        raise AdmissionBlocked("NONFINITE_JSON")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                         parse_constant=nonfinite)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise AdmissionBlocked("PROPOSAL_JSON_INVALID") from exc
    require(isinstance(obj, dict), "PROPOSAL_NOT_OBJECT")
    return obj

def safe_path(path: str) -> str:
    require(isinstance(path, str) and len(path) <= 220 and bool(NAME.fullmatch(path)),
            "PATH_FORMAT")
    parts = path.split("/")
    require(len(parts) > 1 and all(p and p not in (".", "..") for p in parts),
            "PATH_TRAVERSAL")
    require(not path.startswith("/") and "\\" not in path and "//" not in path,
            "PATH_TRAVERSAL")
    lowered = path.lower()
    require(path not in DENY_EXACT and not path.startswith(DENY_PREFIXES)
            and parts[-1].lower() not in DENY_FILENAMES
            and not (set(x.lower() for x in parts) & DENY_SEGMENTS)
            and not any(term in lowered for term in DENY_PATH_SUBSTRINGS),
            "PATH_PROTECTED")
    require(path.endswith(TEXT_SUFFIXES), "PATH_NOT_TEXT")
    return path

def _in_scope(path: str, allowed: tuple[str, ...]) -> bool:
    # fnmatch operates on POSIX forward-slash paths; ** is confined by
    # the exact, reviewed prefix patterns in SCOPE_ALLOW, never by model text.
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in allowed)

def verify_scope(scope: dict) -> dict:
    """A higher-privilege caller authenticates this dict against reviewed main."""
    require(isinstance(scope, dict) and set(scope) ==
            {"contract", "mission_id", "main_sha", "test_command_id",
             "allowlist", "source_files", "stage", "previous_repair"}, "SCOPE_SCHEMA")
    require(scope["contract"] == SCOPE_CONTRACT, "SCOPE_CONTRACT")
    mid, main, test_id = (scope[k] for k in
                          ("mission_id", "main_sha", "test_command_id"))
    require(isinstance(mid, str) and MISSION_ID.fullmatch(mid), "SCOPE_MISSION")
    require(isinstance(main, str) and HEX40.fullmatch(main), "SCOPE_MAIN")
    require(test_id in SCOPE_ALLOW and test_id in TEST_COMMANDS,
            "SCOPE_TEST_COMMAND")
    allowed = scope["allowlist"]
    require(isinstance(allowed, list) and allowed and len(allowed) <= 8
            and len(set(allowed)) == len(allowed)
            and set(allowed) <= set(SCOPE_ALLOW[test_id]), "SCOPE_ALLOWLIST")
    stage = scope["stage"]
    require(type(stage) is int and stage in (1, 2), "SCOPE_STAGE")
    previous = scope["previous_repair"]
    if stage == 1:
        require(previous is None, "REPAIR_UNEXPECTED")
    else:
        require(isinstance(previous, dict) and set(previous) ==
                {"mission_id", "stage", "status", "test_receipt_sha256"}
                and previous["mission_id"] == mid and previous["stage"] == 1
                and previous["status"] == "VERIFIED_SANDBOX_TEST_FAILURE"
                and isinstance(previous["test_receipt_sha256"], str)
                and HEX64.fullmatch(previous["test_receipt_sha256"]),
                "REPAIR_EVIDENCE_MISSING")
    sources = scope["source_files"]
    require(isinstance(sources, dict) and 0 < len(sources) <= MAX_FILES,
            "SCOPE_SOURCE_FILES")
    for path, meta in sources.items():
        safe_path(path)
        require(_in_scope(path, tuple(allowed)), "SOURCE_OUTSIDE_SCOPE")
        require(meta is None or
                (isinstance(meta, dict) and set(meta) == {"sha256", "mode"}
                 and meta["mode"] == "100644"
                 and isinstance(meta["sha256"], str)
                 and HEX64.fullmatch(meta["sha256"])), "SOURCE_PREIMAGE")
    return scope

def admit(raw: bytes, scope: dict) -> dict:
    """Validate only, returning a safe manifest and no authority to execute.

    'source_files' is a trusted exact-main manifest. The caller MUST verify
    those original file hashes, filesystem type and Git SHA independently.
    In particular, a model cannot add paths or choose test commands.
    """
    verify_scope(scope)
    obj = parse_untrusted(raw)
    require(set(obj) == {"status", "files", "test_command_id",
                          "rationale", "risks"}, "PROPOSAL_SCHEMA")
    require(obj["status"] in ("BUILD", "ABSTAIN"), "PROPOSAL_STATUS")
    require(obj["test_command_id"] == scope["test_command_id"],
            "MODEL_SELECTED_DIFFERENT_TEST")
    require(isinstance(obj["rationale"], str)
            and len(obj["rationale"]) <= MAX_RATIONALE, "RATIONALE_INVALID")
    risks = obj["risks"]
    require(isinstance(risks, list) and len(risks) <= MAX_RISKS
            and all(isinstance(x, str) and len(x) <= 500 for x in risks),
            "RISKS_INVALID")
    files = obj["files"]
    require(isinstance(files, list) and len(files) <= MAX_FILES,
            "FILES_SCHEMA")
    if obj["status"] == "ABSTAIN":
        require(files == [], "ABSTAIN_WITH_FILES")
    else:
        require(bool(files), "BUILD_WITHOUT_FILES")
    total, manifest, seen = 0, [], set()
    for row in files:
        require(isinstance(row, dict) and set(row) == {"path", "action", "content"},
                "FILE_ROW_SCHEMA")
        path = safe_path(row["path"])
        require(_in_scope(path, tuple(scope["allowlist"]))
                and path in scope["source_files"] and path not in seen,
                "FILE_OUT_OF_SCOPE_OR_DUPLICATED")
        action = row["action"]
        before = scope["source_files"][path]
        require(action in ("create", "modify"), "ACTION_INVALID")
        require((action == "create" and before is None)
                or (action == "modify" and before is not None),
                "ACTION_PREIMAGE_MISMATCH")
        if path.startswith("scripts/governance/s1_closure_"):
            require(path.count("/") == 2 and action == "create",
                    "M3_CLOSURE_CREATE_ONLY")
        # The model may ADD unit tests, never silently change a baseline test
        # or its collection/runner configuration in the PR used for CI proof.
        if path.startswith("tests/"):
            require(action == "create", "TRUSTED_BASELINE_TESTS_READ_ONLY")
        content = row["content"]
        require(isinstance(content, str) and bool(content.strip())
                and not any(((ord(ch) < 32 and ch not in ("\n", "\t"))
                             or ord(ch) == 127) for ch in content),
                "CONTENT_NOT_TEXT")
        try:
            data = content.encode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise AdmissionBlocked("CONTENT_UTF8") from exc
        require(0 < len(data) <= MAX_FILE_BYTES, "FILE_TOO_LARGE")
        require(KEY_OR_SECRET.search(content) is None, "CREDENTIAL_PATTERN")
        total += len(data)
        require(total <= MAX_TOTAL_BYTES, "BUNDLE_TOO_LARGE")
        manifest.append({"path": path, "action": action, "sha256": digest(data),
                         "bytes": len(data), "preimage_sha256":
                         before["sha256"] if before else None})
        seen.add(path)
    return {"contract": RECEIPT_CONTRACT, "status":
            "ABSTAINED" if obj["status"] == "ABSTAIN" else
            "ADMITTED_UNTRUSTED_CODE_TEST_REQUIRED",
            "mission_id": scope["mission_id"], "stage": scope["stage"],
            "main_sha": scope["main_sha"],
            "test_command_id": scope["test_command_id"],
            "proposal_sha256": digest(raw),
            "proposal_bytes": len(raw), "files": sorted(manifest, key=lambda r: r["path"]),
            "total_content_bytes": total, "sandbox_executed": False,
            "merged": False, "paid_authority": False,
            "commands": "FIXED_BY_REVIEWED_CODE_NOT_MODEL"}
