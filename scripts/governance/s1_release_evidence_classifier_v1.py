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
    risk_map = {"LOW": "LOW", "MEDIUM": "MEDIUM", "HIGH": "HIGH_IMPACT"}
    if type(r.get("risk")) is not str:
        return False
    risk = risk_map.get(r["risk"])
    if risk is None:
        return False
    independent = v.get("independence")
    if independent != "INDEPENDENT" and not (risk == "LOW" and independent == "SELF_AUTHORED_DESIGN"):
        return False
    if risk == "HIGH_IMPACT" and r.get("high_impact_owner_approval") is not True:
        return False
    if (v.get("contract") != "CLAUDE_REVIEW_v1"
            or v.get("verdict") != "APPROVE"
            or v.get("repo") != r["repo_full_name"]
            or v.get("pr") != pr
            or v.get("head_sha") != current["head"]
            or v.get("requested_head_sha") != current["head"]
            or v.get("risk_class") != risk
            or v.get("body_readback_verified") is not True
            or v.get("report_readback_verified") is not True
            or re.fullmatch(r"[a-f0-9]{64}", str(v.get("report_sha256", ""))) is None
            or re.fullmatch(r"[a-f0-9]{64}", str(v.get("body_sha256", ""))) is None):
        return False
    return True


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

    def finish(disposition, reason, requirement, owner, trigger):
        # Observation clocks cannot create a new receipt on every tick. A
        # changed disposition/reason (e.g. expired proof) IS a material change.
        fields = ("current", "evaluated", "risk", "platform_denied", "merged", "merge",
                  "expected_changed_paths", "production", "closed", "supersession",
                  "active_writer_lease", "merge_state", "required_rules_enforced", "rule_census",
                  "unresolved_p0_p1", "source_science_gate", "required_pr_job_names",
                  "pr_jobs", "independent_review_required", "review", "review_requires_current_main",
                  "claude_review", "native_rules_verified", "native_approval_required",
                  "repo_full_name", "pr_number", "independent_reviewer_available",
                  "high_impact_owner_approval",
                  "physical_site_review_required", "physical_site_review_passed",
                  "owner_physical_review_waiver", "recovery", "release_assessment", "recovery_max_age_seconds",
                  "safepoint_source", "owner_authorized",
                  "s1_general_preflight_required", "s1_general_preflight")
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
        return {
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
                p == "AGENTS.md" or p.startswith(".github/workflows/")
                or p.startswith("01_CORE_FRAMEWORK/governance/")
                or p.startswith("00_ARCHIVE_CONTROL/")
                for p in changed_paths):
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
    if r.get("active_writer_lease") is not False:
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
    if r.get("source_science_gate") != "PASS":
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
    if r.get("physical_site_review_required") is True and r.get("physical_site_review_passed") is not True and r.get("owner_physical_review_waiver") is not True:
        return blocked("EXTERNAL_DEPENDENCY", "PHYSICAL_REVIEW_REQUIRED", "Applicable physical SITE review policy", "EXISTING_SITE_OWNER")
    if r.get("risk") not in ("LOW", "MEDIUM", "HIGH"):
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
