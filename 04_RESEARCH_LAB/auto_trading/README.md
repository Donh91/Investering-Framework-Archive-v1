# AUTO_TRADING RESEARCH VAULT

Status: RESEARCH ONLY
Owner: Investering Framework Research Lab
Created: 2026-09-08
Authority: Non-core, non-execution, non-canonical until separately promoted through existing governance.

## Purpose

This folder is the controlled intake and research area for theories, architectures, repositories, datasets, strategy ideas and agent patterns that may become useful for future automated AI trading.

The near-term objective is collection, deduplication and disciplined hypothesis formation **plus execution of falsifiable research**. The long-term objective is to give Astra a clean body of evidence to audit, reproduce, reject, combine or promote.

This folder must not create a parallel market framework. It must reuse existing Investering Framework state, Research Lab governance, Forecast/Sequence accountability, data provenance standards and existing source contracts wherever possible.

## Current prioritization — READ THIS FIRST

The independent 2026-09-12 architecture audit has materially changed ordering without changing the safety boundary.

Read:

- `EXTERNAL_ARCHITECTURE_AUDIT_2026-09-12__SECOND_PASS_DECISION.md`

Current posture:

`EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER`

The next binding work is empirical, not architectural:

1. reconcile/backfill high-value historical data against independently captured overlap;
2. make proposal-time hypothesis count `N` a first-class monotonic research object;
3. implement mechanical right-truncation and warm-up/convergence leakage tests;
4. only then expand multiple-testing/statistical search controls and run actual hypotheses.

New execution engines, signers, swarms and GUI adapters are deferred until evidence makes them load-bearing.

## Hard boundary

Nothing in this folder may place real orders, hold private keys, connect a wallet for execution, or silently become an execution authority.

Until a future explicit promotion decision, all strategy work is limited to:

- theory capture
- historical research
- simulation
- backtesting
- walk-forward validation
- paper/frozen-forward research where separately admitted
- execution-cost modelling
- failure analysis

Historical success alone does not grant promotion authority.

## Research pipeline

SOURCE -> CLAIM EXTRACTION -> HYPOTHESIS -> DATA CONTRACT -> BASELINE -> LEAKAGE TESTS -> BACKTEST -> MULTIPLICITY / PROCEDURE AUDIT -> WALK-FORWARD -> FROZEN-FORWARD / PAPER -> ADVERSARIAL AUDIT -> PROMOTE / REVISE / KILL

Every candidate must be evaluated against simple baselines and realistic fees, spread, slippage and liquidity constraints appropriate to the strategy horizon.

## Folder files

- `SOURCE_REGISTER.md` - provenance and status of external inspiration.
- `THEORY_LEDGER.md` - explicit hypotheses worth testing.
- `GOVERNANCE.md` - safety, evidence and promotion rules.
- `INTAKE_TEMPLATE.md` - repeatable template for future links, repos and ideas.
- `ASTRA_HANDOVER.md` - instructions for Astra when it takes ownership of the heavy research phase.
- `EXTERNAL_ARCHITECTURE_AUDIT_2026-09-12__SECOND_PASS_DECISION.md` - framework-native decision after the independent Cowork audit; current prioritization authority for AUTO_TRADING research ordering.
- `ASTRA_CHAIN_NATIVE_RESEARCH_COMPILER_V1.md` - Astra-era extension of the chain-specific research-agent idea into context packs, specialist blind-opposition passes, visibility/capacity research, failure-aware retrieval and prospective A/B evaluation.
- `ASTRA_DISCOVERY_VALIDATION_RESEARCH_QUEUE.md` - research queue for independent grading, machine-checkable kill switches, search-bias controls, pre-reasoning cost gates, bounded parallelism and future Agents API execution-lane benchmarking; subject to the P0 ordering in the second-pass decision above.
- `MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md` - governed point-in-time research contract for small/microcap assets before any strategy layer evaluates them.
- `MMT_V3_RESEARCH_QUEUE.md` - microstructure/order-flow + typed-scripting research queue, with duplicate-data audit and free/live-first acquisition policy.
- `NANSEN_MCP_RESEARCH_QUEUE.md` - read-only Nansen evaluation queue for wallet/entity labels, Smart Money/onchain features, duplicate-coverage control, point-in-time label leakage and API-credit efficiency.
- `TRADINGVIEW_MCP_RESEARCH_QUEUE.md` - **closed / rejected for AUTO_TRADING** after independent audit and direct second-pass verification of the upstream usage restriction; retained only as archived provenance.
- `OPEN_SOURCE_TRADING_STACK_LANDSCAPE_2026-09-12.md` - preserved discovery map of external repositories. Its original ordering is superseded for prioritization by the independent-audit second-pass decision.
- `source_notes/AT-SRC-0012_FOMO_ROBINHOOD_RADAR.md` - source/code audit of a Robinhood Chain wallet-intelligence pipeline with transaction-provenance defenses, wallet scoring, burst/exit logic and explicit point-in-time caveats; likely strongest operational fit is existing Alpha Lab/meme research, not execution.
- `source_notes/` - deeper source-specific notes when a link is useful but the original material is only partially recoverable or needs dedicated analysis.
- `maeve/` - MAEVE/CFGI historical action-reconstruction research track.

## Relationship to existing framework

The existing Investering Framework remains authoritative for market state, regime interpretation, learning/accountability and governance. AUTO_TRADING is an experimental consumer of that framework, not a replacement for it.

Useful future architecture should prefer adapters into existing DATA PING / regime / forecast / sequence outputs rather than duplicating those engines.

The no-duplicate rule only applies when an actual owner exists. A proven missing capability such as mechanical leakage detection or trial-count accounting is a real gap, not a reason to avoid implementation.

## Current research interpretation of external sources

The existing source notes remain valuable for discovery, but external architecture does not outrank empirical validation.

The 563 Robinhood Chain research-buddy source is used through the canonical microcap research contract and chain-native compiler ideas, not as execution authority.

MMT Scripting v3 / Market Data remains a candidate microstructure and deterministic research-compiler layer. Paid historical acquisition remains blocked until duplicate coverage and an explicit evidence gap are demonstrated.

The RohOnChain Astra architecture source is retained for independent grading, externally verifiable kill switches, cheap filtering before expensive reasoning, artifact-backed proof and discovery/validation separation. Its fixed swarm, arbitrary numeric thresholds and direct deployment concepts are not adopted.

Nansen MCP/API remains a candidate read-only labeled onchain intelligence layer, especially for Alpha Lab / meme research. Duplicate coverage and point-in-time label leakage remain mandatory audits before paid use.

TradingView MCP is now rejected for AUTO_TRADING. The upstream repository explicitly prohibits automated trading or algorithmic decision-making using extracted data, and its desktop/CDP architecture adds unnecessary operational and authority surface. The source note stays archived; the research lane is closed unless upstream conditions materially change.

The broader open-source landscape remains useful, but priorities have changed:

- **Freqtrade mechanical look-ahead / recursive-analysis principles:** immediate reverse-engineering target.
- **`arch` multiple-comparison tooling:** immediate statistical component candidate after P0 data/leak controls.
- **Nautilus Agents protocol ideas:** borrow authority/receipt schema concepts; do not adopt the early-alpha crate.
- **NautilusTrader engine:** defer until richer execution data and surviving strategy requirements make it testable.
- **RD-Agent:** negative benchmark + provenance ideas, not strategy-selection owner.
- **Condor:** borrow fail-closed gate semantics; reject as runtime component under current authority surface.
- **VectorBT / lightweight in-house sweeper:** later cheap-screening benchmark, not current first priority.

FOMO Robinhood Radar remains a wallet-intelligence / provenance benchmark, not a trading engine. Receipt-level trade attribution, anti-seeding defenses, point-in-time score history and cohort burst/exit research are the strongest transferable ideas. Social performance claims remain unverified until reproduced under strict point-in-time scoring.

## Next major review trigger

Do not trigger another major AUTO_TRADING architecture redesign merely because a new repository or AI-trading thread appears.

Trigger the next architecture review when empirical evidence exists:

- historical reconciliation completed;
- planted-leak benchmark passed;
- monotonic trial counter operational;
- at least one THEORY_LEDGER hypothesis has a reproducible result artifact.

External links may still be logged and screened in the meantime.