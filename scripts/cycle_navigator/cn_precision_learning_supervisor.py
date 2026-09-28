#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
from typing import Any

AUTHORITY = "RESEARCH_ONLY_NON_CANONICAL"
STATE_CONTRACT = "CN_PRECISION_LEARNING_STATE_v1"
SNAPSHOT_CONTRACT = "CN_PRECISION_WEEKLY_TREND_v1"
CHECKPOINT_CONTRACT = "CN_PRECISION_4W_CHECKPOINT_v1"
ALLOWED_RESEARCH_ACTION = "RESEARCH_NEW_HYPOTHESIS"
WAIT_ACTION = "WAIT_FOR_MORE_EVIDENCE"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def append_jsonl_dedup(path: Path, row: dict[str, Any], key: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_jsonl(path)
    if any(x.get(key) == row.get(key) for x in existing):
        return False
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    return True


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def score_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clean = []
    seen = set()
    for row in rows:
        key = str(row.get("score_key") or "")
        if not key or key in seen:
            continue
        if row.get("authority") != "INTERNAL_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY":
            continue
        seen.add(key)
        clean.append(row)
    return sorted(clean, key=lambda r: (
        int(r["completed_iso_year"]),
        int(r["completed_iso_week"]),
        int(r.get("issue_scored", 0)),
    ))


def classify_family(
    family: str,
    settlements: list[dict[str, Any]],
    previous_state: str | None,
    policy: dict[str, Any],
) -> dict[str, Any]:
    recent_rows = settlements[-4:]
    previous_rows = settlements[-8:-4]
    recent_values = [r.get("family_scores", {}).get(family) for r in recent_rows]
    previous_values = [r.get("family_scores", {}).get(family) for r in previous_rows]
    recent = [float(x) for x in recent_values if isinstance(x, (int, float))]
    prev = [float(x) for x in previous_values if isinstance(x, (int, float))]

    thresholds = policy["thresholds"]
    low_max = float(thresholds["low_score_max"])
    persistent_mean_max = float(thresholds["persistent_mean_max"])
    watch_decline = float(thresholds["watch_decline_pp"])
    recovery_min = float(thresholds["recovery_score_min"])
    min_valid = int(thresholds["min_valid_observations_4w"])

    weak_count = sum(1 for x in recent if x <= low_max)
    zero_count = sum(1 for x in recent if x == 0)
    recent_mean = round(sum(recent) / len(recent), 2) if recent else None
    recent_median = round(float(median(recent)), 2) if recent else None
    prev_mean = round(sum(prev) / len(prev), 2) if prev else None
    decline = round(prev_mean - recent_mean, 2) if recent_mean is not None and prev_mean is not None else None
    last_two = recent[-2:]
    recovery_ready = len(last_two) == 2 and all(x >= recovery_min for x in last_two)

    raw_state = "NORMAL"
    if len(recent) >= min_valid:
        if zero_count >= 2:
            raw_state = "DEEP_REVIEW"
        elif weak_count >= 3 or (recent_mean is not None and recent_mean < persistent_mean_max):
            raw_state = "PERSISTENT_WEAKNESS"
        elif weak_count >= 2 or (decline is not None and decline >= watch_decline):
            raw_state = "WATCH"

    state = raw_state
    if previous_state in {"PERSISTENT_WEAKNESS", "DEEP_REVIEW"} and raw_state == "NORMAL" and not recovery_ready:
        state = "WATCH"

    streak = 0
    for value in reversed(recent):
        if value <= low_max:
            streak += 1
        else:
            break

    return {
        "family": family,
        "state": state,
        "raw_state": raw_state,
        "valid_observations_4w": len(recent),
        "recent_scores": recent_values,
        "mean_4w": recent_mean,
        "median_4w": recent_median,
        "weak_weeks_4w": weak_count,
        "zero_weeks_4w": zero_count,
        "low_score_streak": streak,
        "previous_4w_mean": prev_mean,
        "change_vs_previous_4w_pp": (-decline if decline is not None else None),
        "recovery_ready": recovery_ready,
    }


def build(repo: Path) -> dict[str, Any]:
    base = repo / "05_CYCLE_NAVIGATOR/internal_learning"
    policy = read_json(base / "POLICY.json")
    previous = read_json(base / "STATE.json", {}) or {}
    ledger_path = repo / "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PRECISION_LEDGER.jsonl"
    settlements = score_rows(read_jsonl(ledger_path))
    if not settlements:
        raise SystemExit("CN_PRECISION_LEARNING_NO_SETTLED_INTERNAL_SCORES")

    latest = settlements[-1]
    families = sorted({k for row in settlements for k in (row.get("family_scores") or {})})
    prev_family_states = previous.get("family_states") or {}
    trends = {}
    for fam in families:
        prior_state = (prev_family_states.get(fam) or {}).get("state")
        trends[fam] = classify_family(fam, settlements, prior_state, policy)

    settled_count = len(settlements)
    last_checkpoint_count = int(previous.get("last_checkpoint_settled_count", 0) or 0)
    checkpoint_every = int(policy["checkpoint"]["settled_weeks"])
    checkpoint_due = settled_count >= checkpoint_every and settled_count - last_checkpoint_count >= checkpoint_every

    severity_order = {"NORMAL": 0, "WATCH": 1, "PERSISTENT_WEAKNESS": 2, "DEEP_REVIEW": 3}
    ranked = sorted(
        trends.values(),
        key=lambda x: (
            -severity_order[x["state"]],
            x["mean_4w"] if x["mean_4w"] is not None else 999,
            x["family"],
        ),
    )
    persistent = [x for x in ranked if x["state"] in {"PERSISTENT_WEAKNESS", "DEEP_REVIEW"}]
    watched = [x for x in ranked if x["state"] == "WATCH"]

    checkpoint_sequence = int(previous.get("checkpoint_sequence", 0) or 0)
    if checkpoint_due:
        checkpoint_sequence += 1

    action = WAIT_ACTION
    target = ""
    family = ""
    reason = "No persistent multi-week precision weakness has matured to a research escalation."
    if checkpoint_due and persistent:
        top = persistent[0]
        action = ALLOWED_RESEARCH_ACTION
        target = f"CN_PRECISION::{top['family']}"
        family = top["family"]
        reason = (
            f"4-settlement checkpoint detected {top['state']} in {family}: "
            f"mean_4w={top['mean_4w']} weak_weeks={top['weak_weeks_4w']} "
            f"zero_weeks={top['zero_weeks_4w']}. Research-only falsification is warranted; "
            "no threshold, weight, forecast, public score or portfolio change is authorized."
        )
    elif persistent:
        top = persistent[0]
        reason = (
            f"Persistent weakness is visible in {top['family']} but the next four-settlement checkpoint "
            "has not matured. Continue observing without research escalation."
        )
    elif watched:
        reason = f"Watch-only weakness exists in {watched[0]['family']}; continue collecting settled evidence."

    snapshot = {
        "contract": SNAPSHOT_CONTRACT,
        "authority": AUTHORITY,
        "completed_iso_year": int(latest["completed_iso_year"]),
        "completed_iso_week": int(latest["completed_iso_week"]),
        "score_key": latest["score_key"],
        "settled_week_count": settled_count,
        "checkpoint_due": checkpoint_due,
        "family_trends": trends,
        "persistent_families": [x["family"] for x in persistent],
        "watch_families": [x["family"] for x in watched],
        "public_surface_effect": False,
        "canonical_effect": False,
        "portfolio_execution": False,
    }
    weekly_path = base / "weekly" / str(latest["completed_iso_year"]) / f"W{int(latest['completed_iso_week']):02d}.json"
    write_json(weekly_path, snapshot)

    checkpoint = None
    if checkpoint_due:
        recent_keys = [r["score_key"] for r in settlements[-4:]]
        previous_keys = [r["score_key"] for r in settlements[-8:-4]]
        checkpoint = {
            "contract": CHECKPOINT_CONTRACT,
            "authority": AUTHORITY,
            "checkpoint_sequence": checkpoint_sequence,
            "completed_iso_year": int(latest["completed_iso_year"]),
            "completed_iso_week": int(latest["completed_iso_week"]),
            "settlement_count": settled_count,
            "recent_score_keys": recent_keys,
            "previous_score_keys": previous_keys,
            "family_trends": trends,
            "persistent_families": [x["family"] for x in persistent],
            "watch_families": [x["family"] for x in watched],
            "api_review_required": bool(persistent),
            "api_review_tier": (
                "SOL_HIGH"
                if any(x["state"] == "DEEP_REVIEW" for x in persistent)
                else "TERRA_MEDIUM"
            ) if persistent else None,
            "api_review": None,
            "research_signal": {
                "primary_action": action,
                "target": target,
                "family": family,
                "reason": reason,
            },
            "canonical_effect": False,
            "portfolio_execution": False,
            "public_surface_effect": False,
        }
        cp_path = (
            base
            / "checkpoints"
            / str(latest["completed_iso_year"])
            / f"W{int(latest['completed_iso_week']):02d}_C{checkpoint_sequence:03d}.json"
        )
        write_json(cp_path, checkpoint)
        append_jsonl_dedup(
            base / "CN_PRECISION_CHECKPOINT_LEDGER.jsonl",
            {
                "checkpoint_id": (
                    f"C{checkpoint_sequence:03d}-Y{latest['completed_iso_year']}"
                    f"-W{int(latest['completed_iso_week']):02d}"
                ),
                "checkpoint_sequence": checkpoint_sequence,
                "completed_iso_year": int(latest["completed_iso_year"]),
                "completed_iso_week": int(latest["completed_iso_week"]),
                "settlement_count": settled_count,
                "persistent_families": checkpoint["persistent_families"],
                "api_review_required": checkpoint["api_review_required"],
                "api_review_tier": checkpoint["api_review_tier"],
                "authority": AUTHORITY,
            },
            "checkpoint_id",
        )

    evidence = {
        "latest_score_key": latest["score_key"],
        "settled_week_count": settled_count,
        "family_trends": trends,
        "checkpoint_due": checkpoint_due,
        "checkpoint_sequence": checkpoint_sequence,
    }
    latest_checkpoint = previous.get("latest_checkpoint")
    if checkpoint_due:
        latest_checkpoint = (
            base
            / "checkpoints"
            / str(latest["completed_iso_year"])
            / f"W{int(latest['completed_iso_week']):02d}_C{checkpoint_sequence:03d}.json"
        ).relative_to(repo).as_posix()

    state = {
        "contract": STATE_CONTRACT,
        "authority": AUTHORITY,
        "primary_action": action,
        "target": target,
        "family": family,
        "reason": reason,
        "evidence_fingerprint": digest(evidence),
        "last_settled_score_key": latest["score_key"],
        "settled_week_count": settled_count,
        "last_checkpoint_settled_count": settled_count if checkpoint_due else last_checkpoint_count,
        "checkpoint_sequence": checkpoint_sequence,
        "family_states": trends,
        "latest_weekly_snapshot": weekly_path.relative_to(repo).as_posix(),
        "latest_checkpoint": latest_checkpoint,
        "api_review_status": "PENDING" if checkpoint_due and persistent else "NOT_REQUIRED",
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
        "external_provider_calls_authorized": False,
        "automatic_promotion": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
        "public_surface_effect": False,
    }
    write_json(base / "STATE.json", state)

    runtime = repo / "runtime/cn_precision_learning"
    runtime.mkdir(parents=True, exist_ok=True)
    control = {
        "checkpoint_due": checkpoint_due,
        "api_review_required": bool(checkpoint and checkpoint["api_review_required"]),
        "api_review_tier": checkpoint["api_review_tier"] if checkpoint else None,
        "completed_iso_year": int(latest["completed_iso_year"]),
        "completed_iso_week": int(latest["completed_iso_week"]),
        "checkpoint_sequence": checkpoint_sequence,
        "checkpoint_path": state.get("latest_checkpoint"),
    }
    write_json(runtime / "control.json", control)

    if checkpoint and checkpoint["api_review_required"]:
        context = {
            "source_refs": [
                "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PRECISION_LEDGER.jsonl",
                "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PARAMETER_LEDGER.jsonl",
                state["latest_checkpoint"],
            ],
            "checkpoint": checkpoint,
            "recent_settlements": settlements[-8:],
        }
        write_json(runtime / "context.json", context)
        (runtime / "prompt.txt").write_text(
            "Analyze the supplied four-settlement Cycle Navigator internal precision checkpoint. "
            "Look for recurring error classes, cross-family blind spots, regime dependence, timing bias, "
            "range-shape problems and overly rigid frozen claims that a single weekly review could miss. "
            "Try to falsify the apparent weakness before accepting it. Propose only bounded research hypotheses "
            "or shadow tests. Never recommend changing public SITE/X precision semantics, historical public scores, "
            "canonical thresholds, model weights, forecast authority or portfolio execution. "
            "forecast_candidates MUST be empty.\n"
        )

    print(json.dumps(control, sort_keys=True))
    return control


def finalize(repo: Path, api_output: Path | None) -> None:
    base = repo / "05_CYCLE_NAVIGATOR/internal_learning"
    state = read_json(base / "STATE.json")
    control = read_json(repo / "runtime/cn_precision_learning/control.json")

    if not control.get("api_review_required"):
        state["api_review_status"] = "NOT_REQUIRED"
        write_json(base / "STATE.json", state)
        return

    cp_path = repo / control["checkpoint_path"]
    checkpoint = read_json(cp_path)

    if api_output is None or not api_output.exists():
        state["api_review_status"] = "SKIPPED_OR_UNAVAILABLE"
        checkpoint["api_review"] = {"status": "SKIPPED_OR_UNAVAILABLE"}
        write_json(cp_path, checkpoint)
        write_json(base / "STATE.json", state)
        return

    review = read_json(api_output)
    if review.get("forecast_candidates") not in ([], None):
        raise SystemExit("CN_PRECISION_LEARNING_API_FORECAST_CANDIDATES_FORBIDDEN")

    checkpoint["api_review"] = review
    state["api_review_status"] = str(review.get("status") or "UNKNOWN")
    summary = str(review.get("summary") or "").strip()
    hypotheses = review.get("hypotheses") if isinstance(review.get("hypotheses"), list) else []

    if state.get("primary_action") == ALLOWED_RESEARCH_ACTION and summary:
        state["reason"] = state["reason"] + " Deep review: " + summary[:900]
        if hypotheses:
            state["reason"] += " First bounded hypothesis: " + str(hypotheses[0])[:600]
        state["evidence_fingerprint"] = digest({
            "deterministic": state["evidence_fingerprint"],
            "api_review": review,
        })

    write_json(cp_path, checkpoint)
    write_json(base / "STATE.json", state)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--phase", choices=["build", "finalize"], default="build")
    ap.add_argument("--api-output", type=Path)
    args = ap.parse_args()
    repo = args.repo_root.resolve()

    if args.phase == "build":
        build(repo)
    else:
        finalize(repo, args.api_output)


if __name__ == "__main__":
    main()
