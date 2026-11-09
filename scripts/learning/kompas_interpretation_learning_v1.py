#!/usr/bin/env python3
"""KIL v1: prospectively register Official Compass claims and learn from due 72h outcomes.

Research only. Chat analyst interpretations are NOT automatically registered.
Uses the existing Official Compass Outcomes workflow, not a second issuer or scheduler.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

COPENHAGEN = ZoneInfo("Europe/Copenhagen")
CONTRACT = "KIL_OFFICIAL_SOURCE_PROXY_v1"
OUTCOME_CONTRACT = "KIL_DUE_72H_REVIEW_v1"
REPORT_CONTRACT = "KIL_THREE_DAY_RESEARCH_REPORT_v1"
ROOT = Path("04_MARKET_LEARNING/handlekompas")
LATEST = ROOT / "official/LATEST_COMPASS.json"
OUTPUT = ROOT / "research/interpretation_learning_v1"
SCRIPT_PATH = "scripts/learning/kompas_interpretation_learning_v1.py"
ID_RE = re.compile(r"^CMP-[0-9]{8}-[a-zA-Z0-9_-]{4,64}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
PILOT_DURATION_DAYS = 56
MAX_ISSUE_AGE = timedelta(hours=6)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("MISSING_UTC")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.utcoffset() is None:
        raise ValueError("NAIVE_UTC")
    return stamp.astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_obj(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_bytes())
    if not isinstance(obj, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return obj


def validated_self_hash(obj: dict[str, Any], field: str) -> bool:
    value = obj.get(field)
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value)) and value == digest({k: v for k, v in obj.items() if k != field})


def git_first_added(repo: Path, relative_path: str) -> tuple[str, datetime] | None:
    """Git main publication is a custody lower bound, NOT provider first-known."""
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H|%cI", "-1", "--", relative_path],
        cwd=repo, capture_output=True, text=True, check=False, timeout=10,
    )
    line = result.stdout.strip().splitlines()
    if result.returncode or not line or "|" not in line[0]:
        return None
    commit, stamp = line[0].split("|", 1)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        return None
    return commit, utc(stamp)


def write_once(path: Path, record: dict[str, Any]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as f:
            f.write(canonical(record))
        return True
    except FileExistsError:
        # Never rewrite a prior registration, mature outcome or report.
        return False


def registration_path(start_day: str) -> Path:
    return OUTPUT / "registrations" / start_day[:4] / start_day[5:7] / f"{start_day}_OFFICIAL.json"


def evaluate_path(start_day: str) -> Path:
    return OUTPUT / "outcomes" / start_day[:4] / start_day[5:7] / f"{start_day}_72H.json"


def report_path(day: str) -> Path:
    return OUTPUT / "reports" / day[:4] / day[5:7] / f"{day}_KIL_REPORT.json"


def register_latest(repo: Path, now: datetime, activated: datetime, *, dry_run: bool) -> str:
    pointer_path = repo / LATEST
    if not pointer_path.exists():
        return "NO_OFFICIAL_POINTER"
    pointer = read_obj(pointer_path)
    source_relative = pointer.get("compass_path")
    if not isinstance(source_relative, str) or not source_relative.startswith(str(ROOT / "official/daily") + "/"):
        return "SOURCE_PATH_NOT_ALLOWLISTED"
    if ".." in Path(source_relative).parts or not source_relative.endswith(".json"):
        return "SOURCE_PATH_INVALID"
    source_path = repo / source_relative
    if not source_path.is_file():
        return "SOURCE_NOT_FOUND"
    original = read_obj(source_path)
    compass_id = original.get("compass_id")
    if not isinstance(compass_id, str) or not ID_RE.fullmatch(compass_id):
        return "SOURCE_ID_INVALID"
    if source_path.name != compass_id + ".json" or pointer.get("compass_id") != compass_id:
        return "SOURCE_ID_MISMATCH"
    if not validated_self_hash(original, "compass_sha256"):
        return "SOURCE_HASH_INVALID"
    if original["compass_sha256"] != pointer.get("compass_sha256"):
        return "SOURCE_POINTER_MISMATCH"
    if pointer.get("contract") != "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1":
        return "SOURCE_POINTER_CONTRACT_INVALID"
    if original.get("contract") != "OFFICIAL_DAILY_COMPASS_v1":
        return "SOURCE_CONTRACT_INVALID"
    issued = utc(original.get("issued_at_utc"))
    if pointer.get("issued_at_utc") != original.get("issued_at_utc"):
        return "ISSUE_CLOCK_MISMATCH"
    if issued < activated or issued > now or now - issued > MAX_ISSUE_AGE:
        return "NOT_PROSPECTIVE_ELIGIBLE"
    pilot_day = (now.astimezone(COPENHAGEN).date() - activated.astimezone(COPENHAGEN).date()).days
    if pilot_day < 0 or pilot_day >= PILOT_DURATION_DAYS:
        return "PILOT_OUTSIDE_WINDOW"
    original_day = issued.astimezone(COPENHAGEN).date().isoformat()
    now_day = now.astimezone(COPENHAGEN).date().isoformat()
    if now_day != original_day:
        return "NOT_SAME_LOCAL_DAY"
    if registration_path(original_day).is_relative_to(Path(".")) is False:
        return "INVALID_REGISTRATION_PATH"
    if (repo / registration_path(original_day)).exists():
        return "ALREADY_REGISTERED"

    publication = git_first_added(repo, source_relative)
    if publication is None:
        return "SOURCE_GIT_PUBLICATION_UNAVAILABLE"
    first_commit, first_commit_at = publication
    if first_commit_at > now or first_commit_at < activated or first_commit_at > issued + MAX_ISSUE_AGE:
        return "SOURCE_GIT_PUBLICATION_OUT_OF_WINDOW"

    horizon = (original.get("horizons") or {}).get("NEXT_1_3D") or {}
    reference = original.get("market_reference") or {}
    if not isinstance(horizon, dict) or not isinstance(reference, dict):
        return "MISSING_STRUCTURED_72H_SOURCE"
    reference_at_raw = reference.get("source_window_end_utc")
    if reference_at_raw is None:
        start_open = reference.get("observation_open_utc")
        if start_open is None:
            return "MISSING_REFERENCE_CLOCK"
        reference_at = utc(start_open) + timedelta(hours=1)
    else:
        reference_at = utc(reference_at_raw)
    target = reference_at + timedelta(hours=72)
    if not reference_at <= issued < target or first_commit_at >= target:
        return "INVALID_FORECAST_CLOCK"
    direction = horizon.get("expected_direction")
    if direction not in {"UP", "DOWN", "SIDEWAYS", "MIXED", "NO_EDGE", "UNAVAILABLE"}:
        return "UNSUPPORTED_DIRECTION"

    packet = {
        "contract": CONTRACT,
        "registration_scope": "OFFICIAL_72H_STRUCTURED_SOURCE_ONLY",
        "chat_analyst_interpretation": "NOT_CAPTURED_NOT_SCORED",
        "independent_challenger": "NOT_ISSUED",
        "original_compass_id": compass_id,
        "source_path": source_relative,
        "source_compass_sha256": original["compass_sha256"],
        "source_git_initial_commit": first_commit,
        "source_repo_committed_at_utc": iso(first_commit_at),
        "first_known_attestation": "GIT_INITIAL_COMMIT_ONLY_PROVIDER_FIRST_KNOWN_UNKNOWN",
        "original_issued_at_utc": iso(issued),
        "registered_at_utc": iso(now),
        "start_reference_at_utc": iso(reference_at),
        "target_at_utc": iso(target),
        "source_data_status": original.get("data_status"),
        "decision_policy_version": original.get("decision_policy_version"),
        "official_action": original.get("action_now"),
        "official_72h_direction": direction,
        "official_72h_action_posture": horizon.get("action_posture"),
        "official_72h_expected_path": horizon.get("expected_path"),
        "official_72h_eta": horizon.get("eta"),
        "official_protection_status": ((original.get("protection_tracker") or {}).get("state")),
        "authority": {
            "research_only": True,
            "automatic_promotion": False,
            "portfolio_execution": False,
            "forecast_rewrite": False,
            "assistant_narrative_claim_scoring": False,
            "independent_predictive_edge_established": False,
        },
    }
    packet["registration_sha256"] = digest(packet)
    if dry_run:
        return "WOULD_REGISTER"
    return "REGISTERED" if write_once(repo / registration_path(original_day), packet) else "ALREADY_REGISTERED"


def evaluate_one(repo: Path, reg_path: Path, now: datetime, *, dry_run: bool) -> str:
    reg = read_obj(reg_path)
    if reg.get("contract") != CONTRACT or not validated_self_hash(reg, "registration_sha256"):
        return "INVALID_REGISTRATION"
    target = utc(reg.get("target_at_utc"))
    if now < target:
        return "PENDING_72H"
    date = utc(reg["original_issued_at_utc"]).date()
    # Official outcome directory is indexed by UTC forecast issuance, not local registration day.
    out_rel = ROOT / "official/outcomes" / f"{date:%Y/%m/%d}" / (reg["original_compass_id"] + "_72h.json")
    original_outcome = repo / out_rel
    if not original_outcome.exists():
        return "PENDING_OFFICIAL_OUTCOME"
    outcome = read_obj(original_outcome)
    if outcome.get("contract") != "OFFICIAL_DAILY_COMPASS_OUTCOME_v1":
        return "OUTCOME_CONTRACT_INVALID"
    if not validated_self_hash(outcome, "outcome_sha256"):
        return "OUTCOME_DIGEST_INVALID"
    if outcome.get("compass_id") != reg.get("original_compass_id") or outcome.get("compass_sha256") != reg.get("source_compass_sha256"):
        return "OUTCOME_SOURCE_MISMATCH"
    if outcome.get("horizon") != "72h" or outcome.get("scoring_contract") != "OFFICIAL_DAILY_COMPASS_SCORING_v3":
        return "OUTCOME_SCORING_INCOMPATIBLE"
    if utc(outcome.get("target_at_utc")) != target:
        return "OUTCOME_TARGET_MISMATCH"
    matured = utc(outcome.get("matured_at_utc"))
    observed_end = utc(outcome.get("target_source_window_end_utc"))
    if matured < target or observed_end > matured or matured > now:
        return "OUTCOME_CLOCK_INVALID"
    if (outcome.get("time_basis") or {}).get("status") != "PASS":
        return "OUTCOME_TIME_BASIS_INELIGIBLE"

    local_day = utc(reg["original_issued_at_utc"]).astimezone(COPENHAGEN).date().isoformat()
    if (repo / evaluate_path(local_day)).exists():
        return "ALREADY_EVALUATED"
    review = {
        "contract": OUTCOME_CONTRACT,
        "registration_path": reg_path.relative_to(repo).as_posix(),
        "registration_sha256": reg["registration_sha256"],
        "original_compass_id": reg["original_compass_id"],
        "original_issued_at_utc": reg["original_issued_at_utc"],
        "target_at_utc": reg["target_at_utc"],
        "matured_at_utc": iso(matured),
        "reviewed_at_utc": iso(now),
        "official_outcome_path": out_rel.as_posix(),
        "official_outcome_sha256": outcome["outcome_sha256"],
        "direction_accuracy": outcome.get("direction_accuracy"),
        "realized": outcome.get("realized"),
        "persistence_baseline": (outcome.get("baselines") or {}).get("persistence"),
        "action_utility": outcome.get("action_utility"),
        "analyst_interpretation_verdict": "NOT_EVALUABLE_NO_PROSPECTIVE_CHAT_RECEIPT",
        "sequence_and_turning_point_verdict": "NOT_EVALUABLE_NO_ISSUED_STRUCTURED_SEQUENCE_TARGET",
        "warning_timeliness_verdict": "DEFER_TO_EXISTING_M6_OWNER",
        "economic_edge": "NOT_PROVEN_FROM_PROXY_ACTION_UTILITY",
        "authority": {"research_only": True, "no_new_official_score": True, "automatic_promotion": False, "portfolio_execution": False},
    }
    review["review_sha256"] = digest(review)
    if dry_run:
        return "WOULD_EVALUATE"
    return "EVALUATED" if write_once(repo / evaluate_path(local_day), review) else "ALREADY_EVALUATED"


def report(repo: Path, now: datetime, activated: datetime, *, dry_run: bool) -> str:
    local_now = now.astimezone(COPENHAGEN)
    start = activated.astimezone(COPENHAGEN).date()
    day = (local_now.date() - start).days
    if not (day >= 3 and day <= PILOT_DURATION_DAYS and day % 3 == 0 and local_now.hour >= 12):
        return "REPORT_NOT_DUE"
    report_day = local_now.date().isoformat()
    if (repo / report_path(report_day)).exists():
        return "REPORT_EXISTS"
    cutoff = now - timedelta(days=14)
    reviews = []
    for path in sorted((repo / OUTPUT / "outcomes").rglob("*_72H.json")):
        r = read_obj(path)
        if r.get("contract") != OUTCOME_CONTRACT or not validated_self_hash(r, "review_sha256"):
            continue
        issued = utc(r["original_issued_at_utc"])
        if cutoff <= issued <= now:
            reviews.append(r)
    reviews.sort(key=lambda r: r["original_issued_at_utc"])
    # Three-day windows overlap heavily. Non-overlap N is a transparent descriptive
    # count, NOT a proof that market episodes or BTC/ETH observations are independent.
    non_overlap = []
    last_target = None
    for r in reviews:
        issued = utc(r["original_issued_at_utc"])
        if last_target is None or issued >= last_target:
            non_overlap.append(r["original_compass_id"])
            last_target = utc(r["target_at_utc"])
    btc = [r.get("direction_accuracy", {}).get("btc", {}) for r in reviews]
    eth = [r.get("direction_accuracy", {}).get("eth", {}) for r in reviews]
    def group(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {state: sum(x.get("result") == state for x in rows) for state in ("CORRECT", "INCORRECT", "ABSTAINED", "UNAVAILABLE")}
    doc = {
        "contract": REPORT_CONTRACT,
        "report_at_utc": iso(now),
        "local_report_date": report_day,
        "pilot_day": day,
        "review_window_days": 14,
        "registered_72h_reviews": len(reviews),
        "nonoverlapping_72h_windows_count": len(non_overlap),
        "nonoverlapping_example_ids": non_overlap[:20],
        "official_72h_direction_btc_descriptive": group(btc),
        "official_72h_direction_eth_descriptive": group(eth),
        "source_receipts": [{"original_compass_id": r["original_compass_id"],
                             "review_sha256": r["review_sha256"],
                             "registration_sha256": r["registration_sha256"]} for r in reviews],
        "qualitative_interpretation_score": "UNAVAILABLE_NO_REGISTERED_CHAT_ANALYST_CLAIMS",
        "investor_incremental_edge": "UNPROVEN",
        "scientific_note": "Repeated/overlapping BTC-ETH and 72h outcomes are correlated. These counts are descriptive, not calibrated skill, forecast accuracy of chat analysis, or portfolio return.",
        "forward_learning_decision": "OBSERVE_ONLY_NO_AUTO_POLICY_CHANGE",
        "authority": {"automatic_model_reweighting": False, "automatic_promotion": False, "portfolio_execution": False},
    }
    doc["report_sha256"] = digest(doc)
    if dry_run:
        return "WOULD_REPORT"
    return "REPORTED" if write_once(repo / report_path(report_day), doc) else "REPORT_EXISTS"


def run(repo: Path, now: datetime, *, dry_run: bool = False, activated_at: datetime | None = None) -> dict[str, Any]:
    activation = activated_at
    if activation is None:
        evidence = git_first_added(repo, SCRIPT_PATH)
        if evidence is None:
            return {"contract": "KIL_RUN_v1", "status": "BLOCKED_NO_MAIN_ACTIVATION", "register": None, "report": None, "evaluations": {}}
        activation = evidence[1]
    if activation > now:
        return {"contract": "KIL_RUN_v1", "status": "PENDING_ACTIVATION", "register": None, "report": None, "evaluations": {}}
    registration = register_latest(repo, now, activation, dry_run=dry_run)
    evaluations: dict[str, int] = {}
    for path in sorted((repo / OUTPUT / "registrations").rglob("*_OFFICIAL.json")):
        state = evaluate_one(repo, path, now, dry_run=dry_run)
        evaluations[state] = evaluations.get(state, 0) + 1
    report_status = report(repo, now, activation, dry_run=dry_run)
    return {"contract": "KIL_RUN_v1", "status": "RESEARCH_ONLY",
            "activated_at_utc": iso(activation), "register": registration,
            "evaluations": evaluations, "report": report_status,
            "chat_analyst_interpretation": "NOT_CAPTURED",
            "automatic_promotion": False, "portfolio_execution": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--now-utc")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    now = utc(args.now_utc) if args.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    print(json.dumps(run(args.repo_root, now, dry_run=args.dry_run), sort_keys=True))


if __name__ == "__main__":
    main()
