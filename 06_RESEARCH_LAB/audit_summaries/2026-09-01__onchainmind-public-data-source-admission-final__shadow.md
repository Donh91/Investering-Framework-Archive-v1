# OnChainMind / Public Data Source Admission - Final Shadow Audit

Date: 2026-09-01  
Status: `FINAL SHADOW RESEARCH / NO LIVE AUTHORITY`

## Executive verdict

The OnChainMind deep dive produced value, but not by admitting OnChainMind itself.

The useful outcome is a cleaner upstream source architecture:

- **OnChainMind** discovers concepts.
- **Coin Metrics Community** owns reproducible long-history baselines.
- **BGeometrics** supplies bounded transient on-chain research and recent URPD topology.
- **Polymarket** remains a potentially orthogonal expectations source, with persistence still deliberately blocked.
- **DefiLlama** stays with its existing owner.

No new engine, vote, threshold, portfolio action, or live state change is justified.

## Agent A - source and rights

### OnChainMind

Disposition: `DISCOVERY_ONLY`

The site is useful for concept discovery, especially cost-basis topology and holder-state framing, but it is not admitted as a machine source. Automated extraction and raw archiving remain prohibited by the source contract.

### Coin Metrics Community

Disposition: `APPROVED_RESEARCH_BASELINE`

Validated properties:

- keyless Community API,
- official GitHub data archive,
- CC BY-NC 4.0 community data,
- long BTC history,
- immutable Git references can bind evidence runs.

Validated reference during this audit:

- commit: `f1a36afb962731c387bb03982758ab0103063da5`
- BTC CSV blob: `5e50f336d268e1f3a38e9885b5aaef36de529700`

Rule: mutable `main/master` may be used for discovery, not evidence.

### BGeometrics

Disposition: `APPROVED_TRANSIENT_RESEARCH_ONLY`

Current public materials document hundreds of metrics and a free research tier. Public pages disagree on the exact hourly free limit, so the adapter uses the conservative 8/hour and 15/day ceiling.

Raw provider payloads are not persisted in the public repository.

### Polymarket

Disposition: `RESEARCH_ACCESS_SUPPORTED / PERSISTENCE UNRESOLVED`

The Polymarket Institute explicitly documents open exchange APIs for research and exposes historical CLOB pricing. That supports source study and offline parsing.

The public archive still does not assume durable raw-history redistribution rights. Network persistence remains disabled.

## Agent B - compact quantitative replay

### Research design

A bounded 48-observation monthly replay tested whether MVRV adds forecast information beyond simple BTC price/trend.

Baseline:

- 1-month price return,
- 3-month price return,
- 6-month drawdown.

Challenger additions:

- MVRV level,
- 1-month MVRV delta.

Expanding ridge replay:

- minimum train: 18 observations,
- alpha sensitivity: 1 / 10 / 100,
- horizons: 1 month and 3 months.

Admission gate:

- >=5% MAE improvement,
- >=5 percentage-point direction improvement,
- robust across sensitivity.

### Result

`NO_ROBUST_INCREMENTAL_PREDICTIVE_VALUE`

The challenger sometimes reduced MAE, especially on the 3-month target, but did not improve directional accuracy. At stronger regularization, the MAE advantage mostly disappeared.

Disposition:

- kill MVRV as a new predictive feature,
- keep it as valuation/stress context,
- do not expand into broad metric mining.

### Useful negative result

MVRV below 1.2 was associated with stronger subsequent returns in this small 2022-2026 sample, but only eight 1-month and six 3-month forward cases were available. This is context, not proof.

### Source-family check

Five sampled dates showed BGeometrics and Coin Metrics MVRV reasonably close but not identical, with about 1.9% mean absolute percentage difference.

Therefore provider methodology is part of the evidence identity and may not be silently substituted.

### Extraction failures caught

- A structured BTC-price extraction repeated identical historical values across different years, so it was rejected and Binance was used transiently for the price baseline.
- A structured SOPR extraction declared months missing while simultaneously returning those months, so it was excluded.

These are extraction-path failures, not proof that the provider's raw source is bad.

## Agent C - URPD and expectations

### URPD

Disposition: `PROSPECTIVE SHADOW OBSERVATION ONLY`

The official OpenAPI exposes:

- `GET /v1/urpd?day=...`
- `GET /v1/urpd/{last}`

with `UrpdDay` fields:

- `priceLower`
- `priceUpper`
- `utxoCount`
- `btcSupply`
- `pctSupply`

A 2026-08-30 date request returned a non-empty distribution, while 2026-07-15 returned empty during the audit.

This supports recent point-in-time observation but not a long historical replay claim.

The new probe therefore emits derived topology only and binds the requested day explicitly into the receipt.

### Polymarket

Disposition: `KEEP_OFFLINE / FUTURE EXPECTATIONS RESEARCH`

This remains the most orthogonal candidate information class because market-implied event probabilities are not simply another BTC price/on-chain transform.

However, no network collector is activated until durable storage/derived-use rules and a predeclared event taxonomy are explicit.

## Agent D - architecture and governance

### No duplicate owners

- DefiLlama stays with its existing owner.
- BGeometrics Regime Score is rejected as a new vote because its component families materially overlap signals the framework already owns.
- Self-hosted URPD remains deferred due the cost of UTXO/indexer and acquisition-price lineage.

### Research receipt boundary

Every public research receipt must preserve:

- source identity,
- immutable/pinned source reference where possible,
- payload hash,
- retrieval timestamp,
- `raw_persisted=false`,
- all authority flags false.

## Final source admission table

| Source/family | Disposition | Role |
|---|---|---|
| OnChainMind | DISCOVERY ONLY | concept/context |
| Coin Metrics Community | KEEP | long-history baseline |
| BGeometrics MVRV | CONTEXT ONLY | valuation/stress |
| BGeometrics broad metric sweep | KILL | avoid metric fishing |
| BGeometrics URPD | KEEP SHADOW | prospective structure topology |
| BGeometrics Regime Score | REJECT NEW VOTE | benchmark only |
| Polymarket | DEFER NETWORK | expectations research |
| DefiLlama | REUSE | existing owner/crosscheck |
| Self-hosted URPD | DEFER HEAVY | sovereignty fallback only |

## Final conclusion

The research did not justify more signals.

It justified better source discipline and one genuinely differentiated observation family, URPD topology.

The correct next state is therefore:

- fewer duplicated confirmations,
- stronger immutable provenance,
- MVRV retained only as context,
- URPD observed prospectively without action authority,
- Polymarket held behind an explicit persistence contract,
- no live framework change.
