# Alpha Lab Prospective Readiness + Source Learning Audit v1

Date: 2026-09-21
Status: PRE_PROSPECTIVE_HARDENING / RESEARCH_ONLY
Owner: #1087
Authority: no trade, no production promotion, no model-weight change

## Why this audit now

The historical false-negative/matched-denominator packet has improved falsification, but the canonical Rick addendum correctly says the highest-leverage step is real prospective rows. This audit therefore asks what can still corrupt those rows before the Project→CA and FOMO paths start accumulating evidence.

## Readiness verdict

**NOT YET READY TO CLAIM PROSPECTIVE EDGE. READY TO PREPARE PROSPECTIVE OBSERVATION.**

The architecture has the required components, but five measurement hazards must remain explicit during activation.

### R1 - discovery-source denominator can silently disappear
A source outage, parser failure, unavailable page or empty query must not become 'no project/no candidate'. Existing UNKNOWN discipline covers this conceptually, but prospective Project Memory must retain source-health coverage at each observation cut.

Required observation fields:
- source_family
- source_locator
- query_or_collection_id
- retrieved_at_utc
- source_event_time_or_null
- source_health
- coverage_state
- raw_evidence_hash
- project_trial_ids_emitted

Zero emitted projects is valid only with healthy coverage.

### R2 - first-seen source attribution must be separate from identity truth
A directory, caller, wallet or social account may discover a project first without being authoritative for project/token identity.

Freeze separately:
- discovery_source_first_seen
- identity_authority_source
- exact_ca_binding_source
- first_market_observation_source

Never overwrite the first because a stronger source appears later.

### R3 - project-level and token-level clocks must not collapse
For project-first edge, at least these clocks must remain distinct:
- T_project_first_seen
- T_material_change
- T_ca_candidate
- T_bound_high
- T_market_eligible
- T_champion_first_seen
- T_broad_social_or_KOL
- T_outcome_maturity

Lead-time claims require comparable clocks and availability timestamps. Missing clock = UNKNOWN, not zero lead.

### R4 - Deep Dive load is part of the denominator
A project-first architecture can fake recall by sending everything to Deep Dive. Every eligible project trial therefore needs a frozen route outcome, including REJECT/RETAIN/DEEP_DIVE, plus queue/budget context.

Required metrics:
- eligible project trials
- Deep Dives
- qualified watches
- false identity links
- critical evidence losses
- source-health exclusions
- DD load per eligible trial
- recall/FNR after outcome maturity

### R5 - source/caller learning can become an ATH leaderboard
P3 must learn whether a source adds **early, realizable, independent information**, not whether it once mentioned a later winner.

Caller/source scorecard should only use prospective frozen rows and include:
- eligible calls/projects
- first-seen count
- independent-first-seen count
- median lead to champion/public market/social
- exact identity accuracy
- sellability at frozen observation
- realizable MFE/MAE after frozen entry assumptions
- false-positive/reject burden
- source-health/coverage
- contribution conditional on other evidence families

No ATH-only ranking and no retrospective promotion.

## Source-family priority hypothesis for prospective measurement

This is a **measurement order**, not a weight table and not a promotion rule.

Tier A - cheap deterministic discovery:
1. authenticated ecosystem/buildathon/project directories;
2. on-chain deployment/factory events;
3. GitHub release/deployment/config changes with Robinhood anchors;
4. package registry releases with chain-specific anchors.

Tier B - identity/mechanic verification:
5. first-party docs/app/site;
6. authenticated project social publication;
7. verified contract/control-root evidence;
8. Pons/factory relation as candidate evidence.

Tier C - corroboration/context:
9. wallets/callers;
10. market aggregators;
11. general social/KOL propagation;
12. broad web/search.

Reason: A should maximize early cheap recall; B should establish what the project/CA actually is; C should measure corroboration and public propagation. A source may move tiers later only from prospective evidence, never from a historical winner.

## Source-learning receipt

For each source observation freeze:
`source_observation_id`
`project_trial_id`
`source_family`
`source_locator`
`observed_at_utc`
`available_at_utc`
`source_event_at_utc_or_null`
`source_health`
`coverage_state`
`evidence_sha256`
`discovery_role = FIRST_SEEN | CORROBORATION | IDENTITY_AUTHORITY | MARKET_CONTEXT`
`independent_of_prior_source = TRUE | FALSE | UNKNOWN`
`project_state_at_observation`
`token_state_at_observation`

The same evidence mirrored across websites must not count as independent source convergence.

## Historical cases converted to regression questions, not scores

- Boost Town: would Tier A/B retain project before market hype and later bind exact CA?
- lpTOKEN.fun: would the same path retain the project while correctly preserving NO_PROJECT_TOKEN?
- MEEP vs Neon Mech Legion: can product-live evidence avoid implying fungible-token opportunity?
- QLWY: can bridge/continuity evidence prevent false NEW_TOKEN classification?
- DARK vs BiX Robin: can falsifiable product/economic evidence distinguish generic AI language without using outcome?
- NET/SAFIX vs Oasis: can identity/mechanic evidence improve Deep-Dive selection without treating RWA/credit as alpha?
- RobinFlow: can serious infrastructure remain in denominator with no token opportunity?

## Prospective activation checklist

A Project→CA prospective counter may start only when:
1. P1 Project Memory passes focused tests and independent review.
2. Source health/coverage is retained for zero-result observations.
3. project/token clocks are distinct.
4. first-seen source cannot be overwritten.
5. P2 binding is fail-closed and false-link tolerance remains zero.
6. Deep-Dive route/reject is recorded for every eligible trial.
7. historical design cases cannot increment prospective counters.
8. outcome fields are unavailable to pre-maturity routing.
9. duplicate/mirrored sources do not create independent evidence.
10. explicit activation receipt sets counters to zero.

FOMO prospective convergence additionally remains blocked by the separate Sol runtime audit until its fail-closed remediation passes.

## Sol conclusion

Do not add another scanner. The next intelligence gain is measurement quality:
**source coverage -> immutable first seen -> project memory -> exact identity -> bounded Deep Dive -> realizable outcome -> conditional source learning.**

If this chain is preserved, future false negatives can be attributed to a specific stage rather than becoming vague 'scanner misses'. That attribution is the prerequisite for compounding learning.
