# Point-in-Time Breadth Sidecar Retention Addendum v1

**Date:** 2026-07-29 22:48 CEST  
**Status:** CANONICAL_OPERATIONAL_ADDENDUM  
**Parent protocol:** `02_DATA_PING/protocols/2026-07-28__data-ping-deep-capture-escalation-protocol-v1__canonical.md`  
**Implementation issue:** `#224`  
**Authority:** evidence retention only

## 1. Triggering learning

`DCR-20260729-EVENT-002` attempted to recover the constituent-level explanation for a material breadth relapse. The accepted DATA PINGs preserved aggregate breadth and an unchanged membership hash, but the exact CoinGecko page payloads and filtered constituent rows were not retained. Historical reconstruction was unavailable and current-universe substitution was correctly prohibited.

## 2. Prospective rule

Whenever an accepted DATA PING successfully retrieves the CoinGecko Top-100 page pair used by `COINGECKO_TOP100_FILTERED_v2`, the collector or ingest pipeline must emit a bounded point-in-time sidecar artifact.

The sidecar must preserve:

```yaml
source_identity:
  - endpoint_or_connector
  - method_id
  - filter_id
  - page_source_timestamps
  - retrieval_timestamp
  - freeze_timestamp

included_rows:
  fields:
    - id
    - symbol
    - market_cap_rank
    - market_cap_usd
    - price_usd
    - return_24h_pct

excluded_rows:
  fields:
    - id
    - symbol
    - exclusion_reason_code

aggregates:
  - raw_count
  - deduped_count
  - included_count
  - excluded_count
  - advancers
  - decliners
  - unchanged
  - advance_ratio
  - median_return_24h_pct
  - membership_sha256

integrity:
  - deterministic_sort_rule
  - artifact_row_count
  - artifact_bytes
  - artifact_sha256
  - lineage_path
```

## 3. Compact packet boundary

The ordinary compact DATA PING schema remains unchanged. Constituent rows belong in a sidecar artifact referenced by the packet or ingest receipt.

This addendum does not authorize enlarging the one-line packet, adding interpretation fields or changing trigger thresholds.

## 4. Fail-closed behavior

When the Top-100 retrieval succeeds but no sidecar is persisted, record:

```yaml
breadth_aggregate_status: AVAILABLE
breadth_replayability: FAIL
constituent_transition_analysis: NOT_PERMITTED
historical_recovery_assumption: FORBIDDEN
```

When source pages fail, retain the existing source-failure semantics. Missing values remain `UNKNOWN`, never zero.

## 5. Replay and testing requirements

The implementation must prove:

- deterministic row ordering and hash stability;
- aggregate replay parity from the sidecar;
- page-pair source-timestamp parity;
- exclusion-rule parity;
- no current-universe substitution;
- no post-freeze source calls;
- fixture and live-path receipts;
- bounded payload behavior.

## 6. Governance

The sidecar is evidence infrastructure only. It cannot:

- create or change market state;
- ratify rotation, rebuy, entry or exit;
- create retrospective prospective evidence;
- upgrade an A-class receipt;
- change sensor weight or threshold;
- authorize portfolio action;
- open the final holdout.

## 7. Application state

```yaml
applies_prospectively_from: MERGE_OF_THIS_ADDENDUM
retroactive_reconstruction: FORBIDDEN
compact_DATA_PING_change: NONE
implementation_status: TRACKED_IN_ISSUE_224
canonical_market_authority: ZERO
portfolio_authority: ZERO
```