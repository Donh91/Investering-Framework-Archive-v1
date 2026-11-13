#!/usr/bin/env python3
"""Deterministic public-source longitudinal CN/Master Monday data and baseline pack.

No market API, LLM, trades, model promotion, post-hoc first-known, scheduler or writes
outside an explicitly supplied local output directory. Python standard library.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone, date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CN = Path("05_CYCLE_NAVIGATOR")
ACTUAL = Path("03_DAILY_CAPTURE_LOGS/weekly_close/2026")
BACKBONE = Path("research/api_agent/outputs/weekly/2026")
BASE = CN / "weekly/2026"
LEGACY = [
    Path("canonical-project-archive/06_CYCLE_NAVIGATOR/published-x-posts"),
    CN / "published/2026",
    Path("canonical-project-archive/06_CYCLE_NAVIGATOR/historical-posts"),
]
MASTER = [
    Path("canonical-project-archive/07_MASTER_MONDAY/runs"),
    Path("03_WEEKLY_OPERATIONS/master_monday"),
    Path("03_WEEKLY_OPERATIONS/forecast_ledger"),
]
SRC_CONTRACT = "TASK2_ALL_CN_HISTORICAL_REPLAY_v1"
MAX_SOURCE_DOC_BYTES = 40000
MAX_LEGACY_SOURCE_BYTES = 180000
ALLOW_CUTOFF_WEEK = 45  # W46 not maturity-complete on Friday Nov 13.
TIMING_STATUS = "ORIGINAL_IN_REPO_ISSUE_AND_FIRST_DELIVERY_CLOCK_NOT_INDEPENDENTLY_PROVED"
QUOTE = "BINANCE_MARKET_DATA_ONLY_1H_KLINES"
RE = re.compile(r"(BTC|ETH)\s*\$?\s*([\d,]+(?:\.\d+)?)\s*[\u2013\u2014-]\s*\$?\s*([\d,]+(?:\.\d+)?)", re.I)
PRICES = ("BTC", "ETH")
FIELDS = [
    "week", "asset", "source_issue_number", "original_source_path",
    "original_freeze_sha256", "source_pointer_sha256", "source_master_pointer",
    "source_clock_class", "outcome_source_path", "outcome_sha256",
    "observed_hour_count", "target_mature", "forecast_available", "prior_week_available",
    "forecast_low", "forecast_high", "forecast_width_fraction",
    "actual_low", "actual_high", "actual_close", "prior_close",
    "naive_prior_low", "naive_prior_high", "naive_prior_width_fraction",
    "forecast_full_path_covered", "naive_full_path_covered",
    "forecast_close_covered", "naive_close_covered",
    "forecast_boundary_miss_fraction", "naive_boundary_miss_fraction",
    "forecast_midpoint_close_error_fraction_PROXY_ONLY",
    "naive_last_close_error_fraction",
]

def h(data):
    return hashlib.sha256(data).hexdigest()

def read_text(root: Path, path: Path):
    f = root / path
    if not f.is_file() or f.is_symlink():
        return None, None
    data = f.read_bytes()
    if len(data) > MAX_SOURCE_DOC_BYTES:
        return None, {"path":str(path), "sha256":h(data), "bytes":len(data),
                      "state":"TOO_LARGE_FOR_FULL_CORPUS"}
    try:
        return data.decode("utf-8"), {"path":str(path),"sha256":h(data),"bytes":len(data),
                                      "state":"READ_OK"}
    except UnicodeError:
        return None, {"path":str(path),"sha256":h(data),"bytes":len(data),
                      "state":"INVALID_UTF8"}

def read_json(root, path):
    t, meta = read_text(root, path)
    if t is None:
        return None, meta
    try:
        value = json.loads(t)
    except (json.JSONDecodeError, ValueError):
        return None, {**meta, "state":"INVALID_JSON"}
    return value, meta

def n(value):
    if isinstance(value, bool) or not isinstance(value, (float,int)) or not (0<float(value)<10**10):
        return None
    return float(value)

def valid_observed_week(pkg, week):
    if not isinstance(pkg,dict):
        return False, "MISSING_WEEKLY_CLOSE"
    if (pkg.get("contract") != "WEEKLY_MARKET_CLOSE_PACKAGE_v3"
            or pkg.get("final") is not True
            or pkg.get("completeness") != "COMPLETE"
            or pkg.get("iso_year") != 2026 or pkg.get("iso_week") != week
            or pkg.get("source") != QUOTE):
        return False, "OUTCOME_PACKAGE_NOT_FINAL_OR_SOURCE_MISMATCH"
    for asset in ("BTCUSDT","ETHUSDT"):
        v=(pkg.get("symbols") or {}).get(asset) or {}
        days=v.get("daily_ranges") or []
        start=date.fromisocalendar(2026, week, 1)
        expected=[str(start.fromordinal(start.toordinal()+i)) for i in range(7)]
        if (v.get("completeness")!="PASS" or v.get("hour_count")!=168
                or v.get("expected_hour_count")!=168
                or len(days)!=7 or [d.get("date_utc") for d in days]!=expected
                or any(d.get("hour_count")!=24 or n(d.get("close")) is None
                       or n(d.get("low")) is None or n(d.get("high")) is None
                       for d in days)
                or n(v.get("weekly_close")) is None
                or n(v.get("weekly_low")) is None or n(v.get("weekly_high")) is None):
            return False, "ACTUAL_168H_OR_DAILY_GRID_INCOMPLETE_" + asset
    return True, "COMPLETE_168H"

def safe_window(days, start, end):
    selected=days[start:end]
    if len(selected)!=end-start or any(d.get("hour_count")!=24 for d in selected):
        return None
    return {"low":min(d["low"] for d in selected), "high":max(d["high"] for d in selected),
            "close":selected[-1]["close"]}

def check_interval(low, high, actual):
    if None in (low,high) or low<=0 or high<=low:
        return {"full":None,"close":None,"width":None,"miss":None,"midpoint_err_proxy":None}
    ref=actual["prev_close"]
    if ref is None or ref<=0:
        return {"full":None,"close":None,"width":None,"miss":None,"midpoint_err_proxy":None}
    o=actual["observed"]
    return {
        "full":int(o["low"]>=low and o["high"]<=high),
        "close":int(low<=o["close"]<=high),
        "width":round((high-low)/ref,8),
        "miss":round((max(0,low-o["low"])+max(0,o["high"]-high))/ref,8),
        "midpoint_err_proxy":round(abs((low+high)/2-o["close"])/ref,8),
    }

def legacy_documents(root):
    catalog=[]
    texts=[]
    seen=set()
    for base in LEGACY:
        for file in sorted((root/base).glob("*.md")):
            rel=file.relative_to(root)
            content,meta=read_text(root,rel)
            if not meta: continue
            if not (re.search(r"CN[_ -]?0*\d+",file.name,re.I) or
                    "CYCLE_NAVIGATOR_" in file.name):
                continue
            issue_match=re.search(r"(?:CN|CYCLE_NAVIGATOR)[_ -]*0*(\d+)",file.name,re.I)
            num=int(issue_match.group(1)) if issue_match else None
            state="RECOVERED_OR_IMPORT" if "RECOVERED" in file.name or base.name=="historical-posts" else "DOCUMENTED_PUBLICATION_CLAIM"
            # Separate historic text evidence from native machine freeze and first-seen proof.
            row={**meta, "issue_number":num,"origin":str(base),"claim_class":state,
                 "first_known_utc":"UNKNOWN","issuer_original_time_verified":False}
            catalog.append(row)
            if content is not None and meta["sha256"] not in seen:
                texts.append({"path":str(rel),"sha256":meta["sha256"],"issue_number":num,
                              "record_class":state,"text":content})
                seen.add(meta["sha256"])
    return catalog,texts

def master_documents(root):
    catalog=[]
    texts=[]
    for base in MASTER:
        for file in sorted((root/base).rglob("*.md")):
            rel=file.relative_to(root)
            content,meta=read_text(root,rel)
            if not meta: continue
            catalog.append({**meta, "record_class":"MASTER_MONDAY_ARCHIVE_REFERENCE",
                            "original_model_issue_utc":"UNKNOWN"})
            if content and (file.name.startswith(("MM_","MASTER_MONDAY_","2026")) or
                            "final" in file.name.lower()):
                texts.append({"path":str(rel),"sha256":meta["sha256"],
                              "record_class":"MASTER_MONDAY_ARCHIVE_REFERENCE","text":content})
    # All weekly machine packages W32-W45 are inventoried, but not substituted for
    # original CN forecast. Compact extract only; prevent a 14-week JSON overshare.
    for file in sorted((root/BACKBONE).glob("W*/MASTER_MONDAY_MACHINE_PACKAGE.json")):
        rel=file.relative_to(root);content,meta=read_text(root,rel)
        if meta: catalog.append({**meta,"record_class":"MASTER_MONDAY_MACHINE_PACKAGE"})
        if content:
            try:
                x=json.loads(content)
                texts.append({"path":str(rel),"sha256":meta["sha256"],"record_class":"MASTER_MONDAY_MACHINE_PACKAGE",
                              "value":{k:v for k,v in x.items() if k in (
                                "contract","iso_year","iso_week","status","phase","regime",
                                "market_state","market_outlook","summary","generated_at_utc",
                                "source","source_week","forecast","market_data")}})
            except ValueError: pass
    return catalog,texts

def build(root):
    weekly_dirs=sorted((root/BASE).glob("W[0-9][0-9]"))
    market_files=sorted((root/ACTUAL).glob("W[0-9][0-9]/WEEKLY_MARKET_CLOSE_PACKAGE.json"))
    market={}
    manifest=[]
    errors=[]
    for file in market_files:
        p=file.relative_to(root)
        pkg,meta=read_json(root,p)
        if meta:manifest.append(meta)
        week=int(file.parent.name[1:])
        valid,reason=valid_observed_week(pkg,week)
        if not valid:
            errors.append({"source":str(p),"error":reason})
        market[week]={"package":pkg,"meta":meta,"valid":valid,"reason":reason}
    rows=[]
    internal=[]
    weekly=[]
    forecast_corpus=[]
    original_week_count=0
    for week_dir in weekly_dirs:
        w=int(week_dir.name[1:])
        base=week_dir.relative_to(root)
        freeze_path=base/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
        freeze,freeze_meta=read_json(root,freeze_path)
        ptr,ptr_meta=read_json(root,base/"CYCLE_NAVIGATOR_DELIVERY_POINTER.json")
        internal_freeze,internal_meta=read_json(root,base/"CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json")
        if not isinstance(freeze,dict) or not isinstance(ptr,dict):
            errors.append({"week":w,"error":"ORIGINAL_FORECAST_OR_POINTER_MISSING"});continue
        original_week_count+=1
        for meta in (freeze_meta,ptr_meta,internal_meta):
            if meta:manifest.append(meta)
        status=ptr.get("status")
        weekly.append({"week":w,"issue_number":ptr.get("issue_number"),
                       "forecast_freeze_path":str(freeze_path),
                       "forecast_sha256":freeze_meta.get("sha256") if freeze_meta else None,
                       "pointer_status":status,
                       "pointer_sha256":ptr_meta.get("sha256") if ptr_meta else None,
                       "first_public_delivery_utc":"UNKNOWN",
                       "machine_original_issue_utc":"UNKNOWN",
                       "source_master_monday_pointer":ptr.get("master_monday_pointer_sha256"),
                       "historical_freeze_available":True,
                       "internal_claim_count":len(internal_freeze.get("claims",[])) if isinstance(internal_freeze,dict) else 0})
        forecast_corpus.append({"week":w,"forecast":freeze,"delivery_pointer":ptr,
                                "source_file":str(freeze_path),"source_sha256":freeze_meta.get("sha256")})
        if isinstance(internal_freeze,dict):
            for claim in internal_freeze.get("claims",[]):
                mweek=claim.get("maturity_iso_week")
                maturity=(isinstance(mweek,int) and mweek<=ALLOW_CUTOFF_WEEK)
                state=("TARGET_NOT_MATURE" if not maturity
                        else "SEMANTIC_CLAIM_NOT_MACHINE_SCORED" if claim.get("family") not in (
                            "btc_range","eth_range","intraday_day_1_2","intraday_day_3_4","intraday_day_5_7")
                        else "NUMERIC_CLAIM_CAN_BE_COMPARED_WITH_COMPLETE_ACTUALS")
                internal.append({k:claim.get(k) for k in ("claim_id","family","forecast",
                             "horizon","alias_of","maturity_iso_week","maturity_iso_year",
                             "source_public_freeze_sha256","source_machine_package_sha256_at_materialization")}
                                |{"source_week":w,"maturity_complete":maturity,"scientific_status":state,
                                   "original_first_known_utc":"UNKNOWN",
                                   "unscored_reason":"PIT_ISSUE_DELIVERY_NOT_VERIFIED"})
        actual=market.get(w) or {}
        prev=market.get(w-1) or {}
        mature=(w<=ALLOW_CUTOFF_WEEK and actual.get("valid") is True)
        for asset in PRICES:
            current_symbol=(actual.get("package") or {}).get("symbols",{}).get(asset+"USDT") if mature else None
            prev_symbol=(prev.get("package") or {}).get("symbols",{}).get(asset+"USDT") if prev.get("valid") else None
            o= {"low":n(current_symbol.get("weekly_low")),"high":n(current_symbol.get("weekly_high")),"close":n(current_symbol.get("weekly_close"))} if current_symbol else None
            pc=n(prev_symbol.get("weekly_close")) if prev_symbol else None
            low=n(freeze.get(asset.lower()+"_range_low"))
            high=n(freeze.get(asset.lower()+"_range_high"))
            available=low is not None and high is not None and low<high
            row={key:None for key in FIELDS}
            row.update({"week":w,"asset":asset,"source_issue_number":ptr.get("issue_number"),
                        "original_source_path":str(freeze_path),
                        "original_freeze_sha256":freeze_meta.get("sha256"),
                        "source_pointer_sha256":ptr_meta.get("sha256"),
                        "source_master_pointer":ptr.get("master_monday_pointer_sha256"),
                        "source_clock_class":TIMING_STATUS,
                        "outcome_source_path":str(ACTUAL/f"W{w:02d}"/"WEEKLY_MARKET_CLOSE_PACKAGE.json") if actual else None,
                        "outcome_sha256":(actual.get("meta") or {}).get("sha256"),
                        "observed_hour_count":current_symbol.get("hour_count") if current_symbol else None,
                        "target_mature":mature,
                        "forecast_available":available,
                        "prior_week_available":prev_symbol is not None,
                        "forecast_low":low, "forecast_high":high, "actual_low":o["low"] if o else None,
                        "actual_high":o["high"] if o else None, "actual_close":o["close"] if o else None,
                        "prior_close":pc, "naive_prior_low":n(prev_symbol.get("weekly_low")) if prev_symbol else None,
                        "naive_prior_high":n(prev_symbol.get("weekly_high")) if prev_symbol else None,
                       })
            if mature and pc:
                a={"observed":o,"prev_close":pc}
                fc=check_interval(low,high,a) if available else None
                naive=check_interval(n(prev_symbol.get("weekly_low")),n(prev_symbol.get("weekly_high")),a) if prev_symbol else None
                row.update({"forecast_width_fraction":fc["width"] if fc else None,
                    "forecast_full_path_covered":fc["full"] if fc else None,
                    "forecast_close_covered":fc["close"] if fc else None,
                    "forecast_boundary_miss_fraction":fc["miss"] if fc else None,
                    "forecast_midpoint_close_error_fraction_PROXY_ONLY":fc["midpoint_err_proxy"] if fc else None,
                    "naive_prior_width_fraction":naive["width"] if naive else None,
                    "naive_full_path_covered":naive["full"] if naive else None,
                    "naive_close_covered":naive["close"] if naive else None,
                    "naive_boundary_miss_fraction":naive["miss"] if naive else None,
                    "naive_last_close_error_fraction":round(abs(pc-o["close"])/pc,8)})
            rows.append(row)
    # Independent observed-window comparisons for numeric intraday claims, never
    # official claims of precision unless source clock and originally frozen issue verified.
    intraday=[]
    for c in internal:
        if c.get("family") not in ("intraday_day_1_2","intraday_day_3_4","intraday_day_5_7"):
            continue
        w=c["source_week"]
        a=market.get(w) or {}
        if not a.get("valid") or w>ALLOW_CUTOFF_WEEK:continue
        segment={"intraday_day_1_2":(0,2),"intraday_day_3_4":(2,4),
                 "intraday_day_5_7":(4,7)}[c["family"]]
        text=c.get("forecast") or ""
        matches={m.group(1).upper():(float(m.group(2).replace(",","")),
                                        float(m.group(3).replace(",",""))) for m in RE.finditer(text)}
        for asset in PRICES:
            interval=matches.get(asset)
            observed=safe_window(a["package"]["symbols"][asset+"USDT"]["daily_ranges"],*segment)
            actual_src=(a.get("meta") or {}).get("sha256")
            raw={"claim_id":c["claim_id"],"source_week":w,"horizon":c["horizon"],
                 "asset":asset,"original_text":text,"has_parseable_range":interval is not None,
                 "outcome_sha256":actual_src,"observation":observed,
                 "source_clock_class":TIMING_STATUS,"reconstructed_original_issue":False,
                 "alias_of":c["alias_of"]}
            if interval and observed:
                low,high=interval
                raw.update({"forecast_low":low,"forecast_high":high,
                     "full_window_covered":int(observed["low"]>=low and observed["high"]<=high),
                     "window_close_in_band":int(low<=observed["close"]<=high),
                     "max_breach_fraction":round((max(0,low-observed["low"])+max(0,observed["high"]-high))/observed["close"],7)})
            intraday.append(raw)
    lcat,legacy=legacy_documents(root)
    mcat,masters=master_documents(root)
    for doc in lcat+mcat:
        manifest.append({k:doc[k] for k in ("path","sha256","bytes","state") if k in doc})
    summary={
      "contract":SRC_CONTRACT,"source_main_sha":os.environ.get("GITHUB_SHA") or "LOCAL_UNPINNED",
      "valuation_asof_utc":datetime.now(timezone.utc).isoformat(),
      "archive_scope":"ALL_FOUND_2026_CN_WEEKLY_AND_PUBLISHED_MASTER_MONDAY",
      "scoring_cutoff_complete_week":"2026-W45",
      "weeks_with_machine_cn":len(weekly),
      "weeks_with_internal_freeze":sum(w["internal_claim_count"]>0 for w in weekly),
      "internal_claims":len(internal),
      "legacy_cn_published_or_recovered_documents":len(lcat),
      "legacy_distinct_issue_numbers":len({x["issue_number"] for x in lcat if x["issue_number"] is not None}),
      "master_monday_archived_documents":len(mcat),
      "market_completed_week_packages":sum(x.get("valid",False) for x in market.values()),
      "weekly_price_rows_total":len(rows),
      "weekly_price_rows_frozen_and_matured":sum(bool(x["target_mature"] and x["forecast_available"]) for x in rows),
      "weekly_price_rows_frozen_and_matured_with_prior_baseline":sum(bool(x["target_mature"] and x["forecast_available"] and x["prior_week_available"]) for x in rows),
      "intraday_numeric_comparison_rows":len(intraday),
      "source_claims_independently_verified_first_known":0,
      "strict_prospective_skill_eligible_rows":0,
      "note":"Historical archive-based arithmetic, NOT source-clock certified PIT scientific skill. No final W46 label or reissued 14 original claims.",
    }
    byasset={}
    for asset in PRICES:
        matched=[x for x in rows if x["asset"]==asset and x["target_mature"] and x["forecast_full_path_covered"] is not None and x["naive_full_path_covered"] is not None]
        stats={}
        for col in ("forecast_full_path_covered","naive_full_path_covered",
                    "forecast_close_covered","naive_close_covered",
                    "forecast_width_fraction","naive_prior_width_fraction",
                    "forecast_boundary_miss_fraction","naive_boundary_miss_fraction"):
            values=[x[col] for x in matched if isinstance(x[col],(int,float))]
            stats[col+"_mean"]=round(statistics.mean(values),7) if values else None
        stats["matched_independent_weeks"]=len(matched)
        stats["forecast_vs_naive_full_path_cover_diff_pp"]=(round(100*(stats["forecast_full_path_covered_mean"]-stats["naive_full_path_covered_mean"]),3) if matched else None)
        stats["scientific_inference"]="NOT_ESTABLISHED_CLOCK_UNKNOWN_AND_SMALL_N"
        byasset[asset]=stats
    summary["descriptive_paired_benchmark"]=byasset
    summary["errors"]=errors[:60]
    summary["exclusions"]=[
      "W46 outcome incomplete and 7/7 owner revision distinct from original INTERNAL W46 issue",
      "CN 1-23 X-published documents not promoted into machine-frozen original forecasts",
      "W36-W38 numeric freeze ranges often null; do not treat as wrong",
      "2_3_WEEKS and 4_8_WEEKS prose not mathematically scored",
      "source first-known / original consumer delivery UNKNOWN for these archive-only rows",
      "weekly interval width versus containment descriptive, not a probability or quantile score",
      "Fable R5 prospective W47+ / live research remains assigned to Fable, excluded from this retrospective package",
    ]
    return summary, rows, weekly, internal, intraday, lcat, mcat, legacy, masters, forecast_corpus, manifest

def emit(root:Path, out:Path):
    summary, rows, weekly, internal, intraday, lcat, mcat, legacy, masters, forecasts, manifest=build(root)
    out.mkdir(parents=True,exist_ok=True)
    def js(name,value):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,default=str)+"\n",encoding="utf-8")
    def table(name,items,fields=None):
        if not items:return
        fields=fields or sorted(set().union(*(x.keys() for x in items)))
        with (out/name).open("w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore");w.writeheader()
            for item in items:w.writerow({key:item.get(key) for key in fields})
    js("summary.json",summary)
    js("week_source_ledger.json",weekly)
    js("internal_claim_ledger.json",internal)
    js("intraday_window_comparisons.json",intraday)
    js("legacy_archive_index.json",lcat)
    js("master_monday_archive_index.json",mcat)
    js("source_manifest.json",manifest)
    table("weekly_forecast_vs_prior_week_naive.csv",rows,FIELDS)
    table("intraday_window_comparisons.csv",intraday)
    table("internal_claim_ledger.csv",internal)
    # Full non-PIT data retained for inspection. Neither forecast numbers nor market
    # prices are invented when the underlying source is missing.
    js("original_weekly_forecast_corpus.json",forecasts)
    # Empirical body first: every matched row and all internal claims.
    packet={"contract":"ASTRA_ALL_CN_LONGITUDINAL_EMPIRICAL_INPUT_v1",
            "summary":summary,"weekly_rows":rows,"intraday_window_rows":intraday,
            "internal_claims":internal,"forecasts":forecasts,
            "legacy_index":lcat,"master_index":mcat,
            "source_sha_manifest":manifest}
    body=json.dumps(packet,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
    # Preserved text included after deterministic structured data, bounded by
    # HARD budget and dedup using path/digest. No chronology is rewritten.
    remaining=400000-len(body.encode("utf-8"))
    extra=[];seen=set()
    for item in legacy+masters:
        raw=json.dumps(item,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        size=len(raw.encode("utf-8"))
        if size>remaining:continue
        digest=item.get("sha256") or item.get("path")
        if digest in seen:continue
        extra.append(item);seen.add(digest);remaining-=size
    packet["archived_original_text_evidence"]=extra
    packet["omitted_legacy_or_master_text_count"]=(len(legacy)+len(masters)-len(extra))
    body=json.dumps(packet,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
    js("astra_source_pit_empirical_packet.json",packet)
    (out/"astra_empirical_input.txt").write_text(
        "EMPIRICAL SOURCE-PINNED DATA. SOURCE FIRST-KNOWN UNKNOWN, NO AUTOMATIC PIT SKILL CLAIM.\n"
        +body,encoding="utf-8")
    print(json.dumps({"status":"RESEARCH_SOURCE_PACK_COMPLETE","output_dir":str(out),
                      "machine_cn_weeks":summary["weeks_with_machine_cn"],
                      "legacy_documents":summary["legacy_cn_published_or_recovered_documents"],
                      "market_complete_weeks":summary["market_completed_week_packages"],
                      "matched_rows":summary["weekly_price_rows_frozen_and_matured_with_prior_baseline"],
                      "packed_bytes":len(body.encode("utf-8")),
                      "errors":len(summary["errors"])},sort_keys=True))
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    emit(a.root,a.out)

if __name__=="__main__":main()
