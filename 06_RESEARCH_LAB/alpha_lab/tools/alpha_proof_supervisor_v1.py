#!/usr/bin/env python3
import json,sys
from pathlib import Path
STATE=Path("06_RESEARCH_LAB/alpha_lab/proof_state.json")
def load(p):
 try:return json.loads(Path(p).read_text())
 except:return None
s=json.loads(STATE.read_text()) if STATE.exists() else {"state":"WAIT_SHADOW04","shadow04_attempts":0,"next_action":"WAIT"}
artifact=load(sys.argv[1]) if len(sys.argv)>1 else None
if artifact:
 if artifact.get("test")!="SHADOW-04-PROSPECTIVE":
  s.update(state="HALT_CRITICAL",next_action="HALT_CRITICAL",reason="unexpected_artifact")
 elif not artifact.get("prospective") or not artifact.get("spec_sha256") or not artifact.get("future_start_block"):
  s.update(state="HALT_CRITICAL",next_action="HALT_CRITICAL",reason="prospective_invariant_missing")
 elif artifact.get("provider_disagreement",1)!=0:
  s.update(state="SHADOW04_FAIL",next_action="HALT_CRITICAL",reason="provider_disagreement")
 elif artifact.get("PASS_COLLECTION") and artifact.get("n",0)>=1000:
  s.update(state="SHADOW04_PASS",next_action="START_SHADOW07",reason="prospective_gate_pass")
 else:
  a=int(s.get("shadow04_attempts",0))+1;s["shadow04_attempts"]=a
  if a<=2:s.update(state="WAIT_SHADOW04",next_action="RETRY_SHADOW04",reason="infrastructure_or_incomplete")
  else:s.update(state="SHADOW04_FAIL",next_action="HALT_CRITICAL",reason="retry_budget_exhausted")
STATE.write_text(json.dumps(s,indent=2)+"\n")
print(json.dumps(s,indent=2))
