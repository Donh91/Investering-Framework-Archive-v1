#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

PACKAGE_COMMITS = [
    ("#1348", "61de752a8e097e2b5f4d1d93d8781c85ab0bd021"),
    ("#1349", "157a49cb7758676f6449fbdf53fdde8904a7b16d"),
    ("#1350", "3faac71f8902c2becb5afefea8143ef6237b0e95"),
    ("#1351", "6051e01c4baf63040bc107eef4b979330cc3a6a8"),
    ("#1352", "666ef5c5d2de332dc8c2d12171cb06ddb3e2ff4c"),
    ("#1353", "c1ad9091816f6d779569f54e78862e170796ee62"),
    ("#1354", "78e951c189ea7e3cad7d0ce8f0aa3de1ce848d7f"),
    ("#1355", "793cbff9b792a50527ca7d09c29ebb83843f2cf3"),
    ("#1356", "735eaef61a81ad28619ee880f4bb8be7c10072b3"),
    ("#1357", "a630eac9b00015fec68d9a30b961e15bc07f3607"),
]

CURRENT_FILES = [
    "scripts/daily_capture/build_capture_index.py",
    "scripts/health/build_architecture_health.py",
    "scripts/health/build_automation_health.py",
    "scripts/learning/action_compass_exit_calibration.py",
    "scripts/experiments/build_experiment_yield_shadow.py",
    "scripts/learning/segment_return_foundation.py",
    "scripts/remediation/merge_codex_research_intake.py",
    "scripts/remediation/write_codex_research_completion_receipt.py",
    ".github/workflows/daily-compass.yml",
    "research/api_agent/API_TASK_REGISTRY_v1.json",
    "research/api_agent/API_INTELLIGENCE_POLICY_v2.json",
    "research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json",
    "00_ARCHIVE_CONTROL/research_governance_v1/AI_ROLE_ALLOCATION_v1.json",
    "scripts/api_agent/api_gateway.py",
    "scripts/api_agent/capability_router.py",
    "research/api_agent/meme_alpha/MEME_ALPHA_RUNTIME_POLICY_v1.json",
    "scripts/api_agent/meme_alpha_runtime.py",
    "scripts/framework_intelligence/framework_learning_supervisor.py",
    ".github/workflows/framework-learning-supervisor.yml",
]

PROMPT = """Perform one independent senior post-merge architecture audit of the supplied frozen public-repository package. Try to falsify the repairs rather than praise or restate them.

Audit owner-topology health, recovery-streak convergence, typed prospective Protection calibration, experiment-yield observability, DEL point-in-time segment-return methodology, completion-receipt convergence, GPT-6 model migration and legacy cost readback, Compass UNAVAILABLE warning validation, and Sol-first senior routing/budget authority.

Specifically try to prove: false GREEN/AMBER paths; manual/skipped/wrong-event recovery clearance; historical/prose/degraded Protection leakage; experiment state mutation or silent candidate loss; look-ahead/survivorship/irregular-cadence DEL bias; immutable receipt contradiction/replay failures; historical 5.6 receipt repricing failure; Terra synthesis displacement; Sol senior-lane budget bypass or automatic execution; increased periodic API call frequency; code/merge/canonical/market/portfolio authority leakage.

Use only supplied evidence. Do not invent missing repository state. forecast_candidates MUST be empty.

Encode the result inside the existing strict gateway schema:
- summary MUST begin with PASS, PASS_WITH_FINDINGS, or FAIL and include MODEL_USED=gpt-6-sol, NO_CODE_WRITE_PERFORMED, NO_AUTHORITY_CHANGE.
- evidence_for: concise verified defenses with exact path/commit references.
- evidence_against: each actionable finding as P0|..., P1|..., P2|... or P3|..., including affected path/commit and deterministic reproduction.
- uncertainties: anything not proven from the supplied packet.
- hypotheses: proposed owner/routing for repairs only, never direct writes.
- forecast_candidates: [].
"""


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.STDOUT)


def clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "\n[TRUNCATED_AT_BOUND]\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


MAX_CONTEXT_BYTES = 360_000
PATCH_CLIP_CHARS = 8_000
STAT_CLIP_CHARS = 3_000
FILE_CLIP_CHARS = 8_000


def build_context(repo_root: Path, output_dir: Path, issue_number: int, comment_id: str) -> dict[str, Any]:
    head = run_git("rev-parse", "HEAD").strip()
    package = []
    for label, sha in PACKAGE_COMMITS:
        try:
            stat = run_git("show", "--no-ext-diff", "--format=fuller", "--stat", sha)
            patch = run_git("show", "--no-ext-diff", "--format=", "--unified=12", sha)
            package.append({"label": label, "sha": sha, "stat": clip(stat, STAT_CLIP_CHARS), "patch": clip(patch, PATCH_CLIP_CHARS)})
        except subprocess.CalledProcessError as exc:
            package.append({"label": label, "sha": sha, "error": clip(exc.output, 4000)})

    files = []
    for rel in CURRENT_FILES:
        path = repo_root / rel
        if not path.exists():
            files.append({"path": rel, "status": "MISSING"})
            continue
        raw = path.read_bytes()
        files.append({"path": rel, "sha256": sha256_bytes(raw), "content": clip(raw.decode(errors="replace"), FILE_CLIP_CHARS)})

    context = {
        "contract": "SENIOR_REPAIR_AUDIT_CONTEXT_v1",
        "authority": "ADVISORY_READ_ONLY",
        "trigger": {"issue_number": issue_number, "comment_id": comment_id, "trigger_class": "POST_MERGE_HIGH_CONSEQUENCE_AUDIT"},
        "current_main_sha": head,
        "package_commits": package,
        "current_files": files,
        "hard_boundaries": {
            "code_write": False,
            "automatic_merge": False,
            "canonical_promotion": False,
            "market_rule_change": False,
            "threshold_change": False,
            "weight_change": False,
            "portfolio_action": False,
            "forecast_candidates_required_empty": True,
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    context_path = output_dir / "context.json"
    context_bytes = (json.dumps(context, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(context_bytes) > MAX_CONTEXT_BYTES:
        raise ValueError(f"senior_audit_context_too_large:{len(context_bytes)}>{MAX_CONTEXT_BYTES}")
    context_path.write_bytes(context_bytes)
    (output_dir / "prompt.txt").write_text(PROMPT)
    manifest = {
        "contract": "SENIOR_REPAIR_AUDIT_CONTEXT_MANIFEST_v1",
        "current_main_sha": head,
        "issue_number": issue_number,
        "comment_id": comment_id,
        "context_sha256": sha256_bytes(context_path.read_bytes()),
        "context_bytes": len(context_path.read_bytes()),
        "context_byte_limit": MAX_CONTEXT_BYTES,
        "package_commits": [{"label": label, "sha": sha} for label, sha in PACKAGE_COMMITS],
        "paths": [row["path"] for row in files],
        "private_data_included": False,
    }
    (output_dir / "context_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def validate_result(output_dir: Path) -> dict[str, Any]:
    receipt = json.loads((output_dir / "output" / "receipt.json").read_text())
    output = json.loads((output_dir / "output" / "output.json").read_text())
    if receipt.get("status") != "PASS":
        raise ValueError("senior_audit_receipt_not_pass")
    if receipt.get("model") != "gpt-6-sol" or receipt.get("reasoning_effort") != "high":
        raise ValueError("senior_audit_model_binding_invalid")
    cost = receipt.get("estimated_cost_usd")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not 0 <= float(cost) <= 3.0:
        raise ValueError("senior_audit_cost_invalid")
    if receipt.get("forecast_candidate_count") != 0 or output.get("forecast_candidates") != []:
        raise ValueError("senior_audit_forecast_candidates_forbidden")
    summary = str(output.get("summary") or "")
    if not summary.startswith(("PASS", "PASS_WITH_FINDINGS", "FAIL")):
        raise ValueError("senior_audit_summary_verdict_missing")
    for marker in ("MODEL_USED=gpt-6-sol", "NO_CODE_WRITE_PERFORMED", "NO_AUTHORITY_CHANGE"):
        if marker not in summary:
            raise ValueError("senior_audit_summary_marker_missing:" + marker)
    authority = receipt.get("authority")
    if not isinstance(authority, dict) or any(value is not False for value in authority.values()):
        raise ValueError("senior_audit_authority_not_zero")
    return {"receipt": receipt, "output": output}


def failure_report_markdown(output_dir: Path, comment_id: str) -> str:
    receipt_path = output_dir / "output" / "receipt.json"
    if not receipt_path.exists():
        return (
            "## SENIOR_REPAIR_AUDIT failed before a paid receipt was persisted\n\n"
            "Trigger comment: " + comment_id + "\n"
            "No API receipt exists in the runtime output directory. The failure occurred before a durable paid-call receipt was available.\n"
        )
    receipt = json.loads(receipt_path.read_text())
    errors = receipt.get("parse_errors") if isinstance(receipt.get("parse_errors"), list) else []
    return "\n".join([
        "## SENIOR_REPAIR_AUDIT attempt failed closed",
        "",
        "Trigger comment: " + comment_id,
        "Model: " + str(receipt.get("model")),
        "Receipt status: " + str(receipt.get("status")),
        "Tokens: input=" + str(receipt.get("input_tokens")) + ", output=" + str(receipt.get("output_tokens")),
        "Estimated API cost: " + f"{float(receipt.get('estimated_cost_usd') or 0.0):.6f}" + " USD",
        "Attempts: " + str(receipt.get("attempt_count")),
        "Parse/incomplete evidence: " + json.dumps(errors, sort_keys=True),
        "",
        "The receipt and blocked output were persisted for budget/accounting evidence. No audit conclusion was accepted.",
    ]) + "\n"


def report_markdown(output_dir: Path, comment_id: str, persisted_path: str) -> str:
    result = validate_result(output_dir)
    receipt, output = result["receipt"], result["output"]
    findings = [row for row in output.get("evidence_against", []) if isinstance(row, str) and row.startswith(("P0|", "P1|", "P2|", "P3|"))]
    body = [
        "## SENIOR_REPAIR_AUDIT completed",
        "",
        "Trigger comment: " + comment_id,
        "Model: " + str(receipt["model"]) + ", reasoning: " + str(receipt["reasoning_effort"]),
        "Tokens: input=" + str(receipt["input_tokens"]) + ", output=" + str(receipt["output_tokens"]),
        "Estimated API cost: " + f"{float(receipt['estimated_cost_usd']):.6f}" + " USD",
        "Status: " + str(output["status"]),
        "",
        str(output["summary"]),
        "",
        "Actionable findings: " + str(len(findings)),
    ]
    body.extend(["- " + row for row in findings[:8]] or ["- none"])
    body.extend(["", "Full immutable output and receipt: " + persisted_path + "."])
    return "\n".join(body) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    build = sub.add_parser("build")
    build.add_argument("--repo-root", type=Path, default=Path("."))
    build.add_argument("--output-dir", type=Path, required=True)
    build.add_argument("--issue-number", type=int, required=True)
    build.add_argument("--comment-id", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--output-dir", type=Path, required=True)
    report = sub.add_parser("report")
    report.add_argument("--output-dir", type=Path, required=True)
    report.add_argument("--comment-id", required=True)
    report.add_argument("--persisted-path", required=True)
    report.add_argument("--output", type=Path, required=True)
    failure_report = sub.add_parser("failure-report")
    failure_report.add_argument("--output-dir", type=Path, required=True)
    failure_report.add_argument("--comment-id", required=True)
    failure_report.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "build":
        result = build_context(args.repo_root, args.output_dir, args.issue_number, args.comment_id)
        print(json.dumps(result, sort_keys=True))
    elif args.cmd == "validate":
        result = validate_result(args.output_dir)
        print(json.dumps({
            "status": "PASS",
            "model": result["receipt"]["model"],
            "input_tokens": result["receipt"]["input_tokens"],
            "output_tokens": result["receipt"]["output_tokens"],
            "estimated_cost_usd": result["receipt"]["estimated_cost_usd"],
        }, sort_keys=True))
    elif args.cmd == "report":
        body = report_markdown(args.output_dir, args.comment_id, args.persisted_path)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body)
        print(json.dumps({"status": "PASS", "output": str(args.output)}, sort_keys=True))
    else:
        body = failure_report_markdown(args.output_dir, args.comment_id)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body)
        print(json.dumps({"status": "PASS", "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
