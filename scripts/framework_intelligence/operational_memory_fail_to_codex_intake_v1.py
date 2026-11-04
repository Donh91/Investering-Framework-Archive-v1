#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FORBIDDEN = [
    "market gates",
    "model weights",
    "canonical authority",
    "portfolio logic",
    "API budget",
    "new policy semantics",
]

ALLOWED_SCOPE = [
    ".github/workflows/framework-learning-supervisor.yml",
    "00_FMOS/OPERATIONAL_MEMORY_AND_RETRIEVAL_v1.md",
    "scripts/framework_intelligence/operational_memory_v1.py",
    "scripts/framework_intelligence/operational_memory_post_production_audit_v1.py",
    "scripts/framework_intelligence/operational_memory_fail_to_codex_intake_v1.py",
    "scripts/orchestration/build_framework_handoff_manifest.py",
    "tests/framework_intelligence/test_operational_memory_v1.py",
    "tests/framework_intelligence/test_operational_memory_post_production_audit_v1.py",
    "tests/framework_intelligence/test_operational_memory_fail_to_codex_intake_v1.py",
]


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalized_failures(audit: dict[str, Any]) -> list[str]:
    return sorted({str(x).strip() for x in audit.get("failures", []) if str(x).strip()})


def failure_fingerprint(audit: dict[str, Any]) -> str:
    failures = normalized_failures(audit)
    raw = json.dumps(failures, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def candidate_prefix(audit: dict[str, Any]) -> str:
    return f"codex-operational-memory-audit-{failure_fingerprint(audit)}"


NOTICE_PREFIX = "OPMEM_NATIVE_NOTICE_v1 "


def notice_payload(audit: dict[str, Any], run_id: int) -> dict[str, Any]:
    """A notification receipt, never proof that repair or recovery succeeded."""
    if type(run_id) is not int or run_id <= 0:
        raise ValueError("invalid_native_run_id")
    status = audit.get("status")
    if status not in {"FAIL", "PASS", "WARN"}:
        raise ValueError("invalid_audit_notice_status")
    return {"run_id": run_id, "status": status,
            "failure_fingerprint": failure_fingerprint(audit) if status == "FAIL" else None}


def native_notice(comment: dict[str, Any], run: dict[str, Any], repository: str) -> dict[str, Any] | None:
    """Authenticate provenance from native API objects, never marker text alone.

    Caller obtains the comment and referenced run from this repository's API.
    This trusts the existing GitHub Actions principal, not arbitrary issue users.
    A compromised trusted workflow is outside this notification-only boundary.
    """
    user = comment.get("user") or {}
    if user.get("login") != "github-actions[bot]" or user.get("type") != "Bot":
        return None
    if comment.get("updated_at") != comment.get("created_at"):
        return None
    try:
        first = comment["body"].splitlines()[0]
        if not first.startswith(NOTICE_PREFIX):
            return None
        payload = json.loads(first[len(NOTICE_PREFIX):])
        if set(payload) != {"run_id", "status", "failure_fingerprint"}:
            return None
        run_id = payload["run_id"]
        if type(run_id) is not int or run_id <= 0 or run.get("id") != run_id:
            return None
        if (run.get("path") != ".github/workflows/framework-learning-supervisor.yml"
                or run.get("head_branch") != "main"
                or run.get("event") not in {"schedule", "workflow_dispatch", "workflow_run"}
                or run.get("status") != "completed"
                or run.get("html_url") != f"https://github.com/{repository}/actions/runs/{run_id}"):
            return None
        created = datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00"))
        started = datetime.fromisoformat(run["run_started_at"].replace("Z", "+00:00"))
        ended = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
        if not started <= created <= ended:
            return None
        fingerprint = payload["failure_fingerprint"]
        if payload["status"] == "FAIL":
            if (not isinstance(fingerprint, str) or len(fingerprint) != 16
                    or any(c not in "0123456789abcdef" for c in fingerprint)):
                return None
        elif payload["status"] not in {"PASS", "WARN"} or fingerprint is not None:
            return None
        return payload
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def notification_action(audit: dict[str, Any], latest_notice: dict[str, Any] | None,
                        *, census_complete: bool) -> str:
    """Clock/source-HEAD churn cannot reactivate the same failure notice."""
    if not census_complete:
        return "NOTICE_EVIDENCE_UNAVAILABLE"
    status = audit.get("status")
    if status == "FAIL":
        if (latest_notice and latest_notice.get("status") == "FAIL"
                and latest_notice.get("failure_fingerprint") == failure_fingerprint(audit)):
            return "UNCHANGED_FAILURE_NOOP"
        return "PUBLISH_FAILURE"
    if status in {"PASS", "WARN"}:
        return "RECOVERY_ALREADY_NOTIFIED" if latest_notice and latest_notice.get("status") in {"PASS", "WARN"} else "PUBLISH_RECOVERY"
    return "NOTICE_EVIDENCE_UNAVAILABLE"


def maturation_dispatch_required(route_result: dict[str, Any]) -> bool:
    """Only first delivery. Durable pending intake is also read by natural runs.

    Caller must commit/read back a newly created candidate BEFORE dispatch.
    A failed dispatch leaves intake pending; it is never recorded as an ACK.
    """
    return (route_result.get("created") is True
            and route_result.get("reason") == "FAIL_ROUTED_TO_BOUNDED_CODEX_INTAKE"
            and bool(route_result.get("candidate_id")) and bool(route_result.get("path")))


def intake_paths(repo: Path, prefix: str) -> list[Path]:
    root = repo / "research/codex/intake"
    if not root.exists():
        return []
    return sorted(p for p in root.rglob(f"{prefix}*.json") if p.is_file())


def completion_exists(repo: Path, candidate_id: str) -> bool:
    return (repo / "research/codex/completions" / f"{candidate_id}.json").exists()


def pending_candidate(repo: Path, prefix: str) -> tuple[str, Path] | None:
    for path in intake_paths(repo, prefix):
        data = read_json(path, {})
        cid = str(data.get("candidate_id") or path.stem)
        if cid.startswith(prefix) and not completion_exists(repo, cid):
            return cid, path
    return None


def candidate_id_for(audit: dict[str, Any], repo: Path) -> str:
    prefix = candidate_prefix(audit)
    base = f"{prefix}-v1"
    base_path = next((p for p in intake_paths(repo, prefix) if p.stem == base), None)
    if base_path is None:
        return base
    if not completion_exists(repo, base):
        return base
    head = str(audit.get("source_head_sha") or "unknown")[:10]
    return f"{prefix}-{head}-v1"


def submitted_parts(audit: dict[str, Any]) -> tuple[str, str, str]:
    raw = str(audit.get("generated_at_utc") or now_iso())
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.now(timezone.utc)
    return str(dt.year), f"{dt.month:02d}", raw


def build_candidate(audit: dict[str, Any], candidate_id: str, submitted_at: str) -> dict[str, Any]:
    failures = normalized_failures(audit)
    head = str(audit.get("source_head_sha") or "UNKNOWN")
    failure_text = "; ".join(failures) if failures else "unspecified post-production audit failure"
    audit_ref = "research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT.json"
    return {
        "contract": "CODEX_RESEARCH_CANDIDATE_v1",
        "candidate_id": candidate_id,
        "status": "SUBMITTED",
        "title": "Repair Operational Memory post-production audit failure",
        "summary": (
            "Bounded code-remediation candidate generated automatically because the Operational Memory "
            "post-production audit blocked memory reuse. Restore PASS/WARN without weakening audit, authority, "
            "staleness or provenance gates."
        ),
        "submitted_at_utc": submitted_at,
        "source_issue": "[AUTO] Operational Memory production audit failure",
        "finding_key": "OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT_FAIL",
        "requested_priority": "EXPEDITED",
        "authority_boundary": "CODE_REMEDIATION_ONLY",
        "requires_framework_owner_authority": False,
        "evidence": [
            {"kind": "AUDIT", "ref": audit_ref, "why": f"Audit status FAIL with: {failure_text}"},
            {"kind": "SOURCE_HEAD", "ref": head, "why": "Exact main state against which the failing audit was generated."},
            {
                "kind": "WORKFLOW",
                "ref": ".github/workflows/framework-learning-supervisor.yml",
                "why": "Owner workflow that generated and enforced the failing audit.",
            },
        ],
        "problem_statement": (
            f"Operational Memory reuse is blocked by its post-production audit on main `{head}`. "
            f"Observed failures: {failure_text}."
        ),
        "objective": (
            "Reproduce the exact Operational Memory audit failure on the cited main state, implement the smallest "
            "bounded code fix inside allowed_change_scope, preserve all authority and stale-memory firewalls, and "
            "restore a deterministic PASS or WARN production-shape audit."
        ),
        "reproduction": (
            "Read the cited audit and source HEAD; run the Framework Learning Supervisor validation stack, harvest "
            "Operational Memory, run deterministic preflight, then run operational_memory_post_production_audit_v1.py "
            "against the production-shaped outputs and reproduce at least one recorded failure before changing code."
        ),
        "methodology": {
            "baseline_readbacks": [audit_ref, ".github/workflows/framework-learning-supervisor.yml"],
            "reproduction_steps": [
                "Check out the exact source_head_sha from the audit.",
                "Run existing Operational Memory and post-production audit tests before changes.",
                "Reproduce the recorded audit failure using deterministic production-shaped inputs.",
            ],
            "smallest_change_first": True,
            "deterministic_test_before_after": True,
            "negative_test": "Prove stale/removed memory stays quarantined and all authority booleans remain false.",
            "fallback_if_gate_fails": "Stop without broadening scope; leave memory reuse blocked and escalate to framework owner authority only if required.",
        },
        "allowed_change_scope": list(ALLOWED_SCOPE),
        "forbidden_changes": list(REQUIRED_FORBIDDEN),
        "outputs": [
            "bounded code-remediation PR",
            "passing deterministic Operational Memory tests",
            "PASS/WARN production-shape post-production audit evidence",
        ],
        "acceptance_tests": {
            "positive": [
                "Operational Memory and post-production audit unit tests pass.",
                "Production-shape audit returns PASS or WARN.",
                "memory_reuse_allowed is true only when audit status is not FAIL.",
            ],
            "negative": [
                "DRIFTED/REMOVED memories remain excluded from reusable_prior_work.",
                "No canonical, portfolio, automatic-promotion or automatic-skill authority becomes true.",
                "No test, threshold or FAIL gate is weakened merely to obtain a passing result.",
            ],
        },
        "post_fix_gate": "CI_PLUS_ONE_PRODUCTION_SHAPE_RUN",
        "runtime_readback": [
            "The repaired audit binds to the current main source_head_sha.",
            "The next production-shaped audit is PASS or WARN and memory_reuse_allowed is true.",
        ],
        "authority": {
            "code_remediation_only": True,
            "framework_state_change": False,
            "portfolio_action": False,
            "automatic_merge": False,
        },
        "resources": [
            audit_ref,
            "00_FMOS/OPERATIONAL_MEMORY_AND_RETRIEVAL_v1.md",
            "scripts/framework_intelligence/operational_memory_v1.py",
            "scripts/framework_intelligence/operational_memory_post_production_audit_v1.py",
        ],
        "automatic_origin": {
            "contract": "OPERATIONAL_MEMORY_FAIL_TO_CODEX_INTAKE_v1",
            "failure_fingerprint": failure_fingerprint(audit),
            "source_head_sha": head,
            "dedupe_policy": "ONE_PENDING_CANDIDATE_PER_FAILURE_FINGERPRINT; NEW_RECURRENCE_ONLY_AFTER_PRIOR_COMPLETION",
        },
    }


def route(repo: Path, audit_path: Path) -> dict[str, Any]:
    audit = read_json(audit_path, {})
    if audit.get("contract") != "OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT_v1":
        return {"created": False, "candidate_id": None, "path": None, "reason": "AUDIT_MISSING_OR_INVALID"}
    if audit.get("status") != "FAIL":
        return {"created": False, "candidate_id": None, "path": None, "reason": "AUDIT_NOT_FAIL"}

    prefix = candidate_prefix(audit)
    pending = pending_candidate(repo, prefix)
    if pending:
        cid, path = pending
        return {
            "created": False,
            "candidate_id": cid,
            "path": path.relative_to(repo).as_posix(),
            "reason": "MATCHING_PENDING_CANDIDATE_EXISTS",
        }

    year, month, submitted_at = submitted_parts(audit)
    cid = candidate_id_for(audit, repo)
    path = repo / "research/codex/intake" / year / month / f"{cid}.json"
    if path.exists():
        return {
            "created": False,
            "candidate_id": cid,
            "path": path.relative_to(repo).as_posix(),
            "reason": "CANDIDATE_ALREADY_EXISTS",
        }

    candidate = build_candidate(audit, cid, submitted_at)
    write_json(path, candidate)
    return {
        "created": True,
        "candidate_id": cid,
        "path": path.relative_to(repo).as_posix(),
        "reason": "FAIL_ROUTED_TO_BOUNDED_CODEX_INTAKE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--audit",
        type=Path,
        default=Path("research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT.json"),
    )
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    audit_path = args.audit if args.audit.is_absolute() else repo / args.audit
    result = route(repo, audit_path)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

