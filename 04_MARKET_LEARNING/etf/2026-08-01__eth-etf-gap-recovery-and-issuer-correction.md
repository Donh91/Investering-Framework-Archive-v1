# ETH ETF gap recovery and issuer correction

```yaml
source: FARSIDE_ETH_DIRECT_TABLE
source_retrieval_utc: 2026-08-01T05:48:4xZ
source_footer: 31_JULY_2026
authority: DIRECT_SOURCE_REPORTED_BY_CLAUDE_OTA
canonical_effect: NONE
portfolio_effect: NONE
```

## Settled session rows

| Session | Net flow USD m | Status |
|---|---:|---|
| 2026-07-27 | +11.7 | Revalidated previously known row |
| 2026-07-28 | +9.4 | Newly recovered |
| 2026-07-29 | -32.9 | Newly recovered |
| 2026-07-30 | +12.8 | Newly recovered; matches main DATA PING |
| 2026-07-31 | — | Unpublished at retrieval; unknown, not zero |

## Derived structure

```yaml
three_session_sum_usd_m: -9.7
five_session_sum_usd_m: 1.0
seven_session_sum_usd_m: -0.7
interpretation: OSCILLATING_AROUND_ZERO
intensity_claim_supported: NO
directional_flow_claim_supported: NO
```

The net ETH ETF picture through 30 July is effectively flat over seven sessions. Positive and negative sessions alternate, so the evidence does not support sustained institutional accumulation or sustained distribution.

## Issuer correction for 23 July

```yaml
prior_incorrect_claim: ETHA_100_PERCENT_OF_GROSS_POSITIVE_FLOW
corrected_positive_rows_usd_m:
  ETHA: 8.5
  ETHB: 2.9
  FETH: 14.9
corrected_leader: FETH
corrected_share_pct: APPROX_57
error_origin: INCOMPLETE_COLUMN_READ_BY_RESEARCH_SOURCE
farside_source_error: NO
```

Any downstream issuer-concentration analysis must use the corrected FETH-led distribution.

## Product-model addition

The source report identifies ETHB as a BlackRock staking Ethereum ETF and reports a 10% staking fee and a 104.7 million seed. These product attributes are preserved as supplied and remain pending independent issuer-document verification before canonical product metadata use.

## Framework use

```yaml
rotation_confirmation: NO
rebuy_unlock: NO
new_entry_permission: NO
operational_action_change: NONE
```

This file is evidence and source QA, not an independent portfolio signal.