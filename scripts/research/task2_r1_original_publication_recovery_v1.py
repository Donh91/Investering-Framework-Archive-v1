#!/usr/bin/env python3
"""Task2 R1 one-case GitHub-origin publication witness, additive to frozen R1.

The original 2026-10-23 10/11 source result remains immutable.
This program proves only the public source packet reached main BEFORE the
registered original forecast issuance. It does NOT certify upstream provider
first-publication, entire model information PIT, user delivery or PnL.
No external network calls or restricted values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts.research.task2_r1_scoped_readiness_v1 import (
    ROOT, pinned_inputs, reconcile, utc, need,
)

CONTRACT="TASK2_R1_ORIGINAL_PACKET_PUBLICATION_RECOVERY_V1"
PATH=("06_RESEARCH_LAB/hugging_face_task2_audit_20261022/"
      "2026-11-05__TASK2_R1_MISSING_PUBLICATION_WITNESS_V1.json")
PINNED_WITNESS_GIT_BLOB="68466d8dacf1805d0e872cd5b15bc93fda0e66db"
FROZEN_ID="CMP-20261012-904299b09eca"
COMMIT="6495f36225e51d4bab9c3afafb9bd27ce56e4bfc"
PACKET="04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/10/12/195803_d6d9ee28ede4.json"
BLOB="2612c9b8272ad375c6a75ba917351f2465e1fd1b"
ISSUED="2026-10-12T19:59:38Z"
RUN_ID=38300767397
JOB_ID=114983897925

ORIGINAL_LINES={
    "original_commit":"2026-10-12T19:58:03.8341518Z [main 6495f36225] learning: entry signal ledger 38300767397",
    "original_path_first_add":"2026-10-12T19:58:03.8343024Z  create mode 100644 04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/10/12/195803_d6d9ee28ede4.json",
    "remote_push":"2026-10-12T19:58:05.7521591Z    74130fa250..6495f36225  HEAD -> main",
}
SHA40=re.compile(r"^[0-9a-f]{40}$")


def load_witness(root=ROOT):
    raw=(Path(root)/PATH).read_bytes()
    blob=hashlib.sha1(
        b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw
    ).hexdigest()
    need(blob==PINNED_WITNESS_GIT_BLOB,"WITNESS_IMMUTABLE_BLOB_CHANGED")
    return json.loads(raw)


def logtime(line):
    need(isinstance(line,str) and "Z " in line,"ORIGINAL_LOG_LINE_INVALID")
    return utc(line.split("Z ",1)[0]+"Z")


def recover(inputs,witness):
    base=reconcile(inputs)
    need(witness.get("contract")=="TASK2_R1_MISSING_ORIGINAL_PUBLICATION_WITNESS_V1",
         "RECOVERED_WITNESS_CONTRACT")
    need(witness.get("classification")=="PUBLIC_SAFE_GITHUB_SERVER_LOG_METADATA_ONLY",
         "RECOVERED_WITNESS_VISIBILITY")
    need(witness.get("source_forecast_id")==FROZEN_ID==
         base["source_unverified_forecast_id"],
         "RECOVERED_WITNESS_NOT_ORIGINAL_MISSING_CASE")
    original=next(x for x in inputs["ledger"]["rows"]
                  if x["forecast_id"]==FROZEN_ID)
    previously=next(x for x in inputs["source"]["rows"]
                    if x["forecast_id"]==FROZEN_ID)
    need(original["original_outcome_status"]=="PRESENT" and
         original["admissibility"]=="NOT_ADMITTED" and
         original["issued_at_utc"]==ISSUED==
         witness.get("original_forecast_issued_at_utc"),
         "RECOVERED_WITNESS_ORIGINAL_ISSUER_CHANGED")
    need(original["source_packet"]["path"]==PACKET==
         witness.get("original_packet_path") and
         original["source_packet"]["git_blob_sha"]==BLOB==
         witness.get("original_packet_blob_sha") and
         original["source_packet"]["first_git_commit_sha"]==COMMIT==
         witness.get("original_packet_first_add_commit"),
         "RECOVERED_WITNESS_ORIGINAL_SOURCE_IDENTITY")
    need(previously["packet_publication"]["status"]=="UNVERIFIED" and
         previously["scope_specific_source_chain_complete"] is False,
         "RECOVERED_WITNESS_PREVIOUS_SCOPE_CHANGED")
    need(witness.get("github_original_run_id")==RUN_ID and
         witness.get("github_original_job_id")==JOB_ID and
         witness.get("github_original_job_name")=="ledger" and
         witness.get("github_original_job_status")=="completed" and
         witness.get("github_original_job_conclusion")=="success",
         "RECOVERED_WITNESS_GITHUB_RUN_BINDING")
    lines=witness.get("authenticated_log_lines")
    need(isinstance(lines,dict) and lines==ORIGINAL_LINES,
         "RECOVERED_WITNESS_ORIGINAL_LOG_IDENTITY")
    commit_time=logtime(lines["original_commit"])
    add_time=logtime(lines["original_path_first_add"])
    push_time=logtime(lines["remote_push"])
    issue=utc(ISSUED)
    need(commit_time<=add_time<=push_time<issue,
         "RECOVERED_WITNESS_SOURCE_AFTER_ISSUE")
    need(witness.get("original_packet_publication_completed_at_utc")==
         lines["remote_push"].split("Z ",1)[0]+"Z" and
         witness.get("source_packet_pre_issue_verified_by_GitHub_server_log") is True and
         witness.get("original_packet_publication_before_frozen_issue") is True and
         witness.get("public_packet_observed_identical_git_blob_at_original_commit_and_current_main") is True,
         "RECOVERED_WITNESS_UNBOUND_CLAIM")
    forbidden={
        "first_user_delivery_verified":False,
        "all_24_original_context_feature_upstream_vintages_verified":False,
        "first_provider_publication_or_original_response_full_model_verified":False,
        "independent_market_shock_families_verified":False,
        "full_compass_R1_pit_admitted":False,
        "original_model_r1_information_edge_claim":False,
        "original_investor_after_cost_edge_claim":False,
        "round3_analysis_authorized":False,
        "live_market_or_portfolio_changes":False,
        "data_files_overwritten":False,
    }
    for k,v in forbidden.items():
        need(witness.get(k) is v,"RECOVERED_WITNESS_FORBIDDEN_PROMOTION_"+k.upper())
    need(witness.get("source_scope_complete_after_this_witness")==
         "11_OF_11_ORIGINAL_PACKET_PUBLICATION_WITNESSES_ONLY",
         "RECOVERED_WITNESS_SCOPED_CLASSIFICATION")

    return {
        "contract":CONTRACT,
        "original_owner_issue":1596,
        "source_scope":"ORIGINAL_PACKET_PUBLICATION_ONLY",
        "snapshot_epoch":"2026-10-12_13_ORIGINALS_WITH_NOV5_SERVER_LOG_RECOVERY",
        "witness_git_blob":PINNED_WITNESS_GIT_BLOB,
        "original_forecasts":11,
        "preexisting_original_publication_witnesses":10,
        "new_original_publication_witnesses":1,
        "scoped_original_publication_witnesses":11,
        "historic_original_outcomes_present":9,
        "historic_original_outcomes_absent":2,
        "scoped_source_replays":11,
        "untouched_holdout":False,
        "certified_independent_event_families":0,
        "full_R1_scientific_PIT_admissions":0,
        "economic_edge_established":False,
        "historical_backtest_release":"BLOCKED_FULL_MODEL_VINTAGE_AND_INDEPENDENT_N",
        "investor_after_cost_backtest":"BLOCKED_DELIVERY_AND_EXECUTABLE_SELLABILITY",
        "round3_analysis":"FORBIDDEN",
        "original_witness_source_run_id":RUN_ID,
        "original_witness_source_job_id":JOB_ID,
        "original_witness_publication_commit":COMMIT,
        "original_witness_publication_git_blob":BLOB,
        "new_evidence_semantics":"GITHUB_SERVER_LOG_PACKET_MAIN_BEFORE_ORIGINAL_ISSUE_NOT_PROVIDER_OR_USER_FIRST_KNOWN",
        "next_source_trigger":"Original source custodian independently authenticates all context field vintages or full preserved original response, then new genuinely prospective independent market episode and clock-matched control. No historical admission from these publication-only receipts.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    report=recover(pinned_inputs(),load_witness())
    txt=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.write_text(txt)
    else:
        print(txt,end="")


if __name__=="__main__":
    main()
