#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path

AUTHORITY={"framework_state_change":False,"portfolio_action":False}

def classify(repo_bytes:int, artifact_bytes:int|None, artifact_budget:int=500*1024*1024):
    if repo_bytes>=3*1024**3: repo='RED'
    elif repo_bytes>=1*1024**3: repo='ORANGE'
    elif repo_bytes>=500*1024**2: repo='YELLOW'
    else: repo='GREEN'
    if artifact_bytes is None: art='UNKNOWN'
    else:
        r=artifact_bytes/artifact_budget
        art='EMERGENCY' if r>=.9 else 'PROMOTE' if r>=.75 else 'WARN' if r>=.6 else 'GREEN'
    return repo,art

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path('.')); ap.add_argument('--artifact-bytes',type=int); ap.add_argument('--output',type=Path); a=ap.parse_args()
    files=[p for p in a.root.rglob('*') if p.is_file() and '.git' not in p.parts]
    repo_bytes=sum(p.stat().st_size for p in files); largest=sorted((p.stat().st_size,p.as_posix()) for p in files)[-20:]
    repo,art=classify(repo_bytes,a.artifact_bytes)
    out={"contract":"STORAGE_TELEMETRY_v1","repo_worktree_bytes":repo_bytes,"repo_health":repo,"artifact_bytes":a.artifact_bytes,"artifact_health":art,"largest_files":[{"path":p,"bytes":b} for b,p in reversed(largest)],"bulk_commit_allowed":repo not in ('ORANGE','RED'),"authority":AUTHORITY}
    if a.output: a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,sort_keys=True)); return 0 if repo!='RED' else 2
if __name__=='__main__': raise SystemExit(main())
