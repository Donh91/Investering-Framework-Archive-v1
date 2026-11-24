"""Task2 comparison readback, using original immutable A score and CN forecast.

Retrospective source consistency only. No new writer, forecast, or use of
post-issue outcomes for features. First-parent Git clock is not HTTP delivery.
"""
from __future__ import annotations
import json
import math
from statistics import mean
from scripts.research import task2_challenger_a_sqrt_t_vol_band_v1 as A

def first_pinned_path(replay, path):
    # Explicit checkout rather than mutable main/worktree. Reject edit/restore.
    commits = replay._git("log","--first-parent","--reverse","--format=%H",
                          replay.checkout,"--",path).decode().splitlines()
    if len(commits)!=1:
        raise ValueError("TASK2_PINNED_PATH_NOT_IMMUTABLE:"+path)
    first=commits[0]
    replay.require_ancestor(first)
    raw=replay.read_blob(first,path)
    if raw!=replay.read_blob(replay.checkout,path):
        raise ValueError("TASK2_PINNED_PATH_CHANGED")
    blob=replay._git("rev-parse",first+":"+path).decode().strip()
    clock=A.iso(A.utc(replay._git("show","-s","--format=%cI",first).decode().strip()))
    return json.loads(raw), {"commit":first,"blob":blob,"clock":clock}

def point_panel(issued, freeze, bars, original_score):
    """C0 CN expected close vs C1 existing A no-drift anchor on SAME days."""
    paired={(r["asset"],r["day"]) for r in original_score["rows"] if "CN_interval_score" in r}
    if len(paired)!=original_score["paired_rows"]:
        raise ValueError("TASK2_POINT_DUPLICATE_PAIR")
    rows=[]
    for asset,spec in issued["assets"].items():
        points=freeze["daily_price_path"][asset]["points"]
        by_day={p["day"]:p for p in points}
        if len(by_day)!=len(points):
            raise ValueError("TASK2_DUPLICATE_CN_POINT")
        for d in spec["days"]:
            key=(asset,d["day"])
            if key not in paired: continue
            actual=A.realized(bars,asset,A.utc(d["scored_from_utc"]),A.utc(d["end_utc"]))
            p0=spec["P0"]
            cn=by_day[d["day"]]["expected_close"]
            if actual is None or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0
                                     for v in (p0,cn,actual["close"])):
                raise ValueError("TASK2_POINT_SOURCE_INVALID")
            close=actual["close"]
            rows.append({"asset":asset,"day":d["day"],"c0_close":cn,"c1_close":p0,
                         "actual_close":close,"c0_abs_error_fraction":abs(cn-close)/p0,
                         "c1_abs_error_fraction":abs(p0-close)/p0})
    if {(r["asset"],r["day"]) for r in rows}!=paired or len(rows)!=len(paired):
        raise ValueError("TASK2_POINT_DENOMINATOR_MISMATCH")
    def summary(items):
        return {"n":len(items),"c0_mean_abs_error_fraction":mean(r["c0_abs_error_fraction"] for r in items) if items else None,
                "c1_mean_abs_error_fraction":mean(r["c1_abs_error_fraction"] for r in items) if items else None}
    return {"rows":rows,"all":summary(rows),"by_asset":{a:summary([r for r in rows if r["asset"]==a]) for a in ("BTC","ETH")}}

def audit_week(replay, year, week):
    args={"year":year,"week":week}
    issued,ip=first_pinned_path(replay,A.ISSUANCE_PATH.format(**args))
    freeze,fp=first_pinned_path(replay,A.FREEZE_PATH.format(**args))
    score,sp=first_pinned_path(replay,A.SCORE_PATH.format(**args))
    A.verify_issuance_digest(issued)
    expected=f"{year}-W{week:02d}"
    source=issued["source"]
    attested=score["first_main_issuance"]
    if (issued["week"]!=expected or score["week"]!=expected or
        freeze["daily_price_path"]["forecast_week"]!=expected or
        source["clock_class"]!="MAIN_FIRST_PARENT_COMMITTER_CLOCK_NOT_HTTP_DELIVERY" or
        source["freeze_first_main_commit"]!=fp["commit"] or source["freeze_blob_sha"]!=fp["blob"] or
        source["freeze_first_main_utc"]!=fp["clock"] or issued["issue_clock_utc"]!=fp["clock"] or
        attested["first_main_commit"]!=ip["commit"] or attested["first_main_blob_sha"]!=ip["blob"] or
        score["issuance_first_main_utc"]!=ip["clock"] or attested["issuance_first_main_utc"]!=ip["clock"] or
        score["issuance_sha256"]!=issued["issuance_sha256"] or
        score["contract"]!=A.CONTRACT+"_SCORE" or score["decision_status"]!="SHADOW_ONLY_NO_PROMOTION" or
        score["first_http_delivery"]!="UNKNOWN"):
        raise ValueError("TASK2_ORIGINAL_SOURCE_BINDING_MISMATCH")
    monday=A.week_monday(year,week)
    mature=monday+7*A.DAY
    if not A.utc(fp["clock"])<=A.utc(ip["clock"])<mature<=A.utc(sp["clock"])<=mature+A.SCORE_FIRST_MATURITY_GRACE:
        raise ValueError("TASK2_ORIGINAL_CLOCK_MISMATCH")
    pin=score["hourly_bars_commit_sha"]
    replay.require_ancestor(pin)
    A.verify_hourly_bars_pin(replay.repo,pin,sp["commit"],year,week)
    bars=A.load_hourly(replay.repo,monday,mature,git_ref=pin)
    A.verify_replayed_score(score,issued,ip["clock"],freeze,bars)
    A.verify_first_main_paired_outcomes(score,issued,ip["clock"],freeze)
    return {"contract":"CN_MM_TASK2_ORIGINAL_COMPARATOR_READBACK_v1",
            "week":expected,"status":"SOURCE_REPLAYED_DESCRIPTIVE_ONLY",
            "source_checkout":replay.checkout,"original_issue":ip,"original_cn_freeze":fp,
            "original_score":sp,"hourly_pin":pin,"paired_n":score["paired_rows"],
            "interval_metrics":score["aggregate_primary_paired"],
            "point_comparison":point_panel(issued,freeze,bars,score),
            "original_week_winner":score["week_winner_interval_score"],
            "scientific_pit_eligible":False,"first_http_delivery":"UNKNOWN",
            "forecast_authority":False,"edge_established":False,
            "c2_status":"BLOCKED_PENDING_REVIEWED_PROSPECTIVE_ACTIVATION_AND_KNOWN_BY_PROOF"}
