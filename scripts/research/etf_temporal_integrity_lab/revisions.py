"""Sections 3 (derived fields) and 4 (revision taxonomy): per-session vintage chains from the raw ledger.

DATA REVISION  = a later vintage of the same session carries a different value (fund or total).
KNOWLEDGE-TIME DELAY = the session was not yet published / not yet complete when an attempt looked (no value change).
The two are counted separately and never merged.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from statistics import median

from etf_lab_common import WORK, is_session, iso, session_close_utc, ts, write_json

OUT = WORK / "out"
EPS = 0.05
ZERO_FILL_SOURCES = {"TRUTH_LAYER_HISTORY_PACK_v1"}  # '-' exported as 0.0: None and 0.0 indistinguishable
SETTLED = {"DAILY_SETTLED_ETF_CALIBRATION_v2", "SETTLED_REVERIFICATION_RECEIPT"}


def zero_filled(r):
    return r["observation_source"] in ZERO_FILL_SOURCES or (r["observation_source"] == "DATA_PING_FARSIDE_SUPPLEMENT" and r["value_scope"] == "FUND_LEVEL")


def funds(r):
    if not r["fund_header_set"] or r["fund_values"] is None:
        return None
    return dict(zip(r["fund_header_set"], r["fund_values"]))


def compare(a, b):
    """Classify the transition from earlier row a to later row b. Returns (kind|None, detail)."""
    fa, fb = funds(a), funds(b)
    zf = zero_filled(a) or zero_filled(b)
    ta, tb = a["reported_total"], b["reported_total"]
    total_delta = None if ta is None or tb is None else round(tb - ta, 4)
    comps = defaultdict(float)
    diffs = []
    added, removed = [], []
    if fa is not None and fb is not None:
        full = a["value_scope"] == "FUND_LEVEL" and b["value_scope"] == "FUND_LEVEL"
        added = [f for f in fb if f not in fa] if full else []
        removed = [f for f in fa if f not in fb] if full else []
        for f in fb:
            if f not in fa and f not in added:
                continue  # partial evidence: compare only funds present on both sides
            vb = fb[f]
            if f in added:
                if vb not in (None, 0.0):
                    comps["NEW_FUND_BACKFILL"] += vb
                    diffs.append({"fund": f, "from": "ABSENT_COLUMN", "to": vb})
                continue
            va = fa[f]
            # a 0.0 exported by a zero-filling source may stand for '-': equivalence only on that side
            if zero_filled(a) and va == 0.0 and vb is None:
                continue
            if zero_filled(b) and vb == 0.0 and va is None:
                continue
            if va is None and vb is None:
                continue
            if va is None and vb is not None:
                if vb != 0.0:
                    comps["LATE_FUND_VALUE"] += vb
                diffs.append({"fund": f, "from": None, "to": vb})
            elif va is not None and vb is None:
                comps["UNKNOWN_REVISION"] -= va
                diffs.append({"fund": f, "from": va, "to": None})
            elif abs(va - vb) > EPS:
                comps["SOURCE_CORRECTION"] += vb - va
                diffs.append({"fund": f, "from": va, "to": vb})
    total_changed = total_delta is not None and abs(total_delta) > EPS
    value_changed = total_changed or any(abs(v) > EPS for v in comps.values())
    detail = {"total_from": ta, "total_to": tb, "total_delta": total_delta, "fund_diffs": diffs[:6], "components": {k: round(v, 4) for k, v in comps.items()},
              "added_funds": added, "removed_funds": removed, "zero_fill_comparison": zf}
    if not value_changed:
        if added or removed:
            return "SCHEMA_EXTENSION", detail
        return None, detail
    if fa is None or fb is None:
        # total-only evidence on one side: attribute only if the fund-level side names the late fund
        known_late = a.get("notes") and a["notes"].get("ibit_not_reported") if isinstance(a.get("notes"), dict) else False
        return ("LATE_FUND_VALUE" if known_late else "UNKNOWN_REVISION"), detail
    explained = sum(comps.values())
    if total_changed and not comps:
        return "TOTAL_RECOMPUTE", detail
    if total_changed and abs(explained - total_delta) > 0.15:
        return "UNKNOWN_REVISION", detail
    kind = max(comps, key=lambda k: abs(comps[k]))
    return kind, detail


def build(ledger, attempts):
    by = defaultdict(list)
    for r in ledger:
        by[(r["asset"], r["session_date"])].append(r)
    sessions = []
    events = []
    for (asset, day), rows in sorted(by.items()):
        rows.sort(key=lambda r: (r["observed_at_utc"], r["observation_source"]))
        chain = [r for r in rows if not r.get("not_source_revision")]
        close = session_close_utc(day)
        realtime = [r for r in chain if r["observation_kind"] in ("REAL_TIME_CAPTURE", "MEDIATED_CAPTURE")]
        final = chain[-1]
        # --- revision chain (consecutive distinct vintages)
        transitions = []
        prev = None
        for r in chain:
            if prev is not None:
                kind, detail = compare(prev, r)
                if kind:
                    transitions.append({"kind": kind, "from_source": prev["observation_source"], "from_observed_at": prev["observed_at_utc"],
                                        "to_source": r["observation_source"], "to_observed_at": r["observed_at_utc"],
                                        "lag_after_first_observation_h": round((ts(r["observed_at_utc"]) - ts(chain[0]["observed_at_utc"])).total_seconds() / 3600, 2),
                                        "lag_after_session_close_h": round((ts(r["observed_at_utc"]) - close).total_seconds() / 3600, 2), **detail})
            prev = r
        value_transitions = [t for t in transitions if t["kind"] != "SCHEMA_EXTENSION"]
        # --- knowledge-time windows
        first = chain[0]
        first_rt = realtime[0] if realtime else None
        absent_before = [a for a in attempts if a.get("asset_ok", {}).get(asset) and ts(a["at"]) > close
                         and day not in a.get("sessions_seen", {}).get(asset, []) and a.get("window_min", {}).get(asset, "9") <= day
                         and (first_rt is None or ts(a["at"]) < ts(first_rt["observed_at_utc"]))]
        settled_absent = [a for a in attempts if a["lane"] == "SETTLED_DOUBLE_READ" and a.get("latest_session") and a["latest_session"] < day
                          and ts(a["at"]) > close and (first_rt is None or ts(a["at"]) < ts(first_rt["observed_at_utc"]))]
        last_absent = max([a["at"] for a in absent_before + settled_absent], default=None)

        def complete_live_rule(r):
            if r["fund_values"] is None or r["reported_total"] is None or r["parity"] is not True:
                return None
            return r["unknown_cell_count"] == 0 or set(r["unknown_funds"]) <= set(r.get("_structural_dash") or [])

        final_f = funds(final) or {}
        def complete_hindsight(r):
            f = funds(r)
            if f is None or r["reported_total"] is None:
                return None
            missing = [k for k, v in f.items() if v is None and final_f.get(k) not in (None, 0.0)]
            return not missing and abs((r["reported_total"] or 0) - (final["reported_total"] or 0)) <= EPS or (not missing and zero_filled(r))

        def same_as_final(r):
            k, _ = compare(r, final)
            return k is None or k == "SCHEMA_EXTENSION"

        rt_complete = [r for r in realtime if complete_hindsight(r)]
        rt_incomplete_before = [r for r in realtime if complete_hindsight(r) is False]
        settled_rows = [r for r in chain if r["observation_source"] in SETTLED]
        first_settled = settled_rows[0] if settled_rows else None
        # verified-final = settled observation equal to the latest vintage with no later differing observation
        vf = None
        for i, r in enumerate(chain):
            if r["observation_source"] in SETTLED and same_as_final(r) and all(same_as_final(x) for x in chain[i:]):
                vf = r
                break
        status = "OBSERVED" if realtime else ("LOWER_BOUND_ONLY" if chain else "UNKNOWN")
        s = {
            "asset": asset, "session_date": day, "is_nyse_session": is_session(day), "session_close_utc": iso(close),
            "observations": len(rows), "realtime_observations": len(realtime),
            "sources": sorted({r["observation_source"] for r in rows}),
            "first_observed_at_utc": first["observed_at_utc"], "first_observed_source": first["observation_source"], "first_observed_total": first["reported_total"],
            "first_realtime_observed_at_utc": first_rt["observed_at_utc"] if first_rt else None,
            "first_realtime_total": first_rt["reported_total"] if first_rt else None,
            "first_realtime_unknown_funds": first_rt["unknown_funds"] if first_rt else None,
            "first_realtime_lag_h": round((ts(first_rt["observed_at_utc"]) - close).total_seconds() / 3600, 2) if first_rt else None,
            "last_attempt_absent_before_first_observation_utc": last_absent,
            "later_observed_total": final["reported_total"], "later_observed_at_utc": final["observed_at_utc"], "later_observed_source": final["observation_source"],
            "revision_detected": bool(value_transitions), "schema_only_change_detected": any(t["kind"] == "SCHEMA_EXTENSION" for t in transitions),
            "revision_kinds": sorted({t["kind"] for t in value_transitions}),
            "revision_delta_total": round((final["reported_total"] or 0) - (first["reported_total"] or 0), 4) if first["reported_total"] is not None and final["reported_total"] is not None else None,
            "first_complete_observation_at_utc": rt_complete[0]["observed_at_utc"] if rt_complete else None,
            "last_incomplete_observation_at_utc": rt_incomplete_before[-1]["observed_at_utc"] if rt_incomplete_before else None,
            "first_settled_observation_at_utc": first_settled["observed_at_utc"] if first_settled else None,
            "first_settled_verification_completed_at_utc": first_settled["verification_completed_at_utc"] if first_settled else None,
            "first_settled_unknown_funds": first_settled["unknown_funds"] if first_settled else None,
            "first_settled_equals_latest_vintage": same_as_final(first_settled) if first_settled else None,
            "first_verified_final_observation_at_utc": (vf["verification_completed_at_utc"] or vf["observed_at_utc"]) if vf else None,
            "knowledge_time_status": status,
            "transitions": transitions,
            "not_source_revision_rows": [{"observed_at": r["observed_at_utc"], "total": r["reported_total"], "why": r["not_source_revision"], "path": r["source_evidence_path"]} for r in rows if r.get("not_source_revision")],
        }
        sessions.append(s)
        for t in value_transitions:
            events.append({"asset": asset, "session_date": day, **{k: t[k] for k in ("kind", "from_source", "to_source", "from_observed_at", "to_observed_at", "total_from", "total_to", "total_delta", "lag_after_first_observation_h", "lag_after_session_close_h", "components")}})
    return sessions, events


def attempt_index(attempts, ledger):
    """Enrich FLO attempts with per-asset success and window bounds (only assets that parsed)."""
    for a in attempts:
        if a["lane"] != "FLO_OWNER_SNAPSHOT":
            continue
        errs = {e["asset"] for e in (a.get("errors") or [])}
        seen = a.get("sessions_seen") or {}
        a["asset_ok"] = {x: (x not in errs and bool(seen.get(x))) for x in ("BTC", "ETH")}
        a["window_min"] = {x: min(v) for x, v in seen.items() if v}
    return attempts


if __name__ == "__main__":
    ledger = [json.loads(l) for l in (OUT / "ledger_raw.jsonl").read_text().splitlines()]
    attempts = attempt_index(json.loads((OUT / "capture_attempts.json").read_text()), ledger)
    sessions, events = build(ledger, attempts)
    write_json(OUT / "sessions.json", sessions)
    write_json(OUT / "revision_events.json", events)
    print(len(sessions), Counter(s["knowledge_time_status"] for s in sessions))
    print(Counter((e["asset"], e["kind"], e["to_source"]) for e in events))
