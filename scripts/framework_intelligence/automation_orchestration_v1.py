#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ACTIVE_REMEDIATION_STATES = {
    "CODEX_READY",
    "IN_REMEDIATION",
    "POST_FIX_OBSERVATION",
    "REOPENED",
}
SOL_FINDINGS = {
    "REPEATED_CONSECUTIVE_FAILURES",
    "REPEATED_PR_GATE_REJECTIONS",
}


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def workflow_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text.endswith(".yml"):
        text = text[:-4]
    elif text.endswith(".yaml"):
        text = text[:-5]
    return text


def remediation_rows(value: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for key in ("items", "tasks", "codex_ready_tasks", "active_remediation"):
        for item in value.get(key, []) or []:
            if not isinstance(item, dict):
                continue
            identity = (
                str(item.get("signature") or ""),
                str(item.get("candidate_id") or ""),
                str(item.get("state") or ""),
            )
            if identity in seen:
                continue
            seen.add(identity)
            rows.append(item)
    return rows


def row_matches_workflow(row: dict[str, Any], workflow: str) -> bool:
    target = workflow_key(workflow)
    if not target:
        return False
    candidates = [
        row.get("workflow"),
        row.get("finding"),
        row.get("objective"),
        row.get("candidate_id"),
        row.get("candidate_path"),
    ]
    return any(target in workflow_key(value) or workflow_key(value) in target for value in candidates if value)


def best_remediation_match(rows: list[dict[str, Any]], workflow: str) -> dict[str, Any] | None:
    matches = [row for row in rows if row_matches_workflow(row, workflow)]
    if not matches:
        return None
    rank = {
        "IN_REMEDIATION": 0,
        "CODEX_READY": 1,
        "POST_FIX_OBSERVATION": 2,
        "REOPENED": 3,
        "NEEDS_MORE_EVIDENCE": 4,
        "OBSERVED": 5,
    }
    return sorted(matches, key=lambda row: (rank.get(str(row.get("state")), 99), str(row.get("signature") or "")))[0]


def red_clusters(red_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_head: dict[str, list[dict[str, Any]]] = {}
    for row in red_rows:
        head = (((row.get("live") or {}).get("latest_run") or {}).get("head_sha"))
        if head:
            by_head.setdefault(str(head), []).append(row)
    clusters: list[dict[str, Any]] = []
    for head, members in sorted(by_head.items()):
        if len(members) < 3:
            continue
        clusters.append(
            {
                "cluster_id": f"HEAD-{head[:12]}",
                "head_sha": head,
                "workflow_count": len(members),
                "workflows": sorted(str(x.get("workflow")) for x in members),
                "reason": "Multiple RED workflows failed on the same repository head; test shared-cause before independent repairs.",
            }
        )
    return clusters


def build_plan(repo: Path, out_root: Path) -> dict[str, Any]:
    health_path = repo / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
    remediation_path = repo / "research/remediation/LATEST_REMEDIATION_QUEUE.json"
    codex_path = repo / "research/remediation/LATEST_CODEX_READY_TASKS.json"

    health = read_json(health_path, {})
    remediation = read_json(remediation_path, {})
    codex = read_json(codex_path, {})
    if health.get("contract") is None or not isinstance(health.get("workflows"), list):
        raise SystemExit("automation_health_unavailable_or_invalid")

    all_remediation = remediation_rows(remediation) + remediation_rows(codex)
    red_rows = [x for x in health["workflows"] if isinstance(x, dict) and x.get("status") == "RED"]
    clusters = red_clusters(red_rows)
    cluster_by_workflow: dict[str, str] = {}
    for cluster in clusters:
        for workflow in cluster["workflows"]:
            cluster_by_workflow[workflow] = cluster["cluster_id"]

    items: list[dict[str, Any]] = []
    luna_items: list[dict[str, Any]] = []
    sol_items: list[dict[str, Any]] = []
    existing_items: list[dict[str, Any]] = []

    for row in sorted(red_rows, key=lambda x: str(x.get("workflow") or "")):
        workflow = str(row.get("workflow") or "")
        live = row.get("live") if isinstance(row.get("live"), dict) else {}
        latest = live.get("latest_run") if isinstance(live.get("latest_run"), dict) else {}
        findings = [str(x) for x in (row.get("findings") or [])]
        match = best_remediation_match(all_remediation, workflow)
        remediation_state = str((match or {}).get("state") or "")
        repeated = bool(SOL_FINDINGS.intersection(findings)) or int(live.get("failure_streak") or 0) >= 2
        cluster_id = cluster_by_workflow.get(workflow)

        if match and remediation_state in ACTIVE_REMEDIATION_STATES:
            route = "FOLLOW_EXISTING_REMEDIATION"
            model_lane = "NONE"
        elif cluster_id:
            route = "SOL_CLUSTER_DIAGNOSIS"
            model_lane = "GPT_6_1_SOL"
        elif repeated:
            route = "SOL_DIAGNOSIS"
            model_lane = "GPT_6_1_SOL"
        else:
            route = "LUNA_TRIAGE"
            model_lane = "GPT_6_LUNA"

        item = {
            "workflow": workflow,
            "findings": findings,
            "failure_streak": int(live.get("failure_streak") or 0),
            "recent_failure_count": int(live.get("recent_failure_count") or 0),
            "latest_run_id": latest.get("id"),
            "latest_run_url": latest.get("html_url"),
            "latest_head_sha": latest.get("head_sha"),
            "scheduled": bool(row.get("scheduled")),
            "openai_enabled": bool(row.get("openai_enabled")),
            "write_target_class": row.get("write_target_class"),
            "writer_group": row.get("writer_group"),
            "route": route,
            "model_lane": model_lane,
            "cluster_id": cluster_id,
            "existing_remediation": (
                {
                    "state": remediation_state,
                    "signature": match.get("signature"),
                    "finding": match.get("finding"),
                    "route": match.get("route"),
                }
                if match
                else None
            ),
        }
        items.append(item)
        if model_lane == "GPT_6_LUNA":
            luna_items.append(item)
        elif model_lane == "GPT_6_1_SOL":
            sol_items.append(item)
        else:
            existing_items.append(item)

    fingerprint_basis = {
        "health_generated_at_utc": health.get("generated_at_utc"),
        "items": [
            {
                "workflow": x["workflow"],
                "findings": x["findings"],
                "failure_streak": x["failure_streak"],
                "latest_head_sha": x["latest_head_sha"],
                "route": x["route"],
                "remediation_state": (x.get("existing_remediation") or {}).get("state"),
            }
            for x in items
        ],
        "clusters": clusters,
    }
    fingerprint = canonical_hash(fingerprint_basis)
    previous = read_json(out_root / "LATEST_PLAN.json", {})
    material_delta = previous.get("fingerprint") != fingerprint

    plan = {
        "contract": "AUTOMATION_INTELLIGENT_ORCHESTRATION_PLAN_v1",
        "authority": "ADVISORY_ORCHESTRATION_ONLY",
        "generated_at_utc": now_iso(),
        "source_health_generated_at_utc": health.get("generated_at_utc"),
        "source_health_status": health.get("status"),
        "fingerprint": fingerprint,
        "material_delta": material_delta,
        "fleet": {
            "workflow_count": health.get("workflow_count"),
            "scheduled_workflow_count": health.get("scheduled_workflow_count"),
            "writer_count": health.get("writer_count"),
            "green_count": health.get("green_count"),
            "amber_count": health.get("amber_count"),
            "red_count": health.get("red_count"),
        },
        "routing_summary": {
            "luna_triage_count": len(luna_items),
            "sol_6_1_diagnosis_count": len(sol_items),
            "existing_remediation_count": len(existing_items),
            "shared_head_cluster_count": len(clusters),
        },
        "agent_calls": {
            "luna_required": bool(luna_items) and material_delta,
            "sol_6_1_required": bool(sol_items) and material_delta,
            "max_luna_calls_this_run": 1,
            "max_sol_calls_this_run": 1,
            "astra_required": False,
        },
        "clusters": clusters,
        "items": items,
        "guardrails": {
            "deterministic_first": True,
            "batch_before_model_call": True,
            "existing_remediation_is_authoritative": True,
            "codex_ready_authority_remains_remediation_controller": True,
            "no_duplicate_repair_task_creation": True,
            "no_repository_write_authority_for_models": True,
            "no_automatic_merge": True,
            "no_market_or_portfolio_authority": True,
            "astra_periodic_use": False,
        },
    }
    write_json(out_root / "LATEST_PLAN.json", plan)

    luna_context = {
        "contract": "AUTOMATION_ORCHESTRATOR_LUNA_CONTEXT_v1",
        "plan_fingerprint": fingerprint,
        "source_health_generated_at_utc": health.get("generated_at_utc"),
        "items": luna_items,
        "instructions_context": "Triage only. Distinguish transient execution failure, likely shared dependency, missing evidence, or code-defect candidate. Do not create remediation authority.",
    }
    sol_context = {
        "contract": "AUTOMATION_ORCHESTRATOR_SOL_CONTEXT_v1",
        "plan_fingerprint": fingerprint,
        "source_health_generated_at_utc": health.get("generated_at_utc"),
        "clusters": clusters,
        "items": sol_items,
        "instructions_context": "Root-cause and deduplication only. Test shared-cause before independent repair. Existing remediation state remains authoritative.",
    }
    write_json(out_root / "LUNA_CONTEXT.json", luna_context)
    write_json(out_root / "SOL_CONTEXT.json", sol_context)
    (out_root / "LUNA_PROMPT.txt").write_text(
        "Triage the supplied current RED automation-health items as a cheap first-pass operations analyst. "
        "Use only supplied evidence. For each workflow, identify the most likely failure class, what evidence is missing, "
        "whether the issue looks transient or persistent, and which EXISTING owner should inspect it next. "
        "Do not create CODEX_READY authority, do not propose market/framework changes, and do not request repository writes. "
        "Prefer concise batching and explicit uncertainty.\n"
    )
    (out_root / "SOL_PROMPT.txt").write_text(
        "Perform a senior cross-workflow root-cause and deduplication review of the supplied RED automation-health items. "
        "Prioritize shared-head clusters, repeated failures, and interactions among upstream/downstream workflows. "
        "Try to falsify the idea that each failure is independent. Respect existing remediation/Codex states, and identify "
        "only bounded diagnostic next steps. No code write, no merge, no canonical change, no market or portfolio authority.\n"
    )
    return plan


def finalize(out_root: Path, luna_output: Path | None, sol_output: Path | None) -> dict[str, Any]:
    plan = read_json(out_root / "LATEST_PLAN.json", {})
    if plan.get("contract") != "AUTOMATION_INTELLIGENT_ORCHESTRATION_PLAN_v1":
        raise SystemExit("orchestration_plan_missing")
    luna = read_json(luna_output, None) if luna_output else None
    sol = read_json(sol_output, None) if sol_output else None
    readout = {
        "contract": "AUTOMATION_INTELLIGENT_ORCHESTRATION_READOUT_v1",
        "authority": "ADVISORY_ORCHESTRATION_ONLY",
        "generated_at_utc": now_iso(),
        "plan_fingerprint": plan.get("fingerprint"),
        "source_health_generated_at_utc": plan.get("source_health_generated_at_utc"),
        "routing_summary": plan.get("routing_summary"),
        "luna_triage": luna,
        "sol_6_1_diagnosis": sol,
        "guardrails": plan.get("guardrails"),
        "note": "Agent outputs are evidence/diagnosis only. Remediation Maturation remains the sole CODEX_READY authority.",
    }
    write_json(out_root / "LATEST_AGENT_READOUT.json", readout)
    return readout


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--repo-root", type=Path, default=Path("."))
    build.add_argument(
        "--output-root",
        type=Path,
        default=Path("research/framework_learning/automation_orchestration"),
    )

    fin = sub.add_parser("finalize")
    fin.add_argument(
        "--output-root",
        type=Path,
        default=Path("research/framework_learning/automation_orchestration"),
    )
    fin.add_argument("--luna-output", type=Path)
    fin.add_argument("--sol-output", type=Path)

    args = parser.parse_args()
    if args.command == "build":
        plan = build_plan(args.repo_root.resolve(), args.output_root)
        print(json.dumps({"status": "PASS", "plan": str(args.output_root / "LATEST_PLAN.json"), "routing_summary": plan["routing_summary"], "agent_calls": plan["agent_calls"]}, sort_keys=True))
        return 0
    readout = finalize(args.output_root, args.luna_output, args.sol_output)
    print(json.dumps({"status": "PASS", "readout": str(args.output_root / "LATEST_AGENT_READOUT.json"), "plan_fingerprint": readout["plan_fingerprint"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
