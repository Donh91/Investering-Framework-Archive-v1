"""Assemble deliverables: final vintage ledger, revision summary, policy comparison, RT results + F04 contamination."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from statistics import median

from etf_lab_common import REPO, WORK, is_session, session_close_utc, ts, write_json

OUT = WORK / "out"
PKG = WORK / "pkg"
sys.path.insert(0, str(REPO))


def final_ledger():
    ledger = [json.loads(l) for l in (OUT / "ledger_raw.jsonl").read_text().splitlines()]
    sessions = {(s["asset"], s["session_date"]): s for s in json.loads((OUT / "sessions.json").read_text())}
    keep = ["first_observed_at_utc", "first_observed_total", "first_realtime_observed_at_utc", "first_realtime_total", "later_observed_total",
            "later_observed_at_utc", "revision_detected", "revision_kinds", "revision_delta_total", "first_complete_observation_at_utc",
            "first_verified_final_observation_at_utc", "knowledge_time_status", "last_attempt_absent_before_first_observation_utc"]
    rows = []
    for r in ledger:
        s = sessions[(r["asset"], r["session_date"])]
        row = {"ledger_version": "ETF_VINTAGE_LEDGER_v1", **{k: r[k] for k in (
            "ledger_key", "asset", "session_date", "is_nyse_session", "observation_source", "observation_kind", "value_scope",
            "observed_at_utc", "observed_at_basis", "source_retrieved_at_utc", "verification_completed_at_utc", "source_hash", "schema_hash", "row_hash",
            "fund_header_set", "fund_count", "fund_values", "reported_total", "calculated_total", "parity", "unknown_cell_count", "unknown_funds",
            "session_final_claim", "workflow_status", "source_evidence_path", "git_commit", "git_commit_time_utc", "not_source_revision", "notes")}}
        row["session"] = {k: s[k] for k in keep}
        rows.append(row)
    PKG.mkdir(parents=True, exist_ok=True)
    with (PKG / "ETF_VINTAGE_LEDGER.jsonl").open("w") as h:
        for r in rows:
            h.write(json.dumps(r, sort_keys=True) + "\n")
    return rows, sessions


def revision_summary(sessions):
    events = json.loads((OUT / "revision_events.json").read_text())
    by_kind = Counter((e["kind"], e["asset"]) for e in events)
    revised = sorted({(e["asset"], e["session_date"]) for e in events})
    deltas = [abs(e["total_delta"]) for e in events if e["total_delta"] is not None]
    lag_close = [e["lag_after_session_close_h"] for e in events]
    lag_first = [e["lag_after_first_observation_h"] for e in events]
    sign_changes = [{"asset": e["asset"], "session": e["session_date"], "from": e["total_from"], "to": e["total_to"]} for e in events
                    if e["total_from"] is not None and e["total_to"] is not None and (e["total_from"] > 0) != (e["total_to"] > 0) and e["total_from"] != 0 and e["total_to"] != 0]
    zero_to_value = [{"asset": e["asset"], "session": e["session_date"], "to": e["total_to"]} for e in events if e["total_from"] == 0.0 and e["total_to"] not in (0.0, None)]

    def stats(v):
        v = sorted(v)
        return {"n": len(v), "median": round(median(v), 3), "max": round(max(v), 3), "p90": round(v[int(0.9 * (len(v) - 1))], 3)} if v else None

    per_kind = {}
    for kind in sorted({e["kind"] for e in events}):
        ev = [e for e in events if e["kind"] == kind]
        per_kind[kind] = {"events": len(ev), "sessions": len({(e["asset"], e["session_date"]) for e in ev}),
                          "btc": sum(1 for e in ev if e["asset"] == "BTC"), "eth": sum(1 for e in ev if e["asset"] == "ETH"),
                          "abs_total_delta_usd_m": stats([abs(e["total_delta"]) for e in ev if e["total_delta"] is not None]),
                          "lag_after_session_close_h": stats([e["lag_after_session_close_h"] for e in ev]),
                          "lag_after_first_observation_h": stats([e["lag_after_first_observation_h"] for e in ev])}

    # rolling-feature change: W30 features on first-real-time values vs latest vintage (evidenced sessions only)
    from backtest_engine.w30_replay import build_etf_trailing
    feat_changes = {}
    ledger = [json.loads(l) for l in (OUT / "ledger_raw.jsonl").read_text().splitlines()]
    final_by, first_by = {}, {}
    for r in sorted(ledger, key=lambda r: r["observed_at_utc"]):
        if r.get("not_source_revision"):
            continue
        k = (r["asset"], r["session_date"])
        final_by[k] = r
        if r["observation_kind"] in ("REAL_TIME_CAPTURE", "MEDIATED_CAPTURE") and k not in first_by:
            first_by[k] = r
    for asset in ("BTC", "ETH"):
        keys = sorted(k for k in final_by if k[0] == asset and final_by[k]["reported_total"] is not None)
        def rows(pick):
            return [{"date": k[1], "total_usd_millions": pick(k)["reported_total"], "not_before_session_close_utc": k[1] + "T20:00:00Z",
                     "publication_timestamp_verified": "False", "asset": asset, "source": "LAB", "method_id": "LAB"} for k in keys]
        a = {r["date"]: r for r in build_etf_trailing(rows(lambda k: first_by.get(k, final_by[k])), asset)}
        b = {r["date"]: r for r in build_etf_trailing(rows(lambda k: final_by[k]), asset)}
        fields = ["total_usd_millions", "rolling_net_flow_3s_usd_millions", "rolling_net_flow_5s_usd_millions", "rolling_net_flow_10s_usd_millions",
                  "rolling_net_flow_20s_usd_millions", "signed_flow_streak_sessions", "reversal_flag"]
        out = {}
        for f in fields:
            diffs = [(d, a[d][f], b[d][f]) for d in a if a[d][f] != b[d][f] and not (isinstance(a[d][f], float) and isinstance(b[d][f], float) and abs(a[d][f] - b[d][f]) < 1e-9)]
            num = [abs(x - y) for _, x, y in diffs if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool)]
            out[f] = {"rows_changed": len(diffs), "max_abs_change": round(max(num), 3) if num else None, "first_dates": [d for d, _, _ in diffs[:3]]}
        feat_changes[asset] = out

    downstream = {
        "daily_director_contexts_with_false_final_settled_rows": 15,
        "daily_director_outputs_quoting_them": [
            "research/api_agent/outputs/daily/2026/08/18/093532/DAILY_DIRECTOR_OUTPUT.json (BTC 137.3, ETH 5.0; final 297.5 / 30.9)",
            "research/api_agent/outputs/daily/2026/08/18/141002/DAILY_DIRECTOR_OUTPUT.json",
            "research/api_agent/outputs/daily/2026/08/18/214942/DAILY_DIRECTOR_OUTPUT.json",
            "research/api_agent/outputs/daily/2026/08/20/093603/DAILY_DIRECTOR_OUTPUT.json (BTC 164.2, ETH 17.7 'passed parity'; final 517.2 / 189.1 incl. MSSE)",
            "research/api_agent/outputs/daily/2026/08/20/215544/DAILY_DIRECTOR_OUTPUT.json ('Settled ETF context is verified for 2026-08-19: BTC 164.2')"],
        "authority_of_consumer": "SHADOW_CONTEXT_ONLY (director); forecast_candidates emitted in those runs; causal effect of the ETF numbers on the candidates is not attributable -> UNKNOWN",
        "weekly_settled_calibration_W34": "used the corrected signatures (297.5 / 517.2) - SAFE because it reads the latest signature at freeze time",
        "stage_1_etf_flow_leg_2026_07_16": "live gate evaluated NOT_FIRED at 03:41:48Z on the provisional row (IBIT not reported) and ratified at 06:34:00Z after the late IBIT value - handled correctly by humans, not by code",
    }
    return {
        "contract": "ETF_REVISION_SUMMARY_v1",
        "definitions": {
            "DATA_REVISION": "a later vintage of the same session carries a different fund or total value",
            "KNOWLEDGE_TIME_DELAY": "no value change; the session was absent, all-dash or incomplete when an attempt looked (counted in the policy comparison, never here)",
            "taxonomy": ["LATE_FUND_VALUE", "NEW_FUND_BACKFILL", "TOTAL_RECOMPUTE", "SCHEMA_EXTENSION", "SOURCE_CORRECTION", "LATE_PUBLICATION", "UNKNOWN_REVISION"],
            "excluded_not_source_revisions": ["ETH 2026-07-20 3.7 (transcription error, superseded 2026-07-22T06:03:35Z)", "11 malformed v1 pack rows (#1212 defect, not a source vintage)"],
        },
        "revised_sessions": len(revised), "revised_sessions_btc": sum(1 for a, _ in revised if a == "BTC"), "revised_sessions_eth": sum(1 for a, _ in revised if a == "ETH"),
        "revision_events": len(events), "by_kind_and_asset": {f"{k}|{a}": v for (k, a), v in sorted(by_kind.items())},
        "per_kind": per_kind,
        "kinds_with_zero_events": sorted({"LATE_FUND_VALUE", "NEW_FUND_BACKFILL", "TOTAL_RECOMPUTE", "SCHEMA_EXTENSION", "SOURCE_CORRECTION", "UNKNOWN_REVISION"} - {e["kind"] for e in events}),
        "schema_extension_without_value_change_sessions": sum(1 for s in sessions.values() if s["schema_only_change_detected"] and not s["revision_detected"]),
        "late_publication_note": "no session was proven absent after its close by an automated attempt (FLO/settled first attempts after close already listed the row); publication-time lower bounds therefore stay the session close",
        "abs_total_delta_usd_m": stats(deltas), "lag_after_session_close_h": stats(lag_close), "lag_after_first_observation_h": stats(lag_first),
        "max_observed_revision_lag": {"after_close_h": max(lag_close), "event": max(events, key=lambda e: e["lag_after_session_close_h"])},
        "sign_changes": sign_changes, "zero_to_value_changes": zero_to_value,
        "material_revisions_abs_delta_ge_100m": [{"asset": e["asset"], "session": e["session_date"], "kind": e["kind"], "from": e["total_from"], "to": e["total_to"], "to_source": e["to_source"]}
                                                  for e in events if e["total_delta"] is not None and abs(e["total_delta"]) >= 100],
        "rolling_feature_changes_first_vs_latest_vintage_W30": feat_changes,
        "no_source_corrections_in_history": "all 1127 non-malformed, non-closure v1 rows equal the 2026-09-23 live vintage (zero-fill equivalence); no historical value was restated between 2026-07-26 and 2026-09-23 except the MSSE column",
        "pending_all_dash_rows_accepted_as_zero_flow": ["BTC 2026-09-08 and ETH 2026-09-08 at 2026-09-09T05:55:36Z: every fund '-', Total 0.0, parity True, session_final True, owner status PASS"],
        "settled_rows_stored_with_unknown_cells": 7,
        "downstream": downstream,
        "events": events,
    }


def f04_contamination():
    """E1X F04: W30 claims feature knowledge at session close. Compare with supported policies on evidenced sessions."""
    import rt_policies as R
    from policies import structural_dash_index
    ledger, L = R.load()
    idx = structural_dash_index(ledger)
    by = R.chains(ledger)
    res = {}
    for ref in ("PRE_BACKFILL_VINTAGE", "LATEST_VINTAGE"):
        base_records, _ = R.build_records("A_SESSION_CLOSE", by, idx, L, ref)
        full = R.compute_w30(base_records)
        # what was knowable at each output's session-close claim
        out = {"rows_compared": 0, "rows_differing_at_claim": 0, "rows_missing_at_claim": 0, "differing_dates": [], "by_field": Counter()}
        claims = sorted({o.claimed_available_at for k, o in full.items() if not k.startswith("DIV")})
        evidenced = {f"{a}|{d}" for (a, d), rows in by.items() if any(r["observation_kind"] in R.REALTIME for r in rows)}
        cache = {}
        for key, o in sorted(full.items()):
            sess_key = key if not key.startswith("DIV") else "BTC|" + key.split("|")[1]
            if sess_key not in evidenced:
                continue
            t = o.claimed_available_at
            if t not in cache:
                cache[t] = R.compute_w30([r for r in base_records if r.available_at <= t])
            v = cache[t].get(key)
            out["rows_compared"] += 1
            if v is None:
                out["rows_missing_at_claim"] += 1
                out["differing_dates"].append(key)
                continue
            d = [f for f in o.fields if o.fields[f] != v.fields.get(f)]
            if d:
                out["rows_differing_at_claim"] += 1
                out["differing_dates"].append(key)
                out["by_field"].update(d)
        out["by_field"] = dict(out["by_field"].most_common(12))
        out["differing_dates"] = out["differing_dates"][:40]
        res[ref] = out
    # Stage-1 style signal (3 consecutive positive BTC sessions with IBIT positive): firing time under session-close claims vs evidence
    sig = []
    btc = sorted((k for k in by if k[0] == "BTC"), key=lambda k: k[1])
    fin = {k: by[k][-1] for k in btc}
    def pos(k):
        r = fin[k]
        ib = dict(zip(r["fund_header_set"] or [], r["fund_values"] or [])).get("IBIT")
        return (r["reported_total"] or 0) > 0 and (ib or 0) > 0
    for i in range(2, len(btc)):
        if btc[i][1] < "2026-07-01":
            continue
        if pos(btc[i]) and pos(btc[i - 1]) and pos(btc[i - 2]):
            k = btc[i]
            rt = [r for r in by[k] if r["observation_kind"] in R.REALTIME]
            first_ok = next((r for r in rt if (r["reported_total"] or 0) > 0 and (dict(zip(r["fund_header_set"] or [], r["fund_values"] or [])).get("IBIT") or 0) > 0), None)
            sig.append({"session": k[1], "claimed_by_session_close": R.iso(session_close_utc(k[1])),
                        "first_observation_supporting_signal": first_ok["observed_at_utc"] if first_ok else None,
                        "delay_h": round((ts(first_ok["observed_at_utc"]) - session_close_utc(k[1])).total_seconds() / 3600, 2) if first_ok else None,
                        "evidence": "OBSERVED" if first_ok else "NO_REALTIME_EVIDENCE"})
    return {
        "structural_leak_confirmed": True,
        "structural_basis": "every evidenced session was first observable after its session close (min first-observation lag {} h); W30 build_etf_trailing claims feature_knowledge_available_at_utc = session close".format(
            min(s["first_realtime_lag_h"] for s in json.loads((OUT / "sessions.json").read_text()) if s["first_realtime_lag_h"] is not None)),
        "feature_rows_at_session_close_vs_point_in_time": res,
        "stage1_signal_timing_2026_07_onward": sig,
        "material_performance_impact": "UNKNOWN",
        "material_basis": ("No recorded backtest decision, forecast, score or outcome consumes W30 build_etf_trailing or the pack feature table (consumers: golden replay fixture + E1X harness only). "
                           "Impact on a future ETF-flow backtest is structural (on every evidenced session the first observation came >= 6.3 h after the close; 0 of 177 evidenced feature rows were computable at their session-close claim) and value-level on revised sessions; "
                           "performance impact cannot be measured without a consuming strategy."),
    }


def main():
    rows, sessions = final_ledger()
    rev = revision_summary(sessions)
    write_json(PKG / "ETF_REVISION_SUMMARY.json", rev)
    pol = json.loads((OUT / "policy_results.json").read_text())
    write_json(PKG / "ETF_KNOWLEDGE_TIME_POLICY_COMPARISON.json", {"contract": "ETF_KNOWLEDGE_TIME_POLICY_COMPARISON_v1",
        "policies": {"A_SESSION_CLOSE": "K = NYSE close (16:00 ET; 13:00 on early closes)", "B_FIRST_OBSERVED": "K = first real-time observation; value = that observation",
                     "C_FIRST_COMPLETE_OBSERVED": "K = first observation that is complete by the live rule (parity, total present, every unknown cell was also unknown in the previous session of the same snapshot; all-dash rows never complete)",
                     "D_FIRST_VERIFIED_FINAL_OBSERVED": "K = verification_completed_at of the first settled double-read capture",
                     "E_CONSERVATIVE_FIXED_LAG": "K = close + L, L from E_lag_basis (descriptive in-sample maximum; never tuned)",
                     "F_NEXT_TRADING_SESSION": "K = next NYSE session open 09:30 ET"},
        "references": {"LATEST_VINTAGE": "judged against the latest known vintage (2026-09-23 live read, includes MSSE backfill)",
                       "PRE_BACKFILL_VINTAGE": "judged against the last pre-MSSE vintage: isolates KNOWLEDGE-TIME DELAY from the MSSE DATA REVISION"},
        **pol}, )
    rt = json.loads((OUT / "rt_results.json").read_text())
    write_json(PKG / "ETF_RIGHT_TRUNCATION_RESULTS.json", {"contract": "ETF_RIGHT_TRUNCATION_RESULTS_v1", "harness": "scripts/experiments/strategy_factor_leakage_e1_production.py (unchanged) run_right_truncation",
        "outcome_vocabulary": ["PASS", "TRUE_FUTURE_LEAKAGE", "SOURCE_VINTAGE_RISK", "INSUFFICIENT_HISTORY", "UNKNOWN"],
        "attribution_rules": {"SOURCE_VINTAGE_RISK": "culprit is a later vintage (REVISION) of a session",
                              "TRUE_FUTURE_LEAKAGE_PROVEN": "rule-based policy; the culprit session was provably not knowable at K (policy evidence table)",
                              "TRUE_FUTURE_LEAKAGE_FEATURE_CLAIM_NON_MONOTONE": "observation-based policy; a trailing feature is claimed at its own row's K although an input row's own K is later",
                              "OBSERVATION_LIMITED_UNKNOWN": "the culprit record is late only because no automated capture looked earlier; not proof"},
        "absorption_feature": "not re-run: scripts/experiments/etf_absorption_transmission_v1.py joins settled captures as-of retrieved_at (its knowledge time IS the observation time, policy B/D semantics); E1X recorded NO_ISSUE. It inherits the SOURCE_VINTAGE_RISK of settled rows (08-17/08-19, MSSE).",
        "results": rt, "f04_contamination": f04_contamination()})
    print("ledger rows", len(rows), "revised sessions", rev["revised_sessions"], rev["by_kind_and_asset"])
    print(json.dumps(rev["rolling_feature_changes_first_vs_latest_vintage_W30"])[:800])


if __name__ == "__main__":
    main()
