"""Section 8: v1.1 (#1212 / candidate 4a968f5f) revalidation. Research only; no v1.1 artifact is created here.

Kept strictly apart from #1211: nothing here assigns publication or knowledge times.
"""
from __future__ import annotations

import hashlib
import json
import subprocess

from etf_lab_common import NYSE_CLOSED, PACK, REPO, WORK, live_table, num, pack_rows, write_json

OUT = WORK / "out"
CAND = REPO / "research/codex/intake/2026/09/codex-research-etf-history-pack-v1-1-row-integrity-v1.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validator_readback():
    import shutil, tempfile
    with tempfile.TemporaryDirectory() as tmp:
        dst = shutil.copytree(PACK, f"{tmp}/pack")
        p = subprocess.run(["python3", "scripts/validate_etf_flow_history.py"], cwd=dst, capture_output=True, text=True, timeout=120)
    return {"command": "python scripts/validate_etf_flow_history.py (on a temporary copy of the pack)", "exit_code": p.returncode,
            "output": (p.stdout + p.stderr).strip()[-300:],
            "note": "README/manifest claim STRUCTURE_VALIDATED with 0 null cells; the committed bytes fail the pack's own fail-closed validator; no CI job runs it"}


def main():
    cand = json.loads(CAND.read_text())
    rec = cand["recovery_evidence"]
    frozen = rec.get("malformed_rows") or []
    live = {a: {r["date"]: r for r in live_table(a)["date_rows"]} for a in ("BTC", "ETH")}
    live_tick = {a: live_table(a)["header_rows"][0][1:-1] for a in ("BTC", "ETH")}

    # ---- 1. v1 immutable readback: files vs committed CHECKSUMS / manifest, and git history of the data files
    checks = {}
    ck = {}
    for line in (PACK / "CHECKSUMS.sha256").read_text().splitlines():
        if line.strip():
            h, name = line.split(maxsplit=1)
            ck[name.strip().lstrip("*")] = h
    for p in sorted((PACK / "data").glob("*.csv")):
        rel = f"data/{p.name}"
        log = subprocess.run(["git", "log", "--format=%h %cI", "--", str(p.relative_to(REPO))], cwd=REPO, capture_output=True, text=True).stdout.split("\n")
        checks[rel] = {"sha256_now": sha(p), "checksums_file": ck.get(rel), "matches_checksums": sha(p) == ck.get(rel),
                       "bytes": p.stat().st_size, "git_commits_touching": [l for l in log if l]}

    # ---- 2. malformed rows: pack raw line vs frozen recovery rows vs live page (independent later vintage)
    mal = []
    for asset in ("BTC", "ETH"):
        rows = pack_rows(asset)
        header = list(rows[0].keys())
        for r in rows:
            if r.get("Total") not in (None, ""):
                continue
            day = r["date"]
            fr = next((f for f in frozen if f.get("asset") == asset and f.get("date") == day), None)
            lv = live[asset].get(day)
            live_vals = dict(zip(live_tick[asset], [num(c) for c in lv["cells"][1:-1]])) if lv else None
            live_total = num(lv["cells"][-1]) if lv else None
            pack_vals = [r[h] for h in header if h not in ("date",)]
            # deterministic mapping test: which single column, if removed from the true row, yields the shifted pack cells?
            truth_seq = [0.0 if (live_vals or {}).get(t) is None else live_vals[t] for t in live_tick[asset] if t in header] + [live_total]
            shifted = [float(v) for v in pack_vals if v not in ("", None)]
            drop_idx = [i for i in range(len(truth_seq)) if [round(x, 1) for x in truth_seq[:i] + truth_seq[i + 1:]] == [round(x, 1) for x in shifted]]
            fr_total = None if fr is None else fr.get("Total")
            fund_mismatch = [t for t in live_tick[asset] if fr is not None and t in fr and abs(float(fr[t]) - ((live_vals or {}).get(t) or 0.0)) > 0.05]
            mal.append({"asset": asset, "date": day, "pack_cells_nonempty": len(shifted), "schema_width": len(header) - 1,
                        "frozen_recovery_row_present": fr is not None, "frozen_total": fr_total, "live_total_2026_09_23": live_total,
                        "frozen_equals_live_total": (fr_total is not None and live_total is not None and abs(float(fr_total) - live_total) < 0.05),
                        "frozen_fund_values_equal_live_by_ticker": fr is not None and not fund_mismatch, "frozen_vs_live_fund_mismatches": fund_mismatch,
                        "v1_cells_only_candidate_drop_positions": drop_idx,
                        "mapping_from_v1_cells_alone_unique": len(drop_idx) == 1,
                        "mapping_from_keyed_source_deterministic": fr is not None and not fund_mismatch})

    # ---- 3. non-session rows
    ns = []
    for asset in ("BTC", "ETH"):
        for r in pack_rows(asset):
            if r["date"] in NYSE_CLOSED:
                vals = [float(v) for k, v in r.items() if k != "date" and v not in ("", None)]
                lv = live[asset].get(r["date"])
                ns.append({"asset": asset, "date": r["date"], "pack_all_zero": all(v == 0.0 for v in vals),
                           "live_row_present": lv is not None,
                           "live_fund_cells_all_dash": lv is not None and all(num(c) is None for c in lv["cells"][1:-1]),
                           "live_total_cell": lv["cells"][-1] if lv else None,
                           "live_owner_parse_would_keep_as_zero_flow_row": lv is not None and any(num(c) is not None for c in lv["cells"][1:])})

    # ---- 4. unaffected rows: pack == live for every non-malformed, non-closure session (zero-fill equivalence)
    diff, same = [], 0
    for asset in ("BTC", "ETH"):
        for r in pack_rows(asset):
            if r.get("Total") in (None, "") or r["date"] in NYSE_CLOSED:
                continue
            lv = live[asset].get(r["date"])
            if lv is None:
                diff.append({"asset": asset, "date": r["date"], "why": "NOT_ON_LIVE_PAGE"})
                continue
            lvv = dict(zip(live_tick[asset], [num(c) for c in lv["cells"][1:-1]]))
            ok = abs(float(r["Total"]) - num(lv["cells"][-1])) < 0.05 and all(
                abs(float(r[h]) - (lvv.get(h) or 0.0)) < 0.05 for h in r if h not in ("date", "Total"))
            extra = {t: v for t, v in lvv.items() if t not in r and v not in (None, 0.0)}
            if ok and not extra:
                same += 1
            else:
                diff.append({"asset": asset, "date": r["date"], "why": "VALUE_DIFF" if not ok else "NEW_COLUMN_NONZERO", "extra": extra})

    # ---- 5. non-session semantics prototype (research): what the closure rows do to W30 features in v1
    import sys
    sys.path.insert(0, str(REPO))
    from backtest_engine.w30_replay import build_etf_trailing
    sem = {}
    for asset in ("BTC", "ETH"):
        rows = [r for r in pack_rows(asset) if r.get("Total") not in (None, "")]
        def fmt(rs):
            return [{**{k: v for k, v in r.items() if k not in ("date", "Total")}, "date": r["date"], "total_usd_millions": r["Total"],
                     "not_before_session_close_utc": r["date"] + "T20:00:00Z", "publication_timestamp_verified": "False", "asset": asset,
                     "source": "V1", "method_id": "LAB"} for r in rs]
        v1 = {r["date"]: r for r in build_etf_trailing(fmt(rows), asset)}
        proto = {r["date"]: r for r in build_etf_trailing(fmt([r for r in rows if r["date"] not in NYSE_CLOSED]), asset)}
        closures = [d for d in v1 if d in NYSE_CLOSED]
        changed_windows = sum(1 for d in proto if any(v1[d][f"rolling_net_flow_{w}s_usd_millions"] != proto[d][f"rolling_net_flow_{w}s_usd_millions"] for w in (3, 5, 10, 20)))
        streak_resets = sum(1 for d in closures if v1[d]["signed_flow_streak_sessions"] == 0)
        changed_streak = sum(1 for d in proto if v1[d]["signed_flow_streak_sessions"] != proto[d]["signed_flow_streak_sessions"])
        sem[asset] = {"closure_rows_in_v1": len(closures), "closure_rows_emitted_as_zero_flow_feature_rows": sum(1 for d in closures if v1[d]["total_usd_millions"] == 0.0),
                      "closure_rows_reset_signed_streak": streak_resets,
                      "session_rows_with_different_N_session_sums_if_closures_excluded": changed_windows,
                      "session_rows_with_different_signed_streak_if_closures_excluded": changed_streak}

    result = {
        "contract": "ETF_V1_1_REVALIDATION_v1", "scope": "#1212 / candidate codex-research-etf-history-pack-v1-1-row-integrity-v1 (4a968f5f); no #1211 semantics",
        "source_export_hashes": {
            "candidate_claims": rec.get("source_exports"),
            "reverified_this_session": False,
            "why_not": "the Projects tool returns extracted text for these document uploads, not original bytes; byte-level sha256 cannot be recomputed from it. Content-level checks below use the text export and the independent live Farside vintage.",
            "content_check": "Etf btc.md read in full via project_read: 651-row JSON export, 11 Jan 2024..24 Jul 2026, '-' cells exported as 0.0; BTC 2025-09-19 row = IBIT 246.1, GBTC -23.5, Total 222.6 (matches the frozen recovery row)",
        },
        "v1_immutable_readback": checks,
        "v1_checksum_summary": {"files": len(checks), "matching": sum(1 for c in checks.values() if c["matches_checksums"]),
                                "mismatching": [k for k, c in checks.items() if not c["matches_checksums"]]},
        "malformed_rows": mal,
        "malformed_summary": {"count": len(mal), "btc": sum(1 for m in mal if m["asset"] == "BTC"), "eth": sum(1 for m in mal if m["asset"] == "ETH"),
                              "frozen_rows_present": sum(1 for m in mal if m["frozen_recovery_row_present"]),
                              "frozen_total_equals_live": sum(1 for m in mal if m["frozen_equals_live_total"]),
                              "frozen_funds_equal_live_by_ticker": sum(1 for m in mal if m["frozen_fund_values_equal_live_by_ticker"]),
                              "v1_cells_alone_give_unique_mapping": sum(1 for m in mal if m["mapping_from_v1_cells_alone_unique"]),
                              "keyed_source_mapping_deterministic": sum(1 for m in mal if m["mapping_from_keyed_source_deterministic"]),
                              "note": "a one-cell-short row cannot be repaired from its own cells (zero columns make the dropped position ambiguous); the repair must come from a keyed source (export JSON keys or live ticker header)"},
        "non_session_rows": ns,
        "non_session_summary": {"count": len(ns), "btc": sum(1 for n in ns if n["asset"] == "BTC"), "eth": sum(1 for n in ns if n["asset"] == "ETH"),
                                "all_zero_in_pack": sum(1 for n in ns if n["pack_all_zero"]),
                                "live_source_fund_cells_all_dash_total_0_0": sum(1 for n in ns if n["live_fund_cells_all_dash"] and n["live_total_cell"] == "0.0"),
                                "live_owner_parser_would_keep_as_zero_flow": sum(1 for n in ns if n["live_owner_parse_would_keep_as_zero_flow_row"]),
                                "closure_rows_listed_by_farside_after_2025_06_19": "none (2025-07-04 .. 2026-09-07 closures have no row on the live page)",
                                "last_date": max(n["date"] for n in ns)},
        "unaffected_rows": {"identical_to_live_vintage": same, "differences": diff[:20], "difference_count": len(diff)},
        "non_session_semantics_prototype_W30": sem,
        "pack_validator_on_committed_bytes": validator_readback(),
        "verdict": None,
    }
    ms = result["malformed_summary"]
    result["verdict"] = {
        "v1_1_still_needed": True,
        "reasons": [f"{ms['count']} malformed rows still in v1 ({ms['btc']} BTC, {ms['eth']} ETH); v1 bytes must stay immutable",
                    f"{result['non_session_summary']['count']} closure rows still exported as zero flow; the live source shows every fund as '-' with Total '0.0' for them (same shape as a pending row)",
                    "the non-session prototype shows closure rows change N-session sums and reset streaks in the production W30 feature builder"],
        "candidate_packet_consistent_with_fresh_evidence": ms["frozen_rows_present"] == ms["count"] and ms["frozen_total_equals_live"] == ms["count"] and ms["frozen_funds_equal_live_by_ticker"] == ms["count"],
    }
    write_json(OUT / "ETF_V1_1_REVALIDATION.json", result)
    print(json.dumps({k: result[k] for k in ("v1_checksum_summary", "malformed_summary", "non_session_summary", "non_session_semantics_prototype_W30", "verdict")}, indent=1))
    print("unaffected", result["unaffected_rows"]["identical_to_live_vintage"], result["unaffected_rows"]["difference_count"], result["unaffected_rows"]["differences"][:3])
    print(json.dumps(mal[:2]))


if __name__ == "__main__":
    main()
