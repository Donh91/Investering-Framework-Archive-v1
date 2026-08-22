#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "00_ARCHIVE_CONTROL/source_recovery_controller_v1"
POLICY_PATH = BASE / "POLICY.json"
STATE_PATH = BASE / "STATE.json"
LEDGER_PATH = BASE / "ACTION_LEDGER.csv"
ACTION_DIR = BASE / "research_actions"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _walk(obj: Any) -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k), v
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _value_text(obj: Any) -> str:
    values: List[str] = []
    for _, value in _walk(obj):
        if isinstance(value, (str, int, float, bool)):
            values.append(str(value))
    return " ".join(values).upper()


def _key_values(obj: Any, wanted: Iterable[str]) -> List[Any]:
    wanted_set = {w.lower() for w in wanted}
    return [v for k, v in _walk(obj) if k.lower() in wanted_set]


def _any_true(obj: Any, keys: Iterable[str]) -> bool:
    for v in _key_values(obj, keys):
        if v is True or str(v).strip().upper() in {"TRUE", "YES", "1"}:
            return True
    return False


def _any_false(obj: Any, keys: Iterable[str]) -> bool:
    for v in _key_values(obj, keys):
        if v is False or str(v).strip().upper() in {"FALSE", "NO", "0"}:
            return True
    return False


def _numeric_zero(obj: Any, keys: Iterable[str]) -> bool:
    for v in _key_values(obj, keys):
        try:
            if float(v) == 0:
                return True
        except (TypeError, ValueError):
            pass
    return False


def classify_receipt(policy: Dict[str, Any], receipt_path: str, receipt: Dict[str, Any]) -> Dict[str, Any]:
    text = _value_text(receipt)
    status_text = " ".join(str(v).upper() for v in _key_values(receipt, [
        "status", "state", "conclusion", "classification", "interpretation",
        "provider_runtime_failure", "error", "reason", "enrichment_run_conclusion_at_receipt",
        "verification_status"
    ]))
    transform_status_text = " ".join(str(v).upper() for v in _key_values(receipt, [
        "transform_status", "transform_result", "transform_conclusion"
    ]))

    explicit_not_testable = "NOT_TESTABLE" in text or "NOT TESTABLE" in text
    terminal_no_rows = (
        ("TERMINAL" in status_text or _any_true(receipt, ["terminal"]))
        and (_numeric_zero(receipt, ["returned_row_count", "row_count", "rows_returned"]) or _any_true(receipt, ["no_fill"]))
    )
    stop_retry = _any_true(receipt, [
        "no_additional_paid_retry_authorized", "no_additional_retry_authorized", "stop_retrying", "retry_terminal"
    ]) or "TERMINAL_PROVIDER" in status_text
    stale = _any_true(receipt, ["stale", "source_stale", "is_stale"]) or "STALE" in status_text
    transform_failure = (
        bool(transform_status_text) and any(tok in transform_status_text for tok in ("FAIL", "INVALID", "ERROR", "BROKEN"))
    ) or _any_true(receipt, ["transform_failed", "transform_invalid"])
    approved_free_source = bool(_key_values(receipt, [
        "approved_free_source", "approved_free_alternative_source", "approved_free_alternative_sources"
    ]))
    free_retry = _any_true(receipt, ["free_retry_authorized", "retry_same_owner_authorized"]) or (
        _any_true(receipt, ["retry_authorized"]) and not _any_true(receipt, ["paid_retry", "paid_data_required"])
    )
    bounded_gapfill = _any_true(receipt, ["bounded_gapfill_authorized", "gapfill_authorized"]) and (
        _numeric_zero(receipt, ["cost", "expected_cost", "paid_cost"]) or _any_false(receipt, ["paid", "paid_data_required"])
    )
    paid_needed = _any_true(receipt, [
        "paid_data_required", "paid_gapfill_requested", "paid_gapfill_required", "requires_paid_data", "paid_retry"
    ])
    unresolved_failure = any(tok in status_text for tok in ("FAIL", "ERROR", "INVALID", "UNRESOLVED")) or bool(
        _key_values(receipt, ["provider_runtime_failure"])
    )

    if explicit_not_testable or terminal_no_rows:
        action, reason = "DECLARE_NOT_TESTABLE", "receipt explicitly establishes non-testability or terminal zero-row evidence"
    elif stop_retry:
        action, reason = "STOP_RETRYING", "receipt explicitly closes further retry authority or marks provider terminal"
    elif stale:
        action, reason = "QUARANTINE_STALE_SOURCE", "receipt explicitly marks source/evidence stale"
    elif transform_failure:
        action, reason = "REPAIR_TRANSFORM", "receipt explicitly identifies transform failure/invalidity"
    elif approved_free_source:
        action, reason = "CROSSCHECK_APPROVED_FREE_SOURCE", "receipt names a separately approved free alternative source"
    elif free_retry:
        action, reason = "RETRY_SAME_OWNER", "receipt explicitly authorizes a free same-owner retry"
    elif bounded_gapfill:
        action, reason = "REQUEST_BOUNDED_GAPFILL", "receipt explicitly authorizes bounded non-paid gapfill research"
    elif paid_needed:
        action, reason = "GENERATE_PAID_DATA_VOI_PACKET", "receipt says paid data may be required; controller may only create a VOI packet"
    elif unresolved_failure:
        action, reason = "VERIFY_PROVENANCE", "receipt contains unresolved provider/source failure without stronger authorized recovery semantics"
    else:
        action, reason = "CONTINUE_SOURCE_MONITORING", "receipt contains no explicit condition authorizing stronger recovery action"

    return {
        "receipt_path": receipt_path,
        "selected_action": action,
        "reason": reason,
        "canonical_effect": False,
        "portfolio_execution": False,
        "external_provider_calls_authorized": False,
        "paid_data_authorized": False,
        "proxy_substitution_authorized": False,
        "interpolation_authorized": False,
    }


def _discover_receipts(policy: Dict[str, Any]) -> List[Dict[str, Any]]:
    found: Dict[str, Dict[str, Any]] = {}
    for pattern in policy.get("receipt_globs", []):
        for path in ROOT.glob(pattern):
            if not path.is_file() or path.suffix.lower() != ".json":
                continue
            rel = path.relative_to(ROOT).as_posix()
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {"status": "INVALID_JSON", "error": "JSON_PARSE_FAILURE"}
            if not isinstance(data, dict):
                continue
            content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            found[rel] = {"path": rel, "data": data, "content_hash": content_hash}
    return [found[k] for k in sorted(found)]


def evaluate_receipts(policy: Dict[str, Any], entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    priority = {name: i for i, name in enumerate(policy["priority"])}
    queue: List[Dict[str, Any]] = []
    for entry in entries:
        item = classify_receipt(policy, entry["path"], entry["data"])
        item["content_hash"] = entry.get("content_hash") or hashlib.sha256(
            json.dumps(entry["data"], sort_keys=True).encode()
        ).hexdigest()
        queue.append(item)
    queue.sort(key=lambda x: (priority.get(x["selected_action"], 999), x["receipt_path"]))
    actionable = [q for q in queue if q["selected_action"] != "CONTINUE_SOURCE_MONITORING"]
    primary = actionable[0] if actionable else (queue[0] if queue else {
        "receipt_path": "NONE", "selected_action": "CONTINUE_SOURCE_MONITORING",
        "reason": "no configured machine-readable receipts were discovered", "content_hash": "NONE",
        "canonical_effect": False, "portfolio_execution": False, "external_provider_calls_authorized": False,
        "paid_data_authorized": False, "proxy_substitution_authorized": False, "interpolation_authorized": False
    })
    fingerprint_payload = [
        {"path": q["receipt_path"], "action": q["selected_action"], "content_hash": q["content_hash"]}
        for q in queue
    ]
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode()).hexdigest()
    return {
        "contract": "SOURCE_PROVENANCE_RECOVERY_DECISION_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "selected_action": primary["selected_action"],
        "target_receipt": primary["receipt_path"],
        "reason": primary["reason"],
        "receipt_n": len(queue),
        "actionable_receipt_n": len(actionable),
        "action_queue": queue,
        "evidence_fingerprint": fingerprint,
        "canonical_effect": False,
        "portfolio_execution": False,
        "external_provider_calls_authorized": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
        "proxy_substitution_authorized": False,
        "interpolation_authorized": False,
    }


def _existing_ids() -> set:
    if not LEDGER_PATH.exists():
        return set()
    with LEDGER_PATH.open(newline="", encoding="utf-8") as f:
        return {r.get("action_id", "") for r in csv.DictReader(f)}


def persist(decision: Dict[str, Any]) -> str:
    BASE.mkdir(parents=True, exist_ok=True)
    ACTION_DIR.mkdir(parents=True, exist_ok=True)
    raw = decision["selected_action"] + "|" + decision["target_receipt"] + "|" + decision["evidence_fingerprint"]
    action_id = hashlib.sha256(raw.encode()).hexdigest()[:20]
    state = dict(decision)
    state["contract"] = "SOURCE_PROVENANCE_RECOVERY_STATE_v1"
    state["status"] = "ACTIVE"
    state["action_id"] = action_id
    old = _load_json(STATE_PATH, {})
    if old != state:
        STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if action_id not in _existing_ids():
        packet = dict(decision); packet["action_id"] = action_id
        if decision["selected_action"] == "GENERATE_PAID_DATA_VOI_PACKET":
            packet["voi_gate"] = {
                "paid_data_authorized": False,
                "requires_separate_explicit_authorization": True,
                "controller_spend": 0
            }
        (ACTION_DIR / f"{action_id}.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        exists = LEDGER_PATH.exists() and LEDGER_PATH.stat().st_size > 0
        with LEDGER_PATH.open("a", newline="", encoding="utf-8") as f:
            fields = ["action_id", "selected_action", "target_receipt", "evidence_fingerprint", "actionable_receipt_n", "paid_data_authorized", "canonical_effect"]
            writer = csv.DictWriter(f, fieldnames=fields)
            if not exists: writer.writeheader()
            writer.writerow({
                "action_id": action_id,
                "selected_action": decision["selected_action"],
                "target_receipt": decision["target_receipt"],
                "evidence_fingerprint": decision["evidence_fingerprint"],
                "actionable_receipt_n": decision["actionable_receipt_n"],
                "paid_data_authorized": "false",
                "canonical_effect": "false"
            })
    return action_id


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); args = ap.parse_args()
    policy = _load_json(POLICY_PATH, {})
    if policy.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise SystemExit("source recovery authority invalid")
    if any(policy.get(k) is not False for k in (
        "canonical_effect", "external_provider_calls_authorized", "automatic_paid_data_authorization",
        "automatic_proxy_substitution", "automatic_interpolation"
    )):
        raise SystemExit("source recovery firewall invalid")
    decision = evaluate_receipts(policy, _discover_receipts(policy))
    if args.dry_run:
        print(json.dumps(decision, indent=2, sort_keys=True)); return 0
    action_id = persist(decision)
    print(json.dumps({"action_id": action_id, **decision}, indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
