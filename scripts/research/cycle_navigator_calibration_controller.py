#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "05_CYCLE_NAVIGATOR" / "autonomous_calibration_v1"
POLICY_PATH = BASE / "POLICY.json"
STATE_PATH = BASE / "STATE.json"
ACTION_LEDGER = BASE / "ACTION_LEDGER.csv"
ACTION_DIR = BASE / "research_actions"
FORWARD_LEDGER = ROOT / "05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl"
PROMOTION_PACKET = BASE / "PROMOTION_CANDIDATE.json"


def _truthy(value: Any) -> bool:
    return str(value).strip().upper() in {"1", "TRUE", "YES", "Y"}


def _number(value: Any) -> Optional[float]:
    try:
        text = str(value).strip()
        if not text:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _verified(row: Dict[str, str]) -> bool:
    if str(row.get("publication_ts", "")).upper().startswith("EXAMPLE"):
        return False
    if str(row.get("forecast_id", "")).upper().endswith("EXAMPLE_BTC"):
        return False
    if _number(row.get("actual_low")) is None or _number(row.get("actual_high")) is None:
        return False
    status = str(row.get("actual_verification_status", "")).strip().upper()
    if status and status not in {"PASS", "VERIFIED", "COMPLETE", "SETTLED", "SETTLED_COMPLETE", "OK"}:
        return False
    if not status and not (str(row.get("actual_source", "")).strip() and str(row.get("actual_verified_ts", "")).strip()):
        return False
    return True


def _row_identity(row: Dict[str, str]) -> str:
    return "|".join([
        str(row.get("forecast_id", "")),
        str(row.get("publication_ts", "")),
        str(row.get("actual_verified_ts", "")),
        str(row.get("actual_low", "")),
        str(row.get("actual_high", "")),
        str(row.get("range_score", "")),
        str(row.get("timing_score", "")),
        str(row.get("rotation_score", "")),
    ])


def evidence_fingerprint(rows: List[Dict[str, str]], promotion: Optional[Dict[str, Any]] = None) -> str:
    payload = {"rows": [_row_identity(r) for r in rows], "promotion": promotion or {}}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _explicit_promotion_ready(promotion: Optional[Dict[str, Any]], eligible_n: int) -> bool:
    if not promotion or promotion.get("ready") is not True:
        return False
    required = int(promotion.get("minimum_verified_rows", 10**9))
    return eligible_n >= required and promotion.get("prospective_review_required", True) is True


def evaluate_rows(policy: Dict[str, Any], all_rows: List[Dict[str, str]], promotion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    rows = [r for r in all_rows if _verified(r)]
    floors = policy["research_escalation_floors"]
    min_review = int(floors["minimum_verified_rows_for_review"])
    min_pattern = int(floors["minimum_verified_rows_for_persistent_pattern"])
    recent_n = int(floors["recent_comparison_window_rows"])
    latest = rows[-1] if rows else {}
    notes_blob = " ".join(
        " ".join(str(r.get(k, "")) for k in ("notes", "structure_label", "scenario_label", "kill_flags"))
        for r in rows[-recent_n:]
    ).upper()

    if _explicit_promotion_ready(promotion, len(rows)):
        action, reason = "CANONICAL_REVIEW_JUSTIFIED", "explicit prospective-safe promotion packet met its own evidence floor"
    elif "SLOW_BLEED" in notes_blob or "SLOW-BLEED" in notes_blob:
        action, reason = "INVESTIGATE_SLOW_BLEED_FAKE_ROTATION", "existing ledger text explicitly identifies a slow-bleed calibration case"
    elif "SPIKE" in notes_blob or "GRIND" in notes_blob:
        action, reason = "AUDIT_GATE_CROSS_SIGNATURE", "existing ledger text explicitly identifies a spike/grind signature"
    elif rows and _truthy(latest.get("reanchor_shadow_flag")):
        action, reason = "STRESS_TEST_REANCHOR", "latest verified row carries the existing reanchor shadow flag"
    else:
        recent = rows[-recent_n:]
        comparison_losses = 0
        for r in recent:
            a15 = _number(r.get("adjustment_alpha_vs_DUMB15"))
            a20 = _number(r.get("adjustment_alpha_vs_DUMB20"))
            if a15 is not None and a20 is not None and a15 < 0 and a20 < 0:
                comparison_losses += 1
        if len(rows) >= min_review and comparison_losses >= min(2, len(recent)):
            action, reason = "INVESTIGATE_RANGE_MISS", "recent verified CN rows underperform both preregistered dumb ATR baselines"
        elif len(rows) >= min_review and any(_truthy(r.get("transition_watch_flag")) for r in recent):
            action, reason = "AUDIT_TRANSITION_FAKEOUT", "existing transition-watch flags are present in verified review rows"
        elif len(rows) >= min_pattern:
            action, reason = "RESEARCH_NEW_PHASE_HYPOTHESIS", "enough verified rows exist for bounded hypothesis research without changing canonical semantics"
        elif len(rows) >= min_review:
            action, reason = "REVIEW_CALIBRATION_EVIDENCE", "minimum verified research-review floor reached"
        else:
            action, reason = "CONTINUE_CALIBRATION", "insufficient verified forward rows for escalation"

    fp = evidence_fingerprint(rows, promotion)
    latest_id = str(latest.get("forecast_id", "")) if latest else ""
    latest_ts = str(latest.get("actual_verified_ts") or latest.get("publication_ts") or "") if latest else ""
    return {
        "contract": "CYCLE_NAVIGATOR_AUTONOMOUS_CALIBRATION_DECISION_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "selected_action": action,
        "reason": reason,
        "eligible_verified_row_n": len(rows),
        "latest_forecast_id": latest_id,
        "latest_observation_ts": latest_ts,
        "evidence_fingerprint": fp,
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
    }


def _load_rows(policy: Dict[str, Any]) -> List[Dict[str, Any]]:
    # The policy must identify the live, append-only freeze ledger. Never fall
    # back to the example CSV, or interpret a missing source as empty evidence.
    if policy.get("source_ledger") != FORWARD_LEDGER.relative_to(ROOT).as_posix():
        raise ValueError("unexpected forward ledger policy")
    with FORWARD_LEDGER.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _coverage_v2(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    intervals = {"weekly": (0, 7), "day_1_2": (0, 2),
                 "day_3_4": (2, 4), "day_5_7": (4, 7)}
    valid_status = {"FROZEN_PROSPECTIVE", "ISSUED_AFTER_WINDOW_START",
                    "RECOVERED_FROM_IMMUTABLE_PROSPECTIVE_PUBLICATION"}
    clocks, prospective_clocks, windows, prospective_windows = set(), set(), set(), set()
    weeks, prospective_weeks = set(), set()
    prospective_n, missing_clock_n = 0, 0
    for row in rows:
        if not isinstance(row, dict) or row.get("contract") != "CN_FORWARD_RANGE_FREEZE_v2":
            raise ValueError("invalid v2 freeze contract")
        week = row.get("forecast_week")
        window, status = row.get("window"), row.get("status")
        if (not isinstance(week, str) or not re.fullmatch(r"[0-9]{4}-W[0-9]{2}", week)
                or window not in intervals or status not in valid_status
                or row.get("asset") not in {"BTC", "ETH"}):
            raise ValueError("invalid v2 freeze identity")
        monday = date.fromisocalendar(int(week[:4]), int(week[-2:]), 1)
        low, high = row.get("forecast_low"), row.get("forecast_high")
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in (low, high)) or not 0 < low <= high:
            raise ValueError("invalid v2 forecast bounds")
        start, stop = intervals[window]
        interval = (monday + timedelta(days=start), monday + timedelta(days=stop))
        weeks.add(week)
        windows.add(interval)
        clock = row.get("generated_unix")
        if clock is None:
            missing_clock_n += 1
        elif type(clock) is int and clock > 0:
            clocks.add(clock)
        else:
            raise ValueError("invalid v2 freeze clock")
        if status == "FROZEN_PROSPECTIVE":
            if clock is None:
                raise ValueError("prospective freeze missing clock")
            prospective_n += 1
            prospective_clocks.add(clock)
            prospective_weeks.add(week)
            prospective_windows.add(interval)

    def nonoverlap(windows: set) -> int:
        # Earliest finish is maximum-cardinality interval scheduling. Assets
        # and repeated forecasts sharing the same window do not add episodes.
        last, count = date.min, 0
        for start, stop in sorted(windows, key=lambda w: (w[1], w[0])):
            if start >= last:
                count += 1
                last = stop
        return count

    return {
        "raw_rows": len(rows),
        "unique_recorded_freeze_clocks": len(clocks),
        "missing_freeze_clock_rows": missing_clock_n,
        "calendar_week_clusters": len(weeks),
        "max_nonoverlapping_calendar_windows": nonoverlap(windows),
        "labelled_prospective_rows": prospective_n,
        "labelled_prospective_unique_clocks": len(prospective_clocks),
        "labelled_prospective_calendar_week_clusters": len(prospective_weeks),
        "labelled_prospective_max_nonoverlapping_windows": nonoverlap(prospective_windows),
        "scientific_eligibility": "UNADMITTED_FREEZE_LEDGER_ONLY",
        "independence_attested": False,
    }


def evaluate_v2_freezes(policy: Dict[str, Any], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Freeze rows do not establish verified actuals or baseline score custody.
    # Do not accept even plausible outcome fields injected into freeze rows.
    result = evaluate_rows(policy, [], None)
    result["source_coverage_v2"] = _coverage_v2(rows)
    result["reason"] = "live freeze ledger read; no independently admitted baseline/outcome join"
    result["evidence_fingerprint"] = hashlib.sha256(
        json.dumps(rows, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()
    ).hexdigest()
    return result


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _existing_action_ids() -> set:
    if not ACTION_LEDGER.exists():
        return set()
    with ACTION_LEDGER.open(newline="", encoding="utf-8") as f:
        return {r.get("action_id", "") for r in csv.DictReader(f)}


def _persist(decision: Dict[str, Any]) -> str:
    BASE.mkdir(parents=True, exist_ok=True)
    ACTION_DIR.mkdir(parents=True, exist_ok=True)
    action_id = hashlib.sha256((decision["selected_action"] + "|" + decision["evidence_fingerprint"]).encode()).hexdigest()[:20]
    state = dict(decision)
    state["contract"] = "CYCLE_NAVIGATOR_AUTONOMOUS_CALIBRATION_STATE_v1"
    state["status"] = "ACTIVE"
    state["action_id"] = action_id

    old_state = _load_json(STATE_PATH, {})
    if old_state != state:
        STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if action_id not in _existing_action_ids():
        packet = dict(decision)
        packet["action_id"] = action_id
        (ACTION_DIR / f"{action_id}.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        exists = ACTION_LEDGER.exists() and ACTION_LEDGER.stat().st_size > 0
        with ACTION_LEDGER.open("a", newline="", encoding="utf-8") as f:
            fields = ["action_id", "selected_action", "evidence_fingerprint", "eligible_row_n", "latest_forecast_id", "latest_observation_ts", "canonical_effect"]
            writer = csv.DictWriter(f, fieldnames=fields)
            if not exists:
                writer.writeheader()
            writer.writerow({
                "action_id": action_id,
                "selected_action": decision["selected_action"],
                "evidence_fingerprint": decision["evidence_fingerprint"],
                "eligible_row_n": decision["eligible_verified_row_n"],
                "latest_forecast_id": decision["latest_forecast_id"],
                "latest_observation_ts": decision["latest_observation_ts"],
                "canonical_effect": "false",
            })
    return action_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    policy = _load_json(POLICY_PATH, {})
    if policy.get("authority") != "RESEARCH_ONLY_NON_CANONICAL" or policy.get("canonical_effect") is not False:
        raise SystemExit("policy firewall invalid")
    decision = evaluate_v2_freezes(policy, _load_rows(policy))
    if args.dry_run:
        print(json.dumps(decision, indent=2, sort_keys=True))
        return 0
    action_id = _persist(decision)
    print(json.dumps({"action_id": action_id, **decision}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
