#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

LAB = Path("06_RESEARCH_LAB/historical_altseason_pullback_v1")
ART = LAB / "artifacts"
CONFIG = LAB / "config.json"
CATALOG = ART / "EPISODE_CATALOG.json"
BILLING = ART / "CFGI_BILLING.json"
CUMULATIVE_BILLING = ART / "CFGI_CUMULATIVE_BILLING.json"
SUMMARY = ART / "BACKTEST_SUMMARY.json"
LEDGER = Path("00_ARCHIVE_CONTROL/research_runtime/HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER.json")

REQUIRED_PRIOR_OUTPUTS = [
    "CFGI_BILLING.json",
    "CFGI_COVERAGE.json",
    "CFGI_FIELD_COVERAGE.json",
    "cfgi_targeted.jsonl.gz",
    "CFGI_EVENT_SIGNATURES.json",
    "CFGI_EVENT_PATHS.jsonl.gz",
    "RESEARCH_READINESS_MANIFEST.json",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_events(catalog: dict) -> list[dict]:
    c = catalog.get("cfgi_candidate_windows") or {}
    rows = []
    for kind, key in (("PULLBACK", "pullbacks"), ("CONTROL", "controls")):
        for row in c.get(key, []):
            rows.append({"kind": kind, **row})
    return sorted(rows, key=lambda x: (x.get("event_utc", ""), x.get("episode_id", x.get("control_id", "")), x["kind"]))


def fingerprint() -> str:
    cfg = load(CONFIG)
    catalog = load(CATALOG)
    payload = {
        "contract": "CFGI_TARGETED_INPUT_FINGERPRINT_v1",
        "cfgi_config": cfg["cfgi"],
        "candidate_events": candidate_events(catalog),
        "authority": cfg["authority"],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def existing_is_complete(fp: str) -> bool:
    if not BILLING.exists():
        return False
    try:
        billing = load(BILLING)
    except Exception:
        return False
    if billing.get("status") != "PASS":
        return False
    if billing.get("input_fingerprint_sha256") != fp:
        return False
    for name in REQUIRED_PRIOR_OUTPUTS:
        p = ART / name
        if not p.exists() or p.stat().st_size == 0:
            return False
    try:
        manifest = load(ART / "RESEARCH_READINESS_MANIFEST.json")
    except Exception:
        return False
    return (
        manifest.get("readiness_verdict") == "PASS"
        and manifest.get("automatic_promotion") is False
        and manifest.get("historical_findings_max_classification") == "FORWARD_TEST"
    )


def restore_summary_from_billing():
    if not SUMMARY.exists() or not BILLING.exists():
        return
    summary = load(SUMMARY)
    billing = load(BILLING)
    summary.update({
        "cfgi_status": "TARGETED_ENRICHMENT_COMPLETE",
        "cfgi_selected_event_count": len(billing.get("selected_events") or []),
        "cfgi_expected_worst_case_credits": billing.get("expected_worst_case_credits"),
        "cfgi_actual_credits_used_from_headers": billing.get("actual_credits_used_from_headers"),
        "cfgi_final_credits_remaining": billing.get("final_credits_remaining"),
        "cfgi_comparison_artifact": "CFGI_EVENT_SIGNATURES.json",
        "interpretation_status": "DESCRIPTIVE_BOOTSTRAP_NOT_PROMOTED_TO_RULES",
        "cfgi_idempotent_reuse": True,
        "cfgi_input_fingerprint_sha256": billing.get("input_fingerprint_sha256"),
    })
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_cumulative_billing(fp: str, billing: dict) -> dict:
    ledger = load(LEDGER)
    assert ledger["contract"] == "HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER_v1"
    assert ledger["input_fingerprint_sha256"] == fp
    prior = int(ledger["cumulative_actual_credits_used"])
    current = int(billing.get("actual_credits_used_from_headers") or 0)
    remaining = billing.get("final_credits_remaining")
    cumulative = prior + current
    out = {
        "contract": "HISTORICAL_ALTSEASON_CFGI_CUMULATIVE_BILLING_v1",
        "input_fingerprint_sha256": fp,
        "prior_actual_credits_used": prior,
        "current_actual_credits_used": current,
        "cumulative_actual_credits_used": cumulative,
        "hard_cap_credits": int(ledger["hard_cap_credits"]),
        "final_credits_remaining": remaining,
        "minimum_reserve_credits": int(ledger["minimum_reserve_credits"]),
        "prior_attempt_count": len(ledger.get("attempts") or []),
        "current_run_id": os.environ.get("GITHUB_RUN_ID"),
        "status": "PASS" if cumulative <= int(ledger["hard_cap_credits"]) and remaining is not None and int(remaining) >= int(ledger["minimum_reserve_credits"]) else "FAIL",
    }
    if out["status"] != "PASS":
        raise SystemExit("CFGI_CUMULATIVE_BILLING_GUARD_FAIL")
    CUMULATIVE_BILLING.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def stamp(fp: str):
    billing = load(BILLING)
    if billing.get("status") != "PASS":
        raise SystemExit("CFGI_IDEMPOTENCY_STAMP_BLOCKED billing_not_pass")
    billing["input_fingerprint_contract"] = "CFGI_TARGETED_INPUT_FINGERPRINT_v1"
    billing["input_fingerprint_sha256"] = fp
    BILLING.write_text(json.dumps(billing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cumulative = write_cumulative_billing(fp, billing)
    if SUMMARY.exists():
        summary = load(SUMMARY)
        summary["cfgi_input_fingerprint_sha256"] = fp
        summary["cfgi_cumulative_actual_credits_used"] = cumulative["cumulative_actual_credits_used"]
        SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "STAMPED", "input_fingerprint_sha256": fp, "cumulative_actual_credits_used": cumulative["cumulative_actual_credits_used"]}, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["check", "stamp"], required=True)
    args = ap.parse_args()
    fp = fingerprint()
    if args.mode == "stamp":
        stamp(fp)
        return 0
    skip = existing_is_complete(fp)
    if skip:
        restore_summary_from_billing()
    else:
        subprocess.check_call(["python", "scripts/historical_lab/cfgi_recovery_budget_guard.py"])
    print(json.dumps({
        "contract": "CFGI_IDEMPOTENCY_GUARD_v1",
        "input_fingerprint_sha256": fp,
        "skip_paid": skip,
        "reason": "EXACT_COMPLETE_PRIOR_ENRICHMENT" if skip else "PAID_ENRICHMENT_REQUIRED_CUMULATIVE_BUDGET_PASS",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
