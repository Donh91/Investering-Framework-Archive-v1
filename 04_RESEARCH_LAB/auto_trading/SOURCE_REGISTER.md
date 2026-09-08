# AUTO_TRADING SOURCE REGISTER

Purpose: preserve provenance without confusing inspiration with evidence.

## Source statuses

- `INBOX` - captured, not reviewed.
- `SCREENED` - relevant concepts extracted.
- `RESEARCH_QUEUED` - worth deeper study.
- `TESTED` - claims or strategy ideas tested against data.
- `REJECTED` - insufficient, duplicated, non-reproducible or structurally weak.
- `PROMOTED` - passed the required governance path into a separately approved downstream component.

---

## AT-SRC-0001

Date captured: 2026-09-08
Source type: X / social-media post
Author: RohOnChain
URL: https://x.com/rohonchain/status/2097303933081489605?s=46
Status: SCREENED
Evidence class: INSPIRATION, NOT VERIFIED PERFORMANCE EVIDENCE

### Source summary

The post describes a quant-research course that walks through three strategies from data to backtest and frames systematic strategy construction as accessible rather than mysterious. The post also contains a third-party anecdotal profit claim about a private quantitative system.

### Retain

1. Strategy development should be an explicit pipeline from data to hypothesis to backtest.
2. Full worked examples are more useful than isolated indicators.
3. Reproducibility and implementation detail matter more than strategy storytelling.
4. Multiple independent strategy families are preferable to one monolithic bot.
5. Future AI agents can help generate, implement and challenge hypotheses, but must be constrained by evidence and governance.

### Do not retain as fact

- Any claimed annual profit figure.
- Any implication that quantitative trading is easy merely because implementation can be explained simply.
- Any strategy performance without code, data, costs, timestamps, out-of-sample validation and reproducible results.

### Research follow-up

- Locate the underlying course/video/article if directly identifiable.
- Extract the three strategy families and their exact assumptions.
- Search for original code or equivalent open implementations.
- Reproduce with crypto data only if the hypotheses make structural sense for our universe.
- Benchmark against simple buy-and-hold, trend, mean-reversion and volatility baselines.

### Promotion test

No concept from this source may be promoted because of social engagement, creator authority or claimed PnL. Promotion requires reproducible evidence under `GOVERNANCE.md`.

---

## AT-SRC-0002

Date captured: 2026-09-08
Source type: Product / public beta / trading infrastructure
Project: No More Screen Time (NMST)
URL: https://nmst.io
Status: RESEARCH_QUEUED
Evidence class: ARCHITECTURE INSPIRATION; PRODUCT PERFORMANCE UNPROVEN
Related ecosystem: CFGI appears publicly associated with NMST, but the NMST website itself does not currently document ownership/team provenance in detail.

### Source summary

NMST presents itself as privacy-first trading infrastructure for humans and agents. Its public beta separates strategy construction, deterministic testing, public simulated forward records, ranking and a future marketplace for proven strategies/data modules.

The Foundry exposes a constrained strategy pipeline with market, product, timeframe, signal, entry, exit, risk and review fields. Its AI layer is explicitly constrained to filling supported strategy fields rather than freely inventing hidden logic. Backtesting is described as deterministic replay on closed candles with bar-close signals, next-open fills and visible costs.

The League is a shared virtual runtime with a common market clock and common cost model. Strategies are published with frozen rules into simulated forward records. Ranking is explicitly not based on return alone, but incorporates return, drawdown, downside, consistency and integrity. During the current public beta, NMST reports zero active public records, so no live strategy edge is yet demonstrated.

### Retain

1. Natural language should compile into an inspectable deterministic strategy specification, not directly into opaque trade decisions.
2. AI can be restricted to supported fields and then require human/agent review before testing.
3. Backtest assumptions should expose fill timing and costs explicitly.
4. Strategy comparison is more trustworthy under one shared clock and one shared cost model.
5. Frozen strategy rules plus public forward simulation provide stronger evidence than editable private backtests.
6. Ranking should include drawdown, downside, consistency and integrity rather than return alone.
7. Strategy/data modules should remain modular so a data provider can be evaluated separately from the strategy consuming it.
8. Self-host/privacy-first architecture is relevant for future execution systems handling exchange credentials or proprietary signals.

### CFGI-specific relevance

CFGI currently exposes live and historical sentiment data across hundreds of crypto and stock assets, four timeframes and multiple sub-signals through REST/webhooks. NMST explicitly says users can supply data or signals and anticipates ready data modules.

This creates a high-value research hypothesis for our vault:

CFGI should be treated as an upstream feature/data module that can be plugged into deterministic strategy tests, rather than as a standalone buy/sell oracle.

Priority tests should focus on:
- CFGI score change/velocity rather than raw level alone;
- cross-timeframe disagreement, e.g. 15m/1h improving while 4h/1d remain weak;
- asset-vs-market sentiment dispersion;
- individual CFGI components, such as whales/order-book/technical inputs, rather than composite score only;
- regime-conditioned usefulness, especially stress, post-flush, recovery and rotation states;
- whether CFGI adds post-cost out-of-sample value beyond price/volume baselines.

### Important negative evidence

CFGI itself states that its sentiment is a gauge rather than a price predictor and that next-day predictive relationship is weak in its own records. Therefore no raw CFGI threshold should be assumed to have alpha.

### Current limitations

- NMST public beta currently shows no published live strategy records.
- No verified live execution track record is available from the public pages reviewed.
- Product architecture can be copied conceptually, but product claims cannot substitute for our own testing.
- Relationship between CFGI and NMST is strongly suggested by public ecosystem references, but should not be relied on for any financial or governance conclusion without primary-source confirmation.

### Research follow-up for Astra

1. Audit NMST Foundry rule schema and supported strategy primitives once docs/source become available.
2. Reproduce the best architectural ideas internally without creating dependency on NMST.
3. Build a CFGI feature-ablation study across BTC, ETH, large caps and selected midcaps.
4. Compare raw CFGI level vs velocity, divergence, dispersion and component-level features.
5. Run common-clock/common-cost simulated forward tests on surviving strategies.
6. Treat NMST League-style public/frozen records as inspiration for our own shadow strategy leaderboard.
7. Revisit when NMST publishes real strategies, source code, docs or API/data-module contracts.

### Promotion test

No NMST or CFGI-derived strategy logic may be promoted solely because it exists in the same ecosystem or looks polished. Promotion requires reproducible post-cost evidence under `GOVERNANCE.md`, with forward or walk-forward survival and an explicit kill criterion.
