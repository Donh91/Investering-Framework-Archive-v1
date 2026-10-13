#!/usr/bin/env python3
"""Task 1.5 reproducible, bounded source-publication chronology audit.

Research-only. A first-parent Git commit timestamp is a bounded approximation of
archive publication, NEVER provider first-knowledge or a canonical scorer rewrite.
Samples are selected by frozen issue clock and original outcome STATUS ONLY,
not by direction result or returns. No market API, LLM or trading permission.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

WINDOW = datetime(2026, 9, 15, 6, tzinfo=timezone.utc)
HORIZONS = ("1H", "4H", "24H")
ASSETS = ("BTC", "ETH")
STATES = ("CENSORED", "MATURED")
LEDGER = "TASK15_R0_FROZEN_FORECAST_TAPE_CENSOR_LEDGER.csv"

def parse(s):
    if not isinstance(s, str) or not s.endswith("Z"):
        raise ValueError(f"UTC_Z_REQUIRED:{s}")
    x = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if x.utcoffset() != timedelta(0):
        raise ValueError("NON_UTC")
    return x

def iso(x):
    return x.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def git(root, *args, env=None, check=True):
    proc = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True,
        timeout=120, env=env,
    )
    if check and proc.returncode:
        raise RuntimeError(f"GIT_ARCHIVE_UNAVAILABLE:{args[0]}:{proc.stderr[:150]}")
    return proc

def select_cases(ledger: Path):
    with ledger.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates = [r for r in rows
                  if r.get("horizon") in HORIZONS and r.get("asset") in ASSETS
                  and r.get("original_outcome_status") in STATES
                  and r.get("direction") in ("UP", "DOWN")
                  and r.get("forecast_status") == "ELIGIBLE"
                  and r.get("research_admission") in
                    ("RESEARCH_TAPE_SENSITIVITY_ONLY",
                     "CENSORED_ORIGINAL_RESEARCH_TAPE_SENSITIVITY_ONLY")]
    cohorts = []
    for week in range(4):
        start, end = WINDOW + timedelta(days=7 * week), WINDOW + timedelta(days=7 * (week + 1))
        for horizon in HORIZONS:
            for asset in ASSETS:
                for status in STATES:
                    cohort = [r for r in candidates
                              if start <= parse(r["issue_utc"]) < end
                              and r["horizon"] == horizon and r["asset"] == asset
                              and r["original_outcome_status"] == status]
                    cohort.sort(key=lambda r: (r["issue_utc"], r["prediction_id"]))
                    cohorts.extend(cohort[:2])  # first two in each predefined stratum
    if len({r["prediction_id"] for r in cohorts}) != len(cohorts):
        raise ValueError("SAMPLED_FORECAST_DUPLICATE")
    return cohorts, len(candidates), len(rows)

def path_at_due(due):
    candle = due - timedelta(hours=1)
    return f"03_DAILY_CAPTURE_LOGS/hourly/{candle:%Y/%m/%Y-%m-%d}.csv"

def contains_exact_candle(raw_csv: str, due, asset):
    open_time = iso(due - timedelta(hours=1))
    try:
        rows = list(csv.DictReader(raw_csv.splitlines()))
        matching = [r for r in rows if r.get("timestamp_utc") == open_time]
        return (len(matching) == 1 and matching[0].get("spot_status") == "PASS"
                and float(matching[0][f"{asset.lower()}_close"]) > 0)
    except (ValueError, KeyError, TypeError, csv.Error):
        return False

def provenance_history(root, ref, relative, cache):
    key = ("log", relative)
    if key in cache:
        return cache[key]
    raw = git(root, "log", "--first-parent", "--format=%H %ct", ref, "--", relative).stdout
    parsed = []
    for line in raw.splitlines():
        bits = line.strip().split()
        if len(bits) != 2 or not bits[1].isdigit() or len(bits[0]) != 40:
            raise ValueError("INVALID_FIRST_PARENT_HISTORY_RECORD")
        parsed.append((bits[0], datetime.fromtimestamp(int(bits[1]), timezone.utc)))
    cache[key] = list(reversed(parsed)) # oldest first, not later-replayed candle order
    return cache[key]

def first_recorded_publication(root, ref, due, asset, cache):
    source_path = path_at_due(due)
    commits = provenance_history(root, ref, source_path, cache)
    for commit, timestamp in commits:
        key = ("file", commit, source_path)
        if key not in cache:
            out = git(root, "show", f"{commit}:{source_path}", check=False)
            cache[key] = out.stdout if out.returncode == 0 else None
        contents = cache[key]
        if contents is not None and contains_exact_candle(contents, due, asset):
            return {"source_path": source_path, "first_present_main_commit": commit,
                    "first_present_committer_utc": iso(timestamp)}
    return {"source_path": source_path, "first_present_main_commit": None,
            "first_present_committer_utc": None}

def census(root, ledger, output, ref):
    if git(root, "rev-parse", "--is-shallow-repository").stdout.strip() != "false":
        raise RuntimeError("FULL_FIRST_PARENT_GIT_HISTORY_REQUIRED")
    main_sha = git(root, "rev-parse", "--verify", ref).stdout.strip()
    if len(main_sha) != 40:
        raise RuntimeError("MAIN_REF_SHA_UNAVAILABLE")
    sample, total_candidates, all_slots = select_cases(ledger)
    cache, records = {}, []
    for row in sample:
        due = parse(row["due_utc"])
        cutoff = due + timedelta(hours=1.5)
        source = first_recorded_publication(root, ref, due, row["asset"], cache)
        first = parse(source["first_present_committer_utc"]) if source["first_present_committer_utc"] else None
        if first is None:
            status = "NOT_PRESENT_IN_AVAILABLE_FIRST_PARENT_HISTORY"
        elif first < due:
            status = "INVALID_FUTURE_HOUR_ARCHIVE_CLOCK"
        elif first <= cutoff:
            status = "PRESENT_BY_90_MIN_CUTOFF"
        else:
            status = "FIRST_PRESENT_AFTER_90_MIN_CUTOFF"
        records.append({
            "prediction_id": row["prediction_id"],
            "horizon": row["horizon"], "asset": row["asset"],
            "issued_at_utc": row["issue_utc"], "due_at_utc": row["due_utc"],
            "deadline_utc": iso(cutoff),
            "original_outcome_status": row["original_outcome_status"],
            "original_outcome_sha256": row["original_outcome_sha256"],
            **source,
            "archive_publication_class": status,
            "publication_minutes_from_due": round((first - due).total_seconds() / 60, 3) if first else None,
            "scorer_would_have_received_source": "UNVERIFIED_EXECUTION_CONTEXT",
        })
    comparison = {state: dict(Counter(r["archive_publication_class"] for r in records
                                       if r["original_outcome_status"] == state))
                  for state in STATES}
    receipt = {
        "contract": "EDGE_TASK15_FIRST_PARENT_PUBLICATION_SAMPLE_v1",
        "result_classification": "RESEARCH_SAMPLED_AUDIT_ONLY_NO_FORECAST_ALPHA",
        "authority": {"market_rule_change": False, "scorer_rewrite": False,
                      "later_censored_price_substitution": False,
                      "portfolio_execution": False},
        "source_ref": ref, "source_main_commit_sha": main_sha,
        "input_ledger_sha256": hashlib.sha256(ledger.read_bytes()).hexdigest(),
        "sampling_policy": "FIRST_TWO_FORECASTS_BY_ISSUE_CLOCK_PER_7D_WEEK_X_HORIZON_X_ASSET_X_ORIGINAL_MATURITY_STATE; NO_RETURN_SELECTION",
        "sampling_max": 4 * len(HORIZONS) * len(ASSETS) * len(STATES) * 2,
        "candidate_rows_in_full_research_tape": total_candidates,
        "all_issuance_slots": all_slots,
        "sampled_rows": len(records), "crosscheck": comparison,
        "cases": records,
        "limitations": [
            "Committer timestamps on current canonical first-parent path history approximate archive availability, NOT exchange/source-provider first knowledge.",
            "Later source backfills NEVER turn frozen CENSORED into MATURED.",
            "Sample selection is deterministic by issuance UTC within censor/matured strata; not representative independent events or causal evidence.",
            "This checks main path-changing commits; publication/use in original runner context may differ and needs independent run/owner receipt verification.",
            "No claim that every censor shares the sampled publication-gap root cause; full census and recovery SLA remain separate.",
        ],
        "admission_verdict": "NOT_PIT_CERTIFIED_NO_AUTO_MODEL_PROMOTION",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return receipt

def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        git(root, "init", "-q")
        git(root, "config", "user.name", "task15-fixture")
        git(root, "config", "user.email", "task15@example.invalid")
        git(root, "checkout", "-qb", "main")
        rel = "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-15.csv"
        fp = root / rel
        fp.parent.mkdir(parents=True)
        for date, body in (
            ("2026-09-15T18:07:11+00:00", "timestamp_utc,spot_status,btc_close\n2026-09-15T17:00:00Z,PASS,100\n"),
            ("2026-09-15T22:07:22+00:00", "timestamp_utc,spot_status,btc_close\n2026-09-15T17:00:00Z,PASS,100\n2026-09-15T18:00:00Z,PASS,101\n"),
        ):
            fp.write_text(body, encoding="utf-8")
            git(root, "add", rel)
            env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
            git(root, "commit", "-qm", "fixture", env=env)
        git(root, "update-ref", "refs/remotes/origin/main", git(root, "rev-parse", "HEAD").stdout.strip())
        cache = {}
        late = first_recorded_publication(root, "origin/main", parse("2026-09-15T19:00:00Z"), "BTC", cache)
        early = first_recorded_publication(root, "origin/main", parse("2026-09-15T18:00:00Z"), "BTC", cache)
        assert late["first_present_committer_utc"] == "2026-09-15T22:07:22Z", late
        assert early["first_present_committer_utc"] == "2026-09-15T18:07:11Z", early
        assert not contains_exact_candle(fp.read_text(), parse("2026-09-15T20:00:00Z"), "BTC")
    return "PASS: frozen cutoff late-candle test, on-time positive control, missing candle negative"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--input", default="/tmp/task15-evidence/" + LEDGER)
    ap.add_argument("--out", default="/tmp/task15-evidence/TASK15_R1_OWNER_PUBLICATION_SAMPLE.json")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        print(self_test())
        return
    r = census(Path(args.root), Path(args.input), Path(args.out), args.ref)
    print(json.dumps({"sampled_rows": r["sampled_rows"],
                      "candidate_rows_in_full_research_tape":r["candidate_rows_in_full_research_tape"],
                      "source_main_commit_sha":r["source_main_commit_sha"],
                      "crosscheck":r["crosscheck"],
                      "limit":r["limitations"]},sort_keys=True))

if __name__ == "__main__":
    main()
