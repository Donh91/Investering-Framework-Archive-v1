#!/usr/bin/env python3
"""Dependency-free, read-only commit archaeology for a tracked file."""
from __future__ import annotations
import argparse, collections, json, re, subprocess

REF_RE=re.compile(r"(?:#\d+|PR\s*#?\d+|pull request\s*#?\d+)",re.I)
SIG_RE=re.compile(r"\b(revert|workaround|todo|fixme|hack|temporary)\b",re.I)

def git(args):
    r=subprocess.run(["git",*args], text=True, capture_output=True, check=False)
    return r.returncode,r.stdout,r.stderr

def linespec(path,start,end):
    return [f"-L{start},{end}:{path}"] if start and end else []

def commits(path,start=None,end=None):
    args=["log","--follow","--format=%H%x1f%aI%x1f%an%x1f%s","--name-only",*linespec(path,start,end),"--",path]
    code,out,err=git(args)
    if code: return [], err.strip()
    items=[]; cur=None
    for line in out.splitlines():
        if "\x1f" in line:
            h,d,a,s=line.split("\x1f",3); cur={"sha":h,"date":d,"author":a,"subject":s,"paths":[]}; items.append(cur)
        elif line.strip() and cur: cur["paths"].append(line.strip())
    return list(reversed(items)), None

def blame(path):
    code,out,_=git(["blame","--line-porcelain","--",path])
    if code: return {"evidence_class":"NOT_DETERMINABLE","counts":{}}
    c=collections.Counter(line[7:] for line in out.splitlines() if line.startswith("author "))
    return {"evidence_class":"FACT_FROM_GIT","counts":dict(sorted(c.items()))}

def analyze(path,start=None,end=None,text=False):
    code,_,_=git(["ls-files","--error-unmatch",path])
    if code:
        return {"tool":"commit_archaeology","path":path,"status":"NOT_TRACKED","evidence_class":"NOT_DETERMINABLE","note":"Path is not tracked by local Git history."}
    timeline,err=commits(path,start,end)
    aliases=sorted({p for c in timeline for p in c["paths"] if p!=path})
    co=collections.Counter(p for c in timeline for p in c["paths"] if p!=path)
    meta=[]
    for c in timeline:
        refs=REF_RE.findall(c["subject"]); sig=SIG_RE.findall(c["subject"])
        if refs or sig: meta.append({"sha":c["sha"],"evidence_class":"HEURISTIC_FROM_COMMIT_TEXT","references":refs,"signals":sig,"subject":c["subject"]})
    return {"tool":"commit_archaeology","path":path,"line_range":[start,end] if start and end else None,"status":"OK","introducing_commit":{"evidence_class":"FACT_FROM_GIT","sha":timeline[0]["sha"] if timeline else None},"timeline":[{k:c[k] for k in ("sha","date","author","subject")} for c in timeline],"aliases_or_renames":{"evidence_class":"FACT_FROM_GIT" if aliases else "NOT_DETERMINABLE","paths":aliases},"co_changed_files":{"evidence_class":"FACT_FROM_GIT","counts":dict(sorted(co.items()))},"metadata_signals":meta,"blame_author_counts":blame(path),"change_risk_note":{"evidence_class":"HEURISTIC_FROM_COMMIT_TEXT","text":"Higher caution if history shows many authors, renames, co-changes, or revert/workaround/TODO signals."},"limitations":["Uses only local Git history; remote PR discussions are not inspected.","Commit text signals are heuristic, not authority.","Blame counts are evidence, not ownership authority."]}

def main():
    p=argparse.ArgumentParser(); p.add_argument("path"); p.add_argument("--start",type=int); p.add_argument("--end",type=int); p.add_argument("--text",action="store_true")
    ns=p.parse_args(); data=analyze(ns.path,ns.start,ns.end,ns.text)
    if ns.text:
        print(f"{data['status']}: {data['path']}"); print(json.dumps(data.get('introducing_commit',{}),sort_keys=True)); return
    print(json.dumps(data,indent=2,sort_keys=True))
if __name__=="__main__": main()
