#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

ROUTES={"SELF_HEAL_SAFE","DETERMINISTIC_REPAIR","SOURCE_OWNER","SPECIALIST_AGENT","RESEARCH_EXPERIMENT","CODEX_REQUIRED","GOVERNANCE_REVIEW","WAIT_FOR_EVIDENCE","HUMAN_AUTHORITY","NO_ACTION"}

def read(p, default=None):
    try: return json.loads(p.read_text()) if p.exists() else default
    except Exception: return default

def read_frozen_snapshot(p):
    if not p.exists():
        return None
    text=p.read_text()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Legacy W40 FINAL was written with a literal trailing "\\n".
        # Accept only that exact historical writer defect without mutating frozen evidence.
        if text.endswith("\\n"):
            try:
                return json.loads(text[:-2])
            except json.JSONDecodeError:
                pass
        return None

def write_json(p, doc):
    p.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")

def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest()[:20]

def finding(module,severity,route,reason,evidence,owner,next_action,stop,gate,confidence="MEDIUM"):
    assert route in ROUTES
    core={"module":module,"severity":severity,"route":route,"reason":reason,"evidence_refs":evidence,"owner":owner}
    return {**core,"fingerprint":h(core),"dedup_key":h({"m":module,"r":reason,"o":owner}),"root_cause_confidence":confidence,
            "cheapest_sufficient_executor":"DETERMINISTIC" if route in {"SELF_HEAL_SAFE","DETERMINISTIC_REPAIR","NO_ACTION","WAIT_FOR_EVIDENCE"} else "OWNER_OR_SPECIALIST",
            "next_action":next_action,"stop_condition":stop,"acceptance_gate":gate}

def surgical_source_findings(root):
    """Bounded, read-only FSA source-contract scan; never an alternative market owner."""
    pointer_path = "04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json"
    pointer = read(root / pointer_path, {})
    path = pointer.get("packet_path") if isinstance(pointer, dict) else None
    def unavailable():
        return [finding("DATA_EVIDENCE_INTEGRITY", "HIGH", "SOURCE_OWNER",
            "FSA auto-market packet binding unavailable or invalid",
            [pointer_path], "#1827", "verify original pointer and self-digest",
            "stop if a newer verified packet supersedes the observation", "EXACT_PACKET_DIGEST_AND_LINEAGE", "HIGH")]
    if not isinstance(path, str) or not re.fullmatch(
        r"04_MARKET_LEARNING/entry_signals/auto_market_state/runs/\d{4}/\d{2}/\d{2}/\d{6}_[0-9a-f]{12}\.json", path):
        return unavailable()
    packet = read(root / path, {})
    if not isinstance(packet, dict):
        return unavailable()
    try:
        payload = (json.dumps({k:v for k,v in packet.items() if k != "packet_sha256"},
            sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()
    except (ValueError, TypeError):
        return unavailable()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != packet.get("packet_sha256") or digest != pointer.get("packet_sha256"):
        return unavailable()
    def get(value, *keys):
        for key in keys:
            if not isinstance(value, dict):
                return None
            value = value.get(key)
        return value
    def numeric(value):
        return type(value) in (int, float) and math.isfinite(value)
    checks = [
        ("hourly_market", get(packet,"source_health","hourly_market","row","status") == "PASS"
         and all(numeric(get(packet,"normalized_state","live_market",k))
                 and get(packet,"normalized_state","live_market",k) > 0
                 for k in ("btc_usdt","eth_usdt","ethbtc")),
         "FSA hourly PASS without valid exact row or required prices"),
        ("altseason_context", get(packet,"normalized_state","altseason_context","blockchaincenter_altcoin_season","status") == "PASS"
         and numeric(get(packet,"normalized_state","altseason_context","blockchaincenter_altcoin_season","horizons","90","published_score"))
         and 0 <= get(packet,"normalized_state","altseason_context","blockchaincenter_altcoin_season","horizons","90","published_score") <= 100,
         "FSA altseason PASS without valid BlockchainCenter 90d"),
    ]
    findings = []
    for lane, complete, reason in checks:
        if get(packet, "source_health", lane, "status") == "PASS" and not complete:
            findings.append(finding("DATA_EVIDENCE_INTEGRITY","HIGH","SOURCE_OWNER",reason,
                [pointer_path,path],"#1827","dedup existing PR then reproduce and repair producer contract",
                "stop if existing PR covers defect or newer verified producer/consumer has corrected it",
                "EXACT_SOURCE_NEGATIVE_TEST_AND_NATURAL_CONSUMER_READBACK","HIGH"))
    return findings

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--output-root",default="research/framework_learning/weekly_forensics"); ap.add_argument("--mode",choices=["PRELIMINARY","FINAL"],default="FINAL"); ap.add_argument("--as-of-utc"); a=ap.parse_args()
    root=Path(a.repo_root); out=root/a.output_root
    now=datetime.fromisoformat(a.as_of_utc.replace("Z","+00:00")) if a.as_of_utc else datetime.now(timezone.utc)
    local=now.astimezone(ZoneInfo("Europe/Copenhagen"))
    target=local-timedelta(days=1) if a.mode=="FINAL" and local.weekday()==0 else local
    y,w,_=target.isocalendar(); gen=now.isoformat().replace("+00:00","Z")
    paths={
      "pullback":root/"04_MARKET_LEARNING/pullback_learning/LATEST.json",
      "eligibility":root/"04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json",
      "automation":root/"research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
      "architecture":root/"research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json",
      "remediation":root/"research/remediation/LATEST_REMEDIATION_QUEUE.json",
      "compounding":root/"00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json",
      "phase1":root/"research/framework_intelligence/phase1/LATEST.json",
    }
    src={k:read(p,{}) or {} for k,p in paths.items()}; findings=surgical_source_findings(root)

    pb=src["pullback"]; elig=src["eligibility"]
    suspended=(str(pb.get("eligibility_status",{}).get("status","")).startswith("SUSPENDED") or str(elig.get("status","")).startswith("SUSPENDED"))
    if suspended:
      findings.append(finding("PULLBACK_REENTRY","HIGH","GOVERNANCE_REVIEW","pullback episode eligibility is suspended; descriptive learning may continue but episode creation/maturation must remain blocked",
        ["04_MARKET_LEARNING/pullback_learning/LATEST.json","04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json"],"PULLBACK_ELIGIBILITY_OWNER",
        "resolve the existing eligibility-owner contract without inventing episodes or bypassing suspension","stop if a valid superseding eligibility contract already exists","VALID_ELIGIBILITY_CONTRACT_PLUS_EXISTING_PULLBACK_TESTS", "HIGH"))
    obs=pb.get("observation_count")
    findings.append(finding("PULLBACK_REENTRY","INFO","WAIT_FOR_EVIDENCE",f"preserve point-in-time pullback observations for weekly descriptive and near-miss learning; observation_count={obs}",
      ["04_MARKET_LEARNING/pullback_learning/LATEST.json"],"PULLBACK_LEARNING_LEDGER","continue observation collection and evaluate only fields available at observation time","stop if provenance/timestamps are incomplete","POINT_IN_TIME_PROVENANCE_PRESENT"))

    auto=src["automation"]; red=auto.get("red_count"); amber=auto.get("amber_count")
    blockers=auto.get("blockers") or []
    if red or blockers:
      findings.append(finding("META_HEALTH","HIGH","DETERMINISTIC_REPAIR",f"automation health contains active RED/blocker evidence (red={red}, amber={amber}, blockers={len(blockers)})",
        ["research/architecture_health/LATEST_AUTOMATION_HEALTH.json","research/remediation/LATEST_REMEDIATION_QUEUE.json"],"REMEDIATION_MATURATION",
        "deduplicate against the existing remediation queue and route only unresolved reproducible signatures","stop when finding is absent, superseded, already fixed, or requires semantic/budget change","EXISTING_TASK_SPECIFIC_POST_FIX_GATE","HIGH"))

    phase=src["phase1"]
    if phase.get("would_offer_to_master_monday") and not phase.get("live_consumed"):
      findings.append(finding("CONSUMPTION_HEALTH","MEDIUM","SOURCE_OWNER","high-value advisory evidence exists but is intentionally/not yet consumed by Master Monday",
        ["research/framework_intelligence/phase1/LATEST.json"],"FRAMEWORK_LEARNING_SUPERVISOR","carry only a compact advisory delta; do not grant live authority","stop if phase gate forbids consumption","MASTER_MONDAY_ADVISORY_FIREWALL_PASS"))

    comp=src["compounding"]; families=comp.get("hypothesis_families") or []
    matured=sum(int(x.get("matured_outcome_count_total") or 0) for x in families if isinstance(x,dict))
    findings.append(finding("LEARNING_MATURATION","INFO","NO_ACTION",f"weekly maturation snapshot: families={len(families)}, matured_outcomes={matured}",
      ["00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json"],"COMPOUNDING_LEARNING_CONTROLLER","retain delta-only learning and negative memory; no automatic promotion","stop if source authority is not research-only","NO_CANONICAL_PROMOTION"))

    missing=[str(p.relative_to(root)) for p in paths.values() if not p.exists()]
    if missing:
      findings.append(finding("DATA_EVIDENCE_INTEGRITY","HIGH","SOURCE_OWNER","required weekly evidence inputs are missing",
        missing,"FRAMEWORK_LEARNING_SUPERVISOR","restore or explicitly quarantine missing evidence; never coerce UNKNOWN to zero/false","stop if missing inputs are optional under current phase","REQUIRED_INPUTS_PRESENT_OR_EXPLICITLY_QUARANTINED","HIGH"))

    actionable=[x for x in findings if x["route"] not in {"NO_ACTION","WAIT_FOR_EVIDENCE"}]
    doc={"contract":"WEEKLY_FORENSICS_PACK_v1","authority":"RESEARCH_ONLY_NON_CANONICAL","mode":a.mode,"generated_at_utc":gen,"iso_year":y,"iso_week":w,
         "canonical_effect":False,"portfolio_execution":False,"automatic_market_semantic_change":False,"automatic_budget_guard_change":False,"automatic_promotion":False,
         "point_in_time_required":True,"unknown_is_not_zero":True,"existing_remediation_queue_is_sole_repair_queue":True,
         "modules":["PULLBACK_REENTRY","FORECAST_DECISION","ROTATION_TRANSMISSION","META_HEALTH","LEARNING_MATURATION","DATA_EVIDENCE_INTEGRITY"],
         "findings":findings,"actionable_count":len(actionable),"routing_contract":sorted(ROUTES),
         "master_monday_delta":{"authority":"ADVISORY_ONLY","source_iso_year":y,"source_iso_week":w,"source_mode":a.mode,"items":[{"module":x["module"],"severity":x["severity"],"reason":x["reason"],"route":x["route"]} for x in actionable[:8]]}}
    out.mkdir(parents=True,exist_ok=True); write_json(out/"LATEST.json",doc)
    snap=out/"snapshots"/str(y)/f"W{w:02d}"; snap.mkdir(parents=True,exist_ok=True); snapfile=snap/f"{a.mode}.json"
    if a.mode=="FINAL" and snapfile.exists():
      frozen=read_frozen_snapshot(snapfile) or {}
      if frozen.get("contract")=="WEEKLY_FORENSICS_PACK_v1":
        doc=frozen
        write_json(out/"LATEST.json",doc)
      else: raise SystemExit("FINAL_FREEZE_CONTRACT_INVALID")
    else: write_json(snapfile,doc)
    print(json.dumps({"status":"PASS","mode":a.mode,"findings":len(findings),"actionable":len(actionable)}))
if __name__=="__main__": main()
