#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
from pathlib import Path
from typing import Any

SPAR_PATH = Path("scripts/experiments/spar_v1.py")
CAPTURE_ROOT = Path("03_DAILY_CAPTURE_LOGS/captures")
METHOD_PATH = "06_RESEARCH_LAB/m6_methods/2026-10-05__spar-comparator-feasibility-method-v1.md"


def load_spar(repo_root: Path):
    path = repo_root / SPAR_PATH
    spec = importlib.util.spec_from_file_location("spar_v1_module", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot_load_spar_module")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def cooldown(indices: list[int], snaps, hours: int = 72) -> list[int]:
    out=[]
    last=None
    for idx in sorted(set(indices)):
        if last is None or (snaps[idx].t-snaps[last].t).total_seconds() >= hours*3600:
            out.append(idx)
            last=idx
    return out


def non_overlapping(times, hours: int) -> int:
    n=0
    last=None
    for t in sorted(times):
        if last is None or (t-last).total_seconds() >= hours*3600:
            n += 1
            last=t
    return n


def med(vals):
    vals=[x for x in vals if isinstance(x,(int,float))]
    return statistics.median(vals) if vals else None


def event_summary(mod, snaps, indices: list[int]) -> dict[str, Any]:
    rows=[]
    for idx in indices:
        rows.append({
            "event_timestamp_utc": mod.iso(snaps[idx].t),
            "source_path": snaps[idx].p,
            "outcomes": {str(h): mod.outcome(snaps,idx,h) for h in (24,72,168)},
        })
    horizons={}
    for h in ("24","72","168"):
        matured=[r["outcomes"][h] for r in rows if r["outcomes"][h].get("status")=="MATURED"]
        horizons[h]={
            "matured_count":len(matured),
            "median_btc_return_pct":med([x.get("btc_return_pct") for x in matured]),
            "median_btc_mae_pct":med([x.get("btc_mae_pct") for x in matured]),
            "median_btc_mfe_pct":med([x.get("btc_mfe_pct") for x in matured]),
            "median_eth_return_pct":med([x.get("eth_return_pct") for x in matured]),
            "median_eth_mae_pct":med([x.get("eth_mae_pct") for x in matured]),
            "median_eth_mfe_pct":med([x.get("eth_mfe_pct") for x in matured]),
            "median_ethbtc_return_pct":med([x.get("ethbtc_return_pct") for x in matured]),
        }
    times=[snaps[i].t for i in indices]
    return {
        "event_count":len(indices),
        "non_overlapping_72h_count":non_overlapping(times,72),
        "non_overlapping_168h_count":non_overlapping(times,168),
        "event_timestamps_utc":[mod.iso(t) for t in times],
        "horizons":horizons,
        "events":rows,
    }


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root",type=Path,default=Path("."))
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    root=args.repo_root
    mod=load_spar(root)

    all_snaps,audit=mod.load_snapshots_audit(root/CAPTURE_ROOT)
    cut=max(mod.ts(mod.PREREGISTRATION_UTC),mod.ts(mod.ADAPTER_V2_CUTOVER_UTC))
    snaps=[s for s in all_snaps if s.t >= cut]
    if len(snaps)<2:
        raise ValueError("insufficient_post_cutover_snapshots")

    tr=[mod.transition(snaps[i-1],snaps[i]) for i in range(1,len(snaps))]

    eth=[]
    breadth=[]
    precursor=[]
    strict=[]
    for i,row in enumerate(tr):
        if row["eth_relative_weakness"]:
            eth.append(i+1)
        if row["breadth_deterioration"]:
            breadth.append(i+1)
        if row["btc_resilience"] and row["breadth_deterioration"]:
            precursor.append(i+1)
            j=next(
                (j for j in range(i+1,min(len(tr),i+3)) if tr[j]["eth_relative_weakness"]),
                None,
            )
            if j is not None:
                strict.append(j+1)

    ids={
        "TARGET_STRICT_P3":cooldown(strict,snaps),
        "PRIMARY_COMPARATOR_ETH_WEAKNESS":cooldown(eth,snaps),
        "SECONDARY_COMPARATOR_BREADTH":cooldown(breadth,snaps),
        "PRECURSOR_ONLY":cooldown(precursor,snaps),
        "REFERENCE_V1_P3":mod.detect_events(snaps,72)["SPAR-P3"],
    }

    summaries={name:event_summary(mod,snaps,idxs) for name,idxs in ids.items()}
    target=set(ids["TARGET_STRICT_P3"])
    overlap={}
    for name,idxs in ids.items():
        if name=="TARGET_STRICT_P3":
            continue
        s=set(idxs)
        overlap[name]={
            "exact_event_index_overlap_count":len(target&s),
            "target_event_count":len(target),
            "comparator_event_count":len(s),
        }

    primary=summaries["PRIMARY_COMPARATOR_ETH_WEAKNESS"]["horizons"]["72"]
    target72=summaries["TARGET_STRICT_P3"]["horizons"]["72"]
    descriptive_delta={
        "btc_return_median_delta_pp": (
            target72["median_btc_return_pct"]-primary["median_btc_return_pct"]
            if target72["median_btc_return_pct"] is not None and primary["median_btc_return_pct"] is not None else None
        ),
        "btc_mae_median_delta_pp": (
            target72["median_btc_mae_pct"]-primary["median_btc_mae_pct"]
            if target72["median_btc_mae_pct"] is not None and primary["median_btc_mae_pct"] is not None else None
        ),
        "note":"DISCOVERY_ONLY. A negative delta is not inferential incremental value."
    }

    result={
        "contract":"M6_SPAR_COMPARATOR_FEASIBILITY_v1",
        "mission_id":"RL-DISTRIBUTION-SURVIVAL-META-006",
        "status":"DISCOVERY_ONLY_NOT_CONFIRMATORY",
        "method_path":METHOD_PATH,
        "source":{
            "capture_root":str(CAPTURE_ROOT),
            "post_cutover_start_utc":mod.iso(cut),
            "eligible_snapshot_count":len(snaps),
            "first_snapshot_utc":mod.iso(snaps[0].t),
            "last_snapshot_utc":mod.iso(snaps[-1].t),
            "source_audit":audit,
        },
        "event_definitions":{
            "TARGET_STRICT_P3":"BTC resilience + breadth deterioration, then ETH relative weakness on one of the next two transitions; never same transition; 72h cooldown.",
            "PRIMARY_COMPARATOR_ETH_WEAKNESS":"Any ETH relative weakness transition; 72h cooldown.",
            "SECONDARY_COMPARATOR_BREADTH":"Any breadth deterioration transition; 72h cooldown.",
            "PRECURSOR_ONLY":"BTC resilience + breadth deterioration same transition; 72h cooldown.",
            "REFERENCE_V1_P3":"Existing SPAR-v1 P3 semantics, reference only."
        },
        "summaries":summaries,
        "overlap_diagnostics":overlap,
        "descriptive_target_minus_primary_72h":descriptive_delta,
        "decision_inputs":{
            "target_event_count":summaries["TARGET_STRICT_P3"]["event_count"],
            "target_matured_72h_count":target72["matured_count"],
            "primary_comparator_event_count":summaries["PRIMARY_COMPARATOR_ETH_WEAKNESS"]["event_count"],
            "primary_comparator_matured_72h_count":primary["matured_count"],
            "zero_paid_data":True,
            "confirmation_authorized":False,
        },
        "interpretation_boundary":[
            "Comparator definitions were frozen before this replay, but were not part of original SPAR-v1 preregistration.",
            "All results are feasibility/discovery evidence only.",
            "A stricter P3 identity requires a new prospective experiment identity for any confirmatory claim.",
            "No historical median difference authorizes a market, exit or portfolio rule.",
            "A future design must still freeze placebo/regime mechanics and multiplicity before outcome visibility."
        ],
        "authority":{
            "market_rule_change":False,
            "portfolio_action":False,
            "canonical_promotion":False,
            "live_exit_rule":False,
        }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":"PASS",
        "target":result["decision_inputs"],
        "delta":descriptive_delta,
        "counts":{k:v["event_count"] for k,v in summaries.items()},
    },sort_keys=True))


if __name__=="__main__":
    main()
