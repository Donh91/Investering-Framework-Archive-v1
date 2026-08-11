# Deep Research Horizon Queue Method v1

**Date:** 2026-08-11  
**Status:** OPERATIONAL_RESEARCH_QUEUE  
**Authority:** research evidence only  
**Owner:** Research Intake -> retained MCP sidecars -> Research Lab Red Team

## Purpose

Run a disciplined queue of deep research questions that improve understanding of market direction and cycle transitions at:

- 1-3 days
- 5-7 days
- 2-3 weeks
- explicit cross-horizon conflict

The queue is designed around the framework's practical objectives: earlier understanding of the best pre-altseason accumulation window, stronger discrimination of real versus fake rotation, and earlier recognition of distribution risk. It also improves general market-direction context without creating a parallel market-state engine.

## Governance boundary

This is an operational research queue, not a new forward-test registry and not a new engine.

Canonical unresolved questions remain owned by:

`01_CORE_FRAMEWORK/governance/2026-07-10__open-questions-register-v1-2__canonical.md`

Canonical active tests remain owned by:

`06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`

A queue item may support an existing Open Question or active test, but it cannot create a valid outcome row, change a test, add a new test, promote a rule or alter live framework semantics.

If a result suggests a framework change, route it to the existing owner and Research Lab Red Team. Any market-rule, threshold, weight, policy, sensor or portfolio change remains a separate governance proposal.

## Provider eligibility

A provider is usable only after the MCP connection evaluation program places it in a retained terminal state:

- `RESEARCH_ACTIVE_BASELINE`
- `RESEARCH_ACTIVE`
- `CROSSCHECK_ACTIVE`
- `SHADOW_OBSERVATION`
- `CANDIDATE_DISCOVERY_ACTIVE`
- `DIAGNOSTICS_ACTIVE`

`READY_FOR_TOOL_DISCOVERY`, `QUEUED`, `DATA_BLOCKED`, `HOLD`, `KILL` and blocked/unverified states are not usable.

Provider ceilings remain binding. For example:

- LunarCrush can provide shadow social-attention evidence but cannot become a framework sensor through this queue.
- CoinMarketCap can provide independent crosscheck/recovery evidence but cannot replace a canonical market-data owner.
- altFINS can provide candidate-discovery context but its technical signals are not framework permission.
- Binance Agent Native is diagnostics-only and remains unavailable until its official MCP surface is verified.

## Sequential execution

At most one deep-research item is active at a time.

Selection order:

1. P0 core-goal research
2. P1 leading/causal market-structure research
3. P2 calibration, latency, conflict and error-library research

If the next item is blocked by a provider that has not yet earned retention, the queue skips that item temporarily and selects the next executable item. This prevents a missing API key or blocked provider from stopping all research.

An item may be re-run later when a newly retained provider can materially deepen it. Re-runs must preserve the prior result and state exactly what new provider/evidence was added.

## Research waves

### Wave 0 - CoinGecko baseline

Immediately available.

Focus:
- cross-horizon directional evidence map
- breadth/alt participation
- horizon conflict
- false-positive/false-negative research context
- leader/laggard structure

Purpose: establish a reproducible baseline before richer connections are allowed to influence research.

### Wave 1 - Dune

Begins only if Dune survives the connection pilot.

Adds:
- stablecoin/liquidity deployment
- onchain/exchange-flow asymmetry
- DEX activity
- rotation sequence
- pre-altseason and distribution anatomy

### Wave 2 - LunarCrush

Begins only inside its shadow ceiling.

Adds:
- social acceleration lead/lag
- euphoria versus participation
- narrative durability
- narrative-capital decoupling

No social metric becomes a framework sensor automatically.

### Wave 3 - CoinMarketCap

Crosscheck/recovery only.

Adds:
- independent market-cap/volume/category comparison
- source discrepancy analysis
- provider-recovery value

### Wave 4 - The Graph

Used only where protocol/contract-level evidence adds something beyond Dune.

Adds:
- protocol activity breadth
- usage persistence
- contract-level confirmation or falsification

### Wave 5 - altFINS

Candidate discovery only.

Adds:
- technical candidate surfacing
- leader/laggard and breadth exploration

Its technical signals may nominate research targets but cannot create trading permission.

### Wave 6 - Binance Agent Native

Diagnostics only after official MCP endpoint and tool surface are independently verified.

Potential use:
- public market/API diagnostics
- spot/derivatives context crosscheck

No order, account, portfolio or fund-movement tool is permitted.

### Wave 7 - retained-provider synthesis

Only providers that survived their individual pilots may participate.

The purpose is not to maximize source count. It is to determine the smallest provider set that materially improves:

- 1-3d tactical understanding
- 5-7d rotation/continuation understanding
- 2-3w cycle-transition understanding
- altseason pre-trigger context
- distribution precursor context

## Required question structure

Every queue item must define:

- research question
- horizon
- primary goal
- required and optional providers
- baseline
- hypothesis
- decision divergence
- falsifier
- kill condition
- integration ceiling
- links to existing canonical questions/tests when relevant

No queue item is promotable merely because the answer sounds coherent.

## Required evidence structure

Each research result must separate, per horizon:

- evidence for risk-on
- evidence for risk-off
- evidence for range/chop
- evidence for transition
- conflicts
- unknowns
- provider provenance

Cross-horizon output must additionally identify:

- agreement
- conflict
- possible leading evidence
- confirming evidence
- late/redundant evidence

These are research classifications, not canonical market states.

## Directional discipline

The queue must not force one conclusion when horizons disagree.

Examples:

- 1-3d risk-on + 2-3w weak -> preserve conflict.
- 1-3d stress + 2-3w improving -> distinguish tactical flush from cycle deterioration.
- 5-7d broadening + 2-3w flat -> investigate whether rotation is early, false or data-incomplete.

Missing data remains unknown. It is not bearish evidence.

## Research Lab gate

Any finding proposed for wider framework use must pass the existing Research Lab Red Team method:

- measurable decision divergence
- baseline comparison
- strongest supporting case
- strongest falsification case
- false-positive cost
- false-negative cost
- provenance
- falsifier
- kill condition
- explicit authority boundary

Model agreement is not independent evidence.

## Integration classes

Allowed queue outputs:

- `RESEARCH_CONTEXT_ONLY`
- `EXISTING_TEST_SUPPORT_ONLY`
- `SHADOW_OBSERVATION_ONLY`
- `CROSSCHECK_ONLY`
- `CANDIDATE_DISCOVERY_CONTEXT_ONLY`
- `RESEARCH_INFRASTRUCTURE_ONLY`

None of these classes changes live framework state.

## Initial active research

At initialization only CoinGecko is in a retained usable state.

The first active item is therefore:

`DRQ-001 - Cross-Horizon Directional Market Map - Baseline`

Dune-dependent P0 studies remain visible but waiting. The queue may still advance to other CoinGecko-only items while Dune is being evaluated.

## Success condition

The program succeeds if, over time, it produces a smaller set of high-value research inputs that:

- improve horizon-specific understanding;
- expose useful conflicts earlier;
- reduce explanatory duplication;
- clarify pre-altseason versus fake-rotation context;
- clarify continuation versus distribution context;
- preserve complete provenance;
- and remain outside market/portfolio authority until separately ratified.

The program fails if it becomes a parallel prediction engine, rewards provider count, invents semantics, or produces research that cannot change or falsify an interpretation.
