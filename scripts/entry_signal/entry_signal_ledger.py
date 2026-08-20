#!/usr/bin/env python3
import csv, json, statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("04_MARKET_LEARNING/entry_signals")
EVENTS = ROOT / "events"
OUTCOMES = ROOT / "outcomes"
STATE = ROOT / "STATE.json"
LATEST = ROOT / "LATEST.json"
SUMMARY = ROOT / "PERFORMANCE_SUMMARY.json"
HOURLY_POINTER = Path("03_DAILY_CAPTURE_LOGS/hourly/LATEST.json")
HORIZONS_H = {"24h": 24, "72h": 72, "7d": 168, "14d": 336, "30d": 720}


def now_utc():
    return datetime.now(timezone.utc)


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def hourly_latest_row():
    pointer = read_json(HOURLY_POINTER)
    if not pointer or pointer.get("status") != "COMPLETE":
        raise RuntimeError("hourly sequence pointer missing/incomplete")
    end = parse_utc(pointer["window_end_utc"])
    csv_path = Path(f"03_DAILY_CAPTURE_LOGS/hourly/{end:%Y/%m/%Y-%m-%d}.csv")
    if not csv_path.exists():
        raise RuntimeError(f"hourly permanent CSV missing: {csv_path}")
    rows = []
    with csv_path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("spot_status") != "PASS":
                continue
            ts = parse_utc(row["timestamp_utc"])
            if ts <= end:
                rows.append((ts, row))
    if not rows:
        raise RuntimeError("no complete hourly row available")
    ts, row = max(rows, key=lambda x: x[0])
    required = ("btc_close", "eth_close", "ethbtc_close")
    if any(not row.get(k) for k in required):
        raise RuntimeError("latest hourly row missing direct spot close")
    return pointer, ts, row


def latest_market():
    breadth_obj = read_json("03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
    if not breadth_obj:
        raise RuntimeError("breadth_rich LATEST missing/unreadable")
    agg = breadth_obj.get("aggregate", breadth_obj)
    breadth = agg.get("advance_ratio")
    if breadth is None and agg.get("advancer_pct") is not None:
        breadth = float(agg["advancer_pct"]) / 100.0
    if breadth is None:
        raise RuntimeError("breadth ratio unavailable")
    pointer, hourly_ts, row = hourly_latest_row()
    return {
        "captured_at_utc": now_utc().isoformat(),
        "price_observation_utc": hourly_ts.isoformat(),
        "hourly_sequence_run_id": pointer.get("run_id"),
        "price_source": "GITHUB_HOURLY_SEQUENCE_DIRECT_CLOSES",
        "btc_usdt": float(row["btc_close"]),
        "eth_usdt": float(row["eth_close"]),
        "ethbtc": float(row["ethbtc_close"]),
        "top100_advance_ratio": float(breadth),
        "top100_advancer_pct": agg.get("advancer_pct"),
        "btc_return_24h_pct": agg.get("btc_return_24h_pct"),
        "eth_return_24h_pct": agg.get("eth_return_24h_pct"),
        "equal_weight_mean_return_24h_pct": agg.get("equal_weight_mean_return_24h_pct"),
        "median_return_24h_pct": agg.get("median_return_24h_pct"),
        "breadth_membership_hash": agg.get("membership_hash"),
        "constituents": {
            str(x.get("asset_id")): float(x["price_usd"])
            for x in breadth_obj.get("constituents", [])
            if x.get("asset_id") and x.get("price_usd") not in (None, 0)
        },
    }


def classify(m):
    br = m.get("btc_return_24h_pct")
    er = m.get("eth_return_24h_pct")
    checks = {
        "ethbtc_above_registered_0_0300": m["ethbtc"] > 0.03,
        "top100_proxy_breadth_ge_50pct": m["top100_advance_ratio"] >= 0.50,
        "eth_outperforms_btc_24h": er is not None and br is not None and er > br,
    }
    active = all(checks.values())
    heat = "HOT" if ((er or 0) >= 12 or (br or 0) >= 8 or (m.get("median_return_24h_pct") or 0) >= 4) else "NORMAL"
    return ("GRADUATED_ALTCOIN_TOPUP_ACTIVE" if active else "WAIT"), checks, heat


def event_id(ts, state):
    return ts.strftime("%Y%m%dT%H%M%SZ") + "_" + state.lower()


def matching_return(baseline, current):
    b = baseline.get("constituents", {})
    c = current.get("constituents", {})
    vals = []
    for k, p0 in b.items():
        p1 = c.get(k)
        if p0 and p1:
            vals.append((p1 / p0 - 1.0) * 100.0)
    return None if not vals else sum(vals) / len(vals)


def return_bundle(base, current):
    return {
        "btc_pct": (current["btc_usdt"] / base["btc_usdt"] - 1.0) * 100.0,
        "eth_pct": (current["eth_usdt"] / base["eth_usdt"] - 1.0) * 100.0,
        "ethbtc_pct": (current["ethbtc"] / base["ethbtc"] - 1.0) * 100.0,
        "matched_top100_equal_weight_pct": matching_return(base, current),
    }


def update_extreme(stats, key, value, now_iso, mode):
    if value is None:
        return
    cur = stats.get(key)
    if cur is None or (mode == "min" and value < cur["value_pct"]) or (mode == "max" and value > cur["value_pct"]):
        stats[key] = {"value_pct": value, "observed_at_utc": now_iso}


def update_outcomes(current, now):
    if not EVENTS.exists():
        return
    now_iso = now.isoformat()
    for f in EVENTS.glob("*.json"):
        ev = read_json(f)
        if not ev or ev.get("event_type") != "ACTIVATION":
            continue
        base = ev["market_snapshot"]
        t = parse_utc(ev["event_time_utc"])
        age = (now - t).total_seconds() / 3600.0
        op = OUTCOMES / (ev["event_id"] + ".json")
        out = read_json(op) or {
            "contract": "ENTRY_SIGNAL_OUTCOME_v1",
            "event_id": ev["event_id"],
            "event_time_utc": ev["event_time_utc"],
            "horizons": {},
            "path_stats": {},
        }
        rb = return_bundle(base, current)
        ps = out.setdefault("path_stats", {})
        for name, value in rb.items():
            update_extreme(ps, f"{name}_mae", value, now_iso, "min")
            update_extreme(ps, f"{name}_mfe", value, now_iso, "max")
        ps["last_observed_at_utc"] = now_iso
        ps["last_age_hours"] = round(age, 3)
        ps["latest_returns"] = rb
        ps["latest_top100_advance_ratio"] = current.get("top100_advance_ratio")
        ps["price_observation_utc"] = current.get("price_observation_utc")
        for label, h in HORIZONS_H.items():
            if age < h or label in out["horizons"]:
                continue
            out["horizons"][label] = {
                "matured_at_utc": now_iso,
                "age_hours": round(age, 3),
                "price_observation_utc": current.get("price_observation_utc"),
                "btc_return_since_signal_pct": rb["btc_pct"],
                "eth_return_since_signal_pct": rb["eth_pct"],
                "ethbtc_return_since_signal_pct": rb["ethbtc_pct"],
                "matched_top100_equal_weight_return_since_signal_pct": rb["matched_top100_equal_weight_pct"],
                "current_top100_advance_ratio": current.get("top100_advance_ratio"),
                "descriptive_positive_outcome": None if rb["matched_top100_equal_weight_pct"] is None else rb["matched_top100_equal_weight_pct"] > 0,
            }
        write_json(op, out)


def build_summary(now):
    by_horizon = {}
    activation_events = 0
    if EVENTS.exists():
        activation_events = sum(1 for f in EVENTS.glob("*.json") if (read_json(f) or {}).get("event_type") == "ACTIVATION")
    for label in HORIZONS_H:
        vals, btc_vals, eth_vals = [], [], []
        matured = 0
        if OUTCOMES.exists():
            for f in OUTCOMES.glob("*.json"):
                h = ((read_json(f) or {}).get("horizons") or {}).get(label)
                if not h:
                    continue
                matured += 1
                btc_vals.append(h["btc_return_since_signal_pct"])
                eth_vals.append(h["eth_return_since_signal_pct"])
                v = h.get("matched_top100_equal_weight_return_since_signal_pct")
                if v is not None:
                    vals.append(v)
        by_horizon[label] = {
            "matured_event_count": matured,
            "matched_top100_available_count": len(vals),
            "matched_top100_positive_rate_pct": None if not vals else 100.0 * sum(v > 0 for v in vals) / len(vals),
            "matched_top100_mean_return_pct": None if not vals else statistics.fmean(vals),
            "matched_top100_median_return_pct": None if not vals else statistics.median(vals),
            "btc_mean_return_pct": None if not btc_vals else statistics.fmean(btc_vals),
            "eth_mean_return_pct": None if not eth_vals else statistics.fmean(eth_vals),
        }
    write_json(SUMMARY, {
        "contract": "ENTRY_SIGNAL_PERFORMANCE_SUMMARY_v1",
        "generated_at_utc": now.isoformat(),
        "activation_event_count": activation_events,
        "evaluation_note": "Positive-rate is descriptive forward evidence, not a trading rule or optimized hit threshold.",
        "horizons": by_horizon,
    })


def main():
    now = now_utc()
    current = latest_market()
    state, checks, heat = classify(current)
    prev = read_json(STATE) or {}
    previous = prev.get("state")
    latest = {
        "contract": "ENTRY_SIGNAL_LATEST_v1",
        "generated_at_utc": now.isoformat(),
        "state": state,
        "previous_state": previous,
        "execution_temperature": heat,
        "criteria": checks,
        "market_snapshot": {k: v for k, v in current.items() if k != "constituents"},
        "authority": {
            "canonical_market_state": False,
            "portfolio_execution": False,
            "market_rule_change": False,
            "purpose": "timestamped decision-observation and forward outcome learning",
        },
        "data_ping_bridge": {
            "display_line": f"ENTRY/TOP-UP: {state} | heat={heat} | ETHBTC={current['ethbtc']:.5f} | breadth={current['top100_advance_ratio']*100:.0f}%"
        },
    }
    write_json(LATEST, latest)
    if previous is None or previous != state:
        etype = "ACTIVATION" if state == "GRADUATED_ALTCOIN_TOPUP_ACTIVE" else ("DEACTIVATION" if previous == "GRADUATED_ALTCOIN_TOPUP_ACTIVE" else "INITIAL_STATE")
        eid = event_id(now, state)
        write_json(EVENTS / (eid + ".json"), {
            "contract": "ENTRY_SIGNAL_EVENT_v1",
            "event_id": eid,
            "event_type": etype,
            "event_time_utc": now.isoformat(),
            "state": state,
            "previous_state": previous,
            "execution_temperature": heat,
            "criteria": checks,
            "market_snapshot": current,
            "authority": {"canonical_market_state": False, "portfolio_execution": False, "retrospective_rule_change": False},
        })
    write_json(STATE, {
        "contract": "ENTRY_SIGNAL_STATE_v1",
        "updated_at_utc": now.isoformat(),
        "state": state,
        "execution_temperature": heat,
        "criteria": checks,
    })
    update_outcomes(current, now)
    build_summary(now)
    print(json.dumps(latest, sort_keys=True))


if __name__ == "__main__":
    main()
