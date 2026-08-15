#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GAP_MARKERS = (
    "no conclusion", "not supplied", "unavailable", "unknown", "missing", "insufficient",
    "cannot evaluate", "not retrieved", "not confirmed", "would have", "could have",
    "no history", "no broader", "not establish persistence", "not sourceable"
)


def canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canonical(v)).hexdigest()


def iter_strings(v: Any, path: str = "$"):
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, item in enumerate(v):
            yield from iter_strings(item, f"{path}[{i}]")
    elif isinstance(v, dict):
        for k, item in v.items():
            yield from iter_strings(item, f"{path}.{k}")


def is_gap(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in GAP_MARKERS)


def lane_for(text: str, catalog: dict[str, Any]) -> str | None:
    low = text.lower()
    scored = []
    for lane, spec in catalog.get("lanes", {}).items():
        hits = sum(term.lower() in low for term in spec.get("match_terms", []))
        if hits:
            scored.append((hits, lane))
    return sorted(scored, reverse=True)[0][1] if scored else None


def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text[:1200]


def episode_id(path: Path, payload: dict[str, Any]) -> str:
    stamp = payload.get("run_id") or payload.get("response_id") or payload.get("created_at_utc") or payload.get("created_unix")
    return f"{path.as_posix()}::{stamp or 'NA'}"


def load_registry(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict) and isinstance(data.get("candidates"), dict):
                return data
        except Exception:
            pass
    return {"contract":"ADAPTIVE_EVIDENCE_GAP_REGISTRY_v1","candidates":{},"authority":{"canonical_state":False,"portfolio_action":False,"automatic_sensor_promotion":False}}


def candidate_key(lane: str | None, text: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:90]
    return f"{lane or 'UNCLASSIFIED'}::{token}"


def scan_file(path: Path, catalog: dict[str, Any], registry: dict[str, Any], now: str) -> int:
    try:
        payload = json.loads(path.read_text())
    except Exception:
        return 0
    if not isinstance(payload, (dict, list)):
        return 0
    ep = episode_id(path, payload if isinstance(payload, dict) else {})
    created = 0
    for json_path, raw in iter_strings(payload):
        text = normalize(raw)
        if len(text) < 12 or not is_gap(text):
            continue
        lane = lane_for(text, catalog)
        key = candidate_key(lane, text)
        cands = registry["candidates"]
        if key not in cands:
            spec = catalog.get("lanes", {}).get(lane, {}) if lane else {}
            cands[key] = {
                "candidate_id": "EG-" + sha({"key":key})[:12],
                "lane": lane or "UNCLASSIFIED",
                "status": "SOURCE_CLASSIFIED" if lane else "DISCOVERED",
                "first_seen_utc": now,
                "last_seen_utc": now,
                "discovery_only_episode": ep,
                "discovery_text": text,
                "source_mode": spec.get("mode", "RESEARCH_ONLY"),
                "backfill": spec.get("backfill", "UNKNOWN"),
                "prospective": bool(spec.get("prospective", False)),
                "auto_provision": bool(spec.get("auto_provision", False)),
                "occurrences": 0,
                "independent_episode_count": 0,
                "episodes": [],
                "validation": {
                    "discovery_episode_counts_as_validation": False,
                    "non_discovery_episode_count": 0,
                    "incremental_value": "UNTESTED",
                    "promotion_review_eligible": False
                }
            }
            created += 1
        cand = cands[key]
        cand["last_seen_utc"] = now
        cand["occurrences"] += 1
        if ep not in cand["episodes"]:
            cand["episodes"].append(ep)
            cand["independent_episode_count"] = len(cand["episodes"])
        cand.setdefault("observations", [])
        obs = {"episode":ep,"path":path.as_posix(),"json_path":json_path,"text":text}
        if obs not in cand["observations"]:
            cand["observations"].append(obs)
            cand["observations"] = cand["observations"][-30:]
    return created


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--roots", type=Path, nargs="+", required=True)
    ap.add_argument("--requests-output", type=Path, required=True)
    args=ap.parse_args()
    catalog=json.loads(args.catalog.read_text()); registry=load_registry(args.registry)
    now=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    files=[]
    for root in args.roots:
        if root.exists(): files.extend(root.rglob("*.json"))
    files=sorted(set(files), key=lambda p:p.stat().st_mtime if p.exists() else 0)[-500:]
    created=0
    for path in files: created += scan_file(path,catalog,registry,now)
    requests=[]; research=[]
    for cand in registry["candidates"].values():
        if cand.get("auto_provision") and cand.get("status") in {"SOURCE_CLASSIFIED","DISCOVERED"}:
            requests.append({"candidate_id":cand["candidate_id"],"lane":cand["lane"],"mode":cand["source_mode"],"backfill":cand["backfill"],"action":"ACTIVATE_OR_VERIFY_SHADOW_EVIDENCE_LANE"})
        elif not cand.get("auto_provision"):
            research.append({"candidate_id":cand["candidate_id"],"lane":cand["lane"],"action":"RESEARCH_SOURCE_AND_PROSPECTIVE_DESIGN"})
    registry["updated_at_utc"]=now
    registry["counts"]={"candidates":len(registry["candidates"]),"auto_provision_requests":len(requests),"research_candidates":len(research)}
    args.registry.parent.mkdir(parents=True,exist_ok=True); args.registry.write_text(json.dumps(registry,indent=2,sort_keys=True)+"\n")
    out={"contract":"EVIDENCE_GAP_ACQUISITION_REQUESTS_v1","created_at_utc":now,"auto_provision_requests":requests,"research_queue_candidates":research,"authority":{"market_rule_change":False,"canonical_state_change":False,"portfolio_action":False,"automatic_sensor_promotion":False}}
    args.requests_output.parent.mkdir(parents=True,exist_ok=True); args.requests_output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","scanned_files":len(files),"new_candidates":created,**registry["counts"]},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
