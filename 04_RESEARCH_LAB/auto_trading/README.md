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
- `MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md` - governed point-in-time research contract for small/microcap assets before any strategy layer evaluates them.
- `source_notes/` - deeper source-specific notes when a link is useful but the original material is only partially recoverable or needs dedicated analysis.
- `maeve/` - MAEVE/CFGI historical action-reconstruction research track.

## Relationship to existing framework

The existing Investering Framework remains authoritative for market state, regime interpretation, learning/accountability and governance. AUTO_TRADING is an experimental consumer of that framework, not a replacement for it.

Useful future architecture should prefer adapters into existing DATA PING / regime / forecast / sequence outputs rather than duplicating those engines.

## Current seed

Seed #001 comes from a RohOnChain post describing a quant-research course and a workflow where full strategies are built from raw data through backtesting. The useful part is the process discipline. Any performance or income claims attached to the social-media post are unverified and must not be treated as evidence.

The vault now also captures chain-specific AI research-agent patterns. These are treated as upstream evidence-generation workflows only: they may create structured research packets, but they cannot create trading authority. Persuasive outputs such as a concise bull thesis are downstream presentation layers and must never replace internal falsification.
