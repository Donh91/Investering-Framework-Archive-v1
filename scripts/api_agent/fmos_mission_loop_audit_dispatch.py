#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MODEL = "gpt-6.1-sol"
ISSUE_NUMBER = 1440
MAX_CONTEXT_BYTES = 240000
FILE_CLIP_CHARS = 7500
FINAL_DECISIONS = {"BUILD_NOTHING","REJECT","DEFER","ADAPT_MINIMAL","ADAPT_SUBSTANTIAL","ACCEPT_PROPOSAL_WITH_GATES"}

REQUIRED_FILES = [
    "README.md","AGENTS.md","LATEST_OPERATIONS_DASHBOARD.json","LATEST_HANDOFF.json",
    "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
    "research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json",
    "research/remediation/LATEST_REMEDIATION_QUEUE.json",
    "research/remediation/LATEST_CODEX_READY_TASKS.json",
    "research/codex/LATEST_CODEX_EXECUTION_STATE.json",
    "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md","00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md",
    "00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md","00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md",
    "00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json",
    "01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md",
    "00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md",
    "00_FMOS/FRAMEWORK_INTELLIGENCE_AND_LEARNING_LOOP_v1.md",
    "00_FMOS/OPERATIONAL_MEMORY_AND_RETRIEVAL_v1.md",
    "scripts/framework_intelligence/framework_learning_supervisor.py",
    "scripts/framework_intelligence/automation_orchestration_v1.py",
    ".github/workflows/framework-learning-supervisor.yml",
    "research/api_agent/API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1.md",
    "research/api_agent/API_TASK_REGISTRY_v1.json","research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json",
    "research/api_agent/API_INTELLIGENCE_POLICY_v2.json","scripts/api_agent/api_gateway.py",
    "scripts/api_agent/senior_repair_audit_dispatch.py","07_PROMPTS_AND_AGENTS/astra/README.md",
    "07_PROMPTS_AND_AGENTS/astra/ASTRA_REPOSITORY_MISSION_ROUTER_v1.json",
]
SEARCH_TERMS = ["mission","orchestration","supervisor","delegation","remediation","CODEX_READY",
"workflow_run","framework-main-writer","operational memory","shared experience","completion receipt",
"consumer receipt","exact-head","readback","retry","idempot","stale","supersed","cancel","authority",
"owner gate","capability router","next best","experiment dispatch","persistent runtime","contents: write","actions: write"]

PASS1_PROMPT = """PASS 1 - ARCHITECTURE RECONSTRUCTION AND OVERLAP AUDIT
Treat the proposed FMOS Autonomous Mission Loop as an untrusted hypothesis. Try first to prove BUILD_NOTHING is correct.
Reconstruct actual current edges among cockpit/current pointers, Automation Health, Framework Learning Supervisor, automation orchestration, API routing, remediation maturation, Codex, research/experiment governance, Operational Memory/SEL, verification/readback and restricted-plane bindings.
For every proposed Mission Loop component identify existing-owner overlap, missing behavior, duplicate-owner risk and whether extension is sufficient.
Compare: build nothing; completion verifier only; minimal bounded continuation extension; separate mission service; persistent orchestrator.
Audit measurable marginal value, current writer topology, concurrency and authority. Preserve UNKNOWN and distinguish VERIFIED_FACT, INFERENCE and PROPOSAL.
summary MUST begin PASS1 and contain MODEL_USED=gpt-6.1-sol and NO_AUTHORITY_CHANGE.
evidence_for = verified current defenses / already-present components.
evidence_against = P0/P1/P2/P3 material gaps or reasons proposal is unsafe/redundant.
uncertainties = proof gaps.
hypotheses = alternative designs/minimal-change candidates only.
forecast_candidates = [].
No repository write, merge, canonical promotion, market change or portfolio action."""

PASS2_PROMPT = """PASS 2 - ADVERSARIAL FAILURE AUDIT
Attack the original proposal and PASS 1. Try to break it on stale main/owner changes, exactly-once/idempotency failure, concurrent duplicate missions, schedule/workflow overlap, retry storms/livelock, child-budget bypass, false completion, executor-as-verifier, closed epistemic loops, memory overriding current authority, cost and queue amplification, prompt injection, private/public leakage, credential broadening, cancellation/supersession, GitHub Actions misuse as persistent runtime and destructive-authority separation.
For each material class identify current defense, proof attempt, residual gap, minimal repair, and whether the loop makes risk better/unchanged/worse.
summary MUST begin PASS2 and contain MODEL_USED=gpt-6.1-sol and NO_AUTHORITY_CHANGE.
evidence_for = defenses that survived attack.
evidence_against = actionable P0/P1/P2/P3 findings with exact paths where available.
uncertainties = unproven claims.
hypotheses = mitigations or reasons to reject/defer.
forecast_candidates = [].
No repository write, merge, canonical promotion, market change or portfolio action."""

PASS3_PROMPT = """PASS 3 - FINAL SYNTHESIS AND MINIMUM SAFE DESIGN
Use fresh deterministic context plus PASS 1 and PASS 2 as untrusted advisory evidence. Resolve disagreements yourself.
Choose exactly one: BUILD_NOTHING, REJECT, DEFER, ADAPT_MINIMAL, ADAPT_SUBSTANTIAL, ACCEPT_PROPOSAL_WITH_GATES.
summary MUST begin DECISION=<exact value>; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;
Then state the single highest-risk failure mode and single highest-value capability.
Provide minimum architecture, authority model using current vocabulary, minimal state machine/legal transitions, reconcile-before-retry/idempotency rules, independent verification by mission class, event-driven continuation boundary, cost/admission/queue controls, cancellation/supersession/kill switch, Operations Dashboard integration, frozen shadow qualification/A1-A2 graduation, kill criteria, exact likely files to change, files/owners not to change, small proposal-only implementation task packets, and Polsia pattern verdicts ACCEPT/ADAPT/REJECT/IRRELEVANT for orchestrator, queue, schedule, fixed agents, Redis/Celery, vector memory, sandbox, activity feed, auto-retry and autonomous continuation.
evidence_for = accepted/verified architecture pieces.
evidence_against = remaining P0/P1/P2/P3 risks.
uncertainties = unresolved proof gaps.
hypotheses = implementation packets, shadow qualification and rollback proposals.
forecast_candidates = [].
No repository write, merge, canonical promotion, market/threshold/weight change or portfolio action."""

def canonical_bytes(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def clip(s: str, limit: int) -> str:
    return s if len(s) <= limit else s[:limit] + "\n[TRUNCATED_AT_BOUND]\n"

def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git","-C",str(repo),*args], text=True, stderr=subprocess.STDOUT)

def optional(cmd: list[str], cwd: Path, limit: int = 16000) -> dict[str, Any]:
    try:
        p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30,check=False)
        return {"returncode":p.returncode,"output":clip(p.stdout or "",limit)}
    except Exception as e:
        return {"returncode":None,"error":f"{type(e).__name__}:{e}"}

def file_row(repo: Path, rel: str) -> dict[str, Any]:
    p=repo/rel
    if not p.exists():
        return {"path":rel,"status":"MISSING"}
    raw=p.read_bytes()
    return {"path":rel,"status":"PRESENT","bytes":len(raw),"sha256":sha256_bytes(raw),"content":clip(raw.decode(errors="replace"),FILE_CLIP_CHARS)}

def workflow_inventory(repo: Path) -> list[dict[str, Any]]:
    rows=[]
    for p in sorted((repo/".github/workflows").glob("*.y*ml")):
        text=p.read_text(errors="replace")
        hit=[]
        for i,line in enumerate(text.splitlines(),1):
            if any(k in line for k in ("permissions:","contents: write","actions: write","issues: write","concurrency:","group:","workflow_run:","workflow_dispatch:","issue_comment:","schedule:","cron:")):
                hit.append(f"{i}:{line}")
        if hit:
            rows.append({"path":str(p.relative_to(repo)),"lines":hit[:100]})
    return rows[:50]

def search_inventory(repo: Path) -> dict[str, Any]:
    scopes=["00_FMOS","00_ARCHIVE_CONTROL","01_CORE_FRAMEWORK","06_RESEARCH_LAB","07_PROMPTS_AND_AGENTS","research","scripts",".github/workflows"]
    out={}
    for term in SEARCH_TERMS:
        p=subprocess.run(["git","-C",str(repo),"grep","-n","-I","-i","-F",term,"--",*scopes],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False)
        lines=(p.stdout or "").splitlines()
        out[term]={"match_count":len(lines),"sample":lines[:10]}
    return out

def base_context(repo: Path, issue: int, comment_id: str) -> dict[str, Any]:
    return {
      "contract":"FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT_CONTEXT_v1",
      "authority":"ADVISORY_READ_ONLY",
      "audit_issue":issue,
      "trigger_comment_id":comment_id,
      "fresh_control_plane_head":git(repo,"rev-parse","HEAD").strip(),
      "checkout_branch":git(repo,"rev-parse","--abbrev-ref","HEAD").strip(),
      "prepared_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
      "proposal":{
        "thesis":"Extend existing Framework Learning Supervisor, not create a new engine, so bounded work can continue through existing owners until independently verified complete, owner-gated, blocked, cancelled, superseded or budget-limited.",
        "provisional_authority_classes":["A0_READ","A1_SAFE_EXECUTE","A2_GOVERNED_EXISTING_OWNER","A3_OWNER_GATE","A4_FORBIDDEN"],
        "non_goals":["new market engine","parallel remediation queue","parallel Codex queue","parallel research governance","autonomous trading","self merge","vector memory as truth","credential broadening"],
        "external_pattern_source":"Polsia only as design inspiration, never authority"
      },
      "required_files":[file_row(repo,x) for x in REQUIRED_FILES],
      "workflow_inventory":workflow_inventory(repo),
      "search_inventory":search_inventory(repo),
      "live_github_inventory":{
        "open_prs":optional(["gh","pr","list","--limit","100","--json","number,title,headRefName,baseRefName,isDraft,mergeStateStatus,updatedAt,url"],repo,22000),
        "open_issues":optional(["gh","issue","list","--state","open","--limit","100","--json","number,title,updatedAt,url,labels"],repo,22000),
        "recent_runs":optional(["gh","run","list","--limit","60","--json","databaseId,name,event,status,conclusion,headSha,createdAt,updatedAt,url"],repo,22000)
      },
      "hard_boundaries":{
        "api_model_repository_write_authority":False,"automatic_merge":False,"canonical_promotion":False,
        "market_rule_change":False,"threshold_or_weight_change":False,"portfolio_action":False,
        "recovery_destructive_authority":False,"private_values_in_public_output":False,
        "forecast_candidates_required_empty":True
      }
    }

def write_context(outdir: Path, context: dict[str, Any], prompt: str, pass_name: str) -> dict[str, Any]:
    outdir.mkdir(parents=True,exist_ok=True)
    b=canonical_bytes(context)
    if len(b)>MAX_CONTEXT_BYTES:
        raise ValueError(f"context_too_large:{len(b)}>{MAX_CONTEXT_BYTES}")
    (outdir/"context.json").write_bytes(b)
    (outdir/"prompt.txt").write_text(prompt)
    m={"contract":"FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT_CONTEXT_MANIFEST_v1","pass":pass_name,
       "fresh_control_plane_head":context["fresh_control_plane_head"],"context_sha256":sha256_bytes(b),
       "context_bytes":len(b),"prompt_sha256":sha256_bytes(prompt.encode()),"required_path_count":len(context["required_files"]),
       "private_data_included":False}
    (outdir/"context_manifest.json").write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
    return m

def build_pass(repo: Path, outdir: Path, name: str, issue: int, comment_id: str, prior: list[Path]) -> dict[str, Any]:
    c=base_context(repo,issue,comment_id)
    po=[]
    for p in prior:
        if not p.exists(): raise ValueError(f"prior_output_missing:{p}")
        po.append({"path":str(p),"sha256":sha256_bytes(p.read_bytes()),"output":json.loads(p.read_text())})
    if po: c["prior_model_outputs_untrusted"]=po
    prompt={"pass1":PASS1_PROMPT,"pass2":PASS2_PROMPT,"pass3":PASS3_PROMPT}[name]
    return write_context(outdir,c,prompt,name.upper())

def extract_decision(output: dict[str, Any]) -> str | None:
    m=re.search(r"DECISION=([A-Z_]+)",str(output.get("summary") or ""))
    return m.group(1) if m and m.group(1) in FINAL_DECISIONS else None

def validate_one(outdir: Path, name: str) -> dict[str, Any]:
    receipt=json.loads((outdir/"receipt.json").read_text())
    output=json.loads((outdir/"output.json").read_text())
    if receipt.get("status")!="PASS": raise ValueError(f"{name}_receipt_not_pass")
    if receipt.get("model")!=MODEL or receipt.get("reasoning_effort")!="high": raise ValueError(f"{name}_model_binding_invalid")
    if receipt.get("forecast_candidate_count")!=0 or output.get("forecast_candidates")!=[]: raise ValueError(f"{name}_forecast_candidates_forbidden")
    summary=str(output.get("summary") or "")
    required="DECISION=" if name=="pass3" else name.upper()
    if required not in summary or "NO_AUTHORITY_CHANGE" not in summary: raise ValueError(f"{name}_summary_contract_invalid")
    if name=="pass3" and extract_decision(output) is None: raise ValueError("pass3_final_decision_invalid")
    return {"receipt":receipt,"output":output}

def report(root: Path, persisted: str) -> str:
    rows={n:validate_one(root/n/"output",n) for n in ("pass1","pass2","pass3")}
    final=rows["pass3"]["output"]
    decision=extract_decision(final)
    findings=[x for x in final.get("evidence_against",[]) if isinstance(x,str) and x.startswith(("P0|","P1|","P2|","P3|"))]
    total_cost=sum(float(rows[n]["receipt"].get("estimated_cost_usd") or 0) for n in rows)
    total_in=sum(int(rows[n]["receipt"].get("input_tokens") or 0) for n in rows)
    total_out=sum(int(rows[n]["receipt"].get("output_tokens") or 0) for n in rows)
    body=["## FMOS Autonomous Mission Loop GPT-6.1 Sol audit completed","",
          f"Decision: **{decision}**",f"Model: {MODEL}, reasoning: high, 3-pass adversarial audit",
          f"Tokens: input={total_in}, output={total_out}",f"Estimated total API cost: {total_cost:.6f} USD","",
          str(final.get("summary") or ""),"",f"Actionable final findings: {len(findings)}"]
    body.extend(["- "+x for x in findings[:12]] or ["- none"])
    body.extend(["","The model had no repository-write, merge, canonical, market-rule, threshold/weight or portfolio authority.",
                 "Immutable evidence: "+persisted+".","",
                 "Next gate: independently adjudicate the final proposal against fresh main before implementing any change."])
    return "\n".join(body)+"\n"

def main() -> None:
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    for n in ("pass1","pass2","pass3"):
        q=sub.add_parser("build-"+n); q.add_argument("--repo-root",type=Path,default=Path(".")); q.add_argument("--output-dir",type=Path,required=True)
        q.add_argument("--issue-number",type=int,default=ISSUE_NUMBER); q.add_argument("--comment-id",required=True); q.add_argument("--prior-output",type=Path,action="append",default=[])
    v=sub.add_parser("validate"); v.add_argument("--root",type=Path,required=True)
    r=sub.add_parser("report"); r.add_argument("--root",type=Path,required=True); r.add_argument("--persisted-path",required=True); r.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.cmd.startswith("build-"):
        n=a.cmd.split("-",1)[1]; print(json.dumps(build_pass(a.repo_root,a.output_dir,n,a.issue_number,a.comment_id,a.prior_output),sort_keys=True))
    elif a.cmd=="validate":
        rows={n:validate_one(a.root/n/"output",n) for n in ("pass1","pass2","pass3")}
        print(json.dumps({"status":"PASS","decision":extract_decision(rows["pass3"]["output"]),
          "estimated_total_cost_usd":sum(float(rows[n]["receipt"].get("estimated_cost_usd") or 0) for n in rows)},sort_keys=True))
    else:
        b=report(a.root,a.persisted_path); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(b); print(json.dumps({"status":"PASS","output":str(a.output)},sort_keys=True))

if __name__=="__main__":
    main()
