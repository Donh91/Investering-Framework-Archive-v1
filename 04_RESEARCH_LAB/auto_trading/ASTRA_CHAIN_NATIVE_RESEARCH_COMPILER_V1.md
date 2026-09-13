# ASTRA CHAIN-NATIVE RESEARCH COMPILER V1

Status: `PREPARED_FOR_ASTRA`
Authority: `RESEARCH_ONLY`
Owner: Investering Framework Research Lab
Source inspiration: `source_notes/AT-SRC-0005_563_CODEX_ROBINHOOD_RESEARCH_BUDDY.md`
Canonical evidence contract: `MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md`

## Purpose

Use the useful idea in the 563 source — a chain-specific AI research buddy with a repeatable prompt structure — as a springboard for a more rigorous Astra-class research system without creating a parallel market engine.

The exact three-part 563 prompt was not recoverable at capture time. This document therefore does not reconstruct or quote unseen prompt text. It formalizes only the visible design insight and extends it using existing Investering Framework evidence, governance and prospective-learning rules.

## Core thesis to test

A chain-native research system should outperform a generic token-research prompt because it knows the relevant market object, venue mechanics, source hierarchy, failure modes and chain-specific observability before it reasons about the token.

This is a hypothesis, not an assumption. Astra must test it against a generic baseline.

## 1. Chain-native context packs

Do not make one giant universal prompt. Maintain small versioned context packs that plug into the canonical microcap evidence contract.

Each pack should define, where applicable:

- chain identity and token standards;
- authoritative explorers / RPC / indexers;
- canonical DEXs, launchpads and migration paths;
- quote-asset conventions;
- pool and liquidity mechanics;
- routing / aggregator behavior;
- common service addresses, bridges, CEX hot wallets and routers that should not be misclassified as economic entities;
- creator/deployer authority semantics;
- common launch manipulation patterns;
- chain-specific MEV / bot / bundle behavior;
- holder/account-model caveats;
- social and ecosystem surfaces that matter on that chain;
- historical failure modes;
- known blind spots and data-quality limitations.

Initial research packs should be prioritized for:

1. Solana / Pump.fun / PumpSwap / Raydium / Meteora;
2. Ethereum / Uniswap and mature EVM forensic history;
3. Robinhood Chain and its tokenized-stock / stock-meme / emerging venue mechanics;
4. Base / Aerodrome and EVM event/narrative migration.

A context pack supplies environment knowledge. It does not supply a bullish conclusion.

## 2. Research packet compiler

Astra should compile every serious candidate into the same canonical evidence object rather than improvising a prose answer.

Minimum stages:

```text
IDENTITY
-> MARKET / VENUE BINDING
-> EXECUTABILITY
-> CONTRACT / CONTROL
-> ECONOMIC ENTITY GRAPH
-> WALLET / HOLDER BEHAVIOR
-> NARRATIVE / PROPAGATION
-> VISIBILITY / CROWDING
-> FRAMEWORK CONTEXT
-> BLIND OPPOSITION
-> SYNTHESIS
-> FROZEN PROSPECTIVE OUTCOME BINDING
```

The compiler must preserve field-level provenance, `observed_at`, `available_at`, `computed_at`, source latency and missingness. Load-bearing conversions such as epoch time, decimals and token units remain deterministic code, never model inference.

## 3. Astra specialist passes

For high-value cases only, Astra may fan the same frozen packet into independent specialist passes. This is research decomposition, not a new multi-agent authority stack.

Recommended specialists:

### Chain mechanic / identity pass

Resolve exact chain, CA/mint, canonical pools, quote assets, duplicate instances, migration state and venue-specific mechanics.

### Economic entity / forensic pass

Cluster addresses conservatively using evidence edges. Distinguish address count from economic actor count. Do not award safety because no cluster was found.

### Execution / capacity pass

Estimate realistic route, depth, slippage, fees, latency, signal capacity and whether headline returns were executable at predefined notionals.

### Narrative / propagation pass

Identify narrative origin, derivative relationships, independent propagation versus syndication, exact-instance competition and current crowding.

### Bull pass

Build the strongest mechanism-supported continuation thesis from the frozen evidence only.

### Kill pass

Independently attack manipulation, concentration, liquidity, crowding, adverse selection, narrative exhaustion and hidden assumptions.

The bull and kill passes must not see one another before commit when `BLIND_OPPOSITION` is active.

Astra's synthesis may reconcile disagreements only after all passes are frozen.

## 4. The missing question: is the signal still ours?

The Memes v3 empirical-hardening work adds a critical dimension not present in the visible 563 preview: a useful signal can become economically useless because it is public, crowded or deliberately planted.

For every externally visible wallet/caller/agent signal, research:

- first public visibility timestamp;
- surfaces where it appeared;
- estimated follower capital, not merely follower count;
- executable depth at the signal time;
- entry lag between originating actor and public visibility;
- whether forward expectancy deteriorated after public labeling;
- whether the actor's behavior became more legible after gaining followers;
- whether the apparent signal could be bait.

Treat visibility as a candidate adverse-selection feature, not as proof of fakery.

Preferred research quantity:

```text
signal_capacity_pressure = estimated_follower_notional / executable_depth
```

This should be tested prospectively. Do not hard-code a universal follower-count cutoff.

## 5. Retrieval memory must contain failures

When Astra researches a new token, retrieval should not surface only famous winners.

Retrieve matched prior cases by:

- chain;
- venue;
- token age;
- liquidity bucket;
- market-cap / FDV bucket;
- launch type;
- narrative family;
- entry-state classification;
- entity-concentration pattern;
- propagation state.

The retrieved set must include both winners and matched failures from the Rejection Ledger / graveyard. A persuasive historical analogy is invalid if the nearest failed siblings are omitted.

## 6. Prospective apprenticeship loop

Every serious research packet becomes training material only after it is frozen before outcome.

Required loop:

```text
research candidate
-> freeze packet
-> freeze source and feature availability
-> register matched controls / rejected siblings
-> observe fixed-horizon outcomes
-> compute executable outcomes
-> score which claims survived
-> attribute misses to data / inference / execution / regime / manipulation
-> update research-memory evidence
-> propose one bounded change
-> re-test prospectively
```

No later win may rewrite an earlier wallet score, narrative score or confidence field.

## 7. Chain-native versus generic A/B experiment

Astra's first direct test of the 563 inspiration should be an A/B research experiment, not deployment.

### Arm A — generic free-form research prompt

Give the model only token identity and the same allowed sources.

### Arm B — canonical microcap contract + correct chain-native context pack

Give the model the same token, same decision time and same source budget, but require the structured contract.

Compare on a prospective, balanced set containing winners and failures.

Measure:

- identity errors;
- source coverage;
- factual completeness;
- hallucination rate;
- unresolved fields correctly left `UNKNOWN`;
- missed critical risk fields;
- repeat-run reproducibility;
- research time and token cost;
- ability to reject impostor / duplicate instances;
- quality of execution-risk estimates;
- ability to identify later failures;
- incremental information value over simple deterministic baselines.

Promotion criterion:

The chain-native compiler survives only if it improves research quality or forward discrimination enough to justify its extra cost.

## 8. Research output hierarchy

Internal truth comes first:

```text
RAW / PRIMARY EVIDENCE
-> NORMALIZED FACTS
-> ENTITY / MARKET STRUCTURE
-> INFERENCE
-> HYPOTHESIS
-> BULL + KILL PASSES
-> SYNTHESIS
-> OPTIONAL CONCISE THESIS
```

The concise bull thesis inspired by the visible 563 workflow is useful as a presentation layer. It is never the evidence object and can never overwrite it.

## 9. Astra source-recovery mission

When Astra has browser/research capability sufficient to revisit the source:

1. recover the exact original 563 three-part prompt if publicly accessible;
2. preserve it byte-for-byte or quote only within copyright limits where required;
3. diff its actual components against this compiler and `MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md`;
4. identify genuinely novel components;
5. reject redundant or weaker instructions;
6. test any novel component independently before adoption.

The source should remain `WORKFLOW_INSPIRATION_NOT_SIGNAL_EVIDENCE` even if the exact prompt is recovered.

## 10. What Astra should try to discover beyond the article

The highest-value extension is not better prose. It is discovering which research procedures themselves improve forward outcomes.

Astra should investigate:

- which fields most often prevent false positives;
- which chain-specific context actually adds lift versus generic research;
- whether entity-adjusted structure improves over raw holder metrics;
- whether visibility/capacity explains decay in public smart-wallet signals;
- whether early-confirmation states outperform sniper or chase states after costs;
- whether first-distribution survival identifies second-leg winners;
- whether exact-instance selection can be predicted before sibling divergence;
- which research fields can be removed with no loss, reducing cost and overfitting.

The long-term objective is a self-improving research process whose complexity is earned by prospective evidence.

## Guardrails

- No new market-state engine.
- No automatic BUY / SELL / sizing authority.
- No private-key or execution integration.
- No model identity confers authority.
- No source praise or social engagement is performance evidence.
- No retrospective winner can validate a feature without matched failures.
- Unknown stays unknown.
- Cheapest qualified executor handles routine work; Astra is reserved for high-VOI synthesis, conflict resolution and difficult cross-domain research.
