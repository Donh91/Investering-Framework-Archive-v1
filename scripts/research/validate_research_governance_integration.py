#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
m=load("m","scripts/research/research_memory_novelty_gate.py")
v=load("v","scripts/research/research_decision_impact_router.py")
s=load("s","scripts/research/independent_research_adversarial_sentinel.py")
o=load("o","scripts/research/research_meta_orchestrator.py")
mp={"near_duplicate_jaccard_min":0.75}
op={"max_concurrent_heavy_workstreams":1}
states={"SHARED_ROW":{"selected_action":"RESEARCH_NEW_HYPOTHESIS","target":"C_NEW","reason":"novel rotation residual","evidence_fingerprint":"NEW","authority":"RESEARCH_ONLY_NON_CANONICAL","canonical_effect":False}}
mem=m.evaluate(mp,m.current_proposals(states),[])
voi=v.route({},states,mem)
sen=s.evaluate({},states,mem,voi)
meta=o.orchestrate(op,states,mem,voi,sen)
assert mem["selected_verdict"]=="NOVEL" and voi["selected_impact_tier"]=="HIGH" and sen["verdict"]=="PASS" and meta["primary_action"]=="QUEUE_BOUNDED_RESEARCH"; print("PASS novel_high_value_pipeline")
prior={"record_type":"NOVELTY_LEDGER","source":"SHARED_ROW","action":"RESEARCH_NEW_HYPOTHESIS","target":"C_NEW","reason":"novel rotation residual","evidence_fingerprint":"NEW"}
mem=m.evaluate(mp,m.current_proposals(states),[prior])
voi=v.route({},states,mem); sen=s.evaluate({},states,mem,voi); meta=o.orchestrate(op,states,mem,voi,sen)
assert mem["selected_verdict"]=="DUPLICATE_EXACT" and meta["primary_action"]=="SUPPRESS_DUPLICATE_RESEARCH"; print("PASS duplicate_pipeline")
bad={"SHARED_ROW":dict(states["SHARED_ROW"],canonical_effect=True)}
mem=m.evaluate(mp,m.current_proposals(bad),[]); voi=v.route({},bad,mem); sen=s.evaluate({},bad,mem,voi); meta=o.orchestrate(op,bad,mem,voi,sen)
assert sen["verdict"]=="FIREWALL_BREACH" and meta["primary_action"]=="HALT_ESCALATION_AND_AUDIT"; print("PASS unsafe_pipeline_halts")
states2=dict(states); states2["SOURCE_RECOVERY"]={"selected_action":"DECLARE_NOT_TESTABLE","target_receipt":"legacy","evidence_fingerprint":"OLD","authority":"RESEARCH_ONLY_NON_CANONICAL"}
mem=m.evaluate(mp,m.current_proposals(states2),[]); voi=v.route({},states2,mem); sen=s.evaluate({},states2,mem,voi); meta=o.orchestrate(op,states2,mem,voi,sen)
assert meta["primary_source"]=="SHARED_ROW"; print("PASS terminal_source_non_starvation")
print("AUTONOMOUS_RESEARCH_GOVERNANCE_INTEGRATION_GATE_v1 PASS")
