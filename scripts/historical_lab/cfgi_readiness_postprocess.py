#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("06_RESEARCH_LAB/historical_altseason_pullback_v1")
DEFAULT_ARTIFACTS = ROOT / "artifacts"
DEFAULT_CONFIG = ROOT / "config.json"


def dt(value: str) -> datetime:
    x = datetime.fromisoformat(value.replace("Z", "+00:00"))
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
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def read_jsonl_gz(path: Path) -> list[dict]:
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def requested_value(row: dict | None, field: str):
    if row is None:
        return None
    if field == "score":
        return row.get("score")
    return row.get(f"component_{field}")


def event_id(ev: dict) -> str:
    return str(
        ev.get("window_id")
        or ev.get("episode_id")
        or ev.get("control_id")
        or f"{ev.get('kind','UNKNOWN')}:{ev.get('event_utc','UNKNOWN')}"
    )


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


def build_field_coverage(
    events: list[dict], rows: list[dict], cfg: dict
) -> tuple[dict, list[dict], dict]:
    ccfg = cfg["cfgi"]
    pre = int(ccfg["pre_event_hours"])
    post = int(ccfg["post_event_hours"])
    fields = list(ccfg["fields"])
    symbols = list(ccfg["symbols"])

    lookup: dict[tuple[str, str], dict] = {}
    duplicate_keys = []
    for row in rows:
        sym = row.get("symbol")
        ts = row.get("timestamp")
        if not sym or not ts:
            continue
        key = (str(sym), iso(dt(str(ts))))
        if key in lookup:
            duplicate_keys.append({"symbol": key[0], "timestamp": key[1]})
        lookup[key] = row

    path_rows: list[dict] = []
    per_sf = defaultdict(lambda: {"expected": 0, "timestamp_present": 0, "non_null": 0})
    per_event = {}
    stale_series = defaultdict(list)
    non_hour_aligned_events = []

    for ev in events:
        t = dt(ev["event_utc"])
        if any((t.minute, t.second, t.microsecond)):
            non_hour_aligned_events.append(
                {"event_id": event_id(ev), "event_utc": iso(t)}
            )
        eid = event_id(ev)
        ev_expected = 0
        ev_present = 0

        for rh in range(-pre, post + 1):
            expected_dt = t + timedelta(hours=rh)
            expected_ts = iso(expected_dt)
            for sym in symbols:
                row = lookup.get((sym, expected_ts))
                values = {field: requested_value(row, field) for field in fields}
                rec = {
                    "event_id": eid,
                    "kind": ev.get("kind"),
                    "event_utc": iso(t),
                    "relative_hour": rh,
                    "symbol": sym,
                    "expected_timestamp_utc": expected_ts,
                    "observed_exact_hour": row is not None,
                    "observed_timestamp_utc": None if row is None else iso(dt(str(row["timestamp"]))),
                    "classification": None if row is None else row.get("classification"),
                    "real_price": None if row is None else row.get("real_price"),
                    "fields": values,
                }
                path_rows.append(rec)
                ev_expected += 1
                ev_present += int(row is not None)
                for field in fields:
                    key = (sym, field)
                    per_sf[key]["expected"] += 1
                    per_sf[key]["timestamp_present"] += int(row is not None)
                    per_sf[key]["non_null"] += int(values[field] is not None)
                    stale_series[(eid, sym, field)].append((rh, values[field]))

        per_event[eid] = {
            "kind": ev.get("kind"),
            "event_utc": iso(t),
            "expected_symbol_hours": ev_expected,
            "observed_exact_symbol_hours": ev_present,
            "exact_timestamp_coverage_ratio": 0.0 if not ev_expected else ev_present / ev_expected,
        }

    field_rows = []
    for sym in symbols:
        for field in fields:
            x = per_sf[(sym, field)]
            expected = x["expected"]
            present = x["timestamp_present"]
            non_null = x["non_null"]
            max_run = 0
            for ev in events:
                max_run = max(
                    max_run,
                    max_constant_run(stale_series[(event_id(ev), sym, field)]),
                )
            field_rows.append(
                {
                    "symbol": sym,
                    "field": field,
                    "expected_slots": expected,
                    "exact_timestamp_slots": present,
                    "non_null_slots": non_null,
                    "timestamp_coverage_ratio": None if not expected else present / expected,
                    "field_coverage_ratio": None if not expected else non_null / expected,
                    "missing_ratio": None if not expected else 1 - (non_null / expected),
                    "max_constant_run_hours": max_run,
                    "staleness_interpretation": "DIAGNOSTIC_ONLY_NO_HARD_THRESHOLD",
                }
            )

    expected_all = len(events) * (pre + post + 1) * len(symbols)
    present_all = sum(1 for x in path_rows if x["observed_exact_hour"])
    coverage = {
        "contract": "CFGI_FIELD_COVERAGE_v1",
        "exact_relative_hour_semantics": True,
        "pre_event_hours": pre,
        "post_event_hours": post,
        "symbols": symbols,
        "fields": fields,
        "event_count": len(events),
        "expected_symbol_hours": expected_all,
        "observed_exact_symbol_hours": present_all,
        "exact_timestamp_coverage_ratio": None if not expected_all else present_all / expected_all,
        "field_coverage": field_rows,
        "event_coverage": per_event,
        "diagnostics": {
            "duplicate_symbol_timestamp_keys": duplicate_keys,
            "non_hour_aligned_events": non_hour_aligned_events,
            "staleness_is_measured_not_thresholded": True,
            "no_silent_fallback": True,
        },
    }
    structural = {
        "duplicate_symbol_timestamp_keys": duplicate_keys,
        "non_hour_aligned_events": non_hour_aligned_events,
        "expected_symbol_hours": expected_all,
        "observed_exact_symbol_hours": present_all,
    }
    return coverage, path_rows, structural


def build_manifest(
    artifacts: Path, cfg: dict, field_coverage: dict, structural: dict
) -> dict:
    readiness = cfg["readiness"]
    ccfg = cfg["cfgi"]
    auth = cfg["authority"]

    required_free = list(readiness["free_stage_required_artifacts"])
    required_cfgi = list(readiness["cfgi_stage_required_artifacts"])
    required = required_free + required_cfgi

    blockers: list[str] = []
    warnings: list[str] = []
    artifact_state = {}

    for name in required:
        path = artifacts / name
        exists = path.exists() and path.stat().st_size > 0
        artifact_state[name] = {
            "exists": exists,
            "bytes": path.stat().st_size if exists else 0,
            "sha256": sha256(path) if exists else None,
        }
        if not exists:
            blockers.append(f"MISSING_ARTIFACT:{name}")

    supplemental = "FREE_EVENT_PATHS_COVERAGE.json"
    sp = artifacts / supplemental
    artifact_state[supplemental] = {
        "exists": sp.exists() and sp.stat().st_size > 0,
        "bytes": sp.stat().st_size if sp.exists() else 0,
        "sha256": sha256(sp) if sp.exists() else None,
    }
    if not artifact_state[supplemental]["exists"]:
        blockers.append(f"MISSING_ARTIFACT:{supplemental}")

    if structural["duplicate_symbol_timestamp_keys"]:
        blockers.append("CFGI_DUPLICATE_SYMBOL_TIMESTAMP_KEYS")
    if structural["non_hour_aligned_events"]:
        blockers.append("CFGI_EVENT_TIMESTAMPS_NOT_HOUR_ALIGNED")
    expected_symbol_hours = int(structural["expected_symbol_hours"])
    observed_exact_symbol_hours = int(structural["observed_exact_symbol_hours"])
    if expected_symbol_hours != observed_exact_symbol_hours:
        warnings.append(
            f"CFGI_EXACT_OBSERVATION_MISSINGNESS:{expected_symbol_hours-observed_exact_symbol_hours}/{expected_symbol_hours}"
        )

    billing_path = artifacts / "CFGI_BILLING.json"
    billing = json.loads(billing_path.read_text()) if billing_path.exists() else {}
    if billing.get("status") != "PASS":
        blockers.append(f"CFGI_BILLING_STATUS:{billing.get('status','MISSING')}")
    expected_credits = billing.get("expected_worst_case_credits")
    if expected_credits is None or expected_credits > int(ccfg["expected_credit_hard_cap"]):
        blockers.append("CFGI_EXPECTED_CREDITS_EXCEED_OR_MISSING_HARD_CAP")
    actual = billing.get("actual_credits_used_from_headers")
    if actual is None:
        warnings.append("CFGI_ACTUAL_CREDITS_HEADER_UNAVAILABLE")
    elif actual > int(ccfg["expected_credit_hard_cap"]):
        blockers.append("CFGI_ACTUAL_CREDITS_EXCEED_HARD_CAP")
    remaining = billing.get("final_credits_remaining")
    if remaining is None:
        blockers.append("CFGI_FINAL_RESERVE_HEADER_UNAVAILABLE")
    elif remaining < int(ccfg["minimum_credits_reserve"]):
        blockers.append("CFGI_MINIMUM_RESERVE_BREACHED")

    for row in field_coverage.get("field_coverage", []):
        if row.get("field_coverage_ratio") == 0:
            warnings.append(f"CFGI_ZERO_FIELD_COVERAGE:{row['symbol']}.{row['field']}")
        elif row.get("missing_ratio") not in (None, 0):
            warnings.append(
                f"CFGI_FIELD_MISSINGNESS:{row['symbol']}.{row['field']}:{row['missing_ratio']:.6f}"
            )

    if auth.get("research_only") is not True:
        blockers.append("AUTHORITY_RESEARCH_ONLY_NOT_TRUE")
    if auth.get("portfolio_execution") is not False:
        blockers.append("AUTHORITY_PORTFOLIO_EXECUTION_NOT_FALSE")
    if auth.get("canonical_market_state") is not False:
        blockers.append("AUTHORITY_CANONICAL_MARKET_STATE_NOT_FALSE")
    if auth.get("automatic_rule_changes") is not False:
        blockers.append("AUTHORITY_AUTOMATIC_RULE_CHANGES_NOT_FALSE")
    if auth.get("promotion_requires_separate_review") is not True:
        blockers.append("AUTHORITY_PROMOTION_REVIEW_NOT_REQUIRED")

    return {
        "contract": "RESEARCH_READINESS_MANIFEST_v1",
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
            "expected_worst_case_credits": expected_credits,
            "actual_credits_used_from_headers": actual,
            "final_credits_remaining": remaining,
            "hard_cap": ccfg["expected_credit_hard_cap"],
            "minimum_reserve": ccfg["minimum_credits_reserve"],
            "event_count": field_coverage.get("event_count"),
            "exact_timestamp_coverage_ratio": field_coverage.get("exact_timestamp_coverage_ratio"),
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
    cfg = json.loads(DEFAULT_CONFIG.read_text())
    artifacts = DEFAULT_ARTIFACTS
    billing_path = artifacts / "CFGI_BILLING.json"
    rows_path = artifacts / "cfgi_targeted.jsonl.gz"

    if not billing_path.exists():
        raise SystemExit("CFGI_BILLING.json_missing")
    if not rows_path.exists():
        raise SystemExit("cfgi_targeted.jsonl.gz_missing")

    billing = json.loads(billing_path.read_text())
    events = billing.get("selected_events") or []
    if not events:
        raise SystemExit("CFGI_selected_events_missing")

    rows = read_jsonl_gz(rows_path)
    coverage, path_rows, structural = build_field_coverage(events, rows, cfg)

    (artifacts / "CFGI_FIELD_COVERAGE.json").write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n"
    )
    with gzip.open(artifacts / "CFGI_EVENT_PATHS.jsonl.gz", "wt", encoding="utf-8") as fh:
        for row in path_rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    manifest = build_manifest(artifacts, cfg, coverage, structural)
    (artifacts / "RESEARCH_READINESS_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(
        {
            "status": manifest["readiness_verdict"],
            "events": len(events),
            "path_rows": len(path_rows),
            "blockers": manifest["blockers"],
            "warnings": len(manifest["warnings"]),
        },
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
