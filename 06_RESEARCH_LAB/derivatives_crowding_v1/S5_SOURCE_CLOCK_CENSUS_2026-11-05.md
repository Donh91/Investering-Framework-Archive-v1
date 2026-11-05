# S5 Source Clock and Coverage Census | 2026-11-05

**Status:** REPRODUCED_STATIC_CAPTURE_CENSUS / FIRST_KNOWN_UNVERIFIED / RESEARCH_ONLY  
**Owner:** existing [#1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512) S5 lane, original implementation [#1514](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1514) closed/merged [#1515](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1515).  
**Method intake:** [PR #1934](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1934), now merged and exact main read back at commit `56659cb4222efcd028c9cb9d254391309a3505b6`.  
**Source baseline:** public GitHub blob identities below, as read from current Archive main on 2026-11-05. No restricted data accessed, no paid source, no live market changes.

## Actual first bounded experiment: source-clock and 24h coverage audit

The existing S5 transformer implements a legitimate source-agnostic 1h/4h/12h/24h **descriptive** derivative feature computation: price, spot/futures taker imbalance, OI value delta, basis and settled funding. The prior [S5 execution receipt](../../04_RESEARCH_LAB/external_specialist_dissection/S5_EXECUTION_RECEIPT_2026-10-06.md) correctly states `BASELINE_MERGED / PROSPECTIVE_GRADING_PENDING`, **not** that any forecast edge is proved.

Read public fixtures by exact Git blob:

| Parameter | BTCUSDT | ETHUSDT |
| --- | ---: | ---: |
| Source capture fixture blob | `9e90465cd3f2bf7f770a8e7397193404a56767c8` | `3f14f9588f53c50e4e0c254ef8ae462cd37b3b60` |
| Original date label | 2026-10-06 | 2026-10-06 |
| Decision cutoff | 2026-10-06T08:00:00Z | 2026-10-06T08:00:00Z |
| Spot rows / before cutoff / at-or-after | 30 / 29 / 1 | 30 / 29 / 1 |
| OI rows / before cutoff / at-or-after | 30 / 29 / 1 | 30 / 29 / 1 |
| Futures taker rows / before cutoff | 30 / 30 | 30 / 30 |
| Basis rows / before cutoff | 30 / 30 | 30 / 30 |
| Funding events / before cutoff / at-or-after | 10 / 9 / 1 | 10 / 9 / 1 |
| Missing required hourly timestamps, 24h spot/OI baseline and taker/basis flow | **0** | **0** |
| Explicit capture `captured_at_utc` or retrieval instant | **ABSENT** | **ABSENT** |
| Provider first-publication clock per row across five sources | **0** | **0** |
| Explicit retrieval clock per row across five sources | **0** | **0** |

**Interpretation:** The 24h census checks exactly the source rows consumed by the current S5 feature transformer: **25 spot hourly timestamps** (including the price baseline), **two OI endpoints**, **24 futures-taker hours**, and **one latest basis hour**. It does not falsely require unused intermediate OI or basis values. Both files are complete 24h *fixture-calculation inputs*. Neither fixes the provider's contemporaneous publication clock, end-to-end knowledge time, immutable original capture receipt, or an eligible independent outcome population. A historical candle timestamp is NOT proof the candle, OI value or funding rate was accessible at that timestamp. Funding settlement time is not an announcement/publication timestamp. The at-or-after-cutoff rows must be rejected from as-of features as the existing transformer already does.

The new read-only `scripts/research/s5_source_clock_census_v1.py` enumerates coverage and self-declared clocks, without granting scientific admission. It explicitly emits:
- `capability_24h_window_state=COMPLETE` for these fixture shapes;
- `source_clock_state=UNVERIFIED_FIRST_KNOWN`;
- `independent_provider_first_known_verified=false`;
- `prospective_pit_admitted=false`;
- `economic_edge_claim=NOT_ESTIMABLE`.

This is by design: **a self-declared timestamp in an unverified file can never independently certify historic provider availability.** The program is a value-free diagnostic, not a PIT adjudicator or collector.

## Reproducibility and negative controls
```bash
python -m unittest tests.experiments.test_derivatives_crowding_features_v1 -v
python scripts/research/s5_source_clock_census_v1.py --input 06_RESEARCH_LAB/derivatives_crowding_v1/fixtures/BINANCE_BTCUSDT_2026-10-06.json --git-blob-sha 9e90465cd3f2bf7f770a8e7397193404a56767c8
python scripts/research/s5_source_clock_census_v1.py --input 06_RESEARCH_LAB/derivatives_crowding_v1/fixtures/BINANCE_ETHUSDT_2026-10-06.json --git-blob-sha 3f14f9588f53c50e4e0c254ef8ae462cd37b3b60
```

Seven additional tests cover complete fixture with NO PIT proof, missing 24h baseline, self-declared fake publication clocks, duplicate hourly timestamp, naive cutoff, empty funding, and removal of unconsumed OI/basis hourly rows. Existing S5 CI workflow already runs this test module on its changed path; new workflow/cron not needed. Local detached test logic passed 7/7 before GitHub submission; **GitHub CI and independent review must be independently checked on this PR head**, never presumed.

## Exact next decision and blocking trigger, no parking
1. **Terminal disposition for current public historic fixtures:** `SOURCE_CLOCK_UNVERIFIED` / `INSUFFICIENT_PROSPECTIVE_EVIDENCE`; do not calculate directional or economic skill, do not promote a vendor/flow label as market rule.
2. **Existing S5/M6 prospective lane trigger:** first *new* contemporaneously frozen BTC/ETH source vector with immutable and externally checkable source/retrieval/publication or completion evidence, exact symbol/venue/schema/24h coverage and original decision/delivery clock; restricted raw values stay in the restricted data plane. Do not backfill pseudo-first-known onto historical fixture.
3. **Next one bounded H2 experiment only after trigger:** preregister price-only vs S5 full-vector paired 24h/72h/7d outcomes with equal availability and lag, unique pullback episode families, first-known and next-bar execution, fees/slippage, no-leakage controls; no cross-asset/triple-vote pseudo-independent observations. Any negative/null result is retained, no automatic production signals.
4. **H1 decision economics:** existing `scripts/learning/decision_economics_ledger.py` already implements a shadow-only Action Ledger. Do NOT build a second Ghost-like scorekeeper; #1596/#1157 must audit actual eligible freeze coverage and delivery/fill rather than infer costs from reconstructed daily snapshots.
5. Reconfirm latest S5 source coverage and future private receipts only through source authority and existing owners. Private values and unapproved source APIs are out of this public census.

**Explicit verdict:** `SIMPLER_REPLAY_WORKS / PREDICTIVE_EDGE_UNKNOWN / ACTION_EDGE_NOT_ESTIMABLE`. No new indicator weight, forecasting engine, source subscription, auto trade, or scheduler. Public file size and row counts are source diagnostics, not market observations usable as prospective N.
