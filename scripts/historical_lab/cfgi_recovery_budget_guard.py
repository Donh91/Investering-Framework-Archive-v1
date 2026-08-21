#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
from pathlib import Path

from cfgi_targeted_backfill import dt, estimated_rows

ROOT=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1")
ART=ROOT/"artifacts"
LEDGER=Path("00_ARCHIVE_CONTROL/research_runtime/HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER.json")
RESERVATION=Path("00_ARCHIVE_CONTROL/research_runtime/HISTORICAL_ALTSEASON_CFGI_PAID_RESERVATION.json")
GAP_AUTH=Path("00_ARCHIVE_CONTROL/research_runtime/HISTORICAL_ALTSEASON_CFGI_MARKET_GAPFILL_AUTHORIZATION.json")
FINGERPRINT="6106f96285a66f03e324595b68c1777627f4d83e5e70dc6c64d9b1022e544a8f"


def read_symbols(path:Path)->set[str]:
    if not path.exists(): return set()
    out=set()
    with gzip.open(path,"rt",encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r=json.loads(line)
                if r.get("symbol"): out.add(str(r["symbol"]))
    return out


def main()->None:
    cfg=json.loads((ROOT/"config.json").read_text());ccfg=cfg["cfgi"];hard=int(ccfg["expected_credit_hard_cap"]);reserve=int(ccfg["minimum_credits_reserve"])
    ledger=json.loads(LEDGER.read_text());reservation=json.loads(RESERVATION.read_text())
    assert ledger["contract"] in {"HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER_v1","HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER_v2"}
    assert reservation["contract"]=="HISTORICAL_ALTSEASON_CFGI_PAID_RESERVATION_v1"
    assert ledger["input_fingerprint_sha256"]==reservation["input_fingerprint_sha256"]==FINGERPRINT
    assert ledger["automatic_retry_after_failure"] is False
    cumulative_path=ART/"CFGI_CUMULATIVE_BILLING.json";billing_path=ART/"CFGI_BILLING.json";present=read_symbols(ART/"cfgi_targeted.jsonl.gz");required=set(ccfg["symbols"]);missing=sorted(required-present)
    if cumulative_path.exists() and billing_path.exists():
        cumulative=json.loads(cumulative_path.read_text());billing=json.loads(billing_path.read_text());prior_actual=int(cumulative["cumulative_actual_credits_used"]);last_remaining=int(cumulative["final_credits_remaining"])
        if cumulative.get("status")!="PASS":raise SystemExit("CFGI_CUMULATIVE_BILLING_NOT_PASS")
        assert cumulative["input_fingerprint_sha256"]==FINGERPRINT
        intervals=[(dt(x["start"]),dt(x["end"])) for x in billing.get("merged_intervals") or []]
        if missing:
            if missing!=["MARKET"] or not GAP_AUTH.exists():raise SystemExit(f"CFGI_UNAUTHORIZED_MISSING_SYMBOL_PLAN:{missing}")
            auth=json.loads(GAP_AUTH.read_text());assert auth["contract"]=="HISTORICAL_ALTSEASON_CFGI_MARKET_GAPFILL_AUTHORIZATION_v1";assert auth["owner_authorized"] is True;assert auth["input_fingerprint_sha256"]==FINGERPRINT;assert auth["allowed_symbols"]==["MARKET"]
            expected=estimated_rows(intervals,1)*len(ccfg["fields"])+1
            if expected>int(auth["max_worst_case_credits"]):raise SystemExit("CFGI_MARKET_GAPFILL_AUTHORIZED_CAP_EXCEEDED")
            plan="MARKET_ONLY_GAPFILL"
        else:
            expected=0;plan="NO_FURTHER_PAID_CALL_REQUIRED"
    else:
        attempts=ledger.get("attempts") or [];prior_actual=sum(int(x.get("actual_credits_used_from_headers") or 0) for x in attempts);last_remaining=next((int(x["final_credits_remaining"]) for x in reversed(attempts) if x.get("final_credits_remaining") is not None),None)
        if last_remaining is None:raise SystemExit("CFGI_LEDGER_RESERVE_MISSING")
        pre=int(ccfg["pre_event_hours"]);post=int(ccfg["post_event_hours"]);expected=int(reservation["candidate_event_count"])*(pre+post+1)*len(ccfg["symbols"])*len(ccfg["fields"]);plan="LEGACY_FULL_RECOVERY"
    projected=prior_actual+expected;projected_remaining=last_remaining-expected;blockers=[]
    if projected>hard:blockers.append("CUMULATIVE_HARD_CAP_EXCEEDED")
    if projected_remaining<reserve:blockers.append("PROJECTED_RESERVE_BREACH")
    out={"contract":"HISTORICAL_ALTSEASON_CFGI_RECOVERY_BUDGET_GUARD_v2","input_fingerprint_sha256":FINGERPRINT,"plan":plan,"present_symbols":sorted(present),"missing_symbols":missing,"prior_actual_credits_used":prior_actual,"expected_current_worst_case_credits":expected,"projected_cumulative_credits":projected,"hard_cap_credits":hard,"last_known_credits_remaining":last_remaining,"projected_credits_remaining":projected_remaining,"minimum_reserve_credits":reserve,"blockers":blockers,"status":"PASS" if not blockers else "FAIL"}
    print(json.dumps(out,sort_keys=True))
    if blockers:raise SystemExit(2)


if __name__=="__main__":main()
