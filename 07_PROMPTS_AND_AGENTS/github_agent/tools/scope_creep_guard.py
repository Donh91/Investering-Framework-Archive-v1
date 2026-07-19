#!/usr/bin/env python3
"""Dependency-free, read-only scope-creep guard for Codex diffs."""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

DEPS={"requirements.txt","pyproject.toml","poetry.lock","package.json","package-lock.json","pnpm-lock.yaml","yarn.lock","Pipfile","Pipfile.lock"}
CONTRACT_RE=re.compile(r"(schema|contract|api|protocol|canonical|DATA_PING|portfolio|market)",re.I)
WORKFLOW_RE=re.compile(r"(^|/)\.github/workflows/",re.I)
DIFF_PATH_RE=re.compile(r"^diff --git a/(.*?) b/(.*)$")


def run_git(args):
    return subprocess.run(["git",*args], text=True, capture_output=True, check=False).stdout

def read_diff(ns):
    if ns.staged: return run_git(["diff","--cached","--find-renames"])
    if ns.base: return run_git(["diff","--find-renames",ns.base,"--"])
    if ns.diff == "-": return sys.stdin.read()
    return Path(ns.diff).read_text(encoding="utf-8")

def parse(diff):
    paths=[]; statuses=[]; cur=None; plus=minus=0
    max_hunk=0
    for line in diff.splitlines():
        m=DIFF_PATH_RE.match(line)
        if m:
            if cur: max_hunk=max(max_hunk, plus+minus)
            cur=m.group(2); paths.append(cur); plus=minus=0
        elif line.startswith("deleted file mode"):
            statuses.append({"path":cur,"status":"deleted"})
        elif line.startswith("rename from") or line.startswith("rename to"):
            statuses.append({"path":cur,"status":"renamed"})
        elif line.startswith("@@"):
            max_hunk=max(max_hunk, plus+minus); plus=minus=0
        elif line.startswith("+") and not line.startswith("+++"):
            plus+=1
        elif line.startswith("-") and not line.startswith("---"):
            minus+=1
    if cur: max_hunk=max(max_hunk, plus+minus)
    return sorted(set(paths)), statuses, max_hunk

def subsystem(path):
    parts=Path(path).parts
    return parts[0] if parts else path

def finding(code, classification, evidence):
    return {"code":code,"classification":classification,"evidence":evidence}

def analyze(intent, diff):
    paths,statuses,max_hunk=parse(diff)
    subs=sorted({subsystem(p) for p in paths})
    finds=[]
    allowed=[w.lower().strip("`.,:;()[]") for w in intent.split() if "/" in w or "github" in w.lower() or "agent" in w.lower()]
    unrelated=[p for p in paths if allowed and not any(a in p.lower() for a in allowed)]
    if unrelated and len(subs)>1: finds.append(finding("UNRELATED_PATH_FAMILY","JUSTIFY",unrelated))
    deps=[p for p in paths if Path(p).name in DEPS]
    if deps: finds.append(finding("DEPENDENCY_MANIFEST_CHANGE","BLOCK_REVIEW",deps))
    wf=[p for p in paths if WORKFLOW_RE.search(p)]
    if wf: finds.append(finding("WORKFLOW_OR_SCHEDULE_CHANGE","BLOCK_REVIEW",wf))
    contracts=[p for p in paths if CONTRACT_RE.search(p) and "github_agent/tools" not in p]
    if contracts: finds.append(finding("PUBLIC_CONTRACT_OR_AUTHORITY_SIGNAL","SPLIT",contracts))
    if statuses: finds.append(finding("DESTRUCTIVE_OR_MOVE_SIGNAL","BLOCK_REVIEW",statuses))
    if max_hunk>250: finds.append(finding("OVERSIZED_HUNK","JUSTIFY",max_hunk))
    if not finds: finds.append(finding("NO_SCOPE_CREEP_SIGNALS","KEEP",[]))
    overall="KEEP" if all(f["classification"]=="KEEP" for f in finds) else ("BLOCK_REVIEW" if any(f["classification"]=="BLOCK_REVIEW" for f in finds) else "JUSTIFY")
    return {"tool":"scope_creep_guard","status":overall,"intent":intent,"changed_paths":paths,"subsystems":subs,"findings":finds,"limitations":["Deterministic path/text checks only; no semantic LLM review.","Formatting-only spill is only detectable when represented by diff/path signals.","Market impact is not inferred."]}

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True); g.add_argument("--intent"); g.add_argument("--intent-file")
    s=p.add_mutually_exclusive_group(required=True); s.add_argument("--staged",action="store_true"); s.add_argument("--base"); s.add_argument("--diff")
    ns=p.parse_args(); intent=ns.intent or Path(ns.intent_file).read_text(encoding="utf-8").strip()
    print(json.dumps(analyze(intent, read_diff(ns)), indent=2, sort_keys=True))
if __name__=="__main__": main()
