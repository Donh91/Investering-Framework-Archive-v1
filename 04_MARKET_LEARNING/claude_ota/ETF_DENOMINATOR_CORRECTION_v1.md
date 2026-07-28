# ETF denominator correction v1

```yaml
status: RATIFIED_SOURCE_QA_CORRECTION
identified_at_utc: 2026-07-28T18:49:39.660Z
origin: CLAUDE_STANDALONE_OTA
adjudicated_by: CHATGPT_MAIN_FRAMEWORK
canonical_market_state_effect: NONE
portfolio_effect: NONE
```

## Defect

The Farside final `Total` row was previously interpreted as ETF assets under management.

That interpretation is incorrect. The table is a historical flow table. Its final row contains cumulative historical net-flow totals by fund and for the combined complex.

The following calculations are withdrawn as AUM-normalized metrics:

```yaml
BTC_7_session_flow_div_false_AUM: 0.301_percent
ETH_7_session_flow_div_false_AUM: 1.356_percent
ETH_relative_multiple: 4.5x
```

They were calculated against cumulative net-flow totals, not AUM.

## Why the error matters

Cumulative net flow is not a valid size denominator. It can be heavily distorted by legacy outflows. In the BTC table, GBTC's large cumulative negative flow reduces the combined net-flow total and therefore distorts any ratio that treats it as asset size.

The previous multiple is not merely noisy. Its denominator represents the wrong economic quantity.

## Permanent rule

Any ETF flow normalization must preserve:

```yaml
numerator_window:
denominator_type: TRUE_AUM_OR_NET_ASSETS
denominator_source:
denominator_valuation_date:
funds_included:
funds_missing:
share_class_treatment:
formula:
source_timestamp:
retrieval_timestamp:
revision_status:
```

Forbidden denominators for `flow_pct_AUM`:

- cumulative net flow;
- market value without fund-level coverage;
- stale AUM without a valuation date;
- estimated AUM derived from price times unverified shares;
- mixed-date AUM across funds without disclosure.

## Current status

```yaml
true_BTC_ETF_AUM: UNKNOWN
true_ETH_ETF_AUM: UNKNOWN
size_normalized_flow_comparison: QUARANTINED
absolute_multi_session_flow: ALLOWED_WITH_ROW_LINEAGE
issuer_concentration: ALLOWED_WITH_COMPLETE_FUND_ROWS
```

This correction does not change any closed experiment or current framework state.