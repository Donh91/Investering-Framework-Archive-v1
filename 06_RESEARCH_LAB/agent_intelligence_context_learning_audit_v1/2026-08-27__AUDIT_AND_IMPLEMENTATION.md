# Agent Intelligence, Context Routing, Learning Loop and Sensor Compression Audit v1

Date: 2026-08-27
Authority: RESEARCH_ONLY_NON_CANONICAL
Portfolio authority: NONE
Canonical state authority: NONE

## Executive verdict

The framework is no longer primarily collection-constrained. It is increasingly **routing- and learning-constrained**.

At audit time the operations layer reported a fresh Daily Capture, fresh experiment registry/receipt sync, 153 experiment candidates and 142 matured outcomes, while the Daily Director still described some families as missing even though at least BTC dominance and macro evidence existed elsewhere in the repository/capture plane. This demonstrates the core rule:

> A collected datum is not available to an agent unless it is deterministically routed into that agent's context.

The framework's artifact-mediated agent architecture is sounder than free-form agent-to-agent chat because evidence is inspectable, hashable and replayable. However, artifact production alone is not collaboration. Collaboration is only established when an upstream output is routed, consumed, and can be traced into a downstream hypothesis, forecast, experiment or negative-learning decision.

## P0 operational findings

### O1 Historical altseason throughput gate was stale relative to the retired reservation lane

The throughput gate still treated `historical-altseason-cfgi-reservation.yml` as a main writer even though the reservation workflow is explicitly retired, read-only and manually dispatchable. This caused repeated gate failures.

Decision: FIX.

The gate now validates the reservation lane as retired/read-only and excludes it from writer assertions. Bounded artifact-retention assertions are explicit for the actual publisher workflows.

### O2 Automation health artifact-retention false positive

The production-health scanner uses substring detection for `actions/upload-artifact@`. A gate workflow that merely quotes that token in validation code can therefore look like an artifact uploader. Explicit `retention-days: 30` validation is now present in the throughput gate, preventing the current false positive without weakening bounded-retention requirements.

Longer-term improvement: static workflow health should parse YAML steps rather than raw substrings.

### O3 Weekly output TARGET_HASH_MISMATCH

The weekly delivery pointer declares the machine package's `package_sha256`, while the operations dashboard compares that declaration with the SHA-256 of the final serialized file that itself contains `package_sha256`. These are different hash semantics and cannot generally be equal without a fixed-point construction.

Decision: BUG CONFIRMED. The dashboard verifier must distinguish semantic package hash from file-byte hash instead of treating the package's self-hash as a byte hash.

This is an observability defect, not evidence that the W34 package content is necessarily corrupt.

## Agent intelligence and context-routing findings

### A1 Collectors work, but context coverage is incomplete

The current capture plane contains macro values including DGS2, DGS10, DTWEXBGS and VIXCLS. A separate daily BTC-dominance owner also persists a current direct-source series. Yet the latest Director output stated that macro and BTC dominance were missing.

Macro may have been absent in the specific earlier context used for that Director run, so this audit does not rewrite that historical output. The important structural finding is that specialist owners outside the base capture are not automatically visible to the Director.

Decision: IMPLEMENT deterministic context routing for BTC dominance and experiment learning. Preserve source hashes and missingness.

### A2 Agents do not need free-form chat to collaborate

Current architecture communicates through owner payloads, immutable captures, context files, receipts, conflict-router outputs, experiment registries and matured outcomes. This is preferable to unsourced agent conversation.

The missing capability is not 'more talking'. It is **closed-loop evidence routing**.

### A3 Matured experiment learning was not explicitly routed back into the Daily Director

The experiment registry had substantial matured evidence, but `augment_director_context_v2.py` did not provide a bounded summary of supported/not-supported/inconclusive outcomes to the next Director context.

Decision: FIX.

A deterministic post-augmentation step now routes a bounded learning summary. `MATURED_SUPPORTED` and `MATURED_NOT_SUPPORTED` may act as prior evidence/counterevidence. `MATURED_INCONCLUSIVE` is explicitly forbidden from being treated as support. No state can promote itself to canonical authority.

### A4 Information-loss guard

New contract: `DIRECTOR_CONTEXT_ROUTING_v1`.

Principles:
- collected != routed;
- routed != authoritative;
- missing remains missing;
- a present top-level context family must not be called missing merely because another nested object omits it;
- every routed family carries path/hash provenance where practical;
- learning feedback is bounded to avoid context bloat.

## Learning-loop audit

Current experiment lifecycle demonstrates genuine maturation, not merely candidate generation. However, the distribution is important: many outcomes are inconclusive, and only a small subset are supported or not-supported.

Interpretation:
- this is not evidence of failure by itself;
- it is evidence that 'number of experiments' is a poor success metric;
- the valuable unit is a matured, decision-relevant, reproducible learning that changes future interpretation or kills a hypothesis.

New closure test:

`observation -> hypothesis -> prospective candidate -> matured outcome -> bounded learning context -> later Director interpretation`

A learning loop is not considered closed merely because an outcome file exists.

## Sensor compression / redundancy tournament

The repository already has the correct machinery in `shared_row_model_tournament_v1`; creating a second sensor tournament would be sensor-governance duplication.

Current `RELEVANCE_STATE.json` is `COLLECTING` with `eligible_row_n=0`, `divergence_n=0`, and terminal verdict `INSUFFICIENT_EVIDENCE`. Therefore no sensor can honestly be removed or promoted from this tournament yet.

Decision:
- DO NOT create another tournament.
- DO NOT prune sensors from zero eligible shared rows.
- Continue the existing prospective tournament.
- Use K16 containment/redundancy logic for obvious structural duplicates before empirical maturation.

This is negative learning: the framework has enough compression machinery, but not enough eligible shared-row evidence yet.

## Highest-value next research target

After operational and routing repairs, the highest-value market research problem remains:

`MID_CYCLE_PULLBACK versus TERMINAL_DISTRIBUTION`

This should be a classifier/challenger problem, not a new single indicator. Candidate information families:
- breadth and participation;
- ETH/BTC leadership and persistence;
- BTC dominance path;
- spot/aggressive flow;
- funding/OI/leverage/liquidations;
- stablecoin liquidity/deployment;
- ETF flow quality;
- rates/dollar/VIX macro context;
- Copper/Gold slow-cycle shadow;
- NFCICREDIT only if its preregistered research path survives source/vintage tests.

Guardrails:
- prospective first;
- no threshold search on known tops;
- small-N acknowledged;
- negative controls required;
- family-level redundancy before voting;
- no portfolio execution authority;
- confirmation and persistence over anticipation.

## What this mission changes

1. Repairs the stale historical-altseason throughput gate assumptions.
2. Makes artifact retention explicit in that gate.
3. Adds deterministic BTC-dominance routing to the Daily Director context.
4. Routes bounded matured experiment learning back to the Daily Director.
5. Adds a context-routing contract that distinguishes collection, routing and authority.
6. Reuses, rather than duplicates, the existing shared-row tournament.
7. Records the weekly hash mismatch as a hash-semantics bug requiring verifier repair.
8. Establishes mid-cycle-vs-terminal classification as the next high-value research problem after the operational/routing layer is green.

## Kill criteria for this architecture change

Rollback or modify if:
- routed learning materially bloats Director context/cost;
- experiment learning is treated as automatic authority;
- BTC dominance routing cannot preserve deterministic provenance;
- Director outputs begin treating inconclusive outcomes as support;
- routing makes stale data appear current;
- the added context causes workflow congestion or repeated failures.

## Final assessment

Collectors: **FUNCTIONAL WITH OPERATIONAL DEBT**.

Agent analysis: **FUNCTIONAL AND INCREASINGLY USEFUL**.

Agent collaboration: **PARTIAL, ARTIFACT-MEDIATED, NOT YET FULLY CLOSED LOOP**.

Primary bottleneck: **CONTEXT ROUTING + LEARNING CLOSURE, NOT SENSOR COUNT**.
