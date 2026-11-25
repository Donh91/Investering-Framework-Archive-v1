"""C2 relative tilt candidate: synthetic fixture math ONLY, no issuance interface.

Not a live or historical forecast generator. Activation, independently attested
known-by, first delivery, and reviewed scoring contracts remain separate gates.
"""
from __future__ import annotations
import math
from scripts.research import task2_challenger_a_sqrt_t_vol_band_v1 as A

CONTRACT = "CN_MM_C2_RELATIVE_TILT_FIXTURE_v1"
COEFFICIENT = 0.5
MAX_HOURS = 168
AUTHORITY = {"research_only":True,"fixture_only":True,"forecast_authority":False,
             "canonical_effect":False,"portfolio_execution":False,"promotion":False}

def positive(value):
    if type(value) not in (int,float) or not math.isfinite(value) or value<=0:
        raise ValueError("C2_INVALID_POSITIVE_NUMBER")
    return float(value)

def fixture_projection(issuance, permission):
    """Symmetric ETH/BTC log tilt; same A log band widths, no new calibration.

    True: relative log drift = 0.5 * min(hourly sigmas) * sqrt(24) * h/24.
    Each asset gets half that drift with opposite signs. False: exact no-drift
    baseline. None: abstain; never translate unknown into bearish or neutral.
    All input A data MUST be explicitly synthetic, even if digest is valid.
    """
    A.verify_issuance_digest(issuance)
    if issuance.get("source") != {"clock_class":"FIXTURE_NOT_MAIN_ATTESTED"}:
        raise ValueError("C2_REAL_ISSUANCE_FORBIDDEN_UNTIL_REVIEWED_ACTIVATION")
    if permission is not None and type(permission) is not bool:
        raise ValueError("C2_PERMISSION_INVALID")
    if set(issuance["assets"])!={"BTC","ETH"}:
        raise ValueError("C2_ASSET_SET_INVALID")
    assets=issuance["assets"]
    sigma=min(positive(a["sigma_hourly"]) for a in assets.values())
    windows={}
    for asset,a in assets.items():
        positive(a["P0"])
        seen=set()
        ds=[]
        for d in a["days"]:
            day=d["day"]
            h=positive(d["h"])
            start,end=A.utc(d["scored_from_utc"]),A.utc(d["end_utc"])
            if type(day) is not int or not 1<=day<=7 or day in seen or h>MAX_HOURS or start>=end:
                raise ValueError("C2_DAY_WINDOW_INVALID")
            seen.add(day)
            ds.append((day,start,end,h))
        if not ds or ds!=sorted(ds) or any(x[2]>y[1] for x,y in zip(ds,ds[1:])):
            raise ValueError("C2_DAY_WINDOW_ORDER_INVALID")
        windows[asset]=ds
    if windows["BTC"]!=windows["ETH"]:
        raise ValueError("C2_MATCHED_WINDOWS_REQUIRED")
    out={"contract":CONTRACT,"authority":dict(AUTHORITY),"status":"ABSTAIN_SOURCE_UNAVAILABLE" if permission is None else "SYNTHETIC_FIXTURE_ONLY",
         "a_issuance_sha256":issuance["issuance_sha256"],"permission":permission,
         "scientific_pit_eligible":False,"coefficient":COEFFICIENT,
         "interval_coverage_recalibrated":False,"assets":{}}
    if permission is None:
        return out
    for asset,a in assets.items():
        sign=1 if asset=="ETH" else -1
        rows=[]
        for d in a["days"]:
            h=float(d["h"])
            drift=COEFFICIENT*sigma*math.sqrt(24)*h/24 if permission else 0.0
            factor=math.exp(sign*drift/2)
            centre=positive(float(a["P0"])*factor)
            bands={}
            for family in ("close","range"):
                levels=d["band"][family]
                if set(levels)!={"0.5","0.8","0.95"}:
                    raise ValueError("C2_QUANTILE_SET_INVALID")
                bands[family]={}
                previous=None
                for q in ("0.5","0.8","0.95"):
                    lo,hi=map(positive,levels[q])
                    if lo>hi or (previous and not lo<=previous[0]<=previous[1]<=hi):
                        raise ValueError("C2_BAND_INVALID")
                    bands[family][q]=[positive(lo*factor),positive(hi*factor)]
                    previous=(lo,hi)
            rows.append({"day":d["day"],"scored_from_utc":d["scored_from_utc"],"end_utc":d["end_utc"],
                         "h":d["h"],"centre":centre,"log_shift":sign*drift/2,"bands":bands})
        out["assets"][asset]={"P0":a["P0"],"days":rows}
    return out

def fixture_evaluation(issuance, permission, bars, *, first_delivery_utc, evaluated_at_utc):
    """Exercise the matched future evaluation design on synthetic fixtures only.

    Recompute C2 from the exact A issuance, not caller-supplied predictions.
    Both spot assets must share the same eligible days and continuous outcome
    bars. Availability must precede the whole scored window. No retrospective
    evidence admission, independent edge test, portfolio return or promotion.
    """
    projection=fixture_projection(issuance,permission)
    delivery,evaluated=A.utc(first_delivery_utc),A.utc(evaluated_at_utc)
    issue=A.utc(issuance["issue_clock_utc"])
    if not issue<=delivery<=evaluated:
        raise ValueError("C2_EVALUATION_CLOCK_ORDER_INVALID")
    if not isinstance(bars,dict):
        raise ValueError("C2_FIXTURE_BARS_INVALID")
    # Validate the originally registered A windows using its owner, including
    # partial issue days. h is rounded in the original issuance contract.
    year,week=map(int,issuance["week"].split("-W"))
    monday=A.week_monday(year,week)
    if not monday<=issue<monday+7*A.DAY:
        raise ValueError("C2_FIXTURE_WEEK_INVALID")
    expected=[(k,start,end,round(h,4)) for k,start,end,h in A.day_windows(monday,issue)]
    for asset in ("BTC","ETH"):
        actual=[(d["day"],A.utc(d["scored_from_utc"]),A.utc(d["end_utc"]),d["h"])
                for d in issuance["assets"][asset]["days"]]
        if actual!=expected:
            raise ValueError("C2_FIXTURE_WINDOWS_DO_NOT_MATCH_A_OWNER")
    rows=[];relative=[];abstentions=[]
    def direction(pred,anchor):
        return "UP" if pred>anchor else "DOWN" if pred<anchor else "FLAT"
    def valid_ohlc(asset,start,end):
        # Use original owner realization only after screening its entire
        # required hourly path for nonfinite, invalid or inconsistent bars.
        n=int((end-start).total_seconds()/3600)
        for i in range(n):
            row=bars.get(start+i*A.HOUR)
            if not isinstance(row,dict) or asset not in row:
                return None
            v=row[asset]
            if not isinstance(v,(tuple,list)) or len(v)!=3:
                raise ValueError("C2_FIXTURE_OHLC_SHAPE_INVALID")
            close,high,low=map(positive,v)
            if not low<=close<=high:
                raise ValueError("C2_FIXTURE_OHLC_ORDER_INVALID")
        return A.realized(bars,asset,start,end)
    q=str(A.PARAMS["primary_quantile"]);alpha=A.PARAMS["alpha_primary"]
    for day,start,end,h in expected:
        reason=None
        if permission is None:
            reason="ABSTAIN_SOURCE_UNAVAILABLE"
        elif start<delivery:
            reason="ABSTAIN_PRE_DELIVERY"
        elif end>evaluated:
            reason="ABSTAIN_NOT_MATURE"
        if reason:
            abstentions.append({"day":day,"reason":reason})
            continue
        realized={a:valid_ohlc(a,start,end) for a in ("BTC","ETH")}
        if any(v is None for v in realized.values()):
            abstentions.append({"day":day,"reason":"ABSTAIN_INCOMPLETE_MATCHED_HOURLY"})
            continue
        preds={}
        for asset in ("BTC","ETH"):
            a=issuance["assets"][asset]
            p0=positive(a["P0"]);r=realized[asset]
            c1=next(d for d in a["days"] if d["day"]==day)
            c2=next(d for d in projection["assets"][asset]["days"] if d["day"]==day)
            preds[asset]=(p0,c2["centre"],r["close"])
            row={"asset":asset,"day":day,"bars":r["bars"]}
            for model,center,bands in (("C1",p0,c1["band"]),("C2",c2["centre"],c2["bands"])):
                lo,hi=bands["close"][q];rl,rh=bands["range"][q]
                row.update({model+"_abs_error_fraction":abs(center-r["close"])/p0,
                            model+"_direction_correct":int(direction(center,p0)==direction(r["close"],p0)),
                            model+"_close_covered":int(lo<=r["close"]<=hi),
                            model+"_range_covered":int(rl<=r["low"]<=r["high"]<=rh),
                            model+"_interval_score":A.interval_score(lo,hi,r["close"],alpha)/p0,
                            model+"_width":(hi-lo)/p0})
            rows.append(row)
        b,e=preds["BTC"],preds["ETH"]
        # Relative return uses the same paired spot closes, not a separately
        # timestamped ETHBTC series. Normalize by the frozen implied ratio.
        base=e[0]/b[0];pred=e[1]/b[1];actual=e[2]/b[2]
        relative.append({"day":day,"C1_abs_error_fraction":abs(base-actual)/base,
                         "C2_abs_error_fraction":abs(pred-actual)/base,
                         "C1_direction_correct":int(direction(base,base)==direction(actual,base)),
                         "C2_direction_correct":int(direction(pred,base)==direction(actual,base))})
    def aggregate(items):
        fields=("abs_error_fraction","direction_correct","close_covered","range_covered","interval_score","width")
        return {"n":len(items),"metrics":{k:sum(r[k] for r in items)/len(items)
                for k in (m+"_"+f for m in ("C1","C2") for f in fields) if items and all(k in r for r in items)}}
    return {"contract":"CN_MM_C2_MATCHED_EVALUATION_FIXTURE_v1","authority":dict(AUTHORITY),
            "status":"SYNTHETIC_MATCHED_ONLY" if rows else "ABSTAIN_NO_MATCHED_DAYS",
            "a_issuance_sha256":issuance["issuance_sha256"],"permission":permission,
            "paired_day_count":len(relative),"paired_asset_day_count":len(rows),
            "abstentions":abstentions,"rows":rows,"relative_rows":relative,
            "all":aggregate(rows),"by_asset":{a:aggregate([r for r in rows if r["asset"]==a]) for a in ("BTC","ETH")},
            "relative":aggregate(relative),"independent_sample_size":None,"edge_established":False,
            "scientific_pit_eligible":False,"first_delivery_verified":False}
