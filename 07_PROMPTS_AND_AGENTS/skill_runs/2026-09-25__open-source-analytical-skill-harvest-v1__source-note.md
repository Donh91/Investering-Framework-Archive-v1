# Open-Source Analytical Skill Harvest v1

**Date:** 2026-09-25  
**Status:** SOURCE_NOTE / ADMISSION_REVIEW  
**Scope:** external agent skills, deep-research systems, evaluation frameworks, finance/onchain analysis patterns  
**Authority:** research/design only - no market, portfolio, automatic-trading or automatic skill-promotion authority  
**Local owners reviewed:** `.agents/skills/research-lab-red-team/SKILL.md`, `.agents/skills/prospective-evidence-ledger/SKILL.md`, `.agents/skills/developer-source-research/SKILL.md`, `.agents/skills/skill-quality-gate/SKILL.md`, `.agents/skills/meme-alpha-supervisor/SKILL.md`

## Mission

Review 10-20 current public GitHub repositories for analytical mechanisms that can improve the existing Investering framework without importing overlapping frameworks or creating parallel truth engines.

The harvest is mechanism-first:

`external mechanism -> local gap -> existing owner -> bounded test -> admission decision`

No third-party executable code or prompt text was copied into active local skills by this mission.

## Dedupe baseline

The local stack already owns:

- repository authority/context routing;
- prospective evidence lifecycle and frozen point-in-time rows;
- red-team/falsification and no-self-promotion;
- external developer-source verification;
- skill baseline/candidate quality evaluation;
- Alpha Lab exact-CA, source-authentication, wallet-forensics and prospective-learning discipline;
- explicit UNKNOWN/degraded semantics, budget hard stops and bounded work queues.

Therefore a third-party project is not valuable merely because it has "deep research", "red team", "finance", "OSINT", "agent", or "skill" in its name.

## Repositories reviewed

| # | Repository | Reviewed revision | License observed | Load-bearing mechanism inspected | Local disposition |
|---|---|---|---|---|---|
| 1 | machachlouei/evidence-graph | `67bcf9fee4b77174d69ecb9f96866c5873b1acc2` | MIT | atomic claim graph, typed support/contradiction edges, contradiction hunter, skeptic, stability stop | **EXTRACT** |
| 2 | atchisonbrent/deep-research | `c3397c84ab626ab1c96a4132b8c579703d87d8fc` | MIT | atomic claims, quote verification, source independence groups, strict validator, competing hypotheses | **EXTRACT** |
| 3 | ngtiendong/Academic-Research-Agent-Skill | `41c611c2e36461596c0c072e7641f9ddba251be8` | MIT | cheapest decisive falsifier, mandatory claim-node kill, reality/feasibility gates | **EXTRACT** |
| 4 | Xrrr1111/deep-research-agent | `1741dc85b6ee69058a8b748a94190d6b547b86f7` | MIT | bounded turns/search budgets, duplicate/no-progress guards, replanning, durable trace, insufficient-evidence terminal state | **EXTRACT** |
| 5 | ByteDance-BandAI/ReportBench | `ca3d65b9ff3136fd7e6107955eeb711b2a7fd894` | Apache-2.0 | cited-statement extraction, citation consistency, uncited factual-statement verification, precision/recall evaluation | **EXTRACT_FOR_EVALS** |
| 6 | SkyworkAI/DeepResearchAgent | `5e3c95d14266f8c4aa6a5deae1fe165c7cd1b87b` | MIT | versioned resource lifecycle plus propose/assess/commit/rollback self-evolution contract | **EXPERIMENT** |
| 7 | JinheonBaek/ResearchAgent | `babb49b51ebfcebedc39ccde12c9785be7bef46c` | LICENSE_UNVERIFIED | parallel multi-dimensional validation and iterative refinement | **CONCEPT_ONLY_EXPERIMENT** |
| 8 | Silence-view/deep-research | `b238ab74c0daaf4b2a46a3cf9fffa5201367f6bc` | MIT | recursive citation chasing, source credibility dimensions, independent triangulation, separate QA wave | **EXTRACT_WITH_MODIFICATION** |
| 9 | ever-just/agentskills | `d2e89c0f7b29c8f10ecabd1108f0969d55152047` | MIT repository; per-skill license may vary | verification/retraction audit, source waterfalls, freshness/ToS annotations, anti-pattern-rich skill design | **EXTRACT_SELECTIVELY** |
| 10 | 24601/agent-deep-research | `1b90f0df29b3053b9599ff0c9ffe1a3ababe321c` | MIT | dry-run cost estimation, structured output, adaptive polling, persistent session state | **REFERENCE** |
| 11 | himself65/finance-skills | `7fe91853b536304b13bce210ecf8b685cf77ec48` | MIT | deterministic finance calculations, router-pattern skills, pass/fail gates, skill authoring rubric | **REFERENCE_SELECTIVELY** |
| 12 | OctagonAI/skills | `51e938c4d086f658de8bdcf734e864d34637167e` | MIT | narrow financial research skills, filing/risk decomposition, source-specific analyst orchestration | **REFERENCE** |
| 13 | ohjay-official/mantle-onchain-research-agent | `83e0434fd98013be978e9c4ae7b75ab44c84f16b` | LICENSE_UNVERIFIED | onchain source hierarchy, SINGLE-SOURCE/UNVERIFIED tags, cause-effect brief | **REFERENCE_ONLY** |
| 14 | lingzhi227/agent-research-skills | `9e6c085d65e313e475e921fdfe795ac11eb7589e` | LICENSE_UNVERIFIED | hard phase gates requiring deep reading and implementation survey before synthesis | **REFERENCE_ONLY** |
| 15 | CaseMark/skills | `afe48c44914d753297766404378e871d1f88d7a8` | Apache-2.0 | very large domain-skill catalog and QA/skill-spec organization | **REJECT_BULK_IMPORT** |
| 16 | neurofoo/agent-skills | `0e7ac2aa4d094352a082ebeedf1dbb4c52b77782` | MIT | generic adversarial red-team checklist | **REJECT_OVERLAP** |
| 17 | qodex-ai/ai-agent-skills | `6ea9f00885c5dc5e6d9435d443dbf7d9ce865e29` | LICENSE_UNVERIFIED | generic plan/gather/evaluate/synthesize research recipe | **REJECT_OVERLAP** |
| 18 | grapeot/deep_research_agent | `35fd19bf45dda700383c9900e229e3d82681af48` | MIT | document-centric scratchpad and persistent context | **REJECT_AS_ALREADY_OWNED** |

## Highest-value mechanisms

### H1 - Cheapest decisive falsifier

**Source:** ngtiendong/Academic-Research-Agent-Skill.

Before a broad deep dive, identify the cheapest observation that can decisively invalidate a mandatory thesis node. If it fails, stop or narrow instead of manufacturing a rescue narrative.

**Why this is incremental:** local red-team already falsifies, but it does not consistently require *falsifier ordering by cost and decisiveness before research expansion*.

**Best local owners:** `research-lab-red-team`, composed into `meme-alpha-supervisor`.

### H2 - Source independence groups

**Sources:** atchisonbrent/deep-research; Silence-view/deep-research.

Corroboration should count independent underlying evidence paths, not URLs/domains. Syndication, copied press releases, shared datasets, one anonymous source repeated by five outlets, or multiple model summaries of one artifact remain one evidence root.

**Why this is incremental:** Alpha Lab already has `control_root_id` for first-party authentication and the red-team skill rejects model consensus as independent evidence. The missing piece is a general cross-domain `independence_group` discipline.

**Best local owners:** `developer-source-research` + `research-lab-red-team`.

### H3 - Atomic claim/evidence graph with contradiction-first search

**Sources:** machachlouei/evidence-graph; atchisonbrent/deep-research.

Represent material claims atomically and explicitly link support, contradiction, qualification and extension. An unresolved contradiction becomes a research target instead of being averaged away in prose.

**Why this is incremental:** the framework has evidence ledgers and red-team outputs but not a generic graph/stability representation for research claims.

**Best local owner:** Research Lab shadow sidecar composed with `research-lab-red-team`; it must not become a second canonical evidence engine.

### H4 - No-progress and repeated-action guards

**Source:** Xrrr1111/deep-research-agent.

Stop/replan on duplicate query, duplicate URL, repeated action, no new evidence, exhausted per-question budget, wall-clock cap or insufficient evidence.

**Why this is incremental:** Alpha Lab already has bounded tasks and budget guards, but generic research loops can still spend tokens without increasing evidence.

**Best local owners:** autonomous research runtime / `meme-alpha-supervisor`; later reusable by other research owners.

### H5 - Research-output factuality and citation evals

**Source:** ByteDance-BandAI/ReportBench.

Evaluate the *report*, not merely workflow health:
- cited factual statement coverage;
- claim-to-citation consistency;
- uncited factual statements;
- factual verification of uncited claims;
- precision/recall-like coverage against a frozen reference set where possible.

**Why this is incremental:** the local skill quality gate tests routing, safety and behavior, but does not yet systematically measure factual/citation quality of research outputs.

**Best local owner:** `skill-quality-gate`, as an evaluation family, not a new production researcher.

### H6 - Versioned self-evolution with rollback

**Source:** SkyworkAI/DeepResearchAgent.

Separate the resource being improved from the improvement protocol. Treat prompt/skill/agent/tool versions as registered resources and require `PROPOSE -> ASSESS -> COMMIT` with lineage and rollback.

**Why this is incremental:** local baselines and governance already cover much of this, but the explicit rollback/evolution state model can strengthen Compounding Learning and skill evolution.

**Best local owners:** existing Skill Quality Gate + Compounding Learning Controller. Never grant self-modification or self-merge authority.

### H7 - Multi-dimensional independent review without score averaging

**Source:** JinheonBaek/ResearchAgent.

Run separate reviewers on orthogonal dimensions. The useful pattern is reviewer separation, not its 1-5 aggregate scoring.

For Alpha Lab a local variant could use:
`IDENTITY / PROVENANCE / CAUSALITY / MARKET-EXECUTION / SELLABILITY / NOVELTY`.

Critical dimensions may veto. Numeric averaging may not override a failed hard gate.

**Best local owner:** `research-lab-red-team`.

### H8 - Bounded source-of-source chasing

**Sources:** Silence-view/deep-research; atchisonbrent/deep-research.

For load-bearing secondary claims, chase backwards to the underlying primary record and, where useful, one forward/independent path. Bound depth and budget.

**Why this is incremental:** developer-source-research already prefers primary evidence, but a formal "source of source" recovery step can reduce secondary-source inheritance.

**Best local owner:** `developer-source-research`.

## Things deliberately not adopted

- Silence-view's fixed "3+ sources = verified" style rule is not adopted. Three dependent sources are not three independent evidence paths.
- Generic source credibility scores are not allowed to override claim-specific evidence or hard gates.
- ResearchAgent's Likert ratings are not adopted as a combined decision score.
- Evidence-graph structural confidence is not imported as market/alpha confidence.
- CaseMark's thousands of skills are not bulk-imported.
- Finance-skills thresholds, SEPA logic, valuation heuristics and trading rules are not imported into market authority.
- Ever-just OSINT endpoints are not automatically activated. Public-project/business OSINT may be tested later under privacy/ToS/source-health governance.
- Third-party agent code is not executed by this review.

## License boundary

Direct code/prompt copying is not required for any current candidate. The preferred action is to synthesize local procedures from the observed mechanism and test them against frozen local baselines.

Where license metadata was not established, disposition is concept-only/reference until license evidence is independently verified.

## Admission recommendation

Proceed in waves:

**Wave A - small local procedure changes with high expected value**
1. cheapest decisive falsifier;
2. source independence groups;
3. bounded source-of-source chasing.

**Wave B - shadow mechanisms requiring evidence**
4. atomic claim/evidence contradiction graph;
5. no-progress/repeated-action research guards;
6. research-output factuality/citation evals.

**Wave C - architecture experiments only**
7. versioned self-evolution/rollback;
8. multi-dimensional independent reviewer panel.

No new top-level scanner, forecast engine, market scorer or portfolio authority should be created.

## Success criterion

The harvest is valuable only if a candidate beats its current local baseline on a frozen case set without introducing a critical authority/safety regression or increasing unnecessary research cost.

The machine should prefer `KEEP_BASELINE` over additional complexity when incremental value is not demonstrated.
