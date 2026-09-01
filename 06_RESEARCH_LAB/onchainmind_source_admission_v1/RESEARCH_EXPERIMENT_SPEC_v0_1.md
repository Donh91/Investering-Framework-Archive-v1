# Public On-Chain Source Admission Research Experiment v1

Status: `EXECUTED TRIAGE + PROSPECTIVE SHADOW CONTRACT`

## Research question

Can public/reproducible on-chain or expectations data add decision-relevant information beyond simple BTC price/trend and existing framework owners without creating duplicate confirmation, rights violations, or pseudo-evidence?

## Evidence classes

1. **Retrospective exploratory research** - may rank or kill candidates, never promotes them.
2. **Prospective state observation** - may produce immutable derived receipts, but is not a prediction unless a separate forward-test contract exists.
3. **Prospective evidence** - forbidden here unless the canonical ledger/schema/maturity contract is explicitly satisfied.

## Executed MVRV challenger replay

Sample:

- 48 month-end observations, 2022-09 through 2026-08.
- BTC price baseline: transient Binance BTCUSDT monthly klines.
- MVRV challenger: transient BGeometrics month-end observations.
- Provider raw rows were not committed.

Causal features available at each observation:

- baseline: 1-month price return, 3-month price return, 6-month drawdown from recent high,
- challenger additions: MVRV level and 1-month MVRV delta.

Method:

- expanding walk-forward,
- fixed minimum training set: 18 observations,
- ridge regularization sensitivity: alpha 1, 10, 100,
- target horizons: 1 and 3 rows/months,
- no threshold mining.

Predeclared admission gate for this bounded triage:

- challenger must improve MAE by at least 5%,
- challenger must improve direction accuracy by at least 5 percentage points,
- improvement must not disappear under reasonable fixed regularization sensitivity.

Result:

`NO_ROBUST_INCREMENTAL_PREDICTIVE_VALUE`

MVRV sometimes improved MAE, especially on the 3-month target, but never improved directional accuracy under the tested sensitivity set. It therefore fails predictive admission.

Descriptive context remains useful: MVRV below 1.2 coincided with stronger subsequent returns in this small sample, but the count is too small and regime-specific to promote. Treat it as valuation/stress context only.

## Cross-source source-family check

Five sampled month-end MVRV observations from BGeometrics and the pinned Coin Metrics Community archive differed by about 1.9% mean absolute percentage. They are close but not identical.

Rule:

- never silently mix provider methodologies,
- pin the source family and exact reference for every research run.

## Data-quality kills

Two extraction paths were rejected before use:

- the structured BGeometrics BTC-price extraction repeated historical values across different years,
- the structured SOPR extraction returned completeness metadata that contradicted its own rows.

These findings identify an extraction/tooling path failure. They do not prove corruption of the provider's raw source data.

## URPD prospective observation

URPD is not admitted as a predictor.

It may produce only derived, non-actionable Stress & Structure features:

- supply near spot,
- supply immediately below/above spot,
- above/below asymmetry,
- nearest dense cost-basis bin,
- nearest low-density/vacuum bin,
- normalized cost-basis concentration entropy.

Critical lineage rule:

The current `UrpdDay` schema contains bin fields but does not embed the snapshot date in each row. The requested `day` must therefore be bound into the receipt together with the payload hash and externally-settled BTC spot.

Retention rule:

Recent dated snapshots are supported, but no long-history claim is permitted. A 2026-08-30 snapshot was non-empty while a 2026-07-15 request was empty during this audit.

## Polymarket expectations research

Official research material explicitly describes open APIs and historical price data as available to researchers. This clears discovery and methodological research.

It does **not** automatically clear durable raw history publication in this public archive.

Therefore:

- parser remains offline-only,
- event taxonomy must be predeclared before any experiment,
- no post-hoc market selection,
- no new portfolio signal,
- network persistence stays disabled until rights are explicit.

## Remaining work that is intentionally not done

- no 200-metric on-chain sweep,
- no self-hosted historical URPD node/indexer build,
- no new regime composite,
- no production owner integration,
- no forward ledger rows fabricated from retrospective data.
