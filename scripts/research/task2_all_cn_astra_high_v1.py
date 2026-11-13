#!/usr/bin/env python3
"""One owner-initiated GitHub issue_comment -> GitHub Actions -> Astra High call.

Separate NEW mission from the already CONSUMED original Astra Task2 one-shot.
Uses native pre-HTTP, persistent issue claim and canonical monthly shared reserve.
Does not add a scheduler, model router, trading path or any recurring model call.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Script entrypoints run with scripts/research as sys.path[0]; anchor repo root first.
REPO_IMPORT_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_IMPORT_ROOT))
from scripts.api_agent import manual_astra_task2_high_v1 as core

MODEL = "gpt-6-astra"
EFFORT = "high"
MISSION = "ASTRA-HIGH-TASK2-ALL-CN-HISTORICAL-20261113-ONE"
ISSUE = 1596
TRIGGER = "OWNER_LAUNCH_ASTRA_HIGH_ALL_CN_20261113_BUDGET_10USD_ONE_SHOT"
CLAIM_MARKER = "ASTRA_TASK2_ALLCN_PAID_CLAIM_V1 mission=" + MISSION
ARTIFACT_CLAIM = "astra-task2-allcn-20261113-one-paid-attempt-claim"
TOKEN_PRICE_INPUT = 10.0
TOKEN_PRICE_OUTPUT = 50.0
MAX_INPUT_REQUEST_BYTES = 510_000
MAX_OUTPUT_TOKENS = 85_000
MAX_COST_USD = 10.0
RESPONSE_ID = re.compile(r"resp_[A-Za-z0-9_-]{4,180}\Z")
ROOT = Path(__file__).resolve().parents[2]
CANONICAL_LEDGER = ROOT / "research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"
SOURCE_MANUAL = ROOT / (
    "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/"
    "kompas_scientific_edge_program_v2_1/"
    "ASTRA_HIGH_SCIENTIFIC_BREAKTHROUGH_MASTER_PACKET_2026-11-13_v1.md"
)
SOURCE_FABLE = ROOT / "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/CLAUDE_POST_ASTRA_INDEPENDENT_AUDIT_CONTRACT_2026-11-13_v1.md"

def put(path, obj):
    core.write_once(path, obj)

def read(path):
    return core.read(path)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def http(method,url,**kwargs):
    return core.http_json(method,url,**kwargs)

def fail(reason):
    raise ValueError(reason)

def owner_event():
    if (os.getenv("GITHUB_ACTOR") != "Donh91"
            or os.getenv("GITHUB_EVENT_NAME") != "issue_comment"
            or os.getenv("GITHUB_REF") != "refs/heads/main"
            or os.getenv("GITHUB_REPOSITORY") != "Donh91/Investering-Framework-Archive-v1"):
        fail("OWNER_EVENT_GATE_FAILED")
    event_path=os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).is_file():
        fail("OWNER_NATIVE_EVENT_MISSING")
    obj=json.loads(Path(event_path).read_text(encoding="utf-8"))
    if (obj.get("action") != "created"
            or (obj.get("issue") or {}).get("number") != ISSUE
            or (obj.get("comment") or {}).get("body") != TRIGGER
            or (obj.get("comment") or {}).get("user",{}).get("login") != "Donh91"):
        fail("EXACT_OWNER_TRIGGER_NOT_MATCHED")
    if not re.fullmatch(r"[0-9a-f]{40}",os.getenv("GITHUB_SHA") or ""):
        fail("SOURCE_MAIN_SHA_INVALID")
    return obj

def check_reserve():
    value=read(CANONICAL_LEDGER)
    reserve=value.get("owner_reservations")
    if not isinstance(reserve,list):
        fail("SHARED_BUDGET_LEDGER_MISSING")
    eligible=[x for x in reserve if isinstance(x,dict) and
              x.get("work_id")==MISSION and
              x.get("status")=="OWNER_RESERVED_PREHTTP" and
              x.get("upper_usd")==10 and
              x.get("reconciliation_required") is True and
              x.get("one_paid_post_max")==1]
    if len(eligible)!=1:
        fail("EXACT_ALLCN_10USD_RESERVATION_MISSING")

def census(token):
    repo=os.environ["GITHUB_REPOSITORY"]
    for page in range(1,21):
        url="https://api.github.com/repos/"+repo+"/issues/"+str(ISSUE)+"/comments?per_page=100&page="+str(page)
        rows=http("GET",url,github_token=token,timeout=40)
        if not isinstance(rows,list):fail("ORIGINAL_ISSUE_CENSUS_INVALID")
        if any(CLAIM_MARKER in str(x.get("body","")) for x in rows if isinstance(x,dict)):
            fail("ALLCN_ONE_USE_CLAIM_ALREADY_CONSUMED_NO_POST")
        if len(rows)<100:return
    fail("ORIGINAL_ISSUE_CENSUS_TRUNCATED_FAIL_CLOSED")

def artifact_census(token):
    repo=os.environ["GITHUB_REPOSITORY"]
    url="https://api.github.com/repos/"+repo+"/actions/artifacts?name="+ARTIFACT_CLAIM+"&per_page=100"
    d=http("GET",url,github_token=token,timeout=30)
    if not isinstance(d.get("artifacts"),list):
        fail("ARTIFACT_CENSUS_MISSING")
    # Even an expired artifact must block. Native Issue claim remains durable.
    if any(x.get("name")==ARTIFACT_CLAIM for x in d["artifacts"]):
        fail("ALLCN_ONE_USE_ARTIFACT_ALREADY_EXISTS_NO_POST")

def source_bundle(analysis_dir):
    p=analysis_dir/"astra_empirical_input.txt"
    summary=analysis_dir/"summary.json"
    manifest=analysis_dir/"source_manifest.json"
    for f in (p,summary,manifest,SOURCE_MANUAL,SOURCE_FABLE):
        if not f.is_file() or f.is_symlink():
            fail("MANDATORY_PUBLIC_SOURCE_MISSING:" + f.name)
    text=p.read_text(encoding="utf-8")
    s=read(summary)
    if s.get("contract")!="TASK2_ALL_CN_HISTORICAL_REPLAY_v1":
        fail("REPLAY_CONTRACT_INVALID")
    if s.get("source_main_sha")!=os.getenv("GITHUB_SHA"):
        fail("REPLAY_WRONG_SOURCE_MAIN")
    if s.get("weeks_with_machine_cn",0)<10 or s.get("market_completed_week_packages",0)<10:
        fail("LONGITUDINAL_DATASET_TOO_SMALL")
    if s.get("source_claims_independently_verified_first_known") != 0:
        fail("RETROSPECTIVE_FIRST_KNOWN_FABRICATION")
    source_list=read(manifest)
    if not isinstance(source_list,list) or len(source_list)<50:
        fail("LONGITUDINAL_SOURCE_MANIFEST_INCOMPLETE")
    raw=(SOURCE_MANUAL.read_text(encoding="utf-8") +
         "\n\nINDEPENDENT CLAUDE AUDIT CONTRACT (AUDIT ONLY AFTER RESULTS):\n"+
         SOURCE_FABLE.read_text(encoding="utf-8"))
    return text,raw,s,source_list

def prepare(out,analysis):
    owner_event()
    check_reserve()
    empirical,contract,summary,sources=source_bundle(analysis)
    mission=(
      "EXECUTE, DON'T JUST DESCRIBE: A full, critical, historical retrospective "
      "scientific study of ALL archived Master Mondays and Cycle Navigators from "
      "the attached actual GitHub-derived ORIGINAL files and real, 168h-complete "
      "Binance weekly OHLC observations, with individually SHA-pinned sources. "
      "The source bundle contains originally archived CN1-28 textual issues, "
      "machine-frozen CN weeks 36-46, internal claim freezes W39-46, "
      "weekly closes W32-45, all available Master Mondays, plus actual compiled "
      "weekly paired forecast-vs-prior-week baseline rows and daily intraday "
      "numeric claim comparisons. Operate in read-only analytical mode, no tools "
      "claimed available inside this isolated API call. Source legal first-known "
      "unknown => no genuine prospective/PIT skill or trading authority claim. "
      "Fable 5.2 has prospective W47+ forecast engine held and Alpha paper-wallet "
      "data-gated; DO NOT redo those prospective studies, autonomous merge pilots, "
      "T5/source site fixes or live trading bot. Focus UNIQUE historical census and "
      "empirical red team. Critically reconstruct descriptive BTC/ETH full-range "
      "coverage versus naive previous week band, width/coverage ratio, normalized "
      "miss size, score inflation due to unavailable/aliases, 1-2d/3-4d/5-7d "
      "window failures, regime stratification where real data allow, "
      "early warning 3/5 -> 4/5 false positives, breadth/ETHBTC/ETF and volatility "
      "ablation using only actually available data; kill hypotheses with no data "
      "or matched independent event cohorts. Uniquely evaluate pre-2026-W36 "
      "published CNs with their original provenance and missing raw quantitative "
      "data; do NOT incorrectly backfill from 2026 market history or treat textual "
      "score as machine-proven. Identify best and worst weeks, errors and drivers, "
      "including W46 shock as exposed/unmatured. Use small N, clustered time "
      "dependencies, no p-hacking and correct source issue clocks. Do not conflate "
      "forecast ranges with issued expected closes, never claim a 2-week estimate "
      "from one overlap. Be both quantitative and skeptical. Avoid external studies "
      "unless sourced. Produce an executive dashboard, ten demonstrated/falsified "
      "findings with row-level source SHA citations, yearwide coverage inventory, "
      "actual individual-week paired tables and simple baseline comparison, "
      "fully specified 3 challengers max with pre-registered falsifiers and true "
      "data prerequisites, feasibility for cost-aware Alpha v4 with existing ledger, "
      "producer-consumer validity limitations, cause-analysis incl range inflation, "
      "and three highest-EV original-owner implementation proposals + regression "
      "tests. At least 35,000 characters if data warrant, favor evidence over "
      "length. Do not invent CSV execution, markdown tests or provider calls. "
      "End with CLAUDE INDEPENDENT AUDIT QUESTIONS, source limitations, complete "
      "list of rejected hypotheses and honest BLOCKED classes. "
      "Never alter source values, rules, weights, jobs or tokens, no real trades."
    )
    txt=("OWNER AUTHORIZED EXTRAORDINARY FULL HISTORICAL KOMPAS RESEARCH\n"
         +"Mission ID: "+MISSION+"\nSource main: "+os.environ["GITHUB_SHA"]+"\n"
         +mission+"\n\nCANONICAL SCIENCE INSTRUCTIONS:\n"+contract
         +"\n\nORIGINAL GITHUB SOURCE ROWS AND ACTUAL 168H OHLC + COMPUTED BASELINES:\n"
         +empirical)
    payload={"model":MODEL,"reasoning":{"effort":EFFORT},
             "background":True,"store":True,
             "max_output_tokens":MAX_OUTPUT_TOKENS,
             "input":[{"role":"user","content":[{"type":"input_text","text":txt}]}]}
    raw=core.canonical(payload)
    upper=(len(raw)*TOKEN_PRICE_INPUT+MAX_OUTPUT_TOKENS*TOKEN_PRICE_OUTPUT)/1_000_000
    if len(raw)>MAX_INPUT_REQUEST_BYTES or upper>MAX_COST_USD:
        fail("SOURCE_PACKET_EXCEEDS_GUARANTEED_BUDGET:"+str(len(raw))+":"+str(round(upper,4)))
    req_sha=sha(raw)
    meta={
      "contract":"ALL_CN_ASTRA_HIGH_OWNER_EXECUTION_v1",
      "mission":MISSION,
      "source_main_sha":os.environ["GITHUB_SHA"],
      "source_manifest_sha256":sha(core.canonical(sources)),
      "source_manifest_count":len(sources),
      "empirical_packet_sha256":sha(empirical.encode("utf-8")),
      "request_sha256":req_sha,"model":MODEL,"effort":EFFORT,
      "input_utf8_bytes":len(raw),"max_output_tokens":MAX_OUTPUT_TOKENS,
      "theoretical_worst_cost_usd":round(upper,7),"owner_cap_usd":MAX_COST_USD,
      "already_used_prior_mission":True,"independent_claude_audit_required":True,
      "first_known_coverage":"UNVERIFIED_ARCHIVAL_FIRST_KNOWN",
      "scope_summary":summary
    }
    put(out/"request.json",payload)
    put(out/"prepared.json",meta)
    print("ALLCN_PREPARED_NO_POST",req_sha,"bytes",len(raw),"cap",MAX_COST_USD,"worst",round(upper,5))

def reserve(out):
    ev=owner_event()
    check_reserve()
    token=core.required_env("GITHUB_TOKEN")
    census(token)
    artifact_census(token)
    data=read(out/"prepared.json")
    if data["request_sha256"]!=sha(core.canonical(read(out/"request.json"))):
        fail("ALLCN_PREPARED_REQUEST_HASH_MISMATCH")
    project=http("GET",core.API+"/models/"+MODEL,
                 api_key=core.required_env("OPENAI_API_KEY"),timeout=30)
    if project.get("id")!=MODEL:
        fail("ASTRA_HIGH_NOT_AVAILABLE_TO_API_PROJECT")
    claim={"mission":MISSION,"source_main_sha":data["source_main_sha"],
           "request_sha256":data["request_sha256"],
           "native_trigger_comment_id":ev["comment"].get("id"),
           "github_run_id":core.required_env("GITHUB_RUN_ID"),
           "posted_before_api":True,"max_billable_posts":1,
           "max_reserved_usd":10,
           "time_utc":datetime.now(timezone.utc).isoformat()}
    body=(CLAIM_MARKER+" run="+claim["github_run_id"]+
          " source_main_sha="+claim["source_main_sha"]+
          " request_sha256="+claim["request_sha256"]+
          " original_trigger_comment_id="+str(claim["native_trigger_comment_id"])+
          " max_exposure_usd=10.00 no_retry=true analysis_only=true")
    response=http("POST","https://api.github.com/repos/"+
                  os.environ["GITHUB_REPOSITORY"]+"/issues/"+str(ISSUE)+"/comments",
                  github_token=token,body={"body":body},timeout=40)
    if type(response.get("id")) is not int:
        fail("NATIVE_PERSISTENT_CLAIM_UNATTESTED_STOP")
    claim["native_claim_comment_id"]=response["id"]
    put(out/"claim.json",claim)
    print("ALLCN_DURABLE_CLAIM_CREATED_NO_PAID_POST",claim["native_claim_comment_id"])

def submit(out):
    claim=read(out/"claim.json");request=read(out/"request.json")
    prepared=read(out/"prepared.json")
    if claim.get("mission")!=MISSION or prepared.get("request_sha256")!=claim.get("request_sha256"):
        fail("ALLCN_DURABLE_CLAIM_MISMATCH")
    if sha(core.canonical(request))!=claim["request_sha256"]:
        fail("ALLCN_REQUEST_MUTATED")
    if (request.get("model")!=MODEL or request.get("reasoning",{}).get("effort")!=EFFORT
            or request.get("background") is not True or request.get("store") is not True):
        fail("ALLCN_REQUEST_UNSAFE")
    put(out/"attempt.json",{
      "mission":MISSION,"request_sha256":claim["request_sha256"],
      "source_main_sha":claim["source_main_sha"],"attempt_count":1,
      "unknown_post_means_no_replay":True,
      "started_at_utc":datetime.now(timezone.utc).isoformat()})
    response=http("POST",core.API+"/responses",
                  api_key=core.required_env("OPENAI_API_KEY"),
                  body=request,timeout=100)
    rid=response.get("id")
    if not isinstance(rid,str) or not RESPONSE_ID.fullmatch(rid):
        fail("ALLCN_REAL_RESPONSE_ID_MISSING_NO_RETRY")
    if response.get("model") not in (MODEL,None):
        fail("ALLCN_RESPONSE_MODEL_MISMATCH")
    put(out/"response_handle.json",{
      "response_id":rid,"initial_status":response.get("status"),
      "mission":MISSION,"request_sha256":claim["request_sha256"],
      "source_main_sha":claim["source_main_sha"],"model":MODEL})
    print("ALLCN_REAL_ASTRA_HIGH_POST",rid,response.get("status"))

def collect(out):
    handle=read(out/"response_handle.json")
    rid=handle.get("response_id")
    if not isinstance(rid,str) or not RESPONSE_ID.fullmatch(rid):
        fail("ALLCN_RESPONSE_HANDLE_INVALID")
    key=core.required_env("OPENAI_API_KEY")
    deadline=time.monotonic()+4800
    while True:
        response=http("GET",core.API+"/responses/"+rid,api_key=key,timeout=75)
        if response.get("id")!=rid or response.get("model") not in (MODEL,None):
            fail("ALLCN_RETRIEVED_MODEL_OR_RESPONSE_MISMATCH")
        status=response.get("status")
        if status not in ("queued","in_progress"):
            break
        if time.monotonic()+15 > deadline:
            print("ALLCN_STILL_RUNNING_GET_ONLY",rid)
            return 2
        time.sleep(15)
    out_text=core.response_text(response)
    usage=response.get("usage") or {}
    inp=usage.get("input_tokens") or 0
    op=usage.get("output_tokens") or 0
    cost=(inp*TOKEN_PRICE_INPUT+op*TOKEN_PRICE_OUTPUT)/1_000_000
    receipt={
      "contract":"ALL_CN_ASTRA_HIGH_EXECUTION_RECEIPT_v1",
      "mission":MISSION,"status":status,"response_id":rid,
      "source_main_sha":handle["source_main_sha"],
      "request_sha256":handle["request_sha256"],"model":response.get("model"),
      "reasoning_effort":EFFORT,"usage":usage,
      "estimated_token_price_usd":round(cost,7),
      "output_sha256":sha(out_text.encode("utf-8")),
      "output_utf8_bytes":len(out_text.encode("utf-8")),
      "claude_audit_required":True,"official_signal_change":False,
      "scientific_skill_promoted":False,
      "created_at_utc":datetime.now(timezone.utc).isoformat(),
    }
    put(out/"receipt.json",receipt)
    if out_text:
        (out/"ASTRA_HIGH_ALL_CN_FULL_HISTORICAL_RESEARCH.md").write_text(out_text,encoding="utf-8")
    if status!="completed" or not out_text or cost>MAX_COST_USD:
        print("ALLCN_OUTPUT_NOT_ADMISSIBLE",status,"estimated_cost",cost)
        return 3
    print("ALLCN_AST RA_COMPLETED".replace(" ",""),rid,receipt["output_sha256"],"estimated_usd",cost)
    return 0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("stage",choices=("prepare","reserve","submit","collect"))
    ap.add_argument("--out",type=Path,default=Path("runtime/astra-allcn"))
    ap.add_argument("--analysis-dir",type=Path,default=Path("runtime/task2-allcn"))
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    fun={"prepare":lambda:prepare(a.out,a.analysis_dir),
         "reserve":lambda:reserve(a.out),
         "submit":lambda:submit(a.out),
         "collect":lambda:collect(a.out)}[a.stage]
    result=fun()
    return result if isinstance(result,int) else 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("ALLCN_AST RA_FAIL_CLOSED".replace(" ",""),type(e).__name__,
              str(e)[:180],file=sys.stderr)
        sys.exit(1)
