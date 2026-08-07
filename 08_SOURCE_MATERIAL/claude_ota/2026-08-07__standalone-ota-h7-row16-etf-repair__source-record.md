# Claude OTA source record — H7 row 16 / ETF repair

```yaml
source_run_timestamp_utc: 2026-08-06T23:03:54.029Z
source_run_timestamp_cest: 2026-08-07T01:03:54+02:00
operating_mode: STANDALONE_OTA
reference_bridge_present: false
reference_data_ping_run_id: null
previous_claude_ota_reference: 2026-08-06T07:49:36.027Z
canonical_effect_claimed: NONE
portfolio_effect_claimed: NONE
requires_main_thread_crosscheck: YES
```

## Source-supplied load-bearing claims

### H7 row 16

Claude reports row 16 as directly settled CEST evidence:

- BTCUSDT close `64440.74`
- ETHUSDT close `1906.28`
- ETHBTC close `0.02959`
- BTC 1D `-0.45%`
- ETH 1D `-0.13%`
- spread `+0.32pp`, ETH leads
- COND1 MET under both supplied readings
- COND2 MET `2/3`
- COND3 MET
- five-session OLS slope reported `-0.030%/session`
- first joint condition satisfaction since row 8
- retrigger/lapse semantics explicitly `UNDEFINED_IN_RULE`; Claude did not declare a new signal event.

Raw row hashes supplied:

- BTCUSDT `5c71be2e5c56ee7fc1c002d0c7dcc287d244f5ac794460e39ce19fe882aea88b`
- ETHUSDT `fa41a46e2dc618587c6556dab92d5d7e1b930ad8c7a640e3c59f70851c20a82c`
- ETHBTC `008e1db68d8025bcec1d2c0844bb4da96af3a00729bc5cafcd516fdfb65b7804`

Maximum source label: `EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`.

### ETH ETF rows

Claude reports direct Farside values:

- 2026-08-04 ETH `+53.1M USD`
- 2026-08-05 ETH `+60.8M USD`

The source states both sessions were ETHA-led and withdraws its prior anti-transmission characterization.

Claude-derived rolling claims:

- ETH 3-session `+102.0M`
- ETH 5-session `+123.9M`
- ETH 7-session `+91.1M`
- claimed ETH 5- and 7-session totals exceeded stale/asynchronous BTC windows.

These derived cross-asset claims require main-thread reconciliation and are not source-owner facts.

### Threshold / F1

- ETHBTC 2026-08-06 was still in progress in the source run and had not touched `0.0300`.
- F1 follow-through remained non-scoring design evidence.

## Creative extension — quarantined from H7

Claude supplied CE-01/CE-02 methodology observations about null-frequency and possible dependence of ETH-minus-BTC spread on absolute BTC daily movement. They are explicitly `EXPLORATORY_NOT_PREREGISTERED`, small-sample and post-hoc. They are retained only as future experiment-design backlog and must not alter H7 scoring or current market state.

## Main-thread external crosscheck performed 2026-08-07

Farside direct pages confirmed the ETH 4/8 and 5/8 daily totals. Current pages also displayed a newer 6/8 row:

- BTC 2026-08-06: `+137.6M USD`
- ETH 2026-08-06: `+92.1M USD`

The 6/8 values are current web crosscheck observations only until the framework's direct-owner two-retrieval validation procedure is completed.
