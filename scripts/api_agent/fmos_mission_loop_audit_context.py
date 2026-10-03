#!/usr/bin/env python3
"""Deterministic current-repository context builder for the FMOS mission-loop audit."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

MAX_CONTEXT_BYTES = 650_000
MAX_FILE_CHARS = 18_000
MAX_SEARCH_HITS_PER_TERM = 80

REQUIRED = [
    "README.md", "AGENTS.md", "LATEST_OPERATIONS_DASHBOARD.json", "LATEST_HANDOFF.json",
    "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
    "research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json",
    "research/remediation/LATEST_REMEDIATION_QUEUE.json",
    "research/remediation/LATEST_CODEX_READY_TASKS.json",
    "research/codex/LATEST_CODEX_EXECUTION_STATE.json",
    "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md",
    "00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md",
    "00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md",
    "00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md",
    "00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json",
    "01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md",
    "00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md",
    "00_FMOS/FRAMEWORK_INTELLIGENCE_AND_LEARNING_LOOP_v1.md",
    "00_FMOS/OPERATIONAL_MEMORY_AND_RETRIEVAL_v1.md",
    "scripts/framework_intelligence/framework_learning_supervisor.py",
    "scripts/framework_intelligence/automation_orchestration_v1.py",
    ".github/workflows/framework-learning-supervisor.yml",
    "research/api_agent/API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1.md",
    "research/api_agent/API_TASK_REGISTRY_v1.json",
    "research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json",
    "research/api_agent/API_INTELLIGENCE_POLICY_v2.json",
    "scripts/api_agent/api_gateway.py",
    "scripts/api_agent/senior_repair_audit_dispatch.py",
    "07_PROMPTS_AND_AGENTS/astra/README.md",
    "07_PROMPTS_AND_AGENTS/astra/ASTRA_REPOSITORY_MISSION_ROUTER_v1.json",
]
TERMS = [
    "mission", "orchestration", "supervisor", "delegation queue", "remediation",
    "CODEX_READY", "workflow_run", "framework-main-writer", "operational memory",
    "shared experience", "completion receipt", "consumer receipt", "exact-head",
    "readback", "retry", "idempotent", "stale", "superseded", "cancelled",
    "owner gate", "capability router", "next best experiment", "experiment dispatch",
    "persistent runtime"
]

def sh(*args: str) -> str:
    return subprocess.check_output(list(args), text=True, stderr=subprocess.STDOUT)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def clip(text: str, n: int = MAX_FILE_CHARS) -> tuple[str, bool]:
    if len(text) <= n:
        return text, False
    return text[:n] + "\n[CONTENT_TRUNCATED_BY_CONTEXT_BUILDER]\n", True

def tracked_files() -> list[str]:
    return [x for x in sh("git", "ls-files").splitlines() if x]

def grep_term(term: str) -> list[str]:
    try:
        out = sh("git", "grep", "-n", "-I", "-F", term)
    except subprocess.CalledProcessError as exc:
        out = exc.output or ""
    return out.splitlines()[:MAX_SEARCH_HITS_PER_TERM]

def workflow_inventory(root: Path) -> list[dict]:
    rows = []
    for p in sorted((root / ".github/workflows").glob("*.y*ml")):
        body = p.read_text(errors="replace")
        lower = body.lower()
        key_lines = []
        for i, line in enumerate(body.splitlines(), 1):
            if any(k in line for k in (
                "contents: write", "actions: write", "issues: write", "workflow_run:",
                "workflow_dispatch:", "issue_comment:", "schedule:", "concurrency:",
                "framework-main-writer"
            )):
                key_lines.append(f"{i}:{line}")
        rows.append({
            "path": str(p.relative_to(root)),
            "sha256": sha256(p.read_bytes()),
            "contents_write": "contents: write" in lower,
            "actions_write": "actions: write" in lower,
            "issues_write": "issues: write" in lower,
            "has_schedule": "schedule:" in lower,
            "has_workflow_run": "workflow_run:" in lower,
            "has_issue_comment": "issue_comment:" in lower,
            "has_workflow_dispatch": "workflow_dispatch:" in lower,
            "uses_framework_main_writer": "framework-main-writer" in body,
            "key_lines": key_lines[:80],
        })
    return rows

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    root = args.repo_root.resolve()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    head = sh("git", "rev-parse", "HEAD").strip()
    branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
    tracked = tracked_files()
    members = []
    for rel in REQUIRED:
        p = root / rel
        if not p.exists():
            members.append({"path": rel, "status": "MISSING"})
            continue
        raw = p.read_bytes()
        clipped, truncated = clip(raw.decode(errors="replace"))
        members.append({
            "path": rel, "status": "PRESENT", "bytes": len(raw),
            "sha256": sha256(raw), "truncated": truncated, "content": clipped
        })

    searches = {term: grep_term(term) for term in TERMS}
    workflows = workflow_inventory(root)
    context = {
        "contract": "FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT_CONTEXT_v1",
        "authority": "UNTRUSTED_READ_ONLY_EVIDENCE",
        "control_plane": {
            "repo": "Donh91/Investering-Framework-Archive-v1",
            "head": head, "branch": branch, "tracked_file_count": len(tracked)
        },
        "required_members": members,
        "search_inventory": searches,
        "workflow_writer_inventory": workflows,
        "restricted_plane": {
            "repo": "Donh91/secrets", "content_included": False,
            "rule": "Use separate authorized binding if materially required; never infer private values."
        },
    }
    encoded = (json.dumps(context, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(encoded) > MAX_CONTEXT_BYTES:
        raise SystemExit(f"context_too_large:{len(encoded)}>{MAX_CONTEXT_BYTES}")

    (out / "context.json").write_bytes(encoded)
    coverage = {
        "contract": "FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT_COVERAGE_v1",
        "head": head, "branch": branch, "tracked_file_count": len(tracked),
        "required_path_count": len(REQUIRED),
        "required_present": sum(1 for x in members if x["status"] == "PRESENT"),
        "required_missing": [x["path"] for x in members if x["status"] == "MISSING"],
        "truncated_members": [x["path"] for x in members if x.get("truncated")],
        "search_terms": TERMS, "workflow_count": len(workflows),
        "contents_write_workflows": [x["path"] for x in workflows if x["contents_write"]],
        "actions_write_workflows": [x["path"] for x in workflows if x["actions_write"]],
        "main_writer_workflows": [x["path"] for x in workflows if x["uses_framework_main_writer"]],
    }
    (out / "coverage.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n")
    (out / "workflow_writer_inventory.json").write_text(json.dumps(workflows, indent=2, sort_keys=True) + "\n")
    (out / "search_inventory.json").write_text(json.dumps(searches, indent=2, sort_keys=True) + "\n")
    manifest = {
        "contract": "FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT_CONTEXT_MANIFEST_v1",
        "head": head,
        "context_sha256": sha256((out / "context.json").read_bytes()),
        "context_bytes": len((out / "context.json").read_bytes()),
        "coverage_sha256": sha256((out / "coverage.json").read_bytes()),
        "restricted_values_included": False,
        "member_hashes": {x["path"]: x.get("sha256") for x in members if x["status"] == "PRESENT"},
    }
    (out / "context_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "head": head, "context_bytes": manifest["context_bytes"], "output_dir": str(out)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
