#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("s",ROOT/"scripts/research/independent_research_adversarial_sentinel.py")
s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
safe={"SHARED_ROW":{"selected_action":"CONTINUE_OBSERVING","authority":"RESEARCH_ONLY_NON_CANONICAL","canonical_effect":False}}
r=s.evaluate({},safe,{}, {"queue":[]})
assert r["verdict"] in {"PASS","WATCH"}; print("PASS safe_state")
bad={"SHARED_ROW":{"selected_action":"CONTINUE_OBSERVING","authority":"RESEARCH_ONLY_NON_CANONICAL","canonical_effect":True}}
r=s.evaluate({},bad,{}, {"queue":[]})
assert r["verdict"]=="FIREWALL_BREACH"; print("PASS canonical_firewall")
bad={"SOURCE_RECOVERY":{"selected_action":"DECLARE_NOT_TESTABLE","paid_data_authorized":True,"authority":"RESEARCH_ONLY_NON_CANONICAL"}}
r=s.evaluate({},bad,{}, {"queue":[]})
assert r["verdict"]=="FIREWALL_BREACH"; print("PASS terminal_paid_conflict")
mem={"proposal_results":[{"source":"SHARED_ROW","action":"RESEARCH_NEW_HYPOTHESIS","target":"C01","novelty_verdict":"DUPLICATE_EXACT"}]}
voi={"queue":[{"source":"SHARED_ROW","action":"RESEARCH_NEW_HYPOTHESIS","target":"C01","impact_tier":"HIGH"}]}
r=s.evaluate({},safe,mem,voi)
assert r["verdict"]=="BLOCK_RESEARCH_ESCALATION"; print("PASS novelty_bypass_block")
prem={"CYCLE_NAVIGATOR":{"selected_action":"CANONICAL_REVIEW_JUSTIFIED","eligible_verified_row_n":999,"authority":"RESEARCH_ONLY_NON_CANONICAL"}}
r=s.evaluate({},prem,{}, {"queue":[]})
assert r["verdict"]=="BLOCK_RESEARCH_ESCALATION"; print("PASS premature_cn_promotion")
print("INDEPENDENT_RESEARCH_ADVERSARIAL_SENTINEL_GATE_v1 PASS")
