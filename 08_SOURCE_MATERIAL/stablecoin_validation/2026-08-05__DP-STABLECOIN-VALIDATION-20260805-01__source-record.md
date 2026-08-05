# Targeted Stablecoin Validation Source Record

```yaml
request_id: DP-STABLECOIN-VALIDATION-20260805-01
collection_upper_bound_utc: 2026-08-05T21:21:16Z
qa_status: DEFINITION_UNRESOLVED
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
canonical_sensor_activation: NOT_AUTHORIZED
```

## Question tested

Resolve the same-day discrepancy between:

- research-agent global stablecoin supply: USD 305.9B;
- DefiLlama public stablecoin market cap: USD 300.384B.

## Direct rendered observations

```yaml
DefiLlama_public_global_market_cap_usd: 300384000000
DefiLlama_public_USDC_market_cap_usd: 72244000000
Circle_USDC_circulation_usd: 72000000000
Circle_value_date: 2026-08-03
```

A later DefiLlama USDC detail render separately displayed approximately USD 72.253B market cap and 72.273B total circulating, demonstrating that the source distinguishes price-adjusted market value from circulating units.

## Leading explanation

```yaml
higher_value_candidate_field: totalCirculating.peggedUSD
lower_value_documented_field: totalCirculatingUSD.peggedUSD
economic_difference: NOMINAL_SUPPLY_VERSUS_PRICE_ADJUSTED_MARKET_VALUE
reported_minus_public_usd: 5516000000
reported_minus_public_pct: 1.836316181954
proof_status: NOT_DETERMINISTICALLY_PROVEN
```

DefiLlama's SDK and schema distinguish nominal circulating quantity from price-adjusted USD market value. The official SDK uses `latest.totalCirculatingUSD.peggedUSD` as total stablecoin market cap.

## Why the question remains unresolved

The original USD 305.9B research observation lacks:

- raw endpoint response;
- exact endpoint arguments;
- field path;
- source timestamp;
- peg universe;
- asset membership;
- duplicate/bridged representation rule;
- raw payload SHA-256.

The candidate raw endpoints were too large or unavailable in the validation runtime. No settled historical series was retrieved and hashed.

## Method nominations

```yaml
GLOBAL_STABLECOIN_SUPPLY_TOTAL_v1: WITHHELD
USDC_NET_ISSUANCE_v1: WITHHELD
USDC_SUPPLY_SHARE_v1: WITHHELD
```

## Accepted QA-only derived value

Using the same rendered public-page market-cap basis:

```yaml
USDC_public_page_market_cap_share_pct: 24.050548631086
method_id: USDC_PUBLIC_PAGE_MARKET_CAP_SHARE_QA_ONLY_v0
market_use_permission: NO
```

## Required future separation

```yaml
NOMINAL_USD_PEGGED_SUPPLY:
  field: totalCirculating.peggedUSD
PRICE_ADJUSTED_USD_STABLECOIN_MARKET_CAP:
  field: totalCirculatingUSD.peggedUSD
rule: NEVER_SUBSTITUTE_OR_MERGE_THE_TWO
```

## Final result

```yaml
discrepancy_status: DEFINITION_UNRESOLVED
leading_explanation: TOTAL_CIRCULATING_NOMINAL_VERSUS_TOTAL_CIRCULATING_USD_PRICE_ADJUSTED
method_nomination_authorized: false
canonical_effect: NONE
portfolio_effect: NONE
```

The complete user-supplied validation report remains preserved in the originating conversation transport.