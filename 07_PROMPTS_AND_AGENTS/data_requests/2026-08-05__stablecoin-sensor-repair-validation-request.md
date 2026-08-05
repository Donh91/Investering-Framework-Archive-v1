# Targeted DATA PING Validation Request — Stablecoin Sensor Repair

```yaml
request_id: DP-STABLECOIN-VALIDATION-20260805-01
priority: P1_DATA_DEFINITION_REPAIR
trigger: TRR-CIRCLE-ARC-20260805-01
owner: DATA_PING_CUSTOM_GPT
framework_effect: DEFERRED_TO_MAIN_FRAMEWORK
canonical_effect: NONE
portfolio_effect: NONE
```

## Copy-ready prompt

```text
TARGETED DATA PING SENSOR VALIDATION — GLOBAL STABLECOIN SUPPLY + USDC NET ISSUANCE

REQUEST ID
DP-STABLECOIN-VALIDATION-20260805-01

PURPOSE
Resolve a same-day source-definition discrepancy before the framework activates or scores any stablecoin-supply sensor.

A targeted research agent reported on 2026-08-05:
- global stablecoin supply: USD 305.9B;
- USDC supply: approximately USD 72.0–72.2B.

A separate main-thread read of DefiLlama's public stablecoin overview showed:
- global stablecoin market cap: USD 300.384B;
- USDC: USD 72.244B.

The USDC values are directionally consistent, but the global totals differ materially. Determine exactly why.

ROLE
Work only as Collector + Deterministic Feature Extractor + Source-QA Layer.
Do not classify market regime, rotation, liquidity direction, portfolio action or entry permission.
Set:
"framework_interpretation": "DEFERRED_TO_MAIN_FRAMEWORK"

REQUIRED SOURCE CALLS
1. DefiLlama all-stablecoins overview endpoint.
2. DefiLlama global historical stablecoin chart endpoint.
3. DefiLlama USDC-specific historical endpoint using the verified USDC identifier.
4. DefiLlama public stablecoins page or equivalent independently rendered public total.
5. Circle's latest official USDC circulation disclosure as a definition crosscheck only.

REQUIRED DEFINITION AUDIT
For every returned total, identify:
- endpoint and exact request arguments;
- retrieval timestamp UTC;
- source timestamp UTC;
- peg types included;
- stablecoin asset universe;
- whether commodity-, EUR-, JPY- or other non-USD pegs are included;
- treatment of bridged, canonical and third-party representations;
- whether values are summed by token, chain or both;
- price basis and treatment of off-peg assets;
- field path used, including totalCirculatingUSD.peggedUSD where applicable;
- duplicate-removal rule;
- whether the public page and API use the same universe.

REQUIRED CALCULATIONS
A. GLOBAL_STABLECOIN_SUPPLY_TOTAL at the latest common timestamp.
B. USDC_SUPPLY_TOTAL at the latest common timestamp.
C. USDC_SUPPLY_SHARE = USDC / global total using exactly the same universe and timestamp.
D. USDC_NET_ISSUANCE_1D, 7D and 30D using settled daily observations only.
E. GLOBAL_STABLECOIN_NET_CHANGE_1D, 7D and 30D using the same method.
F. Difference between each API-derived total and the public-page total in USD and percent.
G. Difference between DefiLlama USDC and Circle's latest official disclosure, with date alignment stated explicitly.

FAIL-CLOSED RULES
- Do not select the value closest to expectation.
- Do not average conflicting totals.
- Do not combine different peg universes.
- Do not count bridged representations twice.
- Do not compare different timestamps as if simultaneous.
- Do not forward-fill missing daily values without an explicit source rule.
- If the discrepancy cannot be reproduced and explained, return DEFINITION_UNRESOLVED and do not nominate a canonical sensor value.

REQUIRED OUTPUT
1. Executive QA verdict.
2. Endpoint-and-definition matrix.
3. Raw current values and timestamps.
4. Reproducible aggregation formula.
5. Duplicate and peg-type audit.
6. Public-page-versus-API reconciliation.
7. USDC issuer-disclosure crosscheck.
8. Settled 1D, 7D and 30D changes.
9. Exact reason for the USD 305.9B versus USD 300.384B discrepancy, or UNRESOLVED.
10. Recommended deterministic method ID and fallback hierarchy.
11. Source receipts, payload hashes and error evidence.
12. Main-thread reconciliation package.

METHOD NOMINATION RULE
Nominate GLOBAL_STABLECOIN_SUPPLY_TOTAL_v1 and USDC_NET_ISSUANCE_v1 only if:
- the source universe is explicit;
- the same result is reproducible twice;
- API and public-page differences are explained;
- historical values use the same definition as the current value;
- no duplicate representation is detected;
- all timestamps and hashes are preserved.

MAIN-THREAD RECONCILIATION PACKAGE
For every proposed value provide:
- item_id
- field
- value
- unit
- source endpoint
- exact arguments
- field path
- source timestamp
- retrieval timestamp
- universe definition
- duplicate treatment
- direct_or_derived
- method_id
- payload_sha256
- authority_level
- discrepancy versus public page
- discrepancy versus issuer disclosure
- unresolved dependencies
- canonical_effect_claimed: NONE
- portfolio_effect_claimed: NONE
- requires_main_thread_crosscheck: YES

STOP CONDITION
Stop when the discrepancy is deterministically explained or explicitly proven unresolved. Do not broaden into general stablecoin research or market interpretation.
```
