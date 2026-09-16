#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

AUTH = {"canonical_effect":False,"portfolio_execution":False,"automatic_promotion":False,"automatic_skill_activation":False,"automatic_repository_write":False}
SELF_PREFIX=("research: refresh framework learning supervisor","research: refresh operational memory")
STOP={"a","an","and","as","at","by","for","from","in","into","of","on","or","the","to","v1","v2","v3","with","without"}
ACTIONS={"fix","repair","correct","harden","hardening","close","retire","reconcile","restore","resolve","patch","prevent","build","add","implement","install","activate","extend","bind","archive","preserve","research","audit","preregister","qualify"}

def load(p,d=None):
    try:return json.loads(Path(p).read_text())
    except Exception:return d
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def git(root,*args,check=True):
    r=subprocess.run(["git","-C",str(root),*args],text=True,capture_output=True)
    if check and r.returncode: raise RuntimeError(r.stderr.strip())
    return r.stdout
def head(root):return git(root,"rev-parse","HEAD").strip()
def toks(s):return [x for x in re.findall(r"[a-z0-9]+",s.lower()) if x not in STOP and len(x)>1]
def task_class(text,paths=()):
    b=(text+" "+" ".join(paths)).lower()
    if "cycle navigator" in b or "05_cycle_navigator" in b:return "CYCLE_NAVIGATOR"
    if "moonshot" in b or "meme alpha" in b:return "MEME_ALPHA"
    if "compounding learning" in b or "framework_learning" in b:return "FRAMEWORK_LEARNING"
    if "remediation" in b or "automation health" in b or "workflow" in b:return "AUTOMATION_REMEDIATION"
    if "auto_trading" in b or "auto trading" in b or "edgeonchain" in b:return "AUTO_TRADING_RESEARCH"
    if "api_agent" in b or "api agent" in b:return "API_AGENT"
    if "archive" in b or "preserve" in b or "retention" in b:return "RESEARCH_ARCHIVE"
    if "master monday" in b:return "MASTER_MONDAY"
    if "data ping" in b or "market state" in b or "handlekompas" in b:return "MARKET_STATE"
    return "GENERAL_FRAMEWORK"
def operation(s):
    s=s.lower()
    if any(x in s for x in ("fix","repair","correct","resolve","restore","reconcile","patch")):return "FIX"
    if any(x in s for x in ("harden","hardening","prevent","retire")):return "HARDEN"
    if any(x in s for x in ("build","add","implement","install","activate","extend","bind")):return "BUILD"
    if any(x in s for x in ("research","audit","preregister","qualify","adjudicat")):return "RESEARCH"
    if any(x in s for x in ("archive","preserve","retention")):return "ARCHIVE"
    return "UPDATE"
def signature(s):
    q=[x for x in toks(s) if x not in ACTIONS] or toks(s)
    return "-".join(q[:8])[:120]
def prefix(paths):
    c=Counter(Path(p).parts[0] for p in paths if Path(p).parts)
    return c.most_common(1)[0][0] if c else None
def blob(root,rev,path):
    x=git(root,"rev-parse",f"{rev}:{path}",check=False).strip()
    return x if re.fullmatch(r"[0-9a-f]{40}",x) else None
def compat(src,cur):
    if not src:return {"status":"UNKNOWN","same":0,"changed":0,"removed":0,"checked":0}
    same=changed=removed=0
    for p,o in src.items():
        n=cur.get(p)
        if n is None:removed+=1
        elif n==o:same+=1
        else:changed+=1
    n=len(src)
    st="REMOVED" if removed==n else "EXACT" if changed==0 and removed==0 else "DRIFTED" if same==0 else "PARTIAL"
    return {"status":st,"same":same,"changed":changed,"removed":removed,"checked":n}
def commits(root,n):
    raw=git(root,"log","--first-parent",f"-n{n}","--date=iso-strict","--format=%H%x1f%cI%x1f%s%x1f%b%x1e")
    out=[]
    for b in raw.split("\x1e"):
        b=b.strip("\n\r")
        if not b:continue
        p=b.split("\x1f",3)
        if len(p)==4:out.append(dict(zip(("sha","timestamp","subject","body"),[x.strip() for x in p])))
    return out
def paths(root,sha):
    return [x.strip() for x in git(root,"diff-tree","--root","--no-commit-id","--name-only","-r",sha).splitlines() if x.strip()][:60]
def episode(root,r):
    s=r["subject"]
    if not s or s.lower().startswith(SELF_PREFIX):return None
    ps=paths(root,r["sha"]);op=operation(s);src={p:blob(root,r["sha"],p) for p in ps[:25]}
    body=" ".join(x.strip() for x in r["body"].splitlines() if x.strip())[:600] or s
    return {"contract":"OPERATIONAL_EPISODE_v1","episode_id":"OE-"+r["sha"][:16],"source_kind":"MERGED_MAIN_COMMIT","source_commit_sha":r["sha"],"source_timestamp":r["timestamp"],"task_class":task_class(s+"\n"+r["body"],ps),"operation_type":op,"task_summary":s,"resolution_summary":body,"failure_signature":signature(s) if op in {"FIX","HARDEN"} else None,"changed_paths":ps,"dominant_path_prefix":prefix(ps),"source_blob_shas":src,"outcome":"MERGED_TO_MAIN","failed_approaches":[],"reusable_pattern":None,"evidence_limits":["Merged commit proves accepted repository change, not causal effectiveness by itself.","No failed approach is inferred unless separately evidenced.","No chain-of-thought or raw prompt is stored."],"authority":AUTH}
def ep_path(out,e):
    try:d=datetime.fromisoformat(e["source_timestamp"].replace("Z","+00:00"));ym=(str(d.year),f"{d.month:02d}")
    except Exception:ym=("unknown","unknown")
    return out/"episodes"/ym[0]/ym[1]/f'{e["episode_id"]}.json'
def harvest(root,out,n=250):
    made=[];skipped=0
    for r in reversed(commits(root,n)):
        e=episode(root,r)
        if e is None:skipped+=1;continue
        p=ep_path(out,e)
        if not p.exists():write(p,e);made.append(p)
    return made,skipped
def episodes(out):
    rows=[]
    for p in sorted((out/"episodes").rglob("OE-*.json")) if (out/"episodes").exists() else []:
        e=load(p,{})
        if e.get("contract")=="OPERATIONAL_EPISODE_v1":e["_path"]=str(p.relative_to(out));rows.append(e)
    return sorted(rows,key=lambda x:(x.get("source_timestamp",""),x.get("episode_id","")))
def index(root,eps,when):
    latest={}
    for e in eps:
        k=(e.get("task_class",""),e.get("failure_signature",""))
        if k[1]:latest[k]=e["episode_id"]
    cache={};rows=[]
    for e in eps:
        src=e.get("source_blob_shas") or {}
        for p in src:
            if p not in cache:cache[p]=blob(root,"HEAD",p)
        cp=compat(src,{p:cache.get(p) for p in src});k=(e.get("task_class",""),e.get("failure_signature",""))
        newer=latest.get(k) if k[1] and latest.get(k)!=e["episode_id"] else None
        tier="REVALIDATE" if cp["status"] in {"DRIFTED","REMOVED"} else "WARM"
        rows.append({"episode_id":e["episode_id"],"source_commit_sha":e["source_commit_sha"],"source_timestamp":e["source_timestamp"],"task_class":e["task_class"],"operation_type":e["operation_type"],"task_summary":e["task_summary"],"failure_signature":e.get("failure_signature"),"dominant_path_prefix":e.get("dominant_path_prefix"),"changed_paths":e.get("changed_paths",[])[:25],"compatibility":cp,"retrieval_tier":tier,"newer_related_episode":newer,"episode_path":e["_path"]})
    return {"contract":"OPERATIONAL_MEMORY_INDEX_v1","authority":AUTH,"generated_at_utc":when,"source_head_sha":head(root),"episode_count":len(rows),"rows":rows}
def candidates(idx,when):
    g=defaultdict(list)
    for r in idx["rows"]:
        if r["operation_type"] not in {"FIX","HARDEN","BUILD"}:continue
        fam="REMEDIATION" if r["operation_type"] in {"FIX","HARDEN"} else "BUILD"
        g[(r["task_class"],fam,r.get("dominant_path_prefix"))].append(r)
    out=[]
    for (tc,fam,pr),rs in g.items():
        cs={r["source_commit_sha"] for r in rs}
        if len(cs)<3:continue
        cid=hashlib.sha256(f"{tc}|{fam}|{pr}".encode()).hexdigest()[:16]
        out.append({"candidate_id":"PC-"+cid,"task_class":tc,"operation_family":fam,"dominant_path_prefix":pr,"independent_commit_count":len(cs),"currently_compatible_count":sum((r["compatibility"]["status"] in {"EXACT","PARTIAL"}) for r in rs),"supporting_episode_ids":[r["episode_id"] for r in rs[-8:]],"failure_signature_diversity":len({r.get("failure_signature") for r in rs if r.get("failure_signature")}),"status":"CANDIDATE_ONLY","automatic_skill_activation":False,"promotion_allowed":False,"required_next_gate":"GOVERNED_SKILL_REVIEW_WITH_CLEAR_PRECONDITIONS_EXIT_CRITERIA_FAILURE_MODES_AND_VERSIONING"})
    out.sort(key=lambda x:(-x["independent_commit_count"],x["task_class"],x["operation_family"]))
    return {"contract":"OPERATIONAL_PROCEDURAL_CANDIDATES_v1","authority":AUTH,"generated_at_utc":when,"promotion_policy":"NO_AUTOMATIC_SKILL_PROMOTION","candidate_count":len(out),"candidates":out[:50]}
def overlap(a,b):
    a,b=set(toks(a)),set(toks(b));return len(a&b)/len(a|b) if a and b else 0
def path_overlap(q,c):
    if not q or not c:return 0
    if set(q)&set(c):return min(1,len(set(q)&set(c))/max(1,len(set(q))))
    qp={Path(x).parts[0] for x in q if Path(x).parts};cp={Path(x).parts[0] for x in c if Path(x).parts};return len(qp&cp)/max(1,len(qp|cp))
def score(task,qpaths,fail,r):
    s=35 if r["task_class"]==task_class(task,qpaths) else 0;s+=30*path_overlap(qpaths,r.get("changed_paths",[]));s+=25*overlap(task+" "+(fail or ""),str(r.get("task_summary",""))+" "+str(r.get("failure_signature","")))
    if fail and r.get("failure_signature")==signature(fail):s+=15
    st=r["compatibility"]["status"];s+=8 if st=="EXACT" else 4 if st=="PARTIAL" else -15 if st=="DRIFTED" else -30 if st=="REMOVED" else 0
    if r.get("newer_related_episode"):s-=5
    return round(s,3)
def preflight(idx,task,qpaths,fail=None,top=5):
    ranked=[]
    for r in idx["rows"]:
        z=score(task,qpaths,fail,r)
        if z>0:x=dict(r);x["retrieval_score"]=z;ranked.append(x)
    ranked.sort(key=lambda x:-x["retrieval_score"]);sel=ranked[:max(1,min(top,10))]
    return {"contract":"OPERATIONAL_MEMORY_PREFLIGHT_v1","authority":AUTH,"task":task,"task_class":task_class(task,qpaths),"query_paths":qpaths,"source_index_head_sha":idx["source_head_sha"],"candidate_count":len(ranked),"selected_count":len(sel),"reusable_prior_work":[{"episode_id":x["episode_id"],"source_commit_sha":x["source_commit_sha"],"task_summary":x["task_summary"],"episode_path":x["episode_path"],"compatibility":x["compatibility"]["status"],"retrieval_score":x["retrieval_score"]} for x in sel if x["compatibility"]["status"] in {"EXACT","PARTIAL"}],"revalidation_required":[{"episode_id":x["episode_id"],"reason":x["compatibility"]["status"],"source_commit_sha":x["source_commit_sha"]} for x in sel if x["compatibility"]["status"] in {"DRIFTED","REMOVED"}],"known_failure_patterns":[{"episode_id":x["episode_id"],"failure_signature":x["failure_signature"],"task_summary":x["task_summary"]} for x in sel if x.get("failure_signature")],"selected":sel,"usage_instruction":"Acceleration context only. Re-read current authoritative files before acting. Memory never overrides current main.","telemetry":{"context_savings_baseline_status":"BASELINE_REQUIRED","repeated_investigation_baseline_status":"BASELINE_REQUIRED","no_savings_claim_without_measurement":True}}
def health(idx,cand,when):
    ids=[r["episode_id"] for r in idx["rows"]];dups=[k for k,v in Counter(ids).items() if v>1];bad=[r["episode_id"] for r in idx["rows"] if not r.get("source_commit_sha")]
    return {"contract":"OPERATIONAL_MEMORY_HEALTH_v1","generated_at_utc":when,"status":"PASS" if not dups and not bad else "FAIL","authority":AUTH,"episode_count":len(ids),"compatibility_counts":dict(Counter(r["compatibility"]["status"] for r in idx["rows"])),"procedural_candidate_count":cand["candidate_count"],"duplicate_episode_ids":dups,"episodes_missing_source_commit":bad,"retrieval_policy":"DETERMINISTIC_FIRST_NO_VECTOR_DB_NO_MODEL_CALLS","source_of_truth":"CURRENT_GITHUB_MAIN","memory_role":"DERIVED_ACCELERATION_LAYER_ONLY"}
def do_harvest(a):
    root=Path(a.repo_root);out=root/a.output_root;made,sk=harvest(root,out,a.max_commits);when=datetime.now(timezone.utc).isoformat().replace("+00:00","Z");idx=index(root,episodes(out),when);cand=candidates(idx,when);h=health(idx,cand,when)
    write(out/"LATEST_OPERATIONAL_MEMORY_INDEX.json",idx);write(out/"LATEST_PROCEDURAL_CANDIDATES.json",cand);write(out/"LATEST_OPERATIONAL_MEMORY_HEALTH.json",h)
    state={"contract":"OPERATIONAL_MEMORY_AND_RETRIEVAL_v1","generated_at_utc":when,"status":h["status"],"source_head_sha":idx["source_head_sha"],"new_episode_count":len(made),"episode_count":idx["episode_count"],"procedural_candidate_count":cand["candidate_count"],"self_generated_commits_skipped":sk,"authority":AUTH};write(out/"LATEST_OPERATIONAL_MEMORY_STATE.json",state);print(json.dumps(state,sort_keys=True))
def do_preflight(a):
    root=Path(a.repo_root);out=root/a.output_root;idx=load(out/"LATEST_OPERATIONAL_MEMORY_INDEX.json",{})
    if idx.get("contract")!="OPERATIONAL_MEMORY_INDEX_v1":raise SystemExit("operational memory index missing; run harvest first")
    if idx.get("source_head_sha")!=head(root):idx=index(root,episodes(out),datetime.now(timezone.utc).isoformat().replace("+00:00","Z"))
    doc=preflight(idx,a.task,a.path or [],a.failure_signature,a.top_k)
    if a.output:write(a.output,doc)
    print(json.dumps(doc,sort_keys=True))
def main():
    p=argparse.ArgumentParser();p.add_argument("--repo-root",default=".");p.add_argument("--output-root",default="research/framework_learning/operational_memory");sp=p.add_subparsers(dest="cmd",required=True)
    h=sp.add_parser("harvest");h.add_argument("--max-commits",type=int,default=250);h.set_defaults(fn=do_harvest)
    q=sp.add_parser("preflight");q.add_argument("--task",required=True);q.add_argument("--path",action="append",default=[]);q.add_argument("--failure-signature");q.add_argument("--top-k",type=int,default=5);q.add_argument("--output");q.set_defaults(fn=do_preflight)
    a=p.parse_args();a.fn(a)
if __name__=="__main__":main()
