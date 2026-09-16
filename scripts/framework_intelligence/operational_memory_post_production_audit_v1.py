#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import operational_memory_v1 as opmem

FORBIDDEN_TRUE_KEYS = {
    "canonical_effect",
    "portfolio_execution",
    "automatic_promotion",
    "automatic_skill_activation",
    "automatic_repository_write",
    "canonical_promotion",
    "model_weight_change",
    "portfolio_action",
}

EXPECTED_CONTRACTS = {
    "LATEST_OPERATIONAL_MEMORY_STATE.json": "OPERATIONAL_MEMORY_AND_RETRIEVAL_v1",
    "LATEST_OPERATIONAL_MEMORY_INDEX.json": "OPERATIONAL_MEMORY_INDEX_v1",
    "LATEST_OPERATIONAL_MEMORY_HEALTH.json": "OPERATIONAL_MEMORY_HEALTH_v1",
    "LATEST_PROCEDURAL_CANDIDATES.json": "OPERATIONAL_PROCEDURAL_CANDIDATES_v1",
}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def head_sha(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def true_authority_paths(value, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in FORBIDDEN_TRUE_KEYS and child is True:
                hits.append(path)
            hits.extend(true_authority_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            path = f"{prefix}[{index}]"
            hits.extend(true_authority_paths(child, path))
    return hits


def audit(root: Path, operational_root: Path) -> dict:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    current_head = head_sha(root)
    docs = {name: load_json(operational_root / name) for name in EXPECTED_CONTRACTS}

    failures: list[str] = []
    warnings: list[str] = []

    for name, contract in EXPECTED_CONTRACTS.items():
        doc = docs[name]
        if not doc:
            failures.append(f"missing_or_invalid:{name}")
        elif doc.get("contract") != contract:
            failures.append(f"contract_mismatch:{name}:{doc.get('contract')}")

    state = docs["LATEST_OPERATIONAL_MEMORY_STATE.json"]
    index = docs["LATEST_OPERATIONAL_MEMORY_INDEX.json"]
    health = docs["LATEST_OPERATIONAL_MEMORY_HEALTH.json"]
    candidates = docs["LATEST_PROCEDURAL_CANDIDATES.json"]

    authority_violations: list[str] = []
    for name, doc in docs.items():
        authority_violations.extend(f"{name}:{path}" for path in true_authority_paths(doc))
    if authority_violations:
        failures.extend(f"authority_violation:{path}" for path in authority_violations)

    rows = index.get("rows") if isinstance(index.get("rows"), list) else []
    candidate_rows = candidates.get("candidates") if isinstance(candidates.get("candidates"), list) else []
    reported_candidate_count = int(candidates.get("candidate_count") or 0) if candidates else 0

    episode_count = len(rows)
    if index.get("episode_count") != episode_count:
        failures.append("index_episode_count_mismatch")
    if state and state.get("episode_count") != episode_count:
        failures.append("state_episode_count_mismatch")
    if health and health.get("episode_count") != episode_count:
        failures.append("health_episode_count_mismatch")
    if len(candidate_rows) < 50 and reported_candidate_count != len(candidate_rows):
        failures.append("candidate_count_mismatch")
    if len(candidate_rows) == 50 and reported_candidate_count < len(candidate_rows):
        failures.append("candidate_count_mismatch")

    if health and health.get("status") != "PASS":
        failures.append(f"health_not_pass:{health.get('status')}")
    if index and index.get("source_head_sha") != current_head:
        failures.append("index_not_bound_to_current_head")
    if state and state.get("source_head_sha") != current_head:
        failures.append("state_not_bound_to_current_head")

    compatibility_counts = Counter()
    stale_retrieval_violations: list[str] = []
    for row in rows:
        compatibility = (row.get("compatibility") or {}).get("status", "UNKNOWN")
        compatibility_counts[compatibility] += 1
        tier = row.get("retrieval_tier")
        if compatibility in {"DRIFTED", "REMOVED"} and tier != "REVALIDATE":
            stale_retrieval_violations.append(str(row.get("episode_id")))
    if stale_retrieval_violations:
        failures.extend(f"stale_memory_not_quarantined:{episode_id}" for episode_id in stale_retrieval_violations)

    unsafe_candidates: list[str] = []
    candidate_noise_flags: list[str] = []
    for row in candidate_rows:
        candidate_id = str(row.get("candidate_id"))
        if row.get("automatic_skill_activation") is True or row.get("promotion_allowed") is True:
            unsafe_candidates.append(candidate_id)
        if int(row.get("independent_commit_count") or 0) < 3:
            unsafe_candidates.append(candidate_id)
        if int(row.get("currently_compatible_count") or 0) == 0:
            candidate_noise_flags.append(candidate_id)
    if unsafe_candidates:
        failures.extend(f"unsafe_procedural_candidate:{candidate_id}" for candidate_id in sorted(set(unsafe_candidates)))
    if candidate_noise_flags:
        warnings.append(f"candidate_requires_revalidation:{len(candidate_noise_flags)}")

    compatible_rows = [
        row
        for row in rows
        if (row.get("compatibility") or {}).get("status") in {"EXACT", "PARTIAL"}
        and row.get("task_summary")
    ]
    probe_rows = compatible_rows[-12:]
    probe_results = []
    probe_hits = 0
    stale_reuse_probe_violations = 0
    for row in probe_rows:
        query_paths = list(row.get("changed_paths") or [])[:3]
        preflight = opmem.preflight(index, str(row.get("task_summary")), query_paths, top=5)
        selected = preflight.get("selected") or []
        top = selected[0] if selected else None
        top_class_match = bool(top and top.get("task_class") == row.get("task_class"))
        if top_class_match:
            probe_hits += 1
        stale_reused = [
            item
            for item in preflight.get("reusable_prior_work") or []
            if item.get("compatibility") not in {"EXACT", "PARTIAL"}
        ]
        stale_reuse_probe_violations += len(stale_reused)
        probe_results.append(
            {
                "episode_id": row.get("episode_id"),
                "expected_task_class": row.get("task_class"),
                "top_task_class": top.get("task_class") if top else None,
                "top_class_match": top_class_match,
                "selected_count": len(selected),
                "reusable_count": len(preflight.get("reusable_prior_work") or []),
                "revalidation_count": len(preflight.get("revalidation_required") or []),
            }
        )

    if stale_reuse_probe_violations:
        failures.append(f"preflight_reused_stale_memory:{stale_reuse_probe_violations}")

    probe_count = len(probe_results)
    probe_precision = round(probe_hits / probe_count, 4) if probe_count else None
    if episode_count == 0:
        warnings.append("no_episodes_yet")
    if probe_count == 0:
        warnings.append("retrieval_probe_baseline_unavailable")
    elif probe_count >= 5 and probe_precision is not None and probe_precision < 0.80:
        warnings.append(f"retrieval_precision_below_shadow_target:{probe_precision}")

    stale_count = compatibility_counts.get("DRIFTED", 0) + compatibility_counts.get("REMOVED", 0)
    stale_share = round(stale_count / episode_count, 4) if episode_count else 0.0
    if episode_count >= 20 and stale_share > 0.80:
        warnings.append(f"high_stale_share:{stale_share}")

    status = "FAIL" if failures else "WARN" if warnings else "PASS"
    action = (
        "BLOCK_OPERATIONAL_MEMORY_REUSE_AND_REPAIR"
        if status == "FAIL"
        else "CONTINUE_SHADOW_AND_ACCUMULATE_BASELINE"
        if status == "WARN"
        else "CONTINUE_SHADOW_AUTONOMOUSLY"
    )

    return {
        "contract": "OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT_v1",
        "generated_at_utc": generated_at,
        "status": status,
        "source_head_sha": current_head,
        "authority": {
            "canonical_effect": False,
            "portfolio_execution": False,
            "automatic_promotion": False,
            "automatic_skill_activation": False,
            "automatic_repository_write": False,
        },
        "episode_count": episode_count,
        "new_episode_count": state.get("new_episode_count") if state else None,
        "compatibility_counts": dict(sorted(compatibility_counts.items())),
        "stale_share": stale_share,
        "procedural_candidate_count": reported_candidate_count,
        "materialized_candidate_count": len(candidate_rows),
        "candidate_revalidation_count": len(candidate_noise_flags),
        "retrieval_probe": {
            "probe_count": probe_count,
            "top_task_class_hits": probe_hits,
            "top_task_class_precision": probe_precision,
            "stale_reuse_violations": stale_reuse_probe_violations,
            "results": probe_results,
        },
        "failures": failures,
        "warnings": warnings,
        "automatic_escalation_required": status == "FAIL",
        "memory_reuse_allowed": status != "FAIL",
        "recommended_action": action,
        "measurement": {
            "repeated_investigation_rate": "BASELINE_ACCUMULATING",
            "task_bootstrap_context_load": "BASELINE_ACCUMULATING",
            "useful_retrieval_precision": probe_precision,
            "stale_memory_safety": "PASS" if not stale_reuse_probe_violations and not stale_retrieval_violations else "FAIL",
            "failed_task_rate": "BASELINE_ACCUMULATING",
            "no_savings_claim_without_measurement": True,
        },
    }


def markdown(doc: dict) -> str:
    lines = [
        "# Operational Memory Post-Production Audit",
        "",
        f"Status: **{doc['status']}**",
        f"Source head: `{doc['source_head_sha']}`",
        f"Episodes: {doc['episode_count']}",
        f"New episodes this run: {doc.get('new_episode_count')}",
        f"Procedural candidates: {doc['procedural_candidate_count']}",
        f"Compatibility: `{json.dumps(doc['compatibility_counts'], sort_keys=True)}`",
        f"Retrieval probe precision: {doc['retrieval_probe']['top_task_class_precision']}",
        f"Recommended action: `{doc['recommended_action']}`",
        "",
        "## Failures",
    ]
    lines.extend(f"- {item}" for item in doc["failures"] or ["None"])
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in doc["warnings"] or ["None"])
    lines.extend(
        [
            "",
            "This audit is advisory framework-operations evidence only. Current GitHub `main` remains authoritative.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--operational-root",
        type=Path,
        default=Path("research/framework_learning/operational_memory"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT.md"),
    )
    parser.add_argument("--fail-on-fail", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    operational_root = args.operational_root
    if not operational_root.is_absolute():
        operational_root = root / operational_root
    output = args.output
    if not output.is_absolute():
        output = root / output
    markdown_output = args.markdown_output
    if not markdown_output.is_absolute():
        markdown_output = root / markdown_output

    doc = audit(root, operational_root)
    write_json(output, doc)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(markdown(doc))
    print(json.dumps({"status": doc["status"], "episode_count": doc["episode_count"], "probe_precision": doc["retrieval_probe"]["top_task_class_precision"]}, sort_keys=True))
    if args.fail_on_fail and doc["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
