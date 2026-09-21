# Project -> CA Bridge - Sol Prebuild Specification P2-P6 v1

Status: PREIMPLEMENTATION_FROZEN / SHADOW_ONLY
Owner: #1087
Parent: PROJECT_CA_INTELLIGENCE_BRIDGE_SHADOW_BUILD_CONTRACT_v1
Prerequisite: P1 Project Memory must pass its own focused tests, independent review and fresh-main readback before any P2 code write.
Design supervisor: GPT-5.6 Sol High
Code policy: leave only irreducible code writes to the authorized code executor.
Production/trade/alert authority: NONE

## Purpose

Reduce P2-P6 to deterministic implementation work without changing the frozen A/B/C experiment. This document is not permission to implement later packets early.

## Cross-packet invariants

- Same frozen unique eligible project trial is the denominator unit.
- Project identity is separate from token identity.
- Token primary key is exact `chain_id + token_ca`.
- Name/ticker/logo/social similarity never proves identity.
- UNKNOWN and CONFLICTED are first-class states.
- Historical evidence is append-only or explicitly superseded.
- NET, SAFIX/SFX and DARK remain design/regression cases with zero prospective credit.
- No packet may create a scanner, scheduler, parallel ledger, trading engine, user-alert owner or production promotion path.
- No outcome field may influence discovery, identity, material-change or A/B/C routing before maturity.
- A/B/C share the exact same frozen input and source-availability cut.
- P2-P6 remain blocked until the preceding packet passes review.

## P2 - exact Project -> CA binding

### Input contract
Consumes only a P1-frozen project trial plus authenticated/bounded evidence already available at the observation cut.

### State machine
`UNBOUND -> CANDIDATE_BINDING -> BOUND_HIGH`

Safety branches:
`UNBOUND|CANDIDATE_BINDING -> CONFLICTED`
`BOUND_HIGH -> SUPERSEDED_WITH_PROOF`
`* -> REVOKED` only with explicit revocation evidence.

### BOUND_HIGH conjunction
All must be true:
1. exact chain_id;
2. exact token contract verified on-chain;
3. authenticated project source OR deterministic project-controlled on-chain relation;
4. zero unresolved material identity conflict;
5. observed_at and available_at retained;
6. evidence hash retained;
7. relationship_type explicit;
8. migration/relaunch has explicit continuity proof.

No weighted score can substitute for this conjunction.

### Conflict precedence
A material conflicting exact CA, chain, control root, migration claim or project-authentication claim forces `CONFLICTED` until resolved by new explicit evidence. Recency alone never resolves conflict.

### Relationship vocabulary
Minimum deterministic vocabulary:
- FIRST_PARTY_EXPLICIT_CA
- PROJECT_CONTROLLED_ONCHAIN_RELATION
- FACTORY_LAUNCH_CANDIDATE_ONLY
- SOCIAL_CANDIDATE_ONLY
- MIGRATION_WITH_CONTINUITY_PROOF
- RELAUNCH_WITH_CONTINUITY_PROOF
- UNKNOWN

Only the first two, or migration/relaunch with explicit continuity proof plus the required conjunction, may support BOUND_HIGH. Pons/factory occurrence is candidate evidence only.

### Required receipts
binding_id, project_trial_id, chain_id, token_ca, relationship_type, binding_state, binding_provenance refs, first_candidate_at_utc, bound_high_at_utc_or_null, conflict_ids, onchain_verification, project_control_binding, supersedes_binding_id_or_null, evidence hashes.

### Tests
Positive:
- authenticated first-party exact CA + on-chain verification + no conflict -> BOUND_HIGH;
- deterministic project-controlled on-chain relation satisfying all required evidence -> BOUND_HIGH;
- explicit migration continuity preserves old binding and creates SUPERSEDED_WITH_PROOF lineage.

Negative:
- same ticker/name at two CAs -> CONFLICTED, never latest-wins;
- Pons TokenLaunched with copied project name -> at most CANDIDATE_BINDING;
- social-only CA -> at most CANDIDATE_BINDING;
- missing available_at/evidence hash/relationship type -> cannot BOUND_HIGH;
- source outage -> UNKNOWN/source-health failure, not REVOKED;
- SAFIX/SFX fixture remains CONFLICTED absent explicit continuity proof.

Hard kill: any material false Project->CA BOUND_HIGH link.

## P3 - deterministic material-change detector

### Principle
Compare P1/P2 frozen snapshots, never free-form current pages. Emit a retrigger only for a frozen material transition.

### Allowed transition classes
- NEW_AUTHENTICATED_CONTROL_ROOT
- NO_TOKEN_TO_PUBLIC_CA
- DESIGN_TO_DEPLOYED_MAINNET
- UNVERIFIED_CODE_TO_VERIFIED_DEPLOYED_CONTRACT
- NO_WORKING_SURFACE_TO_INDEPENDENTLY_OBSERVABLE_LIVE_USE
- NO_CHAIN_SPECIFIC_MECHANISM_TO_NEW_CHAIN_NATIVE_PRIMITIVE
- NEW_USABLE_PACKAGE_OR_RELEASE
- NEW_LINKABLE_FACTORY_EVENT
- STABLE_TO_AUTHENTICATED_CONTRADICTION_OR_CONFLICT
- FIRST_SELLABILITY_OR_LIQUIDITY_AFTER_BINDING

### Receipt
transition_id, project_trial_id, before_state_sha256, after_state_sha256, transition_class, observed_at_utc, available_at_utc, evidence_refs, source_health, conflict_state, retrigger_boolean.

### Explicit non-events
README wording, repeated marketing, engagement counts, reordered fields, duplicate URLs, unchanged package metadata and source outage are not material project transitions.

Tests:
- semantic no-op/reordering -> no retrigger;
- authenticated first CA publication -> retrigger;
- verified mainnet deployment after design-only -> retrigger;
- contradiction -> retrigger and preserve both states;
- source disappears -> source-health event only, no negative project inference;
- repeated same transition hash -> idempotent, no duplicate denominator or repeated DD trigger.

## P4 - exact-input A/B/C shadow comparator

### Immutable trial cut
One `comparison_input_sha256` generated from the same eligible project trial and source availability cut. A/B/C receive that exact immutable input.

### Variant isolation
- A: deterministic project-first baseline.
- B: A plus P5 bounded Jev semantic features.
- C: deterministic material-transition/evidence-family delta.
No variant can mutate shared input or fetch private incremental evidence.

### Outcome firewall
Discovery/comparison receipt is sealed before outcome maturity. Outcome joins by trial id only after maturity and cannot rewrite prior outputs.

### Comparator receipt
project_trial_id, comparison_input_sha256, eligibility_manifest_sha256, A output hash, B output hash, C output hash, route class per variant, DD decision per variant, evidence-retention hash, cost/latency fields, created_at_utc.

Tests:
- same input hash across A/B/C;
- mutation attempt rejected;
- permutation siblings do not create new trial;
- hidden outcome field rejected from pre-maturity input;
- repeated replay yields same deterministic A/C result;
- counters begin at zero on explicit shadow activation, never from historical fixtures.

## P5 - narrow Jev adapter

### Allowed questions only
- real_product_surface
- chain_native_specificity
- mechanic_falsifiability
- semantic_delta_value after deterministic before/after freeze

Direct `deep_dive_value` authority remains killed.

### Input sanitizer
B may receive authenticated/bounded semantic artifacts and deterministic labels only. Strip/withhold outcome, winner/failure labels, token returns, arithmetic tasks, date-order tasks, exact CA choice prompts and raw instruction-like adversarial text not needed as evidence.

### Authority
Jev output is a feature bundle, never truth. It cannot decide identity, provenance, CA, arithmetic, dates, MC, liquidity, sellability, BUY, SELL, DROP, promotion or thresholds.

### Failure behavior
service error, malformed response, low confidence or representation inconsistency -> RETAIN_OR_ESCALATE_NEVER_DROP and deterministic A/C remain valid.

### Required log
model_id=jev-1.13.0, model_version, state_sha256, question_set_sha256, question_id, answer, probability_distribution, confidence_if_supported, latency_ms, service_error, representation_order_id.

### Representation suite
Canonical, reversed evidence-item order, shuffled non-semantic metadata. Siblings are test-only and do not increase denominator. Material route-class flip from order alone is a Jev failure.

## P6 - denominator, outcomes and kill-state wiring

### Population
- unit: UNIQUE_ELIGIBLE_PROJECT_TRIAL
- >=30 future eligible projects
- >=2 distinct regimes
- >=10 qualified watches
- preserve zero-result days and every reject
- N1-N10 retained when observed
- NET/SAFIX/DARK prospective credit = 0

### Outcome join
Only after frozen observation and exact CA/sellability prerequisites where relevant. Store entry age, MC or UNKNOWN, liquidity, sellable MFE/MAE 1h/6h/24h/7d, realizable return after frozen slippage/notional rules, exit feasibility, first broad social/KOL propagation time and evidence-family conditioning.

Peak MC is never realizable return.

### Automatic research stop states, not promotion
Surface a STOP_RESEARCH condition when any frozen hard kill occurs:
- material false Project->CA link;
- critical evidence loss;
- Jev representation dependency;
- unsafe spoof/injection downgrade or unacceptable cost;
- advantage disappears with failed/similar denominator;
- advantage exists only on NET/SAFIX/DARK-like narratives;
- prospective held-out advantage fails;
- DD load rises without useful recall/precision gain;
- C matches B within frozen margin.

No STOP_RESEARCH condition can create production action. No pass can auto-promote.

### Survival calculations
Use exactly the frozen preregistration:
- B efficiency path: DD load reduction >=20%, recall no worse than A by >5pp, precision not worse, no material lead-time loss.
- B recall path: recall improvement >=10pp, DD load <=1.10x A, precision no worse by >5pp, median lead time not worse.
- B must add value vs C on >=1 primary metric beyond ordinary repeated-evaluation noise.
- best safe project-first challenger must find >=2 prospective qualified opportunities champion missed or found materially later, false links=0, critical evidence losses=0, DD load <=1.25x champion unless compensated, denominator complete.

## Release discipline

P2 code is the only next code packet after P1 acceptance. P3 cannot be released because P2 merely has a PR. It requires P2 tests + independent review + fresh-main readback. Repeat through P6.

For each packet Sol supervisor should perform:
1. fresh-main owner/redundancy check;
2. semantic diff against frozen prereg;
3. negative-test audit;
4. authority audit;
5. readback of merged canonical state.

Codex should not perform architecture discovery, threshold invention, research interpretation or policy design for these packets.
