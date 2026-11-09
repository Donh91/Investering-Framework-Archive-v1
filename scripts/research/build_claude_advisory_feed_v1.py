#!/usr/bin/env python3
"""Deterministic advisory feed from existing original research owners.

Never dispatch Claude, promote a model, trade, or create a second scheduler.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

GOV = "00_ARCHIVE_CONTROL/research_governance_v1/"
SOURCES = {
    "meta": GOV + "meta_orchestrator_v1/STATE.json",
    "precision": "05_CYCLE_NAVIGATOR/internal_learning/STATE.json",
    "compounding": GOV + "compounding_learning_v1/NEXT_BEST_EXPERIMENT.json",
}
OUTPUT = GOV + "claude_advisory_feed/LATEST.json"
CONTRACTS = {
    "meta": "RESEARCH_META_ORCHESTRATOR_STATE_v1",
    "precision": "CN_PRECISION_LEARNING_STATE_v1",
    "compounding": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
}
WATCH_STATES = {"PERSISTENT_WEAKNESS", "DEEP_REVIEW", "WATCH"}
ALLOWED_PRIMARY_ACTIONS = {
    "QUEUE_BOUNDED_RESEARCH", "PREPARE_CANONICAL_REVIEW", "PRIORITIZE_DATA_INTEGRITY"
}


class SourceFailure(ValueError):
    pass


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def checked_read(root: Path, name: str) -> tuple[dict, str]:
    p = root / SOURCES[name]
    if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
        raise SourceFailure("SOURCE_MISSING_OR_UNSAFE:" + name)
    raw = p.read_bytes()
    if not raw or len(raw) > 1_500_000:
        raise SourceFailure("SOURCE_SIZE_INVALID:" + name)
    try:
        obj = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise SourceFailure("SOURCE_JSON_INVALID:" + name) from exc
    if not isinstance(obj, dict) or obj.get("contract") != CONTRACTS[name]:
        raise SourceFailure("SOURCE_CONTRACT_INVALID:" + name)
    if obj.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise SourceFailure("SOURCE_AUTHORITY_INVALID:" + name)
    for field in ("canonical_effect", "portfolio_execution"):
        if obj.get(field) is not False:
            raise SourceFailure("SOURCE_AUTHORITY_ELEVATION:" + name + ":" + field)
    return obj, hashlib.sha256(raw).hexdigest()


def source_head(root: Path) -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                           text=True, timeout=5, check=False)
        v = r.stdout.strip()
        if r.returncode == 0 and len(v) == 40 and all(c in "0123456789abcdef" for c in v):
            return v
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def build(root: Path, *, head: str | None = None) -> dict:
    sources, receipts = {}, {}
    for name in SOURCES:
        sources[name], sha = checked_read(root, name)
        receipts[name] = {"path": SOURCES[name], "sha256": sha,
                          "contract": CONTRACTS[name], "basis": "LOCAL_SOURCE_BYTES"}
    meta, precision, learning = (sources[x] for x in ("meta", "precision", "compounding"))
    if meta.get("binding_integrity") != "PRIMARY_COMPLETE" or meta.get("sentinel_verdict") != "PASS":
        raise SourceFailure("META_GOVERNANCE_PRIMARY_OR_SENTINEL_BLOCK")
    if meta.get("paid_data_authorized") is not False or meta.get("external_provider_calls_authorized") is not False:
        raise SourceFailure("META_PAID_OR_PROVIDER_AUTHORITY_VIOLATION")
    if learning.get("automatic_execution") is not False or learning.get("automatic_promotion") is not False:
        raise SourceFailure("LEARNING_AUTOMATIC_PROMOTION_VIOLATION")
    items: list[dict] = []
    primary = {
        "action": str(meta.get("primary_action") or ""),
        "source": str(meta.get("primary_source") or ""),
        "target": str(meta.get("primary_target") or ""),
    }
    if primary["action"] in ALLOWED_PRIMARY_ACTIONS:
        match = next((row for row in meta.get("queue", [])
                      if isinstance(row, dict)
                      and row.get("orchestrator_action") == primary["action"]
                      and row.get("source") == primary["source"]
                      and row.get("target") == primary["target"]), None)
        if match is None:
            raise SourceFailure("PRIMARY_QUEUE_ITEM_UNVERIFIED")
        source_fp = match.get("evidence_fingerprint")
        if not (isinstance(source_fp, str) and len(source_fp) == 64
                and all(c in "0123456789abcdef" for c in source_fp)):
            raise SourceFailure("PRIMARY_SOURCE_FINGERPRINT_UNVERIFIED")
        proof = meta.get("execution_proof", {})
        items.append({
            "id": "CURRENT_ORIGINAL_RESEARCH_EXECUTION_GAP",
            "source": primary["source"],
            "target": primary["target"],
            "original_action": primary["action"],
            "original_source_fingerprint": source_fp,
            "reproduced_issue": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1157",
            "existing_closure_owner": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156",
            "source_evaluator_status": "NEEDS_OWNER_VALIDATION",
            "priority": "P0_REVIEW_ONLY",
            "dispatch": "NO_AUTO_DISPATCH",
            "execution_proof_in_current_state": proof.get("status", "NOT_OBSERVED_IN_SOURCE"),
            "native_action_run_id": None,
            "calibration_outcome": None,
            "question": "Falsify and close the existing-owner research executor-to-due-only-outcome gap",
            "next_gate": "EXACT_ORIGINAL_OWNER_NATIVE_RUN_AND_SCIENCE_ADMISSION",
        })
    states = precision.get("family_states")
    if not isinstance(states, dict):
        raise SourceFailure("CN_FAMILY_STATES_INVALID")
    weak = sorted(({
        "family": k, "state": v.get("state"),
        "scoreable_observations": v.get("valid_observations_4w"),
        "mean_4w": v.get("mean_4w")
    } for k, v in states.items() if isinstance(v, dict)
                and v.get("state") in WATCH_STATES), key=lambda x: x["family"])
    if weak:
        items.append({
            "id": "CN_4_SETTLEMENT_WEAKNESS_CONTEXT",
            "original_owner": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516",
            "scientific_owner": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596",
            "priority": "WATCH_MATURITY", "dispatch": "NO_AUTO_DISPATCH",
            "last_settled_score_key": precision.get("last_settled_score_key"),
            "checkpoint_sequence": precision.get("checkpoint_sequence"),
            "weak_families": weak,
            "question": "Review original CN errors versus same-clock width-adjusted baselines only at an eligible checkpoint",
            "next_gate": "NEXT_SUCCESSFUL_4_SETTLEMENT_CHECKPOINT_AND_MATCHED_SOURCE_CLOCKS",
        })
    out = {
        "contract": "CLAUDE_ORIGINAL_OWNER_ADVISORY_FEED_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "research_queue_is_canonical": False,
        "is_new_scheduler_or_agent": False,
        "claude_invoked": False,
        "automatic_execution": False,
        "automatic_paid_dispatch": False,
        "automatic_canonical_promotion": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "source_checkout_sha": head if head is not None else source_head(root),
        "source_receipts": receipts,
        "current_selected_source": primary,
        "current_learning_proposal": str(learning.get("proposal_status") or "UNKNOWN"),
        "candidate_count": len(items),
        "candidates": items,
        "bridge_home": "https://github.com/Donh91/Investering-AI-Audit-Bridge",
        "bridge_intake_path": "tasks/claude/CLAUDE_MAX_AUDIT_INTAKE_v1.json",
        "notes": "Discovery only. No Claude dispatch, scientific approval or native execution receipt is made here. Recheck source main and original owner before every audit.",
    }
    out["semantic_fingerprint"] = digest({k: v for k, v in out.items()
                                          if k not in ("source_checkout_sha", "source_receipts", "semantic_fingerprint")})
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--output", default=OUTPUT)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    root = Path(args.repo_root).resolve()
    try:
        data = build(root)
    except SourceFailure as exc:
        raise SystemExit("CLAUDE_ADVISORY_FEED_FAIL_CLOSED:" + str(exc)) from exc
    serialized = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.dry_run:
        print(serialized)
        return
    path = root / args.output
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise SystemExit("CLAUDE_ADVISORY_FEED_OUTPUT_PATH_UNSAFE")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != serialized:
        path.write_text(serialized, encoding="utf-8")
    print(json.dumps({"contract": data["contract"], "candidate_count": data["candidate_count"],
                      "semantic_fingerprint": data["semantic_fingerprint"],
                      "claude_invoked": False, "output": args.output}, sort_keys=True))


if __name__ == "__main__":
    main()
