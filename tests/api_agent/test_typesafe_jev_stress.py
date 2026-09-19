#!/usr/bin/env python3
from __future__ import annotations
import json, math
from copy import deepcopy
from scripts.api_agent.meme_alpha_prospective import freeze_shadow_observation, stable_hash
from scripts.api_agent.typesafe_jev_replay import build_blind_state, counterfactual_route, freeze_challenger_prediction

BASE_FEATURE={
 "feature_name":"liquidity_usd","feature_value_at_cutoff":75000,
 "feature_effective_at_utc":"2026-09-19T09:04:00Z","source_observed_at_utc":"2026-09-19T09:04:30Z",
 "source_or_schema_version":"stress-v1","source_record_or_event_identity":"stress:liq","mutability_class":"SNAPSHOT_PINNED"}

def obs(features=None, roles=None):
 return freeze_shadow_observation(identity={"chain":"solana","token_id":"StressToken111","token_origin_utc":"2026-09-19T09:00:00Z"},cutoff_minutes=5,cutoff_utc="2026-09-19T09:05:00Z",features=features or [deepcopy(BASE_FEATURE)],wallet_roles=roles or ["UNKNOWN"])

def expect_error(name, fn, needle):
 try: fn()
 except Exception as e:
  assert needle in str(e), (name,str(e)); return
 raise AssertionError(name+": expected "+needle)

o=obs(); s=build_blind_state(o)
assert s["source_observation_sha256"]==o["observation_sha256"]
assert "authority" not in s
assert s["blind_state_sha256"]==stable_hash({k:v for k,v in s.items() if k!="blind_state_sha256"})
assert build_blind_state(o)["blind_state_sha256"]==s["blind_state_sha256"]
x=deepcopy(o); x["observation_sha256"]="0"*64
expect_error("forged-observation-hash",lambda:build_blind_state(x),"OBSERVATION_SHA256_MISMATCH")

for key in ["outcome","future_price","ath","missed_winner_audit"]:
 x=deepcopy(o); x["nested"]={"a":[{"b":{key:1}}]}
 expect_error("leak:"+key,lambda x=x:build_blind_state(x),"OUTCOME_LEAKAGE_DETECTED")

x=deepcopy(o); x["features"][0]["mutability_class"]="MUTABLE_LIVE_FIELD"
expect_error("mutable",lambda:build_blind_state(x),"MUTABLE_LIVE_FIELD_NOT_HISTORICAL_EVIDENCE")
x=deepcopy(o); x["features"][0]["source_observed_at_utc"]="2026-09-19T09:06:00Z"
expect_error("late",lambda:build_blind_state(x),"SNAPSHOT_OBSERVED_AFTER_CUTOFF")
x=deepcopy(o); x["features"][0]["feature_effective_at_utc"]="2026-09-19T09:06:00Z"
expect_error("future-effective",lambda:build_blind_state(x),"FEATURE_EFFECTIVE_AFTER_CUTOFF")
x=deepcopy(o); x["features"][0]["mutability_class"]="UNKNOWN"; x["features"][0]["feature_value_at_cutoff"]=1
expect_error("unknown-positive",lambda:build_blind_state(x),"UNKNOWN_MUTABILITY_CANNOT_CARRY_POSITIVE_VALUE")

assert counterfactual_route({"frontier_review_need":.8})=="FRONTIER_REVIEW"
assert counterfactual_route({"evidence_conflict":.8})=="FRONTIER_REVIEW"
assert counterfactual_route({"deep_dive_value":.7})=="DEEP_DIVE"
assert counterfactual_route({"material_evidence":.7})=="DEEP_DIVE"
assert counterfactual_route({})=="RETAIN"
for bad in (-0.01,1.01,float("nan"),float("inf")):
 expect_error("invalid-probability",lambda bad=bad:counterfactual_route({"material_evidence":bad}),"INVALID_JUDGMENT_PROBABILITY")
for vals in ({"material_evidence":0},{"material_evidence":1},{"evidence_conflict":1},{"frontier_review_need":1}):
 assert counterfactual_route(vals)!="DROP"

p=freeze_challenger_prediction(blind_state=s,challenger="STRESS",question_contract_version="STRESS_V1",predictions={"route":"RETAIN"})
assert all(v is False for v in p["authority"].values())
expect_error("prediction leak",lambda:freeze_challenger_prediction(blind_state=s,challenger="STRESS",question_contract_version="STRESS_V1",predictions={"future_price":2}),"PREDICTION_CONTAINS_OUTCOME_FIELD")
expect_error("forbidden-frozen-route",lambda:freeze_challenger_prediction(blind_state=s,challenger="STRESS",question_contract_version="STRESS_V1",predictions={"route":"DROP"}),"FORBIDDEN_REPLAY_ROUTE")

# Size / irrelevant-detail stress, deterministic only. It proves hashing/validation behavior, not Jev intelligence.
features=[]
for i in range(255):
 f=deepcopy(BASE_FEATURE); f["feature_name"]=f"f_{i:03d}"; f["feature_value_at_cutoff"]=i; f["source_record_or_event_identity"]=f"stress:{i}"
 features.append(f)
large=obs(features=features); large_state=build_blind_state(large)
assert len(large_state["features"])==255
print(json.dumps({"status":"PASS","contract":"JEV_REPLAY_STRESS_V1","checks":"leakage,hash-integrity,mutability,time,unknown,probability-bounds,route,authority,determinism,255-feature-size","large_state_sha256":large_state["blind_state_sha256"]},sort_keys=True))
