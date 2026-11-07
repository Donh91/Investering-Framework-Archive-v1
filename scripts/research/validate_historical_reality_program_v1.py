#!/usr/bin/env python3
"""Validate the owner-gated HRE plan and episode atlas; no network or execution."""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

QUEUE_CONTRACT = "HRE_RESEARCH_QUEUE_V1"
ATLAS_CONTRACT = "HRE_HISTORICAL_EPISODE_ATLAS_V1"
ALLOWED_SCIENCE = {"ORIGINAL_ISSUED_2026", "FROZEN_RETROSPECTIVE_2020_2026", "CHALLENGER_DEVELOPMENT"}
TERMINAL_EVIDENCE = {"MERGED_MAIN_VERIFIED", "NATURAL_CONSUMER_VERIFIED", "SCIENTIFIC_TEST_COMPLETE"}
APPROVAL_REQUIRED = "NOT_STARTED_OWNER_APPROVAL_REQUIRED"


def utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("non-UTC timestamp")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() != dt.timedelta(0):
        raise ValueError("non-UTC offset")
    return parsed


def inspect(queue, atlas):
    errors = []
    if queue.get("contract") != QUEUE_CONTRACT:
        errors.append("queue_contract")
    if atlas.get("contract") != ATLAS_CONTRACT:
        errors.append("atlas_contract")
    if queue.get("queue_is_not_dispatcher") is not True:
        errors.append("queue_cannot_dispatch")
    for key in ("new_cron", "new_supervisor", "new_github_identity", "new_workflow_in_this_proposal",
                "automatic_paid_sol", "automatic_research_model_promotion", "automatic_live_portfolio_action"):
        if queue.get(key) is not False:
            errors.append("forbidden_authority:" + key)
    if queue.get("existing_supervisor_task_id") != "6ae5fd466b48819187abc224ec0f1c5f":
        errors.append("not_existing_supervisor")
    if not 2 <= queue.get("max_concurrent_read_only_compute_jobs_after_approval", 0) <= 4:
        errors.append("compute_concurrency_cap")
    if set(queue.get("source_classes", [])) != ALLOWED_SCIENCE:
        errors.append("science_class_scope")
    if queue.get("activation") and not queue.get("owner_approval_receipt"):
        errors.append("activation_without_authenticated_owner_receipt")
    tasks = queue.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks_missing")
        tasks = []
    ids = [t.get("id") for t in tasks if isinstance(t, dict)]
    if len(set(ids)) != len(ids):
        errors.append("duplicate_task_id")
    by_id = {t["id"]: t for t in tasks if isinstance(t, dict) and isinstance(t.get("id"), str)}
    graph = {}
    for t in tasks:
        if not isinstance(t, dict):
            errors.append("non_object_task")
            continue
        task_id = t.get("id", "?")
        deps = t.get("depends_on", [])
        if not isinstance(deps, list):
            errors.append("invalid_dependencies:" + task_id)
            deps = []
        graph[task_id] = deps
        if any(d not in by_id for d in deps):
            errors.append("unbound_dependency:" + task_id)
        if not re.fullmatch(r"HR-[0-9]{3}", task_id):
            errors.append("bad_task_id:" + task_id)
        if not isinstance(t.get("original_owner_issue"), str) or "#" not in t["original_owner_issue"]:
            errors.append("no_original_owner:" + task_id)
        if not t.get("question") or not t.get("first_action") or not t.get("required_evidence"):
            errors.append("empty_research_contract:" + task_id)
        if t.get("authorized_spend_usd", 0) != 0:
            errors.append("plan_cannot_authorize_spend:" + task_id)
        if t.get("preapproval_action_allowed") is not False:
            errors.append("preapproval_execution:" + task_id)
        if t.get("stage") in TERMINAL_EVIDENCE:
            receipt = t.get("completion_receipt")
            if not isinstance(receipt, dict) or not receipt.get("source_digest") or not receipt.get("run_url") or not re.fullmatch(r"[0-9a-f]{40}", str(receipt.get("main_sha", ""))):
                errors.append("completion_without_native_evidence:" + task_id)
    state = {}
    def visit(node):
        color = state.get(node, 0)
        if color == 1:
            return True
        if color == 2:
            return False
        state[node] = 1
        for dep in graph.get(node, []):
            if dep in graph and visit(dep):
                return True
        state[node] = 2
        return False
    if any(visit(n) for n in graph if state.get(n, 0) == 0):
        errors.append("cyclic_dependencies")
    episodes = atlas.get("episodes", [])
    if not isinstance(episodes, list) or not episodes:
        errors.append("episodes_missing")
        episodes = []
    if atlas.get("episode_count") != len(episodes):
        errors.append("episode_count_mismatch")
    seen = set()
    for e in episodes:
        eid = e.get("id", "?")
        if eid in seen:
            errors.append("duplicate_episode:" + eid)
        seen.add(eid)
        try:
            start = utc(e["window_start_utc"])
            end = utc(e["window_end_utc"])
            anchor = utc(e["candidate_anchor_utc"])
            if not start <= anchor < end:
                errors.append("outside_episode_window:" + eid)
            if start.year < 2020 or end.year > 2027:
                errors.append("out_of_scope_episode:" + eid)
        except (KeyError, ValueError, TypeError):
            errors.append("episode_clock:" + eid)
        if e.get("status") == "UNSCORED_CANDIDATE":
            if any(e.get(k) is not None for k in ("forecast_accuracy", "observed_warning_lead_hours", "simulated_warning_lead_hours", "economic_edge")):
                errors.append("fabricated_unscored_outcome:" + eid)
        elif not e.get("verified_result_ref"):
            errors.append("scored_without_verified_evidence:" + eid)
        if not e.get("negative_control_policy"):
            errors.append("missing_negative_control:" + eid)
        if e.get("feature_coverage") in ("COMPLETE", "ADMITTED") and not e.get("source_qa_receipt"):
            errors.append("fake_source_admission:" + eid)
        if start.year < 2026 and e.get("retrospective_original_policy") != "FROZEN_RETROSPECTIVE_ONLY":
            errors.append("fabricated_original_era:" + eid)
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", default="research/historical_reality_engine/RESEARCH_QUEUE_v1.json")
    ap.add_argument("--atlas", default="research/historical_reality_engine/EPISODE_ATLAS_v1.json")
    args = ap.parse_args()
    queue = json.loads(Path(args.queue).read_text(encoding="utf-8"))
    atlas = json.loads(Path(args.atlas).read_text(encoding="utf-8"))
    errors = inspect(queue, atlas)
    if errors:
        for error in errors:
            print("HRE_BLOCK:", error)
        return 1
    print(f"HRE_DESIGN_CONTRACT_PASS tasks={len(queue['tasks'])} episodes={len(atlas['episodes'])} activated={queue['activation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
