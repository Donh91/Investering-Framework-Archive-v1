#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, List

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "04_MARKET_LEARNING/shadow_registry/REGISTRY.json"
BASE = ROOT / "04_MARKET_LEARNING/shadow_registry/autonomous_portfolio_v1"
POLICY_PATH = BASE / "POLICY.json"
STATE_PATH = BASE / "STATE.json"
LEDGER_PATH = BASE / "ACTION_LEDGER.csv"
ACTION_DIR = BASE / "research_actions"


def _exists(path: str) -> bool:
    return (ROOT / path).exists()


def sensor_action(sensor: Dict[str, Any], path_exists: Callable[[str], bool]) -> Dict[str, Any]:
    missing = [p for p in sensor.get("evidence_paths", []) if not path_exists(p)]
    relevance = str(sensor.get("relevance_state", "WATCH")).upper()
    evaluator = str(sensor.get("evaluator", "")).upper()
    sensor_id = str(sensor.get("sensor_id", "UNKNOWN"))

    if missing:
        action, reason = "RECOVER_EVIDENCE_PATH", "one or more registered evidence paths are absent"
    elif evaluator == "NONE_RECOVERY_REQUIRED":
        action, reason = "RECOVER_EVALUATOR", "registered source material exists but exact evaluator recovery is still required"
    elif relevance == "PROMOTION_CANDIDATE":
        action, reason = "OPEN_PROSPECTIVE_FORWARD_TEST", "registry marks sensor as promotion candidate; direct promotion remains forbidden"
    elif relevance == "REDUNDANT":
        action, reason = "RUN_REDUNDANCY_CONFIRMATION", "registry marks sensor redundant and requires confirmation before retirement"
    elif sensor.get("incremental_value_ready") is True:
        action, reason = "RUN_INCREMENTAL_VALUE_TEST", "sensor explicitly declares readiness for incremental-value testing"
    elif relevance == "REGIME_SPECIFIC":
        action, reason = "STRESS_TEST_REGIME_SPECIFICITY", "registry marks sensor regime-specific"
    elif relevance == "NOISE":
        action, reason = "DEPRIORITIZE", "registry marks sensor as noise"
    elif relevance == "UNTESTABLE":
        action, reason = "ARCHIVE_UNTESTABLE", "registry marks sensor scientifically untestable"
    else:
        action, reason = "CONTINUE_OBSERVING", "no stronger research action is justified by registered state"

    return {
        "sensor_id": sensor_id,
        "family": sensor.get("family"),
        "selected_action": action,
        "reason": reason,
        "missing_evidence_paths": missing,
        "relevance_state": relevance,
        "evaluator": sensor.get("evaluator"),
        "canonical_effect": False,
    }


def evaluate_registry(policy: Dict[str, Any], registry: Dict[str, Any], path_exists: Callable[[str], bool] = _exists) -> Dict[str, Any]:
    priority = {name: i for i, name in enumerate(policy["priority"])}
    queue = [sensor_action(s, path_exists) for s in registry.get("sensors", [])]
    queue.sort(key=lambda x: (priority.get(x["selected_action"], 999), x["sensor_id"]))
    actionable = [q for q in queue if q["selected_action"] != "CONTINUE_OBSERVING"]
    primary = actionable[0] if actionable else (queue[0] if queue else {
        "sensor_id": "NONE", "selected_action": "CONTINUE_OBSERVING", "reason": "registry contains no sensors", "missing_evidence_paths": [], "canonical_effect": False
    })
    fp_payload = [{k: q.get(k) for k in ("sensor_id", "selected_action", "missing_evidence_paths", "relevance_state", "evaluator")} for q in queue]
    fingerprint = hashlib.sha256(json.dumps(fp_payload, sort_keys=True).encode()).hexdigest()
    return {
        "contract": "SHADOW_REGISTRY_AUTONOMOUS_PORTFOLIO_DECISION_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "selected_action": primary["selected_action"],
        "target_sensor_id": primary["sensor_id"],
        "reason": primary["reason"],
        "actionable_sensor_n": len(actionable),
        "sensor_n": len(queue),
        "action_queue": queue,
        "evidence_fingerprint": fingerprint,
        "registry_mutation": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
    }


def _load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _existing_ids() -> set:
    if not LEDGER_PATH.exists():
        return set()
    with LEDGER_PATH.open(newline="", encoding="utf-8") as f:
        return {r.get("action_id", "") for r in csv.DictReader(f)}


def persist(decision: Dict[str, Any]) -> str:
    BASE.mkdir(parents=True, exist_ok=True)
    ACTION_DIR.mkdir(parents=True, exist_ok=True)
    raw = decision["selected_action"] + "|" + decision["target_sensor_id"] + "|" + decision["evidence_fingerprint"]
    action_id = hashlib.sha256(raw.encode()).hexdigest()[:20]
    state = dict(decision)
    state["contract"] = "SHADOW_REGISTRY_AUTONOMOUS_PORTFOLIO_STATE_v1"
    state["status"] = "ACTIVE"
    state["action_id"] = action_id
    old = _load(STATE_PATH, {})
    if old != state:
        STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if action_id not in _existing_ids():
        packet = dict(decision); packet["action_id"] = action_id
        (ACTION_DIR / f"{action_id}.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        exists = LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0
        with LEDGER_PATH.open("a", newline="", encoding="utf-8") as f:
            fields = ["action_id", "selected_action", "target_sensor_id", "evidence_fingerprint", "actionable_sensor_n", "canonical_effect"]
            writer = csv.DictWriter(f, fieldnames=fields)
            if not exists: writer.writeheader()
            writer.writerow({
                "action_id": action_id,
                "selected_action": decision["selected_action"],
                "target_sensor_id": decision["target_sensor_id"],
                "evidence_fingerprint": decision["evidence_fingerprint"],
                "actionable_sensor_n": decision["actionable_sensor_n"],
                "canonical_effect": "false",
            })
    return action_id


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); args = ap.parse_args()
    policy = _load(POLICY_PATH, {})
    if policy.get("authority") != "RESEARCH_ONLY_NON_CANONICAL" or policy.get("registry_mutation_forbidden") is not True:
        raise SystemExit("shadow portfolio policy firewall invalid")
    registry = _load(REGISTRY, {"sensors": []})
    decision = evaluate_registry(policy, registry)
    if args.dry_run:
        print(json.dumps(decision, indent=2, sort_keys=True)); return 0
    action_id = persist(decision)
    print(json.dumps({"action_id": action_id, **decision}, indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
