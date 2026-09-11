# NANSEN x ALPHA LAB ABLATION v1

Status: `RESEARCH_QUEUED`
Date: 2026-09-11
Authority: `RESEARCH_ONLY`
Parent: `NANSEN_MCP_RESEARCH_QUEUE.md`
Source note: `source_notes/AT-SRC-0008_NANSEN_MCP_ONCHAIN_INTELLIGENCE.md`

## Purpose

Test whether official Nansen API/MCP data adds material, reproducible information to the existing Alpha Meme Lab research process versus the framework's own/free onchain evidence.

This is an ablation and provider-value test, not an integration decision and not a trading signal.

## Core question

> Does Nansen add unique wallet/entity/history information or enough research-efficiency improvement to justify an optional Shadow adapter, after point-in-time leakage, duplicate coverage, provider cost and licensing constraints are controlled?

## Experiment arms

Run the same frozen case packet through:

A. `FRAMEWORK_BASELINE` — current Alpha Lab + existing archive/free public sources.
B. `FREE_RAW_EQUIVALENT` — raw/free onchain features closest to the desired Nansen fields.
C. `NANSEN_AUGMENTED` — baseline plus only official Nansen API/MCP fields available at the research timestamp.
D. `NANSEN_ONLY` — optional diagnostic arm to reveal what is lost when provider labels replace framework context.

No arm may see future outcomes during feature construction.

## Cohort design

The exact competitive identifiers remain private. The private benchmark manifest binds representative case families including:

- provisional/high-priority wallet research;
- publicly disclosed Robinhood wallet cohort research;
- historical Ethereum meme references;
- active Robinhood Chain cases;
- the frozen 2026-09-11 prospective token cohort and matched failures/rejection rows;
- future newly discovered cases only when frozen before outcome.

Do not cherry-pick only known winners.

## Feature families to compare

- wallet/entity labels and confidence;
- wallet PnL/history and realized-vs-unrealized context;
- related wallets / counterparties / economic-entity clues;
- Smart Money participation, netflow and trade composition where supported;
- holder segmentation and entity-adjusted concentration;
- DEX trade flow and buyer/seller composition;
- exchange interactions / labeled inflow-outflow context;
- historical depth and retrieval efficiency;
- chain/asset coverage gaps.

Every Nansen-derived field must preserve provider endpoint/tool, retrieved_at, effective/observable time when available, ranking/label window when applicable, credits consumed and missingness.

## Point-in-time rule

A label visible today may not be back-applied as if it was known at a historical decision timestamp.

If historical label state cannot be reconstructed, mark:

`RETROSPECTIVE_LABEL_RISK`

Such fields may be used for forensic explanation but not clean prospective validation.

## Primary measurements

Measure per case and aggregate by case family:

- factual correctness against deterministic/explorer evidence;
- unique verified facts added;
- entity-resolution improvement;
- false-label / false-confidence events;
- point-in-time leakage incidents;
- unresolved-risk reduction;
- material conclusion changes;
- forward discrimination once outcomes mature;
- research latency;
- model/tool-call count;
- Nansen credits consumed;
- information gained per provider credit;
- duplicate coverage with existing/free data.

Do not reward prettier labels or more verbose output.

## Alpha Lab-specific tests

1. `GLOBAL_SMART_MONEY vs CONDITIONAL_WALLET_ALPHA`
   - test whether Nansen wallet labels add value after chain, venue, token age, liquidity, market-cap state, visibility/crowding and entry taxonomy are conditioned.

2. `RAW_HOLDERS vs ENTITY_ADJUSTED_STRUCTURE`
   - test whether labeled entities materially improve concentration and independence estimates versus service/router/LP-aware free derivation.

3. `PUBLIC_VISIBILITY_DECAY`
   - where disclosure timestamps exist, compare pre-public and post-public wallet expectancy without using later labels to rewrite earlier state.

4. `EXECUTABLE_OUTCOME`
   - provider PnL/chart outcomes do not replace Alpha Lab executable-return semantics.

5. `MATCHED_FAILURES`
   - Nansen features must be evaluated on failures/rejections as well as memorable winners.

## Provider/legal boundary

Use official Nansen API/MCP/CLI only under the then-current terms and licensing rules.

Do not scrape the authenticated UI, copy proprietary databases, reverse engineer proprietary algorithms, redistribute restricted provider data, or build a direct clone of Nansen.

The framework may independently implement general analytical ideas from public blockchain data.

## Cost boundary

- Start with free/zero-paid capability only.
- No broad historical backfill.
- No recurring paid polling.
- Re-check endpoint pricing/credits at execution time.
- Any paid acquisition requires a separately documented frozen hypothesis, expected information gain and owner-approved budget.

## Promotion gate

Promote to an optional `NANSEN_SHADOW_ADAPTER` only if the benchmark demonstrates reproducible incremental value beyond existing/free sources in more than one relevant case family, with acceptable point-in-time semantics and provider cost.

Provider convenience alone is insufficient.

If promoted, Nansen remains an `EXTERNAL_LABEL_PRIOR` / research capability. It receives no market-state ownership, canonical signal authority, portfolio authority, signing authority or execution authority.

## Astra / Codex split

Codex may implement the deterministic read-only adapter, schemas, fixtures, credit accounting and A/B harness.

Astra later owns the difficult adjudication questions: source conflicts, causal/mechanism synthesis, conditional wallet-skill analysis, information-gain assessment and whether the provider genuinely changes forward research quality.

## Current verdict

`HIGH_VALUE_TOOL_LEAD -> BENCHMARK_BEFORE_INTEGRATION`
