"""Read-only evidence stage classifier for S1 post-merge observations."""

import re
import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _sha(value):
    return isinstance(value, str) and _SHA40.fullmatch(value) is not None


def classify_release_evidence(record):
    """Return an evidence level, never release or trading authorization.

    GitHub identities, URLs and source material must be verified by the caller.
    This code classifies supplied records, not their external authenticity.
    """
    if not isinstance(record, dict) or not _sha(record.get("original_head")):
        return {"stage": "INVALID_INPUT", "authorized": False}
    head = record["original_head"]
    jobs = record.get("required_pr_jobs")
    if not isinstance(jobs, list) or not jobs:
        return {"stage": "CI_NOT_PROVEN", "authorized": False}
    for job in jobs:
        if (not isinstance(job, dict)
                or job.get("head") != head
                or job.get("event") != "pull_request"
                or job.get("status") != "completed"
                or job.get("conclusion") != "success"
                or type(job.get("executed_test_steps")) is not int
                or job["executed_test_steps"] < 1):
            return {"stage": "CI_NOT_PROVEN", "authorized": False}
    if not _sha(record.get("merge_sha")) or not _sha(record.get("main_sha")):
        return {"stage": "CI_ONLY", "authorized": False}
    blobs = record.get("changed_main_blobs")
    if not isinstance(blobs, list) or not blobs:
        return {"stage": "MAIN_NOT_PROVEN", "authorized": False}
    for blob in blobs:
        if (not isinstance(blob, dict) or not blob.get("path")
                or not _sha(blob.get("expected_sha"))
                or blob.get("actual_sha") != blob["expected_sha"]):
            return {"stage": "MAIN_NOT_PROVEN", "authorized": False}
    natural = record.get("natural_consumer")
    if not isinstance(natural, dict):
        return {"stage": "MAIN_READBACK_SUPPLIED", "authorized": False}
    if (natural.get("event") != "natural"
            or not natural.get("run_url")
            or not natural.get("consumer_url")
            or not natural.get("source_id")
            or natural.get("source_id") != natural.get("delivered_source_id")
            or natural.get("clock_eligible") is not True):
        return {"stage": "PRODUCTION_NOT_PROVEN", "authorized": False}
    return {"stage": "PROD_EVIDENCE_SUPPLIED_NEEDS_AUTHENTICATION",
            "authorized": False, "externally_authenticated": False}


def _github(value):
    if not isinstance(value, str):
        return False
    try:
        u = urlparse(value)
    except ValueError:
        return False
    return (u.scheme == "https" and u.netloc == "github.com"
            and u.path.startswith("/Donh91/")
            and not any(s in (".", "..") for s in unquote(u.path).replace(chr(92), "/").split("/")))


def _owner_approval_comment_url(value, repo, pr):
    """Check owner-evidence URL structure; caller MUST verify comment author/body."""
    if not _github(value) or repo != "Donh91/Investering-Framework-Archive-v1":
        return False
    u = urlparse(value)
    allowed_paths = {
        f"/Donh91/Investering-Framework-Archive-v1/pull/{pr}",
        "/Donh91/Investering-Framework-Archive-v1/issues/1156",
    }
    return (u.path in allowed_paths and not u.query and
            re.fullmatch(r"issuecomment-[1-9][0-9]*", u.fragment) is not None)


def _release_sensitive_path(path):
    return (path == "AGENTS.md" or path.startswith(".github/")
            or path.startswith("01_CORE_FRAMEWORK/governance/")
            or path.startswith("00_ARCHIVE_CONTROL/")
            or path.startswith("scripts/governance/s1_")
            or path.startswith("tests/governance/test_s1_")
            or path == "scripts/governance/check_codex_review_finality.py")


def _stamp(value):
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value) is None:
        return None
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)
    except ValueError:
        return None


def _claude_review_is_valid(record, current):
    """Owner-admitted advisory review, NEVER a native GitHub approval or merge permit.

    All *_verified evidence must be independently read back from native GitHub
    and the private Bridge by S1 before this deterministic classifier is called.
    Claimed booleans / supplied hashes have no authentication power here.
    """
    r = record
    v = r.get("claude_review")
    if not isinstance(v, dict):
        return False
    if r.get("native_rules_verified") is not True or r.get("native_approval_required") is not False:
        return False  # unknown or required native approval: fail closed
    if r.get("repo_full_name") != "Donh91/Investering-Framework-Archive-v1":
        return False
    pr = r.get("pr_number")
    cid = v.get("comment_id")
    if type(pr) is not int or pr < 1 or type(cid) is not int or cid < 1:
        return False
    if v.get("comment_url") != (
        f"https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/173#issuecomment-{cid}"
    ):
        return False
    risk_map = {"LOW": "LOW", "HIGH": "HIGH_IMPACT"}
    # MEDIUM has no reviewed custody semantics. Reject it until defined.
    if type(r.get("risk")) is not str:
        return False
    risk = risk_map.get(r["risk"])
    if risk is None:
        return False
    independent = v.get("independence")
    if independent != "INDEPENDENT" and not (risk == "LOW" and independent == "SELF_AUTHORED_DESIGN"):
        return False
    # A caller-supplied LOW label cannot down-classify changed release controls.
    # S1 must independently authenticate the entire native exact-HEAD path list.
    paths = r.get("expected_changed_paths")
    if (not isinstance(paths, list) or not paths
            or any(type(p) is not str or not p.strip() or p != p.strip()
                   or p.startswith("/") or ".." in p.split("/") for p in paths)
            or len(set(paths)) != len(paths)
            or (risk == "LOW" and any(_release_sensitive_path(p) for p in paths))):
        return False
    if risk == "HIGH_IMPACT":
        owner = r.get("high_impact_owner_approval")
        if (not isinstance(owner, dict)
                or owner.get("approved") is not True
                or owner.get("repo") != r["repo_full_name"]
                or type(owner.get("pr")) is not int or owner["pr"] != pr
                or owner.get("head_sha") != current["head"]
                or not _owner_approval_comment_url(owner.get("evidence_url"), r["repo_full_name"], pr)
                or owner.get("evidence_url") == v.get("comment_url")):
            return False
    if (v.get("contract") != "CLAUDE_REVIEW_v1"
            or v.get("verdict") != "APPROVE"
            or v.get("repo") != r["repo_full_name"]
            or type(v.get("pr")) is not int or v.get("pr") != pr
            or v.get("head_sha") != current["head"]
            or v.get("requested_head_sha") != current["head"]
            or v.get("risk_class") != risk
            or any(v.get(k) != current[k] for k in (
                ("head", "policy", "source") +
                (() if r.get("review_requires_current_main") is False else ("main",))))
            or v.get("body_readback_verified") is not True
            or v.get("report_readback_verified") is not True
            or re.fullmatch(r"[a-f0-9]{64}", str(v.get("report_sha256", ""))) is None
            or re.fullmatch(r"[a-f0-9]{64}", str(v.get("body_sha256", ""))) is None):
        return False
    return True


def _changed_test_execution_issue(record, current):
    """IC-1: source-supplied native PR file statuses, not name-only deletion guesses.

    This is advisory, never a GitHub authenticator. The S1 caller MUST read
    the changed-file status list from the original PR at the exact current HEAD.
    Absent or conflicting status for a changed Python test fails closed.
    Removed tests require no impossible execution receipt; rename destinations do.
    """
    paths = record.get("expected_changed_paths")
    if not isinstance(paths, list):
        # RP1 / Fable P5 D1: a missing census must not skip IC-1 when PR jobs are offered as evidence.
        if "release_process" in record:  # legacy records unchanged (would break 20 legacy fixtures)
            return "CHANGED_TEST_PATH_CENSUS_MISSING"
        return None  # Existing general/Claude path-census gates remain separate.
    # Untrusted JSON can contain nested lists/objects. Reject per-PR before set(paths).
    # The native path census is independently authenticated by S1, never by this input.
    if any(type(p) is not str or not p or p != p.strip()
           or p.startswith("/") or ".." in p.split("/") for p in paths):
        return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
    rp1 = record.get("release_process") == RP1
    tests = [p for p in paths if _is_changed_test_path(p, rp1)]
    entries = record.get("changed_file_statuses")
    # RP1 / Fable P5 D3: a test renamed out of test discovery silently drops coverage.
    renamed_out = isinstance(entries, list) and any(
        isinstance(e, dict) and type(e.get("previous_filename")) is str
        and _is_changed_test_path(e["previous_filename"], rp1) and type(e.get("path")) is str
        and not _is_changed_test_path(e["path"], rp1) for e in entries)
    if not tests and not renamed_out:
        return None
    if (record.get("changed_file_statuses_source") != "GITHUB_PR_FILES"
            or record.get("changed_file_statuses_head_sha") != current.get("head")
            or not isinstance(entries, list)):
        return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
    statuses = {}
    for entry in entries:
        if not isinstance(entry, dict):
            return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
        path = entry.get("path")
        status = entry.get("status")
        exists = entry.get("head_exists")
        if (type(path) is not str or path not in paths or path in statuses
                or type(status) is not str
                or status not in ({"added", "modified", "renamed", "copied", "removed", "deleted"}
                                  | ({"changed"} if rp1 else set()))  # RP1 05 / G1: file-mode change
                or type(exists) is not bool):
            return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
        if status in {"removed", "deleted"}:
            if exists:
                return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
        elif not exists:
            return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
        if status == "renamed":
            previous = entry.get("previous_filename")
            if type(previous) is not str or not previous or previous == path:
                return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
        statuses[path] = status
    if set(statuses) != set(paths):
        return "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"
    if renamed_out:
        return "CHANGED_TEST_RENAMED_OUT_OF_DISCOVERY"

    required_jobs = []
    for name in record.get("required_pr_job_names") or []:
        required_jobs.extend(
            job for job in record.get("pr_jobs") or []
            if isinstance(job, dict) and job.get("name") == name
        )
    for path in tests:
        if statuses[path] in {"removed", "deleted"}:
            continue
        dotted = path[:-3].replace("/", ".") if path.endswith(".py") else None
        found = False
        for job in required_jobs:
            if _scope_covers(job, path):
                found = True
                break
            ids = job.get("executed_test_ids")
            if not isinstance(ids, list):
                continue
            # Native unittest discovery -s tests/learning without -t uses
            # module IDs relative to its discovery root. Bind the root to the
            # native CI job, never trust an unscoped basename match.
            scope = job.get("test_discovery_root")
            scoped = None
            if (type(scope) is str and scope and scope == scope.strip("/")
                    and ".." not in scope.split("/") and path.startswith(scope + "/")):
                scoped = path[len(scope) + 1:-3].replace("/", ".")
            for test_id in ids:
                if type(test_id) is not str:
                    continue
                if (test_id == path or test_id.startswith(path + "::")
                        or (dotted is not None and (test_id == dotted or test_id.startswith(dotted + ".")))
                        or (scoped is not None and
                            (test_id == scoped or test_id.startswith(scoped + ".")))):
                    found = True
                    break
            if found:
                break
        if not found:
            return "CHANGED_TESTS_NOT_EXECUTED"
    return None

# ---------------------------------------------------------------------------
# S1 Release Process v1 (RP1) - Grok proposal 2026-11-12, advisory and opt-in.
# Opt-in with record["release_process"] == "S1_RP_V1". Without it every legacy
# disposition is unchanged; only the additive `release_action` output exists.
# Nothing here authenticates input, grants authority or returns authorized=True.
# ---------------------------------------------------------------------------
RP1 = "S1_RP_V1"
RP1_LOW_CLASSES = ("DOCS_ONLY", "LOW_CODE")
_RP1_DOC_SUFFIXES = (".md", ".txt", ".rst")
_RP1_JS_TEST_SUFFIXES = (".test.mjs", ".test.js", ".test.cjs", ".test.ts", ".spec.mjs", ".spec.js", ".spec.ts")
_RP1_RESTRICTED_SEGMENTS = {"secrets", "secret", "credentials", "credential", "wallet", "wallets",
                            "orders", "payments", "payment", "vault", "private"}
_RP1_RESTRICTED_PREFIXES = ("research/api_agent/", "scripts/api_agent/", "tests/api_agent/",
                            "scripts/billing/", "scripts/payment/", "scripts/paid/")
_RP1_GOVERNANCE_PREFIXES = (".github/", ".agents/", "00_ARCHIVE_CONTROL/", "00_FMOS/",
                            "01_CORE_FRAMEWORK/governance/", "01_CORE_FRAMEWORK/architecture/",
                            "scripts/governance/", "tests/governance/", "scripts/security/",
                            "tests/security/", "07_PROMPTS_AND_AGENTS/", "schemas/")
_RP1_GOVERNANCE_EXACT = {"AGENTS.md", "CLAUDE.md", "requirements.txt", "requirements-dev.txt",
                         "pyproject.toml", "setup.cfg", "pytest.ini", "conftest.py", "tests/conftest.py",
                         "package.json", "package-lock.json"}
_RP1_DATA_PREFIXES = ("02_DATA_PING/", "05_CYCLE_NAVIGATOR/", "08_SOURCE_MATERIAL/",
                      "06_RESEARCH_LAB/forward_tests/", "06_RESEARCH_LAB/compass_research_engine_v1/",
                      "03_WEEKLY_OPERATIONS/", "04_MARKET_LEARNING/master_monday/")
_RP1_LOW_CODE_PREFIXES = ("scripts/", "tests/", "06_RESEARCH_LAB/", "04_RESEARCH_LAB/", "research/",
                          "04_MARKET_LEARNING/", "09_ARCHIVE_INBOX/")
_RP1_ORDER = ("DOCS_ONLY", "LOW_CODE", "UNCLASSIFIED_HIGH", "PUBLIC_DATA_INTEGRITY",
              "GOVERNANCE_WORKFLOW", "PRIVATE_PAID_AUTHORITY")


def _is_changed_test_path(p, rp1=False):
    if type(p) is not str:
        return False
    name = p.rsplit("/", 1)[-1]
    if ((p.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py")))
            or p.endswith(_RP1_JS_TEST_SUFFIXES)):
        return True
    # RP1 addendum (Fable M7 residual), RP1 records only: nested conftest.py and shell tests also
    # change what CI runs. Legacy/#2088 semantics (conftest = fixture, no execution) are unchanged.
    return rp1 and (name == "conftest.py"
                    or (name.endswith(".sh") and (name.startswith("test_") or "/tests/" in "/" + p)))


def _scope_covers(job, path):
    """Step-scope execution evidence: a non-collect-only, unmasked pytest/unittest/node step
    whose path arguments (read from the workflow at the exact HEAD) cover the changed test.
    `pytest -q <dir>` prints no test IDs, so per-ID evidence is unobtainable for those steps."""
    scopes = job.get("executed_scope_paths")
    if job.get("executed_scope_unmasked") is not True or not isinstance(scopes, list):
        return False
    if path.endswith(".sh"):
        return False  # a pytest/node dir scope does not execute shell tests; require an exact executed ID
    # Unittest -s with a narrow -p does NOT run all tests under -s. A complete
    # filename-selector census from the exact executed CI step is required for
    # directory scopes. A caller-supplied directory alone cannot prove execution.
    patterns = job.get("executed_scope_discovery_patterns")
    patterns_complete = job.get("executed_scope_patterns_complete") is True
    for s in scopes:
        if (type(s) is not str or not s or s in (".", "./") or s.startswith("/")
                or ".." in s.split("/") or s != s.strip()):
            continue
        s = s.rstrip("/")
        if path == s:
            return True  # exact test FILE was named by the executed step
        if path.startswith(s + "/") and patterns_complete and isinstance(patterns, list) and patterns:
            import fnmatch
            name = path.rsplit("/", 1)[-1]
            if all(type(p) is str and bool(p) and "/" not in p and "\\" not in p
                   and ".." not in p for p in patterns):
                if any(fnmatch.fnmatchcase(name, p) for p in patterns):
                    return True
    return False


def _rp1_path_class(path):
    if type(path) is not str or not path or path.startswith("/") or ".." in path.split("/") or path != path.strip():
        return None
    low = path.lower()
    segments = set(low.split("/"))
    name = low.rsplit("/", 1)[-1]
    if (segments & _RP1_RESTRICTED_SEGMENTS or low.startswith(_RP1_RESTRICTED_PREFIXES)
            or name == ".env" or name.startswith(".env.")):
        return "PRIVATE_PAID_AUTHORITY"
    if path in _RP1_GOVERNANCE_EXACT or path.startswith(_RP1_GOVERNANCE_PREFIXES) or _release_sensitive_path(path):
        return "GOVERNANCE_WORKFLOW"
    if (path.startswith(_RP1_DATA_PREFIXES) or name.startswith("latest")
            or ("forecast" in low and path.startswith("04_MARKET_LEARNING/"))):
        return "PUBLIC_DATA_INTEGRITY"
    if "/" not in path and not path.endswith(_RP1_DOC_SUFFIXES):
        return "GOVERNANCE_WORKFLOW"  # root pointers/config (LATEST_*.json etc.)
    if path.endswith(_RP1_DOC_SUFFIXES):
        return "DOCS_ONLY"
    if path.startswith(_RP1_LOW_CODE_PREFIXES):
        return "LOW_CODE"
    return "UNCLASSIFIED_HIGH"


def derive_release_class(changed_files):
    """Most restrictive class over every changed path AND every rename source.
    `changed_files`: GitHub PR files API shape [{path|filename, status, previous_filename?}].
    Returns None for a missing/malformed census (fail closed)."""
    if not isinstance(changed_files, list) or not changed_files:
        return None
    worst = 0
    for f in changed_files:
        if not isinstance(f, dict):
            return None
        names = [f.get("path", f.get("filename"))]
        if f.get("status") == "renamed" or f.get("previous_filename") is not None:
            names.append(f.get("previous_filename"))
        for n in names:
            c = _rp1_path_class(n)
            if c is None:
                return None
            worst = max(worst, _RP1_ORDER.index(c))
    return _RP1_ORDER[worst]


_RP1_RULESET_TARGETS = ("branch", "push", "tag", "repository")


def _rp1_ref_include_matches(pattern, default_branch):
    """Fail-closed include matcher for refs/heads/main: may over-match, never under-match."""
    if pattern == "~ALL":
        return True
    if pattern == "~DEFAULT_BRANCH":
        return default_branch in ("main", None)  # unknown default branch => assume it is main
    if type(pattern) is not str:
        return True
    if not any(ch in pattern for ch in "*?["):
        return pattern in ("refs/heads/main", "main")
    import fnmatch
    return fnmatch.fnmatchcase("refs/heads/main", pattern) or fnmatch.fnmatchcase("main", pattern)


def _rp1_ref_exclude_matches(pattern, default_branch):
    """Fail-closed exclude matcher: only an exact, unambiguous exclusion of main is honoured;
    wildcard excludes are ignored (could only under-match the census)."""
    if pattern == "~DEFAULT_BRANCH":
        return default_branch == "main"
    return pattern == "refs/heads/main"


def _rp1_ruleset_applies(rs, default_branch):
    """Return (applies: bool, basis: str) for one NON-disabled ruleset, fail closed to applies=True."""
    target = rs.get("target")
    if target == "tag":
        return False, "TARGET_TAG"
    if target not in ("branch", "push", "repository"):
        return True, "TARGET_UNKNOWN_ASSUMED_APPLIES"
    if target in ("push", "repository"):
        return True, "TARGET_" + target.upper() + "_APPLIES_TO_ALL_REFS"
    if rs.get("detail_http") != 200 or not isinstance(rs.get("conditions"), dict):
        return True, "CONDITIONS_UNREADABLE_ASSUMED_APPLIES"
    cond = rs["conditions"]
    if set(cond) - {"ref_name"}:
        return True, "NON_REF_CONDITIONS_ASSUMED_APPLIES"  # e.g. org repository_name/property conditions
    ref = cond.get("ref_name")
    if (not isinstance(ref, dict) or not isinstance(ref.get("include"), list)
            or not isinstance(ref.get("exclude", []), list)):
        return True, "CONDITIONS_MALFORMED_ASSUMED_APPLIES"
    if any(_rp1_ref_exclude_matches(x, default_branch) for x in ref.get("exclude", [])):
        return False, "CONDITIONS_EXCLUDE_MAIN"
    if any(_rp1_ref_include_matches(x, default_branch) for x in ref["include"]):
        return True, "CONDITIONS_INCLUDE_MAIN"
    return False, "CONDITIONS_DO_NOT_INCLUDE_MAIN"


def rp1_rule_census_report(reads):
    """RP1 patch 05: tiered native rule census. Never raises; returns a dict with status OK|RECHECK.

    Tier (a) PRIMARY (must be readable): GET /repos/{o}/{r}/branches/main (protected, protection.enabled)
      + GET /repos/{o}/{r}/rulesets?includes_parents=true (all pages) + GET /rulesets/{id} detail
      (target/conditions) for every NON-disabled ruleset + GET /repos/{o}/{r} default_branch/owner type.
    Tier (b) OPTIONAL corroboration: GET /repos/{o}/{r}/rules/branches/main. Any non-200 (400 connector
      rejection, 401/403/404/5xx, None) => effective_rules_endpoint UNAVAILABLE and the census proceeds on (a).
      A 200 that is malformed, or readable and disagreeing with (a), => RECHECK (never READY).
    An active ruleset that applies (or whose applicability cannot be proven absent) and a protected branch are
    BINDING census entries => the caller escalates (RP1_ACTIVE_RULES_REQUIRE_NATIVE_COMPLIANCE); they are never
    ignored. A 400/403 is never converted into proof of zero rules; no bypass is ever assumed."""
    rep = {"status": "RECHECK", "census": None, "effective_rules_endpoint": "NOT_EVALUATED",
           "org_rulesets": "UNVERIFIED", "reason": None}

    def fail(reason):
        rep["reason"] = reason
        return rep
    if not isinstance(reads, dict) or reads.get("branch_http") != 200 or reads.get("rulesets_http") != 200:
        return fail("PRIMARY_READ_FAILED")
    if type(reads.get("protected")) is not bool or reads.get("rulesets_pages_complete") is not True:
        return fail("PRIMARY_INCOMPLETE")
    if reads.get("rulesets_includes_parents") is False:
        return fail("PARENT_RULESETS_EXCLUDED")  # API default is true; an explicit false hides org/enterprise rulesets
    owner_type = reads.get("repo_owner_type")
    if owner_type == "User":
        rep["org_rulesets"] = "NOT_APPLICABLE_USER_OWNED_REPO"
    elif owner_type == "Organization":
        rep["org_rulesets"] = "INCLUDED_VIA_INCLUDES_PARENTS"
    else:
        rep["org_rulesets"] = "UNVERIFIED_OWNER_TYPE_INCLUDES_PARENTS_DEFAULT_TRUE"
    default_branch = reads.get("default_branch") if type(reads.get("default_branch")) is str else None
    rulesets = reads.get("rulesets")
    if not isinstance(rulesets, list):
        return fail("RULESETS_MALFORMED")
    census = []
    for rs in rulesets:
        if not isinstance(rs, dict) or rs.get("enforcement") not in ("active", "evaluate", "disabled"):
            return fail("RULESET_MALFORMED")
        if "target" in rs and rs["target"] not in _RP1_RULESET_TARGETS:
            return fail("RULESET_TARGET_UNKNOWN")
        if rs["enforcement"] == "disabled":
            continue  # disabled rulesets enforce nothing (GitHub docs); no detail read needed
        if "target" in rs or "conditions" in rs or "detail_http" in rs:
            applies, basis = _rp1_ruleset_applies(rs, default_branch)
            supplied = rs.get("applies_to_main")
            if type(supplied) is bool and supplied != applies and not basis.endswith("ASSUMED_APPLIES"):
                return fail("SUPPLIED_APPLIES_TO_MAIN_CONTRADICTS_CONDITIONS")
        else:  # pre-05 record shape: an unverifiable caller claim can only widen, never narrow, the census
            applies, basis = True, "LEGACY_SHAPE_ASSUMED_APPLIES"
            if rs.get("applies_to_main") is not True and type(rs.get("applies_to_main")) is not bool:
                return fail("RULESET_MALFORMED")
        if not applies:
            continue
        census.append({"binding": rs["enforcement"] == "active", "enforcement": rs["enforcement"],
                       "source": "ruleset", "id": rs.get("id"), "applies_basis": basis})
    if reads["protected"] is False:
        if reads.get("protection_enabled") is not False:
            return fail("PROTECTION_FLAGS_CONTRADICT")
    elif reads.get("protection_detail_http") == 200 and isinstance(reads.get("protection_requirements"), list):
        census += [{"binding": True, "enforcement": "active", "source": "branch_protection", "rule": str(x)}
                   for x in reads["protection_requirements"]]
        if not reads["protection_requirements"]:
            census.append({"binding": True, "enforcement": "active", "source": "branch_protection", "rule": "PROTECTED"})
    else:
        # Protection EXISTS but its requirements cannot be read (classic detail needs admin): do not loop on
        # RECHECK and never treat as absent - it is a binding, unverifiable rule => owner escalation.
        census.append({"binding": True, "enforcement": "active", "source": "branch_protection",
                       "rule": "REQUIREMENTS_UNREADABLE"})
    eff_http = reads.get("effective_rules_http")
    if eff_http != 200:
        rep["effective_rules_endpoint"] = "UNAVAILABLE"
    else:
        eff = reads.get("effective_rules")
        if not isinstance(eff, list):
            return fail("EFFECTIVE_RULES_MALFORMED")
        eff_ids = set()
        for rule in eff:
            if not isinstance(rule, dict) or not isinstance(rule.get("type"), str) or type(rule.get("ruleset_id")) is not int:
                return fail("EFFECTIVE_RULES_MALFORMED")
            eff_ids.add(rule["ruleset_id"])
        active_ids = {c.get("id") for c in census if c["binding"] and c["source"] == "ruleset"}
        has_binding = any(c["binding"] for c in census)
        if eff_ids != active_ids:
            rep["effective_rules_endpoint"] = "READ_DISAGREES_WITH_PRIMARY"
            if not has_binding:
                return fail("EFFECTIVE_RULES_CONTRADICT_PRIMARY")  # fail closed: RECHECK, never READY
        else:
            rep["effective_rules_endpoint"] = "READ_AGREES_WITH_PRIMARY"
        census += [{"binding": True, "enforcement": "active", "source": "rules_branches_main",
                    "id": rule["ruleset_id"], "rule": rule["type"]} for rule in eff]
    rep.update(status="OK", census=census)
    return rep


def rp1_rule_census(reads):
    """Native rule census per IC-2 v1.1 + Archive #2089 recipe + RP1 patch 05 tiering.
    Returns (census, enforced) or None (=> RECHECK). See rp1_rule_census_report for the contract."""
    rep = rp1_rule_census_report(reads)
    if rep["status"] != "OK":
        return None
    return rep["census"], True


def rp1_merge_state(layers):
    """IC-2 v1.1: (A) optional local git merge-tree exit, (B) GitHub REST view. 403/null/contradiction
    is 'unknown_recheck', never clean and never conflict. Returns clean|conflicting|rule_blocked|unknown_recheck."""
    if not isinstance(layers, dict):
        return "unknown_recheck"
    http, mergeable, mstate = layers.get("rest_http"), layers.get("rest_mergeable"), layers.get("rest_mergeable_state")
    if http != 200:
        b = "unknown_recheck"
    elif mergeable is True and mstate == "clean":
        b = "clean"
    elif mergeable is True and mstate in ("blocked", "behind", "unstable", "has_hooks"):
        b = "rule_blocked"
    elif mergeable is False and mstate == "dirty":
        b = "conflicting"
    else:
        b = "unknown_recheck"
    exit_code = layers.get("git_merge_tree_exit")
    a = {0: "clean", 1: "conflicting", None: b}.get(exit_code, "unknown_recheck") if type(exit_code) in (int, type(None)) else "unknown_recheck"
    if a == b:
        return b
    if b == "rule_blocked" and a == "clean":
        return "rule_blocked"
    return "unknown_recheck"


_RP1_ACTION_BY_REASON = {
    "CURRENT_BINDING_MISSING": "RECHECK", "EVALUATION_BINDING_CHANGED": "RECHECK",
    "WRITER_LEASE_ACTIVE_OR_UNKNOWN": "RECHECK", "MERGEABILITY_COMPUTING_OR_RULE_BLOCKED": "RECHECK",
    "MERGEABILITY_UNKNOWN_RECHECK": "RECHECK", "REQUIRED_RULE_CENSUS_MISSING": "RECHECK",
    "RULE_CENSUS_UNAVAILABLE": "RECHECK", "REQUIRED_JOB_CENSUS_MISSING": "RECHECK",
    "CI_PENDING_RECHECK": "RECHECK", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED": "RECHECK",
    "MERGE_MAIN_READBACK_UNVERIFIED": "RECHECK", "RP1_PATH_CENSUS_MISSING": "RECHECK",
    "ORIGINAL_BRANCH_CONFLICT": "HOLD", "BLOCKING_FINDING_OPEN_OR_UNKNOWN": "HOLD",
    "SOURCE_OR_SCIENCE_REQUIREMENT_UNMET": "HOLD", "CURRENT_PR_TEST_EXECUTION_UNPROVEN": "HOLD",
    "REQUIRED_CI_FAILED": "HOLD", "CHANGED_TESTS_NOT_EXECUTED": "HOLD",
    "REQUIRED_INDEPENDENT_APPROVAL_MISSING_OR_STALE": "HOLD", "REVIEW_MAIN_DRIFT_UNVERIFIED": "HOLD",
    "RISK_CLASSIFICATION_MISSING": "HOLD", "HIGH_IMPACT_PATH_MARKED_LOW": "HOLD",
    "RP1_PRIVACY_CHECK_MISSING": "HOLD", "RP1_DRAFT": "HOLD", "RP1_LANE_INVALID": "HOLD",
    "RP1_EVIDENCE_MISMATCH": "HOLD",
    "PLATFORM_ACTION_DENIED": "ESCALATE_OWNER", "REQUIRED_RULES_NOT_ENFORCED": "ESCALATE_OWNER",
    "RP1_ACTIVE_RULES_REQUIRE_NATIVE_COMPLIANCE": "ESCALATE_OWNER",
    "OWNER_RELEASE_MANDATE_UNVERIFIED": "ESCALATE_OWNER", "REVIEW_POLICY_UNKNOWN": "ESCALATE_OWNER",
    "INDEPENDENT_REVIEWER_IDENTITY_ABSENT": "ESCALATE_OWNER", "PHYSICAL_REVIEW_REQUIRED": "ESCALATE_OWNER",
    "RP1_NOT_ELIGIBLE_UNATTENDED": "ESCALATE_OWNER", "CLOSED_WITHOUT_SUPERSESSION_PROOF": "ESCALATE_OWNER",
}


def rp1_release_action(disposition, reason, record, terminal=False):
    """Map a disposition to ONE operational action. READY only for READY_TO_MERGE; unknown
    reasons fail closed to HOLD. A RECHECK repeated 3+ times on the same evidence escalates."""
    if disposition == "READY_TO_MERGE":
        return "READY"
    if disposition in ("MERGED_VERIFIED", "CLOSED_SUPERSEDED"):
        return "DONE"
    if disposition == "INDEPENDENT_RECOVERY_UNVERIFIED":
        action = "ESCALATE_OWNER"
    elif reason.startswith("S1_GENERAL_"):
        action = "HOLD"
    else:
        action = _RP1_ACTION_BY_REASON.get(reason, "HOLD")
    if reason == "CURRENT_PR_TEST_EXECUTION_UNPROVEN" and any(
            isinstance(j, dict) and j.get("status") in ("queued", "in_progress", "waiting", "pending", "requested")
            for j in (record.get("pr_jobs") or [])):
        action = "RECHECK"
    if action == "RECHECK" and type(record.get("consecutive_rechecks")) is int and record["consecutive_rechecks"] >= 3:
        action = "ESCALATE_OWNER"
    if terminal and action in ("HOLD", "RECHECK"):
        action = "ESCALATE_OWNER"
    return action


def _rp1_gate(r, current):
    """RP1 opt-in gate for an OPEN PR. Returns (code, reason, requirement, owner) or None, plus class.
    Strictly additive except one bounded relaxation: DOCS_ONLY may carry
    source_science_gate == NOT_APPLICABLE_BY_PATH (applied by the caller below)."""
    lane = r.get("release_lane")
    if lane not in ("UNATTENDED_S1", "OWNER_DIRECTED"):
        return ("INTERNAL_REPAIRABLE", "RP1_LANE_INVALID", "release_lane UNATTENDED_S1 or OWNER_DIRECTED", "EXISTING_PR_OWNER"), None
    files = r.get("changed_file_statuses")
    paths = r.get("expected_changed_paths")
    if (r.get("changed_file_statuses_source") != "GITHUB_PR_FILES"
            or r.get("changed_file_statuses_head_sha") != current["head"]
            or not isinstance(files, list) or not isinstance(paths, list) or not paths
            or any(type(p) is not str for p in paths) or len(set(paths)) != len(paths)
            or any(not isinstance(f, dict) for f in files)
            or sorted(f.get("path") for f in files if type(f.get("path")) is str) != sorted(paths)
            or len(files) != len(paths)
            # RP1 05 / G3: a truncated (unpaginated) PR-files read is internally consistent but incomplete.
            # Bind it to GET /pulls/{n} `changed_files` read at the same exact HEAD; >3000 is unlistable.
            or type(r.get("pr_changed_files_count")) is not int
            or r.get("pr_changed_files_count_head_sha") != current["head"]
            or r["pr_changed_files_count"] != len(paths) or r["pr_changed_files_count"] > 3000):
        return ("INTERNAL_REPAIRABLE", "RP1_PATH_CENSUS_MISSING",
                "Complete native exact-HEAD PR files census (path/status/previous_filename) equal to expected_changed_paths"
                " and to GET /pulls/{n}.changed_files at the same HEAD",
                "EXISTING_PR_OWNER"), None
    cls = derive_release_class(files)
    if cls is None:
        return ("INTERNAL_REPAIRABLE", "RP1_PATH_CENSUS_MISSING", "Well-formed changed path census", "EXISTING_PR_OWNER"), None
    low = cls in RP1_LOW_CLASSES
    if r.get("risk") == "LOW" and not low:
        return ("SOURCE_OR_SCIENCE_GATE", "HIGH_IMPACT_PATH_MARKED_LOW",
                "Path-derived class " + cls + " is never LOW", "EXISTING_PR_OWNER"), cls
    if lane == "UNATTENDED_S1" and not low:
        return ("EXTERNAL_DEPENDENCY", "RP1_NOT_ELIGIBLE_UNATTENDED",
                "Owner-directed exact-HEAD release for class " + cls, "REPOSITORY_OWNER"), cls
    if r.get("draft") is not False:
        return ("INTERNAL_REPAIRABLE", "RP1_DRAFT", "Non-draft PR", "EXISTING_PR_OWNER"), cls
    if lane == "UNATTENDED_S1":
        m = r.get("owner_mandate")
        if (not isinstance(m, dict) or m.get("source") != "AGENTS.md#0.2c" or m.get("effective_on_main") is not True
                or not _sha(m.get("agents_blob_sha")) or m.get("agents_blob_sha") != current["policy"]
                or r.get("owner_authorized") is not True):
            return ("EXTERNAL_DEPENDENCY", "OWNER_RELEASE_MANDATE_UNVERIFIED",
                    "Effective merged bounded policy bound to current policy blob", "REPOSITORY_OWNER"), cls
    computed = rp1_rule_census(r.get("native_rule_reads"))
    if computed is None:
        return ("EXTERNAL_DEPENDENCY", "RULE_CENSUS_UNAVAILABLE",
                "Branch status + complete ruleset pages (protected branch needs readable detail)", "REPOSITORY_POLICY_OWNER"), cls
    if any(rule["binding"] for rule in computed[0]):
        return ("EXTERNAL_DEPENDENCY", "RP1_ACTIVE_RULES_REQUIRE_NATIVE_COMPLIANCE",
                "Active binding rule: native compliance (e.g. native approval) required", "REPOSITORY_POLICY_OWNER"), cls
    if (r.get("rule_census") != computed[0] or r.get("required_rules_enforced") is not True
            or r.get("native_rules_verified") not in (None, True)):
        return ("INTERNAL_REPAIRABLE", "RP1_EVIDENCE_MISMATCH", "Supplied rule census equals native-read census", "EXISTING_PR_OWNER"), cls
    ms = rp1_merge_state(r.get("merge_layers"))
    if ms == "conflicting":
        return ("MERGE_CONFLICT", "ORIGINAL_BRANCH_CONFLICT", "Clean tested original PR integration", "EXISTING_PR_OWNER"), cls
    if ms != "clean":
        return ("EXTERNAL_DEPENDENCY", "MERGEABILITY_UNKNOWN_RECHECK" if ms == "unknown_recheck" else "MERGEABILITY_COMPUTING_OR_RULE_BLOCKED",
                "Fresh native mergeability; 403/null/contradiction is never clean or conflict", "GITHUB_PLATFORM"), cls
    if r.get("merge_state") != ms:
        return ("INTERNAL_REPAIRABLE", "RP1_EVIDENCE_MISMATCH", "Supplied merge_state equals layered native state", "EXISTING_PR_OWNER"), cls
    lease = r.get("writer_lease")
    reads = lease.get("head_reads") if isinstance(lease, dict) else None
    if ("active_writer_lease" not in r or r["active_writer_lease"] not in (False, None)
            or type(r["active_writer_lease"]) not in (bool, type(None))
            or not isinstance(lease, dict)
            or lease.get("basis") != "EXPECTED_HEAD_MERGE_AND_STABLE_HEAD"
            or not isinstance(reads, list) or len(reads) < 2 or any(h != current["head"] for h in reads)
            or lease.get("foreign_active_leases") != 0 or type(lease.get("foreign_active_leases")) is not int):
        return ("EXTERNAL_DEPENDENCY", "WRITER_LEASE_ACTIVE_OR_UNKNOWN",
                "Two stable exact-HEAD reads, zero foreign S1 lease receipts, expected-head merge", "EXISTING_LEASE_OWNER"), cls
    census = r.get("pr_run_census")
    if (not isinstance(census, dict) or census.get("complete") is not True
            or type(census.get("pending")) is not int or type(census.get("failed")) is not int
            or census.get("head") != current["head"]
            or not isinstance(census.get("job_names"), list)
            or not isinstance(r.get("required_pr_job_names"), list)
            or sorted(set(map(str, census["job_names"]))) != sorted(set(map(str, r["required_pr_job_names"])))):
        return ("CI_NOT_EXECUTED", "REQUIRED_JOB_CENSUS_MISSING",
                "Complete exact-HEAD pull_request run census (client-side head filter, all pages)", "EXISTING_CI_OWNER"), cls
    if census["pending"] > 0:
        return ("CI_NOT_EXECUTED", "CI_PENDING_RECHECK", "Queued/in-progress exact-HEAD runs must complete", "EXISTING_CI_OWNER"), cls
    if census["failed"] > 0:
        return ("CI_NOT_EXECUTED", "REQUIRED_CI_FAILED", "Every exact-HEAD pull_request run concluded success", "EXISTING_CI_OWNER"), cls
    if lane == "UNATTENDED_S1":
        pc = r.get("privacy_check")
        if (not isinstance(pc, dict) or pc.get("head") != current["head"]
                or pc.get("result") != "NO_RESTRICTED_CONTENT"
                or pc.get("method") != "S1_DIFF_SCAN_V1"):
            return ("SOURCE_OR_SCIENCE_GATE", "RP1_PRIVACY_CHECK_MISSING",
                    "Exact-HEAD public/private boundary check of the full diff", "EXISTING_PR_OWNER"), cls
    if r.get("review_requires_current_main") is False:
        drift = r.get("main_drift")
        review_main = None
        if isinstance(r.get("claude_review"), dict):
            review_main = r["claude_review"].get("main")
        if isinstance(r.get("review"), dict) and r["review"].get("main"):
            review_main = r["review"].get("main")
        touched = drift.get("touched_paths") if isinstance(drift, dict) else None
        pr_names = set(paths) | {f.get("previous_filename") for f in files if f.get("previous_filename")}
        if (not isinstance(drift, dict) or drift.get("complete") is not True
                or drift.get("from_main") != review_main or not _sha(review_main)
                or drift.get("to_main") != current["main"] or not isinstance(touched, list)
                or any(type(t) is not str for t in touched) or pr_names & set(touched)
                or (touched and derive_release_class([{"path": t, "status": "modified"} for t in touched])
                    not in RP1_LOW_CLASSES + ("PUBLIC_DATA_INTEGRITY",))):
            return ("REVIEW_REQUIRED_BY_POLICY", "REVIEW_MAIN_DRIFT_UNVERIFIED",
                    "Main drift since review is complete, disjoint from PR paths and touches no governance/private path",
                    "EXISTING_REVIEW_OWNER"), cls
    return None, cls


def classify_pr_disposition(record):
    """Classify supplied evidence for ONE PR; never grant release authority.

    No supplied boolean, URL or hash authenticates an issuer. The existing
    operator must obtain all inputs from current native sources, authenticate
    custody separately and enforce platform rules immediately before merging.
    READY_TO_MERGE and MERGED_VERIFIED are advisory dispositions of the supplied
    record, not authenticated claims or an executable merge permission.
    Missing telemetry is local to this PR. No I/O, provider call or writer.
    """
    r = record if isinstance(record, dict) else {}
    current = r.get("current") if isinstance(r.get("current"), dict) else {}
    evaluated = r.get("evaluated") if isinstance(r.get("evaluated"), dict) else {}
    rp1_class_holder = [None]

    def finish(disposition, reason, requirement, owner, trigger):
        # Observation clocks cannot create a new receipt on every tick. A
        # changed disposition/reason (e.g. expired proof) IS a material change.
        fields = ("current", "evaluated", "risk", "platform_denied", "merged", "merge",
                  "expected_changed_paths", "changed_file_statuses", "changed_file_statuses_source",
                  "changed_file_statuses_head_sha", "production", "closed", "supersession",
                  "active_writer_lease", "merge_state", "required_rules_enforced", "rule_census",
                  "unresolved_p0_p1", "source_science_gate", "required_pr_job_names",
                  "pr_jobs", "independent_review_required", "review", "review_requires_current_main",
                  "claude_review", "native_rules_verified", "native_approval_required",
                  "repo_full_name", "pr_number", "independent_reviewer_available",
                  "high_impact_owner_approval",
                  "physical_site_review_required", "physical_site_review_passed",
                  "owner_physical_review_waiver", "recovery", "release_assessment", "recovery_max_age_seconds",
                  "safepoint_source", "owner_authorized",
                  "s1_general_preflight_required", "s1_general_preflight",
                  "release_process", "release_lane", "draft", "owner_mandate", "native_rule_reads",
                  "merge_layers", "writer_lease", "pr_run_census", "privacy_check", "main_drift",
                  "pr_changed_files_count", "pr_changed_files_count_head_sha")
        def material_value(value):
            if isinstance(value, dict):
                return {k: material_value(v) for k, v in value.items()
                        if k not in ("observed_at_utc", "updated_at", "updated_at_utc",
                                     "checked_at_utc", "last_seen_at_utc")}
            if isinstance(value, list):
                return [material_value(v) for v in value]
            return value
        material = {k: material_value(r[k]) for k in fields if k in r}
        try:
            encoded = json.dumps([material, disposition, reason], sort_keys=True,
                                 separators=(",", ":"), allow_nan=False)
        except (TypeError, ValueError):
            encoded = json.dumps([current.get("head"), disposition, reason], default=str)
        fingerprint = hashlib.sha256(encoded.encode()).hexdigest()
        same = r.get("previous_fingerprint") == fingerprint
        touches = r.get("material_touches", 0)
        blocked = disposition not in ("READY_TO_MERGE", "MERGED_VERIFIED", "CLOSED_SUPERSEDED")
        terminal = blocked and type(touches) is int and touches >= 4
        out = {
            "release_action": rp1_release_action(disposition, reason, r, terminal),
            "release_class": rp1_class_holder[0],
            "contract": "S1_PR_DISPOSITION_ADVISORY_V1",
            "disposition": disposition, "reason": reason,
            "binding_requirement": requirement, "responsible_owner": owner,
            "reactivation_trigger": trigger, "other_prs_may_continue": True,
            "authorized": False, "externally_authenticated": False,
            "evidence_status": "SUPPLIED_RECORD_REQUIRES_NATIVE_AUTHENTICATION",
            "fingerprint": fingerprint, "emit_receipt": not same,
            "terminal_until_material_change": blocked and type(touches) is int and touches >= 4,
            "reactivated": bool(r.get("previous_fingerprint")) and not same,
        }
        if r.get("release_process") == RP1 and "native_rule_reads" in r:
            meta = rp1_rule_census_report(r.get("native_rule_reads"))
            out["rule_census_meta"] = {k: meta[k] for k in ("status", "effective_rules_endpoint", "org_rulesets", "reason")}
        return out

    def blocked(code, reason, requirement, owner="EXISTING_PR_OWNER", trigger="Current native evidence satisfying the named requirement"):
        return finish(code, reason, requirement, owner, trigger)

    if not r or not all(_sha(current.get(k)) for k in ("head", "main", "policy", "source")):
        return blocked("INTERNAL_REPAIRABLE", "CURRENT_BINDING_MISSING", "Current exact HEAD/main/policy/source SHA census")
    # Opt-in adapter for the existing S1 General source-bound preflight.
    # Existing historical callers remain compatible. A declared S1 General
    # release cannot silently omit the supplementary evidence guard.
    general_required = r.get("s1_general_preflight_required")
    if "s1_general_preflight" in r and general_required is not True:
        return blocked("EXTERNAL_DEPENDENCY", "S1_GENERAL_OPT_IN_UNVERIFIED",
                       "Explicit opt-in and complete native current evidence")
    if general_required is not None and type(general_required) is not bool:
        return blocked("EXTERNAL_DEPENDENCY", "S1_GENERAL_OPT_IN_INVALID",
                       "Exact boolean S1 General preflight requirement")
    if general_required is True:
        from scripts.governance.s1_general_release_evidence_v1 import classify as classify_general
        snapshot = r.get("s1_general_preflight")
        advisory = classify_general(snapshot)
        if advisory["status"] != "EVIDENCE_COMPLETE_RECHECK_NATIVE":
            return blocked("EXTERNAL_DEPENDENCY",
                           "S1_GENERAL_" + advisory["reason"],
                           "Current authenticated owner, source, rule, review and executed-test evidence")
        if (snapshot["head"] != current["head"]
                or snapshot["main"] != current["main"]
                or snapshot["high_impact"] != (r.get("risk") == "HIGH")
                or r.get("risk") not in ("LOW", "HIGH")):
            return blocked("EXTERNAL_DEPENDENCY", "S1_GENERAL_NATIVE_BINDING_MISMATCH",
                           "Exact PR HEAD/main and path-derived risk agreement")
        # A caller-selected LOW risk label is not sufficient for source/workflow
        # changes. This is a conservative path falsifier, not a GitHub census:
        # the original caller MUST independently authenticate the complete
        # changed paths against the current PR head before using this advice.
        changed_paths = r.get("expected_changed_paths")
        if (not isinstance(changed_paths, list) or not changed_paths
                or any(type(p) is not str or not p.strip() or p != p.strip()
                       or p.startswith("/") or ".." in p.split("/") for p in changed_paths)
                or len(set(changed_paths)) != len(changed_paths)):
            return blocked("EXTERNAL_DEPENDENCY", "S1_GENERAL_NATIVE_PATH_CENSUS_MISSING",
                           "Complete native exact-head changed paths")
        if r["risk"] == "LOW" and any(
                _release_sensitive_path(p) for p in changed_paths):
            return blocked("SOURCE_OR_SCIENCE_GATE", "HIGH_IMPACT_PATH_MARKED_LOW",
                           "Existing source/workflow governance and independent recovery gates")
        jobs = r.get("pr_jobs")
        names = r.get("required_pr_job_names")
        if (not isinstance(names, list) or not names
                or any(type(n) is not str or not n.strip() for n in names)
                or len(set(names)) != len(names)
                or not isinstance(jobs, list)):
            return blocked("CI_NOT_EXECUTED", "S1_GENERAL_NATIVE_CI_MANIFEST_MISSING",
                           "Policy-derived unique required PR jobs and exact HEAD")
        observed = set()
        for name in names:
            matches = [j for j in jobs if isinstance(j, dict) and j.get("name") == name]
            if (len(matches) != 1
                    or matches[0].get("head") != current["head"]
                    or matches[0].get("event") != "pull_request"
                    or matches[0].get("status") != "completed"
                    or matches[0].get("conclusion") != "success"):
                return blocked("CI_NOT_EXECUTED", "S1_GENERAL_NATIVE_JOB_NOT_EXECUTED",
                               "Exact-head completed native pull_request job")
            step_ids = matches[0].get("executed_test_ids")
            if (not isinstance(step_ids, list) or not step_ids
                    or any(type(t) is not str or not t.strip() or t != t.strip() for t in step_ids)
                    or len(set(step_ids)) != len(step_ids)):
                return blocked("CI_NOT_EXECUTED", "S1_GENERAL_NATIVE_TEST_IDS_UNVERIFIED",
                               "Native run/job/step bound substantive executed test IDs")
            observed.update(step_ids)
        if observed != set(snapshot["executed_tests"]):
            return blocked("CI_NOT_EXECUTED", "S1_GENERAL_TEST_PROOF_MISMATCH",
                           "Exact same named executed tests in native jobs and S1 preflight")

    if r.get("platform_denied") is True:
        return blocked("EXTERNAL_DEPENDENCY", "PLATFORM_ACTION_DENIED", "GitHub/platform approval enforcement", "PLATFORM_CONTROL_OWNER", "Authorized platform control explicitly permits the exact action; no alternate-route evasion")
    if r.get("merged") is True:
        merge = r.get("merge") if isinstance(r.get("merge"), dict) else {}
        paths = r.get("expected_changed_paths")
        blobs = merge.get("blobs")
        valid = (merge.get("head") == current["head"] and _sha(merge.get("sha"))
                 and merge.get("observed_main") == current["main"]
                 and merge.get("main_contains_merge") is True
                 and _sha(merge.get("rollback_sha"))
                 and isinstance(paths, list) and bool(paths)
                 and all(isinstance(p, str) and bool(p) for p in paths)
                 and len(set(paths)) == len(paths)
                 and isinstance(blobs, list) and len(blobs) == len(paths))
        if valid:
            valid = (all(isinstance(b, dict) and isinstance(b.get("path"), str)
                         and _sha(b.get("expected_sha"))
                         and b.get("actual_sha") == b["expected_sha"] for b in blobs)
                     and {b["path"] for b in blobs} == set(paths))
        if not valid:
            return blocked("EXTERNAL_DEPENDENCY", "MERGE_MAIN_READBACK_UNVERIFIED", "Exact merged HEAD, ancestry, complete changed blobs and rollback anchor", trigger="Native merge/main/changed-blob readback succeeds")
        production = r.get("production") or {}
        pending = not (isinstance(production, dict) and production.get("natural") is True
                       and production.get("source") == current["source"]
                       and production.get("fresh") is True and production.get("public_readback") is True)
        out = finish("MERGED_VERIFIED", "POST_FIX_OBSERVATION" if pending else "NATURAL_PRODUCTION_EVIDENCE_SUPPLIED",
                     "Exact merge and main readback", "EXISTING_DOMAIN_OWNER",
                     "Next natural source-to-consumer observation" if pending else "New material source or code change")
        out["production_observation_pending"] = pending
        return out
    if r.get("closed") is True:
        replacement = r.get("supersession") or {}
        if isinstance(replacement, dict) and _github(replacement.get("url")) and replacement.get("verified") is True and _sha(replacement.get("commit")):
            return finish("CLOSED_SUPERSEDED", "EXACT_REPLACEMENT_EVIDENCE_SUPPLIED", "Original owner verified replacement", "EXISTING_PR_OWNER", "New contrary evidence")
        return blocked("EXTERNAL_DEPENDENCY", "CLOSED_WITHOUT_SUPERSESSION_PROOF", "Closed PR is not proof of resolved defect")
    if any(evaluated.get(k) != current[k] for k in ("head", "main", "policy", "source")):
        return blocked("INTERNAL_REPAIRABLE", "EVALUATION_BINDING_CHANGED", "Revalidate changed HEAD/main/policy/source before merge")
    rp1_on = "release_process" in r
    if rp1_on:
        if r.get("release_process") != RP1:
            return blocked("INTERNAL_REPAIRABLE", "RP1_LANE_INVALID", "Exact release_process S1_RP_V1 or field absent")
        gate, rp1_class_holder[0] = _rp1_gate(r, current)
        if gate:
            return blocked(*gate)
    if r.get("active_writer_lease") is not False and not (
            rp1_on and "active_writer_lease" in r and r["active_writer_lease"] is None
            and isinstance(r.get("writer_lease"), dict)
            and r["writer_lease"].get("basis") == "EXPECTED_HEAD_MERGE_AND_STABLE_HEAD"):
        # RP1 05 (D4): None = no lease registry exists; the RP1 gate above already required the
        # optimistic-concurrency evidence (2 stable HEAD reads + expected-head merge). Legacy unchanged.
        return blocked("EXTERNAL_DEPENDENCY", "WRITER_LEASE_ACTIVE_OR_UNKNOWN", "Single writer and exact HEAD ownership", "EXISTING_LEASE_OWNER", "Authenticated lease release or expiry and fresh HEAD check")
    state = r.get("merge_state")
    if state == "conflicting":
        return blocked("MERGE_CONFLICT", "ORIGINAL_BRANCH_CONFLICT", "Clean tested original PR integration", trigger="Original branch conflict repaired, new exact-head CI and review")
    if state != "clean":
        return blocked("EXTERNAL_DEPENDENCY", "MERGEABILITY_COMPUTING_OR_RULE_BLOCKED", "Native mergeability and platform rule census", "GITHUB_PLATFORM", "Completed GitHub computation or satisfied named platform requirement")
    census = r.get("rule_census")
    if not isinstance(census, list) or any(not isinstance(rule, dict) or type(rule.get("binding")) is not bool for rule in census):
        return blocked("EXTERNAL_DEPENDENCY", "REQUIRED_RULE_CENSUS_MISSING", "Current applicable binding-rule census, explicitly empty when none", "REPOSITORY_POLICY_OWNER")
    if r.get("required_rules_enforced") is not True or any(rule["binding"] and rule.get("enforcement") != "active" for rule in census):
        return blocked("EXTERNAL_DEPENDENCY", "REQUIRED_RULES_NOT_ENFORCED", "Binding required rules must be active", "REPOSITORY_POLICY_OWNER", "Required protection demonstrably active, without bypass")
    if r.get("unresolved_p0_p1") is not False:
        return blocked("INTERNAL_REPAIRABLE", "BLOCKING_FINDING_OPEN_OR_UNKNOWN", "No unresolved concrete P0/P1")
    if r.get("owner_authorized") is not True:
        return blocked("EXTERNAL_DEPENDENCY", "OWNER_RELEASE_MANDATE_UNVERIFIED", "Valid owner authorization for this release scope", "REPOSITORY_OWNER")
    if r.get("source_science_gate") != "PASS" and not (
            "release_process" in r and rp1_class_holder[0] == "DOCS_ONLY"
            and r.get("source_science_gate") == "NOT_APPLICABLE_BY_PATH"):
        return blocked("SOURCE_OR_SCIENCE_GATE", "SOURCE_OR_SCIENCE_REQUIREMENT_UNMET", "Original source/science contract", "EXISTING_SOURCE_OWNER")
    names = r.get("required_pr_job_names")
    jobs = r.get("pr_jobs")
    if not isinstance(names, list) or not names or not all(isinstance(x, str) and x for x in names) or len(set(names)) != len(names) or not isinstance(jobs, list):
        return blocked("CI_NOT_EXECUTED", "REQUIRED_JOB_CENSUS_MISSING", "Policy-derived complete required PR job census", "EXISTING_CI_OWNER")
    for name in names:
        matches = [j for j in jobs if isinstance(j, dict) and j.get("name") == name]
        if len(matches) != 1 or any(matches[0].get(k) != v for k, v in {
            "head": current["head"], "event": "pull_request", "status": "completed", "conclusion": "success"}.items()) or type(matches[0].get("executed_test_steps")) is not int or matches[0]["executed_test_steps"] < 1:
            return blocked("CI_NOT_EXECUTED", "CURRENT_PR_TEST_EXECUTION_UNPROVEN", "Exact-head PR-event required jobs with actual executed test steps", "EXISTING_CI_OWNER")
    if type(r.get("independent_review_required")) is not bool:
        return blocked("REVIEW_REQUIRED_BY_POLICY", "REVIEW_POLICY_UNKNOWN", "Current domain/platform review policy", "EXISTING_REVIEW_OWNER")
    if r["independent_review_required"]:
        review = r.get("review") or {}
        # A policy may permit reuse across an unrelated main advance, but not
        # across head, source or policy changes. Missing policy stays strict.
        review_keys = ("head", "policy", "source")
        if r.get("review_requires_current_main") is not False:
            review_keys += ("main",)
        native_ok = (isinstance(review, dict) and review.get("state") == "APPROVED"
                     and review.get("independent") is True
                     and all(review.get(k) == current[k] for k in review_keys))
        if not native_ok and not _claude_review_is_valid(r, current):
            # Claude's Audit-02b: a proven absent reviewer identity is an OWNER
            # resolution, never an excuse to remove a binding approval gate.
            if r.get("independent_reviewer_available") is False:
                return blocked("REVIEW_REQUIRED_BY_POLICY", "INDEPENDENT_REVIEWER_IDENTITY_ABSENT",
                               "Independent approval required but no non-author native reviewer exists",
                               "REPOSITORY_OWNER",
                               "Owner supplies independent reviewer or admissible source-bound Claude advisory review with native-rule verification")
            return blocked("REVIEW_REQUIRED_BY_POLICY", "REQUIRED_INDEPENDENT_APPROVAL_MISSING_OR_STALE",
                           "Native approval or qualified exact-head Claude review under owner policy",
                           "EXISTING_REVIEW_OWNER")
    changed_test_issue = _changed_test_execution_issue(r, current)
    if changed_test_issue:
        return blocked("CI_NOT_EXECUTED", changed_test_issue,
                       "Native exact-HEAD changed-test status and actually executed tests, "
                       "excluding removed sources and using rename destinations",
                       "EXISTING_CI_OWNER")
    if r.get("physical_site_review_required") is True and r.get("physical_site_review_passed") is not True and r.get("owner_physical_review_waiver") is not True:
        return blocked("EXTERNAL_DEPENDENCY", "PHYSICAL_REVIEW_REQUIRED", "Applicable physical SITE review policy", "EXISTING_SITE_OWNER")
    if r.get("risk") not in ("LOW", "HIGH"):
        return blocked("INTERNAL_REPAIRABLE", "RISK_CLASSIFICATION_MISSING", "Changed-file/domain risk classification")
    if r["risk"] == "HIGH":
        recovery = r.get("recovery") or {}
        if not isinstance(recovery, dict) or recovery.get("technical_recovery") is not True:
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "TECHNICAL_RECOVERY_MISSING", "High-impact independently verified recovery", "EXISTING_RECOVERY_CUSTODIAN")
        if recovery.get("source") != current["source"]:
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_SOURCE_STALE", "Recovery bound to exact intended source", "EXISTING_RECOVERY_CUSTODIAN")
        if not all(_sha(recovery.get(k)) for k in ("snapshot", "tree", "workflow")) or not re.fullmatch(r"[a-f0-9]{64}", str(recovery.get("manifest_sha256", ""))) or not _github(recovery.get("receipt_url")):
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_IDENTITY_INCOMPLETE", "Snapshot/tree/workflow/manifest and native receipt binding", "EXISTING_RECOVERY_CUSTODIAN")
        observed, now = _stamp(recovery.get("observed_at_utc")), _stamp(r.get("now_utc"))
        limit = r.get("recovery_max_age_seconds")
        if observed is None or now is None or type(limit) is not int or not 1 <= limit <= 86400 or not 0 <= (now - observed).total_seconds() <= limit:
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_FRESHNESS_UNPROVEN", "Policy freshness at use, never future-dated or clock-only attestation", "EXISTING_RECOVERY_CUSTODIAN")
        # The native receipt never grants release permission. Its false flag
        # must remain false even when separate custody/release evidence exists.
        if recovery.get("native_release_permission") is not False:
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "NATIVE_TECHNICAL_RECEIPT_AUTHORITY_INVALID", "Preserve native technical receipt release_permission=false", "EXISTING_RECOVERY_CUSTODIAN")
        for field, reason in (("independent_custody", "CUSTODY_UNATTESTED"), ("separation", "DESTRUCTIVE_AUTHORITY_SEPARATION_UNVERIFIED")):
            if recovery.get(field) is not True:
                return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", reason, "Independent source-bound custody and release proof", "EXISTING_RECOVERY_CUSTODIAN")
        assessment = r.get("release_assessment") or {}
        if not isinstance(assessment, dict) or assessment.get("release_permission") is not True:
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_RELEASE_NOT_PERMITTED", "Separate independent aggregated release assessment, not native receipt mutation", "EXISTING_RECOVERY_CUSTODIAN")
        if (assessment.get("independent") is not True
                or not _github(assessment.get("attestation_url"))
                or assessment.get("attestation_url") == recovery["receipt_url"]
                or any(assessment.get(k) != current[k] for k in ("head", "main", "policy", "source"))
                or any(assessment.get(k) != recovery[k] for k in ("snapshot", "manifest_sha256"))):
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "RELEASE_ASSESSMENT_BINDING_UNVERIFIED", "Independent issuer and exact PR/main/policy/source/snapshot/manifest binding", "EXISTING_RECOVERY_CUSTODIAN")
        assessment_time = _stamp(assessment.get("observed_at_utc"))
        if assessment_time is None or not 0 <= (now - assessment_time).total_seconds() <= limit:
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "RELEASE_ASSESSMENT_STALE", "Current independent release assessment at use", "EXISTING_RECOVERY_CUSTODIAN")
        if r.get("safepoint_source") != current["source"]:
            return blocked("INDEPENDENT_RECOVERY_UNVERIFIED", "IMMEDIATE_SAFEPOINT_MISSING", "Verified immediate safepoint for exact source", "EXISTING_SOURCE_OWNER")
    return finish("READY_TO_MERGE", "CURRENT_REQUIRED_EVIDENCE_SUPPLIED", "Authenticated owner mandate and fresh native enforcement still required", "EXISTING_AUTHORIZED_INTEGRATOR", "Any change of HEAD/main/policy/source or binding evidence requires reevaluation")


def classify_pr_batch(records):
    """Existing S1 can evaluate independent candidates without global HOLD."""
    if not isinstance(records, list):
        raise ValueError("PR record list required")
    return [{"input_index": index, **classify_pr_disposition(record)}
            for index, record in enumerate(records)]


if __name__ == "__main__":
    # Finite read-only invocation by the existing S1/operator, not a scheduler
    # or unattended integrator. JSON goes to stdout; no repository writes.
    import sys
    payload = json.load(sys.stdin)
    print(json.dumps({"contract": "S1_PR_DISPOSITION_BATCH_ADVISORY_V1",
                      "authorized": False, "externally_authenticated": False,
                      "results": classify_pr_batch(payload)}, sort_keys=True))
