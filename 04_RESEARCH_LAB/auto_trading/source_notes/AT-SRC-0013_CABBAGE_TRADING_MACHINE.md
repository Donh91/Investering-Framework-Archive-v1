# AT-SRC-0013 - CABBAGE Trading Machine extraction note

Date: 2026-09-25
Status: EXTRACT_SELECTIVELY / NO ENGINE ADOPTION
Source: https://github.com/sopersone/cabbage-trading-machine
Site: https://cabbagetm.xyz/
Upstream license: Apache-2.0

## What it actually is

CABBAGE is a thin integration/wrapper around Investing Algorithm Framework 9.0.0a18. Its documented strategy is long-only spot RSI/EMA crossover, fixed quote ticket, fixed percentage stop, incomplete-candle exclusion, paper/live execution through the upstream framework and CCXT.

The repository explicitly states that it does not implement Jev, Robinhood Chain RPC/DEX wallet scanning, smart-wallet scoring, or the promotional smart-wallet strategy/trade history.

Validation dated 2026-09-24 establishes integration behavior, not edge: dependency/install checks passed; 12 named upstream tests plus 6 CABBAGE integration tests passed; paper BUY/SELL/accounting/report path was exercised; bundled June 10-20 2024 BTC/EUR event-driven backtest produced zero trades; no profitability or production-readiness claim was established; no live order was executed in validation.

## Relevance to our framework

### Keep / learn

1. Paper/live hard separation - paper mode cannot silently inherit a live flag; live rejects absent credentials.
2. Explicit execution command - real orders require an explicit live path rather than accidental promotion.
3. State isolation - mode/market/pair separated under runtime state.
4. Run receipt/report persistence - bounded/normal runs export a machine-readable latest-run artifact.
5. Integration-test pattern - signal -> order -> fill -> portfolio/trade accounting -> persisted report is tested as one path.
6. Upstream integrity check - vendored framework files were compared byte-for-byte to upstream in validation.
7. Honest negative validation - zero-trade backtest and unavailable online validation are reported rather than converted into a performance story.

### Do not import as alpha

- RSI/EMA crossover is not evidence of incremental edge for Alpha Lab, Cycle Navigator or portfolio timing.
- Fixed 5% stop / fixed ticket defaults are software defaults, not calibrated risk policy.
- CCXT spot execution is not a substitute for Robinhood-chain/Pons execution, wallet intelligence or Project->CA.
- No Jev/smart-money implementation exists to steal.
- No independently verified profitable trade history is supplied.
- Do not vendor the full repository or create a parallel trading engine.

## Best extraction targets

Treat CABBAGE as a reliability/execution test-pattern source, not a strategy source.

- MODE_AUTHORITY: paper cannot become live through inherited environment/config.
- LIVE_CREDENTIAL_GATE: missing credentials fail closed before executor activation.
- STATE_NAMESPACE: isolate state by mode + venue + pair/asset.
- END_TO_END_EXECUTION_RECEIPT: prove order lifecycle and accounting with deterministic fixtures.
- UPSTREAM_INTEGRITY_RECEIPT: pin/check upstream dependency provenance where code is vendored.
- NEGATIVE_RESULT_IS_VALID: zero orders / unavailable venue remains a valid outcome.

## Alpha Lab relationship

No direct promotion. The useful transfer is governance: when Alpha Lab eventually hands a candidate to paper/execution research, preserve the frozen candidate evidence and test the full downstream lifecycle without allowing execution plumbing to rewrite the alpha thesis.

For Pons/Robinhood work, CABBAGE does not solve pool-id -> exact CA, deployer/creator/factory provenance, launch calldata/exemptions, early buyer breadth, wallet clustering/repeat-winner skill, sellability/liquidity, or prospective launch detection. Existing Blockscout + Project->CA + wallet/cabal owners remain authoritative.

## Decision

EXTRACT_SELECTIVELY.

No new scheduler, scorer, scanner, execution engine or canonical strategy. No copy of the full upstream tree. Only transplant small reliability/test concepts into existing owners when they close a demonstrated gap.

Kill condition for further work: if existing Auto Trading owners already enforce equivalent paper/live separation, state namespacing, fail-closed credential gating and end-to-end execution receipts, mark this source NOOP and retain this note only as external corroboration.