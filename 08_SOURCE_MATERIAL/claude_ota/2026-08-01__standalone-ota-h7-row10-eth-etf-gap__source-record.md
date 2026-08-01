# Claude OTA source record — H7 row 10 and ETH ETF recovery

```yaml
source_run_timestamp_utc: 2026-08-01T05:48:32.902Z
operating_mode: STANDALONE_OTA
reference_bridge_present: NO
reference_data_ping_run_id: NOT_PROVIDED
source_authority: NONCANONICAL_RESEARCH_AND_AUDITOR_INPUT
canonical_effect_claimed_by_source: NONE
portfolio_effect_claimed_by_source: NONE
```

## Supplied incremental claims

1. H7 row 10 settled CEST values:
   - BTCUSDT 62947.78
   - ETHUSDT 1861.81
   - ETHBTC 0.02957
   - COND2 last-three ETH leadership count 0 of 3
   - rolling five-session OLS slope approximately -0.395% per session
2. ETH ETF rows from Farside:
   - 2026-07-27 +11.7 million USD
   - 2026-07-28 +9.4 million USD
   - 2026-07-29 -32.9 million USD
   - 2026-07-30 +12.8 million USD
   - 2026-07-31 unpublished at retrieval
3. ETHB added to the source column model; source reports 10% staking fee and 104.7 million seed.
4. Prior source claim that ETHA represented 100% of 23 July gross inflow was self-corrected to ETHA 8.5, ETHB 2.9 and FETH 14.9 million USD, making FETH approximately 57% of the listed gross positive flow.
5. H-SRC-02 strong time-of-day form self-falsified by a fresh Farside payload retrieved at 05:48 UTC.
6. H-WIN-01 source confidence reduced from MODERATE to LOW_MODERATE after the 31 July intraday threshold approach was not sustained into the close.
7. ETHBTC 0.0300 sequence remained terminated with no reported touch on 30 July, 31 July or the in-progress 1 August session.

## Source receipts supplied

```yaml
BTCUSDT_row10_sha256: 98a7f856c5c8ec5800c892d4dbba3e2ea6c303e400ff064a2a1010e67774a48e
ETHUSDT_row10_sha256: d21aa77fedfa6f12a05ca0544f49a4031acd3e9cc602b006cd27874bff4812ea
ETHBTC_row10_sha256: 8f01513bc19c471df95ad18f323bdab015aec48eae86d60896f8a86c4d0934d4
ETHBTC_threshold_source_hash: da1826e68d81424fb98d137db6d78fbd
```

This record preserves the supplied report. Framework corrections and authority boundaries are recorded separately.