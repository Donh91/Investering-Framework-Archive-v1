# EXTERNAL ALPHA DISCOVERY POLICY v1

Status: STANDING / RESEARCH ONLY
Owner: #937
Scientific lifecycle: #885

## Objective

Find a small number of external systems where the expected learning value justifies forensic research cost.

Discovery is not a popularity contest and not a feed of trading recommendations.

The lane should prefer systems whose actions can be reconstructed point-in-time and falsified against simple baselines.

## Discovery inputs

Permitted read-only discovery sources include:

- user-supplied links, screenshots and repositories;
- public GitHub repositories and issues;
- public research papers / preprints;
- public X/social posts as discovery leads only;
- public chain explorers / APIs;
- public prediction-market profiles / APIs;
- public dashboards, docs and archives;
- reputable independent technical audits or reproducibility reports.

Paid/restricted/private data may only be used under the Framework's existing data and permission boundaries.

## Default prior

Every new candidate begins as `UNADMITTED`.

The burden of proof is on the candidate.

Do not create a new case because:

- the bot is viral;
- an LLM is mentioned;
- a chart shows high Sharpe;
- a wallet has a large PnL screenshot;
- a strategy has a high win rate;
- a creator claims autonomous execution;
- a repository has many stars.

These facts may justify discovery, never promotion.

## Deduplication before research

Before opening a new case:

1. compare source identity / URLs against `EXTERNAL_ALPHA_REGISTRY.json`;
2. search existing `AT-SRC-*` notes;
3. search case-specific queues and killed candidates;
4. search current Framework owners for the claimed primitive;
5. classify the new item as:
   - new evidence for existing candidate;
   - new external candidate;
   - duplicate architecture;
   - hypothesis-only inspiration;
   - reject/noise.

A new post about Edge, MAEVE, FOMO Radar or STAMPEDE normally updates the existing candidate.

## Fast rejection screen

Reject or hold at WATCH if one or more of these dominate the case:

- performance is only screenshots or creator assertions;
- only winners are visible;
- timestamps are retrospective or editable;
- identity cannot plausibly be resolved;
- trade/action history is too small to distinguish edge from luck;
- no usable baseline or counterfactual exists;
- execution assumptions are impossible to reconstruct;
- the claimed edge depends on inaccessible proprietary data with no observable behavior to study;
- apparent value duplicates an existing Framework primitive with no plausible incremental benefit;
- legal/licensing or security boundaries make responsible research impractical.

## High-value discovery traits

Prefer candidates with:

- public forward records rather than retrospective backtests;
- immutable/on-chain/venue receipts;
- both winners and losers;
- sufficient row count or long enough time coverage;
- explicit entry/exit/action timestamps;
- reconstructable candidate universe / no-action controls;
- executable price, liquidity, fee or latency evidence;
- identifiable version changes;
- transparent open-source components that can be ablated;
- a mechanism materially different from already tested Framework owners.

## Research-value priority

When multiple candidates compete for attention, rank expected information value approximately as:

`evidence quality x mechanistic novelty x transferability x falsifiability / research cost`

This is a prioritization heuristic, not a performance forecast.

Favor experiments that can either produce a reusable primitive or kill an attractive false story cheaply.

## Promotion workflow

Discovery agent may nominate:

- `REJECT`
- `WATCH`
- `RESEARCH_QUEUE`
- `REVERSE_ENGINEER`

It may not grant:

- verified source alpha;
- copyability;
- scalability;
- transfer to execution.

Those require result artifacts under #885.

## Candidate research packet

A candidate admitted to `RESEARCH_QUEUE` should have, at minimum:

1. exact candidate identity or explicit unresolved-identity task;
2. sources and retrieval context;
3. all material performance claims marked by evidence class;
4. proposed action-ledger source;
5. proposed opportunity-set/control source;
6. execution/cost-data plan;
7. expected reusable primitive(s);
8. explicit falsifiers / kill criteria;
9. smallest next experiment;
10. authority boundary.

Use `CANDIDATE_INTAKE_SCHEMA.json` for intake structure.

## Autonomous cadence

Standing supervisors / future Astra may run discovery opportunistically when:

- user provides a new candidate;
- a trusted research source surfaces a genuinely new system;
- an existing candidate publishes new primary evidence;
- the active research queue has capacity.

Broad web discovery should be periodic and budget-aware rather than continuous high-cost crawling.

A reasonable default is a weekly bounded discovery pass plus event-driven intake from user links. Existing higher-authority scheduler/supervisor policy controls the actual runtime cadence and model budget.

## Stop rules

Stop spending research budget when a hard falsifier is met.

Examples:

- complete ledger shows no post-cost source edge;
- headline PnL is mostly leverage/compounding with no predictive edge;
- opportunity-set reconstruction reveals selection bias;
- copy delay destroys expectancy;
- source identity cannot be resolved;
- strategy is too capacity constrained to matter;
- proposed primitive adds no incremental value over an existing owner.

Preserve the rejected case and reason. A killed candidate is useful negative evidence and should prevent repeated rediscovery work.

## Relationship to user-supplied links

User-supplied links enter through the same evidence gate as autonomous discoveries.

The Framework should be especially responsive to them, but never lower scientific standards because a candidate was manually supplied.

The preferred user-facing outcome remains short:

`REJECT / WATCH / RESEARCH_QUEUE / REVERSE_ENGINEER` plus the single highest-value reason and next action.

## Success metric

Discovery quality is measured by:

- fraction of admitted candidates that produce decisive evidence;
- number of reusable primitives independently validated;
- false-positive research cost avoided;
- duplicate research avoided;
- time from discovery to falsifiable experiment;
- ability to preserve and reuse negative results.

Candidate count itself is not a success metric.
