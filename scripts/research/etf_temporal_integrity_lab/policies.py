"""Section 5: #1211 knowledge-time policy experiment (A..F) over the vintage ledger.

A policy maps a session to a declared knowledge time K(s). It is judged only against observed evidence:
  * PROVEN_LOOKAHEAD      the value a backtest would bind (latest vintage) was demonstrably NOT observable at K
  * REVISED_AFTER_K       the value observable at K differs from the latest vintage (false finality if the policy claims finality)
  * CONSISTENT_AT_K       the latest vintage was already observed at or before K
  * UNKNOWN_AT_K          nothing observed at/before K and the next observation already equals the latest vintage
  * UNDEFINED             the policy cannot assign K (data loss)
No lag is chosen for performance; E's lag is the descriptive sample maximum of an evidence quantity and is reported as such.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import timedelta
from statistics import median

from etf_lab_common import WORK, iso, is_session, next_session, session_close_utc, session_open_utc, ts, write_json
from revisions import SETTLED, compare, funds

OUT = WORK / "out"
REALTIME = ("REAL_TIME_CAPTURE", "MEDIATED_CAPTURE")


def load():
    ledger = [json.loads(l) for l in (OUT / "ledger_raw.jsonl").read_text().splitlines()]
    sessions = {(s["asset"], s["session_date"]): s for s in json.loads((OUT / "sessions.json").read_text())}
    return ledger, sessions


def structural_dash_index(ledger):
    """(source, observed_at, asset) -> {session: set(unknown funds)} to apply the live completeness rule."""
    idx = defaultdict(dict)
    for r in ledger:
        if r["fund_values"] is not None:
            idx[(r["observation_source"], r["observed_at_utc"], r["asset"])][r["session_date"]] = set(r["unknown_funds"])
    return idx


def complete_live(r, idx):
    """Implementable at observation time: parity holds, total present, and every unknown cell is a fund that was
    also unknown in the previous session of the SAME snapshot (structural dash, e.g. not-yet-launched fund)."""
    if r["fund_values"] is None or r["reported_total"] is None or r["parity"] is not True:
        return None
    if r["unknown_cell_count"] == 0:
        return True
    if r["unknown_cell_count"] == r["fund_count"]:
        return False  # all-dash row: pending, even when Total shows 0.0
    same = idx.get((r["observation_source"], r["observed_at_utc"], r["asset"]), {})
    prev = [d for d in same if d < r["session_date"]]
    if not prev:
        return None
    return set(r["unknown_funds"]) <= same[max(prev)]


def eq_final(r, final):
    k, _ = compare(r, final)
    return k is None or k == "SCHEMA_EXTENSION"


BACKFILL_CUT = "2026-09-17T11:35:26Z"  # last observation of the pre-MSSE layout (settled capture); MSSE backfill first observable after it


def evaluate(ledger, sessions, reference="LATEST_VINTAGE", attempts=None):
    idx = structural_dash_index(ledger)
    by = defaultdict(list)
    for r in ledger:
        if not r.get("not_source_revision"):
            by[(r["asset"], r["session_date"])].append(r)
    for rows in by.values():
        rows.sort(key=lambda r: (r["observed_at_utc"], r["observation_source"]))

    # ---- evidence quantity for E: lag from session close to first live-rule-complete observation
    complete_lags = []
    per = {}
    for key, rows in by.items():
        rt = [r for r in rows if r["observation_kind"] in REALTIME]
        if not rt or not is_session(key[1]):
            continue
        close = session_close_utc(key[1])
        comp = [r for r in rt if complete_live(r, idx) is True]
        final = rows[-1]
        if reference == "PRE_BACKFILL_VINTAGE":
            pre = [r for r in rt if r["observed_at_utc"] <= BACKFILL_CUT]
            final = pre[-1] if pre else rows[-1]
        per[key] = {"rt": rt, "final": final, "close": close, "complete": comp}
        if comp:
            complete_lags.append(((ts(comp[0]["observed_at_utc"]) - close).total_seconds() / 3600, key))
    # Only sessions whose timing is not observation-limited: an automated daily lane (FLO owner / settled double-read)
    # made an attempt within 24 h after the close. Mediated July captures are excluded from the lag basis.
    if attempts is None:
        attempts = json.loads((OUT / "capture_attempts.json").read_text())
    def daily_cadence(key):
        close = session_close_utc(key[1])
        return any(0 < (ts(a["at"]) - close).total_seconds() <= 86400 for a in attempts)
    basis = []
    for lag, key in complete_lags:
        if not daily_cadence(key):
            continue
        rt = per[key]["rt"]
        close = per[key]["close"]
        incompl = [r for r in rt if complete_live(r, idx) is False and ts(r["observed_at_utc"]) < ts(per[key]["complete"][0]["observed_at_utc"])]
        lower = (ts(incompl[-1]["observed_at_utc"]) - close).total_seconds() / 3600 if incompl else None
        basis.append({"asset": key[0], "session": key[1], "complete_upper_bound_h": round(lag, 3), "_exact": lag, "incomplete_lower_bound_h": None if lower is None else round(lower, 3)})
    L_hours = max(b["_exact"] for b in basis)
    for b in basis:
        b.pop("_exact")
    L_key = max(basis, key=lambda b: b["complete_upper_bound_h"])
    L_min_noncontradicted = max(b["incomplete_lower_bound_h"] for b in basis if b["incomplete_lower_bound_h"] is not None)

    def K(policy, key):
        p = per.get(key)
        day = key[1]
        close = session_close_utc(day)
        if policy == "A_SESSION_CLOSE":
            return close
        if policy == "E_CONSERVATIVE_FIXED_LAG":
            return close + timedelta(hours=L_hours)
        if policy == "F_NEXT_TRADING_SESSION":
            return session_open_utc(next_session(day))
        if p is None:
            return None
        if policy == "B_FIRST_OBSERVED":
            return ts(p["rt"][0]["observed_at_utc"])
        if policy == "C_FIRST_COMPLETE_OBSERVED":
            return ts(p["complete"][0]["observed_at_utc"]) if p["complete"] else None
        if policy == "D_FIRST_VERIFIED_FINAL_OBSERVED":
            st = [r for r in p["rt"] if r["observation_source"] in SETTLED]
            if not st:
                return None
            return ts(st[0]["verification_completed_at_utc"] or st[0]["observed_at_utc"])
        raise KeyError(policy)

    policies = ["A_SESSION_CLOSE", "B_FIRST_OBSERVED", "C_FIRST_COMPLETE_OBSERVED", "D_FIRST_VERIFIED_FINAL_OBSERVED",
                "E_CONSERVATIVE_FIXED_LAG", "F_NEXT_TRADING_SESSION"]
    binds_final = {"A_SESSION_CLOSE", "E_CONSERVATIVE_FIXED_LAG", "F_NEXT_TRADING_SESSION"}  # rule-based: backtests bind the latest vintage
    all_keys = [k for k in by if is_session(k[1])]
    results, per_session = {}, defaultdict(dict)
    for pol in policies:
        outcomes = Counter()
        kinds = Counter()
        lags_rev, latency, examples = [], [], defaultdict(list)
        for key in all_keys:
            k = K(pol, key)
            p = per.get(key)
            if k is None:
                o = "UNDEFINED_NO_QUALIFYING_OBSERVATION" if p else "UNDEFINED_NO_REALTIME_EVIDENCE"
                outcomes[o] += 1
                per_session[key][pol] = {"K": None, "outcome": o}
                continue
            if p is None:
                outcomes["DEFINED_UNVERIFIABLE_HISTORY"] += 1
                per_session[key][pol] = {"K": iso(k), "outcome": "DEFINED_UNVERIFIABLE_HISTORY"}
                continue
            final = p["final"]
            latency.append((k - p["close"]).total_seconds() / 3600)
            at_k = [r for r in p["rt"] if ts(r["observed_at_utc"]) <= k]
            after = [r for r in p["rt"] if ts(r["observed_at_utc"]) > k]
            v = at_k[-1] if at_k else None
            if v is None:
                nxt = after[0] if after else None
                if nxt is not None and not eq_final(nxt, final):
                    o = "PROVEN_LOOKAHEAD"
                else:
                    o = "UNKNOWN_AT_K"
            elif eq_final(v, final):
                o = "CONSISTENT_AT_K"
            else:
                o = "PROVEN_LOOKAHEAD" if pol in binds_final else "REVISED_AFTER_K"
                kind, _ = compare(v, final)
                kinds[kind] += 1
                fin = next((r for r in p["rt"] if ts(r["observed_at_utc"]) > k and eq_final(r, final)), None)
                lag = (ts((fin or final)["observed_at_utc"]) - k).total_seconds() / 3600
                lags_rev.append(lag)
            outcomes[o] += 1
            per_session[key][pol] = {"K": iso(k), "outcome": o}
            if len(examples[o]) < 4:
                examples[o].append({"asset": key[0], "session": key[1], "K": iso(k), "value_at_K": v["reported_total"] if v else None,
                                    "latest_vintage": final["reported_total"]})
        n = len(all_keys)
        undefined = sum(v for o, v in outcomes.items() if o.startswith("UNDEFINED"))
        evaluable = sum(v for o, v in outcomes.items() if o in ("PROVEN_LOOKAHEAD", "REVISED_AFTER_K", "CONSISTENT_AT_K", "UNKNOWN_AT_K"))
        results[pol] = {
            "sessions_total": n, "coverage_defined": n - undefined, "coverage_share": round((n - undefined) / n, 4),
            "evaluable_with_realtime_evidence": evaluable,
            "outcomes": dict(outcomes),
            "usable_verified": outcomes["CONSISTENT_AT_K"],
            "usable_unverified_history": outcomes["DEFINED_UNVERIFIABLE_HISTORY"],
            "unknown": outcomes["UNKNOWN_AT_K"] + outcomes["DEFINED_UNVERIFIABLE_HISTORY"],
            "later_revisions_after_declared_time": outcomes["REVISED_AFTER_K"] + (outcomes["PROVEN_LOOKAHEAD"] if pol in binds_final else 0),
            "revision_kinds_after_K": dict(kinds),
            "revision_lag_after_K_hours": {"max": round(max(lags_rev), 2), "median": round(median(lags_rev), 2)} if lags_rev else None,
            "false_finality": outcomes["REVISED_AFTER_K"] if pol != "B_FIRST_OBSERVED" else "NOT_A_FINALITY_CLAIM",
            "lookahead_failures_proven": outcomes["PROVEN_LOOKAHEAD"],
            "data_loss_sessions": undefined,
            "feature_latency_after_close_hours": {"median": round(median(latency), 2), "max": round(max(latency), 2)} if latency else None,
            "examples": dict(examples),
        }
    return results, per_session, {
        "rule": "L = maximum over daily-cadence sessions of (first live-rule-complete observation - session close); a descriptive UPPER bound of observed completion, not tuned on any outcome",
        "L_hours": round(L_hours, 3), "L_defining_session": L_key,
        "minimal_non_contradicted_lag_hours": round(L_min_noncontradicted, 3),
        "daily_cadence_sessions": len(basis),
        "complete_upper_bound_quantiles_h": quantiles([b["complete_upper_bound_h"] for b in basis]),
        "excluded_observation_limited_sessions": len(complete_lags) - len(basis),
        "basis": basis}


def quantiles(v):
    v = sorted(v)
    q = lambda p: round(v[min(len(v) - 1, int(p * (len(v) - 1)))], 2)
    return {"min": q(0), "p50": q(0.5), "p90": q(0.9), "max": q(1.0)}


def verdicts(results):
    out = {}
    for pol, r in results.items():
        if pol == "E_CONSERVATIVE_FIXED_LAG" and not r["lookahead_failures_proven"]:
            v, why = "NOT_ENOUGH_EVIDENCE", ("consistent in-sample only by construction (L is the in-sample maximum completion lag); no out-of-sample "
                                             "or pre-2026-07 publication evidence exists, so the lag cannot be validated for the history it would be applied to")
        elif r["lookahead_failures_proven"]:
            v, why = "UNSUPPORTED", f"{r['lookahead_failures_proven']} sessions where the bound value was provably not observable at K"
        elif pol == "B_FIRST_OBSERVED":
            v, why = "SUPPORTED_AS_VINTAGE_TIME_NOT_FINALITY", "K is an observed time, but the observed value is revised later in {} sessions; requires vintage-accurate storage".format(r["outcomes"].get("REVISED_AFTER_K", 0))
        elif r["false_finality"]:
            v, why = "UNSUPPORTED_AS_FINALITY", f"{r['false_finality']} sessions revised after K ({r['revision_kinds_after_K']})"
        else:
            v, why = "SUPPORTED", "no contradiction in evaluable sessions"
        if r["data_loss_sessions"] and r["coverage_share"] < 0.5:
            why += f"; drops {r['data_loss_sessions']} of {r['sessions_total']} sessions (all pre-capture history)"
        out[pol] = {"verdict": v, "why": why}
    return out


if __name__ == "__main__":
    ledger, sessions = load()
    out = {}
    for ref in ("LATEST_VINTAGE", "PRE_BACKFILL_VINTAGE"):
        results, per_session, e_basis = evaluate(ledger, sessions, ref)
        ver = verdicts(results)
        out[ref] = {"results": results, "verdicts": ver}
        write_json(OUT / f"policy_per_session_{ref}.json", {f"{a}|{d}": v for (a, d), v in sorted(per_session.items())})
        print("==", ref)
        for p, r in results.items():
            print(p, ver[p]["verdict"], r["coverage_defined"], r["outcomes"], r["revision_kinds_after_K"], r["feature_latency_after_close_hours"], r["revision_lag_after_K_hours"])
    out["E_lag_basis"] = e_basis
    write_json(OUT / "policy_results.json", out)
