#!/usr/bin/env python3
import json, statistics, sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))
from daily_capture.hourly_sequence_consumer import read_latest_complete_spot_row

ROOT = Path("04_MARKET_LEARNING/entry_signals")
EVENTS = ROOT / "events"
OUTCOMES = ROOT / "outcomes"
STATE = ROOT / "STATE.json"
LATEST = ROOT / "LATEST.json"
SUMMARY = ROOT / "PERFORMANCE_SUMMARY.json"
HOURLY_POINTER = Path("03_DAILY_CAPTURE_LOGS/hourly/LATEST.json")
HOURLY_ROOT = Path("03_DAILY_CAPTURE_LOGS/hourly")
HORIZONS_H = {"24h": 24, "72h": 72, "7d": 168, "14d": 336, "30d": 720}
DEFINITION_VERSION = "ENTRY_SIGNAL_DEFINITION_v1_1_MEASUREMENT_VALIDITY_GUARD"
SENSOR_RELATIONSHIP_OWNER = "01_CORE_FRAMEWORK/governance/2026-07-22__sensor-relationship-and-incremental-value-standard__canonical.md"
HISTORICAL_VALIDITY_POLICY = (
    "Historical signal records remain immutable. Later outcomes may calibrate definition quality but must not "
    "retroactively invalidate a signal solely because the later outcome was poor. A contemporaneous evidence-role "
    "or measurement-validity defect may be annotated prospectively without rewriting the historical event."
)
ROLLING_WINDOW_POLICY = (
    "Repeated observations from an overlapping rolling window are descriptive persistence only and are not, by "
    "themselves, independent confirmation."
)


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
    return read_latest_complete_spot_row(HOURLY_POINTER, HOURLY_ROOT)


def measurement_validity_from_breadth(breadth_obj, agg=None):
    agg = agg or breadth_obj.get("aggregate", breadth_obj)
    semantics = breadth_obj.get("evidence_semantics") or {}
    observation = breadth_obj.get("observation") or {}
    count = agg.get("constituent_count")
    out_btc = agg.get("outperforming_btc_count")
    out_eth = agg.get("outperforming_eth_count")
    evidence_role = semantics.get("evidence_role", "UNKNOWN")
    canonical_compatible = semantics.get("canonical_compatible") is True
    proxy_only = evidence_role == "PROXY_ONLY"
    independent_eligible = canonical_compatible and not proxy_only

    def share(value):
        if value is None or count in (None, 0):
            return None
        return float(value) / float(count)

    return {
        "sensor_relationship_owner": SENSOR_RELATIONSHIP_OWNER,
        "evidence_role": evidence_role,
        "canonical_compatible": canonical_compatible,
        "canonical_large_cap_breadth": semantics.get("canonical_large_cap_breadth", "UNCONFIRMED"),
        "canonical_broad_alt_breadth": semantics.get("canonical_broad_alt_breadth", "UNCONFIRMED"),
        "absolute_breadth_semantics": (
            "DESCRIPTIVE_PARTICIPATION_ONLY" if proxy_only or not canonical_compatible else "OWNER_CONFIRMATION_ELIGIBLE"
        ),
        "independent_rotation_confirmation_eligible": independent_eligible,
        "independent_rotation_confirmation_reason": (
            "ELIGIBLE" if independent_eligible else "PROXY_OR_CANONICAL_COMPATIBILITY_UNCONFIRMED"
        ),
        "relative_breadth": {
            "constituent_count": count,
            "outperforming_btc_count": out_btc,
            "outperforming_btc_share": share(out_btc),
            "outperforming_eth_count": out_eth,
            "outperforming_eth_share": share(out_eth),
            "median_return_24h_pct": agg.get("median_return_24h_pct"),
            "equal_weight_mean_return_24h_pct": agg.get("equal_weight_mean_return_24h_pct"),
        },
        "window_semantics": observation.get("window_semantics", "UNKNOWN"),
        "rolling_window_confirmation_policy": ROLLING_WINDOW_POLICY,
        "capture_cadence_note": (
            "Capture-level correlation or survival analysis must account for adaptive/uneven cadence; repeated "
            "checkpoints are not assumed independent samples."
        ),
    }


def hourly_directional_context(pointer):
    run_path = pointer.get("run_path")
    if not run_path:
        return {"availability": "UNAVAILABLE", "reason": "POINTER_RUN_PATH_MISSING"}
    run = read_json(run_path)
    if not run:
        return {"availability": "UNAVAILABLE", "reason": "HOURLY_RUN_UNREADABLE", "run_path": run_path}
    summary = run.get("directional_summary") or {}
    counts = summary.get("registered_directional_counts") or {}

    def count_value(name):
        raw = counts.get(name) or {}
        return raw.get("value") if isinstance(raw, dict) else raw

    return {
        "availability": "AVAILABLE" if summary else "UNAVAILABLE",
        "source_run_id": pointer.get("run_id"),
        "source_run_path": run_path,
        "confirmation_level": ((summary.get("evidence_semantics") or {}).get("confirmation_level")),
        "eth_leads_btc_hours": count_value("eth_leads_btc"),
        "ethbtc_positive_hours": count_value("ethbtc_positive_hours"),
        "trailing_ethbtc_positive_run": count_value("trailing_ethbtc_positive_run"),
        "latest_relative_performance": summary.get("latest_relative_performance"),
        "registered_0_0300_role": "STRUCTURAL_FLOOR_CONTEXT_ONLY",
        "directional_interpretation": "OWNER_CONTEXT_ONLY_NOT_USED_AS_A_NEW_THRESHOLD_BY_THIS_LEDGER",
    }


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
    directional = hourly_directional_context(pointer)
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
        "outperforming_btc_count": agg.get("outperforming_btc_count"),
        "outperforming_eth_count": agg.get("outperforming_eth_count"),
        "breadth_membership_hash": agg.get("membership_hash"),
        "ethbtc_evidence_semantics": directional,
        "measurement_validity": measurement_validity_from_breadth(breadth_obj, agg),
        "constituents": {
            str(x.get("asset_id")): float(x["price_usd"])
            for x in breadth_obj.get("constituents", [])
            if x.get("asset_id") and x.get("price_usd") not in (None, 0)
        },
    }


def classify(m):
    br = m.get("btc_return_24h_pct")
    er = m.get("eth_return_24h_pct")
    legacy_checks = {
        "ethbtc_above_registered_0_0300": m["ethbtc"] > 0.03,
        "top100_proxy_breadth_ge_50pct": m["top100_advance_ratio"] >= 0.50,
        "eth_outperforms_btc_24h": er is not None and br is not None and er > br,
    }
    pattern_observed = all(legacy_checks.values())
    validity = m.get("measurement_validity") or {}
    breadth_authority_eligible = validity.get("independent_rotation_confirmation_eligible") is True
    active = pattern_observed and breadth_authority_eligible
    if active:
        observer_state = "AUTHORIZED_PATTERN_OBSERVED"
    elif pattern_observed:
        observer_state = "PROXY_PATTERN_OBSERVED_NOT_ACTION_ELIGIBLE"
    else:
        observer_state = "NO_PATTERN"
    heat = "HOT" if ((er or 0) >= 12 or (br or 0) >= 8 or (m.get("median_return_24h_pct") or 0) >= 4) else "NORMAL"
    state = "GRADUATED_ALTCOIN_TOPUP_ACTIVE" if active else "WAIT"
    return state, legacy_checks, heat, observer_state


def bridge_display_line(state, observer_state, heat, current):
    rel = ((current.get("measurement_validity") or {}).get("relative_breadth") or {}).get("outperforming_btc_share")
    rel_text = "UNKNOWN" if rel is None else f"{rel * 100:.0f}%"
    return (
        f"LEARNING OBSERVER: {observer_state} | canonical_action_authority=NONE | state={state} | "
        f"heat={heat} | ETHBTC={current['ethbtc']:.5f} | abs_breadth={current['top100_advance_ratio']*100:.0f}% | "
        f"outperforming_BTC={rel_text}"
    )


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
    btc = (current["btc_usdt"] / base["btc_usdt"] - 1.0) * 100.0
    eth = (current["eth_usdt"] / base["eth_usdt"] - 1.0) * 100.0
    ethbtc = (current["ethbtc"] / base["ethbtc"] - 1.0) * 100.0
    matched = matching_return(base, current)
    return {
        "btc_pct": btc,
        "eth_pct": eth,
        "ethbtc_pct": ethbtc,
        "matched_top100_equal_weight_pct": matched,
        "matched_top100_minus_btc_pp": None if matched is None else matched - btc,
        "matched_top100_minus_eth_pp": None if matched is None else matched - eth,
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
            "historical_validity_policy": HISTORICAL_VALIDITY_POLICY,
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
                "matched_top100_minus_btc_pp": rb["matched_top100_minus_btc_pp"],
                "matched_top100_minus_eth_pp": rb["matched_top100_minus_eth_pp"],
                "current_top100_advance_ratio": current.get("top100_advance_ratio"),
                "descriptive_positive_outcome": None if rb["matched_top100_equal_weight_pct"] is None else rb["matched_top100_equal_weight_pct"] > 0,
                "descriptive_outperformed_btc": None if rb["matched_top100_minus_btc_pp"] is None else rb["matched_top100_minus_btc_pp"] > 0,
                "historical_validity_policy": HISTORICAL_VALIDITY_POLICY,
            }
        write_json(op, out)


def build_summary(now):
    by_horizon = {}
    activation_events = 0
    if EVENTS.exists():
        activation_events = sum(1 for f in EVENTS.glob("*.json") if (read_json(f) or {}).get("event_type") == "ACTIVATION")
    for label in HORIZONS_H:
        vals, btc_vals, eth_vals, alpha_btc_vals, alpha_eth_vals = [], [], [], [], []
        matured = 0
        if OUTCOMES.exists():
            for f in OUTCOMES.glob("*.json"):
                h = ((read_json(f) or {}).get("horizons") or {}).get(label)
                if not h:
                    continue
                matured += 1
                btc = h["btc_return_since_signal_pct"]
                eth = h["eth_return_since_signal_pct"]
                btc_vals.append(btc)
                eth_vals.append(eth)
                v = h.get("matched_top100_equal_weight_return_since_signal_pct")
                if v is not None:
                    vals.append(v)
                    alpha_btc_vals.append(h.get("matched_top100_minus_btc_pp", v - btc))
                    alpha_eth_vals.append(h.get("matched_top100_minus_eth_pp", v - eth))
        by_horizon[label] = {
            "matured_event_count": matured,
            "matched_top100_available_count": len(vals),
            "matched_top100_positive_rate_pct": None if not vals else 100.0 * sum(v > 0 for v in vals) / len(vals),
            "matched_top100_mean_return_pct": None if not vals else statistics.fmean(vals),
            "matched_top100_median_return_pct": None if not vals else statistics.median(vals),
            "matched_top100_outperformed_btc_rate_pct": None if not alpha_btc_vals else 100.0 * sum(v > 0 for v in alpha_btc_vals) / len(alpha_btc_vals),
            "matched_top100_minus_btc_mean_pp": None if not alpha_btc_vals else statistics.fmean(alpha_btc_vals),
            "matched_top100_outperformed_eth_rate_pct": None if not alpha_eth_vals else 100.0 * sum(v > 0 for v in alpha_eth_vals) / len(alpha_eth_vals),
            "matched_top100_minus_eth_mean_pp": None if not alpha_eth_vals else statistics.fmean(alpha_eth_vals),
            "btc_mean_return_pct": None if not btc_vals else statistics.fmean(btc_vals),
            "eth_mean_return_pct": None if not eth_vals else statistics.fmean(eth_vals),
        }
    write_json(SUMMARY, {
        "contract": "ENTRY_SIGNAL_PERFORMANCE_SUMMARY_v1",
        "definition_version": DEFINITION_VERSION,
        "generated_at_utc": now.isoformat(),
        "activation_event_count": activation_events,
        "evaluation_note": (
            "Forward outcomes are descriptive definition-quality evidence, not a trading rule, optimized hit threshold, "
            "or authority to rewrite historical event validity."
        ),
        "historical_validity_policy": HISTORICAL_VALIDITY_POLICY,
        "horizons": by_horizon,
    })


def main():
    now = now_utc()
    current = latest_market()
    state, checks, heat, observer_state = classify(current)
    prev = read_json(STATE) or {}
    previous = prev.get("state")
    latest = {
        "contract": "ENTRY_SIGNAL_LATEST_v1",
        "definition_version": DEFINITION_VERSION,
        "generated_at_utc": now.isoformat(),
        "state": state,
        "observer_state": observer_state,
        "previous_state": previous,
        "execution_temperature": heat,
        "criteria": checks,
        "market_snapshot": {k: v for k, v in current.items() if k != "constituents"},
        "measurement_validity": current.get("measurement_validity"),
        "historical_validity_policy": HISTORICAL_VALIDITY_POLICY,
        "authority": {
            "canonical_market_state": False,
            "portfolio_execution": False,
            "market_rule_change": False,
            "purpose": "timestamped measurement-validity-aware observation and forward outcome learning",
        },
        "data_ping_bridge": {
            "binding": False,
            "canonical_action_authority": "NONE",
            "display_line": bridge_display_line(state, observer_state, heat, current),
        },
    }
    write_json(LATEST, latest)
    if previous is None or previous != state:
        etype = "ACTIVATION" if state == "GRADUATED_ALTCOIN_TOPUP_ACTIVE" else ("DEACTIVATION" if previous == "GRADUATED_ALTCOIN_TOPUP_ACTIVE" else "INITIAL_STATE")
        eid = event_id(now, state)
        write_json(EVENTS / (eid + ".json"), {
            "contract": "ENTRY_SIGNAL_EVENT_v1",
            "definition_version": DEFINITION_VERSION,
            "event_id": eid,
            "event_type": etype,
            "event_time_utc": now.isoformat(),
            "state": state,
            "observer_state": observer_state,
            "previous_state": previous,
            "execution_temperature": heat,
            "criteria": checks,
            "market_snapshot": current,
            "measurement_validity": current.get("measurement_validity"),
            "historical_validity_policy": HISTORICAL_VALIDITY_POLICY,
            "authority": {"canonical_market_state": False, "portfolio_execution": False, "retrospective_rule_change": False},
        })
    write_json(STATE, {
        "contract": "ENTRY_SIGNAL_STATE_v1",
        "definition_version": DEFINITION_VERSION,
        "updated_at_utc": now.isoformat(),
        "state": state,
        "observer_state": observer_state,
        "execution_temperature": heat,
        "criteria": checks,
        "measurement_validity": current.get("measurement_validity"),
        "historical_validity_policy": HISTORICAL_VALIDITY_POLICY,
    })
    update_outcomes(current, now)
    build_summary(now)
    print(json.dumps(latest, sort_keys=True))


if __name__ == "__main__":
    main()
