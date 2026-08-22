#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("nac", HERE / "shared_row_next_action_controller.py")
nac = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(nac)

POLICY_SRC = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1/RESEARCH_NEXT_ACTION_POLICY_v1.json")
REG_SRC = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1/03_CANDIDATE_REGISTRY.json")
MATRIX_SRC = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1/OWNER_BINDING_MATRIX.json")

ROW_FIELDS = [
    "event_id","observation_timestamp_utc","information_cutoff_utc","source_version_commit","regime_tag","catalyst_tag","candidate_decisions",
    "outcome_24h","outcome_72h","outcome_7d","mae_24h","mfe_24h","mae_72h","mfe_72h","mae_7d","mfe_7d","provenance_hash"
]
DIV_FIELDS = [
    "divergence_id","event_id","observation_timestamp_utc","candidate_a","candidate_b","decision_a","decision_b","information_cutoff_utc","catalyst_tag","regime_tag",
    "outcome_24h","outcome_72h","outcome_7d","mae_24h","mfe_24h","mae_72h","mfe_72h","mae_7d","mfe_7d","status","provenance_hash"
]


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def mkroot():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    (root / "data").mkdir(parents=True)
    (root / "RESEARCH_NEXT_ACTION_POLICY_v1.json").write_text(POLICY_SRC.read_text())
    (root / "03_CANDIDATE_REGISTRY.json").write_text(REG_SRC.read_text())
    (root / "OWNER_BINDING_MATRIX.json").write_text(MATRIX_SRC.read_text())
    (root / "RUNTIME_STATUS.json").write_text(json.dumps({"core_prospective_eligibility_start":"2026-08-23T04:50:00Z"}))
    write_csv(root / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv", ROW_FIELDS, [])
    write_csv(root / "14_DIVERGENCE_FNP_LEDGER.csv", DIV_FIELDS, [])
    return td, root


def row(i, outcome="1", regime="R1"):
    ts = datetime(2026,8,23,12,0,tzinfo=timezone.utc) + timedelta(days=i)
    return {
        "event_id":f"E{i}","observation_timestamp_utc":nac.iso(ts),"information_cutoff_utc":nac.iso(ts),"source_version_commit":"x",
        "regime_tag":regime,"catalyst_tag":"NONE","candidate_decisions":json.dumps({"C07_SIMPLE_3": True}),
        "outcome_24h":outcome,"outcome_72h":outcome,"outcome_7d":outcome,"mae_7d":"-0.01","mfe_7d":"0.02","provenance_hash":f"p{i}"
    }


def div(i, target="C04_ETHBTC_BREADTH", target_correct=True, target_decision=1, outcome=1, regime=None, catalyst=None, mae="-0.01"):
    r = regime or ("R1" if i % 2 == 0 else "R2")
    c = catalyst or ("NONE" if i % 2 == 0 else "CAT")
    base_dec = 1 - target_decision
    if target_correct:
        outcome = target_decision
    else:
        outcome = base_dec
    ts = datetime(2026,8,24,12,0,tzinfo=timezone.utc) + timedelta(days=i)
    return {
        "divergence_id":f"D{i}","event_id":f"E{i}","observation_timestamp_utc":nac.iso(ts),"candidate_a":"C07_SIMPLE_3","candidate_b":target,
        "decision_a":str(base_dec),"decision_b":str(target_decision),"information_cutoff_utc":nac.iso(ts),"catalyst_tag":c,"regime_tag":r,
        "outcome_24h":str(outcome),"outcome_72h":str(outcome),"outcome_7d":str(outcome),"mae_7d":mae,"mfe_7d":"0.02","status":"MATURED","provenance_hash":f"d{i}"
    }


def decide(root, now):
    p=json.loads((root/"RESEARCH_NEXT_ACTION_POLICY_v1.json").read_text())
    rows=nac.read_csv(root/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv")
    ds=nac.read_csv(root/"14_DIVERGENCE_FNP_LEDGER.csv")
    ev=nac.evidence(rows,ds,p)
    return nac.choose_action(root,rows,ev,p,now,nac.read_csv(root/"data/NEXT_ACTION_LEDGER.csv")), ev


def assert_eq(got, want, name):
    if got != want: raise AssertionError(f"{name}: got={got!r} want={want!r}")


def main():
    checks=[]

    td,root=mkroot();
    try:
        a,_=decide(root,datetime(2026,8,23,5,0,tzinfo=timezone.utc)); assert_eq(a[0],"CONTINUE_OBSERVING","pre-floor-no-gap"); checks.append("pre_floor_observe")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        a,_=decide(root,datetime(2026,8,24,17,0,tzinfo=timezone.utc)); assert_eq(a[0],"INVESTIGATE_DATA_GAP","stale-no-row"); checks.append("data_gap_after_36h")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        write_csv(root/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",ROW_FIELDS,[row(i) for i in range(7)])
        write_csv(root/"14_DIVERGENCE_FNP_LEDGER.csv",DIV_FIELDS,[div(i) for i in range(2)])
        a,_=decide(root,datetime(2026,9,15,tzinfo=timezone.utc)); assert_eq(a[0],"EXTEND_OBSERVATION","sparse-divergence"); checks.append("extend_sparse_divergence")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        write_csv(root/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",ROW_FIELDS,[row(i) for i in range(7)])
        write_csv(root/"14_DIVERGENCE_FNP_LEDGER.csv",DIV_FIELDS,[div(i) for i in range(3)])
        a,_=decide(root,datetime(2026,9,15,tzinfo=timezone.utc)); assert_eq(a[0],"INVESTIGATE_DIVERGENCE","first-review"); checks.append("first_information_review")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        rows=[row(i,regime="R1" if i%2==0 else "R2") for i in range(10)]
        ds=[div(i,target="C04_ETHBTC_BREADTH",target_correct=False,target_decision=(i%2),regime="R1" if i%2==0 else "R1",catalyst="A" if i%2==0 else "B") for i in range(5)]
        write_csv(root/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",ROW_FIELDS,rows); write_csv(root/"14_DIVERGENCE_FNP_LEDGER.csv",DIV_FIELDS,ds)
        a,_=decide(root,datetime(2026,10,1,tzinfo=timezone.utc)); assert_eq(a[0],"STRESS_TEST","multi-context-errors"); checks.append("stress_test_trigger")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        rows=[row(i,regime="R1" if i%2==0 else "R2") for i in range(12)]
        ds=[div(i,target="C04_ETHBTC_BREADTH",target_correct=False,target_decision=(i%2),regime="R1" if i%2==0 else "R2") for i in range(8)]
        write_csv(root/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",ROW_FIELDS,rows); write_csv(root/"14_DIVERGENCE_FNP_LEDGER.csv",DIV_FIELDS,ds)
        write_csv(root/"data/NEXT_ACTION_LEDGER.csv",["decision_fingerprint","generated_at_utc","primary_action","target","reason","eligible_rows_total","divergences_total","matured_24h_rows","matured_72h_rows","matured_7d_rows","matured_7d_divergences","canonical_effect","paid_data_authorized","deep_research_authorized"],[{"decision_fingerprint":"x","generated_at_utc":"2026-09-20T00:00:00Z","primary_action":"STRESS_TEST","target":"C04_ETHBTC_BREADTH","reason":"x","eligible_rows_total":"10","divergences_total":"6","matured_24h_rows":"10","matured_72h_rows":"10","matured_7d_rows":"10","matured_7d_divergences":"6","canonical_effect":"false","paid_data_authorized":"false","deep_research_authorized":"false"}])
        a,_=decide(root,datetime(2026,10,15,tzinfo=timezone.utc)); assert_eq(a[0],"RESEARCH_NEW_HYPOTHESIS","persistent-errors"); checks.append("new_hypothesis_after_stress")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        rows=[row(i) for i in range(20)]
        ds=[]
        for i in range(12):
            if i < 11: ds.append(div(i,target="C04_ETHBTC_BREADTH",target_correct=True,target_decision=1,outcome=1,mae="-0.005"))
            else: ds.append(div(i,target="C04_ETHBTC_BREADTH",target_correct=False,target_decision=0,outcome=1,mae="-0.002"))
        write_csv(root/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",ROW_FIELDS,rows); write_csv(root/"14_DIVERGENCE_FNP_LEDGER.csv",DIV_FIELDS,ds)
        a,ev=decide(root,datetime(2026,11,15,tzinfo=timezone.utc)); assert_eq(a[0],"PROMOTE_FOR_CANONICAL_REVIEW","strong-pairwise-promotion");
        assert ev["pairwise_vs_baseline_7d"]["C04_ETHBTC_BREADTH"]["wilson_lower"] > 0.5; checks.append("promotion_requires_strong_pairwise_evidence")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        rows=[row(i) for i in range(20)]
        ds=[]
        for i in range(12):
            if i < 11: ds.append(div(i,target="C04_ETHBTC_BREADTH",target_correct=False,target_decision=1,outcome=0))
            else: ds.append(div(i,target="C04_ETHBTC_BREADTH",target_correct=True,target_decision=1,outcome=1))
        write_csv(root/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",ROW_FIELDS,rows); write_csv(root/"14_DIVERGENCE_FNP_LEDGER.csv",DIV_FIELDS,ds)
        a,_=decide(root,datetime(2026,11,15,tzinfo=timezone.utc)); assert_eq(a[0],"DEPRIORITIZE","strong-pairwise-deprioritize"); checks.append("deprioritize_requires_strong_pairwise_evidence")
    finally: td.cleanup()

    td,root=mkroot();
    try:
        p=json.loads((root/"RESEARCH_NEXT_ACTION_POLICY_v1.json").read_text()); ev=nac.evidence([],[],p); packet=nac.packet_for("CONTINUE_OBSERVING","CORE_C01_C07","x",ev,nac.candidate_registry(root),[],root,datetime.now(timezone.utc))
        assert packet["canonical_effect"] is False and packet["paid_data_authorized"] is False and packet["deep_research_authorized"] is False
        state={**packet,"decision_fingerprint":"same"}
        first=nac.write_ledger(root/"data/NEXT_ACTION_LEDGER.csv",state); second=nac.write_ledger(root/"data/NEXT_ACTION_LEDGER.csv",state)
        assert first is True and second is False and len(nac.read_csv(root/"data/NEXT_ACTION_LEDGER.csv"))==1
        checks += ["canonical_firewall","no_paid_or_deep_research_auto","idempotent_action_ledger"]
    finally: td.cleanup()

    print(json.dumps({"contract":"RESEARCH_NEXT_ACTION_CONTROLLER_SYNTHETIC_GATE_v1","status":"PASS","checks":checks},sort_keys=True))

if __name__=="__main__": main()
