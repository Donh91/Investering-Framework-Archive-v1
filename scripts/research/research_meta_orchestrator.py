#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib, re, subprocess
from pathlib import Path
from typing import Any, Dict, List
from research_governance_common import ROOT, GOV, load_json, specialist_states, specialist_binding_report, action_of, target_of, evidence_fp, digest, persist_json, append_csv

BASE=GOV/"meta_orchestrator_v1"
POLICY=BASE/"POLICY.json"
STATE=BASE/"STATE.json"
QUEUE=BASE/"EXECUTION_QUEUE.json"
LEDGER=BASE/"ACTION_LEDGER.csv"
MEMORY=GOV/"memory_novelty_v1/STATE.json"
VOI=GOV/"decision_impact_v1/STATE.json"
SENTINEL=GOV/"adversarial_sentinel_v1/STATE.json"

CANONICAL_REVIEW_ACTIONS={"PROMOTE_FOR_CANONICAL_REVIEW","CANONICAL_REVIEW_JUSTIFIED"}
DATA_ACTIONS={"REPAIR_TRANSFORM","QUARANTINE_STALE_SOURCE","VERIFY_PROVENANCE","CROSSCHECK_APPROVED_FREE_SOURCE","RETRY_SAME_OWNER","REQUEST_BOUNDED_GAPFILL"}
FREEZE_ACTIONS={"OPEN_PROSPECTIVE_FORWARD_TEST","FREEZE_NEW_CHALLENGER"}

def _memory_for(memory,source,action,target):
    for r in memory.get("proposal_results",[]):
        if r.get("source")==source and r.get("action")==action and r.get("target")==target:
            return r.get("novelty_verdict")
    return None

def _default_binding_report(states):
    return {
        "contract":"RESEARCH_GOVERNANCE_SPECIALIST_BINDING_REPORT_v1_SYNTHETIC",
        "expected_sources":sorted(states),
        "bindings":{k:{"mode":"PRIMARY_READY"} for k in states},
        "missing_primary_sources":[],
        "missing_all_sources":[],
        "complete_primary":True,
        "resolvable":True,
        "binding_integrity":"PRIMARY_COMPLETE",
    }

def orchestrate(policy:Dict[str,Any], states:Dict[str,Dict[str,Any]], memory:Dict[str,Any], voi:Dict[str,Any], sentinel:Dict[str,Any], binding_report:Dict[str,Any]|None=None) -> Dict[str,Any]:
    binding_report = binding_report or _default_binding_report(states)
    sv=sentinel.get("verdict","PASS")
    conflicts=[]
    rawq=voi.get("queue",[])
    for i,a in enumerate(rawq):
        for b in rawq[i+1:]:
            ta=str(a.get("target") or "").strip().lower(); tb=str(b.get("target") or "").strip().lower()
            if ta and ta==tb:
                aa=str(a.get("action") or ""); ab=str(b.get("action") or "")
                if ({aa,ab} & CANONICAL_REVIEW_ACTIONS) and ({aa,ab} & {"DEPRIORITIZE","ARCHIVE_UNTESTABLE","STOP_RETRYING"}):
                    conflicts.append({"target":ta,"source_a":a.get("source"),"action_a":aa,"source_b":b.get("source"),"action_b":ab})
    if conflicts:
        sv="BLOCK_RESEARCH_ESCALATION"

    if sv in {"FIREWALL_BREACH","BLOCK_RESEARCH_ESCALATION"}:
        primary={
            "orchestrator_action":"HALT_ESCALATION_AND_AUDIT","source":"ADVERSARIAL_SENTINEL",
            "target":sv,"execution_mode":"AUTO_LOCAL_RESEARCH",
            "reason":"adversarial sentinel blocks escalation until governance finding is resolved",
            "impact_tier":"HIGH",
        }
        queue=[primary]
    elif not binding_report.get("resolvable", True):
        missing=",".join(binding_report.get("missing_all_sources") or [])
        primary={
            "orchestrator_action":"WAIT_FOR_BINDING_COMPLETENESS","source":"GOVERNANCE_BINDING",
            "target":missing or "UNKNOWN_BINDING","execution_mode":"AUTO_OBSERVE",
            "reason":"one or more specialist bindings are completely unavailable; do not infer absence of research work",
            "impact_tier":"BLOCKED",
        }
        queue=[primary]
    elif not binding_report.get("complete_primary", True):
        missing=",".join(binding_report.get("missing_primary_sources") or [])
        primary={
            "orchestrator_action":"WAIT_FOR_BINDING_COMPLETENESS","source":"GOVERNANCE_BINDING",
            "target":missing or "PRIMARY_STATE_PENDING","execution_mode":"AUTO_OBSERVE",
            "reason":"one or more primary specialist states are not yet materialized; fallback status may be observed but research escalation remains paused",
            "impact_tier":"LOW",
        }
        queue=[primary]
    else:
        queue=[]
        for item in voi.get("queue",[]):
            source=item.get("source"); action=item.get("action"); target=item.get("target")
            tier=item.get("impact_tier","LOW")
            novelty=_memory_for(memory,source,action,target)
            if tier=="BLOCKED" or novelty in {"DUPLICATE_EXACT","DUPLICATE_NEAR"}:
                oa="SUPPRESS_DUPLICATE_RESEARCH"; mode="AUTO_LOCAL_RESEARCH"
            elif action in CANONICAL_REVIEW_ACTIONS and tier=="HIGH":
                oa="PREPARE_CANONICAL_REVIEW"; mode="REQUIRES_CANONICAL_REVIEW"
            elif source=="SOURCE_RECOVERY" and action in DATA_ACTIONS and tier=="HIGH":
                oa="PRIORITIZE_DATA_INTEGRITY"; mode="AUTO_LOCAL_RESEARCH"
            elif action=="GENERATE_PAID_DATA_VOI_PACKET":
                oa="QUEUE_VOI_REVIEW"; mode="REQUIRES_VOI_REVIEW"
            elif tier in {"HIGH","MEDIUM"}:
                oa="QUEUE_BOUNDED_RESEARCH"; mode="REQUIRES_PROSPECTIVE_FREEZE" if action in FREEZE_ACTIONS else "AUTO_LOCAL_RESEARCH"
            elif tier=="LOW":
                oa="WAIT_FOR_EVIDENCE"; mode="AUTO_OBSERVE"
            else:
                oa="CONTINUE_MONITORING"; mode="AUTO_OBSERVE"
            queue.append({
                "orchestrator_action":oa,"source":source,"specialist_action":action,"target":target,
                "impact_tier":tier,"decision_surface":item.get("decision_surface"),
                "execution_mode":mode,"novelty_verdict":novelty,
                "reason":item.get("reason",""),"evidence_fingerprint":item.get("evidence_fingerprint",""),
                "canonical_effect":False,"portfolio_execution":False,"paid_data_authorized":False,
            })
        rank={
            "PREPARE_CANONICAL_REVIEW":0,"PRIORITIZE_DATA_INTEGRITY":1,"QUEUE_BOUNDED_RESEARCH":2,
            "QUEUE_VOI_REVIEW":3,"SUPPRESS_DUPLICATE_RESEARCH":4,"WAIT_FOR_EVIDENCE":5,"CONTINUE_MONITORING":6,
        }
        queue.sort(key=lambda x:(rank.get(x["orchestrator_action"],99), {"HIGH":0,"MEDIUM":1,"LOW":2,"NONE":3,"BLOCKED":4}.get(x.get("impact_tier"),9), str(x.get("source"))))
        primary=queue[0] if queue else {
            "orchestrator_action":"WAIT_FOR_EVIDENCE","source":"NONE","target":"NONE",
            "execution_mode":"AUTO_OBSERVE","reason":"all configured specialist primary states are present and no actionable research proposal is active","impact_tier":"LOW"
        }

    maxheavy=int(policy.get("max_concurrent_heavy_workstreams",1))
    active=[]
    if binding_report.get("complete_primary", True) and sv not in {"FIREWALL_BREACH","BLOCK_RESEARCH_ESCALATION"}:
        for q in queue:
            if q["orchestrator_action"] in {"PREPARE_CANONICAL_REVIEW","PRIORITIZE_DATA_INTEGRITY","QUEUE_BOUNDED_RESEARCH","QUEUE_VOI_REVIEW"}:
                if len(active)<maxheavy: active.append(q)
    return {
        "contract":"RESEARCH_META_ORCHESTRATOR_STATE_v1",
        "authority":"RESEARCH_ONLY_NON_CANONICAL",
        "primary_action":primary["orchestrator_action"],"primary_source":primary.get("source"),
        "primary_target":primary.get("target"),"primary_execution_mode":primary.get("execution_mode"),
        "reason":primary.get("reason"),"queue":queue,"queue_n":len(queue),
        "active_heavy_workstreams":active,"max_concurrent_heavy_workstreams":maxheavy,
        "sentinel_verdict":sv,"controller_conflicts":conflicts,
        "binding_integrity":binding_report.get("binding_integrity","UNKNOWN"),
        "binding_report":binding_report,
        "evidence_fingerprint":digest({"memory":memory,"voi":voi,"sentinel":sentinel,"states":states,"bindings":binding_report}),
        "canonical_effect":False,"portfolio_execution":False,"paid_data_authorized":False,
        "deep_research_authorized":False,"external_provider_calls_authorized":False,
    }


SPECIALIST_QUEUE_REL="04_RESEARCH_LAB/external_specialist_dissection/QUEUE_V1.json"
SPECIALIST_NOTES_DIR="04_RESEARCH_LAB/external_specialist_dissection/"
INTAKE_ID_RE=re.compile(r"^[A-Z][A-Z0-9_]{5,100}$")
MAX_METHOD_INTAKES=20


def _git_bytes(root:Path,*args:str)->bytes|None:
    try:
        p=subprocess.run(["git","-C",str(root),*args],stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL,check=False,timeout=12)
        return p.stdout if p.returncode==0 else None
    except (OSError,subprocess.SubprocessError):
        return None


def _main_checkout_verified(root:Path)->bool:
    """Only a clean source checkout at the advertised public origin/main may admit notes.

    This is not a PR-merge detector on its own: the exact tracked bytes and
    source queue are independently compared with committed main below.
    """
    top=_git_bytes(root,"rev-parse","--show-toplevel")
    head=_git_bytes(root,"rev-parse","HEAD")
    main=_git_bytes(root,"rev-parse","refs/remotes/origin/main")
    return (bool(top and head and main) and
            Path(top.decode().strip()).resolve()==root.resolve() and
            head.strip()==main.strip())


def specialist_intake_handoff(root:Path=ROOT)->dict:
    """Observe only immutable public origin/main queue and note bytes.

    A PR checkout, modified worktree note, symlink escape or untracked note
    cannot acquire even low-priority observation eligibility. All rejections
    preserve the existing execution/market authority at zero.
    """
    result={"contract":"RESEARCH_SPECIALIST_INTAKE_HANDOFF_v1",
            "authority":"RESEARCH_ONLY_NON_CANONICAL",
            "source_queue":SPECIALIST_QUEUE_REL,
            "status":"NO_REGISTERED_INTAKES","entries":[],
            "source_notes_verified_as_market_evidence":False,
            "source_license_or_api_admission":False,
            "canonical_effect":False,"portfolio_execution":False,
            "paid_data_authorized":False}
    root=root.resolve()
    queue_file=root/SPECIALIST_QUEUE_REL
    allowed_directory=root/SPECIALIST_NOTES_DIR
    if not queue_file.is_file():
        return {**result,"status":"SOURCE_QUEUE_UNAVAILABLE"}
    if (not queue_file.resolve().is_relative_to(root) or
            not allowed_directory.resolve().is_relative_to(root)):
        return {**result,"status":"SOURCE_QUEUE_OUTSIDE_REPO"}
    if not _main_checkout_verified(root):
        return {**result,"status":"MAIN_CHECKOUT_NOT_VERIFIED"}
    try:
        # The queue itself must be the bytes in the exact main commit.
        queue_bytes=queue_file.read_bytes()
        if _git_bytes(root,"show",f"HEAD:{SPECIALIST_QUEUE_REL}")!=queue_bytes:
            return {**result,"status":"SOURCE_QUEUE_NOT_COMMITTED"}
        source=json.loads(queue_bytes.decode("utf-8"))
        if not isinstance(source,dict):
            return {**result,"status":"INVALID_SOURCE_QUEUE_TYPE"}
        if source.get("contract")!="RESEARCH_LAB_EXTERNAL_SPECIALIST_DISSECTION_QUEUE_V1":
            return {**result,"status":"INVALID_SOURCE_QUEUE_CONTRACT"}
        lanes={x["id"] for x in source.get("lanes",[]) if isinstance(x,dict) and isinstance(x.get("id"),str)}
        raw=source.get("method_intakes",[])
        if not isinstance(raw,list) or len(raw)>MAX_METHOD_INTAKES:
            return {**result,"status":"INVALID_INTAKE_COUNT_OR_TYPE"}
        seen=set()
        for item in raw:
            if not isinstance(item,dict):
                return {**result,"status":"INVALID_INTAKE_ENTRY","entries":[]}
            iid=item.get("id"); owner=item.get("owner_lane"); note=item.get("evidence_note")
            if (not isinstance(iid,str) or not INTAKE_ID_RE.fullmatch(iid) or iid in seen or
                    not isinstance(owner,str) or
                    owner not in lanes|{"TASK2_R1_EXISTING_SOURCE_ADMISSION"} or
                    item.get("execution_permission") is not False or
                    not isinstance(note,str) or not note.startswith(SPECIALIST_NOTES_DIR) or
                    not note.endswith(".md") or ".." in Path(note).parts):
                return {**result,"status":"INVALID_INTAKE_AUTHORITY_OR_PATH","entries":[]}
            seen.add(iid)
            p=(root/note).resolve()
            if not p.is_relative_to(allowed_directory.resolve()) or not p.is_relative_to(root):
                return {**result,"status":"PATH_OUTSIDE_SPECIALIST_PUBLIC_NOTES","entries":[]}
            # One atomic local file read: no has-file/read-hash race.
            try:
                note_bytes=p.read_bytes()
            except OSError:
                note_bytes=None
            committed=_git_bytes(root,"show",f"HEAD:{note}") if note_bytes is not None else None
            verified=(note_bytes is not None and committed is not None and note_bytes==committed)
            sha=hashlib.sha256(note_bytes).hexdigest() if verified else None
            result["entries"].append({
                "id":iid,"owner_lane":owner,"related_lane":item.get("related_lane"),
                "evidence_note":note,"note_sha256":sha,
                "status":"NOTE_PRESENT_NOT_SOURCE_ADMITTED" if verified else "NOTE_NOT_MERGED_OR_MISSING",
                "review_state":item.get("review_state","REVIEW_PENDING"),
                "incremental_value":item.get("incremental_value","UNPROVEN"),
                "source_access":item.get("source_access","UNVERIFIED"),
                "execution_mode":"AUTO_OBSERVE","requires_owner_review":True,
                "market_source_admitted":False,"automatic_promotion":False})
        result["status"]="PUBLIC_NOTES_READ_ONLY" if raw else "NO_REGISTERED_INTAKES"
        return result
    except (OSError,UnicodeError,TypeError,ValueError,KeyError):
        return {**result,"status":"INVALID_OR_UNREADABLE_INTAKE","entries":[]}


def attach_specialist_intakes(state:dict,root:Path=ROOT)->dict:
    """Add low-priority observations to the EXISTING research queue, never work orders."""
    report=specialist_intake_handoff(root)
    updated={**state,"specialist_intake_handoff":report}
    if (report["status"]!="PUBLIC_NOTES_READ_ONLY" or
            state.get("sentinel_verdict")!="PASS" or
            state.get("binding_integrity")!="PRIMARY_COMPLETE"):
        return updated
    observations=[]
    for row in report["entries"]:
        if (row["status"]!="NOTE_PRESENT_NOT_SOURCE_ADMITTED" or
                not isinstance(row.get("note_sha256"),str) or len(row["note_sha256"])!=64):
            continue
        observations.append({
            "orchestrator_action":"WAIT_FOR_EVIDENCE",
            "source":"EXTERNAL_SPECIALIST_INTAKE",
            "specialist_action":"EXISTING_OWNER_REVIEW_ONLY",
            "target":row["id"],
            "owner_lane":row["owner_lane"],
            "evidence_note":row["evidence_note"],
            "evidence_fingerprint":row["note_sha256"],
            "impact_tier":"LOW",
            "execution_mode":"AUTO_OBSERVE",
            "reason":"Public method description is not verified independent market evidence",
            "canonical_effect":False,
            "portfolio_execution":False,
            "paid_data_authorized":False,
        })
    # Preserve the existing high-value priority ordering and heavy workstream.
    updated["queue"]=[*state["queue"],*observations]
    updated["queue_n"]=len(updated["queue"])
    updated["evidence_fingerprint"]=digest({
        "prior_fingerprint":state["evidence_fingerprint"],
        "specialist_intake_handoff":report,
    })
    return updated

def persist(state):
    persist_json(STATE,state)
    persist_json(QUEUE,{"contract":"RESEARCH_META_EXECUTION_QUEUE_v1","authority":"RESEARCH_ONLY_NON_CANONICAL","queue":state["queue"],"active_heavy_workstreams":state["active_heavy_workstreams"],"binding_integrity":state["binding_integrity"],"canonical_effect":False})
    aid=hashlib.sha256((state["primary_action"]+"|"+str(state["primary_source"])+"|"+str(state["primary_target"])+"|"+state["evidence_fingerprint"]).encode()).hexdigest()[:20]
    append_csv(LEDGER,["action_id","primary_action","primary_source","primary_target","execution_mode","sentinel_verdict","binding_integrity","evidence_fingerprint","canonical_effect"],{
        "action_id":aid,"primary_action":state["primary_action"],"primary_source":state["primary_source"],
        "primary_target":state["primary_target"],"execution_mode":state["primary_execution_mode"],
        "sentinel_verdict":state["sentinel_verdict"],"binding_integrity":state["binding_integrity"],
        "evidence_fingerprint":state["evidence_fingerprint"],"canonical_effect":"false"
    },"action_id",aid)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    policy=load_json(POLICY,{})
    if policy.get("authority")!="RESEARCH_ONLY_NON_CANONICAL" or any(policy.get(k) is not False for k in ("canonical_effect","automatic_canonical_write","automatic_paid_data_authorization","portfolio_execution")):
        raise SystemExit("meta orchestrator firewall invalid")
    states=specialist_states()
    bindings=specialist_binding_report()
    state=orchestrate(policy,states,load_json(MEMORY,{}),load_json(VOI,{}),load_json(SENTINEL,{}),bindings)
    state=attach_specialist_intakes(state)
    if args.dry_run: print(json.dumps(state,indent=2,sort_keys=True)); return
    persist(state); print(json.dumps(state,indent=2,sort_keys=True))
if __name__=="__main__": main()
