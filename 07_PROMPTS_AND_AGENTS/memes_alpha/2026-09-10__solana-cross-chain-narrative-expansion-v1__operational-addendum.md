# Memes v3 Solana + Cross-Chain Narrative Expansion v1

**Dato:** 2026-09-10  
**Status:** OPERATIONAL_OWNER_APPROVED  
**Område:** Memes v3 / Alpha Lab / autonomous research  
**Primary folder:** `07_PROMPTS_AND_AGENTS/memes_alpha/`  
**Depends on:** `2026-09-09__memes-v3-autonomous-alpha-research-workstream-v1__operational.md`

## Purpose

Extend the existing Memes v3 autonomous Alpha Research Workstream to treat Solana as a first-class research lane and to test cross-chain narrative selection without creating a new engine.

The motivating user observation is that a meme narrative can be directionally correct while one chain implementation fails and another implementation captures the move. The research target is therefore not only token selection, but also early chain/venue selection.

## New research surface

Add Solana public evidence using deterministic sources before model reasoning. Research must support:

- Pump.fun / PumpSwap and Raydium pool discovery;
- exact Solana mint identity;
- creator history where publicly available;
- mint/freeze authority state;
- first buyers and unique buyer acceleration;
- sniper, bundler and fresh-wallet cohorts;
- common funder / wallet-cluster evidence;
- holder concentration plus distributed-insider concentration;
- paid boost timestamps separated from organic propagation;
- Telegram/X/caller propagation timestamps;
- cross-chain narrative siblings and copy timing;
- fixed-horizon outcomes.

## Cross-chain narrative contract

Create a research feature family, not a buy score:

```text
NARRATIVE_ID
CHAIN
TOKEN_IDENTITY
LAUNCH_TIME
FIRST_ORGANIC_BUY_ACCELERATION
FIRST_QUALIFIED_WALLET_EVENT
FIRST_SOCIAL_PROPAGATION
FIRST_PAID_BOOST
LIQUIDITY_GROWTH
UNIQUE_BUYER_GROWTH
INSIDER_CLUSTER_SHARE
COMMON_FUNDER_SHARE
OUTCOME_1H
OUTCOME_6H
OUTCOME_24H
OUTCOME_7D
MAX_DRAWDOWN
```

A narrative winner may only be classified prospectively from frozen early evidence. Later price success may not be used to backdate chain-selection quality.

## Solana-specific guardrails

- Low top-10 concentration is not proof of fair distribution. Distributed bundle/funder networks may control supply across many fresh wallets.
- DexScreener boosts and paid listings are marketing metadata, not alpha evidence.
- A Telegram or KOL call is a propagation event, not proof of independent demand.
- Sniper and bundler counts require source provenance and do not automatically imply malicious behavior.
- Creator history, wallet funding and bundle structure must be evaluated together.
- Exact Solana mint addresses must be verified before cross-chain comparison.
- Unknown chain identity stays unresolved.

## Research comparison priority

Prioritize matched comparisons between:

1. apparently organic narrative diffusion with broad real buyer growth;
2. coordinated/bundled launches with high apparent activity;
3. the same narrative expressed on multiple chains;
4. social-first versus on-chain-first propagation;
5. paid-boost-first versus organic-first discovery.

This is intended to produce both positive cases and negative controls.

## Autonomous development

The existing Compounding Learning and Research Governance owners may propose bounded improvements to Solana collection/classification when false positives, missingness or new evidence gaps are observed. Code-local improvements route through the existing Codex intake path.

No automatic trade action, portfolio action, API-budget increase, paid provider authorization, canonical market rule, self-promotion or self-merge is granted by this addendum.

## Implementation dependency

The existing base candidate `codex-research-memes-v3-autonomous-alpha-workstream-v1` remains unchanged and authoritative for the base workstream. Solana support should be implemented as a bounded extension after or alongside the base implementation only where it does not invalidate the frozen base candidate.
