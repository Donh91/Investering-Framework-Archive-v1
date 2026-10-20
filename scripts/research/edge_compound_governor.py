#!/usr/bin/env python3
"""Deterministic EDGE Compound Governor. Research-routing only, zero market authority."""
from __future__ import annotations
import argparse,hashlib,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Any

CONTRACT="EDGE_COMPOUND_GOVERNOR_v1"
AUTHORITY={"market_state_change":False,"portfolio_action":False,"sell":False,"trim":False,"threshold_change":False,"canonical_promotion":False,"automatic_external_dispatch":False}
PATHS={
 "compass_pointer":Path("04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json"),
 "m6_events":Path("research/framework_memory/m6_warning_events/LATEST.json"),
 "edge_features":Path("research/framework_memory/edge001_tsunami_features/LATEST.json"),
 "calibration":Path("research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json"),
 "task15_gate":Path("04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK_1_5_EDGE_ADMISSION_GATE_v1.json"),
}

def canon(v:Any)->bytes:
    return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()

def digest(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def file_sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def read_json(path:Path):
    try:return json.loads(path.read_text())
    except Exception:return None

def load(root:Path,key:str):
    rel=PATHS[key];p=root/rel
    if not p.exists():return None,{"path":rel.as_posix(),"status":"MISSING","sha256":None}
    value=read_json(p)
    return value,{"path":rel.as_posix(),"status":"PASS" if isinstance(value,dict) else "INVALID_JSON","sha256":file_sha(p)}

def task15_advisory(gate:dict|None,binding:dict):
    """Fail-closed research-only readback: cannot affect collection, decisions or actions."""
    source_status=binding.get("status")
    base={"source_status":source_status,"source_sha256":binding.get("sha256"),
          "market_authority":False,"automatic_promotion":False,
          "collection_policy_change":False}
    if not isinstance(gate,dict):
        return {**base,"status":"NOT_LOADED_NOT_ADMITTED","declared_research_status":None}
    permissions=gate.get("permissions")
    valid=(gate.get("contract")=="EDGE_TASK_1_5_ADMISSION_GATE_v1"
           and isinstance(permissions,dict)
           and permissions.get("continue_existing_market_data_collection") is True
           and permissions.get("allow_official_model_weight_change") is False
           and permissions.get("allow_trade_or_sell_signal") is False
           and permissions.get("allow_historical_pullback_economic_claim") is False
           and permissions.get("allow_legacy_censor_rewrite") is False
           and gate.get("task15_closure_allowed") is False)
    if not valid:
        return {**base,"status":"INVALID_NONBINDING_RESEARCH_GATE","declared_research_status":None}
    upstream=gate.get("status")
    # A missing, non-string or novel status is NOT a valid research gate.
    # Unknown research results must never be disguised as reviewed pending.
    if type(upstream) is not str or upstream not in (
        "BLOCKED_SCIENTIFIC_CLOSURE", "UNREVIEWED"
    ):
        return {**base,"status":"INVALID_NONBINDING_RESEARCH_GATE","declared_research_status":None}
    state=("BLOCKED_RESEARCH_PREFLIGHT" if upstream=="BLOCKED_SCIENTIFIC_CLOSURE"
           else "UNREVIEWED_RESEARCH_ONLY")
    return {**base,"status":state,"declared_research_status":upstream}

def freeze_from_pointer(root:Path,pointer:dict|None):
    if not isinstance(pointer,dict):return None,None
    raw=pointer.get("compass_path")
    if not isinstance(raw,str) or not raw:return None,None
    p=root/raw
    if not p.exists():return None,{"path":raw,"status":"MISSING"}
    j=read_json(p);return j,{"path":raw,"status":"PASS" if isinstance(j,dict) else "INVALID_JSON","sha256":file_sha(p)}

def matured_counts(m6:dict|None):
    horizons=("24h","72h","7d","14d","30d")
    out={h:0 for h in horizons};families={h:set() for h in horizons}
    unknown={h:0 for h in horizons}
    if not isinstance(m6,dict):return out,{h:0 for h in horizons},unknown
    events=m6.get("events")
    if not isinstance(events,list):
        return out,{h:0 for h in horizons},unknown
    for e in events:
        if not isinstance(e,dict):continue
        fid=e.get("episode_family_id")
        payload=e.get("horizons")
        if not isinstance(payload,dict):continue
        for h in horizons:
            row=payload.get(h)
            if not isinstance(row,dict):continue
            state=row.get("maturity_state")
            if state=="MATURED":
                out[h]+=1
                if fid:families[h].add(fid)
            elif isinstance(state,str) and state.startswith("UNKNOWN"):
                unknown[h]+=1
    return out,{h:len(families[h]) for h in horizons},unknown

def m6_integrity(m6:dict|None, features:dict|None):
    """Validate chronological/typed identity and 1:N feature cohort parity, fail-closed."""
    events=(m6 or {}).get("events") if isinstance(m6,dict) else None
    rows=(features or {}).get("rows") if isinstance(features,dict) else None
    if not isinstance(events,list) or not isinstance(rows,list):
        return {"status":"UNKNOWN_MISSING_OWNER","chronological":False,"family_anchor_valid":False,
                "first_warning_weight_valid":False,"feature_cohort_parity":False,"family_lineage_fingerprint":None}
    parsed=[]
    for e in events:
        if not isinstance(e,dict) or not isinstance(e.get("knowledge_timestamp"),str):
            return {"status":"INVALID_EVENT","chronological":False,"family_anchor_valid":False,
                    "first_warning_weight_valid":False,"feature_cohort_parity":False,"family_lineage_fingerprint":None}
        try:
            when=datetime.fromisoformat(e["knowledge_timestamp"].replace("Z","+00:00"))
        except ValueError:
            return {"status":"INVALID_TIME","chronological":False,"family_anchor_valid":False,
                    "first_warning_weight_valid":False,"feature_cohort_parity":False,"family_lineage_fingerprint":None}
        parsed.append((when,e))
    chronological=all(a[0]<=b[0] for a,b in zip(parsed,parsed[1:]))
    grouped={}
    for when,e in parsed:
        grouped.setdefault(e.get("episode_family_id"),[]).append((when,e))
    anchors=True
    weights=True
    for family,grp in grouped.items():
        if not isinstance(family,str) or family!=("M6F-"+min(ts for ts,_ in grp).strftime("%Y%m%dT%H%M%SZ")):
            anchors=False
        ordered=sorted(grp,key=lambda item:(item[0],str(item[1].get("compass_id") or "")))
        if [r.get("independent_family_weight") for _,r in ordered]!=[1.0]+[0.0]*(len(ordered)-1):
            weights=False
    event_cohort=[(e.get("compass_id"),e.get("knowledge_timestamp")) for _,e in parsed]
    feature_cohort=[(r.get("compass_id"),r.get("knowledge_timestamp")) for r in rows if isinstance(r,dict)]
    # Reject malformed IDs deterministically; never crash on mixed/null types.
    valid_ids=all(isinstance(a,str) and a and isinstance(b,str) and b for a,b in event_cohort+feature_cohort)
    parity=(valid_ids and len(event_cohort)==len(feature_cohort) and
            sorted(event_cohort)==sorted(feature_cohort))
    lineage=[(e.get("compass_id"),e.get("knowledge_timestamp"),e.get("episode_family_id"),e.get("independent_family_weight")) for _,e in parsed]
    return {"status":"PASS" if chronological and anchors and weights and parity else "BLOCKED",
            "chronological":chronological,"family_anchor_valid":anchors,
            "first_warning_weight_valid":weights,"feature_cohort_parity":parity,
            "family_lineage_fingerprint":digest(sorted(lineage,key=lambda x:(str(x[0]),str(x[1]))))}

HORIZON_HOURS={"24h":24,"72h":72,"7d":168,"14d":336,"30d":720}

def matured_payload_integrity(m6:dict|None,now:datetime):
    """Independently fail-close malformed 'MATURED' rows before any Edge replay.

    This is structural validation, NOT source vintage attestation, independent
    adverse-family proof, scientific scoring, or trading permission.
    """
    events=(m6 or {}).get("events") if isinstance(m6,dict) else None
    if not isinstance(events,list):
        return {"status":"UNKNOWN_MISSING_OWNER","checked":0,"invalid":0,"reasons":[]}
    checked=0;invalid=0;reasons=[]
    def mark(code:str):
        nonlocal invalid
        invalid+=1
        if len(reasons)<8:reasons.append(code)
    def number(v):
        return isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v)
    def positive(v):
        return number(v) and v>0
    def clock(v):
        if not isinstance(v,str):return None
        try:
            t=datetime.fromisoformat(v.replace("Z","+00:00"))
            return t.astimezone(timezone.utc) if t.tzinfo is not None else None
        except (ValueError,OverflowError):return None
    def shifted_clock(dt,hours):
        if dt is None or hours is None:return None
        try:return dt+timedelta(hours=hours)
        except OverflowError:return None
    for index,event in enumerate(events):
        if not isinstance(event,dict):
            mark("INVALID_EVENT_ROW");continue
        knowledge=clock(event.get("knowledge_timestamp"))
        horizons=event.get("horizons")
        if not isinstance(horizons,dict):
            mark("MISSING_HORIZONS");continue
        for name,horizon in horizons.items():
            if not isinstance(horizon,dict):
                mark("MALFORMED_HORIZON");continue
            if horizon.get("maturity_state")!="MATURED":continue
            checked+=1
            hours=HORIZON_HOURS.get(name)
            coverage=horizon.get("coverage")
            target=clock(horizon.get("target_at_utc"))
            first_close=clock(coverage.get("first_close")) if isinstance(coverage,dict) else None
            last_close=clock(coverage.get("last_close")) if isinstance(coverage,dict) else None
            expected_target=shifted_clock(knowledge,hours)
            max_first_close=shifted_clock(knowledge,1)
            min_last_close=shifted_clock(target,-1)
            valid=(hours is not None and knowledge is not None and target is not None and
                expected_target is not None and max_first_close is not None and min_last_close is not None and
                target==expected_target and target<=now and
                isinstance(coverage,dict) and coverage.get("reason")=="COMPLETE_HOURLY_CLOSE_GRID" and
                number(coverage.get("row_count")) and
                coverage["row_count"] in (hours,hours+1) and
                number(coverage.get("max_gap_hours")) and
                math.isclose(coverage["max_gap_hours"],1.0,rel_tol=0.0,abs_tol=1e-9) and
                first_close is not None and last_close is not None and
                knowledge<=first_close<=max_first_close and
                first_close.minute==0 and first_close.second==0 and first_close.microsecond==0 and
                min_last_close<=last_close<=target and
                last_close.minute==0 and last_close.second==0 and last_close.microsecond==0 and
                last_close>=first_close and
                last_close-first_close==timedelta(hours=coverage["row_count"]-1))
            if valid:
                for symbol in ("BTC","ETH"):
                    asset=horizon.get(symbol)
                    if not isinstance(asset,dict):
                        valid=False;break
                    reference=asset.get("reference_anchor")
                    post=asset.get("post_knowledge_close_anchor")
                    terminal=asset.get("terminal")
                    if not all(isinstance(item,dict) for item in (reference,post,terminal)):
                        valid=False;break
                    start_close=clock(post.get("timestamp"))
                    end_close=clock(terminal.get("timestamp"))
                    if not (asset.get("state")=="MATURED" and
                            positive(reference.get("price")) and
                            positive(post.get("price")) and positive(terminal.get("close")) and
                            all(number(reference.get(k)) for k in ("mae_pct","mfe_pct","terminal_return_pct")) and
                            all(number(post.get(k)) for k in ("mae_pct","mfe_pct","terminal_return_pct")) and
                            (start_close==first_close and end_close==last_close)):
                        valid=False;break
                    barriers=asset.get("adverse_barriers")
                    expected=("-10.0","-15.0","-20.0") if symbol=="BTC" else ("-15.0","-20.0","-30.0")
                    if not isinstance(barriers,dict) or set(barriers)!=set(expected):
                        valid=False;break
                    # The immutable owner contract supplies three fixed adverse
                    # barriers per asset, including explicit untouched outcomes.
                    previous_touch=None
                    for barrier_level in expected:
                        row=barriers[barrier_level]
                        if not isinstance(row,dict) or type(row.get("touched")) is not bool:
                            valid=False;break
                        # Owner barrier_view compares FIRST reference price with
                        # the same full-post-knowledge low series as the MAE.
                        # Threshold crossing and first-touch order must agree.
                        should_touch=reference["mae_pct"]<=float(barrier_level)
                        if row["touched"] is not should_touch:
                            valid=False;break
                        if (row.get("basis")!="FIRST_POST_WARNING_CLOSE_PLUS_FULL_POST_KNOWLEDGE_BAR_LOWS" or
                            row.get("touch_time_semantics")!="HOURLY_BAR_END_NOT_EXACT_LOW_TIME"):
                            valid=False;break
                        when=clock(row.get("first_touch_timestamp"))
                        if row["touched"]:
                            if (when is None or not start_close<=when<=end_close or
                                (when-start_close).total_seconds()%3600!=0 or
                                (previous_touch is not None and when<previous_touch)):
                                valid=False;break
                            previous_touch=when
                        elif row.get("first_touch_timestamp") is not None:
                            valid=False;break
                    if not valid:break
            if not valid:mark(f"INVALID_MATURED_HORIZON_{name}")
    return {"status":"BLOCKED" if invalid else ("PASS" if checked else "PASS_NO_MATURED_YET"),
            "checked":checked,"invalid":invalid,"reasons":reasons}

def feature_counts(features:dict|None):
    rows=(features or {}).get("rows") if isinstance(features,dict) else []
    rows=rows if isinstance(rows,list) else []
    pit=sum(1 for r in rows if isinstance(r,dict) and (((r.get("features") or {}).get("source_row_integrity") or {}).get("point_in_time_feature_capture_eligible") is True))
    unverified=sum(1 for r in rows if isinstance(r,dict) and r.get("hourly_source_path") and (((r.get("features") or {}).get("source_row_integrity") or {}).get("point_in_time_feature_capture_eligible") is not True))
    return len(rows),pit,unverified

def latest_sol(root:Path):
    base=root/"research/api_agent/outputs/research_lab_sol/RL-DISTRIBUTION-SURVIVAL-META-006/issue-1476"
    if not base.exists():return {"status":"ABSENT"}
    candidates=[]
    for p in base.glob("comment-*/RESEARCH_LAB_SOL_ANALYSIS.json"):
        try:j=json.loads(p.read_text())
        except Exception:continue
        try:cid=int(p.parent.name.split("-")[-1])
        except Exception:cid=0
        candidates.append((cid,p,j))
    if not candidates:return {"status":"ABSENT"}
    cid,p,j=max(candidates,key=lambda x:x[0]);summary=str(j.get("summary") or "")
    verdict="UNKNOWN"
    if summary.startswith("VERDICT="):verdict=summary.split(";",1)[0].split("=",1)[1]
    return {"status":"PASS","comment_id":cid,"path":p.relative_to(root).as_posix(),"sha256":file_sha(p),"verdict":verdict}

def semantic_snapshot(root:Path,now:datetime):
    pointer,pb=load(root,"compass_pointer");freeze,fb=freeze_from_pointer(root,pointer)
    m6,mb=load(root,"m6_events");features,xb=load(root,"edge_features");cal,cb=load(root,"calibration")
    task15_gate,tgb=load(root,"task15_gate");task15_admission=task15_advisory(task15_gate,tgb)
    tracker=(freeze or {}).get("protection_tracker") if isinstance(freeze,dict) else {}
    tracker=tracker if isinstance(tracker,dict) else {}
    maturity,families,unknown=matured_counts(m6)
    fcount,pit,unverified=feature_counts(features)
    m6_check=m6_integrity(m6,features)
    payload_check=matured_payload_integrity(m6,now)
    sol=latest_sol(root)
    blockers=[]
    if isinstance(features,dict) and features.get("integrity_revision")!="v1.1_PIT_STRICT":blockers.append("FEATURE_COLLECTOR_INTEGRITY_REVISION_NOT_STRICT")
    if isinstance(m6,dict) and m6.get("integrity_revision")!="v1.2_POST_KNOWLEDGE_BAR_INTEGRITY":blockers.append("M6_OUTCOME_INTEGRITY_REVISION_NOT_STRICT")
    if unverified:blockers.append("PIT_UNVERIFIED_FEATURE_ROWS")
    if m6_check["status"]!="PASS":blockers.append("M6_EVENT_CHRONOLOGY_FAMILY_OR_COHORT_INVALID")
    if payload_check["status"]=="BLOCKED":blockers.append("M6_MATURED_OUTCOME_PAYLOAD_INVALID")
    primary_state=tracker.get("pullback_risk_state") or "UNAVAILABLE"
    if primary_state in {"ELEVATED","HIGH","CONFIRMED"} and fcount==0:blockers.append("PRIMARY_WARNING_WITHOUT_EDGE_FEATURE_ROW")
    semantic={
      "pullback_risk_state":primary_state,
      "distribution_risk":tracker.get("distribution_risk") or "UNKNOWN",
      "m6_integrity":m6_check,"m6_matured_payload_integrity":payload_check,
      "m6_event_count":int((m6 or {}).get("event_count") or 0) if isinstance(m6,dict) else 0,
      "m6_provisional_family_count":int((m6 or {}).get("provisional_independent_family_count") or 0) if isinstance(m6,dict) else 0,
      "m6_family_semantics":"PROVISIONAL_WARNING_OBSERVATION_CLUSTERS_NOT_PEAK_TROUGH_ADVERSE_FAMILIES",
      "verified_independent_adverse_family_count":None,
      "information_edge_claim":"NOT_ESTABLISHED",
      "economic_action_edge_claim":"NOT_ESTABLISHED",
      "matured_event_counts":maturity,"matured_family_counts":families,"unknown_horizon_counts":unknown,
      "feature_row_count":fcount,"pit_verified_feature_rows":pit,"pit_unverified_feature_rows":unverified,
      "calibration_eligible_rows":int((cal or {}).get("eligible_series_row_count") or 0) if isinstance(cal,dict) else 0,
      "calibration_warning_rows":int((cal or {}).get("warning_series_row_count") or 0) if isinstance(cal,dict) else 0,
      "feature_integrity_revision":(features or {}).get("integrity_revision") if isinstance(features,dict) else None,
      "m6_integrity_revision":(m6 or {}).get("integrity_revision") if isinstance(m6,dict) else None,
      "latest_sol_verdict":sol.get("verdict"),
      "task15_research_admission":task15_admission,
      "blockers":sorted(blockers),
    }
    bindings={"compass_pointer":pb,"compass_freeze":fb,"m6_events":mb,"edge_features":xb,"calibration":cb,"latest_sol":sol,"task15_gate":tgb}
    return semantic,bindings

def previous_state(path:Path):
    j=read_json(path) if path.exists() else None
    return j if isinstance(j,dict) and j.get("contract")==CONTRACT else None

def deltas(prev:dict|None,current:dict):
    if not prev:return ["INITIAL_GOVERNOR_SNAPSHOT"]
    old=prev.get("semantic_state") or {};d=[]
    scalar=("pullback_risk_state","distribution_risk","m6_event_count","m6_provisional_family_count","feature_row_count","pit_verified_feature_rows","pit_unverified_feature_rows","latest_sol_verdict")
    for k in scalar:
        if old.get(k)!=current.get(k):d.append(f"{k}:{old.get(k)}->{current.get(k)}")
    for group in ("matured_event_counts","matured_family_counts","unknown_horizon_counts"):
        a=old.get(group) or {};b=current.get(group) or {}
        for k in sorted(set(a)|set(b)):
            if a.get(k)!=b.get(k):d.append(f"{group}.{k}:{a.get(k)}->{b.get(k)}")
    if old.get("blockers")!=current.get("blockers"):d.append("BLOCKER_SET_CHANGED")
    if old.get("m6_integrity")!=current.get("m6_integrity"):d.append("M6_FAMILY_OR_COHORT_LINEAGE_CHANGED")
    if old.get("m6_matured_payload_integrity")!=current.get("m6_matured_payload_integrity"):d.append("M6_MATURED_PAYLOAD_INTEGRITY_CHANGED")
    if old.get("feature_integrity_revision")!=current.get("feature_integrity_revision"):d.append("FEATURE_INTEGRITY_REVISION_CHANGED")
    if old.get("m6_integrity_revision")!=current.get("m6_integrity_revision"):d.append("M6_INTEGRITY_REVISION_CHANGED")
    if old.get("task15_research_admission")!=current.get("task15_research_admission"):d.append("TASK15_RESEARCH_ADMISSION_ADVISORY_CHANGED")
    return d

def choose(prev:dict|None,s:dict,d:list[str]):
    blockers=s["blockers"]
    if blockers:
        return "FALSIFY",False,False,"Resolve deterministic integrity/cohort blockers before scoring or external interpretation."
    if prev is None:
        active_evidence=(s["m6_event_count"]>0 or s["feature_row_count"]>0 or s["pullback_risk_state"] in {"BUILDING","ELEVATED","HIGH","CONFIRMED"})
        if active_evidence:
            return "COLLECT",False,False,"Initial governor snapshot establishes the comparison baseline only; existing maturity is not a new-family delta."
        return "NOOP",False,False,"Initial governor snapshot establishes an empty comparison baseline; no external review is justified."
    prevsem=prev.get("semantic_state") or {}
    prevfam=prevsem.get("matured_family_counts") or {}
    new7=s["matured_family_counts"]["7d"]>int(prevfam.get("7d") or 0)
    new14=s["matured_family_counts"]["14d"]>int(prevfam.get("14d") or 0)
    new30=s["matured_family_counts"]["30d"]>int(prevfam.get("30d") or 0)
    # M6 warning-observation clusters are not independently confirmed adverse
    # peak-to-trough families. Maturity of warning clusters alone cannot open
    # an Edge conclusion gate or justify automatic paid external review.
    if new30 or new14 or new7:
        return "COLLECT",False,False,"New matured WARNING-CLUSTER data are descriptive controls, not independent adverse-family proof; await separately frozen conclusion-candidate admission."
    if s["pullback_risk_state"] in {"ELEVATED","HIGH","CONFIRMED"} or s["feature_row_count"]>int(prevsem.get("feature_row_count") or 0):
        return "COLLECT",False,False,"Natural warning evidence is accumulating; preserve pre-outcome features and await maturation."
    if s["pullback_risk_state"]=="BUILDING":
        return "COLLECT",False,False,"BUILDING remains watch/control only; continue collection without expensive external review."
    return "NOOP",False,False,"No material Edge evidence requiring action beyond existing collectors."

def build(root:Path,output:Path,history_root:Path,now:datetime):
    current,bindings=semantic_snapshot(root,now);prev=previous_state(output);d=deltas(prev,current)
    # Earlier v1 bootstrap treated a first snapshot's already-matured families as
    # new discoveries and emitted a false CONCLUSION_REVIEW. Reconcile LATEST
    # without silently mutating its immutable archived historical copy.
    legacy_bootstrap=bool(
        prev and prev.get("deltas")==["INITIAL_GOVERNOR_SNAPSHOT"]
        and prev.get("decision")=="CONCLUSION_REVIEW"
    )
    if legacy_bootstrap:
        # A repaired producer legitimately changes the semantic fingerprint;
        # the old false escalation must still be superseded explicitly.
        d=["LEGACY_BOOTSTRAP_FALSE_ESCALATION_SUPERSEDED"]+d
    material=bool(d)
    decision,sol,claude,reason=choose(prev,current,d)
    state={"contract":CONTRACT,"generated_at_utc":now.astimezone(timezone.utc).isoformat().replace("+00:00","Z"),
      "semantic_fingerprint":digest(current),"material_delta":material,"deltas":d,"decision":decision,"decision_reason":reason,
      "external_routing":{"sol_recommended":sol,"claude_recommended":claude,"automatic_dispatch":False},
      "conclusion_layer":{"separate_from_collection":True,"review_due":decision=="CONCLUSION_REVIEW","automatic_promotion":False},
      "semantic_state":current,"source_bindings":bindings,"authority":AUTHORITY,
      "prior_false_bootstrap_supersession":({
        "previous_decision":"CONCLUSION_REVIEW","reason":"INITIAL_EXISTING_MATURITY_IS_NOT_NEW_EVIDENCE",
        "previous_generated_at_utc":prev.get("generated_at_utc"),"previous_semantic_fingerprint":prev.get("semantic_fingerprint")
      } if legacy_bootstrap else None),
      "rules":{"warning_is_sell":False,"live_exit_rule":"NONE","raw_external_output_canonical":False,"negative_results_preserved":True}}
    if material or prev is None:
        output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
        # An explicit correction must not overwrite or disappear behind the
        # same-fingerprint original bootstrap history receipt.
        historical_key=state['semantic_fingerprint'][:16]+("-bootstrap-supersession" if legacy_bootstrap else "")
        hp=history_root/f"{now:%Y/%m/%d}"/f"{historical_key}.json";hp.parent.mkdir(parents=True,exist_ok=True)
        if not hp.exists():hp.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    return state

def main():
    p=argparse.ArgumentParser();p.add_argument("--repo-root",type=Path,default=Path.cwd());p.add_argument("--output",type=Path,required=True);p.add_argument("--history-root",type=Path,required=True);p.add_argument("--now-utc")
    a=p.parse_args();now=datetime.fromisoformat(a.now_utc.replace("Z","+00:00")) if a.now_utc else datetime.now(timezone.utc)
    r=build(a.repo_root,a.output,a.history_root,now)
    print(json.dumps({"contract":r["contract"],"decision":r["decision"],"material_delta":r["material_delta"],"sol_recommended":r["external_routing"]["sol_recommended"],"claude_recommended":r["external_routing"]["claude_recommended"],"fingerprint":r["semantic_fingerprint"]}))
if __name__=="__main__":main()
