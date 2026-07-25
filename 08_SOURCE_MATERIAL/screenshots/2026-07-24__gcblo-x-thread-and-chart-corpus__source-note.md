# GCBLO X Thread and Chart Corpus

**Dato:** 2026-07-24  
**Status:** SOURCE_NOTE  
**Område:** external macro-liquidity source / Bitcoin timing claim  
**Primary folder:** `08_SOURCE_MATERIAL/screenshots/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `04_MARKET_LEARNING/macro_shadow/`  
**Depends on:** user-supplied screenshots and source URL  

## Source identity

```yaml
source_account_display: At the Bitcoin Frontier
source_handle_visible: @thebtcfrontierX
source_url: https://x.com/thebtcfrontierx/status/2080763618229146099
source_date_visible: 2026-07-24
historical_post_date_visible: 2025-10-07
indicator_name_visible: Global Central Banks Liquidity Oscillator (W) (Adjustable)
indicator_abbreviation_used: GCBLO
source_evidence_class: SOURCE_BACKED_NOT_OUTCOME
formula_code_available: NO
settings_export_available: NO
machine_readable_series_available: NO
```

## Screenshot integrity ledger

The following user-supplied images were inspected as the source corpus. Hashes are local upload hashes, not hashes of the original X-hosted media.

| File | SHA-256 |
|---|---|
| `96ECBB41-C399-44A7-918E-8C1E03F14696.png` | `340fe8f16cf7e93e7d423949a00f01e24d3937467eb59d7079e8038a028eea27` |
| `706650F6-FB7D-4E96-97F8-AAAD8D432631.png` | `595cfc2fdcbec060f1d6b0610538f9d2156a3a44412cac9bf770b246538ac299` |
| `18D5BE64-E755-43AF-98D0-C00A7C2E22F1.png` | `0b3dd272e144d70aa6bcae06f5fca0422c640270be2f9676ede5b036261f9a2a` |
| `ECC9E598-04FB-4B75-BBE0-3C13C80A35A6.png` | `5ae5508599232479351d6aa0775109b04bd1d21c7a1ba23a2e496b5478ed9c38` |
| `68F301CD-9FC0-403C-BF30-B51310058EBB.png` | `a4bc4a21b5a1e3cd412ef6d44fb95485bd5dd2b7ef096173210ac6657d1e39dd` |
| `76848584-19F6-47D9-B69C-0FC9B72D3770.png` | `5c4ce2f3b42b1fb1bbeaf8542e3aec3ab05e2c442d887bd6a5fd729771ebd81b` |
| `13628074-7094-4382-AFB9-0181F23AAB57.png` | `4573eada1a256d60411ee655926309a119bc9dd255ab5cca21c1f85b4a6884f0` |
| `FC8D635F-C650-426D-9495-6E86E6A6DB92.jpeg` | `f21fdebdfcda61a1582130e52996f35a74ba4e865458e04f75a7c583c649dfd2` |
| `69D63AEB-BB75-4BF0-AFF9-3D06259F6DEA.jpeg` | `93307bdbea1681d89a3534e31568d2747cd2dd882c7c85b3f93ffe2835444371` |

## Claims transcribed from the source

### Construction claim

The source describes the indicator as a normalized composite of central-bank balance-sheet dynamics and financial-system drains.

Expansion variables shown:

```text
Federal Reserve total assets
European Central Bank total assets
Bank of Japan total assets
```

Drain variables shown:

```text
Treasury General Account, TGA
Reverse Repo Facility, RRP
```

Transformations described:

```text
1. first difference / delta operator
2. z-score standardization
3. weighted composite aggregation
4. EMA low-pass smoothing
5. arctangent nonlinear bounding
```

### Threshold interpretation claim

The source states approximately:

```text
above +86 after a halving:
final high-liquidity / risk-on phase

cross below +86 after the post-halving rise:
final Bitcoin cycle-top marker in liquidity terms

rapid move below -80:
last warning / final exit opportunity before bear market

cross back above -80:
new Bitcoin bull-market or re-entry phase in liquidity terms
```

### Historical timing claim

The source claims that an October 7, 2025 post identified the macro regime change one day after Bitcoin's October 6, 2025 price high.

The historical screenshot shows approximately:

```text
GCBLO: 87.27
BTC chart value: 123,735
visible date: 2025-10-07
```

### Current re-entry claim

The July 24, 2026 source states that the liquidity bottom is in and labels the current configuration as re-entry, at least from the indicator's liquidity perspective.

The current screenshot shows approximately:

```text
GCBLO: -78.37
BTC chart value: 64,186
visible interpretation: RE-ENTRY
```

## What the source does not supply

The source corpus does not disclose:

- exact data-series identifiers;
- currency-conversion method;
- release calendar and as-of timing;
- historical vintage policy;
- weekly alignment rule;
- difference horizon;
- z-score lookback;
- weights and signs in executable form;
- EMA length;
- arctangent scale parameter;
- threshold-selection method;
- threshold sensitivity;
- exact date and timestamp of every historical crossing;
- TradingView export;
- executable Pine code;
- a complete pre-registered backtest;
- false-positive or false-negative counts;
- transaction, tax, delay or opportunity-cost analysis.

## Public cross-reference

A TradingView community listing independently confirms that an indicator with the exact visible name exists and describes it as a standardized, smoothed aggregate of major central-bank balance sheets and policy flows. The listing does not, from the accessible description, resolve the missing implementation details above.

## Evidence boundary

```text
SOURCE CLAIMS: PRESERVED
FORMULA: NOT VERIFIED
THRESHOLDS: NOT VERIFIED
HISTORICAL LABELS: NOT VERIFIED AS EX-ANTE
CURRENT RE-ENTRY: NOT A FRAMEWORK SIGNAL
OUTCOME STATUS: UNSCORED
PORTFOLIO AUTHORITY: ZERO
```
