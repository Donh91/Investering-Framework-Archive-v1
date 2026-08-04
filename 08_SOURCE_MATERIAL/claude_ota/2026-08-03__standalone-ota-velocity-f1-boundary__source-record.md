# Claude OTA Source Record — Velocity Flag

```yaml
run_timestamp_utc: 2026-08-03T15:38:36.441Z
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: null
run_type: VELOCITY_FLAG_NOT_FULL_RUN
previous_claude_ota_reference: 2026-08-03T07:51:17.027Z
new_information_count: 1
matured_claude_experiment_count: 0
source_qa_event_count: 1
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Accepted source observations

- BTC 3 August intraday range supplied as 62,300.00 to 63,992.71.
- The 62,300 low was 0.07% below the higher F1 candidate at 62,342 but remained above the lower candidate at 62,200.
- The F1 evaluation window was already closed and its rule used settled closes, not intraday lows.
- No historical F1 score change was claimed.
- ETH/BTC was supplied at 0.02923, below 0.0300 and above 0.0275.
- H-WIN-01 remained UNPROVEN with LOW_MODERATE confidence.
- Cache guard was reported CURRENT_RUN_FRESH across four venues.

## Source boundaries

This was explicitly a velocity flag, not a full OTA run. It contained no reference bridge and did not know framework state. Its market-state claims therefore have no direct framework authority. The later 4 August row-13 OTA report settles the relevant BTC and ETH/BTC observations and supersedes this run for experiment maturity.

The complete user-supplied packet remains in the originating conversation transport.