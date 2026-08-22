#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / "00_ARCHIVE_CONTROL" / "research_governance_v1"

SPECIALIST_BINDINGS = {
    "SHARED_ROW": {
        "primary": ROOT / "06_RESEARCH_LAB/shared_row_model_tournament_v1/NEXT_ACTION_STATE.json",
        "fallback": ROOT / "06_RESEARCH_LAB/shared_row_model_tournament_v1/RUNTIME_STATUS.json",
    },
    "CYCLE_NAVIGATOR": {
        "primary": ROOT / "05_CYCLE_NAVIGATOR/autonomous_calibration_v1/STATE.json",
        "fallback": None,
    },
    "SHADOW_REGISTRY": {
        "primary": ROOT / "04_MARKET_LEARNING/shadow_registry/autonomous_portfolio_v1/STATE.json",
        "fallback": None,
    },
    "SOURCE_RECOVERY": {
        "primary": ROOT / "00_ARCHIVE_CONTROL/source_recovery_controller_v1/STATE.json",
        "fallback": None,
    },
}

RESEARCH_PROPOSAL_ACTIONS = {
    "RESEARCH_NEW_HYPOTHESIS", "FREEZE_NEW_CHALLENGER",
    "RESEARCH_NEW_PHASE_HYPOTHESIS", "OPEN_PROSPECTIVE_FORWARD_TEST",
    "RUN_INCREMENTAL_VALUE_TEST", "RUN_REDUNDANCY_CONFIRMATION",
    "STRESS_TEST", "STRESS_TEST_REANCHOR", "STRESS_TEST_REGIME_SPECIFICITY",
    "AUDIT_TRANSITION_FAKEOUT", "AUDIT_GATE_CROSS_SIGNATURE",
    "INVESTIGATE_SLOW_BLEED_FAKE_ROTATION", "INVESTIGATE_RANGE_MISS",
    "INVESTIGATE_DIVERGENCE",
}

AGGRESSIVE_ACTIONS = RESEARCH_PROPOSAL_ACTIONS | {
    "PROMOTE_FOR_CANONICAL_REVIEW", "CANONICAL_REVIEW_JUSTIFIED",
    "GENERATE_PAID_DATA_VOI_PACKET",
}

def load_json(path: Path, default: Any=None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def safe_text(x: Any) -> str:
    if x is None: return ""
    if isinstance(x, (dict, list)):
        return json.dumps(x, sort_keys=True, ensure_ascii=False)
    return str(x)

def normalize_text(text: Any) -> str:
    s = safe_text(text).lower()
    s = re.sub(r"[^a-z0-9æøå_]+", " ", s)
    return " ".join(s.split())

def tokens(text: Any) -> set[str]:
    return {t for t in normalize_text(text).split() if len(t) > 2}

def jaccard(a: Any, b: Any) -> float:
    x, y = tokens(a), tokens(b)
    if not x and not y: return 1.0
    if not x or not y: return 0.0
    return len(x & y) / len(x | y)

def digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()

def specialist_binding_report() -> Dict[str, Any]:
    bindings = {}
    missing_primary = []
    missing_all = []
    for source, cfg in SPECIALIST_BINDINGS.items():
        primary = cfg["primary"]
        fallback = cfg.get("fallback")
        primary_data = load_json(primary, {})
        fallback_data = load_json(fallback, {}) if fallback else {}
        if isinstance(primary_data, dict) and primary_data:
            mode = "PRIMARY_READY"
            selected = primary
        elif fallback and isinstance(fallback_data, dict) and fallback_data:
            mode = "FALLBACK_STATUS_ONLY"
            selected = fallback
            missing_primary.append(source)
        else:
            mode = "MISSING"
            selected = None
            missing_primary.append(source)
            missing_all.append(source)
        bindings[source] = {
            "mode": mode,
            "primary_path": str(primary.relative_to(ROOT)),
            "fallback_path": str(fallback.relative_to(ROOT)) if fallback else None,
            "selected_path": str(selected.relative_to(ROOT)) if selected else None,
        }
    return {
        "contract": "RESEARCH_GOVERNANCE_SPECIALIST_BINDING_REPORT_v1",
        "expected_sources": sorted(SPECIALIST_BINDINGS),
        "bindings": bindings,
        "missing_primary_sources": sorted(missing_primary),
        "missing_all_sources": sorted(missing_all),
        "complete_primary": not missing_primary,
        "resolvable": not missing_all,
        "binding_integrity": (
            "PRIMARY_COMPLETE" if not missing_primary
            else "DEGRADED_PRIMARY_FALLBACK" if not missing_all
            else "BROKEN"
        ),
    }

def specialist_states() -> Dict[str, Dict[str, Any]]:
    report = specialist_binding_report()
    out = {}
    for source, cfg in SPECIALIST_BINDINGS.items():
        b = report["bindings"][source]
        selected = b.get("selected_path")
        if not selected:
            continue
        path = ROOT / selected
        data = load_json(path, {})
        if isinstance(data, dict) and data:
            value = dict(data)
            value["_governance_binding_mode"] = b["mode"]
            value["_governance_binding_path"] = selected
            out[source] = value
    return out

def action_of(state: Dict[str, Any]) -> str:
    return str(state.get("primary_action") or state.get("selected_action") or "").strip().upper()

def target_of(state: Dict[str, Any]) -> str:
    return str(state.get("target") or state.get("target_sensor_id") or state.get("target_receipt") or state.get("latest_forecast_id") or "").strip()

def evidence_fp(state: Dict[str, Any]) -> str:
    return str(state.get("evidence_fingerprint") or state.get("fingerprint") or "").strip()

def reason_of(state: Dict[str, Any]) -> str:
    return str(state.get("reason") or state.get("rationale") or "").strip()

def proposal_from(source: str, state: Dict[str, Any]) -> Dict[str, Any]:
    action = action_of(state)
    target = target_of(state)
    reason = reason_of(state)
    return {
        "source": source,
        "action": action,
        "target": target,
        "reason": reason,
        "evidence_fingerprint": evidence_fp(state),
        "family": str(state.get("family") or state.get("target_family") or ""),
        "authority": state.get("authority"),
        "canonical_effect": bool(state.get("canonical_effect", False)),
        "portfolio_execution": bool(state.get("portfolio_execution", False)),
        "paid_data_authorized": bool(state.get("paid_data_authorized", False)),
        "deep_research_authorized": bool(state.get("deep_research_authorized", False)),
        "external_provider_calls_authorized": bool(state.get("external_provider_calls_authorized", False)),
    }

def current_proposals(states: Dict[str, Dict[str, Any]]|None=None) -> List[Dict[str, Any]]:
    states = states or specialist_states()
    out = []
    for source, state in states.items():
        p = proposal_from(source, state)
        if p["action"] in RESEARCH_PROPOSAL_ACTIONS or p["action"] in {"PROMOTE_FOR_CANONICAL_REVIEW","CANONICAL_REVIEW_JUSTIFIED","GENERATE_PAID_DATA_VOI_PACKET"}:
            out.append(p)
    return sorted(out, key=lambda x:(x["source"],x["action"],x["target"]))

def firewall_flags(obj: Dict[str, Any]) -> List[str]:
    bad=[]
    for k in ("canonical_effect","portfolio_execution","paid_data_authorized","deep_research_authorized","external_provider_calls_authorized","registry_mutation"):
        if obj.get(k) is True:
            bad.append(k)
    auth=obj.get("authority")
    if auth not in (None,"","RESEARCH_ONLY_NON_CANONICAL"):
        bad.append("authority")
    return bad

def persist_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)+"\n", encoding="utf-8")

def append_csv(path: Path, fields: List[str], row: Dict[str, Any], id_field: str, id_value: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    existing=set()
    if path.exists() and path.stat().st_size:
        for r in load_csv(path):
            existing.add(r.get(id_field,""))
    if id_value in existing:
        return False
    exists=path.exists() and path.stat().st_size>0
    with path.open("a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        if not exists: w.writeheader()
        w.writerow({k:row.get(k,"") for k in fields})
    return True
