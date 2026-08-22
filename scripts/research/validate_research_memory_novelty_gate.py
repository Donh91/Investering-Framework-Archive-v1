#!/usr/bin/env python3
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("m",ROOT/"scripts/research/research_memory_novelty_gate.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
policy={"near_duplicate_jaccard_min":0.70}
def p(fp="A",reason="new slow bleed rotation pattern",target="C01",action="RESEARCH_NEW_HYPOTHESIS",source="SHARED_ROW",family="rotation"):
    return {"source":source,"action":action,"target":target,"reason":reason,"evidence_fingerprint":fp,"family":family}
prior={"record_type":"NOVELTY_LEDGER","source":"SHARED_ROW","action":"RESEARCH_NEW_HYPOTHESIS","target":"C01","reason":"new slow bleed rotation pattern","evidence_fingerprint":"A","family":"rotation"}
assert m.classify(policy,p(),[prior])["novelty_verdict"]=="DUPLICATE_EXACT"; print("PASS exact_duplicate")
assert m.classify(policy,p("B"),[prior])["novelty_verdict"]=="REOPEN_WITH_NEW_EVIDENCE"; print("PASS reopen_new_evidence")
near=dict(prior); near["source"]="CYCLE_NAVIGATOR"; near["action"]="RESEARCH_NEW_PHASE_HYPOTHESIS"; near["reason"]="slow bleed rotation pattern research"
x=p("C",reason="slow bleed rotation pattern research",action="RESEARCH_NEW_PHASE_HYPOTHESIS",source="CYCLE_NAVIGATOR")
assert m.classify(policy,x,[near])["novelty_verdict"]=="DUPLICATE_EXACT" or m.classify(policy,x,[near])["novelty_verdict"] in {"REOPEN_WITH_NEW_EVIDENCE","DUPLICATE_NEAR"}
n={"record_type":"NOVELTY_LEDGER","source":"OTHER","action":"RESEARCH_NEW_HYPOTHESIS","target":"OLD","family":"rotation","reason":"slow bleed fake rotation under declining breadth","evidence_fingerprint":"X"}
r=m.classify(policy,p("Y",target="NEW",family="rotation",reason="slow bleed fake rotation under declining breadth"),[n])
assert r["novelty_verdict"]=="DUPLICATE_NEAR",r; print("PASS near_duplicate_same_family")
r=m.classify(policy,p("Z",target="UNRELATED",family="other",reason="liquidity fracture"),[n])
assert r["novelty_verdict"]=="NOVEL"; print("PASS unrelated_novel")
state=m.evaluate(policy,[],[])
assert state["selected_verdict"]=="NO_NEW_HYPOTHESIS"; print("PASS no_proposal")
assert state["canonical_effect"] is False and state["paid_data_authorized"] is False
print("RESEARCH_MEMORY_NOVELTY_GATE_v1 PASS")
