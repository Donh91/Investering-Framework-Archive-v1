# Framework Reconciliation — DP-STABLECOIN-VALIDATION-20260805-01

```yaml
reconciled_at_utc: 2026-08-05T21:36:00Z
qa_verdict: DEFINITION_UNRESOLVED
leading_explanation: NOMINAL_SUPPLY_VERSUS_PRICE_ADJUSTED_MARKET_VALUE
method_nomination_authorized: false
canonical_sensor_activation: NOT_AUTHORIZED
canonical_state_change: NONE
portfolio_effect: NONE
```

## What was learned

The USD 305.9B versus USD 300.384B discrepancy is no longer an undifferentiated source conflict. The validation identified a concrete, source-supported definition split:

```yaml
totalCirculating.peggedUSD: nominal circulating units for USD-pegged assets
totalCirculatingUSD.peggedUSD: price-adjusted USD market value
```

DefiLlama's public headline and SDK treat the second quantity as stablecoin market cap. A separate USDC page render also displayed different values for market cap and total circulating. This makes nominal-versus-price-adjusted treatment the leading explanation for the global discrepancy.

## Why the explanation is not promoted to fact

The original research-agent value of USD 305.9B cannot be traced to a preserved raw payload. Its endpoint, field path, timestamp, asset universe, duplicate rule and hash are missing. The raw global and historical endpoints could not be retrieved within the targeted validation runtime.

Therefore:

- the hypothesis is stronger;
- the discrepancy is better classified;
- the exact cause remains unproven;
- no baseline or historical delta is admitted.

## Sensor decision

The earlier sensor-design ratification remains valid, but activation remains blocked.

```yaml
GLOBAL_STABLECOIN_SUPPLY_TOTAL:
  design_status: ACCEPTED
  value_status: QUARANTINED
  activation: BLOCKED_DEFINITION_UNRESOLVED

USDC_NET_ISSUANCE:
  design_status: ACCEPTED
  activation: BLOCKED_RAW_SETTLED_HISTORY_UNAVAILABLE

USDC_SUPPLY_SHARE:
  design_status: ACCEPTED
  activation: BLOCKED_COMMON_UNIVERSE_AND_TIMESTAMP_UNRESOLVED
```

## Required metric separation

Future collectors must emit separate, explicitly named quantities:

1. `GLOBAL_USD_PEGGED_NOMINAL_SUPPLY`
2. `GLOBAL_USD_STABLECOIN_MARKET_CAP_PRICE_ADJUSTED`
3. `USDC_NOMINAL_CIRCULATION`
4. `USDC_MARKET_CAP_PRICE_ADJUSTED`

No process may silently substitute one for another. USDC share must declare whether both numerator and denominator use nominal supply or price-adjusted market-cap basis.

## Public-page value

The rendered page supports a QA-only market-cap share:

```yaml
USDC_market_cap: 72.244B
Global_stablecoin_market_cap: 300.384B
USDC_market_cap_share_pct: 24.050548631086
method: SAME_RENDERED_PAGE_MARKET_CAP_BASIS
market_gate_permission: NO
```

This value is not a settled API owner and cannot be used longitudinally.

## Immediate follow-up classification

```yaml
broad_deep_research_required: NO
narrow_source_provenance_followup_required: YES
owner: CLAUDE_ORIGINAL_RESEARCH_RUN
reason: ONLY_THE_ORIGINAL_RESEARCH_AGENT_CAN_SUPPLY_OR_RETRACT_THE_MISSING_305_9B_RAW_LINEAGE
collector_engineering_required: YES
reason_2: RAW_ENDPOINTS_EXCEEDED_CURRENT_RUNTIME_LIMITS
```

## Market separation

The latest bounded market observation remains `run-e841c63ea8e04a028918`. Stablecoin validation does not change its interpretation because no accepted stablecoin value or delta was produced.
