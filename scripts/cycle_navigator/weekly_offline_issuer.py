"""API-free, source-first weekly CN scenario issuer (existing owner #1516).

Forecasts are uncertain hypotheses. This is not replay, measured economic edge,
an API response, a trade action or an override of archived prior forecasts.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date
import math

METHOD = "CN_OWNER_AUTHORIZED_API_FREE_SEVEN_DAY_v1"
DIM_IDS = ("REGIME_RESILIENCE", "LEADERSHIP", "ROTATION_TRANSMISSION",
           "BREADTH_PERSISTENCE", "FLOW_QUALITY_FRAGILITY")
DOWN_SEQ = (-.7, -.55, .35, -.45, .9, .65, -.3)
UP_SEQ = (.7, .55, -.35, .45, -.9, -.65, .3)


def build_offline_value(context, baseline, previous, year, week, issue, public_issue):
    source = context.get("completed_week_hourly_capture") or {}
    mm = context.get("master_monday_pointer") or {}
    diag = source.get("hourly_gap_diagnostics") or {}
    if (source.get("contract") != "WEEKLY_RAW_CALIBRATION_PACK_v3"
        or source.get("readiness") != "READY"
        or source.get("iso_year") != mm.get("iso_year")
        or source.get("iso_week") != mm.get("iso_week")
        or diag.get("observed_hours") != 168 or diag.get("missing_hour_count") != 0
        or not source.get("source_capture_paths")):
        raise ValueError("CN_OFFLINE_SOURCE_UNQUALIFIED")
    if (baseline.get("status") != "READY" or
        baseline.get("target_iso_year") != year or baseline.get("target_iso_week") != week or
        baseline.get("anchor_contiguous") is not True):
        raise ValueError("CN_OFFLINE_BASELINE_UNQUALIFIED")
    if previous is None or previous.get("contract") != "CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1":
        raise ValueError("CN_OFFLINE_PRIOR_ISSUE_UNAVAILABLE")
    week_id = "%04d-W%02d" % (year, week)
    assets, weekly_ranges = {}, {}
    moves = {}
    for asset in ("BTC", "ETH"):
        completed = source["hourly_sequence"][asset.lower()]["week_range"]
        predicted = baseline["assets"][asset]
        if predicted.get("status") != "READY":
            raise ValueError("CN_OFFLINE_ASSET_BASELINE_UNAVAILABLE:" + asset)
        anchor, opened = float(completed["close"]), float(completed["open"])
        low, high = float(predicted["low"]), float(predicted["high"])
        if (not all(math.isfinite(x) for x in (anchor, opened, low, high))
            or not 0 < low < anchor < high or opened <= 0):
            raise ValueError("CN_OFFLINE_NONFINITE_OR_INCONSISTENT:" + asset)
        weekly_ranges[asset] = (round(low, 2), round(high, 2))
        drift = anchor / opened - 1
        moves[asset] = drift
        scale = min(.017, max(.005, abs(drift)/7))
        seq = DOWN_SEQ if drift < 0 else UP_SEQ
        reason = ("retest, tentative stabilization, renewed test, conditional late recovery"
                  if drift < 0 else
                  "continuation, possible pullback, support test, tentative recovery")
        total_width = high-low
        current = anchor
        closes, intervals = [], []
        for i, factor in enumerate(seq, 1):
            current = max(low + .10*total_width,
                          min(high - .10*total_width, current*(1+scale*factor)))
            half = total_width*(.13+.012*i)
            a, b = round(max(low, current-half),2), round(min(high, current+half),2)
            center = round(current,2)
            if not a < center < b:
                raise ValueError("CN_OFFLINE_DAILY_BOUNDS_INVALID")
            closes.append(dict(day=i,expected_close=center,low=a,high=b))
            intervals.append(dict(day=i,low=a,high=b,
              why="Day %d: %s. Conditional source-week volatility scenario, not a known future outcome." % (i,reason),
              invalidate_if="Source-qualified price breaks the frozen weekly envelope or the conditional sequence fails."))
        assets[asset] = dict(close=closes, range=intervals)
    bearish = moves["BTC"] < 0 or moves["ETH"] < 0
    bias = "LEAN_BEARISH" if bearish else "LEAN_BULLISH"
    week_text = ("Previous BTC/ETH week declined. Conditional early retest, midweek stabilization and possible late recovery."
                 if bearish else
                 "Previous BTC/ETH week rose. Conditional early extension, midweek support test and possible late recovery.")
    week_text += " Prices are pre-outcome deterministic hypotheses with uncalibrated uncertainty, not API model predictions."
    medium = "No verified 2–3-week numeric price path or confirmed broad altcoin rotation; no timing guarantee."
    long = "4–8-week price sequence and established market cycle phase remain UNAVAILABLE."
    freeze = deepcopy(previous["forecast_freeze"])
    freeze.update({
        "btc_range_low": weekly_ranges["BTC"][0],
        "btc_range_high": weekly_ranges["BTC"][1],
        "eth_range_low": weekly_ranges["ETH"][0],
        "eth_range_high": weekly_ranges["ETH"][1],
        "price_quote": {"BTC":"USDT","ETH":"USDT"},
        "forecast_horizon_days":7,
        "daily_price_path": {"contract":"CN_FROZEN_DAILY_PRICE_PATH_v1","forecast_week":week_id,
            **{a:dict(status="PUBLISHED",reason="API-free owner-authorized uncertain scenario; independently verified source gate still required.",points=assets[a]["close"]) for a in assets}},
        "daily_range_plan":{"contract":"CN_FROZEN_DAILY_RANGE_PLAN_v1","forecast_week":week_id,
            **{a:dict(status="PUBLISHED",reason="Day-specific source-week volatility hypothesis.",points=assets[a]["range"]) for a in assets}},
        "ethbtc_condition":"Durable ETH-relative leadership remains unverified; no forced ETH/BTC daily target.",
        "breadth_condition":"Persistent broad altcoin participation not verified by source-week BTC/ETH alone.",
        "structural_calls":[
            "REGIME_RESILIENCE: test whether source-week pressure stabilizes.",
            "LEADERSHIP: require independently observed ETH-relative strength.",
            "ROTATION_TRANSMISSION: do not infer microcap handoffs.",
            "BREADTH_PERSISTENCE: broad altseason remains unconfirmed.",
            "FLOW_QUALITY_FRAGILITY: retained venue spot flow is not market-wide flow."],
    })
    windows = {"day_1_2":(0,2),"day_3_4":(2,4),"day_5_7":(4,7)}
    freeze["intraday_map"] = {}
    for window,(first,stop) in windows.items():
        phrases=[]
        for asset in ("BTC","ETH"):
            daily=assets[asset]["close"][first:stop]
            lo=min(x["low"] for x in daily);hi=max(x["high"] for x in daily)
            phrases.append("%s $%.2f–$%.2f" % (asset,lo,hi))
        freeze["intraday_map"][window]="; ".join(phrases)+". Original daily scenario envelope aggregation, never reverse interpolation."
    dims = [
        "Previous-week price weakness admits another retest, not a guaranteed breakdown.",
        "ETH/BTC leadership is not established by source OHLC alone.",
        "Large, mid and microcap transmission require different independently admitted data.",
        "No verified durable broad participation in this deterministic issue.",
        "Hourly venue taker data are not proof of global buying or distribution.",
    ]
    freeze["market_structure_analysis"]={
        "contract":"CN_PUBLIC_MARKET_STRUCTURE_ANALYSIS_v1","status":"FROZEN_WEEK_AHEAD_ANALYSIS",
        "public_issue_number":public_issue,"forecast_week":week_id,"scoring_authority":False,
        "dimensions":[{"id":k,"label":k.replace("_"," ").title(),"analysis":txt} for k,txt in zip(DIM_IDS,dims)],
        "invariants":["Analysis only, no market structure accuracy claim.","No portfolio action."]}
    freeze["bull_bear_scale"]={
        "contract":"CN_PUBLIC_BULL_BEAR_SCALE_v1","public_issue_number":public_issue,
        "forecast_week":week_id,"semantics":"EVIDENCE_BALANCE_NOT_PROBABILITY",
        "horizons":{h:{"bull":3 if bearish else 6,"bear":7 if bearish else 4,
                       "bias":bias,"summary":week_text if h!="2_3w" else medium}
                    for h in ("1_3d","5_7d","2_3w")},
        "invariants":["Evidence balance not probability.","No independent economic edge."]}
    # Independent actual W45 containment scoring, no false structural grading.
    prior=previous["forecast_freeze"]
    expected=[]
    for k in ("btc_range","eth_range"):
        if prior.get(k+"_low") is not None and prior.get(k+"_high") is not None: expected.append(k)
    if prior.get("ethbtc_condition"): expected.append("ethbtc_condition")
    if prior.get("breadth_condition"): expected.append("breadth_condition")
    expected += ["structural_call_"+str(i) for i,s in enumerate(prior.get("structural_calls") or [],1) if s]
    expected += ["intraday_"+w for w in windows if str((prior.get("intraday_map") or {}).get(w) or "").strip().upper() != "UNAVAILABLE"]
    scored={}
    for k in ("btc_range","eth_range"):
        actual=source["hourly_sequence"][k[:3]]["week_range"]
        lo,hi=prior.get(k+"_low"),prior.get(k+"_high")
        if lo is not None and hi is not None:
            yes=float(lo)<=float(actual["low"]) and float(actual["high"])<=float(hi)
            scored[k]=(yes,"%s actual %.2f–%.2f; prior freeze %.2f–%.2f"%(k,actual["low"],actual["high"],lo,hi))
    rows=[]
    for k in expected:
        t=scored.get(k)
        rows.append(dict(parameter_id=k,status=("SUPPORTED" if t[0] else "CONTRADICTED") if t else "NOT_EVALUABLE",
            score=(100 if t[0] else 0) if t else None,
            evidence=t[1] if t else "Not independently evaluated, no invented scoring."))
    count=sum(x["score"] is not None for x in rows)
    eval_={"score_status":"REPRODUCIBLE",
           "public_continuity_score":sum(x["score"] for x in rows if x["score"] is not None)/count if count else None,
           "price_range_score":100*sum(t[0] for t in scored.values())/len(scored) if scored else None,
           "structural_score":None,"decision_utility_score":None,"parameter_scores":rows,
           "parameter_coverage_pct":round(100*count/len(rows),6) if rows else 0,
           "strengths":["Prior weekly BTC/ETH ranges scored against completed 168h source."],
           "misses":["Unadmitted structure and intraday analysis remain NOT_EVALUABLE rather than fabricated."],
           "method_note":"REPRODUCIBLE partial-range-only completed-week test; excludes non-evaluable parameters, with explicitly limited coverage."}
    decision=deepcopy(previous["decision_projection"])
    decision["next_1_3d"]={"direction":"DOWN" if bearish else "UP","summary":week_text}
    decision["next_5_7d"]={"direction":"MIXED","summary":"Conditional late-week recovery or failure of the retest; no guaranteed turning day."}
    decision["next_2_3w"]={"direction":"NO_EDGE","summary":medium}
    month=decision["next_21_30d"]
    month.update({"direction":"NO_EDGE","btc_direction":"NO_EDGE","eth_direction":"NO_EDGE",
                  "ethbtc_direction":"NO_EDGE","regime_destination":"NO_EDGE","confidence":"UNKNOWN",
                  "action_posture":"WAIT","summary":"No source-qualified month-ahead numeric price forecast.",
                  "expected_path":"Wait for source-qualified breadth and ETH/BTC confirmation.",
                  "falsification":["Independent durable broad expansion.","Independent persistent contraction."]})
    month["scenarios"]=[{"label":k,"weight_pct":w,"thesis":t} for k,w,t in
       [("BASE",50,"No proven edge."),("BULL",25,"Broad recovery confirms."),("BEAR",25,"Contraction persists.")]]
    decision["weeks_4_8"].update({"direction":"UNAVAILABLE","state":"UNCLEAR","warning":"NONE",
                                  "action_posture":"UNAVAILABLE","summary":long,
                                  "through_date":None,"horizon_days":None,"confidence":"UNKNOWN",
                                  "eta":"No supported transition window."})
    decision["protection"].update({"drivers":["Completed-week source price moves and bounded original weekly ranges."],
                                    "eta_window":"UNAVAILABLE","confidence_quality":"LOW",
                                    "invalidation":"Source-bound recovery and durable improved breadth weaken downside concern."})
    lines=["# Cycle Navigator "+week_id,"","Method: "+METHOD,
           "ISSUED after completed source week. Original UTC issue/freeze clock is recorded by the publisher.",
           "Not backdated, not an AI answer, not a known outcome or calibrated investment edge.",
           "",week_text,"",
           "| UTC day | BTC expected close | BTC low/high | ETH expected close | ETH low/high | Sequence |",
           "|---|---:|---:|---:|---:|---|"]
    for i in range(7):
        stamp=date.fromordinal(date.fromisocalendar(year,week,1).toordinal()+i).isoformat()
        b=assets["BTC"]["close"][i];e=assets["ETH"]["close"][i]
        direction="UP" if i and b["expected_close"]>assets["BTC"]["close"][i-1]["expected_close"] else "DOWN/RETEST"
        lines.append("| %s | %.2f | %.2f–%.2f | %.2f | %.2f–%.2f | %s |"%
                    (stamp,b["expected_close"],b["low"],b["high"],e["expected_close"],e["low"],e["high"],direction))
    lines += ["","All price units USDT, independent quote integrity must pass before public daily admission.",
              "Daily uncertainty bands and expected close are separate original day-level hypotheses.",
              "## Day-window summary"] + [k+": "+v for k,v in freeze["intraday_map"].items()]
    lines += ["","## 2–3 weeks",medium,"","## 4–8 weeks",long]
    return {
        "status":"DEGRADED","status_reason_codes":["CONTINUITY_FALLBACK","COVERAGE_LIMITATION"],
        "issue_number":issue,"previous_issue_number":int(previous["issue_number"]),
        "market_state":"MIXED_WITH_DOWNSIDE_PRESSURE" if bearish else "MIXED_WITH_UPSIDE_BIAS",
        "evaluation":eval_,
        "base_case_this_week":week_text,"base_case_2_3_weeks":medium,"base_case_4_8_weeks":long,
        "altseason_countdown":[{"phase":p,"window":w} for p,w in [
            ("Source-issued daily BTC/ETH scenario, altseason not confirmed",week_id),
            ("ETH relative leadership requires independent confirmation","2-3 weeks conditional"),
            ("Large and midcap rotation unverified","No valid ETA"),
            ("Microcap rotation unverified","No valid ETA")]],
        "rotation_ladder":[{"segment":k,"status":"UNCONFIRMED"} for k in ("BTC","ETH","LARGE","MID","MICRO")],
        "market_cycle_context":{"current_phase":"UNAVAILABLE",
              "why":"Original price source does not independently establish cycle phase.",
              "next_gate":"Confirm persistent relative strength and broad participation."},
        "forecast_freeze":freeze,"decision_projection":decision,
        "readable_markdown":"\n".join(lines),"x_ready_markdown":"\n".join(lines),
        "uncertainties":["Daily forecasts generated without API; deterministic source-based uncalibrated hypotheses.",
                         "Raw Binance quote attestation and source/PIT admission gates still apply.",
                         "Only selected previous-range rows scored, no invented structural outcomes.",
                         "No automated trading or false market-cycle authority."],
        "public_translations":[
          {"en":week_text,"da":"Afsluttet kildeuge angiver en betinget kurssekvens med risiko for test og mulig rekyl. Ikke en AI-beregnet eller kalibreret prognose."},
          {"en":medium,"da":"Ingen verificeret 2–3-ugers prissti eller bekræftet bred altcoin-rotation."},
          {"en":long,"da":"4–8-ugers prissti og markedsfase er ikke tilgængelige."}]
    }
