#!/usr/bin/env python3
"""Deterministic weekly skill-calibration advisory for the EXISTING Learning Supervisor.

No network, model, new cron, invoker, skill activation, execution authority or
new repair queue. Source-bound self-reports are NOT proof of native skill usage.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

CONTRACT = "WEEKLY_SKILL_CALIBRATION_v1"
ROOT_INDEX = "00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json"
FINAL_PATH = "research/framework_learning/weekly_forensics/LATEST.json"
RECEIPT_BASE = "research/framework_learning/skill_usage/observations"
SOURCES = ("research/api_agent/outputs/", "research/framework_learning/operational_memory/",
           "07_PROMPTS_AND_AGENTS/skill_runs/")
PILOT_FLAGS = ("PILOT_CANDIDATE", "SHADOW_ONLY", "EXPERIMENTAL", "NOT_ACTIVATED")
PHASES = {"SUGGESTED_ONLY", "READ_CONFIRMED", "PROCEDURE_APPLIED"}
MAX_RECEIPTS = 200


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(root: Path, rel: str, max_bytes: int = 100_000) -> tuple[dict[str, Any] | None, str | None]:
    path = root / rel
    if (path.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(root.resolve())):
        return None, None
    try:
        data = path.read_bytes()
        if len(data) > max_bytes:
            return None, None
        obj = json.loads(data)
        if not isinstance(obj, dict):
            return None, None
        return obj, digest(data)
    except (OSError, ValueError, UnicodeDecodeError):
        return None, None


def _time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        moment = datetime.fromisoformat(value[:-1] + "+00:00")
        return moment if moment.tzinfo is not None else None
    except ValueError:
        return None


def _week(value: datetime) -> str:
    y, w, _ = value.astimezone(ZoneInfo("Europe/Copenhagen")).isocalendar()
    return f"{y}-W{w:02d}"


def _eligible_week(now: datetime) -> str | None:
    if now.tzinfo is None:
        raise ValueError("CALIBRATION_CLOCK_MUST_BE_AWARE")
    local = now.astimezone(ZoneInfo("Europe/Copenhagen"))
    if local.weekday() != 0:
        return None
    return _week(local - timedelta(days=1))


def _safe_receipt(root: Path, path: Path, skills: dict[str, dict], week: str) -> dict[str, Any] | None:
    rel = path.relative_to(root).as_posix()
    observation, _ = _read_json(root, rel, max_bytes=16_000)
    if not observation or observation.get("contract") != "SKILL_USE_OBSERVATION_v1":
        return None
    if observation.get("week") != week or observation.get("authority") != "ADVISORY_SELF_REPORT_ONLY":
        return None
    if observation.get("automatic_skill_activation") is not False:
        return None
    skill = observation.get("skill_name")
    if not isinstance(skill, str) or skill not in skills:
        return None
    phase = observation.get("use_phase")
    if not isinstance(phase, str) or phase not in PHASES:
        return None
    invocation = observation.get("invocation_id")
    if not isinstance(invocation, str) or not re.fullmatch(r"[a-zA-Z0-9._:-]{4,96}", invocation):
        return None
    observed = _time(observation.get("observed_at_utc"))
    if observed is None or _week(observed) != week:
        return None
    src = observation.get("execution_receipt_path")
    proof = observation.get("execution_receipt_sha256")
    if not isinstance(src, str) or not src.startswith(SOURCES) or ".." in src.split("/"):
        return None
    if not isinstance(proof, str) or not re.fullmatch(r"[a-f0-9]{64}", proof):
        return None
    # This check binds bytes, NOT the asserted semantic content or the actor.
    original = root / src
    if (original.is_symlink() or not original.is_file()
            or not original.resolve().is_relative_to(root.resolve())
            or original == path):
        return None
    raw = original.read_bytes()
    if len(raw) > 1_000_000 or digest(raw) != proof:
        return None
    # Never accept a skill path from an untrusted receipt.
    metadata = skills[skill]
    current_skill = root / metadata["skill_path"]
    if (current_skill.is_symlink() or not current_skill.is_file()
            or not current_skill.resolve().is_relative_to(root.resolve())):
        return None
    if digest(current_skill.read_bytes()) != observation.get("skill_sha256"):
        return None
    return {"key": f"{invocation}:{skill}", "skill": skill, "phase": phase,
            "pilot": metadata["pilot"], "implicit": metadata["implicit"],
            "source_path": src, "source_hash": proof}


def _scan_observations(root: Path, skills: dict[str, dict], week: str) -> dict[str, Any]:
    base = root / RECEIPT_BASE / week
    if not base.exists():
        return {"state": "ABSENT", "reported": None, "invalid": None,
                "duplicate": None, "pilots_reported_applied": None, "by_phase": None,
                "source_paths": []}
    if base.is_symlink() or not base.is_dir() or not base.resolve().is_relative_to(root.resolve()):
        return {"state": "INVALID_SOURCE_ROOT", "reported": None, "invalid": None,
                "duplicate": None, "pilots_reported_applied": None, "by_phase": None,
                "source_paths": []}
    files = sorted(base.iterdir())
    if len(files) > MAX_RECEIPTS or any(f.is_symlink() or not f.is_file() or f.suffix != ".json" for f in files):
        return {"state": "UNBOUNDED_OR_INVALID_FILES", "reported": None, "invalid": None,
                "duplicate": None, "pilots_reported_applied": None, "by_phase": None,
                "source_paths": []}
    valid, invalid, duplicate = {}, 0, 0
    phase_conflicts: set[str] = set()
    pilot_applied_keys: set[str] = set()
    source_paths: set[str] = set()
    for p in files:
        row = _safe_receipt(root, p, skills, week)
        if row is None:
            invalid += 1
            continue
        source_paths.add(row["source_path"])
        if row["pilot"] and row["phase"] == "PROCEDURE_APPLIED":
            # A qualifying, *self-reported* pilot-use claim is always surfaced
            # for original-native review, even if another row contradicts it.
            pilot_applied_keys.add(row["key"])
        if row["key"] not in valid:
            valid[row["key"]] = row
        elif row["phase"] != valid[row["key"]]["phase"]:
            phase_conflicts.add(row["key"])
        else:
            duplicate += 1
    return {
        "state": "SOURCE_BOUND_SELF_REPORTS_NOT_INDEPENDENT_PROOF",
        "reported": len(valid),
        "invalid": invalid,
        "duplicate": duplicate,
        "phase_conflicts": len(phase_conflicts),
        "pilots_reported_applied": len(pilot_applied_keys),
        "by_phase": {x: sum(row["phase"] == x and key not in phase_conflicts
                            for key, row in valid.items()) for x in sorted(PHASES)},
        "source_paths": sorted(source_paths)[:15],
    }


def _catalog(root: Path) -> tuple[dict[str, dict], dict[str, Any]]:
    index, sha = _read_json(root, ROOT_INDEX, max_bytes=125_000)
    if not index or index.get("status") != "DERIVED_ROUTING_ONLY" or index.get("authority") != "NONE_BY_ITSELF" or index.get("canonical_owner") != "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md":
        raise ValueError("INVALID_SKILL_ROUTING_INDEX")
    entries = index.get("skills")
    if not isinstance(entries, list) or not entries:
        raise ValueError("INVALID_SKILL_CATALOG")
    skills = {}
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise ValueError("INVALID_SKILL_ENTRY")
        name = item["name"]
        if name in skills or not re.fullmatch("[a-z0-9-]{3,90}", name):
            raise ValueError("DUPLICATE_OR_UNSAFE_SKILL")
        path = item.get("skill_path")
        if not isinstance(path, str) or path != f".agents/skills/{name}/SKILL.md":
            raise ValueError("SKILL_PATH_NOT_CANONICAL")
        if type(item.get("allow_implicit_invocation")) is not bool:
            raise ValueError("SKILL_IMPLICIT_POLICY_UNKNOWN")
        maturity = str(item.get("maturity", "")).upper()
        pilot = any(x in maturity for x in PILOT_FLAGS)
        skills[name] = {"skill_path": path, "pilot": pilot,
                        "implicit": item["allow_implicit_invocation"]}
        if pilot and item["allow_implicit_invocation"]:
            raise ValueError("PILOT_IMPLICIT_INVOCATION_FORBIDDEN")
    return skills, {"source": ROOT_INDEX, "sha256": sha, "catalog_total": len(skills),
                    "pilot_count": sum(x["pilot"] for x in skills.values()),
                    "nonpilot_count": sum(not x["pilot"] for x in skills.values()),
                    "implicit_allowed_count": sum(x["implicit"] and not x["pilot"] for x in skills.values())}


def _previous(root: Path, week: str) -> dict[str, Any] | None:
    previous_local = datetime.fromisocalendar(int(week[:4]), int(week[-2:]), 1) - timedelta(days=7)
    prev = _week(previous_local.replace(tzinfo=ZoneInfo("Europe/Copenhagen")))
    path = f"research/framework_learning/skill_calibration/weeks/{prev}.json"
    row, _ = _read_json(root, path)
    if not row or row.get("contract") != CONTRACT or row.get("evaluated_week") != prev:
        return None
    return row


def load_frozen_last_completed_week(out_root: Path, now: datetime) -> dict[str, Any] | None:
    """Reuse only a hash-verifiable, previously published weekly scorecard.

    This makes the Monday result visible in the existing daily Supervisor
    without counting each daily execution as a new independent observation.
    """
    if now.tzinfo is None:
        raise ValueError("CALIBRATION_CLOCK_MUST_BE_AWARE")
    local = now.astimezone(ZoneInfo("Europe/Copenhagen"))
    # Previous Sunday is the last closed weekly period on *every* weekday.
    completed = _week(local - timedelta(days=local.weekday() + 1))
    path = out_root / "skill_calibration" / "weeks" / f"{completed}.json"
    if (path.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(out_root.resolve())):
        return None
    try:
        raw = path.read_bytes()
        if len(raw) > 100_000:
            return None
        row = json.loads(raw)
        if (not isinstance(row, dict) or
                row.get("contract") != CONTRACT or
                row.get("authority") != "ADVISORY_ONLY" or
                row.get("evaluated_week") != completed or
                row.get("auto_skill_activation") is not False or
                row.get("scientific_or_performance_promotion") is not False or
                row.get("new_agent_or_scheduler") is not False or
                row.get("automatic_model_calls") is not False):
            return None
        timestamp = _time(row.get("calibrated_at_utc"))
        if timestamp is None or timestamp > now.astimezone(timezone.utc):
            return None
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("source_final_sha256", ""))):
            return None
        return row
    except (OSError, ValueError, TypeError, UnicodeDecodeError):
        return None


def frozen_scorecard_sha256(row: dict[str, Any]) -> str:
    """Match the existing Supervisor write_json byte format exactly."""
    return digest((json.dumps(row, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def build(root: Path, now: datetime) -> dict[str, Any] | None:
    """Monday-only deterministic scoring of the PREVIOUS completed ISO week."""
    week = _eligible_week(now)
    if week is None:
        return None
    if now.tzinfo is None:
        raise ValueError("UTC_TIMESTAMP_REQUIRED")
    root = root.resolve()
    final, final_sha = _read_json(root, FINAL_PATH)
    final_good = (bool(final) and final.get("contract") == "WEEKLY_FORENSICS_PACK_v1"
                  and final.get("mode") == "FINAL"
                  and f'{final.get("iso_year")}-W{int(final.get("iso_week", 0)):02d}' == week
                  and final.get("authority") == "RESEARCH_ONLY_NON_CANONICAL")
    final_time = _time(final.get("generated_at_utc")) if final_good else None
    fresh = (final_time is not None
             and timedelta(seconds=0) <= now.astimezone(timezone.utc) - final_time <= timedelta(hours=48))
    report = {
        "contract": CONTRACT, "authority": "ADVISORY_ONLY", "evaluated_week": week,
        "calibrated_at_utc": now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_final_path": FINAL_PATH,
        "source_final_sha256": final_sha if fresh else None,
        "scientific_or_performance_promotion": False, "auto_skill_activation": False,
        "automatic_model_calls": False, "new_agent_or_scheduler": False,
        "prior_comparison_status": "UNKNOWN",
        "independent_skill_effect_rate": None,
        "verified_native_skill_usage_count": None,
        "actual_api_cost_usd": None,
        "action": None,
    }
    if not fresh:
        return {**report, "status": "WAIT_FOR_FINAL_WEEKLY_SOURCE",
                "metrics": None,
                "action": {"priority": "P1", "owner": "Framework Learning Supervisor / #1157",
                           "code": "REPAIR_FINAL_SOURCE_FIRST", "auto_execute": False,
                           "next_gate": "Matching, fresh FINAL weekly forensics source with hash"}}
    try:
        skills, catalog = _catalog(root)
    except ValueError as exc:
        return {**report, "status": "CATALOG_BLOCKED", "metrics": None,
                "action": {"priority": "P1", "owner": "Skill Registry / #1157",
                           "code": "REPAIR_SKILL_METADATA", "auto_execute": False,
                           "next_gate": str(exc)}}
    usage = _scan_observations(root, skills, week)
    prev = _previous(root, week)
    prior_metrics = prev.get("metrics") if isinstance(prev, dict) else None
    report["prior_comparison_status"] = "PREVIOUS_WEEK_PRESENT" if isinstance(prior_metrics, dict) else "UNKNOWN"
    prior_action = prev.get("action") if isinstance(prev, dict) else None
    prior_code = prior_action.get("code") if isinstance(prior_action, dict) else None
    report["prior_action_followup"] = {
        "previous_code": prior_code,
        "previous_week": prev.get("evaluated_week") if isinstance(prev, dict) else None,
        "native_resolution_verified": None,
        "actual_incremental_benefit_verified": None,
        "evidence_status": "UNKNOWN_UNLESS_ORIGINAL_OWNER_OUTCOME_IS_READ_BACK",
    }
    delta = None
    if isinstance(prior_metrics, dict):
        old = prior_metrics.get("catalog")
        if isinstance(old, dict) and type(old.get("catalog_total")) is int:
            delta = catalog["catalog_total"] - old["catalog_total"]
    status = ("BASELINE_ONLY_NATIVE_USAGE_UNKNOWN" if usage["state"] == "ABSENT"
              else "SOURCE_QUALITY_BLOCKED" if usage["state"] != "SOURCE_BOUND_SELF_REPORTS_NOT_INDEPENDENT_PROOF"
              else "SOURCE_BOUND_REPORTS_ADVISORY_ONLY")
    report["status"] = status
    report["metrics"] = {
        "catalog": catalog, "catalog_change_vs_prior_week": delta,
        "catalog_trend_unit": "registered_skills_not_skill_usage",
        "observations": usage,
        "eligible_invocation_denominator": None,
        "documented_activation_rate": None,
        "independent_skill_effect_rate": None,
        "actual_error_reduction": None,
        "verified_duplicate_work_avoided": None,
        "false_positive_rate": None,
        "false_negative_rate": None,
        "cost_and_latency_delta": None,
    }
    if usage["pilots_reported_applied"]:
        action = ("P0", "INVESTIGATE_UNAUTHORIZED_PILOT_USE",
                  "Determine actual native invocation authority from original execution receipt; do not assume report is proof")
    elif usage["state"] == "ABSENT":
        action = ("P1", "INSTRUMENT_NATIVE_SKILL_USAGE",
                  "Bind one genuine existing S1/Research native run to an authenticated skill read/use receipt; compare against no-skill baseline")
    elif (usage["state"] != "SOURCE_BOUND_SELF_REPORTS_NOT_INDEPENDENT_PROOF"
          or usage["invalid"] or usage.get("phase_conflicts")):
        action = ("P1", "REPAIR_SKILL_RECEIPT_INTEGRITY",
                  "Repair the original source/first-known or receipt hash, without counting rejected observations as a zero-benefit outcome")
    else:
        action = ("P2", "INDEPENDENT_SKILL_QUALITY_COMPARISON",
                  "Run one original-owner skill-quality-gate baseline comparison; source-bound self-report cannot establish marginal utility")
    report["action_fingerprint"] = digest(
        f"SKILL_CALIBRATION|{action[1]}|Framework Learning Supervisor / #1157".encode()
    )[:20]
    report["prior_action_followup"]["same_open_action_as_previous_week"] = (
        prior_code == action[1] if prior_code is not None else None
    )
    report["action"] = {"priority": action[0], "code": action[1],
                        "owner": "Existing Framework Learning Supervisor + Skill Quality Gate / #1157",
                        "bounded_next_action": action[2],
                        "auto_execute": False,
                        "follow_up_trigger": "New actual native read/usage and independently adjudicated outcome source; no repeated unchanged report"}
    report["calibration_policy"] = {
        "weekly_source": "LAST_COMPLETED_ISO_WEEK_FINAL_ONLY",
        "one_owner_action_max": 1, "measured_outcome_claim": "UNKNOWN_UNTIL_INDEPENDENT_NATIVE_PROOF",
        "week_over_week_comparison": "CANDIDATE_ONLY_UNTIL_TWO_QUALIFIED_WEEKLY_SAMPLES",
        "negative_control": "Routine work, suggestions and pilot matching never count as applied skills",
        "no_hindsight": True,
        "no_rewrite_past_scorings": True,
    }
    return report
