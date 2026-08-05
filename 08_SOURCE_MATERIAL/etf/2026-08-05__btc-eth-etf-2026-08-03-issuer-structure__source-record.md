# ETF Source Record — 3 August 2026 BTC and ETH

```yaml
session: 2026-08-03
latest_session_total_authority: DATA_PING_DIRECT_OWNER
issuer_detail_authority: USER_SUPPLIED_CLAUDE_OTA_FRESH_FARSIDE_PAYLOAD
main_thread_independent_issuer_retrieval: false
```

## Direct settled totals

```yaml
BTC_total_usd_m: 170.1
ETH_total_usd_m: -11.9
```

These totals were already recorded by the valid bounded DATA PING owner `run_18f02b7aa0334c9e` and are corroborated by both Claude OTA reports.

## Issuer structure supplied by Claude OTA

### BTC

```yaml
positive_tickers: 8
negative_tickers: 0
IBIT: 111.4
FBTC: 33.4
EZBC: 9.2
BTCO: 6.7
HODL: 4.5
BITB: 2.8
ARKB: 2.1
```

### ETH

```yaml
positive_tickers: 1
ETHA: -9.0
ETHE: -7.8
FETH: -0.9
ETHB: 5.8
```

The issuer values are preserved as user-supplied fresh-payload evidence. They were not independently retrieved by the main thread.

## Cross-asset structure

```yaml
BTC_total_sign: POSITIVE
ETH_total_sign: NEGATIVE
IBIT_sign: POSITIVE
ETHA_sign: NEGATIVE
interpretation_boundary: BTC_ABSORPTION_WITHOUT_ETH_TRANSMISSION
```

The same-session opposite signs support the existing weak-transmission classification. They do not independently authorize a rotation, entry or portfolio change.

## 31 July provenance resolution

The Claude OTA reports that the fresh 4 August Farside generation reproduced the archived 31 July BTC total and issuer breakdown exactly:

```yaml
BTC_2026_07_31_total_usd_m: -265.4
reverification_status: USER_SUPPLIED_FRESH_GENERATION_MATCH
revision_detected: false
```

## Phantom-session correction

`ETH-ETF 1/8` is cancelled from unresolved provenance. 1 August 2026 was a Saturday and no US ETF trading session existed.

## Rolling-window reproducibility

Owner-window calculations use the archived direct row payload through 31 July plus the direct settled 3 August totals.

```yaml
BTC_3_session_usd_m: 137.8
BTC_5_session_usd_m: 120.2
BTC_7_session_usd_m: -131.5
BTC_10_session_usd_m: -84.3
BTC_20_session_status: UNAVAILABLE_ONLY_14_ROWS
ETH_3_session_usd_m: 9.9
ETH_5_session_usd_m: -13.6
ETH_7_session_usd_m: -72.6
ETH_10_session_usd_m: 63.9
ETH_20_session_status: UNAVAILABLE_ONLY_14_ROWS
```

The following OTA rolling-window claims are not reproducible from the repository's direct row ledger and remain quarantined:

```yaml
OTA_BTC_5_session_claim_usd_m: 108.3
OTA_BTC_20_session_claim_usd_m: -100.8
OTA_ETH_3_session_claim_usd_m: 10.6
OTA_ETH_5_session_claim_usd_m: -13.7
OTA_ETH_7_session_claim_usd_m: -16.9
```

The directly reproducible windows retain owner authority.