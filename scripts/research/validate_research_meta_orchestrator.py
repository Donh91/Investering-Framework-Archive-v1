#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("o",ROOT/"scripts/research/research_meta_orchestrator.py")
o=importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
pol={"max_concurrent_heavy_workstreams":1}
voi={"queue":[
 {"source":"SOURCE_RECOVERY","action":"DECLARE_NOT_TESTABLE","target":"old","impact_tier":"NONE","decision_surface":"DATA_INTEGRITY","reason":"terminal"},
 {"source":"SHARED_ROW","action":"STRESS_TEST","target":"C01","impact_tier":"HIGH","decision_surface":"ALTSEASON_ENTRY_ROTATION","reason":"errors","evidence_fingerprint":"x"}
]}
r=o.orchestrate(pol,{}, {}, voi, {"verdict":"PASS"})
assert r["primary_source"]=="SHARED_ROW" and r["primary_action"]=="QUEUE_BOUNDED_RESEARCH"; print("PASS terminal_source_does_not_starve_research")
r=o.orchestrate(pol,{}, {}, voi, {"verdict":"BLOCK_RESEARCH_ESCALATION"})
assert r["primary_action"]=="HALT_ESCALATION_AND_AUDIT"; print("PASS sentinel_precedence")
mem={"proposal_results":[{"source":"SHARED_ROW","action":"STRESS_TEST","target":"C01","novelty_verdict":"DUPLICATE_EXACT"}]}
r=o.orchestrate(pol,{},mem,voi,{"verdict":"PASS"})
sr=[x for x in r["queue"] if x.get("source")=="SHARED_ROW"][0]
assert sr["orchestrator_action"]=="SUPPRESS_DUPLICATE_RESEARCH"; print("PASS duplicate_suppression")
canon={"queue":[{"source":"CYCLE_NAVIGATOR","action":"CANONICAL_REVIEW_JUSTIFIED","target":"CN","impact_tier":"HIGH","decision_surface":"ALTSEASON_ENTRY_ROTATION","reason":"pass","evidence_fingerprint":"z"}]}
r=o.orchestrate(pol,{}, {}, canon, {"verdict":"PASS"})
assert r["primary_action"]=="PREPARE_CANONICAL_REVIEW" and r["primary_execution_mode"]=="REQUIRES_CANONICAL_REVIEW"; print("PASS canonical_review_packet_only")
assert len(r["active_heavy_workstreams"])<=1 and r["canonical_effect"] is False and r["paid_data_authorized"] is False
print("RESEARCH_META_ORCHESTRATOR_GATE_v1 PASS")
