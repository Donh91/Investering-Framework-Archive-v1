from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path, default: Any) -> Any:
    if not path.exists(): return default
    try: return json.loads(path.read_text())
    except Exception: return default


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def evidence_exists(root: Path, capability: str, field: str) -> tuple[bool, str]:
    if capability == "STABLECOIN_LIQUIDITY":
        latest = root / "03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json"
        history = root / "03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/backfill/global_history.jsonl.gz"
        return latest.exists() and history.exists(), "stablecoin_latest_plus_historical_backfill"
    if capability == "LIVE_BREADTH":
        latest = root / "03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json"
        return latest.exists(), "rich_breadth_prospective_checkpoint"
    if capability == "PULLBACK_FORENSICS":
        latest = root / "03_DAILY_CAPTURE_LOGS/pullback_forensics/LATEST.json"
        return latest.exists(), "pullback_forensics_prospective_capture"
    if capability == "SETTLED_ETF":
        latest = root / "03_DAILY_CAPTURE_LOGS/etf/LATEST.json"
        return latest.exists(), "settled_etf_archive"
    if capability == "HOURLY_SEQUENCE":
        hourly = root / "03_DAILY_CAPTURE_LOGS/hourly"
        return hourly.exists() and any(hourly.rglob("*.csv")), "hourly_sequence_archive"
    if capability == "FRED_MACRO":
        captures = root / "03_DAILY_CAPTURE_LOGS/captures"
        return captures.exists(), "retained_capture_archive"
    if capability == "EXISTING_REPO_DERIVATION":
        return False, "metric_specific_provenance_required"
    return False, "no_deterministic_evidence_probe"


def reconcile_item(root: Path, item: dict[str, Any], caps: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    capability = str(item.get("capability_hint") or "UNKNOWN_SOURCE")
    field = item.get("known_field_hint")
    cap = caps.get(capability) if isinstance(caps.get(capability), dict) else {}
    known_fields = cap.get("known_fields") if isinstance(cap.get("known_fields"), list) else []
    if not isinstance(field, str) or field not in known_fields:
        return str(item.get("closure_state") or "SOURCE_DISCOVERY_REQUIRED"), {"verified": False, "reason": "NO_EXACT_KNOWN_FIELD_BINDING"}
    exists, probe = evidence_exists(root, capability, field)
    if not exists:
        return str(item.get("closure_state") or "DETECTED"), {"verified": False, "reason": "EVIDENCE_NOT_YET_PRESENT", "probe": probe}
    if capability in {"LIVE_BREADTH", "PULLBACK_FORENSICS"}:
        return "PROSPECTIVE_CAPTURE_ACTIVE", {"verified": True, "probe": probe, "historical_gap": "UNKNOWN_UNLESS_SEPARATELY_BACKFILLED"}
    if capability == "STABLECOIN_LIQUIDITY":
        return "CLOSED", {"verified": True, "probe": probe, "historical_backfill": True}
    if capability in {"HOURLY_SEQUENCE", "SETTLED_ETF", "FRED_MACRO"}:
        return "DERIVABLE_FROM_EXISTING_ARCHIVE", {"verified": True, "probe": probe, "automatic_derivation_allowed": True}
    return str(item.get("closure_state") or "DETECTED"), {"verified": False, "reason": "NO_CLOSURE_RULE"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--capabilities", type=Path, required=True)
    ap.add_argument("--queue", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    registry = load(args.registry, {"items": {}}); capability_doc = load(args.capabilities, {"capabilities": {}}); caps = capability_doc.get("capabilities", {})
    items = registry.get("items") if isinstance(registry.get("items"), dict) else {}; changed=[]; timestamp=now_utc()
    for gap_id, item in list(items.items()):
        if not isinstance(item, dict): continue
        old = str(item.get("closure_state") or "DETECTED")
        if old in {"CLOSED", "ALREADY_COVERED"}: continue
        new, verification = reconcile_item(args.repo_root, item, caps)
        item["closure_verification"] = verification
        if new != old:
            item["closure_state"] = new; item["closure_state_updated_at_utc"] = timestamp; changed.append({"gap_id":gap_id,"from":old,"to":new})
    registry["updated_at_utc"] = timestamp; write(args.registry, registry)
    actionable={"BACKFILL_QUEUED","PROSPECTIVE_CAPTURE_REQUIRED","SOURCE_DISCOVERY_REQUIRED"}
    queue_items=[v for v in items.values() if isinstance(v,dict) and v.get("closure_state") in actionable]
    queue_items.sort(key=lambda r:(-int(r.get("observation_count",0) or 0),str(r.get("first_seen_utc",""))))
    queue={"contract":"ADAPTIVE_EVIDENCE_GAP_QUEUE_v1_2","generated_at_utc":timestamp,"items":queue_items,"rules":["Only exact known-field bindings may be deterministically reconciled.","Prospective evidence never retroactively fills an unavailable historical period.","Unknown-source items remain source-discovery research tasks."]}; write(args.queue,queue)
    receipt={"contract":"ADAPTIVE_EVIDENCE_GAP_CLOSURE_RECEIPT_v1","created_at_utc":timestamp,"changed":changed,"registry_item_count":len(items),"remaining_actionable_count":len(queue_items),"authority":{"market_rule_change":False,"threshold_change":False,"weight_change":False,"canonical_state":False,"portfolio_action":False,"self_merge":False}}; write(args.receipt,receipt)
    print(json.dumps({"status":"PASS","changed":len(changed),"remaining_actionable":len(queue_items)},sort_keys=True))

if __name__ == "__main__": main()
