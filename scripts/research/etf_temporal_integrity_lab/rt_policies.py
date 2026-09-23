"""Section 6: E1X right-truncation per knowledge-time policy, using the production E1X harness unchanged.

For each policy P the feature output of session s is CLAIMED at K_P(s). Input records carry their EVIDENCED
availability: every real-time vintage from the ledger at its observed time (first = VALUE, later = REVISION);
history-only sessions carry no evidence, so they are placed at K_P(s) and counted as UNVERIFIABLE (never guessed).
Two runs per policy and feature family:
  * TRUNCATE : records known after t removed (standard E1X)
  * POISON   : future VALUE records kept but poisoned (1e6), future REVISIONs removed -> isolates causal leakage
Features: production W30 build_etf_trailing (total, 1/3/5/10/20-session sums, signed streak, acceleration, reversal,
issuer concentration), production W30 build_etf_divergence (BTC vs ETH relative flow), and the truth-layer pack
builder (pandas: sums/means/z-score/streaks/cumulative). ETF absorption is not re-run (see report).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import timedelta

from etf_lab_common import REPO, WORK, iso, is_session, next_session, pack_rows, session_close_utc, session_open_utc, ts, write_json

sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location("e1x_harness", REPO / "scripts/experiments/strategy_factor_leakage_e1_production.py")
H = importlib.util.module_from_spec(spec)
sys.modules["e1x_harness"] = H
spec.loader.exec_module(H)

from policies import BACKFILL_CUT, complete_live, structural_dash_index  # noqa: E402
from revisions import SETTLED, compare  # noqa: E402

OUT = WORK / "out"
REALTIME = ("REAL_TIME_CAPTURE", "MEDIATED_CAPTURE")
POLICIES = ["A_SESSION_CLOSE", "B_FIRST_OBSERVED", "C_FIRST_COMPLETE_OBSERVED", "D_FIRST_VERIFIED_FINAL_OBSERVED",
            "E_CONSERVATIVE_FIXED_LAG", "F_NEXT_TRADING_SESSION"]
POISON = 1.0e6
PACK_COLS = {a: [k for k in pack_rows(a)[0].keys() if k not in ("date",)] for a in ("BTC", "ETH")}  # funds + Total


def load():
    ledger = [json.loads(l) for l in (OUT / "ledger_raw.jsonl").read_text().splitlines()]
    pol = json.loads((OUT / "policy_results.json").read_text())
    return ledger, pol["E_lag_basis"]["L_hours"]


def chains(ledger):
    by = defaultdict(list)
    for r in ledger:
        if not r.get("not_source_revision") and r["session_date"] <= "2026-09-22":
            by[(r["asset"], r["session_date"])].append(r)
    # v1 semantics (not v1.1): the 11 malformed pack rows are excluded exactly as the E1X adapter does; non-session
    # zero rows stay in (their repair belongs to #1212 / v1.1 and is not mixed into this #1211 experiment)
    malformed = {(r["asset"], r["session_date"]) for r in ledger if r.get("not_source_revision", "") and "MALFORMED" in r["not_source_revision"]}
    for k in malformed:
        by.pop(k, None)
    for rows in by.values():
        rows.sort(key=lambda r: (r["observed_at_utc"], r["observation_source"]))
    return by


def declared_K(policy, key, rows, idx, L):
    day = key[1]
    close = session_close_utc(day)
    rt = [r for r in rows if r["observation_kind"] in REALTIME]
    if policy == "A_SESSION_CLOSE":
        return close
    if policy == "E_CONSERVATIVE_FIXED_LAG":
        return close + timedelta(hours=L)
    if policy == "F_NEXT_TRADING_SESSION":
        return session_open_utc(next_session(day))
    if not rt:
        return None
    if policy == "B_FIRST_OBSERVED":
        return ts(rt[0]["observed_at_utc"])
    if policy == "C_FIRST_COMPLETE_OBSERVED":
        c = [r for r in rt if complete_live(r, idx) is True]
        return ts(c[0]["observed_at_utc"]) if c else None
    if policy == "D_FIRST_VERIFIED_FINAL_OBSERVED":
        s = [r for r in rt if r["observation_source"] in SETTLED]
        return ts(s[0]["verification_completed_at_utc"] or s[0]["observed_at_utc"]) if s else None


def fund_payload(asset, r, K):
    headers = r["fund_header_set"] or []
    vals = dict(zip(headers, r["fund_values"] or []))
    cols = [c for c in PACK_COLS[asset] if c != "Total"] + (["MSSE"] if asset == "ETH" else [])
    row = {c: ("" if vals.get(c) is None else vals[c]) for c in cols}
    row.update({"date": r["session_date"], "total_usd_millions": r["reported_total"], "not_before_session_close_utc": iso(K),
                "publication_timestamp_verified": "False", "asset": asset, "source": r["observation_source"], "method_id": "ETF_LAB_RT"})
    return row


def build_records(policy, ledger_by, idx, L, reference):
    """Records with evidenced availability; value vintages restricted by reference (pre-backfill or latest)."""
    records, unverifiable, claimed, dropped = [], 0, {}, 0
    for key, rows in sorted(ledger_by.items()):
        K = declared_K(policy, key, rows, idx, L)
        if K is None:
            dropped += 1
            continue
        claimed[key] = K
        rt = [r for r in rows if r["observation_kind"] in REALTIME]
        if rt:
            # evidenced session: every vintage (real-time and later retrospective reads) at its observed time
            rt = [r for r in rows if r["observed_at_utc"] >= rt[0]["observed_at_utc"]]
            if reference == "PRE_BACKFILL_VINTAGE":
                rt = [r for r in rt if r["observed_at_utc"] <= BACKFILL_CUT] or rt[:1]
        if rt:
            prev = None
            for r in rt:
                if prev is not None:
                    k, _ = compare(prev, r)
                    if k is None or k == "SCHEMA_EXTENSION":
                        continue
                records.append(H.Record(ts(r["observed_at_utc"]), "VALUE" if prev is None else "REVISION", f"{key[0]}|{key[1]}", fund_payload(key[0], r, K)))
                prev = r
        else:
            unverifiable += 1
            hist = next((r for r in rows if r["observation_source"] == "TRUTH_LAYER_HISTORY_PACK_v1"), rows[-1])
            records.append(H.Record(K, "VALUE", f"{key[0]}|{key[1]}", fund_payload(key[0], hist, K)))
    return records, {"sessions_claimed": len(claimed), "sessions_dropped_by_policy": dropped, "history_sessions_unverifiable": unverifiable}


def compute_w30(records):
    w30 = H._w30()
    latest = {}
    for rec in sorted(records, key=lambda r: (r.available_at, r.kind)):
        latest[rec.key] = rec
    by_asset = defaultdict(list)
    for rec in latest.values():
        by_asset[rec.payload["asset"]].append(dict(rec.payload))
    out = {}
    totals = {}
    for asset, rows in by_asset.items():
        rows.sort(key=lambda r: r["date"])
        for row in w30.build_etf_trailing(rows, asset):
            f = {k: v for k, v in row.items() if k not in ("asset", "date", "not_before_session_close_utc", "feature_knowledge_available_at_utc", "feature_method_id")}
            out[f"{asset}|{row['date']}"] = H.Output(ts(row["feature_knowledge_available_at_utc"]), f)
        totals[asset] = {r["date"]: r for r in rows}
    if "BTC" in totals and "ETH" in totals:
        b = [totals["BTC"][d] for d in sorted(totals["BTC"])]
        e = [totals["ETH"][d] for d in sorted(totals["ETH"])]
        for row in w30.build_etf_divergence(b, e):
            d = row["date"]
            k = max(ts(totals["BTC"][d]["not_before_session_close_utc"]), ts(totals["ETH"][d]["not_before_session_close_utc"]))
            out[f"DIV|{d}"] = H.Output(k, {x: row[x] for x in ("total_usd_millions_btc", "total_usd_millions_eth", "btc_minus_eth_flow_usd_millions", "opposite_sign_divergence")})
    return out


def cummax_claims(out):
    """Feature-level knowledge time = max over every input session up to and including the row (trailing windows)."""
    fixed = {}
    for prefix in ("BTC", "ETH", "DIV"):
        run = None
        for key in sorted(k for k in out if k.startswith(prefix + "|")):
            o = out[key]
            run = o.claimed_available_at if run is None else max(run, o.claimed_available_at)
            fixed[key] = H.Output(run, o.fields)
    # divergence depends on both assets' trailing inputs only through same-date totals; cummax per prefix is conservative
    return fixed


def compute_w30_cummax(records):
    return cummax_claims(compute_w30(records))


def compute_pack_builder(records):
    raw_records = []
    claim = {}
    for rec in records:
        p = rec.payload
        raw = {c: ("" if p.get(c, "") in ("", None) else p[c]) for c in PACK_COLS[p["asset"]] if c != "Total"}
        raw = {c: (0.0 if v == "" else v) for c, v in raw.items()}  # the pack format zero-fills '-' (documented v1 semantics)
        raw["date"] = p["date"]
        raw["Total"] = p["total_usd_millions"]
        raw = {"date": raw.pop("date"), **raw}
        raw_records.append(H.Record(rec.available_at, rec.kind, rec.key, (p["asset"], raw)))
        claim[rec.key] = ts(p["not_before_session_close_utc"])
    for a in ("BTC", "ETH"):
        H.ETF_HEADERS[a] = ["date", *PACK_COLS[a]]
    out = H.compute_truth_layer_etf_features(raw_records)
    return {k: H.Output(claim.get(k, v.claimed_available_at), v.fields) for k, v in out.items()}


def poison(rec):
    if rec.kind == "REVISION":
        return None
    p = dict(rec.payload)
    p["total_usd_millions"] = POISON
    return replace(rec, payload=p)


def poison_pack(rec):
    return poison(rec)


def run_case(policy, family, records, meta, mode, reference):
    compute = {"W30_TRAILING_AND_DIVERGENCE": compute_w30, "W30_CUMMAX_FEATURE_CLAIM": compute_w30_cummax,
               "TRUTH_LAYER_PACK_BUILDER": compute_pack_builder}[family]
    H.MAX_MINIMIZATIONS_PER_CASE = 80 if family.startswith("W30") else 4
    rt_claims = sorted({r.available_at for r in records if r.payload["source"] != "TRUTH_LAYER_HISTORY_PACK_v1"})
    case = H.RightTruncationCase(
        case_id=f"RT-ETF-{policy}-{family}-{mode}-{reference}", owner="ETF temporal integrity lab (research)",
        production_path="backtest_engine/w30_replay.py" if family.startswith("W30") else H.ETF_FEATURE_SCRIPT,
        production_callable="build_etf_trailing + build_etf_divergence" if family.startswith("W30") else "main",
        description=f"{family} with knowledge time declared by {policy}; records at evidenced availability ({reference})",
        records=records, compute=compute, max_targets=24 if family.startswith("W30") else 8,
        targets=(sorted({ts(r.payload["not_before_session_close_utc"]) for r in records if r.payload["source"] != "TRUTH_LAYER_HISTORY_PACK_v1"}
                        | {r.available_at for r in records if r.kind == "REVISION"})
                 if family.startswith("W30") else "PER_OUTPUT"),
        censor_future=poison if mode == "POISON" else None,
        knowledge_time_rule=policy, data_binding=meta)
    return H.run_right_truncation(case)


PER_SESSION = {}


def attribute(result, policy, reference):
    """Split each minimised mismatch into PROVEN / VINTAGE / OBSERVATION_LIMITED using the policy evidence table."""
    table = PER_SESSION.setdefault(reference, json.loads((OUT / f"policy_per_session_{reference}.json").read_text()))
    counts = Counter()
    for m in result["mismatches"]:
        cul = (m.get("minimization") or {}).get("first_contaminating_record")
        if not cul:
            counts["NOT_MINIMIZED"] += 1
            continue
        if cul["kind"] == "REVISION":
            counts["SOURCE_VINTAGE_RISK"] += 1
        elif policy[0] in "BCD":
            own = m["output_key"].split("|")[0] in ("BTC", "ETH") and cul["key"] == m["output_key"]
            counts["TRUE_FUTURE_LEAKAGE_OWN_ROW" if own else "TRUE_FUTURE_LEAKAGE_FEATURE_CLAIM_NON_MONOTONE"] += 1
        else:
            o = (table.get(cul["key"]) or {}).get(policy, {}).get("outcome")
            counts["TRUE_FUTURE_LEAKAGE_PROVEN" if o == "PROVEN_LOOKAHEAD" else "OBSERVATION_LIMITED_UNKNOWN"] += 1
    return dict(counts)


def classify(result, meta, family, policy, attribution=None):
    if attribution is not None and result["observed"] == "FAIL":
        a = attribution
        if any(k.startswith("TRUE_FUTURE_LEAKAGE") for k in a):
            return "TRUE_FUTURE_LEAKAGE"
        if a.get("SOURCE_VINTAGE_RISK"):
            return "SOURCE_VINTAGE_RISK"
        return "UNKNOWN"
    if result["observed"] == "NOT_RUN":
        return "UNKNOWN"
    if result["observed"] == "PASS":
        if meta["sessions_dropped_by_policy"] > 600:
            return "INSUFFICIENT_HISTORY"
        return "PASS"
    cls = set(result["classifications"])
    if "TRUE_FUTURE_LEAKAGE" in cls:
        return "TRUE_FUTURE_LEAKAGE"
    if "SOURCE_VINTAGE_RISK" in cls:
        return "SOURCE_VINTAGE_RISK"
    if cls & {"NOT_MINIMIZED"}:
        return "UNKNOWN"
    return sorted(cls)[0]


def main():
    ledger, L = load()
    idx = structural_dash_index(ledger)
    by = chains(ledger)
    results = []
    for reference in ("PRE_BACKFILL_VINTAGE", "LATEST_VINTAGE"):
        for policy in POLICIES:
            records, meta = build_records(policy, by, idx, L, reference)
            for family in ("W30_TRAILING_AND_DIVERGENCE", "W30_CUMMAX_FEATURE_CLAIM", "TRUTH_LAYER_PACK_BUILDER"):
                for mode in ("TRUNCATE", "POISON"):
                    if family != "W30_TRAILING_AND_DIVERGENCE" and mode == "POISON" and reference == "LATEST_VINTAGE":
                        continue
                    if family == "TRUTH_LAYER_PACK_BUILDER" and mode == "POISON":
                        continue
                    res = run_case(policy, family, records, meta, mode, reference)
                    attribution = attribute(res, policy, reference)
                    outcome = classify(res, meta, family, policy, attribution)
                    slim = {k: res[k] for k in ("case_id", "records", "record_kinds", "outputs_full", "targets_tested", "output_comparisons", "mismatch_count",
                                                 "minimized_mismatch_count", "contaminating_lead_seconds", "observed", "classifications")}
                    slim["first_mismatches"] = [{k: m.get(k) for k in ("target_utc", "output_key", "claimed_available_at_utc", "field_difference_count", "classification")} |
                                                {"first_contaminating_record": (m.get("minimization") or {}).get("first_contaminating_record"),
                                                 "fields": [f["field"] for f in m["field_differences"][:5]]} for m in res["mismatches"][:5]]
                    results.append({"reference": reference, "policy": policy, "feature_family": family, "mode": mode, "outcome": outcome,
                                    "mismatch_attribution": attribution, **meta, "harness": slim})
                    print(reference, policy, family, mode, outcome, res["mismatch_count"], attribution, meta["sessions_dropped_by_policy"])
    write_json(OUT / "rt_results.json", results)


if __name__ == "__main__":
    main()
