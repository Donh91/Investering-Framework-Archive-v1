#!/usr/bin/env python3
import json, os, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("04_MARKET_LEARNING/entry_signals")
EVENTS = ROOT / "events"
OUTCOMES = ROOT / "outcomes"
STATE = ROOT / "STATE.json"
LATEST = ROOT / "LATEST.json"
HORIZONS_H = {"24h":24, "72h":72, "7d":168, "14d":336, "30d":720}


def now_utc():
    return datetime.now(timezone.utc)


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def write_json(path, obj):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent":"framework-entry-ledger/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def latest_market():
    breadth_obj = read_json("03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
    if not breadth_obj:
        raise RuntimeError("breadth_rich LATEST missing/unreadable")
    agg = breadth_obj.get("aggregate", breadth_obj)
    breadth = agg.get("advance_ratio")
    if breadth is None and agg.get("advancer_pct") is not None:
        breadth = float(agg["advancer_pct"]) / 100.0
    ethbtc = float(http_json("https://api.binance.com/api/v3/ticker/price?symbol=ETHBTC")["price"])
    btc = float(http_json("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")["price"])
    eth = float(http_json("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")["price"])
    return {
        "captured_at_utc": now_utc().isoformat(),
        "btc_usdt": btc,
        "eth_usdt": eth,
        "ethbtc": ethbtc,
        "top100_advance_ratio": None if breadth is None else float(breadth),
        "top100_advancer_pct": agg.get("advancer_pct"),
        "btc_return_24h_pct": agg.get("btc_return_24h_pct"),
        "eth_return_24h_pct": agg.get("eth_return_24h_pct"),
        "equal_weight_mean_return_24h_pct": agg.get("equal_weight_mean_return_24h_pct"),
        "median_return_24h_pct": agg.get("median_return_24h_pct"),
        "breadth_membership_hash": agg.get("membership_hash"),
        "constituents": {str(x.get("asset_id")): float(x["price_usd"]) for x in breadth_obj.get("constituents", []) if x.get("asset_id") and x.get("price_usd") not in (None,0)},
    }


def classify(m):
    b = m.get("top100_advance_ratio")
    br = m.get("btc_return_24h_pct")
    er = m.get("eth_return_24h_pct")
    checks = {
        "ethbtc_above_registered_0_0300": m["ethbtc"] > 0.03,
        "top100_proxy_breadth_ge_50pct": b is not None and b >= 0.50,
        "eth_outperforms_btc_24h": er is not None and br is not None and er > br,
    }
    active = all(checks.values())
    # Execution heat is descriptive only and cannot activate/deactivate the signal.
    heat = "HOT" if ((er or 0) >= 12 or (br or 0) >= 8 or (m.get("median_return_24h_pct") or 0) >= 4) else "NORMAL"
    return ("GRADUATED_ALTCOIN_TOPUP_ACTIVE" if active else "WAIT"), checks, heat


def event_id(ts, state):
    return ts.strftime("%Y%m%dT%H%M%SZ") + "_" + state.lower()


def matching_return(baseline, current):
    b = baseline.get("constituents", {}); c = current.get("constituents", {})
    vals=[]
    for k,p0 in b.items():
        p1=c.get(k)
        if p0 and p1:
            vals.append((p1/p0-1.0)*100.0)
    return None if not vals else sum(vals)/len(vals)


def update_outcomes(current, now):
    if not EVENTS.exists(): return
    for f in EVENTS.glob("*.json"):
        ev=read_json(f)
        if not ev or ev.get("event_type")!="ACTIVATION": continue
        t=datetime.fromisoformat(ev["event_time_utc"].replace("Z","+00:00"))
        age=(now-t).total_seconds()/3600
        op=OUTCOMES/(ev["event_id"]+".json")
        out=read_json(op) or {"contract":"ENTRY_SIGNAL_OUTCOME_v1","event_id":ev["event_id"],"event_time_utc":ev["event_time_utc"],"horizons":{}}
        changed=False
        for label,h in HORIZONS_H.items():
            if age < h or label in out["horizons"]: continue
            base=ev["market_snapshot"]
            out["horizons"][label]={
                "matured_at_utc":now.isoformat(),
                "age_hours":round(age,3),
                "btc_return_since_signal_pct":(current["btc_usdt"]/base["btc_usdt"]-1)*100,
                "eth_return_since_signal_pct":(current["eth_usdt"]/base["eth_usdt"]-1)*100,
                "ethbtc_return_since_signal_pct":(current["ethbtc"]/base["ethbtc"]-1)*100,
                "matched_top100_equal_weight_return_since_signal_pct":matching_return(base,current),
                "current_top100_advance_ratio":current.get("top100_advance_ratio"),
            }
            changed=True
        if changed: write_json(op,out)


def main():
    now=now_utc(); current=latest_market(); state, checks, heat=classify(current)
    prev=read_json(STATE) or {}
    previous=prev.get("state")
    latest={
        "contract":"ENTRY_SIGNAL_LATEST_v1",
        "generated_at_utc":now.isoformat(),
        "state":state,
        "previous_state":previous,
        "execution_temperature":heat,
        "criteria":checks,
        "market_snapshot":{k:v for k,v in current.items() if k!="constituents"},
        "authority":{"canonical_market_state":False,"portfolio_execution":False,"market_rule_change":False,"purpose":"timestamped decision-observation and forward outcome learning"},
        "data_ping_bridge":{"display_line":f"ENTRY/TOP-UP: {state} | heat={heat} | ETHBTC={current['ethbtc']:.5f} | breadth={(current.get('top100_advance_ratio') or 0)*100:.0f}%"},
    }
    write_json(LATEST,latest)
    transition = previous is not None and previous != state
    # Bootstrap first run as an event so every deployed state has a timestamp.
    if previous is None or transition:
        etype="ACTIVATION" if state=="GRADUATED_ALTCOIN_TOPUP_ACTIVE" else ("DEACTIVATION" if previous=="GRADUATED_ALTCOIN_TOPUP_ACTIVE" else "INITIAL_STATE")
        eid=event_id(now,state)
        event={
            "contract":"ENTRY_SIGNAL_EVENT_v1","event_id":eid,"event_type":etype,
            "event_time_utc":now.isoformat(),"state":state,"previous_state":previous,
            "execution_temperature":heat,"criteria":checks,"market_snapshot":current,
            "authority":{"canonical_market_state":False,"portfolio_execution":False,"retrospective_rule_change":False},
        }
        write_json(EVENTS/(eid+".json"),event)
    write_json(STATE,{"contract":"ENTRY_SIGNAL_STATE_v1","updated_at_utc":now.isoformat(),"state":state,"execution_temperature":heat,"criteria":checks})
    update_outcomes(current,now)
    print(json.dumps(latest,sort_keys=True))

if __name__=="__main__":
    main()
