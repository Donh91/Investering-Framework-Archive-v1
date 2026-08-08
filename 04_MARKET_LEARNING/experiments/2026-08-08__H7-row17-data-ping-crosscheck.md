# H7 row 17 — DATA PING crosscheck

```yaml
source_run_id: dp-run-2cdf5d87b6799342dc22
source_snapshot_utc: 2026-08-07T22:37:36.388Z
source_authority: VALIDATED_NON_OWNER_DATA_PING
experiment: H7_transmission_challenger
historical_score_change: NONE
new_signal_event: false
rotation_effect: NONE
```

## Settled CEST row 17 evidence

The 15.3.3 DATA PING supplies settled daily CEST-window values ending `2026-08-07T21:59:59.999Z`:

- BTC: open 64440.74, close 64928.01, return +0.75615209%
- ETH: open 1906.28, close 1916.55, return +0.53874562%
- ETH-minus-BTC spread: -0.21740647 percentage points -> BTC leads row 17
- ETHBTC: open 0.02959, close 0.02952, return -0.23656641%

## H7 follow-through interpretation

Rows 15-17 retain ETH leadership in 2 of the latest 3 rows because rows 15 and 16 were ETH-led while row 17 is BTC-led. Therefore source-level COND2 remains 2/3 MET.

However row 17 does not provide a second consecutive clean follow-through day for the row-16 joint requalification. ETHBTC fell from 0.02959 to 0.02952. Under the stricter latest-three interpretation of COND1 that requires both recent sequential changes to remain positive, the latest-three condition is no longer jointly satisfied; the historical/existence reading remains previously satisfied. This renewed wording divergence is not used to rescore H7.

Main-thread lifecycle governance remains controlling:

- row 16 = `JOINT_CONDITION_REQUALIFICATION_FOLLOW_THROUGH`
- row 17 = `MIXED_FOLLOW_THROUGH_BTC_LED_WITH_COND2_STILL_2_OF_3`
- no retrigger semantics were preregistered
- no new H7 signal event
- no rotation permission
- historical maximum label remains `EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`

This row supports keeping H7 as prospective learning evidence rather than upgrading it into a decision trigger.