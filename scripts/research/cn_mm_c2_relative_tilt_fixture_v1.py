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
