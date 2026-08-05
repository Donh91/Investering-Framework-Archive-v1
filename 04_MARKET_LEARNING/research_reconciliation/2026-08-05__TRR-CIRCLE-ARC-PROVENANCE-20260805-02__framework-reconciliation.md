# Stablecoin Provenance Reconciliation

```yaml
request_id: TRR-CIRCLE-ARC-PROVENANCE-20260805-02
verdict: ACCEPT_METHOD_RECOVERY_AND_CORRECTIONS_RETAIN_FAIL_CLOSED
canonical_effect: NONE
portfolio_effect: NONE
```

## Proven

The original rounded value came from the DefiLlama global chart endpoint and the field `totalCirculatingUSD.peggedUSD` in the row dated 2026-08-05 UTC. It was a direct price-adjusted USD-peg aggregate, not a local asset or chain sum.

## Corrected

- The row was still in progress when read and later revised. The rounded 305.9B value is withdrawn as a settled observation.
- The original raw payload hash and exact retrieval timestamp were not preserved.
- Nominal-versus-price-adjusted semantics are real, but their observed spread was about 0.17B and does not explain the roughly 5.52B difference from the rendered public page.
- The original USDT and USDC shares are withdrawn because their components and denominator came from a different endpoint and field basis than the headline total.

## Mandatory method rules

```yaml
settlement_rule: LATEST_COMPLETED_UTC_DAILY_ROW_ONLY
in_progress_daily_rows: FORBIDDEN
price_adjusted_field: totalCirculatingUSD.peggedUSD
companion_nominal_field: totalCirculating.peggedUSD
cross_endpoint_share_calculation: FORBIDDEN
raw_payload_sha256: REQUIRED
repeat_fetch_count: 2
public_page_role: QA_ONLY
```

## New QA candidate

The research reports the completed 2026-08-04 row at approximately 305.8608B USD from the price-adjusted field, using reproduced payload hash `b215b5b4ab7b7ee15f301a53480476ca695f9b0f7b723e088dd0eba47c974910`.

This remains QA-only because the rendered public page, the chart aggregate and the asset-level sum still disagree, and source duplicate handling is not independently documented.

## Remaining work

The remaining task is deterministic collector engineering under issue #315: bounded raw capture, completed-row selection, dual-field capture, repeated hashes and same-basis reconciliation across endpoints.

```yaml
RESEARCH_ESCALATION: NO
reason: PROVENANCE_STOP_CONDITION_MET_REMAINING_WORK_IS_ENGINEERING
GLOBAL_STABLECOIN_SUPPLY_TOTAL_v1: WITHHELD
USDC_NET_ISSUANCE_v1: WITHHELD
USDC_SUPPLY_SHARE_v1: WITHHELD
```
