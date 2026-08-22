#!/usr/bin/env python3
from research_governance_common import SPECIALIST_BINDINGS, specialist_binding_report, specialist_states
from research_meta_orchestrator import orchestrate

expected={"SHARED_ROW","CYCLE_NAVIGATOR","SHADOW_REGISTRY","SOURCE_RECOVERY"}
assert set(SPECIALIST_BINDINGS)==expected
report=specialist_binding_report()
assert set(report["expected_sources"])==expected
assert report["resolvable"] is True, report
assert not report["missing_all_sources"], report
for source in ("CYCLE_NAVIGATOR","SHADOW_REGISTRY","SOURCE_RECOVERY"):
    assert report["bindings"][source]["mode"]=="PRIMARY_READY", report
assert report["bindings"]["SHARED_ROW"]["mode"] in {"PRIMARY_READY","FALLBACK_STATUS_ONLY"}, report
states=specialist_states()
assert set(states)==expected, (states.keys(),report)
for source,state in states.items():
    assert state.get("_governance_binding_mode") in {"PRIMARY_READY","FALLBACK_STATUS_ONLY"}
    assert state.get("_governance_binding_path")

synthetic_states={k:{"authority":"RESEARCH_ONLY_NON_CANONICAL"} for k in expected}
degraded={
    "contract":"RESEARCH_GOVERNANCE_SPECIALIST_BINDING_REPORT_v1_TEST",
    "expected_sources":sorted(expected),
    "bindings":{k:{"mode":"PRIMARY_READY"} for k in expected},
    "missing_primary_sources":["SHARED_ROW"],"missing_all_sources":[],
    "complete_primary":False,"resolvable":True,"binding_integrity":"DEGRADED_PRIMARY_FALLBACK",
}
degraded["bindings"]["SHARED_ROW"]={"mode":"FALLBACK_STATUS_ONLY"}
meta=orchestrate({"max_concurrent_heavy_workstreams":1},synthetic_states,{}, {"queue":[]},{"verdict":"PASS"},degraded)
assert meta["primary_action"]=="WAIT_FOR_BINDING_COMPLETENESS", meta
assert meta["active_heavy_workstreams"]==[], meta
assert meta["binding_integrity"]=="DEGRADED_PRIMARY_FALLBACK"

broken={**degraded,"missing_all_sources":["SHARED_ROW"],"resolvable":False,"binding_integrity":"BROKEN"}
meta=orchestrate({"max_concurrent_heavy_workstreams":1},synthetic_states,{}, {"queue":[]},{"verdict":"PASS"},broken)
assert meta["primary_action"]=="WAIT_FOR_BINDING_COMPLETENESS"
assert meta["binding_integrity"]=="BROKEN"

complete={**degraded,"missing_primary_sources":[],"missing_all_sources":[],"complete_primary":True,"resolvable":True,"binding_integrity":"PRIMARY_COMPLETE","bindings":{k:{"mode":"PRIMARY_READY"} for k in expected}}
meta=orchestrate({"max_concurrent_heavy_workstreams":1},synthetic_states,{}, {"queue":[]},{"verdict":"PASS"},complete)
assert meta["primary_action"]=="WAIT_FOR_EVIDENCE", meta

print("RESEARCH_GOVERNANCE_BINDING_INTEGRITY_GATE_v1 PASS")
print(report)
