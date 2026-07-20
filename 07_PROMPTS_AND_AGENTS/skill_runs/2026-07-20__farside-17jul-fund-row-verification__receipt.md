# Farside 17 July Fund-Row Verification — Archive Receipt

**Dato:** 2026-07-20  
**Status:** RECEIPT  
**Område:** DATA PING / Farside ETF source verification / accepted-log supplement  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`

## Decision manifest

```yaml
archive_decision: ARCHIVE_RELEVANT_FARSIDE_FUND_LEVEL_ROWS_AND_LINK_CURRENT_POINTERS
classification: SOURCE_VERIFICATION_SUPPLEMENT
primary_owner: 02_DATA_PING/operational_handoffs/accepted_logs/supplements/2026-07-20T035540Z__farside-17jul-fund-row-verification.json
operation: CREATE_AND_UPDATE
target_branch: agent/task-20260720-farside-17jul-verification
branch_assertion: PASS
canonical_index_change: NO
addendum_registry_change: NOT_APPLICABLE_POINTER_DISCOVERABLE
high_impact_gate: NOT_REQUIRED
duplicate_check: EXISTING_ACCEPTED_PAYLOAD_HAS_COMPACT_TOTALS_BUT_NOT_FULL_LATEST_10_FUND_LEVEL_ROWS
source_lineage: USER_SUPPLIED_DIRECT_FARSIDE_API_RESPONSE_LINKED_TO_DATA_PING_V6_20260719T200033Z
backup_product: NONE
```

## Paths

Created:

```text
02_DATA_PING/operational_handoffs/accepted_logs/supplements/2026-07-20T035540Z__farside-17jul-fund-row-verification.json
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-20__farside-17jul-fund-row-verification__receipt.md
```

Updated:

```text
02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
02_DATA_PING/operational_handoffs/latest_decision_context_state.json
```

## Branch readback

```yaml
supplement_blob_sha: 1665cc409ef4932aaaaba816be09632e56a4f9b2
latest_accepted_log_pointer_blob_sha: 275f46343bcc5abffef1792ed6b84ea4b48f7837
latest_decision_context_pointer_blob_sha: eb8741e62c3299c5d390ebb0662ffc3de4e978f6
normalized_latest_10_session_rows_sha256: ebe4e2114a75a5e000b994f106774ec8a7ff52699e6be15965ff018cefa8bc4a
branch_readback_status: PASS
```

## Source verification result

```yaml
latest_completed_session: 2026-07-17
btc_total_usd_m: 132.3
ibit_usd_m: 136.5
fbtc_usd_m: -4.2
btc_internal_sum_status: PASS
eth_total_usd_m: 36.7
etha_usd_m: 31.7
feth_usd_m: 5.0
eth_internal_sum_status: PASS
btc_total_positive_streak: 4
btc_total_and_ibit_positive_streak: 4
btc_3_5_7_10_session_sums_usd_m: [319.1, 75.5, 70.6, 272.9]
eth_3_5_7_10_session_sums_usd_m: [62.6, 105.5, 71.7, 189.8]
prior_136_5_revision_delta_ambiguity: RESOLVED_AS_FALSE
secondary_ota_lookonchain_values: PRESERVED_SEPARATELY_PROVISIONAL
```

## Authority and impact

```yaml
accepted_payload_rewritten: NO
stage_1_etf_flow_status_change: NO_ALREADY_COMPLETE_RATIFIED
market_state_change: NO
rotation_change: NO
portfolio_action_change: NO
source_quality_effect: FUND_LEVEL_REPRODUCIBILITY_IMPROVED
```

## Pull request and main validation

```yaml
pull_request: PENDING
merge_commit_sha: PENDING
main_readback_status: PENDING
final_repository_state: PENDING
write_governance_result: PASS_SO_FAR
incident_count: 0
```
