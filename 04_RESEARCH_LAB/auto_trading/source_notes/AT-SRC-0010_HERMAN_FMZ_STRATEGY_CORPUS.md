# AT-SRC-0010 - Herman Trading / FMZ strategy corpus

Date captured: 2026-09-12
Status: RESEARCH_QUEUED
Evidence class: MIXED - open-source code + public statistical research + commercial marketing

## Sources

- https://twilight-sky-83a4.helmans13.workers.dev/Herman_Trading_Strategy_Vault
- https://github.com/fmzquant/strategies
- https://github.com/HermanTrading
- https://www.hermantrading.pro/premium
- User-supplied X captures and exported NQ London Playbook

## Executive verdict

The strongest value is NOT the headline count of 5,800+ strategies and not the advertised TradingView backtest results.

The strongest value is the corpus as a research/discovery library plus the execution/infrastructure patterns buried inside FMZ, especially exchange adapters, WebSocket/event handling, funding monitors, multi-symbol control, order/position utilities, TradingView-to-exchange bridges and concurrency patterns.

Herman's own public GitHub footprint is currently small. The inspected `Trend-Rebalance-Map-Herman-` repository contains a transparent Pine v6 strategy with explicit anti-repaint choices, slippage/commission assumptions and documented edge cases. That is useful as a reproducible test fixture, but it is not evidence of durable alpha.

## FMZ corpus - retain

Useful categories found in the public repository include:

- TradingView signal execution examples for Binance / OKX;
- WebSocket acceleration and multi-symbol templates;
- funding-rate aggregation and multi-venue funding monitoring;
- order, position, precision and account utilities;
- multi-exchange concurrency and hedging examples;
- HFT/order-flow examples;
- historical candle pagination;
- Uniswap V3 and other exchange/DEX trading helpers;
- arbitrage and pair-trading examples.

These should be treated as implementation references and research fixtures, not imported strategies.

## FMZ licensing warning

No single root LICENSE was found during this audit. Individual files carry heterogeneous licenses, including MPL-2.0 and WTFPL examples.

Therefore:

- do not bulk-copy the repository into the Framework;
- preserve per-file license and attribution before any code reuse;
- prefer reverse-engineering architecture principles or writing clean-room adapters when practical.

## Herman Trend Rebalance Map - code audit

Observed properties:

- Pine Script v6;
- no `request.security()` / higher-timeframe look-ahead;
- signals require `barstate.isconfirmed`;
- `process_orders_on_close = true` and `calc_on_every_tick = false`;
- commission and slippage are explicitly modelled;
- one position at a time;
- strategy documents a rare target-side edge case;
- performance table reads closed trades from TradingView's broker emulator.

Strategy logic itself is simple: a close crossing the fast SMA back toward a separated slow SMA, with configurable fixed/slow-SMA target and fixed/1R stop.

Verdict: `BENCHMARK / TEST_FIXTURE`, not `EDGE_CONFIRMED`.

## NQ London Playbook - research audit

Public methodology is materially stronger than typical social-media trading content:

- Jan 2022-Aug 2025 NQ 1-minute sample;
- 719 trading days;
- explicit session definitions;
- branch-specific sample counts;
- medians rather than averages for penetration/time;
- deterministic concepts: Asia size, Pre-London sweep, Opening Range follow/flip, London continuation/retest.

Examples reported include branch continuation/sweep probabilities around 72-86% with explicit `n` values, and median extensions/timing.

However, the source reviewed does NOT establish:

- a sealed untouched out-of-sample period;
- multiple-testing correction across all candidate branches;
- walk-forward stability;
- realistic commission/spread/slippage impact on the exact entry/retest rules;
- parameter sensitivity around session boundaries and Asia-range threshold;
- stability across pre/post-2022 volatility regimes;
- independent reproduction from the raw purchased data.

Verdict: `REPRODUCTION_CASE / METHODOLOGY_BENCHMARK`, not promotion evidence.

Recommended future test: independently reproduce the decision tree from raw point-in-time NQ minute data, freeze the specification, then test 2025-2026 unseen data and transaction-cost sensitivity.

## Herman premium products

The premium site advertises probability maps built from long NQ/Gold historical samples and embeds historical probabilities into TradingView.

Research value: moderate as inspiration for context-conditioned probability maps.

Priority: LOW-MEDIUM relative to open source alternatives because the proprietary indicators cannot currently be independently audited or reproduced from source.

Do not purchase or treat marketing claims such as 'statistically proven edge' as evidence.

## Framework classification

- FMZ strategy corpus: `BENCHMARK + BORROW_PRINCIPLE`
- FMZ execution plumbing: `POTENTIAL_REFERENCE_COMPONENT`, source-code audit required
- Herman NQ playbook: `REPRODUCTION_CASE`
- Herman Trend Rebalance Map: `TEST_FIXTURE`
- Herman premium indicators: `LOW_PRIORITY / CLOSED_SOURCE`

## Primary research questions for Astra

1. Which FMZ modules solve real gaps not already covered better by NautilusTrader, Hummingbot, Freqtrade or existing Framework code?
2. Can a license-safe shortlist of execution utilities materially reduce engineering risk?
3. Can Herman's NQ session-probability study be independently reproduced and survive a frozen forward window?
4. Can the Herman Strategy Vault be used as an idea corpus while tracking search budget and false-discovery risk rather than cherry-picking attractive backtests?

No execution authority is granted by this source.