# AUTO_TRADING RESEARCH VAULT

Status: RESEARCH ONLY
Owner: Investering Framework Research Lab
Created: 2026-09-08
Authority: Non-core, non-execution, non-canonical until separately promoted through existing governance.

## Purpose

This folder is the controlled intake and research area for theories, architectures, repositories, datasets, strategy ideas and agent patterns that may become useful for future automated AI trading.

The near-term objective is collection, deduplication and disciplined hypothesis formation. The long-term objective is to give Astra a clean body of evidence to audit, reproduce, reject, combine or promote.

This folder must not create a parallel market framework. It must reuse existing Investering Framework state, Research Lab governance, Forecast/Sequence accountability, data provenance standards and existing source contracts wherever possible.

## Hard boundary

Nothing in this folder may place real orders, hold private keys, connect a wallet for execution, or silently become an execution authority.

Until a future explicit promotion decision, all strategy work is limited to:

- theory capture
- historical research
- simulation
- backtesting
- walk-forward validation
- paper trading
- execution-cost modelling
- failure analysis

## Research pipeline

SOURCE -> CLAIM EXTRACTION -> HYPOTHESIS -> DATA CONTRACT -> BASELINE -> BACKTEST -> WALK-FORWARD -> PAPER TEST -> ADVERSARIAL AUDIT -> PROMOTE / REVISE / KILL

Every candidate must be evaluated against simple baselines and realistic fees, spread, slippage, latency and liquidity constraints.

## Folder files

- `SOURCE_REGISTER.md` - provenance and status of external inspiration.
- `THEORY_LEDGER.md` - explicit hypotheses worth testing.
- `GOVERNANCE.md` - safety, evidence and promotion rules.
- `INTAKE_TEMPLATE.md` - repeatable template for future links, repos and ideas.
- `ASTRA_HANDOVER.md` - instructions for Astra when it takes ownership of the heavy research phase.
- `ASTRA_CHAIN_NATIVE_RESEARCH_COMPILER_V1.md` - Astra-era extension of the chain-specific research-agent idea into context packs, specialist blind-opposition passes, visibility/capacity research, failure-aware retrieval and prospective A/B evaluation.
- `ASTRA_DISCOVERY_VALIDATION_RESEARCH_QUEUE.md` - research queue for independent grading, machine-checkable kill switches, search-bias controls, pre-reasoning cost gates, bounded parallelism and future Agents API execution-lane benchmarking.
- `MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md` - governed point-in-time research contract for small/microcap assets before any strategy layer evaluates them.
- `MMT_V3_RESEARCH_QUEUE.md` - microstructure/order-flow + typed-scripting research queue, with duplicate-data audit and free/live-first acquisition policy.
- `NANSEN_MCP_RESEARCH_QUEUE.md` - read-only Nansen evaluation queue for wallet/entity labels, Smart Money/onchain features, duplicate-coverage control, point-in-time label leakage and API-credit efficiency.
- `source_notes/` - deeper source-specific notes when a link is useful but the original material is only partially recoverable or needs dedicated analysis.
- `maeve/` - MAEVE/CFGI historical action-reconstruction research track.

## Relationship to existing framework

The existing Investering Framework remains authoritative for market state, regime interpretation, learning/accountability and governance. AUTO_TRADING is an experimental consumer of that framework, not a replacement for it.

Useful future architecture should prefer adapters into existing DATA PING / regime / forecast / sequence outputs rather than duplicating those engines.

## Current seed

Seed #001 comes from a RohOnChain post describing a quant-research course and a workflow where full strategies are built from raw data through backtesting. The useful part is the process discipline. Any performance or income claims attached to the social-media post are unverified and must not be treated as evidence.

The vault now also captures chain-specific AI research-agent patterns. These are treated as upstream evidence-generation workflows only: they may create structured research packets, but they cannot create trading authority. Persuasive outputs such as a concise bull thesis are downstream presentation layers and must never replace internal falsification.

The 563 Robinhood Chain research-buddy source is now used in two layers: `MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md` defines the canonical evidence packet, while `ASTRA_CHAIN_NATIVE_RESEARCH_COMPILER_V1.md` defines how Astra should test chain-native context, specialist research decomposition, adverse-selection/visibility, matched failure memory and prospective research-process improvement without creating a parallel engine.

MMT Scripting v3 / Market Data is tracked as a candidate **microstructure and deterministic research-compiler layer**, not as another market-state engine. The research order is deliberately: audit duplicate coverage first, exploit free/live prospective collection where sufficient, then buy historical data only for explicit unresolved evidence gaps.

The 2026-09-11 RohOnChain Astra architecture source is retained only for its strongest transferable principles: **independent grading, externally verifiable kill switches, cheap filtering before expensive reasoning, artifact-backed proof that tests ran, and strict separation between discovery and validation**. Its fixed 300-agent swarm, direct deployment, arbitrary risk thresholds and naive universal performance gates are explicitly not adopted. These ideas are queued in `ASTRA_DISCOVERY_VALIDATION_RESEARCH_QUEUE.md` for future Astra testing.

Nansen MCP/API is tracked as a candidate **read-only labeled onchain intelligence layer**, with especially high relevance to Alpha Lab / meme research and future Astra feature studies. Its differentiation must be proved through wallet/entity label quality, historical depth or research-efficiency gains versus existing/free data. The framework must audit duplicate coverage and point-in-time label leakage before paid backfill or recurring use, and Nansen receives no execution/signing authority from this research track.
