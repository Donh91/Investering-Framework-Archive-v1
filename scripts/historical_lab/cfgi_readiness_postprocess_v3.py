#!/usr/bin/env python3
from __future__ import annotations

import bisect
import gzip
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("06_RESEARCH_LAB/historical_altseason_pullback_v1")
ART = ROOT / "artifacts"
CONFIG = ROOT / "config.json"

ALIGNMENT_POLICY = "LAST_KNOWN_WITHIN_DECLARED_1H_CADENCE_NO_LOOKAHEAD"
MAX_AGE_SECONDS = 3600


def dt(value: str) -> datetime:
    x = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if x.tzinfo is None:
        x = x.replace(tzinfo=timezone.utc)
    return x.astimezone(timezone.utc)


def iso(x: datetime) -> str:
    return x.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def read_jsonl_gz(path: Path) -> list[dict]:
    rows = []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def requested_value(row: dict | None, field: str):
    if row is None:
        return None
    if field == "score":
        return row.get("score")
    return row.get(f"component_{field}")


def event_id(ev: dict) -> str:
    return str(ev.get("window_id") or ev.get("episode_id") or ev.get("control_id") or f"{ev.get('kind','UNKNOWN')}:{ev.get('event_utc','UNKNOWN')}")


def max_constant_run(values: list[tuple[int, object]]) -> int:
    best = 0
    run = 0
    prev_h = None
    prev_v = object()
    for hour, value in values:
        if value is None:
            run = 0
            prev_h = None
            prev_v = object()
            continue
        if prev_h is not None and hour == prev_h + 1 and value == prev_v:
            run += 1
        else:
            run = 1
        best = max(best, run)
        prev_h, prev_v = hour, value
    return best


def build(cfg: dict, events: list[dict], raw_rows: list[dict]) -> tuple[dict, list[dict], dict]:
    ccfg = cfg["cfgi"]
    pre = int(ccfg["pre_event_hours"])
    post = int(ccfg["post_event_hours"])
    fields = list(ccfg["fields"])
    symbols = list(ccfg["symbols"])

    by_symbol: dict[str, list[tuple[datetime, dict]]] = {s: [] for s in symbols}
    exact_lookup = {}
    duplicates = []
    malformed = []
    for row in raw_rows:
        sym = str(row.get("symbol") or "")
        ts = row.get("timestamp")
        if sym not in by_symbol or not ts:
            if sym or ts:
                malformed.append({"symbol": sym or None, "timestamp": ts})
            continue
        t = dt(str(ts))
        key = (sym, iso(t))
        if key in exact_lookup:
            duplicates.append({"symbol": sym, "timestamp": iso(t)})
        exact_lookup[key] = row
        by_symbol[sym].append((t, row))
    for sym in symbols:
        by_symbol[sym].sort(key=lambda x: x[0])

    times = {s: [x[0] for x in by_symbol[s]] for s in symbols}
    path_rows = []
    per_sf = defaultdict(lambda: {"expected": 0, "exact": 0, "asof": 0, "non_null": 0})
    stale = defaultdict(list)
    per_event = {}
    non_hour_events = []
    future_read_violations = []
    age_violations = []
    row_reuse_counts = defaultdict(int)

    for ev in events:
        t = dt(ev["event_utc"])
        eid = event_id(ev)
        if any((t.minute, t.second, t.microsecond)):
            non_hour_events.append({"event_id": eid, "event_utc": iso(t)})
        ev_exp = ev_exact = ev_asof = 0
        for rh in range(-pre, post + 1):
            expected = t + timedelta(hours=rh)
            expected_ts = iso(expected)
            for sym in symbols:
                exact = exact_lookup.get((sym, expected_ts))
                selected = None
                source = "MISSING"
                if exact is not None:
                    selected = exact
                    source = "EXACT_TIMESTAMP"
                else:
                    arr = times[sym]
                    idx = bisect.bisect_right(arr, expected) - 1
                    if idx >= 0:
                        cand_t, cand_row = by_symbol[sym][idx]
                        age = (expected - cand_t).total_seconds()
                        if 0 <= age < MAX_AGE_SECONDS:
                            selected = cand_row
                            source = "ASOF_PREVIOUS_WITHIN_1H"
                obs_t = None if selected is None else dt(str(selected["timestamp"]))
                age_seconds = None if obs_t is None else int((expected - obs_t).total_seconds())
                lookahead_seconds = 0 if obs_t is None or obs_t <= expected else int((obs_t - expected).total_seconds())
                if lookahead_seconds:
                    future_read_violations.append({"event_id": eid, "symbol": sym, "expected": expected_ts, "observed": iso(obs_t), "lookahead_seconds": lookahead_seconds})
                if age_seconds is not None and not (0 <= age_seconds < MAX_AGE_SECONDS):
                    age_violations.append({"event_id": eid, "symbol": sym, "expected": expected_ts, "observed": iso(obs_t), "age_seconds": age_seconds})
                if selected is not None:
                    row_reuse_counts[(sym, iso(obs_t))] += 1
                values = {field: requested_value(selected, field) for field in fields}
                rec = {
                    "event_id": eid,
                    "kind": ev.get("kind"),
                    "event_utc": iso(t),
                    "relative_hour": rh,
                    "symbol": sym,
                    "expected_timestamp_utc": expected_ts,
                    "observed_exact_hour": exact is not None,
                    "observed_asof_available": selected is not None,
                    "observed_timestamp_utc": None if obs_t is None else iso(obs_t),
                    "availability_age_seconds": age_seconds,
                    "lookahead_seconds": lookahead_seconds,
                    "alignment_policy": ALIGNMENT_POLICY if selected is not None else "MISSING_NO_VALID_PRIOR_OBSERVATION_WITHIN_1H",
                    "alignment_source": source,
                    "classification": None if selected is None else selected.get("classification"),
                    "real_price": None if selected is None else selected.get("real_price"),
                    "fields": values,
                }
                path_rows.append(rec)
                ev_exp += 1
                ev_exact += int(exact is not None)
                ev_asof += int(selected is not None)
                for field in fields:
                    x = per_sf[(sym, field)]
                    x["expected"] += 1
                    x["exact"] += int(exact is not None)
                    x["asof"] += int(selected is not None)
                    x["non_null"] += int(values[field] is not None)
                    stale[(eid, sym, field)].append((rh, values[field]))
        per_event[eid] = {
            "kind": ev.get("kind"),
            "event_utc": iso(t),
            "expected_symbol_hours": ev_exp,
            "exact_timestamp_symbol_hours": ev_exact,
            "asof_available_symbol_hours": ev_asof,
            "asof_coverage_ratio": 0.0 if not ev_exp else ev_asof / ev_exp,
        }

    field_rows = []
    symbol_summary = {}
    for sym in symbols:
        sym_expected = sym_exact = sym_asof = 0
        for field in fields:
            x = per_sf[(sym, field)]
            max_run = 0
            for ev in events:
                max_run = max(max_run, max_constant_run(stale[(event_id(ev), sym, field)]))
            exp = x["expected"]
            ex = x["exact"]
            av = x["asof"]
            nn = x["non_null"]
            field_rows.append({
                "symbol": sym,
                "field": field,
                "expected_slots": exp,
                "exact_timestamp_slots": ex,
                "asof_available_slots": av,
                "non_null_slots": nn,
                "exact_timestamp_coverage_ratio": None if not exp else ex / exp,
                "asof_coverage_ratio": None if not exp else av / exp,
                "field_coverage_ratio": None if not exp else nn / exp,
                "missing_ratio": None if not exp else 1 - (nn / exp),
                "max_constant_run_hours": max_run,
                "staleness_interpretation": "DIAGNOSTIC_ONLY_NO_HARD_THRESHOLD",
            })
            sym_expected = max(sym_expected, exp)
            sym_exact = max(sym_exact, ex)
            sym_asof = max(sym_asof, av)
        symbol_summary[sym] = {
            "expected_slots": sym_expected,
            "exact_timestamp_slots": sym_exact,
            "asof_available_slots": sym_asof,
            "asof_coverage_ratio": None if not sym_expected else sym_asof / sym_expected,
        }

    expected_all = len(events) * (pre + post + 1) * len(symbols)
    exact_all = sum(1 for r in path_rows if r["observed_exact_hour"])
    asof_all = sum(1 for r in path_rows if r["observed_asof_available"])
    reused = [{"symbol": k[0], "timestamp": k[1], "use_count": v} for k, v in row_reuse_counts.items() if v > 1]
    coverage = {
        "contract": "CFGI_FIELD_COVERAGE_v3",
        "time_alignment_contract": "CFGI_ASOF_1H_NO_LOOKAHEAD_v1",
        "exact_relative_hour_scaffold": True,
        "alignment_policy": ALIGNMENT_POLICY,
        "max_observation_age_seconds_exclusive": MAX_AGE_SECONDS,
        "pre_event_hours": pre,
        "post_event_hours": post,
        "symbols": symbols,
        "fields": fields,
        "event_count": len(events),
        "expected_symbol_hours": expected_all,
        "exact_timestamp_symbol_hours": exact_all,
        "asof_available_symbol_hours": asof_all,
        "exact_timestamp_coverage_ratio": None if not expected_all else exact_all / expected_all,
        "asof_coverage_ratio": None if not expected_all else asof_all / expected_all,
        "symbol_coverage": symbol_summary,
        "field_coverage": field_rows,
        "event_coverage": per_event,
        "diagnostics": {
            "duplicate_symbol_timestamp_keys": duplicates,
            "malformed_or_unrequested_rows": malformed,
            "non_hour_aligned_events": non_hour_events,
            "future_read_violations": future_read_violations,
            "age_window_violations": age_violations,
            "raw_rows_reused_across_multiple_slots": reused,
            "no_silent_fallback": True,
            "no_interpolation": True,
            "no_forward_fill_beyond_declared_1h_cadence": True,
            "no_lookahead": len(future_read_violations) == 0,
            "staleness_is_measured_not_thresholded": True,
        },
    }
    structural = {
        "expected": expected_all,
        "exact": exact_all,
        "asof": asof_all,
        "duplicates": duplicates,
        "malformed": malformed,
        "non_hour_events": non_hour_events,
        "future": future_read_violations,
        "age": age_violations,
        "reused": reused,
        "symbol_summary": symbol_summary,
    }
    return coverage, path_rows, structural


def build_manifest(cfg: dict, billing: dict, coverage: dict, structural: dict) -> dict:
    auth = cfg["authority"]
    ccfg = cfg["cfgi"]
    readiness = cfg["readiness"]
    blockers = []
    warnings = []
    if structural["duplicates"]:
        blockers.append("CFGI_DUPLICATE_SYMBOL_TIMESTAMP_KEYS")
    if structural["non_hour_events"]:
        blockers.append("CFGI_EVENT_TIMESTAMPS_NOT_HOUR_ALIGNED")
    if structural["future"]:
        blockers.append("CFGI_LOOKAHEAD_VIOLATION")
    if structural["age"]:
        blockers.append("CFGI_ASOF_AGE_WINDOW_VIOLATION")
    if structural["reused"]:
        blockers.append("CFGI_RAW_ROW_REUSED_ACROSS_MULTIPLE_EVENT_SLOTS")
    for sym, x in structural["symbol_summary"].items():
        if int(x.get("asof_available_slots") or 0) == 0:
            blockers.append(f"CFGI_REQUIRED_SYMBOL_ZERO_ASOF_COVERAGE:{sym}")
        elif int(x["asof_available_slots"]) < int(x["expected_slots"]):
            warnings.append(f"CFGI_ASOF_MISSINGNESS:{sym}:{x['expected_slots'] - x['asof_available_slots']}/{x['expected_slots']}")
    for row in coverage["field_coverage"]:
        if row["non_null_slots"] == 0:
            warnings.append(f"CFGI_ZERO_FIELD_COVERAGE:{row['symbol']}.{row['field']}")
        elif row["non_null_slots"] < row["expected_slots"]:
            warnings.append(f"CFGI_FIELD_MISSINGNESS:{row['symbol']}.{row['field']}:{1 - row['non_null_slots'] / row['expected_slots']:.6f}")
    if billing.get("status") != "PASS":
        blockers.append(f"CFGI_BILLING_STATUS:{billing.get('status','MISSING')}")
    if billing.get("expected_worst_case_credits") is None or int(billing["expected_worst_case_credits"]) > int(ccfg["expected_credit_hard_cap"]):
        blockers.append("CFGI_CURRENT_BILLING_HARD_CAP_FAIL")
    remaining = billing.get("final_credits_remaining")
    if remaining is None or int(remaining) < int(ccfg["minimum_credits_reserve"]):
        blockers.append("CFGI_MINIMUM_RESERVE_BREACHED")
    expected_auth = {"research_only": True, "portfolio_execution": False, "canonical_market_state": False, "automatic_rule_changes": False, "promotion_requires_separate_review": True}
    for k, v in expected_auth.items():
        if auth.get(k) is not v:
            blockers.append(f"AUTHORITY_INVALID:{k}")

    artifact_state = {}
    required = list(readiness["free_stage_required_artifacts"]) + list(readiness["cfgi_stage_required_artifacts"])
    for name in sorted(set(required)):
        p = ART / name
        ok = p.exists() and p.stat().st_size > 0
        artifact_state[name] = {"exists": ok, "bytes": p.stat().st_size if ok else 0, "sha256": sha256(p) if ok else None}
        if not ok:
            blockers.append(f"MISSING_ARTIFACT:{name}")
    for name in ["CFGI_EVENT_PATHS.jsonl.gz", "CFGI_FIELD_COVERAGE.json"]:
        p = ART / name
        if p.exists() and p.stat().st_size > 0:
            artifact_state[name] = {"exists": True, "bytes": p.stat().st_size, "sha256": sha256(p)}

    return {
        "contract": "RESEARCH_READINESS_MANIFEST_v3",
        "repo_commit_identity": git_head(),
        "config_contract_version": cfg.get("contract"),
        "artifact_state": artifact_state,
        "time_integrity_required": {
            "strict_timestamp_lags": cfg["time_integrity"]["strict_timestamp_lags"],
            "cross_window_lags_forbidden": cfg["time_integrity"]["cross_window_lags_forbidden"],
            "max_continuity_gap_hours": cfg["time_integrity"]["max_continuity_gap_hours"],
        },
        "cfgi": {
            "billing_status": billing.get("status"),
            "current_actual_credits_used_from_headers": billing.get("actual_credits_used_from_headers"),
            "final_credits_remaining": billing.get("final_credits_remaining"),
            "hard_cap": ccfg["expected_credit_hard_cap"],
            "minimum_reserve": ccfg["minimum_credits_reserve"],
            "event_count": coverage["event_count"],
            "expected_symbol_hours": coverage["expected_symbol_hours"],
            "exact_timestamp_symbol_hours": coverage["exact_timestamp_symbol_hours"],
            "asof_available_symbol_hours": coverage["asof_available_symbol_hours"],
            "missing_asof_symbol_hours": coverage["expected_symbol_hours"] - coverage["asof_available_symbol_hours"],
            "exact_timestamp_coverage_ratio": coverage["exact_timestamp_coverage_ratio"],
            "asof_coverage_ratio": coverage["asof_coverage_ratio"],
            "symbol_coverage": coverage["symbol_coverage"],
            "alignment_policy": ALIGNMENT_POLICY,
            "time_alignment_contract": "CFGI_ASOF_1H_NO_LOOKAHEAD_v1",
            "max_observation_age_seconds_exclusive": MAX_AGE_SECONDS,
            "no_lookahead": coverage["diagnostics"]["no_lookahead"],
            "missingness_policy": "EXPLICIT_MISSING_NOT_FILLED_NOT_INTERPOLATED_NOT_A_GLOBAL_BLOCKER_UNLESS_REQUIRED_SYMBOL_HAS_ZERO_USABLE_COVERAGE",
            "analysis_eligibility_policy": "DOWNSTREAM_ANALYSIS_MUST_MARK_UNSUPPORTED_SLICES_NOT_TESTABLE",
            "field_coverage_artifact": "CFGI_FIELD_COVERAGE.json",
            "event_paths_artifact": "CFGI_EVENT_PATHS.jsonl.gz",
        },
        "authority": auth,
        "historical_findings_max_classification": "FORWARD_TEST",
        "automatic_promotion": False,
        "warnings": sorted(set(warnings)),
        "blockers": sorted(set(blockers)),
        "readiness_verdict": "PASS" if not blockers else "FAIL",
    }


def main() -> None:
    cfg = json.loads(CONFIG.read_text())
    billing = json.loads((ART / "CFGI_BILLING.json").read_text())
    events = billing.get("selected_events") or []
    if not events:
        raise SystemExit("CFGI_selected_events_missing")
    raw = read_jsonl_gz(ART / "cfgi_targeted.jsonl.gz")
    coverage, path_rows, structural = build(cfg, events, raw)
    (ART / "CFGI_FIELD_COVERAGE.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n")
    with gzip.open(ART / "CFGI_EVENT_PATHS.jsonl.gz", "wt", encoding="utf-8") as fh:
        for row in path_rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    manifest = build_manifest(cfg, billing, coverage, structural)
    for name in ["CFGI_FIELD_COVERAGE.json", "CFGI_EVENT_PATHS.jsonl.gz"]:
        p = ART / name
        manifest["artifact_state"][name] = {"exists": True, "bytes": p.stat().st_size, "sha256": sha256(p)}
    (ART / "RESEARCH_READINESS_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": manifest["readiness_verdict"],
        "events": len(events),
        "path_rows": len(path_rows),
        "exact_timestamp_symbol_hours": coverage["exact_timestamp_symbol_hours"],
        "asof_available_symbol_hours": coverage["asof_available_symbol_hours"],
        "missing_asof_symbol_hours": coverage["expected_symbol_hours"] - coverage["asof_available_symbol_hours"],
        "symbol_coverage": coverage["symbol_coverage"],
        "blockers": manifest["blockers"],
        "warnings": len(manifest["warnings"]),
    }, sort_keys=True))
    if manifest["readiness_verdict"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
