# Claude OTA framework reconciliation — H7 row 10 and ETH ETF evidence

## Acceptance boundary

```yaml
source_run_timestamp_utc: 2026-08-01T05:48:32.902Z
operating_mode: STANDALONE_OTA_NO_REFERENCE_BRIDGE
main_framework_acceptance: NONCANONICAL_RESEARCH_EVIDENCE_AND_SOURCE_QA
canonical_state_change: NONE
portfolio_action_change: NONE
new_policy_event: NO
new_A_class_receipt: NO
new_shadow_dual_run: NO
```

## H7 row 10

The supplied CEST close values match the latest DATA PING settled Copenhagen row:

```yaml
CEST_date: 2026-07-31
BTCUSDT_close: 62947.78
ETHUSDT_close: 1861.81
ETHBTC_close: 0.02957
COND2_last_3_ETH_lead_count: 0
COND2_requirement: AT_LEAST_2
rolling_5_session_OLS_pct_per_session: -0.395
post_maturity_follow_through: INACTIVE_CONFIRMED
```

Row 10 is not a new canonical maturity. H7 already matured after five settled CEST rows and retained the historical score `EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`. Row 10 is accepted only as post-maturity extension evidence. It strengthens the conclusion that the early candidate did not persist into durable transmission, without retroactively changing the frozen historical result.

No lapse, retirement or retrigger rule is invented. Those semantics remain prospectively undefined.

## ETH ETF recovery

The source report restores three previously missing settled sessions and revalidates one already known session:

```yaml
2026_07_27_usd_m: 11.7
2026_07_27_status: REVALIDATED_PREVIOUSLY_KNOWN
2026_07_28_usd_m: 9.4
2026_07_28_status: NEWLY_RECOVERED
2026_07_29_usd_m: -32.9
2026_07_29_status: NEWLY_RECOVERED
2026_07_30_usd_m: 12.8
2026_07_30_status: NEWLY_RECOVERED_AND_MATCHES_MAIN_DATA_PING
2026_07_31_status: UNPUBLISHED_AT_RETRIEVAL_UNKNOWN_NOT_ZERO
```

Derived sums supplied by the source are retained:

```yaml
three_session_sum_usd_m: -9.7
five_session_sum_usd_m: 1.0
seven_session_sum_usd_m: -0.7
structural_read: OSCILLATING_AROUND_ZERO_NO_DIRECTIONAL_INTENSITY
```

This neutral flow structure does not support either a strong ETH accumulation claim or a persistent ETH outflow claim. It does not override the latest DATA PING reading of breadth below permission zones and settled ETHBTC below 0.0300.

## Source correction: issuer concentration

The source self-corrected its 23 July issuer-concentration claim:

```yaml
prior_claim: ETHA_100_PERCENT_OF_GROSS
corrected_rows_usd_m:
  ETHA: 8.5
  ETHB: 2.9
  FETH: 14.9
corrected_leader: FETH
corrected_share_of_listed_positive_flow_pct: APPROX_57
cause: INCOMPLETE_COLUMN_READ_BY_SOURCE
source_error: NO
```

The correction is accepted as source QA. Historical analyses relying on the earlier ETHA-only concentration claim must use the corrected distribution.

## H-SRC-02

The strong claim that a fresh Farside payload is available only after 16:00 UTC is falsified by the source's own preregistered rule because a fresh payload was retrieved at 05:48 UTC. The weaker descriptive claim — publication during US evening or night can also appear in early European morning — remains unproven and may continue prospectively.

## H-WIN-01 and F1

The source's downgrade from MODERATE to LOW_MODERATE is accepted as auditor-input self-correction. F1 remains `NOT_FAILED`; no score changes. The 31 July intraday low approached the threshold, but the close remained above it, so the observation is boundary stress rather than a failed window.

## ETHBTC threshold sequence

```yaml
status: SEQUENCE_TERMINATED_CONFIRMED
sessions_without_0_0300_touch: 3
settled_closes_above_0_0300_in_arc: 1
rotation_confirmation: NO
```

UTC and Copenhagen settlement rows remain separately labeled. The latest settled Copenhagen close is 0.02957; the supplied UTC settled close is 0.02962.

## Framework state

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
A_rows_total: 2
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

## Operational effect

The OTA adds useful ETF and experiment evidence but does not change the latest DATA PING operational class.

```yaml
operational_top_up_action: DO_NOT_ADD_RISK
reassessment_horizon: 12_TO_24_HOURS_OR_NEW_COMPLETE_DATA_PING
```

The latest decision-bearing DATA PING remains authoritative for the user-facing purchase translation.