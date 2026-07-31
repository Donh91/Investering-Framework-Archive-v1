# Claude OTA source record, H7 row 9 and threshold termination

```yaml
record_type: EXTERNAL_AUDITOR_OTA_INPUT
source_model: Claude
source_run_timestamp_utc: 2026-07-31T16:43:14.869Z
operating_mode: STANDALONE_OTA
reference_bridge_present: NO
reference_data_ping_run_id: NOT_PROVIDED
previous_source_reference: CLAUDE-OTA-2026-07-30T19:04:13.143Z
new_information_count_claimed: 4
matured_experiment_count_claimed: 1
source_qa_event_count_claimed: 2
main_framework_authority: NONE_UNTIL_RECONCILED
```

## Transmitted H7 row 9

```yaml
CEST_date: 2026-07-30
settlement_close_utc: 2026-07-30T21:59:59.999Z
BTCUSDT_close: 64735.53
ETHUSDT_close: 1918.67
ETHBTC_close: 0.02965
BTC_1D_pct: 1.37
ETH_1D_pct: 1.07
ETH_minus_BTC_pp: -0.30
relative_leader: BTC
extended_log_diff_signs: "-+++++--"
rolling_5_session_OLS_approx_pct_per_session: -0.101
source_COND2: 1_OF_LAST_3_NOT_MET
source_classification: CONDITIONS_NO_LONGER_JOINTLY_SATISFIED
```

Source-supplied raw-row SHA-256 claims:

```json
{
  "BTCUSDT": "fa515243e64b4890cec7ea52805b055919ca4e221bc3a6914bd869014dd572b5",
  "ETHUSDT": "08b50b765a29527050ec4b5b19351b00e0674a5e30dfada3b720527dddb4b242",
  "ETHBTC": "9504bd18ee4630f6103bead96d53dc7ea463419d32b95e054703cb05688ca996"
}
```

The raw rows were not transmitted, so these hashes are retained as source claims and were not independently byte-validated.

## ETHBTC threshold sequence

The source reported the UTC daily ETHBTC close for 30 July as 0.02962, with a daily high of 0.02996 and no 0.0300 touch. It classified the arc as `SEQUENCE_TERMINATED`, after one settled acceptance on 28 July followed by rejection and then no touch.

Source response SHA-256 prefix: `0f129607bafe666aab383569a5227626`.

## Post-window claim

The source reported BTC's 31 July intraday low at 62466.00, 0.20% above the higher F1 threshold candidate of 62342 and four sessions after the frozen F1 window closed. It retained the original F1 score and classified this only as `POST_WINDOW_BOUNDARY_STRESS`.

## Hypothesis and QA claims

- H-WIN-01 confidence was raised by the source from low-moderate to moderate, but remains unproven and n=2.
- The source retained explicit counterevidence from the terminated 0.0300 sequence.
- H-SRC-02 received no new observation.
- ETH ETF retrieval failed at the source tool-permission layer.
- Rows 8 and 9 remain annotated as post-FOMC confounded with no causal attribution.

## Source-stated authority boundary

```yaml
framework_state_known_by_source: false
canonical_state_change_claimed: NOT_ASSESSED
portfolio_action_claimed: NOT_ASSESSED
new_entry_permission_claimed: NOT_ASSESSED
```
