#!/usr/bin/env python3
"""One-shot OpenAI API benchmark. Explicitly bounded: one request, no tools, no repo writes.
Requires OPENAI_API_KEY. Model defaults to gpt-5.6; override with OPENAI_BENCH_MODEL.
Logs token usage only, never credentials or full model output.
"""
import json, os, time, urllib.request
key=os.environ.get("OPENAI_API_KEY")
if not key: raise SystemExit("OPENAI_API_KEY missing")
model=os.environ.get("OPENAI_BENCH_MODEL","gpt-5.6")
prompt="""You are an independent research reviewer. Given this synthetic Alpha Lab evidence packet, return JSON only with keys material_evidence (0..1), evidence_conflict (0..1), information_density (0..4), deep_dive_value (0..1), preserve_verbatim (0..1), frontier_review_need (0..1), and one_sentence_rationale. Do not recommend a trade. Evidence: liquidity_usd=75000 at cutoff; source_conflict=UNKNOWN; wallet_role=UNKNOWN; all observations are point-in-time and synthetic."""
body={"model":model,"input":prompt,"max_output_tokens":300}
req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
t=time.perf_counter()
with urllib.request.urlopen(req,timeout=120) as r: data=json.load(r)
ms=round((time.perf_counter()-t)*1000,1)
u=data.get("usage") or {}
safe={"contract":"OPENAI_SOL_TOKEN_BENCH_V1","model_requested":model,"model_returned":data.get("model"),"latency_ms":ms,"input_tokens":u.get("input_tokens"),"output_tokens":u.get("output_tokens"),"total_tokens":u.get("total_tokens"),"status":"PASS"}
print(json.dumps(safe,sort_keys=True))
