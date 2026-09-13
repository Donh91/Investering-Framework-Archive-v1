# Meme Alpha Lab — Research Ideas Registry

**Status:** SHADOW_RESEARCH_INTAKE  
**Authority:** NONE_BY_ITSELF  
**Owner:** Meme Alpha Lab (`04_MARKET_LEARNING/tactical_microcap_lab/`)

## Purpose

This file is the lightweight intake/index for external research patterns, workflow ideas and experimental improvements that may help Meme Alpha Lab.

An idea appearing here is **not** a trading rule, signal, recommendation or promotion. It remains research material until the existing learning, falsification and governance layers show measurable incremental value.

The lab should prefer adapters into existing contracts and owners over new parallel agents or duplicate engines.

## Admission rule

Every research idea should answer:

1. What concrete decision problem could this improve?
2. Which existing owner already covers part of it?
3. What is genuinely new rather than renamed overlap?
4. How can it be tested prospectively or with point-in-time historical evidence?
5. What would falsify it?
6. What data, token or agent cost does it add?
7. Can it be implemented as a profile/adapter instead of a new engine?

## Active ideas

### MAL-RI-0001 — Meme / Early-Token Research Profile

**Status:** `PREPARED_NOT_ACTIVE`  
**Source inspiration:** `AT-SRC-0005` — 563 Codex / Robinhood Chain research-buddy workflow  
**Primary source:** https://x.com/563defi/status/2097731184402759902?s=46  
**Canonical source note:** `04_RESEARCH_LAB/auto_trading/source_notes/AT-SRC-0005_563_CODEX_ROBINHOOD_RESEARCH_BUDDY.md`  
**Canonical shared research contract:** `04_RESEARCH_LAB/auto_trading/MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md`  
**Meme Alpha Lab adapter:** `research_ideas/MEME_EARLY_TOKEN_RESEARCH_PROFILE_v1.md`

**Problem:** generic token research can over-weight narrative and under-weight the short-lived mechanics that dominate memes and tiny microcaps: contract identity, executable liquidity, wallet clusters, distribution, holder/buyer acceleration, social propagation and rapid thesis decay.

**Adaptation:** keep one canonical Microcap Research Agent Contract and specialize it through a Meme Alpha Lab profile. Do not fork the contract or create another permanent research agent.

**Primary hypotheses to test:**

- point-in-time contract + wallet + liquidity + propagation features improve rejection of bad candidates versus free-form LLM research;
- acceleration in unique buyers, holders, credible wallets and independent claims is more useful than raw volume or mention counts alone;
- claim-level deduplication reduces false social momentum from repeated copies of the same thesis;
- blind kill-case review catches materially more rugs, distribution traps or untradeable setups than a bull-thesis-only workflow;
- frozen research packets linked to later outcomes can identify which pre-decision features discriminate temporary winners from failures.

**Falsification:** reject or simplify the profile if prospective samples show no material gain in critical-risk detection, research reproducibility, candidate ranking or later outcome discrimination after accounting for added time/token cost.

## Design boundary

Research ideas may consume existing Meme Alpha Lab case history, wallet registry, signal-source records, public/on-chain evidence and broad Framework regime state. They must not:

- create automatic execution;
- silently change `BUY / SPECULATIVE_BUY / WAIT / REJECT` semantics;
- overwrite upstream Data Ping / Master Monday / Cycle state;
- label wallets as insiders without evidence;
- use outcome data to rewrite the original point-in-time packet;
- duplicate data already stored by an existing owner merely to satisfy a new profile.

## Astra handoff principle

When Astra is active, use this registry as a hypothesis queue, not as a roster of agents. Astra should select the **minimum sufficient capability set**, reuse existing evidence first, and test marginal value before any research idea earns deeper integration.
