#!/usr/bin/env python3
import csv, json, statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("04_MARKET_LEARNING/pullback_learning")
OBS = ROOT / "observations"
EPISODES = ROOT / "episodes"
LATEST = ROOT / "LATEST.json"
STATE = ROOT / "STATE.json"
SUMMARY = ROOT / "PERFORMANCE_SUMMARY.json"
ENTRY_LATEST = Path("04_MARKET_LEARNING/entry_signals/LATEST.json")
BREADTH_LATEST = Path("03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
HOURLY_POINTER = Path("03_DAILY_CAPTURE_LOGS/hourly/LATEST.json")
TRAILING_OBS = 180
MIN_OBS_FOR_ADAPTIVE = 24
MIN_EPISODES_EMERGING = 10
MIN_EPISODES_USABLE = 30
HYPOTHETICAL_TRIM_FRACTION = 0.10
ROUNDTRIP_FRICTION_PCT = 0.20


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


def percentile_rank(values, x):
    vals = [float(v) for v in values if v is not None]
    if not vals:
        return None
    return 100.0 * sum(v <= x for v in vals) / len(vals)


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


def current_snapshot():
    entry = read_json(ENTRY_LATEST)
    breadth = read_json(BREADTH_LATEST)
    if not entry or not breadth:
        raise RuntimeError("entry signal or breadth latest missing")
    agg = breadth.get("aggregate", breadth)
    constituents = {
        str(x.get("asset_id")): float(x["price_usd"])
        for x in breadth.get("constituents", [])
        if x.get("asset_id") and x.get("price_usd") not in (None, 0)
    }
    if not constituents:
        raise RuntimeError("breadth latest has no constituent prices")
    pointer, hourly_ts, row = hourly_latest_row()
    breadth_ratio = agg.get("advance_ratio")
    if breadth_ratio is None and agg.get("advancer_pct") is not None:
        breadth_ratio = float(agg["advancer_pct"]) / 100.0
    if breadth_ratio is None:
        raise RuntimeError("breadth ratio unavailable")
    return {
        "captured_at_utc": now_utc().isoformat(),
        "price_observation_utc": hourly_ts.isoformat(),
        "hourly_sequence_run_id": pointer.get("run_id"),
        "price_source": "GITHUB_HOURLY_SEQUENCE_DIRECT_CLOSES",
        "entry_state": entry.get("state"),
        "entry_heat": entry.get("execution_temperature"),
        "btc_usdt": float(row["btc_close"]),
        "eth_usdt": float(row["eth_close"]),
        "ethbtc": float(row["ethbtc_close"]),
        "breadth": float(breadth_ratio),
        "advancer_pct": agg.get("advancer_pct"),
        "ew_return_24h_pct": agg.get("equal_weight_mean_return_24h_pct"),
        "median_return_24h_pct": agg.get("median_return_24h_pct"),
        "membership_hash": agg.get("membership_hash"),
        "constituents": constituents,
    }


def observation_files():
    return sorted(OBS.rglob("*.json")) if OBS.exists() else []


def load_recent_observations(limit=TRAILING_OBS):
    rows = []
    for p in observation_files()[-limit:]:
        d = read_json(p)
        if d:
            rows.append(d)
    return rows


def matched_return(prev, cur):
    p = prev.get("constituents", {})
    c = cur.get("constituents", {})
    vals = []
    for k, p0 in p.items():
        p1 = c.get(k)
        if p0 and p1:
            vals.append((p1 / p0 - 1.0) * 100.0)
    if not vals:
        return None, 0
    return statistics.fmean(vals), len(vals)


def synthetic_index(prev, step_return_pct):
    if prev is None:
        return 100.0
    prior = float(prev.get("synthetic_top100_index", 100.0))
    if step_return_pct is None:
        return prior
    return prior * (1.0 + step_return_pct / 100.0)


def classify(recent, current_obs, previous_state):
    n = len(recent)
    if n < MIN_OBS_FOR_ADAPTIVE:
        return "LEARNING_WARMUP", {
            "observation_count": n,
            "minimum_required": MIN_OBS_FOR_ADAPTIVE,
            "adaptive_percentiles_ready": False,
        }
    drawdowns = [o.get("drawdown_from_running_peak_pct") for o in recent]
    breadths = [o.get("breadth") for o in recent]
    steps = [o.get("matched_top100_step_return_pct") for o in recent]
    dd_rank = percentile_rank(drawdowns, current_obs["drawdown_from_running_peak_pct"])
    br_rank = percentile_rank(breadths, current_obs["breadth"])
    step_rank = percentile_rank(steps, current_obs["matched_top100_step_return_pct"] or 0.0)
    evidence = {
        "observation_count": n,
        "adaptive_percentiles_ready": True,
        "drawdown_percentile_rank": dd_rank,
        "breadth_percentile_rank": br_rank,
        "step_return_percentile_rank": step_rank,
        "rules_are_research_only": True,
    }
    entry_active = current_obs.get("entry_state") == "GRADUATED_ALTCOIN_TOPUP_ACTIVE"
    if not entry_active:
        return "REGIME_NOT_ACTIVE", evidence
    active = dd_rank is not None and br_rank is not None and step_rank is not None
    if active and dd_rank <= 10 and br_rank <= 20 and step_rank <= 20:
        return "PULLBACK_ACTIVE_RESEARCH", evidence
    if active and dd_rank <= 20 and (br_rank <= 25 or step_rank <= 20):
        return "PULLBACK_RISK_RESEARCH", evidence
    prev = recent[-1] if recent else None
    improving_dd = prev is not None and current_obs["drawdown_from_running_peak_pct"] > prev.get("drawdown_from_running_peak_pct", current_obs["drawdown_from_running_peak_pct"])
    if previous_state in {"PULLBACK_ACTIVE_RESEARCH", "PULLBACK_RISK_RESEARCH"} and improving_dd and br_rank >= 50 and step_rank >= 70:
        return "RELOAD_WATCH_RESEARCH", evidence
    return "NORMAL", evidence


def episode_files():
    return sorted(EPISODES.glob("*.json")) if EPISODES.exists() else []


def active_episode():
    for p in reversed(episode_files()):
        d = read_json(p)
        if d and d.get("status") == "OPEN":
            return p, d
    return None, None


def token_uplift(trim_prices, reload_prices):
    vals = []
    for k, p0 in trim_prices.items():
        p1 = reload_prices.get(k)
        if p0 and p1:
            gross_full_portfolio_pct = HYPOTHETICAL_TRIM_FRACTION * (p0 / p1 - 1.0) * 100.0
            net = gross_full_portfolio_pct - HYPOTHETICAL_TRIM_FRACTION * ROUNDTRIP_FRICTION_PCT
            vals.append(net)
    if not vals:
        return None
    return {
        "matched_constituent_count": len(vals),
        "mean_full_portfolio_token_uplift_pct": statistics.fmean(vals),
        "median_full_portfolio_token_uplift_pct": statistics.median(vals),
        "positive_constituent_rate_pct": 100.0 * sum(v > 0 for v in vals) / len(vals),
        "trim_fraction": HYPOTHETICAL_TRIM_FRACTION,
        "assumed_roundtrip_friction_pct_on_traded_slice": ROUNDTRIP_FRICTION_PCT,
        "benchmark": "HOLD_SAME_CONSTITUENT",
    }


def update_episode(state, obs, now):
    path, ep = active_episode()
    risk_states = {"PULLBACK_RISK_RESEARCH", "PULLBACK_ACTIVE_RESEARCH"}
    if ep is None and state in risk_states:
        eid = now.strftime("%Y%m%dT%H%M%SZ") + "_pullback_research"
        ep = {
            "contract": "PULLBACK_LEARNING_EPISODE_v1",
            "episode_id": eid,
            "status": "OPEN",
            "opened_at_utc": now.isoformat(),
            "opening_research_state": state,
            "trim_candidate_snapshot": obs,
            "trough": {
                "synthetic_top100_index": obs["synthetic_top100_index"],
                "observed_at_utc": now.isoformat(),
            },
            "authority": {
                "portfolio_execution": False,
                "canonical_market_state": False,
                "research_only": True,
            },
        }
        path = EPISODES / f"{eid}.json"
        write_json(path, ep)
        return
    if ep is None:
        return
    idx = obs["synthetic_top100_index"]
    if idx < ep["trough"]["synthetic_top100_index"]:
        ep["trough"] = {"synthetic_top100_index": idx, "observed_at_utc": now.isoformat()}
    ep["last_observed_at_utc"] = now.isoformat()
    ep["last_research_state"] = state
    if state == "RELOAD_WATCH_RESEARCH":
        ep["status"] = "CLOSED_RELOAD_WATCH"
        ep["closed_at_utc"] = now.isoformat()
        ep["reload_candidate_snapshot"] = obs
        ep["hypothetical_10pct_trim_reload_vs_hold"] = token_uplift(
            ep["trim_candidate_snapshot"].get("constituents", {}), obs.get("constituents", {})
        )
    write_json(path, ep)


def build_summary(now):
    closed = []
    for p in episode_files():
        d = read_json(p)
        if d and d.get("status") == "CLOSED_RELOAD_WATCH" and d.get("hypothetical_10pct_trim_reload_vs_hold"):
            closed.append(d)
    vals = [d["hypothetical_10pct_trim_reload_vs_hold"]["median_full_portfolio_token_uplift_pct"] for d in closed]
    count = len(vals)
    confidence = "INSUFFICIENT_SAMPLE"
    if count >= MIN_EPISODES_USABLE:
        confidence = "USABLE_DESCRIPTIVE"
    elif count >= MIN_EPISODES_EMERGING:
        confidence = "EMERGING"
    summary = {
        "contract": "PULLBACK_LEARNING_PERFORMANCE_SUMMARY_v1",
        "generated_at_utc": now.isoformat(),
        "closed_episode_count": count,
        "learning_confidence": confidence,
        "minimum_episodes_emerging": MIN_EPISODES_EMERGING,
        "minimum_episodes_usable_descriptive": MIN_EPISODES_USABLE,
        "hypothetical_10pct_trim_reload_vs_hold": {
            "positive_episode_rate_pct": None if not vals else 100.0 * sum(v > 0 for v in vals) / len(vals),
            "mean_median_token_uplift_pct": None if not vals else statistics.fmean(vals),
            "median_median_token_uplift_pct": None if not vals else statistics.median(vals),
        },
        "governance": {
            "automatic_rule_changes": False,
            "portfolio_execution": False,
            "purpose": "adaptive descriptive learning and future calibration evidence",
            "promotion_requires_separate_review": True,
        },
    }
    write_json(SUMMARY, summary)
    return summary


def main():
    now = now_utc()
    cur = current_snapshot()
    recent = load_recent_observations()
    prev = recent[-1] if recent else None
    if prev and prev.get("price_observation_utc") == cur["price_observation_utc"]:
        summary = build_summary(now)
        latest = read_json(LATEST) or {}
        latest["generated_at_utc"] = now.isoformat()
        latest["duplicate_price_observation_skipped"] = True
        latest["performance_summary"] = summary
        write_json(LATEST, latest)
        print(json.dumps(latest, sort_keys=True))
        return
    step_ret, matched = matched_return(prev or {}, cur) if prev else (None, 0)
    index = synthetic_index(prev, step_ret)
    prior_peaks = [float(o.get("synthetic_top100_index", 100.0)) for o in recent]
    peak = max(prior_peaks + [index]) if prior_peaks else index
    drawdown = (index / peak - 1.0) * 100.0
    obs = dict(cur)
    obs.update({
        "contract": "PULLBACK_LEARNING_OBSERVATION_v1",
        "synthetic_top100_index": index,
        "running_peak_index": peak,
        "drawdown_from_running_peak_pct": drawdown,
        "matched_top100_step_return_pct": step_ret,
        "matched_constituent_count": matched,
    })
    prev_state = (read_json(STATE) or {}).get("research_state")
    state, evidence = classify(recent, obs, prev_state)
    obs["research_state"] = state
    obs["adaptive_evidence"] = evidence
    ts = parse_utc(obs["price_observation_utc"])
    path = OBS / f"{ts:%Y/%m/%d}/{ts:%Y%m%dT%H%M%SZ}.json"
    write_json(path, obs)
    update_episode(state, obs, now)
    summary = build_summary(now)
    state_obj = {
        "contract": "PULLBACK_LEARNING_STATE_v1",
        "updated_at_utc": now.isoformat(),
        "research_state": state,
        "previous_research_state": prev_state,
        "adaptive_evidence": evidence,
        "observation_count": len(recent) + 1,
        "authority": {"portfolio_execution": False, "canonical_market_state": False, "research_only": True},
    }
    write_json(STATE, state_obj)
    latest = {
        "contract": "PULLBACK_LEARNING_LATEST_v1",
        "generated_at_utc": now.isoformat(),
        "research_state": state,
        "previous_research_state": prev_state,
        "market_snapshot": {k: v for k, v in obs.items() if k != "constituents"},
        "adaptive_evidence": evidence,
        "performance_summary": summary,
        "data_ping_bridge": {
            "display_line": f"PULLBACK LEARNING: {state} | dd={drawdown:.2f}% | breadth={obs['breadth']*100:.0f}% | sample={len(recent)+1}"
        },
        "authority": {
            "portfolio_execution": False,
            "canonical_market_state": False,
            "automatic_rule_changes": False,
            "research_only": True,
        },
    }
    write_json(LATEST, latest)
    print(json.dumps(latest, sort_keys=True))


if __name__ == "__main__":
    main()
